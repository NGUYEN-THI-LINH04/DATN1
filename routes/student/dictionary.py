
# -*- coding: utf-8 -*-
"""
MỘC HÁN - TRA TỪ ĐIỂN DÀNH CHO NGƯỜI HỌC

File: routes/student/dictionary.py

Chức năng:
- Tra từ bằng chữ Hán, Pinyin hoặc nghĩa tiếng Việt.
- Tìm kiếm Pinyin không cần nhập dấu thanh.
- Chỉ hiển thị từ vựng đã duyệt trong SQL Server.
- Hiển thị cấp độ HSK, loại từ và câu ví dụ.
- Cung cấp API lấy chi tiết một từ.

Sử dụng các bảng SQL đã có:
    dbo.TuVung
    dbo.TuVungBaiHoc
    dbo.BaiHoc
    dbo.KhoaHoc
    dbo.ViDuTuVung

Không tạo bảng SQL mới.
Chưa thay đổi chức năng Sổ tay từ vựng hiện tại.
"""

import re
from contextlib import closing

import pyodbc
from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from database import get_connection

try:
    from pypinyin import lazy_pinyin, Style
except ImportError:
    lazy_pinyin = None
    Style = None


# ==========================================================
# 1. BLUEPRINT
# ==========================================================

student_dictionary_bp = Blueprint(
    "student_dictionary",
    __name__,
    url_prefix="/student/dictionary",
)

MAX_QUERY_LENGTH = 80
MAX_RESULTS = 40


# ==========================================================
# 2. KIỂM TRA QUYỀN NGƯỜI HỌC
# ==========================================================

@student_dictionary_bp.before_request
def require_student():
    account = getattr(g, "account", None)

    if account is None:
        if request.path.startswith("/student/dictionary/api/"):
            return jsonify({
                "ok": False,
                "error": "Bạn cần đăng nhập trước.",
            }), 401

        return redirect(url_for("auth.login"))

    if account["role"] != "student":
        abort(
            403,
            description="Chức năng dành cho Người học.",
        )


# ==========================================================
# 3. HÀM HỖ TRỢ
# ==========================================================

def fetch_rows(cursor):
    columns = [
        column[0]
        for column in cursor.description
    ]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def normalize_pinyin(value):
    """
    Loại bỏ khoảng trắng, dấu nháy và dấu nối.
    Ví dụ: 'tong xue' -> 'tongxue'.

    SQL Server dùng collation không phân biệt dấu thanh
    để tìm được 'tóngxué' khi nhập 'tongxue'.
    """
    value = str(value or "").strip().lower()

    return re.sub(
        r"[\s'’\-]+",
        "",
        value,
    )


def create_pinyin(chinese):
    """Tạo Pinyin cho câu ví dụ khi SQL chưa có."""
    if not chinese or lazy_pinyin is None:
        return None

    try:
        return " ".join(
            lazy_pinyin(
                chinese,
                style=Style.TONE,
            )
        )
    except Exception:
        return None


def format_word(row):
    level = row.get("MaCapDo")

    return {
        "ma_tu_vung": int(row["MaTuVung"]),
        "chu_han": row["ChuHan"],
        "chu_phon_the": row.get("ChuPhonThe"),
        "phien_am": row["PhienAm"],
        "nghia_tieng_viet": row["NghiaTiengViet"],
        "tu_loai": row.get("TuLoai"),
        "ma_am_thanh": row.get("MaAmThanh"),
        "hsk": int(level) if level is not None else None,
        "vi_du": [],
    }


# ==========================================================
# 4. TRUY VẤN TỪ VỰNG ĐÃ DUYỆT
# ==========================================================

WORD_COLUMNS = """
    v.MaTuVung,
    v.ChuHan,
    v.ChuPhonThe,
    v.PhienAm,
    v.NghiaTiengViet,
    v.TuLoai,
    v.MaAmThanh,
    hsk.MaCapDo,
    v.ViDuTiengTrung,
    v.ViDuTiengViet
"""

WORD_FROM = """
FROM dbo.TuVung AS v

OUTER APPLY (
    SELECT MIN(kh.MaCapDo) AS MaCapDo
    FROM dbo.TuVungBaiHoc AS tvbh

    INNER JOIN dbo.BaiHoc AS bh
        ON bh.MaBaiHoc = tvbh.MaBaiHoc

    INNER JOIN dbo.KhoaHoc AS kh
        ON kh.MaKhoaHoc = bh.MaKhoaHoc

    WHERE tvbh.MaTuVung = v.MaTuVung
) AS hsk
"""

PINYIN_EXPRESSION = """
REPLACE(
    REPLACE(
        REPLACE(LOWER(v.PhienAm), N' ', N''),
        N'''',
        N''
    ),
    N'-',
    N''
) COLLATE Latin1_General_100_CI_AI
"""


def search_words(cursor, query):
    pinyin_query = normalize_pinyin(query)

    sql = f"""
        SELECT TOP ({MAX_RESULTS})
            {WORD_COLUMNS}

        {WORD_FROM}

        WHERE v.DaDuyet = 1
          AND (
              CHARINDEX(?, v.ChuHan) > 0

              OR CHARINDEX(?, v.ChuPhonThe) > 0

              OR CHARINDEX(
                  ?,
                  {PINYIN_EXPRESSION}
              ) > 0

              OR CHARINDEX(
                  ?,
                  v.NghiaTiengViet
                    COLLATE Latin1_General_100_CI_AI
              ) > 0
          )

        ORDER BY
            CASE
                WHEN v.ChuHan = ?
                     OR v.ChuPhonThe = ?
                    THEN 0

                WHEN {PINYIN_EXPRESSION}
                     = ? COLLATE Latin1_General_100_CI_AI
                    THEN 1

                ELSE 2
            END,

            hsk.MaCapDo,
            v.MaTuVung
    """

    cursor.execute(
        sql,
        query,
        query,
        pinyin_query,
        query,
        query,
        query,
        pinyin_query,
    )

    return fetch_rows(cursor)


def get_word_by_id(cursor, word_id):
    sql = f"""
        SELECT
            {WORD_COLUMNS}

        {WORD_FROM}

        WHERE v.MaTuVung = ?
          AND v.DaDuyet = 1
    """

    cursor.execute(sql, int(word_id))

    rows = fetch_rows(cursor)

    return rows[0] if rows else None


# ==========================================================
# 5. LẤY CÂU VÍ DỤ TỪ SQL
# ==========================================================

def attach_examples(cursor, raw_rows):
    if not raw_rows:
        return []

    words = []
    word_map = {}

    for row in raw_rows:
        word = format_word(row)

        word_id = word["ma_tu_vung"]

        # Ví dụ được lưu trực tiếp trong dbo.TuVung.
        chinese = row.get("ViDuTiengTrung")
        vietnamese = row.get("ViDuTiengViet")

        if chinese and vietnamese:
            word["vi_du"].append({
                "tieng_trung": chinese,
                "pinyin": create_pinyin(chinese),
                "tieng_viet": vietnamese,
            })

        words.append(word)
        word_map[word_id] = word

    # Lấy thêm những ví dụ đã xuất bản.
    # Không sử dụng ví dụ còn ở trạng thái bản nháp.
    ids = list(word_map.keys())

    placeholders = ",".join("?" for _ in ids)

    sql = f"""
        SELECT
            MaTuVung,
            CauTiengTrung,
            Pinyin,
            NghiaTiengViet
        FROM dbo.ViDuTuVung
        WHERE MaTuVung IN ({placeholders})
          AND TrangThai IN (
              'da_xuat_ban',
              'da_duyet'
          )
        ORDER BY
            MaTuVung,
            LaViDuChinh DESC,
            ThuTu,
            MaViDu
    """

    cursor.execute(sql, *ids)

    for row in fetch_rows(cursor):
        word_id = int(row["MaTuVung"])

        word = word_map.get(word_id)

        if not word or len(word["vi_du"]) >= 3:
            continue

        chinese = row["CauTiengTrung"]

        # Tránh hiển thị cùng một câu nhiều lần.
        if any(
            example["tieng_trung"] == chinese
            for example in word["vi_du"]
        ):
            continue

        word["vi_du"].append({
            "tieng_trung": chinese,
            "pinyin": (
                row["Pinyin"]
                or create_pinyin(chinese)
            ),
            "tieng_viet": row["NghiaTiengViet"],
        })

    return words


# ==========================================================
# 6. TRANG TRA TỪ ĐIỂN
# ==========================================================

@student_dictionary_bp.get("/")
def index():
    return render_template(
        "student/dictionary.html"
    )


# ==========================================================
# 7. API TÌM KIẾM
#
# GET /student/dictionary/api/search?q=tongxue
# ==========================================================

@student_dictionary_bp.get("/api/search")
def api_search():
    query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    if not query:
        return jsonify({
            "ok": True,
            "query": "",
            "count": 0,
            "results": [],
        })

    if len(query) > MAX_QUERY_LENGTH:
        return jsonify({
            "ok": False,
            "error": "Từ khóa tìm kiếm quá dài.",
        }), 400

    try:
        with closing(get_connection()) as conn:
            cursor = conn.cursor()

            raw_rows = search_words(cursor, query)

            results = attach_examples(
                cursor,
                raw_rows,
            )

        return jsonify({
            "ok": True,
            "query": query,
            "count": len(results),
            "results": results,
        })

    except pyodbc.Error:
        current_app.logger.exception(
            "Lỗi SQL khi tra từ điển"
        )

        return jsonify({
            "ok": False,
            "error": (
                "Chưa thể tra từ lúc này. "
                "Vui lòng thử lại."
            ),
        }), 500


# ==========================================================
# 8. API CHI TIẾT TỪ VỰNG
#
# GET /student/dictionary/api/word/367
# ==========================================================

@student_dictionary_bp.get("/api/word/<int:word_id>")
def api_word_detail(word_id):
    try:
        with closing(get_connection()) as conn:
            cursor = conn.cursor()

            row = get_word_by_id(
                cursor,
                word_id,
            )

            if row is None:
                return jsonify({
                    "ok": False,
                    "error": "Không tìm thấy từ vựng.",
                }), 404

            words = attach_examples(
                cursor,
                [row],
            )

        return jsonify({
            "ok": True,
            "word": words[0],
        })

    except pyodbc.Error:
        current_app.logger.exception(
            "Lỗi SQL khi lấy chi tiết từ vựng"
        )

        return jsonify({
            "ok": False,
            "error": "Không thể tải thông tin từ vựng.",
        }), 500
