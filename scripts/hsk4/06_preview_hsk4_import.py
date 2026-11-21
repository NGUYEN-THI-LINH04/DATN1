# -*- coding: utf-8 -*-
"""
BUOC 06 - PREVIEW IMPORT TU VUNG HSK4

Muc dich:
1. Doc ke hoach 1000 muc HSK4 tu Buoc 05.
2. Kiem tra lai schema dbo.TuVung.
3. Kiem tra lai 1000 MaTuHSK voi TuVungHSKChuan.
4. Xac minh 12 muc TAI_SU_DUNG van dung MaTuVung.
5. Xac minh 988 muc INSERT_MOI van chua ton tai.
6. Xac minh:
   - 978 muc hoan toan chua co ChuHan
   - 10 muc cung ChuHan nhung la Pinyin moi
   - 批 pī van la 2 muc rieng
7. Tao PREVIEW + hash de khoa du lieu cho buoc COMMIT sau.

CHI DOC SQL.
KHONG INSERT.
KHONG UPDATE.
KHONG DELETE.
"""

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

PREVIEW_CSV = (
    DATA_DIR
    / "vocabulary_hsk4_import_preview.csv"
)

PREVIEW_JSON = (
    DATA_DIR
    / "vocabulary_hsk4_import_preview.json"
)


PREVIEW_FIELDS = [
    "MaTuHSK",
    "MaTuHSKTrongSQL",
    "ChuHan",
    "PhienAm",
    "NghiaTiengViet",
    "TuLoai",
    "HanhDongDuKien",
    "MaTuVungDuKien",
    "SoKhopChuHanPinyinSQL",
    "SoKhopChuHanSQL",
    "TrangThaiPreview",
    "GhiChuPreview",
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


def normalize_pinyin(value):

    text = unicodedata.normalize(
        "NFC",
        clean(value).casefold(),
    )

    return (
        text
        .replace(" ", "")
        .replace("'", "")
        .replace("’", "")
    )


def word_key(hanzi, pinyin):
    return (
        clean(hanzi),
        normalize_pinyin(pinyin),
    )


def full_source_key(row):
    return (
        clean(row.get("ChuHan")),
        normalize_pinyin(
            row.get("PhienAm")
        ),
        clean(
            row.get("TuLoai")
        ).casefold(),
        clean(
            row.get(
                "NghiaTiengViet"
            )
        ).casefold(),
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
            f"Khong tim thay file:\n{SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    if len(rows) != EXPECTED_TOTAL:

        raise RuntimeError(
            f"Can {EXPECTED_TOTAL} muc, "
            f"nhan duoc {len(rows)}."
        )

    required_columns = {
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

    actual_columns = set(
        rows[0].keys()
    )

    missing = (
        required_columns
        - actual_columns
    )

    if missing:

        raise RuntimeError(
            "File ke hoach thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    ids = [
        clean(
            row.get("MaTuHSK")
        )
        for row in rows
    ]

    if any(
        not value
        for value in ids
    ):
        raise RuntimeError(
            "Co MaTuHSK rong."
        )

    if len(set(ids)) != EXPECTED_TOTAL:

        raise RuntimeError(
            "MaTuHSK bi trung."
        )

    return rows


# ==========================================================
# 4. KIEM TRA SCHEMA dbo.TuVung
# ==========================================================

def validate_tuvung_schema(cursor):

    cursor.execute(
        """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = 'TuVung'
        ORDER BY ORDINAL_POSITION;
        """
    )

    rows = cursor.fetchall()

    schema = {
        row[0]: {
            "type": row[1],
            "max_length": row[2],
            "nullable": row[3],
            "default": row[4],
        }
        for row in rows
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
        - set(schema)
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
        SELECT
            COLUMNPROPERTY(
                OBJECT_ID('dbo.TuVung'),
                'MaTuVung',
                'IsIdentity'
            );
        """
    )

    is_identity = int(
        cursor.fetchone()[0] or 0
    )

    if is_identity != 1:

        raise RuntimeError(
            "TuVung.MaTuVung "
            "khong phai IDENTITY."
        )

    ngay_tao = schema["NgayTao"]

    if (
        ngay_tao["nullable"] == "NO"
        and ngay_tao["default"] is None
    ):
        raise RuntimeError(
            "NgayTao NOT NULL "
            "nhung khong co DEFAULT."
        )

    return schema


# ==========================================================
# 5. DOC dbo.TuVung
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
            "MaTuVung":
                int(row[0]),

            "ChuHan":
                clean(row[1]),

            "PhienAm":
                clean(row[2]),

            "NghiaTiengViet":
                clean(row[3]),

            "TuLoai":
                clean(row[4]),
        }

        exact[
            word_key(
                item["ChuHan"],
                item["PhienAm"],
            )
        ].append(item)

        by_hanzi[
            item["ChuHan"]
        ].append(item)

    return (
        exact,
        by_hanzi,
        total,
    )


# ==========================================================
# 6. DOC TuVungHSKChuan CAP 4
# ==========================================================

def load_hsk4_reference(cursor):

    cursor.execute(
        """
        SELECT
            MaTuHSK,
            MaMucNoiBo,
            MaCapDo,
            ChuHan,
            PhienAm,
            TuLoai,
            NghiaTiengVietThamChieu
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = ?
        ORDER BY
            SoThuTuNguon,
            MaTuHSK;
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

            "MaTuHSK":
                int(row[0]),

            "MaMucNoiBo":
                code,

            "MaCapDo":
                int(row[2]),

            "ChuHan":
                clean(row[3]),

            "PhienAm":
                clean(row[4]),

            "TuLoai":
                clean(row[5]),

            "NghiaTiengViet":
                clean(row[6]),
        })

    return (
        index,
        total,
    )


# ==========================================================
# 7. XUAT FILE PREVIEW
# ==========================================================

def write_csv(path, rows):

    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=PREVIEW_FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


# ==========================================================
# 8. MAIN
# ==========================================================

def main():

    print("=" * 74)
    print("BUOC 06 - PREVIEW IMPORT TU VUNG HSK4")
    print("=" * 74)

    print(
        "CHE DO: CHI DOC SQL"
    )

    print(
        "KHONG INSERT / UPDATE / DELETE"
    )

    # ======================================================
    # Bao ve preview cu
    # ======================================================

    for path in (
        PREVIEW_CSV,
        PREVIEW_JSON,
    ):

        if path.exists():

            raise FileExistsError(
                f"Da ton tai file:\n{path}\n"
                "Khong tu dong ghi de."
            )

    # ======================================================
    # 1. DOC KE HOACH
    # ======================================================

    print(
        "\n[1] DOC KE HOACH BUOC 05"
    )

    rows = read_source()

    source_hash = sha256_file(
        SOURCE
    )

    planned_counts = Counter(
        clean(
            row.get(
                "HanhDongDeXuat"
            )
        )
        for row in rows
    )

    print(
        "Tong muc:",
        len(rows),
    )

    print(
        "TAI_SU_DUNG:",
        planned_counts[
            "TAI_SU_DUNG"
        ],
    )

    print(
        "INSERT_MOI:",
        planned_counts[
            "INSERT_MOI"
        ],
    )

    if (
        planned_counts["TAI_SU_DUNG"]
        != EXPECTED_REUSE
    ):
        raise RuntimeError(
            "So TAI_SU_DUNG "
            "khac Buoc 05."
        )

    if (
        planned_counts["INSERT_MOI"]
        != EXPECTED_INSERT
    ):
        raise RuntimeError(
            "So INSERT_MOI "
            "khac Buoc 05."
        )

    if set(
        planned_counts.keys()
    ) != {
        "TAI_SU_DUNG",
        "INSERT_MOI",
    }:

        raise RuntimeError(
            "Con HanhDongDeXuat "
            "ngoai TAI_SU_DUNG/INSERT_MOI."
        )

    # ======================================================
    # 2. KIEM TRA NHOM TRUNG TRONG NGUON
    # ======================================================

    print(
        "\n[2] KIEM TRA NHOM "
        "CHUHAN + PINYIN TRONG NGUON"
    )

    source_groups = defaultdict(list)

    for row in rows:

        source_groups[
            word_key(
                row.get("ChuHan"),
                row.get("PhienAm"),
            )
        ].append(row)

    duplicate_groups = {
        key: group
        for key, group
        in source_groups.items()
        if len(group) > 1
    }

    print(
        "So nhom trung:",
        len(duplicate_groups),
    )

    if len(
        duplicate_groups
    ) != 1:

        raise RuntimeError(
            "So nhom trung ChuHan + Pinyin "
            "khac Buoc 05."
        )

    duplicate_key, duplicate_group = next(
        iter(
            duplicate_groups.items()
        )
    )

    if (
        duplicate_key[0] != "批"
        or duplicate_key[1]
        != normalize_pinyin("pī")
        or len(duplicate_group) != 2
    ):

        raise RuntimeError(
            "Nhom trung khong con la "
            "2 muc 批 pī."
        )

    if any(
        clean(
            row.get(
                "HanhDongDeXuat"
            )
        )
        != "INSERT_MOI"
        for row in duplicate_group
    ):

        raise RuntimeError(
            "Hai muc 批 pī "
            "phai la INSERT_MOI."
        )

    if len({
        full_source_key(row)
        for row in duplicate_group
    }) != 2:

        raise RuntimeError(
            "Hai muc 批 pī "
            "khong con phan biet."
        )

    print(
        "PASS: 批 pī = 2 muc rieng."
    )

    # ======================================================
    # 3. DOC VA KIEM TRA SQL
    # ======================================================

    print(
        "\n[3] KIEM TRA SQL HIEN TAI"
    )

    with closing(
        get_connection()
    ) as connection:

        if getattr(
            connection,
            "autocommit",
            False,
        ):

            raise RuntimeError(
                "Ket noi dang "
                "autocommit=True."
            )

        with closing(
            connection.cursor()
        ) as cursor:

            schema = (
                validate_tuvung_schema(
                    cursor
                )
            )

            (
                exact,
                by_hanzi,
                sql_vocab_total,
            ) = load_vocabulary(
                cursor
            )

            (
                hsk_index,
                hsk_total,
            ) = load_hsk4_reference(
                cursor
            )

            # SELECT only, nhung van rollback
            # de ket thuc transaction sach.
            connection.rollback()

    print(
        "dbo.TuVung:",
        sql_vocab_total,
        "ban ghi",
    )

    print(
        "TuVungHSKChuan HSK4:",
        hsk_total,
    )

    if hsk_total != EXPECTED_TOTAL:

        raise RuntimeError(
            "TuVungHSKChuan HSK4 "
            "khong con du 1000 muc."
        )

    if len(
        hsk_index
    ) != EXPECTED_TOTAL:

        raise RuntimeError(
            "MaMucNoiBo HSK4 "
            "bi trung hoac thieu."
        )

    print(
        "PASS: schema dbo.TuVung hop le."
    )

    # ======================================================
    # 4. DOI CHIEU TOAN BO 1000 MUC
    # ======================================================

    print(
        "\n[4] MO PHONG 1000 QUYET DINH"
    )

    result = []

    reuse_count = 0
    insert_count = 0
    new_hanzi_count = 0
    new_reading_count = 0

    warning_count = 0

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

        planned_id_text = clean(
            row.get(
                "MaTuVungDaCo"
            )
        )

        if not (
            code
            and hanzi
            and pinyin
            and meaning
        ):

            raise RuntimeError(
                f"{code}: "
                "thieu du lieu bat buoc."
            )

        # ----------------------------------------------
        # Kiem tra MaTuHSK voi bang chuan
        # ----------------------------------------------

        standards = (
            hsk_index.get(
                code,
                [],
            )
        )

        if len(standards) != 1:

            raise RuntimeError(
                f"{code}: "
                "khong co dung 1 dong "
                "TuVungHSKChuan."
            )

        standard = standards[0]

        if (
            clean(
                standard["ChuHan"]
            )
            != hanzi
        ):

            raise RuntimeError(
                f"{code}: "
                "ChuHan khac TuVungHSKChuan."
            )

        if (
            normalize_pinyin(
                standard["PhienAm"]
            )
            !=
            normalize_pinyin(
                pinyin
            )
        ):

            raise RuntimeError(
                f"{code}: "
                "Pinyin khac TuVungHSKChuan."
            )

        # ----------------------------------------------
        # SQL hien tai
        # ----------------------------------------------

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

        note_parts = []

        # ----------------------------------------------
        # TAI SU DUNG
        # ----------------------------------------------

        if action == "TAI_SU_DUNG":

            reuse_count += 1

            if not planned_id_text:

                raise RuntimeError(
                    f"{code}: "
                    "TAI_SU_DUNG nhung "
                    "thieu MaTuVungDaCo."
                )

            try:

                planned_id = int(
                    planned_id_text
                )

            except ValueError:

                raise RuntimeError(
                    f"{code}: "
                    "MaTuVungDaCo "
                    "khong phai so."
                )

            if len(matches) != 1:

                raise RuntimeError(
                    f"{code}: "
                    "DB da thay doi - "
                    f"tim thay {len(matches)} "
                    "ban ghi ChuHan+Pinyin."
                )

            actual_id = int(
                matches[0][
                    "MaTuVung"
                ]
            )

            if actual_id != planned_id:

                raise RuntimeError(
                    f"{code}: "
                    "MaTuVung thay doi "
                    f"{planned_id} -> "
                    f"{actual_id}."
                )

            preview_status = (
                "PASS_TAI_SU_DUNG"
            )

            preview_id = actual_id

        # ----------------------------------------------
        # INSERT MOI
        # ----------------------------------------------

        elif action == "INSERT_MOI":

            insert_count += 1

            if planned_id_text:

                raise RuntimeError(
                    f"{code}: "
                    "INSERT_MOI nhung "
                    "lai co MaTuVungDaCo."
                )

            # Neu exact key da xuat hien trong DB
            # thi DB da thay doi sau Buoc 05.
            if matches:

                raise RuntimeError(
                    f"{code}: "
                    "du kien INSERT_MOI "
                    "nhung ChuHan + Pinyin "
                    "da ton tai trong SQL."
                )

            if same_hanzi:

                new_reading_count += 1

                preview_status = (
                    "PASS_INSERT_CACH_DOC_MOI"
                )

                note_parts.append(
                    "ChuHan da co, "
                    "Pinyin moi"
                )

            else:

                new_hanzi_count += 1

                preview_status = (
                    "PASS_INSERT_MOI"
                )

            preview_id = ""

        else:

            raise RuntimeError(
                f"{code}: "
                f"HanhDong khong hop le: "
                f"{action}"
            )

        # ----------------------------------------------
        # Canh bao nguon
        # ----------------------------------------------

        old_warning = clean(
            row.get(
                "VanDeCanKiemTra"
            )
        )

        if old_warning:

            warning_count += 1

            note_parts.append(
                old_warning
            )

        result.append({

            "MaTuHSK":
                code,

            "MaTuHSKTrongSQL":
                standard[
                    "MaTuHSK"
                ],

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
                "; ".join(
                    note_parts
                ),
        })

    # ======================================================
    # 5. KIEM TRA SO LUONG CUOI
    # ======================================================

    print(
        "\n[5] KIEM TRA TONG HOP"
    )

    print(
        "Tai su dung:",
        reuse_count,
    )

    print(
        "INSERT moi:",
        insert_count,
    )

    print(
        "  Chua co ChuHan:",
        new_hanzi_count,
    )

    print(
        "  ChuHan co san, "
        "Pinyin moi:",
        new_reading_count,
    )

    print(
        "Muc co canh bao nguon:",
        warning_count,
    )

    if reuse_count != EXPECTED_REUSE:

        raise RuntimeError(
            "So tai su dung "
            "khac Buoc 05."
        )

    if insert_count != EXPECTED_INSERT:

        raise RuntimeError(
            "So INSERT "
            "khac Buoc 05."
        )

    if (
        new_hanzi_count
        != EXPECTED_NEW_HANZI
    ):

        raise RuntimeError(
            "So tu chua co ChuHan "
            "khac Buoc 04-05."
        )

    if (
        new_reading_count
        != EXPECTED_NEW_READING
    ):

        raise RuntimeError(
            "So cach doc moi "
            "khac Buoc 04-05."
        )

    if (
        reuse_count
        + insert_count
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Tong mapping khong bang 1000."
        )

    # ======================================================
    # 6. TAO HASH PREVIEW
    # ======================================================

    plan_hash = sha256_plan(
        result
    )

    summary = {

        "hsk_level":
            HSK_LEVEL,

        "total":
            len(result),

        "reuse":
            reuse_count,

        "insert":
            insert_count,

        "insert_new_hanzi":
            new_hanzi_count,

        "insert_new_reading":
            new_reading_count,

        "source_warning_rows":
            warning_count,

        "duplicate_source_groups":
            len(duplicate_groups),

        "source_file":
            str(SOURCE),

        "source_sha256":
            source_hash,

        "preview_plan_sha256":
            plan_hash,

        "sql_tuvung_count_at_preview":
            sql_vocab_total,

        "sql_hsk4_reference_count":
            hsk_total,
    }

    # ======================================================
    # 7. CHI SAU KHI PASS MOI GHI FILE PREVIEW
    # ======================================================

    write_csv(
        PREVIEW_CSV,
        result,
    )

    PREVIEW_JSON.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # 8. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 74
    )

    print(
        "PREVIEW IMPORT HSK4 THANH CONG"
    )

    print("=" * 74)

    print(
        "Tong mapping:",
        len(result),
    )

    print(
        "Tai su dung:",
        reuse_count,
    )

    print(
        "INSERT moi:",
        insert_count,
    )

    print(
        "  + ChuHan moi:",
        new_hanzi_count,
    )

    print(
        "  + Cach doc moi:",
        new_reading_count,
    )

    print(
        "Nhom trung nguon:",
        len(duplicate_groups),
    )

    print(
        "Muc co canh bao:",
        warning_count,
    )

    print(
        "\nSOURCE SHA256:"
    )

    print(
        source_hash
    )

    print(
        "\nPLAN SHA256:"
    )

    print(
        plan_hash
    )

    print(
        "\nPREVIEW CSV:"
    )

    print(
        " ",
        PREVIEW_CSV
    )

    print(
        "\nPREVIEW JSON:"
    )

    print(
        " ",
        PREVIEW_JSON
    )

    print(
        "\nKHONG CO DU LIEU NAO "
        "DUOC GHI VAO SQL."
    )

    print("=" * 74)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)