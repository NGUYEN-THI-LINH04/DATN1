# -*- coding: utf-8 -*-
"""
BUOC 17 - AUDIT DANH SACH CHU HAN CHUAN HSK4

Muc tieu:
1. Tim cac file co kha nang la DANH SACH CHU HAN CHUAN HSK
   dang ton tai trong project.
2. KHONG quet hang chuc nghin SVG cua Make Me a Hanzi.
3. Doc header + thong ke CSV co lien quan.
4. Thong ke dbo.ChuHan hien tai theo KhoaHoc HSK1-4.
5. Thong ke:
   - tong dong ChuHan
   - so KyTu distinct
   - ky tu trung trong cung khoa
6. Doc dbo.NguonDuLieu de biet MaNguon thuc te.
7. Tao report de Buoc 18 dung.

CHI DOC FILE.
CHI SELECT SQL.
KHONG INSERT.
KHONG UPDATE.
KHONG DELETE.
"""

import csv
import json
import sys

from pathlib import Path
from contextlib import closing
from collections import Counter


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT),
)

from database import get_connection


OUTPUT_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

REPORT_FILE = (
    OUTPUT_DIR
    / "hsk4_standard_hanzi_audit.json"
)


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):

    return (
        str(value).strip()
        if value is not None
        else ""
    )


def fetch_all(
    cursor,
    sql,
    *params,
):

    cursor.execute(
        sql,
        *params,
    )

    columns = [
        item[0]
        for item in cursor.description
    ]

    return [
        dict(
            zip(
                columns,
                row,
            )
        )
        for row in cursor.fetchall()
    ]


def read_csv_info(path):

    info = {
        "DuongDan": str(path),
        "TenFile": path.name,
        "KichThuocByte": (
            path.stat().st_size
        ),
        "Cot": [],
        "TongDong": None,
        "ThongKeLevel": {},
        "LoiDoc": None,
    }

    encodings = [
        "utf-8-sig",
        "utf-8",
        "gb18030",
    ]

    last_error = None

    for encoding in encodings:

        try:

            with path.open(
                "r",
                encoding=encoding,
                newline="",
            ) as file:

                reader = csv.DictReader(
                    file
                )

                fields = (
                    reader.fieldnames
                    or []
                )

                rows = list(
                    reader
                )

            info["Cot"] = fields

            info["TongDong"] = len(
                rows
            )

            # ----------------------------------------------
            # Thu tim cot cap do theo cac ten pho bien.
            # CHI THONG KE neu cot thuc su ton tai.
            # ----------------------------------------------

            possible_level_columns = [
                "Level",
                "level",
                "CapDoHSK",
                "HSK",
                "hsk",
                "Band",
                "band",
            ]

            level_column = None

            for candidate in (
                possible_level_columns
            ):

                if candidate in fields:

                    level_column = candidate
                    break

            if level_column:

                counter = Counter(
                    clean(
                        row.get(
                            level_column
                        )
                    )
                    for row in rows
                    if clean(
                        row.get(
                            level_column
                        )
                    )
                )

                info[
                    "CotCapDoPhatHien"
                ] = level_column

                info[
                    "ThongKeLevel"
                ] = dict(
                    sorted(
                        counter.items()
                    )
                )

            return info

        except Exception as error:

            last_error = error

    info[
        "LoiDoc"
    ] = str(
        last_error
    )

    return info


# ==========================================================
# 3. TIM FILE DANH SACH CHU HAN HSK
# ==========================================================

def find_hsk_hanzi_sources():

    print(
        "\n[1] TIM FILE DANH SACH "
        "CHU HAN / CHARACTER HSK"
    )

    roots = [
        ROOT / "data_sources" / "hsk",
        ROOT / "data_sources" / "hanzi",
        ROOT / "scripts" / "hsk1",
        ROOT / "scripts" / "hsk2",
        ROOT / "scripts" / "hsk3",
    ]

    allowed_extensions = {
        ".csv",
        ".txt",
        ".json",
        ".tsv",
    }

    keywords = [
        "hanzi",
        "character",
        "characters",
        "chuhan",
        "chu_han",
    ]

    # ----------------------------------------------
    # Bo qua cac thu muc lon / khong phai danh sach HSK.
    # ----------------------------------------------

    ignored_path_parts = {
        "svgs",
        ".git",
        "__pycache__",
        "node_modules",
        "venv",
        ".venv",
    }

    found = []

    seen = set()

    for root in roots:

        if not root.exists():
            continue

        for path in root.rglob("*"):

            if not path.is_file():
                continue

            if (
                path.suffix.lower()
                not in allowed_extensions
            ):
                continue

            lower_parts = {
                part.lower()
                for part in path.parts
            }

            if (
                lower_parts
                & ignored_path_parts
            ):
                continue

            text = (
                str(path)
                .lower()
                .replace("\\", "/")
            )

            if not any(
                keyword in text
                for keyword in keywords
            ):
                continue

            key = str(
                path.resolve()
            ).lower()

            if key in seen:
                continue

            seen.add(
                key
            )

            found.append(
                path
            )

    found.sort(
        key=lambda p:
        str(p).lower()
    )

    print(
        "Tong file tim thay:",
        len(found),
    )

    return found


# ==========================================================
# 4. PHAN LOAI FILE
# ==========================================================

def classify_candidate(path):

    text = (
        str(path)
        .lower()
        .replace("\\", "/")
    )

    name = (
        path.name.lower()
    )

    # ----------------------------------------------
    # File co ve la source danh sach HSK chinh.
    # ----------------------------------------------

    if (
        "gf0025" in text
        or "hsk30" in text
        or "standard" in name
    ):
        return "UU_TIEN_CAO"

    # ----------------------------------------------
    # File final/processed cua HSK2/3:
    # huu ich de doi chieu pipeline cu,
    # nhung KHONG mac dinh la source chuan.
    # ----------------------------------------------

    if (
        "/scripts/hsk2/" in text
        or "/scripts/hsk3/" in text
    ):
        return "PIPELINE_CU"

    if "/review/" in text:

        return "REVIEW_CU"

    return "KHAC"


# ==========================================================
# 5. DOC SQL
# ==========================================================

def audit_sql():

    print(
        "\n[3] THONG KE dbo.ChuHan "
        "THEO KHOA HOC"
    )

    result = {
        "by_course": [],
        "duplicate_within_course": [],
        "sources": [],
    }

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            # ==============================================
            # A. ChuHan theo khoa
            # ==============================================

            rows = fetch_all(
                cursor,
                """
                SELECT
                    k.MaKhoaHoc,
                    k.MaCapDo,
                    k.MaKyHieu,
                    k.TrangThai AS TrangThaiKhoa,

                    COUNT(ch.MaChuHan)
                        AS TongDongChuHan,

                    COUNT(
                        DISTINCT ch.KyTu
                    )
                        AS SoKyTuDistinct

                FROM dbo.KhoaHoc AS k

                LEFT JOIN dbo.BaiHoc AS b
                    ON b.MaKhoaHoc = k.MaKhoaHoc

                LEFT JOIN dbo.ChuHan AS ch
                    ON ch.MaBaiHoc = b.MaBaiHoc

                GROUP BY
                    k.MaKhoaHoc,
                    k.MaCapDo,
                    k.MaKyHieu,
                    k.TrangThai

                ORDER BY
                    k.MaKhoaHoc
                """
            )

            result[
                "by_course"
            ] = rows

            for row in rows:

                print(
                    f"HSK{row['MaCapDo']} "
                    f"(MaKhoaHoc={row['MaKhoaHoc']}): "
                    f"rows={row['TongDongChuHan']} | "
                    f"distinct KyTu={row['SoKyTuDistinct']} | "
                    f"{row['TrangThaiKhoa']}"
                )

            # ==============================================
            # B. KyTu lap trong CUNG mot khoa
            # ==============================================

            duplicates = fetch_all(
                cursor,
                """
                SELECT
                    b.MaKhoaHoc,
                    ch.KyTu,
                    COUNT(*) AS SoLan

                FROM dbo.ChuHan AS ch

                INNER JOIN dbo.BaiHoc AS b
                    ON b.MaBaiHoc = ch.MaBaiHoc

                GROUP BY
                    b.MaKhoaHoc,
                    ch.KyTu

                HAVING COUNT(*) > 1

                ORDER BY
                    b.MaKhoaHoc,
                    ch.KyTu
                """
            )

            result[
                "duplicate_within_course"
            ] = duplicates

            duplicate_counter = Counter(
                row[
                    "MaKhoaHoc"
                ]
                for row in duplicates
            )

            print(
                "\nKyTu bi lap trong cung khoa:"
            )

            for course_id in [
                1,
                2,
                3,
                4,
            ]:

                print(
                    f"  MaKhoaHoc={course_id}: "
                    f"{duplicate_counter[course_id]}"
                )

            # ==============================================
            # C. NguonDuLieu
            # ==============================================

            print(
                "\n[4] dbo.NguonDuLieu"
            )

            sources = fetch_all(
                cursor,
                """
                SELECT
                    MaNguon,
                    Ten,
                    LienKetNguon,
                    GiayPhep,
                    GhiChu

                FROM dbo.NguonDuLieu

                ORDER BY MaNguon
                """
            )

            result[
                "sources"
            ] = sources

            for row in sources:

                print(
                    f"  {row['MaNguon']}: "
                    f"{row['Ten']}"
                )

    return result


# ==========================================================
# 6. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 17 - AUDIT DANH SACH "
        "CHU HAN CHUAN HSK4"
    )

    print("=" * 80)

    print(
        "CHI DOC FILE + SELECT SQL"
    )

    print(
        "KHONG GHI SQL"
    )

    # ======================================================
    # 1. FIND
    # ======================================================

    paths = find_hsk_hanzi_sources()

    # ======================================================
    # 2. INSPECT
    # ======================================================

    print(
        "\n[2] KIEM TRA CAC FILE UNG VIEN"
    )

    file_results = []

    for path in paths:

        classification = (
            classify_candidate(
                path
            )
        )

        item = {
            "PhanLoai":
                classification,

            "DuongDan":
                str(path),
        }

        if (
            path.suffix.lower()
            == ".csv"
        ):

            csv_info = read_csv_info(
                path
            )

            item.update(
                csv_info
            )

        else:

            try:

                item[
                    "KichThuocByte"
                ] = path.stat().st_size

            except OSError:

                item[
                    "KichThuocByte"
                ] = None

        file_results.append(
            item
        )

    # ----------------------------------------------
    # In uu tien cao truoc
    # ----------------------------------------------

    priority_order = {
        "UU_TIEN_CAO": 0,
        "PIPELINE_CU": 1,
        "REVIEW_CU": 2,
        "KHAC": 3,
    }

    file_results.sort(
        key=lambda item: (
            priority_order.get(
                item[
                    "PhanLoai"
                ],
                99,
            ),
            item[
                "DuongDan"
            ].lower(),
        )
    )

    for item in file_results:

        print(
            "\n"
            + "-" * 80
        )

        print(
            "Loai:",
            item[
                "PhanLoai"
            ],
        )

        print(
            "File:",
            item[
                "DuongDan"
            ],
        )

        if (
            "TongDong"
            in item
        ):

            print(
                "Rows:",
                item[
                    "TongDong"
                ],
            )

            print(
                "Columns:",
                item.get(
                    "Cot"
                ),
            )

            if item.get(
                "CotCapDoPhatHien"
            ):

                print(
                    "Level column:",
                    item[
                        "CotCapDoPhatHien"
                    ],
                )

                print(
                    "Level counts:",
                    item[
                        "ThongKeLevel"
                    ],
                )

            if item.get(
                "LoiDoc"
            ):

                print(
                    "Loi doc:",
                    item[
                        "LoiDoc"
                    ],
                )

    # ======================================================
    # 3-4. SQL
    # ======================================================

    sql_info = audit_sql()

    # ======================================================
    # 5. REPORT
    # ======================================================

    print(
        "\n[5] TAO REPORT"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if REPORT_FILE.exists():

        raise FileExistsError(
            "Report da ton tai:\n"
            f"{REPORT_FILE}\n"
            "Khong tu dong ghi de."
        )

    report = {
        "status":
            "PASS",

        "buoc":
            17,

        "tong_file_ung_vien":
            len(
                file_results
            ),

        "files":
            file_results,

        "sql":
            sql_info,

        "da_chot_source_hsk4":
            False,

        "da_chot_so_chu_hsk4":
            False,

        "da_tao_hsk4_hanzi":
            False,

        "da_ghi_sql":
            False,

        "ghi_chu":
            (
                "Buoc 17 chi audit danh sach "
                "chu Han HSK va du lieu ChuHan "
                "HSK1-3 hien co. "
                "Khong mac dinh HSK4 co 300 chu "
                "neu chua xac minh source."
            ),
    }

    REPORT_FILE.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # 6. KET QUA
    # ======================================================

    high_priority = [
        item
        for item in file_results
        if item[
            "PhanLoai"
        ]
        == "UU_TIEN_CAO"
    ]

    print(
        "\n" + "=" * 80
    )

    print(
        "AUDIT DANH SACH CHU HAN "
        "HSK4 HOAN THANH"
    )

    print("=" * 80)

    print(
        "Tong file ung vien:",
        len(
            file_results
        ),
    )

    print(
        "File uu tien cao:",
        len(
            high_priority
        ),
    )

    print(
        "Da chot source HSK4: CHUA"
    )

    print(
        "Da chot so chu HSK4: CHUA"
    )

    print(
        "\nREPORT:"
    )

    print(
        " ",
        REPORT_FILE,
    )

    print(
        "\nKHONG TAO CHU HAN HSK4."
    )

    print(
        "KHONG THAY DOI SQL."
    )

    print("=" * 80)


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