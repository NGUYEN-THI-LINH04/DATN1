from pathlib import Path
import csv
import sys
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
STANDARD_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "hsk1_48_grammar_standard.csv"
)

REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
)

OUTPUT_FILE = (
    REVIEW_DIR
    / "hsk1_lesson1_grammar_mapping_review.csv"
)

COURSE_CODE = "HSK1-CORE"
LESSON_NO = 1
SOURCE_ID = 1004
EXPECTED_GRAMMAR_COUNT = 7


# =========================================================
# MAPPING DO DO AN XAC DINH
#
# Luu y:
# - Day la mapping cua do an.
# - Khong sua noi dung 48 muc chuan.
# - Mot muc ngu phap bai hoc co the lien quan
#   toi nhieu hon 1 muc chuan.
# =========================================================
EXPECTED_MAPPING = {

    1: {
        "TenCauTruc": "A + 是 + B",
        "MaMucChuan": "GF1-036",
        "LoaiDoiChieu": "truc_tiep",
        "MucDoTinCay": "cao",
        "GhiChu": (
            "Cau truc A + 是 + B doi chieu truc tiep "
            "voi muc “是”字句."
        ),
    },

    2: {
        "TenCauTruc": "Chủ ngữ + 叫 + tên",
        "MaMucChuan": "GF1-029",
        "LoaiDoiChieu": "theo_kieu_cau",
        "MucDoTinCay": "trung_binh",
        "GhiChu": (
            "GF0025 cap 1 khong tach rieng 叫 thanh mot diem "
            "ngu phap doc lap trong danh sach 48 muc. "
            "Mau Chủ ngữ + 叫 + tên duoc doi chieu theo "
            "dong tu vi ngu: 主谓句1：动词谓语句."
        ),
    },

    3: {
        "TenCauTruc": '什么 - hỏi "gì / cái gì"',
        "MaMucChuan": "GF1-004;GF1-046",
        "LoaiDoiChieu": "nhieu_muc",
        "MucDoTinCay": "cao",
        "GhiChu": (
            "什么 vua thuoc nhom 疑问代词, "
            "vua nam trong phuong phap 用疑问代词提问."
        ),
    },

    4: {
        "TenCauTruc": "Câu trần thuật + 吗？",
        "MaMucChuan": "GF1-022;GF1-045",
        "LoaiDoiChieu": "nhieu_muc",
        "MucDoTinCay": "cao",
        "GhiChu": (
            "吗 vua la 语气助词, "
            "vua co muc rieng 用“吗”提问."
        ),
    },

    5: {
        "TenCauTruc": "...呢？ - hỏi lại hoặc tiếp nối",
        "MaMucChuan": "GF1-022",
        "LoaiDoiChieu": "truc_tiep",
        "MucDoTinCay": "cao",
        "GhiChu": (
            "呢 nam trong nhom 语气助词：吧、了、吗、呢."
        ),
    },

    6: {
        "TenCauTruc": "很 + tính từ",
        "MaMucChuan": "GF1-009;GF1-030",
        "LoaiDoiChieu": "nhieu_muc",
        "MucDoTinCay": "cao",
        "GhiChu": (
            "很 thuoc 程度副词; mau cau voi tinh tu "
            "dong thoi lien quan den 主谓句2：形容词谓语句."
        ),
    },

    7: {
        "TenCauTruc": '也 - "cũng"',
        "MaMucChuan": "GF1-013",
        "LoaiDoiChieu": "truc_tiep",
        "MucDoTinCay": "cao",
        "GhiChu": (
            "也 nam trong nhom 关联副词：还、也."
        ),
    },
}


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


def line():

    print("-" * 115)


def read_csv(path):

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:

            fail(
                f"Khong doc duoc header:\n{path}"
            )

        return reader.fieldnames, list(reader)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H5 - DOI CHIEU 7 NGU PHAP BAI 1 "
        "VOI 48 MUC GF0025"
    )
    print("=" * 115)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE CHUAN")
    print("  CHI SELECT DATABASE")
    print("  TAO FILE REVIEW MAPPING")
    print("  KHONG UPDATE dbo.NguPhap")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG GAN MaNguon=1004")

    # =====================================================
    # 1. VERIFY STANDARD FILE
    # =====================================================
    print()
    print("[1] VERIFY FILE 48 NGU PHAP CHUAN")
    line()

    if not STANDARD_FILE.exists():

        fail(
            "Khong tim thay file:\n"
            f"{STANDARD_FILE}"
        )

    standard_fields, standard_rows = (
        read_csv(
            STANDARD_FILE
        )
    )

    required_fields = {
        "MaMucNguPhapChuan",
        "CapDoHSK",
        "SoThuTuChuan",
        "NhomLonTrung",
        "NhomConTrung",
        "TenMucTrung",
        "NoiDungChuanTrung",
        "MaNguon",
    }

    missing_fields = (
        required_fields
        - set(standard_fields)
    )

    if missing_fields:

        fail(
            "File chuan thieu cot: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if len(standard_rows) != 48:

        fail(
            "File chuan phai co 48 dong. "
            f"Thuc te: {len(standard_rows)}"
        )

    standard_by_id = {}

    for row in standard_rows:

        standard_id = clean(
            row["MaMucNguPhapChuan"]
        )

        if standard_id in standard_by_id:

            fail(
                "MaMucNguPhapChuan bi trung: "
                f"{standard_id}"
            )

        if clean(
            row["MaNguon"]
        ) != str(SOURCE_ID):

            fail(
                "Co muc chuan khong dung "
                "MaNguon=1004."
            )

        standard_by_id[
            standard_id
        ] = row

    expected_ids = {
        f"GF1-{number:03d}"
        for number in range(
            1,
            49,
        )
    }

    if (
        set(standard_by_id)
        != expected_ids
    ):

        fail(
            "Danh sach ID chuan "
            "khong dung GF1-001 -> GF1-048."
        )

    print(
        "Tong muc chuan:",
        len(standard_rows),
    )

    print(
        "GF1-001 -> GF1-048: OK"
    )

    print(
        "MaNguon=1004: 48/48 OK"
    )

    # =====================================================
    # 2. VERIFY CAC ID MAPPING
    # =====================================================
    print()
    print("[2] VERIFY MAPPING TRONG SCRIPT")
    line()

    if len(EXPECTED_MAPPING) != 7:

        fail(
            "EXPECTED_MAPPING phai co "
            "dung 7 muc."
        )

    for grammar_id, mapping in (
        EXPECTED_MAPPING.items()
    ):

        mapped_ids = [
            item.strip()
            for item in mapping[
                "MaMucChuan"
            ].split(";")
            if item.strip()
        ]

        if not mapped_ids:

            fail(
                f"MaNguPhap={grammar_id} "
                "khong co mapping."
            )

        for standard_id in mapped_ids:

            if (
                standard_id
                not in standard_by_id
            ):

                fail(
                    f"Mapping MaNguPhap="
                    f"{grammar_id} "
                    f"tham chieu ID "
                    f"khong ton tai: "
                    f"{standard_id}"
                )

    print(
        "7/7 mapping hop le."
    )

    # =====================================================
    # 3. CONNECT DATABASE
    # =====================================================
    print()
    print("[3] KET NOI DATABASE")
    line()

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        ),
                        DB_NAME(),
                        SUSER_SNAME();
                    """
                )

                (
                    server_name,
                    database_name,
                    login_name,
                ) = cursor.fetchone()

                print(
                    "Server:",
                    server_name,
                )

                print(
                    "Database:",
                    database_name,
                )

                print(
                    "Tai khoan:",
                    login_name,
                )

                if (
                    clean(
                        database_name
                    ).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi nham database."
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 4. VERIFY SOURCE 1004
                # =========================================
                print()
                print(
                    "[4] VERIFY NGUON 1004"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = ?;
                    """,
                    SOURCE_ID,
                )

                source_row = (
                    cursor.fetchone()
                )

                if source_row is None:

                    fail(
                        "Khong tim thay "
                        "MaNguon=1004."
                    )

                print(
                    "MaNguon:",
                    int(source_row[0]),
                )

                print(
                    "Ten:",
                    clean(source_row[1]),
                )

                # =========================================
                # 5. DOC 7 NGU PHAP BAI 1
                # =========================================
                print()
                print(
                    "[5] DOC 7 NGU PHAP BAI 1"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        np.MaNguPhap,
                        np.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe,
                        np.ThuTu,
                        np.TenCauTruc,
                        np.MoTa,
                        np.CachDung,
                        np.ViDuTiengTrung,
                        np.ViDuPinyin,
                        np.ViDuTiengViet,
                        np.MaNguon,
                        np.TrangThai
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc
                        = bh.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai = ?
                    ORDER BY
                        np.ThuTu,
                        np.MaNguPhap;
                    """,
                    COURSE_CODE,
                    LESSON_NO,
                )

                grammar_rows = (
                    cursor.fetchall()
                )

                if (
                    len(grammar_rows)
                    != EXPECTED_GRAMMAR_COUNT
                ):

                    fail(
                        "Bai 1 phai co dung "
                        "7 muc ngu phap. "
                        f"Thuc te: "
                        f"{len(grammar_rows)}"
                    )

                grammar_data = []

                for row in grammar_rows:

                    item = {
                        "MaNguPhap": int(
                            row[0]
                        ),
                        "MaBaiHoc": int(
                            row[1]
                        ),
                        "SoThuTuBai": int(
                            row[2]
                        ),
                        "TieuDeBai": clean(
                            row[3]
                        ),
                        "ThuTu": int(
                            row[4]
                        ),
                        "TenCauTruc": clean(
                            row[5]
                        ),
                        "MoTa": clean(
                            row[6]
                        ),
                        "CachDung": clean(
                            row[7]
                        ),
                        "ViDuTiengTrung": clean(
                            row[8]
                        ),
                        "ViDuPinyin": clean(
                            row[9]
                        ),
                        "ViDuTiengViet": clean(
                            row[10]
                        ),
                        "MaNguonHienTai": (
                            ""
                            if row[11] is None
                            else str(
                                int(row[11])
                            )
                        ),
                        "TrangThai": clean(
                            row[12]
                        ),
                    }

                    grammar_data.append(
                        item
                    )

                print(
                    "Tong:",
                    len(grammar_data),
                )

                # =========================================
                # 6. VERIFY 7 NOI DUNG KHONG BI DOI
                # =========================================
                print()
                print(
                    "[6] VERIFY TEN 7 NGU PHAP"
                )
                line()

                for item in grammar_data:

                    grammar_id = item[
                        "MaNguPhap"
                    ]

                    if (
                        grammar_id
                        not in EXPECTED_MAPPING
                    ):

                        fail(
                            "Phat hien MaNguPhap "
                            "khong mong doi: "
                            f"{grammar_id}"
                        )

                    expected_name = (
                        EXPECTED_MAPPING[
                            grammar_id
                        ][
                            "TenCauTruc"
                        ]
                    )

                    if (
                        item[
                            "TenCauTruc"
                        ]
                        != expected_name
                    ):

                        fail(
                            f"TenCauTruc "
                            f"MaNguPhap="
                            f"{grammar_id} "
                            f"da thay doi.\n"
                            f"Mong doi: "
                            f"{expected_name}\n"
                            f"Thuc te: "
                            f"{item['TenCauTruc']}"
                        )

                    if (
                        item[
                            "MaNguonHienTai"
                        ]
                        != ""
                    ):

                        fail(
                            f"MaNguPhap="
                            f"{grammar_id} "
                            "da co MaNguon. "
                            "Khong tiep tuc "
                            "de tranh mapping "
                            "tren du lieu da sua."
                        )

                    print(
                        f"MaNguPhap="
                        f"{grammar_id} | "
                        f"{item['TenCauTruc']} "
                        f"| OK"
                    )

                # =========================================
                # 7. CREATE REVIEW ROWS
                # =========================================
                print()
                print(
                    "[7] TAO REVIEW MAPPING"
                )
                line()

                output_rows = []

                for item in grammar_data:

                    grammar_id = item[
                        "MaNguPhap"
                    ]

                    mapping = (
                        EXPECTED_MAPPING[
                            grammar_id
                        ]
                    )

                    mapped_ids = [
                        value.strip()
                        for value in mapping[
                            "MaMucChuan"
                        ].split(";")
                        if value.strip()
                    ]

                    mapped_names = []
                    mapped_contents = []

                    for standard_id in (
                        mapped_ids
                    ):

                        standard = (
                            standard_by_id[
                                standard_id
                            ]
                        )

                        mapped_names.append(
                            clean(
                                standard[
                                    "TenMucTrung"
                                ]
                            )
                        )

                        mapped_contents.append(
                            clean(
                                standard[
                                    "NoiDungChuanTrung"
                                ]
                            )
                        )

                    output_rows.append(
                        {
                            "MaNguPhap": (
                                grammar_id
                            ),

                            "SoThuTuBai": (
                                item[
                                    "SoThuTuBai"
                                ]
                            ),

                            "TieuDeBai": (
                                item[
                                    "TieuDeBai"
                                ]
                            ),

                            "ThuTuTrongBai": (
                                item["ThuTu"]
                            ),

                            "TenCauTruc": (
                                item[
                                    "TenCauTruc"
                                ]
                            ),

                            "MoTa": (
                                item["MoTa"]
                            ),

                            "CachDung": (
                                item["CachDung"]
                            ),

                            "ViDuTiengTrung": (
                                item[
                                    "ViDuTiengTrung"
                                ]
                            ),

                            "ViDuPinyin": (
                                item[
                                    "ViDuPinyin"
                                ]
                            ),

                            "ViDuTiengViet": (
                                item[
                                    "ViDuTiengViet"
                                ]
                            ),

                            "MaNguonHienTai": (
                                item[
                                    "MaNguonHienTai"
                                ]
                            ),

                            "MaNguonDeXuat": (
                                SOURCE_ID
                            ),

                            "MaMucNguPhapChuan": (
                                ";".join(
                                    mapped_ids
                                )
                            ),

                            "TenMucChuan": (
                                " | ".join(
                                    mapped_names
                                )
                            ),

                            "NoiDungChuan": (
                                " | ".join(
                                    mapped_contents
                                )
                            ),

                            "LoaiDoiChieu": (
                                mapping[
                                    "LoaiDoiChieu"
                                ]
                            ),

                            "MucDoTinCay": (
                                mapping[
                                    "MucDoTinCay"
                                ]
                            ),

                            "GhiChuDoiChieu": (
                                mapping[
                                    "GhiChu"
                                ]
                            ),

                            # Chua danh dau review.
                            "DaKiemDuyetMapping": 0,

                            "GhiChuKiemDuyet": "",
                        }
                    )

                # =========================================
                # 8. WRITE CSV
                # =========================================
                REVIEW_DIR.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                fieldnames = [
                    "MaNguPhap",
                    "SoThuTuBai",
                    "TieuDeBai",
                    "ThuTuTrongBai",
                    "TenCauTruc",
                    "MoTa",
                    "CachDung",
                    "ViDuTiengTrung",
                    "ViDuPinyin",
                    "ViDuTiengViet",
                    "MaNguonHienTai",
                    "MaNguonDeXuat",
                    "MaMucNguPhapChuan",
                    "TenMucChuan",
                    "NoiDungChuan",
                    "LoaiDoiChieu",
                    "MucDoTinCay",
                    "GhiChuDoiChieu",
                    "DaKiemDuyetMapping",
                    "GhiChuKiemDuyet",
                ]

                with open(
                    OUTPUT_FILE,
                    "w",
                    encoding="utf-8-sig",
                    newline="",
                ) as file:

                    writer = csv.DictWriter(
                        file,
                        fieldnames=fieldnames,
                    )

                    writer.writeheader()

                    writer.writerows(
                        output_rows
                    )

                print(
                    "Da tao:"
                )

                print(
                    OUTPUT_FILE
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 9. VERIFY OUTPUT
    # =====================================================
    print()
    print("[8] VERIFY FILE REVIEW")
    line()

    _, verify_rows = read_csv(
        OUTPUT_FILE
    )

    if len(verify_rows) != 7:

        fail(
            "File review phai "
            "co dung 7 dong."
        )

    grammar_ids = [
        clean(
            row["MaNguPhap"]
        )
        for row in verify_rows
    ]

    if len(
        set(grammar_ids)
    ) != 7:

        fail(
            "MaNguPhap trong review "
            "bi trung."
        )

    wrong_source = [
        row
        for row in verify_rows
        if clean(
            row["MaNguonDeXuat"]
        ) != "1004"
    ]

    if wrong_source:

        fail(
            "Co mapping khong de xuat "
            "MaNguon=1004."
        )

    reviewed = [
        row
        for row in verify_rows
        if clean(
            row[
                "DaKiemDuyetMapping"
            ]
        ) == "1"
    ]

    print(
        "Tong mapping:",
        len(verify_rows),
    )

    print(
        "MaNguPhap duy nhat:",
        len(
            set(grammar_ids)
        ),
    )

    print(
        "MaNguonDeXuat=1004:",
        (
            len(verify_rows)
            - len(wrong_source)
        ),
    )

    print(
        "DaKiemDuyetMapping=1:",
        len(reviewed),
    )

    print(
        "Chua kiem duyet:",
        (
            len(verify_rows)
            - len(reviewed)
        ),
    )

    # =====================================================
    # 10. PRINT MAPPING
    # =====================================================
    print()
    print(
        "[9] NOI DUNG MAPPING DE REVIEW"
    )
    line()

    for row in verify_rows:

        print()
        print(
            f"MaNguPhap="
            f"{row['MaNguPhap']}"
        )

        print(
            "  TenCauTruc:",
            row["TenCauTruc"],
        )

        print(
            "  MaMucChuan:",
            row[
                "MaMucNguPhapChuan"
            ],
        )

        print(
            "  TenMucChuan:",
            row[
                "TenMucChuan"
            ],
        )

        print(
            "  LoaiDoiChieu:",
            row[
                "LoaiDoiChieu"
            ],
        )

        print(
            "  MucDoTinCay:",
            row[
                "MucDoTinCay"
            ],
        )

        print(
            "  GhiChu:",
            row[
                "GhiChuDoiChieu"
            ],
        )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 115)
    print(
        "KET QUA 09H5"
    )
    print("=" * 115)

    print(
        "Tong ngu phap Bai 1:",
        len(verify_rows),
    )

    print(
        "Tong mapping:",
        len(verify_rows),
    )

    print(
        "Da kiem duyet mapping:",
        len(reviewed),
    )

    print(
        "Cho kiem duyet:",
        (
            len(verify_rows)
            - len(reviewed)
        ),
    )

    print()
    print(
        "FILE REVIEW:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "CHUA SUA DATABASE."
    )

    print(
        "CHUA GAN MaNguon=1004."
    )

    print(
        "CHUA INSERT NGU PHAP "
        "BAI 2 -> 23."
    )

    print()
    print(
        "BUOC TIEP THEO LA "
        "KIEM DUYET 7 MAPPING "
        "TRUOC KHI CAP NHAT SQL."
    )

    print()
    print("=" * 115)
    print("HOAN TAT")
    print("=" * 115)


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 115)
        print(
            "09H5 THAT BAI"
        )
        print("=" * 115)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)