
# -*- coding: utf-8 -*-
"""
MỘC HÁN - ADMIN QUẢN LÝ LUYỆN THI HSK

Chức năng:
1. Xem danh sách đề thi HSK.
2. Kiểm tra câu hỏi, hình ảnh và đáp án.
3. Duyệt hoặc bỏ duyệt từng câu hỏi.
4. Xuất bản đề khi toàn bộ câu hỏi đã duyệt.

Không tạo bảng SQL mới.
Không ảnh hưởng dữ liệu Bài tập cũ.
"""

from contextlib import closing

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from database import get_connection


# ==================================================
# 1. BLUEPRINT ADMIN
# ==================================================

admin_luyen_thi_bp = Blueprint(
    "admin_luyen_thi",
    __name__,
    url_prefix="/admin/luyen-thi",
)


# ==================================================
# 2. KIỂM TRA QUYỀN ADMIN
# ==================================================

def require_admin():

    if not session.get("account_id"):
        abort(401)

    role = str(
        session.get("role") or ""
    ).strip().lower()

    if role != "admin":
        abort(403)


# ==================================================
# 3. HÀM ĐỌC KẾT QUẢ SQL
# ==================================================

def fetch_dicts(cursor):

    columns = [
        column[0]
        for column in cursor.description
    ]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_exam(cursor, ma_de, lock=False):

    lock_hint = (
        "WITH (UPDLOCK, HOLDLOCK)"
        if lock else ""
    )

    cursor.execute(f"""
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
            d.TrangThai,
            d.MaTepAudio,
            t.DuongDanTep AS AudioUrl

        FROM dbo.DeThiHSK AS d {lock_hint}

        LEFT JOIN dbo.TepDaPhuongTien AS t
            ON t.MaTep = d.MaTepAudio

        WHERE d.MaDeThi = ?
    """, ma_de)

    row = cursor.fetchone()

    if row is None:
        abort(404)

    columns = [
        column[0]
        for column in cursor.description
    ]

    return dict(zip(columns, row))


# ==================================================
# 4. TRANG DANH SÁCH ĐỀ THI
# ==================================================

@admin_luyen_thi_bp.get("/")
def danh_sach():

    require_admin()

    with closing(get_connection()) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                d.MaDeThi,
                d.MaCapDo,
                d.MaDeGoc,
                d.TenDe,
                d.ThuTu,
                d.TrangThai,
                d.TongSoCau,

                COUNT(c.MaCauHoiThi)
                    AS SoCauDaNhap,

                SUM(
                    CASE
                        WHEN c.DaDuyet = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS SoCauDaDuyet

            FROM dbo.DeThiHSK AS d

            LEFT JOIN dbo.CauHoiThiHSK AS c
                ON c.MaDeThi = d.MaDeThi

            GROUP BY
                d.MaDeThi,
                d.MaCapDo,
                d.MaDeGoc,
                d.TenDe,
                d.ThuTu,
                d.TrangThai,
                d.TongSoCau

            ORDER BY
                d.MaCapDo,
                d.ThuTu
        """)

        danh_sach_de = fetch_dicts(cursor)

    return render_template(
        "admin/luyen_thi_kiem_duyet.html",
        danh_sach_de=danh_sach_de,
        de=None,
        cau_hoi=[],
    )


# ==================================================
# 5. XEM CHI TIẾT ĐỀ THI
# ==================================================

@admin_luyen_thi_bp.get("/<int:ma_de>")
def chi_tiet(ma_de):

    require_admin()

    with closing(get_connection()) as conn:

        cursor = conn.cursor()

        de = get_exam(
            cursor,
            ma_de
        )

        # Admin được xem đáp án để kiểm tra.
        cursor.execute("""
            SELECT
                MaCauHoiThi,
                SoCau,
                KyNang,
                Phan,
                LoaiCauHoi,
                NoiDung,
                AnhCauHoi,
                AnhNhomLuaChon,
                LuaChonJson,
                DapAnDung,
                DaDuyet

            FROM dbo.CauHoiThiHSK

            WHERE MaDeThi = ?

            ORDER BY SoCau
        """, ma_de)

        cau_hoi = fetch_dicts(cursor)

    return render_template(
        "admin/luyen_thi_kiem_duyet.html",
        danh_sach_de=None,
        de=de,
        cau_hoi=cau_hoi,
    )


# ==================================================
# 6. DUYỆT / BỎ DUYỆT MỘT CÂU HỎI
# ==================================================

@admin_luyen_thi_bp.post(
    "/<int:ma_de>/cau/<int:ma_cau>/duyet"
)
def duyet_cau(ma_de, ma_cau):

    require_admin()

    thao_tac = request.form.get(
        "thao_tac"
    )

    if thao_tac not in (
        "duyet",
        "bo_duyet"
    ):
        abort(400)

    with closing(get_connection()) as conn:

        try:
            cursor = conn.cursor()

            de = get_exam(
                cursor,
                ma_de,
                lock=True
            )

            # Không thay đổi câu hỏi của đề
            # đã được xuất bản.
            if de["TrangThai"] not in (
                "ban_nhap",
                "cho_duyet",
            ):
                abort(
                    409,
                    description=(
                        "Chỉ được duyệt câu hỏi "
                        "của đề chưa xuất bản."
                    )
                )

            da_duyet = (
                1 if thao_tac == "duyet"
                else 0
            )

            cursor.execute("""
                UPDATE dbo.CauHoiThiHSK

                SET DaDuyet = ?

                WHERE MaDeThi = ?
                  AND MaCauHoiThi = ?
            """,
                da_duyet,
                ma_de,
                ma_cau
            )

            if cursor.rowcount != 1:
                conn.rollback()
                abort(404)

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    flash(
        "Đã cập nhật trạng thái duyệt câu hỏi.",
        "success"
    )

    return redirect(
        url_for(
            "admin_luyen_thi.chi_tiet",
            ma_de=ma_de
        ) + f"#cau-{ma_cau}"
    )


# ==================================================
# DUYỆT TẤT CẢ CÂU HỎI CỦA MỘT ĐỀ HSK
# ==================================================

@admin_luyen_thi_bp.post(
    "/<int:ma_de>/duyet-tat-ca"
)
def duyet_tat_ca(ma_de):
    """
    Duyệt hàng loạt các câu chưa duyệt.

    - Chỉ Admin được thao tác.
    - Chỉ áp dụng với đề chưa xuất bản.
    - Kiểm tra dữ liệu trước khi duyệt.
    - Không thay đổi hình ảnh, audio, đáp án.
    - Không tự xuất bản đề.
    - Sử dụng transaction để tránh cập nhật dở.
    """

    require_admin()

    # ----------------------------------------------
    # 1. KIỂM TRA XÁC NHẬN
    # ----------------------------------------------

    if request.form.get("xac_nhan") != "DUYET_TAT_CA":
        abort(
            400,
            description="Thiếu xác nhận duyệt tất cả."
        )

    with closing(get_connection()) as conn:

        try:
            cursor = conn.cursor()

            # --------------------------------------
            # 2. KHÓA VÀ KIỂM TRA ĐỀ THI
            # --------------------------------------

            de = get_exam(
                cursor,
                ma_de,
                lock=True
            )

            if de["TrangThai"] not in (
                "ban_nhap",
                "cho_duyet"
            ):
                abort(
                    409,
                    description=(
                        "Đề đã xuất bản hoặc "
                        "không cho phép duyệt."
                    )
                )

            # --------------------------------------
            # 3. ĐỌC VÀ KHÓA CÂU HỎI CỦA ĐỀ
            # --------------------------------------

            cursor.execute("""
                SELECT
                    SoCau,
                    KyNang,
                    DapAnDung,
                    NoiDung,
                    AnhCauHoi,
                    AnhNhomLuaChon,
                    DaDuyet

                FROM dbo.CauHoiThiHSK
                     WITH (UPDLOCK, HOLDLOCK)

                WHERE MaDeThi = ?

                ORDER BY SoCau
            """, ma_de)

            ds_cau = fetch_dicts(cursor)

            tong = de["TongSoCau"]

            # --------------------------------------
            # 4. KIỂM TRA ĐẦY ĐỦ DỮ LIỆU
            # --------------------------------------

            hop_le = (
                tong is not None
                and tong > 0

                and len(ds_cau) == tong

                and [
                    cau["SoCau"]
                    for cau in ds_cau
                ] == list(range(1, tong + 1))

                and sum(
                    cau["KyNang"] == "nghe"
                    for cau in ds_cau
                ) == de["SoCauNghe"]

                and sum(
                    cau["KyNang"] == "doc"
                    for cau in ds_cau
                ) == de["SoCauDoc"]

                and sum(
                    cau["KyNang"] == "viet"
                    for cau in ds_cau
                ) == de["SoCauViet"]

                and all(
                    cau["DapAnDung"] is not None
                    and str(
                        cau["DapAnDung"]
                    ).strip()

                    and (
                        cau["NoiDung"]
                        or cau["AnhCauHoi"]
                        or cau["AnhNhomLuaChon"]
                    )

                    for cau in ds_cau
                )

                and (
                    de["SoCauNghe"] == 0
                    or (
                        de["MaTepAudio"]
                        and de["AudioUrl"]
                    )
                )
            )

            if not hop_le:

                conn.rollback()

                flash(
                    "Chưa thể duyệt tất cả. "
                    "Đề phải đủ số câu liên tục, "
                    "đúng kỹ năng, có nội dung, "
                    "đáp án và MP3.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "admin_luyen_thi.chi_tiet",
                        ma_de=ma_de
                    )
                )

            # --------------------------------------
            # 5. CHỈ DUYỆT CÂU CHƯA DUYỆT
            # --------------------------------------

            cursor.execute("""
                UPDATE dbo.CauHoiThiHSK

                SET DaDuyet = 1

                WHERE MaDeThi = ?
                  AND DaDuyet = 0
            """, ma_de)

            so_vua_duyet = cursor.rowcount

            # --------------------------------------
            # 6. KIỂM TRA KẾT QUẢ SAU UPDATE
            # --------------------------------------

            cursor.execute("""
                SELECT
                    COUNT(*),

                    COALESCE(
                        SUM(
                            CASE
                                WHEN DaDuyet = 1
                                THEN 1
                                ELSE 0
                            END
                        ),
                        0
                    )

                FROM dbo.CauHoiThiHSK

                WHERE MaDeThi = ?
            """, ma_de)

            tong_sau, da_duyet_sau = (
                cursor.fetchone()
            )

            if (
                tong_sau != tong
                or da_duyet_sau != tong
            ):
                raise ValueError(
                    "Không duyệt đủ câu hỏi. "
                    "Đã hoàn tác giao dịch."
                )

            # --------------------------------------
            # 7. LƯU TRANSACTION
            # --------------------------------------

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    # ----------------------------------------------
    # 8. THÔNG BÁO KẾT QUẢ
    # ----------------------------------------------

    if so_vua_duyet > 0:

        flash(
            f"Đã duyệt thêm {so_vua_duyet} câu. "
            f"Toàn bộ {tong}/{tong} câu đã duyệt. "
            "Bạn vẫn cần xuất bản đề thi.",
            "success"
        )

    else:

        flash(
            "Tất cả câu hỏi của đề này "
            "đã được duyệt trước đó.",
            "success"
        )

    return redirect(
        url_for(
            "admin_luyen_thi.chi_tiet",
            ma_de=ma_de
        )
    )


# ==================================================
# 7. XUẤT BẢN ĐỀ THI
# ==================================================

@admin_luyen_thi_bp.post(
    "/<int:ma_de>/xuat-ban"
)
def xuat_ban(ma_de):

    require_admin()

    # Yêu cầu xác nhận trước khi xuất bản.
    if request.form.get("xac_nhan") != "XUAT_BAN":

        flash(
            "Bạn cần xác nhận xuất bản đề thi.",
            "warning"
        )

        return redirect(
            url_for(
                "admin_luyen_thi.chi_tiet",
                ma_de=ma_de
            )
        )

    with closing(get_connection()) as conn:

        try:
            cursor = conn.cursor()

            de = get_exam(
                cursor,
                ma_de,
                lock=True
            )

            if de["TrangThai"] == "da_xuat_ban":

                conn.rollback()

                flash(
                    "Đề thi này đã được xuất bản.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "admin_luyen_thi.chi_tiet",
                        ma_de=ma_de
                    )
                )

            if de["TrangThai"] not in (
                "ban_nhap",
                "cho_duyet",
            ):
                abort(
                    409,
                    description=(
                        "Trạng thái đề không cho phép "
                        "xuất bản."
                    )
                )

            # --------------------------------------
            # 7.1. KIỂM TRA TOÀN BỘ CÂU HỎI
            # --------------------------------------

            cursor.execute("""
                SELECT
                    COUNT(*) AS Tong,

                    COALESCE(SUM(
                        CASE
                            WHEN DaDuyet = 1
                            THEN 1 ELSE 0
                        END
                    ), 0) AS DaDuyet,

                    COALESCE(SUM(
                        CASE
                            WHEN KyNang = 'nghe'
                            THEN 1 ELSE 0
                        END
                    ), 0) AS Nghe,

                    COALESCE(SUM(
                        CASE
                            WHEN KyNang = 'doc'
                            THEN 1 ELSE 0
                        END
                    ), 0) AS Doc,

                    COALESCE(SUM(
                        CASE
                            WHEN KyNang = 'viet'
                            THEN 1 ELSE 0
                        END
                    ), 0) AS Viet,

                    COALESCE(SUM(
                        CASE
                            WHEN LTRIM(
                                RTRIM(DapAnDung)
                            ) = ''
                            THEN 1 ELSE 0
                        END
                    ), 0) AS ThieuDapAn,

                    MIN(SoCau) AS SoCauDau,
                    MAX(SoCau) AS SoCauCuoi

                FROM dbo.CauHoiThiHSK
                    WITH (HOLDLOCK)

                WHERE MaDeThi = ?
            """, ma_de)

            (
                tong,
                so_da_duyet,
                so_nghe,
                so_doc,
                so_viet,
                thieu_dap_an,
                so_cau_dau,
                so_cau_cuoi,
            ) = cursor.fetchone()

            # --------------------------------------
            # 7.2. ĐIỀU KIỆN XUẤT BẢN
            # --------------------------------------

            hop_le = (
                tong == de["TongSoCau"]
                and tong > 0

                and so_da_duyet == tong

                and so_nghe == de["SoCauNghe"]
                and so_doc == de["SoCauDoc"]
                and so_viet == de["SoCauViet"]

                and thieu_dap_an == 0

                and so_cau_dau == 1
                and so_cau_cuoi == tong

                and (
                    so_nghe == 0
                    or (
                        de["MaTepAudio"]
                        and de["AudioUrl"]
                    )
                )
            )

            if not hop_le:

                conn.rollback()

                flash(
                    "Chưa đủ điều kiện xuất bản. "
                    "Hãy kiểm tra số câu, đáp án, "
                    "MP3 và duyệt đầy đủ từng câu.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "admin_luyen_thi.chi_tiet",
                        ma_de=ma_de
                    )
                )

            # --------------------------------------
            # 7.3. CẬP NHẬT TRẠNG THÁI ĐỀ
            # --------------------------------------

            cursor.execute("""
                UPDATE dbo.DeThiHSK

                SET TrangThai = 'da_xuat_ban'

                WHERE MaDeThi = ?
                  AND TrangThai IN (
                      'ban_nhap',
                      'cho_duyet'
                  )
            """, ma_de)

            if cursor.rowcount != 1:
                conn.rollback()
                abort(409)

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    flash(
        "Đã xuất bản đề thi thành công. "
        "Người học có thể thấy đề trong danh sách.",
        "success"
    )

    return redirect(
        url_for(
            "admin_luyen_thi.chi_tiet",
            ma_de=ma_de
        )
    )
