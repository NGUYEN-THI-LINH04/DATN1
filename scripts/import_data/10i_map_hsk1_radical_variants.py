from pathlib import Path
import csv
import sys
from collections import Counter, defaultdict
from contextlib import closing


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# CONFIG
# =========================================================
EXPECTED_HANZI = 301
EXPECTED_EXACT = 209
EXPECTED_VARIANT = 92
EXPECTED_RADICALS = 214
EXPECTED_RAW_VARIANTS = 33


# =========================================================
# INPUT / OUTPUT
# =========================================================
REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

INPUT_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_structure_review.csv"
)

OUTPUT_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_radical_mapped_review.csv"
)

SUMMARY_FILE = (
    REVIEW_DIR
    / "hsk1_radical_variant_mapping_summary.csv"
)

ISSUES_FILE = (
    REVIEW_DIR
    / "hsk1_radical_variant_mapping_issues.csv"
)


# =========================================================
# NORMALIZATION
# =========================================================

# 32 truong hop co the map truc tiep tu dang bien the
# sang bo Khang Hy chuan.
RADICAL_VARIANT_MAP = {

    "讠": "言",
    "亻": "人",
    "辶": "辵",
    "氵": "水",
    "⺮": "竹",

    "王": "玉",
    "刂": "刀",
    "忄": "心",
    "艹": "艸",

    "见": "見",
    "门": "門",
    "饣": "食",
    "⺼": "肉",

    "扌": "手",
    "攵": "攴",
    "灬": "火",
    "纟": "糸",
    "钅": "金",

    "丷": "八",
    "乚": "乙",
    "户": "戶",
    "爫": "爪",
    "耂": "老",

    "西": "襾",
    "覀": "襾",

    "贝": "貝",
    "车": "車",
    "页": "頁",
    "风": "風",
    "飞": "飛",
    "马": "馬",
    "鸟": "鳥",
}


# =========================================================
# 阝 DAC BIET
# =========================================================
#
# 阝 ben trai = 阜
# 阝 ben phai = 邑
#
# Trong 301 chu HSK1 hien tai:
#
# 院 -> 阜
# 那 -> 邑
# 都 -> 邑
#
SPECIAL_FU_YI_MAP = {
    "院": "阜",
    "那": "邑",
    "都": "邑",
}


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


def load_csv(path):

    if not path.exists():

        fail(
            "Khong tim thay file:\n"
            f"{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:

            fail(
                "Khong doc duoc header CSV."
            )

        return (
            reader.fieldnames,
            list(reader),
        )


def write_csv(
    path,
    fieldnames,
    rows,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10I - MAP RADICAL BIEN THE "
        "VAO 214 BO THU KHANG HY"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  GIU NGUYEN 209 CHU DA MAP EXACT")
    print("  MAP 92 CHU CON LAI")
    print("  XU LY RIENG 阝 BEN TRAI / BEN PHAI")
    print("  DOI CHIEU MaBoThu TRONG DATABASE")
    print("  TAO FILE REVIEW 301 CHU")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  KHONG SUA FILE 10G")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")

    # =====================================================
    # 1. READ 10G
    # =====================================================
    print()
    print("[1] DOC FILE 10G")
    print("-" * 120)

    fields, rows = load_csv(
        INPUT_FILE
    )

    required_fields = {
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "MaBaiHoc",
        "TieuDeBai",
        "TuVungDauTien",
        "PinyinNguonRaw",
        "DefinitionEnglishNguon",
        "RadicalNguon",
        "MaBoThuDeXuat",
        "TenBoThuSQL",
        "YNghiaBoThuSQL",
        "KiemTraBoThu",
        "DecompositionNguon",
        "SoNetNguon",
        "SoMedianNguon",
        "KiemTraStrokeMedian",
        "DaCoTrongChuHan",
        "MaChuHanHienTai",
        "MaBoThuSQLHienTai",
        "SoNetSQLHienTai",
    }

    missing_fields = (
        required_fields
        - set(fields)
    )

    if missing_fields:

        fail(
            "File 10G thieu cot: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if len(rows) != EXPECTED_HANZI:

        fail(
            "File 10G khong co "
            "dung 301 dong."
        )

    exact_rows = [
        row
        for row in rows
        if clean(
            row["KiemTraBoThu"]
        ) == "OK"
    ]

    unmapped_rows = [
        row
        for row in rows
        if clean(
            row["KiemTraBoThu"]
        ) != "OK"
    ]

    print(
        "Tong Chu Han:",
        len(rows),
    )

    print(
        "Exact map tu 10G:",
        len(exact_rows),
    )

    print(
        "Can map variant:",
        len(unmapped_rows),
    )

    if len(exact_rows) != EXPECTED_EXACT:

        fail(
            "Exact map khong con 209."
        )

    if len(unmapped_rows) != EXPECTED_VARIANT:

        fail(
            "Variant khong con 92."
        )

    raw_variants = {
        clean(
            row["RadicalNguon"]
        )
        for row in unmapped_rows
    }

    print(
        "RadicalNguon khac nhau:",
        len(raw_variants),
    )

    if (
        len(raw_variants)
        != EXPECTED_RAW_VARIANTS
    ):

        fail(
            "Khong con dung "
            "33 RadicalNguon."
        )

    # =====================================================
    # 2. VERIFY EXPECTED RAW RADICAL SET
    # =====================================================
    print()
    print(
        "[2] KIEM TRA 33 RadicalNguon"
    )
    print("-" * 120)

    expected_raw = (
        set(
            RADICAL_VARIANT_MAP.keys()
        )
        | {"阝"}
    )

    unexpected = (
        raw_variants
        - expected_raw
    )

    missing_expected = (
        expected_raw
        - raw_variants
    )

    print(
        "Variant mong doi:",
        len(expected_raw),
    )

    print(
        "Variant la:",
        len(unexpected),
    )

    print(
        "Variant mong doi "
        "nhung khong con trong du lieu:",
        len(missing_expected),
    )

    if unexpected:

        print(
            "Variant la:",
            " ".join(
                sorted(unexpected)
            ),
        )

        fail(
            "Co RadicalNguon "
            "chua duoc dinh nghia mapping."
        )

    if missing_expected:

        print(
            "Khong con gap:",
            " ".join(
                sorted(missing_expected)
            ),
        )

        fail(
            "Tap RadicalNguon "
            "khac ket qua 10H."
        )

    print(
        "33/33 RADICAL RAW: OK"
    )

    # =====================================================
    # 3. READ BoThu
    # =====================================================
    print()
    print(
        "[3] DOC 214 BoThu"
    )
    print("-" * 120)

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    "SELECT DB_NAME();"
                )

                db_name = clean(
                    cursor.fetchone()[0]
                )

                if (
                    db_name.lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                cursor.execute(
                    """
                    SELECT
                        MaBoThu,
                        SoBoThu,
                        KyHieu,
                        TenBoThu,
                        YNghia,
                        SoNet,
                        MaNguon,
                        TrangThai
                    FROM dbo.BoThu
                    ORDER BY MaBoThu;
                    """
                )

                radical_rows = (
                    cursor.fetchall()
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    if (
        len(radical_rows)
        != EXPECTED_RADICALS
    ):

        fail(
            "BoThu SQL khong bang 214."
        )

    sql_radical_map = defaultdict(
        list
    )

    for row in radical_rows:

        record = {
            "MaBoThu": int(row[0]),
            "SoBoThu": int(row[1]),
            "KyHieu": clean(row[2]),
            "TenBoThu": clean(row[3]),
            "YNghia": clean(row[4]),
            "SoNet": row[5],
            "MaNguon": row[6],
            "TrangThai": clean(row[7]),
        }

        sql_radical_map[
            record["KyHieu"]
        ].append(
            record
        )

    print(
        "BoThu SQL:",
        len(radical_rows),
    )

    print(
        "KyHieu khac nhau:",
        len(sql_radical_map),
    )

    duplicates = {
        key: items
        for key, items
        in sql_radical_map.items()
        if len(items) > 1
    }

    if duplicates:

        fail(
            "BoThu SQL co KyHieu bi trung."
        )

    # =====================================================
    # 4. VERIFY ALL TARGET RADICALS EXIST
    # =====================================================
    print()
    print(
        "[4] KIEM TRA BO THU CHUAN "
        "CO TON TAI TRONG SQL"
    )
    print("-" * 120)

    target_radicals = (
        set(
            RADICAL_VARIANT_MAP.values()
        )
        | {"阜", "邑"}
    )

    missing_targets = []

    for radical in sorted(
        target_radicals
    ):

        matches = (
            sql_radical_map.get(
                radical,
                [],
            )
        )

        if len(matches) != 1:

            missing_targets.append(
                radical
            )

            print(
                "KHONG KHOP:",
                radical,
                "=>",
                len(matches),
            )

        else:

            item = matches[0]

            print(
                f"{radical} "
                f"=> MaBoThu="
                f"{item['MaBoThu']} "
                f"| SoBoThu="
                f"{item['SoBoThu']} "
                f"| {item['TenBoThu']}"
            )

    if missing_targets:

        fail(
            "Co bo thu chuan "
            "khong ton tai duy nhat "
            "trong SQL."
        )

    print()
    print(
        "CAC BO THU DICH DEU TON TAI: OK"
    )

    # =====================================================
    # 5. MAP 301 ROWS
    # =====================================================
    print()
    print(
        "[5] MAP 301 CHU"
    )
    print("-" * 120)

    output_rows = []

    issues = []

    mapping_type_counts = Counter()

    variant_summary = defaultdict(
        lambda: {
            "count": 0,
            "chars": [],
            "targets": set(),
        }
    )

    total_ok = 0

    for row in rows:

        char = clean(
            row["KyTu"]
        )

        source_radical = clean(
            row["RadicalNguon"]
        )

        old_status = clean(
            row["KiemTraBoThu"]
        )

        # -----------------------------------------
        # EXACT FROM 10G
        # -----------------------------------------
        if old_status == "OK":

            target_radical = (
                source_radical
            )

            mapping_type = (
                "EXACT"
            )

        # -----------------------------------------
        # SPECIAL 阝
        # -----------------------------------------
        elif source_radical == "阝":

            if (
                char
                not in SPECIAL_FU_YI_MAP
            ):

                issues.append(
                    {
                        "KyTu": char,
                        "RadicalNguon": (
                            source_radical
                        ),
                        "VanDe": (
                            "CHUA_DINH_NGHIA_"
                            "TRAI_PHAI_CHO 阝"
                        ),
                        "ChiTiet": "",
                    }
                )

                target_radical = ""
                mapping_type = (
                    "SPECIAL_FAIL"
                )

            else:

                target_radical = (
                    SPECIAL_FU_YI_MAP[
                        char
                    ]
                )

                mapping_type = (
                    "SPECIAL_阝"
                )

        # -----------------------------------------
        # NORMAL VARIANT
        # -----------------------------------------
        else:

            target_radical = (
                RADICAL_VARIANT_MAP.get(
                    source_radical,
                    "",
                )
            )

            mapping_type = (
                "VARIANT"
            )

        # -----------------------------------------
        # SQL lookup
        # -----------------------------------------
        sql_match = []

        if target_radical:

            sql_match = (
                sql_radical_map.get(
                    target_radical,
                    [],
                )
            )

        if len(sql_match) == 1:

            radical_record = (
                sql_match[0]
            )

            map_status = "OK"

            total_ok += 1

            ma_bo_thu = (
                radical_record[
                    "MaBoThu"
                ]
            )

            so_bo_thu = (
                radical_record[
                    "SoBoThu"
                ]
            )

            radical_name = (
                radical_record[
                    "TenBoThu"
                ]
            )

            radical_meaning = (
                radical_record[
                    "YNghia"
                ]
            )

        else:

            map_status = (
                "KHONG_MAP_DUOC"
            )

            ma_bo_thu = ""
            so_bo_thu = ""
            radical_name = ""
            radical_meaning = ""

            issues.append(
                {
                    "KyTu": char,
                    "RadicalNguon": (
                        source_radical
                    ),
                    "VanDe": (
                        "KHONG_MAP_DUOC_SQL"
                    ),
                    "ChiTiet": (
                        f"Target="
                        f"{target_radical}; "
                        f"Matches="
                        f"{len(sql_match)}"
                    ),
                }
            )

        mapping_type_counts[
            mapping_type
        ] += 1

        if (
            old_status != "OK"
        ):

            group = (
                variant_summary[
                    source_radical
                ]
            )

            group["count"] += 1

            group["chars"].append(
                char
            )

            if target_radical:

                group["targets"].add(
                    target_radical
                )

        # -----------------------------------------
        # Existing SQL safety check
        # -----------------------------------------
        current_radical = clean(
            row[
                "MaBoThuSQLHienTai"
            ]
        )

        current_check = ""

        if (
            clean(
                row[
                    "DaCoTrongChuHan"
                ]
            ) == "1"
        ):

            if (
                current_radical
                == str(
                    ma_bo_thu
                )
            ):

                current_check = "OK"

            else:

                current_check = (
                    "LECH"
                )

                issues.append(
                    {
                        "KyTu": char,
                        "RadicalNguon": (
                            source_radical
                        ),
                        "VanDe": (
                            "LECH_BOTHU_"
                            "CHUHAN_HIEN_CO"
                        ),
                        "ChiTiet": (
                            f"SQL="
                            f"{current_radical}; "
                            f"Mapped="
                            f"{ma_bo_thu}"
                        ),
                    }
                )

        # -----------------------------------------
        # OUTPUT
        # -----------------------------------------
        output_rows.append(
            {
                "KyTu": char,

                "PhamVi": clean(
                    row["PhamVi"]
                ),

                "BaiXuatHienDau": clean(
                    row[
                        "BaiXuatHienDau"
                    ]
                ),

                "MaBaiHoc": clean(
                    row["MaBaiHoc"]
                ),

                "TieuDeBai": clean(
                    row["TieuDeBai"]
                ),

                "TuVungDauTien": clean(
                    row[
                        "TuVungDauTien"
                    ]
                ),

                "PinyinNguonRaw": clean(
                    row[
                        "PinyinNguonRaw"
                    ]
                ),

                "DefinitionEnglishNguon": clean(
                    row[
                        "DefinitionEnglishNguon"
                    ]
                ),

                "RadicalNguon": (
                    source_radical
                ),

                "RadicalChuan": (
                    target_radical
                ),

                "LoaiMappingBoThu": (
                    mapping_type
                ),

                "MaBoThuChuan": (
                    ma_bo_thu
                ),

                "SoBoThuChuan": (
                    so_bo_thu
                ),

                "TenBoThuChuan": (
                    radical_name
                ),

                "YNghiaBoThuChuan": (
                    radical_meaning
                ),

                "KiemTraMappingBoThu": (
                    map_status
                ),

                "DecompositionNguon": clean(
                    row[
                        "DecompositionNguon"
                    ]
                ),

                "SoNetNguon": clean(
                    row[
                        "SoNetNguon"
                    ]
                ),

                "SoMedianNguon": clean(
                    row[
                        "SoMedianNguon"
                    ]
                ),

                "KiemTraStrokeMedian": clean(
                    row[
                        "KiemTraStrokeMedian"
                    ]
                ),

                "DaCoTrongChuHan": clean(
                    row[
                        "DaCoTrongChuHan"
                    ]
                ),

                "MaChuHanHienTai": clean(
                    row[
                        "MaChuHanHienTai"
                    ]
                ),

                "MaBoThuSQLHienTai": (
                    current_radical
                ),

                "KiemTraBoThuHienTai": (
                    current_check
                ),

                "SanSangMappingBoThu": (
                    1
                    if map_status
                    == "OK"
                    else 0
                ),

                "DaKiemDuyetMappingBoThu": 0,

                "GhiChuKiemDuyet": "",
            }
        )

    # =====================================================
    # 6. SUMMARY OF 33 RAW VARIANTS
    # =====================================================
    print()
    print(
        "[6] KET QUA MAPPING 33 VARIANT"
    )
    print("-" * 120)

    summary_rows = []

    for source_radical in sorted(
        variant_summary,
        key=lambda key: (
            -variant_summary[
                key
            ]["count"],
            key,
        ),
    ):

        data = (
            variant_summary[
                source_radical
            ]
        )

        targets = sorted(
            data["targets"]
        )

        print(
            f"{source_radical!r:<6} "
            f"| SoChu="
            f"{data['count']:>2} "
            f"| Target="
            f"{' / '.join(targets)} "
            f"| Chu="
            f"{''.join(data['chars'])}"
        )

        summary_rows.append(
            {
                "RadicalNguon": (
                    source_radical
                ),

                "SoChu": (
                    data["count"]
                ),

                "DanhSachChu": (
                    " ".join(
                        data["chars"]
                    )
                ),

                "RadicalChuan": (
                    " / ".join(
                        targets
                    )
                ),

                "LoaiMapping": (
                    (
                        "THEO_VI_TRI"
                        if source_radical
                        == "阝"
                        else "BIEN_THE"
                    )
                ),

                "DaKiemDuyet": 0,

                "GhiChu": (
                    (
                        "阝 trai -> 阜; "
                        "阝 phai -> 邑"
                    )
                    if source_radical
                    == "阝"
                    else ""
                ),
            }
        )

    # =====================================================
    # 7. WRITE FILES
    # =====================================================
    print()
    print(
        "[7] GHI FILE REVIEW"
    )
    print("-" * 120)

    write_csv(
        OUTPUT_FILE,
        [
            "KyTu",
            "PhamVi",
            "BaiXuatHienDau",
            "MaBaiHoc",
            "TieuDeBai",
            "TuVungDauTien",
            "PinyinNguonRaw",
            "DefinitionEnglishNguon",
            "RadicalNguon",
            "RadicalChuan",
            "LoaiMappingBoThu",
            "MaBoThuChuan",
            "SoBoThuChuan",
            "TenBoThuChuan",
            "YNghiaBoThuChuan",
            "KiemTraMappingBoThu",
            "DecompositionNguon",
            "SoNetNguon",
            "SoMedianNguon",
            "KiemTraStrokeMedian",
            "DaCoTrongChuHan",
            "MaChuHanHienTai",
            "MaBoThuSQLHienTai",
            "KiemTraBoThuHienTai",
            "SanSangMappingBoThu",
            "DaKiemDuyetMappingBoThu",
            "GhiChuKiemDuyet",
        ],
        output_rows,
    )

    write_csv(
        SUMMARY_FILE,
        [
            "RadicalNguon",
            "SoChu",
            "DanhSachChu",
            "RadicalChuan",
            "LoaiMapping",
            "DaKiemDuyet",
            "GhiChu",
        ],
        summary_rows,
    )

    write_csv(
        ISSUES_FILE,
        [
            "KyTu",
            "RadicalNguon",
            "VanDe",
            "ChiTiet",
        ],
        issues,
    )

    print(
        "Mapped review:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "Mapping summary:"
    )

    print(
        SUMMARY_FILE
    )

    print()
    print(
        "Issues:"
    )

    print(
        ISSUES_FILE
    )

    # =====================================================
    # 8. FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10I"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(output_rows),
    )

    print(
        "Exact:",
        mapping_type_counts[
            "EXACT"
        ],
    )

    print(
        "Variant:",
        mapping_type_counts[
            "VARIANT"
        ],
    )

    print(
        "Special 阝:",
        mapping_type_counts[
            "SPECIAL_阝"
        ],
    )

    print(
        "Map BoThu OK:",
        total_ok,
        "/301",
    )

    print(
        "Tong issue:",
        len(issues),
    )

    existing_checks = [
        row
        for row in output_rows
        if row[
            "DaCoTrongChuHan"
        ] == "1"
    ]

    existing_ok = sum(
        1
        for row in existing_checks
        if row[
            "KiemTraBoThuHienTai"
        ] == "OK"
    )

    print(
        "17 ChuHan hien co "
        "khop mapping:",
        existing_ok,
        "/17",
    )

    print()
    print(
        "DaKiemDuyetMappingBoThu=1:",
        0,
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "FILE 10G KHONG BI SUA."
    )

    print(
        "CHUA INSERT ChuHan."
    )

    print(
        "CHUA INSERT NetChuHan."
    )

    print()
    print(
        "BUOC TIEP THEO:"
    )

    print(
        "NEU MAP DAT 301/301 VA ISSUE=0, "
        "CHUYEN SANG CHUAN HOA PINYIN "
        "VA NGHIA TIENG VIET CUA 301 CHU."
    )

    print()
    print("=" * 120)
    print("HOAN TAT")
    print("=" * 120)


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 120)
        print(
            "10I THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)