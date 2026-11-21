from pathlib import Path
import sys
import zipfile
import re
import hashlib


# =========================================================
# THƯ MỤC GỐC D:\DATN1
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# THƯ MỤC CHỨA CC-CEDICT
# =========================================================
CEDICT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "cedict"
)

SOURCE_NAME = "CC-CEDICT"

# Chia nhỏ dữ liệu để import ổn định hơn
BATCH_SIZE = 1000


# =========================================================
# TÌM FILE ZIP CC-CEDICT
# =========================================================
def find_cedict_zip():
    if not CEDICT_DIR.exists():
        raise FileNotFoundError(
            f"Khong tim thay thu muc: {CEDICT_DIR}"
        )

    zip_files = list(
        CEDICT_DIR.glob("*.zip")
    )

    if not zip_files:
        raise FileNotFoundError(
            "Khong tim thay file ZIP CC-CEDICT "
            f"trong thu muc: {CEDICT_DIR}"
        )

    # Ưu tiên file có tên chứa cedict
    for path in zip_files:
        if "cedict" in path.name.lower():
            return path

    return zip_files[0]


# =========================================================
# TÌM FILE DỮ LIỆU TRONG ZIP
# =========================================================
def find_dictionary_member(zip_file):
    members = zip_file.namelist()

    # Ưu tiên file cedict*.u8
    for name in members:
        lower = name.lower()

        if (
            "cedict" in lower
            and lower.endswith(".u8")
        ):
            return name

    # Nếu không có thì thử txt
    for name in members:
        lower = name.lower()

        if (
            "cedict" in lower
            and lower.endswith(".txt")
        ):
            return name

    # Cuối cùng tìm file .u8 bất kỳ
    for name in members:
        if name.lower().endswith(".u8"):
            return name

    raise RuntimeError(
        "Khong tim thay file du lieu CC-CEDICT "
        "ben trong ZIP."
    )


# =========================================================
# ĐỊNH DẠNG 1 DÒNG CC-CEDICT
#
# Traditional Simplified [Pinyin] /definition/definition/
# =========================================================
ENTRY_PATTERN = re.compile(
    r"^(\S+)\s+(\S+)\s+\[([^\]]+)\]\s+/(.*)/$"
)


# =========================================================
# PARSE 1 DÒNG CC-CEDICT
# =========================================================
def parse_entry(line):
    line = line.strip()

    if not line:
        return None

    # Bỏ comment/header
    if line.startswith("#"):
        return None

    match = ENTRY_PATTERN.match(line)

    if not match:
        return None

    traditional = match.group(1).strip()
    simplified = match.group(2).strip()
    pinyin = match.group(3).strip()
    definition_block = match.group(4).strip()

    definitions = [
        item.strip()
        for item in definition_block.split("/")
        if item.strip()
    ]

    if not simplified:
        return None

    if not pinyin:
        return None

    if not definitions:
        return None

    # =====================================================
    # KIỂM TRA ĐÚNG GIỚI HẠN SQL
    #
    # ChuHan  : nvarchar(100)
    # PhienAm : nvarchar(200)
    #
    # Nếu vượt giới hạn thì báo lỗi,
    # KHÔNG tự cắt dữ liệu.
    # =====================================================
    if len(simplified) > 100:
        raise RuntimeError(
            "CC-CEDICT co ChuHan vuot 100 ky tu. "
            f"Do dai={len(simplified)} | "
            f"Du lieu={simplified[:100]}"
        )

    if len(pinyin) > 200:
        raise RuntimeError(
            "CC-CEDICT co PhienAm vuot 200 ky tu. "
            f"ChuHan={simplified} | "
            f"Do dai Pinyin={len(pinyin)}"
        )

    # NghiaGoc trong SQL là nvarchar(max)
    # nên giữ nguyên toàn bộ nghĩa.
    nghia_goc = " / ".join(definitions)

    # =====================================================
    # TẠO ID ỔN ĐỊNH CHO ENTRY
    #
    # Traditional chỉ dùng để tạo ID phân biệt entry.
    # KHÔNG lưu vào ChuPhonThe.
    # =====================================================
    key = (
        f"{traditional}|"
        f"{simplified}|"
        f"{pinyin}"
    )

    digest = hashlib.sha1(
        key.encode("utf-8")
    ).hexdigest()

    external_id = (
        "cedict:"
        + digest
    )

    return {
        "external_id": external_id,
        "simplified": simplified,
        "pinyin": pinyin,
        "definition": nghia_goc,
    }


# =========================================================
# LẤY MaNguon CỦA CC-CEDICT
# =========================================================
def get_source_id(cursor):
    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        SOURCE_NAME,
    )

    row = cursor.fetchone()

    if not row:
        raise RuntimeError(
            "Khong tim thay nguon CC-CEDICT. "
            "Hay chay 01_import_sources.py truoc."
        )

    return row[0]


# =========================================================
# TẠO BẢNG TẠM
# =========================================================
def create_stage_table(cursor):
    cursor.execute(
        """
        IF OBJECT_ID('tempdb..#CedictStage') IS NOT NULL
            DROP TABLE #CedictStage;

        CREATE TABLE #CedictStage
        (
            MaNguon int NOT NULL,

            MaNguonBenNgoai nvarchar(200)
                COLLATE DATABASE_DEFAULT
                NOT NULL,

            ChuHan nvarchar(100)
                COLLATE DATABASE_DEFAULT
                NOT NULL,

            PhienAm nvarchar(200)
                COLLATE DATABASE_DEFAULT
                NOT NULL,

            NghiaGoc nvarchar(max)
                COLLATE DATABASE_DEFAULT
                NOT NULL,

            CONSTRAINT PK_CedictStage
                PRIMARY KEY
                (
                    MaNguon,
                    MaNguonBenNgoai
                )
        );
        """
    )


# =========================================================
# INSERT MỘT BATCH VÀO BẢNG TẠM
#
# KHÔNG DÙNG fast_executemany
# vì NghiaGoc có độ dài thay đổi lớn.
# =========================================================
def insert_batch(cursor, batch):
    if not batch:
        return

    # Đây là chỗ đã sửa lỗi:
    # String data, right truncation
    cursor.fast_executemany = False

    cursor.executemany(
        """
        INSERT INTO #CedictStage
        (
            MaNguon,
            MaNguonBenNgoai,
            ChuHan,
            PhienAm,
            NghiaGoc
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        batch,
    )


# =========================================================
# ĐỌC CC-CEDICT VÀ ĐƯA VÀO BẢNG TẠM
# =========================================================
def load_cedict_to_stage(
    cursor,
    zip_path,
    member_name,
    ma_nguon,
):
    total_lines = 0
    valid_entries = 0
    invalid_lines = 0
    duplicate_entries = 0

    batch = []
    seen_ids = set()

    samples = []

    with zipfile.ZipFile(
        zip_path,
        "r",
    ) as zip_file:

        with zip_file.open(
            member_name,
            "r",
        ) as file:

            for raw_line in file:
                total_lines += 1

                try:
                    line = raw_line.decode(
                        "utf-8"
                    ).rstrip("\r\n")

                except UnicodeDecodeError:
                    invalid_lines += 1
                    continue

                # Bỏ comment và dòng trống
                if (
                    not line.strip()
                    or line.lstrip().startswith("#")
                ):
                    continue

                entry = parse_entry(line)

                if entry is None:
                    invalid_lines += 1
                    continue

                external_id = (
                    entry["external_id"]
                )

                # Tránh trùng ngay trong file nguồn
                if external_id in seen_ids:
                    duplicate_entries += 1
                    continue

                seen_ids.add(
                    external_id
                )

                row = (
                    ma_nguon,
                    external_id,

                    # CHỈ LƯU GIẢN THỂ
                    entry["simplified"],

                    entry["pinyin"],
                    entry["definition"],
                )

                batch.append(row)

                valid_entries += 1

                # Lấy 5 dòng mẫu
                if len(samples) < 5:
                    samples.append(
                        (
                            entry["simplified"],
                            entry["pinyin"],
                            entry["definition"],
                        )
                    )

                # Đủ 1000 thì insert
                if len(batch) >= BATCH_SIZE:

                    insert_batch(
                        cursor,
                        batch,
                    )

                    batch.clear()

                # In tiến độ
                if (
                    valid_entries % 10000 == 0
                ):
                    print(
                        f"Da doc va dua vao bang tam: "
                        f"{valid_entries} muc..."
                    )

            # Batch cuối cùng
            if batch:
                insert_batch(
                    cursor,
                    batch,
                )

    return {
        "total_lines": total_lines,
        "valid_entries": valid_entries,
        "invalid_lines": invalid_lines,
        "duplicate_entries": duplicate_entries,
        "samples": samples,
    }


# =========================================================
# ĐỒNG BỘ BẢNG TẠM → MucTuDien
# =========================================================
def sync_to_dictionary(cursor):

    # =====================================================
    # 1. CẬP NHẬT ENTRY CC-CEDICT ĐÃ TỒN TẠI
    #
    # Không ghi đè:
    # - NghiaTiengViet
    # - NghiaVietDaDuyet
    # =====================================================
    cursor.execute(
        """
        UPDATE target

        SET
            target.ChuHan =
                source.ChuHan,

            target.ChuPhonThe =
                NULL,

            target.PhienAm =
                source.PhienAm,

            target.NghiaGoc =
                source.NghiaGoc,

            target.NgonNguNghiaGoc =
                'en'

        FROM dbo.MucTuDien AS target

        INNER JOIN #CedictStage AS source

            ON target.MaNguon =
               source.MaNguon

           AND target.MaNguonBenNgoai
                   COLLATE DATABASE_DEFAULT
               =
               source.MaNguonBenNgoai
                   COLLATE DATABASE_DEFAULT;
        """
    )

    # =====================================================
    # 2. THÊM ENTRY CHƯA TỒN TẠI
    # =====================================================
    cursor.execute(
        """
        INSERT INTO dbo.MucTuDien
        (
            MaNguon,
            MaNguonBenNgoai,
            ChuHan,
            ChuPhonThe,
            PhienAm,
            NghiaGoc,
            NgonNguNghiaGoc,
            NghiaTiengViet,
            NghiaVietDaDuyet
        )

        SELECT
            source.MaNguon,
            source.MaNguonBenNgoai,

            -- Chữ giản thể
            source.ChuHan,

            -- Không lưu chữ phồn thể
            NULL,

            source.PhienAm,
            source.NghiaGoc,

            -- Nghĩa gốc CC-CEDICT là tiếng Anh
            'en',

            -- Chưa có nghĩa Việt
            NULL,

            -- Chưa duyệt nghĩa Việt
            0

        FROM #CedictStage AS source

        WHERE NOT EXISTS
        (
            SELECT 1

            FROM dbo.MucTuDien AS target

            WHERE target.MaNguon =
                  source.MaNguon

              AND target.MaNguonBenNgoai
                      COLLATE DATABASE_DEFAULT
                  =
                  source.MaNguonBenNgoai
                      COLLATE DATABASE_DEFAULT
        );
        """
    )

    # =====================================================
    # 2. THÊM ENTRY CHƯA CÓ
    # =====================================================
    cursor.execute(
        """
        INSERT INTO dbo.MucTuDien
        (
            MaNguon,
            MaNguonBenNgoai,
            ChuHan,
            ChuPhonThe,
            PhienAm,
            NghiaGoc,
            NgonNguNghiaGoc,
            NghiaTiengViet,
            NghiaVietDaDuyet
        )

        SELECT
            source.MaNguon,
            source.MaNguonBenNgoai,

            -- Chữ giản thể
            source.ChuHan,

            -- Không lưu phồn thể
            NULL,

            source.PhienAm,
            source.NghiaGoc,

            -- Nghĩa gốc CC-CEDICT là tiếng Anh
            'en',

            -- Chưa dịch tiếng Việt
            NULL,

            -- Chưa được duyệt nghĩa Việt
            0

        FROM #CedictStage AS source

        WHERE NOT EXISTS
        (
            SELECT 1

            FROM dbo.MucTuDien AS target

            WHERE target.MaNguon =
                  source.MaNguon

              AND target.MaNguonBenNgoai =
                  source.MaNguonBenNgoai
        );
        """
    )


# =========================================================
# MAIN
# =========================================================
def main():
    conn = None

    try:
        print("=" * 72)
        print(
            "BAT DAU IMPORT CC-CEDICT "
            "VAO MucTuDien"
        )
        print("=" * 72)

        # -------------------------------------------------
        # TÌM FILE ZIP
        # -------------------------------------------------
        zip_path = find_cedict_zip()

        print(
            f"File ZIP: "
            f"{zip_path.name}"
        )

        # -------------------------------------------------
        # TÌM FILE .u8 TRONG ZIP
        # -------------------------------------------------
        with zipfile.ZipFile(
            zip_path,
            "r",
        ) as zip_file:

            member_name = (
                find_dictionary_member(
                    zip_file
                )
            )

        print(
            f"File du lieu trong ZIP: "
            f"{member_name}"
        )

        # -------------------------------------------------
        # KẾT NỐI SQL
        # -------------------------------------------------
        conn = get_connection()
        cursor = conn.cursor()

        ma_nguon = get_source_id(
            cursor
        )

        print(
            f"MaNguon CC-CEDICT: "
            f"{ma_nguon}"
        )

        # -------------------------------------------------
        # ĐẾM TRƯỚC KHI IMPORT
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.MucTuDien
            WHERE MaNguon = ?
            """,
            ma_nguon,
        )

        before_count = (
            cursor.fetchone()[0]
        )

        print(
            "So muc CC-CEDICT "
            f"truoc import: {before_count}"
        )

        print()
        print(
            "Dang doc va phan tich "
            "du lieu CC-CEDICT..."
        )
        print()

        # -------------------------------------------------
        # TẠO BẢNG TẠM
        # -------------------------------------------------
        create_stage_table(
            cursor
        )

        # -------------------------------------------------
        # ĐỌC FILE
        # -------------------------------------------------
        stats = load_cedict_to_stage(
            cursor=cursor,
            zip_path=zip_path,
            member_name=member_name,
            ma_nguon=ma_nguon,
        )

        print()
        print("-" * 72)

        print(
            f"Tong so dong da doc: "
            f"{stats['total_lines']}"
        )

        print(
            f"So muc hop le: "
            f"{stats['valid_entries']}"
        )

        print(
            f"So dong khong parse duoc: "
            f"{stats['invalid_lines']}"
        )

        print(
            f"So muc trung lap bo qua: "
            f"{stats['duplicate_entries']}"
        )

        # -------------------------------------------------
        # KIỂM TRA AN TOÀN
        # -------------------------------------------------
        if stats["valid_entries"] < 1000:

            raise RuntimeError(
                "So muc parse duoc qua it. "
                "Co the dinh dang file khong dung "
                "CC-CEDICT. Dung import."
            )

        # -------------------------------------------------
        # IN 5 MỤC MẪU
        # -------------------------------------------------
        print()
        print("5 MUC MAU SAU KHI PARSE:")
        print()

        for (
            chu_han,
            pinyin,
            definition,
        ) in stats["samples"]:

            short_definition = (
                definition[:120]
            )

            print(
                f"{chu_han} | "
                f"{pinyin} | "
                f"{short_definition}"
            )

        # -------------------------------------------------
        # ĐỒNG BỘ VÀO MucTuDien
        # -------------------------------------------------
        print()
        print(
            "Dang dong bo vao "
            "dbo.MucTuDien..."
        )

        sync_to_dictionary(
            cursor
        )

        # -------------------------------------------------
        # COMMIT
        # -------------------------------------------------
        conn.commit()

        # -------------------------------------------------
        # ĐẾM SAU IMPORT
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.MucTuDien
            WHERE MaNguon = ?
            """,
            ma_nguon,
        )

        after_count = (
            cursor.fetchone()[0]
        )

        new_count = (
            after_count
            - before_count
        )

        print()
        print("-" * 72)
        print("IMPORT THANH CONG")
        print("-" * 72)

        print(
            f"So muc truoc import: "
            f"{before_count}"
        )

        print(
            f"So muc sau import: "
            f"{after_count}"
        )

        print(
            f"So muc moi tang them: "
            f"{new_count}"
        )

        # -------------------------------------------------
        # KIỂM TRA KHÔNG LƯU PHỒN THỂ
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.MucTuDien
            WHERE MaNguon = ?
              AND ChuPhonThe IS NOT NULL
            """,
            ma_nguon,
        )

        traditional_count = (
            cursor.fetchone()[0]
        )

        print(
            "So dong ChuPhonThe "
            f"khac NULL: {traditional_count}"
        )

        # -------------------------------------------------
        # KIỂM TRA NGHĨA VIỆT
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.MucTuDien
            WHERE MaNguon = ?
              AND NghiaVietDaDuyet = 1
            """,
            ma_nguon,
        )

        approved_vi = (
            cursor.fetchone()[0]
        )

        print(
            "So muc nghia Viet "
            f"da duyet: {approved_vi}"
        )

        # -------------------------------------------------
        # 10 DÒNG ĐẦU TRONG SQL
        # -------------------------------------------------
        print()
        print("10 MUC DAU TRONG SQL:")
        print()

        cursor.execute(
            """
            SELECT TOP 10
                MaMucTu,
                ChuHan,
                ChuPhonThe,
                PhienAm,
                NghiaGoc,
                NghiaTiengViet,
                NghiaVietDaDuyet
            FROM dbo.MucTuDien
            WHERE MaNguon = ?
            ORDER BY MaMucTu
            """,
            ma_nguon,
        )

        for row in cursor.fetchall():

            if row.NghiaGoc:
                nghia = (
                    row.NghiaGoc[:100]
                )
            else:
                nghia = ""

            print(
                f"{row.MaMucTu} | "
                f"{row.ChuHan} | "
                f"{row.PhienAm} | "
                f"{nghia}"
            )

        print()
        print("=" * 72)
        print("HOAN TAT")
        print("=" * 72)

        cursor.close()

    except Exception as e:

        # Nếu có lỗi thì không lưu dở dữ liệu
        if conn:
            conn.rollback()

        print()
        print("=" * 72)
        print("IMPORT THAT BAI")
        print("=" * 72)
        print("Loi:", e)

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()