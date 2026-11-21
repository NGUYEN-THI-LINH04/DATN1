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
# NOI DUNG HOC TAP BAI 16
#
# 我生病了 - Tôi bị ốm rồi
#
# Chu de:
# - Suc khoe
# - Co the
# - Di kham benh
# - Bac si / benh vien
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON16_REVIEW = {

    "病": {
        "type": "Danh từ / động từ",
        "meaning": "bệnh; ốm",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "bệnh hoặc bị ốm."
        ),
    },

    "病人": {
        "type": "Danh từ",
        "meaning": "bệnh nhân; người bệnh",
        "note": (
            "Chỉ người đang bị bệnh "
            "hoặc đang được điều trị."
        ),
    },

    "看病": {
        "type": "Động từ",
        "meaning": "đi khám bệnh; khám bệnh",
        "note": (
            "Có thể dùng khi người bệnh đi khám "
            "hoặc khi bác sĩ khám cho bệnh nhân."
        ),
    },

    "口": {
        "type": "Danh từ / lượng từ",
        "meaning": "miệng",
        "note": (
            "Trong bài về cơ thể chỉ học "
            "nghĩa cơ bản là miệng."
        ),
    },

    "毛": {
        "type": "Danh từ",
        "meaning": "lông; tóc",
        "note": (
            "Trong bài về cơ thể tập trung vào "
            "nghĩa lông hoặc tóc; không dùng "
            "nghĩa đơn vị tiền tệ."
        ),
    },

    "身上": {
        "type": "Danh từ chỉ vị trí",
        "meaning": "trên người; trên cơ thể",
        "note": (
            "Dùng để nói vị trí hoặc trạng thái "
            "ở trên cơ thể một người."
        ),
    },

    "身体": {
        "type": "Danh từ",
        "meaning": "cơ thể; sức khỏe",
        "note": (
            "Có thể chỉ cơ thể hoặc tình trạng "
            "sức khỏe của một người."
        ),
    },

    "生病": {
        "type": "Động từ",
        "meaning": "bị ốm; mắc bệnh",
        "note": (
            "Từ trọng tâm của bài, "
            "ví dụ 我生病了."
        ),
    },

    "生气": {
        "type": "Động từ / tính từ",
        "meaning": "tức giận; nổi giận",
        "note": (
            "Trong bài này giữ nghĩa thông dụng "
            "là tức giận hoặc nổi giận."
        ),
    },

    "手": {
        "type": "Danh từ",
        "meaning": "tay; bàn tay",
        "note": (
            "Trong bài về cơ thể chỉ dùng "
            "nghĩa tay."
        ),
    },

    "医生": {
        "type": "Danh từ",
        "meaning": "bác sĩ",
        "note": (
            "Chỉ người làm công việc "
            "khám và chữa bệnh."
        ),
    },

    "医院": {
        "type": "Danh từ",
        "meaning": "bệnh viện",
        "note": (
            "Nơi khám, chữa bệnh "
            "và chăm sóc sức khỏe."
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
    print("09G18 - KIEM DUYET TU VUNG BAI 16")
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
    # 3. KIEM TRA COT
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
    # 4. KIEM TRA BAI 1 -> 15
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
    # 5. LAY BAI 16
    # =====================================================
    lesson16 = get_lesson_rows(
        rows,
        16,
    )

    if len(lesson16) != 12:
        raise RuntimeError(
            "Bai 16 phai co dung 12 tu. "
            f"Thuc te: {len(lesson16)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson16
    }

    expected_words = set(
        LESSON16_REVIEW.keys()
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
            "Danh sach 12 tu Bai 16 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 16 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson16
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 16 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 17 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 17
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 17 -> 23 "
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
    # 10. CAP NHAT BAI 16
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 16:
            continue

        word = row["ChuHan"].strip()
        review = LESSON16_REVIEW[word]

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

    if updated != 12:
        raise RuntimeError(
            "So dong cap nhat Bai 16 "
            "khong bang 12."
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
    # 13. VERIFY BAI 1 -> 16
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
    # 14. DAM BAO BAI 17 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson16 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 17
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson16:
        raise RuntimeError(
            "Bai 17 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 16
    # =====================================================
    lesson16_verified = get_reviewed_rows(
        verify_rows,
        16,
    )

    lesson16_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 16 SAU REVIEW")
    print("-" * 95)

    for row in lesson16_verified:

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

    if reviewed_total != 354:
        raise RuntimeError(
            "Sau Bai 16 phai co "
            "354 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 147:
        raise RuntimeError(
            "Sau Bai 16 phai con "
            "147 tu chua kiem duyet. "
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