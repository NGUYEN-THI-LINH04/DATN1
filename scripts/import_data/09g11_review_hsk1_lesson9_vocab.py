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
# NOI DUNG HOC TAP BAI 9
#
# 我每天上班 - Tôi đi làm mỗi ngày
#
# Chu de:
# - Sinh hoat hang ngay
# - Cong viec
# - Di lam / tan lam
# - Nghi ngoi / ngu nghi
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON9_REVIEW = {

    "穿": {
        "type": "Động từ",
        "meaning": "mặc; đi; mang",
        "note": (
            "Dùng với quần áo hoặc một số đồ mang trên người, "
            "ví dụ 穿衣服."
        ),
    },

    "等": {
        "type": "Động từ",
        "meaning": "đợi; chờ",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "đợi hoặc chờ một người, sự việc."
        ),
    },

    "动": {
        "type": "Động từ",
        "meaning": "động; di chuyển; cử động",
        "note": (
            "Dùng để nói người hoặc vật bắt đầu "
            "di chuyển hoặc cử động."
        ),
    },

    "动作": {
        "type": "Danh từ",
        "meaning": "động tác; hành động; cử động",
        "note": (
            "Chỉ một chuyển động hoặc động tác "
            "của cơ thể."
        ),
    },

    "干": {
        "type": "Động từ",
        "meaning": "làm; làm việc",
        "note": (
            "Đây là mục đọc gàn, dùng với nghĩa làm việc "
            "hoặc thực hiện một việc. Cần phân biệt với "
            "干 gān nghĩa là khô."
        ),
    },

    "工人": {
        "type": "Danh từ",
        "meaning": "công nhân",
        "note": (
            "Chỉ người lao động làm công việc "
            "sản xuất hoặc lao động chân tay."
        ),
    },

    "工作": {
        "type": "Động từ / danh từ",
        "meaning": "làm việc; công việc",
        "note": (
            "Có thể dùng làm động từ 'làm việc' "
            "hoặc danh từ 'công việc'."
        ),
    },

    "回家": {
        "type": "Động từ",
        "meaning": "về nhà",
        "note": (
            "Dùng để nói việc trở về nhà."
        ),
    },

    "开会": {
        "type": "Động từ",
        "meaning": "họp; họp hành",
        "note": (
            "Dùng để nói việc tổ chức hoặc "
            "tham gia một cuộc họp."
        ),
    },

    "累": {
        "type": "Tính từ",
        "meaning": "mệt; mệt mỏi",
        "note": (
            "Dùng để miêu tả trạng thái mệt "
            "sau khi làm việc hoặc hoạt động."
        ),
    },

    "忙": {
        "type": "Tính từ",
        "meaning": "bận",
        "note": (
            "Dùng để nói một người có nhiều việc "
            "cần làm."
        ),
    },

    "起": {
        "type": "Động từ",
        "meaning": "dậy; đứng lên; bắt đầu",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "dậy hoặc đứng lên; thường gặp trong 起床."
        ),
    },

    "起床": {
        "type": "Động từ",
        "meaning": "thức dậy; ra khỏi giường",
        "note": (
            "Dùng để nói hoạt động thức dậy "
            "sau khi ngủ."
        ),
    },

    "起来": {
        "type": "Động từ / bổ ngữ xu hướng",
        "meaning": "đứng dậy; thức dậy; lên",
        "note": (
            "Trong bài này học nghĩa cơ bản là "
            "đứng lên hoặc thức dậy. Các cách dùng "
            "ngữ pháp mở rộng sẽ học sau."
        ),
    },

    "上班": {
        "type": "Động từ",
        "meaning": "đi làm; vào làm",
        "note": (
            "Dùng để nói việc bắt đầu hoặc "
            "đến nơi làm việc."
        ),
    },

    "睡": {
        "type": "Động từ",
        "meaning": "ngủ",
        "note": (
            "Động từ cơ bản chỉ trạng thái ngủ."
        ),
    },

    "睡觉": {
        "type": "Động từ",
        "meaning": "ngủ; đi ngủ",
        "note": (
            "Cách nói thông dụng để diễn tả "
            "hoạt động ngủ."
        ),
    },

    "洗": {
        "type": "Động từ",
        "meaning": "rửa; giặt; tắm",
        "note": (
            "Nghĩa cụ thể phụ thuộc vào tân ngữ, "
            "ví dụ 洗手 là rửa tay."
        ),
    },

    "下班": {
        "type": "Động từ",
        "meaning": "tan làm; tan ca",
        "note": (
            "Chỉ thời điểm kết thúc công việc "
            "trong ngày hoặc kết thúc ca làm."
        ),
    },

    "休息": {
        "type": "Động từ",
        "meaning": "nghỉ; nghỉ ngơi",
        "note": (
            "Dùng khi tạm ngừng học hoặc làm việc "
            "để nghỉ ngơi."
        ),
    },

    "在家": {
        "type": "Động từ / cụm chỉ nơi chốn",
        "meaning": "ở nhà",
        "note": (
            "Trong bài này dùng để nói một người "
            "đang ở tại nhà."
        ),
    },

    "做": {
        "type": "Động từ",
        "meaning": "làm",
        "note": (
            "Động từ thông dụng dùng để nói "
            "thực hiện hoặc làm một công việc."
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
    print("09G11 - KIEM DUYET TU VUNG BAI 9")
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
    # 4. KIEM TRA BAI 1 -> 8
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
    # 5. LAY BAI 9
    # =====================================================
    lesson9 = get_lesson_rows(
        rows,
        9,
    )

    if len(lesson9) != 22:

        raise RuntimeError(
            "Bai 9 phai co dung 22 tu. "
            f"Thuc te: {len(lesson9)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson9
    }

    expected_words = set(
        LESSON9_REVIEW.keys()
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
            "Danh sach 22 tu Bai 9 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 9 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson9
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 9 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 10 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 10
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 10 -> 23 "
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
    # 10. CAP NHAT BAI 9
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 9:
            continue

        word = row["ChuHan"].strip()

        review = LESSON9_REVIEW[word]

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
            "So dong cap nhat Bai 9 "
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
    # 13. VERIFY BAI 1 -> 9
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
    # 14. DAM BAO BAI 10 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson9 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 10
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson9:

        raise RuntimeError(
            "Bai 10 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 9
    # =====================================================
    lesson9_verified = get_reviewed_rows(
        verify_rows,
        9,
    )

    lesson9_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 9 SAU REVIEW")
    print("-" * 95)

    for row in lesson9_verified:

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

    if reviewed_total != 210:

        raise RuntimeError(
            "Sau Bai 9 phai co "
            "210 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 291:

        raise RuntimeError(
            "Sau Bai 9 phai con "
            "291 tu chua kiem duyet. "
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