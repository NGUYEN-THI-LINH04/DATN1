from pathlib import Path
import sys
import csv
import re


# =========================================================
# THƯ MỤC GỐC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# FILE
# =========================================================
HSK_DIR = ROOT_DIR / "data_sources" / "hsk"

READY_FILE = (
    HSK_DIR
    / "hsk1_4_clean_ready.csv"
)

MANUAL_FILE = (
    HSK_DIR
    / "hsk1_4_clean_manual.csv"
)

OUTPUT_FILE = (
    HSK_DIR
    / "hsk1_4_final_base.csv"
)

STILL_MANUAL_FILE = (
    HSK_DIR
    / "hsk1_4_still_manual.csv"
)


# =========================================================
# CHUẨN HÓA PINYIN
#
# Dùng ở bước fallback.
# Không dùng làm điều kiện chính.
# =========================================================
def normalize_pinyin(value):

    if not value:
        return ""

    value = value.strip().lower()

    value = value.replace("ü", "v")
    value = value.replace("u:", "v")

    value = value.replace("'", "")
    value = value.replace("’", "")
    value = value.replace("·", "")
    value = value.replace("-", "")
    value = value.replace(" ", "")

    return value


# =========================================================
# LẤY MaNguon CC-CEDICT
# =========================================================
def get_cedict_source_id(cursor):

    cursor.execute(
        """
        SELECT MaNguon
        FROM dbo.NguonDuLieu
        WHERE Ten = ?
        """,
        "CC-CEDICT",
    )

    row = cursor.fetchone()

    if not row:
        raise RuntimeError(
            "Khong tim thay nguon CC-CEDICT."
        )

    return row[0]


# =========================================================
# TÌM LẠI ENTRY CC-CEDICT
#
# Dùng cho 4 trường hợp có CEDICTKey
# nhưng bước 05d chưa nối được.
# =========================================================
def find_cedict_candidates(
    cursor,
    ma_nguon,
    word,
):

    cursor.execute(
        """
        SELECT
            MaMucTu,
            ChuHan,
            PhienAm,
            NghiaGoc
        FROM dbo.MucTuDien
        WHERE MaNguon = ?
          AND ChuHan = ?
        ORDER BY MaMucTu
        """,
        ma_nguon,
        word,
    )

    result = []

    for row in cursor.fetchall():

        result.append(
            {
                "MaMucTu": row.MaMucTu,
                "ChuHan": row.ChuHan,
                "PhienAm": row.PhienAm or "",
                "NghiaGoc": row.NghiaGoc or "",
            }
        )

    return result


# =========================================================
# CHỌN CANDIDATE AN TOÀN
# =========================================================
def choose_candidate(
    candidates,
    standard_pinyin,
):

    if not candidates:
        return []

    # -----------------------------------------------------
    # Nếu chỉ có đúng một entry cho chữ này
    # thì có thể dùng luôn.
    # -----------------------------------------------------
    if len(candidates) == 1:
        return candidates

    standard = normalize_pinyin(
        standard_pinyin
    )

    matched = []

    for candidate in candidates:

        candidate_pinyin = (
            normalize_pinyin(
                candidate["PhienAm"]
            )
        )

        if candidate_pinyin == standard:
            matched.append(
                candidate
            )

    # Chỉ lấy khi sau đối chiếu còn đúng 1 entry
    if len(matched) == 1:
        return matched

    # Nếu có nhiều entry nhưng tất cả đều cùng Pinyin,
    # có thể giữ chúng để gộp nghĩa.
    if len(matched) > 1:

        pinyins = {
            normalize_pinyin(
                item["PhienAm"]
            )
            for item in matched
        }

        if len(pinyins) == 1:
            return matched

    return []


# =========================================================
# ĐỌC CSV
# =========================================================
def read_csv_file(path):

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        return (
            list(reader),
            list(reader.fieldnames or []),
        )


# =========================================================
# LOẠI TRÙNG GIỮ THỨ TỰ
# =========================================================
def unique_keep_order(values):

    result = []
    seen = set()

    for value in values:

        if not value:
            continue

        if value in seen:
            continue

        seen.add(value)
        result.append(value)

    return result


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 72)
        print(
            "HOAN TAT BO TU VUNG HSK 1-4"
        )
        print("=" * 72)

        if not READY_FILE.exists():
            raise FileNotFoundError(
                f"Khong tim thay: {READY_FILE}"
            )

        if not MANUAL_FILE.exists():
            raise FileNotFoundError(
                f"Khong tim thay: {MANUAL_FILE}"
            )

        # -------------------------------------------------
        # Đọc dữ liệu
        # -------------------------------------------------
        ready_rows, fieldnames = (
            read_csv_file(
                READY_FILE
            )
        )

        manual_rows, manual_fields = (
            read_csv_file(
                MANUAL_FILE
            )
        )

        print(
            f"So dong da sach: "
            f"{len(ready_rows)}"
        )

        print(
            f"So dong manual: "
            f"{len(manual_rows)}"
        )

        # -------------------------------------------------
        # Thêm cột quản lý nguồn
        # -------------------------------------------------
        extra_fields = [
            "NguonTuVung",
            "NguonNghiaGoc",
            "CanKiemTraThuCong",
        ]

        for field in extra_fields:

            if field not in fieldnames:
                fieldnames.append(
                    field
                )

        # -------------------------------------------------
        # Các dòng 3232 đã sạch
        # -------------------------------------------------
        final_rows = []

        for row in ready_rows:

            row[
                "NguonTuVung"
            ] = "GF0025-2021"

            row[
                "NguonNghiaGoc"
            ] = "CC-CEDICT"

            row[
                "CanKiemTraThuCong"
            ] = "0"

            final_rows.append(
                row
            )

        # -------------------------------------------------
        # SQL
        # -------------------------------------------------
        conn = get_connection()
        cursor = conn.cursor()

        ma_nguon_cedict = (
            get_cedict_source_id(
                cursor
            )
        )

        resolved = 0
        hsk_only = 0

        still_manual = []

        # -------------------------------------------------
        # Xử lý 13 mục còn lại
        # -------------------------------------------------
        for row in manual_rows:

            cedict_key = (
                row.get(
                    "CEDICTKey",
                    "",
                )
                .strip()
            )

            word = (
                row.get(
                    "TuChinh",
                    "",
                )
                .strip()
            )

            pinyin = (
                row.get(
                    "PinyinChuan",
                    "",
                )
                .strip()
            )

            # =============================================
            # NHÓM 1:
            # Có CEDICTKey nhưng chưa match SQL
            # =============================================
            if cedict_key:

                candidates = (
                    find_cedict_candidates(
                        cursor,
                        ma_nguon_cedict,
                        word,
                    )
                )

                selected = (
                    choose_candidate(
                        candidates,
                        pinyin,
                    )
                )

                if selected:

                    row[
                        "SoKetQuaCedict"
                    ] = str(
                        len(selected)
                    )

                    row[
                        "MaMucTuCedict"
                    ] = " | ".join(
                        str(
                            item["MaMucTu"]
                        )
                        for item
                        in selected
                    )

                    row[
                        "TuCedictKhop"
                    ] = " | ".join(
                        unique_keep_order(
                            [
                                item["ChuHan"]
                                for item
                                in selected
                            ]
                        )
                    )

                    row[
                        "PinyinCedictKhop"
                    ] = " | ".join(
                        unique_keep_order(
                            [
                                item["PhienAm"]
                                for item
                                in selected
                            ]
                        )
                    )

                    row[
                        "NghiaAnhCedict"
                    ] = " || ".join(
                        unique_keep_order(
                            [
                                item["NghiaGoc"]
                                for item
                                in selected
                            ]
                        )
                    )

                    row[
                        "TrangThaiDoiChieu"
                    ] = (
                        "fallback_cedict_ok"
                    )

                    row[
                        "NguonTuVung"
                    ] = (
                        "GF0025-2021"
                    )

                    row[
                        "NguonNghiaGoc"
                    ] = (
                        "CC-CEDICT"
                    )

                    row[
                        "CanKiemTraThuCong"
                    ] = "0"

                    final_rows.append(
                        row
                    )

                    resolved += 1

                    continue

                # Không tự đoán nếu vẫn mơ hồ
                row[
                    "NguonTuVung"
                ] = "GF0025-2021"

                row[
                    "NguonNghiaGoc"
                ] = ""

                row[
                    "CanKiemTraThuCong"
                ] = "1"

                still_manual.append(
                    row
                )

                continue

            # =============================================
            # NHÓM 2:
            # Có trong HSK nhưng CC-CEDICT
            # không có entry riêng.
            #
            # Vẫn phải giữ trong bộ HSK.
            # =============================================
            row[
                "SoKetQuaCedict"
            ] = "0"

            row[
                "MaMucTuCedict"
            ] = ""

            row[
                "TuCedictKhop"
            ] = ""

            row[
                "PinyinCedictKhop"
            ] = ""

            row[
                "NghiaAnhCedict"
            ] = ""

            row[
                "TrangThaiDoiChieu"
            ] = (
                "hsk_khong_co_cedict"
            )

            row[
                "NguonTuVung"
            ] = (
                "GF0025-2021"
            )

            row[
                "NguonNghiaGoc"
            ] = ""

            # Chưa có nguồn nghĩa,
            # nên bắt buộc phải duyệt thủ công
            row[
                "CanKiemTraThuCong"
            ] = "1"

            final_rows.append(
                row
            )

            hsk_only += 1

        # -------------------------------------------------
        # Sắp xếp theo ID HSK
        # -------------------------------------------------
        final_rows.sort(
            key=lambda x: (
                int(
                    x.get(
                        "CapDoHSK",
                        "0",
                    )
                    or 0
                ),
                x.get(
                    "ID",
                    "",
                ),
            )
        )

        # -------------------------------------------------
        # Ghi file hoàn chỉnh
        # -------------------------------------------------
        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            writer.writeheader()

            writer.writerows(
                final_rows
            )

        # -------------------------------------------------
        # Ghi những mục vẫn chưa xử lý được
        # -------------------------------------------------
        with open(
            STILL_MANUAL_FILE,
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            writer.writeheader()

            writer.writerows(
                still_manual
            )

        # -------------------------------------------------
        # Kết quả
        # -------------------------------------------------
        print()
        print("-" * 72)
        print("KET QUA")
        print("-" * 72)

        print(
            "3232 muc ban dau: "
            f"{len(ready_rows)}"
        )

        print(
            "CEDICT fallback xu ly duoc: "
            f"{resolved}"
        )

        print(
            "Muc HSK khong co CEDICT rieng: "
            f"{hsk_only}"
        )

        print(
            "Van can kiem tra CEDICT: "
            f"{len(still_manual)}"
        )

        print()
        print(
            "Tong trong file final: "
            f"{len(final_rows)}"
        )

        print()
        print(
            "File final:"
        )

        print(
            OUTPUT_FILE
        )

        print()
        print(
            "File van can kiem tra:"
        )

        print(
            STILL_MANUAL_FILE
        )

        print()

        if len(final_rows) == 3245:
            print(
                "DA DU 3245 MUC HSK 1-4."
            )
        else:
            print(
                "CHUA DU 3245 MUC."
            )

        print()
        print(
            "CHUA INSERT VAO TuVung."
        )

        print(
            "CHUA DAT DaDuyet = 1."
        )

        print()
        print("=" * 72)
        print("HOAN TAT")
        print("=" * 72)

        cursor.close()

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 72)
        print("THUC HIEN THAT BAI")
        print("=" * 72)

        print(
            "Loi:",
            e,
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()