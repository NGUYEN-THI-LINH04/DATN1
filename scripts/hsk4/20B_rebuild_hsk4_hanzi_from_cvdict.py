# -*- coding: utf-8 -*-

"""
BUOC 20B - DOI CHIEU 300 CHU HAN HSK4 VOI CVDICT.u8

INPUT:
    hanzi_hsk4_300_pinyin_meaning_draft.csv

NGUON:
    D:\\DATN1\\data_sources\\cvdict\\CVDICT.u8

NGUYEN TAC:
1. Khoa SHA256 output Buoc 20.
2. Khoa SHA256 CVDICT.u8.
3. Giu nguyen cac nghia da co tu Buoc 20.
4. Chi bo sung nghia CVDICT khi:
       - KyTu tim thay trong CVDICT
       - PinyinDeXuat da co
       - co DUNG 1 ung vien nghia khop Pinyin
5. Neu co nhieu muc cung Pinyin:
       -> KHONG tu dong chon.
6. Neu Pinyin dang can review:
       -> CVDICT chi lam du lieu tham khao.
7. KHONG GHI SQL.
8. KHONG GAN BAI HOC.
9. KHONG TAO AUDIO.
"""

import csv
import hashlib
import json
import re
import unicodedata

from collections import Counter
from collections import defaultdict
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


SOURCE = (
    DATA_DIR
    / "hanzi_hsk4_300_pinyin_meaning_draft.csv"
)


CVDICT = (
    ROOT
    / "data_sources"
    / "cvdict"
    / "CVDICT.u8"
)


OUTPUT = (
    DATA_DIR
    / "hanzi_hsk4_300_cvdict_rebuilt.csv"
)


REVIEW = (
    DATA_DIR
    / "hanzi_hsk4_300_after_cvdict_review.csv"
)


SUMMARY = (
    DATA_DIR
    / "hanzi_hsk4_300_cvdict_summary.json"
)


EXPECTED_SOURCE_SHA256 = (
    "337f86d394a1fa5986439c1b4493bdd"
    "0153088414487bbd2231b89a89b6dadfb"
)


EXPECTED_CVDICT_SHA256 = (
    "5dd696ba6a2ad1438a38341e2ec11893"
    "706d2918e93ad7a8222b57514e248c6b"
)


EXPECTED_TOTAL = 300


# ==========================================================
# 2. HELPER
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
            f"Khong tim thay file:\n{path}"
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


def unique_keep_order(values):

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

    return result


# ==========================================================
# 3. PINYIN NORMALIZATION
# ==========================================================

TONE_MAP = {

    "ā": ("a", "1"),
    "á": ("a", "2"),
    "ǎ": ("a", "3"),
    "à": ("a", "4"),

    "ē": ("e", "1"),
    "é": ("e", "2"),
    "ě": ("e", "3"),
    "è": ("e", "4"),

    "ī": ("i", "1"),
    "í": ("i", "2"),
    "ǐ": ("i", "3"),
    "ì": ("i", "4"),

    "ō": ("o", "1"),
    "ó": ("o", "2"),
    "ǒ": ("o", "3"),
    "ò": ("o", "4"),

    "ū": ("u", "1"),
    "ú": ("u", "2"),
    "ǔ": ("u", "3"),
    "ù": ("u", "4"),

    "ǖ": ("v", "1"),
    "ǘ": ("v", "2"),
    "ǚ": ("v", "3"),
    "ǜ": ("v", "4"),

    "ü": ("v", ""),

    "ń": ("n", "2"),
    "ň": ("n", "3"),
    "ǹ": ("n", "4"),

    "ḿ": ("m", "2"),
}


def normalize_one_syllable(value):
    """
    Vi du:

        ǎi  -> ai3
        à   -> a4
        shi4 -> shi4
        lü4 -> lv4
        lu:4 -> lv4
    """

    text = clean(
        value
    ).lower()

    if not text:
        return ""

    text = (
        text
        .replace("u:", "v")
        .replace("ü", "v")
        .replace("'", "")
        .replace("’", "")
    )

    # ----------------------------------------------
    # Da la pinyin number.
    # ----------------------------------------------

    match = re.fullmatch(
        r"([a-zv]+)([1-5])",
        text,
    )

    if match:

        return (
            match.group(1)
            + match.group(2)
        )

    tone = ""

    output = []

    for char in text:

        if char in TONE_MAP:

            base, found_tone = (
                TONE_MAP[
                    char
                ]
            )

            output.append(
                base
            )

            if found_tone:
                tone = found_tone

            continue

        decomposed = (
            unicodedata.normalize(
                "NFD",
                char,
            )
        )

        base = "".join(
            item
            for item in decomposed
            if (
                unicodedata.category(
                    item
                )
                != "Mn"
            )
        )

        base = re.sub(
            r"[^a-zv]",
            "",
            base,
        )

        if base:

            output.append(
                base
            )

    base_text = "".join(
        output
    )

    if not base_text:
        return ""

    return (
        base_text
        + tone
    )


def normalize_pinyin(value):
    """
    Dung de so sanh.

    Vi du:

        "shí"       -> shi2
        "shi2"      -> shi2
        "lü4"       -> lv4

    Voi nhieu am tiet:
        "zhong1 guo2"
        -> zhong1guo2
    """

    text = clean(
        value
    )

    if not text:
        return ""

    parts = re.split(
        r"[\s·\-]+",
        text,
    )

    normalized = []

    for part in parts:

        part = clean(
            part
        )

        if not part:
            continue

        item = normalize_one_syllable(
            part
        )

        if item:

            normalized.append(
                item
            )

    return "".join(
        normalized
    )


# ==========================================================
# 4. CVDICT PARSER
# ==========================================================

def parse_cvdict_meaning(raw):
    """
    Phan sau:
        /nghia 1/nghia 2/nghia 3/

    chuyen thanh:
        nghia 1; nghia 2; nghia 3
    """

    text = clean(
        raw
    )

    if not text:
        return ""

    pieces = [
        clean(item)
        for item
        in text.split("/")
    ]

    pieces = [
        item
        for item
        in pieces
        if item
    ]

    pieces = unique_keep_order(
        pieces
    )

    return "; ".join(
        pieces
    )


def read_cvdict(
    target_chars,
):
    """
    Format CVDICT / CEDICT:

    PHON_THE GIAN_THE [pin1 yin1] /nghia/nghia/

    Giong pipeline HSK3 cu:
        dictionary[simplified].append(...)
    """

    if not CVDICT.is_file():

        raise FileNotFoundError(
            "Khong tim thay CVDICT.u8:\n"
            + str(
                CVDICT
            )
        )

    pattern = re.compile(
        r"^(\S+)\s+"
        r"(\S+)\s+"
        r"\[([^\]]+)\]\s+"
        r"/(.+)/$"
    )

    dictionary = defaultdict(
        list
    )

    total_lines = 0
    parsed_lines = 0

    with CVDICT.open(
        "r",
        encoding="utf-8-sig",
        errors="replace",
    ) as file:

        for raw_line in file:

            total_lines += 1

            line = raw_line.strip()

            if not line:
                continue

            if line.startswith(
                "#"
            ):
                continue

            match = pattern.match(
                line
            )

            if not match:
                continue

            traditional = clean(
                match.group(1)
            )

            simplified = clean(
                match.group(2)
            )

            pinyin = clean(
                match.group(3)
            )

            meaning = (
                parse_cvdict_meaning(
                    match.group(4)
                )
            )

            if (
                simplified
                not in target_chars
            ):
                continue

            parsed_lines += 1

            dictionary[
                simplified
            ].append({

                "traditional":
                    traditional,

                "simplified":
                    simplified,

                "pinyin":
                    pinyin,

                "pinyin_key":
                    normalize_pinyin(
                        pinyin
                    ),

                "meaning":
                    meaning,

                "raw":
                    line,
            })

    return (
        dictionary,
        total_lines,
        parsed_lines,
    )


def unique_candidates(
    candidates,
):
    """
    Bo trung theo:
        pinyin_key + meaning
    """

    result = []

    seen = set()

    for item in candidates:

        key = (
            clean(
                item[
                    "pinyin_key"
                ]
            ),
            clean(
                item[
                    "meaning"
                ]
            ),
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            item
        )

    return result


# ==========================================================
# 5. MAIN
# ==========================================================

def main():

    print(
        "=" * 80
    )

    print(
        "BUOC 20B - DOI CHIEU HSK4 VOI CVDICT.u8"
    )

    print(
        "=" * 80
    )

    print(
        "CHI DOC NGUON + TAO CSV"
    )

    print(
        "KHONG GHI SQL"
    )

    # ======================================================
    # [1] LOCK SNAPSHOT
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT"
    )

    source_hash = (
        sha256_file(
            SOURCE
        )
    )

    cvdict_hash = (
        sha256_file(
            CVDICT
        )
    )

    print(
        "STEP20 SHA256:"
    )

    print(
        source_hash
    )

    print(
        "CVDICT SHA256:"
    )

    print(
        cvdict_hash
    )

    if (
        source_hash
        != EXPECTED_SOURCE_SHA256
    ):

        raise RuntimeError(
            "Output Buoc 20 da thay doi."
        )

    if (
        cvdict_hash
        != EXPECTED_CVDICT_SHA256
    ):

        raise RuntimeError(
            "CVDICT.u8 khong dung "
            "snapshot da kiem tra."
        )

    print(
        "PASS: hash input hop le."
    )

    # ======================================================
    # [2] DOC INPUT
    # ======================================================

    print(
        "\n[2] DOC 300 CHU HSK4"
    )

    fields, rows = (
        read_csv(
            SOURCE
        )
    )

    required_fields = {

        "MaChuHanTam",
        "KyTu",

        "PinyinDeXuat",
        "NguonPinyinDeXuat",
        "TrangThaiPinyin",

        "NghiaTiengVietDeXuat",
        "NguonNghiaDeXuat",
        "TrangThaiNghia",

        "CanKiemTraPinyin",
        "CanKiemTraNghia",
        "CanKiemTraCauTruc",

        "TrangThaiKiemDuyet",
        "LyDoCanReview",
    }

    missing = (
        required_fields
        - set(
            fields
        )
    )

    if missing:

        raise RuntimeError(
            "Input thieu cot: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    if (
        len(
            rows
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Input khong dung 300 dong."
        )

    target_chars = {
        clean(
            row[
                "KyTu"
            ]
        )
        for row
        in rows
    }

    if (
        len(
            target_chars
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "KyTu bi trung."
        )

    existing_meanings = sum(
        1
        for row in rows
        if clean(
            row[
                "NghiaTiengVietDeXuat"
            ]
        )
    )

    missing_meanings = (
        EXPECTED_TOTAL
        - existing_meanings
    )

    print(
        "Tong:",
        len(
            rows
        ),
    )

    print(
        "Da co nghia Buoc 20:",
        existing_meanings,
    )

    print(
        "Con thieu nghia:",
        missing_meanings,
    )

    # ======================================================
    # [3] DOC CVDICT
    # ======================================================

    print(
        "\n[3] DOC CVDICT.u8"
    )

    (
        dictionary,
        total_lines,
        matched_source_lines,
    ) = read_cvdict(
        target_chars
    )

    print(
        "Tong dong source:",
        total_lines,
    )

    print(
        "Dong CVDICT trung 300 KyTu:",
        matched_source_lines,
    )

    print(
        "KyTu co candidate:",
        len(
            dictionary
        ),
        "/ 300",
    )

    # ======================================================
    # [4] PROCESS
    # ======================================================

    print(
        "\n[4] DOI CHIEU NGHIA"
    )

    output_rows = []

    review_rows = []

    stats = Counter()

    for source_row in rows:

        row = dict(
            source_row
        )

        char = clean(
            row[
                "KyTu"
            ]
        )

        pinyin = clean(
            row[
                "PinyinDeXuat"
            ]
        )

        target_pinyin = (
            normalize_pinyin(
                pinyin
            )
        )

        old_meaning = clean(
            row[
                "NghiaTiengVietDeXuat"
            ]
        )

        all_candidates = (
            unique_candidates(
                dictionary.get(
                    char,
                    []
                )
            )
        )

        exact = []

        if target_pinyin:

            exact = (
                unique_candidates([
                    item
                    for item
                    in all_candidates
                    if (
                        item[
                            "pinyin_key"
                        ]
                        == target_pinyin
                    )
                ])
            )

        # ==================================================
        # THONG TIN CVDICT
        # ==================================================

        all_readings = (
            unique_keep_order([
                item[
                    "pinyin"
                ]
                for item
                in all_candidates
            ])
        )

        exact_candidates_text = (
            " || ".join(
                f"[{item['pinyin']}] "
                f"{item['meaning']}"
                for item
                in exact
            )
        )

        all_candidates_text = (
            " || ".join(
                f"[{item['pinyin']}] "
                f"{item['meaning']}"
                for item
                in all_candidates
            )
        )

        row[
            "SoMucCVDICTFile"
        ] = len(
            all_candidates
        )

        row[
            "SoMucCVDICTKhopPinyin"
        ] = len(
            exact
        )

        row[
            "CacCachDocCVDICTFile"
        ] = " | ".join(
            all_readings
        )

        row[
            "UngVienNghiaCVDICTKhopPinyin"
        ] = exact_candidates_text

        row[
            "TatCaUngVienCVDICT"
        ] = all_candidates_text

        # ==================================================
        # DOI CHIEU
        # ==================================================

        current_meaning = (
            old_meaning
        )

        current_source = clean(
            row[
                "NguonNghiaDeXuat"
            ]
        )

        cvdict_status = ""

        meaning_review = "KHONG"

        # --------------------------------------------------
        # A. Da co nghia tu Buoc 20
        # --------------------------------------------------

        if old_meaning:

            cvdict_status = (
                "GIU_NGUYEN_NGHIA_BUOC20"
            )

            stats[
                "giu_nguyen"
            ] += 1

        # --------------------------------------------------
        # B. Chua co nghia, nhung Pinyin chua chot
        # --------------------------------------------------

        elif not target_pinyin:

            cvdict_status = (
                "CHUA_CO_PINYIN_DE_DOI_CHIEU"
            )

            meaning_review = "CO"

            stats[
                "khong_co_pinyin"
            ] += 1

        # --------------------------------------------------
        # C. Dung 1 muc khop Pinyin
        # --------------------------------------------------

        elif (
            len(
                exact
            )
            == 1
        ):

            current_meaning = clean(
                exact[0][
                    "meaning"
                ]
            )

            current_source = (
                "CVDICT.u8"
            )

            cvdict_status = (
                "CVDICT_KHOP_PINYIN_1_MUC_CAN_DUYET"
            )

            # CVDICT chi la nghia de xuat,
            # khong tu coi la da kiem duyet.
            meaning_review = "CO"

            stats[
                "bo_sung"
            ] += 1

        # --------------------------------------------------
        # D. Nhieu muc cung Pinyin
        # --------------------------------------------------

        elif (
            len(
                exact
            )
            > 1
        ):

            cvdict_status = (
                "NHIEU_MUC_CUNG_PINYIN"
            )

            meaning_review = "CO"

            stats[
                "nhieu_muc"
            ] += 1

        # --------------------------------------------------
        # E. Co chu, nhung khong khop Pinyin
        # --------------------------------------------------

        elif all_candidates:

            cvdict_status = (
                "CO_CHU_NHUNG_KHONG_KHOP_PINYIN"
            )

            meaning_review = "CO"

            stats[
                "khong_khop_pinyin"
            ] += 1

        # --------------------------------------------------
        # F. Khong tim thay chu
        # --------------------------------------------------

        else:

            cvdict_status = (
                "KHONG_TIM_THAY_CHU_TRONG_CVDICT"
            )

            meaning_review = "CO"

            stats[
                "khong_tim_thay"
            ] += 1

        # ==================================================
        # LUU KET QUA SAU CVDICT
        # ==================================================

        row[
            "NghiaTiengVietSauCVDICT"
        ] = current_meaning

        row[
            "NguonNghiaSauCVDICT"
        ] = current_source

        row[
            "TrangThaiDoiChieuCVDICT"
        ] = cvdict_status

        row[
            "CanKiemTraNghiaSauCVDICT"
        ] = meaning_review

        # ==================================================
        # TONG REVIEW
        # ==================================================

        reasons = []

        if (
            clean(
                row[
                    "CanKiemTraPinyin"
                ]
            )
            == "CO"
        ):

            reasons.append(
                "PINYIN"
            )

        if (
            meaning_review
            == "CO"
        ):

            reasons.append(
                "NGHIA"
            )

        if (
            clean(
                row[
                    "CanKiemTraCauTruc"
                ]
            )
            == "CO"
        ):

            reasons.append(
                "CAU_TRUC"
            )

        if reasons:

            row[
                "TrangThaiSau20B"
            ] = "CAN_REVIEW"

            row[
                "LyDoCanReviewSau20B"
            ] = " | ".join(
                reasons
            )

            review_rows.append(
                row
            )

        else:

            row[
                "TrangThaiSau20B"
            ] = (
                "SAN_SANG_KIEM_DUYET_CUOI"
            )

            row[
                "LyDoCanReviewSau20B"
            ] = ""

        if not current_meaning:

            stats[
                "con_thieu_nghia"
            ] += 1

        output_rows.append(
            row
        )

    # ======================================================
    # [5] VALIDATE
    # ======================================================

    print(
        "\n[5] KIEM TRA KET QUA"
    )

    if (
        len(
            output_rows
        )
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Output khong dung 300 dong."
        )

    if (
        len({
            clean(
                row[
                    "KyTu"
                ]
            )
            for row
            in output_rows
        })
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Output bi trung KyTu."
        )

    completed_meanings = sum(
        1
        for row in output_rows
        if clean(
            row[
                "NghiaTiengVietSauCVDICT"
            ]
        )
    )

    print(
        "PASS: 300 KyTu duy nhat."
    )

    print(
        "Giu nguyen nghia Buoc 20:",
        stats[
            "giu_nguyen"
        ],
    )

    print(
        "Bo sung tu CVDICT:",
        stats[
            "bo_sung"
        ],
    )

    print(
        "Nhieu muc cung Pinyin:",
        stats[
            "nhieu_muc"
        ],
    )

    print(
        "Co chu nhung khong khop Pinyin:",
        stats[
            "khong_khop_pinyin"
        ],
    )

    print(
        "Chua co Pinyin de doi chieu:",
        stats[
            "khong_co_pinyin"
        ],
    )

    print(
        "Khong tim thay chu:",
        stats[
            "khong_tim_thay"
        ],
    )

    print(
        "Da co nghia sau 20B:",
        completed_meanings,
        "/ 300",
    )

    print(
        "Con thieu nghia:",
        stats[
            "con_thieu_nghia"
        ],
    )

    print(
        "Tong KyTu can review bat ky muc:",
        len(
            review_rows
        ),
    )

    # ======================================================
    # [6] GHI FILE
    # ======================================================

    print(
        "\n[6] GHI FILE"
    )

    additional_fields = [

        "SoMucCVDICTFile",
        "SoMucCVDICTKhopPinyin",
        "CacCachDocCVDICTFile",
        "UngVienNghiaCVDICTKhopPinyin",
        "TatCaUngVienCVDICT",

        "NghiaTiengVietSauCVDICT",
        "NguonNghiaSauCVDICT",
        "TrangThaiDoiChieuCVDICT",
        "CanKiemTraNghiaSauCVDICT",

        "TrangThaiSau20B",
        "LyDoCanReviewSau20B",
    ]

    output_fields = (
        list(
            fields
        )
    )

    for field in additional_fields:

        if (
            field
            not in output_fields
        ):

            output_fields.append(
                field
            )

    write_csv(
        OUTPUT,
        output_rows,
        output_fields,
    )

    write_csv(
        REVIEW,
        review_rows,
        output_fields,
    )

    output_hash = (
        sha256_file(
            OUTPUT
        )
    )

    review_hash = (
        sha256_file(
            REVIEW
        )
    )

    # ======================================================
    # [7] SUMMARY
    # ======================================================

    status_counts = Counter(
        clean(
            row[
                "TrangThaiDoiChieuCVDICT"
            ]
        )
        for row
        in output_rows
    )

    summary = {

        "status":
            "PASS",

        "buoc":
            "20B",

        "tong_chu":
            EXPECTED_TOTAL,

        "source_step20":
            str(
                SOURCE
            ),

        "source_step20_sha256":
            source_hash,

        "cvdict":
            str(
                CVDICT
            ),

        "cvdict_sha256":
            cvdict_hash,

        "cvdict_total_lines":
            total_lines,

        "cvdict_matched_source_lines":
            matched_source_lines,

        "cvdict_character_coverage":
            len(
                dictionary
            ),

        "giu_nguyen_nghia_buoc20":
            stats[
                "giu_nguyen"
            ],

        "bo_sung_tu_cvdict":
            stats[
                "bo_sung"
            ],

        "nhieu_muc_cung_pinyin":
            stats[
                "nhieu_muc"
            ],

        "khong_khop_pinyin":
            stats[
                "khong_khop_pinyin"
            ],

        "chua_co_pinyin":
            stats[
                "khong_co_pinyin"
            ],

        "khong_tim_thay_chu":
            stats[
                "khong_tim_thay"
            ],

        "da_co_nghia_sau_20B":
            completed_meanings,

        "con_thieu_nghia":
            stats[
                "con_thieu_nghia"
            ],

        "tong_chu_can_review":
            len(
                review_rows
            ),

        "status_counts":
            dict(
                status_counts
            ),

        "output":
            str(
                OUTPUT
            ),

        "output_sha256":
            output_hash,

        "review":
            str(
                REVIEW
            ),

        "review_sha256":
            review_hash,

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
    # [8] PREVIEW
    # ======================================================

    print(
        "\n[7] PREVIEW CAC TRUONG HOP "
        "CVDICT CHUA TU CHOT"
    )

    cvdict_review = [
        row
        for row
        in output_rows
        if (
            clean(
                row[
                    "CanKiemTraNghiaSauCVDICT"
                ]
            )
            == "CO"
        )
    ]

    for row in cvdict_review[
        :40
    ]:

        print(
            row[
                "MaChuHanTam"
            ],
            "|",
            row[
                "KyTu"
            ],
            "| Pinyin:",
            row[
                "PinyinDeXuat"
            ],
            "|",
            row[
                "TrangThaiDoiChieuCVDICT"
            ],
            "| matches:",
            row[
                "SoMucCVDICTKhopPinyin"
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
        "BUOC 20B HOAN THANH"
    )

    print(
        "=" * 80
    )

    print(
        "CVDICT character coverage:",
        len(
            dictionary
        ),
        "/ 300",
    )

    print(
        "Giu nguyen nghia Buoc 20:",
        stats[
            "giu_nguyen"
        ],
    )

    print(
        "Bo sung CVDICT:",
        stats[
            "bo_sung"
        ],
    )

    print(
        "Nhieu muc cung Pinyin:",
        stats[
            "nhieu_muc"
        ],
    )

    print(
        "Khong khop Pinyin:",
        stats[
            "khong_khop_pinyin"
        ],
    )

    print(
        "Chua co Pinyin:",
        stats[
            "khong_co_pinyin"
        ],
    )

    print(
        "Khong tim thay chu:",
        stats[
            "khong_tim_thay"
        ],
    )

    print(
        "Da co nghia:",
        completed_meanings,
        "/ 300",
    )

    print(
        "Con thieu nghia:",
        stats[
            "con_thieu_nghia"
        ],
    )

    print(
        "Tong KyTu can review:",
        len(
            review_rows
        ),
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
        "\nREVIEW:"
    )

    print(
        " ",
        REVIEW
    )

    print(
        "SHA256:"
    )

    print(
        review_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY
    )

    print(
        "\nKHONG THAY DOI SQL."
    )

    print(
        "CHUA GAN BAI HOC."
    )

    print(
        "CHUA TAO AUDIO."
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