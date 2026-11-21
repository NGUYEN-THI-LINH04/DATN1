from pathlib import Path
import argparse
import csv
import re
import sys


# ============================================================
# ROOT PROJECT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from database import get_connection


# ============================================================
# PYPINYIN
# ============================================================

try:

    from pypinyin import lazy_pinyin, Style

except ImportError:

    print()
    print("❌ Chưa cài pypinyin.")
    print()
    print("Hãy chạy:")
    print()
    print("python -m pip install pypinyin")
    print()

    sys.exit(1)


# ============================================================
# CẤU HÌNH
# ============================================================

COURSE_CODE = "HSK1-CORE"

EXPECTED_HANZI = 301

OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "hsk1_hanzi_content_preview.csv"
)


# ============================================================
# HELPER
# ============================================================

def clean(value):

    if value is None:
        return ""

    value = str(value).strip()

    if value.upper() == "NULL":
        return ""

    return value


def first_meaning(value):

    value = clean(value)

    if ";" in value:

        value = value.split(
            ";",
            1,
        )[0].strip()

    return value


# ============================================================
# CHUYỂN CÂU TRUNG -> PINYIN
# ============================================================

def make_pinyin(text):

    text = clean(text)

    if not text:
        return ""

    parts = lazy_pinyin(
        text,
        style=Style.TONE,
        neutral_tone_with_five=False,
        errors=lambda chars: list(chars),
    )

    result = " ".join(parts)

    # Bỏ khoảng trắng trước dấu câu
    result = re.sub(
        r"\s+([，。！？、；：,.!?;:])",
        r"\1",
        result,
    )

    # Xử lý ngoặc kép Trung
    result = result.replace(
        "“ ",
        "“"
    )

    result = result.replace(
        " ”",
        "”"
    )

    # Xóa khoảng trắng thừa
    result = re.sub(
        r"\s+",
        " ",
        result,
    ).strip()

    return result


# ============================================================
# LẤY KHÓA HSK1
# ============================================================

def get_course(cursor):

    cursor.execute(
        """
        SELECT
            MaKhoaHoc,
            MaKyHieu,
            TieuDe

        FROM dbo.KhoaHoc

        WHERE MaKyHieu = ?
        """,
        COURSE_CODE,
    )

    rows = cursor.fetchall()

    if len(rows) != 1:

        raise RuntimeError(
            f"Không tìm thấy duy nhất "
            f"{COURSE_CODE}. "
            f"Số bản ghi: {len(rows)}"
        )

    return rows[0]


# ============================================================
# LẤY 301 CHỮ HÁN
# ============================================================

def load_hanzi(
    cursor,
    ma_khoa_hoc,
):

    cursor.execute(
        """
        SELECT
            bh.SoThuTuBai,
            bh.MaBaiHoc,

            ch.ThuTu,
            ch.MaChuHan,

            ch.KyTu,
            ch.Pinyin,
            ch.NghiaTiengViet,

            ch.MaBoThu,

            bt.KyHieu
                AS BoThuKyHieu,

            bt.TenBoThu,
            bt.YNghia
                AS YNghiaBoThu,

            ch.SoNet,

            ch.CachGhiNho,

            ch.ViDuTiengTrung,
            ch.ViDuPinyin,
            ch.ViDuTiengViet,

            ch.MaTep,
            ch.MaNguon,
            ch.TrangThai

        FROM dbo.ChuHan ch

        INNER JOIN dbo.BaiHoc bh
            ON bh.MaBaiHoc = ch.MaBaiHoc

        LEFT JOIN dbo.BoThu bt
            ON bt.MaBoThu = ch.MaBoThu

        WHERE bh.MaKhoaHoc = ?

        ORDER BY
            bh.SoThuTuBai,
            ch.ThuTu
        """,
        ma_khoa_hoc,
    )

    rows = cursor.fetchall()

    if len(rows) != EXPECTED_HANZI:

        raise RuntimeError(
            f"HSK1 phải có "
            f"{EXPECTED_HANZI} chữ Hán. "
            f"Thực tế: {len(rows)}"
        )

    return rows


# ============================================================
# TÌM VÍ DỤ TỪ 501 TỪ VỰNG ĐÃ HOÀN THIỆN
#
# Ưu tiên:
# 1. Từ thuộc cùng bài
# 2. Từ ngắn hơn
# 3. Có câu ví dụ chứa chính chữ Hán đang xét
# ============================================================

def find_vocab_example(
    cursor,
    ma_khoa_hoc,
    lesson_number,
    hanzi,
):

    like_value = (
        "%"
        + hanzi
        + "%"
    )

    cursor.execute(
        """
        SELECT TOP 1
            tv.MaTuVung,
            tv.ChuHan,
            tv.ViDuTiengTrung,
            tv.ViDuTiengViet,

            bh.SoThuTuBai

        FROM dbo.TuVung tv

        INNER JOIN dbo.TuVungBaiHoc tvbh
            ON tvbh.MaTuVung = tv.MaTuVung

        INNER JOIN dbo.BaiHoc bh
            ON bh.MaBaiHoc = tvbh.MaBaiHoc

        WHERE bh.MaKhoaHoc = ?

          AND tv.ChuHan LIKE ?

          AND tv.ViDuTiengTrung IS NOT NULL
          AND LTRIM(
                RTRIM(
                    tv.ViDuTiengTrung
                )
              ) <> ''

          AND tv.ViDuTiengViet IS NOT NULL
          AND LTRIM(
                RTRIM(
                    tv.ViDuTiengViet
                )
              ) <> ''

          AND tv.ViDuTiengTrung LIKE ?

        ORDER BY

            CASE
                WHEN bh.SoThuTuBai = ?
                THEN 0
                ELSE 1
            END,

            LEN(tv.ChuHan),

            bh.SoThuTuBai,

            tvbh.ThuTu
        """,

        ma_khoa_hoc,
        like_value,
        like_value,
        lesson_number,
    )

    return cursor.fetchone()


# ============================================================
# TẠO CÁCH GHI NHỚ
#
# Lưu ý:
# Đây là mẹo học mặt chữ,
# KHÔNG tuyên bố là giải thích nguồn gốc chữ.
# ============================================================

def make_memory_tip(row):

    hanzi = clean(
        row.KyTu
    )

    meaning = first_meaning(
        row.NghiaTiengViet
    )

    radical = clean(
        row.BoThuKyHieu
    )

    radical_name = clean(
        row.TenBoThu
    )

    if (
        radical
        and radical_name
    ):

        return (
            f"Nhận diện bộ {radical} "
            f"({radical_name}) trong chữ {hanzi}; "
            f"sau đó liên hệ toàn chữ với nghĩa "
            f"“{meaning}” để ghi nhớ mặt chữ."
        )

    if radical:

        return (
            f"Nhận diện bộ {radical} "
            f"trong chữ {hanzi}; "
            f"liên hệ toàn chữ với nghĩa "
            f"“{meaning}” để ghi nhớ."
        )

    return (
        f"Ghi nhớ mặt chữ {hanzi} "
        f"bằng cách liên hệ với nghĩa "
        f"“{meaning}”."
    )


# ============================================================
# VÍ DỤ DỰ PHÒNG
#
# Chỉ dùng nếu không tìm được ví dụ từ TuVung.
# ============================================================

def make_fallback_example(row):

    hanzi = clean(
        row.KyTu
    )

    chinese = (
        f"这是“{hanzi}”字。"
    )

    vietnamese = (
        f"Đây là chữ “{hanzi}”."
    )

    return (
        chinese,
        vietnamese,
    )


# ============================================================
# TẠO BỘ DỮ LIỆU PREVIEW
# ============================================================

def build_content(
    cursor,
    course,
    hanzi_rows,
):

    result = []

    kept_examples = 0
    from_vocab = 0
    fallback = 0


    print()
    print(
        "[4] Tạo nội dung cho 301 chữ"
    )

    print("-" * 100)


    for index, row in enumerate(
        hanzi_rows,
        start=1,
    ):

        old_memory = clean(
            row.CachGhiNho
        )

        old_zh = clean(
            row.ViDuTiengTrung
        )

        old_py = clean(
            row.ViDuPinyin
        )

        old_vi = clean(
            row.ViDuTiengViet
        )


        # ====================================================
        # CÁCH GHI NHỚ
        # ====================================================

        if old_memory:

            new_memory = old_memory

        else:

            new_memory = make_memory_tip(
                row
            )


        # ====================================================
        # GIỮ NGUYÊN VÍ DỤ ĐÃ CÓ
        # ====================================================

        if (
            old_zh
            and old_py
            and old_vi
        ):

            new_zh = old_zh
            new_py = old_py
            new_vi = old_vi

            source_type = (
                "giu_nguyen_db"
            )

            kept_examples += 1


        else:

            # ================================================
            # TÌM VÍ DỤ TỪ TỪ VỰNG
            # ================================================

            candidate = find_vocab_example(
                cursor,
                course.MaKhoaHoc,
                row.SoThuTuBai,
                clean(row.KyTu),
            )


            if candidate is not None:

                new_zh = clean(
                    candidate.ViDuTiengTrung
                )

                new_vi = clean(
                    candidate.ViDuTiengViet
                )

                new_py = make_pinyin(
                    new_zh
                )

                source_type = (
                    "TuVung:"
                    + str(
                        candidate.MaTuVung
                    )
                )

                from_vocab += 1


            else:

                # ============================================
                # FALLBACK
                # ============================================

                (
                    new_zh,
                    new_vi,
                ) = make_fallback_example(
                    row
                )

                new_py = make_pinyin(
                    new_zh
                )

                source_type = (
                    "fallback"
                )

                fallback += 1


        # ====================================================
        # CHECK
        # ====================================================

        if not new_memory:

            raise RuntimeError(
                f"{row.KyTu}: "
                "thiếu CachGhiNho."
            )


        if not new_zh:

            raise RuntimeError(
                f"{row.KyTu}: "
                "thiếu ViDuTiengTrung."
            )


        if not new_py:

            raise RuntimeError(
                f"{row.KyTu}: "
                "thiếu ViDuPinyin."
            )


        if not new_vi:

            raise RuntimeError(
                f"{row.KyTu}: "
                "thiếu ViDuTiengViet."
            )


        result.append(
            {
                "SoThuTuBai":
                    row.SoThuTuBai,

                "MaBaiHoc":
                    row.MaBaiHoc,

                "ThuTu":
                    row.ThuTu,

                "MaChuHan":
                    row.MaChuHan,

                "KyTu":
                    clean(
                        row.KyTu
                    ),

                "Pinyin":
                    clean(
                        row.Pinyin
                    ),

                "NghiaTiengViet":
                    clean(
                        row.NghiaTiengViet
                    ),

                "MaBoThu":
                    row.MaBoThu,

                "BoThuKyHieu":
                    clean(
                        row.BoThuKyHieu
                    ),

                "TenBoThu":
                    clean(
                        row.TenBoThu
                    ),

                "SoNet":
                    row.SoNet,

                "CachGhiNho":
                    new_memory,

                "ViDuTiengTrung":
                    new_zh,

                "ViDuPinyin":
                    new_py,

                "ViDuTiengViet":
                    new_vi,

                "NguonViDu":
                    source_type,
            }
        )


        if (
            index % 50 == 0
            or index == len(hanzi_rows)
        ):

            print(
                f"Đã xử lý "
                f"{index}/{len(hanzi_rows)} chữ..."
            )


    print()
    print(
        "Giữ nguyên ví dụ cũ:",
        kept_examples,
    )

    print(
        "Lấy ví dụ từ TuVung:",
        from_vocab,
    )

    print(
        "Dùng fallback:",
        fallback,
    )


    if len(result) != EXPECTED_HANZI:

        raise RuntimeError(
            "Kết quả không đủ 301 chữ."
        )


    return result


# ============================================================
# XUẤT PREVIEW CSV
# ============================================================

def export_preview(rows):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    fields = [
        "SoThuTuBai",
        "MaBaiHoc",
        "ThuTu",
        "MaChuHan",
        "KyTu",
        "Pinyin",
        "NghiaTiengViet",
        "MaBoThu",
        "BoThuKyHieu",
        "TenBoThu",
        "SoNet",
        "CachGhiNho",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "NguonViDu",
    ]


    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    print()
    print(
        "[5] Đã tạo preview CSV"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# KIỂM TRA PREVIEW
# ============================================================

def validate_preview(rows):

    print()
    print(
        "[6] Kiểm tra preview"
    )

    ids = [
        row["MaChuHan"]
        for row in rows
    ]


    if len(ids) != EXPECTED_HANZI:

        raise RuntimeError(
            "Preview không đủ 301 dòng."
        )


    if len(ids) != len(set(ids)):

        raise RuntimeError(
            "MaChuHan bị trùng."
        )


    for row in rows:

        required = [
            "KyTu",
            "Pinyin",
            "NghiaTiengViet",
            "CachGhiNho",
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
        ]


        for field in required:

            if not clean(
                row[field]
            ):

                raise RuntimeError(
                    f"MaChuHan="
                    f"{row['MaChuHan']} "
                    f"thiếu {field}."
                )


    print(
        "Preview: OK"
    )

    print(
        "301/301 chữ có đủ "
        "nội dung cần nhập."
    )


# ============================================================
# UPDATE DATABASE
# ============================================================

def apply_database(
    conn,
    cursor,
    course,
    rows,
):

    print()
    print("=" * 100)
    print(
        "[7] UPDATE CHỮ HÁN HSK1"
    )
    print("=" * 100)


    updated = 0


    try:

        for index, row in enumerate(
            rows,
            start=1,
        ):

            cursor.execute(
                """
                UPDATE dbo.ChuHan

                SET

                    CachGhiNho =
                        CASE
                            WHEN CachGhiNho IS NULL
                              OR LTRIM(
                                    RTRIM(
                                        CachGhiNho
                                    )
                                 ) = ''
                            THEN ?
                            ELSE CachGhiNho
                        END,

                    ViDuTiengTrung =
                        CASE
                            WHEN ViDuTiengTrung IS NULL
                              OR LTRIM(
                                    RTRIM(
                                        ViDuTiengTrung
                                    )
                                 ) = ''
                            THEN ?
                            ELSE ViDuTiengTrung
                        END,

                    ViDuPinyin =
                        CASE
                            WHEN ViDuPinyin IS NULL
                              OR LTRIM(
                                    RTRIM(
                                        ViDuPinyin
                                    )
                                 ) = ''
                            THEN ?
                            ELSE ViDuPinyin
                        END,

                    ViDuTiengViet =
                        CASE
                            WHEN ViDuTiengViet IS NULL
                              OR LTRIM(
                                    RTRIM(
                                        ViDuTiengViet
                                    )
                                 ) = ''
                            THEN ?
                            ELSE ViDuTiengViet
                        END

                WHERE MaChuHan = ?
                  AND KyTu = ?
                """,

                row["CachGhiNho"],
                row["ViDuTiengTrung"],
                row["ViDuPinyin"],
                row["ViDuTiengViet"],

                row["MaChuHan"],
                row["KyTu"],
            )


            if cursor.rowcount != 1:

                raise RuntimeError(
                    "UPDATE không đúng 1 dòng: "
                    f"MaChuHan="
                    f"{row['MaChuHan']} "
                    f"{row['KyTu']}"
                )


            updated += 1


            if (
                index % 50 == 0
                or index == len(rows)
            ):

                print(
                    f"Đã UPDATE "
                    f"{index}/{len(rows)} chữ..."
                )


        # ====================================================
        # AUDIT TRƯỚC COMMIT
        # ====================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS TongChu,

                SUM(
                    CASE
                        WHEN
                            ch.CachGhiNho IS NULL
                            OR LTRIM(
                                RTRIM(
                                    ch.CachGhiNho
                                )
                            ) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuGhiNho,

                SUM(
                    CASE
                        WHEN
                            ch.ViDuTiengTrung IS NULL
                            OR LTRIM(
                                RTRIM(
                                    ch.ViDuTiengTrung
                                )
                            ) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuVDTrung,

                SUM(
                    CASE
                        WHEN
                            ch.ViDuPinyin IS NULL
                            OR LTRIM(
                                RTRIM(
                                    ch.ViDuPinyin
                                )
                            ) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuVDPinyin,

                SUM(
                    CASE
                        WHEN
                            ch.ViDuTiengViet IS NULL
                            OR LTRIM(
                                RTRIM(
                                    ch.ViDuTiengViet
                                )
                            ) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuVDViet,

                SUM(
                    CASE
                        WHEN ch.MaTep IS NULL
                        THEN 1
                        ELSE 0
                    END
                ) AS ChuaCoMedia

            FROM dbo.ChuHan ch

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc = ch.MaBaiHoc

            WHERE bh.MaKhoaHoc = ?
            """,
            course.MaKhoaHoc,
        )


        audit = cursor.fetchone()


        print()
        print("=" * 100)
        print(
            "AUDIT TRƯỚC COMMIT"
        )
        print("=" * 100)


        print(
            "Tổng chữ:",
            audit.TongChu,
        )

        print(
            "Thiếu cách ghi nhớ:",
            audit.ThieuGhiNho,
        )

        print(
            "Thiếu ví dụ Trung:",
            audit.ThieuVDTrung,
        )

        print(
            "Thiếu ví dụ Pinyin:",
            audit.ThieuVDPinyin,
        )

        print(
            "Thiếu ví dụ Việt:",
            audit.ThieuVDViet,
        )

        print(
            "Chưa có media:",
            audit.ChuaCoMedia,
        )


        if (
            audit.TongChu != EXPECTED_HANZI

            or audit.ThieuGhiNho != 0

            or audit.ThieuVDTrung != 0

            or audit.ThieuVDPinyin != 0

            or audit.ThieuVDViet != 0
        ):

            raise RuntimeError(
                "Audit chưa sạch. "
                "Không COMMIT."
            )


        conn.commit()


        print()
        print(
            "✅ 301/301 CHỮ HÁN "
            "ĐÃ ĐỦ NỘI DUNG HỌC."
        )

        print(
            "✅ COMMIT THÀNH CÔNG."
        )


    except Exception:

        conn.rollback()

        print()
        print(
            "❌ ĐÃ ROLLBACK."
        )

        print(
            "Database không giữ "
            "thay đổi của lần chạy lỗi."
        )

        raise


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser()


    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Thực sự UPDATE database. "
            "Không có --apply chỉ dry-run."
        ),
    )


    args = parser.parse_args()


    conn = None


    try:

        print("=" * 100)

        print(
            "10E - HOÀN THIỆN NỘI DUNG "
            "301 CHỮ HÁN HSK1"
        )

        print("=" * 100)


        # ====================================================
        # CONNECT
        # ====================================================

        print()
        print(
            "[1] Kết nối database"
        )


        conn = get_connection()

        conn.autocommit = False

        cursor = conn.cursor()


        print(
            "Kết nối database: OK"
        )


        # ====================================================
        # COURSE
        # ====================================================

        course = get_course(
            cursor
        )


        print()
        print(
            "[2] Khóa:",
            course.MaKyHieu
        )


        # ====================================================
        # LOAD HANZI
        # ====================================================

        hanzi_rows = load_hanzi(
            cursor,
            course.MaKhoaHoc,
        )


        print()
        print(
            "[3] Tổng chữ Hán:",
            len(hanzi_rows),
        )


        # ====================================================
        # BUILD
        # ====================================================

        preview_rows = build_content(
            cursor,
            course,
            hanzi_rows,
        )


        # ====================================================
        # EXPORT
        # ====================================================

        export_preview(
            preview_rows
        )


        # ====================================================
        # VALIDATE
        # ====================================================

        validate_preview(
            preview_rows
        )


        # ====================================================
        # DRY RUN
        # ====================================================

        if not args.apply:

            conn.rollback()

            print()
            print("=" * 100)

            print(
                "✅ DRY-RUN THÀNH CÔNG"
            )

            print("=" * 100)


            print(
                "301 chữ đã được chuẩn bị."
            )

            print(
                "DATABASE CHƯA BỊ SỬA."
            )

            print()
            print(
                "Preview:"
            )

            print(
                OUTPUT_FILE
            )

            print()
            print(
                "Nếu kết quả sạch, "
                "chạy lại với --apply."
            )

            return


        # ====================================================
        # APPLY
        # ====================================================

        apply_database(
            conn,
            cursor,
            course,
            preview_rows,
        )


    except Exception as error:

        if conn is not None:

            try:
                conn.rollback()

            except Exception:
                pass


        print()
        print("=" * 100)
        print("❌ CÓ LỖI")
        print("=" * 100)

        print(error)


    finally:

        if conn is not None:
            conn.close()


        print()
        print(
            "Đã đóng kết nối database."
        )


if __name__ == "__main__":
    main()