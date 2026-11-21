from pathlib import Path
import csv
import json
import sys
from collections import Counter, defaultdict


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

EXPECTED_HANZI = 301

EXPECTED_TOTAL_NET = 2162

EXPECTED_EXISTING_NET = 106
EXPECTED_KEEP = 106
EXPECTED_INSERT = 2056

MAKE_ME_A_HANZI_SOURCE_ID = 3

MEDIAN_COLUMN = "DuongTrungTamJson"


# =========================================================
# PATHS
# =========================================================
REVIEW_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

INPUT_FILE = (
    REVIEW_DIR
    / "hsk1_301_netchuhan_preinsert_review.csv"
)

AFTER_FILE = (
    REVIEW_DIR
    / "hsk1_2162_netchuhan_after_10t.csv"
)


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def to_int(value, default=None):

    value = clean(value)

    if not value:
        return default

    return int(value)


def fail(message):

    raise RuntimeError(message)


def load_csv(path):

    if not path.exists():

        fail(
            "Khong tim thay file:\n"
            f"{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:

            fail(
                "Khong doc duoc header CSV."
            )

        return (
            reader.fieldnames,
            list(reader),
        )


def write_csv(
    path,
    fieldnames,
    rows,
):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def normalize_json_text(value):

    value = clean(value)

    if not value:
        return ""

    try:

        data = json.loads(
            value
        )

        return json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    except Exception:

        return value


# =========================================================
# READ DATABASE NetChuHan
# =========================================================
def get_current_netchuhan(
    cursor,
):

    cursor.execute(
        f"""
        SELECT
            n.MaNetChuHan,
            n.MaChuHan,
            n.ThuTuNet,
            n.DuongNetSVG,
            n.{MEDIAN_COLUMN},
            n.MaNguon,
            n.NgayTao,
            ch.KyTu,
            bh.SoThuTuBai

        FROM dbo.NetChuHan AS n

        INNER JOIN dbo.ChuHan AS ch
            ON n.MaChuHan
            = ch.MaChuHan

        INNER JOIN dbo.BaiHoc AS bh
            ON ch.MaBaiHoc
            = bh.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON bh.MaKhoaHoc
            = kh.MaKhoaHoc

        WHERE
            kh.MaKyHieu = ?

        ORDER BY
            bh.SoThuTuBai,
            ch.ThuTu,
            n.ThuTuNet;
        """,
        COURSE_CODE,
    )

    result = []

    for row in cursor.fetchall():

        result.append(
            {
                "MaNetChuHan": int(
                    row[0]
                ),

                "MaChuHan": int(
                    row[1]
                ),

                "ThuTuNet": int(
                    row[2]
                ),

                "DuongNetSVG": clean(
                    row[3]
                ),

                "DuongTrungTamJson": clean(
                    row[4]
                ),

                "MaNguon": int(
                    row[5]
                ),

                "NgayTao": clean(
                    row[6]
                ),

                "KyTu": clean(
                    row[7]
                ),

                "SoThuTuBai": int(
                    row[8]
                ),
            }
        )

    return result


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10T - INSERT NetChuHan HSK1 "
        "VAO DATABASE"
    )
    print("=" * 120)

    print()
    print(
        "DAY LA BUOC GHI DATABASE THAT."
    )

    print()
    print("MUC TIEU:")
    print("  GIU NGUYEN 106 NET CU DA KHOP")
    print("  INSERT 2056 NET CON THIEU")
    print("  TONG SAU CUNG = 2162 NET")
    print("  MA NGUON NET = 3 (MAKE ME A HANZI)")

    print()
    print("AN TOAN:")
    print("  KHONG DELETE")
    print("  KHONG UPDATE 106 NET CU")
    print("  TRANSACTION")
    print("  SAI -> ROLLBACK")
    print("  DUNG -> COMMIT")

    # =====================================================
    # 1. READ 10S REVIEW
    # =====================================================
    print()
    print(
        "[1] DOC FILE REVIEW 10S"
    )
    print("-" * 120)

    fields, rows = load_csv(
        INPUT_FILE
    )

    required = {
        "KyTu",
        "MaChuHan",
        "SoThuTuBai",
        "ThuTuChuHan",

        "SoNetChuHan",
        "SoNetGraphics",
        "KiemTraSoNet",

        "ThuTuNet",

        "DuongNetSVGNguon",
        "DuongTrungTamNguon",

        "MaNguonDeXuat",

        "MaNetChuHanHienTai",
        "MaNguonHienTai",

        "HanhDongDeXuat",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        fail(
            "File 10S thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    if (
        len(rows)
        != EXPECTED_TOTAL_NET
    ):

        fail(
            "File 10S khong co dung "
            f"{EXPECTED_TOTAL_NET} dong. "
            f"Thuc te: {len(rows)}"
        )

    # =====================================================
    # 2. VERIFY REVIEW FILE
    # =====================================================
    print()
    print(
        "[2] KIEM TRA KE HOACH NET"
    )
    print("-" * 120)

    key_map = {}

    chars = set()

    action_counter = Counter()

    stroke_count_by_char = defaultdict(
        int
    )

    expected_count_by_char = {}

    for row in rows:

        char = clean(
            row["KyTu"]
        )

        ma_chu_han = to_int(
            row["MaChuHan"]
        )

        stroke_order = to_int(
            row["ThuTuNet"]
        )

        svg = clean(
            row[
                "DuongNetSVGNguon"
            ]
        )

        median_json = clean(
            row[
                "DuongTrungTamNguon"
            ]
        )

        source_id = to_int(
            row[
                "MaNguonDeXuat"
            ]
        )

        action = clean(
            row[
                "HanhDongDeXuat"
            ]
        )

        if not char:

            fail(
                "Co dong thieu KyTu."
            )

        if ma_chu_han is None:

            fail(
                f"{char}: thieu MaChuHan."
            )

        if (
            stroke_order is None
            or stroke_order <= 0
        ):

            fail(
                f"{char}: ThuTuNet "
                "khong hop le."
            )

        if not svg:

            fail(
                f"{char} net {stroke_order}: "
                "thieu DuongNetSVG."
            )

        if not median_json:

            fail(
                f"{char} net {stroke_order}: "
                "thieu DuongTrungTam."
            )

        # Verify JSON median
        try:

            median_data = json.loads(
                median_json
            )

        except Exception as error:

            fail(
                f"{char} net {stroke_order}: "
                "median JSON khong hop le: "
                f"{error}"
            )

        if not isinstance(
            median_data,
            list,
        ):

            fail(
                f"{char} net {stroke_order}: "
                "median khong phai list."
            )

        if (
            source_id
            != MAKE_ME_A_HANZI_SOURCE_ID
        ):

            fail(
                f"{char} net {stroke_order}: "
                "MaNguonDeXuat khong phai 3."
            )

        if action not in {
            "KEEP",
            "INSERT",
        }:

            fail(
                f"{char} net {stroke_order}: "
                f"HanhDongDeXuat={action}"
            )

        if clean(
            row["KiemTraSoNet"]
        ) != "OK":

            fail(
                f"{char}: SoNet "
                "chua duoc audit OK."
            )

        key = (
            ma_chu_han,
            stroke_order,
        )

        if key in key_map:

            fail(
                "Trung key "
                "MaChuHan + ThuTuNet: "
                f"{key}"
            )

        key_map[
            key
        ] = row

        chars.add(
            char
        )

        action_counter[
            action
        ] += 1

        stroke_count_by_char[
            char
        ] += 1

        expected_count = to_int(
            row[
                "SoNetGraphics"
            ]
        )

        if (
            char
            in expected_count_by_char
            and
            expected_count_by_char[
                char
            ]
            != expected_count
        ):

            fail(
                f"{char}: SoNetGraphics "
                "khong nhat quan."
            )

        expected_count_by_char[
            char
        ] = expected_count

    if (
        len(chars)
        != EXPECTED_HANZI
    ):

        fail(
            "File 10S khong co dung "
            "301 KyTu."
        )

    for char in chars:

        if (
            stroke_count_by_char[
                char
            ]
            !=
            expected_count_by_char[
                char
            ]
        ):

            fail(
                f"{char}: so dong net "
                "khong bang SoNetGraphics."
            )

    keep_rows = [
        row
        for row in rows
        if clean(
            row[
                "HanhDongDeXuat"
            ]
        ) == "KEEP"
    ]

    insert_rows = [
        row
        for row in rows
        if clean(
            row[
                "HanhDongDeXuat"
            ]
        ) == "INSERT"
    ]

    print(
        "Tong net ke hoach:",
        len(rows),
    )

    print(
        "Tong Chu Han:",
        len(chars),
    )

    print(
        "KEEP:",
        len(keep_rows),
    )

    print(
        "INSERT:",
        len(insert_rows),
    )

    if (
        len(keep_rows)
        != EXPECTED_KEEP
    ):

        fail(
            "KEEP khong con bang 106."
        )

    if (
        len(insert_rows)
        != EXPECTED_INSERT
    ):

        fail(
            "INSERT khong con bang 2056."
        )

    print(
        "KE HOACH 10S: OK"
    )

    # =====================================================
    # 3. CONNECT DATABASE
    # =====================================================
    print()
    print(
        "[3] KET NOI DATABASE"
    )
    print("-" * 120)

    connection = get_connection()

    try:

        connection.autocommit = False

        cursor = (
            connection.cursor()
        )

        cursor.execute(
            """
            SELECT
                DB_NAME(),
                CONVERT(
                    nvarchar(128),
                    SERVERPROPERTY('ServerName')
                );
            """
        )

        db_name, server_name = (
            cursor.fetchone()
        )

        print(
            "Server:",
            clean(server_name),
        )

        print(
            "Database:",
            clean(db_name),
        )

        if (
            clean(db_name).lower()
            != "hoctiengtrungdb"
        ):

            fail(
                "Dang ket noi nham database."
            )

        # =================================================
        # 4. VERIFY SCHEMA
        # =================================================
        print()
        print(
            "[4] KIEM TRA SCHEMA LIVE"
        )
        print("-" * 120)

        cursor.execute(
            """
            SELECT
                COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE
                TABLE_SCHEMA = 'dbo'
                AND TABLE_NAME = 'NetChuHan'
            ORDER BY
                ORDINAL_POSITION;
            """
        )

        net_columns = [
            clean(row[0])
            for row in cursor.fetchall()
        ]

        expected_columns = [
            "MaNetChuHan",
            "MaChuHan",
            "ThuTuNet",
            "DuongNetSVG",
            "DuongTrungTamJson",
            "MaNguon",
            "NgayTao",
        ]

        if (
            net_columns
            != expected_columns
        ):

            fail(
                "Schema NetChuHan da thay doi.\n"
                f"Thuc te: {net_columns}"
            )

        print(
            "Schema NetChuHan: OK"
        )

        # =============================================
        # Verify source 3
        # =============================================
        cursor.execute(
            """
            SELECT
                Ten
            FROM dbo.NguonDuLieu
            WHERE
                MaNguon = ?;
            """,
            MAKE_ME_A_HANZI_SOURCE_ID,
        )

        source_row = (
            cursor.fetchone()
        )

        if source_row is None:

            fail(
                "Khong ton tai "
                "MaNguon=3."
            )

        print(
            "MaNguon=3:",
            clean(source_row[0]),
        )

        # =================================================
        # 5. VERIFY 301 ChuHan
        # =================================================
        print()
        print(
            "[5] KIEM TRA 301 ChuHan"
        )
        print("-" * 120)

        cursor.execute(
            """
            SELECT
                ch.MaChuHan,
                ch.KyTu,
                ch.SoNet

            FROM dbo.ChuHan AS ch

            INNER JOIN dbo.BaiHoc AS bh
                ON ch.MaBaiHoc
                = bh.MaBaiHoc

            INNER JOIN dbo.KhoaHoc AS kh
                ON bh.MaKhoaHoc
                = kh.MaKhoaHoc

            WHERE
                kh.MaKyHieu = ?;
            """,
            COURSE_CODE,
        )

        hanzi_rows = (
            cursor.fetchall()
        )

        if (
            len(hanzi_rows)
            != EXPECTED_HANZI
        ):

            fail(
                "SQL khong con dung "
                "301 ChuHan."
            )

        db_hanzi = {}

        for row in hanzi_rows:

            char = clean(
                row[1]
            )

            db_hanzi[
                char
            ] = {
                "MaChuHan": int(
                    row[0]
                ),

                "SoNet": int(
                    row[2]
                ),
            }

        for char in chars:

            if char not in db_hanzi:

                fail(
                    f"{char}: "
                    "khong ton tai trong dbo.ChuHan."
                )

        for row in rows:

            char = clean(
                row["KyTu"]
            )

            file_id = to_int(
                row[
                    "MaChuHan"
                ]
            )

            db_id = (
                db_hanzi[
                    char
                ][
                    "MaChuHan"
                ]
            )

            if file_id != db_id:

                fail(
                    f"{char}: MaChuHan "
                    "file khong khop SQL."
                )

            if (
                db_hanzi[
                    char
                ][
                    "SoNet"
                ]
                !=
                to_int(
                    row[
                        "SoNetGraphics"
                    ]
                )
            ):

                fail(
                    f"{char}: SoNet "
                    "SQL khong khop 10S."
                )

        print(
            "301 ChuHan: OK"
        )

        # =================================================
        # 6. CURRENT NetChuHan
        # =================================================
        print()
        print(
            "[6] PRE-FLIGHT NetChuHan"
        )
        print("-" * 120)

        before_rows = (
            get_current_netchuhan(
                cursor
            )
        )

        before_count = len(
            before_rows
        )

        print(
            "NetChuHan HSK1 hien tai:",
            before_count,
        )

        # Prevent accidental re-run
        if (
            before_count
            == EXPECTED_TOTAL_NET
        ):

            fail(
                "Database da co du "
                "2162 NetChuHan. "
                "Co ve 10T da chay thanh cong truoc do. "
                "KHONG CHAY LAI."
            )

        if (
            before_count
            != EXPECTED_EXISTING_NET
        ):

            fail(
                "NetChuHan truoc 10T "
                "khong con bang 106. "
                f"Thuc te: {before_count}"
            )

        before_map = {}

        for row in before_rows:

            key = (
                row[
                    "MaChuHan"
                ],
                row[
                    "ThuTuNet"
                ],
            )

            if key in before_map:

                fail(
                    "SQL dang trung "
                    "MaChuHan + ThuTuNet."
                )

            before_map[
                key
            ] = row

        # =================================================
        # 7. VERIFY KEEP + INSERT KEYS
        # =================================================
        print()
        print(
            "[7] DOI CHIEU 106 KEEP"
        )
        print("-" * 120)

        keep_verified = 0

        for row in keep_rows:

            key = (
                to_int(
                    row[
                        "MaChuHan"
                    ]
                ),
                to_int(
                    row[
                        "ThuTuNet"
                    ]
                ),
            )

            existing = (
                before_map.get(
                    key
                )
            )

            if existing is None:

                fail(
                    f"KEEP {key} "
                    "nhung SQL khong co."
                )

            source_svg = clean(
                row[
                    "DuongNetSVGNguon"
                ]
            )

            source_median = (
                normalize_json_text(
                    row[
                        "DuongTrungTamNguon"
                    ]
                )
            )

            if (
                existing[
                    "DuongNetSVG"
                ]
                != source_svg
            ):

                fail(
                    f"KEEP {key}: "
                    "DuongNetSVG khong khop."
                )

            if (
                normalize_json_text(
                    existing[
                        "DuongTrungTamJson"
                    ]
                )
                != source_median
            ):

                fail(
                    f"KEEP {key}: "
                    "DuongTrungTamJson "
                    "khong khop."
                )

            if (
                existing[
                    "MaNguon"
                ]
                !=
                MAKE_ME_A_HANZI_SOURCE_ID
            ):

                fail(
                    f"KEEP {key}: "
                    "MaNguon khong phai 3."
                )

            keep_verified += 1

        print(
            "KEEP khop SQL:",
            keep_verified,
            "/106",
        )

        if (
            keep_verified
            != EXPECTED_KEEP
        ):

            fail(
                "Khong verify du 106 KEEP."
            )

        # -----------------------------------------
        # INSERT keys must not already exist
        # -----------------------------------------
        insert_key_conflict = 0

        for row in insert_rows:

            key = (
                to_int(
                    row[
                        "MaChuHan"
                    ]
                ),
                to_int(
                    row[
                        "ThuTuNet"
                    ]
                ),
            )

            if key in before_map:

                insert_key_conflict += 1

        print(
            "INSERT key da ton tai:",
            insert_key_conflict,
        )

        if insert_key_conflict != 0:

            fail(
                "Co key INSERT da ton tai "
                "trong SQL."
            )

        print(
            "PRE-FLIGHT NetChuHan: OK"
        )

        # =================================================
        # 8. INSERT 2056
        # =================================================
        print()
        print(
            "[8] INSERT 2056 NetChuHan"
        )
        print("-" * 120)

        inserted = 0

        for index, row in enumerate(
            insert_rows,
            start=1,
        ):

            ma_chu_han = to_int(
                row[
                    "MaChuHan"
                ]
            )

            stroke_order = to_int(
                row[
                    "ThuTuNet"
                ]
            )

            svg = clean(
                row[
                    "DuongNetSVGNguon"
                ]
            )

            median_json = (
                normalize_json_text(
                    row[
                        "DuongTrungTamNguon"
                    ]
                )
            )

            cursor.execute(
                """
                INSERT INTO dbo.NetChuHan
                (
                    MaChuHan,
                    ThuTuNet,
                    DuongNetSVG,
                    DuongTrungTamJson,
                    MaNguon,
                    NgayTao
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    SYSUTCDATETIME()
                );
                """,
                ma_chu_han,
                stroke_order,
                svg,
                median_json,
                MAKE_ME_A_HANZI_SOURCE_ID,
            )

            inserted += 1

            if (
                index % 250 == 0
                or index
                == len(
                    insert_rows
                )
            ):

                print(
                    f"  Da INSERT: "
                    f"{index}/"
                    f"{len(insert_rows)}"
                )

        if (
            inserted
            != EXPECTED_INSERT
        ):

            fail(
                "Khong INSERT du "
                "2056 dong."
            )

        print(
            "INSERT hoan tat:",
            inserted,
        )

        # =================================================
        # 9. AUDIT INSIDE TRANSACTION
        # =================================================
        print()
        print(
            "[9] AUDIT TRUOC COMMIT"
        )
        print("-" * 120)

        after_rows = (
            get_current_netchuhan(
                cursor
            )
        )

        after_count = len(
            after_rows
        )

        print(
            "NetChuHan HSK1:",
            after_count,
        )

        if (
            after_count
            != EXPECTED_TOTAL_NET
        ):

            fail(
                "Sau INSERT khong co "
                "dung 2162 NetChuHan."
            )

        after_map = {}

        duplicate_keys = []

        for item in after_rows:

            key = (
                item[
                    "MaChuHan"
                ],
                item[
                    "ThuTuNet"
                ],
            )

            if key in after_map:

                duplicate_keys.append(
                    key
                )

            else:

                after_map[
                    key
                ] = item

        print(
            "Duplicate MaChuHan + ThuTuNet:",
            len(
                duplicate_keys
            ),
        )

        if duplicate_keys:

            fail(
                "Co duplicate net sau INSERT."
            )

        # -----------------------------------------
        # Exact compare all 2162 rows
        # -----------------------------------------
        mismatch = []

        for row in rows:

            key = (
                to_int(
                    row[
                        "MaChuHan"
                    ]
                ),
                to_int(
                    row[
                        "ThuTuNet"
                    ]
                ),
            )

            actual = (
                after_map.get(
                    key
                )
            )

            if actual is None:

                mismatch.append(
                    {
                        "key": key,
                        "diff": (
                            "THIEU_DONG"
                        ),
                    }
                )

                continue

            differences = []

            expected_svg = clean(
                row[
                    "DuongNetSVGNguon"
                ]
            )

            expected_median = (
                normalize_json_text(
                    row[
                        "DuongTrungTamNguon"
                    ]
                )
            )

            if (
                actual[
                    "DuongNetSVG"
                ]
                != expected_svg
            ):

                differences.append(
                    "DuongNetSVG"
                )

            if (
                normalize_json_text(
                    actual[
                        "DuongTrungTamJson"
                    ]
                )
                != expected_median
            ):

                differences.append(
                    "DuongTrungTamJson"
                )

            if (
                actual[
                    "MaNguon"
                ]
                !=
                MAKE_ME_A_HANZI_SOURCE_ID
            ):

                differences.append(
                    "MaNguon"
                )

            if differences:

                mismatch.append(
                    {
                        "key": key,
                        "diff": (
                            " | ".join(
                                differences
                            )
                        ),
                    }
                )

        print(
            "Mismatch voi 10S:",
            len(mismatch),
        )

        if mismatch:

            for item in (
                mismatch[:20]
            ):

                print(
                    "  ",
                    item,
                )

            fail(
                "NetChuHan SQL "
                "khong khop file 10S."
            )

        # -----------------------------------------
        # Verify source 3 count
        # -----------------------------------------
        source3_count = sum(
            1
            for row in after_rows
            if row[
                "MaNguon"
            ]
            ==
            MAKE_ME_A_HANZI_SOURCE_ID
        )

        print(
            "MaNguon=3:",
            source3_count,
            "/2162",
        )

        if (
            source3_count
            != EXPECTED_TOTAL_NET
        ):

            fail(
                "Khong phai 2162 net "
                "deu co MaNguon=3."
            )

        # -----------------------------------------
        # Verify stroke count per Hanzi
        # -----------------------------------------
        cursor.execute(
            """
            SELECT
                ch.MaChuHan,
                ch.KyTu,
                ch.SoNet,
                COUNT(
                    n.MaNetChuHan
                ) AS SoNetThucTe

            FROM dbo.ChuHan AS ch

            INNER JOIN dbo.BaiHoc AS bh
                ON ch.MaBaiHoc
                = bh.MaBaiHoc

            INNER JOIN dbo.KhoaHoc AS kh
                ON bh.MaKhoaHoc
                = kh.MaKhoaHoc

            LEFT JOIN dbo.NetChuHan AS n
                ON ch.MaChuHan
                = n.MaChuHan

            WHERE
                kh.MaKyHieu = ?

            GROUP BY
                ch.MaChuHan,
                ch.KyTu,
                ch.SoNet

            HAVING
                COUNT(
                    n.MaNetChuHan
                ) <> ch.SoNet;
            """,
            COURSE_CODE,
        )

        stroke_count_mismatch = (
            cursor.fetchall()
        )

        print(
            "Chu co so dong NetChuHan "
            "khong bang SoNet:",
            len(
                stroke_count_mismatch
            ),
        )

        if stroke_count_mismatch:

            for row in (
                stroke_count_mismatch[:20]
            ):

                print(
                    f"  {clean(row[1])} "
                    f"| SoNet="
                    f"{row[2]} "
                    f"| SQL="
                    f"{row[3]}"
                )

            fail(
                "Co ChuHan chua du net."
            )

        print()
        print(
            "AUDIT TRONG TRANSACTION: OK"
        )

        # =================================================
        # 10. COMMIT
        # =================================================
        print()
        print(
            "[10] COMMIT"
        )
        print("-" * 120)

        connection.commit()

        print(
            "COMMIT THANH CONG."
        )

        # =================================================
        # 11. VERIFY AFTER COMMIT
        # =================================================
        print()
        print(
            "[11] KIEM TRA SAU COMMIT"
        )
        print("-" * 120)

        committed_rows = (
            get_current_netchuhan(
                cursor
            )
        )

        committed_count = len(
            committed_rows
        )

        print(
            "NetChuHan sau COMMIT:",
            committed_count,
        )

        if (
            committed_count
            != EXPECTED_TOTAL_NET
        ):

            fail(
                "Sau COMMIT khong con "
                "dung 2162 dong."
            )

        # =================================================
        # 12. SAVE SNAPSHOT
        # =================================================
        print()
        print(
            "[12] LUU SNAPSHOT"
        )
        print("-" * 120)

        write_csv(
            AFTER_FILE,
            [
                "MaNetChuHan",
                "MaChuHan",
                "KyTu",
                "SoThuTuBai",
                "ThuTuNet",
                "DuongNetSVG",
                "DuongTrungTamJson",
                "MaNguon",
                "NgayTao",
            ],
            committed_rows,
        )

        print(
            AFTER_FILE
        )

        # =================================================
        # FINAL
        # =================================================
        print()
        print("=" * 120)
        print(
            "KET QUA 10T"
        )
        print("=" * 120)

        print(
            "ChuHan HSK1:",
            EXPECTED_HANZI,
        )

        print(
            "Tong net mong doi:",
            EXPECTED_TOTAL_NET,
        )

        print()
        print(
            "NetChuHan truoc:",
            before_count,
        )

        print(
            "KEEP net cu:",
            EXPECTED_KEEP,
        )

        print(
            "INSERT net moi:",
            inserted,
        )

        print(
            "NetChuHan sau:",
            committed_count,
        )

        print()
        print(
            "Mismatch:",
            0,
        )

        print(
            "Duplicate:",
            0,
        )

        print(
            "Chu thieu net:",
            0,
        )

        print(
            "Net MaNguon=3:",
            source3_count,
            "/2162",
        )

        print()
        print(
            "DATABASE DA DUOC COMMIT."
        )

        print(
            "NetChuHan HSK1 "
            "DA CO DU 2162 NET."
        )

        print()
        print(
            "KHONG XOA 106 NET CU."
        )

        print(
            "KHONG UPDATE 106 NET CU."
        )

        print()
        print("=" * 120)
        print("HOAN TAT")
        print("=" * 120)

    except Exception:

        try:

            connection.rollback()

            print()
            print("=" * 120)
            print(
                "ROLLBACK DATABASE"
            )
            print("=" * 120)

            print(
                "Tat ca INSERT cua 10T "
                "da duoc ROLLBACK."
            )

            print(
                "106 NetChuHan cu "
                "khong bi thay doi."
            )

        except Exception as rollback_error:

            print(
                "LOI KHI ROLLBACK:",
                rollback_error,
            )

        raise

    finally:

        try:

            connection.close()

        except Exception:
            pass


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 120)
        print(
            "10T THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "NEU PHIA TREN CO "
            "'ROLLBACK DATABASE' "
            "THI CAC INSERT CUA 10T "
            "DA BI HUY."
        )

        sys.exit(1)