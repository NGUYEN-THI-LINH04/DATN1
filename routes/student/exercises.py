
# -*- coding: utf-8 -*-
"""Mộc Hán - Bài tập Student. Sử dụng schema SQL Server hiện tại."""

import hashlib
import hmac
import json
import random
import unicodedata

from contextlib import closing
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

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

from itsdangerous import (
    BadSignature,
    SignatureExpired,
    URLSafeTimedSerializer,
)

from database import get_connection


# ============================================================
# CẤU HÌNH
# ============================================================

student_exercises_bp = Blueprint(
    "student_exercises",
    __name__,
    url_prefix="/student/exercises",
)


SUPPORTED_TYPES = {
    "chon_mot",
    "chon_nhieu",
    "dung_sai",
    "dien_tu",
    "sap_xep",
    "ghep_cap",
    "viet_ngan",
}

TYPE_LABELS = {
    "chon_mot": "Chọn một đáp án",
    "chon_nhieu": "Chọn nhiều đáp án",
    "dung_sai": "Đúng / Sai",
    "dien_tu": "Điền từ",
    "sap_xep": "Sắp xếp câu",
    "ghep_cap": "Ghép cặp",
    "viet_ngan": "Viết ngắn",
}


MAX_QUESTIONS = 200
MAX_TOKEN_AGE = 4 * 60 * 60
CENT = Decimal("0.01")


# ============================================================
# HELPER
# ============================================================

def records(cursor):
    cols = [
        col[0]
        for col in cursor.description
    ]

    return [
        dict(zip(cols, row))
        for row in cursor.fetchall()
    ]


def one(cursor):
    cols = [
        col[0]
        for col in cursor.description
    ]

    row = cursor.fetchone()

    return (
        dict(zip(cols, row))
        if row
        else None
    )


def parse_json(value, default=None):
    if isinstance(value, (dict, list)):
        return value

    try:
        return (
            json.loads(value)
            if value is not None
            else default
        )
    except (TypeError, ValueError):
        return default


def as_json(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    )


def amount(value):
    return Decimal(
        str(value or 0)
    ).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def num(value):
    return float(amount(value))


def positive_int(value):
    if isinstance(value, bool):
        return None

    try:
        n = int(value)
    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None

    return n if n > 0 else None


def clean_text(value):
    text = unicodedata.normalize(
        "NFC",
        str(value or ""),
    )

    return " ".join(
        text.casefold().split()
    )


def response_error(message, code=400):
    return jsonify(
        success=False,
        message=message,
    ), code


# ============================================================
# QUYỀN STUDENT
# ============================================================

@student_exercises_bp.before_request
def require_student():
    account = getattr(
        g,
        "account",
        None,
    )

    if not account:
        if request.path.startswith(
            "/student/exercises/api/"
        ):
            return response_error(
                "Bạn cần đăng nhập để làm bài.",
                401,
            )

        return redirect(
            url_for("auth.login")
        )

    if account.get("role") != "student":
        abort(403)


def student_id():
    user_id = positive_int(
        g.account.get("id")
    )

    if not user_id:
        abort(403)

    return user_id


@student_exercises_bp.errorhandler(pyodbc.Error)
def sql_error(error):
    current_app.logger.exception(
        "Lỗi SQL Student Exercises"
    )

    if request.path.startswith(
        "/student/exercises/api/"
    ):
        return response_error(
            "Không thể kết nối hoặc xử lý "
            "dữ liệu SQL Server.",
            503,
        )

    return (
        "Không thể tải trang bài tập.",
        503,
    )


# ============================================================
# TOKEN LƯỢT LÀM
# ============================================================

def serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="moc-han-exercise-attempt-v2",
    )


def make_token(attempt_id):
    return serializer().dumps({
        "attempt_id": attempt_id,
        "user_id": student_id(),
    })


def token_attempt_id(token):
    if not isinstance(token, str):
        return None

    try:
        data = serializer().loads(
            token,
            max_age=MAX_TOKEN_AGE,
        )

    except (
        BadSignature,
        SignatureExpired,
    ):
        return None

    if not isinstance(data, dict):
        return None

    if data.get("user_id") != student_id():
        return None

    return positive_int(
        data.get("attempt_id")
    )


# ============================================================
# LẤY BÀI TẬP ĐÃ XUẤT BẢN
# ============================================================

def exercise(cursor, exercise_id):
    cursor.execute(
        """
        SELECT
            bt.MaBaiTap,
            bt.MaBaiHoc,
            bt.TieuDe,
            bt.HuongDan,
            bt.ThoiGianGioiHanGiay,
            bt.PhanTramDat,
            bh.SoThuTuBai,
            bh.TieuDe AS TenBaiHoc,
            kh.MaCapDo

        FROM dbo.BaiTap AS bt

        JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = bt.MaBaiHoc

        JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc = bh.MaKhoaHoc

        WHERE bt.MaBaiTap = ?
          AND bt.TrangThai = 'da_xuat_ban';
        """,
        exercise_id,
    )

    return one(cursor)


def levels(cursor):
    cursor.execute(
        """
        SELECT DISTINCT
            kh.MaCapDo

        FROM dbo.KhoaHoc AS kh

        JOIN dbo.BaiHoc AS bh
            ON bh.MaKhoaHoc = kh.MaKhoaHoc

        JOIN dbo.BaiTap AS bt
            ON bt.MaBaiHoc = bh.MaBaiHoc

        WHERE bt.TrangThai = 'da_xuat_ban'

        ORDER BY kh.MaCapDo;
        """
    )

    return [
        row["MaCapDo"]
        for row in records(cursor)
    ]


# ============================================================
# DANH SÁCH BÀI TẬP
# ============================================================

def exercise_list(cursor, level=None):
    level_where = (
        " AND kh.MaCapDo = ?"
        if level is not None
        else ""
    )

    sql = """
        SELECT
            bt.MaBaiTap,
            bt.MaBaiHoc,
            bt.TieuDe,
            bt.HuongDan,
            bt.ThoiGianGioiHanGiay,
            bt.PhanTramDat,

            bh.SoThuTuBai,
            bh.TieuDe AS TenBaiHoc,

            kh.MaCapDo,

            (
                SELECT COUNT(*)
                FROM dbo.CauHoi AS ch
                WHERE ch.MaBaiTap = bt.MaBaiTap
            ) AS SoCauHoi,

            (
                SELECT COUNT(*)
                FROM dbo.CauHoi AS ch
                WHERE ch.MaBaiTap = bt.MaBaiTap
                  AND (
                    ch.LoaiCauHoi NOT IN (
                        'chon_mot',
                        'chon_nhieu',
                        'dung_sai',
                        'dien_tu',
                        'sap_xep',
                        'ghep_cap',
                        'viet_ngan'
                    )
                    OR ch.MaTep IS NOT NULL
                  )
            ) AS SoCauChuaHoTro,

            (
                SELECT COUNT(*)
                FROM dbo.LanLamBai AS llb
                WHERE llb.MaBaiTap = bt.MaBaiTap
                  AND llb.MaNguoiDung = ?
                  AND llb.TrangThai = 'da_cham'
            ) AS SoLanDaLam

        FROM dbo.BaiTap AS bt

        JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = bt.MaBaiHoc

        JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc = bh.MaKhoaHoc

        WHERE bt.TrangThai = 'da_xuat_ban'
    """

    sql += level_where

    sql += """
        ORDER BY
            kh.MaCapDo,
            bh.SoThuTuBai,
            bt.MaBaiTap;
    """

    params = [student_id()]

    if level is not None:
        params.append(level)

    cursor.execute(
        sql,
        *params,
    )

    data = records(cursor)

    for row in data:
        count = int(
            row["SoCauHoi"] or 0
        )

        unsupported = int(
            row["SoCauChuaHoTro"] or 0
        )

        row["CoTheLam"] = (
            0 < count <= MAX_QUESTIONS
            and unsupported == 0
        )

    return data


# ============================================================
# CÂU HỎI DO ADMIN TẠO
# ============================================================

def questions_from_admin(cursor, exercise_id):
    cursor.execute(
        """
        SELECT
            MaCauHoi,
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

        WHERE MaBaiTap = ?

        ORDER BY
            ThuTu,
            MaCauHoi;
        """,
        exercise_id,
    )

    qs = records(cursor)

    for q in qs:
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
            q["MaCauHoi"],
        )

        q["choices"] = records(cursor)

        q["answer_data"] = parse_json(
            q["DapAnJson"],
            {},
        )

    return qs


# ============================================================
# KIỂM TRA CÂU HỎI CÓ THỂ CHẤM
# ============================================================

def validate_question(q):
    typ = q["LoaiCauHoi"]

    # Hiện JS chưa có phần phát media thực tế.
    if (
        typ not in SUPPORTED_TYPES
        or q["MaTep"] is not None
    ):
        return False

    if (
        not (q["NoiDungCauHoi"] or "").strip()
        or amount(q["DiemToiDa"]) <= 0
    ):
        return False

    data = q["answer_data"]

    if not isinstance(data, dict):
        return False

    if typ in ("chon_mot", "chon_nhieu"):
        correct = sum(
            bool(c["LaDapAnDung"])
            for c in q["choices"]
        )

        if len(q["choices"]) < 2:
            return False

        if typ == "chon_mot":
            return correct == 1

        return correct >= 1

    if typ == "dung_sai":
        return data.get("answer") in (
            "dung",
            "sai",
        )

    if typ == "dien_tu":
        answers = data.get("answers")

        return (
            isinstance(answers, list)
            and any(
                isinstance(v, str) and v.strip()
                for v in answers
            )
        )

    if typ == "sap_xep":
        items = data.get("items")

        return (
            isinstance(items, list)
            and 2 <= len(items) <= 60
            and all(
                isinstance(v, str) and v.strip()
                for v in items
            )
        )
    
    # GHÉP CẶP
    if typ == "ghep_cap":
        pairs = data.get("pairs")

        return (
            isinstance(pairs, list)
            and 2 <= len(pairs) <= 60
            and all(
                isinstance(pair, dict)
                and isinstance(pair.get("left"), str)
                and isinstance(pair.get("right"), str)
                and pair["left"].strip()
                and pair["right"].strip()
                for pair in pairs
            )
            and len({
                clean_text(pair["left"])
                for pair in pairs
            }) == len(pairs)
        )

    # VIẾT NGẮN
    if typ == "viet_ngan":
        sample = data.get("sample_answer")
        alternatives = data.get("accepted_answers", [])

        return (
            isinstance(sample, str)
            and bool(sample.strip())
            and isinstance(alternatives, list)
            and all(
                isinstance(item, str)
                for item in alternatives
            )
        )

    return False


# ============================================================
# TRỘN TỪ CHO CÂU SẮP XẾP
#
# Server biết thứ tự đúng.
# Trình duyệt chỉ nhận danh sách đã trộn.
# ============================================================

def shuffled_items(items, attempt_id, question_id):
    secret = str(
        current_app.config["SECRET_KEY"]
    ).encode("utf-8")

    digest = hmac.new(
        secret,
        f"{attempt_id}:{question_id}".encode(),
        hashlib.sha256,
    ).digest()

    indices = list(
        range(len(items))
    )

    rng = random.Random(
        int.from_bytes(digest, "big")
    )

    rng.shuffle(indices)

    # Không để nguyên thứ tự nếu trộn
    # tình cờ ra đúng vị trí ban đầu.
    if (
        len(indices) > 1
        and indices == list(range(len(indices)))
    ):
        indices[0], indices[-1] = (
            indices[-1],
            indices[0],
        )

    return [
        items[index]
        for index in indices
    ]


# ============================================================
# CHỤP CÂU HỎI TẠI THỜI ĐIỂM BẮT ĐẦU
# ============================================================

def make_snapshot(q, attempt_id):
    snap = {
        "id": int(q["MaCauHoi"]),
        "type": q["LoaiCauHoi"],
        "skill": q["KyNang"],
        "content": q["NoiDungCauHoi"],
        "passage": q["DoanVan"],
        "explanation": q["GiaiThich"],
        "max_score": num(q["DiemToiDa"]),
        "order": int(q["ThuTu"]),
        "answer_data": q["answer_data"],

        "choices": [
            {
                "id": int(c["MaLuaChon"]),
                "text": c["NoiDungLuaChon"],
                "correct": bool(c["LaDapAnDung"]),
                "order": int(c["ThuTu"]),
            }
            for c in q["choices"]
        ],
    }

    if q["LoaiCauHoi"] == "sap_xep":
        snap["presentation_items"] = shuffled_items(
            q["answer_data"]["items"],
            attempt_id,
            q["MaCauHoi"],
        )

    return snap


# ============================================================
# DỮ LIỆU CÔNG KHAI CHO TRÌNH DUYỆT
#
# Không gửi đáp án và giải thích khi chưa nộp.
# ============================================================

def public_snapshot(snap):
    return {
        "id": snap["id"],
        "type": snap["type"],

        "type_label": TYPE_LABELS.get(
            snap["type"],
            "Câu hỏi",
        ),

        "skill": snap["skill"],
        "content": snap["content"],
        "passage": snap["passage"],

        "media_id": None,
        "max_score": snap["max_score"],
        "order": snap["order"],

        "choices": [
            {
                "id": c["id"],
                "text": c["text"],
                "order": c["order"],
            }
            for c in snap["choices"]
        ],

        "items": snap.get(
            "presentation_items",
            [],
        ),
    
        "left_items": (
            [
                pair["left"]
                for pair in snap["answer_data"]["pairs"]
            ]
            if snap["type"] == "ghep_cap"
            else []
        ),

        "right_items": (
            shuffled_items(
                [
                    pair["right"]
                    for pair in snap["answer_data"]["pairs"]
                ],
                0,
                snap["id"],
            )
            if snap["type"] == "ghep_cap"
            else []
        ),

    }


# ============================================================
# CHẤM ĐIỂM
# ============================================================

def grade(snap, answer):
    typ = snap["type"]

    choices = snap["choices"]
    data = snap["answer_data"]

    correct = False

    # --------------------------------------------------------
    # CHỌN MỘT
    # --------------------------------------------------------

    if typ == "chon_mot":
        expected = {
            c["id"]
            for c in choices
            if c["correct"]
        }

        selected = positive_int(answer)

        correct = (
            selected is not None
            and {selected} == expected
        )

    # --------------------------------------------------------
    # CHỌN NHIỀU
    # --------------------------------------------------------

    elif typ == "chon_nhieu":
        expected = {
            c["id"]
            for c in choices
            if c["correct"]
        }

        if isinstance(answer, list):
            selected = [
                positive_int(v)
                for v in answer
            ]

            correct = (
                all(v is not None for v in selected)
                and len(set(selected)) == len(selected)
                and set(selected) == expected
            )

    # --------------------------------------------------------
    # ĐÚNG / SAI
    # --------------------------------------------------------

    elif typ == "dung_sai":
        correct = (
            answer in ("dung", "sai")
            and answer == data.get("answer")
        )

    # --------------------------------------------------------
    # ĐIỀN TỪ
    # --------------------------------------------------------

    elif typ == "dien_tu":
        correct = (
            isinstance(answer, str)
            and bool(clean_text(answer))
            and any(
                clean_text(answer) == clean_text(candidate)
                for candidate in data["answers"]
            )
        )

    # --------------------------------------------------------
    # SẮP XẾP CÂU
    #
    # answer chứa vị trí từ trong mảng đã trộn.
    # Khôi phục câu người học tạo rồi so sánh.
    # --------------------------------------------------------

    elif (
        typ == "sap_xep"
        and isinstance(answer, list)
    ):
        presented = snap["presentation_items"]

        valid = (
            len(answer) == len(presented)
            and all(
                type(v) is int
                for v in answer
            )
            and sorted(answer) == list(
                range(len(presented))
            )
        )

        if valid:
            arranged = [
                presented[i]
                for i in answer
            ]

            correct = (
                arranged == data["items"]
            )
    
    # --------------------------------------------------------
    # GHÉP CẶP
    # answer: danh sách các cặp {"left": ..., "right": ...}
    # --------------------------------------------------------

    elif typ == "ghep_cap":
        expected_pairs = data.get("pairs", [])

        if isinstance(answer, list):
            expected = {
                clean_text(pair["left"]): clean_text(pair["right"])
                for pair in expected_pairs
            }

            submitted = {}

            valid = len(answer) == len(expected)

            if valid:
                for pair in answer:
                    if not isinstance(pair, dict):
                        valid = False
                        break

                    left = pair.get("left")
                    right = pair.get("right")

                    if not isinstance(left, str) or not isinstance(right, str):
                        valid = False
                        break

                    left_key = clean_text(left)
                    right_value = clean_text(right)

                    if (
                        not left_key
                        or not right_value
                        or left_key in submitted
                    ):
                        valid = False
                        break

                    submitted[left_key] = right_value

            correct = valid and submitted == expected

    # --------------------------------------------------------
    # VIẾT NGẮN
    # So khớp đáp án mẫu hoặc các đáp án được chấp nhận.
    # --------------------------------------------------------

    elif typ == "viet_ngan":
        if isinstance(answer, str):
            sample = data.get("sample_answer", "")
            alternatives = data.get("accepted_answers", [])

            if not isinstance(alternatives, list):
                alternatives = []

            accepted = [
                sample,
                *[
                    item
                    for item in alternatives
                    if isinstance(item, str)
                ],
            ]

            normalized_answer = clean_text(answer)

            correct = (
                bool(normalized_answer)
                and any(
                    normalized_answer == clean_text(candidate)
                    for candidate in accepted
                )
            )

    maximum = amount(
        snap["max_score"]
    )

    points = (
        maximum
        if correct
        else Decimal("0.00")
    )

    return (
        correct,
        points,
        maximum,
    )


# ============================================================
# NHẬN DIỆN CÂU ĐÃ TRẢ LỜI
# ============================================================

def answered(snap, answer):
    if answer is None:
        return False

    if isinstance(answer, str):
        return bool(answer.strip())

    if isinstance(answer, list):
        return bool(answer)

    return True


# ============================================================
# HIỂN THỊ ĐÁP ÁN TRONG TRANG KẾT QUẢ
# ============================================================

def answer_display(snap, answer):
    typ = snap["type"]

    if not answered(snap, answer):
        return None

    if typ in ("chon_mot", "chon_nhieu"):
        ids = (
            answer
            if isinstance(answer, list)
            else [answer]
        )

        texts = [
            str(c["text"])
            for c in snap["choices"]
            if c["id"] in ids
        ]

        return (
            " · ".join(texts)
            or "Không hợp lệ"
        )

    if typ == "dung_sai":
        if answer == "dung":
            return "Đúng"

        if answer == "sai":
            return "Sai"

        return "Không hợp lệ"

    if typ == "dien_tu":
        return str(answer)

    if typ == "sap_xep":
        arr = snap.get(
            "presentation_items",
            [],
        )

        if (
            isinstance(answer, list)
            and all(
                type(i) is int
                and 0 <= i < len(arr)
                for i in answer
            )
        ):
            return " ".join(
                arr[i]
                for i in answer
            )
    
    if typ == "ghep_cap":
        if isinstance(answer, list):
            pairs = []

            for pair in answer:
                if not isinstance(pair, dict):
                    return "Không hợp lệ"

                left = pair.get("left")
                right = pair.get("right")

                if not isinstance(left, str) or not isinstance(right, str):
                    return "Không hợp lệ"

                pairs.append(f"{left} → {right}")

            return " | ".join(pairs) or "Chưa trả lời"

        return "Không hợp lệ"

    if typ == "viet_ngan":
        return str(answer)

    return "Không hợp lệ"


def correct_display(snap):
    typ = snap["type"]
    data = snap["answer_data"]

    if typ in ("chon_mot", "chon_nhieu"):
        return " · ".join(
            str(c["text"])
            for c in snap["choices"]
            if c["correct"]
        )

    if typ == "dung_sai":
        return (
            "Đúng"
            if data.get("answer") == "dung"
            else "Sai"
        )

    if typ == "dien_tu":
        return " / ".join(
            data.get("answers", [])
        )

    if typ == "sap_xep":
        return " ".join(
            data.get("items", [])
        )
    
    if typ == "ghep_cap":
        pairs = data.get("pairs", [])

        return " | ".join(
            f"{pair['left']} → {pair['right']}"
            for pair in pairs
        )

    if typ == "viet_ngan":
        return str(data.get("sample_answer", ""))

    return ""


# ============================================================
# TRANG DANH SÁCH BÀI TẬP
# ============================================================

@student_exercises_bp.get("/")
def index():
    level = request.args.get(
        "hsk",
        type=int,
    )

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cur:
            all_levels = levels(cur)

            items = exercise_list(
                cur,
                level,
            )

    return render_template(
        "student/exercise.html",
        levels=all_levels,
        exercises=items,
        selected_level=level,
    )


# ============================================================
# API DANH SÁCH
# ============================================================

@student_exercises_bp.get("/api/exercises")
def api_exercises():
    level = request.args.get(
        "hsk",
        type=int,
    )

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cur:
            items = exercise_list(
                cur,
                level,
            )

    return jsonify(
        success=True,
        exercises=items,
    )


# ============================================================
# BẮT ĐẦU LÀM BÀI
#
# Tạo LanLamBai = dang_thuc_hien
# Tạo ChiTietBaiLam với điểm NULL
# ============================================================

@student_exercises_bp.post(
    "/api/exercises/<int:exercise_id>/start"
)
def api_start(exercise_id):
    with closing(get_connection()) as conn:
        try:
            with closing(conn.cursor()) as cur:
                ex = exercise(
                    cur,
                    exercise_id,
                )

                if not ex:
                    return response_error(
                        "Bài tập không tồn tại "
                        "hoặc chưa xuất bản.",
                        404,
                    )

                qs = questions_from_admin(
                    cur,
                    exercise_id,
                )

                valid = (
                    0 < len(qs) <= MAX_QUESTIONS
                    and all(
                        validate_question(q)
                        for q in qs
                    )
                )

                if not valid:
                    return response_error(
                        "Bài tập thiếu đáp án hợp lệ, "
                        "chứa media hoặc dạng câu hỏi "
                        "chưa được hỗ trợ."
                    )

                maximum = sum(
                    (
                        amount(q["DiemToiDa"])
                        for q in qs
                    ),
                    Decimal("0.00"),
                )

                # Tạo lượt làm thật.
                cur.execute(
                    """
                    INSERT INTO dbo.LanLamBai
                    (
                        MaNguoiDung,
                        MaBaiTap,
                        NgayBatDau,
                        NgayNop,
                        TrangThai,
                        Diem,
                        DiemToiDaLucLam
                    )

                    OUTPUT INSERTED.MaLanLamBai

                    VALUES
                    (
                        ?,
                        ?,
                        SYSUTCDATETIME(),
                        NULL,
                        'dang_thuc_hien',
                        NULL,
                        ?
                    );
                    """,
                    student_id(),
                    exercise_id,
                    maximum,
                )

                attempt_id = int(
                    cur.fetchone()[0]
                )

                snaps = [
                    make_snapshot(q, attempt_id)
                    for q in qs
                ]

                # Lưu bản chụp từng câu trước khi làm.
                for snap in snaps:
                    cur.execute(
                        """
                        INSERT INTO dbo.ChiTietBaiLam
                        (
                            MaLanLamBai,
                            MaBaiTap,
                            MaCauHoi,
                            CauTraLoiJson,
                            BanChupCauHoiJson,
                            DiemToiDaLucLam,
                            Diem,
                            LaDapAnDung,
                            CachChamDiem,
                            GopY
                        )

                        VALUES
                        (
                            ?,
                            ?,
                            ?,
                            NULL,
                            ?,
                            ?,
                            NULL,
                            NULL,
                            NULL,
                            NULL
                        );
                        """,
                        attempt_id,
                        exercise_id,
                        snap["id"],
                        as_json(snap),
                        amount(snap["max_score"]),
                    )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    return jsonify(
        success=True,

        attempt_token=make_token(
            attempt_id
        ),

        exercise={
            "id": ex["MaBaiTap"],
            "title": ex["TieuDe"],
            "instruction": ex["HuongDan"],
            "hsk": ex["MaCapDo"],
            "lesson": ex["TenBaiHoc"],

            "time_limit_seconds": ex[
                "ThoiGianGioiHanGiay"
            ],

            "pass_percent": num(
                ex["PhanTramDat"]
            ),
        },

        questions=[
            public_snapshot(snap)
            for snap in snaps
        ],
    )


# ============================================================
# NỘP BÀI
#
# Chỉ cập nhật lượt đã tạo.
# Không INSERT một LanLamBai mới khi nộp.
# ============================================================

@student_exercises_bp.post(
    "/api/exercises/<int:exercise_id>/submit"
)
def api_submit(exercise_id):
    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):
        return response_error(
            "Dữ liệu nộp bài không hợp lệ."
        )

    attempt_id = token_attempt_id(
        data.get("attempt_token")
    )

    if not attempt_id:
        return response_error(
            "Phiên làm bài không hợp lệ "
            "hoặc đã hết hạn."
        )

    posted = data.get("answers")

    if (
        not isinstance(posted, list)
        or len(posted) > MAX_QUESTIONS
    ):
        return response_error(
            "Danh sách câu trả lời không hợp lệ."
        )

    answers = {}

    for item in posted:
        if not isinstance(item, dict):
            return response_error(
                "Câu trả lời không đúng định dạng."
            )

        qid = positive_int(
            item.get("question_id")
        )

        if not qid or qid in answers:
            return response_error(
                "Mã câu hỏi sai hoặc bị trùng."
            )

        answers[qid] = item.get("answer")

    with closing(get_connection()) as conn:
        try:
            with closing(conn.cursor()) as cur:

                # Khóa lượt làm để tránh nộp đồng thời.
                cur.execute(
                    """
                    SELECT
                        MaLanLamBai,
                        MaBaiTap,
                        TrangThai,
                        NgayBatDau,
                        DiemToiDaLucLam

                    FROM dbo.LanLamBai
                        WITH (UPDLOCK, HOLDLOCK)

                    WHERE MaLanLamBai = ?
                      AND MaNguoiDung = ?
                      AND MaBaiTap = ?;
                    """,
                    attempt_id,
                    student_id(),
                    exercise_id,
                )

                attempt = one(cur)

                if not attempt:
                    return response_error(
                        "Không tìm thấy lượt làm bài.",
                        404,
                    )

                # Đã nộp thì trả về kết quả cũ.
                # Không tạo bản ghi thứ hai.
                if attempt["TrangThai"] == "da_cham":
                    return jsonify(
                        success=True,
                        attempt_id=attempt_id,
                        result_url=url_for(
                            "student_exercises.result_page",
                            attempt_id=attempt_id,
                        ),
                        message=(
                            "Lượt làm này đã nộp trước đó."
                        ),
                    )

                if attempt["TrangThai"] != "dang_thuc_hien":
                    return response_error(
                        "Lượt làm đang được xử lý.",
                        409,
                    )

                elapsed = (
                    datetime.utcnow()
                    - attempt["NgayBatDau"]
                ).total_seconds()

                if (
                    elapsed < -30
                    or elapsed > MAX_TOKEN_AGE
                ):
                    return response_error(
                        "Lượt làm đã hết hạn. "
                        "Vui lòng bắt đầu lại."
                    )

                ex = exercise(
                    cur,
                    exercise_id,
                )

                if not ex:
                    return response_error(
                        "Bài tập hiện không còn "
                        "được xuất bản.",
                        409,
                    )

                limit = ex[
                    "ThoiGianGioiHanGiay"
                ]

                if (
                    limit is not None
                    and elapsed > int(limit) + 30
                ):
                    return response_error(
                        "Đã hết thời gian làm bài."
                    )

                # Lấy bản chụp tại thời điểm
                # người học bắt đầu, không lấy
                # đáp án Admin hiện tại để chấm.
                cur.execute(
                    """
                    SELECT
                        MaCauHoi,
                        BanChupCauHoiJson

                    FROM dbo.ChiTietBaiLam

                    WHERE MaLanLamBai = ?
                      AND MaBaiTap = ?;
                    """,
                    attempt_id,
                    exercise_id,
                )

                details = records(cur)

                snaps = {
                    int(row["MaCauHoi"]): parse_json(
                        row["BanChupCauHoiJson"]
                    )
                    for row in details
                }

                valid = (
                    bool(snaps)
                    and len(snaps) <= MAX_QUESTIONS
                    and all(
                        isinstance(s, dict)
                        for s in snaps.values()
                    )
                    and set(answers).issubset(snaps)
                )

                if not valid:
                    return response_error(
                        "Dữ liệu câu hỏi của lượt làm "
                        "không hợp lệ."
                    )

                score = Decimal("0.00")
                maximum = Decimal("0.00")

                # Chấm và lưu chi tiết từng câu.
                for qid, snap in snaps.items():
                    answer = answers.get(qid)

                    correct, points, possible = grade(
                        snap,
                        answer,
                    )

                    score += points
                    maximum += possible

                    cur.execute(
                        """
                        UPDATE dbo.ChiTietBaiLam

                        SET
                            CauTraLoiJson = ?,
                            Diem = ?,
                            LaDapAnDung = ?,
                            CachChamDiem = 'quy_tac',
                            GopY = ?

                        WHERE MaLanLamBai = ?
                          AND MaBaiTap = ?
                          AND MaCauHoi = ?;
                        """,
                        as_json({
                            "answer": answer
                        }),
                        points,
                        int(correct),

                        (
                            "Chính xác!"
                            if correct
                            else "Câu trả lời chưa đúng."
                        ),

                        attempt_id,
                        exercise_id,
                        qid,
                    )

                if (
                    maximum <= 0
                    or maximum != amount(
                        attempt["DiemToiDaLucLam"]
                    )
                ):
                    raise ValueError(
                        "Tổng điểm của lượt làm "
                        "không khớp bản chụp."
                    )

                # Chốt lượt làm.
                cur.execute(
                    """
                    UPDATE dbo.LanLamBai

                    SET
                        NgayNop = SYSUTCDATETIME(),
                        TrangThai = 'da_cham',
                        Diem = ?

                    WHERE MaLanLamBai = ?
                      AND MaNguoiDung = ?
                      AND TrangThai = 'dang_thuc_hien';
                    """,
                    score,
                    attempt_id,
                    student_id(),
                )

                if cur.rowcount != 1:
                    raise ValueError(
                        "Lượt làm đã thay đổi trạng thái."
                    )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    percentage = score / maximum * 100

    return jsonify(
        success=True,
        message="Đã nộp bài thành công.",

        attempt_id=attempt_id,
        score=num(score),
        max_score=num(maximum),

        percentage=round(
            float(percentage),
            2,
        ),

        passed=(
            percentage
            >= Decimal(str(ex["PhanTramDat"]))
        ),

        result_url=url_for(
            "student_exercises.result_page",
            attempt_id=attempt_id,
        ),
    )


# ============================================================
# LỊCH SỬ LÀM BÀI
# ============================================================

@student_exercises_bp.get("/api/history")
def api_history():
    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                """
                SELECT TOP (50)
                    llb.MaLanLamBai,
                    llb.MaBaiTap,
                    bt.TieuDe,
                    llb.NgayBatDau,
                    llb.NgayNop,
                    llb.TrangThai,
                    llb.Diem,
                    llb.DiemToiDaLucLam

                FROM dbo.LanLamBai AS llb

                JOIN dbo.BaiTap AS bt
                    ON bt.MaBaiTap = llb.MaBaiTap

                WHERE llb.MaNguoiDung = ?
                  AND llb.TrangThai = 'da_cham'

                ORDER BY
                    llb.MaLanLamBai DESC;
                """,
                student_id(),
            )

            history = records(cur)

    return jsonify(
        success=True,
        history=history,
    )


# ============================================================
# LẤY KẾT QUẢ THẬT TỪ SQL SERVER
# ============================================================

def load_result(cur, attempt_id):
    cur.execute(
        """
        SELECT
            llb.MaLanLamBai,
            llb.MaBaiTap,
            llb.NgayNop,
            llb.Diem,
            llb.DiemToiDaLucLam,

            bt.PhanTramDat,
            bt.TieuDe,

            kh.MaCapDo

        FROM dbo.LanLamBai AS llb

        JOIN dbo.BaiTap AS bt
            ON bt.MaBaiTap = llb.MaBaiTap

        JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = bt.MaBaiHoc

        JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc = bh.MaKhoaHoc

        WHERE llb.MaLanLamBai = ?
          AND llb.MaNguoiDung = ?
          AND llb.TrangThai = 'da_cham';
        """,
        attempt_id,
        student_id(),
    )

    attempt = one(cur)

    if not attempt:
        return None, None

    cur.execute(
        """
        SELECT
            MaCauHoi,
            CauTraLoiJson,
            BanChupCauHoiJson,
            Diem,
            LaDapAnDung

        FROM dbo.ChiTietBaiLam

        WHERE MaLanLamBai = ?
          AND MaBaiTap = ?;
        """,
        attempt_id,
        attempt["MaBaiTap"],
    )

    qs = []

    for row in records(cur):
        snap = parse_json(
            row["BanChupCauHoiJson"],
            {},
        )

        response = parse_json(
            row["CauTraLoiJson"],
            {},
        )

        answer = (
            response.get("answer")
            if isinstance(response, dict)
            else None
        )

        is_answered = answered(
            snap,
            answer,
        )

        if not is_answered:
            status = "unanswered"
        elif row["LaDapAnDung"]:
            status = "correct"
        else:
            status = "wrong"

        qs.append({
            "order": snap.get(
                "order",
                row["MaCauHoi"],
            ),

            "content": snap.get(
                "content",
                "",
            ),

            "status": status,

            "user_answer": answer_display(
                snap,
                answer,
            ),

            "correct_answer": correct_display(
                snap
            ),

            "explanation": snap.get(
                "explanation",
                "",
            ),
        })

    qs.sort(
        key=lambda q: q["order"] or 0
    )

    maximum = amount(
        attempt["DiemToiDaLucLam"]
    )

    score = amount(
        attempt["Diem"]
    )

    percent = (
        round(float(score / maximum * 100), 2)
        if maximum
        else 0
    )

    submitted_at = None

    if attempt["NgayNop"]:
        # SQL lưu theo giờ UTC.
        # Chuyển sang giờ Việt Nam khi hiển thị.
        vietnam_time = (
            attempt["NgayNop"]
            + timedelta(hours=7)
        )

        submitted_at = vietnam_time.strftime(
            "%d/%m/%Y %H:%M"
        )

    result = {
        "attempt_id": attempt_id,

        "exercise_id": attempt["MaBaiTap"],

        "title": attempt["TieuDe"],

        "hsk": attempt["MaCapDo"],

        "score": num(score),

        "max_score": num(maximum),

        "percentage": percent,

        "passed": (
            Decimal(str(percent))
            >= Decimal(str(attempt["PhanTramDat"]))
        ),

        "submitted_at": submitted_at,

        "total_questions": len(qs),

        "correct_count": sum(
            q["status"] == "correct"
            for q in qs
        ),

        "wrong_count": sum(
            q["status"] == "wrong"
            for q in qs
        ),

        "unanswered_count": sum(
            q["status"] == "unanswered"
            for q in qs
        ),
    }

    return result, qs


# ============================================================
# API KẾT QUẢ
# ============================================================

@student_exercises_bp.get(
    "/api/results/<int:attempt_id>"
)
def api_result(attempt_id):
    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cur:
            result, qs = load_result(
                cur,
                attempt_id,
            )

    if not result:
        return response_error(
            "Không tìm thấy kết quả.",
            404,
        )

    return jsonify(
        success=True,
        result=result,
        questions=qs,
    )


# ============================================================
# TRANG KẾT QUẢ
# ============================================================

@student_exercises_bp.get(
    "/result/<int:attempt_id>"
)
def result_page(attempt_id):
    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cur:
            result, qs = load_result(
                cur,
                attempt_id,
            )

    if not result:
        abort(404)

    return render_template(
        "student/result.html",
        result=result,
        questions=qs,
    )
