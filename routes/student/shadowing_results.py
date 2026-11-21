
import math
import unicodedata

from contextlib import closing

from flask import (
    Blueprint,
    g,
    jsonify,
    request,
)

from database import get_connection

from routes.student.shadowing import (
    parse_shadowing_data,
    parse_sentences,
)


# ============================================================
# 1. BLUEPRINT LUU KET QUA SHADOWING
# ============================================================

shadowing_results_bp = Blueprint(
    "shadowing_results",
    __name__,
    url_prefix="/shadowing/api",
)


# ============================================================
# 2. CHUAN HOA CAU TIENG TRUNG
#
# Giong quy tac cham diem hien tai trong
# static/js/shadowing-study.js:
# - Chuan hoa Unicode NFKC
# - Bo khoang trang
# - Bo dau cau va ky hieu
# - Khong chuyen gian the / phon the
# ============================================================

def normalize_hanzi(value):

    text = unicodedata.normalize(
        "NFKC",
        value,
    )

    return "".join(
        char
        for char in text
        if not char.isspace()
        and unicodedata.category(char)[0]
        not in ("P", "S")
    )


# ============================================================
# 3. DEM SO KY TU KHAC NHAU
# Thuat toan Levenshtein
# ============================================================

def count_character_errors(expected, actual):

    a = list(expected)
    b = list(actual)

    previous = list(
        range(len(b) + 1)
    )

    for i, char_a in enumerate(a, 1):

        current = [i]

        for j, char_b in enumerate(b, 1):

            cost = 0 if char_a == char_b else 1

            current.append(
                min(
                    previous[j] + 1,
                    current[j - 1] + 1,
                    previous[j - 1] + cost,
                )
            )

        previous = current

    return previous[-1]


# ============================================================
# 4. CHAM DIEM TAI FLASK
#
# Khong su dung diem do trinh duyet gui len.
# Lay dap an dung truc tiep tu SQL Server.
# ============================================================

def calculate_score(expected, submitted):

    correct_text = normalize_hanzi(expected)

    submitted_text = normalize_hanzi(submitted)

    errors = count_character_errors(
        correct_text,
        submitted_text,
    )

    total = len(correct_text)

    if total == 0:
        return 0, errors, False

    score = max(
        0,
        math.floor(
            (1 - errors / total) * 100 + 0.5
        ),
    )

    correct = errors == 0

    return score, errors, correct


# ============================================================
# 5. KIEM TRA DANG NHAP NGUOI HOC
# ============================================================

def get_student_id():

    account = getattr(
        g,
        "account",
        None,
    )

    if account is None:

        return None, (
            jsonify(
                error="Bạn cần đăng nhập để lưu kết quả."
            ),
            401,
        )

    if account.get("role") != "student":

        return None, (
            jsonify(
                error="Chức năng này chỉ dành cho người học."
            ),
            403,
        )

    return int(account["id"]), None


# ============================================================
# 6. LAY CAU THOAI GOC TU SQL SERVER
# ============================================================

def get_video_sentences(cursor, content_id):

    cursor.execute(
        """
        SELECT NoiDung

        FROM dbo.NoiDungBaiHoc

        WHERE MaNoiDung = ?
          AND LoaiNoiDung = 'nghe'
        """,
        content_id,
    )

    row = cursor.fetchone()

    if row is None:
        return None

    data = parse_shadowing_data(
        row[0]
    )

    if data is None:
        return None

    return parse_sentences(data)


# ============================================================
# 7. TINH TIEN DO LUYEN TAP
#
# Moi cau co the lam nhieu lan.
# Lay ket qua moi nhat cua tung cau / che do.
# ============================================================

def get_progress(
    cursor,
    user_id,
    content_id,
    total_sentences,
):

    cursor.execute(
        """
        WITH LatestAttempts AS
        (
            SELECT
                CheDo,
                ViTriCau,
                Diem,
                LaDapAnDung,

                ROW_NUMBER() OVER
                (
                    PARTITION BY CheDo, ViTriCau

                    ORDER BY
                        MaKetQuaShadowing DESC

                ) AS RowNumber

            FROM dbo.KetQuaShadowing

            WHERE MaNguoiDung = ?
              AND MaNoiDung = ?
              AND ViTriCau < ?
        )

        SELECT
            CheDo,

            COUNT(*) AS SoCauDaLam,

            AVG(
                CONVERT(FLOAT, Diem)
            ) AS DiemTrungBinh,

            SUM(
                CONVERT(INT, LaDapAnDung)
            ) AS SoCauDung

        FROM LatestAttempts

        WHERE RowNumber = 1

        GROUP BY CheDo
        """,
        user_id,
        content_id,
        total_sentences,
    )

    modes = {
        "dictation": {
            "done": 0,
            "average": 0,
            "correct": 0,
        },
        "assemble": {
            "done": 0,
            "average": 0,
            "correct": 0,
        },
    }

    for row in cursor.fetchall():

        mode = row[0]

        if mode not in modes:
            continue

        modes[mode] = {
            "done": int(row[1]),
            "average": int(
                math.floor(float(row[2]) + 0.5)
            ),
            "correct": int(row[3]),
        }

    return {
        "total_sentences": total_sentences,
        "modes": modes,
    }


# ============================================================
# 8. API LUU KET QUA
#
# POST /shadowing/api/ket-qua
# ============================================================

@shadowing_results_bp.post("/ket-qua")
def save_result():

    user_id, error = get_student_id()

    if error is not None:
        return error

    # Gioi han kich thuoc request.
    if (
        request.content_length is not None
        and request.content_length > 8192
    ):
        return jsonify(
            error="Dữ liệu gửi lên quá lớn."
        ), 413

    payload = request.get_json(
        silent=True
    )

    if not isinstance(payload, dict):

        return jsonify(
            error="Dữ liệu JSON không hợp lệ."
        ), 400

    content_id = payload.get("content_id")

    sentence_index = payload.get(
        "sentence_index"
    )

    mode = payload.get("mode")

    answer = payload.get("answer")

    replay_count = payload.get(
        "replay_count",
        0,
    )

    # --------------------------------------------------------
    # 8.1. KIEM TRA DU LIEU GUI LEN
    # --------------------------------------------------------

    if (
        type(content_id) is not int
        or content_id <= 0

        or type(sentence_index) is not int
        or sentence_index < 0

        or mode not in ("dictation", "assemble")

        or not isinstance(answer, str)
        or not (1 <= len(answer) <= 2000)

        or type(replay_count) is not int
        or not (0 <= replay_count <= 1000)
    ):

        return jsonify(
            error="Thông tin bài làm không hợp lệ."
        ), 400

    answer = answer.strip()

    if not normalize_hanzi(answer):

        return jsonify(
            error="Bạn chưa nhập đáp án hợp lệ."
        ), 400

    # --------------------------------------------------------
    # 8.2. LAY DAP AN GOC VA CHAM DIEM
    # --------------------------------------------------------

    with closing(get_connection()) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                sentences = get_video_sentences(
                    cursor,
                    content_id,
                )

                if sentences is None:

                    return jsonify(
                        error="Không tìm thấy video Shadowing."
                    ), 404

                if sentence_index >= len(sentences):

                    return jsonify(
                        error="Câu thoại không tồn tại."
                    ), 400

                sentence = sentences[sentence_index]

                expected = sentence["hanzi"]

                score, errors, correct = calculate_score(
                    expected,
                    answer,
                )

                # --------------------------------------------
                # 8.3. LUU VAO KETQUASHADOWING
                # --------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO dbo.KetQuaShadowing
                    (
                        MaNguoiDung,
                        MaNoiDung,
                        CheDo,
                        ViTriCau,
                        CauTraLoi,
                        Diem,
                        SoLoi,
                        LaDapAnDung,
                        SoLanNgheLai
                    )

                    OUTPUT INSERTED.MaKetQuaShadowing

                    VALUES
                    (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    user_id,
                    content_id,
                    mode,
                    sentence_index,
                    answer,
                    score,
                    errors,
                    int(correct),
                    replay_count,
                )

                inserted = cursor.fetchone()

                result_id = int(inserted[0])

            connection.commit()

        except Exception:

            connection.rollback()
            raise

        # ----------------------------------------------------
        # 8.4. DOC TIEN DO SAU KHI LUU
        # ----------------------------------------------------

        with closing(
            connection.cursor()
        ) as cursor:

            summary = get_progress(
                cursor,
                user_id,
                content_id,
                len(sentences),
            )

    return jsonify({
        "saved": True,
        "result_id": result_id,
        "score": score,
        "errors": errors,
        "correct": correct,
        "summary": summary,
    })


# ============================================================
# 9. API LAY TIEN DO LUYEN TAP
#
# GET /shadowing/api/tong-ket/<content_id>
# ============================================================

@shadowing_results_bp.get(
    "/tong-ket/<int:content_id>"
)
def get_summary(content_id):

    user_id, error = get_student_id()

    if error is not None:
        return error

    with closing(get_connection()) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            sentences = get_video_sentences(
                cursor,
                content_id,
            )

            if sentences is None:

                return jsonify(
                    error="Không tìm thấy video Shadowing."
                ), 404

            summary = get_progress(
                cursor,
                user_id,
                content_id,
                len(sentences),
            )

    return jsonify(summary)
