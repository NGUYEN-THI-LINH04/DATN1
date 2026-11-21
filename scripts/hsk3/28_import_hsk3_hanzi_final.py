
# -*- coding: utf-8 -*-
"""
BUOC 64 - IMPORT 300 CHU HAN HSK3 (BAN NHAP)

Nguon:
hanzi_hsk3_300_with_radicals.csv

PREVIEW:
python scripts/hsk3/28_import_hsk3_hanzi_final.py

COMMIT:
python scripts/hsk3/28_import_hsk3_hanzi_final.py --commit

An toan:
- 288 chu co MaBoThuSQL, 12 chu de NULL.
- Khong sua HSK1/HSK2.
- Khong UPDATE, DELETE.
- Khong INSERT trung KyTu.
- Transaction / rollback.
- Khong xuat ban.
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

SOURCE = DATA / "hanzi_hsk3_300_with_radicals.csv"
PREVIEW = DATA / "hsk3_hanzi_final_preview.json"
RESULT = DATA / "hanzi_hsk3_final_sql_result.csv"

COURSE_ID = 3
EXPECTED = 300


def clean(value):
    return str(value or "").strip()


def nullable_int(value):
    value = clean(value)
    return int(value) if value else None


def get_rows():
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    with SOURCE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        rows = list(reader)

    required = {
        "KyTu", "MaBaiHoc", "SoThuTuBai",
        "Pinyin", "NghiaTiengViet", "SoNet",
        "MaBoThuSQL", "TrangThaiGanBoThu",
    }

    if required - fields:
        raise ValueError(
            f"CSV thieu cot: {sorted(required - fields)}"
        )

    if len(rows) != EXPECTED:
        raise ValueError(
            f"Can 300 chu, hien co {len(rows)}"
        )

    chars = set()
    prepared = []

    for row in rows:
        char = clean(row["KyTu"])

        if len(char) != 1 or char in chars:
            raise ValueError(
                f"Ky tu sai hoac trung: {char}"
            )

        chars.add(char)

        for field in ("Pinyin", "NghiaTiengViet"):
            if not clean(row[field]):
                raise ValueError(
                    f"{char}: thieu {field}"
                )

        strokes = int(row["SoNet"])
        if not 1 <= strokes <= 64:
            raise ValueError(
                f"{char}: SoNet bat thuong"
            )

        radical_id = nullable_int(row["MaBoThuSQL"])
        radical_status = clean(
            row["TrangThaiGanBoThu"]
        )

        if radical_status == "KHOP_SQL":
            if radical_id is None:
                raise ValueError(
                    f"{char}: thieu MaBoThuSQL"
                )
        elif radical_status == "NHIEU_BO_THU_UNIHAN":
            if radical_id is not None:
                raise ValueError(
                    f"{char}: bo thu chua duoc xac minh"
                )
        else:
            raise ValueError(
                f"{char}: trang thai bo thu chua xu ly: "
                f"{radical_status}"
            )

        prepared.append({
            "KyTu": char,
            "MaBaiHoc": int(row["MaBaiHoc"]),
            "SoThuTuBai": int(row["SoThuTuBai"]),
            "Pinyin": clean(row["Pinyin"]),
            "NghiaTiengViet": clean(
                row["NghiaTiengViet"]
            ),
            "SoNet": strokes,
            "MaBoThu": radical_id,
            "TrangThai": "ban_nhap",
        })

    prepared.sort(
        key=lambda r: (r["SoThuTuBai"], r["KyTu"])
    )

    return prepared


def check_sql(cursor, rows):
    cursor.execute("""
        SELECT MaBaiHoc, SoThuTuBai, TrangThai
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = ?;
    """, COURSE_ID)

    lessons = {
        int(r[0]): (int(r[1]), clean(r[2]))
        for r in cursor.fetchall()
    }

    if len(lessons) != 20:
        raise RuntimeError(
            "Khong co dung 20 bai HSK3"
        )

    cursor.execute("""
        SELECT KyTu
        FROM dbo.ChuHan
        WHERE KyTu IS NOT NULL;
    """)

    existing = {
        clean(r[0]) for r in cursor.fetchall()
    }

    cursor.execute("""
        SELECT MaBoThu
        FROM dbo.BoThu;
    """)

    valid_radicals = {
        int(r[0]) for r in cursor.fetchall()
    }

    for row in rows:
        char = row["KyTu"]
        lesson = lessons.get(row["MaBaiHoc"])

        if lesson is None:
            raise RuntimeError(
                f"{char}: MaBaiHoc khong thuoc HSK3"
            )

        if lesson[0] != row["SoThuTuBai"]:
            raise RuntimeError(
                f"{char}: SoThuTuBai khong khop"
            )

        if lesson[1] != "ban_nhap":
            raise RuntimeError(
                f"{char}: bai hoc khong phai ban_nhap"
            )

        if char in existing:
            raise RuntimeError(
                f"{char}: da ton tai trong dbo.ChuHan"
            )

        if (
            row["MaBoThu"] is not None
            and row["MaBoThu"] not in valid_radicals
        ):
            raise RuntimeError(
                f"{char}: MaBoThu khong ton tai"
            )

    # Xac nhan cac cot bat buoc va mac dinh
    cursor.execute("""
        SELECT
            c.name,
            c.is_nullable,
            c.is_identity,
            c.is_computed,
            CASE WHEN c.default_object_id = 0
                 THEN 0 ELSE 1 END
        FROM sys.columns AS c
        WHERE c.object_id = OBJECT_ID(N'dbo.ChuHan');
    """)

    columns = {
        r[0]: {
            "nullable": bool(r[1]),
            "identity": bool(r[2]),
            "computed": bool(r[3]),
            "default": bool(r[4]),
        }
        for r in cursor.fetchall()
    }

    supplied = {
        "MaBaiHoc", "MaBoThu", "KyTu",
        "Pinyin", "NghiaTiengViet",
        "SoNet", "ThuTu", "TrangThai",
    }

    for name, info in columns.items():
        if name in supplied:
            continue

        if not any(info.values()):
            raise RuntimeError(
                f"Cot bat buoc chua duoc xu ly: {name}"
            )

    for name in supplied:
        if name not in columns:
            raise RuntimeError(
                f"Thieu cot ChuHan.{name}"
            )


def get_current_orders(cursor):
    cursor.execute("""
        SELECT MaBaiHoc, MAX(ThuTu)
        FROM dbo.ChuHan
        WHERE MaBaiHoc IN (
            SELECT MaBaiHoc
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
        )
        GROUP BY MaBaiHoc;
    """, COURSE_ID)

    return {
        int(r[0]): int(r[1] or 0)
        for r in cursor.fetchall()
    }


def make_plan(rows, start_orders):
    counts = Counter()
    plan = []

    for row in rows:
        item = dict(row)
        lesson_id = item["MaBaiHoc"]

        counts[lesson_id] += 1
        item["ThuTu"] = (
            start_orders.get(lesson_id, 0)
            + counts[lesson_id]
        )

        plan.append(item)

    return plan


def get_signature(plan):
    content = {
        "source_sha256": hashlib.sha256(
            SOURCE.read_bytes()
        ).hexdigest(),
        "plan": plan,
    }

    return hashlib.sha256(
        json.dumps(
            content,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def insert_rows(cursor, plan):
    inserted = []

    sql = """
        INSERT INTO dbo.ChuHan
        (
            MaBaiHoc,
            MaBoThu,
            KyTu,
            Pinyin,
            NghiaTiengViet,
            SoNet,
            ThuTu,
            TrangThai
        )
        OUTPUT INSERTED.MaChuHan
        VALUES (?, ?, ?, ?, ?, ?, ?, 'ban_nhap');
    """

    for row in plan:
        cursor.execute(
            sql,
            row["MaBaiHoc"],
            row["MaBoThu"],
            row["KyTu"],
            row["Pinyin"],
            row["NghiaTiengViet"],
            row["SoNet"],
            row["ThuTu"],
        )

        result = cursor.fetchone()
        if result is None:
            raise RuntimeError(
                f"Khong lay duoc ID: {row['KyTu']}"
            )

        inserted.append({
            "MaChuHan": int(result[0]),
            **row,
        })

    return inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--commit",
        action="store_true",
    )
    args = parser.parse_args()

    print("=" * 68)
    print("BUOC 64 - IMPORT CHU HAN HSK3")
    print("=" * 68)
    print(
        "CHE DO:",
        "COMMIT" if args.commit else "PREVIEW"
    )

    rows = get_rows()

    with closing(get_connection()) as conn:
        if getattr(conn, "autocommit", False):
            raise RuntimeError(
                "SQL autocommit=True, khong an toan"
            )

        with closing(conn.cursor()) as cursor:
            try:
                check_sql(cursor, rows)

                plan = make_plan(
                    rows,
                    get_current_orders(cursor),
                )

                count_radicals = sum(
                    row["MaBoThu"] is not None
                    for row in plan
                )

                if count_radicals != 288:
                    raise RuntimeError(
                        "So chu gan bo thu khong dung 288"
                    )

                signature = get_signature(plan)

                print("\nTONG HOP")
                print("Tong chu:", len(plan))
                print("Co MaBoThu:", count_radicals)
                print(
                    "MaBoThu NULL:",
                    len(plan) - count_radicals,
                )
                print(
                    "So bai duoc gan:",
                    len({r["MaBaiHoc"] for r in plan}),
                )
                print("Trang thai: ban_nhap")

                if not args.commit:
                    PREVIEW.write_text(
                        json.dumps(
                            {
                                "signature": signature,
                                "count": len(plan),
                            },
                            indent=2,
                        ),
                        encoding="utf-8",
                    )

                    conn.rollback()

                    print("\nPREVIEW THANH CONG")
                    print("CHUA GHI SQL")
                    return

                if not PREVIEW.is_file():
                    raise RuntimeError(
                        "Chua co PREVIEW"
                    )

                saved = json.loads(
                    PREVIEW.read_text(
                        encoding="utf-8"
                    )
                )

                if (
                    saved.get("signature") != signature
                    or saved.get("count") != 300
                ):
                    raise RuntimeError(
                        "Du lieu thay doi so voi PREVIEW"
                    )

                if RESULT.exists():
                    raise RuntimeError(
                        "File ket qua da ton tai"
                    )

                temp = RESULT.with_suffix(
                    ".pending.csv"
                )

                if temp.exists():
                    raise RuntimeError(
                        "File mapping tam da ton tai"
                    )

                inserted = insert_rows(cursor, plan)

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.ChuHan AS ch
                    INNER JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = ch.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                """, COURSE_ID)

                actual = int(cursor.fetchone()[0])

                if actual != 300:
                    raise RuntimeError(
                        f"SQL HSK3 co {actual} chu, "
                        "du kien 300"
                    )

                fields = [
                    "MaChuHan", "KyTu",
                    "MaBaiHoc", "SoThuTuBai",
                    "Pinyin", "NghiaTiengViet",
                    "SoNet", "MaBoThu",
                    "ThuTu", "TrangThai",
                ]

                with temp.open(
                    "x",
                    encoding="utf-8-sig",
                    newline="",
                ) as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=fields,
                        extrasaction="ignore",
                    )
                    writer.writeheader()
                    writer.writerows(inserted)

                try:
                    conn.commit()
                except Exception:
                    temp.unlink(missing_ok=True)
                    raise

                try:
                    temp.rename(RESULT)
                except OSError:
                    pass

                print("\nCOMMIT THANH CONG")
                print("Da INSERT:", len(inserted))
                print("Co MaBoThu:", count_radicals)
                print(
                    "MaBoThu NULL:",
                    len(inserted) - count_radicals,
                )
                print("Trang thai: ban_nhap")
                print("CHUA XUAT BAN")

            except Exception:
                conn.rollback()
                raise


if __name__ == "__main__":
    main()
