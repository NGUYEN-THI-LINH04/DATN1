from pathlib import Path
import csv
import shutil
import sys
from datetime import datetime


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]


# =========================================================
# FILES
# =========================================================
REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lesson1_grammar_mapping_review.csv"
)

BACKUP_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "backup"
)


# =========================================================
# EXPECTED REVIEW
# =========================================================
EXPECTED = {

    1: {
        "TenCauTruc": "A + 是 + B",
        "MaMucNguPhapChuan": "GF1-036",
        "LoaiDoiChieu": "truc_tiep",
        "MucDoTinCay": "cao",
        "GhiChuKiemDuyet": (
            "Đã đối chiếu. Cấu trúc A + 是 + B "
            "phù hợp trực tiếp với mục “是”字句."
        ),
    },

    2: {
        "TenCauTruc": "Chủ ngữ + 叫 + tên",
        "MaMucNguPhapChuan": "GF1-029",
        "LoaiDoiChieu": "theo_kieu_cau",
        "MucDoTinCay": "trung_binh",
        "GhiChuKiemDuyet": (
            "Đã đối chiếu theo kiểu câu. "
            "叫 không phải một mục độc lập trong danh sách 48; "
            "mẫu Chủ ngữ + 叫 + tên được xếp theo "
            "主谓句1：动词谓语句. "
            "Không coi đây là đối chiếu trực tiếp."
        ),
    },

    3: {
        "TenCauTruc": '什么 - hỏi "gì / cái gì"',
        "MaMucNguPhapChuan": "GF1-004;GF1-046",
        "LoaiDoiChieu": "nhieu_muc",
        "MucDoTinCay": "cao",
        "GhiChuKiemDuyet": (
            "Đã đối chiếu. 什么 vừa thuộc 疑问代词 "
            "vừa thuộc phương pháp 用疑问代词提问."
        ),
    },

    4: {
        "TenCauTruc": "Câu trần thuật + 吗？",
        "MaMucNguPhapChuan": "GF1-022;GF1-045",
        "LoaiDoiChieu": "nhieu_muc",
        "MucDoTinCay": "cao",
        "GhiChuKiemDuyet": (
            "Đã đối chiếu. 吗 vừa thuộc 语气助词 "
            "vừa có mục riêng 用“吗”提问."
        ),
    },

    5: {
        "TenCauTruc": "...呢？ - hỏi lại hoặc tiếp nối",
        "MaMucNguPhapChuan": "GF1-022",
        "LoaiDoiChieu": "truc_tiep",
        "MucDoTinCay": "cao",
        "GhiChuKiemDuyet": (
            "Đã đối chiếu. 呢 thuộc nhóm 语气助词."
        ),
    },

    6: {
        "TenCauTruc": "很 + tính từ",
        "MaMucNguPhapChuan": "GF1-009;GF1-030",
        "LoaiDoiChieu": "nhieu_muc",
        "MucDoTinCay": "cao",
        "GhiChuKiemDuyet": (
            "Đã đối chiếu. 很 thuộc 程度副词; "
            "mẫu vị ngữ tính từ đồng thời liên quan "
            "主谓句2：形容词谓语句."
        ),
    },

    7: {
        "TenCauTruc": '也 - "cũng"',
        "MaMucNguPhapChuan": "GF1-013",
        "LoaiDoiChieu": "truc_tiep",
        "MucDoTinCay": "cao",
        "GhiChuKiemDuyet": (
            "Đã đối chiếu. 也 thuộc nhóm 关联副词：还、也."
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
                f"Không đọc được header:\n{path}"
            )

        return reader.fieldnames, list(reader)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H6 - KIEM DUYET 7 MAPPING NGU PHAP BAI 1"
    )
    print("=" * 115)

    print()
    print("CHE DO:")
    print("  CHI DOC / SUA FILE REVIEW CSV")
    print("  KHONG KET NOI DATABASE")
    print("  KHONG UPDATE dbo.NguPhap")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG GAN MaNguon=1004")

    # =====================================================
    # 1. CHECK FILE
    # =====================================================
    print()
    print("[1] DOC FILE REVIEW")
    print("-" * 115)

    if not REVIEW_FILE.exists():

        fail(
            "Không tìm thấy file review:\n"
            f"{REVIEW_FILE}"
        )

    fieldnames, rows = load_csv(
        REVIEW_FILE
    )

    required_fields = {
        "MaNguPhap",
        "TenCauTruc",
        "MaNguonHienTai",
        "MaNguonDeXuat",
        "MaMucNguPhapChuan",
        "LoaiDoiChieu",
        "MucDoTinCay",
        "DaKiemDuyetMapping",
        "GhiChuKiemDuyet",
    }

    missing_fields = (
        required_fields
        - set(fieldnames)
    )

    if missing_fields:

        fail(
            "File review thiếu cột: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if len(rows) != 7:

        fail(
            "File review phải có đúng 7 dòng. "
            f"Thực tế: {len(rows)}"
        )

    print(
        "Tổng dòng:",
        len(rows),
    )

    # =====================================================
    # 2. VERIFY EACH ROW
    # =====================================================
    print()
    print("[2] KIEM TRA 7 MAPPING")
    print("-" * 115)

    seen_ids = set()

    for row in rows:

        grammar_id_text = clean(
            row["MaNguPhap"]
        )

        if not grammar_id_text.isdigit():

            fail(
                "MaNguPhap không hợp lệ: "
                f"{grammar_id_text}"
            )

        grammar_id = int(
            grammar_id_text
        )

        if grammar_id in seen_ids:

            fail(
                "MaNguPhap bị trùng: "
                f"{grammar_id}"
            )

        seen_ids.add(
            grammar_id
        )

        if grammar_id not in EXPECTED:

            fail(
                "MaNguPhap không mong đợi: "
                f"{grammar_id}"
            )

        expected = EXPECTED[
            grammar_id
        ]

        if (
            clean(
                row["TenCauTruc"]
            )
            != expected["TenCauTruc"]
        ):

            fail(
                f"Sai TenCauTruc "
                f"MaNguPhap={grammar_id}"
            )

        if (
            clean(
                row[
                    "MaMucNguPhapChuan"
                ]
            )
            != expected[
                "MaMucNguPhapChuan"
            ]
        ):

            fail(
                f"Sai mapping chuẩn "
                f"MaNguPhap={grammar_id}"
            )

        if (
            clean(
                row["LoaiDoiChieu"]
            )
            != expected[
                "LoaiDoiChieu"
            ]
        ):

            fail(
                f"Sai LoaiDoiChieu "
                f"MaNguPhap={grammar_id}"
            )

        if (
            clean(
                row["MucDoTinCay"]
            )
            != expected[
                "MucDoTinCay"
            ]
        ):

            fail(
                f"Sai MucDoTinCay "
                f"MaNguPhap={grammar_id}"
            )

        if (
            clean(
                row["MaNguonHienTai"]
            )
            != ""
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "đã có MaNguon trong file review."
            )

        if (
            clean(
                row["MaNguonDeXuat"]
            )
            != "1004"
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "không đề xuất MaNguon=1004."
            )

        current_review = clean(
            row[
                "DaKiemDuyetMapping"
            ]
        )

        if current_review not in {
            "0",
            "1",
        }:

            fail(
                f"DaKiemDuyetMapping "
                f"không hợp lệ "
                f"MaNguPhap={grammar_id}"
            )

        print(
            f"MaNguPhap={grammar_id} | "
            f"{row['TenCauTruc']} | "
            f"{row['MaMucNguPhapChuan']} | "
            "OK"
        )

    if seen_ids != set(
        EXPECTED.keys()
    ):

        fail(
            "Danh sách MaNguPhap "
            "không đúng 1 -> 7."
        )

    print()
    print(
        "7/7 MAPPING: HỢP LỆ"
    )

    # =====================================================
    # 3. BACKUP CURRENT REVIEW
    # =====================================================
    print()
    print("[3] BACKUP FILE REVIEW")
    print("-" * 115)

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = (
        BACKUP_DIR
        / (
            "hsk1_lesson1_grammar_mapping_review_"
            f"before_approve_{timestamp}.csv"
        )
    )

    shutil.copy2(
        REVIEW_FILE,
        backup_file,
    )

    print(
        "Backup:"
    )

    print(
        backup_file
    )

    # =====================================================
    # 4. CONFIRM
    # =====================================================
    print()
    print("=" * 115)
    print("XAC NHAN KIEM DUYET")
    print("=" * 115)

    print()
    print(
        "Sau bước này chỉ file CSV review "
        "được cập nhật."
    )

    print(
        "Database KHÔNG bị sửa."
    )

    confirmation = input(
        "Nhap chinh xac "
        "APPROVE LESSON1 GRAMMAR MAPPING "
        "de tiep tuc: "
    ).strip()

    if (
        confirmation
        != "APPROVE LESSON1 GRAMMAR MAPPING"
    ):

        print()
        print(
            "Không nhận được xác nhận."
        )

        print(
            "File review không bị sửa."
        )

        return

    # =====================================================
    # 5. APPLY REVIEW TO CSV
    # =====================================================
    print()
    print("[4] CAP NHAT FILE REVIEW")
    print("-" * 115)

    for row in rows:

        grammar_id = int(
            clean(
                row["MaNguPhap"]
            )
        )

        expected = EXPECTED[
            grammar_id
        ]

        row[
            "DaKiemDuyetMapping"
        ] = "1"

        row[
            "GhiChuKiemDuyet"
        ] = expected[
            "GhiChuKiemDuyet"
        ]

    with open(
        REVIEW_FILE,
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
            rows
        )

    print(
        "Đã cập nhật:"
    )

    print(
        REVIEW_FILE
    )

    # =====================================================
    # 6. VERIFY AFTER WRITE
    # =====================================================
    print()
    print("[5] VERIFY SAU KIEM DUYET")
    print("-" * 115)

    _, verify_rows = load_csv(
        REVIEW_FILE
    )

    if len(verify_rows) != 7:

        fail(
            "File sau kiểm duyệt "
            "không còn đúng 7 dòng."
        )

    approved_count = 0
    note_missing = 0

    for row in verify_rows:

        grammar_id = int(
            clean(
                row["MaNguPhap"]
            )
        )

        if (
            clean(
                row[
                    "DaKiemDuyetMapping"
                ]
            )
            == "1"
        ):

            approved_count += 1

        if not clean(
            row[
                "GhiChuKiemDuyet"
            ]
        ):

            note_missing += 1

        expected = EXPECTED[
            grammar_id
        ]

        if (
            clean(
                row[
                    "MaMucNguPhapChuan"
                ]
            )
            != expected[
                "MaMucNguPhapChuan"
            ]
        ):

            fail(
                "Mapping bị thay đổi "
                "sau khi ghi file."
            )

    print(
        "Tổng mapping:",
        len(verify_rows),
    )

    print(
        "DaKiemDuyetMapping=1:",
        approved_count,
    )

    print(
        "Thiếu GhiChuKiemDuyet:",
        note_missing,
    )

    if approved_count != 7:

        fail(
            "Không có đủ 7 mapping "
            "được kiểm duyệt."
        )

    if note_missing != 0:

        fail(
            "Có mapping thiếu "
            "GhiChuKiemDuyet."
        )

    print(
        "VERIFY: OK"
    )

    # =====================================================
    # 7. PRINT RESULT
    # =====================================================
    print()
    print("[6] KET QUA KIEM DUYET")
    print("-" * 115)

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
            "  DaKiemDuyetMapping:",
            row[
                "DaKiemDuyetMapping"
            ],
        )

        print(
            "  GhiChuKiemDuyet:",
            row[
                "GhiChuKiemDuyet"
            ],
        )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 115)
    print(
        "KET QUA 09H6"
    )
    print("=" * 115)

    print(
        "Tong mapping:",
        len(verify_rows),
    )

    print(
        "Da kiem duyet:",
        approved_count,
    )

    print(
        "Chua kiem duyet:",
        (
            len(verify_rows)
            - approved_count
        ),
    )

    print(
        "Thieu ghi chu:",
        note_missing,
    )

    print()
    print(
        "7/7 MAPPING BAI 1 "
        "DA DUOC KIEM DUYET."
    )

    print()
    print(
        "DATABASE CHUA BI SUA."
    )

    print(
        "CHUA GAN MaNguon=1004 "
        "CHO dbo.NguPhap."
    )

    print(
        "CHUA INSERT NGU PHAP "
        "BAI 2 -> 23."
    )

    print()
    print(
        "Backup truoc kiem duyet:"
    )

    print(
        backup_file
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
            "09H6 THAT BAI"
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