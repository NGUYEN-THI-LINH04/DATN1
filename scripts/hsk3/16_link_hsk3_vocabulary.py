
# -*- coding: utf-8 -*-
"""
BUOC 51 - LIEN KET TU VUNG VA BAI HOC HSK3

Nguon:
- vocabulary_hsk3_assignment_corrected.csv
- lessons_hsk3_sql_result.csv

Bang SQL:
- BaiHoc
- TuVung
- TuVungBaiHoc

Mac dinh PREVIEW, khong ghi SQL.
--commit moi INSERT lien ket.

KHONG UPDATE / DELETE du lieu cu.
KHONG TU DONG XUAT BAN HSK3.

CANH BAO:
Phan bo chu de chua duoc kiem duyet noi dung.
"""

import argparse
import csv
import hashlib
import json
import sys

from collections import Counter, defaultdict
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"

VOCAB = DATA / "vocabulary_hsk3_assignment_corrected.csv"
LESSONS = DATA / "lessons_hsk3_sql_result.csv"

PREVIEW = DATA / "hsk3_vocabulary_links_preview.json"
RESULT = DATA / "hsk3_vocabulary_links_result.csv"

COURSE_ID = 3
EXPECTED_WORDS = 973
EXPECTED_LESSONS = 20


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_hash(rows):
    content = json.dumps(
        rows, ensure_ascii=False, sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def make_plan():
    vocab_rows = read_csv(VOCAB)
    lesson_rows = read_csv(LESSONS)

    if len(vocab_rows) != EXPECTED_WORDS:
        raise ValueError(
            f"Can 973 muc tu, hien co {len(vocab_rows)}."
        )

    if len(lesson_rows) != EXPECTED_LESSONS:
        raise ValueError(
            "Danh sach bai hoc khong du 20 bai."
        )

    lesson_ids = {}

    for lesson in lesson_rows:
        number = int(lesson["SoThuTuBai"])
        lesson_id = int(lesson["MaBaiHoc"])
        course_id = int(lesson["MaKhoaHoc"])

        if course_id != COURSE_ID:
            raise ValueError(
                f"Bai {number} khong thuoc HSK3."
            )

        if number in lesson_ids:
            raise ValueError(
                f"Trung so thu tu bai {number}."
            )

        lesson_ids[number] = lesson_id

    if set(lesson_ids) != set(range(1, 21)):
        raise ValueError(
            "Danh sach bai HSK3 khong du tu 1 den 20."
        )

    seen_source = set()
    seen_link = set()
    lesson_order = defaultdict(int)
    plan = []

    for row in vocab_rows:
        source_id = str(row.get("MaMucNoiBo", "")).strip()
        word_id = int(row["MaTuVung"])
        lesson_number = int(row["SoThuTuBaiDuKien"])

        if not source_id or source_id in seen_source:
            raise ValueError(
                f"Ma nguon rong hoac trung: {source_id}"
            )

        seen_source.add(source_id)

        if lesson_number not in lesson_ids:
            raise ValueError(
                f"{source_id}: bai hoc khong hop le."
            )

        lesson_id = lesson_ids[lesson_number]
        link_key = (lesson_id, word_id)

        # Mot tu co the co nhieu muc HSK,
        # nhung trong mot bai chi lien ket 1 lan.
        if link_key in seen_link:
            raise ValueError(
                f"{source_id}: MaTuVung={word_id} "
                f"bi trung trong bai {lesson_number}. "
                "Can xu ly mapping truoc khi INSERT."
            )

        seen_link.add(link_key)
        lesson_order[lesson_number] += 1

        plan.append({
            "MaMucNoiBo": source_id,
            "MaBaiHoc": lesson_id,
            "SoThuTuBai": lesson_number,
            "MaTuVung": word_id,
            "ThuTu": lesson_order[lesson_number],
            "ChuHan": row.get("ChuHan", ""),
            "PhienAm": row.get("PhienAm", ""),
        })

    if len(plan) != EXPECTED_WORDS:
        raise RuntimeError(
            "Ke hoach lien ket khong du 973 muc."
        )

    return plan, dict(lesson_order)


def verify_database(cursor, plan):
    # Xac nhan chinh xac cac bai HSK3.
    cursor.execute("""
        SELECT MaBaiHoc, SoThuTuBai, TrangThai
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = ?;
    """, COURSE_ID)

    actual_lessons = {
        int(r[0]): (int(r[1]), str(r[2]))
        for r in cursor.fetchall()
    }

    if len(actual_lessons) != EXPECTED_LESSONS:
        raise RuntimeError(
            "So bai HSK3 trong SQL khong phai 20."
        )

    for row in plan:
        lesson_id = row["MaBaiHoc"]
        number = row["SoThuTuBai"]

        if actual_lessons.get(lesson_id) != (
            number, "ban_nhap"
        ):
            raise RuntimeError(
                f"Bai {number} da thay doi "
                "hoac khong con o trang thai ban_nhap."
            )

    # Xac nhan tu vung ton tai.
    word_ids = sorted({
        r["MaTuVung"] for r in plan
    })

    existing_ids = set()

    # Chia nho danh sach de tranh gioi han tham so SQL.
    for start in range(0, len(word_ids), 500):
        batch = word_ids[start:start + 500]
        placeholders = ",".join("?" for _ in batch)

        cursor.execute(
            f"""
            SELECT MaTuVung
            FROM dbo.TuVung
            WHERE MaTuVung IN ({placeholders});
            """,
            *batch,
        )

        existing_ids.update(
            int(r[0]) for r in cursor.fetchall()
        )

    missing = set(word_ids) - existing_ids

    if missing:
        raise RuntimeError(
            "Co MaTuVung khong ton tai trong SQL: "
            + str(sorted(missing)[:15])
        )

    # Khong ghi trung cac lien ket da ton tai.
    cursor.execute("""
        SELECT COUNT(*)
        FROM dbo.TuVungBaiHoc AS tvbh
        INNER JOIN dbo.BaiHoc AS bh
            ON bh.MaBaiHoc = tvbh.MaBaiHoc
        WHERE bh.MaKhoaHoc = ?;
    """, COURSE_ID)

    existing_links = int(cursor.fetchone()[0])

    if existing_links != 0:
        raise RuntimeError(
            f"HSK3 da co {existing_links} lien ket tu vung. "
            "Dung lai de tranh INSERT lap."
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--commit",
        action="store_true",
    )
    args = parser.parse_args()

    print("=" * 68)
    print("BUOC 51 - LIEN KET TU VUNG HSK3")
    print("=" * 68)
    print(
        "CHE DO:",
        "COMMIT" if args.commit else "PREVIEW"
    )

    plan, counts = make_plan()

    signature = {
        "vocabulary_sha256": file_hash(VOCAB),
        "lessons_sha256": file_hash(LESSONS),
        "plan_sha256": plan_hash(plan),
        "total_links": len(plan),
        "course_id": COURSE_ID,
    }

    with closing(get_connection()) as connection:
        if getattr(connection, "autocommit", False):
            raise RuntimeError(
                "Ket noi autocommit=True. Dung lai."
            )

        with closing(connection.cursor()) as cursor:
            try:
                verify_database(cursor, plan)

                print("\nTONG HOP")
                print("Tong muc HSK3:", len(plan))
                print("So bai:", len(counts))
                print("Lien ket da co trong SQL: 0")

                for number in range(1, 21):
                    print(
                        f"Bai {number:02d}: "
                        f"{counts.get(number, 0)} muc"
                    )

                if not args.commit:
                    PREVIEW.write_text(
                        json.dumps(
                            signature,
                            ensure_ascii=False,
                            indent=2,
                        ),
                        encoding="utf-8",
                    )

                    connection.rollback()

                    print("\nPREVIEW THANH CONG")
                    print("Du kien lien ket:", len(plan))
                    print("Chua thay doi SQL")
                    return

                if not PREVIEW.is_file():
                    raise RuntimeError(
                        "Chua co PREVIEW buoc 51."
                    )

                saved = json.loads(
                    PREVIEW.read_text(encoding="utf-8")
                )

                if saved != signature:
                    raise RuntimeError(
                        "Du lieu khac PREVIEW. "
                        "Can chay PREVIEW lai."
                    )

                if RESULT.exists():
                    raise RuntimeError(
                        "Da co file ket qua, khong INSERT lap."
                    )

                temp = RESULT.with_suffix(".pending.csv")

                if temp.exists():
                    raise RuntimeError(
                        "Da ton tai file mapping tam."
                    )

                for item in plan:
                    cursor.execute("""
                        INSERT INTO dbo.TuVungBaiHoc
                        (
                            MaBaiHoc,
                            MaTuVung,
                            ThuTu
                        )
                        VALUES (?, ?, ?);
                    """,
                        item["MaBaiHoc"],
                        item["MaTuVung"],
                        item["ThuTu"],
                    )

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.TuVungBaiHoc AS tvbh
                    INNER JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = tvbh.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                """, COURSE_ID)

                total = int(cursor.fetchone()[0])

                if total != len(plan):
                    raise RuntimeError(
                        f"SQL co {total} lien ket, "
                        f"du kien {len(plan)}."
                    )

                fields = list(plan[0].keys())

                with temp.open(
                    "x",
                    encoding="utf-8-sig",
                    newline="",
                ) as file:
                    writer = csv.DictWriter(
                        file,
                        fieldnames=fields,
                    )
                    writer.writeheader()
                    writer.writerows(plan)

                try:
                    connection.commit()
                except Exception:
                    temp.unlink(missing_ok=True)
                    raise

                try:
                    temp.rename(RESULT)
                except OSError:
                    print(
                        "SQL da COMMIT. "
                        "File ket qua tam:", temp
                    )

                print("\nCOMMIT THANH CONG!")
                print("Da lien ket:", total)
                print("Bai hoc:", len(counts))
                print("Trang thai bai hoc: ban_nhap")
                print("Chua xuat ban HSK3")

            except Exception:
                connection.rollback()
                raise


if __name__ == "__main__":
    main()
