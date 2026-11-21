
import sys
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1")
sys.path.insert(0, str(ROOT))

from database import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    print("===== CAU TRUC BANG NoiDungBaiHoc =====")

    cursor.execute("""
        SELECT
            c.name,
            t.name AS data_type,
            c.is_nullable,
            c.is_identity,
            c.is_computed,
            dc.definition AS default_value
        FROM sys.columns c
        JOIN sys.types t
            ON c.user_type_id = t.user_type_id
        LEFT JOIN sys.default_constraints dc
            ON c.default_object_id = dc.object_id
        WHERE c.object_id = OBJECT_ID('dbo.NoiDungBaiHoc')
        ORDER BY c.column_id
    """)

    for row in cursor.fetchall():
        print(
            f"{row[0]} | {row[1]} | "
            f"NULL={row[2]} | IDENTITY={row[3]} | "
            f"COMPUTED={row[4]} | DEFAULT={row[5]}"
        )

    print("\n===== CAC VIDEO HSK2 HIEN CO =====")

    cursor.execute("""
        SELECT *
        FROM dbo.NoiDungBaiHoc
        WHERE MaBaiHoc = ?
        ORDER BY MaNoiDung
    """, 25)

    columns = [c[0] for c in cursor.description]

    for row in cursor.fetchall():
        record = dict(zip(columns, row))

        print("\n--- BAN GHI ---")

        for key, value in record.items():
            if key.lower() == "noidung":
                try:
                    obj = json.loads(value or "{}")

                    print("NoiDung.youtube_id:",
                          obj.get("youtube_id"))

                    print("NoiDung.title:",
                          obj.get("title"))

                    print("NoiDung.module:",
                          obj.get("module"))

                    print("NoiDung.so_cau:",
                          len(obj.get("sentences", [])))

                    print("NoiDung.JSON_keys:",
                          list(obj.keys()))

                except (ValueError, TypeError):
                    print("NoiDung: Khong phai JSON hop le")
            else:
                print(f"{key}: {value}")

    print("\n===== KIEM TRA VIDEO THU 3 =====")

    path = (
        ROOT / "scripts" / "shadowing" / "hsk2"
        / "data" / "processed"
        / "video3_ready_for_review.json"
    )

    data = json.loads(path.read_text(encoding="utf-8"))

    print("YouTube ID:", data.get("youtube_id"))
    print("So cau:", len(data.get("sentences", [])))
    print("JSON keys:", list(data.keys()))

    print("\nCHI DOC DU LIEU - KHONG THAY DOI SQL.")

finally:
    conn.close()
