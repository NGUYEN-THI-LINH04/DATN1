
# -*- coding: utf-8 -*-
"""
MỘC HÁN - LUYỆN THI HSK / STUDENT

Chức năng:
- Làm cả đề, Nghe, Đọc, Viết.
- Đồng hồ lấy thời gian từ Flask và SQL Server.
- Tải lại trang không đặt lại thời gian.
- Lưu tạm đáp án vào ChiTietLanThiHSK.
- Hết giờ tự chấm đáp án đã lưu.
- Nộp bài và chấm điểm.
- Kết quả tổng quan, xem lại đáp án, lịch sử.

HSK1-HSK2: Nghe và Đọc.
HSK3-HSK4: thêm Viết nếu có dữ liệu.

Không tạo hoặc sửa bảng SQL.
"""

import json
import re

from contextlib import closing
from decimal import Decimal

from flask import (
    abort,
    jsonify,
    render_template,
    request,
    session,
    url_for,
)

from database import get_connection

from .luyen_thi import (
    student_luyen_thi_bp,
    require_role,
    fetch_dicts,
    get_options,
)


# ==================================================
# 1. CẤU HÌNH THỜI GIAN VÀ KỸ NĂNG
# ==================================================

SKILL_MINUTES = {
    1: {"nghe": 15, "doc": 17},
    2: {"nghe": 25, "doc": 22},
    3: {"nghe": 35, "doc": 30, "viet": 15},
    4: {"nghe": 30, "doc": 40, "viet": 25},
}

SKILLS = {"tat_ca", "nghe", "doc", "viet"}

NETWORK_GRACE_SECONDS = 20


def to_database_skill(skill):
    """
    Website dùng tat_ca.
    SQL Server dùng toan_bo.
    """
    return "toan_bo" if skill == "tat_ca" else skill


def to_app_skill(skill):
    """
    Chuyển kỹ năng trong SQL về quy ước website.
    """
    return "tat_ca" if skill == "toan_bo" else skill


# ==================================================
# 2. XÁC THỰC NGƯỜI HỌC
# ==================================================

def current_student_id():
    require_role("student")

    try:
        return int(session["account_id"])

    except (KeyError, TypeError, ValueError):
        abort(401)


# ==================================================
# 3. THÔNG TIN ĐỀ THI
# ==================================================

def load_exam(
    cursor,
    exam_id,
    *,
    allow_unpublished=False,
):
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
            ThoiGianPhut,
            ThoiLuongAudioGiay,
            TrangThai
        FROM dbo.DeThiHSK
        WHERE MaDeThi = ?
        """,
        exam_id,
    )

    rows = fetch_dicts(cursor)

    if not rows:
        abort(404)

    exam = rows[0]

    if (
        not allow_unpublished
        and exam["TrangThai"] != "da_xuat_ban"
    ):
        abort(404)

    return exam


# ==================================================
# 4. KIỂM TRA KỸ NĂNG
# ==================================================

def validate_skill(exam, skill):
    if skill not in SKILLS:
        abort(404)

    level = int(exam["MaCapDo"])

    if level not in SKILL_MINUTES:
        abort(404)

    if skill == "viet" and level < 3:
        abort(404)


    columns = {
        "nghe": "SoCauNghe",
        "doc": "SoCauDoc",
        "viet": "SoCauViet",
    }

    if skill != "tat_ca":
        count = int(exam[columns[skill]] or 0)

        if count <= 0:
            abort(404)

    if (
        level < 3
        and int(exam["SoCauViet"] or 0) > 0
    ):
        abort(
            409,
            description=(
                "Đề HSK1/HSK2 có dữ liệu "
                "phần Viết bất thường."
            ),
        )


# ==================================================
# 5. TÍNH THỜI GIAN LÀM BÀI
# ==================================================

def limit_seconds(exam, skill):
    level = int(exam["MaCapDo"])

    # Toàn bộ đề ưu tiên thời gian được lưu trong SQL.
    if skill == "tat_ca":
        configured = exam["ThoiGianPhut"]

        if (
            configured is not None
            and int(configured) > 0
        ):
            return int(configured) * 60

        total = 0

        columns = {
            "nghe": "SoCauNghe",
            "doc": "SoCauDoc",
            "viet": "SoCauViet",
        }

        for name, minutes in SKILL_MINUTES[level].items():
            if int(exam[columns[name]] or 0) > 0:
                total += minutes * 60

        return total

    return SKILL_MINUTES[level][skill] * 60


# ==================================================
# 6. ĐỌC CÂU HỎI
# ==================================================

def read_questions(
    cursor,
    exam_id,
    skill,
    *,
    with_answers=False,
):
    columns = """
        MaCauHoiThi,
        SoCau,
        KyNang,
        Phan,
        LoaiCauHoi,
        NoiDung,
        AnhCauHoi,
        AnhNhomLuaChon,
        LuaChonJson,
        DiemToiDa
    """

    if with_answers:
        columns += ", DapAnDung"

    # tat_ca lấy toàn bộ câu hỏi của đề.
    condition = (
        ""
        if skill == "tat_ca"
        else "AND KyNang = ?"
    )

    params = (
        (exam_id,)
        if skill == "tat_ca"
        else (exam_id, skill)
    )

    cursor.execute(
        f"""
        SELECT {columns}
        FROM dbo.CauHoiThiHSK
        WHERE MaDeThi = ?
        {condition}
        ORDER BY SoCau, MaCauHoiThi
        """,
        *params,
    )

    return fetch_dicts(cursor)


# ==================================================
# 7. ĐỌC LẦN THI
# ==================================================

def read_attempt(
    cursor,
    attempt_id,
    uid,
    *,
    lock=False,
):
    hint = (
        " WITH (UPDLOCK, HOLDLOCK)"
        if lock
        else ""
    )

    cursor.execute(
        f"""
        SELECT
            MaLanThi,
            MaNguoiDung,
            MaDeThi,
            KyNang,
            TrangThai,
            NgayBatDau,
            NgayNop,
            Diem,
            DiemToiDaLucLam,

            DATEDIFF(
                SECOND,
                NgayBatDau,
                SYSUTCDATETIME()
            ) AS DaQuaGiay

        FROM dbo.LanThiHSK{hint}
        WHERE MaLanThi = ?
          AND MaNguoiDung = ?
        """,
        attempt_id,
        uid,
    )

    rows = fetch_dicts(cursor)

    if not rows:
        abort(404)

    attempt = rows[0]

    # SQL lưu toan_bo, ứng dụng xử lý tat_ca.
    attempt["KyNang"] = to_app_skill(
        attempt["KyNang"]
    )

    return attempt


# ==================================================
# 8. CHUẨN HÓA ĐÁP ÁN
# ==================================================

def normalize_answer(value, kind):
    if value is None:
        return ""

    if isinstance(value, str):
        value = value.strip()

        if value.startswith("["):
            try:
                value = json.loads(value)

            except (ValueError, TypeError):
                pass

    if isinstance(value, list):
        values = [
            str(x).strip()
            for x in value
        ]

        if kind == "chon_nhieu":
            value = ",".join(sorted(values))
        else:
            value = "".join(values)

    value = str(value).strip().upper()

    if kind == "chon_nhieu":
        items = [
            x.strip()
            for x in re.split(r"[,;|]", value)
            if x.strip()
        ]

        return ",".join(sorted(items))

    if kind in (
        "sap_xep",
        "viet_ngan",
        "dien_tu",
    ):
        return re.sub(
            r"[\s，。！？!?、,.;；：:]",
            "",
            value,
        )

    return re.sub(r"\s+", "", value)


# ==================================================
# 9. KIỂM TRA, LƯU VÀ ĐỌC ĐÁP ÁN
# ==================================================

def valid_answer(value):
    """
    Kiểm tra đáp án người học gửi lên.
    Hỗ trợ chuỗi, danh sách và bỏ trống.
    """
    return (
        value is None
        or (
            isinstance(value, str)
            and len(value) <= 3000
        )
        or (
            isinstance(value, list)
            and len(value) <= 100
            and all(
                isinstance(x, str)
                and len(x) <= 200
                for x in value
            )
        )
    )


def serialize_answer(value):
    """
    Lưu đáp án dưới dạng JSON object,
    tương thích với ISJSON của SQL Server.

    Ví dụ:
    A -> {"value": "A"}
    √ -> {"value": "√"}
    """
    if value is None:
        return None

    return json.dumps(
        {"value": value},
        ensure_ascii=False,
    )


def parse_saved(raw):
    """
    Khôi phục đáp án đã lưu.

    Hỗ trợ JSON object mới và dữ liệu cũ.
    """
    if raw is None:
        return None

    try:
        value = json.loads(raw)

    except (TypeError, ValueError):
        return raw

    if (
        isinstance(value, dict)
        and set(value.keys()) == {"value"}
    ):
        return value["value"]

    return value


# ==================================================
# 10. LƯU TẠM / CHẤM TỪNG CÂU
# ==================================================

def match_hsk4_answer(given, correct_answer, kind):
    """
    Bo sung cham HSK4, giu logic HSK1-HSK3.
    """

    if kind == "viet_cau_theo_tranh":
        # Cham theo dap an tham khao trong JSON.
        # Bo khoang trang va dau cau nhu cac
        # dang cau Viet dang co cua he thong.

        if not isinstance(given, str):
            return False

        actual = normalize_answer(
            given,
            "viet_ngan"
        )

        if not actual:
            return False

        data = correct_answer

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (TypeError, ValueError):
                return False

        if not isinstance(data, dict):
            return False

        references = data.get(
            "dap_an_tham_khao"
        )

        if isinstance(references, str):
            references = [references]

        if not isinstance(references, list):
            return False

        return any(
            isinstance(candidate, str)
            and candidate.strip()
            and actual == normalize_answer(
                candidate,
                "viet_ngan"
            )
            for candidate in references
        )

    actual = normalize_answer(
        given,
        kind,
    )

    if not actual:
        return False

    # Cau 56-65:
    # Nguoi hoc phai xep du A/B/C theo thu tu.
    if kind == "sap_xep_abc":

        if (
            len(actual) != 3
            or set(actual) != {"A", "B", "C"}
        ):
            return False

        return actual == normalize_answer(
            correct_answer,
            kind,
        )

    # Cau 86-95:
    # Co the co nhieu dap an hop le.
    if kind == "sap_xep":

        variants = correct_answer

        if (
            isinstance(variants, str)
            and variants.lstrip().startswith("[")
        ):
            try:
                variants = json.loads(variants)

            except (ValueError, TypeError):
                variants = correct_answer

        if not isinstance(variants, list):
            variants = [variants]

        return any(
            actual == normalize_answer(
                candidate,
                kind,
            )

            for candidate in variants

            if (
                isinstance(candidate, str)
                and candidate.strip()
            )
        )

    # Cac dang cau hoi cu giu nguyen.
    expected = normalize_answer(
        correct_answer,
        kind,
    )

    return (
        bool(actual)
        and actual == expected
    )


def persist_answer(
    cursor,
    attempt_id,
    exam_id,
    question,
    given,
    *,
    graded=False,
):
    maximum = Decimal(
        str(question["DiemToiDa"] or 0)
    )

    correct_answer = (
        question.get("DapAnDung")
        if graded
        else None
    )

    matched = False

    if graded:
        matched = match_hsk4_answer(
            given,
            correct_answer,
            question["LoaiCauHoi"],
        )

    points = (
        maximum
        if matched
        else Decimal("0")
    )

    # Cập nhật nếu câu trả lời đã tồn tại.
    cursor.execute(
        """
        UPDATE dbo.ChiTietLanThiHSK
        SET
            CauTraLoiJson = ?,
            DapAnDungLucCham = ?,
            DiemToiDaLucLam = ?,
            LaDapAnDung = ?,
            Diem = ?,
            NgayCapNhat = SYSUTCDATETIME()
        WHERE MaLanThi = ?
          AND MaDeThi = ?
          AND MaCauHoiThi = ?
        """,
        serialize_answer(given),
        (
            str(correct_answer)
            if graded
            else None
        ),
        maximum,
        int(matched) if graded else None,
        points if graded else None,
        attempt_id,
        exam_id,
        question["MaCauHoiThi"],
    )

    # Thêm mới nếu chưa có câu trả lời.
    if cursor.rowcount == 0:
        cursor.execute(
            """
            INSERT INTO dbo.ChiTietLanThiHSK
            (
                MaLanThi,
                MaDeThi,
                MaCauHoiThi,
                CauTraLoiJson,
                DapAnDungLucCham,
                DiemToiDaLucLam,
                LaDapAnDung,
                Diem,
                NgayCapNhat
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?,
                SYSUTCDATETIME()
            )
            """,
            attempt_id,
            exam_id,
            question["MaCauHoiThi"],
            serialize_answer(given),
            (
                str(correct_answer)
                if graded
                else None
            ),
            maximum,
            int(matched) if graded else None,
            points if graded else None,
        )

    return maximum, points


# ==================================================
# 11. CHẤM VÀ CHỐT LẦN THI
# ==================================================

def finalize(
    cursor,
    attempt,
    exam,
    submitted=None,
):
    """
    Trước hạn:
        Dùng câu trả lời mới và dữ liệu lưu tạm.

    Quá hạn:
        Dùng các đáp án đã lưu trong SQL.
    """
    exam_id = int(exam["MaDeThi"])

    questions = read_questions(
        cursor,
        exam_id,
        attempt["KyNang"],
        with_answers=True,
    )

    cursor.execute(
        """
        SELECT
            MaCauHoiThi,
            CauTraLoiJson
        FROM dbo.ChiTietLanThiHSK
        WHERE MaLanThi = ?
        """,
        attempt["MaLanThi"],
    )

    drafts = {
        str(row[0]): parse_saved(row[1])
        for row in cursor.fetchall()
    }

    total = Decimal("0")
    maximum = Decimal("0")

    for question in questions:
        key = str(
            question["MaCauHoiThi"]
        )

        if (
            submitted is not None
            and key in submitted
        ):
            given = submitted[key]
        else:
            given = drafts.get(key)

        max_points, earned = persist_answer(
            cursor,
            attempt["MaLanThi"],
            exam_id,
            question,
            given,
            graded=True,
        )

        maximum += max_points
        total += earned

    # SQL sử dụng trạng thái da_cham.
    cursor.execute(
        """
        UPDATE dbo.LanThiHSK
        SET
            NgayNop = SYSUTCDATETIME(),
            TrangThai = 'da_cham',
            Diem = ?,
            DiemToiDaLucLam = ?
        WHERE MaLanThi = ?
          AND MaNguoiDung = ?
          AND TrangThai = 'dang_lam'
        """,
        total,
        maximum,
        attempt["MaLanThi"],
        attempt["MaNguoiDung"],
    )

    if cursor.rowcount != 1:
        raise RuntimeError(
            "Không thể chốt kết quả lần thi."
        )

    return total, maximum


# ==================================================
# 12. KIỂM TRA HẾT GIỜ
# ==================================================

def result_url(attempt_id):
    return url_for(
        "student_luyen_thi.trang_ket_qua_luyen_thi",
        ma_lan=attempt_id,
    )


def expired(attempt, exam):
    elapsed = int(
        attempt["DaQuaGiay"] or 0
    )

    limit = limit_seconds(
        exam,
        attempt["KyNang"],
    )

    return (
        elapsed >
        limit + NETWORK_GRACE_SECONDS
    )


# ==================================================
# 13. TRANG LÀM BÀI
# ==================================================

@student_luyen_thi_bp.get(
    "/de/<int:ma_de>/lam-bai",
    defaults={"ky_nang": "tat_ca"},
)
@student_luyen_thi_bp.get(
    "/de/<int:ma_de>/lam-bai/<ky_nang>"
)
def trang_lam_bai(ma_de, ky_nang):
    current_student_id()

    with closing(get_connection()) as conn:
        exam = load_exam(
            conn.cursor(),
            ma_de,
        )

    validate_skill(
        exam,
        ky_nang,
    )

    return render_template(
        "student/luyen_thi_lam_bai.html",
        ma_de=ma_de,
        ky_nang=ky_nang,
        ten_de=exam["TenDe"],
        cap_hsk=exam["MaCapDo"],
    )


# ==================================================
# 14. BẮT ĐẦU HOẶC TIẾP TỤC LẦN THI
# ==================================================

@student_luyen_thi_bp.post(
    "/api/lam-bai/bat-dau"
)
def api_bat_dau_lam_bai():
    uid = current_student_id()

    body = (
        request.get_json(silent=True)
        or {}
    )

    if not isinstance(body, dict):
        return jsonify(
            loi="Dữ liệu bắt đầu thi không hợp lệ."
        ), 400

    try:
        exam_id = int(
            body.get("ma_de")
        )

    except (TypeError, ValueError):
        return jsonify(
            loi="Mã đề không hợp lệ."
        ), 400

    # Giao diện gửi tat_ca.
    skill = str(
        body.get("ky_nang", "tat_ca")
    )

    with closing(get_connection()) as conn:
        try:
            cursor = conn.cursor()

            exam = load_exam(
                cursor,
                exam_id,
            )

            validate_skill(
                exam,
                skill,
            )

            # Chuyển tat_ca sang toan_bo cho SQL.
            db_skill = to_database_skill(skill)

            questions = read_questions(
                cursor,
                exam_id,
                skill,
            )

            if not questions:
                conn.rollback()

                return jsonify(
                    loi="Đề chưa có câu hỏi."
                ), 409

            # Tìm lần thi đang làm.
            cursor.execute(
                """
                SELECT TOP 1 MaLanThi
                FROM dbo.LanThiHSK
                    WITH (UPDLOCK, HOLDLOCK)
                WHERE MaNguoiDung = ?
                  AND MaDeThi = ?
                  AND KyNang = ?
                  AND TrangThai = 'dang_lam'
                ORDER BY MaLanThi DESC
                """,
                uid,
                exam_id,
                db_skill,
            )

            old = cursor.fetchone()

            if old:
                attempt = read_attempt(
                    cursor,
                    int(old[0]),
                    uid,
                    lock=True,
                )

                if expired(attempt, exam):
                    finalize(
                        cursor,
                        attempt,
                        exam,
                    )

                    conn.commit()

                    return jsonify(
                        het_gio=True,
                        ket_qua=result_url(
                            attempt["MaLanThi"]
                        ),
                    )

            if old:
                attempt_id = int(old[0])

            else:
                maximum = sum(
                    (
                        Decimal(
                            str(q["DiemToiDa"] or 0)
                        )
                        for q in questions
                    ),
                    Decimal("0"),
                )

                # SQL lưu toan_bo, không phải tat_ca.
                cursor.execute(
                    """
                    INSERT INTO dbo.LanThiHSK
                    (
                        MaNguoiDung,
                        MaDeThi,
                        KyNang,
                        NgayBatDau,
                        NgayNop,
                        TrangThai,
                        Diem,
                        DiemToiDaLucLam
                    )
                    OUTPUT INSERTED.MaLanThi
                    VALUES
                    (
                        ?, ?, ?,
                        SYSUTCDATETIME(),
                        NULL,
                        'dang_lam',
                        NULL,
                        ?
                    )
                    """,
                    uid,
                    exam_id,
                    db_skill,
                    maximum,
                )

                attempt_id = int(
                    cursor.fetchone()[0]
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    return jsonify(
        ma_lan_thi=attempt_id,
        het_gio=False,
    )


# ==================================================
# 15. API TẢI ĐỀ VÀ THỜI GIAN
# ==================================================

@student_luyen_thi_bp.get(
    "/api/lam-bai/<int:ma_lan>/du-lieu"
)
def api_du_lieu_lam_bai(ma_lan):
    uid = current_student_id()

    with closing(get_connection()) as conn:
        try:
            cursor = conn.cursor()

            attempt = read_attempt(
                cursor,
                ma_lan,
                uid,
                lock=True,
            )

            if attempt["TrangThai"] != "dang_lam":
                conn.rollback()

                return jsonify(
                    loi="Lần thi đã nộp.",
                    ket_qua=result_url(ma_lan),
                ), 409

            exam = load_exam(
                cursor,
                attempt["MaDeThi"],
            )

            validate_skill(
                exam,
                attempt["KyNang"],
            )

            if expired(attempt, exam):
                finalize(
                    cursor,
                    attempt,
                    exam,
                )

                conn.commit()

                return jsonify(
                    loi="Bài đã hết giờ.",
                    ket_qua=result_url(ma_lan),
                ), 409

            questions = read_questions(
                cursor,
                exam["MaDeThi"],
                attempt["KyNang"],
            )

            # Khôi phục đáp án đã lưu.
            cursor.execute(
                """
                SELECT
                    MaCauHoiThi,
                    CauTraLoiJson
                FROM dbo.ChiTietLanThiHSK
                WHERE MaLanThi = ?
                  AND DapAnDungLucCham IS NULL
                """,
                ma_lan,
            )

            drafts = {
                str(row[0]): parse_saved(row[1])
                for row in cursor.fetchall()
            }

            # Lấy MP3 nguyên bài.
            cursor.execute(
                """
                SELECT t.DuongDanTep
                FROM dbo.DeThiHSK AS d
                LEFT JOIN dbo.TepDaPhuongTien AS t
                    ON t.MaTep = d.MaTepAudio
                WHERE d.MaDeThi = ?
                """,
                exam["MaDeThi"],
            )

            audio_row = cursor.fetchone()

            audio_url = (
                audio_row[0]
                if audio_row
                else None
            )

            conn.rollback()

        except Exception:
            conn.rollback()
            raise

    # Không gửi đáp án đúng cho JS khi đang thi.
    for q in questions:
        q.pop("DiemToiDa", None)

        raw = q.pop(
            "LuaChonJson",
            None,
        )

        q["lua_chon"] = get_options(
            q["LoaiCauHoi"],
            raw,
            int(exam["MaCapDo"]),
        )

        # Hỗ trợ dữ liệu sắp xếp từ phần Viết.
        if not q["lua_chon"] and raw:
            try:
                values = (
                    json.loads(raw)
                    if isinstance(raw, str)
                    else raw
                )

                if isinstance(values, list):
                    normalized = []

                    for index, item in enumerate(values):
                        if isinstance(item, dict):
                            code = item.get(
                                "ma",
                                item.get("value", index),
                            )

                            label = item.get(
                                "nhan",
                                item.get(
                                    "label",
                                    item.get("value", ""),
                                ),
                            )

                        else:
                            code = index
                            label = item

                        normalized.append({
                            "ma": str(code),
                            "nhan": str(label),
                        })

                    q["lua_chon"] = normalized

            except (TypeError, ValueError):
                pass

    limit = limit_seconds(
        exam,
        attempt["KyNang"],
    )

    elapsed = max(
        0,
        int(attempt["DaQuaGiay"] or 0),
    )

    return jsonify(
        de_thi={
            "MaDeThi": exam["MaDeThi"],
            "MaCapDo": exam["MaCapDo"],
            "TenDe": exam["TenDe"],
            "ThoiGianPhut": limit / 60,
            "ThoiLuongAudioGiay": (
                float(exam["ThoiLuongAudioGiay"])
                if exam["ThoiLuongAudioGiay"] is not None
                else None
            ),
            "AudioUrl": audio_url,
        },
        ky_nang=attempt["KyNang"],
        ma_lan_thi=ma_lan,
        gioi_han_giay=limit,
        da_qua_giay=elapsed,
        con_lai_giay=max(
            0,
            limit - elapsed,
        ),
        dap_an_da_luu=drafts,
        cau_hoi=questions,
    )


# ==================================================
# 16. API LƯU TẠM ĐÁP ÁN
# ==================================================

@student_luyen_thi_bp.post(
    "/api/lam-bai/<int:ma_lan>/luu-tam"
)
def api_luu_tam_hsk(ma_lan):
    uid = current_student_id()

    body = (
        request.get_json(silent=True)
        or {}
    )

    if not isinstance(body, dict):
        return jsonify(
            loi="Dữ liệu lưu tạm không hợp lệ."
        ), 400

    try:
        question_id = int(
            body.get("ma_cau_hoi")
        )

    except (ValueError, TypeError):
        return jsonify(
            loi="Mã câu hỏi không hợp lệ."
        ), 400

    answer = body.get("cau_tra_loi")

    if not valid_answer(answer):
        return jsonify(
            loi="Câu trả lời không hợp lệ."
        ), 400

    with closing(get_connection()) as conn:
        try:
            cursor = conn.cursor()

            attempt = read_attempt(
                cursor,
                ma_lan,
                uid,
                lock=True,
            )

            if attempt["TrangThai"] != "dang_lam":
                conn.rollback()

                return jsonify(
                    loi="Lần thi đã nộp.",
                    ket_qua=result_url(ma_lan),
                ), 409

            exam = load_exam(
                cursor,
                attempt["MaDeThi"],
            )

            validate_skill(
                exam,
                attempt["KyNang"],
            )

            if expired(attempt, exam):
                finalize(
                    cursor,
                    attempt,
                    exam,
                )

                conn.commit()

                return jsonify(
                    loi="Bài đã hết giờ.",
                    ket_qua=result_url(ma_lan),
                ), 409

            questions = read_questions(
                cursor,
                exam["MaDeThi"],
                attempt["KyNang"],
            )

            question = next(
                (
                    q
                    for q in questions
                    if q["MaCauHoiThi"] == question_id
                ),
                None,
            )

            if not question:
                conn.rollback()

                return jsonify(
                    loi="Câu hỏi không thuộc lần thi này."
                ), 400

            persist_answer(
                cursor,
                ma_lan,
                exam["MaDeThi"],
                question,
                answer,
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    return jsonify(ok=True)


# ==================================================
# 17. NỘP BÀI / CHẤM ĐIỂM
# ==================================================

@student_luyen_thi_bp.post(
    "/api/lam-bai/<int:ma_lan>/nop-bai"
)
def api_nop_bai(ma_lan):
    uid = current_student_id()

    body = (
        request.get_json(silent=True)
        or {}
    )

    if not isinstance(body, dict):
        return jsonify(
            loi="Dữ liệu nộp bài không hợp lệ."
        ), 400

    submitted = body.get(
        "cau_tra_loi",
        {},
    )

    if (
        not isinstance(submitted, dict)
        or len(submitted) > 200
        or any(
            not isinstance(k, str)
            or len(k) > 30
            or not valid_answer(v)
            for k, v in submitted.items()
        )
    ):
        return jsonify(
            loi="Danh sách câu trả lời không hợp lệ."
        ), 400

    with closing(get_connection()) as conn:
        try:
            cursor = conn.cursor()

            attempt = read_attempt(
                cursor,
                ma_lan,
                uid,
                lock=True,
            )

            if attempt["TrangThai"] != "dang_lam":
                conn.rollback()

                return jsonify(
                    ok=True,
                    ket_qua=result_url(ma_lan),
                )

            exam = load_exam(
                cursor,
                attempt["MaDeThi"],
            )

            validate_skill(
                exam,
                attempt["KyNang"],
            )

            questions = read_questions(
                cursor,
                exam["MaDeThi"],
                attempt["KyNang"],
            )

            allowed = {
                str(q["MaCauHoiThi"])
                for q in questions
            }

            if not set(submitted).issubset(allowed):
                conn.rollback()

                return jsonify(
                    loi="Câu hỏi không thuộc lần thi."
                ), 400

            too_late = expired(
                attempt,
                exam,
            )

            finalize(
                cursor,
                attempt,
                exam,
                None if too_late else submitted,
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    return jsonify(
        ok=True,
        het_gio=too_late,
        ket_qua=result_url(ma_lan),
    )



# ==================================================
# 18. TRANG KẾT QUẢ TỔNG QUAN
# Mỗi kỹ năng tối đa 100 điểm.
# HSK1-HSK2: Cả đề 200 điểm.
# HSK3-HSK4: Cả đề 300 điểm.
# ==================================================

@student_luyen_thi_bp.get(
    "/ket-qua/<int:ma_lan>"
)
def trang_ket_qua_luyen_thi(ma_lan):
    uid = current_student_id()

    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        attempt = read_attempt(
            cursor,
            ma_lan,
            uid,
        )

        if attempt["TrangThai"] != "da_cham":
            abort(404)

        exam = load_exam(
            cursor,
            attempt["MaDeThi"],
            allow_unpublished=True,
        )

        # Lấy điểm gốc và số câu theo từng kỹ năng.
        # Không tính lại đáp án, không thay đổi SQL.
        cursor.execute(
            """
            SELECT
                q.KyNang,

                COUNT(*) AS TongCau,

                SUM(
                    CASE
                        WHEN c.LaDapAnDung = 1
                        THEN 1 ELSE 0
                    END
                ) AS SoCauDung,

                COALESCE(
                    SUM(c.Diem),
                    0
                ) AS DiemGoc,

                COALESCE(
                    SUM(c.DiemToiDaLucLam),
                    0
                ) AS DiemGocToiDa

            FROM dbo.ChiTietLanThiHSK AS c

            INNER JOIN dbo.CauHoiThiHSK AS q
                ON q.MaCauHoiThi = c.MaCauHoiThi

            WHERE c.MaLanThi = ?
              AND c.MaDeThi = ?

            GROUP BY q.KyNang
            """,
            ma_lan,
            exam["MaDeThi"],
        )

        rows = fetch_dicts(cursor)

    # ----------------------------------------------
    # 1. Xác định các kỹ năng trong lần thi
    # ----------------------------------------------

    cap_hsk = int(exam["MaCapDo"])
    ky_nang_lam = attempt["KyNang"]

    ten_ky_nang = {
        "nghe": "Nghe hiểu",
        "doc": "Đọc hiểu",
        "viet": "Viết",
    }

    if ky_nang_lam == "tat_ca":
        if cap_hsk in (1, 2):
            ky_nang_can_tinh = ["nghe", "doc"]
        else:
            ky_nang_can_tinh = [
                "nghe",
                "doc",
                "viet",
            ]
    else:
        ky_nang_can_tinh = [ky_nang_lam]

    # ----------------------------------------------
    # 2. Quy đổi từng kỹ năng về thang 100
    # ----------------------------------------------

    du_lieu_theo_ky_nang = {
        row["KyNang"]: row
        for row in rows
    }

    bang_diem = []
    diem_tong = 0.0
    tong_cau = 0
    tong_cau_dung = 0
    thieu_ky_nang = []

    for key in ky_nang_can_tinh:
        row = du_lieu_theo_ky_nang.get(key)

        if row is None:
            thieu_ky_nang.append(
                ten_ky_nang.get(key, key)
            )

        so_cau = int(
            row["TongCau"] or 0
        ) if row else 0

        so_cau_dung = int(
            row["SoCauDung"] or 0
        ) if row else 0

        diem_goc = float(
            row["DiemGoc"] or 0
        ) if row else 0.0

        diem_goc_toi_da = float(
            row["DiemGocToiDa"] or 0
        ) if row else 0.0

        # Ví dụ: Nghe 14/20 -> 70/100 điểm.
        diem_quy_doi = (
            round(
                diem_goc * 100.0
                / diem_goc_toi_da,
                2,
            )
            if diem_goc_toi_da > 0
            else 0.0
        )

        diem_quy_doi = min(
            100.0,
            max(0.0, diem_quy_doi),
        )

        bang_diem.append({
            "ky_nang": key,
            "ten": ten_ky_nang.get(key, key),
            "diem": diem_quy_doi,
            "diem_toi_da": 100,
            "so_cau": so_cau,
            "so_cau_dung": so_cau_dung,
        })

        diem_tong += diem_quy_doi
        tong_cau += so_cau
        tong_cau_dung += so_cau_dung

    # ----------------------------------------------
    # 3. Tổng điểm tối đa và điểm đạt
    # ----------------------------------------------

    # 1 kỹ năng = 100 điểm
    # HSK1-HSK2 cả đề = 200 điểm
    # HSK3-HSK4 cả đề = 300 điểm
    diem_toi_da_hien_thi = (
        len(ky_nang_can_tinh) * 100
    )

    diem_hien_thi = round(diem_tong, 1)

    ty_le = (
        round(
            diem_hien_thi * 100.0
            / diem_toi_da_hien_thi,
            1,
        )
        if diem_toi_da_hien_thi > 0
        else 0.0
    )

    diem_dat = int(
        diem_toi_da_hien_thi * 0.6
    )

    # Không đánh dấu đạt nếu Cả đề thiếu
    # một kỹ năng bắt buộc.
    dat = (
        not thieu_ky_nang
        and diem_hien_thi >= diem_dat
    )

    # ----------------------------------------------
    # 4. Thời gian làm bài thực tế
    # ----------------------------------------------

    started = attempt["NgayBatDau"]
    submitted = attempt["NgayNop"]

    duration = (
        max(
            0,
            int(
                (submitted - started)
                .total_seconds()
            ),
        )
        if (
            started is not None
            and submitted is not None
        )
        else 0
    )

    duration_text = (
        f"{duration // 60}:{duration % 60:02d}"
    )

    # ----------------------------------------------
    # 5. Hiển thị kết quả
    # ----------------------------------------------

    return render_template(
        "student/luyen_thi_ket_qua.html",

        de=exam,
        lan=attempt,

        # Điểm gốc giữ nguyên trong SQL.
        diem=float(attempt["Diem"] or 0),
        diem_toi_da=float(
            attempt["DiemToiDaLucLam"] or 0
        ),

        # Điểm hiển thị theo chuẩn từng kỹ năng.
        diem_hien_thi=diem_hien_thi,
        diem_toi_da_hien_thi=diem_toi_da_hien_thi,
        diem_dat=diem_dat,
        ty_le=ty_le,
        bang_diem=bang_diem,
        thieu_ky_nang=thieu_ky_nang,

        # Số câu.
        so_cau=tong_cau,
        so_cau_dung=tong_cau_dung,
        so_cau_sai=tong_cau - tong_cau_dung,

        # Thời gian.
        thoi_gian_lam_giay=duration,
        thoi_gian_lam=duration_text,

        dat=dat,
    )

# ==================================================
# 19. XEM LẠI ĐÁP ÁN
# ==================================================

@student_luyen_thi_bp.get(
    "/ket-qua/<int:ma_lan>/xem-lai"
)
def trang_xem_lai_dap_an_luyen_thi(ma_lan):
    uid = current_student_id()

    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        attempt = read_attempt(
            cursor,
            ma_lan,
            uid,
        )

        if attempt["TrangThai"] != "da_cham":
            abort(404)

        exam = load_exam(
            cursor,
            attempt["MaDeThi"],
            allow_unpublished=True,
        )

        cursor.execute(
            """
            SELECT
                q.SoCau,
                q.KyNang,
                q.Phan,
                q.LoaiCauHoi,
                q.NoiDung,
                q.AnhCauHoi,
                q.AnhNhomLuaChon,
                q.LuaChonJson,

                c.CauTraLoiJson,
                c.DapAnDungLucCham,
                c.LaDapAnDung,
                c.Diem,
                c.DiemToiDaLucLam

            FROM dbo.ChiTietLanThiHSK AS c

            INNER JOIN dbo.CauHoiThiHSK AS q
                ON q.MaCauHoiThi = c.MaCauHoiThi

            WHERE c.MaLanThi = ?
              AND c.MaDeThi = ?

            ORDER BY q.SoCau, q.MaCauHoiThi
            """,
            ma_lan,
            exam["MaDeThi"],
        )

        details = fetch_dicts(cursor)

        # Lấy MP3 để nghe lại.
        cursor.execute(
            """
            SELECT t.DuongDanTep
            FROM dbo.DeThiHSK AS d
            LEFT JOIN dbo.TepDaPhuongTien AS t
                ON t.MaTep = d.MaTepAudio
            WHERE d.MaDeThi = ?
            """,
            exam["MaDeThi"],
        )

        audio_row = cursor.fetchone()

        audio_url = (
            audio_row[0]
            if audio_row
            else None
        )

    for question in details:
        answer = parse_saved(
            question.pop(
                "CauTraLoiJson",
                None,
            )
        )

        if isinstance(answer, list):
            answer = " ".join(
                str(value)
                for value in answer
            )

        question["CauTraLoi"] = answer

        raw_options = question.pop(
            "LuaChonJson",
            None,
        )

        question["lua_chon"] = get_options(
            question["LoaiCauHoi"],
            raw_options,
            int(exam["MaCapDo"]),
        )

    return render_template(
        "student/luyen_thi_xem_lai.html",
        de=exam,
        lan=attempt,
        chi_tiet=details,
        audio_url=audio_url,
    )


# ==================================================
# 20. LỊCH SỬ LÀM BÀI
# ==================================================

@student_luyen_thi_bp.get(
    "/api/lam-bai/lich-su/<int:ma_de>"
)
def api_lich_su_luyen_thi(ma_de):
    uid = current_student_id()

    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        exam = load_exam(
            cursor,
            ma_de,
            allow_unpublished=True,
        )

        cursor.execute(
            """
            SELECT TOP 20
                MaLanThi,
                KyNang,
                NgayNop,
                Diem,
                DiemToiDaLucLam

            FROM dbo.LanThiHSK

            WHERE MaNguoiDung = ?
              AND MaDeThi = ?
              AND TrangThai = 'da_cham'

            ORDER BY
                NgayNop DESC,
                MaLanThi DESC
            """,
            uid,
            exam["MaDeThi"],
        )

        rows = fetch_dicts(cursor)

    history = []

    for q in rows:
        history.append({
            "ma_lan_thi": int(q["MaLanThi"]),

            # SQL toan_bo -> giao diện tat_ca.
            "ky_nang": to_app_skill(
                q["KyNang"]
            ),

            "ngay_nop": (
                q["NgayNop"].isoformat()
                if q["NgayNop"]
                else ""
            ),

            "diem": float(
                q["Diem"] or 0
            ),

            "diem_toi_da": float(
                q["DiemToiDaLucLam"] or 0
            ),
        })

    return jsonify(
        lich_su=history
    )
