from pathlib import Path
import csv
import sys
import unicodedata
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

EXPECTED_BEFORE = 17
EXPECTED_AFTER = 301

EXPECTED_UPDATE_CONTENT = 10
EXPECTED_KEEP_CONTENT = 7
EXPECTED_INSERT = 284

STATUS_DRAFT = "ban_nhap"


# =========================================================
# NGUON TONG HOP CHO dbo.ChuHan
# =========================================================
SOURCE_NAME = (
    "Dữ liệu Chữ Hán HSK1 - tổng hợp đồ án"
)

SOURCE_LICENSE = (
    "Theo giấy phép của từng nguồn thành phần"
)

SOURCE_NOTE = (
    "Bản dữ liệu tổng hợp dùng cho bảng ChuHan HSK1 của đồ án. "
    "Phạm vi HSK1 được xác định từ GF0025-2021 (MaNguon=1002). "
    "Thông tin chữ Hán, bộ thủ, số nét và cấu trúc được đối chiếu "
    "từ Unicode Character Database và Make Me a Hanzi "
    "(MaNguon=1, MaNguon=3). "
    "Pinyin được đối chiếu từ Make Me a Hanzi, CC-CEDICT và "
    "ngữ cảnh học HSK1. "
    "Nghĩa tiếng Việt lấy từ dữ liệu TuVung đã kiểm duyệt của đồ án "
    "hoặc được đồ án biên soạn/chuẩn hóa dựa trên nghĩa gốc "
    "CC-CEDICT (MaNguon=2). "
    "Bản ghi này thể hiện dữ liệu tổng hợp, không có nghĩa toàn bộ "
    "nội dung đến từ một nguồn duy nhất."
)


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
    / "hsk1_301_hanzi_final_preinsert.csv"
)

BEFORE_FILE = (
    REVIEW_DIR
    / "hsk1_17_hanzi_before_10r.csv"
)

AFTER_FILE = (
    REVIEW_DIR
    / "hsk1_301_hanzi_after_10r.csv"
)


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def normalize(value):

    return unicodedata.normalize(
        "NFC",
        clean(value),
    ).lower()


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


def get_current_hsk1_hanzi(
    cursor,
):

    cursor.execute(
        """
        SELECT
            ch.MaChuHan,
            ch.MaBaiHoc,
            ch.MaBoThu,
            ch.KyTu,
            ch.Pinyin,
            ch.NghiaTiengViet,
            ch.SoNet,
            ch.CachGhiNho,
            ch.ViDuTiengTrung,
            ch.ViDuPinyin,
            ch.ViDuTiengViet,
            ch.MaTep,
            ch.MaNguon,
            ch.ThuTu,
            ch.TrangThai,
            ch.NgayTao,
            bh.SoThuTuBai,
            bh.TieuDe

        FROM dbo.ChuHan AS ch

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
            ch.MaChuHan;
        """,
        COURSE_CODE,
    )

    rows = []

    for row in cursor.fetchall():

        rows.append(
            {
                "MaChuHan": int(row[0]),
                "MaBaiHoc": int(row[1]),
                "MaBoThu": row[2],
                "KyTu": clean(row[3]),
                "Pinyin": clean(row[4]),
                "NghiaTiengViet": clean(
                    row[5]
                ),
                "SoNet": row[6],
                "CachGhiNho": clean(
                    row[7]
                ),
                "ViDuTiengTrung": clean(
                    row[8]
                ),
                "ViDuPinyin": clean(
                    row[9]
                ),
                "ViDuTiengViet": clean(
                    row[10]
                ),
                "MaTep": row[11],
                "MaNguon": row[12],
                "ThuTu": row[13],
                "TrangThai": clean(
                    row[14]
                ),
                "NgayTao": clean(
                    row[15]
                ),
                "SoThuTuBai": int(
                    row[16]
                ),
                "TieuDeBai": clean(
                    row[17]
                ),
            }
        )

    return rows


def get_hsk1_net_count(
    cursor,
):

    cursor.execute(
        """
        SELECT COUNT(*)

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
            kh.MaKyHieu = ?;
        """,
        COURSE_CODE,
    )

    return int(
        cursor.fetchone()[0]
    )


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10R - GHI 301 CHU HAN HSK1 "
        "VAO DATABASE"
    )
    print("=" * 120)

    print()
    print("DAY LA BUOC GHI DATABASE THAT.")
    print()
    print("HANH DONG:")
    print("  17 ChuHan hien co -> GIU MaChuHan, CAP NHAT")
    print("  284 ChuHan con thieu -> INSERT")
    print("  TAO / LAY NguonDuLieu TONG HOP")
    print("  AUDIT 301 CHU TRUOC COMMIT")
    print()
    print("AN TOAN:")
    print("  TRANSACTION")
    print("  SAI -> ROLLBACK")
    print("  DUNG -> COMMIT")
    print("  KHONG DONG VAO NetChuHan")

    # =====================================================
    # 1. READ FINAL PREINSERT
    # =====================================================
    print()
    print("[1] DOC FILE 10Q FINAL")
    print("-" * 120)

    fields, rows = load_csv(
        INPUT_FILE
    )

    required = {
        "KyTu",
        "PhamVi",
        "BaiXuatHienDau",
        "MaBaiHoc",
        "TieuDeBai",
        "TuVungDauTien",
        "ThuTu",
        "Pinyin",
        "NghiaTiengViet",
        "MaBoThu",
        "SoNet",
        "NguonChuHanChienLuoc",
        "TrangThai",
        "DaCoTrongSQL",
        "MaChuHanHienTai",
        "HanhDong10R",
        "CotCanCapNhat",
        "GhiChu",
    }

    missing = (
        required
        - set(fields)
    )

    if missing:

        fail(
            "File 10Q thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    if len(rows) != EXPECTED_AFTER:

        fail(
            "File 10Q khong co "
            "dung 301 dong."
        )

    target_map = {}

    for row in rows:

        char = clean(
            row["KyTu"]
        )

        if char in target_map:

            fail(
                f"Trung KyTu trong file: {char}"
            )

        if not clean(
            row["Pinyin"]
        ):

            fail(
                f"{char}: thieu Pinyin."
            )

        if not clean(
            row["NghiaTiengViet"]
        ):

            fail(
                f"{char}: thieu NghiaTiengViet."
            )

        if to_int(
            row["MaBaiHoc"]
        ) is None:

            fail(
                f"{char}: thieu MaBaiHoc."
            )

        if to_int(
            row["MaBoThu"]
        ) is None:

            fail(
                f"{char}: thieu MaBoThu."
            )

        if to_int(
            row["SoNet"]
        ) is None:

            fail(
                f"{char}: thieu SoNet."
            )

        if (
            to_int(
                row["ThuTu"]
            )
            is None
            or
            to_int(
                row["ThuTu"]
            ) <= 0
        ):

            fail(
                f"{char}: ThuTu khong hop le."
            )

        target_map[
            char
        ] = row

    action_update = sum(
        1
        for row in rows
        if clean(
            row["HanhDong10R"]
        ) == "UPDATE"
    )

    action_keep = sum(
        1
        for row in rows
        if clean(
            row["HanhDong10R"]
        )
        ==
        "GIU_NOI_DUNG_CHI_CHOT_NGUON_10R"
    )

    action_insert = sum(
        1
        for row in rows
        if clean(
            row["HanhDong10R"]
        ) == "INSERT"
    )

    print(
        "Tong dong:",
        len(rows),
    )

    print(
        "Plan UPDATE noi dung:",
        action_update,
    )

    print(
        "Plan giu noi dung:",
        action_keep,
    )

    print(
        "Plan INSERT:",
        action_insert,
    )

    if (
        action_update
        != EXPECTED_UPDATE_CONTENT
    ):

        fail(
            "So plan UPDATE "
            "khong con bang 10."
        )

    if (
        action_keep
        != EXPECTED_KEEP_CONTENT
    ):

        fail(
            "So plan GIU "
            "khong con bang 7."
        )

    if (
        action_insert
        != EXPECTED_INSERT
    ):

        fail(
            "So plan INSERT "
            "khong con bang 284."
        )

    # =====================================================
    # 2. CONNECT
    # =====================================================
    print()
    print("[2] KET NOI DATABASE")
    print("-" * 120)

    connection = get_connection()

    try:

        connection.autocommit = False

        cursor = connection.cursor()

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
        # 3. VERIFY COMPONENT SOURCES
        # =================================================
        print()
        print(
            "[3] KIEM TRA CAC NGUON THANH PHAN"
        )
        print("-" * 120)

        expected_sources = {
            1: "Unicode Character Database",
            2: "CC-CEDICT",
            3: "Make Me a Hanzi",
            1002: "GF0025-2021 - Tu vung HSK",
        }

        placeholders = ",".join(
            "?"
            for _ in expected_sources
        )

        cursor.execute(
            f"""
            SELECT
                MaNguon,
                Ten
            FROM dbo.NguonDuLieu
            WHERE
                MaNguon IN (
                    {placeholders}
                )
            ORDER BY MaNguon;
            """,
            *list(
                expected_sources.keys()
            ),
        )

        source_rows = (
            cursor.fetchall()
        )

        found_sources = {
            int(row[0]): clean(row[1])
            for row in source_rows
        }

        for source_id, expected_name in (
            expected_sources.items()
        ):

            if source_id not in found_sources:

                fail(
                    "Thieu NguonDuLieu "
                    f"MaNguon={source_id}."
                )

            print(
                f"MaNguon={source_id} "
                f"| {found_sources[source_id]}"
            )

        print(
            "CAC NGUON THANH PHAN: OK"
        )

        # =================================================
        # 4. PRE-FLIGHT DATABASE
        # =================================================
        print()
        print(
            "[4] PRE-FLIGHT ChuHan HIEN TAI"
        )
        print("-" * 120)

        before_rows = (
            get_current_hsk1_hanzi(
                cursor
            )
        )

        before_count = len(
            before_rows
        )

        before_net_count = (
            get_hsk1_net_count(
                cursor
            )
        )

        print(
            "ChuHan HSK1 hien tai:",
            before_count,
        )

        print(
            "NetChuHan HSK1 hien tai:",
            before_net_count,
        )

        # Prevent accidental re-run after success
        if before_count == 301:

            fail(
                "Database da co 301 ChuHan HSK1. "
                "Co ve 10R da duoc chay truoc do. "
                "KHONG chay lai 10R."
            )

        if (
            before_count
            != EXPECTED_BEFORE
        ):

            fail(
                "Database khong con dung "
                "17 ChuHan truoc khi import. "
                f"Thuc te: {before_count}"
            )

        before_map = {}

        for row in before_rows:

            char = row["KyTu"]

            if char in before_map:

                fail(
                    "ChuHan hien tai bi trung KyTu: "
                    f"{char}"
                )

            before_map[
                char
            ] = row

        # -----------------------------------------
        # Verify the 17 IDs match 10Q file
        # -----------------------------------------
        for char, current in (
            before_map.items()
        ):

            if char not in target_map:

                fail(
                    f"{char}: co trong SQL "
                    "nhung khong co trong file 301."
                )

            file_row = (
                target_map[
                    char
                ]
            )

            file_current_id = to_int(
                file_row[
                    "MaChuHanHienTai"
                ]
            )

            if (
                file_current_id
                != current["MaChuHan"]
            ):

                fail(
                    f"{char}: MaChuHan trong file "
                    f"({file_current_id}) "
                    "khong khop SQL "
                    f"({current['MaChuHan']})."
                )

        # -----------------------------------------
        # Verify planned INSERT does not already exist
        # -----------------------------------------
        for row in rows:

            char = clean(
                row["KyTu"]
            )

            action = clean(
                row[
                    "HanhDong10R"
                ]
            )

            exists = (
                char in before_map
            )

            if (
                action == "INSERT"
                and exists
            ):

                fail(
                    f"{char}: plan INSERT "
                    "nhung da co trong SQL."
                )

            if (
                action != "INSERT"
                and not exists
            ):

                fail(
                    f"{char}: plan UPDATE/GIU "
                    "nhung khong ton tai trong SQL."
                )

        # -----------------------------------------
        # Verify all lesson IDs belong to HSK1
        # -----------------------------------------
        lesson_ids = sorted(
            {
                to_int(
                    row["MaBaiHoc"]
                )
                for row in rows
            }
        )

        lesson_placeholders = ",".join(
            "?"
            for _ in lesson_ids
        )

        cursor.execute(
            f"""
            SELECT
                bh.MaBaiHoc
            FROM dbo.BaiHoc AS bh
            INNER JOIN dbo.KhoaHoc AS kh
                ON bh.MaKhoaHoc
                = kh.MaKhoaHoc
            WHERE
                kh.MaKyHieu = ?
                AND bh.MaBaiHoc IN (
                    {lesson_placeholders}
                );
            """,
            COURSE_CODE,
            *lesson_ids,
        )

        valid_lesson_ids = {
            int(row[0])
            for row
            in cursor.fetchall()
        }

        if (
            valid_lesson_ids
            != set(lesson_ids)
        ):

            fail(
                "Co MaBaiHoc trong file "
                "khong thuoc HSK1-CORE."
            )

        # -----------------------------------------
        # Verify all radical IDs exist
        # -----------------------------------------
        radical_ids = sorted(
            {
                to_int(
                    row["MaBoThu"]
                )
                for row in rows
            }
        )

        radical_placeholders = ",".join(
            "?"
            for _ in radical_ids
        )

        cursor.execute(
            f"""
            SELECT MaBoThu
            FROM dbo.BoThu
            WHERE
                MaBoThu IN (
                    {radical_placeholders}
                );
            """,
            *radical_ids,
        )

        valid_radicals = {
            int(row[0])
            for row
            in cursor.fetchall()
        }

        if (
            valid_radicals
            != set(radical_ids)
        ):

            fail(
                "Co MaBoThu trong file "
                "khong ton tai trong dbo.BoThu."
            )

        print(
            "PRE-FLIGHT: OK"
        )

        # =================================================
        # 5. WRITE SAFETY SNAPSHOT
        # =================================================
        print()
        print(
            "[5] LUU SNAPSHOT 17 CHU TRUOC 10R"
        )
        print("-" * 120)

        snapshot_fields = [
            "MaChuHan",
            "MaBaiHoc",
            "MaBoThu",
            "KyTu",
            "Pinyin",
            "NghiaTiengViet",
            "SoNet",
            "CachGhiNho",
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
            "MaTep",
            "MaNguon",
            "ThuTu",
            "TrangThai",
            "NgayTao",
            "SoThuTuBai",
            "TieuDeBai",
        ]

        write_csv(
            BEFORE_FILE,
            snapshot_fields,
            before_rows,
        )

        print(
            BEFORE_FILE
        )

        # =================================================
        # 6. CREATE / GET AGGREGATE SOURCE
        # =================================================
        print()
        print(
            "[6] TAO / LAY NGUON TONG HOP"
        )
        print("-" * 120)

        cursor.execute(
            """
            SELECT
                MaNguon,
                Ten,
                GhiChu
            FROM dbo.NguonDuLieu
            WHERE Ten = ?;
            """,
            SOURCE_NAME,
        )

        aggregate_sources = (
            cursor.fetchall()
        )

        if len(
            aggregate_sources
        ) > 1:

            fail(
                "Co nhieu dong NguonDuLieu "
                "trung ten nguon tong hop."
            )

        if len(
            aggregate_sources
        ) == 1:

            aggregate_source_id = int(
                aggregate_sources[0][0]
            )

            print(
                "Da ton tai:"
            )

            print(
                f"MaNguon={aggregate_source_id}"
            )

        else:

            cursor.execute(
                """
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
                SOURCE_NAME,
                SOURCE_LICENSE,
                SOURCE_NOTE,
            )

            aggregate_source_id = int(
                cursor.fetchone()[0]
            )

            print(
                "Da tao trong transaction:"
            )

            print(
                f"MaNguon={aggregate_source_id}"
            )

        # =================================================
        # 7. UPDATE 17 EXISTING
        # =================================================
        print()
        print(
            "[7] UPDATE 17 ChuHan HIEN CO"
        )
        print("-" * 120)

        updated_rows = 0

        content_update_count = 0
        source_only_count = 0

        for row in rows:

            action = clean(
                row["HanhDong10R"]
            )

            if action == "INSERT":
                continue

            char = clean(
                row["KyTu"]
            )

            current = (
                before_map[
                    char
                ]
            )

            cursor.execute(
                """
                UPDATE dbo.ChuHan

                SET
                    MaBaiHoc = ?,
                    MaBoThu = ?,
                    Pinyin = ?,
                    NghiaTiengViet = ?,
                    SoNet = ?,
                    MaNguon = ?,
                    ThuTu = ?,
                    TrangThai = ?

                WHERE
                    MaChuHan = ?;
                """,
                to_int(
                    row["MaBaiHoc"]
                ),
                to_int(
                    row["MaBoThu"]
                ),
                clean(
                    row["Pinyin"]
                ),
                clean(
                    row["NghiaTiengViet"]
                ),
                to_int(
                    row["SoNet"]
                ),
                aggregate_source_id,
                to_int(
                    row["ThuTu"]
                ),
                STATUS_DRAFT,
                current[
                    "MaChuHan"
                ],
            )

            if cursor.rowcount != 1:

                fail(
                    f"{char}: UPDATE rowcount "
                    f"= {cursor.rowcount}"
                )

            updated_rows += 1

            if action == "UPDATE":

                content_update_count += 1

            else:

                source_only_count += 1

        print(
            "UPDATE thanh cong:",
            updated_rows,
        )

        print(
            "  Cap nhat noi dung:",
            content_update_count,
        )

        print(
            "  Chi chot nguon/trang thai:",
            source_only_count,
        )

        if updated_rows != 17:

            fail(
                "Khong UPDATE du 17 chu."
            )

        if (
            content_update_count
            != EXPECTED_UPDATE_CONTENT
        ):

            fail(
                "So content UPDATE "
                "khong bang 10."
            )

        if (
            source_only_count
            != EXPECTED_KEEP_CONTENT
        ):

            fail(
                "So source-only "
                "khong bang 7."
            )

        # =================================================
        # 8. INSERT 284 NEW
        # =================================================
        print()
        print(
            "[8] INSERT 284 ChuHan MOI"
        )
        print("-" * 120)

        inserted_rows = 0

        for row in rows:

            if clean(
                row["HanhDong10R"]
            ) != "INSERT":

                continue

            char = clean(
                row["KyTu"]
            )

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
                    TrangThai,
                    NgayTao
                )
                VALUES
                (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,

                    NULL,
                    NULL,
                    NULL,
                    NULL,

                    NULL,
                    ?,
                    ?,
                    ?,
                    SYSUTCDATETIME()
                );
                """,
                to_int(
                    row["MaBaiHoc"]
                ),
                to_int(
                    row["MaBoThu"]
                ),
                char,
                clean(
                    row["Pinyin"]
                ),
                clean(
                    row["NghiaTiengViet"]
                ),
                to_int(
                    row["SoNet"]
                ),
                aggregate_source_id,
                to_int(
                    row["ThuTu"]
                ),
                STATUS_DRAFT,
            )

            if cursor.rowcount != 1:

                fail(
                    f"{char}: INSERT rowcount "
                    f"= {cursor.rowcount}"
                )

            inserted_rows += 1

        print(
            "INSERT thanh cong:",
            inserted_rows,
        )

        if (
            inserted_rows
            != EXPECTED_INSERT
        ):

            fail(
                "Khong INSERT du 284 chu."
            )

        # =================================================
        # 9. AUDIT INSIDE TRANSACTION
        # =================================================
        print()
        print(
            "[9] AUDIT 301 CHU TRUOC COMMIT"
        )
        print("-" * 120)

        after_rows = (
            get_current_hsk1_hanzi(
                cursor
            )
        )

        after_count = len(
            after_rows
        )

        print(
            "ChuHan HSK1:",
            after_count,
        )

        if (
            after_count
            != EXPECTED_AFTER
        ):

            fail(
                "Sau ghi DB khong co "
                "dung 301 ChuHan."
            )

        after_map = {}

        for current in after_rows:

            char = current[
                "KyTu"
            ]

            if char in after_map:

                fail(
                    "Trung KyTu sau import: "
                    f"{char}"
                )

            after_map[
                char
            ] = current

        if (
            set(after_map)
            != set(target_map)
        ):

            missing_after = (
                set(target_map)
                - set(after_map)
            )

            extra_after = (
                set(after_map)
                - set(target_map)
            )

            fail(
                "Danh sach KyTu sau import "
                "khong khop file 301.\n"
                f"Thieu: "
                f"{' '.join(sorted(missing_after))}\n"
                f"Thua: "
                f"{' '.join(sorted(extra_after))}"
            )

        mismatch_rows = []

        for char, target in (
            target_map.items()
        ):

            actual = (
                after_map[
                    char
                ]
            )

            differences = []

            if (
                actual["MaBaiHoc"]
                !=
                to_int(
                    target[
                        "MaBaiHoc"
                    ]
                )
            ):

                differences.append(
                    "MaBaiHoc"
                )

            if (
                actual["MaBoThu"]
                !=
                to_int(
                    target[
                        "MaBoThu"
                    ]
                )
            ):

                differences.append(
                    "MaBoThu"
                )

            if (
                normalize(
                    actual["Pinyin"]
                )
                !=
                normalize(
                    target["Pinyin"]
                )
            ):

                differences.append(
                    "Pinyin"
                )

            if (
                normalize(
                    actual[
                        "NghiaTiengViet"
                    ]
                )
                !=
                normalize(
                    target[
                        "NghiaTiengViet"
                    ]
                )
            ):

                differences.append(
                    "NghiaTiengViet"
                )

            if (
                actual["SoNet"]
                !=
                to_int(
                    target["SoNet"]
                )
            ):

                differences.append(
                    "SoNet"
                )

            if (
                actual["ThuTu"]
                !=
                to_int(
                    target["ThuTu"]
                )
            ):

                differences.append(
                    "ThuTu"
                )

            if (
                actual["MaNguon"]
                != aggregate_source_id
            ):

                differences.append(
                    "MaNguon"
                )

            if (
                actual["TrangThai"]
                != STATUS_DRAFT
            ):

                differences.append(
                    "TrangThai"
                )

            if differences:

                mismatch_rows.append(
                    {
                        "KyTu": char,
                        "Khac": (
                            " | ".join(
                                differences
                            )
                        ),
                    }
                )

        print(
            "Mismatch voi file 10Q:",
            len(
                mismatch_rows
            ),
        )

        if mismatch_rows:

            for item in (
                mismatch_rows[:20]
            ):

                print(
                    f"  {item['KyTu']}: "
                    f"{item['Khac']}"
                )

            fail(
                "Noi dung SQL khong khop "
                "file preinsert."
            )

        # -----------------------------------------
        # Duplicate lesson order
        # -----------------------------------------
        cursor.execute(
            """
            SELECT
                ch.MaBaiHoc,
                ch.ThuTu,
                COUNT(*) AS SoLuong

            FROM dbo.ChuHan AS ch

            INNER JOIN dbo.BaiHoc AS bh
                ON ch.MaBaiHoc
                = bh.MaBaiHoc

            INNER JOIN dbo.KhoaHoc AS kh
                ON bh.MaKhoaHoc
                = kh.MaKhoaHoc

            WHERE
                kh.MaKyHieu = ?

            GROUP BY
                ch.MaBaiHoc,
                ch.ThuTu

            HAVING
                COUNT(*) > 1;
            """,
            COURSE_CODE,
        )

        duplicate_order = (
            cursor.fetchall()
        )

        print(
            "Trung MaBaiHoc + ThuTu:",
            len(
                duplicate_order
            ),
        )

        if duplicate_order:

            fail(
                "Co ThuTu ChuHan bi trung "
                "trong cung bai."
            )

        # -----------------------------------------
        # All 301 use aggregate source
        # -----------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)

            FROM dbo.ChuHan AS ch

            INNER JOIN dbo.BaiHoc AS bh
                ON ch.MaBaiHoc
                = bh.MaBaiHoc

            INNER JOIN dbo.KhoaHoc AS kh
                ON bh.MaKhoaHoc
                = kh.MaKhoaHoc

            WHERE
                kh.MaKyHieu = ?
                AND ch.MaNguon = ?;
            """,
            COURSE_CODE,
            aggregate_source_id,
        )

        source_count = int(
            cursor.fetchone()[0]
        )

        print(
            "ChuHan dung nguon tong hop:",
            source_count,
            "/301",
        )

        if source_count != 301:

            fail(
                "Khong phai 301 chu "
                "deu dung MaNguon tong hop."
            )

        # -----------------------------------------
        # NetChuHan must not change
        # -----------------------------------------
        after_net_count = (
            get_hsk1_net_count(
                cursor
            )
        )

        print(
            "NetChuHan truoc:",
            before_net_count,
        )

        print(
            "NetChuHan sau:",
            after_net_count,
        )

        if (
            after_net_count
            != before_net_count
        ):

            fail(
                "NetChuHan bi thay doi "
                "ngoai y muon."
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
            get_current_hsk1_hanzi(
                cursor
            )
        )

        committed_count = len(
            committed_rows
        )

        print(
            "ChuHan HSK1 sau COMMIT:",
            committed_count,
        )

        if (
            committed_count
            != EXPECTED_AFTER
        ):

            fail(
                "Sau COMMIT khong con "
                "dung 301 dong."
            )

        write_csv(
            AFTER_FILE,
            snapshot_fields,
            committed_rows,
        )

        print()
        print(
            "Snapshot sau import:"
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
            "KET QUA 10R"
        )
        print("=" * 120)

        print(
            "Nguon tong hop MaNguon:",
            aggregate_source_id,
        )

        print()
        print(
            "ChuHan truoc:",
            before_count,
        )

        print(
            "UPDATE ChuHan:",
            updated_rows,
        )

        print(
            "  Cap nhat noi dung:",
            content_update_count,
        )

        print(
            "  Chi chot nguon/trang thai:",
            source_only_count,
        )

        print(
            "INSERT ChuHan moi:",
            inserted_rows,
        )

        print(
            "ChuHan sau:",
            committed_count,
        )

        print()
        print(
            "Mismatch sau ghi:",
            0,
        )

        print(
            "Trung ThuTu:",
            0,
        )

        print(
            "NetChuHan bi thay doi:",
            0,
        )

        print()
        print(
            "DATABASE DA DUOC COMMIT."
        )

        print(
            "ChuHan HSK1 DA CO DU "
            "301 CHU TRONG SQL."
        )

        print(
            "NetChuHan CHUA DUOC INSERT."
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
                "Tat ca thay doi cua 10R "
                "da duoc ROLLBACK."
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
            "10R THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "Neu thay dong ROLLBACK DATABASE "
            "o tren thi SQL chua bi thay doi."
        )

        sys.exit(1)