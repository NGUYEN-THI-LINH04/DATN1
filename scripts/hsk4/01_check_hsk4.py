# -*- coding: utf-8 -*-
"""
BUOC 01 - KIEM TRA DU LIEU NEN HSK4

Du an: Moc Han
Database: HocTiengTrungDB

Muc dich:
1. Kiem tra khoa hoc HSK4.
2. Kiem tra BaiHoc HSK4 hien tai.
3. Kiem tra 1000 muc TuVungHSKChuan cap 4.
4. Kiem tra cac truong quan trong cua nguon HSK4.
5. Kiem tra cac bang SQL can cho pipeline HSK4.
6. Tao bao cao JSON de luu vet.

CHE DO:
- CHI DOC SQL.
- KHONG INSERT.
- KHONG UPDATE.
- KHONG DELETE.
"""

import json
import sys
from contextlib import closing
from pathlib import Path


# ==========================================================
# 1. DUONG DAN DU AN
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT))

from database import get_connection


HSK_LEVEL = 4
EXPECTED_VOCAB = 1000

OUTPUT_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "hsk4_database_check.json"
)


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def fetch_dicts(cursor):
    columns = [
        item[0]
        for item in cursor.description
    ]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_tables(cursor):
    cursor.execute(
        """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME;
        """
    )

    return {
        row[0]
        for row in cursor.fetchall()
    }


def get_columns(cursor, table_name):
    cursor.execute(
        """
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION;
        """,
        table_name,
    )

    return fetch_dicts(cursor)


# ==========================================================
# 3. MAIN
# ==========================================================

def main():

    print("=" * 70)
    print("BUOC 01 - KIEM TRA DU LIEU NEN HSK4")
    print("=" * 70)

    print(
        "CHE DO: CHI DOC SQL - "
        "KHONG INSERT / UPDATE / DELETE"
    )

    report = {
        "HSK": HSK_LEVEL,
        "expected_vocabulary": EXPECTED_VOCAB,
        "course": [],
        "lessons": [],
        "vocabulary_reference": {},
        "schema": {},
    }

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            # ==================================================
            # 1. KIEM TRA CAC BANG CAN THIET
            # ==================================================

            print("\n[1] KIEM TRA CAC BANG SQL")

            tables = get_tables(cursor)

            required_tables = [
                "CapDoHSK",
                "KhoaHoc",
                "BaiHoc",
                "TuVung",
                "TuVungBaiHoc",
                "TuVungHSKChuan",
                "TuVungHSKMucTuDien",
                "NguPhap",
                "ChuHan",
                "BaiTap",
                "CauHoi",
                "LuaChonCauHoi",
            ]

            for table in required_tables:

                if table in tables:

                    columns = get_columns(
                        cursor,
                        table,
                    )

                    report[
                        "schema"
                    ][table] = columns

                    print(
                        f"  OK  {table}: "
                        f"{len(columns)} cot"
                    )

                else:

                    report[
                        "schema"
                    ][table] = []

                    print(
                        f"  THIEU BANG: {table}"
                    )

            # ==================================================
            # 2. KIEM TRA KHOA HOC HSK4
            # ==================================================

            print("\n[2] KIEM TRA KHOA HOC HSK4")

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

            report["course"] = courses

            if not courses:

                print(
                    "  LOI: Chua co khoa hoc HSK4."
                )

            else:

                for course in courses:

                    print(
                        f"  MaKhoaHoc="
                        f"{course['MaKhoaHoc']}"
                        f" | {course['TieuDe']}"
                        f" | TrangThai="
                        f"{course['TrangThai']}"
                    )

            # ==================================================
            # 3. KIEM TRA BAI HOC HSK4
            # ==================================================

            print("\n[3] KIEM TRA BAI HOC HSK4")

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
                    ON kh.MaKhoaHoc =
                       bh.MaKhoaHoc
                WHERE kh.MaCapDo = ?
                ORDER BY
                    bh.SoThuTuBai,
                    bh.MaBaiHoc;
                """,
                HSK_LEVEL,
            )

            lessons = fetch_dicts(cursor)

            report["lessons"] = lessons

            print(
                "  So bai hoc HSK4 hien tai:",
                len(lessons),
            )

            if not lessons:

                print(
                    "  OK hien trang: "
                    "HSK4 chua tao BaiHoc."
                )

            else:

                for lesson in lessons:

                    print(
                        f"  Bai "
                        f"{lesson['SoThuTuBai']}"
                        f" | MaBaiHoc="
                        f"{lesson['MaBaiHoc']}"
                        f" | {lesson['TieuDe']}"
                    )

            # ==================================================
            # 4. KIEM TRA 1000 TU HSK4 CHUAN
            # ==================================================

            print(
                "\n[4] KIEM TRA TU VUNG HSK4 CHUAN"
            )

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongSo,
                    COUNT(
                        DISTINCT MaMucNoiBo
                    ) AS SoMaMucNoiBoKhacNhau,

                    SUM(
                        CASE
                            WHEN ChuHan IS NULL
                              OR LTRIM(RTRIM(ChuHan)) = ''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuChuHan,

                    SUM(
                        CASE
                            WHEN PhienAm IS NULL
                              OR LTRIM(RTRIM(PhienAm)) = ''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuPhienAm,

                    SUM(
                        CASE
                            WHEN NghiaTiengVietThamChieu
                                 IS NULL
                              OR LTRIM(
                                    RTRIM(
                                        NghiaTiengVietThamChieu
                                    )
                                 ) = ''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuNghiaTiengViet,

                    SUM(
                        CASE
                            WHEN TuLoai IS NULL
                              OR LTRIM(RTRIM(TuLoai)) = ''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuTuLoai

                FROM dbo.TuVungHSKChuan
                WHERE MaCapDo = ?;
                """,
                HSK_LEVEL,
            )

            source_check = fetch_dicts(
                cursor
            )[0]

            report[
                "vocabulary_reference"
            ] = source_check

            print(
                "  Tong muc HSK4:",
                source_check["TongSo"],
            )

            print(
                "  MaMucNoiBo khac nhau:",
                source_check[
                    "SoMaMucNoiBoKhacNhau"
                ],
            )

            print(
                "  Thieu ChuHan:",
                source_check[
                    "ThieuChuHan"
                ],
            )

            print(
                "  Thieu PhienAm:",
                source_check[
                    "ThieuPhienAm"
                ],
            )

            print(
                "  Thieu nghia Viet:",
                source_check[
                    "ThieuNghiaTiengViet"
                ],
            )

            print(
                "  Thieu TuLoai:",
                source_check[
                    "ThieuTuLoai"
                ],
            )

            # ==================================================
            # 5. KIEM TRA SO LUONG BAT BUOC
            # ==================================================

            print(
                "\n[5] DOI CHIEU SO LUONG HSK4"
            )

            total = int(
                source_check["TongSo"]
            )

            unique_ids = int(
                source_check[
                    "SoMaMucNoiBoKhacNhau"
                ]
            )

            if total != EXPECTED_VOCAB:

                raise RuntimeError(
                    "HSK4 khong du "
                    f"{EXPECTED_VOCAB} muc. "
                    f"SQL hien co {total}."
                )

            if unique_ids != EXPECTED_VOCAB:

                raise RuntimeError(
                    "MaMucNoiBo HSK4 "
                    "bi trung hoac thieu. "
                    f"Chi co {unique_ids} "
                    "ma khac nhau."
                )

            print(
                "  PASS: HSK4 co dung "
                f"{EXPECTED_VOCAB} muc."
            )

            print(
                "  PASS: "
                f"{EXPECTED_VOCAB} MaMucNoiBo "
                "khac nhau."
            )

            # ==================================================
            # 6. KIEM TRA BAI TAP HSK4
            # ==================================================

            print(
                "\n[6] KIEM TRA BAI TAP HSK4"
            )

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.BaiTap AS bt
                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc =
                       bt.MaBaiHoc
                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc =
                       bh.MaKhoaHoc
                WHERE kh.MaCapDo = ?;
                """,
                HSK_LEVEL,
            )

            exercise_count = int(
                cursor.fetchone()[0]
            )

            report[
                "exercise_count"
            ] = exercise_count

            print(
                "  So BaiTap HSK4 hien tai:",
                exercise_count,
            )

            # ==================================================
            # 7. TUYET DOI KHONG COMMIT
            # ==================================================

            connection.rollback()

    # ==========================================================
    # 8. GHI BAO CAO RA FILE JSON
    # ==========================================================

    OUTPUT_FILE.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)

    print("KET QUA:")

    print(
        "  HSK4 source: "
        f"{EXPECTED_VOCAB}/{EXPECTED_VOCAB}"
    )

    print(
        "  BaiHoc HSK4:",
        len(report["lessons"]),
    )

    print(
        "  BaiTap HSK4:",
        report["exercise_count"],
    )

    print(
        "\nBao cao:"
    )

    print(
        " ",
        OUTPUT_FILE,
    )

    print(
        "\nHOAN THANH - "
        "KHONG THAY DOI SQL"
    )

    print("=" * 70)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)