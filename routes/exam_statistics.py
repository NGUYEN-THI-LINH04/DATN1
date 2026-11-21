
# -*- coding: utf-8 -*-
"""
MOC HAN - THONG KE LUYEN THI HSK

Dung chung cho:
- Tien do hoc nguoi hoc
- Thong ke Admin (buoc tiep theo)

Du lieu:
- dbo.DeThiHSK
- dbo.CauHoiThiHSK
- dbo.LanThiHSK

Chi doc SQL, khong thay doi du lieu.
"""

from datetime import timedelta


# =====================================================
# 1. THONG KE DANH SACH DE THI
# =====================================================

def get_exam_catalog(cursor):

    levels = {
        level: {
            "level": level,
            "total": 0,
            "published": 0,
            "questions": 0,
            "approved": 0,
        }
        for level in range(1, 5)
    }

    cursor.execute("""
        SELECT
            d.MaCapDo,
            d.TrangThai,
            ISNULL(q.SoCau, 0),
            ISNULL(q.SoDuyet, 0)

        FROM dbo.DeThiHSK AS d

        LEFT JOIN (
            SELECT
                MaDeThi,
                COUNT(*) AS SoCau,
                SUM(
                    CASE WHEN DaDuyet = 1
                    THEN 1 ELSE 0 END
                ) AS SoDuyet
            FROM dbo.CauHoiThiHSK
            GROUP BY MaDeThi
        ) AS q
            ON q.MaDeThi = d.MaDeThi

        WHERE d.MaCapDo BETWEEN 1 AND 4
    """)

    for level, status, questions, approved in cursor.fetchall():

        item = levels[int(level)]

        item["total"] += 1
        item["questions"] += int(questions)
        item["approved"] += int(approved)

        if status == "da_xuat_ban":
            item["published"] += 1

    return levels


# =====================================================
# 2. QUY DOI DIEM SANG THANG 100
# =====================================================

def score_to_100(score, maximum):

    if (
        score is None
        or maximum is None
        or float(maximum) <= 0
    ):
        return None

    return round(
        float(score) * 100.0 / float(maximum),
        1
    )


# =====================================================
# 3. TIEN DO LUYEN THI CUA NGUOI HOC
# =====================================================

def get_student_exam_stats(cursor, user_id):

    levels = get_exam_catalog(cursor)

    for item in levels.values():
        item["attempts"] = 0
        item["full_attempts"] = 0
        item["practiced"] = 0
        item["completed"] = 0
        item["average"] = None
        item["best"] = None

        item["_practiced"] = set()
        item["_completed"] = set()
        item["_scores"] = []

    # ================================================
    # 4. DOC CAC LUOT THI DA CHAM
    # ================================================

    cursor.execute("""
        SELECT
            l.MaLanThi,
            l.MaDeThi,
            d.MaCapDo,
            d.TenDe,
            l.KyNang,
            l.Diem,
            l.DiemToiDaLucLam,
            l.NgayNop

        FROM dbo.LanThiHSK AS l

        INNER JOIN dbo.DeThiHSK AS d
            ON d.MaDeThi = l.MaDeThi

        WHERE l.MaNguoiDung = ?
          AND l.TrangThai = 'da_cham'
          AND l.NgayNop IS NOT NULL
          AND l.Diem IS NOT NULL
          AND l.DiemToiDaLucLam > 0
          AND d.MaCapDo BETWEEN 1 AND 4

        ORDER BY
            l.NgayNop DESC,
            l.MaLanThi DESC
    """, int(user_id))

    rows = cursor.fetchall()

    all_practiced = set()
    all_completed = set()
    all_full_scores = []

    recent = []
    full_attempts = 0

    # ================================================
    # 5. XU LY TUNG LUOT THI
    # ================================================

    for row in rows:

        attempt_id = int(row[0])
        exam_id = int(row[1])
        level = int(row[2])

        exam_name = row[3]
        skill = row[4]
        score = row[5]
        maximum = row[6]
        submitted = row[7]

        item = levels[level]

        item["attempts"] += 1

        item["_practiced"].add(exam_id)
        all_practiced.add(exam_id)

        result = score_to_100(
            score,
            maximum
        )

        # Cac luot lam ca de.
        if skill == "toan_bo":

            full_attempts += 1
            item["full_attempts"] += 1

            item["_completed"].add(exam_id)
            all_completed.add(exam_id)

            if result is not None:

                item["_scores"].append(result)
                all_full_scores.append(result)

        # ============================================
        # 6. LICH SU THI GAN DAY
        # ============================================

        if len(recent) < 5:

            skill_names = {
                "toan_bo": "Cả đề",
                "nghe": "Nghe",
                "doc": "Đọc",
                "viet": "Viết",
            }

            date_text = ""

            if submitted is not None:

                # NgayNop luu UTC.
                # Chuyen sang gio Viet Nam.
                date_text = (
                    submitted + timedelta(hours=7)
                ).strftime("%d/%m/%Y %H:%M")

            recent.append({
                "id": attempt_id,
                "level": level,
                "exam": exam_name,
                "skill": skill_names.get(
                    skill, skill
                ),
                "score": result,
                "date": date_text,
            })

    # ================================================
    # 7. TONG HOP THEO HSK
    # ================================================

    for item in levels.values():

        item["practiced"] = len(
            item.pop("_practiced")
        )

        item["completed"] = len(
            item.pop("_completed")
        )

        values = item.pop("_scores")

        if values:
            item["average"] = round(
                sum(values) / len(values), 1
            )

            item["best"] = max(values)

    # ================================================
    # 8. KET QUA CUOI
    # ================================================

    total_exams = sum(
        item["total"]
        for item in levels.values()
    )

    return {
        "total": total_exams,

        "published": sum(
            item["published"]
            for item in levels.values()
        ),

        "practiced": len(all_practiced),

        "completed": len(all_completed),

        "attempts": len(rows),

        "full_attempts": full_attempts,

        "skill_attempts": (
            len(rows) - full_attempts
        ),

        "average": (
            round(
                sum(all_full_scores)
                / len(all_full_scores),
                1
            )
            if all_full_scores else None
        ),

        "best": (
            max(all_full_scores)
            if all_full_scores else None
        ),

        "levels": list(levels.values()),

        "recent": recent,
    }

# =====================================================
# 9. THONG KE LUYEN THI CHO ADMIN
# =====================================================

def get_admin_exam_stats(cursor):

    # Lay danh sach de va so cau tu SQL.
    # Dung chung voi Tien do hoc.
    levels = get_exam_catalog(cursor)

    for item in levels.values():
        item["attempts"] = 0
        item["users"] = 0
        item["full_attempts"] = 0
        item["average"] = None

    # ================================================
    # 10. THONG KE LUOT THI THEO HSK
    # ================================================

    cursor.execute("""
        SELECT
            d.MaCapDo,

            COUNT(*) AS TongLuot,

            COUNT(
                DISTINCT l.MaNguoiDung
            ) AS TongNguoi,

            SUM(
                CASE
                    WHEN l.KyNang = 'toan_bo'
                    THEN 1
                    ELSE 0
                END
            ) AS LuotCaDe,

            AVG(
                CASE
                    WHEN l.KyNang = 'toan_bo'
                    THEN
                        CAST(l.Diem AS FLOAT)
                        * 100.0
                        / NULLIF(
                            l.DiemToiDaLucLam, 0
                        )
                    ELSE NULL
                END
            ) AS DiemTBCaDe

        FROM dbo.LanThiHSK AS l

        INNER JOIN dbo.DeThiHSK AS d
            ON d.MaDeThi = l.MaDeThi

        WHERE l.TrangThai = 'da_cham'
          AND l.NgayNop IS NOT NULL
          AND l.Diem IS NOT NULL
          AND l.DiemToiDaLucLam > 0
          AND d.MaCapDo BETWEEN 1 AND 4

        GROUP BY d.MaCapDo
    """)

    for row in cursor.fetchall():

        level = int(row[0])
        item = levels[level]

        item["attempts"] = int(row[1] or 0)
        item["users"] = int(row[2] or 0)
        item["full_attempts"] = int(row[3] or 0)

        item["average"] = (
            round(float(row[4]), 1)
            if row[4] is not None
            else None
        )

    # ================================================
    # 11. THONG KE TONG TOAN HE THONG
    # ================================================

    cursor.execute("""
        SELECT
            COUNT(*) AS TongLuot,

            COUNT(
                DISTINCT l.MaNguoiDung
            ) AS TongNguoi,

            SUM(
                CASE
                    WHEN l.KyNang = 'toan_bo'
                    THEN 1
                    ELSE 0
                END
            ) AS LuotCaDe,

            AVG(
                CASE
                    WHEN l.KyNang = 'toan_bo'
                    THEN
                        CAST(l.Diem AS FLOAT)
                        * 100.0
                        / NULLIF(
                            l.DiemToiDaLucLam, 0
                        )
                    ELSE NULL
                END
            ) AS DiemTBCaDe

        FROM dbo.LanThiHSK AS l

        INNER JOIN dbo.DeThiHSK AS d
            ON d.MaDeThi = l.MaDeThi

        WHERE l.TrangThai = 'da_cham'
          AND l.NgayNop IS NOT NULL
          AND l.Diem IS NOT NULL
          AND l.DiemToiDaLucLam > 0
          AND d.MaCapDo BETWEEN 1 AND 4
    """)

    row = cursor.fetchone()

    total_attempts = int(row[0] or 0)
    total_users = int(row[1] or 0)
    full_attempts = int(row[2] or 0)

    average = (
        round(float(row[3]), 1)
        if row[3] is not None
        else None
    )

    # ================================================
    # 12. TONG HOP
    # ================================================

    return {
        "total": sum(
            item["total"]
            for item in levels.values()
        ),

        "published": sum(
            item["published"]
            for item in levels.values()
        ),

        "questions": sum(
            item["questions"]
            for item in levels.values()
        ),

        "approved": sum(
            item["approved"]
            for item in levels.values()
        ),

        "attempts": total_attempts,

        "users": total_users,

        "full_attempts": full_attempts,

        "average": average,

        "levels": list(levels.values()),
    }
