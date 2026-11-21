from pathlib import Path
import csv
import sys
from collections import Counter, defaultdict


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
# SO LUONG TU CUA 23 BAI
# =========================================================
EXPECTED_LESSON_COUNTS = {
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


# =========================================================
# CAC TU DA AM CAN KIEM TRA DAC BIET
#
# Day la cac muc co cung ChuHan
# nhung khac cach doc / nghia.
# =========================================================
SPECIAL_CASES = [
    {
        "lesson": 9,
        "hanzi": "干",
        "pinyin": "gàn",
        "meaning": "làm; làm việc",
    },
    {
        "lesson": 15,
        "hanzi": "干",
        "pinyin": "gān",
        "meaning": "khô",
    },
    {
        "lesson": 20,
        "hanzi": "还",
        "pinyin": "hái",
        "meaning": "vẫn; còn",
    },
    {
        "lesson": 20,
        "hanzi": "还",
        "pinyin": "huán",
        "meaning": "trả lại; hoàn lại",
    },
    {
        "lesson": 13,
        "hanzi": "地",
        "pinyin": "dì",
        "meaning": "đất; mặt đất",
    },
    {
        "lesson": 23,
        "hanzi": "地",
        "pinyin": "de",
        "meaning": "trợ từ nối trạng ngữ với động từ",
    },
]


# =========================================================
# CAC CHU HAN DUOC PHEP LAP
#
# Chi lap vi khac cach doc / nghia.
# =========================================================
EXPECTED_DUPLICATE_HANZI = {
    "干": 2,
    "还": 2,
    "地": 2,
}


# =========================================================
# NGUON DU LIEU MONG DOI
#
# 500 tu HSK1 chuan:
#     MaNguon = 1002
#
# 1 tu bo sung 越南:
#     MaNguon = 2 (CC-CEDICT)
# =========================================================
EXPECTED_SOURCE_COUNTS = {
    "1002": 500,
    "2": 1,
}


# =========================================================
# HELPERS
# =========================================================
def clean(row, column):
    return (row.get(column) or "").strip()


def fail(message):
    raise RuntimeError(message)


def get_lesson_rows(rows, lesson_no):
    return [
        row
        for row in rows
        if int(clean(row, "SoThuTuBai")) == lesson_no
    ]


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 100)
    print("09G26 - AUDIT CUOI TOAN BO TU VUNG HSK1 DA KIEM DUYET")
    print("=" * 100)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE REVIEW")
    print("  KHONG GHI FILE")
    print("  KHONG KET NOI DATABASE")
    print("  KHONG SUA DATABASE")

    # =====================================================
    # 1. KIEM TRA FILE TON TAI
    # =====================================================
    if not REVIEW_FILE.exists():
        fail(
            "Khong tim thay file review:\n"
            f"{REVIEW_FILE}"
        )

    print()
    print("File review:")
    print(REVIEW_FILE)

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
            fail("Khong doc duoc header CSV.")

        rows = list(reader)

    # =====================================================
    # 3. KIEM TRA COT BAT BUOC
    # =====================================================
    required_columns = {
        "SoThuTuBai",
        "TieuDeBai",
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
        fail(
            "File review thieu cot:\n"
            + ", ".join(
                sorted(missing_columns)
            )
        )

    print()
    print("[1] KIEM TRA CAU TRUC FILE")
    print("-" * 100)

    print(
        "So cot:",
        len(fieldnames),
    )

    print(
        "So dong:",
        len(rows),
    )

    if len(rows) != 501:
        fail(
            "File review phai co dung 501 dong. "
            f"Thuc te: {len(rows)}"
        )

    print("Tong 501 dong: OK")

    # =====================================================
    # 4. KIEM TRA DU LIEU BAT BUOC
    # =====================================================
    print()
    print("[2] KIEM TRA CAC TRUONG BAT BUOC")
    print("-" * 100)

    fields_must_not_be_empty = [
        "SoThuTuBai",
        "TieuDeBai",
        "ThuTuTrongBai",
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "NghiaNguon",
        "MaNguon",
        "TuLoaiHocTap",
        "NghiaHocTap",
        "GhiChuKiemDuyet",
        "DaKiemDuyet",
    ]

    for column in fields_must_not_be_empty:

        empty_rows = [
            row
            for row in rows
            if not clean(row, column)
        ]

        print(
            f"{column}:",
            len(empty_rows),
            "dong trong",
        )

        if empty_rows:
            fail(
                f"Phat hien {len(empty_rows)} "
                f"dong thieu {column}."
            )

    print("Tat ca truong bat buoc: OK")

    # =====================================================
    # 5. KIEM TRA 501 DONG DA REVIEW
    # =====================================================
    print()
    print("[3] KIEM TRA TRANG THAI KIEM DUYET")
    print("-" * 100)

    reviewed_rows = [
        row
        for row in rows
        if clean(row, "DaKiemDuyet") == "1"
    ]

    unreviewed_rows = [
        row
        for row in rows
        if clean(row, "DaKiemDuyet") != "1"
    ]

    print(
        "DaKiemDuyet = 1:",
        len(reviewed_rows),
    )

    print(
        "Chua kiem duyet:",
        len(unreviewed_rows),
    )

    if len(reviewed_rows) != 501:
        fail(
            "Khong phai tat ca 501 dong "
            "deu DaKiemDuyet=1."
        )

    if unreviewed_rows:
        fail(
            "Van con dong chua kiem duyet."
        )

    print("Trang thai kiem duyet: OK")

    # =====================================================
    # 6. KIEM TRA SO LUONG 23 BAI
    # =====================================================
    print()
    print("[4] KIEM TRA SO LUONG TU TUNG BAI")
    print("-" * 100)

    lesson_counter = Counter()

    for row in rows:

        try:
            lesson_no = int(
                clean(
                    row,
                    "SoThuTuBai",
                )
            )

        except ValueError:
            fail(
                "SoThuTuBai co gia tri "
                "khong phai so nguyen."
            )

        lesson_counter[lesson_no] += 1

    if set(lesson_counter.keys()) != set(
        EXPECTED_LESSON_COUNTS.keys()
    ):
        fail(
            "Danh sach SoThuTuBai "
            "khong dung tu Bai 1 -> Bai 23."
        )

    for lesson_no, expected_count in (
        EXPECTED_LESSON_COUNTS.items()
    ):

        actual_count = lesson_counter[
            lesson_no
        ]

        status = (
            "OK"
            if actual_count == expected_count
            else "SAI"
        )

        print(
            f"Bai {lesson_no:>2}: "
            f"{actual_count}/{expected_count} "
            f"{status}"
        )

        if actual_count != expected_count:
            fail(
                f"Bai {lesson_no} "
                f"phai co {expected_count} tu, "
                f"thuc te {actual_count}."
            )

    if sum(
        EXPECTED_LESSON_COUNTS.values()
    ) != 501:
        fail(
            "Tong EXPECTED_LESSON_COUNTS "
            "khong bang 501."
        )

    print()
    print("Phan bo 23 bai: OK")

    # =====================================================
    # 7. KIEM TRA THU TU TRONG TUNG BAI
    # =====================================================
    print()
    print("[5] KIEM TRA THU TU TU VUNG TRONG TUNG BAI")
    print("-" * 100)

    for lesson_no, expected_count in (
        EXPECTED_LESSON_COUNTS.items()
    ):

        lesson_rows = get_lesson_rows(
            rows,
            lesson_no,
        )

        try:
            lesson_orders = sorted(
                int(
                    clean(
                        row,
                        "ThuTuTrongBai",
                    )
                )
                for row in lesson_rows
            )

        except ValueError:
            fail(
                f"Bai {lesson_no} co "
                "ThuTuTrongBai khong hop le."
            )

        expected_orders = list(
            range(
                1,
                expected_count + 1,
            )
        )

        if lesson_orders != expected_orders:
            fail(
                f"ThuTuTrongBai cua Bai "
                f"{lesson_no} khong lien tuc "
                f"tu 1 -> {expected_count}."
            )

        print(
            f"Bai {lesson_no:>2}: "
            f"1 -> {expected_count} OK"
        )

    # =====================================================
    # 8. KIEM TRA MaTuVung
    # =====================================================
    print()
    print("[6] KIEM TRA MaTuVung")
    print("-" * 100)

    vocab_ids = []

    for row in rows:

        vocab_id = clean(
            row,
            "MaTuVung",
        )

        if not vocab_id.isdigit():
            fail(
                "Phat hien MaTuVung "
                "khong phai so nguyen: "
                f"{vocab_id}"
            )

        vocab_ids.append(
            int(vocab_id)
        )

    duplicate_ids = [
        vocab_id
        for vocab_id, count
        in Counter(vocab_ids).items()
        if count > 1
    ]

    print(
        "Tong MaTuVung:",
        len(vocab_ids),
    )

    print(
        "MaTuVung duy nhat:",
        len(set(vocab_ids)),
    )

    print(
        "MaTuVung bi lap:",
        len(duplicate_ids),
    )

    if duplicate_ids:
        fail(
            "Phat hien MaTuVung bi lap: "
            + ", ".join(
                map(
                    str,
                    sorted(duplicate_ids),
                )
            )
        )

    if len(set(vocab_ids)) != 501:
        fail(
            "Phai co 501 MaTuVung duy nhat."
        )

    print("MaTuVung: OK")

    # =====================================================
    # 9. KIEM TRA CHU HAN + PINYIN TRUNG NHAU
    # =====================================================
    print()
    print("[7] KIEM TRA KHOA ChuHan + PhienAm")
    print("-" * 100)

    pair_counter = Counter(
        (
            clean(row, "ChuHan"),
            clean(row, "PhienAm"),
        )
        for row in rows
    )

    duplicate_pairs = [
        (key, count)
        for key, count
        in pair_counter.items()
        if count > 1
    ]

    print(
        "Cap ChuHan + PhienAm bi lap:",
        len(duplicate_pairs),
    )

    if duplicate_pairs:

        for (
            hanzi,
            pinyin,
        ), count in duplicate_pairs:

            print(
                f"  {hanzi} [{pinyin}] "
                f"x{count}"
            )

        fail(
            "Phat hien ChuHan + PhienAm "
            "bi trung."
        )

    print(
        "Khong co cap ChuHan + PhienAm "
        "bi trung: OK"
    )

    # =====================================================
    # 10. KIEM TRA CAC CHU HAN LAP DO DA AM
    # =====================================================
    print()
    print("[8] KIEM TRA CAC CHU HAN DA AM")
    print("-" * 100)

    hanzi_counter = Counter(
        clean(row, "ChuHan")
        for row in rows
    )

    duplicate_hanzi = {
        hanzi: count
        for hanzi, count
        in hanzi_counter.items()
        if count > 1
    }

    print(
        "Cac ChuHan xuat hien nhieu hon 1 lan:"
    )

    for hanzi, count in sorted(
        duplicate_hanzi.items()
    ):

        print(
            f"  {hanzi}: {count}"
        )

    if duplicate_hanzi != (
        EXPECTED_DUPLICATE_HANZI
    ):
        print()
        print(
            "Mong doi:",
            EXPECTED_DUPLICATE_HANZI,
        )

        print(
            "Thuc te:",
            duplicate_hanzi,
        )

        fail(
            "Danh sach ChuHan lap "
            "khong dung nhu mong doi."
        )

    print(
        "Danh sach tu da am: OK"
    )

    # =====================================================
    # 11. KIEM TRA CHI TIET TU DA AM
    # =====================================================
    print()
    print("[9] KIEM TRA CHI TIET 干 / 还 / 地")
    print("-" * 100)

    for case in SPECIAL_CASES:

        matches = [
            row
            for row in rows
            if (
                int(
                    clean(
                        row,
                        "SoThuTuBai",
                    )
                )
                == case["lesson"]
                and clean(
                    row,
                    "ChuHan",
                )
                == case["hanzi"]
                and clean(
                    row,
                    "PhienAm",
                )
                == case["pinyin"]
            )
        ]

        if len(matches) != 1:
            fail(
                "Khong tim thay dung 1 muc: "
                f"Bai {case['lesson']} - "
                f"{case['hanzi']} "
                f"[{case['pinyin']}]"
            )

        row = matches[0]

        actual_meaning = clean(
            row,
            "NghiaHocTap",
        )

        if actual_meaning != case["meaning"]:
            fail(
                "Sai NghiaHocTap: "
                f"{case['hanzi']} "
                f"[{case['pinyin']}]\n"
                f"Mong doi: {case['meaning']}\n"
                f"Thuc te: {actual_meaning}"
            )

        print(
            f"Bai {case['lesson']:>2} | "
            f"{case['hanzi']} "
            f"[{case['pinyin']}] "
            f"-> {actual_meaning} OK"
        )

    # =====================================================
    # 12. KIEM TRA NGUON DU LIEU
    # =====================================================
    print()
    print("[10] KIEM TRA NGUON DU LIEU")
    print("-" * 100)

    source_counter = Counter(
        clean(row, "MaNguon")
        for row in rows
    )

    for source_id, count in sorted(
        source_counter.items()
    ):

        print(
            f"MaNguon {source_id}: {count}"
        )

    if dict(source_counter) != (
        EXPECTED_SOURCE_COUNTS
    ):
        print()
        print(
            "Nguon mong doi:",
            EXPECTED_SOURCE_COUNTS,
        )

        print(
            "Nguon thuc te:",
            dict(source_counter),
        )

        fail(
            "So luong MaNguon khong "
            "dung nhu mong doi."
        )

    print(
        "500 tu HSK + 1 tu bo sung: OK"
    )

    # =====================================================
    # 13. KIEM TRA RIENG 越南
    # =====================================================
    print()
    print("[11] KIEM TRA TU BO SUNG 越南")
    print("-" * 100)

    vietnam_rows = [
        row
        for row in rows
        if clean(
            row,
            "ChuHan",
        ) == "越南"
    ]

    if len(vietnam_rows) != 1:
        fail(
            "Phai co dung 1 dong 越南."
        )

    vietnam = vietnam_rows[0]

    if int(
        clean(
            vietnam,
            "SoThuTuBai",
        )
    ) != 2:
        fail(
            "越南 phai nam o Bai 2."
        )

    if clean(
        vietnam,
        "MaNguon",
    ) != "2":
        fail(
            "越南 phai co MaNguon=2."
        )

    if clean(
        vietnam,
        "PhienAm",
    ).casefold() != "yuènán":
        fail(
            "PhienAm cua 越南 khong dung "
            f"mong doi: {clean(vietnam, 'PhienAm')}"
        )

    if clean(
        vietnam,
        "NghiaHocTap",
    ) != "Việt Nam":
        fail(
            "NghiaHocTap cua 越南 "
            "phai la 'Việt Nam'."
        )

    print(
        "Bai:",
        clean(
            vietnam,
            "SoThuTuBai",
        ),
    )

    print(
        "PhienAm:",
        clean(
            vietnam,
            "PhienAm",
        ),
    )

    print(
        "NghiaHocTap:",
        clean(
            vietnam,
            "NghiaHocTap",
        ),
    )

    print(
        "MaNguon:",
        clean(
            vietnam,
            "MaNguon",
        ),
    )

    print("越南: OK")

    # =====================================================
    # 14. KIEM TRA DO DAI NGHIA HOC TAP
    # =====================================================
    print()
    print("[12] KIEM TRA NGHIA HOC TAP")
    print("-" * 100)

    long_meanings = [
        row
        for row in rows
        if len(
            clean(
                row,
                "NghiaHocTap",
            )
        ) > 120
    ]

    max_meaning_row = max(
        rows,
        key=lambda row: len(
            clean(
                row,
                "NghiaHocTap",
            )
        ),
    )

    max_length = len(
        clean(
            max_meaning_row,
            "NghiaHocTap",
        )
    )

    print(
        "NghiaHocTap dai nhat:",
        max_length,
        "ky tu",
    )

    print(
        "NghiaHocTap > 120 ky tu:",
        len(long_meanings),
    )

    if long_meanings:
        fail(
            "Van con NghiaHocTap "
            "qua dai (>120 ky tu)."
        )

    # =====================================================
    # 15. KIEM TRA KY HIEU RAC TRONG NGHIA HOC TAP
    # =====================================================
    suspicious_tokens = [
        "||",
        "{",
        "}",
        "http://",
        "https://",
    ]

    suspicious_rows = []

    for row in rows:

        meaning = clean(
            row,
            "NghiaHocTap",
        )

        found_tokens = [
            token
            for token in suspicious_tokens
            if token in meaning
        ]

        if found_tokens:
            suspicious_rows.append(
                (
                    row,
                    found_tokens,
                )
            )

    print(
        "NghiaHocTap co ky hieu rac:",
        len(suspicious_rows),
    )

    if suspicious_rows:

        for row, tokens in suspicious_rows:

            print(
                clean(row, "ChuHan"),
                clean(row, "PhienAm"),
                tokens,
                clean(row, "NghiaHocTap"),
            )

        fail(
            "Phat hien ky hieu rac "
            "trong NghiaHocTap."
        )

    print("NghiaHocTap: OK")

    # =====================================================
    # 16. KIEM TRA TU LOAI NGUON
    #
    # TuLoaiNguon co the trong.
    # Day la du lieu nguon, KHONG phai loi.
    # =====================================================
    print()
    print("[13] THONG KE TuLoaiNguon")
    print("-" * 100)

    empty_source_pos = [
        row
        for row in rows
        if not clean(
            row,
            "TuLoaiNguon",
        )
    ]

    print(
        "TuLoaiNguon trong:",
        len(empty_source_pos),
    )

    print(
        "Luu y: day la cot du lieu nguon, "
        "khong phai TuLoaiHocTap."
    )

    print(
        "TuLoaiHocTap trong:",
        sum(
            1
            for row in rows
            if not clean(
                row,
                "TuLoaiHocTap",
            )
        ),
    )

    # =====================================================
    # 17. KET QUA CUOI
    # =====================================================
    print()
    print("=" * 100)
    print("KET QUA AUDIT CUOI CUNG")
    print("=" * 100)

    print(
        "Tong dong:",
        len(rows),
    )

    print(
        "Tong bai:",
        len(EXPECTED_LESSON_COUNTS),
    )

    print(
        "DaKiemDuyet=1:",
        len(reviewed_rows),
    )

    print(
        "MaTuVung duy nhat:",
        len(set(vocab_ids)),
    )

    print(
        "Cap ChuHan + PhienAm bi trung:",
        len(duplicate_pairs),
    )

    print(
        "Tu da am duoc kiem tra:",
        len(SPECIAL_CASES),
    )

    print(
        "Tu HSK chuan:",
        source_counter.get(
            "1002",
            0,
        ),
    )

    print(
        "Tu bo sung CC-CEDICT:",
        source_counter.get(
            "2",
            0,
        ),
    )

    print(
        "Dong thieu TuLoaiHocTap:",
        sum(
            1
            for row in rows
            if not clean(
                row,
                "TuLoaiHocTap",
            )
        ),
    )

    print(
        "Dong thieu NghiaHocTap:",
        sum(
            1
            for row in rows
            if not clean(
                row,
                "NghiaHocTap",
            )
        ),
    )

    print(
        "Dong thieu GhiChuKiemDuyet:",
        sum(
            1
            for row in rows
            if not clean(
                row,
                "GhiChuKiemDuyet",
            )
        ),
    )

    print()
    print(
        "AUDIT THANH CONG."
    )

    print(
        "FILE REVIEW HSK1 SAN SANG "
        "CHO BUOC DOI CHIEU VOI DATABASE."
    )

    print()
    print(
        "SCRIPT NAY KHONG SUA FILE REVIEW."
    )

    print(
        "SCRIPT NAY KHONG KET NOI "
        "HOAC SUA DATABASE."
    )

    print()
    print("=" * 100)
    print("HOAN TAT")
    print("=" * 100)


if __name__ == "__main__":

    try:
        main()

    except Exception as e:

        print()
        print("=" * 100)
        print("AUDIT THAT BAI")
        print("=" * 100)

        print()
        print("Loi:")
        print(e)

        print()
        print(
            "KHONG CO DU LIEU NAO "
            "DUOC GHI HOAC SUA."
        )

        sys.exit(1)