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
# NOI DUNG HOC TAP BAI 10
#
# 你喜欢吃什么？ - Bạn thích ăn gì?
#
# Chu de:
# - An uong
# - Mon an
# - Do uong
# - Cac bua an trong ngay
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON10_REVIEW = {

    "包子": {
        "type": "Danh từ",
        "meaning": "bánh bao",
        "note": (
            "Chỉ loại bánh hấp có nhân."
        ),
    },

    "杯子": {
        "type": "Danh từ",
        "meaning": "cốc; ly",
        "note": (
            "Đồ dùng để đựng nước hoặc các loại đồ uống."
        ),
    },

    "菜": {
        "type": "Danh từ",
        "meaning": "rau; món ăn",
        "note": (
            "Trong chủ đề ăn uống có thể dùng để chỉ "
            "rau hoặc một món ăn."
        ),
    },

    "茶": {
        "type": "Danh từ",
        "meaning": "trà",
        "note": (
            "Chỉ trà hoặc đồ uống từ trà."
        ),
    },

    "吃": {
        "type": "Động từ",
        "meaning": "ăn",
        "note": (
            "Động từ cơ bản chỉ hoạt động ăn."
        ),
    },

    "吃饭": {
        "type": "Động từ",
        "meaning": "ăn cơm; dùng bữa",
        "note": (
            "Cách nói thông dụng để chỉ việc ăn "
            "hoặc dùng một bữa ăn."
        ),
    },

    "饿": {
        "type": "Tính từ",
        "meaning": "đói",
        "note": (
            "Dùng để diễn tả trạng thái cảm thấy đói."
        ),
    },

    "饭": {
        "type": "Danh từ",
        "meaning": "cơm; bữa ăn",
        "note": (
            "Có thể chỉ cơm đã nấu hoặc một bữa ăn."
        ),
    },

    "饭店": {
        "type": "Danh từ",
        "meaning": "nhà hàng",
        "note": (
            "Trong bài ăn uống này tập trung vào nghĩa "
            "nhà hàng."
        ),
    },

    "好吃": {
        "type": "Tính từ",
        "meaning": "ngon; ngon miệng",
        "note": (
            "Dùng để miêu tả thức ăn có vị ngon."
        ),
    },

    "喝": {
        "type": "Động từ",
        "meaning": "uống",
        "note": (
            "Động từ cơ bản chỉ hoạt động uống."
        ),
    },

    "鸡蛋": {
        "type": "Danh từ",
        "meaning": "trứng gà",
        "note": (
            "Chỉ trứng của gà."
        ),
    },

    "渴": {
        "type": "Tính từ",
        "meaning": "khát",
        "note": (
            "Dùng để diễn tả trạng thái muốn uống nước."
        ),
    },

    "米饭": {
        "type": "Danh từ",
        "meaning": "cơm",
        "note": (
            "Chỉ cơm đã được nấu chín."
        ),
    },

    "面包": {
        "type": "Danh từ",
        "meaning": "bánh mì",
        "note": (
            "Chỉ bánh mì."
        ),
    },

    "面条儿": {
        "type": "Danh từ",
        "meaning": "mì; mì sợi",
        "note": (
            "Dạng có hiện tượng 儿化 của 面条."
        ),
    },

    "奶": {
        "type": "Danh từ",
        "meaning": "sữa",
        "note": (
            "Trong bài ăn uống này chỉ dùng nghĩa sữa."
        ),
    },

    "牛奶": {
        "type": "Danh từ",
        "meaning": "sữa bò",
        "note": (
            "Đồ uống làm từ sữa bò."
        ),
    },

    "肉": {
        "type": "Danh từ",
        "meaning": "thịt",
        "note": (
            "Trong bài này dùng với nghĩa thịt dùng làm thực phẩm."
        ),
    },

    "水": {
        "type": "Danh từ",
        "meaning": "nước",
        "note": (
            "Trong bài này dùng với nghĩa nước uống."
        ),
    },

    "水果": {
        "type": "Danh từ",
        "meaning": "trái cây; hoa quả",
        "note": (
            "Cách gọi chung các loại trái cây."
        ),
    },

    "晚饭": {
        "type": "Danh từ",
        "meaning": "bữa tối; cơm tối",
        "note": (
            "Bữa ăn vào buổi tối."
        ),
    },

    "午饭": {
        "type": "Danh từ",
        "meaning": "bữa trưa; cơm trưa",
        "note": (
            "Bữa ăn vào buổi trưa."
        ),
    },

    "早饭": {
        "type": "Danh từ",
        "meaning": "bữa sáng",
        "note": (
            "Bữa ăn vào buổi sáng."
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
    print("09G12 - KIEM DUYET TU VUNG BAI 10")
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
    # 4. KIEM TRA BAI 1 -> 9
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
    # 5. LAY BAI 10
    # =====================================================
    lesson10 = get_lesson_rows(
        rows,
        10,
    )

    if len(lesson10) != 24:

        raise RuntimeError(
            "Bai 10 phai co dung 24 tu. "
            f"Thuc te: {len(lesson10)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson10
    }

    expected_words = set(
        LESSON10_REVIEW.keys()
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
            "Danh sach 24 tu Bai 10 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 10 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson10
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 10 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 11 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 11
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 11 -> 23 "
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
    # 10. CAP NHAT BAI 10
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 10:
            continue

        word = row["ChuHan"].strip()

        review = LESSON10_REVIEW[word]

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

    if updated != 24:

        raise RuntimeError(
            "So dong cap nhat Bai 10 "
            "khong bang 24."
        )

    # =====================================================
    # 11. GHI LAI FILE
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
    # 13. VERIFY BAI 1 -> 10
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
    # 14. DAM BAO BAI 11 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson10 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 11
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson10:

        raise RuntimeError(
            "Bai 11 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 10
    # =====================================================
    lesson10_verified = get_reviewed_rows(
        verify_rows,
        10,
    )

    lesson10_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 10 SAU REVIEW")
    print("-" * 95)

    for row in lesson10_verified:

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

    if reviewed_total != 234:

        raise RuntimeError(
            "Sau Bai 10 phai co "
            "234 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 267:

        raise RuntimeError(
            "Sau Bai 10 phai con "
            "267 tu chua kiem duyet. "
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