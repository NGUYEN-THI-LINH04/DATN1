
"""
BUOC 24 - KIEM TRA TRUOC KHI IMPORT BAI TAP HSK2 BAI 1
CHI DOC SQL, KHONG THAY DOI DU LIEU.
"""

import json
import sys
from pathlib import Path
from contextlib import closing
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

FILE_JSON = (
    ROOT / "scripts" / "hsk2" / "data" /
    "processed" / "exercise_hsk2_lesson1_preview.json"
)

REQUIRED_COLUMNS = {
    "BaiTap": {
        "MaBaiTap", "MaBaiHoc", "TieuDe", "HuongDan",
        "ThoiGianGioiHanGiay", "PhanTramDat",
        "TrangThai", "MaQuanTriVienCapNhat"
    },
    "CauHoi": {
        "MaCauHoi", "MaBaiTap", "LoaiCauHoi",
        "KyNang", "NoiDungCauHoi", "DapAnJson",
        "GiaiThich", "DiemToiDa", "ThuTu",
        "MaQuanTriVienCapNhat"
    },
    "LuaChonCauHoi": {
        "MaLuaChon", "MaCauHoi", "NoiDungLuaChon",
        "LaDapAnDung", "ThuTu"
    }
}


def main():
    print("=" * 65)
    print("BUOC 24 - KIEM TRA IMPORT BAI TAP HSK2 BAI 1")
    print("CHI DOC SQL - KHONG INSERT / UPDATE / DELETE")
    print("=" * 65)

    if not FILE_JSON.exists():
        raise FileNotFoundError(FILE_JSON)

    with open(FILE_JSON, encoding="utf-8") as f:
        data = json.load(f)

    questions = data["CauHoi"]
    lesson_id = data["MaBaiHoc"]

    if data["MaKhoaHoc"] != 2 or lesson_id != 25:
        raise ValueError("Sai khoa hoc hoac MaBaiHoc")

    if data["TrangThai"] != "ban_nhap":
        raise ValueError("Bai tap phai o trang thai ban_nhap")

    if len(questions) != 20 or data["SoCauHoi"] != 20:
        raise ValueError("So cau hoi khong khop")

    orders = [q["ThuTu"] for q in questions]

    if sorted(orders) != list(range(1, 21)):
        raise ValueError("ThuTu cau hoi khong hop le")

    for q in questions:
        if not q["NoiDungCauHoi"].strip():
            raise ValueError("Co cau hoi rong")

        if not q["GiaiThich"].strip():
            raise ValueError("Co cau hoi thieu giai thich")

        if q["LoaiCauHoi"] == "chon_mot":
            opts = q["LuaChon"]

            if len(opts) != 4:
                raise ValueError("Cau trac nghiem thieu lua chon")

            if sum(bool(x["LaDapAnDung"]) for x in opts) != 1:
                raise ValueError("Sai so dap an dung")

            if len({x["NoiDungLuaChon"] for x in opts}) != 4:
                raise ValueError("Lua chon bi trung")

        elif q["LoaiCauHoi"] == "dien_tu":
            answers = q["DapAnJson"]["answers"]

            if not answers or q["LuaChon"]:
                raise ValueError("Cau dien tu khong hop le")
        else:
            raise ValueError("Loai cau hoi chua duoc ho tro")

    print("\n1. KIEM TRA JSON: OK")
    print("Tong cau hoi:", len(questions))
    print("Loai cau hoi:", dict(Counter(
        q["LoaiCauHoi"] for q in questions
    )))

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cursor:

            cursor.execute("""
                SELECT MaBaiHoc, TieuDe
                FROM dbo.BaiHoc
                WHERE MaBaiHoc = ?
                  AND MaKhoaHoc = ?
            """, lesson_id, 2)

            lesson = cursor.fetchone()

            if not lesson:
                raise ValueError("Khong tim thay bai hoc HSK2")

            print("\n2. KIEM TRA BAI HOC: OK")
            print("MaBaiHoc:", lesson[0])
            print("Ten bai:", lesson[1])

            cursor.execute("""
                SELECT MaBaiTap, TieuDe, TrangThai
                FROM dbo.BaiTap
                WHERE MaBaiHoc = ?
            """, lesson_id)

            existing = cursor.fetchall()

            print("\n3. BAI TAP HIEN CO:", len(existing))

            for item in existing:
                print(tuple(item))

            if existing:
                raise ValueError(
                    "Bai 1 da co bai tap. DUNG import de tranh trung."
                )

            print("Khong co bai tap trung.")

            print("\n4. KIEM TRA CAU TRUC BANG:")

            for table, required in REQUIRED_COLUMNS.items():
                cursor.execute("""
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = 'dbo'
                      AND TABLE_NAME = ?
                """, table)

                actual = {row[0] for row in cursor.fetchall()}
                missing = required - actual

                if missing:
                    raise ValueError(
                        f"Bang {table} thieu cot: {sorted(missing)}"
                    )

                print(f"{table}: OK")

        conn.rollback()

    print("\n" + "=" * 65)
    print("KIEM TRA THANH CONG")
    print("CHUA GHI BAT KY DU LIEU NAO VAO SQL")
    print("=" * 65)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nLOI:", exc)
        raise SystemExit(1)
