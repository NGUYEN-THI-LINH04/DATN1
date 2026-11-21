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
# NOI DUNG HOC TAP BAI 23
#
# 明天见！ - Hẹn gặp ngày mai!
#
# Chu de:
# - Tu chuc nang
# - Giao tiep thuong ngay
# - Phu dinh
# - Lien tu / gioi tu
# - Tro tu cau
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON23_REVIEW = {

    "吧": {
        "type": "Trợ từ ngữ khí",
        "meaning": "nhé; đi; chứ",
        "note": (
            "Dùng cuối câu để đưa ra gợi ý, "
            "đề nghị hoặc làm câu nói nhẹ hơn, "
            "ví dụ 我们走吧."
        ),
    },

    "别": {
        "type": "Phó từ",
        "meaning": "đừng",
        "note": (
            "Trong bài này tập trung vào cách dùng "
            "trước động từ để khuyên hoặc yêu cầu "
            "không làm một việc, ví dụ 别走."
        ),
    },

    "别人": {
        "type": "Đại từ",
        "meaning": "người khác; những người khác",
        "note": (
            "Dùng để chỉ người không phải "
            "người đang được nói đến."
        ),
    },

    "不用": {
        "type": "Phó từ",
        "meaning": "không cần",
        "note": (
            "Dùng để nói một việc không cần "
            "phải thực hiện."
        ),
    },

    "不": {
        "type": "Phó từ",
        "meaning": "không",
        "note": (
            "Từ phủ định cơ bản, thường đặt trước "
            "động từ hoặc tính từ."
        ),
    },

    "地": {
        "type": "Trợ từ kết cấu",
        "meaning": "trợ từ nối trạng ngữ với động từ",
        "note": (
            "Đây là 地 đọc de, đặt sau trạng ngữ "
            "và trước động từ hoặc tính từ trung tâm. "
            "Cần phân biệt với 地 dì nghĩa là đất "
            "hoặc mặt đất."
        ),
    },

    "的": {
        "type": "Trợ từ kết cấu",
        "meaning": "của; trợ từ nối định ngữ",
        "note": (
            "Dùng sau định ngữ để bổ nghĩa cho danh từ "
            "hoặc biểu thị quan hệ sở hữu, "
            "ví dụ 我的书."
        ),
    },

    "都": {
        "type": "Phó từ",
        "meaning": "đều; tất cả",
        "note": (
            "Dùng để nói nhiều người hoặc vật "
            "đều có cùng đặc điểm hoặc hành động."
        ),
    },

    "跟": {
        "type": "Giới từ / liên từ / động từ",
        "meaning": "với; cùng; theo",
        "note": (
            "Trong giao tiếp cơ bản thường dùng "
            "với nghĩa cùng với ai hoặc đi theo ai."
        ),
    },

    "还是": {
        "type": "Phó từ / liên từ",
        "meaning": "hay là; vẫn; tốt hơn nên",
        "note": (
            "Có thể dùng để đưa ra lựa chọn "
            "hoặc lời khuyên tùy ngữ cảnh. "
            "Trong câu hỏi lựa chọn thường mang nghĩa "
            "'hay là'."
        ),
    },

    "还有": {
        "type": "Cụm từ",
        "meaning": "còn; còn có; ngoài ra còn",
        "note": (
            "Dùng để bổ sung thêm người, vật "
            "hoặc thông tin."
        ),
    },

    "和": {
        "type": "Liên từ / giới từ",
        "meaning": "và; với",
        "note": (
            "Trong bài cơ bản chủ yếu dùng để "
            "nối hai danh từ hoặc cụm danh từ."
        ),
    },

    "没": {
        "type": "Phó từ / động từ",
        "meaning": "không; chưa",
        "note": (
            "Dùng để phủ định sự tồn tại "
            "hoặc hành động chưa xảy ra."
        ),
    },

    "没什么": {
        "type": "Cụm từ",
        "meaning": "không có gì; không sao",
        "note": (
            "Dùng trong giao tiếp để nói rằng "
            "không có vấn đề gì hoặc sự việc "
            "không đáng lo."
        ),
    },

    "是不是": {
        "type": "Cụm nghi vấn",
        "meaning": "có phải... không",
        "note": (
            "Mẫu hỏi chính phản dùng để xác nhận "
            "một thông tin, ví dụ 你是不是学生？"
        ),
    },

    "怎么": {
        "type": "Đại từ nghi vấn",
        "meaning": "thế nào; làm sao; tại sao",
        "note": (
            "Dùng để hỏi cách thức, tình trạng "
            "hoặc nguyên nhân tùy ngữ cảnh."
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
    print("09G25 - KIEM DUYET TU VUNG BAI 23")
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
    # 4. KIEM TRA BAI 1 -> 22
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
        22: 18,
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
    # 5. LAY BAI 23
    # =====================================================
    lesson23 = get_lesson_rows(
        rows,
        23,
    )

    if len(lesson23) != 16:
        raise RuntimeError(
            "Bai 23 phai co dung 16 tu. "
            f"Thuc te: {len(lesson23)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson23
    }

    expected_words = set(
        LESSON23_REVIEW.keys()
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
            "Danh sach 16 tu Bai 23 "
            "khong khop file review."
        )

    # =====================================================
    # 7. KIEM TRA RIENG 地
    # =====================================================
    de_rows = [
        row
        for row in lesson23
        if row["ChuHan"].strip() == "地"
    ]

    if len(de_rows) != 1:
        raise RuntimeError(
            "Bai 23 phai co dung 1 muc 地."
        )

    if de_rows[0]["PhienAm"].strip() != "de":
        raise RuntimeError(
            "Muc 地 trong Bai 23 phai doc la de. "
            f"Thuc te: {de_rows[0]['PhienAm']}"
        )

    print()
    print("Kiem tra tu da am 地:")
    print("  地 [de] -> tro tu ket cau")
    print("  OK")

    # =====================================================
    # 8. DAM BAO BAI 23 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson23
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 23 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
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
    # 10. CAP NHAT BAI 23
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 23:
            continue

        word = row["ChuHan"].strip()
        review = LESSON23_REVIEW[word]

        row["TuLoaiHocTap"] = review["type"]
        row["NghiaHocTap"] = review["meaning"]
        row["GhiChuKiemDuyet"] = review["note"]
        row["DaKiemDuyet"] = "1"

        updated += 1

    if updated != 16:
        raise RuntimeError(
            "So dong cap nhat Bai 23 "
            "khong bang 16."
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

    if len(verify_rows) != 501:
        raise RuntimeError(
            "Sau khi ghi file khong con dung 501 dong."
        )

    # =====================================================
    # 13. VERIFY TOAN BO 23 BAI
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
        23: 16,
    }

    print()
    print("Verify toan bo 23 bai:")

    for lesson_no, expected_count in (
        expected_after.items()
    ):

        lesson_rows = get_lesson_rows(
            verify_rows,
            lesson_no,
        )

        reviewed_rows = get_reviewed_rows(
            verify_rows,
            lesson_no,
        )

        if len(lesson_rows) != expected_count:
            raise RuntimeError(
                f"Bai {lesson_no} khong co dung "
                f"{expected_count} dong."
            )

        if len(reviewed_rows) != expected_count:
            raise RuntimeError(
                f"Bai {lesson_no} khong co dung "
                f"{expected_count} dong da review."
            )

        print(
            f"  Bai {lesson_no}: "
            f"{expected_count}/{expected_count} OK"
        )

    # =====================================================
    # 14. KIEM TRA KHONG CON DONG CHUA REVIEW
    # =====================================================
    unreviewed_rows = [
        row
        for row in verify_rows
        if row["DaKiemDuyet"] != "1"
    ]

    if unreviewed_rows:
        raise RuntimeError(
            "Van con dong chua kiem duyet: "
            f"{len(unreviewed_rows)}"
        )

    # =====================================================
    # 15. KIEM TRA KHONG THIEU NOI DUNG HOC TAP
    # =====================================================
    empty_learning_type = [
        row
        for row in verify_rows
        if not row["TuLoaiHocTap"].strip()
    ]

    empty_learning_meaning = [
        row
        for row in verify_rows
        if not row["NghiaHocTap"].strip()
    ]

    empty_review_note = [
        row
        for row in verify_rows
        if not row["GhiChuKiemDuyet"].strip()
    ]

    if empty_learning_type:
        raise RuntimeError(
            "Con dong thieu TuLoaiHocTap: "
            f"{len(empty_learning_type)}"
        )

    if empty_learning_meaning:
        raise RuntimeError(
            "Con dong thieu NghiaHocTap: "
            f"{len(empty_learning_meaning)}"
        )

    if empty_review_note:
        raise RuntimeError(
            "Con dong thieu GhiChuKiemDuyet: "
            f"{len(empty_review_note)}"
        )

    # =====================================================
    # 16. IN NOI DUNG BAI 23
    # =====================================================
    lesson23_verified = get_reviewed_rows(
        verify_rows,
        23,
    )

    lesson23_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 23 SAU REVIEW")
    print("-" * 95)

    for row in lesson23_verified:

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
    # 17. TONG KET CUOI CUNG
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

    if reviewed_total != 501:
        raise RuntimeError(
            "Phai co dung 501 dong da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 0:
        raise RuntimeError(
            "Sau Bai 23 phai con 0 dong "
            "chua kiem duyet. "
            f"Thuc te: {unreviewed_total}"
        )

    print()
    print("=" * 95)
    print("KET QUA CUOI CUNG")
    print("=" * 95)

    print(
        "Tong tu trong file:",
        len(verify_rows),
    )

    print(
        "Tong bai:",
        len(expected_after),
    )

    print(
        "Tong da kiem duyet:",
        reviewed_total,
    )

    print(
        "Con chua kiem duyet:",
        unreviewed_total,
    )

    print(
        "Dong thieu TuLoaiHocTap:",
        len(empty_learning_type),
    )

    print(
        "Dong thieu NghiaHocTap:",
        len(empty_learning_meaning),
    )

    print(
        "Dong thieu GhiChuKiemDuyet:",
        len(empty_review_note),
    )

    print()
    print(
        "TOAN BO 501 DONG DA DUOC KIEM DUYET."
    )

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