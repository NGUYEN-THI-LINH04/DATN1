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
# NOI DUNG HOC TAP BAI 5
#
# 今天几月几号？ - Hôm nay là ngày mấy?
#
# Chu de:
# - Ngay, thang, nam
# - Thu trong tuan
# - Cac moc thoi gian co ban
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON5_REVIEW = {

    "半年": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "nửa năm; sáu tháng",
        "note": (
            "Chỉ khoảng thời gian bằng một nửa năm."
        ),
    },

    "号": {
        "type": "Danh từ",
        "meaning": "ngày; số",
        "note": (
            "Trong bài này chủ yếu dùng để nói "
            "ngày trong tháng, ví dụ 五月三号."
        ),
    },

    "后天": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "ngày mốt",
        "note": (
            "Chỉ ngày sau ngày mai."
        ),
    },

    "今年": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "năm nay",
        "note": (
            "Chỉ năm hiện tại."
        ),
    },

    "今天": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "hôm nay",
        "note": (
            "Chỉ ngày hiện tại."
        ),
    },

    "明年": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "năm sau",
        "note": (
            "Chỉ năm tiếp theo."
        ),
    },

    "明天": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "ngày mai",
        "note": (
            "Chỉ ngày sau hôm nay."
        ),
    },

    "年": {
        "type": "Danh từ / lượng từ",
        "meaning": "năm",
        "note": (
            "Đơn vị thời gian dùng để nói năm "
            "hoặc khoảng thời gian tính bằng năm."
        ),
    },

    "前天": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "hôm kia",
        "note": (
            "Chỉ ngày trước hôm qua."
        ),
    },

    "去年": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "năm ngoái",
        "note": (
            "Chỉ năm trước năm hiện tại."
        ),
    },

    "日": {
        "type": "Danh từ",
        "meaning": "ngày",
        "note": (
            "Cách dùng trang trọng hơn của 号 "
            "khi ghi ngày tháng, ví dụ 五月三日."
        ),
    },

    "日期": {
        "type": "Danh từ",
        "meaning": "ngày tháng; ngày tháng năm",
        "note": (
            "Chỉ ngày cụ thể trên lịch."
        ),
    },

    "生日": {
        "type": "Danh từ",
        "meaning": "sinh nhật",
        "note": (
            "Ngày một người được sinh ra; "
            "ví dụ 我的生日是五月十号."
        ),
    },

    "天": {
        "type": "Danh từ / lượng từ",
        "meaning": "ngày",
        "note": (
            "Trong bài này dùng làm đơn vị "
            "thời gian tính theo ngày."
        ),
    },

    "新年": {
        "type": "Danh từ",
        "meaning": "năm mới",
        "note": (
            "Chỉ thời điểm bắt đầu một năm mới."
        ),
    },

    "星期": {
        "type": "Danh từ",
        "meaning": "tuần; thứ",
        "note": (
            "Dùng để nói tuần hoặc ngày trong tuần, "
            "ví dụ 星期一、星期二."
        ),
    },

    "星期日": {
        "type": "Danh từ",
        "meaning": "Chủ nhật",
        "note": (
            "Một cách nói ngày Chủ nhật."
        ),
    },

    "星期天": {
        "type": "Danh từ",
        "meaning": "Chủ nhật",
        "note": (
            "Cách nói phổ biến khác của 星期日."
        ),
    },

    "月": {
        "type": "Danh từ",
        "meaning": "tháng",
        "note": (
            "Trong bài này dùng để chỉ tháng "
            "trong năm, ví dụ 五月 là tháng 5."
        ),
    },

    "昨天": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "hôm qua",
        "note": (
            "Chỉ ngày trước hôm nay."
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
    print("09G7 - KIEM DUYET TU VUNG BAI 5")
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
    # 3. KIEM TRA COT BAT BUOC
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
    # 4. KIEM TRA BAI 1 -> 4
    # =====================================================
    expected_previous = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
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
    # 5. LAY 20 TU BAI 5
    # =====================================================
    lesson5 = get_lesson_rows(
        rows,
        5,
    )

    if len(lesson5) != 20:

        raise RuntimeError(
            "Bai 5 phai co dung 20 tu. "
            f"Thuc te: {len(lesson5)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson5
    }

    expected_words = set(
        LESSON5_REVIEW.keys()
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
            "Danh sach 20 tu Bai 5 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 5 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson5
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 5 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. BAI 6 -> 23 PHAI CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 6
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 6 -> 23 "
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
    # 10. CAP NHAT REVIEW BAI 5
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 5:
            continue

        word = row["ChuHan"].strip()

        review = LESSON5_REVIEW[word]

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
            "So dong cap nhat Bai 5 "
            "khong bang 20."
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
    # 13. VERIFY BAI 1 -> 5
    # =====================================================
    expected_after = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
        5: 20,
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
    # 14. DAM BAO BAI 6 -> 23 CHUA BI THAY DOI
    # =====================================================
    reviewed_after_lesson5 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 6
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson5:

        raise RuntimeError(
            "Bai 6 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 5
    # =====================================================
    lesson5_verified = get_reviewed_rows(
        verify_rows,
        5,
    )

    lesson5_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 5 SAU REVIEW")
    print("-" * 95)

    for row in lesson5_verified:

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

    if reviewed_total != 111:

        raise RuntimeError(
            "Sau Bai 5 phai co "
            "111 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 390:

        raise RuntimeError(
            "Sau Bai 5 phai con "
            "390 tu chua kiem duyet. "
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
        26,
    )

    print(
        "Bai 5 da kiem duyet:",
        len(lesson5_verified),
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