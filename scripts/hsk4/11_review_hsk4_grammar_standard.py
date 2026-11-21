# -*- coding: utf-8 -*-
"""
BUOC 11 - RA SOAT 76 DIEM NGU PHAP CHUAN HSK4

Nguon:
1. hsk30_grammar_gf0025.csv
2. hsk4_76_grammar_standard.csv

Muc dich:
- Khoa dung snapshot Buoc 10 bang SHA256.
- Bat buoc co dung 76 muc GF4-001 -> GF4-076.
- Doi chieu tung muc voi raw machine-readable source.
- Kiem tra Source No 212 -> 287.
- Kiem tra Level = 4.
- Kiem tra cac truong Group / Category / Details / Content.
- Phat hien ten/noi dung trung trong HSK4.
- Phat hien muc trung hoan toan voi cap 1-3 neu co.
- Danh dau cac muc can bien soan noi dung hoc sau nay.
- Tao CSV review + JSON summary.

KHONG SUA FILE CHUAN.
KHONG TU VIET MO TA / VI DU.
KHONG GHI SQL.
"""

import csv
import hashlib
import json
import re
import unicodedata

from collections import Counter, defaultdict
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

RAW_FILE = (
    GRAMMAR_DIR
    / "hsk30_grammar_gf0025.csv"
)

STANDARD_FILE = (
    GRAMMAR_DIR
    / "hsk4_76_grammar_standard.csv"
)

OUT_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

REVIEW_FILE = (
    OUT_DIR
    / "grammar_hsk4_standard_review.csv"
)

NEED_REVIEW_FILE = (
    OUT_DIR
    / "grammar_hsk4_standard_need_review.csv"
)

SUMMARY_FILE = (
    OUT_DIR
    / "grammar_hsk4_standard_review_summary.json"
)


EXPECTED_COUNT = 76

EXPECTED_RAW_SHA256 = (
    "9a546944af00976a3afb160fe70dd564a"
    "035d36eff82eb275b6aed7ed8a9ccf4"
)

EXPECTED_STANDARD_SHA256 = (
    "e09ed9d3086c38256c610feb93fae58b"
    "94e28c33188f9b0845c639d93b1659c9"
)


OUTPUT_FIELDS = [
    "MaMucNguPhapChuan",
    "CapDoHSK",
    "SoThuTuChuan",
    "SoThuTuNguon",
    "NhomLonTrung",
    "NhomConTrung",
    "TenMucTrung",
    "ChiTietTrung",
    "NoiDungChuanTrung",
    "RawGroup",
    "RawCategory",
    "RawDetails",
    "RawContent",
    "MaNguon",
    "KhopRaw",
    "TrungHoanToanVoiCapThapHon",
    "CapThapHonTrung",
    "CanBienSoanNoiDungHoc",
    "VanDeCanKiemTra",
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
        r"[\s\u3000]+",
        "",
        value,
    )

    value = re.sub(
        r"[，。！？、；：,.!?;:'\"“”‘’"
        r"\(\)（）《》〈〉【】\[\]{}"
        r"—–\-…·]+",
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


def write_csv(
    path,
    rows,
    fields,
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
            fieldnames=fields,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def raw_signature(row):
    """
    Chu ky noi dung mot dong raw.
    Dung de kiem tra muc HSK4 co trung hoan toan
    voi level 1-3 hay khong.
    """

    return (
        normalize(row.get("Group")),
        normalize(row.get("Category")),
        normalize(row.get("Details")),
        normalize(row.get("Content")),
    )


# ==========================================================
# 3. MAIN
# ==========================================================

def main():

    print("=" * 78)
    print("BUOC 11 - RA SOAT 76 DIEM NGU PHAP CHUAN HSK4")
    print("=" * 78)

    print(
        "CHI DOC NGUON - KHONG GHI SQL"
    )

    # ======================================================
    # 1. KIEM TRA SHA256
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT BUOC 10"
    )

    raw_hash = sha256_file(
        RAW_FILE
    )

    standard_hash = sha256_file(
        STANDARD_FILE
    )

    print(
        "RAW SHA256:"
    )
    print(
        raw_hash
    )

    print(
        "STANDARD SHA256:"
    )
    print(
        standard_hash
    )

    if (
        raw_hash
        != EXPECTED_RAW_SHA256
    ):
        raise RuntimeError(
            "RAW source da thay doi sau Buoc 10."
        )

    if (
        standard_hash
        != EXPECTED_STANDARD_SHA256
    ):
        raise RuntimeError(
            "File standard HSK4 da thay doi "
            "sau Buoc 10."
        )

    print(
        "PASS: snapshot Buoc 10 khong thay doi."
    )

    # ======================================================
    # 2. DOC RAW
    # ======================================================

    print(
        "\n[2] DOC RAW GF0025"
    )

    raw_fields, raw_rows = read_csv(
        RAW_FILE
    )

    required_raw = {
        "No",
        "Level",
        "Group",
        "Category",
        "Details",
        "Content",
    }

    missing = (
        required_raw
        - set(raw_fields)
    )

    if missing:
        raise RuntimeError(
            "RAW thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    raw_hsk4 = [
        row
        for row in raw_rows
        if clean(
            row.get("Level")
        ) == "4"
    ]

    print(
        "Tong RAW:",
        len(raw_rows),
    )

    print(
        "RAW Level 4:",
        len(raw_hsk4),
    )

    if (
        len(raw_hsk4)
        != EXPECTED_COUNT
    ):
        raise RuntimeError(
            "RAW Level 4 khong con dung 76 muc."
        )

    # ======================================================
    # 3. INDEX RAW THEO No
    # ======================================================

    raw_by_no = {}

    for row in raw_hsk4:

        no_text = clean(
            row.get("No")
        )

        try:
            source_no = int(
                no_text
            )
        except ValueError:
            raise RuntimeError(
                f"RAW No khong hop le: {no_text}"
            )

        if source_no in raw_by_no:
            raise RuntimeError(
                f"RAW bi trung No={source_no}"
            )

        raw_by_no[
            source_no
        ] = row

    expected_source_numbers = list(
        range(
            212,
            288,
        )
    )

    if (
        sorted(raw_by_no)
        != expected_source_numbers
    ):
        raise RuntimeError(
            "RAW HSK4 khong con lien tuc "
            "No 212 -> 287."
        )

    print(
        "PASS: RAW No 212 -> 287."
    )

    # ======================================================
    # 4. DOC STANDARD
    # ======================================================

    print(
        "\n[3] DOC FILE STANDARD HSK4"
    )

    standard_fields, standard_rows = (
        read_csv(
            STANDARD_FILE
        )
    )

    required_standard = {
        "MaMucNguPhapChuan",
        "CapDoHSK",
        "SoThuTuChuan",
        "SoThuTuNguon",
        "NhomLonTrung",
        "NhomConTrung",
        "TenMucTrung",
        "ChiTietTrung",
        "NoiDungChuanTrung",
        "MaNguon",
        "TrangThaiReview",
        "GhiChu",
    }

    missing = (
        required_standard
        - set(standard_fields)
    )

    if missing:
        raise RuntimeError(
            "STANDARD thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    print(
        "Tong STANDARD:",
        len(standard_rows),
    )

    if (
        len(standard_rows)
        != EXPECTED_COUNT
    ):
        raise RuntimeError(
            "STANDARD khong co dung 76 muc."
        )

    # ======================================================
    # 5. KIEM TRA ID / THU TU
    # ======================================================

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
        for row in standard_rows
    ]

    if actual_ids != expected_ids:
        raise RuntimeError(
            "MaMucNguPhapChuan "
            "khong con GF4-001 -> GF4-076."
        )

    standard_orders = []

    for row in standard_rows:

        try:
            standard_orders.append(
                int(
                    clean(
                        row.get(
                            "SoThuTuChuan"
                        )
                    )
                )
            )
        except ValueError:
            raise RuntimeError(
                "Co SoThuTuChuan khong hop le."
            )

    if standard_orders != list(
        range(
            1,
            EXPECTED_COUNT + 1,
        )
    ):
        raise RuntimeError(
            "SoThuTuChuan khong lien tuc 1 -> 76."
        )

    print(
        "PASS: GF4-001 -> GF4-076."
    )

    # ======================================================
    # 6. TAO INDEX CAP 1-3
    # ======================================================

    lower_level_index = defaultdict(
        list
    )

    for row in raw_rows:

        level = clean(
            row.get("Level")
        )

        if level not in {
            "1",
            "2",
            "3",
        }:
            continue

        lower_level_index[
            raw_signature(row)
        ].append({
            "Level":
                level,

            "No":
                clean(
                    row.get("No")
                ),
        })

    # ======================================================
    # 7. DOI CHIEU 76 MUC
    # ======================================================

    print(
        "\n[4] DOI CHIEU TUNG MUC VOI RAW"
    )

    result = []

    issue_counter = Counter()

    raw_mismatch_count = 0

    for row in standard_rows:

        code = clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )

        level = clean(
            row.get(
                "CapDoHSK"
            )
        )

        source_no_text = clean(
            row.get(
                "SoThuTuNguon"
            )
        )

        if level != "4":
            raise RuntimeError(
                f"{code}: CapDoHSK != 4"
            )

        try:
            source_no = int(
                source_no_text
            )
        except ValueError:
            raise RuntimeError(
                f"{code}: SoThuTuNguon "
                "khong phai so."
            )

        raw = raw_by_no.get(
            source_no
        )

        if raw is None:
            raise RuntimeError(
                f"{code}: khong tim thay "
                f"RAW No={source_no}"
            )

        issues = []

        # ----------------------------------------------
        # Kiem tra field preserved tu raw
        # ----------------------------------------------

        comparisons = [
            (
                "NhomLonTrung",
                "Group",
            ),
            (
                "NhomConTrung",
                "Category",
            ),
            (
                "ChiTietTrung",
                "Details",
            ),
        ]

        mismatched_fields = []

        for standard_field, raw_field in comparisons:

            if (
                clean(
                    row.get(
                        standard_field
                    )
                )
                !=
                clean(
                    raw.get(
                        raw_field
                    )
                )
            ):
                mismatched_fields.append(
                    f"{standard_field}!={raw_field}"
                )

        # NoiDungChuanTrung o Buoc 10 co phep
        # fallback Content -> Details -> Category -> Group.
        expected_content = (
            clean(
                raw.get("Content")
            )
            or
            clean(
                raw.get("Details")
            )
            or
            clean(
                raw.get("Category")
            )
            or
            clean(
                raw.get("Group")
            )
        )

        if (
            clean(
                row.get(
                    "NoiDungChuanTrung"
                )
            )
            != expected_content
        ):
            mismatched_fields.append(
                "NoiDungChuanTrung"
            )

        if mismatched_fields:

            raw_mismatch_count += 1

            issues.append(
                "KHONG_KHOP_RAW:"
                + ",".join(
                    mismatched_fields
                )
            )

            raw_ok = "KHONG"

        else:
            raw_ok = "CO"

        # ----------------------------------------------
        # MaNguon
        # ----------------------------------------------

        if (
            clean(
                row.get("MaNguon")
            )
            != "1004"
        ):
            issues.append(
                "SAI_MA_NGUON"
            )

        # ----------------------------------------------
        # Kiem tra field rong trong raw
        # Day KHONG co nghia source sai.
        # Chi de biet muc nao can dien giai
        # can than o lop noi dung hoc.
        # ----------------------------------------------

        if not clean(
            raw.get("Category")
        ):
            issues.append(
                "RAW_KHONG_CO_CATEGORY"
            )

        if not clean(
            raw.get("Details")
        ):
            issues.append(
                "RAW_KHONG_CO_DETAILS"
            )

        if not clean(
            raw.get("Content")
        ):
            issues.append(
                "RAW_KHONG_CO_CONTENT"
            )

        # ----------------------------------------------
        # Trung hoan toan voi level 1-3?
        # ----------------------------------------------

        lower_matches = (
            lower_level_index.get(
                raw_signature(raw),
                [],
            )
        )

        if lower_matches:

            issues.append(
                "TRUNG_HOAN_TOAN_VOI_CAP_THAP_HON"
            )

            lower_levels = ",".join(
                sorted({
                    item["Level"]
                    for item in lower_matches
                })
            )

            lower_dup = "CO"

        else:

            lower_levels = ""
            lower_dup = "KHONG"

        # ----------------------------------------------
        # Xac dinh muc can bien soan noi dung hoc
        # ----------------------------------------------

        # Tat ca 76 muc deu can lop giang day
        # tieng Viet sau nay. Neu Content raw rong
        # thi can chu y hon vi Buoc 10 dang dung fallback.
        teaching_review = "CO"

        if not clean(
            raw.get("Content")
        ):
            issues.append(
                "CAN_DIEN_GIAI_TU_CAU_TRUC_NHOM"
            )

        for issue in issues:

            issue_name = (
                issue.split(
                    ":",
                    1,
                )[0]
            )

            issue_counter[
                issue_name
            ] += 1

        result.append({

            "MaMucNguPhapChuan":
                code,

            "CapDoHSK":
                level,

            "SoThuTuChuan":
                clean(
                    row.get(
                        "SoThuTuChuan"
                    )
                ),

            "SoThuTuNguon":
                source_no,

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

            "TenMucTrung":
                clean(
                    row.get(
                        "TenMucTrung"
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

            "RawGroup":
                clean(
                    raw.get("Group")
                ),

            "RawCategory":
                clean(
                    raw.get("Category")
                ),

            "RawDetails":
                clean(
                    raw.get("Details")
                ),

            "RawContent":
                clean(
                    raw.get("Content")
                ),

            "MaNguon":
                clean(
                    row.get("MaNguon")
                ),

            "KhopRaw":
                raw_ok,

            "TrungHoanToanVoiCapThapHon":
                lower_dup,

            "CapThapHonTrung":
                lower_levels,

            "CanBienSoanNoiDungHoc":
                teaching_review,

            "VanDeCanKiemTra":
                "; ".join(
                    issues
                ),
        })

    print(
        "Sai khop RAW:",
        raw_mismatch_count,
    )

    if raw_mismatch_count != 0:
        raise RuntimeError(
            "Co muc STANDARD khong khop RAW. "
            "Dung pipeline de kiem tra."
        )

    print(
        "PASS: 76/76 muc khop raw source."
    )

    # ======================================================
    # 8. KIEM TRA TRUNG TEN / NOI DUNG NOI BO HSK4
    # ======================================================

    print(
        "\n[5] KIEM TRA TRUNG NOI BO HSK4"
    )

    title_groups = defaultdict(
        list
    )

    content_groups = defaultdict(
        list
    )

    for row in result:

        title_groups[
            normalize(
                row["TenMucTrung"]
            )
        ].append(
            row[
                "MaMucNguPhapChuan"
            ]
        )

        content_groups[
            normalize(
                row[
                    "NoiDungChuanTrung"
                ]
            )
        ].append(
            row[
                "MaMucNguPhapChuan"
            ]
        )

    duplicate_titles = {
        key: values
        for key, values
        in title_groups.items()
        if (
            key
            and len(values) > 1
        )
    }

    duplicate_contents = {
        key: values
        for key, values
        in content_groups.items()
        if (
            key
            and len(values) > 1
        )
    }

    print(
        "Nhom TenMucTrung trung:",
        len(duplicate_titles),
    )

    print(
        "Nhom NoiDungChuanTrung trung:",
        len(duplicate_contents),
    )

    # Them canh bao vao result.
    title_duplicate_ids = {
        code
        for values
        in duplicate_titles.values()
        for code in values
    }

    content_duplicate_ids = {
        code
        for values
        in duplicate_contents.values()
        for code in values
    }

    for row in result:

        extras = []

        code = row[
            "MaMucNguPhapChuan"
        ]

        if code in title_duplicate_ids:

            extras.append(
                "TEN_MUC_TRUNG_LAP"
            )

        if code in content_duplicate_ids:

            extras.append(
                "NOI_DUNG_CHUAN_TRUNG_LAP"
            )

        if extras:

            old = clean(
                row[
                    "VanDeCanKiemTra"
                ]
            )

            row[
                "VanDeCanKiemTra"
            ] = (
                old
                + ("; " if old else "")
                + "; ".join(
                    extras
                )
            )

            for issue in extras:

                issue_counter[
                    issue
                ] += 1

    # ======================================================
    # 9. THONG KE NHOM CHUAN
    # ======================================================

    group_counts = Counter(
        row[
            "NhomLonTrung"
        ]
        for row in result
    )

    print(
        "\n[6] THONG KE NHOM"
    )

    for name, count in (
        group_counts.items()
    ):

        print(
            f"  {name}: {count}"
        )

    if sum(
        group_counts.values()
    ) != EXPECTED_COUNT:

        raise RuntimeError(
            "Tong nhom khong bang 76."
        )

    # ======================================================
    # 10. REVIEW ROWS
    # ======================================================

    need_review = [
        row
        for row in result
        if clean(
            row[
                "VanDeCanKiemTra"
            ]
        )
    ]

    lower_duplicate_count = sum(
        row[
            "TrungHoanToanVoiCapThapHon"
        ] == "CO"
        for row in result
    )

    raw_content_missing = sum(
        not clean(
            row[
                "RawContent"
            ]
        )
        for row in result
    )

    print(
        "\n[7] THONG KE REVIEW"
    )

    print(
        "Tong muc:",
        len(result),
    )

    print(
        "Muc co canh bao:",
        len(need_review),
    )

    print(
        "RAW Content rong:",
        raw_content_missing,
    )

    print(
        "Trung hoan toan voi cap 1-3:",
        lower_duplicate_count,
    )

    if issue_counter:

        print(
            "\nChi tiet canh bao:"
        )

        for name, count in sorted(
            issue_counter.items()
        ):

            print(
                f"  {name}: {count}"
            )

    # ======================================================
    # 11. XUAT FILE
    # ======================================================

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        REVIEW_FILE,
        result,
        OUTPUT_FIELDS,
    )

    write_csv(
        NEED_REVIEW_FILE,
        need_review,
        OUTPUT_FIELDS,
    )

    summary = {

        "status":
            "PASS",

        "cap_do_hsk":
            4,

        "tong_muc":
            len(result),

        "ma_dau":
            result[0][
                "MaMucNguPhapChuan"
            ],

        "ma_cuoi":
            result[-1][
                "MaMucNguPhapChuan"
            ],

        "source_no_min":
            min(
                int(
                    row[
                        "SoThuTuNguon"
                    ]
                )
                for row in result
            ),

        "source_no_max":
            max(
                int(
                    row[
                        "SoThuTuNguon"
                    ]
                )
                for row in result
            ),

        "khop_raw":
            sum(
                row["KhopRaw"]
                == "CO"
                for row in result
            ),

        "raw_content_rong":
            raw_content_missing,

        "trung_hoan_toan_voi_cap_1_3":
            lower_duplicate_count,

        "nhom_ten_trung":
            len(
                duplicate_titles
            ),

        "nhom_noi_dung_trung":
            len(
                duplicate_contents
            ),

        "muc_co_canh_bao":
            len(
                need_review
            ),

        "thong_ke_nhom":
            dict(
                group_counts
            ),

        "thong_ke_canh_bao":
            dict(
                issue_counter
            ),

        "raw_sha256":
            raw_hash,

        "standard_sha256":
            standard_hash,

        "da_ghi_sql":
            False,

        "ghi_chu":
            (
                "Review source GF0025 Level 4. "
                "Chua bien soan MoTa/CachDung/"
                "ViDu tieng Viet."
            ),
    }

    if SUMMARY_FILE.exists():

        raise FileExistsError(
            "Da ton tai file:\n"
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
    # 12. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 78
    )

    print(
        "RA SOAT NGU PHAP CHUAN HSK4 THANH CONG"
    )

    print("=" * 78)

    print(
        "Tong:",
        len(result),
        "/ 76",
    )

    print(
        "Khop RAW:",
        sum(
            row["KhopRaw"]
            == "CO"
            for row in result
        ),
        "/ 76",
    )

    print(
        "Ma:",
        result[0][
            "MaMucNguPhapChuan"
        ],
        "->",
        result[-1][
            "MaMucNguPhapChuan"
        ],
    )

    print(
        "Source No:",
        summary[
            "source_no_min"
        ],
        "->",
        summary[
            "source_no_max"
        ],
    )

    print(
        "Muc co canh bao:",
        len(need_review),
    )

    print(
        "RAW Content rong:",
        raw_content_missing,
    )

    print(
        "Trung hoan toan voi cap 1-3:",
        lower_duplicate_count,
    )

    print(
        "\nFILE REVIEW:"
    )

    print(
        " ",
        REVIEW_FILE,
    )

    print(
        "\nFILE CAN KIEM TRA:"
    )

    print(
        " ",
        NEED_REVIEW_FILE,
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY_FILE,
    )

    print(
        "\nCHUA BIEN SOAN NOI DUNG HOC."
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