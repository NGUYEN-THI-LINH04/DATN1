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
# NOI DUNG HOC TAP BAI 7
#
# 我在学校学习汉语
# Tôi học tiếng Trung ở trường
#
# Chu de:
# - Truong hoc
# - Giao vien / hoc sinh
# - Hoc tap
# - Lop hoc / thi cu
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON7_REVIEW = {

    "班": {
        "type": "Danh từ / lượng từ",
        "meaning": "lớp; lớp học",
        "note": (
            "Trong bài này chủ yếu dùng với nghĩa "
            "một lớp học, ví dụ 我们班."
        ),
    },

    "大学": {
        "type": "Danh từ",
        "meaning": "trường đại học; đại học",
        "note": (
            "Chỉ cơ sở giáo dục bậc đại học."
        ),
    },

    "大学生": {
        "type": "Danh từ",
        "meaning": "sinh viên đại học",
        "note": (
            "Chỉ người đang học tại trường đại học."
        ),
    },

    "放假": {
        "type": "Động từ",
        "meaning": "nghỉ; nghỉ học; nghỉ lễ",
        "note": (
            "Chỉ khoảng thời gian được nghỉ học "
            "hoặc nghỉ làm."
        ),
    },

    "放学": {
        "type": "Động từ",
        "meaning": "tan học",
        "note": (
            "Chỉ thời điểm kết thúc buổi học "
            "và học sinh rời trường."
        ),
    },

    "教": {
        "type": "Động từ",
        "meaning": "dạy",
        "note": (
            "Dùng khi một người truyền đạt kiến thức "
            "hoặc kỹ năng cho người khác."
        ),
    },

    "教学楼": {
        "type": "Danh từ",
        "meaning": "tòa nhà giảng dạy; giảng đường",
        "note": (
            "Tòa nhà trong trường dùng cho "
            "hoạt động học và giảng dạy."
        ),
    },

    "考": {
        "type": "Động từ",
        "meaning": "thi; kiểm tra",
        "note": (
            "Trong bài học tập trung vào nghĩa "
            "tham gia hoặc thực hiện bài thi."
        ),
    },

    "考试": {
        "type": "Danh từ / động từ",
        "meaning": "kỳ thi; thi; kiểm tra",
        "note": (
            "Dùng để nói về hoạt động hoặc "
            "một kỳ kiểm tra, kỳ thi."
        ),
    },

    "课": {
        "type": "Danh từ",
        "meaning": "bài học; tiết học; môn học",
        "note": (
            "Dùng trong các từ như 上课、下课 "
            "hoặc để nói về một bài/tiết học."
        ),
    },

    "老师": {
        "type": "Danh từ",
        "meaning": "giáo viên; thầy giáo; cô giáo",
        "note": (
            "Cách gọi người làm công việc giảng dạy."
        ),
    },

    "请假": {
        "type": "Động từ",
        "meaning": "xin nghỉ",
        "note": (
            "Dùng khi xin phép nghỉ học hoặc nghỉ làm."
        ),
    },

    "认真": {
        "type": "Tính từ / phó từ",
        "meaning": "nghiêm túc; chăm chú",
        "note": (
            "Dùng để miêu tả thái độ làm việc "
            "hoặc học tập cẩn thận, nghiêm túc."
        ),
    },

    "上课": {
        "type": "Động từ",
        "meaning": "học; lên lớp; vào học",
        "note": (
            "Có thể chỉ học sinh tham gia lớp "
            "hoặc giáo viên lên lớp giảng dạy."
        ),
    },

    "上学": {
        "type": "Động từ",
        "meaning": "đi học",
        "note": (
            "Chỉ việc đến trường để học."
        ),
    },

    "同学": {
        "type": "Danh từ",
        "meaning": "bạn học; bạn cùng lớp",
        "note": (
            "Chỉ người cùng học tại một trường "
            "hoặc cùng một lớp."
        ),
    },

    "图书馆": {
        "type": "Danh từ",
        "meaning": "thư viện",
        "note": (
            "Nơi lưu giữ sách và tài liệu "
            "phục vụ đọc, học tập."
        ),
    },

    "下课": {
        "type": "Động từ",
        "meaning": "tan học; hết tiết",
        "note": (
            "Trong bài này chỉ thời điểm "
            "một tiết học kết thúc."
        ),
    },

    "小学": {
        "type": "Danh từ",
        "meaning": "trường tiểu học",
        "note": (
            "Cơ sở giáo dục bậc tiểu học."
        ),
    },

    "小学生": {
        "type": "Danh từ",
        "meaning": "học sinh tiểu học",
        "note": (
            "Chỉ học sinh đang học bậc tiểu học."
        ),
    },

    "学": {
        "type": "Động từ",
        "meaning": "học",
        "note": (
            "Động từ cơ bản diễn tả việc "
            "tiếp thu kiến thức hoặc kỹ năng."
        ),
    },

    "学生": {
        "type": "Danh từ",
        "meaning": "học sinh; sinh viên",
        "note": (
            "Cách gọi chung người đang học."
        ),
    },

    "学习": {
        "type": "Động từ",
        "meaning": "học; học tập",
        "note": (
            "Dùng để nói về hoạt động học tập, "
            "ví dụ 学习汉语."
        ),
    },

    "学校": {
        "type": "Danh từ",
        "meaning": "trường học",
        "note": (
            "Nơi tổ chức hoạt động dạy và học."
        ),
    },

    "学院": {
        "type": "Danh từ",
        "meaning": "học viện; trường; khoa",
        "note": (
            "Chỉ một cơ sở giáo dục hoặc "
            "một đơn vị đào tạo trong trường."
        ),
    },

    "知识": {
        "type": "Danh từ",
        "meaning": "kiến thức",
        "note": (
            "Những hiểu biết có được qua "
            "học tập hoặc trải nghiệm."
        ),
    },

    "中学": {
        "type": "Danh từ",
        "meaning": "trường trung học",
        "note": (
            "Chỉ trường ở bậc trung học."
        ),
    },

    "中学生": {
        "type": "Danh từ",
        "meaning": "học sinh trung học",
        "note": (
            "Chỉ học sinh đang học ở bậc trung học."
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
    print("09G9 - KIEM DUYET TU VUNG BAI 7")
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
    # 4. KIEM TRA BAI 1 -> 6
    # =====================================================
    expected_previous = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
        5: 20,
        6: 24,
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
    # 5. LAY BAI 7
    # =====================================================
    lesson7 = get_lesson_rows(
        rows,
        7,
    )

    if len(lesson7) != 28:

        raise RuntimeError(
            "Bai 7 phai co dung 28 tu. "
            f"Thuc te: {len(lesson7)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH 28 TU
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson7
    }

    expected_words = set(
        LESSON7_REVIEW.keys()
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
            "Danh sach 28 tu Bai 7 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 7 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson7
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 7 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 8 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 8
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 8 -> 23 "
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
    # 10. CAP NHAT BAI 7
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 7:
            continue

        word = row["ChuHan"].strip()

        review = LESSON7_REVIEW[word]

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

    if updated != 28:

        raise RuntimeError(
            "So dong cap nhat Bai 7 "
            "khong bang 28."
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
    # 13. VERIFY BAI 1 -> 7
    # =====================================================
    expected_after = {
        1: 13,
        2: 29,
        3: 23,
        4: 26,
        5: 20,
        6: 24,
        7: 28,
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
    # 14. BAI 8 -> 23 KHONG DUOC THAY DOI
    # =====================================================
    reviewed_after_lesson7 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 8
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson7:

        raise RuntimeError(
            "Bai 8 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 7
    # =====================================================
    lesson7_verified = get_reviewed_rows(
        verify_rows,
        7,
    )

    lesson7_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 7 SAU REVIEW")
    print("-" * 95)

    for row in lesson7_verified:

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

    if reviewed_total != 163:

        raise RuntimeError(
            "Sau Bai 7 phai co "
            "163 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 338:

        raise RuntimeError(
            "Sau Bai 7 phai con "
            "338 tu chua kiem duyet. "
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