from pathlib import Path
import csv
import sys


# ============================================================
# ROOT PROJECT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# ============================================================
# CẤU HÌNH
# ============================================================

COURSE_CODE = "HSK1-CORE"

OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "hsk1_hanzi_missing.csv"
)

EXPECTED_LESSONS = 23
EXPECTED_HANZI = 301


# ============================================================
# HELPER
# ============================================================

def clean(value):

    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# TÌM KHÓA HSK1
# ============================================================

def get_course(cursor):

    cursor.execute(
        """
        SELECT
            MaKhoaHoc,
            MaKyHieu,
            TieuDe,
            TrangThai

        FROM dbo.KhoaHoc

        WHERE MaKyHieu = ?
        """,
        COURSE_CODE,
    )

    rows = cursor.fetchall()

    if len(rows) != 1:

        raise RuntimeError(
            f"Không tìm thấy duy nhất khóa {COURSE_CODE}. "
            f"Số bản ghi: {len(rows)}"
        )

    return rows[0]


# ============================================================
# KIỂM TRA 23 BÀI
# ============================================================

def check_lessons(
    cursor,
    ma_khoa_hoc,
):

    cursor.execute(
        """
        SELECT
            MaBaiHoc,
            SoThuTuBai,
            TieuDe

        FROM dbo.BaiHoc

        WHERE MaKhoaHoc = ?

        ORDER BY SoThuTuBai
        """,
        ma_khoa_hoc,
    )

    rows = cursor.fetchall()

    if len(rows) != EXPECTED_LESSONS:

        raise RuntimeError(
            f"HSK1 phải có {EXPECTED_LESSONS} bài. "
            f"Thực tế: {len(rows)}"
        )

    orders = [
        row.SoThuTuBai
        for row in rows
    ]

    if orders != list(
        range(
            1,
            EXPECTED_LESSONS + 1,
        )
    ):

        raise RuntimeError(
            "SoThuTuBai không liên tục 1 -> 23."
        )

    return rows


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
            bh.TieuDe,

            ch.ThuTu,
            ch.MaChuHan,
            ch.KyTu,
            ch.Pinyin,
            ch.NghiaTiengViet,

            ch.MaBoThu,

            bt.KyHieu
                AS BoThuKyHieu,

            bt.TenBoThu
                AS TenBoThu,

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
            f"HSK1 phải có {EXPECTED_HANZI} chữ Hán. "
            f"Thực tế: {len(rows)}"
        )

    return rows


# ============================================================
# THỐNG KÊ THEO TỪNG BÀI
# ============================================================

def audit_by_lesson(rows):

    print()
    print("=" * 120)
    print("AUDIT CHỮ HÁN THEO TỪNG BÀI")
    print("=" * 120)

    stats = {}

    for row in rows:

        lesson = row.SoThuTuBai

        if lesson not in stats:

            stats[lesson] = {
                "tong": 0,
                "pinyin": 0,
                "nghia": 0,
                "buthu": 0,
                "sonet": 0,
                "ghinho": 0,
                "vd_trung": 0,
                "vd_pinyin": 0,
                "vd_viet": 0,
                "nguon": 0,
                "media": 0,
            }

        s = stats[lesson]

        s["tong"] += 1

        if not clean(row.Pinyin):
            s["pinyin"] += 1

        if not clean(
            row.NghiaTiengViet
        ):
            s["nghia"] += 1

        if row.MaBoThu is None:
            s["buthu"] += 1

        if (
            row.SoNet is None
            or row.SoNet <= 0
        ):
            s["sonet"] += 1

        if not clean(
            row.CachGhiNho
        ):
            s["ghinho"] += 1

        if not clean(
            row.ViDuTiengTrung
        ):
            s["vd_trung"] += 1

        if not clean(
            row.ViDuPinyin
        ):
            s["vd_pinyin"] += 1

        if not clean(
            row.ViDuTiengViet
        ):
            s["vd_viet"] += 1

        if row.MaNguon is None:
            s["nguon"] += 1

        if row.MaTep is None:
            s["media"] += 1


    for lesson in range(
        1,
        EXPECTED_LESSONS + 1,
    ):

        s = stats[lesson]

        print(
            f"Bài {lesson:>2} | "
            f"Tổng={s['tong']:>2} | "
            f"Gợi nhớ={s['ghinho']:>2} | "
            f"VD Trung={s['vd_trung']:>2} | "
            f"VD Pinyin={s['vd_pinyin']:>2} | "
            f"VD Việt={s['vd_viet']:>2} | "
            f"Media={s['media']:>2}"
        )

    return stats


# ============================================================
# KIỂM TRA NÉT CHỮ
# ============================================================

def audit_strokes(
    cursor,
    ma_khoa_hoc,
):

    print()
    print("=" * 120)
    print("KIỂM TRA NETCHUHAN")
    print("=" * 120)

    cursor.execute(
        """
        SELECT
            bh.SoThuTuBai,
            ch.ThuTu,
            ch.MaChuHan,
            ch.KyTu,
            ch.SoNet,

            COUNT(nch.MaNetChuHan)
                AS SoNetTrongBang

        FROM dbo.ChuHan ch

        INNER JOIN dbo.BaiHoc bh
            ON bh.MaBaiHoc = ch.MaBaiHoc

        LEFT JOIN dbo.NetChuHan nch
            ON nch.MaChuHan = ch.MaChuHan

        WHERE bh.MaKhoaHoc = ?

        GROUP BY
            bh.SoThuTuBai,
            ch.ThuTu,
            ch.MaChuHan,
            ch.KyTu,
            ch.SoNet

        HAVING
            COUNT(nch.MaNetChuHan)
            <> ISNULL(
                ch.SoNet,
                0
            )

        ORDER BY
            bh.SoThuTuBai,
            ch.ThuTu
        """,
        ma_khoa_hoc,
    )

    rows = cursor.fetchall()

    print(
        "Số chữ bị lệch số nét:",
        len(rows),
    )

    for row in rows:

        print(
            f"Bài {row.SoThuTuBai:>2} | "
            f"{row.KyTu} | "
            f"Khai báo={row.SoNet} | "
            f"Trong NetChuHan="
            f"{row.SoNetTrongBang}"
        )

    return rows


# ============================================================
# TỔNG AUDIT
# ============================================================

def print_total(rows):

    counters = {
        "pinyin": 0,
        "nghia": 0,
        "buthu": 0,
        "sonet": 0,
        "ghinho": 0,
        "vd_trung": 0,
        "vd_pinyin": 0,
        "vd_viet": 0,
        "nguon": 0,
        "media": 0,
    }

    for row in rows:

        if not clean(row.Pinyin):
            counters["pinyin"] += 1

        if not clean(
            row.NghiaTiengViet
        ):
            counters["nghia"] += 1

        if row.MaBoThu is None:
            counters["buthu"] += 1

        if (
            row.SoNet is None
            or row.SoNet <= 0
        ):
            counters["sonet"] += 1

        if not clean(
            row.CachGhiNho
        ):
            counters["ghinho"] += 1

        if not clean(
            row.ViDuTiengTrung
        ):
            counters["vd_trung"] += 1

        if not clean(
            row.ViDuPinyin
        ):
            counters["vd_pinyin"] += 1

        if not clean(
            row.ViDuTiengViet
        ):
            counters["vd_viet"] += 1

        if row.MaNguon is None:
            counters["nguon"] += 1

        if row.MaTep is None:
            counters["media"] += 1


    print()
    print("=" * 120)
    print("TỔNG KẾT CHỮ HÁN HSK1")
    print("=" * 120)

    print(
        "Tổng chữ Hán:",
        len(rows),
    )

    print(
        "Thiếu Pinyin:",
        counters["pinyin"],
    )

    print(
        "Thiếu nghĩa:",
        counters["nghia"],
    )

    print(
        "Thiếu bộ thủ:",
        counters["buthu"],
    )

    print(
        "Thiếu số nét:",
        counters["sonet"],
    )

    print(
        "Thiếu cách ghi nhớ:",
        counters["ghinho"],
    )

    print(
        "Thiếu ví dụ Trung:",
        counters["vd_trung"],
    )

    print(
        "Thiếu ví dụ Pinyin:",
        counters["vd_pinyin"],
    )

    print(
        "Thiếu ví dụ Việt:",
        counters["vd_viet"],
    )

    print(
        "Thiếu nguồn:",
        counters["nguon"],
    )

    print(
        "Chưa có media:",
        counters["media"],
    )

    return counters


# ============================================================
# XUẤT CÁC CHỮ ĐANG THIẾU
# ============================================================

def export_missing(rows):

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
        "MaNguon",
        "TrangThai",
    ]


    missing_rows = []


    for row in rows:

        if (
            not clean(
                row.CachGhiNho
            )

            or not clean(
                row.ViDuTiengTrung
            )

            or not clean(
                row.ViDuPinyin
            )

            or not clean(
                row.ViDuTiengViet
            )
        ):

            missing_rows.append(
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
                        clean(row.KyTu),

                    "Pinyin":
                        clean(row.Pinyin),

                    "NghiaTiengViet":
                        clean(
                            row.NghiaTiengViet
                        ),

                    "MaBoThu":
                        (
                            row.MaBoThu
                            if row.MaBoThu
                            is not None
                            else ""
                        ),

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
                        clean(
                            row.CachGhiNho
                        ),

                    "ViDuTiengTrung":
                        clean(
                            row.ViDuTiengTrung
                        ),

                    "ViDuPinyin":
                        clean(
                            row.ViDuPinyin
                        ),

                    "ViDuTiengViet":
                        clean(
                            row.ViDuTiengViet
                        ),

                    "MaNguon":
                        (
                            row.MaNguon
                            if row.MaNguon
                            is not None
                            else ""
                        ),

                    "TrangThai":
                        clean(
                            row.TrangThai
                        ),
                }
            )


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
            missing_rows
        )


    print()
    print("=" * 120)
    print("FILE CÁC CHỮ CẦN BỔ SUNG")
    print("=" * 120)

    print(
        "Số dòng cần bổ sung:",
        len(missing_rows),
    )

    print(
        "File:",
        OUTPUT_FILE,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    conn = None


    try:

        print("=" * 120)
        print(
            "10D - AUDIT TOÀN BỘ CHỮ HÁN HSK1"
        )
        print("=" * 120)

        print()
        print(
            "CHẾ ĐỘ: CHỈ SELECT + XUẤT CSV"
        )

        print(
            "KHÔNG INSERT / UPDATE / DELETE"
        )


        # ----------------------------------------------------
        # 1. CONNECT
        # ----------------------------------------------------

        print()
        print(
            "[1] Kết nối database"
        )


        conn = get_connection()

        cursor = conn.cursor()


        print(
            "Kết nối database: OK"
        )


        # ----------------------------------------------------
        # 2. COURSE
        # ----------------------------------------------------

        course = get_course(
            cursor
        )


        print()
        print(
            "[2] Khóa:",
            course.MaKyHieu,
        )

        print(
            "TieuDe:",
            course.TieuDe,
        )


        # ----------------------------------------------------
        # 3. LESSONS
        # ----------------------------------------------------

        lessons = check_lessons(
            cursor,
            course.MaKhoaHoc,
        )


        print()
        print(
            "[3] Số bài:",
            len(lessons),
        )


        # ----------------------------------------------------
        # 4. HANZI
        # ----------------------------------------------------

        rows = load_hanzi(
            cursor,
            course.MaKhoaHoc,
        )


        print(
            "Số chữ Hán:",
            len(rows),
        )


        # ----------------------------------------------------
        # 5. AUDIT
        # ----------------------------------------------------

        audit_by_lesson(
            rows
        )


        counters = print_total(
            rows
        )


        # ----------------------------------------------------
        # 6. STROKES
        # ----------------------------------------------------

        stroke_errors = audit_strokes(
            cursor,
            course.MaKhoaHoc,
        )


        # ----------------------------------------------------
        # 7. EXPORT
        # ----------------------------------------------------

        export_missing(
            rows
        )


        # ----------------------------------------------------
        # 8. KẾT LUẬN
        # ----------------------------------------------------

        print()
        print("=" * 120)
        print("KẾT LUẬN")
        print("=" * 120)

        if (
            counters["pinyin"] == 0
            and counters["nghia"] == 0
            and counters["buthu"] == 0
            and counters["sonet"] == 0
            and counters["nguon"] == 0
            and len(stroke_errors) == 0
        ):

            print(
                "✅ Dữ liệu cấu trúc Chữ Hán cơ bản: SẠCH."
            )

        else:

            print(
                "⚠️ Có lỗi cấu trúc Chữ Hán cần kiểm tra."
            )


        if (
            counters["ghinho"] > 0
            or counters["vd_trung"] > 0
            or counters["vd_pinyin"] > 0
            or counters["vd_viet"] > 0
        ):

            print(
                "⚠️ Chữ Hán còn thiếu nội dung học."
            )

        else:

            print(
                "✅ Nội dung học Chữ Hán đã đầy đủ."
            )


        print()
        print(
            "DATABASE KHÔNG BỊ SỬA."
        )


    except Exception as error:

        print()
        print("=" * 120)
        print("❌ CÓ LỖI")
        print("=" * 120)

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