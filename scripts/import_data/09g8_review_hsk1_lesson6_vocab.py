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
# NOI DUNG HOC TAP BAI 6
#
# 现在几点？ - Bây giờ mấy giờ?
#
# Chu de:
# - Gio giac
# - Cac buoi trong ngay
# - Tan suat / trinh tu thoi gian
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON6_REVIEW = {

    "白天": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "ban ngày",
        "note": (
            "Chỉ khoảng thời gian từ sáng đến trước buổi tối."
        ),
    },

    "半天": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "nửa ngày",
        "note": (
            "Trong bài này dùng với nghĩa khoảng thời gian "
            "bằng một nửa ngày."
        ),
    },

    "常": {
        "type": "Phó từ",
        "meaning": "thường; thường xuyên",
        "note": (
            "Dùng để biểu thị hành động hoặc trạng thái "
            "xảy ra thường xuyên."
        ),
    },

    "常常": {
        "type": "Phó từ",
        "meaning": "thường xuyên; thường",
        "note": (
            "Biểu thị một hành động xảy ra nhiều lần."
        ),
    },

    "点": {
        "type": "Danh từ / lượng từ",
        "meaning": "giờ",
        "note": (
            "Trong bài này chủ yếu dùng để nói giờ, "
            "ví dụ 三点 là 3 giờ."
        ),
    },

    "分": {
        "type": "Danh từ / lượng từ",
        "meaning": "phút",
        "note": (
            "Trong bài này dùng làm đơn vị phút, "
            "ví dụ 三点十分 là 3 giờ 10 phút."
        ),
    },

    "马上": {
        "type": "Phó từ",
        "meaning": "ngay; lập tức",
        "note": (
            "Dùng khi một hành động sẽ xảy ra "
            "ngay trong thời gian rất ngắn."
        ),
    },

    "上次": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "lần trước",
        "note": (
            "Chỉ lần xảy ra trước lần hiện tại."
        ),
    },

    "上午": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "buổi sáng",
        "note": (
            "Chỉ khoảng thời gian từ sáng đến trước buổi trưa."
        ),
    },

    "时候": {
        "type": "Danh từ",
        "meaning": "lúc; khi; thời điểm",
        "note": (
            "Dùng để nói về một thời điểm hoặc "
            "khoảng thời gian, ví dụ 什么时候."
        ),
    },

    "时间": {
        "type": "Danh từ",
        "meaning": "thời gian",
        "note": (
            "Chỉ thời gian nói chung hoặc một khoảng thời gian."
        ),
    },

    "晚": {
        "type": "Tính từ",
        "meaning": "muộn; trễ",
        "note": (
            "Dùng để nói một hành động hoặc thời điểm "
            "xảy ra muộn."
        ),
    },

    "晚上": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "buổi tối; ban đêm",
        "note": (
            "Chỉ khoảng thời gian buổi tối."
        ),
    },

    "下次": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "lần sau; lần tới",
        "note": (
            "Chỉ lần xảy ra tiếp theo."
        ),
    },

    "下午": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "buổi chiều",
        "note": (
            "Chỉ khoảng thời gian sau buổi trưa "
            "và trước buổi tối."
        ),
    },

    "先": {
        "type": "Phó từ",
        "meaning": "trước; trước tiên",
        "note": (
            "Dùng để biểu thị hành động nào được "
            "thực hiện trước."
        ),
    },

    "现在": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "bây giờ; hiện tại",
        "note": (
            "Chỉ thời điểm hiện tại, ví dụ 现在几点？"
        ),
    },

    "小时": {
        "type": "Danh từ / lượng từ",
        "meaning": "giờ; tiếng đồng hồ",
        "note": (
            "Đơn vị chỉ khoảng thời gian 60 phút, "
            "ví dụ 两个小时."
        ),
    },

    "一会儿": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "một lát; một lúc",
        "note": (
            "Chỉ một khoảng thời gian ngắn, "
            "ví dụ 等一会儿."
        ),
    },

    "有时候": {
        "type": "Phó từ",
        "meaning": "đôi khi; thỉnh thoảng",
        "note": (
            "Biểu thị một hành động chỉ xảy ra "
            "trong một số thời điểm."
        ),
    },

    "早": {
        "type": "Tính từ / phó từ",
        "meaning": "sớm",
        "note": (
            "Dùng để nói thời điểm sớm, "
            "ví dụ 很早."
        ),
    },

    "早上": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "buổi sáng; sáng sớm",
        "note": (
            "Chỉ khoảng thời gian đầu buổi sáng."
        ),
    },

    "中午": {
        "type": "Danh từ chỉ thời gian",
        "meaning": "buổi trưa",
        "note": (
            "Chỉ khoảng thời gian giữa ngày."
        ),
    },

    "最后": {
        "type": "Danh từ / phó từ",
        "meaning": "cuối cùng; sau cùng",
        "note": (
            "Dùng để chỉ vị trí hoặc hành động "
            "ở cuối một trình tự."
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
    print("09G8 - KIEM DUYET TU VUNG BAI 6")
    print("=" * 95)

    # =====================================================
    # 1. KIEM TRA FILE REVIEW
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
    # 4. KIEM TRA BAI 1 -> 5
    # =====================================================
    expected_previous = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
        5: 20,
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
    # 5. LAY BAI 6
    # =====================================================
    lesson6 = get_lesson_rows(
        rows,
        6,
    )

    if len(lesson6) != 24:

        raise RuntimeError(
            "Bai 6 phai co dung 24 tu. "
            f"Thuc te: {len(lesson6)}"
        )

    # =====================================================
    # 6. DOI CHIEU 24 TU
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson6
    }

    expected_words = set(
        LESSON6_REVIEW.keys()
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
            "Danh sach 24 tu Bai 6 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 6 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson6
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 6 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. BAI 7 -> 23 PHAI CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 7
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 7 -> 23 "
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
    # 10. CAP NHAT BAI 6
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 6:
            continue

        word = row["ChuHan"].strip()

        review = LESSON6_REVIEW[word]

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
            "So dong cap nhat Bai 6 "
            "khong bang 24."
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
    # 13. VERIFY BAI 1 -> 6
    # =====================================================
    expected_after = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
        5: 20,
        6: 24,
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
    # 14. DAM BAO BAI 7 -> 23 CHUA DOI
    # =====================================================
    reviewed_after_lesson6 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 7
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson6:

        raise RuntimeError(
            "Bai 7 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 6
    # =====================================================
    lesson6_verified = get_reviewed_rows(
        verify_rows,
        6,
    )

    lesson6_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 6 SAU REVIEW")
    print("-" * 95)

    for row in lesson6_verified:

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

    if reviewed_total != 135:

        raise RuntimeError(
            "Sau Bai 6 phai co "
            "135 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 366:

        raise RuntimeError(
            "Sau Bai 6 phai con "
            "366 tu chua kiem duyet. "
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

    for lesson_no, count in expected_after.items():

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