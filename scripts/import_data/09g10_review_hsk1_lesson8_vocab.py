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
# NOI DUNG HOC TAP BAI 8
#
# 请打开课本 - Mời mở sách giáo khoa
#
# Chu de:
# - Lop hoc
# - Sach vo
# - Doc / viet / nghe / noi
# - Ghi nho / hoi dap
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON8_REVIEW = {

    "本子": {
        "type": "Danh từ",
        "meaning": "vở; quyển vở",
        "note": (
            "Trong bài này dùng với nghĩa vở "
            "dùng để ghi chép khi học."
        ),
    },

    "打开": {
        "type": "Động từ",
        "meaning": "mở; bật",
        "note": (
            "Trong bài này chủ yếu dùng với nghĩa "
            "mở sách hoặc mở một đồ vật, "
            "ví dụ 打开课本."
        ),
    },

    "读": {
        "type": "Động từ",
        "meaning": "đọc; đọc thành tiếng",
        "note": (
            "Dùng để nói hoạt động đọc chữ, "
            "đọc bài hoặc đọc thành tiếng."
        ),
    },

    "读书": {
        "type": "Động từ",
        "meaning": "đọc sách; học",
        "note": (
            "Có thể chỉ việc đọc sách hoặc "
            "học tập tại trường."
        ),
    },

    "关上": {
        "type": "Động từ",
        "meaning": "đóng; tắt",
        "note": (
            "Dùng để đóng cửa, sách hoặc "
            "tắt thiết bị tùy ngữ cảnh."
        ),
    },

    "回答": {
        "type": "Động từ / danh từ",
        "meaning": "trả lời; câu trả lời",
        "note": (
            "Trong lớp học thường dùng khi "
            "trả lời câu hỏi của giáo viên."
        ),
    },

    "记": {
        "type": "Động từ",
        "meaning": "ghi; nhớ; ghi nhớ",
        "note": (
            "Dùng để ghi chép hoặc ghi nhớ "
            "một nội dung."
        ),
    },

    "记得": {
        "type": "Động từ",
        "meaning": "nhớ",
        "note": (
            "Dùng khi vẫn nhớ một người, "
            "sự việc hoặc nội dung đã học."
        ),
    },

    "记住": {
        "type": "Động từ",
        "meaning": "ghi nhớ; nhớ kỹ",
        "note": (
            "Nhấn mạnh việc ghi một nội dung "
            "vào trí nhớ."
        ),
    },

    "课本": {
        "type": "Danh từ",
        "meaning": "sách giáo khoa",
        "note": (
            "Sách dùng làm tài liệu chính "
            "trong một môn học."
        ),
    },

    "课文": {
        "type": "Danh từ",
        "meaning": "bài khóa; bài đọc",
        "note": (
            "Chỉ phần văn bản chính "
            "trong một bài học."
        ),
    },

    "试": {
        "type": "Động từ",
        "meaning": "thử",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "thử làm một việc, ví dụ 试一试."
        ),
    },

    "书": {
        "type": "Danh từ",
        "meaning": "sách",
        "note": (
            "Danh từ chung chỉ sách."
        ),
    },

    "书包": {
        "type": "Danh từ",
        "meaning": "cặp sách; ba lô đi học",
        "note": (
            "Túi hoặc ba lô dùng để đựng "
            "sách vở và đồ dùng học tập."
        ),
    },

    "说": {
        "type": "Động từ",
        "meaning": "nói",
        "note": (
            "Động từ cơ bản chỉ hoạt động nói, "
            "ví dụ 说中文."
        ),
    },

    "说话": {
        "type": "Động từ",
        "meaning": "nói; nói chuyện",
        "note": (
            "Dùng để chỉ hành động nói chuyện "
            "hoặc giao tiếp bằng lời."
        ),
    },

    "听": {
        "type": "Động từ",
        "meaning": "nghe",
        "note": (
            "Trong bài này dùng với nghĩa "
            "nghe âm thanh hoặc nghe giáo viên nói."
        ),
    },

    "听写": {
        "type": "Động từ / danh từ",
        "meaning": "viết chính tả; bài chính tả",
        "note": (
            "Hoạt động nghe từ hoặc câu rồi "
            "viết lại trong quá trình học."
        ),
    },

    "忘": {
        "type": "Động từ",
        "meaning": "quên",
        "note": (
            "Dùng khi không còn nhớ một việc "
            "hoặc thông tin."
        ),
    },

    "忘记": {
        "type": "Động từ",
        "meaning": "quên",
        "note": (
            "Dùng phổ biến để nói việc "
            "không nhớ người, sự việc hoặc nội dung."
        ),
    },

    "问": {
        "type": "Động từ",
        "meaning": "hỏi",
        "note": (
            "Dùng để đặt câu hỏi hoặc "
            "hỏi thông tin từ người khác."
        ),
    },

    "写": {
        "type": "Động từ",
        "meaning": "viết",
        "note": (
            "Dùng để nói hoạt động viết chữ, "
            "từ hoặc câu."
        ),
    },

    "页": {
        "type": "Lượng từ",
        "meaning": "trang",
        "note": (
            "Dùng để đếm trang sách, "
            "ví dụ 第十页."
        ),
    },

    "字": {
        "type": "Danh từ",
        "meaning": "chữ; ký tự",
        "note": (
            "Trong bài này chủ yếu chỉ "
            "chữ viết, đặc biệt là chữ Hán."
        ),
    },

    "子（桌子）": {
        "type": "Hậu tố",
        "meaning": "hậu tố danh từ",
        "note": (
            "子 trong một số từ như 桌子 "
            "là hậu tố tạo danh từ; "
            "thường đọc thanh nhẹ zi."
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
    print("09G10 - KIEM DUYET TU VUNG BAI 8")
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
    # 4. KIEM TRA BAI 1 -> 7
    # =====================================================
    expected_previous = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
        5: 20,
        6: 24,
        7: 28,
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
    # 5. LAY BAI 8
    # =====================================================
    lesson8 = get_lesson_rows(
        rows,
        8,
    )

    if len(lesson8) != 25:

        raise RuntimeError(
            "Bai 8 phai co dung 25 tu. "
            f"Thuc te: {len(lesson8)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson8
    }

    expected_words = set(
        LESSON8_REVIEW.keys()
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
            "Danh sach 25 tu Bai 8 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 8 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson8
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 8 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 9 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 9
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 9 -> 23 "
            "da co du lieu review."
        )

    # =====================================================
    # 9. TAO BACKUP
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
    # 10. CAP NHAT BAI 8
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 8:
            continue

        word = row["ChuHan"].strip()

        review = LESSON8_REVIEW[word]

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

    if updated != 25:

        raise RuntimeError(
            "So dong cap nhat Bai 8 "
            "khong bang 25."
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
    # 13. VERIFY BAI 1 -> 8
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
    # 14. DAM BAO BAI 9 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson8 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 9
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson8:

        raise RuntimeError(
            "Bai 9 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 8
    # =====================================================
    lesson8_verified = get_reviewed_rows(
        verify_rows,
        8,
    )

    lesson8_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 8 SAU REVIEW")
    print("-" * 95)

    for row in lesson8_verified:

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

    if reviewed_total != 188:

        raise RuntimeError(
            "Sau Bai 8 phai co "
            "188 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 313:

        raise RuntimeError(
            "Sau Bai 8 phai con "
            "313 tu chua kiem duyet. "
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