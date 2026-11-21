from contextlib import closing
from decimal import Decimal, InvalidOperation
from math import ceil
import json

import pyodbc

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from database import get_connection


# ============================================================
# CẤU HÌNH
# ============================================================

admin_questions_bp = Blueprint(
    "admin_questions",
    __name__,
    url_prefix="/admin/cau-hoi",
)

QUESTION_TYPES = {
    "chon_mot": "Chọn một",
    "chon_nhieu": "Chọn nhiều",
    "dung_sai": "Đúng / Sai",
    "dien_tu": "Điền từ",
    "ghep_cap": "Ghép cặp",
    "sap_xep": "Sắp xếp",
    "viet_ngan": "Viết ngắn",
}

SKILLS = {
    "doc": "Đọc",
    "nghe": "Nghe",
    "viet": "Viết",
    "tong_hop": "Tổng hợp",
}

PAGE_SIZE = 25


# ============================================================
# KIỂM TRA QUYỀN ADMIN
# ============================================================

@admin_questions_bp.before_request
def require_admin():
    account = getattr(g, "account", None)

    if account is None:
        return redirect(url_for("auth.admin_login"))

    if account["role"] != "admin":
        abort(
            403,
            description="Bạn không có quyền quản lý câu hỏi.",
        )


@admin_questions_bp.errorhandler(pyodbc.Error)
def handle_database_error(error):
    current_app.logger.exception(
        "Lỗi SQL trong chức năng quản lý câu hỏi"
    )

    return "Không thể xử lý dữ liệu câu hỏi.", 503


# ============================================================
# LẤY ADMIN ĐANG ĐĂNG NHẬP
# ============================================================

def get_admin_id():
    account = getattr(g, "account", None)

    if account is None or account["role"] != "admin":
        abort(403)

    try:
        admin_id = int(account["id"])
    except (KeyError, TypeError, ValueError):
        abort(
            403,
            description="Không xác định được tài khoản Admin.",
        )

    if admin_id <= 0:
        abort(403)

    return admin_id


# ============================================================
# URL GIỮ BỘ LỌC VÀ PHÂN TRANG
# ============================================================

def index_url(**changes):
    allowed = {
        "exercise_id",
        "type",
        "skill",
        "q",
        "page",
        "edit",
    }

    # Chỉ lấy request.args.
    # Không lấy request.form để tránh nhầm tên field.
    args = {
        key: value
        for key, value in request.args.items()
        if key in allowed and value
    }

    for key, value in changes.items():
        if value is None:
            args.pop(key, None)
        else:
            args[key] = value

    return url_for(
        "admin_questions.index",
        **args,
    )


def form_return_url(form):
    exercise_id = form.get("exercise_id")

    if exercise_id:
        return url_for(
            "admin_questions.index",
            exercise_id=exercise_id,
        )

    return url_for("admin_questions.index")


# ============================================================
# ĐỌC JSON ĐÁP ÁN
# ============================================================

def parse_answer_json(raw_value):
    if not raw_value:
        return {}

    try:
        data = json.loads(raw_value)
    except (TypeError, ValueError):
        return {}

    if isinstance(data, dict):
        return data

    return {}


# ============================================================
# LẤY DANH SÁCH BÀI TẬP
# ============================================================

def load_exercises():
    exercises = []

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    bt.MaBaiTap,
                    bt.TieuDe,
                    bt.TrangThai,
                    bh.MaBaiHoc,
                    bh.SoThuTuBai,
                    bh.TieuDe,
                    kh.MaKhoaHoc,
                    kh.MaCapDo,
                    kh.TieuDe
                FROM dbo.BaiTap AS bt
                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc = bt.MaBaiHoc
                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc
                ORDER BY
                    kh.MaCapDo,
                    bh.SoThuTuBai,
                    bt.MaBaiTap;
                """
            )

            for row in cursor.fetchall():
                exercises.append({
                    "id": row[0],
                    "title": row[1],
                    "status": row[2],
                    "lesson_id": row[3],
                    "lesson_order": row[4],
                    "lesson_title": row[5],
                    "course_id": row[6],
                    "course_level": row[7],
                    "course_title": row[8],
                })

    return exercises


# ============================================================
# LẤY DANH SÁCH MEDIA
# ============================================================

def load_media():
    media_items = []

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    MaTep,
                    LoaiTep,
                    TieuDe,
                    DuongDanTep
                FROM dbo.TepDaPhuongTien
                ORDER BY
                    LoaiTep,
                    TieuDe,
                    MaTep;
                """
            )

            for row in cursor.fetchall():
                media_items.append({
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "path": row[3],
                })

    return media_items


# ============================================================
# ĐỌC DỮ LIỆU FORM
# ============================================================

def parse_question_form():
    return {
        "exercise_id": request.form.get(
            "exercise_id",
            type=int,
        ),

        "question_type": request.form.get(
            "question_type",
            "",
        ).strip(),

        "skill": request.form.get(
            "skill",
            "",
        ).strip(),

        "content": request.form.get(
            "content",
            "",
        ).strip(),

        "passage": request.form.get(
            "passage",
            "",
        ).strip(),

        "media_id": request.form.get(
            "media_id",
            type=int,
        ),

        "explanation": request.form.get(
            "explanation",
            "",
        ).strip(),

        "raw_score": request.form.get(
            "max_score",
            "1",
        ).strip(),
    }


# ============================================================
# KIỂM TRA FORM
# ============================================================

def validate_question_form(form):
    if form["exercise_id"] is None:
        return None, "Bạn cần chọn bài tập."

    if form["question_type"] not in QUESTION_TYPES:
        return None, "Loại câu hỏi không hợp lệ."

    if form["skill"] not in SKILLS:
        return None, "Kỹ năng không hợp lệ."

    if not form["content"]:
        return None, (
            "Nội dung câu hỏi không được để trống."
        )

    try:
        max_score = Decimal(form["raw_score"])
    except (InvalidOperation, ValueError):
        return None, "Điểm tối đa không hợp lệ."

    if not max_score.is_finite():
        return None, "Điểm tối đa không hợp lệ."

    if max_score <= 0:
        return None, "Điểm tối đa phải lớn hơn 0."

    if max_score > Decimal("999999.99"):
        return None, "Điểm tối đa vượt giới hạn SQL."

    if max_score.as_tuple().exponent < -2:
        return None, (
            "Điểm chỉ được có tối đa 2 chữ số thập phân."
        )

    return max_score, None


# ============================================================
# TẠO ĐÁP ÁN CHO 7 LOẠI CÂU HỎI
# ============================================================

def build_answer_data(question_type):
    answer_json = None
    choices = []

    # --------------------------------------------------------
    # 1. CHỌN MỘT / CHỌN NHIỀU
    # --------------------------------------------------------

    if question_type in ("chon_mot", "chon_nhieu"):
        for index in range(1, 5):
            choice_text = request.form.get(
                f"choice_{index}",
                "",
            ).strip()

            if not choice_text:
                continue

            is_correct = (
                request.form.get(f"correct_{index}") == "1"
            )

            choices.append({
                "text": choice_text,
                "correct": is_correct,
                "order": len(choices) + 1,
            })

        if len(choices) < 2:
            return None, None, (
                "Câu hỏi lựa chọn cần ít nhất 2 đáp án."
            )

        correct_count = sum(
            1
            for choice in choices
            if choice["correct"]
        )

        if (
            question_type == "chon_mot"
            and correct_count != 1
        ):
            return None, None, (
                "Câu Chọn một phải có đúng 1 đáp án đúng."
            )

        if (
            question_type == "chon_nhieu"
            and correct_count < 1
        ):
            return None, None, (
                "Câu Chọn nhiều phải có ít nhất 1 đáp án đúng."
            )

    # --------------------------------------------------------
    # 2. ĐÚNG / SAI
    # --------------------------------------------------------

    elif question_type == "dung_sai":
        answer = request.form.get(
            "true_false_answer",
            "",
        ).strip()

        if answer not in ("dung", "sai"):
            return None, None, (
                "Bạn cần chọn Đúng hoặc Sai."
            )

        answer_json = json.dumps(
            {"answer": answer},
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # 3. ĐIỀN TỪ
    # --------------------------------------------------------

    elif question_type == "dien_tu":
        raw_answers = request.form.get(
            "fill_answers",
            "",
        ).strip()

        answers = [
            line.strip()
            for line in raw_answers.splitlines()
            if line.strip()
        ]

        if not answers:
            return None, None, (
                "Bạn cần nhập ít nhất một đáp án điền từ."
            )

        answer_json = json.dumps(
            {"answers": answers},
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # 4. GHÉP CẶP
    # --------------------------------------------------------

    elif question_type == "ghep_cap":
        raw_pairs = request.form.get(
            "matching_pairs",
            "",
        ).strip()

        pairs = []

        for line in raw_pairs.splitlines():
            line = line.strip()

            if not line:
                continue

            if "=>" not in line:
                return None, None, (
                    "Mỗi cặp phải có dạng: "
                    "vế trái => vế phải."
                )

            left, right = line.split("=>", 1)

            left = left.strip()
            right = right.strip()

            if not left or not right:
                return None, None, (
                    "Một cặp ghép đang bị thiếu nội dung."
                )

            pairs.append({
                "left": left,
                "right": right,
            })

        if len(pairs) < 2:
            return None, None, (
                "Câu Ghép cặp cần ít nhất 2 cặp."
            )

        answer_json = json.dumps(
            {"pairs": pairs},
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # 5. SẮP XẾP
    # --------------------------------------------------------

    elif question_type == "sap_xep":
        raw_items = request.form.get(
            "sorting_items",
            "",
        ).strip()

        items = [
            line.strip()
            for line in raw_items.splitlines()
            if line.strip()
        ]

        if len(items) < 2:
            return None, None, (
                "Câu Sắp xếp cần ít nhất 2 thành phần."
            )

        answer_json = json.dumps(
            {"items": items},
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # 6. VIẾT NGẮN
    # --------------------------------------------------------

    elif question_type == "viet_ngan":
        sample_answer = request.form.get(
            "sample_answer",
            "",
        ).strip()

        if not sample_answer:
            return None, None, (
                "Câu Viết ngắn cần có đáp án mẫu."
            )

        answer_json = json.dumps(
            {"sample_answer": sample_answer},
            ensure_ascii=False,
        )

    else:
        return None, None, "Loại câu hỏi không hợp lệ."

    return answer_json, choices, None


# ============================================================
# KIỂM TRA LIÊN KẾT BÀI TẬP VÀ MEDIA
# ============================================================

def validate_relations(cursor, exercise_id, media_id):
    cursor.execute(
        """
        SELECT MaBaiTap
        FROM dbo.BaiTap
        WHERE MaBaiTap = ?;
        """,
        exercise_id,
    )

    if cursor.fetchone() is None:
        abort(
            400,
            description="Bài tập không tồn tại.",
        )

    if media_id is not None:
        cursor.execute(
            """
            SELECT MaTep
            FROM dbo.TepDaPhuongTien
            WHERE MaTep = ?;
            """,
            media_id,
        )

        if cursor.fetchone() is None:
            abort(
                400,
                description="Media không tồn tại.",
            )


# ============================================================
# BỘ LỌC CÂU HỎI
# ============================================================

def read_filters(source):
    exercise_id = source.get(
        "exercise_id",
        type=int,
    )

    question_type = source.get(
        "type",
        "all",
    )

    skill = source.get(
        "skill",
        "all",
    )

    keyword = source.get(
        "q",
        "",
    ).strip()

    if (
        question_type != "all"
        and question_type not in QUESTION_TYPES
    ):
        question_type = "all"

    if skill != "all" and skill not in SKILLS:
        skill = "all"

    return (
        exercise_id,
        question_type,
        skill,
        keyword,
    )


def build_filter_sql(
    exercise_id,
    question_type,
    skill,
    keyword,
):
    conditions = []
    params = []

    if exercise_id is not None:
        conditions.append(
            "ch.MaBaiTap = ?"
        )
        params.append(exercise_id)

    if question_type != "all":
        conditions.append(
            "ch.LoaiCauHoi = ?"
        )
        params.append(question_type)

    if skill != "all":
        conditions.append(
            "ch.KyNang = ?"
        )
        params.append(skill)

    if keyword:
        conditions.append(
            """
            (
                CHARINDEX(?, ch.NoiDungCauHoi) > 0

                OR CHARINDEX(
                    ?,
                    ISNULL(ch.GiaiThich, N'')
                ) > 0

                OR CHARINDEX(
                    ?,
                    bt.TieuDe
                ) > 0
            )
            """
        )

        params.extend([
            keyword,
            keyword,
            keyword,
        ])

    where_sql = ""

    if conditions:
        where_sql = (
            " WHERE "
            + " AND ".join(conditions)
        )

    return where_sql, params


# ============================================================
# DANH SÁCH CÂU HỎI
# PHÂN TRANG 25 CÂU / TRANG
# ============================================================

@admin_questions_bp.get("/")
def index():
    (
        exercise_id,
        question_type,
        skill,
        keyword,
    ) = read_filters(request.args)

    edit_id = request.args.get(
        "edit",
        type=int,
    )

    page = max(
        1,
        request.args.get(
            "page",
            1,
            type=int,
        ) or 1,
    )

    exercises = load_exercises()
    media_items = load_media()

    questions = []
    editing_question = None

    total_count = 0
    total_pages = 1
    exercise_question_count = 0

    with closing(get_connection()) as connection:
        with closing(connection.cursor()) as cursor:
            where_sql, params = build_filter_sql(
                exercise_id,
                question_type,
                skill,
                keyword,
            )

            from_sql = """
                FROM dbo.CauHoi AS ch

                INNER JOIN dbo.BaiTap AS bt
                    ON bt.MaBaiTap = ch.MaBaiTap

                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc = bt.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON kh.MaKhoaHoc = bh.MaKhoaHoc

                LEFT JOIN dbo.TepDaPhuongTien AS media
                    ON media.MaTep = ch.MaTep
            """

            # Tổng số câu hỏi theo bộ lọc
            cursor.execute(
                "SELECT COUNT(*) "
                + from_sql
                + where_sql,
                *params,
            )

            total_count = int(
                cursor.fetchone()[0] or 0
            )

            total_pages = max(
                1,
                ceil(total_count / PAGE_SIZE),
            )

            page = min(
                page,
                total_pages,
            )

            offset = (
                page - 1
            ) * PAGE_SIZE

            # Tổng câu hỏi của bài tập đang chọn
            if exercise_id is not None:
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.CauHoi
                    WHERE MaBaiTap = ?;
                    """,
                    exercise_id,
                )

                exercise_question_count = int(
                    cursor.fetchone()[0] or 0
                )

            # Danh sách câu hỏi
            cursor.execute(
                """
                SELECT
                    ch.MaCauHoi,
                    ch.MaBaiTap,
                    ch.LoaiCauHoi,
                    ch.KyNang,
                    ch.NoiDungCauHoi,
                    ch.DoanVan,
                    ch.MaTep,
                    ch.DapAnJson,
                    ch.GiaiThich,
                    ch.DiemToiDa,
                    ch.ThuTu,

                    bt.TieuDe,
                    bt.TrangThai,

                    bh.SoThuTuBai,
                    bh.TieuDe,

                    kh.MaCapDo,

                    media.TieuDe,
                    media.LoaiTep,

                    (
                        SELECT COUNT(*)
                        FROM dbo.LuaChonCauHoi AS lc
                        WHERE lc.MaCauHoi = ch.MaCauHoi
                    ) AS SoLuaChon
                """
                + from_sql
                + where_sql
                + """
                ORDER BY
                    ch.MaBaiTap,
                    ch.ThuTu,
                    ch.MaCauHoi

                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY;
                """,
                *params,
                offset,
                PAGE_SIZE,
            )

            for row in cursor.fetchall():
                questions.append({
                    "id": row[0],
                    "exercise_id": row[1],
                    "type": row[2],
                    "skill": row[3],
                    "content": row[4],
                    "passage": row[5] or "",
                    "media_id": row[6],
                    "answer_json": row[7] or "",
                    "explanation": row[8] or "",
                    "max_score": row[9],
                    "order": row[10],
                    "exercise_title": row[11],
                    "exercise_status": row[12],
                    "lesson_order": row[13],
                    "lesson_title": row[14],
                    "course_level": row[15],
                    "media_title": row[16] or "",
                    "media_type": row[17] or "",
                    "choice_count": int(row[18] or 0),
                })

            # Đọc câu hỏi đang sửa
            if edit_id is not None:
                cursor.execute(
                    """
                    SELECT
                        MaCauHoi,
                        MaBaiTap,
                        LoaiCauHoi,
                        KyNang,
                        NoiDungCauHoi,
                        DoanVan,
                        MaTep,
                        DapAnJson,
                        GiaiThich,
                        DiemToiDa,
                        ThuTu
                    FROM dbo.CauHoi
                    WHERE MaCauHoi = ?;
                    """,
                    edit_id,
                )

                row = cursor.fetchone()

                if row is None:
                    abort(
                        404,
                        description="Không tìm thấy câu hỏi.",
                    )

                editing_question = {
                    "id": row[0],
                    "exercise_id": row[1],
                    "type": row[2],
                    "skill": row[3],
                    "content": row[4],
                    "passage": row[5] or "",
                    "media_id": row[6],
                    "answer_json": row[7] or "",
                    "answer_data": parse_answer_json(row[7]),
                    "explanation": row[8] or "",
                    "max_score": row[9],
                    "order": row[10],
                    "choices": [],
                }

                cursor.execute(
                    """
                    SELECT
                        MaLuaChon,
                        NoiDungLuaChon,
                        LaDapAnDung,
                        ThuTu
                    FROM dbo.LuaChonCauHoi
                    WHERE MaCauHoi = ?
                    ORDER BY
                        ThuTu,
                        MaLuaChon;
                    """,
                    edit_id,
                )

                for choice_row in cursor.fetchall():
                    editing_question["choices"].append({
                        "id": choice_row[0],
                        "text": choice_row[1],
                        "correct": bool(choice_row[2]),
                        "order": choice_row[3],
                    })

    can_reorder = (
        exercise_id is not None
        and question_type == "all"
        and skill == "all"
        and not keyword
        and exercise_question_count > 1
        and exercise_question_count <= PAGE_SIZE
    )

    return render_template(
        "admin/questions.html",

        active_page="questions",

        exercises=exercises,
        media_items=media_items,

        questions=questions,
        editing_question=editing_question,

        question_types=QUESTION_TYPES,
        skills=SKILLS,

        selected_exercise=exercise_id,
        selected_type=question_type,
        selected_skill=skill,
        keyword=keyword,

        page=page,
        page_size=PAGE_SIZE,
        total_count=total_count,
        total_pages=total_pages,

        exercise_question_count=exercise_question_count,
        can_reorder=can_reorder,
    )


# ============================================================
# THÊM CÂU HỎI
# ============================================================

@admin_questions_bp.post("/them")
def create():
    form = parse_question_form()

    max_score, error = validate_question_form(form)

    if error:
        flash(error, "error")
        return redirect(form_return_url(form))

    answer_json, choices, error = build_answer_data(
        form["question_type"]
    )

    if error:
        flash(error, "error")
        return redirect(form_return_url(form))

    admin_id = get_admin_id()

    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:
                validate_relations(
                    cursor,
                    form["exercise_id"],
                    form["media_id"],
                )

                # Khóa bài tập trong giao dịch
                cursor.execute(
                    """
                    SELECT TrangThai
                    FROM dbo.BaiTap WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaBaiTap = ?;
                    """,
                    form["exercise_id"],
                )

                status_row = cursor.fetchone()

                if status_row is None:
                    abort(404)

                if status_row[0] != "ban_nhap":
                    flash(
                        "Chỉ được thêm câu hỏi vào "
                        "bài tập Bản nháp.",
                        "error",
                    )

                    return redirect(
                        form_return_url(form)
                    )

                # Xác định thứ tự mới
                cursor.execute(
                    """
                    SELECT ISNULL(MAX(ThuTu), 0) + 1
                    FROM dbo.CauHoi
                    WHERE MaBaiTap = ?;
                    """,
                    form["exercise_id"],
                )

                next_order = int(
                    cursor.fetchone()[0] or 1
                )

                # Ghi audit khi thêm câu hỏi trên web
                cursor.execute(
                    """
                    INSERT INTO dbo.CauHoi
                    (
                        MaBaiTap,
                        LoaiCauHoi,
                        KyNang,
                        NoiDungCauHoi,
                        DoanVan,
                        MaTep,
                        DapAnJson,
                        GiaiThich,
                        DiemToiDa,
                        ThuTu,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat
                    )
                    OUTPUT INSERTED.MaCauHoi
                    VALUES
                    (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, SYSDATETIME()
                    );
                    """,
                    form["exercise_id"],
                    form["question_type"],
                    form["skill"],
                    form["content"],
                    form["passage"] or None,
                    form["media_id"],
                    answer_json,
                    form["explanation"] or None,
                    max_score,
                    next_order,
                    admin_id,
                )

                question_id = int(
                    cursor.fetchone()[0]
                )

                # Thêm các lựa chọn
                for choice in choices:
                    cursor.execute(
                        """
                        INSERT INTO dbo.LuaChonCauHoi
                        (
                            MaCauHoi,
                            NoiDungLuaChon,
                            LaDapAnDung,
                            ThuTu
                        )
                        VALUES (?, ?, ?, ?);
                        """,
                        question_id,
                        choice["text"],
                        1 if choice["correct"] else 0,
                        choice["order"],
                    )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    flash(
        "Đã thêm câu hỏi thành công.",
        "success",
    )

    return redirect(
        url_for(
            "admin_questions.index",
            exercise_id=form["exercise_id"],
        )
    )


# ============================================================
# SỬA CÂU HỎI
# ============================================================

@admin_questions_bp.post("/<int:question_id>/sua")
def edit(question_id):
    form = parse_question_form()

    max_score, error = validate_question_form(form)

    if error:
        flash(error, "error")
        return redirect(
            index_url(edit=question_id)
        )

    answer_json, choices, error = build_answer_data(
        form["question_type"]
    )

    if error:
        flash(error, "error")
        return redirect(
            index_url(edit=question_id)
        )

    admin_id = get_admin_id()

    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:
                cursor.execute(
                    """
                    SELECT
                        ch.MaBaiTap,
                        ch.ThuTu,
                        bt.TrangThai
                    FROM dbo.CauHoi AS ch
                    WITH (UPDLOCK, HOLDLOCK)

                    INNER JOIN dbo.BaiTap AS bt
                        ON bt.MaBaiTap = ch.MaBaiTap

                    WHERE ch.MaCauHoi = ?;
                    """,
                    question_id,
                )

                current_row = cursor.fetchone()

                if current_row is None:
                    abort(
                        404,
                        description="Không tìm thấy câu hỏi.",
                    )

                old_exercise_id = int(
                    current_row[0]
                )

                current_order = int(
                    current_row[1]
                )

                old_status = current_row[2]

                if old_status != "ban_nhap":
                    flash(
                        "Chỉ được sửa nội dung câu hỏi "
                        "khi bài tập là Bản nháp.",
                        "error",
                    )

                    return redirect(
                        index_url(edit=question_id)
                    )

                # Không sửa câu hỏi đã có lịch sử
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChiTietBaiLam
                    WHERE MaCauHoi = ?;
                    """,
                    question_id,
                )

                history_count = int(
                    cursor.fetchone()[0] or 0
                )

                if history_count > 0:
                    flash(
                        "Câu hỏi đã có lịch sử làm bài. "
                        "Không thể sửa nội dung hoặc đáp án.",
                        "error",
                    )

                    return redirect(
                        index_url(edit=question_id)
                    )

                validate_relations(
                    cursor,
                    form["exercise_id"],
                    form["media_id"],
                )

                cursor.execute(
                    """
                    SELECT TrangThai
                    FROM dbo.BaiTap WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaBaiTap = ?;
                    """,
                    form["exercise_id"],
                )

                target_row = cursor.fetchone()

                if target_row is None:
                    abort(404)

                if target_row[0] != "ban_nhap":
                    flash(
                        "Không thể chuyển câu hỏi vào "
                        "bài tập đã xuất bản hoặc lưu trữ.",
                        "error",
                    )

                    return redirect(
                        index_url(edit=question_id)
                    )

                # Nếu chuyển sang bài tập khác
                if old_exercise_id != form["exercise_id"]:
                    cursor.execute(
                        """
                        SELECT ISNULL(MAX(ThuTu), 0) + 1
                        FROM dbo.CauHoi
                        WHERE MaBaiTap = ?;
                        """,
                        form["exercise_id"],
                    )

                    current_order = int(
                        cursor.fetchone()[0] or 1
                    )

                # Cập nhật câu hỏi và audit
                cursor.execute(
                    """
                    UPDATE dbo.CauHoi
                    SET
                        MaBaiTap = ?,
                        LoaiCauHoi = ?,
                        KyNang = ?,
                        NoiDungCauHoi = ?,
                        DoanVan = ?,
                        MaTep = ?,
                        DapAnJson = ?,
                        GiaiThich = ?,
                        DiemToiDa = ?,
                        ThuTu = ?,
                        MaQuanTriVienCapNhat = ?,
                        NgayCapNhat = SYSDATETIME()
                    WHERE MaCauHoi = ?;
                    """,
                    form["exercise_id"],
                    form["question_type"],
                    form["skill"],
                    form["content"],
                    form["passage"] or None,
                    form["media_id"],
                    answer_json,
                    form["explanation"] or None,
                    max_score,
                    current_order,
                    admin_id,
                    question_id,
                )

                # Xóa lựa chọn cũ
                cursor.execute(
                    """
                    DELETE FROM dbo.LuaChonCauHoi
                    WHERE MaCauHoi = ?;
                    """,
                    question_id,
                )

                # Thêm lựa chọn mới
                for choice in choices:
                    cursor.execute(
                        """
                        INSERT INTO dbo.LuaChonCauHoi
                        (
                            MaCauHoi,
                            NoiDungLuaChon,
                            LaDapAnDung,
                            ThuTu
                        )
                        VALUES (?, ?, ?, ?);
                        """,
                        question_id,
                        choice["text"],
                        1 if choice["correct"] else 0,
                        choice["order"],
                    )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    flash(
        "Đã cập nhật câu hỏi thành công.",
        "success",
    )

    return redirect(
        url_for(
            "admin_questions.index",
            exercise_id=form["exercise_id"],
        )
    )


# ============================================================
# SẮP XẾP THỨ TỰ CÂU HỎI
# ============================================================

@admin_questions_bp.post(
    "/bai-tap/<int:exercise_id>/thu-tu"
)
def reorder(exercise_id):
    admin_id = get_admin_id()

    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:
                # Kiểm tra bài tập
                cursor.execute(
                    """
                    SELECT TrangThai
                    FROM dbo.BaiTap WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaBaiTap = ?;
                    """,
                    exercise_id,
                )

                exercise_row = cursor.fetchone()

                if exercise_row is None:
                    abort(404)

                if exercise_row[0] != "ban_nhap":
                    flash(
                        "Chỉ được sắp xếp câu hỏi "
                        "của bài tập Bản nháp.",
                        "error",
                    )

                    return redirect(
                        url_for(
                            "admin_questions.index",
                            exercise_id=exercise_id,
                        )
                    )

                # Lấy tất cả câu hỏi của bài tập
                cursor.execute(
                    """
                    SELECT
                        MaCauHoi,
                        ThuTu
                    FROM dbo.CauHoi WITH (UPDLOCK, HOLDLOCK)
                    WHERE MaBaiTap = ?
                    ORDER BY
                        ThuTu,
                        MaCauHoi;
                    """,
                    exercise_id,
                )

                rows = cursor.fetchall()

                if len(rows) < 2:
                    flash(
                        "Bài tập chưa đủ câu hỏi để sắp xếp.",
                        "error",
                    )

                    return redirect(
                        url_for(
                            "admin_questions.index",
                            exercise_id=exercise_id,
                        )
                    )

                if len(rows) > PAGE_SIZE:
                    flash(
                        "Bài tập có hơn 25 câu hỏi. "
                        "Không thể sắp xếp toàn bộ "
                        "trên một trang.",
                        "error",
                    )

                    return redirect(
                        url_for(
                            "admin_questions.index",
                            exercise_id=exercise_id,
                        )
                    )

                # Kiểm tra lịch sử làm bài
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChiTietBaiLam AS ct

                    INNER JOIN dbo.CauHoi AS ch
                        ON ch.MaCauHoi = ct.MaCauHoi

                    WHERE ch.MaBaiTap = ?;
                    """,
                    exercise_id,
                )

                history_count = int(
                    cursor.fetchone()[0] or 0
                )

                if history_count > 0:
                    flash(
                        "Bài tập đã có lịch sử làm bài. "
                        "Không thể thay đổi thứ tự câu hỏi.",
                        "error",
                    )

                    return redirect(
                        url_for(
                            "admin_questions.index",
                            exercise_id=exercise_id,
                        )
                    )

                # Đọc thứ tự mới từ HTML
                new_orders = {}

                for row in rows:
                    question_id = int(row[0])

                    raw_order = request.form.get(
                        f"question_order_{question_id}",
                        "",
                    ).strip()

                    try:
                        new_order = int(raw_order)
                    except ValueError:
                        flash(
                            "Thứ tự phải là số nguyên.",
                            "error",
                        )

                        return redirect(
                            url_for(
                                "admin_questions.index",
                                exercise_id=exercise_id,
                            )
                        )

                    new_orders[question_id] = new_order

                # Thứ tự phải liên tục từ 1 đến N
                expected = set(
                    range(1, len(rows) + 1)
                )

                if set(new_orders.values()) != expected:
                    flash(
                        "Thứ tự phải liên tục từ 1 đến "
                        f"{len(rows)}, không được trùng số.",
                        "error",
                    )

                    return redirect(
                        url_for(
                            "admin_questions.index",
                            exercise_id=exercise_id,
                        )
                    )

                # Xác định câu thực sự thay đổi
                changed = [
                    (
                        int(row[0]),
                        new_orders[int(row[0])],
                    )
                    for row in rows
                    if int(row[1]) != new_orders[int(row[0])]
                ]

                if changed:
                    # ========================================
                    # BƯỚC 1: ĐƯA THỨ TỰ SANG VÙNG TẠM
                    # ========================================

                    cursor.execute(
                        """
                        SELECT ISNULL(MAX(ThuTu), 0)
                        FROM dbo.CauHoi
                        WHERE MaBaiTap = ?;
                        """,
                        exercise_id,
                    )

                    max_order = int(
                        cursor.fetchone()[0] or 0
                    )

                    # Dùng khoảng tạm lớn hơn giá trị
                    # hiện tại để tránh đụng thứ tự cũ.
                    temp_offset = max_order + len(rows) + 1

                    # Cập nhật từng câu, tránh lỗi UNIQUE
                    # có thể phát sinh với UPDATE hàng loạt.
                    for row in rows:
                        cursor.execute(
                            """
                            UPDATE dbo.CauHoi
                            SET ThuTu = ThuTu + ?
                            WHERE
                                MaCauHoi = ?
                                AND MaBaiTap = ?;
                            """,
                            temp_offset,
                            int(row[0]),
                            exercise_id,
                        )

                    # ========================================
                    # BƯỚC 2: GÁN THỨ TỰ MỚI
                    # ========================================

                    for row in rows:
                        question_id = int(row[0])
                        old_order = int(row[1])
                        new_order = new_orders[question_id]

                        if old_order != new_order:
                            # Có đổi vị trí -> ghi audit
                            cursor.execute(
                                """
                                UPDATE dbo.CauHoi
                                SET
                                    ThuTu = ?,
                                    MaQuanTriVienCapNhat = ?,
                                    NgayCapNhat = SYSDATETIME()
                                WHERE
                                    MaCauHoi = ?
                                    AND MaBaiTap = ?;
                                """,
                                new_order,
                                admin_id,
                                question_id,
                                exercise_id,
                            )

                        else:
                            # Không đổi vị trí -> không ghi audit
                            cursor.execute(
                                """
                                UPDATE dbo.CauHoi
                                SET ThuTu = ?
                                WHERE
                                    MaCauHoi = ?
                                    AND MaBaiTap = ?;
                                """,
                                old_order,
                                question_id,
                                exercise_id,
                            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    flash(
        "Đã cập nhật thứ tự câu hỏi.",
        "success",
    )

    return redirect(
        url_for(
            "admin_questions.index",
            exercise_id=exercise_id,
        )
    )


# ============================================================
# XÓA CÂU HỎI AN TOÀN
# ============================================================

@admin_questions_bp.post("/<int:question_id>/xoa")
def delete(question_id):
    with closing(get_connection()) as connection:
        try:
            with closing(connection.cursor()) as cursor:
                # Kiểm tra câu hỏi và trạng thái bài tập
                cursor.execute(
                    """
                    SELECT
                        ch.MaBaiTap,
                        ch.NoiDungCauHoi,
                        bt.TrangThai
                    FROM dbo.CauHoi AS ch
                    WITH (UPDLOCK, HOLDLOCK)

                    INNER JOIN dbo.BaiTap AS bt
                        ON bt.MaBaiTap = ch.MaBaiTap

                    WHERE ch.MaCauHoi = ?;
                    """,
                    question_id,
                )

                row = cursor.fetchone()

                if row is None:
                    abort(
                        404,
                        description="Không tìm thấy câu hỏi.",
                    )

                exercise_id = int(row[0])
                question_content = row[1] or ""
                exercise_status = row[2]

                # Chỉ xóa câu hỏi thuộc bài nháp
                if exercise_status != "ban_nhap":
                    flash(
                        "Chỉ được xóa câu hỏi "
                        "của bài tập Bản nháp.",
                        "error",
                    )

                    return redirect(index_url())

                # Kiểm tra lịch sử làm bài
                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM dbo.ChiTietBaiLam
                    WHERE MaCauHoi = ?;
                    """,
                    question_id,
                )

                history_count = int(
                    cursor.fetchone()[0] or 0
                )

                if history_count > 0:
                    flash(
                        "Không thể xóa vì câu hỏi đã có "
                        "lịch sử làm bài của người học.",
                        "error",
                    )

                    return redirect(index_url())

                # Xóa các lựa chọn
                cursor.execute(
                    """
                    DELETE FROM dbo.LuaChonCauHoi
                    WHERE MaCauHoi = ?;
                    """,
                    question_id,
                )

                # Xóa câu hỏi
                cursor.execute(
                    """
                    DELETE FROM dbo.CauHoi
                    WHERE MaCauHoi = ?;
                    """,
                    question_id,
                )

                # Lấy các câu còn lại
                cursor.execute(
                    """
                    SELECT
                        MaCauHoi,
                        ThuTu
                    FROM dbo.CauHoi
                    WHERE MaBaiTap = ?
                    ORDER BY
                        ThuTu,
                        MaCauHoi;
                    """,
                    exercise_id,
                )

                remaining = cursor.fetchall()

                # Chuẩn hóa thứ tự, chỉ cập nhật
                # những câu thực sự thay đổi vị trí.
                admin_id = get_admin_id()

                for new_order, remaining_row in enumerate(
                    remaining,
                    start=1,
                ):
                    old_order = int(remaining_row[1])

                    if old_order == new_order:
                        continue

                    cursor.execute(
                        """
                        UPDATE dbo.CauHoi
                        SET
                            ThuTu = ?,
                            MaQuanTriVienCapNhat = ?,
                            NgayCapNhat = SYSDATETIME()
                        WHERE MaCauHoi = ?;
                        """,
                        new_order,
                        admin_id,
                        remaining_row[0],
                    )

            connection.commit()

        except pyodbc.IntegrityError:
            connection.rollback()

            flash(
                "Không thể xóa câu hỏi vì vẫn còn "
                "dữ liệu liên kết trong SQL.",
                "error",
            )

            return redirect(index_url())

        except Exception:
            connection.rollback()
            raise

    flash(
        "Đã xóa câu hỏi: "
        + question_content[:60],
        "success",
    )

    return redirect(index_url())