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
# NOI DUNG HOC TAP BAI 19
#
# 你在做什么？ - Bạn đang làm gì?
#
# Chu de:
# - Hanh dong dang dien ra
# - Huong di vao / di ra
# - Tro ve
# - Dang / chuan bi / lai
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON19_REVIEW = {

    "帮": {
        "type": "Động từ",
        "meaning": "giúp; giúp đỡ",
        "note": (
            "Trong bài này dùng với nghĩa "
            "giúp hoặc hỗ trợ người khác."
        ),
    },

    "帮忙": {
        "type": "Động từ",
        "meaning": "giúp đỡ; giúp một tay",
        "note": (
            "Cách nói thông dụng khi nhờ "
            "hoặc giúp người khác làm một việc."
        ),
    },

    "出": {
        "type": "Động từ",
        "meaning": "ra; đi ra",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "di chuyển từ bên trong ra bên ngoài."
        ),
    },

    "出来": {
        "type": "Động từ / bổ ngữ xu hướng",
        "meaning": "đi ra; ra đây",
        "note": (
            "Biểu thị hướng di chuyển từ trong ra "
            "và hướng về phía người nói."
        ),
    },

    "出去": {
        "type": "Động từ / bổ ngữ xu hướng",
        "meaning": "đi ra ngoài; ra ngoài",
        "note": (
            "Biểu thị hướng di chuyển từ trong ra "
            "và rời xa người nói."
        ),
    },

    "打": {
        "type": "Động từ",
        "meaning": "đánh; gọi; chơi",
        "note": (
            "Đây là động từ có nhiều cách dùng. "
            "Trong bài cơ bản chỉ giữ các nghĩa phổ biến "
            "như đánh, gọi điện hoặc chơi một môn/trò."
        ),
    },

    "放": {
        "type": "Động từ",
        "meaning": "đặt; để; thả",
        "note": (
            "Trong bài này dùng với nghĩa cơ bản "
            "đặt, để hoặc thả một vật."
        ),
    },

    "干什么": {
        "type": "Cụm nghi vấn",
        "meaning": "làm gì",
        "note": (
            "Dùng để hỏi một người đang hoặc định "
            "làm gì, ví dụ 你在干什么？"
        ),
    },

    "关": {
        "type": "Động từ",
        "meaning": "đóng; tắt",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "đóng cửa hoặc tắt thiết bị."
        ),
    },

    "回": {
        "type": "Động từ",
        "meaning": "về; trở về; quay lại",
        "note": (
            "Trong bài này dùng với nghĩa "
            "trở lại một nơi."
        ),
    },

    "回来": {
        "type": "Động từ / bổ ngữ xu hướng",
        "meaning": "trở về; quay lại đây",
        "note": (
            "Biểu thị sự trở về hướng "
            "về phía người nói."
        ),
    },

    "回去": {
        "type": "Động từ / bổ ngữ xu hướng",
        "meaning": "trở về; quay lại đó",
        "note": (
            "Biểu thị sự trở về theo hướng "
            "rời xa người nói."
        ),
    },

    "进": {
        "type": "Động từ",
        "meaning": "vào; đi vào",
        "note": (
            "Trong bài này dùng với nghĩa "
            "di chuyển từ ngoài vào trong."
        ),
    },

    "进来": {
        "type": "Động từ / bổ ngữ xu hướng",
        "meaning": "đi vào; vào đây",
        "note": (
            "Biểu thị hướng đi vào "
            "và hướng về phía người nói."
        ),
    },

    "进去": {
        "type": "Động từ / bổ ngữ xu hướng",
        "meaning": "đi vào; vào trong",
        "note": (
            "Biểu thị hướng đi vào "
            "và rời xa người nói."
        ),
    },

    "开": {
        "type": "Động từ",
        "meaning": "mở; bật",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "mở cửa hoặc bật thiết bị."
        ),
    },

    "拿": {
        "type": "Động từ",
        "meaning": "cầm; lấy",
        "note": (
            "Dùng để nói việc cầm hoặc "
            "lấy một đồ vật."
        ),
    },

    "一下儿": {
        "type": "Bổ ngữ số lượng động tác",
        "meaning": "một chút; một lát; một lần",
        "note": (
            "Dạng có 儿化 của 一下, thường đặt sau "
            "động từ để làm nhẹ sắc thái hoặc chỉ "
            "hành động diễn ra trong thời gian ngắn."
        ),
    },

    "再": {
        "type": "Phó từ",
        "meaning": "lại; một lần nữa; rồi",
        "note": (
            "Dùng khi một hành động sẽ được "
            "thực hiện lại hoặc thực hiện sau đó."
        ),
    },

    "在": {
        "type": "Động từ / giới từ / phó từ",
        "meaning": "ở; tại; đang",
        "note": (
            "Trong bài này đặc biệt học cách dùng "
            "在 trước động từ để biểu thị "
            "hành động đang diễn ra."
        ),
    },

    "着": {
        "type": "Trợ từ",
        "meaning": "đang; ở trạng thái tiếp diễn",
        "note": (
            "Trợ từ zhe dùng sau động từ để biểu thị "
            "hành động hoặc trạng thái đang tiếp diễn."
        ),
    },

    "正在": {
        "type": "Phó từ",
        "meaning": "đang",
        "note": (
            "Đặt trước động từ để nhấn mạnh "
            "hành động đang diễn ra ngay lúc nói."
        ),
    },

    "准备": {
        "type": "Động từ",
        "meaning": "chuẩn bị; dự định",
        "note": (
            "Dùng để nói đang chuẩn bị "
            "hoặc dự định làm một việc."
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
    print("09G21 - KIEM DUYET TU VUNG BAI 19")
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
    # 4. KIEM TRA BAI 1 -> 18
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
    # 5. LAY BAI 19
    # =====================================================
    lesson19 = get_lesson_rows(
        rows,
        19,
    )

    if len(lesson19) != 23:
        raise RuntimeError(
            "Bai 19 phai co dung 23 tu. "
            f"Thuc te: {len(lesson19)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson19
    }

    expected_words = set(
        LESSON19_REVIEW.keys()
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
            "Danh sach 23 tu Bai 19 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 19 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson19
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 19 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 20 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 20
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 20 -> 23 "
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
    # 10. CAP NHAT BAI 19
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 19:
            continue

        word = row["ChuHan"].strip()
        review = LESSON19_REVIEW[word]

        row["TuLoaiHocTap"] = review["type"]
        row["NghiaHocTap"] = review["meaning"]
        row["GhiChuKiemDuyet"] = review["note"]
        row["DaKiemDuyet"] = "1"

        updated += 1

    if updated != 23:
        raise RuntimeError(
            "So dong cap nhat Bai 19 "
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
    # 13. VERIFY BAI 1 -> 19
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
    # 14. DAM BAO BAI 20 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson19 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 20
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson19:
        raise RuntimeError(
            "Bai 20 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 19
    # =====================================================
    lesson19_verified = get_reviewed_rows(
        verify_rows,
        19,
    )

    lesson19_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 19 SAU REVIEW")
    print("-" * 95)

    for row in lesson19_verified:

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

    if reviewed_total != 424:
        raise RuntimeError(
            "Sau Bai 19 phai co "
            "424 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 77:
        raise RuntimeError(
            "Sau Bai 19 phai con "
            "77 tu chua kiem duyet. "
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