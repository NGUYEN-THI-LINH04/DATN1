# -*- coding: utf-8 -*-
"""
BUOC 18 - TAO TAP CHU HAN HSK4 TU 1000 TU VUNG CHUAN

Nguon pham vi:
- dbo.TuVungHSKChuan
- MaCapDo = 4
- 1000 muc tu GF0025 HSK4

Cach lam:
1. Doc 1000 muc HSK4.
2. Tach cac KyTu Han xuat hien trong ChuHan.
3. Tao tap KyTu unique theo thu tu xuat hien dau tien.
4. Doi chieu voi dbo.ChuHan HSK1-3.
5. Chia:
   - DA_CO_SQL
   - MOI_HSK4
6. Ghi CSV preview.

KHONG tao BaiHoc.
KHONG INSERT ChuHan.
KHONG UPDATE.
KHONG DELETE.
KHONG thay doi SQL.
"""

import csv
import hashlib
import json
import re
import sys

from collections import defaultdict
from contextlib import closing
from pathlib import Path


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT),
)

from database import get_connection


OUTPUT_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

ALL_FILE = (
    OUTPUT_DIR
    / "hanzi_hsk4_all_characters.csv"
)

EXISTING_FILE = (
    OUTPUT_DIR
    / "hanzi_hsk4_existing.csv"
)

NEW_FILE = (
    OUTPUT_DIR
    / "hanzi_hsk4_new_candidates.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR
    / "hanzi_hsk4_candidates_summary.json"
)


EXPECTED_HSK4_VOCAB = 1000
EXPECTED_LEVEL = 4


ALL_FIELDS = [
    "MaChuHanTam",
    "KyTu",

    "ThuTuXuatHienDau",
    "MaTuHSKDauTien",
    "MaMucNoiBoDauTien",
    "SoThuTuNguonDauTien",

    "TuVungDaiDien",
    "PinyinTuDaiDien",
    "NghiaTuDaiDien",

    "SoTuHSK4ChuaKyTu",
    "CacMaMucNoiBo",
    "CacTuHSK4ChuaKyTu",

    "DaCoTrongSQL",
    "SoDongChuHanSQL",
    "MaChuHanDaCo",
    "KhoaHocDaCo",
    "BaiHocDaCo",

    "PinyinSQLThamKhao",
    "NghiaSQLThamKhao",
    "SoNetSQLThamKhao",
    "MaBoThuSQLThamKhao",

    "HanhDongDeXuat",
    "TrangThai",
]


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):

    return (
        str(value).strip()
        if value is not None
        else ""
    )


def fetch_all(
    cursor,
    sql,
    *params,
):

    cursor.execute(
        sql,
        *params,
    )

    columns = [
        item[0]
        for item in cursor.description
    ]

    return [
        dict(
            zip(
                columns,
                row,
            )
        )
        for row in cursor.fetchall()
    ]


def get_columns(
    cursor,
    table_name,
):

    rows = fetch_all(
        cursor,
        """
        SELECT
            COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """,
        table_name,
    )

    return {
        row["COLUMN_NAME"]
        for row in rows
    }


def write_csv(
    path,
    rows,
):

    if path.exists():

        raise FileExistsError(
            f"File da ton tai:\n{path}\n"
            "Khong tu dong ghi de."
        )

    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=ALL_FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def is_han_character(char):
    """
    Kiem tra mot ky tu CJK Han.

    Bao gom:
    - CJK Unified Ideographs Extension A
    - CJK Unified Ideographs
    - CJK Compatibility Ideographs
    - cac extension Unicode ngoai BMP thuong gap
    """

    if len(char) != 1:
        return False

    code = ord(char)

    ranges = [
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0xF900, 0xFAFF),

        (0x20000, 0x2A6DF),
        (0x2A700, 0x2B73F),
        (0x2B740, 0x2B81F),
        (0x2B820, 0x2CEAF),
        (0x2CEB0, 0x2EBEF),
        (0x30000, 0x3134F),
    ]

    return any(
        start <= code <= end
        for start, end in ranges
    )


def extract_hanzi(text):

    chars = []

    seen = set()

    for char in clean(text):

        if not is_han_character(
            char
        ):
            continue

        # Trong cung mot tu:
        # mot KyTu chi tinh mot lan.
        if char in seen:
            continue

        seen.add(
            char
        )

        chars.append(
            char
        )

    return chars


def build_snapshot_hash(rows):
    """
    Hash deterministic cho 1000 muc TuVungHSKChuan HSK4.
    Khong phu thuoc JSON spacing.
    """

    parts = []

    for row in rows:

        parts.append(
            "\t".join([
                clean(
                    row.get(
                        "MaTuHSK"
                    )
                ),
                clean(
                    row.get(
                        "MaMucNoiBo"
                    )
                ),
                clean(
                    row.get(
                        "SoThuTuNguon"
                    )
                ),
                clean(
                    row.get(
                        "ChuHan"
                    )
                ),
                clean(
                    row.get(
                        "PhienAm"
                    )
                ),
                clean(
                    row.get(
                        "TuLoai"
                    )
                ),
                clean(
                    row.get(
                        "NghiaTiengVietThamChieu"
                    )
                ),
            ])
        )

    payload = (
        "\n".join(parts)
        + "\n"
    ).encode(
        "utf-8"
    )

    return hashlib.sha256(
        payload
    ).hexdigest()


def join_unique(
    values,
    separator=" | ",
):

    result = []

    seen = set()

    for value in values:

        value = clean(
            value
        )

        if not value:
            continue

        if value in seen:
            continue

        seen.add(
            value
        )

        result.append(
            value
        )

    return separator.join(
        result
    )


# ==========================================================
# 3. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 18 - TAO TAP CHU HAN "
        "HSK4 TU TU VUNG CHUAN"
    )

    print("=" * 80)

    print(
        "CHI SELECT SQL + TAO CSV"
    )

    print(
        "KHONG INSERT / UPDATE / DELETE"
    )

    # ======================================================
    # 1. DOC SQL
    # ======================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            # ==================================================
            # 1A. KIEM TRA SCHEMA TuVungHSKChuan
            # ==================================================

            print(
                "\n[1] KIEM TRA SCHEMA "
                "dbo.TuVungHSKChuan"
            )

            vocab_columns = get_columns(
                cursor,
                "TuVungHSKChuan",
            )

            required_vocab_columns = {
                "MaTuHSK",
                "MaMucNoiBo",
                "MaCapDo",
                "SoThuTuNguon",
                "ChuHan",
                "PhienAm",
                "TuLoai",
                "NghiaTiengVietThamChieu",
            }

            missing = (
                required_vocab_columns
                - vocab_columns
            )

            if missing:

                raise RuntimeError(
                    "dbo.TuVungHSKChuan "
                    "thieu cot: "
                    + ", ".join(
                        sorted(
                            missing
                        )
                    )
                )

            print(
                "PASS: schema TuVungHSKChuan "
                "du cot can thiet."
            )

            # ==================================================
            # 1B. DOC 1000 MUC HSK4
            # ==================================================

            print(
                "\n[2] DOC TU VUNG CHUAN HSK4"
            )

            vocab_rows = fetch_all(
                cursor,
                """
                SELECT
                    MaTuHSK,
                    MaMucNoiBo,
                    MaCapDo,
                    SoThuTuNguon,
                    ChuHan,
                    PhienAm,
                    TuLoai,
                    NghiaTiengVietThamChieu

                FROM dbo.TuVungHSKChuan

                WHERE MaCapDo = 4

                ORDER BY
                    SoThuTuNguon,
                    MaTuHSK
                """
            )

            print(
                "Tong muc HSK4:",
                len(
                    vocab_rows
                ),
            )

            if (
                len(vocab_rows)
                != EXPECTED_HSK4_VOCAB
            ):

                raise RuntimeError(
                    "TuVungHSKChuan HSK4 "
                    "khong con dung 1000 muc."
                )

            if any(
                int(
                    row[
                        "MaCapDo"
                    ]
                )
                != EXPECTED_LEVEL
                for row in vocab_rows
            ):

                raise RuntimeError(
                    "Co row MaCapDo != 4."
                )

            blank_hanzi = [
                row[
                    "MaMucNoiBo"
                ]
                for row in vocab_rows
                if not clean(
                    row.get(
                        "ChuHan"
                    )
                )
            ]

            if blank_hanzi:

                raise RuntimeError(
                    "Co ChuHan rong: "
                    + ", ".join(
                        blank_hanzi[:20]
                    )
                )

            snapshot_hash = (
                build_snapshot_hash(
                    vocab_rows
                )
            )

            print(
                "HSK4 VOCAB SNAPSHOT SHA256:"
            )

            print(
                snapshot_hash
            )

            print(
                "PASS: 1000/1000 muc."
            )

            # ==================================================
            # 1C. DOC ChuHan HIEN CO
            # ==================================================

            print(
                "\n[3] DOC dbo.ChuHan HSK1-3"
            )

            chu_han_columns = get_columns(
                cursor,
                "ChuHan",
            )

            required_chuhan_columns = {
                "MaChuHan",
                "MaBaiHoc",
                "MaBoThu",
                "KyTu",
                "Pinyin",
                "NghiaTiengViet",
                "SoNet",
            }

            missing = (
                required_chuhan_columns
                - chu_han_columns
            )

            if missing:

                raise RuntimeError(
                    "dbo.ChuHan thieu cot: "
                    + ", ".join(
                        sorted(
                            missing
                        )
                    )
                )

            existing_rows = fetch_all(
                cursor,
                """
                SELECT
                    ch.MaChuHan,
                    ch.KyTu,
                    ch.Pinyin,
                    ch.NghiaTiengViet,
                    ch.SoNet,
                    ch.MaBoThu,

                    ch.MaBaiHoc,

                    b.MaKhoaHoc,
                    b.SoThuTuBai,

                    k.MaCapDo

                FROM dbo.ChuHan AS ch

                INNER JOIN dbo.BaiHoc AS b
                    ON b.MaBaiHoc = ch.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS k
                    ON k.MaKhoaHoc = b.MaKhoaHoc

                WHERE b.MaKhoaHoc IN (1, 2, 3)

                ORDER BY
                    ch.MaChuHan
                """
            )

            print(
                "Tong dong ChuHan HSK1-3:",
                len(
                    existing_rows
                ),
            )

            existing_by_char = (
                defaultdict(list)
            )

            for row in existing_rows:

                char = clean(
                    row.get(
                        "KyTu"
                    )
                )

                if not char:
                    continue

                existing_by_char[
                    char
                ].append(
                    row
                )

            print(
                "KyTu distinct HSK1-3:",
                len(
                    existing_by_char
                ),
            )

    # ======================================================
    # 4. TACH CHU TU 1000 TU
    # ======================================================

    print(
        "\n[4] TACH KY TU HAN TU 1000 TU"
    )

    char_info = {}

    char_order = []

    char_position = 0

    for vocab in vocab_rows:

        source_chars = extract_hanzi(
            vocab[
                "ChuHan"
            ]
        )

        if not source_chars:

            raise RuntimeError(
                "Khong tach duoc Hanzi tu "
                f"{vocab['MaMucNoiBo']} | "
                f"{vocab['ChuHan']}"
            )

        for char in source_chars:

            if char not in char_info:

                char_position += 1

                char_info[
                    char
                ] = {
                    "ThuTuXuatHienDau":
                        char_position,

                    "MaTuHSKDauTien":
                        clean(
                            vocab[
                                "MaTuHSK"
                            ]
                        ),

                    "MaMucNoiBoDauTien":
                        clean(
                            vocab[
                                "MaMucNoiBo"
                            ]
                        ),

                    "SoThuTuNguonDauTien":
                        clean(
                            vocab[
                                "SoThuTuNguon"
                            ]
                        ),

                    "TuVungDaiDien":
                        clean(
                            vocab[
                                "ChuHan"
                            ]
                        ),

                    "PinyinTuDaiDien":
                        clean(
                            vocab[
                                "PhienAm"
                            ]
                        ),

                    "NghiaTuDaiDien":
                        clean(
                            vocab.get(
                                "NghiaTiengVietThamChieu"
                            )
                        ),

                    "MaMucNoiBo":
                        [],

                    "TuVung":
                        [],
                }

                char_order.append(
                    char
                )

            char_info[
                char
            ][
                "MaMucNoiBo"
            ].append(
                clean(
                    vocab[
                        "MaMucNoiBo"
                    ]
                )
            )

            char_info[
                char
            ][
                "TuVung"
            ].append(
                clean(
                    vocab[
                        "ChuHan"
                    ]
                )
            )

    print(
        "Tong KyTu unique tu HSK4:",
        len(
            char_order
        ),
    )

    # ======================================================
    # 5. DOI CHIEU SQL
    # ======================================================

    print(
        "\n[5] DOI CHIEU VOI ChuHan HSK1-3"
    )

    all_rows = []

    existing_output = []

    new_output = []

    for index, char in enumerate(
        char_order,
        start=1,
    ):

        info = char_info[
            char
        ]

        sql_matches = (
            existing_by_char.get(
                char,
                []
            )
        )

        if sql_matches:

            status = "DA_CO_SQL"

            action = (
                "TAI_SU_DUNG_NOI_DUNG_THAM_KHAO"
            )

            ma_chu_han = join_unique(
                [
                    row[
                        "MaChuHan"
                    ]
                    for row
                    in sql_matches
                ],
                ",",
            )

            courses = join_unique(
                [
                    f"HSK{row['MaCapDo']}"
                    for row
                    in sql_matches
                ],
                ",",
            )

            lessons = join_unique(
                [
                    str(
                        row[
                            "MaBaiHoc"
                        ]
                    )
                    for row
                    in sql_matches
                ],
                ",",
            )

            pinyin_sql = join_unique(
                [
                    row[
                        "Pinyin"
                    ]
                    for row
                    in sql_matches
                ]
            )

            meaning_sql = join_unique(
                [
                    row[
                        "NghiaTiengViet"
                    ]
                    for row
                    in sql_matches
                ]
            )

            stroke_sql = join_unique(
                [
                    row[
                        "SoNet"
                    ]
                    for row
                    in sql_matches
                ],
                ",",
            )

            radical_sql = join_unique(
                [
                    row[
                        "MaBoThu"
                    ]
                    for row
                    in sql_matches
                ],
                ",",
            )

        else:

            status = "MOI_HSK4"

            action = (
                "CAN_CHUAN_BI_NOI_DUNG_MOI"
            )

            ma_chu_han = ""
            courses = ""
            lessons = ""
            pinyin_sql = ""
            meaning_sql = ""
            stroke_sql = ""
            radical_sql = ""

        unique_codes = list(
            dict.fromkeys(
                info[
                    "MaMucNoiBo"
                ]
            )
        )

        unique_words = list(
            dict.fromkeys(
                info[
                    "TuVung"
                ]
            )
        )

        row = {
            "MaChuHanTam":
                f"H4-{index:04d}",

            "KyTu":
                char,

            "ThuTuXuatHienDau":
                info[
                    "ThuTuXuatHienDau"
                ],

            "MaTuHSKDauTien":
                info[
                    "MaTuHSKDauTien"
                ],

            "MaMucNoiBoDauTien":
                info[
                    "MaMucNoiBoDauTien"
                ],

            "SoThuTuNguonDauTien":
                info[
                    "SoThuTuNguonDauTien"
                ],

            "TuVungDaiDien":
                info[
                    "TuVungDaiDien"
                ],

            "PinyinTuDaiDien":
                info[
                    "PinyinTuDaiDien"
                ],

            "NghiaTuDaiDien":
                info[
                    "NghiaTuDaiDien"
                ],

            "SoTuHSK4ChuaKyTu":
                len(
                    unique_codes
                ),

            "CacMaMucNoiBo":
                " | ".join(
                    unique_codes
                ),

            "CacTuHSK4ChuaKyTu":
                " | ".join(
                    unique_words
                ),

            "DaCoTrongSQL":
                (
                    "CO"
                    if sql_matches
                    else "KHONG"
                ),

            "SoDongChuHanSQL":
                len(
                    sql_matches
                ),

            "MaChuHanDaCo":
                ma_chu_han,

            "KhoaHocDaCo":
                courses,

            "BaiHocDaCo":
                lessons,

            # CHI THAM KHAO.
            # Khong tu dong coi la Pinyin/Nghia HSK4 cuoi.
            "PinyinSQLThamKhao":
                pinyin_sql,

            "NghiaSQLThamKhao":
                meaning_sql,

            "SoNetSQLThamKhao":
                stroke_sql,

            "MaBoThuSQLThamKhao":
                radical_sql,

            "HanhDongDeXuat":
                action,

            "TrangThai":
                status,
        }

        all_rows.append(
            row
        )

        if sql_matches:

            existing_output.append(
                row
            )

        else:

            new_output.append(
                row
            )

    # ======================================================
    # 6. KIEM TRA TAP HOP
    # ======================================================

    print(
        "Da co HSK1-3:",
        len(
            existing_output
        ),
    )

    print(
        "Moi HSK4:",
        len(
            new_output
        ),
    )

    if (
        len(
            existing_output
        )
        + len(
            new_output
        )
        != len(
            all_rows
        )
    ):

        raise RuntimeError(
            "Phan loai existing/new "
            "khong khop tong."
        )

    if (
        len({
            row["KyTu"]
            for row in all_rows
        })
        != len(
            all_rows
        )
    ):

        raise RuntimeError(
            "KyTu trong output bi trung."
        )

    if (
        len({
            row["MaChuHanTam"]
            for row in all_rows
        })
        != len(
            all_rows
        )
    ):

        raise RuntimeError(
            "MaChuHanTam bi trung."
        )

    print(
        "PASS: moi KyTu chi co 1 dong."
    )

    print(
        "PASS: existing + new = tong."
    )

    # ======================================================
    # 7. GHI FILE
    # ======================================================

    print(
        "\n[6] GHI FILE PREVIEW"
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        ALL_FILE,
        all_rows,
    )

    write_csv(
        EXISTING_FILE,
        existing_output,
    )

    write_csv(
        NEW_FILE,
        new_output,
    )

    # ======================================================
    # 8. HASH OUTPUT
    # ======================================================

    all_hash = hashlib.sha256(
        ALL_FILE.read_bytes()
    ).hexdigest()

    existing_hash = hashlib.sha256(
        EXISTING_FILE.read_bytes()
    ).hexdigest()

    new_hash = hashlib.sha256(
        NEW_FILE.read_bytes()
    ).hexdigest()

    # ======================================================
    # 9. SUMMARY
    # ======================================================

    summary = {
        "status":
            "PASS",

        "buoc":
            18,

        "nguon_pham_vi":
            (
                "dbo.TuVungHSKChuan "
                "MaCapDo=4 / GF0025-2021"
            ),

        "tong_tu_vung_hsk4":
            len(
                vocab_rows
            ),

        "tong_ky_tu_unique":
            len(
                all_rows
            ),

        "da_co_trong_sql_hsk1_3":
            len(
                existing_output
            ),

        "moi_hsk4":
            len(
                new_output
            ),

        "hsk4_vocab_snapshot_sha256":
            snapshot_hash,

        "all_characters_sha256":
            all_hash,

        "existing_sha256":
            existing_hash,

        "new_candidates_sha256":
            new_hash,

        "da_lam_giau_unihan":
            False,

        "da_gan_bo_thu":
            False,

        "da_chot_pinyin":
            False,

        "da_chot_nghia":
            False,

        "da_gan_bai_hoc":
            False,

        "da_ghi_sql":
            False,

        "ghi_chu":
            (
                "KyTu HSK4 duoc trich tu "
                "1000 muc tu vung GF0025 HSK4, "
                "theo cung chien luoc pipeline "
                "cac cap truoc. "
                "PinyinTuDaiDien chi la Pinyin cua TU, "
                "khong phai tu dong la Pinyin cua KY TU."
            ),
    }

    if SUMMARY_FILE.exists():

        raise FileExistsError(
            f"Summary da ton tai:\n"
            f"{SUMMARY_FILE}"
        )

    SUMMARY_FILE.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # 10. PREVIEW MOT SO DONG
    # ======================================================

    print(
        "\n[7] PREVIEW"
    )

    print(
        "\n--- 10 KY TU DA CO ---"
    )

    for row in (
        existing_output[:10]
    ):

        print(
            row["KyTu"],
            "|",
            row["TuVungDaiDien"],
            "|",
            row["KhoaHocDaCo"],
        )

    print(
        "\n--- 20 KY TU MOI DAU ---"
    )

    for row in (
        new_output[:20]
    ):

        print(
            row["MaChuHanTam"],
            "|",
            row["KyTu"],
            "|",
            row["TuVungDaiDien"],
            "|",
            row["PinyinTuDaiDien"],
        )

    # ======================================================
    # 11. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "TAO TAP CHU HAN HSK4 THANH CONG"
    )

    print("=" * 80)

    print(
        "Tu vung HSK4:",
        len(
            vocab_rows
        ),
        "/ 1000",
    )

    print(
        "Tong KyTu unique:",
        len(
            all_rows
        ),
    )

    print(
        "Da co trong ChuHan HSK1-3:",
        len(
            existing_output
        ),
    )

    print(
        "KyTu moi can xu ly HSK4:",
        len(
            new_output
        ),
    )

    print(
        "\nALL:"
    )

    print(
        " ",
        ALL_FILE,
    )

    print(
        "SHA256:"
    )

    print(
        all_hash
    )

    print(
        "\nEXISTING:"
    )

    print(
        " ",
        EXISTING_FILE,
    )

    print(
        "SHA256:"
    )

    print(
        existing_hash
    )

    print(
        "\nNEW:"
    )

    print(
        " ",
        NEW_FILE,
    )

    print(
        "SHA256:"
    )

    print(
        new_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY_FILE,
    )

    print(
        "\nCHUA GAN PINYIN KY TU CUOI."
    )

    print(
        "CHUA GAN NGHIA KY TU CUOI."
    )

    print(
        "CHUA GAN BO THU."
    )

    print(
        "CHUA GAN BAI HOC."
    )

    print(
        "KHONG THAY DOI SQL."
    )

    print("=" * 80)


if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print(
            "\nLOI:"
        )

        print(
            error
        )

        raise SystemExit(1)