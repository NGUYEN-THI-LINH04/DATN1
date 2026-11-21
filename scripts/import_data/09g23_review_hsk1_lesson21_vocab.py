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
# NOI DUNG HOC TAP BAI 21
#
# 这个比那个好
# Cái này tốt hơn cái kia
#
# Chu de:
# - Mieu ta
# - So sanh
# - Muc do
# - Tinh tu co ban
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON21_REVIEW = {

    "比": {
        "type": "Giới từ / động từ",
        "meaning": "so với; hơn",
        "note": (
            "Trong bài này chủ yếu dùng trong "
            "cấu trúc so sánh A 比 B + tính từ, "
            "ví dụ 这个比那个好."
        ),
    },

    "不大": {
        "type": "Cụm từ chỉ mức độ",
        "meaning": "không quá; không nhiều",
        "note": (
            "Dùng để giảm mức độ của tính chất "
            "hoặc hành động."
        ),
    },

    "差": {
        "type": "Tính từ / động từ",
        "meaning": "kém; khác; sai",
        "note": (
            "Trong bài so sánh chủ yếu học nghĩa "
            "kém hoặc có sự khác biệt."
        ),
    },

    "大": {
        "type": "Tính từ",
        "meaning": "to; lớn",
        "note": (
            "Dùng để miêu tả kích thước "
            "hoặc mức độ lớn."
        ),
    },

    "非常": {
        "type": "Phó từ",
        "meaning": "rất; vô cùng",
        "note": (
            "Đặt trước tính từ hoặc động từ "
            "để nhấn mạnh mức độ cao."
        ),
    },

    "高": {
        "type": "Tính từ",
        "meaning": "cao",
        "note": (
            "Dùng để miêu tả chiều cao "
            "hoặc mức độ cao."
        ),
    },

    "坏": {
        "type": "Tính từ",
        "meaning": "xấu; hỏng",
        "note": (
            "Dùng để miêu tả người, sự việc "
            "không tốt hoặc đồ vật bị hỏng."
        ),
    },

    "快": {
        "type": "Tính từ / phó từ",
        "meaning": "nhanh; nhanh chóng",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "tốc độ nhanh."
        ),
    },

    "老": {
        "type": "Tính từ",
        "meaning": "già; lớn tuổi",
        "note": (
            "Trong bài so sánh tập trung vào nghĩa "
            "tuổi cao hoặc lớn tuổi."
        ),
    },

    "慢": {
        "type": "Tính từ",
        "meaning": "chậm",
        "note": (
            "Dùng để miêu tả tốc độ chậm."
        ),
    },

    "难": {
        "type": "Tính từ",
        "meaning": "khó; khó khăn",
        "note": (
            "Dùng để miêu tả một việc "
            "không dễ thực hiện."
        ),
    },

    "太": {
        "type": "Phó từ",
        "meaning": "quá; rất",
        "note": (
            "Đặt trước tính từ để biểu thị "
            "mức độ cao, ví dụ 太大、太难."
        ),
    },

    "小": {
        "type": "Tính từ",
        "meaning": "nhỏ; bé",
        "note": (
            "Dùng để miêu tả kích thước "
            "hoặc mức độ nhỏ."
        ),
    },

    "一样": {
        "type": "Tính từ",
        "meaning": "giống nhau; như nhau",
        "note": (
            "Dùng để nói hai hoặc nhiều "
            "đối tượng giống nhau."
        ),
    },

    "真": {
        "type": "Phó từ / tính từ",
        "meaning": "thật; quả thật",
        "note": (
            "Trong bài này có thể dùng để "
            "nhấn mạnh đánh giá hoặc mức độ."
        ),
    },

    "真的": {
        "type": "Cụm từ",
        "meaning": "thực sự; thật sự; thật",
        "note": (
            "Dùng để nhấn mạnh tính chân thực "
            "hoặc mức độ của một nhận xét."
        ),
    },

    "重": {
        "type": "Tính từ",
        "meaning": "nặng",
        "note": (
            "Trong bài so sánh tập trung vào nghĩa "
            "trọng lượng lớn."
        ),
    },

    "重要": {
        "type": "Tính từ",
        "meaning": "quan trọng",
        "note": (
            "Dùng để miêu tả người, việc "
            "hoặc thông tin có vai trò lớn."
        ),
    },

    "最": {
        "type": "Phó từ",
        "meaning": "nhất",
        "note": (
            "Đặt trước tính từ để biểu thị "
            "mức độ cao nhất, ví dụ 最好."
        ),
    },

    "最好": {
        "type": "Phó từ",
        "meaning": "tốt nhất; tốt hơn hết nên",
        "note": (
            "Có thể chỉ mức độ tốt nhất hoặc "
            "dùng để đưa ra lời khuyên: tốt hơn hết nên..."
        ),
    },
}


# =========================================================
# HELPERS
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
    print("09G23 - KIEM DUYET TU VUNG BAI 21")
    print("=" * 95)

    # =====================================================
    # 1. KIEM TRA FILE
    # =====================================================
    if not REVIEW_FILE.exists():
        raise RuntimeError(
            "Khong tim thay file review:\n"
            f"{REVIEW_FILE}"
        )

    # =====================================================
    # 2. DOC FILE
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
    # 3. KIEM TRA CAC COT
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
    # 4. KIEM TRA BAI 1 -> 20
    # =====================================================
    expected_previous = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
        5: 20,
        6: 24,
        7: 28,
        8: 25,
        9: 22,
        10: 24,
        11: 23,
        12: 22,
        13: 30,
        14: 22,
        15: 11,
        16: 12,
        17: 25,
        18: 22,
        19: 23,
        20: 23,
    }

    print()
    print("Kiem tra bai truoc:")

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
                "chua kiem duyet day du."
            )

        print(
            f"  Bai {lesson_no}: "
            f"{expected_count}/{expected_count} OK"
        )

    # =====================================================
    # 5. LAY BAI 21
    # =====================================================
    lesson21 = get_lesson_rows(
        rows,
        21,
    )

    if len(lesson21) != 20:
        raise RuntimeError(
            "Bai 21 phai co dung 20 tu. "
            f"Thuc te: {len(lesson21)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson21
    }

    expected_words = set(
        LESSON21_REVIEW.keys()
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
            "Danh sach 20 tu Bai 21 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 21 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson21
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 21 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 22 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 22
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 22 -> 23 "
            "da co du lieu review."
        )

    # =====================================================
    # 9. BACKUP
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
    # 10. CAP NHAT BAI 21
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 21:
            continue

        word = row["ChuHan"].strip()

        review = LESSON21_REVIEW[word]

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

    if updated != 20:
        raise RuntimeError(
            "So dong cap nhat Bai 21 "
            "khong bang 20."
        )

    # =====================================================
    # 11. GHI FILE
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
    # 12. DOC LAI VERIFY
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
    # 13. VERIFY BAI 1 -> 21
    # =====================================================
    expected_after = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
        5: 20,
        6: 24,
        7: 28,
        8: 25,
        9: 22,
        10: 24,
        11: 23,
        12: 22,
        13: 30,
        14: 22,
        15: 11,
        16: 12,
        17: 25,
        18: 22,
        19: 23,
        20: 23,
        21: 20,
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
    # 14. DAM BAO BAI 22 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson21 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 22
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson21:
        raise RuntimeError(
            "Bai 22 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 21
    # =====================================================
    lesson21_verified = get_reviewed_rows(
        verify_rows,
        21,
    )

    lesson21_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 21 SAU REVIEW")
    print("-" * 95)

    for row in lesson21_verified:

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

    if reviewed_total != 467:
        raise RuntimeError(
            "Sau Bai 21 phai co "
            "467 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 34:
        raise RuntimeError(
            "Sau Bai 21 phai con "
            "34 tu chua kiem duyet. "
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

    for lesson_no, count in (
        expected_after.items()
    ):

        print(
            f"Bai {lesson_no} da kiem duyet:",
            count,
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