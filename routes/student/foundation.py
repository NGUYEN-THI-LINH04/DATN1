from flask import Blueprint, render_template
from contextlib import closing

from database import get_connection


foundation_bp = Blueprint(
    "foundation",
    __name__,
    url_prefix="/nen-tang"
)


# =========================================================
# HELPER
# =========================================================
def row_to_dict(cursor, row):
    columns = [
        column[0]
        for column in cursor.description
    ]

    return dict(
        zip(columns, row)
    )


# =========================================================
# BẢNG PINYIN
# URL:
# /nen-tang/pinyin
# =========================================================
@foundation_bp.route("/pinyin")
def pinyin():

    thanh_mau = []
    van_mau = []
    am_ghep = []

    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    p.MaPinyin,
                    p.LoaiAm,
                    p.KyHieu,
                    p.CachDoc,
                    p.ViDu,
                    p.MaTep,
                    p.MaNguon,
                    p.ThuTu,
                    p.TrangThai,

                    t.DuongDanTep,
                    t.TieuDe AS TieuDeTep

                FROM dbo.BangPinyin AS p

                LEFT JOIN dbo.TepDaPhuongTien AS t
                    ON p.MaTep = t.MaTep

                ORDER BY
                    CASE p.LoaiAm

                        WHEN 'thanh_mau'
                            THEN 1

                        WHEN 'van_mau'
                            THEN 2

                        WHEN 'am_ghep'
                            THEN 3

                        ELSE 4

                    END,

                    p.ThuTu,
                    p.MaPinyin;
                """
            )

            for row in cursor.fetchall():

                item = row_to_dict(
                    cursor,
                    row
                )

                loai_am = item.get(
                    "LoaiAm"
                )

                if loai_am == "thanh_mau":

                    thanh_mau.append(
                        item
                    )

                elif loai_am == "van_mau":

                    van_mau.append(
                        item
                    )

                elif loai_am == "am_ghep":

                    am_ghep.append(
                        item
                    )


    total_pinyin = (
        len(thanh_mau)
        + len(van_mau)
        + len(am_ghep)
    )


    return render_template(
        "student/pinyin.html",

        thanh_mau=thanh_mau,
        van_mau=van_mau,
        am_ghep=am_ghep,

        total_pinyin=total_pinyin
    )


# =========================================================
# 214 BỘ THỦ
# URL:
# /nen-tang/bo-thu
# =========================================================
@foundation_bp.route("/bo-thu")
def radicals():

    radicals = []

    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    MaBoThu,
                    SoBoThu,
                    KyHieu,
                    TenBoThu,
                    YNghia,
                    SoNet,
                    MoTa,
                    MaTep,
                    MaNguon,
                    TrangThai

                FROM dbo.BoThu

                ORDER BY
                    SoBoThu,
                    MaBoThu;
                """
            )

            for row in cursor.fetchall():

                radicals.append(
                    row_to_dict(
                        cursor,
                        row
                    )
                )


    return render_template(
        "student/radicals.html",

        radicals=radicals,
        total_radicals=len(radicals)
    )


# =========================================================
# QUY TẮC PHÁT ÂM / CHUYỂN ÂM
# URL:
# /nen-tang/quy-tac-phat-am
# =========================================================
@foundation_bp.route("/quy-tac-phat-am")
def pronunciation_rules():

    rules = []

    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    q.MaQuyTac,
                    q.TenQuyTac,
                    q.LoaiQuyTac,
                    q.NoiDung,
                    q.ViDuTiengTrung,
                    q.ViDuPinyin,
                    q.NghiaTiengViet,
                    q.MaTep,
                    q.MaNguon,
                    q.ThuTu,
                    q.TrangThai,

                    t.DuongDanTep,
                    t.TieuDe AS TieuDeTep

                FROM dbo.QuyTacPhatAm AS q

                LEFT JOIN dbo.TepDaPhuongTien AS t
                    ON q.MaTep = t.MaTep

                ORDER BY
                    q.ThuTu,
                    q.MaQuyTac;
                """
            )

            for row in cursor.fetchall():

                rules.append(
                    row_to_dict(
                        cursor,
                        row
                    )
                )


    return render_template(
        "student/pronunciation_rules.html",

        rules=rules,
        total_rules=len(rules)
    )