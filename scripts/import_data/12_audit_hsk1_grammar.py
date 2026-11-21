from pathlib import Path
import sys
from contextlib import closing


# =========================================================
# PROJECT ROOT
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


from database import get_connection


COURSE_CODE = "HSK1-CORE"


# =========================================================
# HELPER
# =========================================================
def print_title(title):

    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def row_to_dict(cursor, row):

    columns = [
        column[0]
        for column in cursor.description
    ]

    return dict(
        zip(
            columns,
            row
        )
    )


def safe_text(value):

    if value is None:
        return ""

    return str(value).strip()


# =========================================================
# MAIN
# =========================================================
def main():

    print_title(
        "AUDIT NGU PHAP HSK1 - READ ONLY"
    )

    print(
        "Course:",
        COURSE_CODE
    )

    print(
        "Che do: CHI DOC - KHONG UPDATE / INSERT / DELETE"
    )


    with closing(
        get_connection()
    ) as conn:

        with closing(
            conn.cursor()
        ) as cursor:

            # =================================================
            # 1. KIEM TRA KHOA HOC
            # =================================================
            print_title(
                "1. KIEM TRA KHOA HOC"
            )

            cursor.execute(
                """
                SELECT
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.MaKyHieu,
                    kh.TieuDe,
                    kh.TrangThai

                FROM dbo.KhoaHoc AS kh

                WHERE kh.MaKyHieu = ?;
                """,
                COURSE_CODE
            )

            course_row = cursor.fetchone()

            if course_row is None:

                print(
                    "LOI: Khong tim thay khoa hoc",
                    COURSE_CODE
                )

                return


            course = row_to_dict(
                cursor,
                course_row
            )


            print(
                "MaKhoaHoc :",
                course["MaKhoaHoc"]
            )

            print(
                "MaCapDo   :",
                course["MaCapDo"]
            )

            print(
                "MaKyHieu  :",
                course["MaKyHieu"]
            )

            print(
                "TieuDe    :",
                course["TieuDe"]
            )

            print(
                "TrangThai :",
                course["TrangThai"]
            )


            # =================================================
            # 2. TONG SO BAI HOC HSK1
            # =================================================
            print_title(
                "2. TONG SO BAI HOC HSK1"
            )

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongBaiHoc

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                WHERE kh.MaKyHieu = ?;
                """,
                COURSE_CODE
            )

            total_lessons = (
                cursor.fetchone()[0]
            )


            print(
                "Tong bai hoc:",
                total_lessons
            )


            # =================================================
            # 3. TONG SO NGU PHAP + CAC TRUONG THIEU
            # =================================================
            print_title(
                "3. KIEM TRA DO DAY DU DU LIEU NGU PHAP"
            )

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongNguPhap,

                    SUM(
                        CASE
                            WHEN ng.TenCauTruc IS NULL
                                 OR LTRIM(
                                        RTRIM(
                                            ng.TenCauTruc
                                        )
                                    ) = N''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuTenCauTruc,

                    SUM(
                        CASE
                            WHEN ng.MoTa IS NULL
                                 OR LTRIM(
                                        RTRIM(
                                            ng.MoTa
                                        )
                                    ) = N''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuMoTa,

                    SUM(
                        CASE
                            WHEN ng.CachDung IS NULL
                                 OR LTRIM(
                                        RTRIM(
                                            ng.CachDung
                                        )
                                    ) = N''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuCachDung,

                    SUM(
                        CASE
                            WHEN ng.ViDuTiengTrung IS NULL
                                 OR LTRIM(
                                        RTRIM(
                                            ng.ViDuTiengTrung
                                        )
                                    ) = N''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuViDuTrung,

                    SUM(
                        CASE
                            WHEN ng.ViDuPinyin IS NULL
                                 OR LTRIM(
                                        RTRIM(
                                            ng.ViDuPinyin
                                        )
                                    ) = N''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuPinyin,

                    SUM(
                        CASE
                            WHEN ng.ViDuTiengViet IS NULL
                                 OR LTRIM(
                                        RTRIM(
                                            ng.ViDuTiengViet
                                        )
                                    ) = N''
                            THEN 1
                            ELSE 0
                        END
                    ) AS ThieuViDuViet,

                    SUM(
                        CASE
                            WHEN ng.MaTep IS NULL
                            THEN 1
                            ELSE 0
                        END
                    ) AS ChuaCoMaTep

                FROM dbo.NguPhap AS ng

                INNER JOIN dbo.BaiHoc AS bh
                    ON ng.MaBaiHoc = bh.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                WHERE kh.MaKyHieu = ?;
                """,
                COURSE_CODE
            )

            audit_row = cursor.fetchone()

            audit = row_to_dict(
                cursor,
                audit_row
            )


            for key, value in audit.items():

                print(
                    f"{key:<20}: {value}"
                )


            # =================================================
            # 4. PHAN BO NGU PHAP THEO 23 BAI
            # =================================================
            print_title(
                "4. PHAN BO NGU PHAP THEO TUNG BAI"
            )

            cursor.execute(
                """
                SELECT
                    bh.MaBaiHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe AS TenBaiHoc,

                    COUNT(
                        ng.MaNguPhap
                    ) AS SoNguPhap

                FROM dbo.BaiHoc AS bh

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                LEFT JOIN dbo.NguPhap AS ng
                    ON bh.MaBaiHoc = ng.MaBaiHoc

                WHERE kh.MaKyHieu = ?

                GROUP BY
                    bh.MaBaiHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe

                ORDER BY
                    bh.SoThuTuBai;
                """,
                COURSE_CODE
            )

            lesson_rows = (
                cursor.fetchall()
            )


            total_by_lessons = 0

            lessons_without_grammar = []


            print(
                f"{'Bai':<6}"
                f"{'So NP':<8}"
                f"Ten bai"
            )

            print(
                "-" * 78
            )


            for row in lesson_rows:

                item = row_to_dict(
                    cursor,
                    row
                )


                count = (
                    item["SoNguPhap"]
                    or 0
                )


                total_by_lessons += (
                    count
                )


                if count == 0:

                    lessons_without_grammar.append(
                        item["SoThuTuBai"]
                    )


                print(
                    f"{item['SoThuTuBai']:<6}"
                    f"{count:<8}"
                    f"{item['TenBaiHoc']}"
                )


            print()
            print(
                "Tong cong:",
                total_by_lessons
            )


            if (
                lessons_without_grammar
            ):

                print(
                    "Bai chua co ngu phap:",
                    lessons_without_grammar
                )

            else:

                print(
                    "OK: Tat ca bai deu co ngu phap."
                )


            # =================================================
            # 5. KIEM TRA BAN GHI THIEU NOI DUNG
            # =================================================
            print_title(
                "5. DANH SACH NGU PHAP THIEU NOI DUNG"
            )

            cursor.execute(
                """
                SELECT
                    bh.SoThuTuBai,

                    ng.MaNguPhap,
                    ng.ThuTu,
                    ng.TenCauTruc,

                    ng.MoTa,
                    ng.CachDung,

                    ng.ViDuTiengTrung,
                    ng.ViDuPinyin,
                    ng.ViDuTiengViet,

                    ng.MaTep,
                    ng.TrangThai

                FROM dbo.NguPhap AS ng

                INNER JOIN dbo.BaiHoc AS bh
                    ON ng.MaBaiHoc = bh.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                WHERE
                    kh.MaKyHieu = ?

                    AND
                    (
                        ng.TenCauTruc IS NULL
                        OR LTRIM(
                            RTRIM(
                                ng.TenCauTruc
                            )
                        ) = N''

                        OR ng.MoTa IS NULL
                        OR LTRIM(
                            RTRIM(
                                ng.MoTa
                            )
                        ) = N''

                        OR ng.CachDung IS NULL
                        OR LTRIM(
                            RTRIM(
                                ng.CachDung
                            )
                        ) = N''

                        OR ng.ViDuTiengTrung IS NULL
                        OR LTRIM(
                            RTRIM(
                                ng.ViDuTiengTrung
                            )
                        ) = N''

                        OR ng.ViDuPinyin IS NULL
                        OR LTRIM(
                            RTRIM(
                                ng.ViDuPinyin
                            )
                        ) = N''

                        OR ng.ViDuTiengViet IS NULL
                        OR LTRIM(
                            RTRIM(
                                ng.ViDuTiengViet
                            )
                        ) = N''
                    )

                ORDER BY
                    bh.SoThuTuBai,
                    ng.ThuTu,
                    ng.MaNguPhap;
                """,
                COURSE_CODE
            )

            incomplete_rows = (
                cursor.fetchall()
            )


            if (
                not incomplete_rows
            ):

                print(
                    "OK: Khong co ban ghi nao thieu "
                    "TenCauTruc / MoTa / CachDung / "
                    "ViDuTrung / Pinyin / ViDuViet."
                )

            else:

                print(
                    "So ban ghi thieu:",
                    len(
                        incomplete_rows
                    )
                )

                print()

                for row in incomplete_rows:

                    item = row_to_dict(
                        cursor,
                        row
                    )


                    missing = []


                    if not safe_text(
                        item["TenCauTruc"]
                    ):
                        missing.append(
                            "TenCauTruc"
                        )


                    if not safe_text(
                        item["MoTa"]
                    ):
                        missing.append(
                            "MoTa"
                        )


                    if not safe_text(
                        item["CachDung"]
                    ):
                        missing.append(
                            "CachDung"
                        )


                    if not safe_text(
                        item["ViDuTiengTrung"]
                    ):
                        missing.append(
                            "ViDuTiengTrung"
                        )


                    if not safe_text(
                        item["ViDuPinyin"]
                    ):
                        missing.append(
                            "ViDuPinyin"
                        )


                    if not safe_text(
                        item["ViDuTiengViet"]
                    ):
                        missing.append(
                            "ViDuTiengViet"
                        )


                    print(
                        "Bai",
                        item["SoThuTuBai"],
                        "| MaNguPhap:",
                        item["MaNguPhap"],
                        "| ThuTu:",
                        item["ThuTu"]
                    )

                    print(
                        "  Cau truc:",
                        item["TenCauTruc"]
                    )

                    print(
                        "  Thieu:",
                        ", ".join(
                            missing
                        )
                    )

                    print()


            # =================================================
            # 6. KIEM TRA THU TU TRUNG TRONG CUNG BAI
            # =================================================
            print_title(
                "6. KIEM TRA THU TU NGU PHAP BI TRUNG"
            )

            cursor.execute(
                """
                SELECT
                    bh.SoThuTuBai,
                    ng.ThuTu,
                    COUNT(*) AS SoBanGhi

                FROM dbo.NguPhap AS ng

                INNER JOIN dbo.BaiHoc AS bh
                    ON ng.MaBaiHoc = bh.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                WHERE kh.MaKyHieu = ?

                GROUP BY
                    bh.SoThuTuBai,
                    ng.ThuTu

                HAVING COUNT(*) > 1

                ORDER BY
                    bh.SoThuTuBai,
                    ng.ThuTu;
                """,
                COURSE_CODE
            )

            duplicate_orders = (
                cursor.fetchall()
            )


            if (
                duplicate_orders
            ):

                print(
                    "CAN KIEM TRA: Co ThuTu bi trung."
                )


                for row in duplicate_orders:

                    item = row_to_dict(
                        cursor,
                        row
                    )


                    print(
                        "Bai",
                        item["SoThuTuBai"],
                        "| ThuTu",
                        item["ThuTu"],
                        "| So ban ghi:",
                        item["SoBanGhi"]
                    )

            else:

                print(
                    "OK: Khong co ThuTu ngu phap bi trung."
                )


            # =================================================
            # 7. KIEM TRA MaTep NEU DA GAN
            # =================================================
            print_title(
                "7. KIEM TRA LIEN KET TEP NGU PHAP"
            )

            cursor.execute(
                """
                SELECT
                    COUNT(*) AS TongNguPhap,

                    SUM(
                        CASE
                            WHEN ng.MaTep IS NOT NULL
                            THEN 1
                            ELSE 0
                        END
                    ) AS DaCoMaTep,

                    SUM(
                        CASE
                            WHEN ng.MaTep IS NULL
                            THEN 1
                            ELSE 0
                        END
                    ) AS ChuaCoMaTep,

                    SUM(
                        CASE
                            WHEN ng.MaTep IS NOT NULL
                                 AND t.MaTep IS NULL
                            THEN 1
                            ELSE 0
                        END
                    ) AS MaTepKhongTonTai

                FROM dbo.NguPhap AS ng

                INNER JOIN dbo.BaiHoc AS bh
                    ON ng.MaBaiHoc = bh.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                LEFT JOIN dbo.TepDaPhuongTien AS t
                    ON ng.MaTep = t.MaTep

                WHERE kh.MaKyHieu = ?;
                """,
                COURSE_CODE
            )

            media_row = (
                cursor.fetchone()
            )


            media = row_to_dict(
                cursor,
                media_row
            )


            for key, value in media.items():

                print(
                    f"{key:<20}: {value}"
                )


            # =================================================
            # 8. CHI TIET NGU PHAP BAI 1
            # =================================================
            print_title(
                "8. CHI TIET NGU PHAP BAI 1"
            )

            cursor.execute(
                """
                SELECT
                    ng.MaNguPhap,
                    ng.ThuTu,

                    ng.TenCauTruc,
                    ng.MoTa,
                    ng.CachDung,

                    ng.ViDuTiengTrung,
                    ng.ViDuPinyin,
                    ng.ViDuTiengViet,

                    ng.MaTep,
                    ng.MaNguon,
                    ng.TrangThai

                FROM dbo.NguPhap AS ng

                INNER JOIN dbo.BaiHoc AS bh
                    ON ng.MaBaiHoc = bh.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc = kh.MaKhoaHoc

                WHERE
                    kh.MaKyHieu = ?
                    AND bh.SoThuTuBai = 1

                ORDER BY
                    ng.ThuTu,
                    ng.MaNguPhap;
                """,
                COURSE_CODE
            )

            grammar_rows = (
                cursor.fetchall()
            )


            print(
                "So ngu phap Bai 1:",
                len(
                    grammar_rows
                )
            )

            print()


            for row in grammar_rows:

                item = row_to_dict(
                    cursor,
                    row
                )


                print(
                    "-" * 78
                )

                print(
                    "MaNguPhap:",
                    item["MaNguPhap"],
                    "| ThuTu:",
                    item["ThuTu"]
                )

                print(
                    "TenCauTruc:",
                    item["TenCauTruc"]
                )

                print(
                    "MoTa:",
                    item["MoTa"]
                )

                print(
                    "CachDung:",
                    item["CachDung"]
                )

                print(
                    "ViDuTiengTrung:",
                    item["ViDuTiengTrung"]
                )

                print(
                    "ViDuPinyin:",
                    item["ViDuPinyin"]
                )

                print(
                    "ViDuTiengViet:",
                    item["ViDuTiengViet"]
                )

                print(
                    "MaTep:",
                    item["MaTep"]
                )

                print(
                    "TrangThai:",
                    item["TrangThai"]
                )


            # =================================================
            # 9. KET LUAN TU DONG
            # =================================================
            print_title(
                "9. KET LUAN"
            )


            print(
                "Tong bai HSK1:",
                total_lessons
            )


            print(
                "Tong ngu phap HSK1:",
                audit["TongNguPhap"]
            )


            print(
                "Ban ghi thieu noi dung:",
                len(
                    incomplete_rows
                )
            )


            print(
                "ThuTu bi trung:",
                len(
                    duplicate_orders
                )
            )


            print(
                "Bai khong co ngu phap:",
                len(
                    lessons_without_grammar
                )
            )


            if (
                audit["TongNguPhap"] == 88
                and total_lessons == 23
                and len(
                    lessons_without_grammar
                ) == 0
                and len(
                    incomplete_rows
                ) == 0
                and len(
                    duplicate_orders
                ) == 0
            ):

                print()
                print(
                    "OK: DU LIEU NGU PHAP HSK1 "
                    "CO BAN DA DAY DU."
                )


            print()
            print(
                "AUDIT HOAN TAT - KHONG CO DU LIEU NAO BI THAY DOI."
            )


if __name__ == "__main__":

    main()