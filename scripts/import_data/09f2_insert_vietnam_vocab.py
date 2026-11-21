from pathlib import Path
import sys
import re


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
COURSE_CODE = "HSK1-CORE"
LESSON_ORDER = 2

TARGET_WORD = "越南"

EXPECTED_DICTIONARY_ID = 30539
EXPECTED_SOURCE_ID = 2

VIETNAMESE_MEANING = "Việt Nam"


# =========================================================
# CHUYEN PINYIN SO -> PINYIN CO DAU
#
# Vi du:
# Yue4 nan2
# ->
# Yuè nán
# =========================================================
TONE_MARKS = {
    "a": ["a", "ā", "á", "ǎ", "à"],
    "e": ["e", "ē", "é", "ě", "è"],
    "i": ["i", "ī", "í", "ǐ", "ì"],
    "o": ["o", "ō", "ó", "ǒ", "ò"],
    "u": ["u", "ū", "ú", "ǔ", "ù"],
    "ü": ["ü", "ǖ", "ǘ", "ǚ", "ǜ"],
    "A": ["A", "Ā", "Á", "Ǎ", "À"],
    "E": ["E", "Ē", "É", "Ě", "È"],
    "I": ["I", "Ī", "Í", "Ǐ", "Ì"],
    "O": ["O", "Ō", "Ó", "Ǒ", "Ò"],
    "U": ["U", "Ū", "Ú", "Ǔ", "Ù"],
    "Ü": ["Ü", "Ǖ", "Ǘ", "Ǚ", "Ǜ"],
}


def mark_syllable(syllable):
    """
    Chuyen 1 am tiet:
    Yue4 -> Yuè
    nan2 -> nán
    """
    match = re.fullmatch(
        r"([A-Za-züÜvV:]+)([1-5])",
        syllable,
    )

    if not match:
        return syllable

    base = match.group(1)
    tone = int(match.group(2))

    # Thanh nhe / tone 5
    if tone == 5:
        return (
            base
            .replace("v", "ü")
            .replace("V", "Ü")
            .replace("u:", "ü")
            .replace("U:", "Ü")
        )

    base = (
        base
        .replace("u:", "ü")
        .replace("U:", "Ü")
        .replace("v", "ü")
        .replace("V", "Ü")
    )

    lower = base.lower()

    # Quy tac dat dau Pinyin:
    # a uu tien
    # e uu tien
    # ou -> o
    # neu khong thi danh dau nguyen am cuoi
    mark_index = None

    if "a" in lower:
        mark_index = lower.index("a")

    elif "e" in lower:
        mark_index = lower.index("e")

    elif "ou" in lower:
        mark_index = lower.index("o")

    else:
        vowel_indexes = [
            i
            for i, char in enumerate(lower)
            if char in "aeiouü"
        ]

        if vowel_indexes:
            mark_index = vowel_indexes[-1]

    if mark_index is None:
        return base

    original_vowel = base[mark_index]

    marked_vowel = TONE_MARKS[
        original_vowel
    ][tone]

    return (
        base[:mark_index]
        + marked_vowel
        + base[mark_index + 1:]
    )


def numeric_pinyin_to_tone_marks(text):
    """
    Yue4 nan2
    ->
    Yuè nán
    """
    parts = text.split()

    return " ".join(
        mark_syllable(part)
        for part in parts
    )


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None
    cursor = None

    try:

        print("=" * 90)
        print(
            "09F2 - THEM TU BO SUNG 越南 "
            "VAO BAI 2"
        )
        print("=" * 90)

        conn = get_connection()
        conn.autocommit = False

        cursor = conn.cursor()

        # =================================================
        # 1. TIM BAI 2
        # =================================================
        cursor.execute(
            """
            SELECT
                bh.MaBaiHoc,
                bh.SoThuTuBai,
                bh.TieuDe,
                bh.TrangThai
            FROM dbo.BaiHoc bh

            INNER JOIN dbo.KhoaHoc kh
                ON kh.MaKhoaHoc = bh.MaKhoaHoc

            WHERE kh.MaKyHieu = ?
              AND bh.SoThuTuBai = ?
            """,
            COURSE_CODE,
            LESSON_ORDER,
        )

        lessons = cursor.fetchall()

        if len(lessons) != 1:

            raise RuntimeError(
                "Khong tim thay duy nhat "
                "Bai 2 cua HSK1-CORE."
            )

        lesson = lessons[0]

        if "我是越南人" not in lesson.TieuDe:

            raise RuntimeError(
                "Bai 2 khong phai "
                "'我是越南人'."
            )

        print()
        print(
            "Bai 2:",
            lesson.TieuDe,
        )

        print(
            "MaBaiHoc:",
            lesson.MaBaiHoc,
        )

        # =================================================
        # 2. DAM BAO 越南 KHONG NAM TRONG 500 HSK1
        # =================================================
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = 1
              AND ChuHan = ?
            """,
            TARGET_WORD,
        )

        hsk_count = cursor.fetchone()[0]

        if hsk_count != 0:

            raise RuntimeError(
                "越南 dang ton tai trong "
                "TuVungHSKChuan HSK1. "
                "Khong coi la tu bo sung."
            )

        print()
        print(
            "越南 trong 500 HSK1:",
            hsk_count,
        )

        # =================================================
        # 3. DAM BAO CHUA CO TRONG TuVung
        # =================================================
        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm
            FROM dbo.TuVung
            WHERE ChuHan = ?
            """,
            TARGET_WORD,
        )

        existing_runtime = cursor.fetchall()

        if existing_runtime:

            raise RuntimeError(
                "越南 da ton tai trong dbo.TuVung. "
                "Khong insert lai."
            )

        # =================================================
        # 4. LAY DU LIEU GOC CC-CEDICT
        # =================================================
        cursor.execute(
            """
            SELECT
                m.MaMucTu,
                m.MaNguon,
                nd.Ten AS TenNguon,
                m.MaNguonBenNgoai,
                m.ChuHan,
                m.ChuPhonThe,
                m.PhienAm,
                m.NghiaGoc,
                m.NgonNguNghiaGoc,
                m.NghiaTiengViet,
                m.NghiaVietDaDuyet
            FROM dbo.MucTuDien m

            INNER JOIN dbo.NguonDuLieu nd
                ON nd.MaNguon = m.MaNguon

            WHERE m.ChuHan = ?
            ORDER BY m.MaMucTu
            """,
            TARGET_WORD,
        )

        dictionary_rows = cursor.fetchall()

        if len(dictionary_rows) != 1:

            raise RuntimeError(
                "Phai co dung 1 muc 越南 "
                "trong MucTuDien. "
                f"Thuc te: {len(dictionary_rows)}"
            )

        source = dictionary_rows[0]

        if source.MaMucTu != EXPECTED_DICTIONARY_ID:

            raise RuntimeError(
                "MaMucTu cua 越南 thay doi. "
                f"Du kien={EXPECTED_DICTIONARY_ID}, "
                f"thuc te={source.MaMucTu}"
            )

        if source.MaNguon != EXPECTED_SOURCE_ID:

            raise RuntimeError(
                "Nguon cua 越南 khong phai "
                "CC-CEDICT MaNguon=2."
            )

        if source.TenNguon != "CC-CEDICT":

            raise RuntimeError(
                "TenNguon khong phai CC-CEDICT."
            )

        if source.NghiaGoc != "Vietnam":

            raise RuntimeError(
                "NghiaGoc cua 越南 khong phai "
                "'Vietnam'."
            )

        # =================================================
        # 5. CHUYEN PINYIN
        # =================================================
        pinyin_with_space = (
            numeric_pinyin_to_tone_marks(
                source.PhienAm
            )
        )

        # Ten rieng dia danh hai am tiet:
        # Yuè nán -> Yuènán
        pinyin_runtime = (
            pinyin_with_space.replace(
                " ",
                "",
            )
        )

        print()
        print("-" * 90)
        print("DU LIEU NGUON")
        print("-" * 90)

        print(
            "MaMucTu    :",
            source.MaMucTu,
        )

        print(
            "Nguon      :",
            source.TenNguon,
        )

        print(
            "ChuHan     :",
            source.ChuHan,
        )

        print(
            "ChuPhonThe :",
            source.ChuPhonThe,
        )

        print(
            "Pinyin goc :",
            source.PhienAm,
        )

        print(
            "Pinyin moi :",
            pinyin_runtime,
        )

        print(
            "NghiaGoc   :",
            source.NghiaGoc,
        )

        print(
            "NghiaViet  :",
            VIETNAMESE_MEANING,
        )

        # =================================================
        # 6. SO TU BAI 2 TRUOC INSERT
        # =================================================
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc
            WHERE MaBaiHoc = ?
            """,
            lesson.MaBaiHoc,
        )

        lesson2_before = cursor.fetchone()[0]

        if lesson2_before != 28:

            raise RuntimeError(
                "Bai 2 truoc 09f2 phai co "
                "28 tu HSK1. "
                f"Thuc te: {lesson2_before}"
            )

        # =================================================
        # 7. THU TU CUOI CUA BAI 2
        # =================================================
        cursor.execute(
            """
            SELECT
                ISNULL(MAX(ThuTu), 0)
            FROM dbo.TuVungBaiHoc
            WHERE MaBaiHoc = ?
            """,
            lesson.MaBaiHoc,
        )

        max_order = cursor.fetchone()[0]

        if max_order != 28:

            raise RuntimeError(
                "ThuTu lon nhat Bai 2 "
                "phai la 28. "
                f"Thuc te: {max_order}"
            )

        new_order = 29

        # =================================================
        # 8. INSERT TuVung
        #
        # Nguon tu: CC-CEDICT
        # Nghia Viet: bo sung cho noi dung hoc
        # DaDuyet = 0 vi chua kiem duyet
        # =================================================
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
                ?,
                ?,
                ?,
                NULL,
                NULL,
                NULL,
                NULL,
                ?,
                0
            )
            """,
            TARGET_WORD,
            source.ChuPhonThe,
            pinyin_runtime,
            VIETNAMESE_MEANING,
            source.MaNguon,
        )

        # =================================================
        # 9. LAY MaTuVung VUA TAO
        # =================================================
        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm,
                NghiaTiengViet,
                MaNguon,
                DaDuyet
            FROM dbo.TuVung
            WHERE ChuHan = ?
              AND PhienAm = ?
            """,
            TARGET_WORD,
            pinyin_runtime,
        )

        inserted_rows = cursor.fetchall()

        if len(inserted_rows) != 1:

            raise RuntimeError(
                "Khong xac dinh duoc duy nhat "
                "TuVung 越南 vua insert."
            )

        inserted_vocab = inserted_rows[0]

        # =================================================
        # 10. GAN VAO BAI 2
        # =================================================
        cursor.execute(
            """
            INSERT INTO dbo.TuVungBaiHoc
            (
                MaBaiHoc,
                MaTuVung,
                ThuTu
            )
            VALUES
            (
                ?, ?, ?
            )
            """,
            lesson.MaBaiHoc,
            inserted_vocab.MaTuVung,
            new_order,
        )

        # =================================================
        # 11. VERIFY BAI 2 = 29 TU
        # =================================================
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc
            WHERE MaBaiHoc = ?
            """,
            lesson.MaBaiHoc,
        )

        lesson2_after = cursor.fetchone()[0]

        if lesson2_after != 29:

            raise RuntimeError(
                "Sau insert Bai 2 "
                "khong co dung 29 tu. "
                f"Thuc te: {lesson2_after}"
            )

        # =================================================
        # 12. VERIFY 越南 CHI GAN 1 LAN
        # =================================================
        cursor.execute(
            """
            SELECT
                tvbh.MaBaiHoc,
                tvbh.MaTuVung,
                tvbh.ThuTu,
                tv.ChuHan,
                tv.PhienAm,
                tv.NghiaTiengViet,
                tv.MaNguon,
                tv.DaDuyet
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.TuVung tv
                ON tv.MaTuVung =
                   tvbh.MaTuVung

            WHERE tv.ChuHan = ?
            """,
            TARGET_WORD,
        )

        links = cursor.fetchall()

        if len(links) != 1:

            raise RuntimeError(
                "越南 phai co dung "
                "1 lien ket bai hoc."
            )

        link = links[0]

        if link.MaBaiHoc != lesson.MaBaiHoc:

            raise RuntimeError(
                "越南 khong duoc gan "
                "vao dung Bai 2."
            )

        if link.ThuTu != 29:

            raise RuntimeError(
                "ThuTu cua 越南 "
                "khong bang 29."
            )

        # =================================================
        # 13. KIEM TRA 500 TU HSK CHUAN VAN GIU NGUYEN
        # =================================================
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = 1
            """
        )

        hsk_standard_count = (
            cursor.fetchone()[0]
        )

        if hsk_standard_count != 500:

            raise RuntimeError(
                "So tu HSK1 chuan "
                "bi thay doi."
            )

        # =================================================
        # 14. DEM TONG TuVung RUNTIME
        # =================================================
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVung
            """
        )

        runtime_total = cursor.fetchone()[0]

        if runtime_total != 501:

            raise RuntimeError(
                "Sau khi them 越南, "
                "TuVung runtime phai co "
                "501 dong. "
                f"Thuc te: {runtime_total}"
            )

        # =================================================
        # 15. DEM TONG LIEN KET HSK1 COURSE
        # =================================================
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc =
                   tvbh.MaBaiHoc

            INNER JOIN dbo.KhoaHoc kh
                ON kh.MaKhoaHoc =
                   bh.MaKhoaHoc

            WHERE kh.MaKyHieu = ?
            """,
            COURSE_CODE,
        )

        course_links = cursor.fetchone()[0]

        if course_links != 501:

            raise RuntimeError(
                "Tong lien ket tu vung "
                "cua HSK1 course "
                "phai la 501."
            )

        # =================================================
        # 16. COMMIT
        # =================================================
        conn.commit()

        # =================================================
        # 17. KET QUA
        # =================================================
        print()
        print("=" * 90)
        print("KET QUA")
        print("=" * 90)

        print(
            "MaTuVung moi :",
            inserted_vocab.MaTuVung,
        )

        print(
            "ChuHan       :",
            inserted_vocab.ChuHan,
        )

        print(
            "PhienAm      :",
            inserted_vocab.PhienAm,
        )

        print(
            "NghiaViet    :",
            inserted_vocab.NghiaTiengViet,
        )

        print(
            "MaNguon      :",
            inserted_vocab.MaNguon,
            "(CC-CEDICT)",
        )

        print(
            "DaDuyet      :",
            inserted_vocab.DaDuyet,
        )

        print()
        print(
            "Bai 2 truoc  :",
            lesson2_before,
        )

        print(
            "Bai 2 sau    :",
            lesson2_after,
        )

        print(
            "ThuTu 越南   :",
            link.ThuTu,
        )

        print()
        print(
            "Tu HSK1 chuan:",
            hsk_standard_count,
        )

        print(
            "TuVung runtime:",
            runtime_total,
        )

        print(
            "Lien ket HSK1 course:",
            course_links,
        )

        print()
        print(
            "DA THEM TU BO SUNG 越南 "
            "VAO BAI 2 THANH CONG."
        )

        print()
        print(
            "越南 KHONG DUOC TINH "
            "TRONG 500 TU HSK1 CHUAN."
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
            "KHONG GIU TuVung 越南 "
            "NEU CO BAT KY LOI NAO."
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


if __name__ == "__main__":
    main()