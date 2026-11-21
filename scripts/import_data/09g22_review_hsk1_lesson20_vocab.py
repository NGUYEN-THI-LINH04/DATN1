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
# NOI DUNG HOC TAP BAI 20
#
# 我会说中文 - Tôi biết nói tiếng Trung
#
# Chu de:
# - Kha nang
# - Ket qua hanh dong
# - Mong muon / y dinh
# - Biet / hieu / nghe thay / nhin thay
#
# LUU Y:
# Bai 20 co 2 muc cung ChuHan la 还:
#   还 [hái]  = van; con
#   还 [huán] = tra lai
#
# Vi vay dung khoa:
#   (ChuHan, PhienAm)
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON20_REVIEW = {

    ("不对", "bùduì"): {
        "type": "Tính từ",
        "meaning": "không đúng; sai",
        "note": (
            "Dùng để nói một câu trả lời, "
            "ý kiến hoặc việc gì đó không đúng."
        ),
    },

    ("错", "cuò"): {
        "type": "Tính từ / danh từ",
        "meaning": "sai; lỗi",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "sai hoặc lỗi."
        ),
    },

    ("得到", "dédào"): {
        "type": "Động từ",
        "meaning": "nhận được; đạt được",
        "note": (
            "Dùng để biểu thị đã nhận hoặc "
            "đạt được một kết quả."
        ),
    },

    ("对", "duì"): {
        "type": "Tính từ",
        "meaning": "đúng; chính xác",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "đúng hoặc chính xác."
        ),
    },

    ("过", "guò"): {
        "type": "Động từ",
        "meaning": "qua; đi qua; trải qua",
        "note": (
            "Mục này trong nguồn là động từ guò. "
            "Trong bài học giữ các nghĩa cơ bản "
            "qua, đi qua hoặc trải qua."
        ),
    },

    ("还", "hái"): {
        "type": "Phó từ",
        "meaning": "vẫn; còn",
        "note": (
            "Đây là cách đọc hái, dùng với nghĩa "
            "vẫn hoặc còn. Phân biệt với 还 huán "
            "nghĩa là trả lại."
        ),
    },

    ("还", "huán"): {
        "type": "Động từ",
        "meaning": "trả lại; hoàn lại",
        "note": (
            "Đây là cách đọc huán, dùng với nghĩa "
            "trả lại. Phân biệt với 还 hái "
            "nghĩa là vẫn hoặc còn."
        ),
    },

    ("会", "huì"): {
        "type": "Động từ năng nguyện",
        "meaning": "biết; có thể",
        "note": (
            "Trong bài này dùng để chỉ khả năng "
            "có được nhờ học hoặc rèn luyện, "
            "ví dụ 我会说中文."
        ),
    },

    ("就", "jiù"): {
        "type": "Phó từ",
        "meaning": "thì; liền; ngay",
        "note": (
            "Trong bài này học các nghĩa cơ bản "
            "dùng để nối kết quả hoặc biểu thị "
            "hành động xảy ra ngay sau đó."
        ),
    },

    ("看到", "kàndào"): {
        "type": "Động từ",
        "meaning": "nhìn thấy",
        "note": (
            "看 kết hợp với 到 để biểu thị "
            "kết quả là đã nhìn thấy."
        ),
    },

    ("看见", "kànjiàn"): {
        "type": "Động từ",
        "meaning": "nhìn thấy; trông thấy",
        "note": (
            "Biểu thị kết quả của hành động nhìn: "
            "đã nhìn thấy một người hoặc vật."
        ),
    },

    ("了", "le"): {
        "type": "Trợ từ",
        "meaning": "rồi; đã",
        "note": (
            "Trợ từ le có thể biểu thị hành động "
            "đã hoàn thành hoặc sự thay đổi trạng thái. "
            "Cách dùng chi tiết sẽ được trình bày "
            "trong phần ngữ pháp."
        ),
    },

    ("没有", "méiyǒu"): {
        "type": "Động từ / phó từ",
        "meaning": "không có; chưa",
        "note": (
            "Dùng để phủ định sự tồn tại hoặc "
            "phủ định hành động chưa xảy ra."
        ),
    },

    ("明白", "míngbai"): {
        "type": "Động từ / tính từ",
        "meaning": "hiểu; rõ",
        "note": (
            "Dùng để nói đã hiểu nội dung, "
            "ý nghĩa hoặc tình huống."
        ),
    },

    ("能", "néng"): {
        "type": "Động từ năng nguyện",
        "meaning": "có thể; có khả năng",
        "note": (
            "Dùng để biểu thị khả năng "
            "hoặc điều kiện cho phép làm một việc."
        ),
    },

    ("听到", "tīngdào"): {
        "type": "Động từ",
        "meaning": "nghe thấy",
        "note": (
            "听 kết hợp với 到 để biểu thị "
            "kết quả là đã nghe thấy."
        ),
    },

    ("听见", "tīngjiàn"): {
        "type": "Động từ",
        "meaning": "nghe thấy",
        "note": (
            "Biểu thị kết quả của hành động nghe: "
            "đã nghe được âm thanh."
        ),
    },

    ("想", "xiǎng"): {
        "type": "Động từ",
        "meaning": "muốn; nghĩ; nghĩ đến",
        "note": (
            "Trong bài này học các nghĩa thông dụng "
            "là muốn làm gì hoặc nghĩ về điều gì."
        ),
    },

    ("要", "yào"): {
        "type": "Động từ năng nguyện",
        "meaning": "muốn; cần; sẽ; sắp",
        "note": (
            "Dùng để diễn tả mong muốn, nhu cầu "
            "hoặc việc sắp xảy ra tùy ngữ cảnh."
        ),
    },

    ("用", "yòng"): {
        "type": "Động từ",
        "meaning": "dùng; sử dụng",
        "note": (
            "Dùng để nói việc sử dụng "
            "một đồ vật, phương tiện hoặc cách thức."
        ),
    },

    ("有", "yǒu"): {
        "type": "Động từ",
        "meaning": "có",
        "note": (
            "Động từ cơ bản dùng để biểu thị "
            "sự sở hữu hoặc sự tồn tại."
        ),
    },

    ("有用", "yǒuyòng"): {
        "type": "Tính từ",
        "meaning": "hữu ích; có ích",
        "note": (
            "Dùng để nói một người, vật hoặc "
            "thông tin có ích."
        ),
    },

    ("知道", "zhīdào"): {
        "type": "Động từ",
        "meaning": "biết",
        "note": (
            "Dùng để nói người học có thông tin "
            "hoặc nhận thức về một sự việc."
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


def make_key(row):
    return (
        row["ChuHan"].strip(),
        row["PhienAm"].strip(),
    )


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 95)
    print("09G22 - KIEM DUYET TU VUNG BAI 20")
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
    # 4. KIEM TRA BAI 1 -> 19
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
    # 5. LAY BAI 20
    # =====================================================
    lesson20 = get_lesson_rows(
        rows,
        20,
    )

    if len(lesson20) != 23:
        raise RuntimeError(
            "Bai 20 phai co dung 23 dong. "
            f"Thuc te: {len(lesson20)}"
        )

    # =====================================================
    # 6. DOI CHIEU BANG CHU HAN + PINYIN
    # =====================================================
    actual_keys = {
        make_key(row)
        for row in lesson20
    }

    expected_keys = set(
        LESSON20_REVIEW.keys()
    )

    if actual_keys != expected_keys:

        missing_keys = (
            expected_keys
            - actual_keys
        )

        extra_keys = (
            actual_keys
            - expected_keys
        )

        print()
        print(
            "Muc thieu so voi script:",
            sorted(missing_keys),
        )

        print(
            "Muc du so voi script:",
            sorted(extra_keys),
        )

        raise RuntimeError(
            "Danh sach Bai 20 "
            "khong khop ChuHan + PhienAm."
        )

    # =====================================================
    # 7. KIEM TRA RIENG HAI MUC 还
    # =====================================================
    huan_hai_rows = [
        row
        for row in lesson20
        if row["ChuHan"].strip() == "还"
    ]

    if len(huan_hai_rows) != 2:
        raise RuntimeError(
            "Bai 20 phai co dung 2 muc 还."
        )

    hai_huan_pinyin = {
        row["PhienAm"].strip()
        for row in huan_hai_rows
    }

    if hai_huan_pinyin != {"hái", "huán"}:
        raise RuntimeError(
            "Hai muc 还 phai la hái va huán. "
            f"Thuc te: {sorted(hai_huan_pinyin)}"
        )

    print()
    print("Kiem tra tu da am 还:")
    print("  还 [hái]  -> van; con")
    print("  还 [huán] -> tra lai")
    print("  OK")

    # =====================================================
    # 8. DAM BAO BAI 20 CHUA REVIEW
    # =====================================================
    already_reviewed = [
        row
        for row in lesson20
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:
        raise RuntimeError(
            "Bai 20 da co tu DaKiemDuyet=1. "
            "Dung lai de tranh ghi de."
        )

    # =====================================================
    # 9. DAM BAO BAI 21 -> 23 CHUA REVIEW
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 21
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:
        raise RuntimeError(
            "Phat hien Bai 21 -> 23 "
            "da co du lieu review."
        )

    # =====================================================
    # 10. BACKUP
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
    # 11. CAP NHAT BAI 20
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 20:
            continue

        key = make_key(row)

        review = LESSON20_REVIEW[key]

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
            "So dong cap nhat Bai 20 "
            "khong bang 23."
        )

    # =====================================================
    # 12. GHI FILE
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
    # 13. DOC LAI VERIFY
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
    # 14. VERIFY BAI 1 -> 20
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
    # 15. VERIFY LAI HAI MUC 还 SAU KHI GHI
    # =====================================================
    lesson20_verified_all = get_lesson_rows(
        verify_rows,
        20,
    )

    hai_row = [
        row
        for row in lesson20_verified_all
        if (
            row["ChuHan"].strip() == "还"
            and row["PhienAm"].strip() == "hái"
        )
    ]

    huan_row = [
        row
        for row in lesson20_verified_all
        if (
            row["ChuHan"].strip() == "还"
            and row["PhienAm"].strip() == "huán"
        )
    ]

    if len(hai_row) != 1:
        raise RuntimeError(
            "Khong verify duoc 还 [hái]."
        )

    if len(huan_row) != 1:
        raise RuntimeError(
            "Khong verify duoc 还 [huán]."
        )

    if hai_row[0]["NghiaHocTap"] != "vẫn; còn":
        raise RuntimeError(
            "Nghia cua 还 [hái] bi sai."
        )

    if huan_row[0]["NghiaHocTap"] != "trả lại; hoàn lại":
        raise RuntimeError(
            "Nghia cua 还 [huán] bi sai."
        )

    # =====================================================
    # 16. DAM BAO BAI 21 -> 23 KHONG DOI
    # =====================================================
    reviewed_after_lesson20 = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 21
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after_lesson20:
        raise RuntimeError(
            "Bai 21 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 17. IN NOI DUNG BAI 20
    # =====================================================
    lesson20_verified = get_reviewed_rows(
        verify_rows,
        20,
    )

    lesson20_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 20 SAU REVIEW")
    print("-" * 95)

    for row in lesson20_verified:

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
    # 18. TONG KET
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

    if reviewed_total != 447:
        raise RuntimeError(
            "Sau Bai 20 phai co "
            "447 tu da kiem duyet. "
            f"Thuc te: {reviewed_total}"
        )

    if unreviewed_total != 54:
        raise RuntimeError(
            "Sau Bai 20 phai con "
            "54 tu chua kiem duyet. "
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