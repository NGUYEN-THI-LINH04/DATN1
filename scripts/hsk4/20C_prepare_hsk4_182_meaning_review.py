# -*- coding: utf-8 -*-

"""
BUOC 20C - TAO GOI REVIEW 182 NGHIA CHU HAN HSK4

INPUT:
1. hanzi_hsk4_300_cvdict_rebuilt.csv
2. hanzi_hsk4_300_enriched_sources.csv

MUC DICH:
- Lay dung 182 chu ma o Buoc 20 chua co nghia.
- KHONG tu dong phe duyet 60 nghia CVDICT vua bo sung.
- Gom day du context tu:
    + GF0025
    + CC-CEDICT
    + CVDICT
    + Unihan
    + Make Me a Hanzi
    + ngu canh tu vung HSK4
- Tao 1 file review gon de kiem duyet nghia.

KHONG:
- ghi SQL
- gan bai hoc
- tao audio
- sua file cu
"""

import csv
import hashlib
import json

from collections import Counter
from pathlib import Path


# ==========================================================
# 1. CONFIG
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]


DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)


SOURCE_20B = (
    DATA_DIR
    / "hanzi_hsk4_300_cvdict_rebuilt.csv"
)


SOURCE_19 = (
    DATA_DIR
    / "hanzi_hsk4_300_enriched_sources.csv"
)


OUTPUT = (
    DATA_DIR
    / "hanzi_hsk4_182_meaning_review_pack.csv"
)


SUMMARY = (
    DATA_DIR
    / "hanzi_hsk4_182_meaning_review_summary.json"
)


EXPECTED_20B_SHA256 = (
    "6c6530445117477bb27a2222fd358f30"
    "ee74f9c6ee54c3b9bbf65a00c8f68712"
)


EXPECTED_19_SHA256 = (
    "5f85c0e6c74693e7a411e5e8531cad82"
    "4ff2742a70e2e4933a089847ada45c8d"
)


EXPECTED_TOTAL = 300
EXPECTED_REVIEW = 182


# ==========================================================
# 2. OUTPUT
# ==========================================================

OUTPUT_FIELDS = [

    # ------------------------------------------------------
    # ID
    # ------------------------------------------------------

    "MaChuHanTam",
    "KyTu",

    # ------------------------------------------------------
    # PINYIN
    # ------------------------------------------------------

    "PinyinDeXuat",
    "TrangThaiPinyin",
    "CanKiemTraPinyin",

    "PinyinUnihanRaw",
    "PinyinMakeMeAHanzi",
    "PinyinGFDon",
    "CacCachDocCEDICT",

    # ------------------------------------------------------
    # NGU CANH HSK4
    # ------------------------------------------------------

    "TuVungDaiDien",
    "PinyinTuDaiDien",
    "NghiaTuDaiDien",

    "CacTuHSK4ChuaKyTu",

    # ------------------------------------------------------
    # GF0025
    # ------------------------------------------------------

    "SoMucGFDon",
    "CapDoGFDon",
    "NghiaGFDon",

    # ------------------------------------------------------
    # CC-CEDICT
    # ------------------------------------------------------

    "SoMucCEDICT",
    "NghiaAnhCEDICT",

    # ------------------------------------------------------
    # MAKE ME A HANZI
    # ------------------------------------------------------

    "DefinitionEnglishMakeMeAHanzi",

    # ------------------------------------------------------
    # CVDICT
    # ------------------------------------------------------

    "SoMucCVDICTFile",
    "SoMucCVDICTKhopPinyin",
    "CacCachDocCVDICTFile",

    "UngVienNghiaCVDICTKhopPinyin",
    "TatCaUngVienCVDICT",

    "NghiaTiengVietSauCVDICT",
    "NguonNghiaSauCVDICT",
    "TrangThaiDoiChieuCVDICT",

    # ------------------------------------------------------
    # REVIEW CUOI - DE TRONG
    # ------------------------------------------------------

    "NghiaTiengVietReview",
    "NguonReview",
    "TrangThaiReview",
    "GhiChuReview",
]


# ==========================================================
# 3. HELPERS
# ==========================================================

def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(
                block
            )

    return digest.hexdigest()


def read_csv(path):

    if not path.is_file():

        raise FileNotFoundError(
            f"Khong tim thay:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        fields = (
            reader.fieldnames
            or []
        )

        rows = list(
            reader
        )

    return fields, rows


def write_csv(
    path,
    rows,
    fields,
):

    if path.exists():

        raise FileExistsError(
            f"File da ton tai:\n"
            f"{path}\n"
            "Khong tu dong ghi de."
        )

    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# ==========================================================
# 4. MAIN
# ==========================================================

def main():

    print(
        "=" * 80
    )

    print(
        "BUOC 20C - TAO GOI REVIEW "
        "182 NGHIA CHU HAN HSK4"
    )

    print(
        "=" * 80
    )

    print(
        "CHI DOC CSV - KHONG GHI SQL"
    )

    # ======================================================
    # [1] LOCK HASH
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT"
    )

    hash_20b = (
        sha256_file(
            SOURCE_20B
        )
    )

    hash_19 = (
        sha256_file(
            SOURCE_19
        )
    )

    print(
        "STEP20B SHA256:"
    )

    print(
        hash_20b
    )

    print(
        "STEP19 SHA256:"
    )

    print(
        hash_19
    )

    if (
        hash_20b
        != EXPECTED_20B_SHA256
    ):

        raise RuntimeError(
            "File Buoc 20B da thay doi."
        )

    if (
        hash_19
        != EXPECTED_19_SHA256
    ):

        raise RuntimeError(
            "File Buoc 19 da thay doi."
        )

    print(
        "PASS: snapshot hop le."
    )

    # ======================================================
    # [2] READ
    # ======================================================

    print(
        "\n[2] DOC DU LIEU"
    )

    fields20b, rows20b = (
        read_csv(
            SOURCE_20B
        )
    )

    fields19, rows19 = (
        read_csv(
            SOURCE_19
        )
    )

    if (
        len(
            rows20b
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Buoc 20B khong dung 300 dong."
        )

    if (
        len(
            rows19
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Buoc 19 khong dung 300 dong."
        )

    required20b = {

        "MaChuHanTam",
        "KyTu",

        "PinyinDeXuat",
        "TrangThaiPinyin",
        "CanKiemTraPinyin",

        "PinyinUnihanRaw",
        "PinyinMakeMeAHanzi",
        "PinyinGFDon",
        "CacCachDocCEDICT",

        "TuVungDaiDien",
        "PinyinTuDaiDien",
        "NghiaTuDaiDien",
        "CacTuHSK4ChuaKyTu",

        "SoMucGFDon",
        "CapDoGFDon",
        "NghiaGFDon",

        "SoMucCEDICT",
        "NghiaAnhCEDICT",

        "SoMucCVDICTFile",
        "SoMucCVDICTKhopPinyin",
        "CacCachDocCVDICTFile",

        "UngVienNghiaCVDICTKhopPinyin",
        "TatCaUngVienCVDICT",

        "NghiaTiengVietDeXuat",

        "NghiaTiengVietSauCVDICT",
        "NguonNghiaSauCVDICT",
        "TrangThaiDoiChieuCVDICT",
    }

    missing20b = (
        required20b
        - set(
            fields20b
        )
    )

    if missing20b:

        raise RuntimeError(
            "Buoc 20B thieu cot: "
            + ", ".join(
                sorted(
                    missing20b
                )
            )
        )

    required19 = {

        "MaChuHanTam",
        "KyTu",
        "DefinitionEnglishMakeMeAHanzi",
    }

    missing19 = (
        required19
        - set(
            fields19
        )
    )

    if missing19:

        raise RuntimeError(
            "Buoc 19 thieu cot: "
            + ", ".join(
                sorted(
                    missing19
                )
            )
        )

    print(
        "Buoc 20B:",
        len(
            rows20b
        ),
    )

    print(
        "Buoc 19:",
        len(
            rows19
        ),
    )

    # ======================================================
    # [3] MAP STEP19
    # ======================================================

    print(
        "\n[3] DOI CHIEU BUOC 19 <-> 20B"
    )

    step19_by_id = {}

    for row in rows19:

        temp_id = clean(
            row[
                "MaChuHanTam"
            ]
        )

        if temp_id in step19_by_id:

            raise RuntimeError(
                f"Buoc 19 trung ID: "
                f"{temp_id}"
            )

        step19_by_id[
            temp_id
        ] = row

    for row in rows20b:

        temp_id = clean(
            row[
                "MaChuHanTam"
            ]
        )

        char = clean(
            row[
                "KyTu"
            ]
        )

        old = step19_by_id.get(
            temp_id
        )

        if old is None:

            raise RuntimeError(
                f"Khong tim thay {temp_id} "
                "trong Buoc 19."
            )

        if (
            clean(
                old[
                    "KyTu"
                ]
            )
            != char
        ):

            raise RuntimeError(
                f"KyTu khong khop tai "
                f"{temp_id}."
            )

    print(
        "PASS: 300/300 mapping khop."
    )

    # ======================================================
    # [4] CHON 182 CHU CAN REVIEW NGHIA
    # ======================================================

    print(
        "\n[4] CHON 182 CHU CAN REVIEW NGHIA"
    )

    review_source_rows = [
        row
        for row in rows20b

        # Day chinh la 182 chu chua co nghia
        # truoc khi CVDICT duoc ap dung.
        if not clean(
            row[
                "NghiaTiengVietDeXuat"
            ]
        )
    ]

    print(
        "Tong review:",
        len(
            review_source_rows
        ),
    )

    if (
        len(
            review_source_rows
        )
        != EXPECTED_REVIEW
    ):

        raise RuntimeError(
            "So dong review khong phai 182."
        )

    # ======================================================
    # [5] TAO REVIEW PACK
    # ======================================================

    print(
        "\n[5] TAO REVIEW PACK"
    )

    output_rows = []

    status_counts = Counter()

    pinyin_review_count = 0

    has_cvdict_proposal = 0
    missing_after_cvdict = 0

    for row in review_source_rows:

        temp_id = clean(
            row[
                "MaChuHanTam"
            ]
        )

        source19 = (
            step19_by_id[
                temp_id
            ]
        )

        status = clean(
            row[
                "TrangThaiDoiChieuCVDICT"
            ]
        )

        status_counts[
            status
        ] += 1

        if (
            clean(
                row[
                    "CanKiemTraPinyin"
                ]
            )
            == "CO"
        ):

            pinyin_review_count += 1

        meaning_after = clean(
            row[
                "NghiaTiengVietSauCVDICT"
            ]
        )

        if meaning_after:

            has_cvdict_proposal += 1

        else:

            missing_after_cvdict += 1

        output_rows.append({

            # ----------------------------------------------
            # ID
            # ----------------------------------------------

            "MaChuHanTam":
                temp_id,

            "KyTu":
                clean(
                    row[
                        "KyTu"
                    ]
                ),

            # ----------------------------------------------
            # PINYIN
            # ----------------------------------------------

            "PinyinDeXuat":
                clean(
                    row[
                        "PinyinDeXuat"
                    ]
                ),

            "TrangThaiPinyin":
                clean(
                    row[
                        "TrangThaiPinyin"
                    ]
                ),

            "CanKiemTraPinyin":
                clean(
                    row[
                        "CanKiemTraPinyin"
                    ]
                ),

            "PinyinUnihanRaw":
                clean(
                    row[
                        "PinyinUnihanRaw"
                    ]
                ),

            "PinyinMakeMeAHanzi":
                clean(
                    row[
                        "PinyinMakeMeAHanzi"
                    ]
                ),

            "PinyinGFDon":
                clean(
                    row[
                        "PinyinGFDon"
                    ]
                ),

            "CacCachDocCEDICT":
                clean(
                    row[
                        "CacCachDocCEDICT"
                    ]
                ),

            # ----------------------------------------------
            # HSK4 CONTEXT
            # ----------------------------------------------

            "TuVungDaiDien":
                clean(
                    row[
                        "TuVungDaiDien"
                    ]
                ),

            "PinyinTuDaiDien":
                clean(
                    row[
                        "PinyinTuDaiDien"
                    ]
                ),

            "NghiaTuDaiDien":
                clean(
                    row[
                        "NghiaTuDaiDien"
                    ]
                ),

            "CacTuHSK4ChuaKyTu":
                clean(
                    row[
                        "CacTuHSK4ChuaKyTu"
                    ]
                ),

            # ----------------------------------------------
            # GF
            # ----------------------------------------------

            "SoMucGFDon":
                clean(
                    row[
                        "SoMucGFDon"
                    ]
                ),

            "CapDoGFDon":
                clean(
                    row[
                        "CapDoGFDon"
                    ]
                ),

            "NghiaGFDon":
                clean(
                    row[
                        "NghiaGFDon"
                    ]
                ),

            # ----------------------------------------------
            # CEDICT
            # ----------------------------------------------

            "SoMucCEDICT":
                clean(
                    row[
                        "SoMucCEDICT"
                    ]
                ),

            "NghiaAnhCEDICT":
                clean(
                    row[
                        "NghiaAnhCEDICT"
                    ]
                ),

            # ----------------------------------------------
            # MMAH
            # ----------------------------------------------

            "DefinitionEnglishMakeMeAHanzi":
                clean(
                    source19[
                        "DefinitionEnglishMakeMeAHanzi"
                    ]
                ),

            # ----------------------------------------------
            # CVDICT
            # ----------------------------------------------

            "SoMucCVDICTFile":
                clean(
                    row[
                        "SoMucCVDICTFile"
                    ]
                ),

            "SoMucCVDICTKhopPinyin":
                clean(
                    row[
                        "SoMucCVDICTKhopPinyin"
                    ]
                ),

            "CacCachDocCVDICTFile":
                clean(
                    row[
                        "CacCachDocCVDICTFile"
                    ]
                ),

            "UngVienNghiaCVDICTKhopPinyin":
                clean(
                    row[
                        "UngVienNghiaCVDICTKhopPinyin"
                    ]
                ),

            "TatCaUngVienCVDICT":
                clean(
                    row[
                        "TatCaUngVienCVDICT"
                    ]
                ),

            "NghiaTiengVietSauCVDICT":
                meaning_after,

            "NguonNghiaSauCVDICT":
                clean(
                    row[
                        "NguonNghiaSauCVDICT"
                    ]
                ),

            "TrangThaiDoiChieuCVDICT":
                status,

            # ----------------------------------------------
            # MANUAL REVIEW
            # ----------------------------------------------

            "NghiaTiengVietReview":
                "",

            "NguonReview":
                "",

            "TrangThaiReview":
                "CHO_REVIEW",

            "GhiChuReview":
                "",
        })

    # ======================================================
    # [6] VALIDATE
    # ======================================================

    print(
        "\n[6] KIEM TRA KET QUA"
    )

    if (
        len(
            output_rows
        )
        != EXPECTED_REVIEW
    ):

        raise RuntimeError(
            "Output khong dung 182."
        )

    ids = [
        row[
            "MaChuHanTam"
        ]
        for row
        in output_rows
    ]

    chars = [
        row[
            "KyTu"
        ]
        for row
        in output_rows
    ]

    if (
        len(
            set(
                ids
            )
        )
        != EXPECTED_REVIEW
    ):

        raise RuntimeError(
            "Output trung MaChuHanTam."
        )

    if (
        len(
            set(
                chars
            )
        )
        != EXPECTED_REVIEW
    ):

        raise RuntimeError(
            "Output trung KyTu."
        )

    print(
        "PASS: 182 ID duy nhat."
    )

    print(
        "PASS: 182 KyTu duy nhat."
    )

    print(
        "\nPhan loai CVDICT:"
    )

    for key, value in sorted(
        status_counts.items()
    ):

        print(
            f"  {key}: {value}"
        )

    print(
        "\nDa co de xuat CVDICT:",
        has_cvdict_proposal,
    )

    print(
        "Van chua co nghia:",
        missing_after_cvdict,
    )

    print(
        "Trong 182 co Pinyin can review:",
        pinyin_review_count,
    )

    # Theo output 20B hien tai:
    # 60 da co nghia CVDICT
    # 122 van chua co nghia
    if (
        has_cvdict_proposal
        != 60
    ):

        raise RuntimeError(
            "So dong co de xuat CVDICT "
            "khong con bang 60."
        )

    if (
        missing_after_cvdict
        != 122
    ):

        raise RuntimeError(
            "So dong thieu nghia "
            "khong con bang 122."
        )

    # ======================================================
    # [7] WRITE
    # ======================================================

    print(
        "\n[7] GHI FILE"
    )

    write_csv(
        OUTPUT,
        output_rows,
        OUTPUT_FIELDS,
    )

    output_hash = (
        sha256_file(
            OUTPUT
        )
    )

    # ======================================================
    # [8] SUMMARY
    # ======================================================

    summary = {

        "status":
            "PASS",

        "buoc":
            "20C",

        "tong_review":
            len(
                output_rows
            ),

        "co_de_xuat_cvdict":
            has_cvdict_proposal,

        "van_thieu_nghia":
            missing_after_cvdict,

        "pinyin_can_review_trong_182":
            pinyin_review_count,

        "cvdict_status_counts":
            dict(
                status_counts
            ),

        "source_20B":
            str(
                SOURCE_20B
            ),

        "source_20B_sha256":
            hash_20b,

        "source_19":
            str(
                SOURCE_19
            ),

        "source_19_sha256":
            hash_19,

        "output":
            str(
                OUTPUT
            ),

        "output_sha256":
            output_hash,

        "da_review":
            False,

        "ghi_sql":
            False,

        "gan_bai_hoc":
            False,

        "tao_audio":
            False,
    }

    if SUMMARY.exists():

        raise FileExistsError(
            f"Summary da ton tai:\n"
            f"{SUMMARY}"
        )

    SUMMARY.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # [9] PREVIEW
    # ======================================================

    print(
        "\n[8] PREVIEW 20 DONG DAU"
    )

    for row in output_rows[
        :20
    ]:

        print(
            row[
                "MaChuHanTam"
            ],
            "|",
            row[
                "KyTu"
            ],
            "|",
            row[
                "PinyinDeXuat"
            ],
            "| CVDICT:",
            row[
                "TrangThaiDoiChieuCVDICT"
            ],
            "| Current:",
            row[
                "NghiaTiengVietSauCVDICT"
            ],
        )

    # ======================================================
    # FINAL
    # ======================================================

    print(
        "\n"
        + "=" * 80
    )

    print(
        "BUOC 20C HOAN THANH"
    )

    print(
        "=" * 80
    )

    print(
        "Tong chu can review nghia:",
        len(
            output_rows
        ),
    )

    print(
        "Co de xuat CVDICT:",
        has_cvdict_proposal,
    )

    print(
        "Con thieu nghia:",
        missing_after_cvdict,
    )

    print(
        "Pinyin can review trong pack:",
        pinyin_review_count,
    )

    print(
        "\nOUTPUT:"
    )

    print(
        " ",
        OUTPUT
    )

    print(
        "SHA256:"
    )

    print(
        output_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY
    )

    print(
        "\nKHONG GHI SQL."
    )

    print(
        "KHONG GAN BAI HOC."
    )

    print(
        "KHONG TAO AUDIO."
    )

    print(
        "=" * 80
    )


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