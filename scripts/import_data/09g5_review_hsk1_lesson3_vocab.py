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
# NOI DUNG HOC TAP BAI 3
#
# 这是我的家 - Đây là gia đình của tôi
#
# CHI CAP NHAT FILE REVIEW.
# KHONG SUA DATABASE.
# =========================================================
LESSON3_REVIEW = {

    "爸爸": {
        "type": "Danh từ",
        "meaning": "bố; ba; cha",
        "note": "Cách gọi thân mật đối với bố.",
    },

    "弟弟": {
        "type": "Danh từ",
        "meaning": "em trai",
        "note": "Chỉ em trai nhỏ tuổi hơn mình.",
    },

    "儿子": {
        "type": "Danh từ",
        "meaning": "con trai",
        "note": "Chỉ con trai trong gia đình.",
    },

    "哥哥": {
        "type": "Danh từ",
        "meaning": "anh trai",
        "note": "Chỉ anh trai lớn tuổi hơn mình.",
    },

    "孩子": {
        "type": "Danh từ",
        "meaning": "đứa trẻ; con cái",
        "note": (
            "Có thể chỉ trẻ em nói chung hoặc "
            "con của một người tùy ngữ cảnh."
        ),
    },

    "家": {
        "type": "Danh từ",
        "meaning": "nhà; gia đình",
        "note": (
            "Trong bài này tập trung vào nghĩa "
            "nhà và gia đình."
        ),
    },

    "家里": {
        "type": "Danh từ chỉ nơi chốn",
        "meaning": "trong nhà; ở nhà",
        "note": (
            "Chỉ bên trong nhà hoặc ở tại nhà."
        ),
    },

    "家人": {
        "type": "Danh từ",
        "meaning": "người nhà; thành viên gia đình",
        "note": (
            "Chỉ những người thuộc cùng một gia đình."
        ),
    },

    "姐姐": {
        "type": "Danh từ",
        "meaning": "chị gái",
        "note": "Chỉ chị gái lớn tuổi hơn mình.",
    },

    "老人": {
        "type": "Danh từ",
        "meaning": "người cao tuổi; người già",
        "note": (
            "Cách gọi chung người lớn tuổi."
        ),
    },

    "妈妈": {
        "type": "Danh từ",
        "meaning": "mẹ; má",
        "note": "Cách gọi thân mật đối với mẹ.",
    },

    "妹妹": {
        "type": "Danh từ",
        "meaning": "em gái",
        "note": "Chỉ em gái nhỏ tuổi hơn mình.",
    },

    "们（朋友们）": {
        "type": "Hậu tố",
        "meaning": "các; những",
        "note": (
            "们 đặt sau đại từ hoặc danh từ chỉ người "
            "để biểu thị số nhiều, ví dụ 朋友们."
        ),
    },

    "奶奶": {
        "type": "Danh từ",
        "meaning": "bà nội",
        "note": (
            "Cách gọi bà bên nội trong gia đình."
        ),
    },

    "男孩儿": {
        "type": "Danh từ",
        "meaning": "bé trai; cậu bé",
        "note": (
            "Chỉ một bé trai hoặc cậu bé."
        ),
    },

    "男朋友": {
        "type": "Danh từ",
        "meaning": "bạn trai",
        "note": (
            "Chỉ người yêu là nam."
        ),
    },

    "女儿": {
        "type": "Danh từ",
        "meaning": "con gái",
        "note": (
            "Chỉ con gái trong gia đình."
        ),
    },

    "女孩儿": {
        "type": "Danh từ",
        "meaning": "bé gái; cô bé",
        "note": (
            "Chỉ một bé gái hoặc cô bé."
        ),
    },

    "女朋友": {
        "type": "Danh từ",
        "meaning": "bạn gái",
        "note": (
            "Chỉ người yêu là nữ."
        ),
    },

    "朋友": {
        "type": "Danh từ",
        "meaning": "bạn; bạn bè",
        "note": (
            "Chỉ người có quan hệ bạn bè."
        ),
    },

    "小孩儿": {
        "type": "Danh từ",
        "meaning": "trẻ con; đứa trẻ",
        "note": (
            "Cách nói thông dụng chỉ trẻ nhỏ."
        ),
    },

    "小朋友": {
        "type": "Danh từ",
        "meaning": "trẻ em; em nhỏ",
        "note": (
            "Cách gọi thân thiện đối với trẻ em."
        ),
    },

    "爷爷": {
        "type": "Danh từ",
        "meaning": "ông nội",
        "note": (
            "Cách gọi ông bên nội trong gia đình."
        ),
    },
}


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 95)
    print("09G5 - KIEM DUYET TU VUNG BAI 3")
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
    # 3. KIEM TRA CAC COT CAN THIET
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
    # 4. DAM BAO BAI 1 DA DUYET 13
    # =====================================================
    lesson1 = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == 1
    ]

    lesson1_reviewed = [
        row
        for row in lesson1
        if row["DaKiemDuyet"] == "1"
    ]

    if len(lesson1) != 13:
        raise RuntimeError(
            "Bai 1 khong co dung 13 tu."
        )

    if len(lesson1_reviewed) != 13:
        raise RuntimeError(
            "Bai 1 chua kiem duyet du 13 tu."
        )

    # =====================================================
    # 5. DAM BAO BAI 2 DA DUYET 29
    # =====================================================
    lesson2 = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == 2
    ]

    lesson2_reviewed = [
        row
        for row in lesson2
        if row["DaKiemDuyet"] == "1"
    ]

    if len(lesson2) != 29:
        raise RuntimeError(
            "Bai 2 khong co dung 29 tu."
        )

    if len(lesson2_reviewed) != 29:
        raise RuntimeError(
            "Bai 2 chua kiem duyet du 29 tu."
        )

    # =====================================================
    # 6. LAY 23 TU BAI 3
    # =====================================================
    lesson3 = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) == 3
    ]

    if len(lesson3) != 23:

        raise RuntimeError(
            "Bai 3 phai co dung 23 tu. "
            f"Thuc te: {len(lesson3)}"
        )

    # =====================================================
    # 7. DOI CHIEU DANH SACH TU
    # =====================================================
    actual_words = {
        row["ChuHan"].strip()
        for row in lesson3
    }

    expected_words = set(
        LESSON3_REVIEW.keys()
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
            "Danh sach 23 tu Bai 3 "
            "khong khop."
        )

    # =====================================================
    # 8. DAM BAO BAI 3 CHUA DUYET
    # =====================================================
    already_reviewed = [
        row
        for row in lesson3
        if row["DaKiemDuyet"] == "1"
    ]

    if already_reviewed:

        raise RuntimeError(
            "Bai 3 da co tu "
            "DaKiemDuyet=1. "
            "Khong ghi de."
        )

    # =====================================================
    # 9. BAI 4 -> 23 PHAI CHUA DUYET
    # =====================================================
    later_reviewed = [
        row
        for row in rows
        if int(row["SoThuTuBai"]) >= 4
        and row["DaKiemDuyet"] == "1"
    ]

    if later_reviewed:

        raise RuntimeError(
            "Phat hien Bai 4 -> 23 "
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
    # 11. CAP NHAT BAI 3
    # =====================================================
    updated = 0

    for row in rows:

        if int(row["SoThuTuBai"]) != 3:
            continue

        word = row["ChuHan"].strip()

        review = LESSON3_REVIEW[word]

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
            "So dong cap nhat Bai 3 "
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

    lesson3_verified = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) == 3
        and row["DaKiemDuyet"] == "1"
    ]

    if len(lesson3_verified) != 23:

        raise RuntimeError(
            "Verify that bai: "
            "Bai 3 khong co du 23 tu."
        )

    # =====================================================
    # 14. CAC BAI SAU KHONG DUOC BI THAY DOI
    # =====================================================
    reviewed_after = [
        row
        for row in verify_rows
        if int(row["SoThuTuBai"]) >= 4
        and row["DaKiemDuyet"] == "1"
    ]

    if reviewed_after:

        raise RuntimeError(
            "Bai 4 -> 23 bi thay doi "
            "ngoai y muon."
        )

    # =====================================================
    # 15. IN NOI DUNG BAI 3
    # =====================================================
    lesson3_verified.sort(
        key=lambda row: int(
            row["ThuTuTrongBai"]
        )
    )

    print()
    print("-" * 95)
    print("NOI DUNG BAI 3 SAU REVIEW")
    print("-" * 95)

    for row in lesson3_verified:

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

    print()
    print("=" * 95)
    print("KET QUA")
    print("=" * 95)

    print(
        "Tong tu trong file:",
        len(verify_rows),
    )

    print(
        "Bai 1 da kiem duyet:",
        13,
    )

    print(
        "Bai 2 da kiem duyet:",
        29,
    )

    print(
        "Bai 3 da kiem duyet:",
        len(lesson3_verified),
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