
"""
BUOC 25 - IMPORT BAI TAP HSK2 BAI 1

Mac dinh: DRY RUN + ROLLBACK
Chi COMMIT khi truyen --commit.

Khong sua/xoa du lieu HSK1, HSK2 da co.
"""

import argparse
import json
import sys
from collections import Counter
from contextlib import closing
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

JSON_FILE = (
    ROOT / "scripts" / "hsk2" / "data"
    / "processed" / "exercise_hsk2_lesson1_preview.json"
)

EXPECTED_LESSON_ID = 25
EXPECTED_QUESTIONS = 20


def load_data():
    if not JSON_FILE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file: {JSON_FILE}"
        )

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if (
        data.get("MaKhoaHoc") != 2
        or data.get("MaBaiHoc") != EXPECTED_LESSON_ID
    ):
        raise ValueError("Sai khoa hoc hoac bai hoc")

    questions = data.get("CauHoi", [])

    if (
        len(questions) != EXPECTED_QUESTIONS
        or data.get("SoCauHoi") != EXPECTED_QUESTIONS
    ):
        raise ValueError("So luong cau hoi khong hop le")

    if data.get("TrangThai") != "ban_nhap":
        raise ValueError("Trang thai phai la ban_nhap")

    orders = [q.get("ThuTu") for q in questions]

    if sorted(orders) != list(
        range(1, EXPECTED_QUESTIONS + 1)
    ):
        raise ValueError("Thu tu cau hoi khong hop le")

    for q in questions:
        if not q.get("NoiDungCauHoi", "").strip():
            raise ValueError("Co cau hoi thieu noi dung")

        if not q.get("GiaiThich", "").strip():
            raise ValueError("Co cau hoi thieu giai thich")

        if Decimal(str(q.get("DiemToiDa", 0))) <= 0:
            raise ValueError("DiemToiDa khong hop le")

        kind = q.get("LoaiCauHoi")
        options = q.get("LuaChon", [])

        if kind == "chon_mot":
            if len(options) != 4:
                raise ValueError(
                    "Cau chon_mot phai co 4 lua chon"
                )

            if sum(
                bool(opt["LaDapAnDung"])
                for opt in options
            ) != 1:
                raise ValueError(
                    "Cau chon_mot phai co 1 dap an dung"
                )

            texts = [
                opt["NoiDungLuaChon"].strip()
                for opt in options
            ]

            if any(not text for text in texts):
                raise ValueError("Co lua chon rong")

            if len(set(texts)) != 4:
                raise ValueError("Lua chon trung lap")

            if sorted(
                opt["ThuTu"] for opt in options
            ) != [1, 2, 3, 4]:
                raise ValueError("Thu tu lua chon sai")

        elif kind == "dien_tu":
            answer = q.get("DapAnJson")

            if (
                not isinstance(answer, dict)
                or not isinstance(
                    answer.get("answers"), list
                )
                or not answer["answers"]
                or options
            ):
                raise ValueError(
                    "Dap an dien_tu khong hop le"
                )

        else:
            raise ValueError(
                f"Loai cau hoi chua ho tro: {kind}"
            )

    return data


def choose_admin(cursor, requested_id):
    cursor.execute("""
        SELECT MaQuanTriVien, TenDangNhap
        FROM dbo.QuanTriVien
        WHERE DangHoatDong = 1
        ORDER BY MaQuanTriVien
    """)

    admins = cursor.fetchall()

    if not admins:
        raise ValueError(
            "Khong co QuanTriVien dang hoat dong"
        )

    if requested_id is not None:
        for admin in admins:
            if int(admin[0]) == requested_id:
                return requested_id

        raise ValueError(
            f"Admin ID {requested_id} khong hop le"
        )

    if len(admins) == 1:
        return int(admins[0][0])

    print("\nCO NHIEU ADMIN DANG HOAT DONG:")
    for admin in admins:
        print(
            f"ID={admin[0]} | TenDangNhap={admin[1]}"
        )

    raise ValueError(
        "Hay chay lai voi --admin-id MA_ADMIN"
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Ghi du lieu vao SQL"
    )

    parser.add_argument(
        "--admin-id",
        type=int,
        default=None,
        help="MaQuanTriVien thuc hien import"
    )

    args = parser.parse_args()

    data = load_data()
    questions = data["CauHoi"]

    print("=" * 68)
    print("BUOC 25 - IMPORT BAI TAP HSK2 BAI 1")
    print("=" * 68)

    print(
        "CHE DO:",
        "COMMIT" if args.commit else "DRY RUN"
    )

    print("MaBaiHoc:", data["MaBaiHoc"])
    print("Tong cau hoi:", len(questions))

    with closing(get_connection()) as conn:
        # Tat autocommit de dam bao transaction
        conn.autocommit = False

        try:
            with closing(conn.cursor()) as cur:

                # Kiem tra database
                cur.execute("SELECT DB_NAME()")
                db_name = cur.fetchone()[0]

                if db_name.lower() != "hoctiengtrungdb":
                    raise ValueError(
                        f"Ket noi nham database: {db_name}"
                    )

                # Chon tai khoan admin
                admin_id = choose_admin(
                    cur, args.admin_id
                )

                print("MaQuanTriVien:", admin_id)

                # Kiem tra bai hoc
                cur.execute("""
                    SELECT MaBaiHoc
                    FROM dbo.BaiHoc
                    WHERE MaBaiHoc = ?
                      AND MaKhoaHoc = 2
                      AND SoThuTuBai = 1
                """, EXPECTED_LESSON_ID)

                if cur.fetchone() is None:
                    raise ValueError(
                        "Khong tim thay HSK2 bai 1"
                    )

                # Kiem tra trung lap ngay truoc INSERT
                cur.execute("""
                    SELECT COUNT(*)
                    FROM dbo.BaiTap WITH (
                        UPDLOCK, HOLDLOCK
                    )
                    WHERE MaBaiHoc = ?
                """, EXPECTED_LESSON_ID)

                existing = int(cur.fetchone()[0])

                if existing != 0:
                    raise ValueError(
                        "Bai hoc da co bai tap. "
                        "Dung import de tranh trung lap."
                    )

                # 1. Tao bai tap
                cur.execute("""
                    INSERT INTO dbo.BaiTap
                    (
                        MaBaiHoc,
                        TieuDe,
                        HuongDan,
                        ThoiGianGioiHanGiay,
                        PhanTramDat,
                        TrangThai,
                        MaQuanTriVienCapNhat,
                        NgayCapNhat
                    )
                    OUTPUT INSERTED.MaBaiTap
                    VALUES
                    (?, ?, ?, ?, ?, ?, ?, SYSDATETIME())
                """,
                    EXPECTED_LESSON_ID,
                    data["TieuDe"],
                    data["HuongDan"],
                    data["ThoiGianGioiHanGiay"],
                    Decimal(str(data["PhanTramDat"])),
                    "ban_nhap",
                    admin_id
                )

                exercise_id = int(cur.fetchone()[0])

                inserted_questions = 0
                inserted_options = 0

                # 2. Tao tung cau hoi
                for q in questions:

                    answer_json = q.get("DapAnJson")

                    if answer_json is not None:
                        answer_json = json.dumps(
                            answer_json,
                            ensure_ascii=False
                        )

                    cur.execute("""
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
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                         SYSDATETIME())
                    """,
                        exercise_id,
                        q["LoaiCauHoi"],
                        q["KyNang"],
                        q["NoiDungCauHoi"],
                        None,
                        None,
                        answer_json,
                        q["GiaiThich"],
                        Decimal(str(q["DiemToiDa"])),
                        q["ThuTu"],
                        admin_id
                    )

                    question_id = int(
                        cur.fetchone()[0]
                    )

                    inserted_questions += 1

                    # 3. Tao lua chon
                    for opt in q["LuaChon"]:
                        cur.execute("""
                            INSERT INTO dbo.LuaChonCauHoi
                            (
                                MaCauHoi,
                                NoiDungLuaChon,
                                LaDapAnDung,
                                ThuTu
                            )
                            VALUES (?, ?, ?, ?)
                        """,
                            question_id,
                            opt["NoiDungLuaChon"],
                            1 if opt["LaDapAnDung"] else 0,
                            opt["ThuTu"]
                        )

                        inserted_options += 1

                # 4. Xac minh trong transaction
                cur.execute("""
                    SELECT COUNT(*)
                    FROM dbo.CauHoi
                    WHERE MaBaiTap = ?
                """, exercise_id)

                count_questions = int(
                    cur.fetchone()[0]
                )

                cur.execute("""
                    SELECT COUNT(*)
                    FROM dbo.LuaChonCauHoi lc
                    INNER JOIN dbo.CauHoi ch
                        ON lc.MaCauHoi = ch.MaCauHoi
                    WHERE ch.MaBaiTap = ?
                """, exercise_id)

                count_options = int(
                    cur.fetchone()[0]
                )

                if (
                    count_questions != 20
                    or inserted_questions != 20
                    or count_options != 72
                    or inserted_options != 72
                ):
                    raise ValueError(
                        "So luong ban ghi khong khop. "
                        "Huy transaction."
                    )

                print("\nKET QUA KIEM TRA:")
                print("MaBaiTap tam:", exercise_id)
                print("Bai tap:", 1)
                print("Cau hoi:", count_questions)
                print("Lua chon:", count_options)
                print("Trang thai: ban_nhap")

                if args.commit:
                    conn.commit()
                    print("\nCOMMIT THANH CONG")
                    print("Da luu du lieu vao SQL")
                else:
                    conn.rollback()
                    print("\nDRY RUN THANH CONG")
                    print("ROLLBACK - KHONG LUU SQL")

        except Exception:
            conn.rollback()
            raise


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nLOI:", exc)
        print("Khong commit du lieu.")
        raise SystemExit(1)
