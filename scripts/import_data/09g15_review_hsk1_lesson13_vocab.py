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
# NOI DUNG HOC TAP BAI 13
#
# 桌子在左边 - Cái bàn ở bên trái
#
# Chu de:
# - Vi tri
# - Phuong huong
# - Ben trai / ben phai
# - Phia truoc / phia sau
# - Dong / Tay / Nam / Bac
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON13_REVIEW = {

    "北": {
        "type": "Danh từ chỉ phương hướng",
        "meaning": "bắc; phía bắc",
        "note": (
            "Trong bài này dùng để chỉ "
            "phương bắc."
        ),
    },

    "北边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "phía bắc; bên phía bắc",
        "note": (
            "Dùng để chỉ vị trí nằm về "
            "phía bắc của một nơi."
        ),
    },

    "地": {
        "type": "Danh từ",
        "meaning": "đất; mặt đất",
        "note": (
            "Đây là cách đọc dì. "
            "Cần phân biệt với 地 de là trợ từ."
        ),
    },

    "地点": {
        "type": "Danh từ",
        "meaning": "địa điểm; nơi; chỗ",
        "note": (
            "Dùng để chỉ một địa điểm "
            "hoặc nơi cụ thể."
        ),
    },

    "地方": {
        "type": "Danh từ",
        "meaning": "nơi; chỗ; địa phương",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "nơi hoặc chỗ."
        ),
    },

    "东": {
        "type": "Danh từ chỉ phương hướng",
        "meaning": "đông; phía đông",
        "note": (
            "Trong bài này dùng để chỉ "
            "phương đông."
        ),
    },

    "东边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "phía đông; bên phía đông",
        "note": (
            "Dùng để chỉ vị trí nằm về "
            "phía đông."
        ),
    },

    "后": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "sau; phía sau",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "vị trí phía sau."
        ),
    },

    "后边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "phía sau; đằng sau",
        "note": (
            "Dùng để chỉ vị trí ở phía sau "
            "một người hoặc vật."
        ),
    },

    "那边": {
        "type": "Đại từ chỉ nơi chốn",
        "meaning": "đằng kia; bên đó",
        "note": (
            "Dùng để chỉ một khu vực hoặc "
            "vị trí ở xa người nói."
        ),
    },

    "那里": {
        "type": "Đại từ chỉ nơi chốn",
        "meaning": "ở đó; nơi đó",
        "note": (
            "Dùng để chỉ một địa điểm "
            "ở xa người nói."
        ),
    },

    "那儿": {
        "type": "Đại từ chỉ nơi chốn",
        "meaning": "ở đó; đằng đó",
        "note": (
            "Cách nói có 儿化, tương đương 那里."
        ),
    },

    "南": {
        "type": "Danh từ chỉ phương hướng",
        "meaning": "nam; phía nam",
        "note": (
            "Trong bài này dùng để chỉ "
            "phương nam."
        ),
    },

    "南边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "phía nam; bên phía nam",
        "note": (
            "Dùng để chỉ vị trí nằm về "
            "phía nam."
        ),
    },

    "旁边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "bên cạnh; cạnh bên",
        "note": (
            "Dùng để chỉ vị trí ở ngay bên "
            "một người hoặc vật."
        ),
    },

    "前": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "trước; phía trước",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "vị trí phía trước."
        ),
    },

    "前边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "phía trước; đằng trước",
        "note": (
            "Dùng để chỉ vị trí ở phía trước "
            "một người hoặc vật."
        ),
    },

    "西": {
        "type": "Danh từ chỉ phương hướng",
        "meaning": "tây; phía tây",
        "note": (
            "Trong bài này dùng để chỉ "
            "phương tây."
        ),
    },

    "西边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "phía tây; bên phía tây",
        "note": (
            "Dùng để chỉ vị trí nằm về "
            "phía tây."
        ),
    },

    "一边": {
        "type": "Danh từ / phó từ",
        "meaning": "một bên; một phía",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "một bên hoặc một phía."
        ),
    },

    "右": {
        "type": "Danh từ chỉ phương hướng",
        "meaning": "phải; bên phải",
        "note": (
            "Trong bài này chỉ dùng nghĩa "
            "phương vị bên phải."
        ),
    },

    "右边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "bên phải; phía bên phải",
        "note": (
            "Dùng để chỉ vị trí ở phía "
            "bên phải."
        ),
    },

    "这边": {
        "type": "Đại từ chỉ nơi chốn",
        "meaning": "bên này; phía này; ở đây",
        "note": (
            "Dùng để chỉ khu vực ở gần "
            "người nói."
        ),
    },

    "这儿": {
        "type": "Đại từ chỉ nơi chốn",
        "meaning": "ở đây",
        "note": (
            "Cách nói có 儿化, tương đương 这里."
        ),
    },

    "这里": {
        "type": "Đại từ chỉ nơi chốn",
        "meaning": "ở đây; nơi này",
        "note": (
            "Dùng để chỉ vị trí gần "
            "người nói."
        ),
    },

    "正": {
        "type": "Phó từ / tính từ",
        "meaning": "chính; đúng; ngay",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "đúng vị trí hoặc ngay tại một vị trí."
        ),
    },

    "中": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "trong; giữa; ở giữa",
        "note": (
            "Trong bài này dùng để chỉ "
            "vị trí bên trong hoặc ở giữa."
        ),
    },

    "中间": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "ở giữa; chính giữa",
        "note": (
            "Dùng để chỉ vị trí nằm giữa "
            "hai hoặc nhiều đối tượng."
        ),
    },

    "左": {
        "type": "Danh từ chỉ phương hướng",
        "meaning": "trái; bên trái",
        "note": (
            "Trong bài này chỉ dùng nghĩa "
            "phương vị bên trái."
        ),
    },

    "左边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "bên trái; phía bên trái",
        "note": (
            "Dùng để chỉ vị trí ở phía "
            "bên trái, ví dụ 桌子在左边."
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
    print("09G15 - KIEM DUYET TU VUNG BAI 13")
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
    # 4. KIEM TRA BAI 1 -> 12
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
    # 5. LAY BAI 13
    # =====================================================
    lesson13 = get_lesson_rows(
        rows,
        13,
    )

    if len(lesson13) != 30:
        raise RuntimeError(
            "Bai 13 phai co dung 30 tu. "
            f"Thuc te: {len(lesson13)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson13
    }

    expected_words = set(
        LESSON13_REVIEW.keys()
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
            "Danh sach 30 tu Bai 13 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 13 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson13
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 13 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 14 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 14
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 14 -> 23 "
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
    # 10. CAP NHAT BAI 13
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 13:
            continue

        word = row["ChuHan"].strip()

        review = LESSON13_REVIEW[word]

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

    if updated != 30:
        raise RuntimeError(
            "So dong cap nhat Bai 13 "
            "khong bang 30."
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
    # 13. VERIFY BAI 1 -> 13
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
    # 14. DAM BAO BAI 14 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson13 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 14
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson13:
        raise RuntimeError(
            "Bai 14 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 13
    # =====================================================
    lesson13_verified = get_reviewed_rows(
        verify_rows,
        13,
    )

    lesson13_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 13 SAU REVIEW")
    print("-" * 95)

    for row in lesson13_verified:

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

    if reviewed_total != 309:
        raise RuntimeError(
            "Sau Bai 13 phai co "
            "309 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 192:
        raise RuntimeError(
            "Sau Bai 13 phai con "
            "192 tu chua kiem duyet. "
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