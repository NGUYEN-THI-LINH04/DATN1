
"""
BUOC 22 - LAY HOC LIEU HSK2 BAI 1
Chi doc SQL Server, KHONG sua du lieu.
"""

from contextlib import closing
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

OUT = (
    ROOT / "scripts" / "hsk2" / "data" / "processed"
    / "exercise_hsk2_lesson1_source.json"
)


def rows(cursor, statement, *params):
    cursor.execute(statement, *params)
    names = [col[0] for col in cursor.description]

    return [
        dict(zip(names, item))
        for item in cursor.fetchall()
    ]


def encode(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return str(value)

    raise TypeError(
        f"Khong the xuat JSON: {type(value).__name__}"
    )


def main():
    print("=" * 68)
    print("BUOC 22 - LAY HOC LIEU HSK2 BAI 1")
    print("CHI DOC SQL - KHONG SUA DU LIEU")
    print("=" * 68)

    with closing(get_connection()) as con:
        with closing(con.cursor()) as cur:

            # 1. Lay thong tin bai hoc
            lesson = rows(
                cur,
                """
                SELECT
                    MaBaiHoc,
                    MaKhoaHoc,
                    SoThuTuBai,
                    TieuDe,
                    TomTat,
                    TrangThai
                FROM dbo.BaiHoc
                WHERE MaKhoaHoc = ?
                  AND SoThuTuBai = ?
                """,
                2, 1
            )

            if len(lesson) != 1:
                raise RuntimeError(
                    "Khong tim thay dung 1 bai HSK2 so 1. "
                    f"So bai tim thay: {len(lesson)}"
                )

            lesson_id = lesson[0]["MaBaiHoc"]

            # 2. Lay tu vung cua bai 1
            vocabulary = rows(
                cur,
                """
                SELECT
                    tvbh.ThuTu,
                    tv.MaTuVung,
                    tv.ChuHan,
                    tv.PhienAm,
                    tv.NghiaTiengViet,
                    tv.TuLoai,
                    tv.ViDuTiengTrung,
                    tv.ViDuTiengViet
                FROM dbo.TuVungBaiHoc tvbh
                INNER JOIN dbo.TuVung tv
                    ON tv.MaTuVung = tvbh.MaTuVung
                WHERE tvbh.MaBaiHoc = ?
                ORDER BY tvbh.ThuTu, tv.MaTuVung
                """,
                lesson_id
            )

            # 3. Lay ngu phap cua bai 1
            grammar = rows(
                cur,
                """
                SELECT
                    MaNguPhap,
                    ThuTu,
                    TenCauTruc,
                    MoTa,
                    CachDung,
                    ViDuTiengTrung,
                    ViDuPinyin,
                    ViDuTiengViet,
                    TrangThai
                FROM dbo.NguPhap
                WHERE MaBaiHoc = ?
                ORDER BY ThuTu, MaNguPhap
                """,
                lesson_id
            )

            # 4. Lay chu Han cua bai 1
            hanzi = rows(
                cur,
                """
                SELECT
                    MaChuHan,
                    ThuTu,
                    KyTu,
                    Pinyin,
                    NghiaTiengViet,
                    SoNet,
                    CachGhiNho,
                    ViDuTiengTrung,
                    ViDuPinyin,
                    ViDuTiengViet,
                    TrangThai
                FROM dbo.ChuHan
                WHERE MaBaiHoc = ?
                ORDER BY ThuTu, MaChuHan
                """,
                lesson_id
            )

            # 5. Kiem tra bai tap da ton tai
            exercises = rows(
                cur,
                """
                SELECT
                    MaBaiTap,
                    MaBaiHoc,
                    TieuDe,
                    HuongDan,
                    ThoiGianGioiHanGiay,
                    PhanTramDat,
                    TrangThai
                FROM dbo.BaiTap
                WHERE MaBaiHoc = ?
                ORDER BY MaBaiTap
                """,
                lesson_id
            )

            # Khong ghi du lieu vao database
            con.rollback()

    # 6. Chuan bi du lieu JSON
    output = {
        "note": "Chi doc du lieu, khong sua SQL.",
        "lesson": lesson[0],
        "vocabulary": vocabulary,
        "grammar": grammar,
        "hanzi": hanzi,
        "existing_exercises": exercises
    }

    # 7. Xuat JSON
    OUT.parent.mkdir(parents=True, exist_ok=True)

    OUT.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
            default=encode
        ),
        encoding="utf-8"
    )

    # 8. In ket qua
    print("\nKET QUA KIEM TRA:")
    print("-" * 68)

    print(
        "Bai hoc:",
        lesson[0]["TieuDe"]
    )

    print("MaBaiHoc:", lesson_id)
    print("Tu vung:", len(vocabulary))
    print("Ngu phap:", len(grammar))
    print("Chu Han:", len(hanzi))
    print("Bai tap hien co:", len(exercises))

    print("\nFILE DU LIEU:")
    print(OUT)

    print("\nHOAN TAT - KHONG INSERT / UPDATE / DELETE")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"LOI: {exc}")
        raise SystemExit(1)
