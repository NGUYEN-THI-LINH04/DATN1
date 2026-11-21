# -*- coding: utf-8 -*-

"""
BUOC 07 - IMPORT TU VUNG HSK4 CO BAO VE

Mac dinh:
- Chi kiem tra truoc COMMIT.
- KHONG INSERT.
- KHONG UPDATE.
- KHONG DELETE.

Khi COMMIT o buoc sau:
- Kiem tra lai SHA256 cua Buoc 06.
- Kiem tra lai SQL hien tai.
- Tai su dung 12 TuVung cu.
- INSERT 988 TuVung moi.
- Tu moi co DaDuyet = 0.
- Tao mapping 1000 MaTuHSK -> MaTuVung.
- Toan bo INSERT trong 1 transaction.
- Loi thi ROLLBACK.

KHONG chay --commit khi chua duoc yeu cau.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata

from collections import Counter, defaultdict
from contextlib import closing
from pathlib import Path


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT),
)

from database import get_connection


HSK_LEVEL = 4

EXPECTED_TOTAL = 1000
EXPECTED_REUSE = 12
EXPECTED_INSERT = 988
EXPECTED_NEW_HANZI = 978
EXPECTED_NEW_READING = 10

EXPECTED_SOURCE_SHA256 = (
    "f911b69275024bffcc9d9b0bb9759ec4"
    "a91500e0858b79250fc9d996f43c816b"
)

EXPECTED_PLAN_SHA256 = (
    "b2f35a0cb9fe86446a7393c46204d85e"
    "8ea7a8edf8f22b92c9f7ee4ff4b07d5f"
)

CONFIRM_TOKEN = "HSK4-988"


DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

SOURCE = (
    DATA_DIR
    / "vocabulary_hsk4_import_draft.csv"
)

PREVIEW_JSON = (
    DATA_DIR
    / "vocabulary_hsk4_import_preview.json"
)

MAPPING = (
    DATA_DIR
    / "vocabulary_hsk4_import_result.csv"
)


MAPPING_FIELDS = [
    "MaMucNoiBo",
    "MaTuHSK",
    "MaTuVung",
    "ChuHan",
    "PhienAm",
    "TuLoai",
    "NghiaTiengViet",
    "HanhDong",
    "TrangThaiKiemDuyet",
    "VanDeCanKiemTra",
]


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def pinyin_key(value):

    return (
        unicodedata.normalize(
            "NFC",
            clean(value).casefold(),
        )
        .replace(" ", "")
        .replace("'", "")
        .replace("’", "")
    )


def word_key(hanzi, pinyin):

    return (
        clean(hanzi),
        pinyin_key(pinyin),
    )


def full_key(
    hanzi,
    pinyin,
    word_type,
    meaning,
):
    return (
        clean(hanzi),
        pinyin_key(pinyin),
        clean(word_type).casefold(),
        clean(meaning).casefold(),
    )


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open("rb") as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def sha256_plan(rows):

    payload = json.dumps(
        rows,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(
        payload
    ).hexdigest()


# ==========================================================
# 3. DOC FILE KE HOACH
# ==========================================================

def read_source():

    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay:\n{SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        required = {
            "MaTuHSK",
            "ChuHan",
            "PhienAm",
            "NghiaTiengViet",
            "TuLoai",
            "MaTuVungDaCo",
            "HanhDongDeXuat",
            "TrangThaiKiemDuyet",
            "VanDeCanKiemTra",
        }

        missing = (
            required
            - set(
                reader.fieldnames
                or []
            )
        )

        if missing:
            raise RuntimeError(
                "File nguon thieu cot: "
                + ", ".join(
                    sorted(missing)
                )
            )

        rows = list(reader)

    if len(rows) != EXPECTED_TOTAL:

        raise RuntimeError(
            f"Can {EXPECTED_TOTAL} muc, "
            f"hien co {len(rows)}."
        )

    codes = set()

    actions = Counter()

    for row in rows:

        code = clean(
            row.get("MaTuHSK")
        )

        if not re.fullmatch(
            r"L4-\d{4}",
            code,
        ):
            raise RuntimeError(
                f"Ma HSK4 khong hop le: "
                f"{code}"
            )

        if code in codes:
            raise RuntimeError(
                f"Trung MaTuHSK: {code}"
            )

        codes.add(code)

        hanzi = clean(
            row.get("ChuHan")
        )

        pinyin = clean(
            row.get("PhienAm")
        )

        meaning = clean(
            row.get(
                "NghiaTiengViet"
            )
        )

        word_type = clean(
            row.get("TuLoai")
        )

        if not (
            hanzi
            and pinyin
            and meaning
        ):
            raise RuntimeError(
                f"{code}: "
                "thieu ChuHan/Pinyin/Nghia."
            )

        if (
            len(hanzi) > 100
            or len(pinyin) > 200
            or len(meaning) > 2000
            or len(word_type) > 100
        ):
            raise RuntimeError(
                f"{code}: "
                "du lieu vuot gioi han."
            )

        action = clean(
            row.get(
                "HanhDongDeXuat"
            )
        )

        if action not in {
            "TAI_SU_DUNG",
            "INSERT_MOI",
        }:
            raise RuntimeError(
                f"{code}: "
                f"hanh dong khong hop le: "
                f"{action}"
            )

        actions[action] += 1

    if (
        actions["TAI_SU_DUNG"]
        != EXPECTED_REUSE
    ):
        raise RuntimeError(
            "Sai so luong TAI_SU_DUNG."
        )

    if (
        actions["INSERT_MOI"]
        != EXPECTED_INSERT
    ):
        raise RuntimeError(
            "Sai so luong INSERT_MOI."
        )

    return rows


# ==========================================================
# 4. DOC PREVIEW BUOC 06
# ==========================================================

def read_preview():

    if not PREVIEW_JSON.is_file():

        raise FileNotFoundError(
            "Chua co preview Buoc 06:\n"
            + str(PREVIEW_JSON)
        )

    data = json.loads(
        PREVIEW_JSON.read_text(
            encoding="utf-8"
        )
    )

    if (
        data.get("source_sha256")
        != EXPECTED_SOURCE_SHA256
    ):
        raise RuntimeError(
            "SOURCE SHA trong preview "
            "khong dung snapshot da kiem tra."
        )

    if (
        data.get("preview_plan_sha256")
        != EXPECTED_PLAN_SHA256
    ):
        raise RuntimeError(
            "PLAN SHA trong preview "
            "khong dung snapshot da kiem tra."
        )

    return data


# ==========================================================
# 5. KIEM TRA SCHEMA
# ==========================================================

def validate_schema(cursor):

    cursor.execute(
        """
        SELECT
            COLUMN_NAME,
            IS_NULLABLE,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = 'TuVung';
        """
    )

    columns = {
        clean(row[0]): {
            "nullable":
                clean(row[1]),

            "type":
                clean(row[2]),

            "max_length":
                row[3],

            "default":
                row[4],
        }
        for row in cursor.fetchall()
    }

    required = {
        "MaTuVung",
        "ChuHan",
        "ChuPhonThe",
        "PhienAm",
        "NghiaTiengViet",
        "TuLoai",
        "ViDuTiengTrung",
        "ViDuTiengViet",
        "MaAmThanh",
        "MaNguon",
        "DaDuyet",
        "MaQuanTriVienCapNhat",
        "NgayTao",
        "NgayCapNhat",
    }

    missing = (
        required
        - set(columns)
    )

    if missing:

        raise RuntimeError(
            "dbo.TuVung thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    cursor.execute(
        """
        SELECT COLUMNPROPERTY(
            OBJECT_ID('dbo.TuVung'),
            'MaTuVung',
            'IsIdentity'
        );
        """
    )

    is_identity = int(
        cursor.fetchone()[0]
        or 0
    )

    if is_identity != 1:

        raise RuntimeError(
            "TuVung.MaTuVung "
            "khong phai IDENTITY."
        )

    return columns


# ==========================================================
# 6. DOC SQL TuVung
# ==========================================================

def load_vocabulary(cursor):

    cursor.execute(
        """
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai
        FROM dbo.TuVung
        ORDER BY MaTuVung;
        """
    )

    exact = defaultdict(list)
    by_hanzi = defaultdict(list)

    total = 0

    for row in cursor.fetchall():

        total += 1

        item = {
            "id":
                int(row[0]),

            "hanzi":
                clean(row[1]),

            "pinyin":
                clean(row[2]),

            "meaning":
                clean(row[3]),

            "type":
                clean(row[4]),
        }

        exact[
            word_key(
                item["hanzi"],
                item["pinyin"],
            )
        ].append(item)

        by_hanzi[
            item["hanzi"]
        ].append(item)

    return (
        exact,
        by_hanzi,
        total,
    )


# ==========================================================
# 7. DOC HSK4 CHUAN
# ==========================================================

def load_hsk_reference(cursor):

    cursor.execute(
        """
        SELECT
            MaTuHSK,
            MaMucNoiBo,
            MaCapDo,
            ChuHan,
            PhienAm
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = ?;
        """,
        HSK_LEVEL,
    )

    index = defaultdict(list)

    total = 0

    for row in cursor.fetchall():

        total += 1

        code = clean(
            row[1]
        )

        index[
            code
        ].append({

            "id":
                int(row[0]),

            "level":
                int(row[2]),

            "hanzi":
                clean(row[3]),

            "pinyin":
                clean(row[4]),
        })

    return (
        index,
        total,
    )


# ==========================================================
# 8. TAO LAI PREVIEW PLAN
# ==========================================================

def rebuild_preview(
    rows,
    exact,
    by_hanzi,
    hsk_index,
):

    result = []

    reuse = 0
    insert = 0

    new_hanzi = 0
    new_reading = 0

    warning_rows = 0

    for row in rows:

        code = clean(
            row.get("MaTuHSK")
        )

        hanzi = clean(
            row.get("ChuHan")
        )

        pinyin = clean(
            row.get("PhienAm")
        )

        meaning = clean(
            row.get(
                "NghiaTiengViet"
            )
        )

        word_type = clean(
            row.get("TuLoai")
        )

        action = clean(
            row.get(
                "HanhDongDeXuat"
            )
        )

        standards = (
            hsk_index.get(
                code,
                [],
            )
        )

        if len(standards) != 1:

            raise RuntimeError(
                f"{code}: "
                "khong co dung 1 "
                "TuVungHSKChuan."
            )

        standard = standards[0]

        if (
            standard["hanzi"]
            != hanzi
        ):
            raise RuntimeError(
                f"{code}: "
                "ChuHan khac "
                "TuVungHSKChuan."
            )

        if (
            pinyin_key(
                standard["pinyin"]
            )
            !=
            pinyin_key(
                pinyin
            )
        ):
            raise RuntimeError(
                f"{code}: "
                "Pinyin khac "
                "TuVungHSKChuan."
            )

        matches = exact.get(
            word_key(
                hanzi,
                pinyin,
            ),
            [],
        )

        same_hanzi = (
            by_hanzi.get(
                hanzi,
                [],
            )
        )

        notes = []

        preview_id = ""

        # --------------------------------------------------
        # TAI SU DUNG
        # --------------------------------------------------

        if action == "TAI_SU_DUNG":

            reuse += 1

            old_id_text = clean(
                row.get(
                    "MaTuVungDaCo"
                )
            )

            if not old_id_text:

                raise RuntimeError(
                    f"{code}: "
                    "TAI_SU_DUNG "
                    "nhung thieu MaTuVung."
                )

            old_id = int(
                old_id_text
            )

            if len(matches) != 1:

                raise RuntimeError(
                    f"{code}: "
                    "SQL da thay doi. "
                    f"Co {len(matches)} "
                    "ban ghi ChuHan+Pinyin."
                )

            actual_id = int(
                matches[0]["id"]
            )

            if actual_id != old_id:

                raise RuntimeError(
                    f"{code}: "
                    "MaTuVung da thay doi."
                )

            preview_id = (
                actual_id
            )

            preview_status = (
                "PASS_TAI_SU_DUNG"
            )

        # --------------------------------------------------
        # INSERT MOI
        # --------------------------------------------------

        elif action == "INSERT_MOI":

            insert += 1

            if clean(
                row.get(
                    "MaTuVungDaCo"
                )
            ):
                raise RuntimeError(
                    f"{code}: "
                    "INSERT_MOI nhung "
                    "lai co MaTuVungDaCo."
                )

            if matches:

                raise RuntimeError(
                    f"{code}: "
                    "du kien INSERT "
                    "nhung ChuHan+Pinyin "
                    "da co trong SQL."
                )

            if same_hanzi:

                new_reading += 1

                preview_status = (
                    "PASS_INSERT_CACH_DOC_MOI"
                )

                notes.append(
                    "ChuHan da co, "
                    "Pinyin moi"
                )

            else:

                new_hanzi += 1

                preview_status = (
                    "PASS_INSERT_MOI"
                )

        else:

            raise RuntimeError(
                f"{code}: "
                "HanhDong khong hop le."
            )

        old_warning = clean(
            row.get(
                "VanDeCanKiemTra"
            )
        )

        if old_warning:

            warning_rows += 1

            notes.append(
                old_warning
            )

        result.append({

            "MaTuHSK":
                code,

            "MaTuHSKTrongSQL":
                standard["id"],

            "ChuHan":
                hanzi,

            "PhienAm":
                pinyin,

            "NghiaTiengViet":
                meaning,

            "TuLoai":
                word_type,

            "HanhDongDuKien":
                action,

            "MaTuVungDuKien":
                preview_id,

            "SoKhopChuHanPinyinSQL":
                len(matches),

            "SoKhopChuHanSQL":
                len(same_hanzi),

            "TrangThaiPreview":
                preview_status,

            "GhiChuPreview":
                "; ".join(notes),
        })

    return {
        "rows":
            result,

        "reuse":
            reuse,

        "insert":
            insert,

        "new_hanzi":
            new_hanzi,

        "new_reading":
            new_reading,

        "warning_rows":
            warning_rows,
    }


# ==========================================================
# 9. KIEM TRA NHOM TRUNG NGUON
# ==========================================================

def validate_source_duplicates(rows):

    groups = defaultdict(list)

    for row in rows:

        groups[
            word_key(
                row.get("ChuHan"),
                row.get("PhienAm"),
            )
        ].append(row)

    duplicates = {
        key: group
        for key, group
        in groups.items()
        if len(group) > 1
    }

    if len(duplicates) != 1:

        raise RuntimeError(
            "So nhom trung ChuHan+Pinyin "
            "khac Buoc 05-06."
        )

    key, group = next(
        iter(
            duplicates.items()
        )
    )

    if (
        key[0] != "批"
        or key[1]
        != pinyin_key("pī")
        or len(group) != 2
    ):

        raise RuntimeError(
            "Nhom trung khong con "
            "la 2 muc 批 pī."
        )

    full_keys = {
        full_key(
            row.get("ChuHan"),
            row.get("PhienAm"),
            row.get("TuLoai"),
            row.get(
                "NghiaTiengViet"
            ),
        )
        for row in group
    }

    if len(full_keys) != 2:

        raise RuntimeError(
            "Hai muc 批 pī "
            "khong con phan biet."
        )

    return len(duplicates)


# ==========================================================
# 10. TAO SUMMARY GIONG BUOC 06
# ==========================================================

def make_summary(
    source_hash,
    plan,
    sql_total,
    hsk_total,
    duplicate_count,
):

    return {

        "hsk_level":
            HSK_LEVEL,

        "total":
            len(
                plan["rows"]
            ),

        "reuse":
            plan["reuse"],

        "insert":
            plan["insert"],

        "insert_new_hanzi":
            plan["new_hanzi"],

        "insert_new_reading":
            plan["new_reading"],

        "source_warning_rows":
            plan["warning_rows"],

        "duplicate_source_groups":
            duplicate_count,

        "source_file":
            str(SOURCE),

        "source_sha256":
            source_hash,

        "preview_plan_sha256":
            sha256_plan(
                plan["rows"]
            ),

        "sql_tuvung_count_at_preview":
            sql_total,

        "sql_hsk4_reference_count":
            hsk_total,
    }


# ==========================================================
# 11. HIEN THI SAI KHAC PREVIEW
# ==========================================================

def compare_summary(
    old,
    current,
):

    if old == current:
        return

    print(
        "\nPREVIEW DA THAY DOI:"
    )

    all_keys = sorted(
        set(old)
        | set(current)
    )

    for key in all_keys:

        old_value = old.get(
            key
        )

        new_value = current.get(
            key
        )

        if old_value != new_value:

            print(
                f"  {key}:"
            )

            print(
                f"    preview = "
                f"{old_value}"
            )

            print(
                f"    hien tai = "
                f"{new_value}"
            )

    raise RuntimeError(
        "Trang thai hien tai "
        "khong con giong Buoc 06. "
        "KHONG DUOC COMMIT."
    )


# ==========================================================
# 12. TAO MAPPING TRUOC IMPORT
# ==========================================================

def build_mapping_plan(
    rows,
    hsk_index,
):

    result = []

    for row in rows:

        code = clean(
            row.get("MaTuHSK")
        )

        standard = (
            hsk_index[code][0]
        )

        action = clean(
            row.get(
                "HanhDongDeXuat"
            )
        )

        old_id = clean(
            row.get(
                "MaTuVungDaCo"
            )
        )

        result.append({

            "MaMucNoiBo":
                code,

            "MaTuHSK":
                standard["id"],

            "MaTuVung":
                (
                    int(old_id)
                    if old_id
                    else None
                ),

            "ChuHan":
                clean(
                    row.get("ChuHan")
                ),

            "PhienAm":
                clean(
                    row.get("PhienAm")
                ),

            "TuLoai":
                clean(
                    row.get("TuLoai")
                ),

            "NghiaTiengViet":
                clean(
                    row.get(
                        "NghiaTiengViet"
                    )
                ),

            "HanhDong":
                action,

            "TrangThaiKiemDuyet":
                clean(
                    row.get(
                        "TrangThaiKiemDuyet"
                    )
                ),

            "VanDeCanKiemTra":
                clean(
                    row.get(
                        "VanDeCanKiemTra"
                    )
                ),
        })

    return result


# ==========================================================
# 13. INSERT 1 TU VUNG
# ==========================================================

def insert_one(
    cursor,
    row,
):

    # Giu cung cach INSERT voi pipeline HSK3.
    # Tu moi chua duyet: DaDuyet = 0.

    cursor.execute(
        """
        INSERT INTO dbo.TuVung
        (
            ChuHan,
            ChuPhonThe,
            PhienAm,
            NghiaTiengViet,
            TuLoai,
            ViDuTiengTrung,
            ViDuTiengViet,
            MaAmThanh,
            MaNguon,
            DaDuyet,
            MaQuanTriVienCapNhat,
            NgayCapNhat
        )
        OUTPUT INSERTED.MaTuVung
        VALUES
        (
            ?,
            NULL,
            ?,
            ?,
            ?,
            NULL,
            NULL,
            NULL,
            NULL,
            0,
            NULL,
            NULL
        );
        """,
        row["ChuHan"],
        row["PhienAm"],
        row["NghiaTiengViet"],
        (
            row["TuLoai"]
            or None
        ),
    )

    inserted = (
        cursor.fetchone()
    )

    if inserted is None:

        raise RuntimeError(
            "Khong lay duoc "
            "MaTuVung sau INSERT."
        )

    return int(
        inserted[0]
    )


# ==========================================================
# 14. KIEM TRA CAC TU VUA INSERT
# ==========================================================

def validate_inserted_rows(
    cursor,
    mapping,
):

    inserted_rows = [
        row
        for row in mapping
        if row["HanhDong"]
        == "INSERT_MOI"
    ]

    ids = [
        int(
            row["MaTuVung"]
        )
        for row in inserted_rows
    ]

    if len(ids) != EXPECTED_INSERT:

        raise RuntimeError(
            "Sai so MaTuVung "
            "vua INSERT."
        )

    if len(set(ids)) != EXPECTED_INSERT:

        raise RuntimeError(
            "MaTuVung moi bi trung."
        )

    placeholders = ",".join(
        "?"
        for _ in ids
    )

    cursor.execute(
        f"""
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai,
            DaDuyet
        FROM dbo.TuVung
        WHERE MaTuVung IN (
            {placeholders}
        );
        """,
        *ids,
    )

    sql_rows = {
        int(row[0]): {
            "ChuHan":
                clean(row[1]),

            "PhienAm":
                clean(row[2]),

            "NghiaTiengViet":
                clean(row[3]),

            "TuLoai":
                clean(row[4]),

            "DaDuyet":
                int(row[5] or 0),
        }
        for row in cursor.fetchall()
    }

    if len(sql_rows) != EXPECTED_INSERT:

        raise RuntimeError(
            "Khong doc lai du "
            "988 tu vua INSERT."
        )

    for item in inserted_rows:

        vocab_id = int(
            item["MaTuVung"]
        )

        sql_row = (
            sql_rows.get(
                vocab_id
            )
        )

        if sql_row is None:

            raise RuntimeError(
                f"Khong tim thay "
                f"MaTuVung={vocab_id}."
            )

        if (
            sql_row["ChuHan"]
            != clean(
                item["ChuHan"]
            )
        ):
            raise RuntimeError(
                f"MaTuVung={vocab_id}: "
                "sai ChuHan."
            )

        if (
            pinyin_key(
                sql_row["PhienAm"]
            )
            !=
            pinyin_key(
                item["PhienAm"]
            )
        ):
            raise RuntimeError(
                f"MaTuVung={vocab_id}: "
                "sai Pinyin."
            )

        if (
            sql_row[
                "NghiaTiengViet"
            ]
            !=
            clean(
                item[
                    "NghiaTiengViet"
                ]
            )
        ):
            raise RuntimeError(
                f"MaTuVung={vocab_id}: "
                "sai nghia Viet."
            )

        if (
            sql_row["TuLoai"]
            !=
            clean(
                item["TuLoai"]
            )
        ):
            raise RuntimeError(
                f"MaTuVung={vocab_id}: "
                "sai TuLoai."
            )

        if (
            sql_row["DaDuyet"]
            != 0
        ):
            raise RuntimeError(
                f"MaTuVung={vocab_id}: "
                "DaDuyet phai bang 0."
            )


# ==========================================================
# 15. GHI FILE MAPPING
# ==========================================================

def write_mapping(
    path,
    rows,
):

    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=
                MAPPING_FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# ==========================================================
# 16. MAIN
# ==========================================================

def main():

    parser = (
        argparse.ArgumentParser()
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Cho phep ghi 988 tu moi vao SQL.",
    )

    parser.add_argument(
        "--confirm",
        default="",
        help="Ma xac nhan COMMIT.",
    )

    args = parser.parse_args()

    print("=" * 76)

    print(
        "BUOC 07 - KIEM TRA / "
        "IMPORT TU VUNG HSK4"
    )

    print("=" * 76)

    print(
        "CHE DO:",
        (
            "COMMIT"
            if args.commit
            else
            "PRE-COMMIT CHECK"
        ),
    )

    # ======================================================
    # 1. BAO VE COMMIT
    # ======================================================

    if args.commit:

        if (
            args.confirm
            != CONFIRM_TOKEN
        ):

            raise RuntimeError(
                "COMMIT bi khoa. "
                "Ma xac nhan khong dung."
            )

    # ======================================================
    # 2. DOC SOURCE + PREVIEW
    # ======================================================

    rows = read_source()

    old_preview = (
        read_preview()
    )

    source_hash = (
        sha256_file(
            SOURCE
        )
    )

    print(
        "\n[1] KIEM TRA SHA256"
    )

    print(
        "SOURCE:",
        source_hash,
    )

    if (
        source_hash
        != EXPECTED_SOURCE_SHA256
    ):

        raise RuntimeError(
            "File Buoc 05 "
            "da bi thay doi."
        )

    print(
        "PASS: SOURCE SHA256"
    )

    duplicate_count = (
        validate_source_duplicates(
            rows
        )
    )

    print(
        "PASS: 批 pī "
        "van la 2 muc rieng."
    )

    # ======================================================
    # 3. KET NOI SQL
    # ======================================================

    with closing(
        get_connection()
    ) as connection:

        connection.autocommit = False

        committed = False

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    "SELECT DB_NAME();"
                )

                db_name = clean(
                    cursor.fetchone()[0]
                )

                print(
                    "\n[2] DATABASE:",
                    db_name,
                )

                if (
                    db_name.casefold()
                    !=
                    "HocTiengTrungDB".casefold()
                ):

                    raise RuntimeError(
                        "Dang ket noi nham "
                        "database."
                    )

                validate_schema(
                    cursor
                )

                # ------------------------------------------
                # Neu COMMIT thi khoa bang TuVung trong
                # transaction de tranh thay doi giua
                # luc kiem tra va INSERT.
                # ------------------------------------------

                if args.commit:

                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM dbo.TuVung
                        WITH (
                            TABLOCKX,
                            HOLDLOCK
                        );
                        """
                    )

                    locked_count = int(
                        cursor.fetchone()[0]
                    )

                    print(
                        "Da khoa dbo.TuVung "
                        "trong transaction."
                    )

                    print(
                        "So ban ghi:",
                        locked_count,
                    )

                # ------------------------------------------
                # Doc trang thai hien tai
                # ------------------------------------------

                (
                    exact,
                    by_hanzi,
                    sql_total,
                ) = load_vocabulary(
                    cursor
                )

                (
                    hsk_index,
                    hsk_total,
                ) = load_hsk_reference(
                    cursor
                )

                print(
                    "dbo.TuVung:",
                    sql_total,
                )

                print(
                    "TuVungHSKChuan HSK4:",
                    hsk_total,
                )

                if (
                    hsk_total
                    != EXPECTED_TOTAL
                ):

                    raise RuntimeError(
                        "HSK4 reference "
                        "khong con 1000."
                    )

                if (
                    len(hsk_index)
                    != EXPECTED_TOTAL
                ):

                    raise RuntimeError(
                        "MaMucNoiBo HSK4 "
                        "bi trung/thieu."
                    )

                # ==========================================
                # 4. REBUILD PREVIEW
                # ==========================================

                print(
                    "\n[3] DOI CHIEU LAI "
                    "VOI BUOC 06"
                )

                plan = rebuild_preview(
                    rows,
                    exact,
                    by_hanzi,
                    hsk_index,
                )

                current_summary = (
                    make_summary(
                        source_hash,
                        plan,
                        sql_total,
                        hsk_total,
                        duplicate_count,
                    )
                )

                compare_summary(
                    old_preview,
                    current_summary,
                )

                current_plan_hash = (
                    current_summary[
                        "preview_plan_sha256"
                    ]
                )

                if (
                    current_plan_hash
                    != EXPECTED_PLAN_SHA256
                ):

                    raise RuntimeError(
                        "PLAN SHA256 "
                        "khong con khop."
                    )

                print(
                    "PASS: PREVIEW "
                    "khong thay doi."
                )

                print(
                    "PLAN SHA256:"
                )

                print(
                    current_plan_hash
                )

                # ==========================================
                # 5. TONG HOP
                # ==========================================

                print(
                    "\n[4] TONG HOP"
                )

                print(
                    "Tong mapping:",
                    len(
                        plan["rows"]
                    ),
                )

                print(
                    "Tai su dung:",
                    plan["reuse"],
                )

                print(
                    "INSERT moi:",
                    plan["insert"],
                )

                print(
                    "  + ChuHan moi:",
                    plan[
                        "new_hanzi"
                    ],
                )

                print(
                    "  + Cach doc moi:",
                    plan[
                        "new_reading"
                    ],
                )

                print(
                    "Canh bao nguon:",
                    plan[
                        "warning_rows"
                    ],
                )

                if (
                    plan["reuse"]
                    != EXPECTED_REUSE
                    or
                    plan["insert"]
                    != EXPECTED_INSERT
                    or
                    plan["new_hanzi"]
                    != EXPECTED_NEW_HANZI
                    or
                    plan["new_reading"]
                    != EXPECTED_NEW_READING
                ):

                    raise RuntimeError(
                        "Thong ke khac "
                        "Buoc 06."
                    )

                # ==========================================
                # 6. MAC DINH CHI KIEM TRA
                # ==========================================

                if not args.commit:

                    connection.rollback()

                    print(
                        "\n" + "=" * 76
                    )

                    print(
                        "PRE-COMMIT CHECK "
                        "HSK4 THANH CONG"
                    )

                    print("=" * 76)

                    print(
                        "Tong:",
                        EXPECTED_TOTAL,
                    )

                    print(
                        "Tai su dung:",
                        EXPECTED_REUSE,
                    )

                    print(
                        "Se INSERT:",
                        EXPECTED_INSERT,
                    )

                    print(
                        "SQL hien tai:",
                        sql_total,
                    )

                    print(
                        "SQL sau import du kien:",
                        sql_total
                        + EXPECTED_INSERT,
                    )

                    print(
                        "\nSAN SANG CHO "
                        "BUOC COMMIT."
                    )

                    print(
                        "CHUA GHI BAT KY "
                        "DU LIEU NAO VAO SQL."
                    )

                    print("=" * 76)

                    return

                # ==========================================
                # 7. BAO VE FILE MAPPING
                # ==========================================

                if MAPPING.exists():

                    raise RuntimeError(
                        "Da ton tai file "
                        "mapping ket qua. "
                        "KHONG IMPORT LAP."
                    )

                pending = (
                    MAPPING.with_suffix(
                        ".pending.csv"
                    )
                )

                if pending.exists():

                    raise RuntimeError(
                        "Da ton tai mapping "
                        "pending. "
                        "Can kiem tra truoc."
                    )

                # ==========================================
                # 8. LAP MAPPING
                # ==========================================

                mapping = (
                    build_mapping_plan(
                        rows,
                        hsk_index,
                    )
                )

                # Bao ve cac INSERT moi:
                # khong duoc trung hoan toan
                # ChuHan+Pinyin+TuLoai+Nghia.

                new_full_keys = []

                for item in mapping:

                    if (
                        item["HanhDong"]
                        != "INSERT_MOI"
                    ):
                        continue

                    new_full_keys.append(
                        full_key(
                            item["ChuHan"],
                            item["PhienAm"],
                            item["TuLoai"],
                            item[
                                "NghiaTiengViet"
                            ],
                        )
                    )

                if (
                    len(new_full_keys)
                    !=
                    len(
                        set(
                            new_full_keys
                        )
                    )
                ):

                    raise RuntimeError(
                        "Co tu moi trung "
                        "hoan toan trong "
                        "cung lan import."
                    )

                # ==========================================
                # 9. INSERT 988 TU MOI
                # ==========================================

                print(
                    "\n[5] BAT DAU INSERT"
                )

                inserted = 0

                for item in mapping:

                    if (
                        item["HanhDong"]
                        != "INSERT_MOI"
                    ):
                        continue

                    new_id = insert_one(
                        cursor,
                        item,
                    )

                    item[
                        "MaTuVung"
                    ] = new_id

                    inserted += 1

                    if (
                        inserted % 100
                        == 0
                    ):

                        print(
                            f"Da INSERT "
                            f"{inserted}/"
                            f"{EXPECTED_INSERT}"
                        )

                if inserted != EXPECTED_INSERT:

                    raise RuntimeError(
                        "So INSERT "
                        "khong dung 988."
                    )

                # ==========================================
                # 10. KIEM TRA TRONG TRANSACTION
                # ==========================================

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.TuVung;
                    """
                )

                after_count = int(
                    cursor.fetchone()[0]
                )

                if (
                    after_count
                    !=
                    sql_total
                    + EXPECTED_INSERT
                ):

                    raise RuntimeError(
                        "Tong TuVung "
                        "sau INSERT "
                        "khong hop le."
                    )

                validate_inserted_rows(
                    cursor,
                    mapping,
                )

                if any(
                    item["MaTuVung"]
                    is None
                    for item in mapping
                ):

                    raise RuntimeError(
                        "Con mapping "
                        "chua co MaTuVung."
                    )

                if len({
                    item["MaMucNoiBo"]
                    for item in mapping
                }) != EXPECTED_TOTAL:

                    raise RuntimeError(
                        "Mapping khong du "
                        "1000 MaTuHSK."
                    )

                print(
                    "PASS: da kiem tra "
                    "988 tu trong transaction."
                )

                print(
                    "Tong dbo.TuVung "
                    "trong transaction:",
                    after_count,
                )

                # ==========================================
                # 11. GHI MAPPING TAM
                # ==========================================

                write_mapping(
                    pending,
                    mapping,
                )

                # ==========================================
                # 12. COMMIT
                # ==========================================

                try:

                    connection.commit()

                    committed = True

                except Exception:

                    pending.unlink(
                        missing_ok=True
                    )

                    raise

                # SQL da commit.
                # Doi ten mapping tam thanh ket qua.

                try:

                    pending.rename(
                        MAPPING
                    )

                except Exception as error:

                    print(
                        "\nCANH BAO QUAN TRONG:"
                    )

                    print(
                        "SQL DA COMMIT "
                        "NHUNG KHONG DOI TEN "
                        "DUOC FILE MAPPING."
                    )

                    print(
                        "File mapping tam:"
                    )

                    print(
                        pending
                    )

                    print(
                        "Loi:",
                        error,
                    )

                    return

                # ==========================================
                # 13. THANH CONG
                # ==========================================

                print(
                    "\n" + "=" * 76
                )

                print(
                    "IMPORT TU VUNG "
                    "HSK4 THANH CONG"
                )

                print("=" * 76)

                print(
                    "Tong mapping:",
                    len(mapping),
                )

                print(
                    "Tai su dung:",
                    EXPECTED_REUSE,
                )

                print(
                    "Da INSERT:",
                    inserted,
                )

                print(
                    "dbo.TuVung truoc:",
                    sql_total,
                )

                print(
                    "dbo.TuVung sau:",
                    after_count,
                )

                print(
                    "Tu moi DaDuyet = 0"
                )

                print(
                    "\nMapping:"
                )

                print(
                    " ",
                    MAPPING,
                )

                print(
                    "\nSQL DA COMMIT."
                )

                print("=" * 76)

        except Exception:

            if not committed:

                connection.rollback()

            raise


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print(
            "\nLOI:"
        )

        print(
            error
        )

        raise SystemExit(1)