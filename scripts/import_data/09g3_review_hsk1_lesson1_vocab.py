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
# NOI DUNG HOC TAP BAI 1
#
# LUU Y:
# - Day la noi dung hoc tap do do an kiem duyet.
# - Khong thay doi NghiaNguon / TuLoaiNguon.
# - Chi dien cac cot review.
# =========================================================
LESSON1_REVIEW = {
    "你": {
        "type": "Đại từ",
        "meaning": "bạn; cậu",
        "note": "Đại từ nhân xưng ngôi thứ hai.",
    },

    "好": {
        "type": "Tính từ",
        "meaning": "tốt; khỏe",
        "note": "Trong 你好 và 你好吗 thường dùng với nghĩa chào hỏi hoặc hỏi tình trạng.",
    },

    "我": {
        "type": "Đại từ",
        "meaning": "tôi; mình",
        "note": "Đại từ nhân xưng ngôi thứ nhất.",
    },

    "是": {
        "type": "Động từ",
        "meaning": "là",
        "note": "Dùng để xác định hoặc giới thiệu người, sự vật.",
    },

    "叫": {
        "type": "Động từ",
        "meaning": "gọi; tên là",
        "note": "Trong mẫu 我叫... dùng để giới thiệu tên.",
    },

    "什么": {
        "type": "Đại từ nghi vấn",
        "meaning": "gì; cái gì",
        "note": "Dùng để hỏi về sự vật, nội dung hoặc thông tin chưa biết.",
    },

    "名字": {
        "type": "Danh từ",
        "meaning": "tên; tên gọi",
        "note": "Thường dùng trong mẫu 你叫什么名字？",
    },

    "很": {
        "type": "Phó từ",
        "meaning": "rất",
        "note": "Đứng trước tính từ, ví dụ 很好、很高兴.",
    },

    "高兴": {
        "type": "Tính từ",
        "meaning": "vui; vui mừng",
        "note": "Dùng để diễn tả cảm xúc vui vẻ.",
    },

    "认识": {
        "type": "Động từ",
        "meaning": "biết; quen; làm quen",
        "note": "Trong 很高兴认识你 dùng với nghĩa làm quen/biết một người.",
    },

    "吗": {
        "type": "Trợ từ",
        "meaning": "trợ từ nghi vấn",
        "note": "Đặt cuối câu trần thuật để tạo câu hỏi có/không.",
    },

    "呢": {
        "type": "Trợ từ",
        "meaning": "trợ từ hỏi lại hoặc tiếp nối chủ đề",
        "note": "Ví dụ: 我很好，你呢？",
    },

    "也": {
        "type": "Phó từ",
        "meaning": "cũng",
        "note": "Dùng để diễn tả người hoặc sự việc có đặc điểm/hành động tương tự.",
    },
}


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 95)
    print("09G3 - KIEM DUYET TU VUNG BAI 1")
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
    # 3. KIEM TRA CAC COT CAN THIET
    # -----------------------------------------------------
    required_columns = {
        "SoThuTuBai",
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
    # 4. LAY 13 TU BAI 1
    # -----------------------------------------------------
    lesson1_rows = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == 1
    ]

    if len(lesson1_rows) != 13:

        raise RuntimeError(
            "Bai 1 phai co dung 13 tu. "
            f"Thuc te: {len(lesson1_rows)}"
        )

    actual_words = {
        row["ChuHan"].strip()
        for row in lesson1_rows
    }

    expected_words = set(
        LESSON1_REVIEW.keys()
    )

    if actual_words != expected_words:

        print()
        print("Tu trong CSV:")
        print(sorted(actual_words))

        print()
        print("Tu du kien:")
        print(sorted(expected_words))

        raise RuntimeError(
            "13 tu Bai 1 trong CSV "
            "khong khop danh sach da chot."
        )

    # -----------------------------------------------------
    # 5. TAO BACKUP TRUOC KHI SUA CSV
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
    # 6. DIEN REVIEW CHO BAI 1
    # -----------------------------------------------------
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 1:
            continue

        word = row["ChuHan"].strip()

        review = LESSON1_REVIEW[word]

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

    if updated != 13:

        raise RuntimeError(
            "So dong review Bai 1 "
            "khong bang 13."
        )

    # -----------------------------------------------------
    # 7. GHI LAI FILE REVIEW
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
    # 8. DOC LAI DE VERIFY
    # -----------------------------------------------------
    with open(
        REVIEW_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)
        verify_rows = list(reader)

    reviewed_lesson1 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) == 1
        and row["DaKiemDuyet"] == "1"
    ]

    if len(reviewed_lesson1) != 13:

        raise RuntimeError(
            "Verify that bai: "
            "Bai 1 khong co dung "
            "13 dong DaKiemDuyet=1."
        )

    # -----------------------------------------------------
    # 9. DAM BAO CAC BAI KHAC CHUA BI REVIEW
    # -----------------------------------------------------
    reviewed_other_lessons = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) != 1
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_other_lessons:

        raise RuntimeError(
            "Phat hien bai khac "
            "da bi danh DaKiemDuyet=1."
        )

    # -----------------------------------------------------
    # 10. IN KET QUA BAI 1
    # -----------------------------------------------------
    print()
    print("-" * 95)
    print("NOI DUNG BAI 1 SAU REVIEW")
    print("-" * 95)

    reviewed_lesson1.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    for row in reviewed_lesson1:

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
    # 11. TONG KET
    # -----------------------------------------------------
    reviewed_total = sum(
        1
        for row in verify_rows
        if row["DaKiemDuyet"] == "1"
    )

    unreviewed_total = (
        len(verify_rows)
        - reviewed_total
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
        len(reviewed_lesson1),
    )

    print(
        "Tong da kiem duyet:",
        reviewed_total,
    )

    print(
        "Con chua kiem duyet:",
        unreviewed_total,
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