from pathlib import Path
import sys
import zipfile
import re


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

UNIHAN_ZIP = (
    ROOT_DIR
    / "data_sources"
    / "unicode"
    / "Unihan.zip"
)


# =========================================================
# 17 CHU HAN CUA HSK1 - BAI 1
#
# Pinyin + nghia o day la NOI DUNG HOC TAP
# trong ngu canh Bai 1.
#
# Bo thu va SoNet KHONG hard-code.
# Hai truong do se lay tu Unihan.
# =========================================================
LESSON_CHARS = [
    {
        "char": "你",
        "pinyin": "nǐ",
        "meaning": "bạn; cậu",
        "example_cn": "你好！",
        "example_py": "Nǐ hǎo!",
        "example_vi": "Xin chào!",
    },
    {
        "char": "好",
        "pinyin": "hǎo",
        "meaning": "tốt; khỏe",
        "example_cn": "你好！",
        "example_py": "Nǐ hǎo!",
        "example_vi": "Xin chào!",
    },
    {
        "char": "我",
        "pinyin": "wǒ",
        "meaning": "tôi; mình",
        "example_cn": "我是安娜。",
        "example_py": "Wǒ shì Ānnà.",
        "example_vi": "Tôi là Anna.",
    },
    {
        "char": "是",
        "pinyin": "shì",
        "meaning": "là",
        "example_cn": "我是安娜。",
        "example_py": "Wǒ shì Ānnà.",
        "example_vi": "Tôi là Anna.",
    },
    {
        "char": "叫",
        "pinyin": "jiào",
        "meaning": "gọi; tên là",
        "example_cn": "我叫安娜。",
        "example_py": "Wǒ jiào Ānnà.",
        "example_vi": "Tôi tên là Anna.",
    },
    {
        "char": "什",
        "pinyin": "shén",
        "meaning": "trong 什么: gì; cái gì",
        "example_cn": "什么",
        "example_py": "shénme",
        "example_vi": "gì; cái gì",
    },
    {
        "char": "么",
        "pinyin": "me",
        "meaning": "thành tố trong 什么: gì; cái gì",
        "example_cn": "什么",
        "example_py": "shénme",
        "example_vi": "gì; cái gì",
    },
    {
        "char": "名",
        "pinyin": "míng",
        "meaning": "tên",
        "example_cn": "名字",
        "example_py": "míngzi",
        "example_vi": "tên; tên gọi",
    },
    {
        "char": "字",
        "pinyin": "zì",
        "meaning": "chữ; trong 名字: tên",
        "example_cn": "名字",
        "example_py": "míngzi",
        "example_vi": "tên; tên gọi",
    },
    {
        "char": "很",
        "pinyin": "hěn",
        "meaning": "rất",
        "example_cn": "很好",
        "example_py": "hěn hǎo",
        "example_vi": "rất tốt; rất khỏe",
    },
    {
        "char": "高",
        "pinyin": "gāo",
        "meaning": "cao; trong 高兴: vui",
        "example_cn": "高兴",
        "example_py": "gāoxìng",
        "example_vi": "vui; vui mừng",
    },
    {
        "char": "兴",
        "pinyin": "xìng",
        "meaning": "hứng; trong 高兴: vui",
        "example_cn": "高兴",
        "example_py": "gāoxìng",
        "example_vi": "vui; vui mừng",
    },
    {
        "char": "认",
        "pinyin": "rèn",
        "meaning": "nhận; nhận biết",
        "example_cn": "认识",
        "example_py": "rènshi",
        "example_vi": "biết; quen; làm quen",
    },
    {
        "char": "识",
        "pinyin": "shi",
        "meaning": "biết; nhận biết",
        "example_cn": "认识",
        "example_py": "rènshi",
        "example_vi": "biết; quen; làm quen",
    },
    {
        "char": "吗",
        "pinyin": "ma",
        "meaning": "trợ từ nghi vấn cuối câu",
        "example_cn": "你好吗？",
        "example_py": "Nǐ hǎo ma?",
        "example_vi": "Bạn khỏe không?",
    },
    {
        "char": "呢",
        "pinyin": "ne",
        "meaning": "trợ từ dùng để hỏi lại hoặc tiếp nối",
        "example_cn": "你呢？",
        "example_py": "Nǐ ne?",
        "example_vi": "Còn bạn thì sao?",
    },
    {
        "char": "也",
        "pinyin": "yě",
        "meaning": "cũng",
        "example_cn": "我也很高兴。",
        "example_py": "Wǒ yě hěn gāoxìng.",
        "example_vi": "Tôi cũng rất vui.",
    },
]


TARGET_PROPERTIES = {
    "kRSUnicode",
    "kTotalStrokes",
}


# =========================================================
# UNIHAN
# =========================================================
def codepoint_to_char(value):

    value = value.strip()

    if not value.startswith("U+"):
        return None

    try:
        return chr(
            int(value[2:], 16)
        )
    except ValueError:
        return None


def parse_radical_number(value):

    if not value:
        return None

    first_value = (
        value.strip()
        .split()[0]
    )

    match = re.match(
        r"^(\d+)'{0,3}\.",
        first_value,
    )

    if not match:
        return None

    return int(
        match.group(1)
    )


def load_unihan():

    if not UNIHAN_ZIP.exists():

        raise FileNotFoundError(
            "Khong tim thay:\n"
            f"{UNIHAN_ZIP}"
        )

    target_chars = {
        item["char"]
        for item in LESSON_CHARS
    }

    result = {
        char: {}
        for char in target_chars
    }

    with zipfile.ZipFile(
        UNIHAN_ZIP,
        "r",
    ) as archive:

        filenames = [
            name
            for name in archive.namelist()
            if (
                name.startswith("Unihan")
                and name.endswith(".txt")
            )
        ]

        for filename in filenames:

            with archive.open(
                filename,
                "r",
            ) as file:

                for raw_line in file:

                    try:
                        line = raw_line.decode(
                            "utf-8"
                        ).strip()

                    except UnicodeDecodeError:
                        continue

                    if (
                        not line
                        or line.startswith("#")
                    ):
                        continue

                    parts = line.split("\t")

                    if len(parts) < 3:
                        continue

                    codepoint = parts[0]
                    property_name = parts[1]
                    property_value = parts[2]

                    if (
                        property_name
                        not in TARGET_PROPERTIES
                    ):
                        continue

                    char = codepoint_to_char(
                        codepoint
                    )

                    if char not in target_chars:
                        continue

                    result[
                        char
                    ][
                        property_name
                    ] = property_value

    return result


# =========================================================
# TIM NGUON UNICODE
# =========================================================
def get_unicode_source(cursor):

    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        "Unicode Character Database",
    )

    rows = cursor.fetchall()

    if len(rows) != 1:

        raise RuntimeError(
            "Khong tim thay duy nhat "
            "nguon Unicode Character Database."
        )

    return rows[0].MaNguon


# =========================================================
# TIM MaBoThu BANG SoBoThu
# =========================================================
def get_radical(cursor, radical_number):

    cursor.execute(
        """
        SELECT
            MaBoThu,
            SoBoThu,
            KyHieu,
            TenBoThu
        FROM dbo.BoThu
        WHERE SoBoThu = ?
        """,
        radical_number,
    )

    rows = cursor.fetchall()

    if len(rows) != 1:

        raise RuntimeError(
            "Khong tim thay duy nhat bo thu "
            f"SoBoThu={radical_number}."
        )

    return rows[0]


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 78)
        print(
            "INSERT CHU HAN CHO HSK1 - BAI 1"
        )
        print("=" * 78)

        # -------------------------------------------------
        # 1. Doc Unihan
        # -------------------------------------------------
        unihan = load_unihan()

        conn = get_connection()
        conn.autocommit = False

        cursor = conn.cursor()

        # -------------------------------------------------
        # 2. Kiem tra bai hoc
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaBaiHoc,
                MaKhoaHoc,
                SoThuTuBai
            FROM dbo.BaiHoc
            WHERE MaBaiHoc = ?
              AND MaKhoaHoc = 1
              AND SoThuTuBai = 1
            """,
            MA_BAI_HOC,
        )

        if not cursor.fetchone():

            raise RuntimeError(
                "Khong tim thay dung "
                "HSK1 - Bai 1."
            )

        # -------------------------------------------------
        # 3. Chan import trung
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.ChuHan
            WHERE MaBaiHoc = ?
            """,
            MA_BAI_HOC,
        )

        existing_count = (
            cursor.fetchone()[0]
        )

        if existing_count != 0:

            raise RuntimeError(
                "Bai 1 da co "
                f"{existing_count} ChuHan. "
                "Khong import lai."
            )

        # -------------------------------------------------
        # 4. Nguon Unicode
        #
        # MaNguon o day bieu thi nguon cau truc:
        # radical + so net.
        #
        # Pinyin/nghia/vi du la hoc lieu
        # bien soan theo ngu canh Bai 1.
        # -------------------------------------------------
        ma_nguon_unicode = (
            get_unicode_source(
                cursor
            )
        )

        print(
            "MaNguon Unicode:",
            ma_nguon_unicode,
        )

        prepared = []

        # -------------------------------------------------
        # 5. Chuan bi 17 dong
        # -------------------------------------------------
        for order, item in enumerate(
            LESSON_CHARS,
            start=1,
        ):

            char = item["char"]

            data = unihan.get(
                char,
                {}
            )

            rs_value = data.get(
                "kRSUnicode"
            )

            total_strokes_text = (
                data.get(
                    "kTotalStrokes"
                )
            )

            if not rs_value:

                raise RuntimeError(
                    f"{char}: thieu kRSUnicode."
                )

            if not total_strokes_text:

                raise RuntimeError(
                    f"{char}: thieu kTotalStrokes."
                )

            radical_number = (
                parse_radical_number(
                    rs_value
                )
            )

            if radical_number is None:

                raise RuntimeError(
                    f"{char}: khong parse duoc "
                    f"kRSUnicode={rs_value}."
                )

            try:

                total_strokes = int(
                    total_strokes_text
                )

            except ValueError:

                raise RuntimeError(
                    f"{char}: kTotalStrokes "
                    f"khong hop le: "
                    f"{total_strokes_text}"
                )

            radical = get_radical(
                cursor,
                radical_number,
            )

            prepared.append(
                {
                    "order": order,
                    "char": char,
                    "pinyin":
                        item["pinyin"],
                    "meaning":
                        item["meaning"],
                    "example_cn":
                        item["example_cn"],
                    "example_py":
                        item["example_py"],
                    "example_vi":
                        item["example_vi"],
                    "ma_bo_thu":
                        radical.MaBoThu,
                    "so_bo_thu":
                        radical.SoBoThu,
                    "ky_hieu_bo":
                        radical.KyHieu,
                    "ten_bo":
                        radical.TenBoThu,
                    "so_net":
                        total_strokes,
                }
            )

        if len(prepared) != 17:

            raise RuntimeError(
                "Khong chuan bi du 17 chu."
            )

        # -------------------------------------------------
        # 6. In preview
        # -------------------------------------------------
        print()
        print("-" * 78)
        print(
            "DU LIEU SE INSERT"
        )
        print("-" * 78)

        for row in prepared:

            print(
                f"{row['order']:02d}"
                f" | {row['char']}"
                f" | {row['pinyin']:<6}"
                f" | Bo {row['so_bo_thu']:>3}"
                f" {row['ky_hieu_bo']}"
                f" ({row['ten_bo']})"
                f" | SoNet={row['so_net']}"
                f" | {row['meaning']}"
            )

        # -------------------------------------------------
        # 7. INSERT
        #
        # CachGhiNho = NULL
        # MaTep = NULL
        #
        # Hai noi dung nay se lam sau voi
        # Make Me a Hanzi / media.
        # -------------------------------------------------
        for row in prepared:

            cursor.execute(
                """
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
                    TrangThai
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?,
                    NULL,
                    ?, ?, ?,
                    NULL,
                    ?,
                    ?,
                    'ban_nhap'
                )
                """,
                MA_BAI_HOC,
                row["ma_bo_thu"],
                row["char"],
                row["pinyin"],
                row["meaning"],
                row["so_net"],
                row["example_cn"],
                row["example_py"],
                row["example_vi"],
                ma_nguon_unicode,
                row["order"],
            )

        # -------------------------------------------------
        # 8. Verify
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.ChuHan
            WHERE MaBaiHoc = ?
            """,
            MA_BAI_HOC,
        )

        count_after = (
            cursor.fetchone()[0]
        )

        if count_after != 17:

            raise RuntimeError(
                "Sau INSERT ChuHan "
                f"co {count_after} dong, "
                "khong dung 17."
            )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.ChuHan ch
            INNER JOIN dbo.BoThu bt
                ON ch.MaBoThu = bt.MaBoThu
            WHERE ch.MaBaiHoc = ?
              AND
              (
                  ch.SoNet IS NULL
                  OR bt.SoBoThu IS NULL
                  OR ch.ThuTu <= 0
              )
            """,
            MA_BAI_HOC,
        )

        invalid_count = (
            cursor.fetchone()[0]
        )

        if invalid_count != 0:

            raise RuntimeError(
                "Co ChuHan thieu "
                "bo thu/so net/thu tu."
            )

        conn.commit()

        # -------------------------------------------------
        # 9. In ket qua
        # -------------------------------------------------
        print()
        print("=" * 78)
        print("KET QUA")
        print("=" * 78)

        cursor.execute(
            """
            SELECT
                ch.ThuTu,
                ch.KyTu,
                ch.Pinyin,
                ch.NghiaTiengViet,
                ch.SoNet,
                bt.SoBoThu,
                bt.KyHieu,
                bt.TenBoThu,
                ch.TrangThai
            FROM dbo.ChuHan ch
            LEFT JOIN dbo.BoThu bt
                ON ch.MaBoThu = bt.MaBoThu
            WHERE ch.MaBaiHoc = ?
            ORDER BY ch.ThuTu
            """,
            MA_BAI_HOC,
        )

        result_rows = (
            cursor.fetchall()
        )

        for row in result_rows:

            print(
                f"{row.ThuTu:02d}"
                f" | {row.KyTu}"
                f" | {row.Pinyin or ''}"
                f" | SoNet={row.SoNet}"
                f" | Bo {row.SoBoThu}"
                f" {row.KyHieu}"
                f" ({row.TenBoThu})"
                f" | {row.TrangThai}"
            )

        print()

        print(
            "Tong ChuHan Bai 1:",
            len(result_rows),
        )

        print(
            "CachGhiNho = NULL."
        )

        print(
            "MaTep = NULL."
        )

        print(
            "TrangThai = ban_nhap."
        )

        print()
        print("=" * 78)
        print("HOAN TAT")
        print("=" * 78)

        cursor.close()

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 78)
        print(
            "INSERT THAT BAI - DA ROLLBACK"
        )
        print("=" * 78)

        print(
            "Loi:",
            e,
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()