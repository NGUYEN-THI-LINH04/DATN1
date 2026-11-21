
"""
MỘC HÁN - QUẢN LÝ LỊCH SỬ CHATBOT

File: routes/chatbot_history.py

Sử dụng SQL Server hiện có:
- dbo.CuocHoiThoai
- dbo.TinNhan

Chức năng:
1. Tạo cuộc trò chuyện khi có tin nhắn đầu tiên
2. Lưu câu hỏi và câu trả lời
3. Lấy danh sách cuộc trò chuyện của người học
4. Xem lại tin nhắn trong cuộc trò chuyện
5. Lấy ngữ cảnh gần nhất cho Qwen3
6. Kiểm tra quyền sở hữu hội thoại

Không tạo bảng mới.
"""

import uuid
from contextlib import closing

from database import get_connection


# ==========================================================
# 01. CÁC GIÁ TRỊ ĐÚNG THEO SQL SERVER
# ==========================================================

USER_ROLE = "nguoi_dung"
ASSISTANT_ROLE = "tro_ly"

VALID_SOURCES = {
    "noi_bo",
    "tu_dien",
    "chi_ai",
    "ket_hop",
    "chua_co_dap_an",
}


# ==========================================================
# 02. KIỂM TRA MÃ NGƯỜI HỌC
#
# MaNguoiDung phải được lấy từ tài khoản
# đã đăng nhập tại Flask, không lấy tùy ý
# từ JSON do trình duyệt gửi lên.
# ==========================================================

def validate_user_id(user_id):

    if isinstance(user_id, bool):
        raise ValueError("Mã người học không hợp lệ.")

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise ValueError(
            "Mã người học không hợp lệ."
        ) from None

    if user_id <= 0:
        raise ValueError(
            "Mã người học không hợp lệ."
        )

    return user_id


# ==========================================================
# 03. KIỂM TRA MÃ CUỘC TRÒ CHUYỆN
# ==========================================================

def validate_conversation_id(conversation_id):

    if isinstance(conversation_id, bool):
        raise ValueError(
            "Mã cuộc trò chuyện không hợp lệ."
        )

    try:
        conversation_id = int(conversation_id)
    except (ValueError, TypeError):
        raise ValueError(
            "Mã cuộc trò chuyện không hợp lệ."
        ) from None

    if conversation_id <= 0:
        raise ValueError(
            "Mã cuộc trò chuyện không hợp lệ."
        )

    return conversation_id


# ==========================================================
# 04. KIỂM TRA QUYỀN SỞ HỮU HỘI THOẠI
#
# Một người học không được xem hoặc ghi
# tin nhắn vào cuộc trò chuyện của người khác.
# ==========================================================

def check_conversation_owner(
    cursor,
    conversation_id,
    user_id,
    lock=False,
):

    table = (
        "dbo.CuocHoiThoai WITH (UPDLOCK, HOLDLOCK)"
        if lock
        else "dbo.CuocHoiThoai"
    )

    cursor.execute(
        f"""
        SELECT MaCuocHoiThoai
        FROM {table}
        WHERE
            MaCuocHoiThoai = ?
            AND MaNguoiDung = ?
        """,
        conversation_id,
        user_id,
    )

    if cursor.fetchone() is None:
        raise LookupError(
            "Không tìm thấy cuộc trò chuyện "
            "thuộc tài khoản này."
        )


# ==========================================================
# 05. TẠO TIÊU ĐỀ HỘI THOẠI
#
# Lấy từ câu hỏi đầu tiên.
# ==========================================================

def make_conversation_title(question):

    title = " ".join(
        str(question or "").split()
    )

    if len(title) > 80:
        title = title[:77].rstrip() + "..."

    return title or "Cuộc trò chuyện mới"


# ==========================================================
# 06. LƯU MỘT LƯỢT HỎI VÀ ĐÁP
#
# Bảng:
# - CuocHoiThoai
# - TinNhan
#
# Nếu conversation_id = None:
#     Tạo hội thoại mới.
#
# Nếu đã có conversation_id:
#     Kiểm tra quyền sở hữu trước khi ghi.
#
# Hai tin nhắn được lưu trong cùng giao dịch.
# ==========================================================

def save_exchange(
    user_id,
    question,
    answer,
    conversation_id=None,
    intent=None,
    model=None,
    source="chi_ai",
):

    user_id = validate_user_id(user_id)

    question = str(question or "").strip()
    answer = str(answer or "").strip()

    if not 1 <= len(question) <= 2000:
        raise ValueError(
            "Câu hỏi phải có từ 1 đến 2000 ký tự."
        )

    if not answer:
        raise ValueError(
            "Không thể lưu câu trả lời rỗng."
        )

    if len(answer) > 20000:
        raise ValueError(
            "Câu trả lời vượt quá giới hạn lưu trữ."
        )

    if source not in VALID_SOURCES:
        raise ValueError(
            "Loại nguồn câu trả lời không hợp lệ."
        )

    if intent is not None:
        intent = str(intent).strip()[:50] or None

    if model is not None:
        model = str(model).strip()[:200] or None

    if conversation_id is not None:
        conversation_id = validate_conversation_id(
            conversation_id
        )

    with closing(get_connection()) as conn:

        try:
            with closing(conn.cursor()) as cursor:

                # ======================================
                # A. TẠO CUỘC TRÒ CHUYỆN MỚI
                # ======================================

                if conversation_id is None:

                    session_id = str(uuid.uuid4())

                    title = make_conversation_title(
                        question
                    )

                    cursor.execute(
                        """
                        INSERT INTO dbo.CuocHoiThoai
                        (
                            MaNguoiDung,
                            MaPhien,
                            TieuDe,
                            NgayTao
                        )
                        OUTPUT INSERTED.MaCuocHoiThoai
                        VALUES
                        (
                            ?, ?, ?, SYSDATETIME()
                        )
                        """,
                        user_id,
                        session_id,
                        title,
                    )

                    conversation_id = int(
                        cursor.fetchone()[0]
                    )

                # ======================================
                # B. HỘI THOẠI CŨ
                # ======================================

                else:

                    check_conversation_owner(
                        cursor,
                        conversation_id,
                        user_id,
                        lock=True,
                    )

                # ======================================
                # C. LƯU TIN NGƯỜI HỌC
                # ======================================

                cursor.execute(
                    """
                    INSERT INTO dbo.TinNhan
                    (
                        MaCuocHoiThoai,
                        VaiTro,
                        NoiDung,
                        YDinh,
                        TenMoHinh,
                        LoaiNguonTraLoi,
                        NgayTao
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, NULL, NULL,
                        SYSDATETIME()
                    )
                    """,
                    conversation_id,
                    USER_ROLE,
                    question,
                    intent,
                )

                # ======================================
                # D. LƯU PHẢN HỒI CỦA CHATBOT
                # ======================================

                cursor.execute(
                    """
                    INSERT INTO dbo.TinNhan
                    (
                        MaCuocHoiThoai,
                        VaiTro,
                        NoiDung,
                        YDinh,
                        TenMoHinh,
                        LoaiNguonTraLoi,
                        NgayTao
                    )
                    VALUES
                    (
                        ?, ?, ?, ?, ?, ?,
                        SYSDATETIME()
                    )
                    """,
                    conversation_id,
                    ASSISTANT_ROLE,
                    answer,
                    intent,
                    model,
                    source,
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

    return conversation_id


# ==========================================================
# 07. LẤY DANH SÁCH CUỘC TRÒ CHUYỆN
#
# Chỉ trả về dữ liệu của người học hiện tại.
# Tối đa 50 cuộc trò chuyện gần nhất.
# ==========================================================

def list_conversations(user_id):

    user_id = validate_user_id(user_id)

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT TOP (50)
                    MaCuocHoiThoai,
                    TieuDe,
                    NgayTao
                FROM dbo.CuocHoiThoai
                WHERE MaNguoiDung = ?
                ORDER BY
                    NgayTao DESC,
                    MaCuocHoiThoai DESC
                """,
                user_id,
            )

            rows = cursor.fetchall()

    return [
        {
            "id": int(row[0]),
            "title": (
                row[1] or "Cuộc trò chuyện"
            ),
            "created_at": (
                row[2].isoformat()
                if row[2] is not None
                else None
            ),
        }
        for row in rows
    ]


# ==========================================================
# 08. XEM CHI TIẾT CUỘC TRÒ CHUYỆN
#
# Trả về tối đa 200 tin nhắn mới nhất,
# theo đúng thứ tự gửi.
#
# Chuyển VaiTro SQL thành role cho frontend:
# nguoi_dung -> user
# tro_ly     -> assistant
# ==========================================================

def get_conversation(
    user_id,
    conversation_id,
):

    user_id = validate_user_id(user_id)

    conversation_id = validate_conversation_id(
        conversation_id
    )

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:

            cursor.execute(
                """
                SELECT
                    MaCuocHoiThoai,
                    TieuDe,
                    NgayTao
                FROM dbo.CuocHoiThoai
                WHERE
                    MaCuocHoiThoai = ?
                    AND MaNguoiDung = ?
                """,
                conversation_id,
                user_id,
            )

            conversation = cursor.fetchone()

            if conversation is None:
                raise LookupError(
                    "Không tìm thấy cuộc trò chuyện "
                    "thuộc tài khoản này."
                )

            cursor.execute(
                """
                SELECT *
                FROM
                (
                    SELECT TOP (200)
                        MaTinNhan,
                        VaiTro,
                        NoiDung,
                        NgayTao
                    FROM dbo.TinNhan
                    WHERE MaCuocHoiThoai = ?
                    ORDER BY MaTinNhan DESC
                ) AS RecentMessages
                ORDER BY MaTinNhan ASC
                """,
                conversation_id,
            )

            rows = cursor.fetchall()

    messages = []

    for row in rows:

        role = (
            "user"
            if row[1] == USER_ROLE
            else "assistant"
        )

        messages.append({
            "id": int(row[0]),
            "role": role,
            "content": row[2],
            "created_at": (
                row[3].isoformat()
                if row[3] is not None
                else None
            ),
        })

    return {
        "id": int(conversation[0]),
        "conversation_id": int(conversation[0]),
        "title": conversation[1] or "Cuộc trò chuyện",
        "messages": messages,
    }


# ==========================================================
# 09. LẤY NGỮ CẢNH HỘI THOẠI CHO QWEN3
#
# Lấy 10 tin nhắn gần nhất làm ngữ cảnh.
# Không gửi toàn bộ lịch sử để tránh quá tải
# mô hình Qwen3 1.7B.
#
# Chỉ nhận lịch sử từ SQL Server,
# không tin danh sách do trình duyệt tự gửi.
# ==========================================================

def get_recent_messages(
    user_id,
    conversation_id,
    limit=10,
):

    user_id = validate_user_id(user_id)

    conversation_id = validate_conversation_id(
        conversation_id
    )

    limit = max(1, min(int(limit), 20))

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:

            check_conversation_owner(
                cursor,
                conversation_id,
                user_id,
            )

            cursor.execute(
                f"""
                SELECT TOP ({limit})
                    VaiTro,
                    NoiDung
                FROM dbo.TinNhan
                WHERE MaCuocHoiThoai = ?
                ORDER BY MaTinNhan DESC
                """,
                conversation_id,
            )

            rows = cursor.fetchall()

    messages = []

    for role, content in reversed(rows):

        messages.append({
            "role": (
                "user"
                if role == USER_ROLE
                else "assistant"
            ),
            "content": str(content)[:3000],
        })

    return messages
