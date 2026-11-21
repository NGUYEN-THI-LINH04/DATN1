
from collections import defaultdict
from contextlib import closing
from datetime import datetime, timedelta, timezone
from routes.exam_statistics import get_student_exam_stats
from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    url_for,
)

from database import get_connection


# =========================================================
# MOC HAN - TIEN DO HOC TAP
# =========================================================

progress_bp = Blueprint(
    "progress",
    __name__,
    url_prefix="/progress"
)

# Mui gio Viet Nam
VN_TZ = timezone(timedelta(hours=7))


# =========================================================
# 1. HAM HO TRO
# =========================================================

def get_student_id():
    """
    Lay ID cua nguoi hoc dang dang nhap.
    Chi tai khoan student moi duoc xem tien do.
    """

    account = getattr(g, "account", None)

    if not account or account.get("role") != "student":
        return None

    return int(account["id"])


def scalar(cursor, sql, *params):
    """
    Lay mot gia tri duy nhat tu SQL Server.
    Neu ket qua rong thi tra ve 0.
    """

    cursor.execute(sql, *params)

    row = cursor.fetchone()

    if row is None or row[0] is None:
        return 0

    return row[0]


# =========================================================
# 2. THONG KE TU VUNG
# =========================================================

def get_vocabulary_stats(cursor, user_id):
    """
    Lay thong ke tu vung thuc te.

    Su dung cac bang:
        dbo.TuVung
        dbo.TuVungDaLuu
        dbo.LichSuOnTap
        dbo.TuVungBaiHoc
        dbo.BaiHoc
        dbo.KhoaHoc
    """

    # -----------------------------------------------------
    # TONG SO TU TRONG KHO
    # -----------------------------------------------------
    # Khong loc DaDuyet = 1 vi se lam sai tong so tu.
    # Mot MaTuVung chi duoc tinh mot lan.

    total = scalar(
        cursor,
        """
        SELECT COUNT(*)
        FROM dbo.TuVung
        """
    )

    # -----------------------------------------------------
    # SO TU DA DUYET
    # -----------------------------------------------------

    approved = scalar(
        cursor,
        """
        SELECT COUNT(*)
        FROM dbo.TuVung
        WHERE DaDuyet = 1
        """
    )

    # -----------------------------------------------------
    # SO TU NGUOI HOC DA LUU
    # -----------------------------------------------------

    saved = scalar(
        cursor,
        """
        SELECT COUNT(DISTINCT MaTuVung)
        FROM dbo.TuVungDaLuu
        WHERE MaNguoiDung = ?
        """,
        user_id
    )

    # -----------------------------------------------------
    # SO TU KHAC NHAU DA TUNG ON
    # -----------------------------------------------------
    # Neu mot tu duoc on nhieu lan van chi tinh mot tu.

    reviewed = scalar(
        cursor,
        """
        SELECT COUNT(DISTINCT MaTuVung)
        FROM dbo.LichSuOnTap
        WHERE MaNguoiDung = ?
        """,
        user_id
    )

    # -----------------------------------------------------
    # SO TU THEO CAP DO HSK1 - HSK4
    # -----------------------------------------------------
    # Dem DISTINCT de tranh mot tu xuat hien nhieu
    # bai hoc trong cung cap HSK bi tinh trung.

    cursor.execute(
        """
        SELECT
            kh.MaCapDo,
            COUNT(DISTINCT tvbh.MaTuVung) AS SoTu

        FROM dbo.TuVungBaiHoc AS tvbh

        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = tvbh.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc = bh.MaKhoaHoc

        WHERE kh.MaCapDo BETWEEN 1 AND 4

        GROUP BY kh.MaCapDo

        ORDER BY kh.MaCapDo
        """
    )

    level_counts = {
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }

    for level, count in cursor.fetchall():
        level_counts[int(level)] = int(count or 0)

    return {
        "total": int(total),
        "approved": int(approved),
        "saved": int(saved),
        "reviewed": int(reviewed),
        "level_counts": level_counts,
    }


# =========================================================
# 3. THONG KE BAI TAP
# =========================================================

def get_exercise_stats(cursor, user_id):
    """
    Thong ke ket qua bai tap da nop.

    Khong tinh bai dang lam do.
    Khong tu tao ket qua cho nguoi hoc.
    """

    cursor.execute(
        """
        SELECT
            COUNT(*) AS SoLuotNop,

            COUNT(DISTINCT MaBaiTap) AS SoBai,

            AVG(
                CASE
                    WHEN Diem IS NOT NULL
                         AND DiemToiDaLucLam > 0
                    THEN
                        CAST(Diem AS FLOAT)
                        * 100.0
                        / DiemToiDaLucLam

                    ELSE NULL
                END
            ) AS DiemTrungBinh

        FROM dbo.LanLamBai

        WHERE MaNguoiDung = ?
          AND NgayNop IS NOT NULL
        """,
        user_id
    )

    row = cursor.fetchone()

    return {
        "attempts": int(row[0] or 0),
        "exercises": int(row[1] or 0),
        "average": round(float(row[2] or 0)),
    }


# =========================================================
# 4. THONG KE SHADOWING
# =========================================================

def get_shadowing_stats(cursor, user_id):
    """
    Tong hop ket qua Shadowing cua nguoi hoc.

    Hai che do:
        dictation = Chep chinh ta
        assemble = Ghep cau

    Moi cau + moi che do chi lay ket qua moi nhat
    de khong tinh trung nhieu lan lam.
    """

    cursor.execute(
        """
        WITH KetQuaMoiNhat AS
        (
            SELECT
                MaNoiDung,
                CheDo,
                ViTriCau,
                Diem,
                LaDapAnDung,

                ROW_NUMBER() OVER
                (
                    PARTITION BY
                        MaNoiDung,
                        CheDo,
                        ViTriCau

                    ORDER BY
                        ThoiDiemLam DESC,
                        MaKetQuaShadowing DESC

                ) AS STT

            FROM dbo.KetQuaShadowing

            WHERE MaNguoiDung = ?
        )

        SELECT
            MaNoiDung,
            CheDo,
            ViTriCau,
            Diem,
            LaDapAnDung

        FROM KetQuaMoiNhat

        WHERE STT = 1
        """,
        user_id
    )

    videos = set()
    sentences = set()

    modes = {
        "dictation": {
            "done": 0,
            "correct": 0,
            "scores": []
        },
        "assemble": {
            "done": 0,
            "correct": 0,
            "scores": []
        }
    }

    for row in cursor.fetchall():

        content_id = int(row[0])
        mode = str(row[1]).strip().lower()
        sentence_index = int(row[2])

        # Chi tinh hai che do Shadowing dang su dung.
        if mode not in modes:
            continue

        videos.add(content_id)

        sentences.add(
            (content_id, sentence_index)
        )

        modes[mode]["done"] += 1

        modes[mode]["correct"] += int(
            row[4] or 0
        )

        modes[mode]["scores"].append(
            float(row[3] or 0)
        )

    # -----------------------------------------------------
    # TINH DIEM TRUNG BINH MOI CHE DO
    # -----------------------------------------------------

    for item in modes.values():

        scores = item.pop("scores")

        if scores:
            item["average"] = round(
                sum(scores) / len(scores)
            )
        else:
            item["average"] = 0

    # -----------------------------------------------------
    # DEM SO VIDEO SHADOWING TRONG HE THONG
    # -----------------------------------------------------
    # NoiDung la JSON, module = shadowing.
    # CASE kiem tra JSON hop le truoc khi doc module.

    total_videos = scalar(
        cursor,
        """
        SELECT COUNT(*)

        FROM dbo.NoiDungBaiHoc

        WHERE
            CASE
                WHEN ISJSON(NoiDung) = 1
                THEN JSON_VALUE(
                    NoiDung,
                    '$.module'
                )
                ELSE NULL
            END = 'shadowing'
        """
    )

    return {
        "videos": len(videos),
        "total_videos": int(total_videos),
        "sentences": len(sentences),

        "attempted_modes": sum(
            item["done"]
            for item in modes.values()
        ),

        "modes": modes,
    }


# =========================================================
# 5. LICH HOAT DONG 365 NGAY
# =========================================================

def get_activity(cursor, user_id):
    """
    Lay du lieu hoat dong hoc tap trong 365 ngay.

    Nguon du lieu:
        KetQuaShadowing
        LichSuOnTap
        LanLamBai

    Ket qua duoc tra ve theo tung ngay YYYY-MM-DD
    de HTML/JavaScript hien thi lich theo thang.
    """

    # -----------------------------------------------------
    # LAY CAC HOAT DONG DA LUU TRONG SQL
    # -----------------------------------------------------

    cursor.execute(
        """
        SELECT
            ThoiDiemLam AS ThoiGian,
            'shadowing' AS Nguon

        FROM dbo.KetQuaShadowing

        WHERE MaNguoiDung = ?

        UNION ALL

        SELECT
            NgayOn AS ThoiGian,
            'vocabulary' AS Nguon

        FROM dbo.LichSuOnTap

        WHERE MaNguoiDung = ?

        UNION ALL

        SELECT
            NgayNop AS ThoiGian,
            'exercise' AS Nguon

        FROM dbo.LanLamBai

        WHERE MaNguoiDung = ?
          AND NgayNop IS NOT NULL
        """,
        user_id,
        user_id,
        user_id
    )

    today = datetime.now(VN_TZ).date()

    daily = defaultdict(int)

    # -----------------------------------------------------
    # GOM SO HOAT DONG THEO NGAY
    # -----------------------------------------------------

    for timestamp, source in cursor.fetchall():

        if timestamp is None:
            continue

        if source == "shadowing":

            # Shadowing duoc luu theo gio UTC.
            # Quy doi sang ngay gio Viet Nam.

            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(
                    tzinfo=timezone.utc
                )

            day = timestamp.astimezone(
                VN_TZ
            ).date()

        else:

            # Giu cach doc ngay cua hai nguon con lai
            # nhu trong progress.py ban dau.

            day = timestamp.date()

        # Khong tinh du lieu co ngay trong tuong lai.
        if day <= today:
            daily[day] += 1

    # -----------------------------------------------------
    # TINH CHUOI NGAY HOC LIEN TIEP
    # -----------------------------------------------------

    anchor = today

    # Neu hom nay chua hoc, tinh chuoi tu hom qua.
    if daily.get(today, 0) == 0:
        anchor = today - timedelta(days=1)

    streak = 0

    while daily.get(anchor, 0) > 0:

        streak += 1

        anchor -= timedelta(days=1)

    # -----------------------------------------------------
    # TAO DU LIEU CHO 365 NGAY
    # -----------------------------------------------------

    start = today - timedelta(days=364)

    calendar = []

    for i in range(365):

        day = start + timedelta(days=i)

        count = daily.get(day, 0)

        # Cap do mau theo so hoat dong trong ngay.

        if count == 0:
            level = 0

        elif count <= 2:
            level = 1

        elif count <= 5:
            level = 2

        elif count <= 10:
            level = 3

        else:
            level = 4

        calendar.append({
            "date": day.isoformat(),
            "count": int(count),
            "level": level,
        })

    return {
        "streak": streak,

        "today": int(
            daily.get(today, 0)
        ),

        "today_date": today.isoformat(),

        "start_date": start.isoformat(),

        "end_date": today.isoformat(),

        "calendar": calendar,
    }


# =========================================================
# 6. VIDEO SHADOWING GAN DAY
# =========================================================

def get_recent_shadowing(cursor, user_id):
    """
    Lay toi da 5 video Shadowing
    nguoi hoc luyen gan nhat.
    """

    cursor.execute(
        """
        SELECT TOP (5)
            k.MaNoiDung,
            nd.TieuDe,

            MAX(
                k.ThoiDiemLam
            ) AS LanLuyenCuoi,

            COUNT(*) AS SoLanLam

        FROM dbo.KetQuaShadowing AS k

        INNER JOIN dbo.NoiDungBaiHoc AS nd
            ON nd.MaNoiDung = k.MaNoiDung

        WHERE k.MaNguoiDung = ?

        GROUP BY
            k.MaNoiDung,
            nd.TieuDe

        ORDER BY
            LanLuyenCuoi DESC
        """,
        user_id
    )

    result = []

    for row in cursor.fetchall():

        result.append({
            "content_id": int(row[0]),

            "title": row[1] or "Video Shadowing",

            "last_practiced": row[2],

            "attempts": int(row[3] or 0),
        })

    return result


# =========================================================
# 7. ROUTE TRANG TIEN DO HOC
# =========================================================

@progress_bp.route("/", methods=["GET"])
def index():

    # -----------------------------------------------------
    # KIEM TRA NGUOI HOC DANG NHAP
    # -----------------------------------------------------

    user_id = get_student_id()

    if user_id is None:

        return redirect(
            url_for(
                "auth.login",
                next="/progress/"
            )
        )

    # -----------------------------------------------------
    # LAY DU LIEU THUC TE TU SQL SERVER
    # -----------------------------------------------------

    with closing(get_connection()) as connection:

        with closing(connection.cursor()) as cursor:

            # Thong ke tu vung
            vocabulary = get_vocabulary_stats(
                cursor,
                user_id
            )

            # Ket qua bai tap
            exercises = get_exercise_stats(
                cursor,
                user_id
            )

            # Ket qua Shadowing
            shadowing = get_shadowing_stats(
                cursor,
                user_id
            )

            # Lich hoc 365 ngay
            activity = get_activity(
                cursor,
                user_id
            )

            # Video Shadowing gan day
            recent = get_recent_shadowing(
                cursor,
                user_id
            )
            # Thong ke Luyen thi HSK tu SQL.
            exam_stats = get_student_exam_stats(
                 cursor,
                 user_id
)
    # -----------------------------------------------------
    # TRUYEN DU LIEU SANG HTML
    # -----------------------------------------------------

    return render_template(
        "student/progress.html",

        vocabulary=vocabulary,

        exercises=exercises,

        shadowing=shadowing,

        activity=activity,

        recent=recent,

        exam_stats=exam_stats,
    )
