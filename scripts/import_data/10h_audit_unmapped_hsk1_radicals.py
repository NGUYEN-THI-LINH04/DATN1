from pathlib import Path
import csv
import sys
from collections import defaultdict
from contextlib import closing


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# CONFIG
# =========================================================
EXPECTED_HANZI = 301
EXPECTED_MAPPED = 209
EXPECTED_UNMAPPED = 92
EXPECTED_RADICALS = 214


# =========================================================
# FILES
# =========================================================
REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

INPUT_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_structure_review.csv"
)

SUMMARY_FILE = (
    REVIEW_DIR
    / "hsk1_unmapped_radical_summary.csv"
)

DETAIL_FILE = (
    REVIEW_DIR
    / "hsk1_unmapped_radical_detail.csv"
)


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


def load_csv(path):

    if not path.exists():

        fail(
            "Khong tim thay file:\n"
            f"{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:

            fail(
                "Khong doc duoc header CSV."
            )

        return (
            reader.fieldnames,
            list(reader),
        )


def write_csv(
    path,
    fieldnames,
    rows,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10H - AUDIT 92 RADICAL "
        "CHUA MAP VAO 214 BoThu"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  XAC DINH CAC RadicalNguon CHUA MAP")
    print("  DEM SO RADICAL RAW KHAC NHAU")
    print("  LIET KE CAC CHU SU DUNG TUNG RADICAL")
    print("  DOI CHIEU TOAN BO 214 BoThu SQL")
    print()
    print("CHE DO:")
    print("  CHI DOC CSV 10G")
    print("  CHI SELECT DATABASE")
    print("  KHONG SUA CSV 10G")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")

    # =====================================================
    # 1. READ 10G
    # =====================================================
    print()
    print(
        "[1] DOC FILE 10G"
    )
    print("-" * 120)

    fields, rows = load_csv(
        INPUT_FILE
    )

    required = {
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "TieuDeBai",
        "TuVungDauTien",
        "RadicalNguon",
        "MaBoThuDeXuat",
        "KiemTraBoThu",
        "DecompositionNguon",
        "SoNetNguon",
        "SanSangCauTruc",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        fail(
            "File 10G thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    if len(rows) != EXPECTED_HANZI:

        fail(
            "File 10G khong co "
            "dung 301 dong."
        )

    mapped_rows = [
        row
        for row in rows
        if clean(
            row["KiemTraBoThu"]
        ) == "OK"
    ]

    unmapped_rows = [
        row
        for row in rows
        if clean(
            row["KiemTraBoThu"]
        ) != "OK"
    ]

    print(
        "Tong Chu Han:",
        len(rows),
    )

    print(
        "Da map BoThu:",
        len(mapped_rows),
    )

    print(
        "Chua map BoThu:",
        len(unmapped_rows),
    )

    if len(mapped_rows) != EXPECTED_MAPPED:

        fail(
            "So dong da map "
            "khong con bang 209."
        )

    if len(unmapped_rows) != EXPECTED_UNMAPPED:

        fail(
            "So dong chua map "
            "khong con bang 92."
        )

    # =====================================================
    # 2. DATABASE SCHEMA
    # =====================================================
    print()
    print(
        "[2] DOC 214 BoThu TRONG SQL"
    )
    print("-" * 120)

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    "SELECT DB_NAME();"
                )

                database_name = clean(
                    cursor.fetchone()[0]
                )

                if (
                    database_name.lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                # -----------------------------------------
                # Kiem tra schema BoThu
                # -----------------------------------------
                cursor.execute(
                    """
                    SELECT
                        COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE
                        TABLE_SCHEMA = 'dbo'
                        AND TABLE_NAME = 'BoThu'
                    ORDER BY ORDINAL_POSITION;
                    """
                )

                bo_thu_columns = [
                    clean(row[0])
                    for row
                    in cursor.fetchall()
                ]

                print(
                    "Cot BoThu:"
                )

                print(
                    ", ".join(
                        bo_thu_columns
                    )
                )

                has_so_bo_thu = (
                    "SoBoThu"
                    in bo_thu_columns
                )

                # -----------------------------------------
                # Dynamic SELECT
                # -----------------------------------------
                if has_so_bo_thu:

                    cursor.execute(
                        """
                        SELECT
                            MaBoThu,
                            SoBoThu,
                            KyHieu,
                            TenBoThu,
                            YNghia,
                            SoNet,
                            MaNguon,
                            TrangThai
                        FROM dbo.BoThu
                        ORDER BY MaBoThu;
                        """
                    )

                    db_rows = (
                        cursor.fetchall()
                    )

                    bo_thu_rows = [
                        {
                            "MaBoThu": int(row[0]),
                            "SoBoThu": clean(row[1]),
                            "KyHieu": clean(row[2]),
                            "TenBoThu": clean(row[3]),
                            "YNghia": clean(row[4]),
                            "SoNet": clean(row[5]),
                            "MaNguon": clean(row[6]),
                            "TrangThai": clean(row[7]),
                        }
                        for row in db_rows
                    ]

                else:

                    cursor.execute(
                        """
                        SELECT
                            MaBoThu,
                            KyHieu,
                            TenBoThu,
                            YNghia,
                            SoNet,
                            MaNguon,
                            TrangThai
                        FROM dbo.BoThu
                        ORDER BY MaBoThu;
                        """
                    )

                    db_rows = (
                        cursor.fetchall()
                    )

                    bo_thu_rows = [
                        {
                            "MaBoThu": int(row[0]),
                            "SoBoThu": "",
                            "KyHieu": clean(row[1]),
                            "TenBoThu": clean(row[2]),
                            "YNghia": clean(row[3]),
                            "SoNet": clean(row[4]),
                            "MaNguon": clean(row[5]),
                            "TrangThai": clean(row[6]),
                        }
                        for row in db_rows
                    ]

                if (
                    len(bo_thu_rows)
                    != EXPECTED_RADICALS
                ):

                    fail(
                        "BoThu SQL "
                        "khong bang 214."
                    )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    print(
        "BoThu:",
        len(bo_thu_rows),
    )

    print(
        "Co cot SoBoThu:",
        (
            "YES"
            if has_so_bo_thu
            else "NO"
        ),
    )

    # =====================================================
    # 3. CHECK SQL KyHieu
    # =====================================================
    print()
    print(
        "[3] KIEM TRA KyHieu 214 BoThu"
    )
    print("-" * 120)

    ky_hieu_map = defaultdict(
        list
    )

    for row in bo_thu_rows:

        ky_hieu_map[
            row["KyHieu"]
        ].append(
            row
        )

    duplicated_ky_hieu = {
        key: value
        for key, value
        in ky_hieu_map.items()
        if len(value) > 1
    }

    print(
        "KyHieu khac nhau:",
        len(ky_hieu_map),
    )

    print(
        "KyHieu bi trung:",
        len(
            duplicated_ky_hieu
        ),
    )

    if duplicated_ky_hieu:

        for key, values in (
            duplicated_ky_hieu.items()
        ):

            print(
                "TRUNG:",
                key,
                "=>",
                [
                    value["MaBoThu"]
                    for value in values
                ],
            )

    # =====================================================
    # 4. GROUP UNMAPPED RAW RADICALS
    # =====================================================
    print()
    print(
        "[4] NHOM 92 CHU THEO RadicalNguon"
    )
    print("-" * 120)

    radical_groups = defaultdict(
        list
    )

    for row in unmapped_rows:

        radical = clean(
            row["RadicalNguon"]
        )

        radical_groups[
            radical
        ].append(
            row
        )

    print(
        "So RadicalNguon khac nhau:",
        len(radical_groups),
    )

    print()

    sorted_groups = sorted(
        radical_groups.items(),
        key=lambda item: (
            -len(item[1]),
            item[0],
        ),
    )

    for radical, items in sorted_groups:

        chars = "".join(
            clean(row["KyTu"])
            for row in items
        )

        print(
            f"RadicalNguon={radical!r:<8} "
            f"| SoChu={len(items):>2} "
            f"| Chu={chars}"
        )

    # =====================================================
    # 5. BUILD SUMMARY
    # =====================================================
    print()
    print(
        "[5] TAO SUMMARY RADICAL"
    )
    print("-" * 120)

    summary_rows = []

    for radical, items in sorted_groups:

        chars = [
            clean(row["KyTu"])
            for row in items
        ]

        lessons = sorted(
            {
                int(
                    clean(
                        row[
                            "BaiXuatHienDau"
                        ]
                    )
                )
                for row in items
            }
        )

        # -----------------------------------------
        # Chi kiem tra exact.
        # CHUA tu dong map variant.
        # -----------------------------------------
        exact_matches = (
            ky_hieu_map.get(
                radical,
                [],
            )
        )

        if len(exact_matches) == 1:

            exact_status = (
                "EXACT_FOUND"
            )

            exact_ma_bo_thu = (
                exact_matches[0][
                    "MaBoThu"
                ]
            )

            exact_ky_hieu = (
                exact_matches[0][
                    "KyHieu"
                ]
            )

        elif len(exact_matches) > 1:

            exact_status = (
                "EXACT_DUPLICATE"
            )

            exact_ma_bo_thu = (
                "|".join(
                    str(
                        item[
                            "MaBoThu"
                        ]
                    )
                    for item
                    in exact_matches
                )
            )

            exact_ky_hieu = (
                radical
            )

        else:

            exact_status = (
                "NO_EXACT_MATCH"
            )

            exact_ma_bo_thu = ""
            exact_ky_hieu = ""

        summary_rows.append(
            {
                "RadicalNguon": (
                    radical
                ),

                "SoChu": (
                    len(items)
                ),

                "DanhSachChu": (
                    " ".join(chars)
                ),

                "DanhSachBaiXuatHienDau": (
                    " ".join(
                        str(number)
                        for number in lessons
                    )
                ),

                "ExactMatchSQL": (
                    exact_status
                ),

                "ExactMaBoThu": (
                    exact_ma_bo_thu
                ),

                "ExactKyHieuSQL": (
                    exact_ky_hieu
                ),

                # Chua de xuat mapping.
                "RadicalChuanDeXuat": "",

                "MaBoThuDeXuat": "",

                "LoaiMappingDeXuat": "",

                "DaKiemDuyetMapping": 0,

                "GhiChu": "",
            }
        )

    # =====================================================
    # 6. BUILD DETAIL
    # =====================================================
    detail_rows = []

    for radical, items in sorted_groups:

        for row in sorted(
            items,
            key=lambda item: (
                int(
                    clean(
                        item[
                            "BaiXuatHienDau"
                        ]
                    )
                ),
                clean(
                    item["KyTu"]
                ),
            ),
        ):

            detail_rows.append(
                {
                    "KyTu": clean(
                        row["KyTu"]
                    ),

                    "PhamVi": clean(
                        row["PhamVi"]
                    ),

                    "BaiXuatHienDau": clean(
                        row[
                            "BaiXuatHienDau"
                        ]
                    ),

                    "TieuDeBai": clean(
                        row["TieuDeBai"]
                    ),

                    "TuVungDauTien": clean(
                        row[
                            "TuVungDauTien"
                        ]
                    ),

                    "RadicalNguon": (
                        radical
                    ),

                    "DecompositionNguon": clean(
                        row[
                            "DecompositionNguon"
                        ]
                    ),

                    "SoNetNguon": clean(
                        row[
                            "SoNetNguon"
                        ]
                    ),

                    "KiemTraBoThu10G": clean(
                        row[
                            "KiemTraBoThu"
                        ]
                    ),

                    "RadicalChuanDeXuat": "",

                    "MaBoThuDeXuat": "",

                    "DaKiemDuyetMapping": 0,

                    "GhiChu": "",
                }
            )

    # =====================================================
    # 7. WRITE FILES
    # =====================================================
    print()
    print(
        "[6] GHI FILE AUDIT"
    )
    print("-" * 120)

    write_csv(
        SUMMARY_FILE,
        [
            "RadicalNguon",
            "SoChu",
            "DanhSachChu",
            "DanhSachBaiXuatHienDau",
            "ExactMatchSQL",
            "ExactMaBoThu",
            "ExactKyHieuSQL",
            "RadicalChuanDeXuat",
            "MaBoThuDeXuat",
            "LoaiMappingDeXuat",
            "DaKiemDuyetMapping",
            "GhiChu",
        ],
        summary_rows,
    )

    write_csv(
        DETAIL_FILE,
        [
            "KyTu",
            "PhamVi",
            "BaiXuatHienDau",
            "TieuDeBai",
            "TuVungDauTien",
            "RadicalNguon",
            "DecompositionNguon",
            "SoNetNguon",
            "KiemTraBoThu10G",
            "RadicalChuanDeXuat",
            "MaBoThuDeXuat",
            "DaKiemDuyetMapping",
            "GhiChu",
        ],
        detail_rows,
    )

    print(
        "Summary:"
    )

    print(
        SUMMARY_FILE
    )

    print()
    print(
        "Detail:"
    )

    print(
        DETAIL_FILE
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10H"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(rows),
    )

    print(
        "BoThu map OK tu 10G:",
        len(mapped_rows),
    )

    print(
        "Chu chua map BoThu:",
        len(unmapped_rows),
    )

    print(
        "RadicalNguon khac nhau "
        "trong 92 chu:",
        len(radical_groups),
    )

    print(
        "BoThu SQL:",
        len(bo_thu_rows),
    )

    print(
        "KyHieu BoThu SQL "
        "khac nhau:",
        len(ky_hieu_map),
    )

    print(
        "KyHieu SQL bi trung:",
        len(
            duplicated_ky_hieu
        ),
    )

    print()
    print(
        "CHUA TU DONG MAP "
        "RADICAL BIEN THE."
    )

    print(
        "DaKiemDuyetMapping=1:",
        0,
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "FILE 10G KHONG BI SUA."
    )

    print()
    print("=" * 120)
    print("HOAN TAT")
    print("=" * 120)


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 120)
        print(
            "10H THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)