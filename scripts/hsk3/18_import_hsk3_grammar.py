
# -*- coding: utf-8 -*-
"""
BUOC 54 - IMPORT NGU PHAP HSK3 VAO SQL SERVER

Nguon:
scripts/hsk3/data/processed/grammar_hsk3_by_lesson_draft.csv

PREVIEW:
python scripts/hsk3/18_import_hsk3_grammar.py

COMMIT:
python scripts/hsk3/18_import_hsk3_grammar.py --commit

- Chi them ngu phap cho khoa hoc HSK3.
- Giu nguyen noi dung tu file CSV.
- Khong sua/xoa du lieu HSK1, HSK2.
- Khong INSERT trung.
- Trang thai luon la ban_nhap.
- Khong tu dong xuat ban.
"""

import argparse
import csv
import hashlib
import json
import sys

from collections import Counter
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "grammar_hsk3_by_lesson_draft.csv"
PREVIEW = DATA / "hsk3_grammar_import_preview.json"
RESULT = DATA / "grammar_hsk3_sql_result.csv"

COURSE_ID = 3
EXPECTED = 20

TEXT_FIELDS = [
    "TenCauTruc",
    "MoTa",
    "CachDung",
    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",
]

RESULT_FIELDS = [
    "MaNguPhap",
    "MaNguPhapTam",
    "MaBaiHoc",
    "SoThuTuBai",
    "ThuTu",
    *TEXT_FIELDS,
    "TrangThai",
]


def clean(value):
    return str(value or "").strip()


def sha256_file(path):
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def read_grammar():
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required = {
            "MaNguPhapTam",
            "MaBaiHoc",
            "SoThuTuBai",
            "ThuTu",
            *TEXT_FIELDS,
        }

        missing = required - set(reader.fieldnames or [])

        if missing:
            raise ValueError(
                f"CSV thieu cot: {sorted(missing)}"
            )

        rows = list(reader)

    if len(rows) != EXPECTED:
        raise ValueError(
            f"Can 20 cau truc, tim thay {len(rows)}."
        )

    codes = set()
    positions = set()
    result = []

    for row in rows:
        code = clean(row["MaNguPhapTam"])

        if not code or code in codes:
            raise ValueError(
                f"Ma ngu phap trung/rong: {code}"
            )

        codes.add(code)

        lesson_id = int(row["MaBaiHoc"])
        lesson_number = int(row["SoThuTuBai"])
        order = int(row["ThuTu"])

        if not 1 <= lesson_number <= 20:
            raise ValueError(
                f"{code}: so bai khong hop le."
            )

        if order < 1:
            raise ValueError(
                f"{code}: ThuTu phai lon hon 0."
            )

        position = (lesson_id, order)

        if position in positions:
            raise ValueError(
                f"{code}: trung ThuTu trong bai."
            )

        positions.add(position)

        item = {
            "MaNguPhapTam": code,
            "MaBaiHoc": lesson_id,
            "SoThuTuBai": lesson_number,
            "ThuTu": order,
            "TrangThai": "ban_nhap",
        }

        for name in TEXT_FIELDS:
            item[name] = clean(row.get(name))

        if not item["TenCauTruc"]:
            raise ValueError(
                f"{code}: thieu TenCauTruc."
            )

        if any(
            not item[name]
            for name in (
                "CachDung",
                "ViDuTiengTrung",
                "ViDuPinyin",
                "ViDuTiengViet",
            )
        ):
            raise ValueError(
                f"{code}: thieu cach dung hoac vi du."
            )

        if len(item["TenCauTruc"]) > 300:
            raise ValueError(
                f"{code}: TenCauTruc qua 300 ky tu."
            )

        for name in (
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
        ):
            if len(item[name]) > 1000:
                raise ValueError(
                    f"{code}: {name} qua 1000 ky tu."
                )

        result.append(item)

    result.sort(
        key=lambda x: (
            x["SoThuTuBai"],
            x["ThuTu"],
        )
    )

    return result


def get_plan_signature(rows):
    payload = {
        "file_sha256": sha256_file(SOURCE),
        "course_id": COURSE_ID,
        "grammar": rows,
    }

    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def check_sql(cursor, rows):
    # Lay bai hoc HSK3 truc tiep tu SQL.
    cursor.execute("""
        SELECT
            MaBaiHoc,
            SoThuTuBai,
            TrangThai
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = ?;
    """, COURSE_ID)

    lessons = {
        int(r[0]): {
            "number": int(r[1]),
            "status": str(r[2]),
        }
        for r in cursor.fetchall()
    }

    if len(lessons) != 20:
        raise RuntimeError(
            "SQL khong co dung 20 bai HSK3."
        )

    for row in rows:
        info = lessons.get(row["MaBaiHoc"])

        if info is None:
            raise RuntimeError(
                f"MaBaiHoc={row['MaBaiHoc']} "
                "khong thuoc HSK3."
            )

        if info["number"] != row["SoThuTuBai"]:
            raise RuntimeError(
                f"{row['MaNguPhapTam']}: "
                "so bai khong khop SQL."
            )

        if info["status"] != "ban_nhap":
            raise RuntimeError(
                "Co bai HSK3 khong con o trang thai nhap."
            )

    # Khong cho import lap hoac ghi de ngu phap da co.
    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.NguPhap AS np
        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = np.MaBaiHoc
        WHERE bh.MaKhoaHoc = ?;
    """, COURSE_ID)

    existing = int(cursor.fetchone()[0])

    if existing != 0:
        raise RuntimeError(
            f"HSK3 da co {existing} ngu phap. "
            "Dung lai, khong import lap."
        )


def insert_grammar(cursor, row):
    cursor.execute("""
        INSERT INTO dbo.NguPhap
        (
            MaBaiHoc,
            TenCauTruc,
            MoTa,
            CachDung,
            ViDuTiengTrung,
            ViDuPinyin,
            ViDuTiengViet,
            MaTep,
            MaNguon,
            ThuTu,
            TrangThai,
            MaQuanTriVienCapNhat,
            NgayCapNhat
        )
        OUTPUT INSERTED.MaNguPhap
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?,
            NULL, NULL, ?,
            'ban_nhap',
            NULL,
            NULL
        );
    """,
        row["MaBaiHoc"],
        row["TenCauTruc"],
        row["MoTa"] or None,
        row["CachDung"] or None,
        row["ViDuTiengTrung"],
        row["ViDuPinyin"],
        row["ViDuTiengViet"],
        row["ThuTu"],
    )

    result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            "Khong nhan duoc MaNguPhap."
        )

    return int(result[0])


def write_csv(path, rows):
    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=RESULT_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--commit",
        action="store_true",
    )

    args = parser.parse_args()

    print("=" * 68)
    print("BUOC 54 - IMPORT NGU PHAP HSK3")
    print("=" * 68)

    print(
        "CHE DO:",
        "COMMIT" if args.commit else "PREVIEW"
    )

    rows = read_grammar()
    signature = get_plan_signature(rows)

    counts = Counter(
        row["SoThuTuBai"] for row in rows
    )

    with closing(get_connection()) as conn:
        if getattr(conn, "autocommit", False):
            raise RuntimeError(
                "Ket noi dang autocommit=True."
            )

        with closing(conn.cursor()) as cursor:
            try:
                check_sql(cursor, rows)

                print("\nTONG HOP")
                print("Tong cau truc:", len(rows))
                print("Bai co ngu phap:", len(counts))
                print("Bai chua co:", 20 - len(counts))

                for number in range(1, 21):
                    print(
                        f"Bai {number:02d}: "
                        f"{counts[number]} cau truc"
                    )

                if not args.commit:
                    PREVIEW.write_text(
                        json.dumps(
                            {
                                "signature": signature,
                                "count": len(rows),
                            },
                            indent=2,
                        ),
                        encoding="utf-8",
                    )

                    conn.rollback()

                    print("\nPREVIEW THANH CONG")
                    print("CHUA GHI SQL")
                    print("File:", PREVIEW)
                    return

                # Xac minh du lieu trung voi PREVIEW.
                if not PREVIEW.exists():
                    raise RuntimeError(
                        "Chua co PREVIEW buoc 54."
                    )

                saved = json.loads(
                    PREVIEW.read_text(
                        encoding="utf-8"
                    )
                )

                if (
                    saved.get("signature") != signature
                    or saved.get("count") != len(rows)
                ):
                    raise RuntimeError(
                        "Du lieu da thay doi. "
                        "Hay chay PREVIEW lai."
                    )

                if RESULT.exists():
                    raise RuntimeError(
                        "Da co file ket qua import."
                    )

                temp = RESULT.with_suffix(
                    ".pending.csv"
                )

                if temp.exists():
                    raise RuntimeError(
                        "Da co file mapping tam."
                    )

                inserted = []

                for row in rows:
                    new_id = insert_grammar(cursor, row)

                    inserted.append({
                        "MaNguPhap": new_id,
                        **row,
                    })

                # Xac minh so luong trong transaction.
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc = bh.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                """, COURSE_ID)

                actual = int(cursor.fetchone()[0])

                if actual != EXPECTED:
                    raise RuntimeError(
                        f"SQL co {actual} cau truc, "
                        f"du kien {EXPECTED}."
                    )

                write_csv(temp, inserted)

                try:
                    conn.commit()
                except Exception:
                    temp.unlink(missing_ok=True)
                    raise

                try:
                    temp.rename(RESULT)
                    result_path = RESULT
                except OSError:
                    result_path = temp

                print("\n" + "=" * 68)
                print("COMMIT THANH CONG!")
                print("=" * 68)
                print("Da INSERT:", actual)
                print("Trang thai: ban_nhap")
                print("Mapping:", result_path)
                print("KHONG SUA HSK1/HSK2")

            except Exception:
                conn.rollback()
                raise


if __name__ == "__main__":
    main()
