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
COURSE_CODE = "HSK1-CORE"
LESSON_NO = 2

EXPECTED_VOCAB_COUNT = 29
EXPECTED_GRAMMAR_COUNT = 3

SOURCE_ID = 1004
SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"


# =========================================================
# FILES
# =========================================================
STANDARD_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "hsk1_48_grammar_standard.csv"
)

CONTEXT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "lesson_context"
    / "hsk1_lesson2_grammar_context.csv"
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
    / "hsk1_lesson2_grammar_review.csv"
)


# =========================================================
# NOI DUNG NGU PHAP BAI 2
#
# Luu y:
# - MaMucNguPhapChuan: tham chieu GF0025.
# - MoTa/CachDung/ViDu: noi dung hoc tap do do an
#   bien soan, khong sao chep nguyen van nguon.
# =========================================================
GRAMMAR_ITEMS = [

    # -----------------------------------------------------
    # 1. DAI TU NHAN XUNG
    # -----------------------------------------------------
    {
        "ThuTu": 1,

        "TenCauTruc": (
            "Đại từ nhân xưng: "
            "我 / 你 / 您 / 他 / 她 / "
            "我们 / 你们 / 他们 / 她们"
        ),

        "MoTa": (
            "Đại từ nhân xưng được dùng để chỉ người nói, "
            "người nghe hoặc người được nhắc đến. "
            "Trong tiếng Trung, 您 là cách gọi lịch sự của 你. "
            "Các dạng có 们 thường biểu thị số nhiều."
        ),

        "CachDung": (
            "我: tôi; 你: bạn; 您: ngài/bạn theo cách lịch sự; "
            "他: anh ấy; 她: cô ấy; 我们: chúng tôi/chúng ta; "
            "你们: các bạn; 他们: họ (nam hoặc nhóm chung); "
            "她们: họ (nữ). "
            "Đại từ nhân xưng thường đứng ở vị trí chủ ngữ "
            "hoặc tân ngữ trong câu."
        ),

        "ViDuTiengTrung": (
            "他们是中国人。"
        ),

        "ViDuPinyin": (
            "Tāmen shì Zhōngguó rén."
        ),

        "ViDuTiengViet": (
            "Họ là người Trung Quốc."
        ),

        "MaMucNguPhapChuan": (
            "GF1-005"
        ),

        "LoaiSuDung": (
            "gioi_thieu"
        ),

        "GhiChuNguon": (
            "Đối chiếu với mục 人称代词 của GF0025-2021."
        ),
    },

    # -----------------------------------------------------
    # 2. 是 - CAU GIOI THIEU / XAC DINH
    # -----------------------------------------------------
    {
        "ThuTu": 2,

        "TenCauTruc": (
            "A + 是 + B - giới thiệu quốc tịch hoặc thân phận"
        ),

        "MoTa": (
            "是 (shì) mang nghĩa 'là', dùng để nối chủ ngữ "
            "với danh từ hoặc cụm danh từ nhằm giới thiệu "
            "hoặc xác định quốc tịch, thân phận hay thông tin "
            "của một người."
        ),

        "CachDung": (
            "Cấu trúc: Chủ ngữ + 是 + danh từ/cụm danh từ. "
            "Trong Bài 2, cấu trúc này được mở rộng để nói "
            "về quốc tịch, ví dụ: 我是越南人, 他是中国人. "
            "Đây là cấu trúc đã xuất hiện ở Bài 1 và được "
            "ôn tập, mở rộng trong Bài 2."
        ),

        "ViDuTiengTrung": (
            "我是越南人。"
        ),

        "ViDuPinyin": (
            "Wǒ shì Yuènán rén."
        ),

        "ViDuTiengViet": (
            "Tôi là người Việt Nam."
        ),

        "MaMucNguPhapChuan": (
            "GF1-036"
        ),

        "LoaiSuDung": (
            "on_tap_mo_rong"
        ),

        "GhiChuNguon": (
            "Đối chiếu với mục “是”字句. "
            "Cấu trúc đã được giới thiệu ở Bài 1; "
            "Bài 2 mở rộng sang chủ đề quốc tịch."
        ),
    },

    # -----------------------------------------------------
    # 3. 谁 - HOI AI
    # -----------------------------------------------------
    {
        "ThuTu": 3,

        "TenCauTruc": (
            "谁 - hỏi 'ai'"
        ),

        "MoTa": (
            "谁 (shéi) là đại từ nghi vấn dùng để hỏi "
            "về người chưa biết hoặc cần xác định."
        ),

        "CachDung": (
            "谁 có thể đứng ở vị trí mà câu trả lời sẽ là "
            "một người. Khi câu đã có từ nghi vấn 谁 thì "
            "không cần thêm 吗 ở cuối câu. "
            "Ví dụ: 他是谁？ - Anh ấy là ai?"
        ),

        "ViDuTiengTrung": (
            "他是谁？"
        ),

        "ViDuPinyin": (
            "Tā shì shéi?"
        ),

        "ViDuTiengViet": (
            "Anh ấy là ai?"
        ),

        "MaMucNguPhapChuan": (
            "GF1-004;GF1-046"
        ),

        "LoaiSuDung": (
            "gioi_thieu"
        ),

        "GhiChuNguon": (
            "谁 thuộc nhóm 疑问代词 và đồng thời "
            "thuộc phương pháp 用疑问代词提问."
        ),
    },
]


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


def load_csv(path):

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


def parse_ids(text):

    return [
        item.strip()
        for item in clean(text).split(";")
        if item.strip()
    ]


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H10B - TAO NOI DUNG "
        "NGU PHAP BAI 2 HSK1"
    )
    print("=" * 115)

    print()
    print("CHE DO:")
    print("  DOC CONTEXT BAI 2")
    print("  DOC 48 MUC NGU PHAP CHUAN")
    print("  SELECT DATABASE DE DOI CHIEU")
    print("  TAO FILE REVIEW")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG UPDATE dbo.NguPhap")
    print("  KHONG DELETE")

    # =====================================================
    # 1. VERIFY GRAMMAR ITEMS
    # =====================================================
    print()
    print("[1] VERIFY 3 NGU PHAP DE XUAT")
    line()

    if (
        len(GRAMMAR_ITEMS)
        != EXPECTED_GRAMMAR_COUNT
    ):

        fail(
            "GRAMMAR_ITEMS phai co dung 3 muc."
        )

    expected_orders = [
        1,
        2,
        3,
    ]

    actual_orders = [
        item["ThuTu"]
        for item in GRAMMAR_ITEMS
    ]

    if actual_orders != expected_orders:

        fail(
            "ThuTu ngu phap phai la 1, 2, 3."
        )

    for item in GRAMMAR_ITEMS:

        required_values = [
            "TenCauTruc",
            "MoTa",
            "CachDung",
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
            "MaMucNguPhapChuan",
            "LoaiSuDung",
            "GhiChuNguon",
        ]

        for field in required_values:

            if not clean(
                item[field]
            ):

                fail(
                    f"ThuTu={item['ThuTu']} "
                    f"thieu {field}."
                )

    print(
        "Tong muc:",
        len(GRAMMAR_ITEMS),
    )

    print(
        "ThuTu 1 -> 3: OK"
    )

    print(
        "Noi dung trong: 0"
    )

    # =====================================================
    # 2. VERIFY STANDARD FILE
    # =====================================================
    print()
    print("[2] VERIFY 48 MUC GF0025")
    line()

    if not STANDARD_FILE.exists():

        fail(
            "Khong tim thay file:\n"
            f"{STANDARD_FILE}"
        )

    standard_fields, standard_rows = (
        load_csv(
            STANDARD_FILE
        )
    )

    if len(standard_rows) != 48:

        fail(
            "File chuan khong co dung 48 dong."
        )

    standard_by_id = {}

    for row in standard_rows:

        standard_id = clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )

        if standard_id in standard_by_id:

            fail(
                "MaMucNguPhapChuan bi trung."
            )

        if clean(
            row["MaNguon"]
        ) != "1004":

            fail(
                f"{standard_id} "
                "khong MaNguon=1004."
            )

        standard_by_id[
            standard_id
        ] = row

    for item in GRAMMAR_ITEMS:

        for standard_id in parse_ids(
            item[
                "MaMucNguPhapChuan"
            ]
        ):

            if standard_id not in (
                standard_by_id
            ):

                fail(
                    "Khong tim thay "
                    f"{standard_id}."
                )

    print(
        "48/48 muc: OK"
    )

    print(
        "Mapping 3 ngu phap: OK"
    )

    # =====================================================
    # 3. VERIFY CONTEXT FILE
    # =====================================================
    print()
    print("[3] VERIFY CONTEXT BAI 2")
    line()

    if not CONTEXT_FILE.exists():

        fail(
            "Khong tim thay context:\n"
            f"{CONTEXT_FILE}"
        )

    _, context_rows = load_csv(
        CONTEXT_FILE
    )

    vocab_rows = [
        row
        for row in context_rows
        if clean(
            row["LoaiDong"]
        ) == "tu_vung"
    ]

    standard_context_rows = [
        row
        for row in context_rows
        if clean(
            row["LoaiDong"]
        ) == "ngu_phap_chuan"
    ]

    if (
        len(vocab_rows)
        != EXPECTED_VOCAB_COUNT
    ):

        fail(
            "Context Bai 2 "
            "khong co dung 29 tu."
        )

    if (
        len(standard_context_rows)
        != 48
    ):

        fail(
            "Context Bai 2 "
            "khong co dung 48 muc GF1."
        )

    vocab_hanzi = {
        clean(
            row["NoiDungChinh"]
        )
        for row in vocab_rows
    }

    # Nhung tu quan trong phai co trong context Bai 2
    required_vocab = {
        "越南",
        "你们",
        "您",
        "他",
        "他们",
        "她",
        "她们",
        "谁",
        "人",
        "中国",
        "中文",
    }

    missing_vocab = (
        required_vocab
        - vocab_hanzi
    )

    if missing_vocab:

        fail(
            "Context Bai 2 thieu tu: "
            + ", ".join(
                sorted(missing_vocab)
            )
        )

    print(
        "Tu vung:",
        len(vocab_rows),
    )

    print(
        "Ngu phap chuan:",
        len(standard_context_rows),
    )

    print(
        "Tu quan trong cho ngu phap: OK"
    )

    # =====================================================
    # 4. CONNECT DATABASE
    # =====================================================
    print()
    print("[4] KET NOI DATABASE")
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
                # 5. FIND LESSON
                # =========================================
                print()
                print(
                    "[5] VERIFY BAI 2"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        bh.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe
                    FROM dbo.BaiHoc AS bh
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai = ?;
                    """,
                    COURSE_CODE,
                    LESSON_NO,
                )

                lesson_rows = (
                    cursor.fetchall()
                )

                if len(lesson_rows) != 1:

                    fail(
                        "Khong tim thay "
                        "dung 1 Bai 2."
                    )

                lesson_id = int(
                    lesson_rows[0][0]
                )

                lesson_title = clean(
                    lesson_rows[0][2]
                )

                print(
                    "MaBaiHoc:",
                    lesson_id,
                )

                print(
                    "TieuDe:",
                    lesson_title,
                )

                if (
                    lesson_title
                    != "我是越南人 - Tôi là người Việt Nam"
                ):

                    fail(
                        "Tieu de Bai 2 "
                        "khong dung mong doi."
                    )

                # =========================================
                # 6. ENSURE NO EXISTING GRAMMAR
                # =========================================
                print()
                print(
                    "[6] KIEM TRA dbo.NguPhap BAI 2"
                )
                line()

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap
                    WHERE MaBaiHoc = ?;
                    """,
                    lesson_id,
                )

                current_count = int(
                    cursor.fetchone()[0]
                )

                print(
                    "Ngu phap hien tai:",
                    current_count,
                )

                if current_count != 0:

                    fail(
                        "Bai 2 da co ngu phap. "
                        "Khong tao review moi "
                        "de tranh trung du lieu."
                    )

                print(
                    "BAI 2 CHUA CO NGU PHAP: OK"
                )

                # =========================================
                # 7. VERIFY SOURCE 1004
                # =========================================
                print()
                print(
                    "[7] VERIFY MaNguon=1004"
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
                        "Khong tim thay MaNguon=1004."
                    )

                if (
                    clean(
                        source_row[1]
                    )
                    != SOURCE_NAME
                ):

                    fail(
                        "MaNguon=1004 "
                        "khong phai nguon "
                        "ngu phap mong doi."
                    )

                print(
                    "MaNguon:",
                    int(source_row[0]),
                )

                print(
                    "Ten:",
                    clean(source_row[1]),
                )

                print(
                    "NGUON: OK"
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 8. BUILD REVIEW ROWS
    # =====================================================
    print()
    print("[8] TAO FILE REVIEW")
    line()

    REVIEW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_rows = []

    for item in GRAMMAR_ITEMS:

        mapped_ids = parse_ids(
            item[
                "MaMucNguPhapChuan"
            ]
        )

        mapped_names = []

        mapped_contents = []

        for standard_id in mapped_ids:

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
                "SoThuTuBai": (
                    LESSON_NO
                ),

                "MaBaiHoc": (
                    lesson_id
                ),

                "TieuDeBai": (
                    lesson_title
                ),

                "ThuTuTrongBai": (
                    item["ThuTu"]
                ),

                "TenCauTruc": (
                    item["TenCauTruc"]
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

                "MaMucNguPhapChuan": (
                    item[
                        "MaMucNguPhapChuan"
                    ]
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

                "LoaiSuDung": (
                    item[
                        "LoaiSuDung"
                    ]
                ),

                "MaNguon": (
                    SOURCE_ID
                ),

                "MaTep": "",

                "TrangThai": (
                    "ban_nhap"
                ),

                "GhiChuNguon": (
                    item[
                        "GhiChuNguon"
                    ]
                ),

                "DaKiemDuyetNoiDung": (
                    0
                ),

                "GhiChuKiemDuyet": "",
            }
        )

    fieldnames = [
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuTrongBai",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaMucNguPhapChuan",
        "TenMucChuan",
        "NoiDungChuan",
        "LoaiSuDung",
        "MaNguon",
        "MaTep",
        "TrangThai",
        "GhiChuNguon",
        "DaKiemDuyetNoiDung",
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

    # =====================================================
    # 9. VERIFY OUTPUT
    # =====================================================
    print()
    print("[9] VERIFY FILE REVIEW")
    line()

    _, verify_rows = load_csv(
        OUTPUT_FILE
    )

    if len(verify_rows) != 3:

        fail(
            "File review phai co dung 3 dong."
        )

    orders = [
        int(
            clean(
                row["ThuTuTrongBai"]
            )
        )
        for row in verify_rows
    ]

    if orders != [
        1,
        2,
        3,
    ]:

        fail(
            "ThuTuTrongBai "
            "khong dung 1,2,3."
        )

    missing_content = []

    for row in verify_rows:

        for field in [
            "TenCauTruc",
            "MoTa",
            "CachDung",
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
            "MaMucNguPhapChuan",
            "GhiChuNguon",
        ]:

            if not clean(
                row[field]
            ):

                missing_content.append(
                    (
                        row[
                            "ThuTuTrongBai"
                        ],
                        field,
                    )
                )

    if missing_content:

        fail(
            "File review co noi dung bi trong."
        )

    wrong_source = [
        row
        for row in verify_rows
        if clean(
            row["MaNguon"]
        ) != "1004"
    ]

    if wrong_source:

        fail(
            "Co dong MaNguon khong bang 1004."
        )

    wrong_status = [
        row
        for row in verify_rows
        if clean(
            row["TrangThai"]
        ) != "ban_nhap"
    ]

    if wrong_status:

        fail(
            "Co dong TrangThai "
            "khong bang ban_nhap."
        )

    approved = [
        row
        for row in verify_rows
        if clean(
            row[
                "DaKiemDuyetNoiDung"
            ]
        ) == "1"
    ]

    print(
        "Tong ngu phap:",
        len(verify_rows),
    )

    print(
        "Noi dung day du:",
        len(verify_rows),
    )

    print(
        "MaNguon=1004:",
        len(verify_rows),
    )

    print(
        "TrangThai=ban_nhap:",
        len(verify_rows),
    )

    print(
        "DaKiemDuyetNoiDung=1:",
        len(approved),
    )

    print(
        "Cho kiem duyet:",
        (
            len(verify_rows)
            - len(approved)
        ),
    )

    # =====================================================
    # 10. PRINT CONTENT
    # =====================================================
    print()
    print(
        "[10] NOI DUNG NGU PHAP BAI 2"
    )
    line()

    for row in verify_rows:

        print()
        print(
            f"[{row['ThuTuTrongBai']}] "
            f"{row['TenCauTruc']}"
        )

        print(
            "  MoTa:",
            row["MoTa"],
        )

        print(
            "  CachDung:",
            row["CachDung"],
        )

        print(
            "  ViDuTiengTrung:",
            row[
                "ViDuTiengTrung"
            ],
        )

        print(
            "  ViDuPinyin:",
            row[
                "ViDuPinyin"
            ],
        )

        print(
            "  ViDuTiengViet:",
            row[
                "ViDuTiengViet"
            ],
        )

        print(
            "  MaMucChuan:",
            row[
                "MaMucNguPhapChuan"
            ],
        )

        print(
            "  LoaiSuDung:",
            row["LoaiSuDung"],
        )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 115)
    print(
        "KET QUA 09H10B"
    )
    print("=" * 115)

    print(
        "Bai:",
        LESSON_NO,
        "-",
        lesson_title,
    )

    print(
        "Tu vung context:",
        len(vocab_rows),
    )

    print(
        "Ngu phap de xuat:",
        len(verify_rows),
    )

    print(
        "Da kiem duyet:",
        len(approved),
    )

    print(
        "Cho kiem duyet:",
        (
            len(verify_rows)
            - len(approved)
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
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA INSERT NGU PHAP BAI 2."
    )

    print()
    print(
        "BUOC TIEP THEO:"
    )

    print(
        "AUDIT + KIEM DUYET 3 MUC, "
        "SAU DO BACKUP + INSERT BAI 2."
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
            "09H10B THAT BAI"
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