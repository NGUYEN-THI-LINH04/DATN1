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
# NOI DUNG HOC TAP BAI 14
#
# 请问，车站在哪儿？
# Cho hỏi, nhà ga ở đâu?
#
# Chu de:
# - Giao thong trong thanh pho
# - Hoi duong
# - Di bo / di xe
# - Len xe / xuong xe
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON14_REVIEW = {

    "车": {
        "type": "Danh từ",
        "meaning": "xe; phương tiện",
        "note": (
            "Trong bài này dùng để chỉ "
            "phương tiện giao thông nói chung."
        ),
    },

    "车上": {
        "type": "Danh từ chỉ nơi chốn",
        "meaning": "trên xe; ở trên xe",
        "note": (
            "Dùng để chỉ vị trí đang ở "
            "trên một phương tiện."
        ),
    },

    "车站": {
        "type": "Danh từ",
        "meaning": "nhà ga; bến xe; trạm xe",
        "note": (
            "Dùng để chỉ nơi phương tiện "
            "dừng để đón hoặc trả khách."
        ),
    },

    "从": {
        "type": "Giới từ",
        "meaning": "từ",
        "note": (
            "Dùng để chỉ điểm bắt đầu "
            "của hành động hoặc hành trình, "
            "ví dụ 从学校到车站."
        ),
    },

    "打车": {
        "type": "Động từ",
        "meaning": "bắt taxi; đi taxi",
        "note": (
            "Cách nói thông dụng chỉ việc "
            "gọi hoặc bắt taxi để di chuyển."
        ),
    },

    "地图": {
        "type": "Danh từ",
        "meaning": "bản đồ",
        "note": (
            "Dùng để xem vị trí và đường đi."
        ),
    },

    "开车": {
        "type": "Động từ",
        "meaning": "lái xe",
        "note": (
            "Dùng để nói việc điều khiển "
            "ô tô hoặc phương tiện."
        ),
    },

    "路": {
        "type": "Danh từ",
        "meaning": "đường; tuyến đường",
        "note": (
            "Trong bài này chủ yếu dùng "
            "để nói đường đi."
        ),
    },

    "路口": {
        "type": "Danh từ",
        "meaning": "ngã tư; giao lộ",
        "note": (
            "Chỉ nơi hai hoặc nhiều con đường "
            "giao nhau."
        ),
    },

    "路上": {
        "type": "Danh từ chỉ nơi chốn",
        "meaning": "trên đường; đang trên đường",
        "note": (
            "Dùng để nói vị trí hoặc trạng thái "
            "đang di chuyển trên đường."
        ),
    },

    "马路": {
        "type": "Danh từ",
        "meaning": "đường phố; đường",
        "note": (
            "Chỉ đường dành cho giao thông "
            "trong thành phố."
        ),
    },

    "哪里": {
        "type": "Đại từ nghi vấn",
        "meaning": "ở đâu; nơi nào",
        "note": (
            "Dùng để hỏi địa điểm."
        ),
    },

    "哪儿": {
        "type": "Đại từ nghi vấn",
        "meaning": "ở đâu; nơi nào",
        "note": (
            "Cách nói có 儿化, "
            "tương đương 哪里."
        ),
    },

    "跑": {
        "type": "Động từ",
        "meaning": "chạy",
        "note": (
            "Trong bài này tập trung vào "
            "nghĩa di chuyển bằng cách chạy."
        ),
    },

    "汽车": {
        "type": "Danh từ",
        "meaning": "ô tô; xe hơi",
        "note": (
            "Chỉ phương tiện giao thông "
            "đường bộ có động cơ."
        ),
    },

    "请问": {
        "type": "Động từ / cách nói lịch sự",
        "meaning": "cho hỏi; xin hỏi",
        "note": (
            "Cách mở đầu lịch sự khi muốn "
            "hỏi thông tin hoặc hỏi đường."
        ),
    },

    "上车": {
        "type": "Động từ",
        "meaning": "lên xe",
        "note": (
            "Dùng khi bước lên xe buýt, "
            "tàu, ô tô hoặc phương tiện khác."
        ),
    },

    "下车": {
        "type": "Động từ",
        "meaning": "xuống xe",
        "note": (
            "Dùng khi rời khỏi xe buýt, "
            "tàu, ô tô hoặc phương tiện khác."
        ),
    },

    "远": {
        "type": "Tính từ",
        "meaning": "xa",
        "note": (
            "Dùng để nói khoảng cách lớn "
            "giữa hai địa điểm."
        ),
    },

    "站": {
        "type": "Danh từ / động từ",
        "meaning": "trạm; ga; đứng",
        "note": (
            "Trong bài giao thông chủ yếu dùng "
            "với nghĩa trạm hoặc ga; cũng có nghĩa đứng."
        ),
    },

    "走": {
        "type": "Động từ",
        "meaning": "đi; đi bộ; rời đi",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "di chuyển hoặc đi khỏi một nơi."
        ),
    },

    "走路": {
        "type": "Động từ",
        "meaning": "đi bộ",
        "note": (
            "Dùng để nói việc di chuyển "
            "bằng chân."
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
    print("09G16 - KIEM DUYET TU VUNG BAI 14")
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
    # 4. KIEM TRA BAI 1 -> 13
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
    # 5. LAY BAI 14
    # =====================================================
    lesson14 = get_lesson_rows(
        rows,
        14,
    )

    if len(lesson14) != 22:
        raise RuntimeError(
            "Bai 14 phai co dung 22 tu. "
            f"Thuc te: {len(lesson14)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson14
    }

    expected_words = set(
        LESSON14_REVIEW.keys()
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
            "Danh sach 22 tu Bai 14 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 14 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson14
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 14 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 15 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 15
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 15 -> 23 "
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
    # 10. CAP NHAT BAI 14
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 14:
            continue

        word = row["ChuHan"].strip()
        review = LESSON14_REVIEW[word]

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
            "So dong cap nhat Bai 14 "
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
    # 13. VERIFY BAI 1 -> 14
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
    # 14. DAM BAO BAI 15 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson14 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 15
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson14:
        raise RuntimeError(
            "Bai 15 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 14
    # =====================================================
    lesson14_verified = get_reviewed_rows(
        verify_rows,
        14,
    )

    lesson14_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 14 SAU REVIEW")
    print("-" * 95)

    for row in lesson14_verified:

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

    if reviewed_total != 331:
        raise RuntimeError(
            "Sau Bai 14 phai co "
            "331 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 170:
        raise RuntimeError(
            "Sau Bai 14 phai con "
            "170 tu chua kiem duyet. "
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