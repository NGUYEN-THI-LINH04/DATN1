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
# CONFIG
# =========================================================
COURSE_CODE = "HSK1-CORE"


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

    print("-" * 115)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 115)
    print(
        "09H2 - AUDIT NGUON DU LIEU "
        "CHO NGU PHAP HSK1"
    )
    print("=" * 115)

    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. CONNECT
    # =====================================================
    print()
    print("[1] KET NOI DATABASE")
    line()

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
                        "Dang ket noi nham database. "
                        f"Thuc te: {database_name}"
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 2. SCHEMA NGUONDULIEU
                # =========================================
                print()
                print(
                    "[2] KIEM TRA SCHEMA "
                    "dbo.NguonDuLieu"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        COLUMN_NAME,
                        DATA_TYPE,
                        CHARACTER_MAXIMUM_LENGTH,
                        IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE
                        TABLE_SCHEMA = 'dbo'
                        AND TABLE_NAME = 'NguonDuLieu'
                    ORDER BY ORDINAL_POSITION;
                    """
                )

                schema_rows = (
                    cursor.fetchall()
                )

                if not schema_rows:

                    fail(
                        "Khong tim thay "
                        "dbo.NguonDuLieu."
                    )

                expected_columns = {
                    "MaNguon",
                    "Ten",
                    "LienKetNguon",
                    "GiayPhep",
                    "GhiChu",
                    "NgayLayDuLieu",
                }

                actual_columns = {
                    clean(row[0])
                    for row in schema_rows
                }

                missing = (
                    expected_columns
                    - actual_columns
                )

                for index, row in enumerate(
                    schema_rows,
                    start=1,
                ):

                    column_name = clean(
                        row[0]
                    )

                    data_type = clean(
                        row[1]
                    )

                    max_length = row[2]

                    nullable = clean(
                        row[3]
                    )

                    if max_length is None:

                        type_text = data_type

                    elif int(max_length) == -1:

                        type_text = (
                            f"{data_type}(max)"
                        )

                    else:

                        type_text = (
                            f"{data_type}"
                            f"({max_length})"
                        )

                    print(
                        f"{index:>2}. "
                        f"{column_name:<20} "
                        f"{type_text:<22} "
                        f"NULL={nullable}"
                    )

                if missing:

                    fail(
                        "NguonDuLieu thieu cot: "
                        + ", ".join(
                            sorted(missing)
                        )
                    )

                print()
                print(
                    "SCHEMA NGUONDULIEU: OK"
                )

                # =========================================
                # 3. DOC TOAN BO NGUON
                # =========================================
                print()
                print(
                    "[3] DANH SACH NGUON "
                    "HIEN CO"
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
                    ORDER BY MaNguon;
                    """
                )

                source_rows = (
                    cursor.fetchall()
                )

                print(
                    "Tong nguon:",
                    len(source_rows),
                )

                if not source_rows:

                    fail(
                        "dbo.NguonDuLieu "
                        "hien khong co nguon nao."
                    )

                sources = []

                for row in source_rows:

                    source = {
                        "MaNguon": int(
                            row[0]
                        ),
                        "Ten": clean(
                            row[1]
                        ),
                        "LienKetNguon": clean(
                            row[2]
                        ),
                        "GiayPhep": clean(
                            row[3]
                        ),
                        "GhiChu": clean(
                            row[4]
                        ),
                        "NgayLayDuLieu": (
                            ""
                            if row[5] is None
                            else str(row[5])
                        ),
                    }

                    sources.append(
                        source
                    )

                for source in sources:

                    print()
                    print(
                        "=" * 115
                    )

                    print(
                        "MaNguon:",
                        source["MaNguon"],
                    )

                    print(
                        "Ten:",
                        (
                            source["Ten"]
                            if source["Ten"]
                            else "<TRONG>"
                        ),
                    )

                    print(
                        "LienKetNguon:",
                        (
                            source["LienKetNguon"]
                            if source[
                                "LienKetNguon"
                            ]
                            else "<TRONG>"
                        ),
                    )

                    print(
                        "GiayPhep:",
                        (
                            source["GiayPhep"]
                            if source[
                                "GiayPhep"
                            ]
                            else "<TRONG>"
                        ),
                    )

                    print(
                        "GhiChu:",
                        (
                            source["GhiChu"]
                            if source[
                                "GhiChu"
                            ]
                            else "<TRONG>"
                        ),
                    )

                    print(
                        "NgayLayDuLieu:",
                        (
                            source[
                                "NgayLayDuLieu"
                            ]
                            if source[
                                "NgayLayDuLieu"
                            ]
                            else "<TRONG>"
                        ),
                    )

                # =========================================
                # 4. NGUON DANG DUNG TRONG TUVUNG
                # =========================================
                print()
                print(
                    "[4] NGUON DANG DUOC DUNG "
                    "TRONG dbo.TuVung"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        tv.MaNguon,
                        nd.Ten,
                        COUNT(*) AS SoLuong
                    FROM dbo.TuVung AS tv
                    LEFT JOIN dbo.NguonDuLieu AS nd
                        ON tv.MaNguon = nd.MaNguon
                    GROUP BY
                        tv.MaNguon,
                        nd.Ten
                    ORDER BY
                        COUNT(*) DESC,
                        tv.MaNguon;
                    """
                )

                vocab_source_rows = (
                    cursor.fetchall()
                )

                if not vocab_source_rows:

                    print(
                        "Khong co du lieu TuVung."
                    )

                else:

                    for row in vocab_source_rows:

                        print(
                            "MaNguon=",
                            row[0],
                            " | ",
                            clean(row[1]),
                            " | SoLuong=",
                            int(row[2]),
                            sep="",
                        )

                # =========================================
                # 5. NGUON NGU PHAP HIEN TAI
                # =========================================
                print()
                print(
                    "[5] NGUON CUA 7 NGU PHAP "
                    "HSK1 HIEN TAI"
                )
                line()

                cursor.execute(
                    """
                    SELECT
                        np.MaNguPhap,
                        bh.SoThuTuBai,
                        np.TenCauTruc,
                        np.MaNguon,
                        nd.Ten
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON np.MaBaiHoc = bh.MaBaiHoc
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc
                    LEFT JOIN dbo.NguonDuLieu AS nd
                        ON np.MaNguon = nd.MaNguon
                    WHERE kh.MaKyHieu = ?
                    ORDER BY
                        bh.SoThuTuBai,
                        np.ThuTu,
                        np.MaNguPhap;
                    """,
                    COURSE_CODE,
                )

                grammar_rows = (
                    cursor.fetchall()
                )

                print(
                    "Tong ngu phap HSK1:",
                    len(grammar_rows),
                )

                grammar_missing_source = 0

                for row in grammar_rows:

                    source_id = row[3]

                    if source_id is None:
                        grammar_missing_source += 1

                    print(
                        "MaNguPhap=",
                        int(row[0]),
                        " | Bai=",
                        int(row[1]),
                        " | ",
                        clean(row[2]),
                        " | MaNguon=",
                        source_id,
                        " | ",
                        (
                            clean(row[4])
                            if row[4] is not None
                            else "<CHUA CO NGUON>"
                        ),
                        sep="",
                    )

                print()
                print(
                    "Ngu phap chua co MaNguon:",
                    grammar_missing_source,
                )

                # =========================================
                # 6. TIM NGUON LIEN QUAN HSK
                # =========================================
                print()
                print(
                    "[6] TIM NGUON CO KHA NANG "
                    "LIEN QUAN DEN HSK"
                )
                line()

                keywords = [
                    "hsk",
                    "gf0025",
                    "国际中文教育",
                    "中文水平等级标准",
                    "等级标准",
                    "proficiency",
                    "grading standard",
                    "standard",
                ]

                candidates = []

                for source in sources:

                    search_text = " ".join([
                        source["Ten"],
                        source[
                            "LienKetNguon"
                        ],
                        source["GhiChu"],
                    ]).casefold()

                    matched_keywords = [
                        keyword
                        for keyword in keywords
                        if (
                            keyword.casefold()
                            in search_text
                        )
                    ]

                    if matched_keywords:

                        candidates.append(
                            (
                                source,
                                matched_keywords,
                            )
                        )

                print(
                    "So nguon tim thay:",
                    len(candidates),
                )

                if not candidates:

                    print(
                        "KHONG TIM THAY NGUON "
                        "CO TU KHOA HSK / STANDARD."
                    )

                else:

                    for (
                        source,
                        matched,
                    ) in candidates:

                        print()
                        print(
                            "MaNguon:",
                            source[
                                "MaNguon"
                            ],
                        )

                        print(
                            "Ten:",
                            source["Ten"],
                        )

                        print(
                            "Tu khoa khop:",
                            ", ".join(
                                matched
                            ),
                        )

                        print(
                            "LienKetNguon:",
                            (
                                source[
                                    "LienKetNguon"
                                ]
                                or "<TRONG>"
                            ),
                        )

                        print(
                            "GiayPhep:",
                            (
                                source[
                                    "GiayPhep"
                                ]
                                or "<TRONG>"
                            ),
                        )

                        print(
                            "GhiChu:",
                            (
                                source[
                                    "GhiChu"
                                ]
                                or "<TRONG>"
                            ),
                        )

                # =========================================
                # 7. KIEM TRA RIENG MaNguon=1002
                # =========================================
                print()
                print(
                    "[7] KIEM TRA RIENG "
                    "MaNguon=1002"
                )
                line()

                source_1002 = [
                    source
                    for source in sources
                    if source[
                        "MaNguon"
                    ] == 1002
                ]

                if not source_1002:

                    print(
                        "MaNguon=1002 "
                        "KHONG TON TAI."
                    )

                else:

                    source = (
                        source_1002[0]
                    )

                    print(
                        "MaNguon:",
                        source["MaNguon"],
                    )

                    print(
                        "Ten:",
                        source["Ten"],
                    )

                    print(
                        "LienKetNguon:",
                        (
                            source[
                                "LienKetNguon"
                            ]
                            or "<TRONG>"
                        ),
                    )

                    print(
                        "GiayPhep:",
                        (
                            source[
                                "GiayPhep"
                            ]
                            or "<TRONG>"
                        ),
                    )

                    print(
                        "GhiChu:",
                        (
                            source[
                                "GhiChu"
                            ]
                            or "<TRONG>"
                        ),
                    )

                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM dbo.TuVung
                        WHERE MaNguon = 1002;
                        """
                    )

                    source_1002_vocab_count = int(
                        cursor.fetchone()[0]
                    )

                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM dbo.NguPhap
                        WHERE MaNguon = 1002;
                        """
                    )

                    source_1002_grammar_count = int(
                        cursor.fetchone()[0]
                    )

                    print(
                        "TuVung dung MaNguon=1002:",
                        source_1002_vocab_count,
                    )

                    print(
                        "NguPhap dung MaNguon=1002:",
                        source_1002_grammar_count,
                    )

                # =========================================
                # 8. KIEM TRA CHAT LUONG NGUON
                # =========================================
                print()
                print(
                    "[8] KIEM TRA CHAT LUONG "
                    "THONG TIN NGUON"
                )
                line()

                missing_link = [
                    source
                    for source in sources
                    if not source[
                        "LienKetNguon"
                    ]
                ]

                missing_license = [
                    source
                    for source in sources
                    if not source[
                        "GiayPhep"
                    ]
                ]

                missing_note = [
                    source
                    for source in sources
                    if not source[
                        "GhiChu"
                    ]
                ]

                print(
                    "Nguon thieu LienKetNguon:",
                    len(missing_link),
                )

                print(
                    "Nguon thieu GiayPhep:",
                    len(missing_license),
                )

                print(
                    "Nguon thieu GhiChu:",
                    len(missing_note),
                )

                # =========================================
                # 9. FINAL
                # =========================================
                print()
                print("=" * 115)
                print(
                    "KET QUA AUDIT NGUON "
                    "NGU PHAP HSK1"
                )
                print("=" * 115)

                print(
                    "Tong nguon:",
                    len(sources),
                )

                print(
                    "Ngu phap HSK1 hien tai:",
                    len(grammar_rows),
                )

                print(
                    "Ngu phap chua co MaNguon:",
                    grammar_missing_source,
                )

                print(
                    "Nguon co tu khoa "
                    "HSK/Standard:",
                    len(candidates),
                )

                print(
                    "MaNguon=1002 ton tai:",
                    (
                        "CO"
                        if source_1002
                        else "KHONG"
                    ),
                )

                print()
                print(
                    "AUDIT NGUON HOAN TAT."
                )

                print(
                    "DATABASE KHONG BI SUA."
                )

                print()
                print(
                    "CHUA GAN MaNguon CHO "
                    "NGU PHAP O BUOC NAY."
                )

                print(
                    "CHUA INSERT NGU PHAP "
                    "BAI 2 -> 23."
                )

                print()
                print("=" * 115)
                print("HOAN TAT")
                print("=" * 115)

        finally:

            try:
                connection.rollback()

            except Exception:
                pass


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
            "AUDIT NGUON THAT BAI"
        )
        print("=" * 115)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "SCRIPT NAY CHI SELECT."
        )

        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)