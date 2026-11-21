
# -*- coding: utf-8 -*-
"""
BUOC 43 - IMPORT TU VUNG HSK3 (BAN SUA)

- Bao toan 973 ma nguon HSK3.
- Kiem tra trung trong CSV va SQL.
- Tai su dung tu vung da co neu phu hop.
- Phan biet tu khac Pinyin, tu loai, nghia.
- Khong INSERT trung trong cung mot lan chay.
- Tu moi co DaDuyet = 0.
- PREVIEW truoc, COMMIT sau.
- Khong sua/xoa du lieu HSK1-HSK2.
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "vocabulary_hsk3_import_draft.csv"
PREVIEW = DATA / "hsk3_import_all_preview.json"
MAPPING = DATA / "vocabulary_hsk3_import_result.csv"

EXPECTED = 973

FIELDS = [
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


def clean(value):
    return re.sub(
        r"\s+", " ", str(value or "")
    ).strip()


def pinyin_key(value):
    return unicodedata.normalize(
        "NFC", clean(value).casefold()
    ).replace(" ", "").replace("'", "")


def word_key(hanzi, pinyin):
    return clean(hanzi), pinyin_key(pinyin)


def full_key(hanzi, pinyin, word_type, meaning):
    return (
        clean(hanzi),
        pinyin_key(pinyin),
        clean(word_type).casefold(),
        clean(meaning).casefold(),
    )


def source_hash():
    return hashlib.sha256(
        SOURCE.read_bytes()
    ).hexdigest()


def read_source():
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    with SOURCE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)

        required = {
            "MaTuHSK",
            "ChuHan",
            "PhienAm",
            "TuLoai",
            "NghiaTiengViet",
        }

        missing = required - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                f"File CSV thieu cot: {sorted(missing)}"
            )

        rows = list(reader)

    if len(rows) != EXPECTED:
        raise ValueError(
            f"Can {EXPECTED} muc, co {len(rows)} muc."
        )

    codes = set()

    for row in rows:
        code = clean(row["MaTuHSK"])

        if not re.fullmatch(r"L3-\d{4}", code):
            raise ValueError(f"Ma khong hop le: {code}")

        if code in codes:
            raise ValueError(f"Trung ma nguon: {code}")

        codes.add(code)

        hanzi = clean(row["ChuHan"])
        pinyin = clean(row["PhienAm"])
        meaning = clean(row["NghiaTiengViet"])
        word_type = clean(row["TuLoai"])

        if not hanzi or not pinyin or not meaning:
            raise ValueError(
                f"{code}: thieu ChuHan/Pinyin/Nghia"
            )

        if (
            len(hanzi) > 100
            or len(pinyin) > 200
            or len(meaning) > 2000
            or len(word_type) > 100
        ):
            raise ValueError(
                f"{code}: du lieu qua dai"
            )

    return rows


def load_hsk(cursor):
    cursor.execute("""
        SELECT
            MaTuHSK,
            MaMucNoiBo,
            MaCapDo,
            ChuHan,
            PhienAm
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = 3;
    """)

    index = defaultdict(list)

    for row in cursor.fetchall():
        index[clean(row[1])].append({
            "id": int(row[0]),
            "level": int(row[2]),
            "hanzi": clean(row[3]),
            "pinyin": clean(row[4]),
        })

    return index


def load_vocabulary(cursor):
    cursor.execute("""
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai
        FROM dbo.TuVung
        ORDER BY MaTuVung;
    """)

    index = defaultdict(list)

    for row in cursor.fetchall():
        item = {
            "id": int(row[0]),
            "hanzi": clean(row[1]),
            "pinyin": clean(row[2]),
            "meaning": clean(row[3]),
            "type": clean(row[4]),
        }

        index[word_key(
            item["hanzi"],
            item["pinyin"],
        )].append(item)

    return index


def validate_sql_schema(cursor):
    """
    Kiem tra cac cot ma script se su dung.
    Dung truoc khi bat dau INSERT.
    """
    cursor.execute("""
        SELECT
            COLUMN_NAME,
            IS_NULLABLE,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = 'TuVung';
    """)

    columns = {
        clean(r[0]): {
            "nullable": clean(r[1]),
            "type": clean(r[2]),
            "max_length": r[3],
            "default": r[4],
        }
        for r in cursor.fetchall()
    }

    required = {
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "NghiaTiengViet",
        "TuLoai",
        "DaDuyet",
    }

    missing = required - set(columns)

    if missing:
        raise RuntimeError(
            f"Bang TuVung thieu cot: {sorted(missing)}"
        )

    limits = {
        "ChuHan": 100,
        "PhienAm": 200,
        "NghiaTiengViet": 2000,
        "TuLoai": 100,
    }

    for name, required_length in limits.items():
        actual = columns[name]["max_length"]

        if actual is not None and actual != -1:
            if actual < required_length:
                raise RuntimeError(
                    f"Cot {name} chi dai {actual}, "
                    f"nhung code cho phep {required_length}."
                )

    # Cac cot khac phai cho phep NULL
    # hoac co DEFAULT; neu khong thi script
    # INSERT se khong du du lieu.
    supplied = {
        "ChuHan",
        "PhienAm",
        "NghiaTiengViet",
        "TuLoai",
        "DaDuyet",
    }

    exempt = {"MaTuVung"}

    unsupported = []

    for name, spec in columns.items():
        if name in supplied or name in exempt:
            continue

        if (
            spec["nullable"] == "NO"
            and spec["default"] is None
        ):
            unsupported.append(name)

    if unsupported:
        raise RuntimeError(
            "Can xem lai cot bat buoc trong TuVung: "
            + ", ".join(unsupported)
        )

    return columns


def select_existing(matches, row, source_types):
    """
    Chi tai su dung khi phu hop.
    Uu tien so sanh day du tu loai + nghia.

    Neu SQL chi co 1 tu cung ChuHan/Pinyin
    va nhom nguon khong co su khac biet
    ve tu loai/nghia, giu cach tai su dung
    da ap dung cho HSK2.
    """
    if not matches:
        return None

    word_type = clean(row["TuLoai"])
    meaning = clean(row["NghiaTiengViet"])

    exact = [
        x for x in matches
        if clean(x["type"]).casefold()
            == word_type.casefold()
        and clean(x["meaning"]).casefold()
            == meaning.casefold()
    ]

    if len(exact) == 1:
        return exact[0]

    if len(exact) > 1:
        raise RuntimeError(
            f"{row['MaTuHSK']}: nhieu ban ghi SQL "
            "trung ca ChuHan/Pinyin/TuLoai/Nghia."
        )

    same_type = [
        x for x in matches
        if clean(x["type"]).casefold()
            == word_type.casefold()
    ]

    if len(same_type) == 1 and len(source_types) == 1:
        return same_type[0]

    if len(matches) == 1 and len(source_types) == 1:
        return matches[0]

    return None


def prepare(rows, hsk_index, vocab_index):
    if len(hsk_index) != EXPECTED:
        raise RuntimeError(
            f"SQL phai co {EXPECTED} ma HSK3, "
            f"hien co {len(hsk_index)}."
        )

    source_groups = defaultdict(list)

    for row in rows:
        source_groups[word_key(
            row["ChuHan"], row["PhienAm"]
        )].append(row)

    # Nhom cac muc moi thuc su duy nhat.
    planned_new = {}

    plan = []
    counts = Counter()

    for row in rows:
        code = clean(row["MaTuHSK"])
        hanzi = clean(row["ChuHan"])
        pinyin = clean(row["PhienAm"])
        meaning = clean(row["NghiaTiengViet"])
        word_type = clean(row["TuLoai"])

        standards = hsk_index.get(code, [])

        if len(standards) != 1:
            raise RuntimeError(
                f"{code}: khong co dung 1 ma HSK."
            )

        standard = standards[0]

        if (
            standard["hanzi"] != hanzi
            or pinyin_key(standard["pinyin"])
               != pinyin_key(pinyin)
        ):
            raise RuntimeError(
                f"{code}: khac du lieu TuVungHSKChuan."
            )

        basic = word_key(hanzi, pinyin)

        source_types = {
            (
                clean(x["TuLoai"]).casefold(),
                clean(x["NghiaTiengViet"]).casefold(),
            )
            for x in source_groups[basic]
        }

        matches = vocab_index.get(basic, [])

        existing = select_existing(
            matches, row, source_types
        )

        new_key = full_key(
            hanzi, pinyin, word_type, meaning
        )

        if existing:
            action = "TAI_SU_DUNG"
            vocab_id = existing["id"]
            group_id = ""

        elif new_key in planned_new:
            action = "DUNG_CHUNG_TU_MOI"
            vocab_id = None
            group_id = planned_new[new_key]

        else:
            action = "INSERT_MOI"
            vocab_id = None
            group_id = code
            planned_new[new_key] = code

        plan.append({
            "MaMucNoiBo": code,
            "MaTuHSK": standard["id"],
            "MaTuVung": vocab_id,
            "ChuHan": hanzi,
            "PhienAm": pinyin,
            "TuLoai": word_type,
            "NghiaTiengViet": meaning,
            "HanhDong": action,
            "NhomTuMoi": group_id,
            "TrangThaiKiemDuyet": clean(
                row.get("TrangThaiKiemDuyet")
            ),
            "VanDeCanKiemTra": clean(
                row.get("VanDeCanKiemTra")
            ),
        })

        counts[action] += 1

    if len(plan) != EXPECTED:
        raise RuntimeError(
            "Ke hoach import khong du 973 muc."
        )

    return plan, counts


def insert_one(cursor, row):
    """
    Giu dung kieu INSERT da dung trong HSK2.
    Chi dua cac cot can thiet vao SQL.
    """
    cursor.execute("""
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
        row["TuLoai"] or None,
    )

    inserted = cursor.fetchone()

    if inserted is None:
        raise RuntimeError(
            "Khong lay duoc MaTuVung sau INSERT."
        )

    return int(inserted[0])


def write_mapping(path, plan):
    with path.open(
        "x", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(plan)


def preview_data(digest, plan, counts):
    return {
        "source_sha256": digest,
        "total": len(plan),
        "reuse": counts["TAI_SU_DUNG"],
        "insert": counts["INSERT_MOI"],
        "shared": counts["DUNG_CHUNG_TU_MOI"],
        "plan_sha256": hashlib.sha256(
            json.dumps(
                plan,
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--commit",
        action="store_true",
    )

    args = parser.parse_args()

    print("=" * 68)
    print("BUOC 43 - IMPORT TU VUNG HSK3 (BAN SUA)")
    print("=" * 68)

    print(
        "CHE DO:",
        "COMMIT" if args.commit else "PREVIEW"
    )

    source_rows = read_source()
    digest = source_hash()

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:

            # Bat dau transaction co chu dich.
            # Khong dung autocommit cho COMMIT.
            if getattr(conn, "autocommit", False):
                raise RuntimeError(
                    "Ket noi dang autocommit=True. "
                    "Dung lai de bao ve giao dich."
                )

            try:
                validate_sql_schema(cursor)

                hsk_index = load_hsk(cursor)
                vocab_index = load_vocabulary(cursor)

                plan, counts = prepare(
                    source_rows,
                    hsk_index,
                    vocab_index,
                )

                summary = preview_data(
                    digest, plan, counts
                )

                print("\nTONG HOP")
                print("Tong muc HSK3:", len(plan))
                print(
                    "Tai su dung SQL:",
                    counts["TAI_SU_DUNG"]
                )
                print(
                    "INSERT moi du kien:",
                    counts["INSERT_MOI"]
                )
                print(
                    "Dung chung tu moi:",
                    counts["DUNG_CHUNG_TU_MOI"]
                )
                print(
                    "Tong mapping:",
                    sum(counts.values())
                )

                warnings = sum(
                    bool(x["VanDeCanKiemTra"])
                    for x in plan
                )

                print(
                    "Muc co canh bao nguon:",
                    warnings
                )

                if not args.commit:
                    PREVIEW.write_text(
                        json.dumps(
                            summary,
                            ensure_ascii=False,
                            indent=2,
                        ),
                        encoding="utf-8",
                    )

                    conn.rollback()

                    print("\nPREVIEW THANH CONG")
                    print("Da luu:", PREVIEW)
                    print("CHUA GHI SQL")
                    return

                if not PREVIEW.is_file():
                    raise RuntimeError(
                        "Chua co PREVIEW."
                    )

                old = json.loads(
                    PREVIEW.read_text(
                        encoding="utf-8"
                    )
                )

                if old != summary:
                    raise RuntimeError(
                        "Du lieu khac PREVIEW. "
                        "Hay chay PREVIEW lai."
                    )

                if MAPPING.exists():
                    raise RuntimeError(
                        "Da co file mapping ket qua. "
                        "Khong import lap."
                    )

                id_by_group = {}
                inserted = 0

                for item in plan:
                    if item["HanhDong"] != "INSERT_MOI":
                        continue

                    new_id = insert_one(cursor, item)

                    item["MaTuVung"] = new_id

                    id_by_group[
                        item["NhomTuMoi"]
                    ] = new_id

                    inserted += 1

                    if inserted % 100 == 0:
                        print(
                            f"Da INSERT {inserted}/"
                            f"{counts['INSERT_MOI']}"
                        )

                # Gan ma moi cho cac muc dung chung.
                for item in plan:
                    if item["HanhDong"] == "DUNG_CHUNG_TU_MOI":
                        item["MaTuVung"] = id_by_group[
                            item["NhomTuMoi"]
                        ]

                if any(
                    item["MaTuVung"] is None
                    for item in plan
                ):
                    raise RuntimeError(
                        "Con muc chua co MaTuVung."
                    )

                if inserted != counts["INSERT_MOI"]:
                    raise RuntimeError(
                        "So INSERT khong khop PREVIEW."
                    )

                if len({
                    x["MaMucNoiBo"] for x in plan
                }) != EXPECTED:
                    raise RuntimeError(
                        "Mapping thieu ma HSK3."
                    )

                # Xuat mapping vao file tam.
                temp_mapping = MAPPING.with_suffix(
                    ".pending.csv"
                )

                if temp_mapping.exists():
                    raise RuntimeError(
                        "Da ton tai file mapping tam. "
                        "Can kiem tra truoc khi chay."
                    )

                write_mapping(temp_mapping, plan)

                try:
                    conn.commit()
                except Exception:
                    temp_mapping.unlink(missing_ok=True)
                    raise

                # SQL da commit; doi ten file ket qua.
                temp_mapping.rename(MAPPING)

                print("\n" + "=" * 68)
                print("IMPORT HSK3 THANH CONG")
                print("=" * 68)

                print("Tong muc mapping:", len(plan))
                print("Da INSERT:", inserted)
                print(
                    "Tai su dung:",
                    counts["TAI_SU_DUNG"]
                )
                print(
                    "Dung chung:",
                    counts["DUNG_CHUNG_TU_MOI"]
                )

                print("Mapping:", MAPPING)
                print("Tu moi: DaDuyet = 0")

            except Exception:
                conn.rollback()
                raise


if __name__ == "__main__":
    main()
