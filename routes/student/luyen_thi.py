
# -*- coding: utf-8 -*-
"""
MỘC HÁN - LUYỆN THI HSK (STUDENT)

Chức năng hiện tại:
1. Hiển thị trang Luyện thi riêng.
2. Lấy danh sách cấp độ HSK1-HSK4.
3. Lấy danh sách đề đã xuất bản từ SQL Server.
4. Đọc câu hỏi và MP3 của đề thi.
5. Tạo lựa chọn phù hợp với các dạng câu HSK1.
6. Cho Admin xem trước đề nháp.

Chưa triển khai:
- Bắt đầu lần thi.
- Nộp bài và chấm điểm.
- Lưu lịch sử làm bài.
- Duyệt và xuất bản đề.

Lưu ý:
- Không trả đáp án đúng trước khi nộp bài.
- Không chia MP3 thành từng câu.
- Không thay đổi dữ liệu Bài tập hiện tại.
"""

import json
from contextlib import closing

from flask import (
    Blueprint,
    abort,
    g,
    jsonify,
    render_template,
    request,
    session,
)

from database import get_connection


# ==================================================
# 1. KHỞI TẠO BLUEPRINT
# ==================================================

student_luyen_thi_bp = Blueprint(
    "student_luyen_thi",
    __name__,
    url_prefix="/student/luyen-thi",
)


# ==================================================
# 2. KIỂM TRA QUYỀN TRUY CẬP
# ==================================================

def require_role(role):
    """
    Kiểm tra tài khoản đang đăng nhập.

    Giữ cách kiểm tra g.account của module hiện tại.
    """

    account = getattr(g, "account", None)

    if not account:
        abort(401)

    if account.get("role") != role:
        abort(403)


# ==================================================
# 3. CHUYỂN DỮ LIỆU SQL THÀNH DICTIONARY
# ==================================================

def fetch_dicts(cursor):
    """
    Chuyển các dòng SQL thành danh sách dictionary.
    """

    if cursor.description is None:
        return []

    columns = [
        col[0]
        for col in cursor.description
    ]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# ==================================================
# 4. TẠO LỰA CHỌN CHO CÂU HỎI
# ==================================================

def get_options(question_type, raw_options, level):
    """
    Tạo các lựa chọn để người học chọn đáp án.

    HSK1 - H10000:
    - Đúng/Sai: √ / ×
    - Trắc nghiệm: A/B/C
    - Ghép hình, ghép cặp: A-F

    Các đề sau ưu tiên dùng LuaChonJson từ SQL.
    """

    # ----------------------------------------------
    # 4.1. CÂU HỎI ĐÚNG / SAI
    # ----------------------------------------------

    if question_type == "dung_sai":
        return [
            {
                "ma": "√",
                "nhan": "Đúng",
            },
            {
                "ma": "×",
                "nhan": "Sai",
            },
        ]

    # ----------------------------------------------
    # 4.2. LỰA CHỌN ĐƯỢC LƯU TRONG SQL
    # ----------------------------------------------

    if raw_options:

        try:
            parsed = json.loads(raw_options)

        except (TypeError, ValueError):
            parsed = None

        if isinstance(parsed, list):

            cleaned = []

            for item in parsed:

                if not isinstance(item, dict):
                    continue

                code = (
                    item.get("ma")
                    or item.get("value")
                )

                label = (
                    item.get("nhan")
                    or item.get("label")
                    or code
                )

                if code is None:
                    continue

                cleaned.append({
                    "ma": str(code),
                    "nhan": str(label),
                })

            if cleaned:
                return cleaned

    # ----------------------------------------------
    # 4.3. LỰA CHỌN CỦA ĐỀ HSK1 - H10000
    # ----------------------------------------------

    if level == 1:

        if question_type == "chon_mot":
            labels = "ABC"

        elif question_type in (
            "ghep_hinh_theo_audio",
            "ghep_hinh_theo_noi_dung",
            "ghep_cap",
        ):
            labels = "ABCDEF"

        else:
            labels = ""

        return [
            {
                "ma": value,
                "nhan": value,
            }
            for value in labels
        ]

    # Các cấp HSK khác sẽ dùng lựa chọn
    # được chuẩn hóa theo từng đề.
    return []


# ==================================================
# 5. TRANG LUYỆN THI - NGƯỜI HỌC
# ==================================================

@student_luyen_thi_bp.get("/")
def trang_luyen_thi():
    """
    Trang chính của Luyện thi.

    URL:
        /student/luyen-thi/

    Chọn HSK1:
        /student/luyen-thi/?hsk=1

    Chọn HSK2:
        /student/luyen-thi/?hsk=2
    """

    require_role("student")

    hsk = request.args.get(
        "hsk",
        type=int
    )

    # Chỉ cho phép HSK1 đến HSK4.
    if (
        hsk is not None
        and hsk not in (1, 2, 3, 4)
    ):
        abort(404)

    with closing(get_connection()) as conn:

        cursor = conn.cursor()

        # ------------------------------------------
        # 5.1. LẤY CẤP ĐỘ HSK
        # ------------------------------------------

        cursor.execute("""
            SELECT
                h.MaCapDo,
                h.MaKyHieu,
                h.TieuDe,

                COUNT(d.MaDeThi) AS SoDeDaXuatBan

            FROM dbo.CapDoHSK AS h

            LEFT JOIN dbo.DeThiHSK AS d
                ON d.MaCapDo = h.MaCapDo
               AND d.TrangThai = 'da_xuat_ban'

            WHERE h.MaCapDo BETWEEN 1 AND 4

            GROUP BY
                h.MaCapDo,
                h.MaKyHieu,
                h.TieuDe

            ORDER BY h.MaCapDo
        """)

        cap_do = fetch_dicts(cursor)

        # ------------------------------------------
        # 5.2. DANH SÁCH ĐỀ THEO HSK
        # ------------------------------------------

        danh_sach_de = []

        if hsk is not None:

            cursor.execute("""
                SELECT
                    MaDeThi,
                    MaDeGoc,
                    TenDe,
                    ThuTu,

                    TongSoCau,
                    SoCauNghe,
                    SoCauDoc,
                    SoCauViet,

                    ThoiGianPhut

                FROM dbo.DeThiHSK

                WHERE MaCapDo = ?
                  AND TrangThai = 'da_xuat_ban'

                ORDER BY ThuTu
            """, hsk)

            danh_sach_de = fetch_dicts(cursor)

    # ----------------------------------------------
    # 5.3. HIỂN THỊ HTML RIÊNG
    # ----------------------------------------------

    return render_template(
        "student/luyenthi.html",

        cap_do=cap_do,

        hsk_dang_chon=hsk,

        danh_sach_de=danh_sach_de,
    )


# ==================================================
# 6. API DANH SÁCH CẤP ĐỘ HSK
# ==================================================

@student_luyen_thi_bp.get("/api/cap-do")
def api_cap_do():
    """
    Trả về danh sách HSK1-HSK4
    và số đề đã xuất bản.
    """

    require_role("student")

    with closing(get_connection()) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                h.MaCapDo,
                h.MaKyHieu,
                h.TieuDe,

                COUNT(d.MaDeThi) AS SoDeDaXuatBan

            FROM dbo.CapDoHSK AS h

            LEFT JOIN dbo.DeThiHSK AS d
                ON d.MaCapDo = h.MaCapDo
               AND d.TrangThai = 'da_xuat_ban'

            WHERE h.MaCapDo BETWEEN 1 AND 4

            GROUP BY
                h.MaCapDo,
                h.MaKyHieu,
                h.TieuDe

            ORDER BY h.MaCapDo
        """)

        levels = fetch_dicts(cursor)

    return jsonify({
        "cap_do": levels,
    })


# ==================================================
# 7. API DANH SÁCH ĐỀ THEO CẤP HSK
# ==================================================

@student_luyen_thi_bp.get("/api/de")
def api_danh_sach_de():
    """
    Ví dụ:
        /student/luyen-thi/api/de?hsk=1
    """

    require_role("student")

    level = request.args.get(
        "hsk",
        type=int
    )

    if level not in (1, 2, 3, 4):

        return jsonify({
            "loi": "Cấp HSK phải từ 1 đến 4."
        }), 400

    with closing(get_connection()) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                MaDeThi,
                MaDeGoc,
                TenDe,
                ThuTu,

                TongSoCau,
                SoCauNghe,
                SoCauDoc,
                SoCauViet,

                ThoiGianPhut

            FROM dbo.DeThiHSK

            WHERE MaCapDo = ?
              AND TrangThai = 'da_xuat_ban'

            ORDER BY ThuTu
        """, level)

        exams = fetch_dicts(cursor)

    return jsonify({
        "cap_hsk": level,
        "de_thi": exams,
    })


# ==================================================
# 8. ĐỌC CHI TIẾT MỘT ĐỀ THI
# ==================================================

def load_exam(ma_de, admin_preview=False):
    """
    Đọc thông tin đề từ SQL Server.

    Không lấy DapAnDung.

    admin_preview=True:
        Cho Admin kiểm tra đề nháp.

    admin_preview=False:
        Chỉ cho Người học xem đề đã xuất bản.
    """

    with closing(get_connection()) as conn:

        cursor = conn.cursor()

        # ------------------------------------------
        # 8.1. THÔNG TIN ĐỀ THI VÀ MP3
        # ------------------------------------------

        cursor.execute("""
            SELECT
                d.MaDeThi,
                d.MaCapDo,
                d.MaDeGoc,
                d.TenDe,
                d.ThuTu,

                d.TongSoCau,
                d.SoCauNghe,
                d.SoCauDoc,
                d.SoCauViet,

                d.ThoiGianPhut,
                d.ThoiLuongAudioGiay,

                d.TrangThai,

                t.DuongDanTep AS AudioUrl

            FROM dbo.DeThiHSK AS d

            LEFT JOIN dbo.TepDaPhuongTien AS t
                ON t.MaTep = d.MaTepAudio

            WHERE d.MaDeThi = ?
        """, ma_de)

        row = cursor.fetchone()

        if row is None:
            abort(404)

        columns = [
            col[0]
            for col in cursor.description
        ]

        exam = dict(zip(columns, row))

        # Người học chỉ xem được đề đã xuất bản.
        if (
            not admin_preview
            and exam["TrangThai"] != "da_xuat_ban"
        ):
            abort(404)

        # ------------------------------------------
        # 8.2. ĐỌC CÂU HỎI
        # ------------------------------------------

        # Không SELECT DapAnDung,
        # tránh lộ đáp án trước khi nộp bài.

        cursor.execute("""
            SELECT
                SoCau,
                KyNang,
                Phan,
                LoaiCauHoi,

                NoiDung,

                AnhCauHoi,
                AnhNhomLuaChon,

                LuaChonJson

            FROM dbo.CauHoiThiHSK

            WHERE MaDeThi = ?

            ORDER BY SoCau
        """, ma_de)

        questions = fetch_dicts(cursor)

    # ----------------------------------------------
    # 8.3. CHUẨN HÓA DỮ LIỆU CHO GIAO DIỆN
    # ----------------------------------------------

    level = exam["MaCapDo"]

    for question in questions:

        raw_options = question.pop(
            "LuaChonJson",
            None
        )

        question["lua_chon"] = get_options(
            question["LoaiCauHoi"],
            raw_options,
            level,
        )

    # Decimal không có JSON encoder mặc định
    # trong mọi môi trường, nên chuyển rõ ràng.
    duration = exam.get(
        "ThoiLuongAudioGiay"
    )

    if duration is not None:
        exam["ThoiLuongAudioGiay"] = float(
            duration
        )

    return jsonify({
        "de_thi": exam,
        "cau_hoi": questions,
    })


# ==================================================
# 9. API CHI TIẾT ĐỀ - NGƯỜI HỌC
# ==================================================

@student_luyen_thi_bp.get(
    "/api/de/<int:ma_de>"
)
def api_chi_tiet_de(ma_de):

    require_role("student")

    return load_exam(ma_de)


# ==================================================
# 10. API XEM TRƯỚC ĐỀ - ADMIN
# ==================================================

@student_luyen_thi_bp.get(
    "/api/xem-truoc/<int:ma_de>"
)
def api_admin_xem_truoc(ma_de):

    require_role("admin")

    # Admin có thể xem đề ban_nhap,
    # nhưng vẫn không trả đáp án đúng.

    return load_exam(
        ma_de,
        admin_preview=True,
    )


# ==================================================
# 11. TRANG DANH SÁCH ĐỀ THI THEO CẤP HSK
# ==================================================

@student_luyen_thi_bp.get("/hsk/<int:ma_cap_do>")
def trang_danh_sach_de(ma_cap_do):
    """
    Hiển thị danh sách đề HSK1-HSK4.

    Trạng thái:
    - Đã làm: đã có lần thi được chấm.
    - Chưa làm: chưa có lần thi được chấm.

    Lịch sử chỉ tính cho người học đang đăng nhập.
    """

    require_role("student")

    if ma_cap_do not in (1, 2, 3, 4):
        abort(404)

    try:
        uid = int(session["account_id"])
    except (KeyError, TypeError, ValueError):
        abort(401)

    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                d.MaDeThi,
                d.MaDeGoc,
                d.TenDe,
                d.ThuTu,
                d.TongSoCau,
                d.SoCauNghe,
                d.SoCauDoc,
                d.SoCauViet,
                d.ThoiGianPhut,

                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM dbo.LanThiHSK AS l
                        WHERE l.MaDeThi = d.MaDeThi
                          AND l.MaNguoiDung = ?
                          AND l.TrangThai = 'da_cham'
                    )
                    THEN 1
                    ELSE 0
                END AS DaLam

            FROM dbo.DeThiHSK AS d

            WHERE d.MaCapDo = ?
              AND d.TrangThai = 'da_xuat_ban'

            ORDER BY d.ThuTu
            """,
            uid,
            ma_cap_do,
        )

        danh_sach_de = fetch_dicts(cursor)

    return render_template(
        "student/luyen_thi_de_list.html",
        cap_hsk=ma_cap_do,
        danh_sach_de=danh_sach_de,
    )

# ==========================================================
# TRANG CHI TIẾT ĐỀ THI HSK - STUDENT
# ==========================================================

@student_luyen_thi_bp.get("/de/<int:ma_de>")
def trang_chi_tiet_de(ma_de):
    """
    Hiển thị màn hình chọn phần thi:
    - Cả đề
    - Nghe hiểu
    - Đọc hiểu
    - Viết (nếu có)

    Chỉ cho phép xem đề đã xuất bản.
    Không trả đáp án đúng cho người học.
    """

    # Kiểm tra quyền người học
    require_role("student")

    # Lấy thông tin đề từ SQL Server
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                MaDeThi,
                MaCapDo,
                MaDeGoc,
                TenDe,
                ThuTu,
                TongSoCau,
                SoCauNghe,
                SoCauDoc,
                SoCauViet,
                ThoiGianPhut

            FROM dbo.DeThiHSK

            WHERE MaDeThi = ?
              AND TrangThai = 'da_xuat_ban'
            """,
            (ma_de,)
        )

        danh_sach = fetch_dicts(cursor)

    # Không tìm thấy đề hoặc đề chưa xuất bản
    if not danh_sach:
        abort(404)

    de = danh_sach[0]

    # Hiển thị màn hình 3
    return render_template(
        "student/luyen_thi_de_detail.html",
        de=de,
        cap_hsk=de["MaCapDo"]
    )

# ==================================================
# 12. ĐĂNG KÝ CHỨC NĂNG LÀM BÀI HSK
# ==================================================

# Import ở cuối file để giữ nguyên Blueprint
# và tất cả các route đã đăng ký phía trên.
from . import luyen_thi_lam_bai  # noqa: F401
