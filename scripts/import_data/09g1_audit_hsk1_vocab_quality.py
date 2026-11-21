from pathlib import Path
import sys
from collections import Counter, defaultdict


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


COURSE_CODE = "HSK1-CORE"


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def make_key(chinese, pinyin):
    return (
        clean(chinese),
        clean(pinyin).lower(),
    )


def main():

    conn = None
    cursor = None

    try:

        print("=" * 95)
        print("09G1 - KIEM TRA CHAT LUONG TU VUNG HSK1")
        print("=" * 95)

        conn = get_connection()
        cursor = conn.cursor()

        # =================================================
        # 1. DOC TOAN BO TU VUNG CUA HSK1 COURSE
        # =================================================
        cursor.execute(
            """
            SELECT
                bh.SoThuTuBai,
                bh.TieuDe AS TieuDeBai,
                tvbh.ThuTu,
                tv.MaTuVung,
                tv.ChuHan,
                tv.ChuPhonThe,
                tv.PhienAm,
                tv.NghiaTiengViet,
                tv.TuLoai,
                tv.MaNguon,
                tv.DaDuyet
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc = tvbh.MaBaiHoc

            INNER JOIN dbo.KhoaHoc kh
                ON kh.MaKhoaHoc = bh.MaKhoaHoc

            INNER JOIN dbo.TuVung tv
                ON tv.MaTuVung = tvbh.MaTuVung

            WHERE kh.MaKyHieu = ?

            ORDER BY
                bh.SoThuTuBai,
                tvbh.ThuTu
            """,
            COURSE_CODE,
        )

        rows = cursor.fetchall()

        print()
        print("Tong lien ket tu vung:", len(rows))

        if len(rows) != 501:
            raise RuntimeError(
                f"HSK1 course phai co 501 lien ket. "
                f"Thuc te: {len(rows)}"
            )

        # =================================================
        # 2. DEM TU KHAC NHAU
        # =================================================
        unique_ids = {
            row.MaTuVung
            for row in rows
        }

        print(
            "TuVung khac nhau:",
            len(unique_ids),
        )

        if len(unique_ids) != 501:
            raise RuntimeError(
                "Co TuVung bi gan nhieu hon 1 bai."
            )

        # =================================================
        # 3. KIEM TRA NGUON
        # =================================================
        source_counter = Counter(
            row.MaNguon
            for row in rows
        )

        print()
        print("-" * 95)
        print("PHAN BO NGUON")
        print("-" * 95)

        for source_id, count in sorted(
            source_counter.items(),
            key=lambda x: (
                x[0] is None,
                x[0] if x[0] is not None else 0
            ),
        ):

            if source_id is None:

                source_name = "NULL"

            else:

                cursor.execute(
                    """
                    SELECT Ten
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = ?
                    """,
                    source_id,
                )

                source_row = cursor.fetchone()

                source_name = (
                    source_row.Ten
                    if source_row
                    else "KHONG TIM THAY NGUON"
                )

            print(
                f"MaNguon={source_id}"
                f" | {source_name}"
                f" | {count} tu"
            )

        # =================================================
        # 4. CAC LOI BAT BUOC
        # =================================================
        missing_hanzi = []
        missing_pinyin = []
        missing_meaning = []
        missing_source = []

        for row in rows:

            if not clean(row.ChuHan):
                missing_hanzi.append(row)

            if not clean(row.PhienAm):
                missing_pinyin.append(row)

            if not clean(row.NghiaTiengViet):
                missing_meaning.append(row)

            if row.MaNguon is None:
                missing_source.append(row)

        # =================================================
        # 5. TU THIEU TuLoai
        # =================================================
        missing_word_type = [
            row
            for row in rows
            if not clean(row.TuLoai)
        ]

        # =================================================
        # 6. KIEM TRA TRUNG ChuHan + PhienAm
        # =================================================
        by_key = defaultdict(list)

        for row in rows:

            by_key[
                make_key(
                    row.ChuHan,
                    row.PhienAm,
                )
            ].append(row)

        duplicate_keys = {
            key: values
            for key, values in by_key.items()
            if len(values) > 1
        }

        # =================================================
        # 7. KIEM TRA DaDuyet
        # =================================================
        approved = [
            row
            for row in rows
            if row.DaDuyet
        ]

        unapproved = [
            row
            for row in rows
            if not row.DaDuyet
        ]

        # =================================================
        # 8. CAC NGHIA DAI BAT THUONG
        # Chi audit, khong ket luan la sai.
        # =================================================
        long_meanings = [
            row
            for row in rows
            if len(
                clean(row.NghiaTiengViet)
            ) > 120
        ]

        # =================================================
        # 9. CAC NGHIA CO KY HIEU CAN XEM LAI
        # =================================================
        suspicious_tokens = [
            "http://",
            "https://",
            "<",
            ">",
            "{",
            "}",
        ]

        suspicious_meanings = []

        for row in rows:

            meaning = clean(
                row.NghiaTiengViet
            )

            if any(
                token in meaning
                for token in suspicious_tokens
            ):
                suspicious_meanings.append(
                    row
                )

        # =================================================
        # 10. THONG KE THEO BAI
        # =================================================
        lesson_counter = Counter(
            row.SoThuTuBai
            for row in rows
        )

        print()
        print("-" * 95)
        print("SO TU TUNG BAI")
        print("-" * 95)

        for lesson_no in range(1, 24):

            print(
                f"Bai {lesson_no:02d}: "
                f"{lesson_counter[lesson_no]} tu"
            )

        # =================================================
        # 11. TU THIEU TU LOAI
        # =================================================
        print()
        print("-" * 95)
        print("TU CHUA CO TuLoai")
        print("-" * 95)

        print(
            "So luong:",
            len(missing_word_type),
        )

        for row in missing_word_type[:50]:

            print(
                f"Bai {row.SoThuTuBai:02d}"
                f" | MaTuVung={row.MaTuVung}"
                f" | {row.ChuHan}"
                f" | {row.PhienAm}"
                f" | {row.NghiaTiengViet}"
            )

        if len(missing_word_type) > 50:

            print(
                "... con",
                len(missing_word_type) - 50,
                "tu khac."
            )

        # =================================================
        # 12. NGHIA DAI
        # =================================================
        print()
        print("-" * 95)
        print("NGHIA DAI > 120 KY TU - CAN XEM LAI")
        print("-" * 95)

        print(
            "So luong:",
            len(long_meanings),
        )

        for row in long_meanings[:30]:

            print()
            print(
                f"Bai {row.SoThuTuBai:02d}"
                f" | {row.ChuHan}"
                f" | {row.PhienAm}"
            )

            print(
                "  Nghia:",
                row.NghiaTiengViet,
            )

        # =================================================
        # 13. NGHIA CO KY HIEU LA
        # =================================================
        print()
        print("-" * 95)
        print("NGHIA CO KY HIEU CAN KIEM TRA")
        print("-" * 95)

        print(
            "So luong:",
            len(suspicious_meanings),
        )

        for row in suspicious_meanings[:30]:

            print(
                f"Bai {row.SoThuTuBai:02d}"
                f" | {row.ChuHan}"
                f" | {row.NghiaTiengViet}"
            )

        # =================================================
        # 14. TONG KET
        # =================================================
        print()
        print("=" * 95)
        print("TONG KET")
        print("=" * 95)

        print(
            "Tong tu:",
            len(rows),
        )

        print(
            "Thieu ChuHan:",
            len(missing_hanzi),
        )

        print(
            "Thieu Pinyin:",
            len(missing_pinyin),
        )

        print(
            "Thieu nghia Viet:",
            len(missing_meaning),
        )

        print(
            "Thieu MaNguon:",
            len(missing_source),
        )

        print(
            "Thieu TuLoai:",
            len(missing_word_type),
        )

        print(
            "Trung ChuHan+Pinyin:",
            len(duplicate_keys),
        )

        print(
            "DaDuyet=1:",
            len(approved),
        )

        print(
            "DaDuyet=0:",
            len(unapproved),
        )

        print(
            "Nghia dai >120:",
            len(long_meanings),
        )

        print(
            "Nghia co ky hieu la:",
            len(suspicious_meanings),
        )

        print()
        print(
            "SCRIPT NAY CHI AUDIT."
        )

        print(
            "KHONG INSERT / UPDATE DATABASE."
        )

        print()
        print("=" * 95)
        print("HOAN TAT")
        print("=" * 95)

    except Exception as e:

        print()
        print("=" * 95)
        print("THUC HIEN THAT BAI")
        print("=" * 95)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "KHONG SUA DATABASE."
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


if __name__ == "__main__":
    main()