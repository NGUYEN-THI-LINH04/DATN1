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
# NOI DUNG HOC TAP BAI 17
#
# 我喜欢唱歌和看电影
# Tôi thích hát và xem phim
#
# Chu de:
# - So thich
# - Giai tri
# - Phim anh / am nhac
# - Internet
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON17_REVIEW = {

    "爱": {
        "type": "Động từ",
        "meaning": "yêu; thích",
        "note": (
            "Dùng để diễn tả tình cảm yêu thích "
            "đối với người, vật hoặc hoạt động."
        ),
    },

    "爱好": {
        "type": "Danh từ / động từ",
        "meaning": "sở thích; yêu thích",
        "note": (
            "Trong bài này chủ yếu dùng để nói "
            "về sở thích cá nhân."
        ),
    },

    "唱": {
        "type": "Động từ",
        "meaning": "hát",
        "note": (
            "Động từ cơ bản chỉ hoạt động hát."
        ),
    },

    "唱歌": {
        "type": "Động từ",
        "meaning": "hát; ca hát",
        "note": (
            "Dùng để nói hoạt động hát, "
            "ví dụ 我喜欢唱歌."
        ),
    },

    "打球": {
        "type": "Động từ",
        "meaning": "chơi bóng",
        "note": (
            "Dùng để nói hoạt động chơi "
            "các môn thể thao với bóng."
        ),
    },

    "电": {
        "type": "Danh từ",
        "meaning": "điện",
        "note": (
            "Trong bài này học nghĩa cơ bản "
            "liên quan đến điện."
        ),
    },

    "电脑": {
        "type": "Danh từ",
        "meaning": "máy tính",
        "note": (
            "Thiết bị điện tử dùng để học tập, "
            "làm việc và giải trí."
        ),
    },

    "电视": {
        "type": "Danh từ",
        "meaning": "truyền hình; TV",
        "note": (
            "Có thể chỉ truyền hình hoặc "
            "nội dung/chương trình truyền hình."
        ),
    },

    "电视机": {
        "type": "Danh từ",
        "meaning": "tivi; máy thu hình",
        "note": (
            "Chỉ thiết bị dùng để xem "
            "các chương trình truyền hình."
        ),
    },

    "电影": {
        "type": "Danh từ",
        "meaning": "phim; điện ảnh",
        "note": (
            "Trong bài này chủ yếu dùng "
            "với nghĩa phim."
        ),
    },

    "电影院": {
        "type": "Danh từ",
        "meaning": "rạp chiếu phim; rạp phim",
        "note": (
            "Nơi chiếu phim cho khán giả xem."
        ),
    },

    "歌": {
        "type": "Danh từ",
        "meaning": "bài hát",
        "note": (
            "Danh từ chỉ một bài hát."
        ),
    },

    "好看": {
        "type": "Tính từ",
        "meaning": "đẹp; hay",
        "note": (
            "Trong chủ đề giải trí có thể dùng "
            "để nói phim hoặc chương trình hay; "
            "cũng có thể miêu tả người/vật đẹp."
        ),
    },

    "好听": {
        "type": "Tính từ",
        "meaning": "nghe hay; hay",
        "note": (
            "Dùng để miêu tả âm thanh, "
            "giọng nói hoặc bài hát nghe hay."
        ),
    },

    "好玩儿": {
        "type": "Tính từ",
        "meaning": "vui; thú vị",
        "note": (
            "Dạng có 儿化 của 好玩, "
            "dùng để nói một hoạt động hoặc "
            "sự việc vui, thú vị."
        ),
    },

    "觉得": {
        "type": "Động từ",
        "meaning": "cảm thấy; nghĩ rằng",
        "note": (
            "Dùng để diễn tả cảm nhận "
            "hoặc ý kiến của người nói."
        ),
    },

    "开玩笑": {
        "type": "Động từ",
        "meaning": "nói đùa; đùa giỡn",
        "note": (
            "Dùng khi nói hoặc làm điều gì đó "
            "với mục đích vui đùa."
        ),
    },

    "看": {
        "type": "Động từ",
        "meaning": "xem; nhìn",
        "note": (
            "Trong bài này tập trung vào nghĩa xem, "
            "ví dụ 看电影、看电视."
        ),
    },

    "球": {
        "type": "Danh từ",
        "meaning": "quả bóng; bóng",
        "note": (
            "Trong bài này chủ yếu dùng "
            "trong hoạt động thể thao."
        ),
    },

    "上网": {
        "type": "Động từ",
        "meaning": "lên mạng; truy cập Internet",
        "note": (
            "Dùng để nói việc kết nối và "
            "sử dụng Internet."
        ),
    },

    "玩儿": {
        "type": "Động từ",
        "meaning": "chơi; vui chơi; đi chơi",
        "note": (
            "Dạng có 儿化, dùng để nói "
            "hoạt động vui chơi hoặc giải trí."
        ),
    },

    "网上": {
        "type": "Cụm chỉ nơi chốn",
        "meaning": "trên mạng; trực tuyến",
        "note": (
            "Dùng để nói một hoạt động hoặc "
            "thông tin ở trên Internet."
        ),
    },

    "网友": {
        "type": "Danh từ",
        "meaning": "bạn trên mạng; người dùng Internet",
        "note": (
            "Có thể chỉ người quen biết qua Internet "
            "hoặc người dùng Internet."
        ),
    },

    "喜欢": {
        "type": "Động từ",
        "meaning": "thích; ưa thích",
        "note": (
            "Từ trọng tâm của bài dùng để nói "
            "về sở thích, ví dụ 我喜欢看电影."
        ),
    },

    "笑": {
        "type": "Động từ",
        "meaning": "cười; mỉm cười",
        "note": (
            "Trong bài này dùng với nghĩa "
            "cười hoặc mỉm cười."
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
    print("09G19 - KIEM DUYET TU VUNG BAI 17")
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
    # 4. KIEM TRA BAI 1 -> 16
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
    # 5. LAY BAI 17
    # =====================================================
    lesson17 = get_lesson_rows(
        rows,
        17,
    )

    if len(lesson17) != 25:
        raise RuntimeError(
            "Bai 17 phai co dung 25 tu. "
            f"Thuc te: {len(lesson17)}"
        )

    # =====================================================
    # 6. DOI CHIEU DANH SACH
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson17
    }

    expected_words = set(
        LESSON17_REVIEW.keys()
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
            "Danh sach 25 tu Bai 17 "
            "khong khop file review."
        )

    # =====================================================
    # 7. DAM BAO BAI 17 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson17
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 17 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 8. DAM BAO BAI 18 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 18
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 18 -> 23 "
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
    # 10. CAP NHAT BAI 17
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 17:
            continue

        word = row["ChuHan"].strip()
        review = LESSON17_REVIEW[word]

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
            "So dong cap nhat Bai 17 "
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
    # 13. VERIFY BAI 1 -> 17
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
    # 14. DAM BAO BAI 18 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson17 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 18
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson17:
        raise RuntimeError(
            "Bai 18 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 17
    # =====================================================
    lesson17_verified = get_reviewed_rows(
        verify_rows,
        17,
    )

    lesson17_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 17 SAU REVIEW")
    print("-" * 95)

    for row in lesson17_verified:

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

    if reviewed_total != 379:
        raise RuntimeError(
            "Sau Bai 17 phai co "
            "379 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 122:
        raise RuntimeError(
            "Sau Bai 17 phai con "
            "122 tu chua kiem duyet. "
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