
# -*- coding: utf-8 -*-
"""
BUOC 36 - KIEM TRA DU LIEU HSK3 TRUOC KHI IMPORT

Du an: Moc Han
Database: HocTiengTrungDB

Chuc nang:
1. Kiem tra khoa hoc HSK3.
2. Kiem tra danh sach bai hoc HSK3.
3. Dem du lieu tu vung, ngu phap, chu Han.
4. Kiem tra cau truc SQL can thiet.

CHE DO: CHI DOC - KHONG GHI SQL.
"""

import sys
import json
from pathlib import Path
from contextlib import closing

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

HSK_LEVEL = 3

OUTPUT_DIR = (
    ROOT / "scripts" / "hsk3" / "data" / "processed"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "hsk3_database_check.json"


def fetch_dicts(cursor):
    columns = [item[0] for item in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_columns(cursor, table_name):
    cursor.execute(
        """
        SELECT
            COLUMN_NAME,
            DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION;
        """,
        table_name,
    )
    return fetch_dicts(cursor)


def get_table_names(cursor):
    cursor.execute(
        """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_TYPE = 'BASE TABLE';
        """
    )
    return {row[0] for row in cursor.fetchall()}


def count_by_lesson(cursor, table_name, lesson_id):
    allowed = {"TuVung", "NguPhap", "ChuHan"}

    if table_name not in allowed:
        return None

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM dbo.{table_name}
        WHERE MaBaiHoc = ?;
        """,
        lesson_id,
    )
    return int(cursor.fetchone()[0])


def main():
    print("=" * 70)
    print("BUOC 36 - KIEM TRA DU LIEU HSK3")
    print("=" * 70)
    print("CHE DO: CHI DOC - KHONG GHI SQL")

    report = {
        "HSK": HSK_LEVEL,
        "courses": [],
        "lessons": [],
        "schema": {},
    }

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:

            tables = get_table_names(cursor)

            # 1. Kiem tra cau truc cac bang quan trong.
            needed_tables = [
                "CapDoHSK",
                "KhoaHoc",
                "BaiHoc",
                "TuVung",
                "TuVungBaiHoc",
                "NguPhap",
                "ChuHan",
                "ChuHanBaiHoc",
            ]

            print("\n[1] CAC BANG SQL")

            for table in needed_tables:
                if table in tables:
                    cols = get_columns(cursor, table)
                    report["schema"][table] = cols
                    print(
                        f"  OK  {table}: {len(cols)} cot"
                    )
                else:
                    report["schema"][table] = []
                    print(f"  --  Khong co bang {table}")

            # 2. Tim khoa hoc HSK3.
            print("\n[2] KHOA HOC HSK3")

            cursor.execute(
                """
                SELECT
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.TieuDe,
                    kh.TrangThai
                FROM dbo.KhoaHoc AS kh
                WHERE kh.MaCapDo = ?
                ORDER BY kh.MaKhoaHoc;
                """,
                HSK_LEVEL,
            )

            courses = fetch_dicts(cursor)
            report["courses"] = courses

            if not courses:
                print("  Chua co khoa hoc HSK3 trong SQL.")
            else:
                for course in courses:
                    print(
                        f"  MaKhoaHoc={course['MaKhoaHoc']}"
                        f" | {course['TieuDe']}"
                        f" | TrangThai={course['TrangThai']}"
                    )

            # 3. Tim bai hoc thuoc HSK3.
            print("\n[3] DANH SACH BAI HOC HSK3")

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    bh.TrangThai
                FROM dbo.BaiHoc AS bh
                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc
                WHERE kh.MaCapDo = ?
                ORDER BY
                    kh.MaKhoaHoc,
                    bh.SoThuTuBai,
                    bh.MaBaiHoc;
                """,
                HSK_LEVEL,
            )

            lessons = fetch_dicts(cursor)
            report["lessons"] = lessons

            if not lessons:
                print("  Chua co bai hoc HSK3.")
            else:
                for lesson in lessons:
                    print(
                        f"  Bai {lesson['SoThuTuBai']:02}"
                        f" | MaBaiHoc={lesson['MaBaiHoc']}"
                        f" | {lesson['TieuDe']}"
                    )

            # 4. Thong tin tong quan.
            print("\n[4] TONG KET")

            print("  So khoa hoc HSK3:", len(courses))
            print("  So bai hoc HSK3:", len(lessons))

    OUTPUT_FILE.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("\nDa luu bao cao:", OUTPUT_FILE)
    print("\nHOAN THANH - KHONG THAY DOI SQL")


if __name__ == "__main__":
    main()
