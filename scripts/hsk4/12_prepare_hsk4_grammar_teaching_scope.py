# -*- coding: utf-8 -*-
"""
BUOC 12 - TAO KHUNG BIEN SOAN NGU PHAP HSK4

Dau vao:
- hsk4_76_grammar_standard.csv
- grammar_hsk4_standard_review.csv

Muc dich:
1. Khoa snapshot 76 diem chuan GF0025 HSK4.
2. Tao duong dan nguon day du:
   Group > Category > Details > Content.
3. Khong dung TenMucTrung ngan lam dinh danh duy nhat.
4. Tao worklist bien soan noi dung tieng Viet.
5. KHONG quy dinh 76 diem chuan = 76 dong dbo.NguPhap.
6. Cac cot noi dung giang day de trong de xu ly o buoc sau.

KHONG GHI SQL.
"""

import csv
import hashlib
import json
import re
import unicodedata

from collections import Counter
from pathlib import Path


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

GRAMMAR_DIR = (
    ROOT
    / "data_sources"
    / "hsk"
    / "grammar"
)

PROCESSED_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

STANDARD_FILE = (
    GRAMMAR_DIR
    / "hsk4_76_grammar_standard.csv"
)

REVIEW_FILE = (
    PROCESSED_DIR
    / "grammar_hsk4_standard_review.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "grammar_hsk4_teaching_scope.csv"
)

SUMMARY_FILE = (
    PROCESSED_DIR
    / "grammar_hsk4_teaching_scope_summary.json"
)


EXPECTED_COUNT = 76

EXPECTED_STANDARD_SHA256 = (
    "e09ed9d3086c38256c610feb93fae58b"
    "94e28c33188f9b0845c639d93b1659c9"
)


OUTPUT_FIELDS = [
    # Dinh danh nguon
    "MaMucNguPhapChuan",
    "CapDoHSK",
    "SoThuTuChuan",
    "SoThuTuNguon",
    "MaNguon",

    # Noi dung goc
    "NhomLonTrung",
    "NhomConTrung",
    "ChiTietTrung",
    "NoiDungChuanTrung",

    # Context phuc vu bien soan
    "DuongDanNguon",
    "TenDiemChuanNguon",
    "CanhBaoNguon",

    # Quyết định tách/gộp
    "QuyetDinhTachGop",
    "SoMucGiangDayDeXuat",

    # Noi dung sau nay se dua vao dbo.NguPhap
    "TenCauTruc",
    "MoTa",
    "CachDung",
    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",

    # Quan ly review
    "TrangThaiBienSoan",
    "GhiChuBienSoan",
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
    ).casefold()

    value = re.sub(
        r"\s+",
        "",
        value,
    )

    return value


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
            f"Khong tim thay file:\n{path}"
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


def build_source_path(row):
    """
    Tao context:
    Group > Category > Details > Content

    Loai bo:
    - field rong
    - field lien tiep trung nhau
    """

    source_parts = [
        clean(
            row.get("NhomLonTrung")
        ),
        clean(
            row.get("NhomConTrung")
        ),
        clean(
            row.get("ChiTietTrung")
        ),
        clean(
            row.get(
                "NoiDungChuanTrung"
            )
        ),
    ]

    result = []

    for value in source_parts:

        if not value:
            continue

        if (
            result
            and normalize(result[-1])
            == normalize(value)
        ):
            continue

        result.append(value)

    return " > ".join(result)


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
# 3. MAIN
# ==========================================================

def main():

    print("=" * 78)

    print(
        "BUOC 12 - TAO KHUNG BIEN SOAN "
        "NGU PHAP HSK4"
    )

    print("=" * 78)

    print(
        "CHI TAO WORKLIST - KHONG GHI SQL"
    )

    # ======================================================
    # 1. KHOA STANDARD
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT STANDARD"
    )

    standard_hash = sha256_file(
        STANDARD_FILE
    )

    print(
        "STANDARD SHA256:"
    )

    print(
        standard_hash
    )

    if (
        standard_hash
        != EXPECTED_STANDARD_SHA256
    ):

        raise RuntimeError(
            "File standard HSK4 da thay doi "
            "sau Buoc 10-11."
        )

    print(
        "PASS: standard khong thay doi."
    )

    # ======================================================
    # 2. DOC REVIEW BUOC 11
    # ======================================================

    print(
        "\n[2] DOC REVIEW BUOC 11"
    )

    fields, rows = read_csv(
        REVIEW_FILE
    )

    required = {
        "MaMucNguPhapChuan",
        "CapDoHSK",
        "SoThuTuChuan",
        "SoThuTuNguon",
        "NhomLonTrung",
        "NhomConTrung",
        "TenMucTrung",
        "ChiTietTrung",
        "NoiDungChuanTrung",
        "RawContent",
        "MaNguon",
        "KhopRaw",
        "TrungHoanToanVoiCapThapHon",
        "VanDeCanKiemTra",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        raise RuntimeError(
            "Review Buoc 11 thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    print(
        "Tong review:",
        len(rows),
    )

    if len(rows) != EXPECTED_COUNT:

        raise RuntimeError(
            "Review HSK4 khong co dung 76 muc."
        )

    # ======================================================
    # 3. KIEM TRA 76 ID
    # ======================================================

    print(
        "\n[3] KIEM TRA DINH DANH"
    )

    expected_ids = [
        f"GF4-{i:03d}"
        for i in range(
            1,
            EXPECTED_COUNT + 1,
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
            "ID khong con dung "
            "GF4-001 -> GF4-076."
        )

    if len(
        set(actual_ids)
    ) != EXPECTED_COUNT:

        raise RuntimeError(
            "MaMucNguPhapChuan bi trung."
        )

    print(
        "PASS: GF4-001 -> GF4-076."
    )

    # ======================================================
    # 4. KIEM TRA TINH TOAN VEN SOURCE
    # ======================================================

    print(
        "\n[4] KIEM TRA SOURCE"
    )

    warning_count = 0
    raw_content_blank = 0

    source_titles = []

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

        if clean(
            row.get("KhopRaw")
        ) != "CO":

            raise RuntimeError(
                f"{code}: chua khop RAW."
            )

        if (
            clean(
                row.get(
                    "TrungHoanToanVoiCapThapHon"
                )
            )
            != "KHONG"
        ):

            raise RuntimeError(
                f"{code}: trung hoan toan "
                "voi cap thap hon."
            )

        source_title = clean(
            row.get(
                "NoiDungChuanTrung"
            )
        )

        if not source_title:

            raise RuntimeError(
                f"{code}: "
                "NoiDungChuanTrung rong."
            )

        source_titles.append(
            source_title
        )

        if clean(
            row.get(
                "VanDeCanKiemTra"
            )
        ):

            warning_count += 1

        if not clean(
            row.get("RawContent")
        ):

            raw_content_blank += 1

    print(
        "Khop RAW:",
        EXPECTED_COUNT,
        "/",
        EXPECTED_COUNT,
    )

    print(
        "Muc co canh bao nguon:",
        warning_count,
    )

    print(
        "RAW Content rong:",
        raw_content_blank,
    )

    # ======================================================
    # 5. KIEM TRA TEN DIEM CHUAN DUY NHAT
    # ======================================================

    print(
        "\n[5] KIEM TRA TEN DIEM CHUAN"
    )

    normalized_titles = [
        normalize(value)
        for value in source_titles
    ]

    duplicate_title_count = (
        len(normalized_titles)
        - len(
            set(
                normalized_titles
            )
        )
    )

    print(
        "NoiDungChuanTrung bi trung:",
        duplicate_title_count,
    )

    if duplicate_title_count != 0:

        raise RuntimeError(
            "NoiDungChuanTrung "
            "khong con duy nhat."
        )

    print(
        "PASS: 76 ten diem chuan "
        "co the dinh danh rieng."
    )

    # ======================================================
    # 6. TAO WORKLIST
    # ======================================================

    print(
        "\n[6] TAO WORKLIST BIEN SOAN"
    )

    output = []

    for row in rows:

        code = clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )

        source_path = (
            build_source_path(
                row
            )
        )

        if not source_path:

            raise RuntimeError(
                f"{code}: "
                "khong tao duoc DuongDanNguon."
            )

        output.append({

            "MaMucNguPhapChuan":
                code,

            "CapDoHSK":
                4,

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

            "MaNguon":
                1004,

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
                source_path,

            "TenDiemChuanNguon":
                clean(
                    row.get(
                        "NoiDungChuanTrung"
                    )
                ),

            "CanhBaoNguon":
                clean(
                    row.get(
                        "VanDeCanKiemTra"
                    )
                ),

            # Chua duoc tu dong quyet dinh
            # 1 diem chuan = bao nhieu noi dung day.
            "QuyetDinhTachGop":
                "",

            "SoMucGiangDayDeXuat":
                "",

            # Noi dung tieng Viet se bien soan
            # o buoc sau.
            "TenCauTruc":
                "",

            "MoTa":
                "",

            "CachDung":
                "",

            "ViDuTiengTrung":
                "",

            "ViDuPinyin":
                "",

            "ViDuTiengViet":
                "",

            "TrangThaiBienSoan":
                "CHO_BIEN_SOAN",

            "GhiChuBienSoan":
                (
                    "Chua quyet dinh 1:1 "
                    "voi dbo.NguPhap; "
                    "phai dua tren toan bo "
                    "DuongDanNguon GF0025."
                ),
        })

    # ======================================================
    # 7. VALIDATE WORKLIST
    # ======================================================

    if len(output) != EXPECTED_COUNT:

        raise RuntimeError(
            "Worklist khong du 76 muc."
        )

    if len({
        row[
            "MaMucNguPhapChuan"
        ]
        for row in output
    }) != EXPECTED_COUNT:

        raise RuntimeError(
            "Worklist bi trung ID."
        )

    if len({
        normalize(
            row[
                "TenDiemChuanNguon"
            ]
        )
        for row in output
    }) != EXPECTED_COUNT:

        raise RuntimeError(
            "TenDiemChuanNguon "
            "khong duy nhat."
        )

    empty_paths = sum(
        not clean(
            row["DuongDanNguon"]
        )
        for row in output
    )

    if empty_paths:

        raise RuntimeError(
            "Co DuongDanNguon rong."
        )

    statuses = Counter(
        row[
            "TrangThaiBienSoan"
        ]
        for row in output
    )

    print(
        "Tong worklist:",
        len(output),
    )

    print(
        "CHO_BIEN_SOAN:",
        statuses[
            "CHO_BIEN_SOAN"
        ],
    )

    # ======================================================
    # 8. BAO VE OUTPUT
    # ======================================================

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        OUTPUT_FILE,
        output,
    )

    # ======================================================
    # 9. SUMMARY
    # ======================================================

    summary = {

        "status":
            "PASS",

        "cap_do_hsk":
            4,

        "tong_diem_chuan":
            len(output),

        "ma_dau":
            output[0][
                "MaMucNguPhapChuan"
            ],

        "ma_cuoi":
            output[-1][
                "MaMucNguPhapChuan"
            ],

        "muc_co_canh_bao_nguon":
            warning_count,

        "raw_content_rong":
            raw_content_blank,

        "ten_diem_chuan_trung":
            duplicate_title_count,

        "cho_bien_soan":
            statuses[
                "CHO_BIEN_SOAN"
            ],

        "quyet_dinh_1_1_voi_sql":
            False,

        "standard_sha256":
            standard_hash,

        "da_ghi_sql":
            False,

        "ghi_chu":
            (
                "Day la worklist theo "
                "76 diem GF0025 HSK4. "
                "Chua phai 76 dong dbo.NguPhap."
            ),
    }

    if SUMMARY_FILE.exists():

        raise FileExistsError(
            f"Da ton tai file:\n"
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
    # 10. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 78
    )

    print(
        "TAO KHUNG BIEN SOAN HSK4 THANH CONG"
    )

    print("=" * 78)

    print(
        "Tong diem chuan:",
        len(output),
        "/ 76",
    )

    print(
        "Ma:",
        output[0][
            "MaMucNguPhapChuan"
        ],
        "->",
        output[-1][
            "MaMucNguPhapChuan"
        ],
    )

    print(
        "Ten diem chuan trung:",
        duplicate_title_count,
    )

    print(
        "Muc co canh bao nguon:",
        warning_count,
    )

    print(
        "RAW Content rong:",
        raw_content_blank,
    )

    print(
        "Trang thai:",
        statuses[
            "CHO_BIEN_SOAN"
        ],
        "CHO_BIEN_SOAN",
    )

    print(
        "\nWORKLIST:"
    )

    print(
        " ",
        OUTPUT_FILE,
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY_FILE,
    )

    print(
        "\nCHUA QUYET DINH "
        "76 DIEM = 76 DONG SQL."
    )

    print(
        "CHUA BIEN SOAN TIENG VIET."
    )

    print(
        "KHONG THAY DOI SQL."
    )

    print("=" * 78)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)