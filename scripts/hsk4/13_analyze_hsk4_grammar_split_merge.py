# -*- coding: utf-8 -*-
"""
BUOC 13 - PHAN TICH TACH/GIU CAC DIEM NGU PHAP HSK4

Nguyen tac:
- 76 MaMucNguPhapChuan GF4-* phai duoc giu nguyen.
- KHONG tu dong gop 2 ma GF4 khac nhau.
- Mot ma GF4 co the:
    GIU_1_MUC
    hoac CAN_XEM_XET_TACH 1 -> N
- Script chi phat hien ung vien can xem xet.
- Quyet dinh cuoi cung de trong.

KHONG GHI SQL.
KHONG BIEN SOAN TIENG VIET.
"""

import csv
import json
import re
import unicodedata

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
    / "grammar_hsk4_teaching_scope.csv"
)

OUTPUT = (
    DATA_DIR
    / "grammar_hsk4_split_merge_analysis.csv"
)

CANDIDATES = (
    DATA_DIR
    / "grammar_hsk4_split_candidates.csv"
)

SUMMARY = (
    DATA_DIR
    / "grammar_hsk4_split_merge_summary.json"
)


EXPECTED_TOTAL = 76


OUTPUT_FIELDS = [
    "MaMucNguPhapChuan",
    "SoThuTuChuan",
    "SoThuTuNguon",
    "NhomLonTrung",
    "NhomConTrung",
    "ChiTietTrung",
    "NoiDungChuanTrung",
    "DuongDanNguon",
    "CanhBaoNguon",

    "SoCumTrichDan",
    "CoDauPhanCach",
    "CoDanhSachDanhSo",
    "CoNhieuCumSongSong",
    "RawContentRong",
    "DoDaiNoiDung",

    "TinHieuPhatHien",
    "DeXuatMay",

    # De trong de quyet dinh sau khi review.
    "QuyetDinhCuoi",
    "SoMucGiangDayCuoi",
    "GhiChuQuyetDinh",
]


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def normalize(value):

    value = unicodedata.normalize(
        "NFKC",
        clean(value),
    )

    return value


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


def count_quoted_items(text):
    """
    Dem cum trong dau ngoac kep Trung Quoc:
    “...”
    """

    return len(
        re.findall(
            r"“[^”]+”",
            text,
        )
    )


def has_numbered_list(text):

    patterns = [
        # （1） / (1)
        r"[（(]\s*\d+\s*[)）]",

        # 1. / 1、
        r"(?:^|[\s；;，,。])\d+\s*[、.．]",

        # 一、 二、 三、
        r"(?:^|[\s；;，,。])"
        r"[一二三四五六七八九十]+\s*、",

        # ① ② ...
        r"[①②③④⑤⑥⑦⑧⑨⑩]",
    ]

    return any(
        re.search(
            pattern,
            text,
        )
        for pattern in patterns
    )


def has_separator(text):

    # Dau '、' rat pho bien trong danh sach nhieu muc.
    # Dau cham phay cung la tin hieu manh.
    return (
        "；" in text
        or ";" in text
        or "、" in text
    )


def parallel_signal(text):
    """
    Tin hieu yeu hon:
    nhieu cum dat song song trong cung diem chuan.

    Khong dong nghia voi bat buoc tach.
    """

    quoted = count_quoted_items(
        text
    )

    if quoted >= 2:
        return True

    # Mot so source liet ke A、B hoac A和B.
    if (
        "以及" in text
        or "分别" in text
    ):
        return True

    return False


# ==========================================================
# 3. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 13 - PHAN TICH TACH/GIU "
        "NGU PHAP HSK4"
    )

    print("=" * 80)

    print(
        "CHI PHAN TICH FILE - KHONG GHI SQL"
    )

    # ======================================================
    # 1. DOC WORKLIST
    # ======================================================

    print(
        "\n[1] DOC WORKLIST BUOC 12"
    )

    fields, rows = read_csv(
        SOURCE
    )

    required = {
        "MaMucNguPhapChuan",
        "CapDoHSK",
        "SoThuTuChuan",
        "SoThuTuNguon",
        "MaNguon",
        "NhomLonTrung",
        "NhomConTrung",
        "ChiTietTrung",
        "NoiDungChuanTrung",
        "DuongDanNguon",
        "CanhBaoNguon",
        "TrangThaiBienSoan",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        raise RuntimeError(
            "Worklist thieu cot: "
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
            "Worklist khong con dung 76 muc."
        )

    # ======================================================
    # 2. VALIDATE ID
    # ======================================================

    print(
        "\n[2] KIEM TRA 76 MA GF4"
    )

    expected_ids = [
        f"GF4-{i:03d}"
        for i in range(
            1,
            EXPECTED_TOTAL + 1,
        )
    ]

    actual_ids = [
        clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )
        for row in rows
    ]

    if actual_ids != expected_ids:

        raise RuntimeError(
            "Ma GF4 khong con lien tuc "
            "GF4-001 -> GF4-076."
        )

    if len(set(actual_ids)) != EXPECTED_TOTAL:

        raise RuntimeError(
            "Ma GF4 bi trung."
        )

    print(
        "PASS: GF4-001 -> GF4-076."
    )

    # ======================================================
    # 3. PHAN TICH TUNG MUC
    # ======================================================

    print(
        "\n[3] PHAN TICH TIN HIEU TACH"
    )

    result = []

    for row in rows:

        code = clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )

        if clean(
            row.get("CapDoHSK")
        ) != "4":

            raise RuntimeError(
                f"{code}: CapDoHSK != 4."
            )

        if clean(
            row.get("MaNguon")
        ) != "1004":

            raise RuntimeError(
                f"{code}: MaNguon != 1004."
            )

        content = normalize(
            row.get(
                "NoiDungChuanTrung"
            )
        )

        source_path = normalize(
            row.get(
                "DuongDanNguon"
            )
        )

        if not content:
            raise RuntimeError(
                f"{code}: "
                "NoiDungChuanTrung rong."
            )

        if not source_path:
            raise RuntimeError(
                f"{code}: "
                "DuongDanNguon rong."
            )

        warning = clean(
            row.get(
                "CanhBaoNguon"
            )
        )

        raw_blank = (
            "RAW_KHONG_CO_CONTENT"
            in warning
        )

        quoted_count = (
            count_quoted_items(
                content
            )
        )

        separator = (
            has_separator(
                content
            )
        )

        numbered = (
            has_numbered_list(
                content
            )
        )

        parallel = (
            parallel_signal(
                content
            )
        )

        signals = []

        # Tin hieu manh
        if numbered:
            signals.append(
                "CO_DANH_SACH_DANH_SO"
            )

        if separator:
            signals.append(
                "CO_DAU_PHAN_CACH"
            )

        # Tin hieu vua
        if quoted_count >= 2:
            signals.append(
                f"CO_{quoted_count}_CUM_TRICH_DAN"
            )

        if parallel:
            signals.append(
                "CO_NHIEU_CUM_SONG_SONG"
            )

        # Raw Content rong:
        # khong phai ly do de tach,
        # nhung bat buoc review thu cong.
        if raw_blank:
            signals.append(
                "RAW_CONTENT_RONG"
            )

        # --------------------------------------------------
        # De xuat MAY, KHONG phai quyet dinh cuoi
        # --------------------------------------------------

        strong_count = sum([
            numbered,
            separator,
        ])

        medium_count = sum([
            quoted_count >= 2,
            parallel,
        ])

        if strong_count >= 1:

            suggestion = (
                "CAN_XEM_XET_TACH"
            )

        elif medium_count >= 1:

            suggestion = (
                "CAN_REVIEW_CAU_TRUC"
            )

        elif raw_blank:

            suggestion = (
                "CAN_REVIEW_NGU_CANH"
            )

        else:

            suggestion = (
                "CO_THE_GIU_1_MUC"
            )

        result.append({

            "MaMucNguPhapChuan":
                code,

            "SoThuTuChuan":
                clean(
                    row.get(
                        "SoThuTuChuan"
                    )
                ),

            "SoThuTuNguon":
                clean(
                    row.get(
                        "SoThuTuNguon"
                    )
                ),

            "NhomLonTrung":
                clean(
                    row.get(
                        "NhomLonTrung"
                    )
                ),

            "NhomConTrung":
                clean(
                    row.get(
                        "NhomConTrung"
                    )
                ),

            "ChiTietTrung":
                clean(
                    row.get(
                        "ChiTietTrung"
                    )
                ),

            "NoiDungChuanTrung":
                clean(
                    row.get(
                        "NoiDungChuanTrung"
                    )
                ),

            "DuongDanNguon":
                clean(
                    row.get(
                        "DuongDanNguon"
                    )
                ),

            "CanhBaoNguon":
                warning,

            "SoCumTrichDan":
                quoted_count,

            "CoDauPhanCach":
                (
                    "CO"
                    if separator
                    else "KHONG"
                ),

            "CoDanhSachDanhSo":
                (
                    "CO"
                    if numbered
                    else "KHONG"
                ),

            "CoNhieuCumSongSong":
                (
                    "CO"
                    if parallel
                    else "KHONG"
                ),

            "RawContentRong":
                (
                    "CO"
                    if raw_blank
                    else "KHONG"
                ),

            "DoDaiNoiDung":
                len(content),

            "TinHieuPhatHien":
                "; ".join(
                    signals
                ),

            "DeXuatMay":
                suggestion,

            # Tuyet doi chua tu dong dien.
            "QuyetDinhCuoi":
                "",

            "SoMucGiangDayCuoi":
                "",

            "GhiChuQuyetDinh":
                "",
        })

    # ======================================================
    # 4. THONG KE
    # ======================================================

    suggestion_counts = Counter(
        row[
            "DeXuatMay"
        ]
        for row in result
    )

    candidates = [
        row
        for row in result
        if row[
            "DeXuatMay"
        ]
        != "CO_THE_GIU_1_MUC"
    ]

    split_candidates = [
        row
        for row in result
        if row[
            "DeXuatMay"
        ]
        == "CAN_XEM_XET_TACH"
    ]

    print(
        "Tong diem chuan:",
        len(result),
    )

    print(
        "\nPhan loai heuristic:"
    )

    for key in [
        "CAN_XEM_XET_TACH",
        "CAN_REVIEW_CAU_TRUC",
        "CAN_REVIEW_NGU_CANH",
        "CO_THE_GIU_1_MUC",
    ]:

        print(
            f"  {key}: "
            f"{suggestion_counts[key]}"
        )

    # ======================================================
    # 5. IN CAC UNG VIEN CAN XEM
    # ======================================================

    print(
        "\n[4] CAC MUC CAN XEM XET"
    )

    if not candidates:

        print(
            "Khong co ung vien."
        )

    else:

        for index, row in enumerate(
            candidates,
            start=1,
        ):

            print(
                "\n"
                + "-" * 80
            )

            print(
                f"[{index}] "
                f"{row['MaMucNguPhapChuan']}"
                f" | Source No "
                f"{row['SoThuTuNguon']}"
            )

            print(
                "De xuat:",
                row[
                    "DeXuatMay"
                ],
            )

            print(
                "Tin hieu:",
                row[
                    "TinHieuPhatHien"
                ]
                or "(khong)",
            )

            print(
                "Duong dan:"
            )

            print(
                " ",
                row[
                    "DuongDanNguon"
                ],
            )

            print(
                "Noi dung:"
            )

            print(
                " ",
                row[
                    "NoiDungChuanTrung"
                ],
            )

    # ======================================================
    # 6. XUAT FILE
    # ======================================================

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        OUTPUT,
        result,
    )

    write_csv(
        CANDIDATES,
        candidates,
    )

    summary = {

        "status":
            "PASS",

        "tong_diem_chuan":
            len(result),

        "gf4_dau":
            result[0][
                "MaMucNguPhapChuan"
            ],

        "gf4_cuoi":
            result[-1][
                "MaMucNguPhapChuan"
            ],

        "phan_loai":
            dict(
                suggestion_counts
            ),

        "tong_muc_can_review":
            len(candidates),

        "ung_vien_tach_manh":
            len(
                split_candidates
            ),

        "cho_phep_gop_giua_hai_ma_gf4":
            False,

        "da_quyet_dinh_tach":
            False,

        "da_bien_soan_noi_dung":
            False,

        "da_ghi_sql":
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
    # 7. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "PHAN TICH TACH/GIU HSK4 HOAN THANH"
    )

    print("=" * 80)

    print(
        "Tong:",
        len(result),
        "/ 76",
    )

    print(
        "Ung vien can review:",
        len(candidates),
    )

    print(
        "Ung vien tach manh:",
        len(split_candidates),
    )

    print(
        "\nFILE PHAN TICH:"
    )

    print(
        " ",
        OUTPUT,
    )

    print(
        "\nFILE UNG VIEN:"
    )

    print(
        " ",
        CANDIDATES,
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY,
    )

    print(
        "\nKHONG GOP CAC MA GF4 KHAC NHAU."
    )

    print(
        "CHUA QUYET DINH TACH 1 -> N."
    )

    print(
        "CHUA BIEN SOAN TIENG VIET."
    )

    print(
        "KHONG THAY DOI SQL."
    )

    print("=" * 80)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)