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
# NOI DUNG HOC TAP BAI 15
#
# 今天天气怎么样？
# Thời tiết hôm nay thế nào?
#
# Chu de:
# - Thoi tiet
# - Nong / lanh / kho
# - Gio / mua
# - Thien nhien co ban
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON15_REVIEW = {

    "白": {
        "type": "Tính từ",
        "meaning": "trắng",
        "note": (
            "Trong bài này chỉ học nghĩa cơ bản "
            "chỉ màu trắng."
        ),
    },

    "风": {
        "type": "Danh từ",
        "meaning": "gió",
        "note": (
            "Trong bài thời tiết dùng với nghĩa "
            "hiện tượng gió."
        ),
    },

    "干": {
        "type": "Tính từ",
        "meaning": "khô",
        "note": (
            "Đây là cách đọc gān, nghĩa là khô. "
            "Cần phân biệt với 干 gàn ở Bài 9 "
            "có nghĩa là làm hoặc làm việc."
        ),
    },

    "花": {
        "type": "Danh từ",
        "meaning": "hoa; bông hoa",
        "note": (
            "Trong bài thiên nhiên chỉ dùng "
            "nghĩa hoa."
        ),
    },

    "冷": {
        "type": "Tính từ",
        "meaning": "lạnh",
        "note": (
            "Dùng để miêu tả thời tiết "
            "hoặc nhiệt độ thấp."
        ),
    },

    "热": {
        "type": "Tính từ",
        "meaning": "nóng",
        "note": (
            "Trong bài này dùng để miêu tả "
            "thời tiết hoặc nhiệt độ cao."
        ),
    },

    "山": {
        "type": "Danh từ",
        "meaning": "núi; đồi",
        "note": (
            "Danh từ chỉ núi hoặc vùng đất cao."
        ),
    },

    "树": {
        "type": "Danh từ",
        "meaning": "cây",
        "note": (
            "Trong bài thiên nhiên dùng với nghĩa "
            "cây cối."
        ),
    },

    "天气": {
        "type": "Danh từ",
        "meaning": "thời tiết",
        "note": (
            "Từ trọng tâm của bài, dùng để nói "
            "tình trạng thời tiết."
        ),
    },

    "下雨": {
        "type": "Động từ",
        "meaning": "mưa; trời mưa",
        "note": (
            "Dùng để diễn tả hiện tượng trời mưa, "
            "ví dụ 今天下雨."
        ),
    },

    "雨": {
        "type": "Danh từ",
        "meaning": "mưa",
        "note": (
            "Danh từ chỉ hiện tượng hoặc "
            "lượng nước mưa."
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
    print("09G17 - KIEM DUYET TU VUNG BAI 15")
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
    # 4. KIEM TRA BAI 1 -> 14
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
    # 5. LAY BAI 15
    # =====================================================
    lesson15 = get_lesson_rows(
        rows,
        15,
    )

    if len(lesson15) != 11:
        raise RuntimeError(
            "Bai 15 phai co dung 11 tu. "
            f"Thuc te: {len(lesson15)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH 11 TU
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson15
    }

    expected_words = set(
        LESSON15_REVIEW.keys()
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
            "Danh sach 11 tu Bai 15 "
            "khong khop file review."
        )

    # =====================================================
    # 7. KIEM TRA RIENG 干 PHAI LA GAN1
    # =====================================================
    gan_rows = [
        row
        for row in lesson15
        if row["ChuHan"].strip() == "干"
    ]

    if len(gan_rows) != 1:
        raise RuntimeError(
            "Bai 15 phai co dung 1 muc 干."
        )

    gan_pinyin = (
        gan_rows[0]["PhienAm"]
        .strip()
        .lower()
    )

    if gan_pinyin != "gān":
        raise RuntimeError(
            "Muc 干 trong Bai 15 phai la gān. "
            f"Thuc te: {gan_rows[0]['PhienAm']}"
        )

    # =====================================================
    # 8. DAM BAO BAI 15 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson15
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 15 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 9. DAM BAO BAI 16 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 16
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 16 -> 23 "
            "da co du lieu review."
        )

    # =====================================================
    # 10. BACKUP
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
    # 11. CAP NHAT BAI 15
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 15:
            continue

        word = row["ChuHan"].strip()
        review = LESSON15_REVIEW[word]

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

    if updated != 11:
        raise RuntimeError(
            "So dong cap nhat Bai 15 "
            "khong bang 11."
        )

    # =====================================================
    # 12. GHI FILE
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
    # 13. DOC LAI VERIFY
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
    # 14. VERIFY BAI 1 -> 15
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
    # 15. DAM BAO BAI 16 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson15 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 16
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson15:
        raise RuntimeError(
            "Bai 16 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 16. IN NOI DUNG BAI 15
    # =====================================================
    lesson15_verified = get_reviewed_rows(
        verify_rows,
        15,
    )

    lesson15_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 15 SAU REVIEW")
    print("-" * 95)

    for row in lesson15_verified:

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
    # 17. TONG KET
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

    if reviewed_total != 342:
        raise RuntimeError(
            "Sau Bai 15 phai co "
            "342 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 159:
        raise RuntimeError(
            "Sau Bai 15 phai con "
            "159 tu chua kiem duyet. "
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