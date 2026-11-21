from pathlib import Path
import csv
import sys
import unicodedata
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
COURSE_CODE = "HSK1-CORE"

EXPECTED_TOTAL = 301
EXPECTED_CURRENT = 17
EXPECTED_INSERT = 284

STATUS_DRAFT = "ban_nhap"


# =========================================================
# 5 PINYIN CAN CHOT SAU 10P
# =========================================================
PINYIN_OVERRIDE = {
    "呢": {
        "Pinyin": "ne",
        "LyDo": (
            "Trong HSK1 dung 呢 lam tro tu ngu khi; "
            "chon am nhe ne."
        ),
    },

    "谁": {
        "Pinyin": "shéi",
        "LyDo": (
            "HSK1 dung cach doc shéi; "
            "shuí cung la cach doc duoc chap nhan, "
            "nhung shéi duoc chon lam cach doc hoc tap."
        ),
    },

    "教": {
        "Pinyin": "jiāo",
        "LyDo": (
            "Theo muc TuVung HSK1 da duyet, "
            "教 trong ngu canh hoc tap co cach doc jiāo = day."
        ),
    },

    "了": {
        "Pinyin": "le",
        "LyDo": (
            "Trong HSK1 dung 了 chu yeu lam tro tu; "
            "chon am nhe le."
        ),
    },

    "吧": {
        "Pinyin": "ba",
        "LyDo": (
            "Trong HSK1 dung 吧 lam tro tu ngu khi; "
            "chon am nhe ba."
        ),
    },
}


# =========================================================
# PATHS
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
    / "hsk1_301_hanzi_merged_review.csv"
)

OUTPUT_FINAL = (
    REVIEW_DIR
    / "hsk1_301_hanzi_final_preinsert.csv"
)

OUTPUT_UPDATE = (
    REVIEW_DIR
    / "hsk1_17_hanzi_update_plan.csv"
)

OUTPUT_INSERT = (
    REVIEW_DIR
    / "hsk1_284_hanzi_insert_plan.csv"
)

OUTPUT_ISSUES = (
    REVIEW_DIR
    / "hsk1_301_hanzi_10q_issues.csv"
)


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def normalize(value):

    return unicodedata.normalize(
        "NFC",
        clean(value)
    ).lower()


def to_int(value, default=None):

    value = clean(value)

    if value == "":
        return default

    return int(value)


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


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10Q - CHOT 301 CHU HAN HSK1 "
        "TRUOC KHI GHI DATABASE"
    )
    print("=" * 120)

    print()
    print("MUC TIEU:")
    print("  CHOT 5 PINYIN CON LAI")
    print("  DAT 301/301 SAN SANG")
    print("  DOI CHIEU 17 ChuHan HIEN CO")
    print("  TAO PLAN UPDATE 17 CHU CU")
    print("  TAO PLAN INSERT 284 CHU MOI")
    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. READ 10P
    # =====================================================
    print()
    print("[1] DOC FILE 10P")
    print("-" * 120)

    fields, rows = load_csv(
        INPUT_FILE
    )

    required = {
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "MaBaiHoc",
        "TieuDeBai",
        "TuVungDauTien",
        "ThuTuDeXuat",

        "PinyinFinalDeXuat",
        "NghiaTiengVietFinalDeXuat",

        "RadicalChuan",
        "MaBoThu",
        "SoBoThu",
        "TenBoThu",

        "SoNet",

        "NguonNgonNgu",
        "MaNguonNgonNgu",

        "TrangThaiPinyin",
        "NgonNguDaKiemDuyet",

        "TrangThaiDeXuat",

        "DaCoTrongChuHan",
        "MaChuHanHienTai",

        "SanSangNoiDung",
        "GhiChu",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        fail(
            "File 10P thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    if len(rows) != EXPECTED_TOTAL:

        fail(
            "File 10P khong co "
            "dung 301 dong."
        )

    char_map = {}

    for row in rows:

        char = clean(
            row["KyTu"]
        )

        if char in char_map:

            fail(
                f"Trung KyTu: {char}"
            )

        char_map[
            char
        ] = row

    print(
        "Tong Chu Han:",
        len(rows),
    )

    # =====================================================
    # 2. VERIFY EXACT 5 UNREADY
    # =====================================================
    print()
    print(
        "[2] KIEM TRA 5 CHU CHUA SAN SANG"
    )
    print("-" * 120)

    unready = [
        row
        for row in rows
        if clean(
            row[
                "SanSangNoiDung"
            ]
        ) != "1"
    ]

    unready_chars = {
        clean(row["KyTu"])
        for row in unready
    }

    expected_override_chars = set(
        PINYIN_OVERRIDE
    )

    print(
        "Chu chua san sang:",
        len(unready),
    )

    print(
        "Danh sach:",
        " ".join(
            clean(row["KyTu"])
            for row in unready
        ),
    )

    if unready_chars != expected_override_chars:

        fail(
            "Danh sach chu chua san sang "
            "khong dung 5 chu mong doi.\n"
            f"Thuc te: "
            f"{' '.join(sorted(unready_chars))}"
        )

    print(
        "DUNG 5 CHU MONG DOI: OK"
    )

    # =====================================================
    # 3. APPLY 5 PINYIN DECISIONS
    # =====================================================
    print()
    print(
        "[3] CHOT 5 PINYIN"
    )
    print("-" * 120)

    for char, override in (
        PINYIN_OVERRIDE.items()
    ):

        row = char_map[
            char
        ]

        old_pinyin = clean(
            row[
                "PinyinFinalDeXuat"
            ]
        )

        new_pinyin = (
            override["Pinyin"]
        )

        old_note = clean(
            row["GhiChu"]
        )

        decision_note = (
            "10Q: "
            + override["LyDo"]
        )

        if old_note:

            new_note = (
                old_note
                + " | "
                + decision_note
            )

        else:

            new_note = (
                decision_note
            )

        row[
            "PinyinFinalDeXuat"
        ] = new_pinyin

        row[
            "TrangThaiPinyin"
        ] = (
            "10Q_DA_CHOT_THEO_NGU_CANH_HSK1"
        )

        row[
            "NgonNguDaKiemDuyet"
        ] = "1"

        row[
            "SanSangNoiDung"
        ] = "1"

        row[
            "GhiChu"
        ] = new_note

        print(
            f"{char}: "
            f"{old_pinyin or '<TRONG>'} "
            f"-> {new_pinyin}"
        )

    # =====================================================
    # 4. FINAL CONTENT AUDIT
    # =====================================================
    print()
    print(
        "[4] AUDIT 301 CHU SAU KHI CHOT"
    )
    print("-" * 120)

    issues = []

    for row in rows:

        char = clean(
            row["KyTu"]
        )

        pinyin = clean(
            row[
                "PinyinFinalDeXuat"
            ]
        )

        meaning = clean(
            row[
                "NghiaTiengVietFinalDeXuat"
            ]
        )

        ma_bai = to_int(
            row["MaBaiHoc"]
        )

        ma_bo_thu = to_int(
            row["MaBoThu"]
        )

        so_net = to_int(
            row["SoNet"]
        )

        thu_tu = to_int(
            row[
                "ThuTuDeXuat"
            ]
        )

        if not pinyin:

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": "THIEU_PINYIN",
                    "ChiTiet": "",
                }
            )

        if not meaning:

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": "THIEU_NGHIA_VIET",
                    "ChiTiet": "",
                }
            )

        if ma_bai is None:

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": "THIEU_MABAIHOC",
                    "ChiTiet": "",
                }
            )

        if ma_bo_thu is None:

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": "THIEU_MABOTHU",
                    "ChiTiet": "",
                }
            )

        if so_net is None:

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": "THIEU_SONET",
                    "ChiTiet": "",
                }
            )

        if (
            thu_tu is None
            or thu_tu <= 0
        ):

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": "THUTU_KHONG_HOP_LE",
                    "ChiTiet": str(
                        thu_tu
                    ),
                }
            )

        if clean(
            row[
                "NgonNguDaKiemDuyet"
            ]
        ) != "1":

            issues.append(
                {
                    "KyTu": char,
                    "LoaiLoi": (
                        "NGON_NGU_CHUA_DUYET"
                    ),
                    "ChiTiet": "",
                }
            )

    ready_count = (
        len(rows)
        - len(
            {
                item["KyTu"]
                for item in issues
            }
        )
    )

    print(
        "San sang:",
        ready_count,
        "/301",
    )

    print(
        "Issue:",
        len(issues),
    )

    # =====================================================
    # 5. DATABASE CURRENT STATE
    # =====================================================
    print()
    print(
        "[5] DOI CHIEU DATABASE"
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

                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        ch.MaBaiHoc,
                        ch.KyTu,
                        ch.Pinyin,
                        ch.NghiaTiengViet,
                        ch.MaBoThu,
                        ch.SoNet,
                        ch.CachGhiNho,
                        ch.ViDuTiengTrung,
                        ch.ViDuPinyin,
                        ch.ViDuTiengViet,
                        ch.MaTep,
                        ch.MaNguon,
                        ch.ThuTu,
                        ch.TrangThai

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    WHERE
                        kh.MaKyHieu = ?

                    ORDER BY
                        bh.SoThuTuBai,
                        ch.ThuTu;
                    """,
                    COURSE_CODE,
                )

                current_rows = (
                    cursor.fetchall()
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    if (
        len(current_rows)
        != EXPECTED_CURRENT
    ):

        fail(
            "ChuHan hien tai "
            "khong con 17."
        )

    current_map = {
        clean(row[2]): {
            "MaChuHan": int(row[0]),
            "MaBaiHoc": int(row[1]),
            "Pinyin": clean(row[3]),
            "Nghia": clean(row[4]),
            "MaBoThu": row[5],
            "SoNet": row[6],
            "CachGhiNho": clean(
                row[7]
            ),
            "ViDuTiengTrung": clean(
                row[8]
            ),
            "ViDuPinyin": clean(
                row[9]
            ),
            "ViDuTiengViet": clean(
                row[10]
            ),
            "MaTep": row[11],
            "MaNguon": row[12],
            "ThuTu": row[13],
            "TrangThai": clean(
                row[14]
            ),
        }
        for row in current_rows
    }

    if len(current_map) != 17:

        fail(
            "Co KyTu trung trong "
            "17 ChuHan hien tai."
        )

    # =====================================================
    # 6. BUILD UPDATE + INSERT PLAN
    # =====================================================
    print()
    print(
        "[6] TAO UPDATE / INSERT PLAN"
    )
    print("-" * 120)

    update_rows = []
    insert_rows = []
    final_rows = []

    update_required = 0
    existing_unchanged = 0

    for row in rows:

        char = clean(
            row["KyTu"]
        )

        proposed = {
            "MaBaiHoc": to_int(
                row[
                    "MaBaiHoc"
                ]
            ),

            "KyTu": char,

            "Pinyin": clean(
                row[
                    "PinyinFinalDeXuat"
                ]
            ),

            "NghiaTiengViet": clean(
                row[
                    "NghiaTiengVietFinalDeXuat"
                ]
            ),

            "MaBoThu": to_int(
                row[
                    "MaBoThu"
                ]
            ),

            "SoNet": to_int(
                row[
                    "SoNet"
                ]
            ),

            "ThuTu": to_int(
                row[
                    "ThuTuDeXuat"
                ]
            ),

            "TrangThai": (
                STATUS_DRAFT
            ),
        }

        current = (
            current_map.get(
                char
            )
        )

        # -----------------------------------------
        # Source strategy
        # -----------------------------------------
        #
        # Khong hard-code MaNguon o 10Q.
        # 10R se tao/tim 1 NguonDuLieu tong hop
        # cua do an va lay MaNguon thuc te.
        #
        source_strategy = (
            "TONG_HOP_CHUHAN_HSK1_DO_AN"
        )

        final_record = {
            "KyTu": char,
            "PhamVi": clean(
                row["PhamVi"]
            ),
            "BaiXuatHienDau": to_int(
                row[
                    "BaiXuatHienDau"
                ]
            ),
            "MaBaiHoc": (
                proposed[
                    "MaBaiHoc"
                ]
            ),
            "TieuDeBai": clean(
                row[
                    "TieuDeBai"
                ]
            ),
            "TuVungDauTien": clean(
                row[
                    "TuVungDauTien"
                ]
            ),
            "ThuTu": (
                proposed["ThuTu"]
            ),
            "Pinyin": (
                proposed["Pinyin"]
            ),
            "NghiaTiengViet": (
                proposed[
                    "NghiaTiengViet"
                ]
            ),
            "MaBoThu": (
                proposed["MaBoThu"]
            ),
            "SoNet": (
                proposed["SoNet"]
            ),
            "CachGhiNho": "",
            "ViDuTiengTrung": "",
            "ViDuPinyin": "",
            "ViDuTiengViet": "",
            "MaTep": "",
            "NguonChuHanChienLuoc": (
                source_strategy
            ),
            "TrangThai": (
                STATUS_DRAFT
            ),
            "DaCoTrongSQL": (
                1
                if current
                else 0
            ),
            "MaChuHanHienTai": (
                current[
                    "MaChuHan"
                ]
                if current
                else ""
            ),
            "HanhDong10R": "",
            "CotCanCapNhat": "",
            "GhiChu": clean(
                row["GhiChu"]
            ),
        }

        if current:

            differences = []

            if (
                current["MaBaiHoc"]
                !=
                proposed["MaBaiHoc"]
            ):

                differences.append(
                    "MaBaiHoc"
                )

            if (
                normalize(
                    current["Pinyin"]
                )
                !=
                normalize(
                    proposed["Pinyin"]
                )
            ):

                differences.append(
                    "Pinyin"
                )

            if (
                normalize(
                    current["Nghia"]
                )
                !=
                normalize(
                    proposed[
                        "NghiaTiengViet"
                    ]
                )
            ):

                differences.append(
                    "NghiaTiengViet"
                )

            if (
                current["MaBoThu"]
                !=
                proposed["MaBoThu"]
            ):

                differences.append(
                    "MaBoThu"
                )

            if (
                current["SoNet"]
                !=
                proposed["SoNet"]
            ):

                differences.append(
                    "SoNet"
                )

            if (
                current["ThuTu"]
                !=
                proposed["ThuTu"]
            ):

                differences.append(
                    "ThuTu"
                )

            if (
                current["TrangThai"]
                !=
                proposed["TrangThai"]
            ):

                differences.append(
                    "TrangThai"
                )

            if differences:

                update_required += 1

                action = "UPDATE"

            else:

                existing_unchanged += 1

                action = (
                    "GIU_NOI_DUNG_"
                    "CHI_CHOT_NGUON_10R"
                )

            final_record[
                "HanhDong10R"
            ] = action

            final_record[
                "CotCanCapNhat"
            ] = (
                " | ".join(
                    differences
                )
            )

            update_rows.append(
                {
                    **final_record,

                    "PinyinHienTai": (
                        current[
                            "Pinyin"
                        ]
                    ),

                    "NghiaHienTai": (
                        current[
                            "Nghia"
                        ]
                    ),

                    "MaBoThuHienTai": (
                        current[
                            "MaBoThu"
                        ]
                    ),

                    "SoNetHienTai": (
                        current[
                            "SoNet"
                        ]
                    ),

                    "ThuTuHienTai": (
                        current[
                            "ThuTu"
                        ]
                    ),

                    "MaNguonHienTai": (
                        current[
                            "MaNguon"
                        ]
                    ),
                }
            )

        else:

            final_record[
                "HanhDong10R"
            ] = "INSERT"

            insert_rows.append(
                final_record.copy()
            )

        final_rows.append(
            final_record
        )

    if len(update_rows) != 17:

        fail(
            "Update plan khong co "
            "dung 17 ChuHan cu."
        )

    if (
        len(insert_rows)
        != EXPECTED_INSERT
    ):

        fail(
            "Insert plan khong co "
            "dung 284 ChuHan moi."
        )

    print(
        "ChuHan hien co:",
        len(update_rows),
    )

    print(
        "  Can UPDATE noi dung:",
        update_required,
    )

    print(
        "  Noi dung da khop:",
        existing_unchanged,
    )

    print(
        "ChuHan can INSERT:",
        len(insert_rows),
    )

    # =====================================================
    # 7. VERIFY LESSON ORDER UNIQUE
    # =====================================================
    print()
    print(
        "[7] KIEM TRA ThuTu TRONG TUNG BAI"
    )
    print("-" * 120)

    lesson_order_seen = {}

    for row in final_rows:

        key = (
            int(
                row[
                    "MaBaiHoc"
                ]
            ),
            int(
                row["ThuTu"]
            ),
        )

        if key in lesson_order_seen:

            issues.append(
                {
                    "KyTu": (
                        row["KyTu"]
                    ),
                    "LoaiLoi": (
                        "TRUNG_THUTU_TRONG_BAI"
                    ),
                    "ChiTiet": (
                        f"Trung voi "
                        f"{lesson_order_seen[key]}"
                    ),
                }
            )

        else:

            lesson_order_seen[
                key
            ] = row["KyTu"]

    print(
        "Cap MaBaiHoc + ThuTu:",
        len(
            lesson_order_seen
        ),
    )

    # =====================================================
    # 8. WRITE
    # =====================================================
    print()
    print(
        "[8] GHI FILE PRE-INSERT"
    )
    print("-" * 120)

    final_fields = [
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "MaBaiHoc",
        "TieuDeBai",
        "TuVungDauTien",
        "ThuTu",
        "Pinyin",
        "NghiaTiengViet",
        "MaBoThu",
        "SoNet",
        "CachGhiNho",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaTep",
        "NguonChuHanChienLuoc",
        "TrangThai",
        "DaCoTrongSQL",
        "MaChuHanHienTai",
        "HanhDong10R",
        "CotCanCapNhat",
        "GhiChu",
    ]

    write_csv(
        OUTPUT_FINAL,
        final_fields,
        final_rows,
    )

    update_fields = (
        final_fields
        + [
            "PinyinHienTai",
            "NghiaHienTai",
            "MaBoThuHienTai",
            "SoNetHienTai",
            "ThuTuHienTai",
            "MaNguonHienTai",
        ]
    )

    write_csv(
        OUTPUT_UPDATE,
        update_fields,
        update_rows,
    )

    write_csv(
        OUTPUT_INSERT,
        final_fields,
        insert_rows,
    )

    write_csv(
        OUTPUT_ISSUES,
        [
            "KyTu",
            "LoaiLoi",
            "ChiTiet",
        ],
        issues,
    )

    print(
        "Final preinsert:"
    )

    print(
        OUTPUT_FINAL
    )

    print()
    print(
        "17 update plan:"
    )

    print(
        OUTPUT_UPDATE
    )

    print()
    print(
        "284 insert plan:"
    )

    print(
        OUTPUT_INSERT
    )

    print()
    print(
        "Issues:"
    )

    print(
        OUTPUT_ISSUES
    )

    # =====================================================
    # FINAL
    # =====================================================
    final_ready = (
        len(final_rows)
        -
        len(
            {
                issue["KyTu"]
                for issue in issues
            }
        )
    )

    print()
    print("=" * 120)
    print(
        "KET QUA 10Q"
    )
    print("=" * 120)

    print(
        "Tong Chu Han:",
        len(final_rows),
    )

    print(
        "San sang nhap SQL:",
        final_ready,
        "/301",
    )

    print(
        "Tong issue:",
        len(issues),
    )

    print()
    print(
        "5 Pinyin da chot:"
    )

    for char in PINYIN_OVERRIDE:

        print(
            f"  {char}: "
            f"{PINYIN_OVERRIDE[char]['Pinyin']}"
        )

    print()
    print(
        "ChuHan hien co:",
        len(update_rows),
    )

    print(
        "Can UPDATE noi dung:",
        update_required,
    )

    print(
        "Noi dung da khop:",
        existing_unchanged,
    )

    print(
        "Can INSERT moi:",
        len(insert_rows),
    )

    print()
    print(
        "NGUON CHUHAN:"
    )

    print(
        "10R se tao/lay mot dong "
        "NguonDuLieu tong hop cua do an."
    )

    print(
        "KHONG hard-code MaNguon "
        "tai buoc 10Q."
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA INSERT ChuHan."
    )

    print(
        "CHUA UPDATE ChuHan."
    )

    print(
        "CHUA INSERT NetChuHan."
    )

    print()
    print(
        "NEU 301/301 VA ISSUE=0:"
    )

    print(
        "BUOC 10R SE GHI DU LIEU "
        "VAO DATABASE BANG TRANSACTION."
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
            "10Q THAT BAI"
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