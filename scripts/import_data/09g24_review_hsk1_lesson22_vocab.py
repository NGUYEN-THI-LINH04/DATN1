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
# NOI DUNG HOC TAP BAI 22
#
# 我给你打电话
# Tôi gọi điện cho bạn
#
# Chu de:
# - Lien lac
# - Goi dien
# - Loi moi
# - Xin loi / cam on
# - Phep lich su co ban
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON22_REVIEW = {

    "不客气": {
        "type": "Cụm từ lịch sự",
        "meaning": "không có gì; không có chi",
        "note": (
            "Trong bài này dùng làm lời đáp lịch sự "
            "sau khi người khác nói 谢谢."
        ),
    },

    "打电话": {
        "type": "Động từ",
        "meaning": "gọi điện thoại",
        "note": (
            "Từ trọng tâm của bài, "
            "ví dụ 我给你打电话."
        ),
    },

    "电话": {
        "type": "Danh từ",
        "meaning": "điện thoại; cuộc gọi điện thoại",
        "note": (
            "Trong bài này dùng để nói điện thoại "
            "hoặc cuộc gọi điện thoại."
        ),
    },

    "对不起": {
        "type": "Cụm từ lịch sự",
        "meaning": "xin lỗi; xin thứ lỗi",
        "note": (
            "Dùng để xin lỗi khi làm phiền "
            "hoặc gây lỗi với người khác."
        ),
    },

    "告诉": {
        "type": "Động từ",
        "meaning": "nói; cho biết; thông báo",
        "note": (
            "Dùng khi truyền đạt thông tin "
            "cho một người khác."
        ),
    },

    "给": {
        "type": "Động từ / giới từ",
        "meaning": "cho; đưa; cho ai",
        "note": (
            "Trong bài này có thể dùng để đưa vật "
            "hoặc chỉ người nhận hành động, "
            "ví dụ 给你打电话."
        ),
    },

    "话": {
        "type": "Danh từ",
        "meaning": "lời nói; lời; câu nói",
        "note": (
            "Trong bài liên lạc dùng với nghĩa "
            "lời nói hoặc điều được nói ra."
        ),
    },

    "见": {
        "type": "Động từ",
        "meaning": "gặp; thấy",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "gặp hoặc nhìn thấy một người."
        ),
    },

    "见面": {
        "type": "Động từ",
        "meaning": "gặp mặt; gặp nhau",
        "note": (
            "Dùng khi hai hoặc nhiều người "
            "trực tiếp gặp nhau."
        ),
    },

    "没关系": {
        "type": "Cụm từ lịch sự",
        "meaning": "không sao; không có gì",
        "note": (
            "Thường dùng để đáp lại lời xin lỗi "
            "và cho biết sự việc không nghiêm trọng."
        ),
    },

    "没事儿": {
        "type": "Cụm từ",
        "meaning": "không sao; không có gì",
        "note": (
            "Trong bài này ưu tiên nghĩa dùng để "
            "trấn an hoặc nói rằng không có vấn đề gì."
        ),
    },

    "请": {
        "type": "Động từ",
        "meaning": "mời; xin; vui lòng",
        "note": (
            "Dùng trong lời mời hoặc yêu cầu "
            "một cách lịch sự."
        ),
    },

    "请进": {
        "type": "Cụm từ lịch sự",
        "meaning": "mời vào",
        "note": (
            "Dùng để mời một người đi vào "
            "phòng hoặc một nơi nào đó."
        ),
    },

    "请坐": {
        "type": "Cụm từ lịch sự",
        "meaning": "mời ngồi",
        "note": (
            "Dùng để mời một người ngồi xuống "
            "một cách lịch sự."
        ),
    },

    "事": {
        "type": "Danh từ",
        "meaning": "việc; chuyện; sự việc",
        "note": (
            "Danh từ chỉ một việc, chuyện "
            "hoặc vấn đề."
        ),
    },

    "手机": {
        "type": "Danh từ",
        "meaning": "điện thoại di động; điện thoại",
        "note": (
            "Thiết bị di động dùng để gọi điện, "
            "nhắn tin và liên lạc."
        ),
    },

    "谢谢": {
        "type": "Động từ / cách nói lịch sự",
        "meaning": "cảm ơn",
        "note": (
            "Cách nói cơ bản để bày tỏ "
            "sự cảm ơn."
        ),
    },

    "再见": {
        "type": "Động từ / cách nói lịch sự",
        "meaning": "tạm biệt; hẹn gặp lại",
        "note": (
            "Dùng khi kết thúc cuộc gặp "
            "hoặc cuộc trò chuyện."
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
    print("09G24 - KIEM DUYET TU VUNG BAI 22")
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
    # 4. KIEM TRA BAI 1 -> 21
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
        21: 20,
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
    # 5. LAY BAI 22
    # =====================================================
    lesson22 = get_lesson_rows(
        rows,
        22,
    )

    if len(lesson22) != 18:
        raise RuntimeError(
            "Bai 22 phai co dung 18 tu. "
            f"Thuc te: {len(lesson22)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson22
    }

    expected_words = set(
        LESSON22_REVIEW.keys()
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
            "Danh sach 18 tu Bai 22 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 22 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson22
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 22 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 23 CHUA REVIEW
    # =====================================================
    lesson23_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == 23
        and row["DaKiemDuyet"] == "1"
    ]

    if lesson23_reviewed:
        raise RuntimeError(
            "Phat hien Bai 23 da co du lieu review."
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
    # 10. CAP NHAT BAI 22
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 22:
            continue

        word = row["ChuHan"].strip()
        review = LESSON22_REVIEW[word]

        row["TuLoaiHocTap"] = review["type"]
        row["NghiaHocTap"] = review["meaning"]
        row["GhiChuKiemDuyet"] = review["note"]
        row["DaKiemDuyet"] = "1"

        updated += 1

    if updated != 18:
        raise RuntimeError(
            "So dong cap nhat Bai 22 "
            "khong bang 18."
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
    # 13. VERIFY BAI 1 -> 22
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
        22: 18,
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
    # 14. DAM BAO BAI 23 KHONG DOI
    # =====================================================
    lesson23_after = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) == 23
        and row["DaKiemDuyet"] == "1"
    ]

    if lesson23_after:
        raise RuntimeError(
            "Bai 23 bi thay doi ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 22
    # =====================================================
    lesson22_verified = get_reviewed_rows(
        verify_rows,
        22,
    )

    lesson22_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 22 SAU REVIEW")
    print("-" * 95)

    for row in lesson22_verified:

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

    if reviewed_total != 485:
        raise RuntimeError(
            "Sau Bai 22 phai co "
            "485 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 16:
        raise RuntimeError(
            "Sau Bai 22 phai con "
            "16 tu chua kiem duyet. "
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