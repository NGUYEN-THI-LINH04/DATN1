import csv
import pyodbc


CSV_PATH = r"D:\DATN1\data_sources\hsk1_tuvung_501_examples.csv"


# ============================================================
# KẾT NỐI SQL SERVER
# ============================================================

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=MSI\\LINH;"
    "DATABASE=HocTiengTrungDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(connection_string)

cursor = conn.cursor()


# ============================================================
# ĐỌC CSV
# ============================================================

updated = 0
skipped = 0


with open(
    CSV_PATH,
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        ma_tu_vung = int(
            row["MaTuVung"]
        )

        chu_han = (
            row["ChuHan"]
            or ""
        ).strip()

        vi_du_trung = (
            row["ViDuTiengTrung"]
            or ""
        ).strip()

        vi_du_viet = (
            row["ViDuTiengViet"]
            or ""
        ).strip()


        if not vi_du_trung or not vi_du_viet:

            print(
                f"Bỏ qua MaTuVung={ma_tu_vung}: "
                "chưa có đủ ví dụ."
            )

            skipped += 1

            continue


        cursor.execute(
            """
            UPDATE TuVung

            SET
                ViDuTiengTrung = ?,
                ViDuTiengViet = ?

            WHERE MaTuVung = ?
              AND ChuHan = ?
            """,

            vi_du_trung,
            vi_du_viet,
            ma_tu_vung,
            chu_han
        )


        if cursor.rowcount == 1:

            updated += 1

        else:

            print(
                f"Không cập nhật được: "
                f"{ma_tu_vung} - {chu_han}"
            )


# ============================================================
# LƯU
# ============================================================

conn.commit()


# ============================================================
# KIỂM TRA SAU KHI UPDATE
# ============================================================

cursor.execute(
    """
    SELECT
        COUNT(*)

    FROM TuVung tv

    INNER JOIN TuVungBaiHoc tvbh
        ON tvbh.MaTuVung = tv.MaTuVung

    INNER JOIN BaiHoc bh
        ON bh.MaBaiHoc = tvbh.MaBaiHoc

    INNER JOIN KhoaHoc kh
        ON kh.MaKhoaHoc = bh.MaKhoaHoc

    WHERE kh.MaKyHieu = 'HSK1-CORE'

      AND
      (
            tv.ViDuTiengTrung IS NULL

         OR LTRIM(
                RTRIM(
                    tv.ViDuTiengTrung
                )
            ) = ''

         OR tv.ViDuTiengViet IS NULL

         OR LTRIM(
                RTRIM(
                    tv.ViDuTiengViet
                )
            ) = ''
      )
    """
)


remaining = cursor.fetchone()[0]


print()
print("================================")
print("HOÀN THÀNH")
print("================================")
print(
    "Đã cập nhật:",
    updated
)

print(
    "Bỏ qua:",
    skipped
)

print(
    "Số từ HSK1 còn thiếu ví dụ:",
    remaining
)


cursor.close()

conn.close()