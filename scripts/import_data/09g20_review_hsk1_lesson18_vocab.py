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
# NOI DUNG HOC TAP BAI 18
#
# 我们坐飞机去北京
# Chúng ta đi Bắc Kinh bằng máy bay
#
# Chu de:
# - Du lich
# - Phuong tien di lai xa
# - San bay / tau hoa
# - Ve
# - Den / di / tro ve
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON18_REVIEW = {

    "北京": {
        "type": "Danh từ riêng",
        "meaning": "Bắc Kinh",
        "note": (
            "Tên địa danh 北京, dùng trong mẫu "
            "我们坐飞机去北京."
        ),
    },

    "车票": {
        "type": "Danh từ",
        "meaning": "vé xe; vé tàu",
        "note": (
            "Vé dùng khi đi xe buýt, tàu hỏa "
            "hoặc một số phương tiện giao thông."
        ),
    },

    "到": {
        "type": "Động từ",
        "meaning": "đến; tới",
        "note": (
            "Dùng để nói việc đến một địa điểm "
            "hoặc đạt tới một thời điểm."
        ),
    },

    "飞": {
        "type": "Động từ",
        "meaning": "bay",
        "note": (
            "Động từ cơ bản chỉ hoạt động bay."
        ),
    },

    "飞机": {
        "type": "Danh từ",
        "meaning": "máy bay",
        "note": (
            "Phương tiện giao thông đường hàng không."
        ),
    },

    "回到": {
        "type": "Động từ",
        "meaning": "trở về; quay lại",
        "note": (
            "Dùng để nói việc trở lại "
            "một địa điểm."
        ),
    },

    "火车": {
        "type": "Danh từ",
        "meaning": "tàu hỏa",
        "note": (
            "Phương tiện giao thông chạy "
            "trên đường sắt."
        ),
    },

    "机场": {
        "type": "Danh từ",
        "meaning": "sân bay",
        "note": (
            "Nơi máy bay cất cánh, hạ cánh "
            "và đón trả hành khách."
        ),
    },

    "机票": {
        "type": "Danh từ",
        "meaning": "vé máy bay",
        "note": (
            "Vé dùng cho hành trình bằng máy bay."
        ),
    },

    "来": {
        "type": "Động từ",
        "meaning": "đến; tới",
        "note": (
            "Biểu thị sự di chuyển hướng về "
            "phía người nói hoặc địa điểm đang nói tới."
        ),
    },

    "来到": {
        "type": "Động từ",
        "meaning": "đến; tới",
        "note": (
            "Dùng để nhấn mạnh việc đã đến "
            "một địa điểm."
        ),
    },

    "门票": {
        "type": "Danh từ",
        "meaning": "vé vào cửa",
        "note": (
            "Vé dùng để vào nơi tham quan, "
            "rạp chiếu phim hoặc địa điểm có thu vé."
        ),
    },

    "票": {
        "type": "Danh từ",
        "meaning": "vé; phiếu",
        "note": (
            "Trong bài du lịch chủ yếu dùng "
            "với nghĩa vé."
        ),
    },

    "去": {
        "type": "Động từ",
        "meaning": "đi; đi đến",
        "note": (
            "Biểu thị sự di chuyển rời khỏi "
            "vị trí hiện tại đến nơi khác."
        ),
    },

    "送": {
        "type": "Động từ",
        "meaning": "tiễn; đưa; gửi",
        "note": (
            "Trong chủ đề đi lại có thể dùng "
            "với nghĩa tiễn hoặc đưa một người."
        ),
    },

    "行": {
        "type": "Động từ / tính từ",
        "meaning": "được; ổn; có thể",
        "note": (
            "Đây là cách đọc xíng. "
            "Ở mức cơ bản dùng để biểu thị "
            "đồng ý, khả năng hoặc việc gì đó ổn."
        ),
    },

    "一块儿": {
        "type": "Phó từ",
        "meaning": "cùng nhau",
        "note": (
            "Dạng có 儿化, trong bài này dùng "
            "với nghĩa cùng nhau làm một việc."
        ),
    },

    "一起": {
        "type": "Phó từ",
        "meaning": "cùng nhau",
        "note": (
            "Dùng khi hai hoặc nhiều người "
            "cùng thực hiện một hoạt động."
        ),
    },

    "找": {
        "type": "Động từ",
        "meaning": "tìm; tìm kiếm",
        "note": (
            "Trong bài này dùng với nghĩa "
            "tìm người, đồ vật hoặc địa điểm."
        ),
    },

    "找到": {
        "type": "Động từ",
        "meaning": "tìm thấy",
        "note": (
            "Biểu thị kết quả đã tìm được "
            "người hoặc vật cần tìm."
        ),
    },

    "坐": {
        "type": "Động từ",
        "meaning": "ngồi; đi bằng",
        "note": (
            "Trong chủ đề giao thông thường dùng "
            "với phương tiện, ví dụ 坐飞机、坐火车."
        ),
    },

    "坐下": {
        "type": "Động từ",
        "meaning": "ngồi xuống",
        "note": (
            "Dùng để nói hành động chuyển "
            "sang tư thế ngồi."
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
    print("09G20 - KIEM DUYET TU VUNG BAI 18")
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
    # 4. KIEM TRA BAI 1 -> 17
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
    # 5. LAY BAI 18
    # =====================================================
    lesson18 = get_lesson_rows(
        rows,
        18,
    )

    if len(lesson18) != 22:
        raise RuntimeError(
            "Bai 18 phai co dung 22 tu. "
            f"Thuc te: {len(lesson18)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson18
    }

    expected_words = set(
        LESSON18_REVIEW.keys()
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
            "Danh sach 22 tu Bai 18 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 18 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson18
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 18 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 19 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 19
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 19 -> 23 "
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
    # 10. CAP NHAT BAI 18
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 18:
            continue

        word = row["ChuHan"].strip()
        review = LESSON18_REVIEW[word]

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

    if updated != 22:
        raise RuntimeError(
            "So dong cap nhat Bai 18 "
            "khong bang 22."
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
    # 13. VERIFY BAI 1 -> 18
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
    # 14. DAM BAO BAI 19 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson18 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 19
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson18:
        raise RuntimeError(
            "Bai 19 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 18
    # =====================================================
    lesson18_verified = get_reviewed_rows(
        verify_rows,
        18,
    )

    lesson18_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 18 SAU REVIEW")
    print("-" * 95)

    for row in lesson18_verified:

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

    if reviewed_total != 401:
        raise RuntimeError(
            "Sau Bai 18 phai co "
            "401 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 100:
        raise RuntimeError(
            "Sau Bai 18 phai con "
            "100 tu chua kiem duyet. "
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