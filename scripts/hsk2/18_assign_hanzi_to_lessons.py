from pathlib import Path
import csv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"


HANZI_FILE = (
    DATA_DIR / "hanzi_hsk2_final.csv"
)

VOCAB_FILE = (
    DATA_DIR / "vocabulary_hsk2_final_by_lesson.csv"
)

OUTPUT_FILE = (
    DATA_DIR / "hanzi_hsk2_by_lesson.csv"
)


LESSON_NAMES = {
    1: "Một ngày của tôi",
    2: "Cuộc sống học tập",
    3: "Công việc",
    4: "Gia đình và bạn bè",
    5: "Ngoại hình và tính cách",
    6: "Thời tiết và các mùa",
    7: "Sức khỏe",
    8: "Ăn uống",
    9: "Mua sắm",
    10: "Vị trí và khoảng cách",
    11: "Hỏi đường và giao thông",
    12: "Du lịch",
    13: "Thể thao",
    14: "Sở thích và cuối tuần",
    15: "Ngày lễ và sự kiện",
    16: "Hành động đã hoàn thành",
    17: "Hành động đang diễn ra",
    18: "So sánh",
    19: "Thay đổi và mức độ",
    20: "Nguyên nhân và điều kiện",
    21: "Liên lạc và giao tiếp",
    22: "Văn hóa và quan điểm",
    23: "Ôn tập và từ dùng chung",
}


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def read_csv(path):

    if not path.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)
        fields = reader.fieldnames

    if not fields:
        raise ValueError(
            f"File khong co header:\n{path}"
        )

    return rows, fields


def main():

    print("=" * 78)
    print("BUOC 18 - PHAN 299 CHU HAN HSK2 VAO 23 BAI")
    print("DUA TREN 772 TU VUNG HSK2 DA CHOT")
    print("KHONG GHI SQL")
    print("=" * 78)

    # ========================================================
    # 1. DOC 299 CHU HAN
    # ========================================================

    hanzi_rows, hanzi_fields = read_csv(
        HANZI_FILE
    )

    if len(hanzi_rows) != 299:
        raise ValueError(
            f"Du kien 299 chu Han HSK2, "
            f"nhung file co {len(hanzi_rows)}."
        )

    # ========================================================
    # 2. DOC 772 TU VUNG DA CHIA BAI
    # ========================================================

    vocab_rows, vocab_fields = read_csv(
        VOCAB_FILE
    )

    if len(vocab_rows) != 772:
        raise ValueError(
            f"Du kien 772 tu HSK2, "
            f"nhung file co {len(vocab_rows)}."
        )

    required_vocab_columns = {
        "MaTuHSK",
        "ChuHan",
        "SoThuTuBai",
        "MaBaiHocTam",
    }

    missing_vocab_columns = (
        required_vocab_columns
        - set(vocab_fields)
    )

    if missing_vocab_columns:

        raise ValueError(
            "File tu vung thieu cot:\n"
            + ", ".join(
                sorted(missing_vocab_columns)
            )
        )

    if "KyTu" not in hanzi_fields:

        raise ValueError(
            "File Chu Han khong co cot KyTu."
        )

    # ========================================================
    # 3. KIEM TRA CAC BAI TU VUNG
    # ========================================================

    for row in vocab_rows:

        lesson_text = clean(
            row["SoThuTuBai"]
        )

        if not lesson_text:

            raise ValueError(
                "Co tu vung chua co SoThuTuBai: "
                f"{row.get('MaTuHSK')}"
            )

        lesson = int(
            lesson_text
        )

        if lesson < 1 or lesson > 23:

            raise ValueError(
                "SoThuTuBai khong hop le: "
                f"{lesson}"
            )

    # Sap xep tu vung theo bai truoc
    vocab_rows.sort(
        key=lambda row: (
            int(row["SoThuTuBai"]),
            int(row["SoThuTuNguon"])
            if clean(
                row.get("SoThuTuNguon")
            )
            else 999999,
            int(row["MaTuHSK"])
        )
    )

    # ========================================================
    # 4. THEM CAC COT PHAN BAI CHU HAN
    # ========================================================

    fields = list(
        hanzi_fields
    )

    extra_fields = [
        "MaBaiHocTam",
        "SoThuTuBai",
        "TenBaiHoc",
        "ThuTuTrongBai",
        "TuVungDaiDien",
        "MaTuHSKDaiDien",
        "CacBaiXuatHien",
        "SoTuHSK2ChuaKyTu",
        "CachPhan",
    ]

    for field in extra_fields:

        if field not in fields:
            fields.append(
                field
            )

    assigned = []
    unmatched = []

    # ========================================================
    # 5. TIM BAI CHO TUNG CHU
    # ========================================================

    for hanzi_row in hanzi_rows:

        char = clean(
            hanzi_row["KyTu"]
        )

        if not char:

            raise ValueError(
                "Co dong Chu Han bi rong KyTu."
            )

        occurrences = []

        for vocab in vocab_rows:

            word = clean(
                vocab["ChuHan"]
            )

            if char in word:

                lesson = int(
                    vocab[
                        "SoThuTuBai"
                    ]
                )

                occurrences.append({
                    "lesson": lesson,
                    "word": word,
                    "MaTuHSK": int(
                        vocab["MaTuHSK"]
                    ),
                    "source_order": int(
                        vocab["SoThuTuNguon"]
                    )
                    if clean(
                        vocab.get(
                            "SoThuTuNguon"
                        )
                    )
                    else 999999,
                })

        # ================================================
        # Chu khong xuat hien trong 772 tu
        # -> khong duoc tu gan bua
        # ================================================

        if not occurrences:

            unmatched.append(
                char
            )

            continue

        # ================================================
        # BAI DAU TIEN MA CHU XUAT HIEN
        # ================================================

        occurrences.sort(
            key=lambda item: (
                item["lesson"],
                item["source_order"],
                item["MaTuHSK"]
            )
        )

        first = occurrences[0]

        lesson = first[
            "lesson"
        ]

        # Cac bai ma chu nay co xuat hien
        lesson_ids = sorted({
            item["lesson"]
            for item in occurrences
        })

        hanzi_row[
            "MaBaiHocTam"
        ] = (
            f"L2-{lesson:02d}"
        )

        hanzi_row[
            "SoThuTuBai"
        ] = lesson

        hanzi_row[
            "TenBaiHoc"
        ] = (
            LESSON_NAMES[
                lesson
            ]
        )

        hanzi_row[
            "TuVungDaiDien"
        ] = first[
            "word"
        ]

        hanzi_row[
            "MaTuHSKDaiDien"
        ] = first[
            "MaTuHSK"
        ]

        hanzi_row[
            "CacBaiXuatHien"
        ] = ",".join(
            map(
                str,
                lesson_ids
            )
        )

        hanzi_row[
            "SoTuHSK2ChuaKyTu"
        ] = len(
            occurrences
        )

        hanzi_row[
            "CachPhan"
        ] = (
            "bai_dau_tien_chua_ky_tu"
        )

        # MaBaiHoc that se gan sau khi tao BaiHoc SQL
        if "MaBaiHoc" in hanzi_row:
            hanzi_row[
                "MaBaiHoc"
            ] = ""

        # Van la ban nhap
        if "TrangThai" in hanzi_row:
            hanzi_row[
                "TrangThai"
            ] = "ban_nhap"

        assigned.append(
            hanzi_row
        )

    # ========================================================
    # 6. KHONG DUOC CO CHU KHONG TIM THAY
    # ========================================================

    if unmatched:

        print()
        print(
            "CAC CHU KHONG TIM THAY "
            "TRONG 772 TU:"
        )

        for char in unmatched:
            print(
                f"  {char}"
            )

        raise ValueError(
            f"Con {len(unmatched)} "
            "chu chua gan duoc bai."
        )

    if len(assigned) != 299:

        raise ValueError(
            "So Chu Han da gan "
            "khong bang 299."
        )

    # ========================================================
    # 7. KIEM TRA KHONG TRUNG KyTu
    # ========================================================

    chars = [
        clean(
            row["KyTu"]
        )
        for row in assigned
    ]

    duplicates = sorted({
        char
        for char in chars
        if chars.count(
            char
        ) > 1
    })

    if duplicates:

        raise ValueError(
            "Co KyTu bi trung:\n"
            + ", ".join(
                duplicates
            )
        )

    # ========================================================
    # 8. SAP THEO BAI
    # ========================================================

    assigned.sort(
        key=lambda row: (
            int(
                row["SoThuTuBai"]
            ),
            int(
                row["MaTuHSKDaiDien"]
            ),
            clean(
                row["KyTu"]
            )
        )
    )

    counters = {
        i: 0
        for i in range(
            1,
            24
        )
    }

    for row in assigned:

        lesson = int(
            row[
                "SoThuTuBai"
            ]
        )

        counters[
            lesson
        ] += 1

        order = counters[
            lesson
        ]

        row[
            "ThuTuTrongBai"
        ] = order

        # ThuTuTam sau nay dung de dua vao ChuHan.ThuTu
        if "ThuTuTam" in row:
            row[
                "ThuTuTam"
            ] = order

    # ========================================================
    # 9. KIEM TRA DU LIEU CHU HAN
    # ========================================================

    required_hanzi_values = [
        "KyTu",
        "Pinyin",
        "NghiaTiengViet",
        "MaBoThu",
        "SoNet",
        "SoThuTuBai",
    ]

    errors = []

    for row in assigned:

        for field in required_hanzi_values:

            if not clean(
                row.get(field)
            ):

                errors.append(
                    (
                        row.get(
                            "KyTu"
                        ),
                        field
                    )
                )

    if errors:

        print()
        print(
            "CAC TRUONG CHU HAN CON THIEU:"
        )

        for char, field in errors:
            print(
                f"  {char}: {field}"
            )

        raise ValueError(
            f"Con {len(errors)} "
            "gia tri Chu Han bi thieu."
        )

    # ========================================================
    # 10. GHI FILE
    # ========================================================

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerows(
            assigned
        )

    # ========================================================
    # 11. THONG KE
    # ========================================================

    print()
    print(
        f"Tong Chu Han HSK2: "
        f"{len(assigned)}"
    )

    print(
        f"Chu chua gan bai: "
        f"{len(unmatched)}"
    )

    print(
        f"KyTu duy nhat: "
        f"{len(set(chars))}"
    )

    print()
    print(
        "CHU HAN THEO BAI:"
    )

    total = 0

    for lesson in range(
        1,
        24
    ):

        count = counters[
            lesson
        ]

        total += count

        print(
            f"  Bai "
            f"{lesson:02d}: "
            f"{count} chu"
        )

    print()
    print(
        f"Tong kiem tra: "
        f"{total}/299"
    )

    print()
    print(
        "Da tao:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "MaBaiHoc van de trong."
    )

    print(
        "TrangThai = ban_nhap."
    )

    print(
        "CHUA INSERT/UPDATE/DELETE SQL."
    )


if __name__ == "__main__":
    main()