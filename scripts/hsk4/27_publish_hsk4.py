# -*- coding: utf-8 -*-

"""
BUOC 27 - CONG BO KHOA HOC HSK4

Doi TrangThai:
- KhoaHoc : ban_nhap -> cong_bo
- BaiHoc  : ban_nhap -> cong_bo
- NguPhap : ban_nhap -> cong_bo
- ChuHan  : ban_nhap -> cong_bo

KHONG:
- Sua TuVung
- Sua audio
- Sua HSK1/HSK2/HSK3
"""

import sys
from contextlib import closing
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection


COURSE_ID = 4
COURSE_CODE = "HSK4-CORE"

EXPECTED_LESSONS = 20
EXPECTED_VOCAB = 1000
EXPECTED_GRAMMAR = 114
EXPECTED_HANZI = 300


def clean(value):
    return str(value).strip() if value is not None else ""


def fail(message):
    raise RuntimeError(message)


def scalar(cursor, sql, params=()):
    cursor.execute(sql, params)
    row = cursor.fetchone()

    if row is None:
        return None

    return row[0]


def main():

    print("=" * 78)
    print("BUOC 27 - CONG BO HSK4")
    print("=" * 78)

    with closing(get_connection()) as conn:

        if conn is None:
            fail("Khong ket noi duoc SQL Server.")

        if getattr(conn, "autocommit", False):
            fail("SQL dang autocommit=True. Dung lai de dam bao transaction.")

        with closing(conn.cursor()) as cursor:

            # =========================================================
            # 1. DATABASE
            # =========================================================

            print("\n[1] KIEM TRA DATABASE")

            cursor.execute("SELECT DB_NAME();")
            db_name = clean(cursor.fetchone()[0])

            print("Database:", db_name)

            if db_name.lower() != "hoctiengtrungdb":
                fail(
                    "Dang ket noi sai database: "
                    + db_name
                )

            print("PASS: dung HocTiengTrungDB.")

            # =========================================================
            # 2. KHOA HOC HSK4
            # =========================================================

            print("\n[2] KIEM TRA KHOA HOC HSK4")

            cursor.execute(
                """
                SELECT
                    MaKhoaHoc,
                    MaCapDo,
                    MaKyHieu,
                    TrangThai
                FROM dbo.KhoaHoc
                WHERE MaKhoaHoc = ?;
                """,
                COURSE_ID,
            )

            rows = cursor.fetchall()

            if len(rows) != 1:
                fail("Khong tim thay dung 1 khoa HSK4.")

            course = rows[0]

            print("MaKhoaHoc :", course[0])
            print("MaCapDo   :", course[1])
            print("MaKyHieu  :", course[2])
            print("TrangThai :", course[3])

            if int(course[0]) != COURSE_ID:
                fail("Sai MaKhoaHoc.")

            if int(course[1]) != 4:
                fail("Sai MaCapDo.")

            if clean(course[2]) != COURSE_CODE:
                fail("Sai MaKyHieu.")

            if clean(course[3]) != "ban_nhap":
                fail(
                    "HSK4 khong con o trang thai ban_nhap. "
                    "Khong tu dong cap nhat."
                )

            print("PASS: HSK4 dang ban_nhap.")

            # =========================================================
            # 3. XAC NHAN cong_bo LA TRANG THAI DA DUOC SU DUNG
            # =========================================================

            print("\n[3] KIEM TRA TRANG THAI cong_bo TRONG HE THONG")

            cursor.execute(
                """
                SELECT
                    MaKhoaHoc,
                    MaKyHieu,
                    TrangThai
                FROM dbo.KhoaHoc
                WHERE MaKhoaHoc <> ?
                ORDER BY MaKhoaHoc;
                """,
                COURSE_ID,
            )

            other_courses = cursor.fetchall()

            found_published = False

            for row in other_courses:
                print(
                    f"MaKhoaHoc={row[0]} | "
                    f"{clean(row[1])} | "
                    f"TrangThai={clean(row[2])}"
                )

                if clean(row[2]) == "cong_bo":
                    found_published = True

            if not found_published:
                fail(
                    "Khong tim thay khoa hoc nao dang dung "
                    "TrangThai='cong_bo'. DUNG LAI de xac minh "
                    "ten trang thai truoc khi ghi SQL."
                )

            print("PASS: cong_bo la trang thai dang duoc su dung.")

            # =========================================================
            # 4. KIEM TRA SO LUONG HSK4
            # =========================================================

            print("\n[4] KIEM TRA DU LIEU HSK4")

            lesson_count = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = ?;
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            vocab_count = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.TuVungBaiHoc AS tvbh
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = tvbh.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            grammar_count = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap AS np
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = np.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            hanzi_count = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChuHan AS ch
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = ch.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            print("BaiHoc       :", lesson_count)
            print("TuVungBaiHoc :", vocab_count)
            print("NguPhap      :", grammar_count)
            print("ChuHan       :", hanzi_count)

            if lesson_count != EXPECTED_LESSONS:
                fail(
                    f"BaiHoc={lesson_count}, "
                    f"can {EXPECTED_LESSONS}."
                )

            if vocab_count != EXPECTED_VOCAB:
                fail(
                    f"TuVungBaiHoc={vocab_count}, "
                    f"can {EXPECTED_VOCAB}."
                )

            if grammar_count != EXPECTED_GRAMMAR:
                fail(
                    f"NguPhap={grammar_count}, "
                    f"can {EXPECTED_GRAMMAR}."
                )

            if hanzi_count != EXPECTED_HANZI:
                fail(
                    f"ChuHan={hanzi_count}, "
                    f"can {EXPECTED_HANZI}."
                )

            print("PASS: du 20 / 1000 / 114 / 300.")

            # =========================================================
            # 5. KIEM TRA AUDIO
            # =========================================================

            print("\n[5] KIEM TRA AUDIO HSK4")

            vocab_audio = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(DISTINCT tv.MaTuVung)
                    FROM dbo.TuVungBaiHoc AS tvbh
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = tvbh.MaBaiHoc
                    JOIN dbo.TuVung AS tv
                        ON tv.MaTuVung = tvbh.MaTuVung
                    JOIN dbo.TepDaPhuongTien AS m
                        ON m.MaTep = tv.MaAmThanh
                    WHERE bh.MaKhoaHoc = ?
                      AND m.LoaiTep = 'am_thanh';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            hanzi_audio = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChuHan AS ch
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = ch.MaBaiHoc
                    JOIN dbo.TepDaPhuongTien AS m
                        ON m.MaTep = ch.MaTep
                    WHERE bh.MaKhoaHoc = ?
                      AND m.LoaiTep = 'am_thanh';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            print(
                f"Audio TuVung: {vocab_audio}/{EXPECTED_VOCAB}"
            )
            print(
                f"Audio ChuHan : {hanzi_audio}/{EXPECTED_HANZI}"
            )

            if vocab_audio != EXPECTED_VOCAB:
                fail("HSK4 chua du audio tu vung.")

            if hanzi_audio != EXPECTED_HANZI:
                fail("HSK4 chua du audio chu Han.")

            print("PASS: audio HSK4 da day du.")

            # =========================================================
            # 6. KIEM TRA TRANG THAI CON
            # =========================================================

            print("\n[6] KIEM TRA TRANG THAI NOI DUNG")

            lesson_draft = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = ?
                      AND TrangThai = 'ban_nhap';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            grammar_draft = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap AS np
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = np.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?
                      AND np.TrangThai = 'ban_nhap';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            hanzi_draft = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChuHan AS ch
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = ch.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?
                      AND ch.TrangThai = 'ban_nhap';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            print("BaiHoc ban_nhap :", lesson_draft)
            print("NguPhap ban_nhap:", grammar_draft)
            print("ChuHan ban_nhap :", hanzi_draft)

            if lesson_draft != 20:
                fail(
                    "Khong phai ca 20 BaiHoc deu dang ban_nhap."
                )

            if grammar_draft != 114:
                fail(
                    "Khong phai ca 114 NguPhap deu dang ban_nhap."
                )

            if hanzi_draft != 300:
                fail(
                    "Khong phai ca 300 ChuHan deu dang ban_nhap."
                )

            print("PASS: noi dung dang o trang thai ban_nhap.")

            # =========================================================
            # 7. XAC NHAN
            # =========================================================

            print("\n" + "=" * 78)
            print("SAN SANG CONG BO HSK4")
            print("=" * 78)

            print("Se doi:")
            print("  KhoaHoc HSK4 : ban_nhap -> cong_bo")
            print("  20 BaiHoc     : ban_nhap -> cong_bo")
            print("  114 NguPhap   : ban_nhap -> cong_bo")
            print("  300 ChuHan    : ban_nhap -> cong_bo")
            print()
            print("KHONG sua TuVung.")
            print("KHONG sua audio.")
            print("KHONG dong vao HSK1/HSK2/HSK3.")
            print()

            confirm = input(
                "Nhap chinh xac PUBLISH HSK4 de cong bo: "
            ).strip()

            if confirm != "PUBLISH HSK4":
                conn.rollback()

                print()
                print("CANCEL: khong dung chuoi xac nhan.")
                print("PASS: KHONG CO DU LIEU NAO BI THAY DOI.")
                return

            # =========================================================
            # 8. UPDATE TRONG TRANSACTION
            # =========================================================

            print("\n[8] CAP NHAT TRANG THAI")

            cursor.execute(
                """
                UPDATE dbo.BaiHoc
                SET TrangThai = 'cong_bo'
                WHERE MaKhoaHoc = ?
                  AND TrangThai = 'ban_nhap';
                """,
                COURSE_ID,
            )

            updated_lessons = cursor.rowcount
            print("BaiHoc updated:", updated_lessons)

            if updated_lessons != 20:
                fail(
                    f"Chi update duoc {updated_lessons}/20 BaiHoc."
                )

            cursor.execute(
                """
                UPDATE np
                SET np.TrangThai = 'cong_bo'
                FROM dbo.NguPhap AS np
                JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc = np.MaBaiHoc
                WHERE bh.MaKhoaHoc = ?
                  AND np.TrangThai = 'ban_nhap';
                """,
                COURSE_ID,
            )

            updated_grammar = cursor.rowcount
            print("NguPhap updated:", updated_grammar)

            if updated_grammar != 114:
                fail(
                    f"Chi update duoc "
                    f"{updated_grammar}/114 NguPhap."
                )

            cursor.execute(
                """
                UPDATE ch
                SET ch.TrangThai = 'cong_bo'
                FROM dbo.ChuHan AS ch
                JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc = ch.MaBaiHoc
                WHERE bh.MaKhoaHoc = ?
                  AND ch.TrangThai = 'ban_nhap';
                """,
                COURSE_ID,
            )

            updated_hanzi = cursor.rowcount
            print("ChuHan updated:", updated_hanzi)

            if updated_hanzi != 300:
                fail(
                    f"Chi update duoc "
                    f"{updated_hanzi}/300 ChuHan."
                )

            cursor.execute(
                """
                UPDATE dbo.KhoaHoc
                SET TrangThai = 'cong_bo'
                WHERE MaKhoaHoc = ?
                  AND MaKyHieu = ?
                  AND TrangThai = 'ban_nhap';
                """,
                COURSE_ID,
                COURSE_CODE,
            )

            updated_course = cursor.rowcount
            print("KhoaHoc updated:", updated_course)

            if updated_course != 1:
                fail(
                    "Khong update duoc chinh xac 1 KhoaHoc."
                )

            # =========================================================
            # 9. VALIDATE TRUOC COMMIT
            # =========================================================

            print("\n[9] VALIDATE TRUOC COMMIT")

            course_status = clean(
                scalar(
                    cursor,
                    """
                    SELECT TrangThai
                    FROM dbo.KhoaHoc
                    WHERE MaKhoaHoc = ?;
                    """,
                    (COURSE_ID,),
                )
            )

            published_lessons = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = ?
                      AND TrangThai = 'cong_bo';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            published_grammar = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap AS np
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = np.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?
                      AND np.TrangThai = 'cong_bo';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            published_hanzi = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChuHan AS ch
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = ch.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?
                      AND ch.TrangThai = 'cong_bo';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            print("KhoaHoc :", course_status)
            print(
                "BaiHoc  :",
                f"{published_lessons}/20 cong_bo"
            )
            print(
                "NguPhap :",
                f"{published_grammar}/114 cong_bo"
            )
            print(
                "ChuHan  :",
                f"{published_hanzi}/300 cong_bo"
            )

            if course_status != "cong_bo":
                fail("KhoaHoc chua cong_bo.")

            if published_lessons != 20:
                fail("Chua du 20 BaiHoc cong_bo.")

            if published_grammar != 114:
                fail("Chua du 114 NguPhap cong_bo.")

            if published_hanzi != 300:
                fail("Chua du 300 ChuHan cong_bo.")

            print("PASS: transaction hop le.")

            # =========================================================
            # 10. COMMIT
            # =========================================================

            print("\n[10] COMMIT")

            conn.commit()

            print("PASS: DA COMMIT.")

            # =========================================================
            # 11. VERIFY SAU COMMIT
            # =========================================================

            print("\n[11] KIEM TRA SAU COMMIT")

            final_status = clean(
                scalar(
                    cursor,
                    """
                    SELECT TrangThai
                    FROM dbo.KhoaHoc
                    WHERE MaKhoaHoc = ?;
                    """,
                    (COURSE_ID,),
                )
            )

            final_lessons = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = ?
                      AND TrangThai = 'cong_bo';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            final_grammar = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.NguPhap AS np
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = np.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?
                      AND np.TrangThai = 'cong_bo';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            final_hanzi = int(
                scalar(
                    cursor,
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChuHan AS ch
                    JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = ch.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?
                      AND ch.TrangThai = 'cong_bo';
                    """,
                    (COURSE_ID,),
                )
                or 0
            )

            print("KhoaHoc HSK4:", final_status)
            print("BaiHoc       :", f"{final_lessons}/20")
            print("NguPhap      :", f"{final_grammar}/114")
            print("ChuHan       :", f"{final_hanzi}/300")

            if (
                final_status != "cong_bo"
                or final_lessons != 20
                or final_grammar != 114
                or final_hanzi != 300
            ):
                fail(
                    "Du lieu sau COMMIT khong dung. "
                    "KHONG chay lai script."
                )

            print()
            print("=" * 78)
            print("PASS: BUOC 27 - HSK4 DA DUOC CONG BO")
            print("=" * 78)
            print("KhoaHoc : cong_bo")
            print("BaiHoc  : 20/20 cong_bo")
            print("NguPhap : 114/114 cong_bo")
            print("ChuHan  : 300/300 cong_bo")
            print("TuVung  : KHONG THAY DOI")
            print("Audio   : KHONG THAY DOI")
            print("=" * 78)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nDA DUNG THEO YEU CAU.")
        raise SystemExit(130)

    except Exception as error:
        print("\nCHUONG TRINH DUNG VI LOI:")
        print(error)
        raise SystemExit(1)