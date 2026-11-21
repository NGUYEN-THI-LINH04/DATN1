# -*- coding: utf-8 -*-
"""
BUOC 15D - REVIEW NOI DUNG NGU PHAP HSK4 BATCH 2

Dau vao:
- grammar_hsk4_teaching_draft_batch02.csv

Muc dich:
1. Khoa snapshot Buoc 15C bang SHA256.
2. Kiem tra dung 20 muc.
3. Kiem tra ID GF4 don vi 21 -> 40.
4. Ap dung review thu cong.
5. Kiem tra:
   - day du noi dung
   - anchor ngu phap
   - Pinyin
   - TenCauTruc
   - ViDuTiengTrung
6. Tao Batch 02 reviewed.

KHONG GHI SQL.
KHONG GAN BAI HOC.
KHONG PUBLISH.
"""

import csv
import hashlib
import json
import re

from collections import Counter
from pathlib import Path


# ==========================================================
# 1. CAU HINH
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
    / "grammar_hsk4_teaching_draft_batch02.csv"
)

OUTPUT = (
    DATA_DIR
    / "grammar_hsk4_teaching_reviewed_batch02.csv"
)

SUMMARY = (
    DATA_DIR
    / "grammar_hsk4_teaching_reviewed_batch02_summary.json"
)


EXPECTED_SOURCE_SHA256 = (
    "c673a6edeea290726c0b32505bc0701c"
    "9e501bcffc63431eb17de4906669cd3e"
)

EXPECTED_TOTAL = 20


OUTPUT_FIELDS = [
    "MaDonViGiangDay",
    "MaMucNguPhapChuan",
    "SoThuTuChuan",
    "SoThuTuNguon",

    "NhanDonViNguonTrung",
    "DuongDanNguon",

    "TenCauTruc",
    "MoTa",
    "CachDung",

    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",

    "MaNguon",
    "TrangThai",
    "TrangThaiKiemDuyet",
    "KetQuaReview",
    "GhiChuReview",
    "GhiChuNguon",
]


# ==========================================================
# 2. 20 ID MONG DOI
# ==========================================================

EXPECTED_IDS = [

    "GF4-007-T02",
    "GF4-007-T03",
    "GF4-007-T04",
    "GF4-007-T05",

    "GF4-008-T01",
    "GF4-008-T02",

    "GF4-009-T01",
    "GF4-010-T01",

    "GF4-011-T01",
    "GF4-011-T02",

    "GF4-012-T01",
    "GF4-012-T02",
    "GF4-012-T03",
    "GF4-012-T04",
    "GF4-012-T05",

    "GF4-013-T01",
    "GF4-014-T01",
    "GF4-015-T01",
    "GF4-016-T01",
    "GF4-017-T01",
]


# ==========================================================
# 3. ANCHOR
# ==========================================================

EXPECTED_ANCHORS = {

    "GF4-007-T02": ["即将"],
    "GF4-007-T03": ["急忙"],
    "GF4-007-T04": ["渐渐"],
    "GF4-007-T05": ["尽快"],

    "GF4-008-T01": ["一再"],
    "GF4-008-T02": ["再三"],

    "GF4-009-T01": ["却"],
    "GF4-010-T01": ["未必"],

    "GF4-011-T01": ["几乎"],
    "GF4-011-T02": ["似乎"],

    "GF4-012-T01": ["的确"],
    "GF4-012-T02": ["反而"],
    "GF4-012-T03": ["还"],
    "GF4-012-T04": ["竟然"],
    "GF4-012-T05": ["究竟"],

    "GF4-013-T01": ["自"],
    "GF4-014-T01": ["对于"],
    "GF4-015-T01": ["关于"],
    "GF4-016-T01": ["替"],
    "GF4-017-T01": ["根据"],
}


# ==========================================================
# 4. HIEU CHINH SAU REVIEW
# ==========================================================

CORRECTIONS = {

    # ------------------------------------------------------
    # 还4
    #
    # Cau Trung va Pinyin giu nguyen.
    # Chi dieu chinh ban dich tieng Viet de the hien
    # ro sac thai ngoai du kien / nhan manh.
    # ------------------------------------------------------

    "GF4-012-T03": {

        "ViDuTiengViet":
            "Không ngờ cách này thực sự hiệu quả.",

        "GhiChuReview":
            (
                "Dieu chinh ban dich cua 还真 de the hien "
                "ro sac thai ngoai du kien/nhan manh; "
                "giu nguyen cau Trung va Pinyin."
            ),
    },
}


# ==========================================================
# 5. HAM HO TRO
# ==========================================================

def clean(value):

    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def normalize(value):

    return clean(
        value
    ).casefold()


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
):

    if path.exists():

        raise FileExistsError(
            f"Da ton tai file:\n{path}\n"
            "Khong tu dong ghi de."
        )

    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# ==========================================================
# 6. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 15D - REVIEW NGU PHAP "
        "HSK4 BATCH 2"
    )

    print("=" * 80)

    print(
        "CHI REVIEW FILE - KHONG GHI SQL"
    )

    # ======================================================
    # 1. KHOA SNAPSHOT 15C
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT 15C"
    )

    source_hash = sha256_file(
        SOURCE
    )

    print(
        "SOURCE SHA256:"
    )

    print(
        source_hash
    )

    if (
        source_hash
        != EXPECTED_SOURCE_SHA256
    ):

        raise RuntimeError(
            "Batch 15C da thay doi."
        )

    print(
        "PASS: snapshot 15C khong thay doi."
    )

    # ======================================================
    # 2. DOC BATCH
    # ======================================================

    print(
        "\n[2] DOC BATCH 2"
    )

    fields, rows = read_csv(
        SOURCE
    )

    required = {
        "MaDonViGiangDay",
        "MaMucNguPhapChuan",
        "SoThuTuChuan",
        "SoThuTuNguon",
        "NhanDonViNguonTrung",
        "DuongDanNguon",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaNguon",
        "TrangThai",
        "TrangThaiKiemDuyet",
        "GhiChuNguon",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        raise RuntimeError(
            "Batch 15C thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    print(
        "Tong:",
        len(rows),
    )

    if (
        len(rows)
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "Batch 2 khong con dung 20 muc."
        )

    # ======================================================
    # 3. KIEM TRA ID / THU TU
    # ======================================================

    print(
        "\n[3] KIEM TRA ID"
    )

    actual_ids = [
        clean(
            row.get(
                "MaDonViGiangDay"
            )
        )
        for row in rows
    ]

    if (
        actual_ids
        != EXPECTED_IDS
    ):

        print(
            "ID hien tai:"
        )

        for value in actual_ids:
            print(
                " ",
                value
            )

        raise RuntimeError(
            "Thu tu ID Batch 2 "
            "khong con dung."
        )

    if (
        len(set(actual_ids))
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "MaDonViGiangDay bi trung."
        )

    print(
        "PASS: 20 ID dung thu tu."
    )

    # ======================================================
    # 4. APPLY REVIEW
    # ======================================================

    print(
        "\n[4] AP DUNG REVIEW"
    )

    result = []

    correction_count = 0

    for original in rows:

        row = dict(
            original
        )

        teaching_id = clean(
            row[
                "MaDonViGiangDay"
            ]
        )

        correction = (
            CORRECTIONS.get(
                teaching_id,
                {}
            )
        )

        if correction:

            correction_count += 1

            for key, value in (
                correction.items()
            ):

                if (
                    key
                    == "GhiChuReview"
                ):
                    continue

                row[
                    key
                ] = value

            row[
                "KetQuaReview"
            ] = (
                "PASS_SAU_HIEU_CHINH"
            )

            row[
                "GhiChuReview"
            ] = correction[
                "GhiChuReview"
            ]

        else:

            row[
                "KetQuaReview"
            ] = "PASS"

            row[
                "GhiChuReview"
            ] = (
                "Giu nguyen sau review Batch 02."
            )

        row[
            "TrangThai"
        ] = "ban_nhap"

        row[
            "TrangThaiKiemDuyet"
        ] = "DA_REVIEW_BATCH_02"

        result.append(
            row
        )

    print(
        "Muc giu nguyen:",
        EXPECTED_TOTAL
        - correction_count,
    )

    print(
        "Muc hieu chinh:",
        correction_count,
    )

    if (
        correction_count
        != 1
    ):

        raise RuntimeError(
            "So muc hieu chinh "
            "khong bang 1."
        )

    # ======================================================
    # 5. KIEM TRA NOI DUNG
    # ======================================================

    print(
        "\n[5] KIEM TRA SAU REVIEW"
    )

    required_text_fields = [
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
    ]

    for row in result:

        code = row[
            "MaDonViGiangDay"
        ]

        for field in (
            required_text_fields
        ):

            if not clean(
                row.get(field)
            ):

                raise RuntimeError(
                    f"{code}: rong {field}"
                )

        if (
            clean(
                row.get(
                    "MaNguon"
                )
            )
            != "1004"
        ):

            raise RuntimeError(
                f"{code}: MaNguon != 1004."
            )

        if (
            row[
                "TrangThai"
            ]
            != "ban_nhap"
        ):

            raise RuntimeError(
                f"{code}: "
                "TrangThai khong phai ban_nhap."
            )

        if (
            row[
                "TrangThaiKiemDuyet"
            ]
            != "DA_REVIEW_BATCH_02"
        ):

            raise RuntimeError(
                f"{code}: sai TrangThaiKiemDuyet."
            )

    # ======================================================
    # 6. KIEM TRA ANCHOR
    # ======================================================

    anchor_errors = []

    for row in result:

        code = row[
            "MaDonViGiangDay"
        ]

        sentence = row[
            "ViDuTiengTrung"
        ]

        anchors = (
            EXPECTED_ANCHORS[
                code
            ]
        )

        if not any(
            anchor in sentence
            for anchor in anchors
        ):

            anchor_errors.append(
                code
            )

    if anchor_errors:

        raise RuntimeError(
            "Vi du khong chua anchor: "
            + ", ".join(
                anchor_errors
            )
        )

    # ======================================================
    # 7. KIEM TRA PINYIN
    # ======================================================

    bad_pinyin = [
        row[
            "MaDonViGiangDay"
        ]
        for row in result
        if re.search(
            r"[\u3400-\u9fff]",
            row[
                "ViDuPinyin"
            ],
        )
    ]

    if bad_pinyin:

        raise RuntimeError(
            "Pinyin con Hanzi: "
            + ", ".join(
                bad_pinyin
            )
        )

    # ======================================================
    # 8. KIEM TRA TRUNG
    # ======================================================

    title_counts = Counter(
        normalize(
            row[
                "TenCauTruc"
            ]
        )
        for row in result
    )

    duplicate_titles = [
        value
        for value, count
        in title_counts.items()
        if count > 1
    ]

    if duplicate_titles:

        raise RuntimeError(
            "TenCauTruc bi trung."
        )

    example_counts = Counter(
        clean(
            row[
                "ViDuTiengTrung"
            ]
        )
        for row in result
    )

    duplicate_examples = [
        value
        for value, count
        in example_counts.items()
        if count > 1
    ]

    if duplicate_examples:

        raise RuntimeError(
            "ViDuTiengTrung bi trung."
        )

    print(
        "PASS: 20/20 noi dung day du."
    )

    print(
        "PASS: 20/20 vi du co anchor."
    )

    print(
        "PASS: Pinyin sach."
    )

    print(
        "PASS: TenCauTruc khong trung."
    )

    print(
        "PASS: ViDuTiengTrung khong trung."
    )

    # ======================================================
    # 9. IN MUC DA SUA
    # ======================================================

    print(
        "\n[6] MUC DA HIEU CHINH"
    )

    for row in result:

        if (
            row[
                "KetQuaReview"
            ]
            != "PASS_SAU_HIEU_CHINH"
        ):
            continue

        print(
            "\n"
            + "-" * 80
        )

        print(
            row[
                "MaDonViGiangDay"
            ]
        )

        print(
            "Ten:",
            row[
                "TenCauTruc"
            ]
        )

        print(
            "VD:",
            row[
                "ViDuTiengTrung"
            ]
        )

        print(
            "PY:",
            row[
                "ViDuPinyin"
            ]
        )

        print(
            "VI:",
            row[
                "ViDuTiengViet"
            ]
        )

        print(
            "Review:",
            row[
                "GhiChuReview"
            ]
        )

    # ======================================================
    # 10. XUAT FILE
    # ======================================================

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        OUTPUT,
        result,
    )

    output_hash = sha256_file(
        OUTPUT
    )

    # ======================================================
    # 11. SUMMARY
    # ======================================================

    summary = {

        "status":
            "PASS",

        "batch":
            2,

        "tong":
            len(result),

        "giu_nguyen":
            (
                EXPECTED_TOTAL
                - correction_count
            ),

        "hieu_chinh":
            correction_count,

        "ket_qua_review": {

            "PASS":
                sum(
                    row[
                        "KetQuaReview"
                    ]
                    == "PASS"
                    for row in result
                ),

            "PASS_SAU_HIEU_CHINH":
                sum(
                    row[
                        "KetQuaReview"
                    ]
                    ==
                    "PASS_SAU_HIEU_CHINH"
                    for row in result
                ),
        },

        "trang_thai":
            "ban_nhap",

        "trang_thai_kiem_duyet":
            "DA_REVIEW_BATCH_02",

        "source_sha256":
            source_hash,

        "output_sha256":
            output_hash,

        "da_ghi_sql":
            False,

        "da_gan_bai_hoc":
            False,

        "da_publish":
            False,
    }

    if SUMMARY.exists():

        raise FileExistsError(
            f"Da ton tai file:\n"
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
    # 12. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "REVIEW HSK4 BATCH 2 THANH CONG"
    )

    print("=" * 80)

    print(
        "Tong:",
        len(result),
        "/ 20",
    )

    print(
        "Giu nguyen:",
        EXPECTED_TOTAL
        - correction_count,
    )

    print(
        "Hieu chinh:",
        correction_count,
    )

    print(
        "Tong da review:",
        40,
        "/ 114",
    )

    print(
        "Con lai:",
        74,
    )

    print(
        "Trang thai SQL tuong lai: ban_nhap"
    )

    print(
        "Kiem duyet batch: DA_REVIEW_BATCH_02"
    )

    print(
        "\nOUTPUT:"
    )

    print(
        " ",
        OUTPUT,
    )

    print(
        "\nOUTPUT SHA256:"
    )

    print(
        output_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY,
    )

    print(
        "\nKHONG GHI SQL."
    )

    print(
        "CHUA GAN BAI HOC."
    )

    print(
        "CHUA PUBLISH."
    )

    print("=" * 80)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)