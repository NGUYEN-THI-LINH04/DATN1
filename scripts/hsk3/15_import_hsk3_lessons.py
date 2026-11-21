
# -*- coding: utf-8 -*-
"""
BUOC 50 - TAO 20 BAI HOC HSK3 TRONG SQL

Nguon:
scripts/hsk3/data/processed/lessons_hsk3_draft.csv

PREVIEW:
python scripts/hsk3/15_import_hsk3_lessons.py

COMMIT:
python scripts/hsk3/15_import_hsk3_lessons.py --commit

An toan:
- Chi thao tac voi MaKhoaHoc = 3.
- Khong sua/xoa HSK1, HSK2.
- Khong ghi de bai hoc da ton tai.
- Bai hoc moi luon la ban_nhap.
- Chua gan TuVungBaiHoc.
"""

import argparse
import csv
import hashlib
import json
import re
import sys

from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

SOURCE = DATA / "lessons_hsk3_draft.csv"

PREVIEW = DATA / "hsk3_lessons_import_preview.json"

RESULT = DATA / "lessons_hsk3_sql_result.csv"

COURSE_ID = 3
ADMIN_ID = 1
EXPECTED_LESSONS = 20


def clean(value):
    return re.sub(
        r"\s+", " ", str(value or "")
    ).strip()


def load_lessons():
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay CSV: {SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        required = {
            "SoThuTuBai",
            "TieuDeTiengTrung",
            "TieuDeTiengViet",
            "ChuDe",
        }

        missing = required - set(
            reader.fieldnames or []
        )

        if missing:
            raise ValueError(
                f"CSV thieu cot: {sorted(missing)}"
            )

        rows = list(reader)

    if len(rows) != EXPECTED_LESSONS:
        raise ValueError(
            f"Can {EXPECTED_LESSONS} bai, "
            f"thuc te {len(rows)}"
        )

    lessons = []
    orders = set()

    for row in rows:
        order = int(row["SoThuTuBai"])

        if order in orders:
            raise ValueError(
                f"Trung SoThuTuBai: {order}"
            )

        orders.add(order)

        title_zh = clean(
            row["TieuDeTiengTrung"]
        )

        title_vi = clean(
            row["TieuDeTiengViet"]
        )

        topic = clean(
            row["ChuDe"]
        )

        if not title_zh or not title_vi or not topic:
            raise ValueError(
                f"Bai {order}: thieu thong tin"
            )

        # Giong cach HSK2:
        # TieuDe gom tieng Trung + tieng Viet.
        title = f"{title_zh} - {title_vi}"

        summary = (
            f"Học và luyện tập tiếng Trung HSK3 "
            f"theo chủ đề {topic.lower()}; "
            f"bao gồm từ vựng, ngữ pháp và chữ Hán."
        )

        if len(title) > 200:
            raise ValueError(
                f"Bai {order}: TieuDe qua dai"
            )

        if len(summary) > 1000:
            raise ValueError(
                f"Bai {order}: TomTat qua dai"
            )

        lessons.append({
            "SoThuTuBai": order,
            "TieuDe": title,
            "TomTat": summary,
            "TrangThai": "ban_nhap",
        })

    if orders != set(range(1, 21)):
        raise ValueError(
            "Thu tu bai phai lien tuc tu 1 den 20"
        )

    lessons.sort(
        key=lambda x: x["SoThuTuBai"]
    )

    return lessons


def get_source_hash():
    return hashlib.sha256(
        SOURCE.read_bytes()
    ).hexdigest()


def check_database(cursor):
    # Kiem tra khoa hoc HSK3.
    cursor.execute("""
        SELECT MaKhoaHoc, MaCapDo, TieuDe
        FROM dbo.KhoaHoc
        WHERE MaKhoaHoc = ?;
    """, COURSE_ID)

    course = cursor.fetchone()

    if course is None:
        raise RuntimeError(
            "Khong tim thay khoa hoc HSK3."
        )

    if int(course[1]) != 3:
        raise RuntimeError(
            "MaKhoaHoc=3 khong thuoc HSK3."
        )

    # Kiem tra Admin 1.
    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.QuanTriVien
        WHERE MaQuanTriVien = ?;
    """, ADMIN_ID)

    if int(cursor.fetchone()[0]) != 1:
        raise RuntimeError(
            "Khong tim thay Admin ID=1."
        )

    # Khong cho import neu HSK3 da co bai hoc.
    # Tranh INSERT lap khi chay lai.
    cursor.execute("""
        SELECT
            MaBaiHoc,
            SoThuTuBai,
            TieuDe
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = ?
        ORDER BY SoThuTuBai;
    """, COURSE_ID)

    existing = cursor.fetchall()

    if existing:
        print("\nHSK3 DA CO BAI HOC:")

        for item in existing:
            print(
                f"  MaBaiHoc={item[0]} | "
                f"Bai {item[1]} | {item[2]}"
            )

        raise RuntimeError(
            "HSK3 da co bai hoc. "
            "Dung lai de tranh tao trung."
        )

    print(
        f"Da xac nhan khoa hoc: "
        f"{course[0]} - {course[2]}"
    )
    print("HSK3 chua co bai hoc.")
    print("Admin ID=1 hop le.")


def get_preview_signature(lessons):
    payload = {
        "source_sha256": get_source_hash(),
        "course_id": COURSE_ID,
        "admin_id": ADMIN_ID,
        "lessons": lessons,
    }

    digest = hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    return digest


def insert_lesson(cursor, item):
    # Dung cach INSERT cua routes/admin/lessons.py.
    cursor.execute("""
        INSERT INTO dbo.BaiHoc
        (
            MaKhoaHoc,
            SoThuTuBai,
            TieuDe,
            TomTat,
            TrangThai,
            MaQuanTriVienCapNhat,
            NgayCapNhat
        )
        OUTPUT INSERTED.MaBaiHoc
        VALUES
        (
            ?, ?, ?, ?,
            'ban_nhap',
            ?,
            SYSUTCDATETIME()
        );
    """,
        COURSE_ID,
        item["SoThuTuBai"],
        item["TieuDe"],
        item["TomTat"],
        ADMIN_ID,
    )

    result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            "Khong lay duoc MaBaiHoc."
        )

    return int(result[0])


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Cho phep INSERT vao SQL"
    )

    args = parser.parse_args()

    print("=" * 68)
    print("BUOC 50 - TAO 20 BAI HOC HSK3")
    print("=" * 68)

    print(
        "CHE DO:",
        "COMMIT" if args.commit else "PREVIEW"
    )

    lessons = load_lessons()

    print("\n[1] DANH SACH BAI HOC")

    for lesson in lessons:
        print(
            f"Bai {lesson['SoThuTuBai']:02d}: "
            f"{lesson['TieuDe']}"
        )

    signature = get_preview_signature(lessons)

    with closing(get_connection()) as connection:
        if getattr(connection, "autocommit", False):
            raise RuntimeError(
                "Ket noi autocommit=True. "
                "Dung lai de dam bao an toan."
            )

        with closing(connection.cursor()) as cursor:
            try:
                print("\n[2] KIEM TRA SQL")

                check_database(cursor)

                if not args.commit:
                    info = {
                        "source_sha256": get_source_hash(),
                        "signature": signature,
                        "course_id": COURSE_ID,
                        "lesson_count": len(lessons),
                        "status": "ban_nhap",
                    }

                    PREVIEW.write_text(
                        json.dumps(
                            info,
                            ensure_ascii=False,
                            indent=2,
                        ),
                        encoding="utf-8",
                    )

                    connection.rollback()

                    print("\nPREVIEW THANH CONG")
                    print("So bai du kien:", len(lessons))
                    print("Trang thai: ban_nhap")
                    print("Da luu:", PREVIEW)
                    print("CHUA GHI SQL")
                    return

                print("\n[3] XAC NHAN PREVIEW")

                if not PREVIEW.is_file():
                    raise RuntimeError(
                        "Chua co PREVIEW. "
                        "Hay chay khong co --commit."
                    )

                preview_data = json.loads(
                    PREVIEW.read_text(
                        encoding="utf-8"
                    )
                )

                if (
                    preview_data.get("signature")
                    != signature
                ):
                    raise RuntimeError(
                        "CSV khac PREVIEW. "
                        "Can PREVIEW lai."
                    )

                if RESULT.exists():
                    raise RuntimeError(
                        "Da ton tai file ket qua. "
                        "Dung lai de tranh import lap."
                    )

                temp_file = RESULT.with_suffix(
                    ".pending.csv"
                )

                if temp_file.exists():
                    raise RuntimeError(
                        "Da ton tai file tam. "
                        "Can kiem tra truoc khi chay lai."
                    )

                print("\n[4] INSERT BAI HOC")

                inserted = []

                for lesson in lessons:
                    lesson_id = insert_lesson(
                        cursor, lesson
                    )

                    inserted.append({
                        "MaBaiHoc": lesson_id,
                        "MaKhoaHoc": COURSE_ID,
                        **lesson,
                    })

                    print(
                        f"  OK Bai "
                        f"{lesson['SoThuTuBai']:02d}"
                        f" -> MaBaiHoc={lesson_id}"
                    )

                # Xac minh tren cung transaction.
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.BaiHoc
                    WHERE MaKhoaHoc = ?;
                """, COURSE_ID)

                total = int(cursor.fetchone()[0])

                if total != EXPECTED_LESSONS:
                    raise RuntimeError(
                        f"SQL co {total} bai, "
                        "khong dung 20."
                    )

                fields = [
                    "MaBaiHoc",
                    "MaKhoaHoc",
                    "SoThuTuBai",
                    "TieuDe",
                    "TomTat",
                    "TrangThai",
                ]

                with temp_file.open(
                    "x",
                    encoding="utf-8-sig",
                    newline="",
                ) as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=fields,
                        extrasaction="ignore",
                    )
                    writer.writeheader()
                    writer.writerows(inserted)

                # SQL COMMIT truoc khi doi ten file.
                try:
                    connection.commit()
                except Exception:
                    temp_file.unlink(
                        missing_ok=True
                    )
                    raise

                try:
                    temp_file.rename(RESULT)
                    mapping_message = str(RESULT)
                except OSError:
                    mapping_message = (
                        "SQL da COMMIT, nhung file mapping "
                        f"van o: {temp_file}"
                    )

                print("\n" + "=" * 68)
                print("COMMIT THANH CONG!")
                print("=" * 68)
                print("Khoa hoc HSK3:", COURSE_ID)
                print("Da tao:", len(inserted), "bai hoc")
                print("Trang thai: ban_nhap")
                print("Mapping:", mapping_message)
                print("CHUA LIEN KET TU VUNG")

            except Exception:
                connection.rollback()
                raise


if __name__ == "__main__":
    main()
