from pathlib import Path
import csv
import sys
from collections import defaultdict
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
CC_CEDICT_SOURCE_ID = 2
CVDICT_SOURCE_ID = 1003

EXPECTED_MISSING = 98

SPECIAL_CHARS = {
    "呢",
    "了",
    "干",
    "地",
    "还",
    "识",
}


# =========================================================
# FILES
# =========================================================
REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

MISSING_INPUT = (
    REVIEW_DIR
    / "hsk1_98_hanzi_missing_vietnamese_source.csv"
)

SPECIAL_INPUT = (
    REVIEW_DIR
    / "hsk1_hanzi_language_special_cases.csv"
)

OUTPUT_SUMMARY = (
    REVIEW_DIR
    / "hsk1_98_hanzi_dictionary_source_summary.csv"
)

OUTPUT_CANDIDATES = (
    REVIEW_DIR
    / "hsk1_hanzi_dictionary_candidates.csv"
)

OUTPUT_SPECIAL = (
    REVIEW_DIR
    / "hsk1_hanzi_dictionary_special_cases.csv"
)


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
                f"Khong doc duoc header:\n{path}"
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


def join_unique(values):

    result = []

    seen = set()

    for value in values:

        value = clean(value)

        if not value:
            continue

        if value in seen:
            continue

        seen.add(value)
        result.append(value)

    return " | ".join(result)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10L - AUDIT CVDICT / CC-CEDICT "
        "CHO 98 CHU HAN CON THIEU NGHIA VIET"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  CHI XU LY 98 CHU CHUA CO NGHIA VIET TU TuVung DON")
    print("  KIEM TRA MucTuDien MaNguon=1003 CVDICT")
    print("  KIEM TRA MucTuDien MaNguon=2 CC-CEDICT")
    print("  DOI CHIEU CAC TRUONG HOP PINYIN DAC BIET")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  KHONG TU DONG CHON NGHIA")
    print("  KHONG TU DONG PHE DUYET CVDICT")
    print("  KHONG UPDATE")
    print("  KHONG INSERT")
    print("  KHONG DELETE")

    # =====================================================
    # 1. READ 98 MISSING
    # =====================================================
    print()
    print("[1] DOC DANH SACH 98 CHU")
    print("-" * 120)

    missing_fields, missing_rows = load_csv(
        MISSING_INPUT
    )

    required_missing = {
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "TieuDeBai",
        "TuVungDauTien",
        "PinyinNguonRaw",
        "DefinitionEnglishNguon",
    }

    absent = (
        required_missing
        - set(missing_fields)
    )

    if absent:

        fail(
            "File 10K thieu cot: "
            + ", ".join(
                sorted(absent)
            )
        )

    if len(missing_rows) != EXPECTED_MISSING:

        fail(
            "Danh sach missing "
            "khong con bang 98."
        )

    missing_chars = [
        clean(row["KyTu"])
        for row in missing_rows
    ]

    if len(set(missing_chars)) != 98:

        fail(
            "98 dong nhung KyTu "
            "khong duy nhat."
        )

    missing_map = {
        clean(row["KyTu"]): row
        for row in missing_rows
    }

    print(
        "Chu thieu nguon nghia Viet:",
        len(missing_chars),
    )

    # =====================================================
    # 2. READ SPECIAL CASES
    # =====================================================
    print()
    print("[2] DOC SPECIAL CASES 10K")
    print("-" * 120)

    special_fields, special_rows = load_csv(
        SPECIAL_INPUT
    )

    required_special = {
        "KyTu",
        "LoaiTruongHop",
        "PinyinNguon",
        "PinyinTuVung",
        "PinyinChuHanHienTai",
        "NghiaVietTuVung",
        "NghiaChuHanHienTai",
        "BaiXuatHienDau",
        "TuVungDauTien",
    }

    absent_special = (
        required_special
        - set(special_fields)
    )

    if absent_special:

        fail(
            "Special file thieu cot: "
            + ", ".join(
                sorted(absent_special)
            )
        )

    actual_special_chars = {
        clean(row["KyTu"])
        for row in special_rows
    }

    print(
        "KyTu dac biet trong file:",
        " ".join(
            sorted(actual_special_chars)
        ),
    )

    # 识 co the da xuat hien trong special.
    # Dam bao query dictionary co du 6 chu can audit.
    audit_chars = (
        set(missing_chars)
        | SPECIAL_CHARS
    )

    print(
        "Tong KyTu se query MucTuDien:",
        len(audit_chars),
    )

    # =====================================================
    # 3. DATABASE + SCHEMA
    # =====================================================
    print()
    print("[3] KIEM TRA DATABASE")
    print("-" * 120)

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        DB_NAME(),
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        );
                    """
                )

                db_name, server_name = (
                    cursor.fetchone()
                )

                print(
                    "Server:",
                    clean(server_name),
                )

                print(
                    "Database:",
                    clean(db_name),
                )

                if (
                    clean(db_name).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi "
                        "nham database."
                    )

                # =========================================
                # Schema MucTuDien
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE
                        TABLE_SCHEMA = 'dbo'
                        AND TABLE_NAME = 'MucTuDien'
                    ORDER BY ORDINAL_POSITION;
                    """
                )

                columns = [
                    clean(row[0])
                    for row in cursor.fetchall()
                ]

                required_columns = {
                    "MaMucTu",
                    "MaNguon",
                    "MaNguonBenNgoai",
                    "ChuHan",
                    "PhienAm",
                    "NghiaGoc",
                    "NgonNguNghiaGoc",
                    "NghiaTiengViet",
                    "NghiaVietDaDuyet",
                }

                missing_columns = (
                    required_columns
                    - set(columns)
                )

                if missing_columns:

                    fail(
                        "MucTuDien thieu cot: "
                        + ", ".join(
                            sorted(
                                missing_columns
                            )
                        )
                    )

                print(
                    "SCHEMA MucTuDien: OK"
                )

                # =========================================
                # Sources
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten,
                        LienKetNguon,
                        GiayPhep,
                        GhiChu
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon IN (?, ?)
                    ORDER BY MaNguon;
                    """,
                    CC_CEDICT_SOURCE_ID,
                    CVDICT_SOURCE_ID,
                )

                source_rows = (
                    cursor.fetchall()
                )

                source_map = {
                    int(row[0]): {
                        "Ten": clean(row[1]),
                        "LienKet": clean(row[2]),
                        "GiayPhep": clean(row[3]),
                        "GhiChu": clean(row[4]),
                    }
                    for row in source_rows
                }

                if (
                    CC_CEDICT_SOURCE_ID
                    not in source_map
                ):

                    fail(
                        "Khong tim thay "
                        "MaNguon=2 CC-CEDICT."
                    )

                if (
                    CVDICT_SOURCE_ID
                    not in source_map
                ):

                    fail(
                        "Khong tim thay "
                        "MaNguon=1003 CVDICT."
                    )

                print(
                    "MaNguon=2:",
                    source_map[2]["Ten"],
                )

                print(
                    "MaNguon=1003:",
                    source_map[1003]["Ten"],
                )

                # =========================================
                # Overall source counts
                # =========================================
                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        COUNT(*) AS SoDong,
                        SUM(
                            CASE
                                WHEN NULLIF(
                                    LTRIM(
                                        RTRIM(
                                            NghiaTiengViet
                                        )
                                    ),
                                    N''
                                ) IS NOT NULL
                                THEN 1
                                ELSE 0
                            END
                        ) AS CoNghiaViet,
                        SUM(
                            CASE
                                WHEN NghiaVietDaDuyet = 1
                                THEN 1
                                ELSE 0
                            END
                        ) AS DaDuyet
                    FROM dbo.MucTuDien
                    WHERE MaNguon IN (?, ?)
                    GROUP BY MaNguon
                    ORDER BY MaNguon;
                    """,
                    CC_CEDICT_SOURCE_ID,
                    CVDICT_SOURCE_ID,
                )

                overall_source_rows = (
                    cursor.fetchall()
                )

                print()
                print(
                    "Tinh trang MucTuDien "
                    "theo nguon:"
                )

                overall_map = {}

                for row in overall_source_rows:

                    source_id = int(row[0])

                    overall_map[
                        source_id
                    ] = {
                        "rows": int(row[1]),
                        "viet": int(
                            row[2] or 0
                        ),
                        "approved": int(
                            row[3] or 0
                        ),
                    }

                    print(
                        f"MaNguon={source_id} "
                        f"| Dong={row[1]} "
                        f"| CoNghiaViet="
                        f"{row[2] or 0} "
                        f"| DaDuyet="
                        f"{row[3] or 0}"
                    )

                # =========================================
                # Exact single-character entries
                # =========================================
                ordered_audit_chars = sorted(
                    audit_chars
                )

                placeholders = ",".join(
                    "?"
                    for _ in ordered_audit_chars
                )

                sql = f"""
                    SELECT
                        MaMucTu,
                        MaNguon,
                        MaNguonBenNgoai,
                        ChuHan,
                        PhienAm,
                        NghiaGoc,
                        NgonNguNghiaGoc,
                        NghiaTiengViet,
                        NghiaVietDaDuyet
                    FROM dbo.MucTuDien
                    WHERE
                        LEN(ChuHan) = 1
                        AND ChuHan IN (
                            {placeholders}
                        )
                        AND MaNguon IN (?, ?)
                    ORDER BY
                        ChuHan,
                        MaNguon,
                        MaMucTu;
                """

                params = (
                    ordered_audit_chars
                    + [
                        CC_CEDICT_SOURCE_ID,
                        CVDICT_SOURCE_ID,
                    ]
                )

                cursor.execute(
                    sql,
                    *params,
                )

                dictionary_rows = (
                    cursor.fetchall()
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 4. BUILD INDEX
    # =====================================================
    print()
    print("[4] PHAN TICH KET QUA TU DIEN")
    print("-" * 120)

    entries_by_char = defaultdict(
        list
    )

    raw_candidate_rows = []

    for row in dictionary_rows:

        record = {
            "MaMucTu": int(row[0]),
            "MaNguon": int(row[1]),
            "MaNguonBenNgoai": clean(
                row[2]
            ),
            "ChuHan": clean(row[3]),
            "PhienAm": clean(row[4]),
            "NghiaGoc": clean(row[5]),
            "NgonNguNghiaGoc": clean(
                row[6]
            ),
            "NghiaTiengViet": clean(
                row[7]
            ),
            "NghiaVietDaDuyet": int(
                row[8]
            ),
        }

        entries_by_char[
            record["ChuHan"]
        ].append(
            record
        )

        raw_candidate_rows.append(
            {
                **record,
                "TenNguon": (
                    source_map[
                        record["MaNguon"]
                    ]["Ten"]
                ),
            }
        )

    print(
        "Tong muc tu tim thay:",
        len(dictionary_rows),
    )

    print(
        "So KyTu co it nhat "
        "1 muc tu:",
        len(entries_by_char),
    )

    # =====================================================
    # 5. 98-CHAR SUMMARY
    # =====================================================
    print()
    print(
        "[5] COVERAGE CUA 98 CHU"
    )
    print("-" * 120)

    summary_rows = []

    cvdict_any = 0
    cvdict_viet = 0
    cvdict_approved = 0

    cedict_any = 0

    no_dictionary = 0

    for char in missing_chars:

        original = (
            missing_map[char]
        )

        entries = (
            entries_by_char.get(
                char,
                [],
            )
        )

        cvdict_entries = [
            item
            for item in entries
            if item["MaNguon"]
            == CVDICT_SOURCE_ID
        ]

        cedict_entries = [
            item
            for item in entries
            if item["MaNguon"]
            == CC_CEDICT_SOURCE_ID
        ]

        cvdict_viet_entries = [
            item
            for item in cvdict_entries
            if item["NghiaTiengViet"]
        ]

        cvdict_approved_entries = [
            item
            for item in cvdict_entries
            if (
                item[
                    "NghiaTiengViet"
                ]
                and item[
                    "NghiaVietDaDuyet"
                ] == 1
            )
        ]

        if cvdict_entries:
            cvdict_any += 1

        if cvdict_viet_entries:
            cvdict_viet += 1

        if cvdict_approved_entries:
            cvdict_approved += 1

        if cedict_entries:
            cedict_any += 1

        if not entries:
            no_dictionary += 1

        # -----------------------------------------
        # Khong tu dong phe duyet.
        # -----------------------------------------
        if cvdict_approved_entries:

            status = (
                "CVDICT_CO_NGHIA_DA_DUYET"
            )

        elif cvdict_viet_entries:

            status = (
                "CVDICT_CO_NGHIA_CHUA_DUYET"
            )

        elif cvdict_entries:

            status = (
                "CVDICT_CO_MUC_NHUNG_CHUA_CO_NGHIA_VIET"
            )

        elif cedict_entries:

            status = (
                "CHI_CO_CC_CEDICT_NGHIA_ANH"
            )

        else:

            status = (
                "KHONG_CO_MUC_TU_DON"
            )

        summary_rows.append(
            {
                "KyTu": char,

                "PhamVi": clean(
                    original["PhamVi"]
                ),

                "BaiXuatHienDau": clean(
                    original[
                        "BaiXuatHienDau"
                    ]
                ),

                "TieuDeBai": clean(
                    original[
                        "TieuDeBai"
                    ]
                ),

                "TuVungDauTien": clean(
                    original[
                        "TuVungDauTien"
                    ]
                ),

                "PinyinMakeMeAHanzi": clean(
                    original[
                        "PinyinNguonRaw"
                    ]
                ),

                "DefinitionEnglishMakeMeAHanzi": clean(
                    original[
                        "DefinitionEnglishNguon"
                    ]
                ),

                "SoMucCVDICT": (
                    len(
                        cvdict_entries
                    )
                ),

                "PinyinCVDICT": (
                    join_unique(
                        item["PhienAm"]
                        for item
                        in cvdict_entries
                    )
                ),

                "NghiaVietCVDICT": (
                    " || ".join(
                        item[
                            "NghiaTiengViet"
                        ]
                        for item
                        in cvdict_viet_entries
                    )
                ),

                "SoMucCVDICTCoNghiaViet": (
                    len(
                        cvdict_viet_entries
                    )
                ),

                "SoMucCVDICTDaDuyet": (
                    len(
                        cvdict_approved_entries
                    )
                ),

                "SoMucCCCEDICT": (
                    len(
                        cedict_entries
                    )
                ),

                "PinyinCCCEDICT": (
                    join_unique(
                        item["PhienAm"]
                        for item
                        in cedict_entries
                    )
                ),

                "NghiaAnhCCCEDICT": (
                    " || ".join(
                        item["NghiaGoc"]
                        for item
                        in cedict_entries
                    )
                ),

                "TrangThaiNguon": (
                    status
                ),

                "NghiaVietChon": "",

                "NguonNghiaVietChon": "",

                "DaKiemDuyet": 0,

                "GhiChu": "",
            }
        )

    print(
        "98 chu co muc CVDICT:",
        cvdict_any,
        "/98",
    )

    print(
        "98 chu co nghia Viet CVDICT:",
        cvdict_viet,
        "/98",
    )

    print(
        "98 chu co nghia Viet "
        "CVDICT da duyet:",
        cvdict_approved,
        "/98",
    )

    print(
        "98 chu co muc CC-CEDICT:",
        cedict_any,
        "/98",
    )

    print(
        "98 chu khong co ca hai:",
        no_dictionary,
        "/98",
    )

    # =====================================================
    # 6. SPECIAL CASES
    # =====================================================
    print()
    print(
        "[6] DOI CHIEU CAC CHU DAC BIET"
    )
    print("-" * 120)

    special_output = []

    for char in sorted(
        SPECIAL_CHARS
    ):

        entries = (
            entries_by_char.get(
                char,
                [],
            )
        )

        cvdict_entries = [
            item
            for item in entries
            if item["MaNguon"]
            == CVDICT_SOURCE_ID
        ]

        cedict_entries = [
            item
            for item in entries
            if item["MaNguon"]
            == CC_CEDICT_SOURCE_ID
        ]

        matching_special_rows = [
            row
            for row in special_rows
            if clean(row["KyTu"])
            == char
        ]

        if matching_special_rows:

            pinyin_source = join_unique(
                row["PinyinNguon"]
                for row
                in matching_special_rows
            )

            pinyin_tuvung = join_unique(
                row["PinyinTuVung"]
                for row
                in matching_special_rows
            )

            pinyin_chuhan = join_unique(
                row[
                    "PinyinChuHanHienTai"
                ]
                for row
                in matching_special_rows
            )

            contexts = join_unique(
                row["TuVungDauTien"]
                for row
                in matching_special_rows
            )

        else:

            pinyin_source = ""
            pinyin_tuvung = ""
            pinyin_chuhan = ""
            contexts = ""

        cvdict_pinyin = join_unique(
            item["PhienAm"]
            for item in cvdict_entries
        )

        cedict_pinyin = join_unique(
            item["PhienAm"]
            for item in cedict_entries
        )

        print()
        print(
            "KyTu:",
            char,
        )

        print(
            "  Pinyin MakeMeAHanzi:",
            pinyin_source,
        )

        print(
            "  Pinyin TuVung:",
            pinyin_tuvung,
        )

        print(
            "  Pinyin ChuHan SQL:",
            pinyin_chuhan,
        )

        print(
            "  CVDICT:",
            cvdict_pinyin,
        )

        print(
            "  CC-CEDICT:",
            cedict_pinyin,
        )

        special_output.append(
            {
                "KyTu": char,

                "NguCanhHSK1": (
                    contexts
                ),

                "PinyinMakeMeAHanzi": (
                    pinyin_source
                ),

                "PinyinTuVungHSK1": (
                    pinyin_tuvung
                ),

                "PinyinChuHanHienTai": (
                    pinyin_chuhan
                ),

                "PinyinCVDICT": (
                    cvdict_pinyin
                ),

                "NghiaVietCVDICT": (
                    " || ".join(
                        item[
                            "NghiaTiengViet"
                        ]
                        for item
                        in cvdict_entries
                        if item[
                            "NghiaTiengViet"
                        ]
                    )
                ),

                "PinyinCCCEDICT": (
                    cedict_pinyin
                ),

                "NghiaAnhCCCEDICT": (
                    " || ".join(
                        item[
                            "NghiaGoc"
                        ]
                        for item
                        in cedict_entries
                    )
                ),

                "PinyinChon": "",

                "LyDoChon": "",

                "DaKiemDuyetPinyin": 0,
            }
        )

    # =====================================================
    # 7. WRITE
    # =====================================================
    print()
    print(
        "[7] GHI FILE AUDIT"
    )
    print("-" * 120)

    write_csv(
        OUTPUT_SUMMARY,
        [
            "KyTu",
            "PhamVi",
            "BaiXuatHienDau",
            "TieuDeBai",
            "TuVungDauTien",
            "PinyinMakeMeAHanzi",
            "DefinitionEnglishMakeMeAHanzi",
            "SoMucCVDICT",
            "PinyinCVDICT",
            "NghiaVietCVDICT",
            "SoMucCVDICTCoNghiaViet",
            "SoMucCVDICTDaDuyet",
            "SoMucCCCEDICT",
            "PinyinCCCEDICT",
            "NghiaAnhCCCEDICT",
            "TrangThaiNguon",
            "NghiaVietChon",
            "NguonNghiaVietChon",
            "DaKiemDuyet",
            "GhiChu",
        ],
        summary_rows,
    )

    write_csv(
        OUTPUT_CANDIDATES,
        [
            "MaMucTu",
            "MaNguon",
            "TenNguon",
            "MaNguonBenNgoai",
            "ChuHan",
            "PhienAm",
            "NghiaGoc",
            "NgonNguNghiaGoc",
            "NghiaTiengViet",
            "NghiaVietDaDuyet",
        ],
        raw_candidate_rows,
    )

    write_csv(
        OUTPUT_SPECIAL,
        [
            "KyTu",
            "NguCanhHSK1",
            "PinyinMakeMeAHanzi",
            "PinyinTuVungHSK1",
            "PinyinChuHanHienTai",
            "PinyinCVDICT",
            "NghiaVietCVDICT",
            "PinyinCCCEDICT",
            "NghiaAnhCCCEDICT",
            "PinyinChon",
            "LyDoChon",
            "DaKiemDuyetPinyin",
        ],
        special_output,
    )

    print(
        "98-char summary:"
    )

    print(
        OUTPUT_SUMMARY
    )

    print()
    print(
        "All dictionary candidates:"
    )

    print(
        OUTPUT_CANDIDATES
    )

    print()
    print(
        "Special cases:"
    )

    print(
        OUTPUT_SPECIAL
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 10L"
    )
    print("=" * 120)

    print(
        "Chu can tim nghia Viet:",
        98,
    )

    cvdict_overall = (
        overall_map.get(
            CVDICT_SOURCE_ID,
            {
                "rows": 0,
                "viet": 0,
                "approved": 0,
            },
        )
    )

    cedict_overall = (
        overall_map.get(
            CC_CEDICT_SOURCE_ID,
            {
                "rows": 0,
                "viet": 0,
                "approved": 0,
            },
        )
    )

    print()
    print(
        "MucTuDien CVDICT tong:",
        cvdict_overall["rows"],
    )

    print(
        "CVDICT co NghiaTiengViet:",
        cvdict_overall["viet"],
    )

    print(
        "CVDICT NghiaVietDaDuyet=1:",
        cvdict_overall["approved"],
    )

    print()
    print(
        "MucTuDien CC-CEDICT tong:",
        cedict_overall["rows"],
    )

    print()
    print(
        "Trong 98 chu:"
    )

    print(
        "  Co muc CVDICT:",
        cvdict_any,
        "/98",
    )

    print(
        "  Co nghia Viet CVDICT:",
        cvdict_viet,
        "/98",
    )

    print(
        "  Co nghia Viet CVDICT "
        "da duyet:",
        cvdict_approved,
        "/98",
    )

    print(
        "  Co muc CC-CEDICT:",
        cedict_any,
        "/98",
    )

    print(
        "  Khong co ca hai:",
        no_dictionary,
        "/98",
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA CHON NGHIA VIET."
    )

    print(
        "CHUA CHON PINYIN CHO "
        "CAC CHU DA AM."
    )

    print(
        "CHUA SUA 识."
    )

    print(
        "CHUA INSERT ChuHan."
    )

    print(
        "CHUA INSERT NetChuHan."
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
            "10L THAT BAI"
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