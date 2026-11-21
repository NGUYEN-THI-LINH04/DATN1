from pathlib import Path
import csv
import hashlib
import sys
from datetime import datetime
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
LESSON_NO = 1
EXPECTED_ROWS = 7
EXPECTED_SOURCE_ID = 1004

REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lesson1_grammar_mapping_review.csv"
)

BACKUP_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "db_backup"
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


def sha256_file(path):

    digest = hashlib.sha256()

    with open(path, "rb") as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def load_csv(path):

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

        return reader.fieldnames, list(reader)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H7 - BACKUP 7 NGU PHAP BAI 1 "
        "TRUOC KHI GAN MaNguon=1004"
    )
    print("=" * 115)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE REVIEW")
    print("  CHI SELECT DATABASE")
    print("  TAO FILE BACKUP CSV")
    print("  KHONG UPDATE dbo.NguPhap")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG DELETE")

    # =====================================================
    # 1. VERIFY REVIEW FILE
    # =====================================================
    print()
    print("[1] VERIFY FILE REVIEW DA KIEM DUYET")
    print("-" * 115)

    if not REVIEW_FILE.exists():

        fail(
            "Khong tim thay file review:\n"
            f"{REVIEW_FILE}"
        )

    review_fields, review_rows = load_csv(
        REVIEW_FILE
    )

    required_fields = {
        "MaNguPhap",
        "TenCauTruc",
        "MaNguonHienTai",
        "MaNguonDeXuat",
        "MaMucNguPhapChuan",
        "DaKiemDuyetMapping",
        "GhiChuKiemDuyet",
    }

    missing_fields = (
        required_fields
        - set(review_fields)
    )

    if missing_fields:

        fail(
            "File review thieu cot: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if len(review_rows) != EXPECTED_ROWS:

        fail(
            "File review phai co dung "
            f"{EXPECTED_ROWS} dong. "
            f"Thuc te: {len(review_rows)}"
        )

    review_by_id = {}

    for row in review_rows:

        grammar_id_text = clean(
            row["MaNguPhap"]
        )

        if not grammar_id_text.isdigit():

            fail(
                "MaNguPhap khong hop le: "
                f"{grammar_id_text}"
            )

        grammar_id = int(
            grammar_id_text
        )

        if grammar_id in review_by_id:

            fail(
                "MaNguPhap bi trung: "
                f"{grammar_id}"
            )

        if (
            clean(
                row["DaKiemDuyetMapping"]
            )
            != "1"
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "chua DaKiemDuyetMapping=1."
            )

        if (
            clean(
                row["MaNguonDeXuat"]
            )
            != str(EXPECTED_SOURCE_ID)
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "khong de xuat MaNguon=1004."
            )

        if (
            clean(
                row["MaNguonHienTai"]
            )
            != ""
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "trong review da co MaNguonHienTai."
            )

        if not clean(
            row["GhiChuKiemDuyet"]
        ):

            fail(
                f"MaNguPhap={grammar_id} "
                "thieu GhiChuKiemDuyet."
            )

        review_by_id[
            grammar_id
        ] = row

    if len(review_by_id) != 7:

        fail(
            "Khong co dung "
            "7 MaNguPhap duy nhat."
        )

    print(
        "Tong mapping:",
        len(review_rows),
    )

    print(
        "DaKiemDuyetMapping=1:",
        sum(
            1
            for row in review_rows
            if clean(
                row["DaKiemDuyetMapping"]
            ) == "1"
        ),
    )

    print(
        "MaNguonDeXuat=1004:",
        sum(
            1
            for row in review_rows
            if clean(
                row["MaNguonDeXuat"]
            ) == "1004"
        ),
    )

    print(
        "FILE REVIEW: OK"
    )

    # =====================================================
    # 2. CONNECT DATABASE
    # =====================================================
    print()
    print("[2] KET NOI DATABASE")
    print("-" * 115)

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
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        ),
                        DB_NAME(),
                        SUSER_SNAME();
                    """
                )

                (
                    server_name,
                    database_name,
                    login_name,
                ) = cursor.fetchone()

                print(
                    "Server:",
                    server_name,
                )

                print(
                    "Database:",
                    database_name,
                )

                print(
                    "Tai khoan:",
                    login_name,
                )

                if (
                    clean(database_name).lower()
                    != "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi nham database."
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 3. VERIFY SOURCE 1004
                # =========================================
                print()
                print(
                    "[3] VERIFY MaNguon=1004"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = ?;
                    """,
                    EXPECTED_SOURCE_ID,
                )

                source_row = (
                    cursor.fetchone()
                )

                if source_row is None:

                    fail(
                        "Khong tim thay MaNguon=1004."
                    )

                print(
                    "MaNguon:",
                    int(source_row[0]),
                )

                print(
                    "Ten:",
                    clean(source_row[1]),
                )

                if (
                    clean(source_row[1])
                    != "GF0025-2021 - Ngữ pháp HSK"
                ):

                    fail(
                        "MaNguon=1004 "
                        "khong phai nguon mong doi."
                    )

                print(
                    "NGUON: OK"
                )

                # =========================================
                # 4. READ LESSON 1 GRAMMAR
                # =========================================
                print()
                print(
                    "[4] DOC 7 NGU PHAP BAI 1"
                )
                print("-" * 115)

                cursor.execute(
                    """
                    SELECT
                        np.MaNguPhap,
                        np.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe,
                        np.TenCauTruc,
                        np.MoTa,
                        np.CachDung,
                        np.ViDuTiengTrung,
                        np.ViDuPinyin,
                        np.ViDuTiengViet,
                        np.MaTep,
                        np.MaNguon,
                        np.ThuTu,
                        np.TrangThai,
                        np.NgayTao
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc = bh.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                        AND bh.SoThuTuBai = ?
                    ORDER BY
                        np.ThuTu,
                        np.MaNguPhap;
                    """,
                    COURSE_CODE,
                    LESSON_NO,
                )

                db_rows = (
                    cursor.fetchall()
                )

                if len(db_rows) != 7:

                    fail(
                        "Bai 1 phai co dung "
                        "7 ngu phap. "
                        f"Thuc te: {len(db_rows)}"
                    )

                backup_rows = []

                for row in db_rows:

                    grammar_id = int(
                        row[0]
                    )

                    if (
                        grammar_id
                        not in review_by_id
                    ):

                        fail(
                            "MaNguPhap trong DB "
                            "khong co trong review: "
                            f"{grammar_id}"
                        )

                    review = review_by_id[
                        grammar_id
                    ]

                    db_name = clean(
                        row[4]
                    )

                    if (
                        db_name
                        != clean(
                            review["TenCauTruc"]
                        )
                    ):

                        fail(
                            f"TenCauTruc "
                            f"MaNguPhap={grammar_id} "
                            "khong khop review."
                        )

                    if row[11] is not None:

                        fail(
                            f"MaNguPhap={grammar_id} "
                            "da co MaNguon="
                            f"{row[11]}. "
                            "Khong tao backup moi "
                            "tren du lieu da thay doi."
                        )

                    backup_rows.append(
                        {
                            "MaNguPhap": grammar_id,
                            "MaBaiHoc": int(
                                row[1]
                            ),
                            "SoThuTuBai": int(
                                row[2]
                            ),
                            "TieuDeBai": clean(
                                row[3]
                            ),
                            "TenCauTruc": clean(
                                row[4]
                            ),
                            "MoTa": clean(
                                row[5]
                            ),
                            "CachDung": clean(
                                row[6]
                            ),
                            "ViDuTiengTrung": clean(
                                row[7]
                            ),
                            "ViDuPinyin": clean(
                                row[8]
                            ),
                            "ViDuTiengViet": clean(
                                row[9]
                            ),
                            "MaTep": (
                                ""
                                if row[10] is None
                                else int(row[10])
                            ),
                            "MaNguon": (
                                ""
                                if row[11] is None
                                else int(row[11])
                            ),
                            "ThuTu": int(
                                row[12]
                            ),
                            "TrangThai": clean(
                                row[13]
                            ),
                            "NgayTao": str(
                                row[14]
                            ),
                        }
                    )

                print(
                    "Tong dong:",
                    len(backup_rows),
                )

                print(
                    "MaNguon=NULL:",
                    sum(
                        1
                        for row in backup_rows
                        if row["MaNguon"] == ""
                    ),
                )

                print(
                    "DB TRUOC APPLY: OK"
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 5. CREATE BACKUP FILE
    # =====================================================
    print()
    print("[5] TAO FILE BACKUP")
    print("-" * 115)

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = (
        BACKUP_DIR
        / (
            "hsk1_lesson1_grammar_"
            f"before_source_apply_{timestamp}.csv"
        )
    )

    fieldnames = [
        "MaNguPhap",
        "MaBaiHoc",
        "SoThuTuBai",
        "TieuDeBai",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaTep",
        "MaNguon",
        "ThuTu",
        "TrangThai",
        "NgayTao",
    ]

    with open(
        backup_file,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            backup_rows
        )

    # =====================================================
    # 6. VERIFY BACKUP FILE
    # =====================================================
    print()
    print("[6] VERIFY BACKUP")
    print("-" * 115)

    _, verify_rows = load_csv(
        backup_file
    )

    if len(verify_rows) != 7:

        fail(
            "Backup khong co dung 7 dong."
        )

    backup_ids = [
        int(
            clean(
                row["MaNguPhap"]
            )
        )
        for row in verify_rows
    ]

    if len(
        set(backup_ids)
    ) != 7:

        fail(
            "Backup co MaNguPhap bi trung."
        )

    if (
        set(backup_ids)
        != set(review_by_id)
    ):

        fail(
            "Danh sach MaNguPhap backup "
            "khong khop review."
        )

    non_null_source = [
        row
        for row in verify_rows
        if clean(
            row["MaNguon"]
        ) != ""
    ]

    if non_null_source:

        fail(
            "Backup co dong MaNguon "
            "khong NULL."
        )

    backup_hash = sha256_file(
        backup_file
    )

    review_hash = sha256_file(
        REVIEW_FILE
    )

    print(
        "Backup:"
    )

    print(
        backup_file
    )

    print()
    print(
        "SHA256 backup:"
    )

    print(
        backup_hash
    )

    print()
    print(
        "Review file:"
    )

    print(
        REVIEW_FILE
    )

    print()
    print(
        "SHA256 review:"
    )

    print(
        review_hash
    )

    print()
    print(
        "Tong dong backup:",
        len(verify_rows),
    )

    print(
        "MaNguPhap duy nhat:",
        len(
            set(backup_ids)
        ),
    )

    print(
        "MaNguon NULL:",
        sum(
            1
            for row in verify_rows
            if clean(
                row["MaNguon"]
            ) == ""
        ),
    )

    print(
        "BACKUP: OK"
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 115)
    print(
        "KET QUA 09H7"
    )
    print("=" * 115)

    print(
        "Tong ngu phap Bai 1:",
        len(verify_rows),
    )

    print(
        "Da backup:",
        len(verify_rows),
    )

    print(
        "MaNguon hien tai:",
        "NULL 7/7",
    )

    print()
    print(
        "BACKUP 7 NGU PHAP BAI 1 "
        "THANH CONG."
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA GAN MaNguon=1004."
    )

    print(
        "CHUA INSERT NGU PHAP "
        "BAI 2 -> 23."
    )

    print()
    print("=" * 115)
    print("HOAN TAT")
    print("=" * 115)


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 115)
        print(
            "09H7 THAT BAI"
        )
        print("=" * 115)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)