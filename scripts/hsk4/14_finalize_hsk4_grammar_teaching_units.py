# -*- coding: utf-8 -*-
"""
BUOC 14 - CHOT DON VI GIANG DAY NGU PHAP HSK4

Ket qua review thu cong:
- 76 diem chuan GF0025 HSK4.
- 13 diem tach thanh nhieu don vi giang day.
- 63 diem giu 1 don vi.
- Tong cuoi: 114 don vi giang day.

QUAN TRONG:
- 76 van la so DIEM CHUAN GF0025.
- 114 chi la DON VI GIANG DAY cua du an Moc Han.
- Khong gop hai MaMucNguPhapChuan khac nhau.
- Chua bien soan MoTa/CachDung/ViDu.
- Khong ghi SQL.
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
    / "grammar_hsk4_split_merge_analysis.csv"
)

OUTPUT = (
    DATA_DIR
    / "grammar_hsk4_teaching_units_plan.csv"
)

SUMMARY = (
    DATA_DIR
    / "grammar_hsk4_teaching_units_summary.json"
)


EXPECTED_STANDARD_POINTS = 76
EXPECTED_SPLIT_POINTS = 13
EXPECTED_KEEP_POINTS = 63
EXPECTED_SPLIT_UNITS = 51
EXPECTED_TEACHING_UNITS = 114


OUTPUT_FIELDS = [
    "MaDonViGiangDay",
    "MaMucNguPhapChuan",
    "SoThuTuChuan",
    "SoThuTuNguon",

    "ThuTuTrongDiemChuan",
    "SoMucGiangDayCuaDiemChuan",

    "QuyetDinhCuoi",
    "LoaiTach",

    "NhomLonTrung",
    "NhomConTrung",
    "ChiTietTrung",
    "NoiDungChuanTrung",
    "DuongDanNguon",

    "NhanDonViNguonTrung",
    "CanhBaoNguon",

    # Cac cot se bien soan o buoc sau
    "TenCauTruc",
    "MoTa",
    "CachDung",
    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",

    "TrangThaiBienSoan",
    "GhiChu",
]


# ==========================================================
# 2. QUYET DINH TACH THU CONG
# ==========================================================

SPLIT_MAP = {

    # ------------------------------------------------------
    # Danh luong tu
    # ------------------------------------------------------

    "GF4-003": {
        "type": "DANH_LUONG_TU",
        "units": [
            ("打", "打"),
            ("袋", "袋"),
            ("根", "根"),
            ("卷", "卷"),
            ("棵", "棵"),
            ("批", "批"),
        ],
    },

    # ------------------------------------------------------
    # Luong tu vay muon
    # ------------------------------------------------------

    "GF4-004": {
        "type": "LUONG_TU_VAY_MUON",
        "units": [
            ("借用名量词：碗", "碗"),
            ("借用名量词：脸", "脸"),
            ("借用名量词：手", "手"),
            ("借用名量词：屋子", "屋子"),
            ("借用名量词：桌子", "桌子"),
            ("借用动量词：刀", "刀"),
            ("借用动量词：针", "针"),
        ],
    },

    # ------------------------------------------------------
    # Pho tu muc do
    # ------------------------------------------------------

    "GF4-005": {
        "type": "PHO_TU_MUC_DO",
        "units": [
            ("格外", "格外"),
            ("极", "极"),
            ("极其", "极其"),
        ],
    },

    # ------------------------------------------------------
    # Pho tu thoi gian
    # ------------------------------------------------------

    "GF4-007": {
        "type": "PHO_TU_THOI_GIAN",
        "units": [
            ("按时", "按时"),
            ("即将", "即将"),
            ("急忙", "急忙"),
            ("渐渐", "渐渐"),
            ("尽快", "尽快"),
        ],
    },

    # ------------------------------------------------------
    # Pho tu tan suat/lap lai
    # ------------------------------------------------------

    "GF4-008": {
        "type": "PHO_TU_TAN_SUAT",
        "units": [
            ("一再", "一再"),
            ("再三", "再三"),
        ],
    },

    # ------------------------------------------------------
    # Pho tu tinh thai
    # ------------------------------------------------------

    "GF4-011": {
        "type": "PHO_TU_TINH_THAI",
        "units": [
            ("几乎", "几乎"),
            ("似乎", "似乎"),
        ],
    },

    # ------------------------------------------------------
    # Pho tu ngu khi
    # ------------------------------------------------------

    "GF4-012": {
        "type": "PHO_TU_NGU_KHI",
        "units": [
            ("的确", "的确"),
            ("反而", "反而"),
            ("还4", "还4"),
            ("竟然", "竟然"),
            ("究竟", "究竟"),
        ],
    },

    # ------------------------------------------------------
    # Lien tu noi tu/cum tu
    # ------------------------------------------------------

    "GF4-019": {
        "type": "LIEN_TU_TU_CUM_TU",
        "units": [
            ("并2", "并2"),
            ("以及", "以及"),
        ],
    },

    # ------------------------------------------------------
    # Lien tu noi menh de/cau
    # ------------------------------------------------------

    "GF4-020": {
        "type": "LIEN_TU_MENH_DE",
        "units": [
            ("此外", "此外"),
            ("而1", "而1"),
            ("而是", "而是"),
            ("既然", "既然"),
            ("可见", "可见"),
            ("甚至", "甚至"),
            ("假如", "假如"),
            ("总之", "总之"),
        ],
    },

    # ------------------------------------------------------
    # 把字句
    # ------------------------------------------------------

    "GF4-038": {
        "type": "MAU_CAU_BA",
        "units": [
            (
                "“把”字句2（1）："
                "主语+把+宾语+动词（+一/了）+动词",
                "动词（+一/了）+动词",
            ),
            (
                "“把”字句2（2）："
                "主语+把+宾语（+给）+动词+了/着",
                "（+给）+动词+了/着",
            ),
            (
                "“把”字句2（3）："
                "主语+把+宾语+动词+动量补语/时量补语",
                "动量补语/时量补语",
            ),
        ],
    },

    # ------------------------------------------------------
    # 存现句
    # ------------------------------------------------------

    "GF4-040": {
        "type": "CAU_TON_HIEN",
        "units": [
            (
                "存现句2：表示出现",
                "表示出现",
            ),
            (
                "存现句2：表示消失",
                "表示消失",
            ),
        ],
    },

    # ------------------------------------------------------
    # 兼语句
    # ------------------------------------------------------

    "GF4-041": {
        "type": "CAU_KIEM_NGU",
        "units": [
            (
                "兼语句2：表爱憎义",
                "表爱憎义",
            ),
            (
                "兼语句2：表称谓或认定义",
                "表称谓或认定义",
            ),
        ],
    },

    # ------------------------------------------------------
    # Cach bieu dat so
    # ------------------------------------------------------

    "GF4-062": {
        "type": "BIEU_DAT_SO",
        "units": [
            (
                "小数的表示法",
                "小数",
            ),
            (
                "分数的表示法",
                "分数",
            ),
            (
                "百分数的表示法",
                "百分数",
            ),
            (
                "倍数的表示法",
                "倍数",
            ),
        ],
    },
}


# ==========================================================
# 3. 24 MUC RAW CONTENT RONG DA REVIEW THU CONG
#    -> GIU 1 MUC
# ==========================================================

CONTEXT_REVIEW_KEEP = {

    "GF4-022",

    "GF4-029",
    "GF4-030",
    "GF4-031",
    "GF4-032",
    "GF4-033",

    "GF4-034",
    "GF4-035",
    "GF4-036",

    "GF4-061",

    "GF4-063",
    "GF4-064",
    "GF4-065",
    "GF4-066",

    "GF4-067",
    "GF4-068",
    "GF4-069",
    "GF4-070",
    "GF4-071",
    "GF4-072",
    "GF4-073",
    "GF4-074",
    "GF4-075",
    "GF4-076",
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


def compact(value):
    """
    Dung khi check substring.
    Bo khoang trang de tranh source chen space.
    """

    return re.sub(
        r"\s+",
        "",
        str(value or ""),
    )


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
# 5. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 14 - CHOT DON VI GIANG DAY "
        "NGU PHAP HSK4"
    )

    print("=" * 80)

    print(
        "CHI TAO KE HOACH - KHONG GHI SQL"
    )

    # ======================================================
    # 1. DOC BUOC 13
    # ======================================================

    print(
        "\n[1] DOC KET QUA BUOC 13"
    )

    fields, rows = read_csv(
        SOURCE
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

    required = {
        "MaMucNguPhapChuan",
        "SoThuTuChuan",
        "SoThuTuNguon",
        "NhomLonTrung",
        "NhomConTrung",
        "ChiTietTrung",
        "NoiDungChuanTrung",
        "DuongDanNguon",
        "CanhBaoNguon",
        "DeXuatMay",
        "RawContentRong",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        raise RuntimeError(
            "File Buoc 13 thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    print(
        "Tong diem chuan:",
        len(rows),
    )

    if (
        len(rows)
        != EXPECTED_STANDARD_POINTS
    ):

        raise RuntimeError(
            "Buoc 13 khong con dung 76 diem."
        )

    # ======================================================
    # 2. KIEM TRA ID
    # ======================================================

    print(
        "\n[2] KIEM TRA GF4"
    )

    expected_ids = [
        f"GF4-{i:03d}"
        for i in range(
            1,
            EXPECTED_STANDARD_POINTS + 1,
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
            "GF4 khong con "
            "GF4-001 -> GF4-076."
        )

    print(
        "PASS: GF4-001 -> GF4-076."
    )

    # ======================================================
    # 3. KIEM TRA HEURISTIC BUOC 13
    # ======================================================

    print(
        "\n[3] KIEM TRA QUYET DINH REVIEW"
    )

    strong_ids = {
        clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )
        for row in rows
        if clean(
            row.get(
                "DeXuatMay"
            )
        )
        == "CAN_XEM_XET_TACH"
    }

    context_ids = {
        clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )
        for row in rows
        if clean(
            row.get(
                "DeXuatMay"
            )
        )
        == "CAN_REVIEW_NGU_CANH"
    }

    structure_ids = {
        clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )
        for row in rows
        if clean(
            row.get(
                "DeXuatMay"
            )
        )
        == "CAN_REVIEW_CAU_TRUC"
    }

    if strong_ids != set(
        SPLIT_MAP
    ):

        print(
            "Trong file:",
            sorted(strong_ids),
        )

        print(
            "Quyet dinh:",
            sorted(SPLIT_MAP),
        )

        raise RuntimeError(
            "13 ung vien tach manh "
            "khong con khop Buoc 13."
        )

    if (
        context_ids
        != CONTEXT_REVIEW_KEEP
    ):

        print(
            "Trong file:",
            sorted(context_ids),
        )

        print(
            "Da review:",
            sorted(
                CONTEXT_REVIEW_KEEP
            ),
        )

        raise RuntimeError(
            "24 muc review ngu canh "
            "khong con khop."
        )

    if structure_ids:

        raise RuntimeError(
            "Van con CAN_REVIEW_CAU_TRUC "
            "chua duoc xu ly."
        )

    print(
        "PASS: 13 diem tach."
    )

    print(
        "PASS: 24 diem ngu canh "
        "giu 1 muc."
    )

    # ======================================================
    # 4. KIEM TRA CAC FRAGMENT TACH
    # ======================================================

    print(
        "\n[4] KIEM TRA NOI DUNG "
        "CAC DIEM SE TACH"
    )

    row_by_id = {
        clean(
            row[
                "MaMucNguPhapChuan"
            ]
        ):
        row
        for row in rows
    }

    for code, config in (
        SPLIT_MAP.items()
    ):

        row = row_by_id[
            code
        ]

        searchable = compact(
            (
                clean(
                    row.get(
                        "NoiDungChuanTrung"
                    )
                )
                + " "
                + clean(
                    row.get(
                        "DuongDanNguon"
                    )
                )
            )
        )

        for label, required_text in (
            config["units"]
        ):

            if compact(
                required_text
            ) not in searchable:

                raise RuntimeError(
                    f"{code}: "
                    f"khong tim thay fragment "
                    f"{required_text!r}"
                )

        print(
            f"  {code}: "
            f"{len(config['units'])} muc"
        )

    # ======================================================
    # 5. TAO 114 DON VI GIANG DAY
    # ======================================================

    print(
        "\n[5] TAO DON VI GIANG DAY"
    )

    teaching_units = []

    split_points = 0
    keep_points = 0

    split_units = 0

    for row in rows:

        code = clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )

        if code in SPLIT_MAP:

            config = (
                SPLIT_MAP[
                    code
                ]
            )

            units = (
                config["units"]
            )

            split_points += 1

            split_units += len(
                units
            )

            decision = (
                f"TACH_THANH_{len(units)}"
            )

            split_type = (
                config["type"]
            )

        else:

            units = [
                (
                    clean(
                        row.get(
                            "NoiDungChuanTrung"
                        )
                    ),
                    None,
                )
            ]

            keep_points += 1

            decision = (
                "GIU_1_MUC"
            )

            if (
                code
                in CONTEXT_REVIEW_KEEP
            ):

                split_type = (
                    "GIU_SAU_REVIEW_NGU_CANH"
                )

            else:

                split_type = (
                    "KHONG_CAN_TACH"
                )

        total_for_source = len(
            units
        )

        for index, (
            label,
            _fragment,
        ) in enumerate(
            units,
            start=1,
        ):

            teaching_id = (
                f"{code}-T{index:02d}"
            )

            teaching_units.append({

                "MaDonViGiangDay":
                    teaching_id,

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

                "ThuTuTrongDiemChuan":
                    index,

                "SoMucGiangDayCuaDiemChuan":
                    total_for_source,

                "QuyetDinhCuoi":
                    decision,

                "LoaiTach":
                    split_type,

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

                "NhanDonViNguonTrung":
                    clean(label),

                "CanhBaoNguon":
                    clean(
                        row.get(
                            "CanhBaoNguon"
                        )
                    ),

                # ------------------------------------------
                # De trong cho buoc bien soan.
                # ------------------------------------------

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

                "GhiChu":
                    (
                        "Truy vet tu "
                        f"{code}; "
                        "chua gan BaiHoc; "
                        "chua ghi SQL."
                    ),
            })

    # ======================================================
    # 6. VALIDATE SO LUONG
    # ======================================================

    print(
        "\n[6] KIEM TRA SO LUONG CUOI"
    )

    print(
        "Diem chuan giu 1:",
        keep_points,
    )

    print(
        "Diem chuan tach:",
        split_points,
    )

    print(
        "Don vi sinh tu 13 diem tach:",
        split_units,
    )

    print(
        "Tong don vi giang day:",
        len(teaching_units),
    )

    if (
        keep_points
        != EXPECTED_KEEP_POINTS
    ):

        raise RuntimeError(
            "So diem giu 1 "
            "khong bang 63."
        )

    if (
        split_points
        != EXPECTED_SPLIT_POINTS
    ):

        raise RuntimeError(
            "So diem tach "
            "khong bang 13."
        )

    if (
        split_units
        != EXPECTED_SPLIT_UNITS
    ):

        raise RuntimeError(
            "13 diem tach "
            "khong sinh dung 51 muc."
        )

    if (
        len(teaching_units)
        != EXPECTED_TEACHING_UNITS
    ):

        raise RuntimeError(
            "Tong don vi giang day "
            "khong bang 114."
        )

    # ======================================================
    # 7. KIEM TRA MA DON VI
    # ======================================================

    teaching_ids = [
        row[
            "MaDonViGiangDay"
        ]
        for row in teaching_units
    ]

    if len(
        set(teaching_ids)
    ) != EXPECTED_TEACHING_UNITS:

        raise RuntimeError(
            "MaDonViGiangDay bi trung."
        )

    # Moi GF4 phai xuat hien it nhat mot lan.
    mapped_source_ids = {
        row[
            "MaMucNguPhapChuan"
        ]
        for row in teaching_units
    }

    if (
        mapped_source_ids
        != set(expected_ids)
    ):

        raise RuntimeError(
            "Khong phu het 76 GF4."
        )

    # ======================================================
    # 8. THONG KE LOAI
    # ======================================================

    decision_counts = Counter(
        row[
            "QuyetDinhCuoi"
        ]
        for row in teaching_units
    )

    type_counts = Counter(
        row[
            "LoaiTach"
        ]
        for row in teaching_units
    )

    print(
        "PASS: 114 MaDonViGiangDay "
        "duy nhat."
    )

    print(
        "PASS: phu du 76/76 GF4."
    )

    # ======================================================
    # 9. XUAT FILE
    # ======================================================

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        OUTPUT,
        teaching_units,
    )

    output_hash = sha256_file(
        OUTPUT
    )

    summary = {

        "status":
            "PASS",

        "gf0025_hsk4_standard_points":
            EXPECTED_STANDARD_POINTS,

        "diem_giu_1":
            keep_points,

        "diem_tach":
            split_points,

        "don_vi_tu_cac_diem_tach":
            split_units,

        "tong_don_vi_giang_day":
            len(teaching_units),

        "don_vi_tang_them_do_tach":
            (
                len(teaching_units)
                - EXPECTED_STANDARD_POINTS
            ),

        "review_ngu_canh_giu_1":
            len(
                CONTEXT_REVIEW_KEEP
            ),

        "split_point_ids":
            sorted(
                SPLIT_MAP.keys()
            ),

        "source_sha256":
            source_hash,

        "output_sha256":
            output_hash,

        "da_bien_soan_tieng_viet":
            False,

        "da_gan_bai_hoc":
            False,

        "da_ghi_sql":
            False,

        "ghi_chu":
            (
                "76 la diem chuan GF0025 HSK4. "
                "114 la don vi giang day cua "
                "du an Moc Han sau review/tach."
            ),
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
    # 10. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "CHOT DON VI GIANG DAY HSK4 THANH CONG"
    )

    print("=" * 80)

    print(
        "Diem chuan GF0025:",
        EXPECTED_STANDARD_POINTS,
    )

    print(
        "Giu 1 muc:",
        keep_points,
    )

    print(
        "Tach:",
        split_points,
        "diem ->",
        split_units,
        "muc",
    )

    print(
        "Tong don vi giang day:",
        len(teaching_units),
    )

    print(
        "Tang them do tach:",
        len(teaching_units)
        - EXPECTED_STANDARD_POINTS,
    )

    print(
        "\nPLAN:"
    )

    print(
        " ",
        OUTPUT,
    )

    print(
        "\nPLAN SHA256:"
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
        "\n76 = DIEM CHUAN GF0025."
    )

    print(
        "114 = DON VI GIANG DAY MOC HAN."
    )

    print(
        "CHUA BIEN SOAN NOI DUNG TIENG VIET."
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

        print("\nLOI:")
        print(error)

        raise SystemExit(1)