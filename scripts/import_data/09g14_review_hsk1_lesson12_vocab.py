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
# NOI DUNG HOC TAP BAI 12
#
# 我家在这里 - Nhà tôi ở đây
#
# Chu de:
# - Nha cua
# - Phong va tang
# - Vi tri trong / ngoai / tren / duoi
# - Do vat co ban trong nha
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON12_REVIEW = {

    "床": {
        "type": "Danh từ",
        "meaning": "giường",
        "note": (
            "Đồ dùng trong nhà dùng để nằm hoặc ngủ."
        ),
    },

    "地上": {
        "type": "Danh từ chỉ nơi chốn",
        "meaning": "trên mặt đất; trên sàn",
        "note": (
            "Dùng để chỉ vị trí ở trên mặt đất "
            "hoặc trên sàn nhà."
        ),
    },

    "房间": {
        "type": "Danh từ",
        "meaning": "phòng; căn phòng",
        "note": (
            "Chỉ một phòng trong nhà hoặc "
            "trong một tòa nhà."
        ),
    },

    "房子": {
        "type": "Danh từ",
        "meaning": "nhà; căn nhà",
        "note": (
            "Chỉ nơi ở hoặc một căn nhà."
        ),
    },

    "干净": {
        "type": "Tính từ",
        "meaning": "sạch; sạch sẽ",
        "note": (
            "Dùng để miêu tả phòng, nhà hoặc đồ vật "
            "không bẩn."
        ),
    },

    "间": {
        "type": "Lượng từ",
        "meaning": "gian; phòng",
        "note": (
            "Lượng từ dùng cho phòng, "
            "ví dụ 一间房间."
        ),
    },

    "里": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "trong; bên trong",
        "note": (
            "Dùng sau danh từ để chỉ phía bên trong, "
            "ví dụ 房间里."
        ),
    },

    "里边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "bên trong; phía trong",
        "note": (
            "Dùng để chỉ vị trí phía bên trong "
            "một nơi hoặc vật."
        ),
    },

    "楼": {
        "type": "Danh từ",
        "meaning": "tòa nhà; tầng",
        "note": (
            "Có thể chỉ tòa nhà nhiều tầng hoặc "
            "một tầng trong tòa nhà tùy ngữ cảnh."
        ),
    },

    "楼上": {
        "type": "Danh từ chỉ nơi chốn",
        "meaning": "tầng trên; trên lầu",
        "note": (
            "Chỉ tầng hoặc khu vực ở phía trên."
        ),
    },

    "楼下": {
        "type": "Danh từ chỉ nơi chốn",
        "meaning": "tầng dưới; dưới lầu",
        "note": (
            "Chỉ tầng hoặc khu vực ở phía dưới."
        ),
    },

    "门": {
        "type": "Danh từ",
        "meaning": "cửa; cổng",
        "note": (
            "Trong bài này dùng chủ yếu với nghĩa "
            "cửa hoặc cổng của nhà/phòng."
        ),
    },

    "门口": {
        "type": "Danh từ chỉ nơi chốn",
        "meaning": "cửa ra vào; trước cửa",
        "note": (
            "Chỉ khu vực ở ngay lối ra vào "
            "của nhà hoặc phòng."
        ),
    },

    "上": {
        "type": "Danh từ chỉ phương vị / động từ",
        "meaning": "trên; lên",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "vị trí phía trên hoặc hướng lên."
        ),
    },

    "上边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "phía trên; bên trên",
        "note": (
            "Dùng để chỉ vị trí ở phía trên "
            "một người hoặc vật."
        ),
    },

    "外": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "ngoài; bên ngoài",
        "note": (
            "Trong bài này dùng để chỉ vị trí "
            "ở phía ngoài."
        ),
    },

    "外边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "bên ngoài; phía ngoài",
        "note": (
            "Chỉ khu vực ở phía ngoài "
            "một nơi hoặc vật."
        ),
    },

    "洗手间": {
        "type": "Danh từ",
        "meaning": "nhà vệ sinh; phòng vệ sinh",
        "note": (
            "Cách gọi thông dụng của nhà vệ sinh."
        ),
    },

    "下": {
        "type": "Danh từ chỉ phương vị / động từ",
        "meaning": "dưới; xuống",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "vị trí phía dưới hoặc hướng xuống."
        ),
    },

    "下边": {
        "type": "Danh từ chỉ phương vị",
        "meaning": "phía dưới; bên dưới",
        "note": (
            "Dùng để chỉ vị trí ở phía dưới "
            "một người hoặc vật."
        ),
    },

    "住": {
        "type": "Động từ",
        "meaning": "ở; sống; cư trú",
        "note": (
            "Dùng để nói một người sống hoặc "
            "ở tại một địa điểm, ví dụ 我住在这里."
        ),
    },

    "桌子": {
        "type": "Danh từ",
        "meaning": "bàn",
        "note": (
            "Đồ dùng có mặt phẳng dùng để học, "
            "làm việc hoặc đặt đồ."
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
    print("09G14 - KIEM DUYET TU VUNG BAI 12")
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
    # 4. KIEM TRA BAI 1 -> 11
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
    # 5. LAY BAI 12
    # =====================================================
    lesson12 = get_lesson_rows(
        rows,
        12,
    )

    if len(lesson12) != 22:
        raise RuntimeError(
            "Bai 12 phai co dung 22 tu. "
            f"Thuc te: {len(lesson12)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson12
    }

    expected_words = set(
        LESSON12_REVIEW.keys()
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
            "Danh sach 22 tu Bai 12 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 12 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson12
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 12 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 13 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 13
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 13 -> 23 "
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
    # 10. CAP NHAT BAI 12
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 12:
            continue

        word = row["ChuHan"].strip()
        review = LESSON12_REVIEW[word]

        row["TuLoaiHocTap"] = review["type"]
        row["NghiaHocTap"] = review["meaning"]
        row["GhiChuKiemDuyet"] = review["note"]
        row["DaKiemDuyet"] = "1"

        updated += 1

    if updated != 22:
        raise RuntimeError(
            "So dong cap nhat Bai 12 "
            "khong bang 22."
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
    # 13. VERIFY BAI 1 -> 12
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
    # 14. DAM BAO BAI 13 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson12 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 13
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson12:
        raise RuntimeError(
            "Bai 13 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 12
    # =====================================================
    lesson12_verified = get_reviewed_rows(
        verify_rows,
        12,
    )

    lesson12_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 12 SAU REVIEW")
    print("-" * 95)

    for row in lesson12_verified:

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

    if reviewed_total != 279:
        raise RuntimeError(
            "Sau Bai 12 phai co "
            "279 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 222:
        raise RuntimeError(
            "Sau Bai 12 phai con "
            "222 tu chua kiem duyet. "
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