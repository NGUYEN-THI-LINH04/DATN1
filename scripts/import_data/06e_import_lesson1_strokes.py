from pathlib import Path
import sys
import zipfile
import json


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

HANZI_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hanzi"
)


# =========================================================
# 17 CHU CUA HSK1 - BAI 1
# =========================================================
LESSON_CHARS = [
    "你",
    "好",
    "我",
    "是",
    "叫",
    "什",
    "么",
    "名",
    "字",
    "很",
    "高",
    "兴",
    "认",
    "识",
    "吗",
    "呢",
    "也",
]


# =========================================================
# TONG SO NET DA DOI CHIEU
#
# 7 + 6 + 7 + 9 + 5 + 4 + 3 + 6 + 6
# + 9 + 10 + 6 + 4 + 7 + 6 + 8 + 3
# = 106
# =========================================================
EXPECTED_TOTAL_STROKES = 106


# =========================================================
# TIM ZIP MAKE ME A HANZI
# =========================================================
def find_makemeahanzi_zip():

    if not HANZI_DIR.exists():

        raise FileNotFoundError(
            "Khong tim thay thu muc:\n"
            f"{HANZI_DIR}"
        )

    candidates = []

    for zip_path in HANZI_DIR.glob("*.zip"):

        try:

            with zipfile.ZipFile(
                zip_path,
                "r",
            ) as archive:

                graphics_files = [
                    name
                    for name in archive.namelist()
                    if name.endswith(
                        "graphics.txt"
                    )
                ]

                if graphics_files:

                    candidates.append(
                        (
                            zip_path,
                            graphics_files[0],
                        )
                    )

        except zipfile.BadZipFile:
            continue

    if len(candidates) == 0:

        raise RuntimeError(
            "Khong tim thay ZIP "
            "Make Me a Hanzi co graphics.txt."
        )

    if len(candidates) > 1:

        print(
            "Tim thay nhieu ZIP co graphics.txt:"
        )

        for path, _ in candidates:

            print(
                "-",
                path,
            )

        raise RuntimeError(
            "Co nhieu file nguon. "
            "Can chon dung Make Me a Hanzi."
        )

    return candidates[0]


# =========================================================
# DOC 17 CHU TU graphics.txt
# =========================================================
def load_graphics(
    zip_path,
    graphics_filename,
):

    target_chars = set(
        LESSON_CHARS
    )

    result = {}

    with zipfile.ZipFile(
        zip_path,
        "r",
    ) as archive:

        with archive.open(
            graphics_filename,
            "r",
        ) as raw_file:

            for line_number, raw_line in enumerate(
                raw_file,
                start=1,
            ):

                try:

                    line = (
                        raw_line
                        .decode("utf-8")
                        .strip()
                    )

                except UnicodeDecodeError:

                    continue

                if not line:
                    continue

                try:

                    item = json.loads(
                        line
                    )

                except json.JSONDecodeError:

                    raise RuntimeError(
                        "JSON loi tai dong "
                        f"{line_number}."
                    )

                character = (
                    item.get(
                        "character"
                    )
                )

                if (
                    character
                    not in target_chars
                ):
                    continue

                strokes = (
                    item.get(
                        "strokes"
                    )
                )

                medians = (
                    item.get(
                        "medians"
                    )
                )

                if not isinstance(
                    strokes,
                    list,
                ):

                    raise RuntimeError(
                        f"{character}: "
                        "strokes khong phai list."
                    )

                if not isinstance(
                    medians,
                    list,
                ):

                    raise RuntimeError(
                        f"{character}: "
                        "medians khong phai list."
                    )

                result[
                    character
                ] = {
                    "strokes": strokes,
                    "medians": medians,
                }

    return result


# =========================================================
# TIM NGUON MAKE ME A HANZI
# =========================================================
def get_source_id(cursor):

    cursor.execute(
        """
        SELECT
            MaNguon,
            Ten
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        "Make Me a Hanzi",
    )

    rows = cursor.fetchall()

    if len(rows) != 1:

        raise RuntimeError(
            "Khong tim thay duy nhat "
            "nguon 'Make Me a Hanzi' "
            "trong dbo.NguonDuLieu."
        )

    return rows[0].MaNguon


# =========================================================
# DOC CHU HAN BAI 1 TU SQL
# =========================================================
def load_lesson_chars(cursor):

    cursor.execute(
        """
        SELECT
            MaChuHan,
            KyTu,
            SoNet,
            ThuTu
        FROM dbo.ChuHan
        WHERE MaBaiHoc = ?
        ORDER BY ThuTu
        """,
        MA_BAI_HOC,
    )

    rows = cursor.fetchall()

    if len(rows) != 17:

        raise RuntimeError(
            "Bai 1 khong co dung 17 ChuHan. "
            f"Thuc te: {len(rows)}"
        )

    result = {}

    for row in rows:

        if row.KyTu in result:

            raise RuntimeError(
                f"Chu {row.KyTu} bi trung "
                "trong dbo.ChuHan."
            )

        result[
            row.KyTu
        ] = {
            "MaChuHan":
                row.MaChuHan,

            "SoNet":
                row.SoNet,

            "ThuTu":
                row.ThuTu,
        }

    expected = set(
        LESSON_CHARS
    )

    actual = set(
        result.keys()
    )

    if actual != expected:

        missing = expected - actual
        extra = actual - expected

        raise RuntimeError(
            "Danh sach ChuHan Bai 1 khong khop.\n"
            f"Thieu: {sorted(missing)}\n"
            f"Thua: {sorted(extra)}"
        )

    return result


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 80)
        print(
            "IMPORT NET VIET HSK1 - BAI 1"
        )
        print("=" * 80)

        # -------------------------------------------------
        # 1. TIM NGUON FILE
        # -------------------------------------------------
        (
            zip_path,
            graphics_filename,
        ) = find_makemeahanzi_zip()

        print()
        print(
            "ZIP:"
        )

        print(
            zip_path
        )

        print()
        print(
            "graphics.txt:"
        )

        print(
            graphics_filename
        )

        # -------------------------------------------------
        # 2. DOC GRAPHICS
        # -------------------------------------------------
        graphics = load_graphics(
            zip_path,
            graphics_filename,
        )

        if len(graphics) != 17:

            missing = (
                set(LESSON_CHARS)
                - set(graphics.keys())
            )

            raise RuntimeError(
                "Khong tim thay du 17 chu "
                "trong Make Me a Hanzi.\n"
                f"Thieu: {sorted(missing)}"
            )

        # -------------------------------------------------
        # 3. KET NOI DB
        # -------------------------------------------------
        conn = get_connection()
        conn.autocommit = False

        cursor = conn.cursor()

        # -------------------------------------------------
        # 4. KIEM TRA BANG NetChuHan
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT OBJECT_ID(
                N'dbo.NetChuHan',
                N'U'
            )
            """
        )

        if not cursor.fetchone()[0]:

            raise RuntimeError(
                "Chua co bang dbo.NetChuHan."
            )

        # -------------------------------------------------
        # 5. DOC ChuHan BAI 1
        # -------------------------------------------------
        lesson_chars = (
            load_lesson_chars(
                cursor
            )
        )

        # -------------------------------------------------
        # 6. NGUON MAKE ME A HANZI
        # -------------------------------------------------
        ma_nguon = (
            get_source_id(
                cursor
            )
        )

        print()
        print(
            "MaNguon Make Me a Hanzi:",
            ma_nguon,
        )

        # -------------------------------------------------
        # 7. CHAN IMPORT LAI
        #
        # Chi kiem tra cac ChuHan cua Bai 1,
        # khong dem net cua bai khac.
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.NetChuHan n
            INNER JOIN dbo.ChuHan ch
                ON ch.MaChuHan = n.MaChuHan
            WHERE ch.MaBaiHoc = ?
            """,
            MA_BAI_HOC,
        )

        existing_count = (
            cursor.fetchone()[0]
        )

        if existing_count != 0:

            raise RuntimeError(
                "Bai 1 da co "
                f"{existing_count} net trong NetChuHan. "
                "Khong import lai."
            )

        # -------------------------------------------------
        # 8. CHUAN BI DU LIEU
        # -------------------------------------------------
        prepared = []

        ordered_chars = sorted(
            lesson_chars.items(),
            key=lambda item:
                item[1]["ThuTu"],
        )

        print()
        print("-" * 80)
        print(
            "KIEM TRA TRUOC KHI INSERT"
        )
        print("-" * 80)

        for char, db_data in (
            ordered_chars
        ):

            source = graphics[
                char
            ]

            strokes = source[
                "strokes"
            ]

            medians = source[
                "medians"
            ]

            if (
                len(strokes)
                != db_data["SoNet"]
            ):

                raise RuntimeError(
                    f"{char}: SQL SoNet="
                    f"{db_data['SoNet']} "
                    f"nhung MakeMeAHanzi="
                    f"{len(strokes)}."
                )

            if (
                len(medians)
                != len(strokes)
            ):

                raise RuntimeError(
                    f"{char}: "
                    "strokes va medians "
                    "khong bang nhau."
                )

            print(
                f"{db_data['ThuTu']:02d}"
                f" | {char}"
                f" | MaChuHan="
                f"{db_data['MaChuHan']}"
                f" | SoNet="
                f"{len(strokes)}"
            )

            for index, (
                stroke_path,
                median,
            ) in enumerate(
                zip(
                    strokes,
                    medians,
                ),
                start=1,
            ):

                if not isinstance(
                    stroke_path,
                    str,
                ):

                    raise RuntimeError(
                        f"{char} net {index}: "
                        "SVG path khong phai chuoi."
                    )

                if not stroke_path.strip():

                    raise RuntimeError(
                        f"{char} net {index}: "
                        "SVG path rong."
                    )

                if not isinstance(
                    median,
                    list,
                ):

                    raise RuntimeError(
                        f"{char} net {index}: "
                        "median khong phai list."
                    )

                # JSON dung de insert vao SQL
                median_json = (
                    json.dumps(
                        median,
                        ensure_ascii=False,
                        separators=(
                            ",",
                            ":",
                        ),
                    )
                )

                prepared.append(
                    {
                        "MaChuHan":
                            db_data[
                                "MaChuHan"
                            ],

                        "KyTu":
                            char,

                        "ThuTuNet":
                            index,

                        "DuongNetSVG":
                            stroke_path,

                        "DuongTrungTamJson":
                            median_json,
                    }
                )

        # -------------------------------------------------
        # 9. KIEM TRA TONG = 106
        # -------------------------------------------------
        if (
            len(prepared)
            != EXPECTED_TOTAL_STROKES
        ):

            raise RuntimeError(
                "Tong so net khong dung.\n"
                f"Mong doi: "
                f"{EXPECTED_TOTAL_STROKES}\n"
                f"Thuc te: {len(prepared)}"
            )

        print()
        print(
            "Tong net se INSERT:",
            len(prepared),
        )

        # -------------------------------------------------
        # 10. INSERT
        # -------------------------------------------------
        print()
        print(
            "Dang INSERT NetChuHan..."
        )

        for index, row in enumerate(
            prepared,
            start=1,
        ):

            cursor.execute(
                """
                INSERT INTO dbo.NetChuHan
                (
                    MaChuHan,
                    ThuTuNet,
                    DuongNetSVG,
                    DuongTrungTamJson,
                    MaNguon
                )
                VALUES
                (
                    ?, ?, ?, ?, ?
                )
                """,
                row["MaChuHan"],
                row["ThuTuNet"],
                row["DuongNetSVG"],
                row[
                    "DuongTrungTamJson"
                ],
                ma_nguon,
            )

            if index % 25 == 0:

                print(
                    f"Da INSERT "
                    f"{index}/"
                    f"{len(prepared)} net..."
                )

        # -------------------------------------------------
        # 11. VERIFY TONG
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.NetChuHan n
            INNER JOIN dbo.ChuHan ch
                ON ch.MaChuHan = n.MaChuHan
            WHERE ch.MaBaiHoc = ?
            """,
            MA_BAI_HOC,
        )

        total_after = (
            cursor.fetchone()[0]
        )

        if (
            total_after
            != EXPECTED_TOTAL_STROKES
        ):

            raise RuntimeError(
                "Sau INSERT co "
                f"{total_after} net, "
                f"khong dung "
                f"{EXPECTED_TOTAL_STROKES}."
            )

        # -------------------------------------------------
        # 12. VERIFY TUNG CHU
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                ch.ThuTu,
                ch.KyTu,
                ch.SoNet,
                COUNT(n.MaNetChuHan)
                    AS SoNetDaNhap,
                MIN(n.ThuTuNet)
                    AS NetDau,
                MAX(n.ThuTuNet)
                    AS NetCuoi
            FROM dbo.ChuHan ch
            LEFT JOIN dbo.NetChuHan n
                ON n.MaChuHan =
                   ch.MaChuHan
            WHERE ch.MaBaiHoc = ?
            GROUP BY
                ch.ThuTu,
                ch.KyTu,
                ch.SoNet
            ORDER BY
                ch.ThuTu
            """,
            MA_BAI_HOC,
        )

        verify_rows = (
            cursor.fetchall()
        )

        if len(verify_rows) != 17:

            raise RuntimeError(
                "Verify khong co du 17 chu."
            )

        for row in verify_rows:

            if (
                row.SoNetDaNhap
                != row.SoNet
            ):

                raise RuntimeError(
                    f"{row.KyTu}: "
                    f"SoNet SQL={row.SoNet}, "
                    f"NetChuHan="
                    f"{row.SoNetDaNhap}."
                )

            if row.NetDau != 1:

                raise RuntimeError(
                    f"{row.KyTu}: "
                    "net dau khong phai 1."
                )

            if (
                row.NetCuoi
                != row.SoNet
            ):

                raise RuntimeError(
                    f"{row.KyTu}: "
                    "ThuTuNet cuoi "
                    "khong khop SoNet."
                )

        # -------------------------------------------------
        # 13. COMMIT
        # -------------------------------------------------
        conn.commit()

        # -------------------------------------------------
        # 14. KET QUA
        # -------------------------------------------------
        print()
        print("=" * 80)
        print("KET QUA")
        print("=" * 80)

        for row in verify_rows:

            print(
                f"{row.ThuTu:02d}"
                f" | {row.KyTu}"
                f" | SoNet SQL="
                f"{row.SoNet}"
                f" | DaNhap="
                f"{row.SoNetDaNhap}"
                f" | ThuTu="
                f"{row.NetDau}"
                f"->{row.NetCuoi}"
            )

        print()
        print(
            "Tong ChuHan Bai 1:",
            len(verify_rows),
        )

        print(
            "Tong NetChuHan Bai 1:",
            total_after,
        )

        print(
            "MaNguon:",
            ma_nguon,
            "(Make Me a Hanzi)",
        )

        print()
        print(
            "DA IMPORT NET VIET THANH CONG."
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
            "IMPORT THAT BAI - DA ROLLBACK"
        )
        print("=" * 80)

        print(
            "Loi:",
            e,
        )

        print()
        print(
            "Neu co loi, khong giu "
            "du lieu dang do."
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()