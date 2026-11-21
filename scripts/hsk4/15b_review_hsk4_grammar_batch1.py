# -*- coding: utf-8 -*-
"""
BUOC 15B - REVIEW NOI DUNG NGU PHAP HSK4 BATCH 1

Dau vao:
- grammar_hsk4_teaching_draft_batch01.csv

Muc dich:
1. Khoa snapshot Buoc 15A bang SHA256.
2. Kiem tra du 20 muc.
3. Kiem tra mapping MaDonViGiangDay.
4. Ap dung 2 hieu chinh noi dung da review thu cong.
5. Kiem tra trung TenCauTruc / vi du.
6. Kiem tra vi du co chua anchor ngu phap can day.
7. Tao batch 1 da review.

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
    / "grammar_hsk4_teaching_draft_batch01.csv"
)

OUTPUT = (
    DATA_DIR
    / "grammar_hsk4_teaching_reviewed_batch01.csv"
)

SUMMARY = (
    DATA_DIR
    / "grammar_hsk4_teaching_reviewed_batch01_summary.json"
)


EXPECTED_SOURCE_SHA256 = (
    "353c44815d6a7334ce6f731c11c0b8d"
    "4d484c1ce580b169c174616546f817900"
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
# 2. ANCHOR BAT BUOC TRONG VI DU
# ==========================================================
#
# Vi du phai the hien chinh don vi dang day.
# ==========================================================

EXPECTED_ANCHORS = {

    "GF4-001-T01": ["得"],

    "GF4-002-T01": ["人家"],

    "GF4-003-T01": ["打"],
    "GF4-003-T02": ["袋"],
    "GF4-003-T03": ["根"],
    "GF4-003-T04": ["卷"],
    "GF4-003-T05": ["棵"],
    "GF4-003-T06": ["批"],

    "GF4-004-T01": ["碗"],
    "GF4-004-T02": ["脸"],
    "GF4-004-T03": ["手"],
    "GF4-004-T04": ["屋子"],
    "GF4-004-T05": ["桌子"],
    "GF4-004-T06": ["刀"],
    "GF4-004-T07": ["针"],

    "GF4-005-T01": ["格外"],
    "GF4-005-T02": ["极"],
    "GF4-005-T03": ["极其"],

    "GF4-006-T01": ["共"],

    "GF4-007-T01": ["按时"],
}


# ==========================================================
# 3. HIEU CHINH SAU REVIEW THU CONG
# ==========================================================

CORRECTIONS = {

    # ------------------------------------------------------
    # 人家:
    # Doi ban dich de hien ro dai tu 人家.
    # ------------------------------------------------------

    "GF4-002-T01": {

        "ViDuTiengViet":
            "Người ta đã đi hết rồi, "
            "bạn còn đang đợi gì nữa?",

        "GhiChuReview":
            (
                "Dieu chinh ban dich de the hien "
                "truc tiep nghia dai tu 人家."
            ),
    },

    # ------------------------------------------------------
    # 一屋子人:
    # 坐着 phu hop hon cho trang thai ton tai/tinh.
    # ------------------------------------------------------

    "GF4-004-T04": {

        "ViDuTiengTrung":
            "屋里坐着一屋子人。",

        "ViDuPinyin":
            "Wūli zuòzhe yì wūzi rén.",

        "ViDuTiengViet":
            (
                "Trong phòng có cả một phòng "
                "đầy người đang ngồi."
            ),

        "GhiChuReview":
            (
                "Doi 坐了 thanh 坐着 de dien ta "
                "trang thai dang ton tai tu nhien hon."
            ),
    },
}


# ==========================================================
# 4. HAM HO TRO
# ==========================================================

def clean(value):

    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def normalize(value):

    return clean(value).casefold()


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open("rb") as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

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

        reader = csv.DictReader(file)

        fields = (
            reader.fieldnames
            or []
        )

        rows = list(reader)

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
        writer.writerows(rows)


# ==========================================================
# 5. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 15B - REVIEW NGU PHAP "
        "HSK4 BATCH 1"
    )

    print("=" * 80)

    print(
        "CHI REVIEW FILE - KHONG GHI SQL"
    )

    # ======================================================
    # 1. KHOA SNAPSHOT 15A
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT 15A"
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
            "Batch 15A da thay doi."
        )

    print(
        "PASS: snapshot 15A khong thay doi."
    )

    # ======================================================
    # 2. DOC BATCH
    # ======================================================

    print(
        "\n[2] DOC BATCH 1"
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
            "Batch 15A thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    print(
        "Tong:",
        len(rows),
    )

    if len(rows) != EXPECTED_TOTAL:

        raise RuntimeError(
            "Batch 1 khong con dung 20 muc."
        )

    # ======================================================
    # 3. KIEM TRA ID
    # ======================================================

    print(
        "\n[3] KIEM TRA ID"
    )

    ids = [
        clean(
            row.get(
                "MaDonViGiangDay"
            )
        )
        for row in rows
    ]

    if (
        len(set(ids))
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "MaDonViGiangDay bi trung."
        )

    if set(ids) != set(
        EXPECTED_ANCHORS
    ):

        raise RuntimeError(
            "Danh sach ID batch 1 "
            "khong con dung ke hoach."
        )

    print(
        "PASS: 20 ID dung."
    )

    # ======================================================
    # 4. APPLY REVIEW
    # ======================================================

    print(
        "\n[4] AP DUNG REVIEW THU CONG"
    )

    result = []

    correction_count = 0

    for original in rows:

        row = dict(original)

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

                row[key] = value

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
                "Giu nguyen sau review batch 1."
            )

        # Van la ban nhap.
        row[
            "TrangThai"
        ] = "ban_nhap"

        # Da review noi dung cua batch,
        # CHUA co nghia la publish.
        row[
            "TrangThaiKiemDuyet"
        ] = "DA_REVIEW_BATCH_01"

        result.append(row)

    print(
        "Muc giu nguyen:",
        EXPECTED_TOTAL
        - correction_count,
    )

    print(
        "Muc hieu chinh:",
        correction_count,
    )

    if correction_count != 2:

        raise RuntimeError(
            "So muc hieu chinh "
            "khong bang 2."
        )

    # ======================================================
    # 5. VALIDATE NOI DUNG
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

        for field in required_text_fields:

            if not clean(
                row.get(field)
            ):

                raise RuntimeError(
                    f"{code}: rong {field}"
                )

        if (
            clean(
                row.get("MaNguon")
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
                "TrangThai phai ban_nhap."
            )

    # ------------------------------------------------------
    # Kiem tra anchor ngu phap trong vi du
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Pinyin khong co Hanzi
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Trung TenCauTruc
    # ------------------------------------------------------

    title_counts = Counter(
        normalize(
            row[
                "TenCauTruc"
            ]
        )
        for row in result
    )

    duplicate_titles = [
        title
        for title, count
        in title_counts.items()
        if count > 1
    ]

    if duplicate_titles:

        raise RuntimeError(
            "TenCauTruc bi trung."
        )

    # ------------------------------------------------------
    # Trung vi du Trung
    # ------------------------------------------------------

    example_counts = Counter(
        clean(
            row[
                "ViDuTiengTrung"
            ]
        )
        for row in result
    )

    duplicate_examples = [
        text
        for text, count
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
        "PASS: 20/20 vi du chua "
        "dung anchor ngu phap."
    )

    print(
        "PASS: TenCauTruc khong trung."
    )

    print(
        "PASS: ViDuTiengTrung khong trung."
    )

    # ======================================================
    # 6. IN 2 MUC DA SUA
    # ======================================================

    print(
        "\n[6] CAC MUC DA HIEU CHINH"
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
    # 7. XUAT FILE
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

    summary = {

        "status":
            "PASS",

        "batch":
            1,

        "tong":
            len(result),

        "giu_nguyen":
            EXPECTED_TOTAL
            - correction_count,

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
            "DA_REVIEW_BATCH_01",

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
    # 8. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "REVIEW HSK4 BATCH 1 THANH CONG"
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
        "Trang thai SQL tuong lai: ban_nhap"
    )

    print(
        "Kiem duyet batch: DA_REVIEW_BATCH_01"
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