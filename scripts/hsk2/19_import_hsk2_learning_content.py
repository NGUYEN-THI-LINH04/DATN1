from pathlib import Path
import csv
import sys
import pyodbc


# ============================================================
# DUONG DAN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

LESSON_FILE = (
    DATA_DIR / "lessons_hsk2_draft.csv"
)

VOCAB_FILE = (
    DATA_DIR / "vocabulary_hsk2_final_by_lesson.csv"
)

GRAMMAR_FILE = (
    DATA_DIR / "grammar_hsk2_by_lesson.csv"
)

HANZI_FILE = (
    DATA_DIR / "hanzi_hsk2_by_lesson.csv"
)


# ============================================================
# SQL SERVER
# ============================================================

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=HocTiengTrungDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


MA_KHOA_HOC_HSK2 = 2

HANZI_SOURCE_NAME = (
    "Dữ liệu Chữ Hán HSK2 - tổng hợp đồ án"
)


def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def to_int_or_none(value):

    value = clean(value)

    if not value:
        return None

    return int(value)


def read_csv(path):

    if not path.exists():

        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)
        fields = reader.fieldnames

    if not fields:

        raise ValueError(
            f"File khong co header:\n{path}"
        )

    return rows, fields


def get_connection():

    return pyodbc.connect(
        CONNECTION_STRING,
        timeout=15,
        autocommit=False
    )


# ============================================================
# DOC VA KIEM TRA 4 FILE
# ============================================================

def load_and_validate_files():

    lessons, lesson_fields = read_csv(
        LESSON_FILE
    )

    vocab, vocab_fields = read_csv(
        VOCAB_FILE
    )

    grammar, grammar_fields = read_csv(
        GRAMMAR_FILE
    )

    hanzi, hanzi_fields = read_csv(
        HANZI_FILE
    )

    if len(lessons) != 23:

        raise ValueError(
            f"Phai co 23 bai hoc, "
            f"hien co {len(lessons)}."
        )

    if len(vocab) != 772:

        raise ValueError(
            f"Phai co 772 tu vung, "
            f"hien co {len(vocab)}."
        )

    if len(grammar) != 48:

        raise ValueError(
            f"Phai co 48 ngu phap, "
            f"hien co {len(grammar)}."
        )

    if len(hanzi) != 299:

        raise ValueError(
            f"Phai co 299 Chu Han, "
            f"hien co {len(hanzi)}."
        )

    # ========================================================
    # KIEM TRA 23 BAI
    # ========================================================

    lesson_numbers = []

    for row in lessons:

        number = int(
            row["SoThuTuBai"]
        )

        if int(row["MaKhoaHoc"]) != 2:

            raise ValueError(
                f"Bai {number} "
                "khong thuoc MaKhoaHoc=2."
            )

        lesson_numbers.append(
            number
        )

    if sorted(lesson_numbers) != list(
        range(1, 24)
    ):

        raise ValueError(
            "SoThuTuBai phai du tu 1 den 23."
        )

    # ========================================================
    # KIEM TRA 772 TU
    # ========================================================

    ma_hsk = [
        int(row["MaTuHSK"])
        for row in vocab
    ]

    if len(set(ma_hsk)) != 772:

        raise ValueError(
            "MaTuHSK trong file tu vung bi trung."
        )

    vocab_pairs = []

    for row in vocab:

        lesson = int(
            row["SoThuTuBai"]
        )

        ma_tu_vung = int(
            row["MaTuVung"]
        )

        if lesson < 1 or lesson > 23:

            raise ValueError(
                f"Tu {row['MaTuHSK']} "
                "co bai khong hop le."
            )

        vocab_pairs.append(
            (
                lesson,
                ma_tu_vung
            )
        )

    if len(vocab_pairs) != len(
        set(vocab_pairs)
    ):

        raise ValueError(
            "Co cap "
            "(SoThuTuBai, MaTuVung) bi trung."
        )

    # ========================================================
    # KIEM TRA NGU PHAP
    # ========================================================

    for row in grammar:

        lesson = int(
            row["SoThuTuBai"]
        )

        if lesson < 1 or lesson > 23:

            raise ValueError(
                "Ngu phap co bai khong hop le: "
                + row["TenCauTruc"]
            )

    # ========================================================
    # KIEM TRA CHU HAN
    # ========================================================

    chars = [
        clean(row["KyTu"])
        for row in hanzi
    ]

    if len(set(chars)) != 299:

        raise ValueError(
            "KyTu Chu Han bi trung."
        )

    for row in hanzi:

        lesson = int(
            row["SoThuTuBai"]
        )

        if lesson < 1 or lesson > 23:

            raise ValueError(
                f"Chu {row['KyTu']} "
                "co bai khong hop le."
            )

        required = [
            "KyTu",
            "Pinyin",
            "NghiaTiengViet",
            "MaBoThu",
            "SoNet",
        ]

        for field in required:

            if not clean(
                row.get(field)
            ):

                raise ValueError(
                    f"Chu {row['KyTu']} "
                    f"thieu {field}."
                )

    return (
        lessons,
        vocab,
        grammar,
        hanzi
    )


# ============================================================
# KIEM TRA CSDL TRUOC KHI INSERT
# ============================================================

def preflight_database(
    cursor,
    vocab_rows
):

    # --------------------------------------------------------
    # KhoaHoc HSK2
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            MaKhoaHoc,
            MaCapDo,
            MaKyHieu,
            TieuDe,
            TrangThai
        FROM dbo.KhoaHoc
        WHERE MaKhoaHoc = ?;
    """, MA_KHOA_HOC_HSK2)

    course = cursor.fetchone()

    if not course:

        raise ValueError(
            "Khong tim thay KhoaHoc HSK2 "
            "MaKhoaHoc=2."
        )

    if int(course.MaCapDo) != 2:

        raise ValueError(
            "MaKhoaHoc=2 khong phai CapDo HSK2."
        )

    # --------------------------------------------------------
    # HSK2 phai chua co BaiHoc
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = ?;
    """, MA_KHOA_HOC_HSK2)

    existing_lessons = int(
        cursor.fetchone()[0]
    )

    if existing_lessons != 0:

        raise ValueError(
            "HSK2 da co BaiHoc trong SQL: "
            f"{existing_lessons} bai.\n"
            "Script nay chi duoc chay khi "
            "HSK2 chua co bai hoc de tranh trung du lieu."
        )

    # --------------------------------------------------------
    # Tat ca MaTuVung phai ton tai
    # --------------------------------------------------------

    vocab_ids = sorted({
        int(row["MaTuVung"])
        for row in vocab_rows
    })

    placeholders = ",".join(
        "?"
        for _ in vocab_ids
    )

    cursor.execute(
        f"""
        SELECT MaTuVung
        FROM dbo.TuVung
        WHERE MaTuVung IN ({placeholders});
        """,
        *vocab_ids
    )

    found_ids = {
        int(row[0])
        for row in cursor.fetchall()
    }

    missing = set(
        vocab_ids
    ) - found_ids

    if missing:

        raise ValueError(
            "Co MaTuVung khong ton tai trong SQL:\n"
            + ", ".join(
                map(str, sorted(missing))
            )
        )

    print()
    print("KhoaHoc HSK2:")
    print(
        f"  MaKhoaHoc: {course.MaKhoaHoc}"
    )
    print(
        f"  MaKyHieu : {course.MaKyHieu}"
    )
    print(
        f"  TieuDe   : {course.TieuDe}"
    )
    print(
        f"  TrangThai: {course.TrangThai}"
    )

    print()
    print(
        f"BaiHoc HSK2 hien tai: "
        f"{existing_lessons}"
    )

    print(
        f"MaTuVung hop le: "
        f"{len(found_ids)}"
    )


# ============================================================
# NGUON CHU HAN HSK2
# ============================================================

def get_or_create_hanzi_source(
    cursor
):

    cursor.execute("""
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?;
    """, HANZI_SOURCE_NAME)

    row = cursor.fetchone()

    if row:

        return int(
            row.MaNguon
        ), False

    cursor.execute("""
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
            NULL,
            ?,
            ?,
            SYSUTCDATETIME()
        );
    """,
        HANZI_SOURCE_NAME,

        "Theo giấy phép của từng nguồn thành phần",

        (
            "Bản dữ liệu tổng hợp dùng cho bảng ChuHan HSK2 "
            "của đồ án. Phạm vi HSK2 được xác định từ "
            "GF0025-2021 (MaNguon=1002). "
            "Thông tin chữ Hán, bộ thủ và số nét được "
            "đối chiếu từ Unicode Character Database "
            "và các nguồn chữ Hán của đồ án. "
            "Pinyin và nghĩa tiếng Việt được chuẩn hóa "
            "phục vụ học liệu HSK2."
        )
    )

    ma_nguon = int(
        cursor.fetchone()[0]
    )

    return ma_nguon, True


# ============================================================
# INSERT 23 BAI HOC
# ============================================================

def insert_lessons(
    cursor,
    lesson_rows
):

    for row in lesson_rows:

        cursor.execute("""
            INSERT INTO dbo.BaiHoc
            (
                MaKhoaHoc,
                SoThuTuBai,
                TieuDe,
                TomTat,
                TrangThai,
                NgayTao
            )
            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                'ban_nhap',
                SYSUTCDATETIME()
            );
        """,
            MA_KHOA_HOC_HSK2,
            int(row["SoThuTuBai"]),
            clean(row["TieuDe"]),
            clean(row["TomTat"])
        )

    # --------------------------------------------------------
    # Lay MaBaiHoc that
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            MaBaiHoc,
            SoThuTuBai
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = ?
        ORDER BY SoThuTuBai;
    """, MA_KHOA_HOC_HSK2)

    lesson_map = {
        int(row.SoThuTuBai):
        int(row.MaBaiHoc)
        for row in cursor.fetchall()
    }

    if len(lesson_map) != 23:

        raise ValueError(
            "Sau INSERT khong co du "
            "23 BaiHoc HSK2."
        )

    return lesson_map


# ============================================================
# INSERT 772 LIEN KET TU VUNG
# ============================================================

def insert_vocabulary_links(
    cursor,
    vocab_rows,
    lesson_map
):

    counters = {
        i: 0
        for i in range(
            1,
            24
        )
    }

    for row in vocab_rows:

        lesson_number = int(
            row["SoThuTuBai"]
        )

        ma_bai_hoc = (
            lesson_map[
                lesson_number
            ]
        )

        counters[
            lesson_number
        ] += 1

        thu_tu = counters[
            lesson_number
        ]

        # Neu file da co ThuTuTrongBai
        # thi dung dung thu tu da chot
        if clean(
            row.get(
                "ThuTuTrongBai"
            )
        ):
            thu_tu = int(
                row[
                    "ThuTuTrongBai"
                ]
            )

        cursor.execute("""
            INSERT INTO dbo.TuVungBaiHoc
            (
                MaBaiHoc,
                MaTuVung,
                ThuTu
            )
            VALUES (?, ?, ?);
        """,
            ma_bai_hoc,
            int(row["MaTuVung"]),
            thu_tu
        )


# ============================================================
# INSERT 48 NGU PHAP
# ============================================================

def insert_grammar(
    cursor,
    grammar_rows,
    lesson_map
):

    for row in grammar_rows:

        lesson_number = int(
            row["SoThuTuBai"]
        )

        ma_bai_hoc = (
            lesson_map[
                lesson_number
            ]
        )

        ma_nguon = to_int_or_none(
            row.get("MaNguon")
        )

        # Grammar HSK dung nguon 1004
        if ma_nguon is None:
            ma_nguon = 1004

        thu_tu = to_int_or_none(
            row.get(
                "ThuTuTrongBai"
            )
        )

        if thu_tu is None:

            thu_tu = to_int_or_none(
                row.get(
                    "ThuTuTam"
                )
            )

        if thu_tu is None:

            raise ValueError(
                "Ngu phap thieu ThuTu: "
                + row["TenCauTruc"]
            )

        cursor.execute("""
            INSERT INTO dbo.NguPhap
            (
                MaBaiHoc,
                TenCauTruc,
                MoTa,
                CachDung,
                ViDuTiengTrung,
                ViDuPinyin,
                ViDuTiengViet,
                MaTep,
                MaNguon,
                ThuTu,
                TrangThai,
                NgayTao
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                'ban_nhap',
                SYSUTCDATETIME()
            );
        """,
            ma_bai_hoc,
            clean(row["TenCauTruc"]),
            clean(row.get("MoTa")) or None,
            clean(row.get("CachDung")) or None,
            clean(row.get("ViDuTiengTrung")) or None,
            clean(row.get("ViDuPinyin")) or None,
            clean(row.get("ViDuTiengViet")) or None,
            to_int_or_none(row.get("MaTep")),
            ma_nguon,
            thu_tu
        )


# ============================================================
# INSERT 299 CHU HAN
# ============================================================

def insert_hanzi(
    cursor,
    hanzi_rows,
    lesson_map,
    hanzi_source_id
):

    for row in hanzi_rows:

        lesson_number = int(
            row["SoThuTuBai"]
        )

        ma_bai_hoc = (
            lesson_map[
                lesson_number
            ]
        )

        thu_tu = to_int_or_none(
            row.get(
                "ThuTuTrongBai"
            )
        )

        if thu_tu is None:

            thu_tu = to_int_or_none(
                row.get(
                    "ThuTuTam"
                )
            )

        if thu_tu is None:

            raise ValueError(
                "Chu Han thieu ThuTu: "
                + row["KyTu"]
            )

        cursor.execute("""
            INSERT INTO dbo.ChuHan
            (
                MaBaiHoc,
                MaBoThu,
                KyTu,
                Pinyin,
                NghiaTiengViet,
                SoNet,
                CachGhiNho,
                ViDuTiengTrung,
                ViDuPinyin,
                ViDuTiengViet,
                MaTep,
                MaNguon,
                ThuTu,
                TrangThai,
                NgayTao
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                'ban_nhap',
                SYSUTCDATETIME()
            );
        """,
            ma_bai_hoc,
            int(row["MaBoThu"]),
            clean(row["KyTu"]),
            clean(row["Pinyin"]),
            clean(row["NghiaTiengViet"]),
            int(row["SoNet"]),
            clean(
                row.get(
                    "CachGhiNho"
                )
            ) or None,
            clean(
                row.get(
                    "ViDuTiengTrung"
                )
            ) or None,
            clean(
                row.get(
                    "ViDuPinyin"
                )
            ) or None,
            clean(
                row.get(
                    "ViDuTiengViet"
                )
            ) or None,
            to_int_or_none(
                row.get("MaTep")
            ),
            hanzi_source_id,
            thu_tu
        )


# ============================================================
# KIEM TRA SAU INSERT
# ============================================================

def verify_after_insert(
    cursor
):

    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = 2;
    """)

    lesson_count = int(
        cursor.fetchone()[0]
    )

    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.TuVungBaiHoc tvbh
        INNER JOIN dbo.BaiHoc bh
            ON bh.MaBaiHoc = tvbh.MaBaiHoc
        WHERE bh.MaKhoaHoc = 2;
    """)

    vocab_count = int(
        cursor.fetchone()[0]
    )

    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.NguPhap np
        INNER JOIN dbo.BaiHoc bh
            ON bh.MaBaiHoc = np.MaBaiHoc
        WHERE bh.MaKhoaHoc = 2;
    """)

    grammar_count = int(
        cursor.fetchone()[0]
    )

    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.ChuHan ch
        INNER JOIN dbo.BaiHoc bh
            ON bh.MaBaiHoc = ch.MaBaiHoc
        WHERE bh.MaKhoaHoc = 2;
    """)

    hanzi_count = int(
        cursor.fetchone()[0]
    )

    print()
    print("KIEM TRA SAU INSERT:")
    print(
        f"  BaiHoc HSK2       : {lesson_count}/23"
    )
    print(
        f"  TuVungBaiHoc HSK2 : {vocab_count}/772"
    )
    print(
        f"  NguPhap HSK2      : {grammar_count}/48"
    )
    print(
        f"  ChuHan HSK2       : {hanzi_count}/299"
    )

    if lesson_count != 23:
        raise ValueError(
            "Sai so luong BaiHoc HSK2."
        )

    if vocab_count != 772:
        raise ValueError(
            "Sai so luong TuVungBaiHoc HSK2."
        )

    if grammar_count != 48:
        raise ValueError(
            "Sai so luong NguPhap HSK2."
        )

    if hanzi_count != 299:
        raise ValueError(
            "Sai so luong ChuHan HSK2."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("BUOC 19 - IMPORT TOAN BO HOC LIEU HSK2 VAO SQL")
    print("23 BAI + 772 TU + 48 NGU PHAP + 299 CHU HAN")
    print("=" * 80)

    commit_mode = (
        len(sys.argv) > 1
        and sys.argv[1].lower()
        == "--commit"
    )

    if commit_mode:

        print()
        print(
            "CHE DO: COMMIT - SE GHI DU LIEU VAO SQL"
        )

    else:

        print()
        print(
            "CHE DO: PREVIEW - CHI KIEM TRA, "
            "KHONG GHI SQL"
        )

    (
        lessons,
        vocab,
        grammar,
        hanzi
    ) = load_and_validate_files()

    print()
    print("KIEM TRA FILE:")
    print(
        f"  BaiHoc : {len(lessons)}/23"
    )
    print(
        f"  TuVung : {len(vocab)}/772"
    )
    print(
        f"  NguPhap: {len(grammar)}/48"
    )
    print(
        f"  ChuHan : {len(hanzi)}/299"
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        preflight_database(
            cursor,
            vocab
        )

        # ====================================================
        # PREVIEW
        # ====================================================

        if not commit_mode:

            connection.rollback()

            print()
            print(
                "PREVIEW HOAN TAT."
            )

            print(
                "KHONG INSERT/UPDATE/DELETE SQL."
            )

            print()
            print(
                "Neu tat ca deu dung, chay:"
            )

            print(
                "python scripts\\hsk2\\"
                "19_import_hsk2_learning_content.py "
                "--commit"
            )

            return

        # ====================================================
        # COMMIT
        # ====================================================

        hanzi_source_id, source_created = (
            get_or_create_hanzi_source(
                cursor
            )
        )

        print()
        print(
            f"MaNguon ChuHan HSK2: "
            f"{hanzi_source_id}"
        )

        print(
            "Nguon ChuHan moi tao: "
            + (
                "CO"
                if source_created
                else "KHONG"
            )
        )

        lesson_map = insert_lessons(
            cursor,
            lessons
        )

        print()
        print(
            "Da tao 23 BaiHoc HSK2."
        )

        insert_vocabulary_links(
            cursor,
            vocab,
            lesson_map
        )

        print(
            "Da gan 772 TuVung vao BaiHoc."
        )

        insert_grammar(
            cursor,
            grammar,
            lesson_map
        )

        print(
            "Da INSERT 48 NguPhap."
        )

        insert_hanzi(
            cursor,
            hanzi,
            lesson_map,
            hanzi_source_id
        )

        print(
            "Da INSERT 299 ChuHan."
        )

        verify_after_insert(
            cursor
        )

        connection.commit()

        print()
        print("=" * 80)
        print(
            "COMMIT THANH CONG."
        )
        print("=" * 80)

        print()
        print(
            "HSK2 da co du lieu that trong SQL."
        )

        print(
            "BaiHoc/NguPhap/ChuHan "
            "van dang TrangThai='ban_nhap'."
        )

        print(
            "KhoaHoc HSK2 van chua duoc "
            "chuyen sang da_xuat_ban."
        )

    except Exception:

        connection.rollback()

        print()
        print(
            "CO LOI -> DA ROLLBACK TOAN BO."
        )

        print(
            "KHONG GIU LAI DU LIEU "
            "INSERT DO DANG."
        )

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()