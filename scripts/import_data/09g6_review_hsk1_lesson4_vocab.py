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
# NOI DUNG HOC TAP BAI 4
#
# 你今年几岁？ - Năm nay bạn bao nhiêu tuổi?
#
# 26 tu:
# So dem + tuoi + luong tu co ban
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON4_REVIEW = {

    "八": {
        "type": "Số từ",
        "meaning": "tám; 8",
        "note": "Số đếm 8.",
    },

    "百": {
        "type": "Số từ",
        "meaning": "một trăm; 100",
        "note": "Đơn vị số đếm hàng trăm.",
    },

    "半": {
        "type": "Số từ",
        "meaning": "một nửa; nửa",
        "note": (
            "Dùng để chỉ một nửa của số lượng "
            "hoặc khoảng thời gian."
        ),
    },

    "杯": {
        "type": "Lượng từ",
        "meaning": "cốc; ly",
        "note": (
            "Lượng từ dùng cho đồ uống hoặc "
            "chất lỏng đựng trong cốc, ly, "
            "ví dụ 一杯水."
        ),
    },

    "本": {
        "type": "Lượng từ",
        "meaning": "quyển; cuốn",
        "note": (
            "Lượng từ dùng cho sách, vở, "
            "tạp chí và các tài liệu đóng quyển, "
            "ví dụ 一本书."
        ),
    },

    "次": {
        "type": "Lượng từ",
        "meaning": "lần",
        "note": (
            "Dùng để đếm số lần một hành động "
            "hoặc sự việc xảy ra."
        ),
    },

    "第（第二）": {
        "type": "Tiền tố",
        "meaning": "thứ; thứ hai",
        "note": (
            "第 đặt trước số đếm để tạo số thứ tự, "
            "ví dụ 第二 là 'thứ hai'."
        ),
    },

    "多": {
        "type": "Tính từ / đại từ",
        "meaning": "nhiều; hơn",
        "note": (
            "Trong bài này học nghĩa số lượng nhiều "
            "và cách dùng sau số để chỉ số lẻ, "
            "ví dụ 二十多岁."
        ),
    },

    "多少": {
        "type": "Đại từ nghi vấn",
        "meaning": "bao nhiêu",
        "note": (
            "Dùng để hỏi số lượng hoặc con số "
            "khi chưa biết cụ thể."
        ),
    },

    "二": {
        "type": "Số từ",
        "meaning": "hai; 2",
        "note": (
            "Số đếm 2. Cần phân biệt với 两 "
            "khi đứng trước lượng từ."
        ),
    },

    "个": {
        "type": "Lượng từ",
        "meaning": "cái; người; chiếc",
        "note": (
            "Lượng từ thông dụng nhất, dùng khi "
            "danh từ không có hoặc chưa học "
            "lượng từ chuyên biệt."
        ),
    },

    "几": {
        "type": "Đại từ nghi vấn / số từ",
        "meaning": "mấy; bao nhiêu; vài",
        "note": (
            "Thường dùng để hỏi số lượng nhỏ, "
            "ví dụ 你几岁？"
        ),
    },

    "九": {
        "type": "Số từ",
        "meaning": "chín; 9",
        "note": "Số đếm 9.",
    },

    "块": {
        "type": "Danh từ / lượng từ",
        "meaning": "miếng; cục; đồng, tệ",
        "note": (
            "Có thể dùng làm lượng từ cho vật dạng "
            "miếng/cục; trong khẩu ngữ còn dùng "
            "để nói đơn vị tiền, ví dụ 五块钱."
        ),
    },

    "两": {
        "type": "Số từ",
        "meaning": "hai",
        "note": (
            "Thường dùng trước lượng từ, "
            "ví dụ 两个人、两本书."
        ),
    },

    "零": {
        "type": "Số từ",
        "meaning": "không; số 0",
        "note": (
            "Dùng để biểu thị số 0 và phần hàng "
            "bị thiếu khi đọc số."
        ),
    },

    "六": {
        "type": "Số từ",
        "meaning": "sáu; 6",
        "note": "Số đếm 6.",
    },

    "七": {
        "type": "Số từ",
        "meaning": "bảy; 7",
        "note": "Số đếm 7.",
    },

    "三": {
        "type": "Số từ",
        "meaning": "ba; 3",
        "note": "Số đếm 3.",
    },

    "少": {
        "type": "Tính từ / động từ",
        "meaning": "ít; thiếu",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "số lượng ít hoặc không đủ."
        ),
    },

    "十": {
        "type": "Số từ",
        "meaning": "mười; 10",
        "note": "Số đếm 10.",
    },

    "四": {
        "type": "Số từ",
        "meaning": "bốn; 4",
        "note": "Số đếm 4.",
    },

    "岁": {
        "type": "Lượng từ",
        "meaning": "tuổi",
        "note": (
            "Dùng để nói hoặc hỏi tuổi, "
            "ví dụ 我二十岁、你几岁？"
        ),
    },

    "五": {
        "type": "Số từ",
        "meaning": "năm; 5",
        "note": "Số đếm 5.",
    },

    "一": {
        "type": "Số từ",
        "meaning": "một; 1",
        "note": (
            "Số đếm 1; có thể kết hợp với lượng từ, "
            "ví dụ 一个人、一本书."
        ),
    },

    "一半": {
        "type": "Số từ",
        "meaning": "một nửa",
        "note": (
            "Chỉ một phần bằng một nửa "
            "của tổng thể."
        ),
    },
}


# =========================================================
# HAM DOC CAC BAI DA REVIEW
# =========================================================
def get_lesson_rows(rows, lesson_no):

    return [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == lesson_no
    ]


def get_reviewed_rows(rows, lesson_no):

    return [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == lesson_no
        and row["DaKiemDuyet"] == "1"
    ]


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 95)
    print("09G6 - KIEM DUYET TU VUNG BAI 4")
    print("=" * 95)

    # =====================================================
    # 1. KIEM TRA FILE REVIEW
    # =====================================================
    if not REVIEW_FILE.exists():

        raise RuntimeError(
            "Khong tim thay file review:\n"
            f"{REVIEW_FILE}"
        )

    # =====================================================
    # 2. DOC FILE CSV
    # =====================================================
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

    # =====================================================
    # 3. KIEM TRA CAC COT BAT BUOC
    # =====================================================
    required_columns = {
        "SoThuTuBai",
        "ThuTuTrongBai",
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "TuLoaiNguon",
        "NghiaNguon",
        "MaNguon",
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

    # =====================================================
    # 4. KIEM TRA CAC BAI 1 -> 3 DA REVIEW
    # =====================================================
    expected_previous = {
        1: 13,
        2: 29,
        3: 23,
    }

    for lesson_no, expected_count in (
        expected_previous.items()
    ):

        lesson_rows = get_lesson_rows(
            rows,
            lesson_no,
        )

        reviewed_rows = get_reviewed_rows(
            rows,
            lesson_no,
        )

        if len(lesson_rows) != expected_count:

            raise RuntimeError(
                f"Bai {lesson_no} phai co "
                f"{expected_count} tu. "
                f"Thuc te: {len(lesson_rows)}"
            )

        if len(reviewed_rows) != expected_count:

            raise RuntimeError(
                f"Bai {lesson_no} "
                "chua duoc kiem duyet day du."
            )

    print()
    print("Kiem tra bai truoc:")
    print("  Bai 1: 13/13 OK")
    print("  Bai 2: 29/29 OK")
    print("  Bai 3: 23/23 OK")

    # =====================================================
    # 5. LAY BAI 4
    # =====================================================
    lesson4 = get_lesson_rows(
        rows,
        4,
    )

    if len(lesson4) != 26:

        raise RuntimeError(
            "Bai 4 phai co dung 26 tu. "
            f"Thuc te: {len(lesson4)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH 26 TU
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson4
    }

    expected_words = set(
        LESSON4_REVIEW.keys()
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
            "Danh sach 26 tu Bai 4 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 4 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson4
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 4 da co tu "
            "DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 5 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 5
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 5 -> 23 "
            "da co du lieu review."
        )

    # =====================================================
    # 9. TAO BACKUP
    # =====================================================
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

    # =====================================================
    # 10. CAP NHAT REVIEW BAI 4
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 4:
            continue

        word = row["ChuHan"].strip()

        review = LESSON4_REVIEW[word]

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

    if updated != 26:

        raise RuntimeError(
            "So dong cap nhat Bai 4 "
            "khong bang 26."
        )

    # =====================================================
    # 11. GHI LAI FILE REVIEW
    # =====================================================
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

    # =====================================================
    # 12. DOC LAI FILE DE VERIFY
    # =====================================================
    with open(
        REVIEW_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        verify_rows = list(reader)

    # =====================================================
    # 13. VERIFY BAI 1 -> 4
    # =====================================================
    expected_after = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
    }

    for lesson_no, expected_count in (
        expected_after.items()
    ):

        reviewed = get_reviewed_rows(
            verify_rows,
            lesson_no,
        )

        if len(reviewed) != expected_count:

            raise RuntimeError(
                f"Sau khi ghi file, "
                f"Bai {lesson_no} "
                f"khong co dung "
                f"{expected_count} tu da review."
            )

    # =====================================================
    # 14. DAM BAO BAI 5 -> 23 VAN CHUA REVIEW
    # =====================================================
    reviewed_after_lesson4 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 5
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson4:

        raise RuntimeError(
            "Bai 5 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 4
    # =====================================================
    lesson4_verified = get_reviewed_rows(
        verify_rows,
        4,
    )

    lesson4_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 4 SAU REVIEW")
    print("-" * 95)

    for row in lesson4_verified:

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

    # =====================================================
    # 16. TONG KET
    # =====================================================
    reviewed_total = sum(
        1
        for row in verify_rows
        if row["DaKiemDuyet"] == "1"
    )

    unreviewed_total = (
        len(verify_rows)
        - reviewed_total
    )

    if reviewed_total != 91:

        raise RuntimeError(
            "Sau Bai 4 phai co "
            "91 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 410:

        raise RuntimeError(
            "Sau Bai 4 phai con "
            "410 tu chua kiem duyet. "
            f"Thuc te: {unreviewed_total}"
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
        13,
    )

    print(
        "Bai 2 da kiem duyet:",
        29,
    )

    print(
        "Bai 3 da kiem duyet:",
        23,
    )

    print(
        "Bai 4 da kiem duyet:",
        len(lesson4_verified),
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