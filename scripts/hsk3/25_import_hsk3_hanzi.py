
# -*- coding: utf-8 -*-
"""
BUOC 61 - KIEM TRA VA IMPORT CHU HAN HSK3

PREVIEW:
python scripts/hsk3/25_import_hsk3_hanzi.py

COMMIT:
python scripts/hsk3/25_import_hsk3_hanzi.py --commit

Nguon:
hanzi_hsk3_300_meanings_draft.csv

An toan:
- PREVIEW mac dinh.
- Chi INSERT, khong UPDATE/DELETE.
- Chi lam viec voi BaiHoc thuoc HSK3.
- Khong tao trung KyTu da co trong ChuHan.
- Tat ca ban ghi moi la ban_nhap.
- Tu kiem tra cau truc cot SQL.
- Transaction va rollback khi co loi.
"""

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"
SOURCE = DATA / "hanzi_hsk3_300_meanings_draft.csv"
PREVIEW_FILE = DATA / "hsk3_hanzi_import_preview.json"
RESULT_FILE = DATA / "hanzi_hsk3_sql_result.csv"

COURSE_ID = 3
EXPECTED = 300

# Chi nhung cot da duoc xac dinh tu du lieu ChuHan.
# Khong co gang ghi vao cot chua biet y nghia.
TEXT_COLUMNS = [
    "KyTu",
    "Pinyin",
    "NghiaTiengViet",
    "CachGhiNho",
    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",
]

OPTIONAL_NULL_COLUMNS = [
    "MaTep",
    "MaNguon",
    "MaQuanTriVienCapNhat",
]


def clean(value):
    return str(value or "").strip()


def read_data():
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)

    with SOURCE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)

    required = {
        "KyTu", "Pinyin", "NghiaTiengViet",
        "MaBaiHoc", "SoNet",
        "SoThuTuBai",
    }

    missing = required - set(fields)
    if missing:
        raise ValueError(
            f"CSV thieu cot: {sorted(missing)}"
        )

    if len(rows) != EXPECTED:
        raise ValueError(
            f"Du kien {EXPECTED} chu, "
            f"file co {len(rows)}."
        )

    chars = set()
    prepared = []

    for row in rows:
        char = clean(row["KyTu"])

        if len(char) != 1:
            raise ValueError(
                f"Ky tu khong hop le: {char!r}"
            )

        if char in chars:
            raise ValueError(f"Trung chu: {char}")

        chars.add(char)

        if not clean(row["Pinyin"]):
            raise ValueError(
                f"{char}: thieu Pinyin"
            )

        if not clean(row["NghiaTiengViet"]):
            raise ValueError(
                f"{char}: thieu nghia"
            )

        strokes = int(clean(row["SoNet"]))
        if not 1 <= strokes <= 64:
            raise ValueError(
                f"{char}: SoNet khong hop le: {strokes}"
            )

        prepared.append({
            **row,
            "KyTu": char,
            "MaBaiHoc": int(row["MaBaiHoc"]),
            "SoThuTuBai": int(row["SoThuTuBai"]),
            "SoNet": strokes,
            "TrangThai": "ban_nhap",
        })

    return prepared


def get_columns(cursor):
    cursor.execute("""
        SELECT
            c.name,
            t.name,
            c.max_length,
            c.is_nullable,
            c.is_identity,
            c.is_computed,
            CASE WHEN dc.object_id IS NULL
                 THEN 0 ELSE 1 END
        FROM sys.columns AS c
        INNER JOIN sys.types AS t
            ON c.user_type_id = t.user_type_id
        LEFT JOIN sys.default_constraints AS dc
            ON dc.object_id = c.default_object_id
        WHERE c.object_id = OBJECT_ID(N'dbo.ChuHan')
        ORDER BY c.column_id;
    """)

    columns = {}

    for r in cursor.fetchall():
        columns[str(r[0])] = {
            "type": str(r[1]).lower(),
            "max_length": int(r[2]),
            "nullable": bool(r[3]),
            "identity": bool(r[4]),
            "computed": bool(r[5]),
            "has_default": bool(r[6]),
        }

    if not columns:
        raise RuntimeError(
            "Khong tim thay dbo.ChuHan."
        )

    return columns


def validate_schema(columns, rows):
    required = {
        "MaChuHan",
        "MaBaiHoc",
        "KyTu",
        "Pinyin",
        "NghiaTiengViet",
        "SoNet",
        "ThuTu",
        "TrangThai",
    }

    missing = required - set(columns)

    if missing:
        raise RuntimeError(
            f"ChuHan thieu cot: {sorted(missing)}"
        )

    # Khong tu dong chen gia tri cho cot bat buoc la.
    supported = (
        required
        | set(TEXT_COLUMNS)
        | set(OPTIONAL_NULL_COLUMNS)
        | {"MaBoThu", "NgayCapNhat"}
    )

    unexpected = []

    for name, info in columns.items():
        if (
            name not in supported
            and not info["nullable"]
            and not info["identity"]
            and not info["computed"]
            and not info["has_default"]
        ):
            unexpected.append(name)

    if unexpected:
        raise RuntimeError(
            "ChuHan co cot bat buoc chua xu ly: "
            + ", ".join(unexpected)
        )

    # Kiem tra gioi han do dai cac cot van ban.
    for row in rows:
        for name in TEXT_COLUMNS:
            if name not in columns:
                continue

            value = clean(row.get(name))
            info = columns[name]

            if not value:
                continue

            data_type = info["type"]
            max_bytes = info["max_length"]

            if max_bytes == -1:
                continue

            if data_type in ("nvarchar", "nchar"):
                length_bytes = len(
                    value.encode("utf-16-le")
                )

                if length_bytes > max_bytes:
                    raise RuntimeError(
                        f"{row['KyTu']}: {name} qua do dai "
                        f"({length_bytes}/{max_bytes} bytes)."
                    )

            elif data_type in ("varchar", "char"):
                # Khong tu doan code page SQL Server.
                if any(ord(ch) > 127 for ch in value):
                    raise RuntimeError(
                        f"Cot {name} khong phai Unicode. "
                        "Can kiem tra schema."
                    )

                if len(value.encode("ascii")) > max_bytes:
                    raise RuntimeError(
                        f"{row['KyTu']}: {name} qua dai."
                    )


def check_lessons(cursor, rows):
    cursor.execute("""
        SELECT MaBaiHoc, SoThuTuBai, TrangThai
        FROM dbo.BaiHoc
        WHERE MaKhoaHoc = ?;
    """, COURSE_ID)

    lessons = {
        int(r[0]): (int(r[1]), clean(r[2]))
        for r in cursor.fetchall()
    }

    if len(lessons) != 20:
        raise RuntimeError(
            "HSK3 khong co dung 20 bai."
        )

    for row in rows:
        lesson = lessons.get(row["MaBaiHoc"])

        if lesson is None:
            raise RuntimeError(
                f"{row['KyTu']}: MaBaiHoc khong thuoc HSK3."
            )

        if lesson[0] != row["SoThuTuBai"]:
            raise RuntimeError(
                f"{row['KyTu']}: so bai khong khop."
            )

        if lesson[1] != "ban_nhap":
            raise RuntimeError(
                "Co bai HSK3 khong o trang thai ban_nhap."
            )


def check_existing(cursor, rows):
    chars = [row["KyTu"] for row in rows]

    placeholders = ",".join("?" for _ in chars)

    cursor.execute(
        "SELECT KyTu FROM dbo.ChuHan "
        f"WHERE KyTu IN ({placeholders});",
        *chars,
    )

    found = sorted({
        clean(r[0]) for r in cursor.fetchall()
    })

    if found:
        raise RuntimeError(
            "Phat hien chu da ton tai trong SQL: "
            + ", ".join(found[:30])
            + (f" ... tong {len(found)}" if len(found) > 30 else "")
        )


def get_order_start(cursor):
    cursor.execute("""
        SELECT
            MaBaiHoc,
            COALESCE(MAX(ThuTu), 0)
        FROM dbo.ChuHan
        WHERE MaBaiHoc IN (
            SELECT MaBaiHoc
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
        )
        GROUP BY MaBaiHoc;
    """, COURSE_ID)

    return {
        int(r[0]): int(r[1])
        for r in cursor.fetchall()
    }


def make_rows(rows, starts):
    counts = Counter()
    prepared = []

    for row in sorted(
        rows,
        key=lambda x: (
            x["SoThuTuBai"],
            clean(x["KyTu"]),
        )
    ):
        lesson_id = row["MaBaiHoc"]
        counts[lesson_id] += 1

        row = dict(row)
        row["ThuTu"] = (
            starts.get(lesson_id, 0)
            + counts[lesson_id]
        )

        prepared.append(row)

    return prepared


def signature(rows, columns):
    payload = {
        "file_hash": hashlib.sha256(
            SOURCE.read_bytes()
        ).hexdigest(),
        "rows": rows,
        "columns": columns,
    }

    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def insert_rows(cursor, rows, columns):
    insert_fields = [
        "MaBaiHoc",
        "KyTu",
        "Pinyin",
        "NghiaTiengViet",
        "SoNet",
        "ThuTu",
        "TrangThai",
    ]

    # Neu schema ho tro cac cot mo rong,
    # su dung du lieu da co trong CSV.
    for name in (
        "CachGhiNho",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
    ):
        if name in columns:
            insert_fields.append(name)

    col_sql = ", ".join(
        f"[{name}]" for name in insert_fields
    )
    marks = ", ".join("?" for _ in insert_fields)

    sql = (
        f"INSERT INTO dbo.ChuHan ({col_sql}) "
        "OUTPUT INSERTED.MaChuHan "
        f"VALUES ({marks});"
    )

    inserted = []

    for row in rows:
        values = [
            (
                clean(row.get(name)) or None
                if name not in (
                    "MaBaiHoc", "SoNet", "ThuTu"
                )
                else row[name]
            )
            for name in insert_fields
        ]

        result_row = dict(row)

        cursor.execute(sql, *values)
        result = cursor.fetchone()

        if result is None:
            raise RuntimeError(
                f"Khong nhan ID cho {row['KyTu']}"
            )

        result_row["MaChuHan"] = int(result[0])
        inserted.append(result_row)

    return inserted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--commit", action="store_true"
    )
    args = parser.parse_args()

    print("=" * 68)
    print("BUOC 61 - IMPORT CHU HAN HSK3")
    print("=" * 68)
    print(
        "CHE DO:",
        "COMMIT" if args.commit else "PREVIEW",
    )

    rows = read_data()

    with closing(get_connection()) as conn:
        if getattr(conn, "autocommit", False):
            raise RuntimeError(
                "SQL connection dang autocommit=True."
            )

        with closing(conn.cursor()) as cursor:
            try:
                columns = get_columns(cursor)
                validate_schema(columns, rows)
                check_lessons(cursor, rows)
                check_existing(cursor, rows)

                starts = get_order_start(cursor)
                prepared = make_rows(rows, starts)

                plan_hash = signature(
                    prepared, columns
                )

                print("\nCAU TRUC BANG ChuHan:")
                for name, info in columns.items():
                    print(
                        f"  {name}: "
                        f"{info['type']} "
                        f"nullable={info['nullable']}"
                    )

                print("\nTONG HOP:")
                print("Tong chu moi:", len(prepared))
                print(
                    "Bai hoc:",
                    len({
                        r["MaBaiHoc"]
                        for r in prepared
                    }),
                )
                print(
                    "Co nghia:",
                    sum(bool(clean(r["NghiaTiengViet"]))
                        for r in prepared),
                )
                print(
                    "Trang thai INSERT: ban_nhap"
                )

                if not args.commit:
                    PREVIEW_FILE.write_text(
                        json.dumps({
                            "signature": plan_hash,
                            "count": len(prepared),
                        }, indent=2),
                        encoding="utf-8",
                    )

                    conn.rollback()
                    print("\nPREVIEW THANH CONG")
                    print("CHUA GHI SQL")
                    return

                if not PREVIEW_FILE.exists():
                    raise RuntimeError(
                        "Chua chay PREVIEW."
                    )

                saved = json.loads(
                    PREVIEW_FILE.read_text(
                        encoding="utf-8"
                    )
                )

                if (
                    saved.get("signature") != plan_hash
                    or saved.get("count") != EXPECTED
                ):
                    raise RuntimeError(
                        "Du lieu da doi so voi PREVIEW."
                    )

                if RESULT_FILE.exists():
                    raise RuntimeError(
                        "File mapping da ton tai."
                    )

                # Luu mapping tam truoc COMMIT.
                temp = RESULT_FILE.with_suffix(
                    ".pending.csv"
                )

                if temp.exists():
                    raise RuntimeError(
                        "Da co mapping tam."
                    )

                inserted = insert_rows(
                    cursor, prepared, columns
                )

                if len(inserted) != EXPECTED:
                    raise RuntimeError(
                        "So luong INSERT khong khop."
                    )

                # Xac minh cac ID vua tao
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM dbo.ChuHan AS ch
                    INNER JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = ch.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                """, COURSE_ID)

                actual = int(cursor.fetchone()[0])

                if actual != EXPECTED:
                    raise RuntimeError(
                        f"SQL HSK3 co {actual} chu, "
                        f"du kien {EXPECTED}."
                    )

                result_fields = [
                    "MaChuHan",
                    "KyTu",
                    "MaBaiHoc",
                    "SoThuTuBai",
                    "Pinyin",
                    "NghiaTiengViet",
                    "SoNet",
                    "ThuTu",
                    "TrangThai",
                ]

                with temp.open(
                    "x",
                    encoding="utf-8-sig",
                    newline="",
                ) as f:
                    writer = csv.DictWriter(
                        f,
                        fieldnames=result_fields,
                        extrasaction="ignore",
                    )
                    writer.writeheader()
                    writer.writerows(inserted)

                try:
                    conn.commit()
                except Exception:
                    temp.unlink(missing_ok=True)
                    raise

                try:
                    temp.rename(RESULT_FILE)
                    mapping_path = RESULT_FILE
                except OSError:
                    mapping_path = temp

                print("\nCOMMIT THANH CONG!")
                print("Da INSERT:", len(inserted))
                print("Trang thai: ban_nhap")
                print("Mapping:", mapping_path)

            except Exception:
                conn.rollback()
                raise


if __name__ == "__main__":
    main()
