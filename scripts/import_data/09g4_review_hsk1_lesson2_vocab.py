from pathlib import Path
import csv
import sys
from datetime import datetime


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
    / "hsk1_501_vocab_review.csv"
)


# =========================================================
# NOI DUNG HOC TAP BAI 2
#
# BAI 2:
# 我是越南人 - Tôi là người Việt Nam
#
# 28 tu HSK1 + 1 tu bo sung 越南
#
# CHI DIEN NOI DUNG REVIEW.
# KHONG SUA DU LIEU NGUON.
# KHONG SUA DATABASE.
# =========================================================
LESSON2_REVIEW = {

    "国": {
        "type": "Danh từ",
        "meaning": "nước; quốc gia",
        "note": (
            "Thường xuất hiện trong các từ ghép liên quan "
            "đến quốc gia, ví dụ 中国、外国."
        ),
    },

    "国家": {
        "type": "Danh từ",
        "meaning": "quốc gia; đất nước",
        "note": (
            "Dùng để chỉ một quốc gia hoặc đất nước."
        ),
    },

    "国外": {
        "type": "Danh từ chỉ nơi chốn",
        "meaning": "nước ngoài; ở nước ngoài",
        "note": (
            "Chỉ khu vực hoặc địa điểm bên ngoài "
            "quốc gia của người nói."
        ),
    },

    "汉语": {
        "type": "Danh từ",
        "meaning": "tiếng Trung; tiếng Hán",
        "note": (
            "Tên gọi ngôn ngữ Hán; trong bài học "
            "được dùng với nghĩa tiếng Trung."
        ),
    },

    "汉字": {
        "type": "Danh từ",
        "meaning": "chữ Hán",
        "note": (
            "Chỉ hệ thống chữ viết bằng chữ Hán."
        ),
    },

    "介绍": {
        "type": "Động từ",
        "meaning": "giới thiệu",
        "note": (
            "Dùng khi giới thiệu bản thân hoặc "
            "giới thiệu một người, sự vật."
        ),
    },

    "男": {
        "type": "Danh từ / tính từ",
        "meaning": "nam; đàn ông",
        "note": (
            "Dùng để chỉ giới tính nam hoặc đứng trước "
            "danh từ để chỉ người nam."
        ),
    },

    "男人": {
        "type": "Danh từ",
        "meaning": "đàn ông; nam giới",
        "note": (
            "Chỉ một người đàn ông trưởng thành."
        ),
    },

    "男生": {
        "type": "Danh từ",
        "meaning": "nam sinh; học sinh nam",
        "note": (
            "Chỉ học sinh hoặc sinh viên nam."
        ),
    },

    "你们": {
        "type": "Đại từ",
        "meaning": "các bạn; các cậu",
        "note": (
            "Dạng số nhiều của 你."
        ),
    },

    "您": {
        "type": "Đại từ",
        "meaning": "ông; bà; ngài; bạn",
        "note": (
            "Cách nói lịch sự, kính trọng của 你."
        ),
    },

    "女": {
        "type": "Danh từ / tính từ",
        "meaning": "nữ; phụ nữ",
        "note": (
            "Dùng để chỉ giới tính nữ hoặc đứng trước "
            "danh từ để chỉ người nữ."
        ),
    },

    "女人": {
        "type": "Danh từ",
        "meaning": "phụ nữ; người phụ nữ",
        "note": (
            "Chỉ một người phụ nữ trưởng thành."
        ),
    },

    "女生": {
        "type": "Danh từ",
        "meaning": "nữ sinh; học sinh nữ",
        "note": (
            "Chỉ học sinh hoặc sinh viên nữ."
        ),
    },

    "人": {
        "type": "Danh từ",
        "meaning": "người",
        "note": (
            "Có thể kết hợp với tên quốc gia để chỉ "
            "người thuộc quốc gia đó, ví dụ 中国人."
        ),
    },

    "谁": {
        "type": "Đại từ nghi vấn",
        "meaning": "ai",
        "note": (
            "Dùng để hỏi về người."
        ),
    },

    "他": {
        "type": "Đại từ",
        "meaning": "anh ấy; ông ấy",
        "note": (
            "Đại từ nhân xưng ngôi thứ ba số ít, "
            "thường dùng cho nam."
        ),
    },

    "他们": {
        "type": "Đại từ",
        "meaning": "họ; bọn họ",
        "note": (
            "Đại từ nhân xưng ngôi thứ ba số nhiều."
        ),
    },

    "她": {
        "type": "Đại từ",
        "meaning": "cô ấy; bà ấy",
        "note": (
            "Đại từ nhân xưng ngôi thứ ba số ít "
            "dùng cho nữ."
        ),
    },

    "她们": {
        "type": "Đại từ",
        "meaning": "họ; các cô ấy",
        "note": (
            "Đại từ nhân xưng số nhiều dùng cho "
            "một nhóm nữ."
        ),
    },

    "外国": {
        "type": "Danh từ",
        "meaning": "nước ngoài; quốc gia nước ngoài",
        "note": (
            "Chỉ một quốc gia khác với quốc gia "
            "của người nói."
        ),
    },

    "外语": {
        "type": "Danh từ",
        "meaning": "ngoại ngữ",
        "note": (
            "Chỉ ngôn ngữ nước ngoài."
        ),
    },

    "我们": {
        "type": "Đại từ",
        "meaning": "chúng tôi; chúng ta",
        "note": (
            "Đại từ nhân xưng ngôi thứ nhất số nhiều."
        ),
    },

    "先生": {
        "type": "Danh từ / cách xưng hô",
        "meaning": "ông; ngài; tiên sinh",
        "note": (
            "Cách xưng hô lịch sự đối với nam giới, "
            "thường dùng sau họ."
        ),
    },

    "小姐": {
        "type": "Danh từ / cách xưng hô",
        "meaning": "cô; tiểu thư",
        "note": (
            "Cách xưng hô với phụ nữ trẻ; sắc thái sử dụng "
            "có thể thay đổi tùy khu vực và ngữ cảnh."
        ),
    },

    "有名": {
        "type": "Tính từ",
        "meaning": "nổi tiếng; có tiếng",
        "note": (
            "Dùng để nói một người, địa điểm hoặc sự vật "
            "được nhiều người biết đến."
        ),
    },

    "中国": {
        "type": "Danh từ riêng",
        "meaning": "Trung Quốc",
        "note": (
            "Tên quốc gia."
        ),
    },

    "中文": {
        "type": "Danh từ",
        "meaning": "tiếng Trung; tiếng Trung Quốc",
        "note": (
            "Dùng để chỉ tiếng Trung hoặc nội dung "
            "được viết bằng tiếng Trung."
        ),
    },

    "越南": {
        "type": "Danh từ riêng",
        "meaning": "Việt Nam",
        "note": (
            "Từ bổ sung phục vụ chủ đề Bài 2; "
            "không tính trong 500 từ HSK1 chuẩn."
        ),
    },
}


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 95)
    print("09G4 - KIEM DUYET TU VUNG BAI 2")
    print("=" * 95)

    # -----------------------------------------------------
    # 1. KIEM TRA FILE
    # -----------------------------------------------------
    if not REVIEW_FILE.exists():

        raise RuntimeError(
            "Khong tim thay file review:\n"
            f"{REVIEW_FILE}"
        )

    # -----------------------------------------------------
    # 2. DOC CSV
    # -----------------------------------------------------
    with open(
        REVIEW_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        fieldnames = reader.fieldnames

        if not fieldnames:

            raise RuntimeError(
                "Khong doc duoc header CSV."
            )

        rows = list(reader)

    if len(rows) != 501:

        raise RuntimeError(
            "File review phai co 501 dong. "
            f"Thuc te: {len(rows)}"
        )

    # -----------------------------------------------------
    # 3. KIEM TRA CAC COT
    # -----------------------------------------------------
    required_columns = {
        "SoThuTuBai",
        "ThuTuTrongBai",
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "TuLoaiNguon",
        "NghiaNguon",
        "TuLoaiHocTap",
        "NghiaHocTap",
        "GhiChuKiemDuyet",
        "DaKiemDuyet",
    }

    missing_columns = (
        required_columns
        - set(fieldnames)
    )

    if missing_columns:

        raise RuntimeError(
            "CSV thieu cot: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    # -----------------------------------------------------
    # 4. DAM BAO BAI 1 DA REVIEW DU 13
    # -----------------------------------------------------
    lesson1_rows = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == 1
    ]

    reviewed_lesson1 = [
        row
        for row in lesson1_rows
        if row["DaKiemDuyet"] == "1"
    ]

    if len(lesson1_rows) != 13:

        raise RuntimeError(
            "Bai 1 khong co dung 13 tu."
        )

    if len(reviewed_lesson1) != 13:

        raise RuntimeError(
            "Bai 1 chua duoc kiem duyet "
            "du 13 tu. Khong tiep tuc Bai 2."
        )

    # -----------------------------------------------------
    # 5. LAY 29 TU BAI 2
    # -----------------------------------------------------
    lesson2_rows = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == 2
    ]

    if len(lesson2_rows) != 29:

        raise RuntimeError(
            "Bai 2 phai co dung 29 tu. "
            f"Thuc te: {len(lesson2_rows)}"
        )

    actual_words = {
        row["ChuHan"].strip()
        for row in lesson2_rows
    }

    expected_words = set(
        LESSON2_REVIEW.keys()
    )

    if actual_words != expected_words:

        missing_words = (
            expected_words
            - actual_words
        )

        extra_words = (
            actual_words
            - expected_words
        )

        print()
        print(
            "Tu thieu so voi script:",
            sorted(missing_words),
        )

        print(
            "Tu du so voi script:",
            sorted(extra_words),
        )

        raise RuntimeError(
            "Danh sach 29 tu Bai 2 "
            "khong khop noi dung review."
        )

    # -----------------------------------------------------
    # 6. DAM BAO BAI 2 CHUA REVIEW TRUOC DO
    # -----------------------------------------------------
    already_reviewed = [
        row
        for row in lesson2_rows
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 2 da co tu duoc "
            "DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # -----------------------------------------------------
    # 7. DAM BAO BAI 3 -> 23 CHUA BI REVIEW
    # -----------------------------------------------------
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 3
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 3 -> 23 "
            "da co dong DaKiemDuyet=1."
        )

    # -----------------------------------------------------
    # 8. BACKUP
    # -----------------------------------------------------
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = REVIEW_FILE.with_name(
        f"hsk1_501_vocab_review_backup_{timestamp}.csv"
    )

    with open(
        backup_file,
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

    print()
    print("Da tao backup:")
    print(backup_file)

    # -----------------------------------------------------
    # 9. DIEN REVIEW BAI 2
    # -----------------------------------------------------
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 2:
            continue

        word = row["ChuHan"].strip()

        review = LESSON2_REVIEW[word]

        row["TuLoaiHocTap"] = (
            review["type"]
        )

        row["NghiaHocTap"] = (
            review["meaning"]
        )

        row["GhiChuKiemDuyet"] = (
            review["note"]
        )

        row["DaKiemDuyet"] = "1"

        updated += 1

    if updated != 29:

        raise RuntimeError(
            "So dong cap nhat Bai 2 "
            "khong bang 29."
        )

    # -----------------------------------------------------
    # 10. GHI LAI FILE
    # -----------------------------------------------------
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
        writer.writerows(rows)

    # -----------------------------------------------------
    # 11. DOC LAI VERIFY
    # -----------------------------------------------------
    with open(
        REVIEW_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        verify_rows = list(reader)

    lesson1_verified = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) == 1
        and row["DaKiemDuyet"] == "1"
    ]

    lesson2_verified = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) == 2
        and row["DaKiemDuyet"] == "1"
    ]

    if len(lesson1_verified) != 13:

        raise RuntimeError(
            "Sau khi ghi file, "
            "Bai 1 khong con du 13 tu review."
        )

    if len(lesson2_verified) != 29:

        raise RuntimeError(
            "Sau khi ghi file, "
            "Bai 2 khong co du 29 tu review."
        )

    # -----------------------------------------------------
    # 12. DAM BAO CAC BAI SAU VAN = 0
    # -----------------------------------------------------
    reviewed_after_lesson2 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 3
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson2:

        raise RuntimeError(
            "Bai 3 -> 23 bi thay doi ngoai y muon."
        )

    # -----------------------------------------------------
    # 13. IN NOI DUNG BAI 2
    # -----------------------------------------------------
    lesson2_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 2 SAU REVIEW")
    print("-" * 95)

    for row in lesson2_verified:

        print()
        print(
            f"{row['ThuTuTrongBai']:>2}. "
            f"{row['ChuHan']} "
            f"[{row['PhienAm']}]"
        )

        print(
            "    Tu loai:",
            row["TuLoaiHocTap"],
        )

        print(
            "    Nghia  :",
            row["NghiaHocTap"],
        )

        print(
            "    Ghi chu:",
            row["GhiChuKiemDuyet"],
        )

    # -----------------------------------------------------
    # 14. KIEM TRA 越南
    # -----------------------------------------------------
    vietnam_rows = [
        row
        for row in lesson2_verified
        if row["ChuHan"].strip() == "越南"
    ]

    if len(vietnam_rows) != 1:

        raise RuntimeError(
            "Khong tim thay duy nhat 越南 "
            "trong Bai 2."
        )

    vietnam = vietnam_rows[0]

    if vietnam["MaNguon"] != "2":

        raise RuntimeError(
            "越南 khong con MaNguon=2."
        )

    # -----------------------------------------------------
    # 15. TONG KET
    # -----------------------------------------------------
    total_reviewed = sum(
        1
        for row in verify_rows
        if row["DaKiemDuyet"] == "1"
    )

    total_unreviewed = (
        len(verify_rows)
        - total_reviewed
    )

    print()
    print("=" * 95)
    print("KET QUA")
    print("=" * 95)

    print(
        "Tong tu trong file:",
        len(verify_rows),
    )

    print(
        "Bai 1 da kiem duyet:",
        len(lesson1_verified),
    )

    print(
        "Bai 2 da kiem duyet:",
        len(lesson2_verified),
    )

    print(
        "Tong da kiem duyet:",
        total_reviewed,
    )

    print(
        "Con chua kiem duyet:",
        total_unreviewed,
    )

    print()
    print(
        "越南:"
    )

    print(
        "  Pinyin :",
        vietnam["PhienAm"],
    )

    print(
        "  Nghia  :",
        vietnam["NghiaHocTap"],
    )

    print(
        "  Nguon  : MaNguon=2 "
        "(CC-CEDICT)"
    )

    print(
        "  Loai   : TU BO SUNG, "
        "khong tinh vao 500 tu HSK1."
    )

    print()
    print(
        "FILE REVIEW DA DUOC CAP NHAT."
    )

    print(
        "DATABASE CHUA BI SUA."
    )

    print()
    print("=" * 95)
    print("HOAN TAT")
    print("=" * 95)


if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        print()
        print("=" * 95)
        print("THUC HIEN THAT BAI")
        print("=" * 95)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)