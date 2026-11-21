
# -*- coding: utf-8 -*-
"""
MỘC HÁN - NHẬP ĐỀ THI HSK VÀO SQL SERVER

--check: Kiểm tra JSON, hình ảnh, MP3; không sửa SQL.
--import: Nhập đề vào SQL bằng transaction.

- Hỗ trợ thời gian thi từ thoi_gian_phut trong JSON.
- Tương thích với JSON Đề 1 chưa có thời gian thi.
- Không sửa dữ liệu Bài tập cũ.
- Không tạo lại ảnh hoặc âm thanh.
- Không nhập trùng hoặc tự ghi đè đề đã tồn tại.
- Đề mới ở trạng thái bản nháp, câu hỏi chưa duyệt.
"""

import argparse
import json
import os
import re

from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath


# ==================================================
# 0. CẤU HÌNH
# ==================================================

ROOT = Path(__file__).resolve().parents[2]

DEFAULT_JSON = (
    ROOT / "scripts" / "luyen_thi"
    / "hsk1" / "data" / "de_01" / "de_01.json"
)

# Giữ nguyên tên database của file gốc.
# Nếu database thực tế có tên khác, phải sửa
# đúng tên trước khi chạy --import.
DB_NAME = "HocTiengTrungDB"


# ==================================================
# 1. CÁC HÀM KIỂM TRA
# ==================================================

def require(condition, message):
    if not condition:
        raise ValueError(message)


def media_file(url):

    require(
        isinstance(url, str)
        and url.startswith("/static/media/luyen_thi/"),
        f"Đường dẫn media không hợp lệ: {url}"
    )

    path = PurePosixPath(url)

    require(
        ".." not in path.parts
        and "\\" not in url
        and "?" not in url,
        f"Đường dẫn media không an toàn: {url}"
    )

    local_file = ROOT.joinpath(*path.parts[1:])

    require(
        local_file.is_file(),
        f"Không tìm thấy file: {local_file}"
    )

    return local_file


# ==================================================
# 2. ĐỌC VÀ KIỂM TRA JSON
# ==================================================

def read_data(path):

    require(
        path.is_file(),
        f"Không tìm thấy JSON: {path}"
    )

    data = json.loads(
        path.read_text(encoding="utf-8-sig")
    )

    require(
        isinstance(data, dict),
        "JSON đề thi không hợp lệ."
    )

    # ----------------------------------------------
    # 2.1. MÃ ĐỀ
    # ----------------------------------------------

    code = str(
        data.get("ma_de_goc", "")
    ).strip()

    require(
        re.fullmatch(
            r"[A-Za-z0-9_-]{1,50}", code
        ) is not None,
        "Mã đề gốc không hợp lệ."
    )

    # ----------------------------------------------
    # 2.2. CẤP HSK
    # ----------------------------------------------

    level = data.get("cap_hsk")

    require(
        type(level) is int and 1 <= level <= 4,
        "Cấp HSK phải từ 1 đến 4."
    )

    # ----------------------------------------------
    # 2.3. TÊN ĐỀ
    # ----------------------------------------------

    title = str(
        data.get("ten_hien_thi", "")
    ).strip()

    require(
        0 < len(title) <= 150,
        "Tên đề không hợp lệ."
    )

    # ----------------------------------------------
    # 2.4. THỨ TỰ ĐỀ
    # ----------------------------------------------

    sequence = data.get("thu_tu")

    if sequence is None:

        for name in (path.parent.name, path.stem):

            match = re.fullmatch(
                r"de[_-]?(\d+)",
                name,
                re.IGNORECASE
            )

            if match:
                sequence = int(match.group(1))
                break

    require(
        type(sequence) is int and sequence > 0,
        "Không xác định được thứ tự đề."
    )

    # ----------------------------------------------
    # 2.5. THỜI GIAN THI - PHẦN ĐÃ SỬA
    #
    # Đề 2: lấy 32 phút từ JSON H10901.
    # Đề cũ: nếu chưa có trường này, để None.
    # Không lấy thời lượng MP3 làm thời gian thi.
    # ----------------------------------------------

    time_minutes = data.get("thoi_gian_phut")

    if time_minutes is not None:

        require(
            type(time_minutes) is int
            and 1 <= time_minutes <= 300,
            "Thời gian thi phải là số nguyên "
            "từ 1 đến 300 phút."
        )

    # ----------------------------------------------
    # 2.6. DANH SÁCH CÂU HỎI
    # ----------------------------------------------

    questions = data.get("cau_hoi")

    require(
        isinstance(questions, list)
        and len(questions) > 0,
        "Thiếu danh sách câu hỏi."
    )

    require(
        len(questions) == data.get("so_cau"),
        "Tổng số câu không khớp."
    )

    counters = {
        "nghe": 0,
        "doc": 0,
        "viet": 0
    }

    normalized = []

    for question in questions:

        number = question.get("so_cau")

        require(
            type(number) is int and number > 0,
            "Số câu không hợp lệ."
        )

        skill = question.get("ky_nang")

        require(
            skill in counters,
            f"Sai kỹ năng ở câu {number}."
        )

        counters[skill] += 1

        part = str(
            question.get("phan") or ""
        ).strip()

        question_type = str(
            question.get("loai_cau_hoi") or ""
        ).strip()

        require(
            0 < len(part) <= 60
            and 0 < len(question_type) <= 60,
            f"Thiếu phần hoặc loại ở câu {number}."
        )

        # ------------------------------------------
        # ĐÁP ÁN
        # ------------------------------------------

        answer = question.get("dap_an_dung")

        if isinstance(answer, (dict, list)):

            answer = json.dumps(
                answer,
                ensure_ascii=False
            )

        else:

            answer = str(
                answer if answer is not None else ""
            ).strip()

        require(
            bool(answer),
            f"Thiếu đáp án câu {number}."
        )

        # ------------------------------------------
        # HÌNH ẢNH
        # ------------------------------------------

        question_image = question.get("anh_cau_hoi")

        group_image = question.get(
            "anh_nhom_lua_chon"
        )

        content = question.get("noi_dung")

        for url in (question_image, group_image):

            if url is not None:
                media_file(url)

        require(
            question_image or group_image or content,
            f"Câu {number} không có nội dung hoặc ảnh."
        )

        # ------------------------------------------
        # LỰA CHỌN JSON
        # ------------------------------------------

        options = question.get("lua_chon_json")

        if (
            options is not None
            and not isinstance(options, str)
        ):

            options = json.dumps(
                options,
                ensure_ascii=False
            )

        if options is not None:
            json.loads(options)

        normalized.append((
            number,
            skill,
            part,
            question_type,
            content,
            question_image,
            group_image,
            options,
            answer
        ))

    # ----------------------------------------------
    # 2.7. KIỂM TRA THỨ TỰ CÂU
    # ----------------------------------------------

    normalized.sort(key=lambda item: item[0])

    require(
        [q[0] for q in normalized]
        == list(range(1, len(normalized) + 1)),
        "Số câu không liên tục, bị thiếu hoặc trùng."
    )

    # ----------------------------------------------
    # 2.8. KIỂM TRA SỐ CÂU THEO KỸ NĂNG
    # ----------------------------------------------

    for skill, key in (
        ("nghe", "so_cau_nghe"),
        ("doc", "so_cau_doc"),
        ("viet", "so_cau_viet")
    ):

        require(
            counters[skill] == data.get(key),
            f"Số câu {skill} không khớp."
        )

    # ----------------------------------------------
    # 2.9. AUDIO MP3
    #
    # Giữ một file MP3 cho toàn bộ phần Nghe.
    # ----------------------------------------------

    audio = data.get("audio") or {}

    audio_url = audio.get("duong_dan")

    if counters["nghe"] > 0:

        require(
            bool(audio_url),
            "Đề có phần Nghe nhưng thiếu MP3."
        )

    if audio_url:

        require(
            media_file(audio_url).suffix.lower() == ".mp3",
            "File nghe phải có đuôi .mp3."
        )

    try:

        audio_length = (
            Decimal(str(audio.get("thoi_luong_giay")))
            if audio_url else None
        )

    except (InvalidOperation, TypeError) as error:

        raise ValueError(
            "Thời lượng MP3 không hợp lệ."
        ) from error

    if audio_length is not None:

        require(
            audio_length.is_finite()
            and Decimal("0") < audio_length
            < Decimal("99999999"),
            "Thời lượng MP3 phải lớn hơn 0."
        )

    # ----------------------------------------------
    # 2.10. PHIÊN BẢN HSK
    # ----------------------------------------------

    version = data.get("phien_ban_hsk")

    if version in (
        "chua_xac_minh", "", None
    ):
        version = None

    if version is not None:

        require(
            isinstance(version, str)
            and len(version) <= 60,
            "Phiên bản HSK không hợp lệ."
        )

    # ----------------------------------------------
    # 2.11. DỮ LIỆU CHUẨN HÓA
    # ----------------------------------------------

    return {
        "code": code,
        "level": level,
        "title": title,
        "sequence": sequence,
        "version": version,
        "counts": counters,
        "questions": normalized,
        "audio_url": audio_url,
        "audio_length": audio_length,
        "time_minutes": time_minutes
    }


# ==================================================
# 3. KẾT NỐI SQL SERVER
# ==================================================

def connect(server):

    import pyodbc

    available_drivers = pyodbc.drivers()

    driver = next(
        (
            name for name in (
                "ODBC Driver 18 for SQL Server",
                "ODBC Driver 17 for SQL Server"
            )
            if name in available_drivers
        ),
        None
    )

    require(
        driver is not None,
        "Chưa cài ODBC Driver 17/18 for SQL Server."
    )

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={DB_NAME}",
        "Encrypt=yes",
        "TrustServerCertificate=yes",
        "Connection Timeout=10"
    ]

    sql_user = os.environ.get("SQL_USER")

    if sql_user:

        require(
            bool(os.environ.get("SQL_PASSWORD")),
            "Đã đặt SQL_USER nhưng thiếu SQL_PASSWORD."
        )

        parts.extend([
            f"UID={sql_user}",
            f"PWD={os.environ['SQL_PASSWORD']}"
        ])

    else:

        parts.append("Trusted_Connection=yes")

    return pyodbc.connect(
        ";".join(parts),
        autocommit=False
    )


# ==================================================
# 4. LƯU THÔNG TIN MP3
# ==================================================

def get_media(cursor, info):

    audio_url = info["audio_url"]

    if not audio_url:
        return None

    # ----------------------------------------------
    # 4.1. KIỂM TRA FILE MEDIA ĐÃ TỒN TẠI
    # ----------------------------------------------

    cursor.execute(
        """
        SELECT MaTep
        FROM dbo.TepDaPhuongTien
             WITH (UPDLOCK, HOLDLOCK)
        WHERE DuongDanTep = ?
        """,
        audio_url
    )

    matches = cursor.fetchall()

    require(
        len(matches) <= 1,
        "Có nhiều bản ghi media trùng đường dẫn."
    )

    if matches:
        return int(matches[0][0])

    # ----------------------------------------------
    # 4.2. THÊM MEDIA MỚI
    # ----------------------------------------------

    cursor.execute(
        """
        INSERT INTO dbo.TepDaPhuongTien
        (
            LoaiTep,
            DuongDanTep,
            TieuDe,
            LoiThoai,
            MaNguon,
            NgayTao,
            MaQuanTriVienCapNhat,
            NgayCapNhat
        )
        OUTPUT INSERTED.MaTep
        VALUES
        (
            'am_thanh',
            ?, ?,
            NULL, NULL,
            SYSUTCDATETIME(),
            NULL, NULL
        )
        """,
        audio_url,
        (
            f"HSK{info['level']} - "
            f"{info['code']} - Audio đề thi"
        )
    )

    return int(cursor.fetchone()[0])


# ==================================================
# 5. NHẬP ĐỀ THI VÀ CÂU HỎI
# ==================================================

def import_exam(connection, info):

    cursor = connection.cursor()

    try:

        # ------------------------------------------
        # 5.1. XÁC NHẬN DATABASE
        # ------------------------------------------

        cursor.execute(
            "SELECT DB_NAME(), @@SERVERNAME"
        )

        database_name, server_name = cursor.fetchone()

        require(
            database_name == DB_NAME,
            "Đang kết nối sai database."
        )

        print(f"SQL Server: {server_name}")
        print(f"Database: {database_name}")

        # ------------------------------------------
        # 5.2. KIỂM TRA CẤP HSK
        # ------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM dbo.CapDoHSK
            WHERE MaCapDo = ?
            """,
            info["level"]
        )

        require(
            cursor.fetchone()[0] == 1,
            "Cấp HSK không tồn tại trong SQL."
        )

        # ------------------------------------------
        # 5.3. LẤY MÃ AUDIO
        # ------------------------------------------

        media_id = get_media(cursor, info)

        # ------------------------------------------
        # 5.4. KIỂM TRA ĐỀ ĐÃ TỒN TẠI
        #
        # Bổ sung kiểm tra ThoiGianPhut.
        # Không tự ghi đè đề cũ.
        # ------------------------------------------

        cursor.execute(
            """
            SELECT
                MaDeThi,
                ThuTu,
                TenDe,
                MaTepAudio,
                TongSoCau,
                SoCauNghe,
                SoCauDoc,
                SoCauViet,
                ThoiGianPhut
            FROM dbo.DeThiHSK
                 WITH (UPDLOCK, HOLDLOCK)
            WHERE MaCapDo = ?
              AND MaDeGoc = ?
            """,
            info["level"],
            info["code"]
        )

        existing = cursor.fetchone()

        if existing:

            exam_id = int(existing[0])

            expected = (
                info["sequence"],
                info["title"],
                media_id,
                len(info["questions"]),
                info["counts"]["nghe"],
                info["counts"]["doc"],
                info["counts"]["viet"]
            )

            require(
                tuple(existing[1:8]) == expected,
                "Đề đã tồn tại nhưng thông tin khác. "
                "Không tự ghi đè."
            )

            # Với đề có thời gian trong JSON,
            # phải kiểm tra cả thời gian trong SQL.
            #
            # JSON cũ chưa có thời gian thì bỏ qua
            # so sánh để không ảnh hưởng H10000.

            if info["time_minutes"] is not None:

                require(
                    existing[8] == info["time_minutes"],
                    "Đề đã tồn tại nhưng thời gian "
                    "thi khác JSON. Không tự ghi đè."
                )

            # --------------------------------------
            # SO SÁNH TOÀN BỘ CÂU HỎI
            # --------------------------------------

            cursor.execute(
                """
                SELECT
                    SoCau,
                    KyNang,
                    Phan,
                    LoaiCauHoi,
                    NoiDung,
                    AnhCauHoi,
                    AnhNhomLuaChon,
                    LuaChonJson,
                    DapAnDung
                FROM dbo.CauHoiThiHSK
                WHERE MaDeThi = ?
                ORDER BY SoCau
                """,
                exam_id
            )

            db_questions = [
                tuple(row)
                for row in cursor.fetchall()
            ]

            require(
                db_questions == info["questions"],
                "Đề đã tồn tại nhưng nội dung câu hỏi "
                "khác JSON. Không tự ghi đè."
            )

            connection.rollback()

            print(
                f"Đề {info['code']} đã có đủ "
                f"{len(db_questions)} câu."
            )

            print("Không nhập lại dữ liệu.")

            return

        # ------------------------------------------
        # 5.5. THÊM THÔNG TIN ĐỀ HSK
        #
        # ThoiGianPhut đã sửa từ NULL thành ?.
        # ------------------------------------------

        cursor.execute(
            """
            INSERT INTO dbo.DeThiHSK
            (
                MaCapDo,
                MaDeGoc,
                ThuTu,
                TenDe,
                PhienBanHSK,
                TongSoCau,
                SoCauNghe,
                SoCauDoc,
                SoCauViet,
                ThoiGianPhut,
                MaTepAudio,
                ThoiLuongAudioGiay,
                TrangThai,
                MaQuanTriVienCapNhat,
                NgayTao,
                NgayCapNhat
            )
            OUTPUT INSERTED.MaDeThi
            VALUES
            (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                'ban_nhap',
                NULL,
                SYSUTCDATETIME(),
                NULL
            )
            """,
            info["level"],
            info["code"],
            info["sequence"],
            info["title"],
            info["version"],
            len(info["questions"]),
            info["counts"]["nghe"],
            info["counts"]["doc"],
            info["counts"]["viet"],
            info["time_minutes"],
            media_id,
            info["audio_length"]
        )

        exam_id = int(cursor.fetchone()[0])

        # ------------------------------------------
        # 5.6. THÊM TỪNG CÂU HỎI
        #
        # Không tự duyệt.
        # ------------------------------------------

        for (
            number,
            skill,
            part,
            question_type,
            content,
            question_image,
            group_image,
            options,
            answer
        ) in info["questions"]:

            cursor.execute(
                """
                INSERT INTO dbo.CauHoiThiHSK
                (
                    MaDeThi,
                    SoCau,
                    KyNang,
                    Phan,
                    LoaiCauHoi,
                    NoiDung,
                    AnhCauHoi,
                    AnhNhomLuaChon,
                    LuaChonJson,
                    DapAnDung,
                    GiaiThich,
                    DiemToiDa,
                    DaDuyet,
                    MaQuanTriVienCapNhat,
                    NgayCapNhat
                )
                VALUES
                (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    NULL, 1, 0, NULL, NULL
                )
                """,
                exam_id,
                number,
                skill,
                part,
                question_type,
                content,
                question_image,
                group_image,
                options,
                answer
            )

        # ------------------------------------------
        # 5.7. KIỂM TRA SAU INSERT
        # ------------------------------------------

        cursor.execute(
            """
            SELECT
                COUNT(*),
                SUM(
                    CASE WHEN KyNang = 'nghe'
                    THEN 1 ELSE 0 END
                ),
                SUM(
                    CASE WHEN KyNang = 'doc'
                    THEN 1 ELSE 0 END
                ),
                SUM(
                    CASE WHEN KyNang = 'viet'
                    THEN 1 ELSE 0 END
                ),
                SUM(
                    CASE
                        WHEN DapAnDung IS NOT NULL
                         AND LEN(DapAnDung) > 0
                        THEN 1 ELSE 0
                    END
                )
            FROM dbo.CauHoiThiHSK
            WHERE MaDeThi = ?
            """,
            exam_id
        )

        total, listening, reading, writing, answered = (
            cursor.fetchone()
        )

        require(
            (
                total,
                listening,
                reading,
                writing,
                answered
            ) == (
                len(info["questions"]),
                info["counts"]["nghe"],
                info["counts"]["doc"],
                info["counts"]["viet"],
                len(info["questions"])
            ),
            "Dữ liệu kiểm tra sau INSERT không đạt."
        )

        # ------------------------------------------
        # 5.8. COMMIT
        # ------------------------------------------

        connection.commit()

        print("\n========== NHẬP THÀNH CÔNG ==========")

        print("Mã đề thi SQL:", exam_id)
        print("Mã đề gốc:", info["code"])
        print("Tổng số câu:", total)
        print("Nghe:", listening)
        print("Đọc:", reading)
        print("Viết:", writing)
        print("Số đáp án:", answered)
        print("Mã file MP3:", media_id)

        print(
            "Thời gian thi:",
            f'{info["time_minutes"]} phút'
            if info["time_minutes"] is not None
            else "chưa thiết lập"
        )

        print("Trạng thái: ban_nhap")
        print("Câu hỏi: chưa duyệt")
        print("Không thay đổi các bảng Bài tập cũ.")

    except Exception:

        connection.rollback()
        raise

    finally:

        cursor.close()


# ==================================================
# 6. CHƯƠNG TRÌNH CHÍNH
# ==================================================

def main():

    parser = argparse.ArgumentParser(
        description="Nhập đề thi HSK từ JSON vào SQL"
    )

    mode = parser.add_mutually_exclusive_group(
        required=True
    )

    mode.add_argument(
        "--check",
        action="store_true",
        help="Chỉ kiểm tra, không nhập SQL"
    )

    mode.add_argument(
        "--import",
        dest="do_import",
        action="store_true",
        help="Nhập dữ liệu vào SQL"
    )

    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_JSON
    )

    parser.add_argument(
        "--server",
        default=None,
        help="Tên SQL Server trong SSMS"
    )

    args = parser.parse_args()

    # ----------------------------------------------
    # 6.1. ĐỌC VÀ KIỂM TRA JSON
    # ----------------------------------------------

    info = read_data(args.file)

    print("\n========== KIỂM TRA ĐỀ ==========")

    print("Mã đề:", info["code"])
    print("Cấp:", f"HSK{info['level']}")
    print("Tên:", info["title"])

    print(
        "Thời gian thi:",
        f'{info["time_minutes"]} phút'
        if info["time_minutes"] is not None
        else "chưa thiết lập trong JSON"
    )

    print("Tổng câu:", len(info["questions"]))
    print("Nghe:", info["counts"]["nghe"])
    print("Đọc:", info["counts"]["doc"])
    print("Viết:", info["counts"]["viet"])
    print("Audio:", info["audio_url"])

    # ----------------------------------------------
    # 6.2. CHỈ KIỂM TRA
    # ----------------------------------------------

    if args.check:

        print("\nKIỂM TRA ĐẠT.")
        print("Chưa kết nối hoặc thay đổi SQL.")

        return

    # ----------------------------------------------
    # 6.3. KẾT NỐI SQL SERVER
    # ----------------------------------------------

    server = (
        args.server
        or os.environ.get("SQL_SERVER")
        or os.environ.get("DB_SERVER")
    )

    if not server:

        server = input(
            "Nhập tên SQL Server trong SSMS "
            "(ví dụ .\\SQLEXPRESS): "
        ).strip()

    require(
        bool(server),
        "Chưa nhập tên SQL Server."
    )

    connection = connect(server)

    try:

        import_exam(connection, info)

    finally:

        connection.close()


if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        raise SystemExit(
            f"\nLỖI: {error}"
        )
