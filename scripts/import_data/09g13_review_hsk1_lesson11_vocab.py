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
# NOI DUNG HOC TAP BAI 11
#
# 我去商店买东西
# Tôi đi cửa hàng mua đồ
#
# Chu de:
# - Mua sam
# - Tien bac
# - Quan ao / do dung
# - Dai tu chi dinh va so luong co ban
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON11_REVIEW = {

    "包": {
        "type": "Danh từ / động từ / lượng từ",
        "meaning": "túi; gói; bọc",
        "note": (
            "Trong bài mua sắm tập trung vào nghĩa "
            "túi, gói hoặc hành động gói/bọc."
        ),
    },

    "别的": {
        "type": "Đại từ",
        "meaning": "khác; cái khác",
        "note": (
            "Dùng để chỉ người hoặc vật khác "
            "so với đối tượng đang nói tới."
        ),
    },

    "东西": {
        "type": "Danh từ",
        "meaning": "đồ vật; đồ; thứ",
        "note": (
            "Trong bài này dùng để nói chung "
            "các món đồ cần mua."
        ),
    },

    "贵": {
        "type": "Tính từ",
        "meaning": "đắt",
        "note": (
            "Trong bài mua sắm dùng để nói "
            "giá của món đồ cao."
        ),
    },

    "买": {
        "type": "Động từ",
        "meaning": "mua",
        "note": (
            "Động từ cơ bản chỉ hoạt động "
            "mua hàng hoặc mua đồ."
        ),
    },

    "哪": {
        "type": "Đại từ nghi vấn",
        "meaning": "nào; cái nào",
        "note": (
            "Dùng để hỏi lựa chọn giữa người "
            "hoặc sự vật, thường đi với lượng từ."
        ),
    },

    "哪些": {
        "type": "Đại từ nghi vấn",
        "meaning": "những cái nào; những gì",
        "note": (
            "Dạng số nhiều dùng để hỏi "
            "nhiều đối tượng."
        ),
    },

    "那": {
        "type": "Đại từ chỉ định",
        "meaning": "đó; cái đó",
        "note": (
            "Dùng để chỉ người hoặc vật "
            "ở xa người nói."
        ),
    },

    "那些": {
        "type": "Đại từ chỉ định",
        "meaning": "những cái đó",
        "note": (
            "Dạng số nhiều của 那 khi chỉ "
            "nhiều người hoặc vật."
        ),
    },

    "钱": {
        "type": "Danh từ",
        "meaning": "tiền",
        "note": (
            "Trong bài này dùng với nghĩa "
            "tiền dùng để mua bán."
        ),
    },

    "钱包": {
        "type": "Danh từ",
        "meaning": "ví; ví tiền",
        "note": (
            "Đồ dùng để đựng tiền, thẻ "
            "và giấy tờ nhỏ."
        ),
    },

    "商场": {
        "type": "Danh từ",
        "meaning": "trung tâm thương mại; trung tâm mua sắm",
        "note": (
            "Nơi tập trung nhiều cửa hàng "
            "và hoạt động mua bán."
        ),
    },

    "商店": {
        "type": "Danh từ",
        "meaning": "cửa hàng; tiệm",
        "note": (
            "Nơi bán hàng hóa."
        ),
    },

    "书店": {
        "type": "Danh từ",
        "meaning": "nhà sách; cửa hàng sách",
        "note": (
            "Cửa hàng chuyên bán sách "
            "và một số đồ dùng liên quan."
        ),
    },

    "新": {
        "type": "Tính từ",
        "meaning": "mới",
        "note": (
            "Dùng để miêu tả đồ vật mới, "
            "ví dụ 新衣服."
        ),
    },

    "衣服": {
        "type": "Danh từ",
        "meaning": "quần áo",
        "note": (
            "Cách gọi chung các loại trang phục."
        ),
    },

    "一点儿": {
        "type": "Cụm chỉ số lượng",
        "meaning": "một chút; một ít",
        "note": (
            "Dùng để chỉ số lượng hoặc mức độ nhỏ."
        ),
    },

    "一些": {
        "type": "Đại từ / số lượng từ",
        "meaning": "một số; một vài; một ít",
        "note": (
            "Dùng để chỉ số lượng không nhiều "
            "và không xác định chính xác."
        ),
    },

    "有的": {
        "type": "Đại từ",
        "meaning": "một số; có cái; có người",
        "note": (
            "Dùng để chỉ một bộ phận trong "
            "một nhóm người hoặc sự vật."
        ),
    },

    "有（一）些": {
        "type": "Đại từ",
        "meaning": "một chút; một ít; một số",
        "note": (
            "Dùng để diễn tả số lượng hoặc "
            "mức độ không lớn."
        ),
    },

    "元": {
        "type": "Lượng từ / đơn vị tiền tệ",
        "meaning": "tệ; đồng nhân dân tệ",
        "note": (
            "Trong bài mua sắm dùng làm đơn vị "
            "tiền tệ, ví dụ 十元."
        ),
    },

    "这": {
        "type": "Đại từ chỉ định",
        "meaning": "này; cái này",
        "note": (
            "Dùng để chỉ người hoặc vật "
            "ở gần người nói."
        ),
    },

    "这些": {
        "type": "Đại từ chỉ định",
        "meaning": "những cái này",
        "note": (
            "Dạng số nhiều của 这 khi chỉ "
            "nhiều người hoặc vật."
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
    print("09G13 - KIEM DUYET TU VUNG BAI 11")
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
    # 2. DOC CSV
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
    # 4. KIEM TRA BAI 1 -> 10
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
    # 5. LAY BAI 11
    # =====================================================
    lesson11 = get_lesson_rows(
        rows,
        11,
    )

    if len(lesson11) != 23:

        raise RuntimeError(
            "Bai 11 phai co dung 23 tu. "
            f"Thuc te: {len(lesson11)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson11
    }

    expected_words = set(
        LESSON11_REVIEW.keys()
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
            "Danh sach 23 tu Bai 11 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 11 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson11
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 11 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 12 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 12
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 12 -> 23 "
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
    # 10. CAP NHAT BAI 11
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 11:
            continue

        word = row["ChuHan"].strip()

        review = LESSON11_REVIEW[word]

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

    if updated != 23:

        raise RuntimeError(
            "So dong cap nhat Bai 11 "
            "khong bang 23."
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
    # 13. VERIFY BAI 1 -> 11
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
    # 14. DAM BAO BAI 12 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson11 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 12
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson11:

        raise RuntimeError(
            "Bai 12 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 11
    # =====================================================
    lesson11_verified = get_reviewed_rows(
        verify_rows,
        11,
    )

    lesson11_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 11 SAU REVIEW")
    print("-" * 95)

    for row in lesson11_verified:

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

    if reviewed_total != 257:

        raise RuntimeError(
            "Sau Bai 11 phai co "
            "257 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 244:

        raise RuntimeError(
            "Sau Bai 11 phai con "
            "244 tu chua kiem duyet. "
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