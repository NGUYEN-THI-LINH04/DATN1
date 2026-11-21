from pathlib import Path
import sys


# =========================================================
# THU MUC GOC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# CAU HINH
# =========================================================
MA_BAI_HOC = 1


# =========================================================
# 13 VI DU DA CHON TU TATOEBA
#
# Moi vi du:
# - word: tu vung cua Bai 1
# - sentence_id: ID goc Tatoeba
# - chinese: cau Trung goc
# - pinyin: pinyin phuc vu hoc tap
# - vietnamese: ban dich phuc vu hoc tap
#
# Pinyin va ban dich Viet la noi dung do do an bien soan,
# khong phai noi dung lay tu Tatoeba.
# =========================================================
EXAMPLES = [
    {
        "word": "你",
        "sentence_id": "4869782",
        "chinese": "你好！",
        "pinyin": "Nǐ hǎo!",
        "vietnamese": "Xin chào!",
    },
    {
        "word": "好",
        "sentence_id": "794004",
        "chinese": "我很好。",
        "pinyin": "Wǒ hěn hǎo.",
        "vietnamese": "Tôi rất khỏe.",
    },
    {
        "word": "我",
        "sentence_id": "6142020",
        "chinese": "我叫小雨。",
        "pinyin": "Wǒ jiào Xiǎoyǔ.",
        "vietnamese": "Tôi tên là Tiểu Vũ.",
    },
    {
        "word": "是",
        "sentence_id": "347291",
        "chinese": "这是书。",
        "pinyin": "Zhè shì shū.",
        "vietnamese": "Đây là sách.",
    },
    {
        "word": "叫",
        "sentence_id": "6142020",
        "chinese": "我叫小雨。",
        "pinyin": "Wǒ jiào Xiǎoyǔ.",
        "vietnamese": "Tôi tên là Tiểu Vũ.",
    },
    {
        "word": "什么",
        "sentence_id": "347292",
        "chinese": "这是什么？",
        "pinyin": "Zhè shì shénme?",
        "vietnamese": "Đây là gì?",
    },
    {
        "word": "名字",
        "sentence_id": "346883",
        "chinese": "你叫什么名字？",
        "pinyin": "Nǐ jiào shénme míngzi?",
        "vietnamese": "Bạn tên là gì?",
    },
    {
        "word": "很",
        "sentence_id": "794004",
        "chinese": "我很好。",
        "pinyin": "Wǒ hěn hǎo.",
        "vietnamese": "Tôi rất khỏe.",
    },
    {
        "word": "高兴",
        "sentence_id": "924590",
        "chinese": "我很高兴。",
        "pinyin": "Wǒ hěn gāoxìng.",
        "vietnamese": "Tôi rất vui.",
    },
    {
        "word": "认识",
        "sentence_id": "2782509",
        "chinese": "我认识你。",
        "pinyin": "Wǒ rènshi nǐ.",
        "vietnamese": "Tôi biết bạn.",
    },
    {
        "word": "吗",
        "sentence_id": "475781",
        "chinese": "你好吗？",
        "pinyin": "Nǐ hǎo ma?",
        "vietnamese": "Bạn khỏe không?",
    },
    {
        "word": "呢",
        "sentence_id": "691992",
        "chinese": "你呢？",
        "pinyin": "Nǐ ne?",
        "vietnamese": "Còn bạn thì sao?",
    },
    {
        "word": "也",
        "sentence_id": "793651",
        "chinese": "我也是。",
        "pinyin": "Wǒ yě shì.",
        "vietnamese": "Tôi cũng vậy.",
    },
]


# =========================================================
# TIM NGUON TATOEBA
# =========================================================
def get_tatoeba_source(cursor):

    cursor.execute(
        """
        SELECT
            MaNguon,
            Ten
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        "Tatoeba",
    )

    rows = cursor.fetchall()

    if len(rows) != 1:
        raise RuntimeError(
            "Khong tim thay duy nhat nguon "
            "'Tatoeba' trong NguonDuLieu."
        )

    return rows[0].MaNguon


# =========================================================
# DOC 13 TU VUNG CUA BAI 1
# =========================================================
def load_lesson_vocab(cursor):

    cursor.execute(
        """
        SELECT
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tvbh.ThuTu
        FROM dbo.TuVungBaiHoc tvbh
        INNER JOIN dbo.TuVung tv
            ON tv.MaTuVung = tvbh.MaTuVung
        WHERE tvbh.MaBaiHoc = ?
        ORDER BY tvbh.ThuTu
        """,
        MA_BAI_HOC,
    )

    rows = cursor.fetchall()

    if len(rows) != 13:
        raise RuntimeError(
            "Bai 1 khong co dung 13 tu vung. "
            f"Thuc te: {len(rows)}"
        )

    result = {}

    for row in rows:

        if row.ChuHan in result:
            raise RuntimeError(
                f"Tu '{row.ChuHan}' bi trung "
                "trong Bai 1."
            )

        result[row.ChuHan] = {
            "MaTuVung": row.MaTuVung,
            "PhienAm": row.PhienAm,
            "ThuTu": row.ThuTu,
        }

    expected_words = {
        item["word"]
        for item in EXAMPLES
    }

    actual_words = set(
        result.keys()
    )

    if expected_words != actual_words:

        missing = (
            expected_words
            - actual_words
        )

        extra = (
            actual_words
            - expected_words
        )

        raise RuntimeError(
            "Danh sach tu vung khong khop.\n"
            f"Thieu: {sorted(missing)}\n"
            f"Thua: {sorted(extra)}"
        )

    return result


# =========================================================
# KIEM TRA BANG
# =========================================================
def check_table(cursor):

    cursor.execute(
        """
        SELECT OBJECT_ID(
            N'dbo.ViDuTuVung',
            N'U'
        )
        """
    )

    value = cursor.fetchone()[0]

    if not value:
        raise RuntimeError(
            "Chua co bang dbo.ViDuTuVung."
        )


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 80)
        print(
            "INSERT VI DU TU VUNG "
            "HSK1 - BAI 1"
        )
        print("=" * 80)

        conn = get_connection()
        conn.autocommit = False

        cursor = conn.cursor()

        # -------------------------------------------------
        # 1. KIEM TRA BANG
        # -------------------------------------------------
        check_table(
            cursor
        )

        # -------------------------------------------------
        # 2. NGUON TATOEBA
        # -------------------------------------------------
        ma_nguon = (
            get_tatoeba_source(
                cursor
            )
        )

        print()
        print(
            "MaNguon Tatoeba:",
            ma_nguon,
        )

        # -------------------------------------------------
        # 3. DOC TU BAI 1
        # -------------------------------------------------
        vocab = (
            load_lesson_vocab(
                cursor
            )
        )

        # -------------------------------------------------
        # 4. CHAN NHAP LAP
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.ViDuTuVung vd
            INNER JOIN dbo.TuVungBaiHoc tvbh
                ON tvbh.MaTuVung =
                   vd.MaTuVung
            WHERE tvbh.MaBaiHoc = ?
            """,
            MA_BAI_HOC,
        )

        existing = (
            cursor.fetchone()[0]
        )

        if existing != 0:

            raise RuntimeError(
                "Bai 1 da co "
                f"{existing} dong ViDuTuVung. "
                "Khong insert lai."
            )

        # -------------------------------------------------
        # 5. HIEN DU LIEU TRUOC INSERT
        # -------------------------------------------------
        print()
        print("-" * 80)
        print(
            "DU LIEU SE INSERT"
        )
        print("-" * 80)

        ordered_examples = sorted(
            EXAMPLES,
            key=lambda item:
                vocab[
                    item["word"]
                ]["ThuTu"],
        )

        for item in ordered_examples:

            word = item[
                "word"
            ]

            info = vocab[
                word
            ]

            print(
                f"{info['ThuTu']:02d}"
                f" | {word}"
                f" | MaTuVung="
                f"{info['MaTuVung']}"
                f" | Tatoeba="
                f"{item['sentence_id']}"
            )

            print(
                "   Trung: "
                + item[
                    "chinese"
                ]
            )

            print(
                "   Pinyin: "
                + item[
                    "pinyin"
                ]
            )

            print(
                "   Viet: "
                + item[
                    "vietnamese"
                ]
            )

        # -------------------------------------------------
        # 6. INSERT
        # -------------------------------------------------
        for item in ordered_examples:

            word = item[
                "word"
            ]

            ma_tu_vung = (
                vocab[
                    word
                ]["MaTuVung"]
            )

            cursor.execute(
                """
                INSERT INTO dbo.ViDuTuVung
                (
                    MaTuVung,
                    CauTiengTrung,
                    Pinyin,
                    NghiaTiengViet,
                    MaNguon,
                    MaDinhDanhNguon,
                    LaViDuChinh,
                    ThuTu,
                    TrangThai
                )
                VALUES
                (
                    ?, ?, ?, ?, ?,
                    ?, 1, 1, 'ban_nhap'
                )
                """,
                ma_tu_vung,
                item["chinese"],
                item["pinyin"],
                item["vietnamese"],
                ma_nguon,
                item["sentence_id"],
            )

        # -------------------------------------------------
        # 7. VERIFY
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                tvbh.ThuTu,
                tv.ChuHan,
                tv.PhienAm,
                vd.CauTiengTrung,
                vd.Pinyin,
                vd.NghiaTiengViet,
                vd.MaDinhDanhNguon,
                nd.Ten AS TenNguon,
                vd.LaViDuChinh,
                vd.TrangThai
            FROM dbo.TuVungBaiHoc tvbh

            INNER JOIN dbo.TuVung tv
                ON tv.MaTuVung =
                   tvbh.MaTuVung

            INNER JOIN dbo.ViDuTuVung vd
                ON vd.MaTuVung =
                   tv.MaTuVung

            LEFT JOIN dbo.NguonDuLieu nd
                ON nd.MaNguon =
                   vd.MaNguon

            WHERE tvbh.MaBaiHoc = ?

            ORDER BY tvbh.ThuTu
            """,
            MA_BAI_HOC,
        )

        rows = (
            cursor.fetchall()
        )

        if len(rows) != 13:

            raise RuntimeError(
                "Sau INSERT khong co dung "
                f"13 vi du. Thuc te: "
                f"{len(rows)}"
            )

        # -------------------------------------------------
        # 8. KIEM TRA TUNG TU
        # -------------------------------------------------
        expected_words = {
            item["word"]
            for item in EXAMPLES
        }

        actual_words = {
            row.ChuHan
            for row in rows
        }

        if (
            actual_words
            != expected_words
        ):

            raise RuntimeError(
                "Danh sach tu sau INSERT "
                "khong khop."
            )

        for row in rows:

            if not row.CauTiengTrung:
                raise RuntimeError(
                    f"{row.ChuHan}: "
                    "thieu CauTiengTrung."
                )

            if not row.Pinyin:
                raise RuntimeError(
                    f"{row.ChuHan}: "
                    "thieu Pinyin."
                )

            if not row.NghiaTiengViet:
                raise RuntimeError(
                    f"{row.ChuHan}: "
                    "thieu NghiaTiengViet."
                )

            if not row.MaDinhDanhNguon:
                raise RuntimeError(
                    f"{row.ChuHan}: "
                    "thieu SentenceId."
                )

            if row.TenNguon != "Tatoeba":
                raise RuntimeError(
                    f"{row.ChuHan}: "
                    "nguon khong phai Tatoeba."
                )

            if row.LaViDuChinh != 1:
                raise RuntimeError(
                    f"{row.ChuHan}: "
                    "LaViDuChinh khong bang 1."
                )

            if row.TrangThai != "ban_nhap":
                raise RuntimeError(
                    f"{row.ChuHan}: "
                    "TrangThai khong dung."
                )

        # -------------------------------------------------
        # 9. COMMIT
        # -------------------------------------------------
        conn.commit()

        # -------------------------------------------------
        # 10. KET QUA
        # -------------------------------------------------
        print()
        print("=" * 80)
        print("KET QUA")
        print("=" * 80)

        for row in rows:

            print(
                f"{row.ThuTu:02d}"
                f" | {row.ChuHan}"
                f" | {row.CauTiengTrung}"
                f" | {row.Pinyin}"
                f" | {row.NghiaTiengViet}"
                f" | Tatoeba "
                f"{row.MaDinhDanhNguon}"
            )

        print()
        print(
            "Tong vi du Bai 1:",
            len(rows),
        )

        print(
            "Nguon:",
            ma_nguon,
            "(Tatoeba)",
        )

        print(
            "LaViDuChinh = 1:",
            sum(
                1
                for row in rows
                if row.LaViDuChinh == 1
            ),
        )

        print(
            "TrangThai = ban_nhap:",
            sum(
                1
                for row in rows
                if row.TrangThai
                == "ban_nhap"
            ),
        )

        print()
        print(
            "DA INSERT VI DU TU VUNG "
            "BAI 1 THANH CONG."
        )

        print()
        print("=" * 80)
        print("HOAN TAT")
        print("=" * 80)

        cursor.close()

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 80)
        print(
            "INSERT THAT BAI - DA ROLLBACK"
        )
        print("=" * 80)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "Khong giu du lieu dang do."
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()