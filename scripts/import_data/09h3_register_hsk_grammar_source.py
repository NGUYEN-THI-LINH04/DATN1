from pathlib import Path
import sys
from contextlib import closing


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# SOURCE INFO
# =========================================================
SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"

SOURCE_URL = (
    "https://admin.chinesetest.cn/"
    "standardsAction.do?means=standardInfo"
)

# Không tự bịa giấy phép nếu nguồn chính thức
# không công bố giấy phép tái sử dụng cụ thể.
SOURCE_LICENSE = None

SOURCE_NOTE = (
    "Nguồn chính thức cho phần ngữ pháp theo "
    "《国际中文教育中文水平等级标准》 (GF0025-2021), "
    "Phụ lục A (规范性) 语法等级大纲. "
    "Dùng để xác định phạm vi, cấp độ và điểm ngữ pháp. "
    "Mô tả tiếng Việt, cách dùng và ví dụ học tập "
    "trong đồ án được biên soạn lại phục vụ người học; "
    "không sao chép nguyên văn nội dung nguồn."
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


def line():

    print("-" * 110)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 110)
    print(
        "09H3 - DANG KY NGUON NGU PHAP "
        "GF0025-2021"
    )
    print("=" * 110)

    print()
    print(
        "BUOC NAY CHI THEM 1 NGUON "
        "VAO dbo.NguonDuLieu."
    )

    print(
        "KHONG SUA 7 NGU PHAP BAI 1."
    )

    print(
        "KHONG INSERT NGU PHAP "
        "BAI 2 -> 23."
    )

    # =====================================================
    # CONNECT
    # =====================================================
    print()
    print("[1] KET NOI DATABASE")
    line()

    with closing(
        get_connection()
    ) as connection:

        committed = False

        try:

            try:
                connection.autocommit = False
            except Exception:
                pass

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
                # PRE-CHECK
                # =========================================
                print()
                print(
                    "[2] KIEM TRA NGUON DA TON TAI"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten,
                        LienKetNguon,
                        GiayPhep,
                        GhiChu
                    FROM dbo.NguonDuLieu
                    WHERE Ten = ?;
                    """,
                    SOURCE_NAME,
                )

                existing = cursor.fetchall()

                if len(existing) > 1:

                    fail(
                        "Phat hien nhieu hon 1 "
                        "nguon cung ten."
                    )

                if len(existing) == 1:

                    row = existing[0]

                    print(
                        "Nguon da ton tai."
                    )

                    print(
                        "MaNguon:",
                        int(row[0]),
                    )

                    print(
                        "Ten:",
                        clean(row[1]),
                    )

                    print(
                        "LienKetNguon:",
                        clean(row[2]),
                    )

                    print(
                        "GiayPhep:",
                        clean(row[3])
                        or "<TRONG>",
                    )

                    print()
                    print(
                        "KHONG INSERT THEM."
                    )

                    print(
                        "DATABASE KHONG BI SUA."
                    )

                    print()
                    print("=" * 110)
                    print("HOAN TAT")
                    print("=" * 110)

                    return

                print(
                    "Chua co nguon ngữ pháp "
                    "GF0025-2021."
                )

                # =========================================
                # KIEM TRA 1002
                # =========================================
                print()
                print(
                    "[3] KIEM TRA KHONG DUNG "
                    "NHAM MaNguon=1002"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten,
                        GhiChu
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = 1002;
                    """
                )

                source_1002 = (
                    cursor.fetchone()
                )

                if source_1002 is None:

                    fail(
                        "Khong tim thay MaNguon=1002."
                    )

                print(
                    "MaNguon:",
                    int(source_1002[0]),
                )

                print(
                    "Ten:",
                    clean(source_1002[1]),
                )

                print(
                    "GhiChu:",
                    clean(source_1002[2]),
                )

                print()
                print(
                    "Nguon 1002 duoc giu rieng "
                    "cho TU VUNG."
                )

                # =========================================
                # SHOW NEW SOURCE
                # =========================================
                print()
                print(
                    "[4] NGUON SE DUOC THEM"
                )
                line()

                print(
                    "Ten:",
                    SOURCE_NAME,
                )

                print(
                    "LienKetNguon:",
                    SOURCE_URL,
                )

                print(
                    "GiayPhep:",
                    "<NULL>",
                )

                print(
                    "GhiChu:",
                    SOURCE_NOTE,
                )

                # =========================================
                # CONFIRM
                # =========================================
                print()
                print("=" * 110)
                print("XAC NHAN")
                print("=" * 110)

                confirmation = input(
                    "Nhap chinh xac "
                    "ADD GRAMMAR SOURCE "
                    "de tiep tuc: "
                ).strip()

                if (
                    confirmation
                    != "ADD GRAMMAR SOURCE"
                ):

                    print()
                    print(
                        "KHONG NHAN DUOC "
                        "XAC NHAN."
                    )

                    print(
                        "DATABASE KHONG BI SUA."
                    )

                    return

                # =========================================
                # INSERT
                # =========================================
                print()
                print(
                    "[5] INSERT NGUON"
                )
                line()

                cursor.execute(
                    """
                    INSERT INTO dbo.NguonDuLieu
                    (
                        Ten,
                        LienKetNguon,
                        GiayPhep,
                        GhiChu,
                        NgayLayDuLieu
                    )
                    OUTPUT INSERTED.MaNguon
                    VALUES
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        SYSUTCDATETIME()
                    );
                    """,
                    SOURCE_NAME,
                    SOURCE_URL,
                    SOURCE_LICENSE,
                    SOURCE_NOTE,
                )

                inserted_row = (
                    cursor.fetchone()
                )

                if inserted_row is None:

                    fail(
                        "INSERT khong tra ve "
                        "MaNguon."
                    )

                new_source_id = int(
                    inserted_row[0]
                )

                print(
                    "MaNguon moi:",
                    new_source_id,
                )

                # =========================================
                # VERIFY BEFORE COMMIT
                # =========================================
                print()
                print(
                    "[6] VERIFY TRUOC COMMIT"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        MaNguon,
                        Ten,
                        LienKetNguon,
                        GiayPhep,
                        GhiChu,
                        NgayLayDuLieu
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = ?;
                    """,
                    new_source_id,
                )

                verify_row = (
                    cursor.fetchone()
                )

                if verify_row is None:

                    fail(
                        "Khong tim thay "
                        "nguon vua INSERT."
                    )

                if (
                    clean(verify_row[1])
                    != SOURCE_NAME
                    or
                    clean(verify_row[2])
                    != SOURCE_URL
                    or
                    clean(verify_row[4])
                    != SOURCE_NOTE
                ):

                    fail(
                        "Nguon vua INSERT "
                        "khong dung du lieu "
                        "mong doi."
                    )

                if verify_row[3] is not None:

                    fail(
                        "GiayPhep phai NULL "
                        "o buoc nay."
                    )

                print(
                    "MaNguon:",
                    int(verify_row[0]),
                )

                print(
                    "Ten:",
                    clean(verify_row[1]),
                )

                print(
                    "LienKetNguon:",
                    clean(verify_row[2]),
                )

                print(
                    "GiayPhep:",
                    "<NULL>",
                )

                print(
                    "NgayLayDuLieu:",
                    verify_row[5],
                )

                print(
                    "VERIFY TRUOC COMMIT: OK"
                )

                # =========================================
                # COMMIT
                # =========================================
                print()
                print(
                    "[7] COMMIT"
                )
                line()

                connection.commit()
                committed = True

                print(
                    "COMMIT THANH CONG."
                )

                # =========================================
                # VERIFY AFTER COMMIT
                # =========================================
                print()
                print(
                    "[8] VERIFY SAU COMMIT"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        COUNT(*)
                    FROM dbo.NguonDuLieu
                    WHERE
                        MaNguon = ?
                        AND Ten = ?;
                    """,
                    new_source_id,
                    SOURCE_NAME,
                )

                count_after = int(
                    cursor.fetchone()[0]
                )

                if count_after != 1:

                    fail(
                        "Nguon sau COMMIT "
                        "khong ton tai duy nhat."
                    )

                print(
                    "Nguon ton tai sau COMMIT: OK"
                )

                # =========================================
                # RESULT
                # =========================================
                print()
                print("=" * 110)
                print(
                    "KET QUA DANG KY NGUON"
                )
                print("=" * 110)

                print(
                    "MaNguon moi:",
                    new_source_id,
                )

                print(
                    "Ten:",
                    SOURCE_NAME,
                )

                print()
                print(
                    "NGUON NGU PHAP "
                    "DA DUOC DANG KY "
                    "THANH CONG."
                )

                print()
                print(
                    "CHUA GAN NGUON NAY "
                    "CHO 7 NGU PHAP BAI 1."
                )

                print(
                    "CHUA INSERT NGU PHAP "
                    "BAI 2 -> 23."
                )

                print()
                print("=" * 110)
                print("HOAN TAT")
                print("=" * 110)

        except Exception:

            if not committed:

                try:

                    connection.rollback()

                    print()
                    print(
                        "TRANSACTION "
                        "DA ROLLBACK."
                    )

                except Exception:
                    pass

            raise


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 110)
        print(
            "DANG KY NGUON THAT BAI"
        )
        print("=" * 110)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "KHONG TIEP TUC "
            "SANG BUOC NGU PHAP."
        )

        sys.exit(1)