from pathlib import Path
import sys
from collections import defaultdict


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# CAU HINH
# =========================================================
HSK_LEVEL = 1

EXPECTED_HSK1 = 500
EXPECTED_EXISTING = 13
EXPECTED_INSERT = 487
EXPECTED_FINAL = 500


# =========================================================
# CHUAN HOA KEY
# =========================================================
def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


def make_key(chinese, pinyin):

    return (
        clean_text(chinese),
        clean_text(pinyin).lower(),
    )


# =========================================================
# DOC COT LIVE DB
# =========================================================
def get_columns(cursor, table_name):

    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo'
          AND TABLE_NAME = ?
        """,
        table_name,
    )

    return {
        row.COLUMN_NAME
        for row in cursor.fetchall()
    }


# =========================================================
# KIEM TRA SCHEMA
# =========================================================
def check_schema(cursor):

    required_hsk = {
        "MaTuHSK",
        "MaCapDo",
        "ChuHan",
        "PhienAm",
        "TuLoai",
        "NghiaTiengVietThamChieu",
        "MaNguonDanhSach",
    }

    required_runtime = {
        "MaTuVung",
        "ChuHan",
        "ChuPhonThe",
        "PhienAm",
        "NghiaTiengViet",
        "TuLoai",
        "ViDuTiengTrung",
        "ViDuTiengViet",
        "MaAmThanh",
        "MaNguon",
        "DaDuyet",
        "NgayTao",
    }

    hsk_columns = get_columns(
        cursor,
        "TuVungHSKChuan",
    )

    runtime_columns = get_columns(
        cursor,
        "TuVung",
    )

    missing_hsk = (
        required_hsk
        - hsk_columns
    )

    missing_runtime = (
        required_runtime
        - runtime_columns
    )

    if missing_hsk:

        raise RuntimeError(
            "TuVungHSKChuan thieu cot: "
            + ", ".join(
                sorted(missing_hsk)
            )
        )

    if missing_runtime:

        raise RuntimeError(
            "TuVung thieu cot: "
            + ", ".join(
                sorted(missing_runtime)
            )
        )

    print()
    print("Schema:")
    print("  TuVungHSKChuan : OK")
    print("  TuVung         : OK")


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None
    cursor = None

    try:

        print("=" * 90)
        print(
            "09D - IMPORT 487 TU HSK1 "
            "CON LAI VAO TuVung"
        )
        print("=" * 90)

        conn = get_connection()
        conn.autocommit = False

        cursor = conn.cursor()

        # =================================================
        # 1. KIEM TRA SCHEMA
        # =================================================
        check_schema(cursor)

        # =================================================
        # 2. DOC 500 TU HSK1 CHUAN
        # =================================================
        cursor.execute(
            """
            SELECT
                MaTuHSK,
                MaMucNoiBo,
                SoThuTuNguon,
                ChuHan,
                PhienAm,
                TuLoai,
                NghiaTiengVietThamChieu,
                MaNguonDanhSach
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = ?
            ORDER BY MaTuHSK
            """,
            HSK_LEVEL,
        )

        hsk_rows = cursor.fetchall()

        print()
        print(
            "Tong HSK1 nguon:",
            len(hsk_rows),
        )

        if len(hsk_rows) != EXPECTED_HSK1:

            raise RuntimeError(
                "HSK1 khong co dung 500 muc. "
                f"Thuc te: {len(hsk_rows)}"
            )

        # =================================================
        # 3. KIEM TRA DU LIEU BAT BUOC
        # =================================================
        invalid_hsk_rows = []

        for row in hsk_rows:

            errors = []

            if not clean_text(
                row.ChuHan
            ):
                errors.append(
                    "thieu ChuHan"
                )

            if not clean_text(
                row.PhienAm
            ):
                errors.append(
                    "thieu PhienAm"
                )

            if not clean_text(
                row.NghiaTiengVietThamChieu
            ):
                errors.append(
                    "thieu NghiaTiengVietThamChieu"
                )

            if row.MaNguonDanhSach is None:
                errors.append(
                    "thieu MaNguonDanhSach"
                )

            if errors:

                invalid_hsk_rows.append(
                    (
                        row.MaTuHSK,
                        row.ChuHan,
                        errors,
                    )
                )

        if invalid_hsk_rows:

            print()
            print(
                "CAC DONG HSK KHONG HOP LE:"
            )

            for item in invalid_hsk_rows[:20]:
                print(item)

            raise RuntimeError(
                "HSK1 co dong thieu du lieu "
                "bat buoc."
            )

        # =================================================
        # 4. KIEM TRA TRUNG KEY
        #    ChuHan + PhienAm TRONG CHINH 500 TU
        # =================================================
        hsk_by_key = defaultdict(list)

        for row in hsk_rows:

            key = make_key(
                row.ChuHan,
                row.PhienAm,
            )

            hsk_by_key[key].append(
                row
            )

        duplicate_hsk_keys = {
            key: rows
            for key, rows
            in hsk_by_key.items()
            if len(rows) > 1
        }

        if duplicate_hsk_keys:

            print()
            print("-" * 90)
            print(
                "PHAT HIEN TRUNG "
                "ChuHan + PhienAm TRONG HSK1"
            )
            print("-" * 90)

            for key, rows in (
                duplicate_hsk_keys.items()
            ):

                print(
                    key,
                    "=> MaTuHSK:",
                    [
                        row.MaTuHSK
                        for row in rows
                    ],
                )

            raise RuntimeError(
                "Khong insert vi 500 tu HSK1 "
                "co key ChuHan+PhienAm bi trung."
            )

        print(
            "Trung ChuHan+PhienAm "
            "trong 500 HSK1: 0"
        )

        # =================================================
        # 5. KIEM TRA NGUON CO TON TAI
        # =================================================
        source_ids = sorted(
            {
                row.MaNguonDanhSach
                for row in hsk_rows
            }
        )

        print(
            "MaNguonDanhSach HSK1:",
            source_ids,
        )

        for source_id in source_ids:

            cursor.execute(
                """
                SELECT
                    MaNguon,
                    Ten
                FROM dbo.NguonDuLieu
                WHERE MaNguon = ?
                """,
                source_id,
            )

            source_row = (
                cursor.fetchone()
            )

            if source_row is None:

                raise RuntimeError(
                    "Khong ton tai MaNguon="
                    f"{source_id} "
                    "trong NguonDuLieu."
                )

            print(
                f"  MaNguon={source_row.MaNguon}"
                f" | {source_row.Ten}"
            )

        # =================================================
        # 6. DOC RUNTIME HIEN TAI
        # =================================================
        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm,
                NghiaTiengViet,
                TuLoai,
                MaNguon,
                DaDuyet
            FROM dbo.TuVung
            ORDER BY MaTuVung
            """
        )

        runtime_rows = (
            cursor.fetchall()
        )

        print()
        print(
            "TuVung runtime truoc import:",
            len(runtime_rows),
        )

        if len(runtime_rows) != EXPECTED_EXISTING:

            raise RuntimeError(
                "Truoc 09d TuVung phai co dung "
                f"13 dong. Thuc te: "
                f"{len(runtime_rows)}"
            )

        # =================================================
        # 7. INDEX RUNTIME
        # =================================================
        runtime_by_key = defaultdict(list)

        for row in runtime_rows:

            key = make_key(
                row.ChuHan,
                row.PhienAm,
            )

            runtime_by_key[key].append(
                row
            )

        runtime_duplicates = {
            key: rows
            for key, rows
            in runtime_by_key.items()
            if len(rows) > 1
        }

        if runtime_duplicates:

            raise RuntimeError(
                "TuVung runtime dang co "
                "ChuHan+PhienAm trung."
            )

        # =================================================
        # 8. XAC DINH 13 DA CO + 487 THIEU
        # =================================================
        existing = []
        missing = []

        for hsk in hsk_rows:

            key = make_key(
                hsk.ChuHan,
                hsk.PhienAm,
            )

            if key in runtime_by_key:

                existing.append(
                    hsk
                )

            else:

                missing.append(
                    hsk
                )

        print()
        print(
            "Da co:",
            len(existing),
        )

        print(
            "Can insert:",
            len(missing),
        )

        if len(existing) != EXPECTED_EXISTING:

            raise RuntimeError(
                "So tu da co khong bang 13."
            )

        if len(missing) != EXPECTED_INSERT:

            raise RuntimeError(
                "So tu can insert khong bang 487."
            )

        # =================================================
        # 9. KIEM TRA 13 TU DA CO CO DUNG NGUON KHONG
        # =================================================
        wrong_existing_source = []

        for hsk in existing:

            key = make_key(
                hsk.ChuHan,
                hsk.PhienAm,
            )

            runtime = (
                runtime_by_key[key][0]
            )

            if (
                runtime.MaNguon
                != hsk.MaNguonDanhSach
            ):

                wrong_existing_source.append(
                    (
                        hsk.MaTuHSK,
                        hsk.ChuHan,
                        runtime.MaNguon,
                        hsk.MaNguonDanhSach,
                    )
                )

        if wrong_existing_source:

            print()
            print(
                "13 TU CU CO NGUON KHONG KHOP:"
            )

            for row in wrong_existing_source:
                print(row)

            raise RuntimeError(
                "Nguon cua tu runtime cu "
                "khong khop HSK."
            )

        # =================================================
        # 10. HIEN THI MOT SO TU SE INSERT
        # =================================================
        print()
        print("-" * 90)
        print("20 TU DAU TIEN SE INSERT")
        print("-" * 90)

        for row in missing[:20]:

            print(
                f"MaTuHSK={row.MaTuHSK:<4}"
                f" | {row.ChuHan:<8}"
                f" | {row.PhienAm:<18}"
                f" | {row.TuLoai or ''}"
            )

        # =================================================
        # 11. INSERT 487 TU
        #
        # LUU Y:
        # - Chi dung chu gian the ChuHan
        # - ChuPhonThe = NULL
        # - Nghia Viet = nghia tham chieu
        # - Chua them vi du
        # - Chua them audio
        # - DaDuyet = 0
        # =================================================
        inserted = 0

        for row in missing:

            cursor.execute(
                """
                INSERT INTO dbo.TuVung
                (
                    ChuHan,
                    ChuPhonThe,
                    PhienAm,
                    NghiaTiengViet,
                    TuLoai,
                    ViDuTiengTrung,
                    ViDuTiengViet,
                    MaAmThanh,
                    MaNguon,
                    DaDuyet
                )
                VALUES
                (
                    ?,
                    NULL,
                    ?,
                    ?,
                    ?,
                    NULL,
                    NULL,
                    NULL,
                    ?,
                    0
                )
                """,
                clean_text(
                    row.ChuHan
                ),
                clean_text(
                    row.PhienAm
                ),
                clean_text(
                    row.NghiaTiengVietThamChieu
                ),
                (
                    clean_text(
                        row.TuLoai
                    )
                    or None
                ),
                row.MaNguonDanhSach,
            )

            inserted += 1

        if inserted != EXPECTED_INSERT:

            raise RuntimeError(
                "So dong insert khong bang 487."
            )

        # =================================================
        # 12. DOC LAI RUNTIME TRONG TRANSACTION
        # =================================================
        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm,
                NghiaTiengViet,
                TuLoai,
                MaNguon,
                DaDuyet
            FROM dbo.TuVung
            ORDER BY MaTuVung
            """
        )

        final_runtime = (
            cursor.fetchall()
        )

        if len(final_runtime) != EXPECTED_FINAL:

            raise RuntimeError(
                "Sau insert TuVung khong co "
                "dung 500 dong. "
                f"Thuc te: {len(final_runtime)}"
            )

        # =================================================
        # 13. KIEM TRA MAPPING 500/500
        # =================================================
        final_by_key = defaultdict(list)

        for row in final_runtime:

            key = make_key(
                row.ChuHan,
                row.PhienAm,
            )

            final_by_key[key].append(
                row
            )

        final_missing = []
        final_ambiguous = []
        final_wrong_source = []

        for hsk in hsk_rows:

            key = make_key(
                hsk.ChuHan,
                hsk.PhienAm,
            )

            candidates = (
                final_by_key.get(
                    key,
                    [],
                )
            )

            if len(candidates) == 0:

                final_missing.append(
                    hsk
                )

            elif len(candidates) > 1:

                final_ambiguous.append(
                    (
                        hsk,
                        candidates,
                    )
                )

            else:

                runtime = (
                    candidates[0]
                )

                if (
                    runtime.MaNguon
                    != hsk.MaNguonDanhSach
                ):

                    final_wrong_source.append(
                        (
                            hsk,
                            runtime,
                        )
                    )

        if final_missing:

            raise RuntimeError(
                "Sau insert van con "
                "HSK1 chua co trong TuVung."
            )

        if final_ambiguous:

            raise RuntimeError(
                "Sau insert co mapping "
                "HSK1 -> TuVung bi mo ho."
            )

        if final_wrong_source:

            raise RuntimeError(
                "Sau insert co TuVung sai nguon."
            )

        # =================================================
        # 14. KIEM TRA DaDuyet
        # =================================================
        cursor.execute(
            """
            SELECT
                COUNT(*) AS Tong,
                SUM(
                    CASE
                        WHEN DaDuyet = 0
                        THEN 1
                        ELSE 0
                    END
                ) AS ChuaDuyet,
                SUM(
                    CASE
                        WHEN DaDuyet = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS DaDuyet
            FROM dbo.TuVung
            """
        )

        approval = (
            cursor.fetchone()
        )

        if approval.Tong != 500:

            raise RuntimeError(
                "Tong TuVung verify != 500."
            )

        if approval.ChuaDuyet != 500:

            raise RuntimeError(
                "Khong phai tat ca 500 tu "
                "dang DaDuyet=0."
            )

        # =================================================
        # 15. COMMIT
        # =================================================
        conn.commit()

        # =================================================
        # 16. KET QUA
        # =================================================
        print()
        print("=" * 90)
        print("KET QUA")
        print("=" * 90)

        print(
            "TuVung truoc import:",
            EXPECTED_EXISTING,
        )

        print(
            "Da insert:",
            inserted,
        )

        print(
            "TuVung sau import:",
            len(final_runtime),
        )

        print()
        print(
            "HSK1 khop TuVung:",
            500,
        )

        print(
            "HSK1 con thieu:",
            len(final_missing),
        )

        print(
            "Mapping mo ho:",
            len(final_ambiguous),
        )

        print(
            "Sai MaNguon:",
            len(final_wrong_source),
        )

        print()
        print(
            "DaDuyet = 0:",
            approval.ChuaDuyet,
        )

        print(
            "DaDuyet = 1:",
            approval.DaDuyet,
        )

        print()
        print(
            "DA IMPORT 487 TU HSK1 "
            "CON LAI THANH CONG."
        )

        print()
        print(
            "500/500 TU HSK1 DA CO "
            "TRONG dbo.TuVung."
        )

        print()
        print(
            "CHUA GAN 487 TU MOI "
            "VAO BAI 2 -> 23."
        )

        print(
            "CHUA DUYET NOI DUNG TU VUNG."
        )

        print(
            "CHUA THEM VI DU / AUDIO."
        )

        print()
        print("=" * 90)
        print("HOAN TAT")
        print("=" * 90)

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 90)
        print(
            "THAT BAI - DA ROLLBACK"
        )
        print("=" * 90)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "KHONG GIU BAT KY TU VUNG "
            "MOI NAO NEU CO LOI."
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


if __name__ == "__main__":
    main()