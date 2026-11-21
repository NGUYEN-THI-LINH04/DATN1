from contextlib import closing
from pathlib import Path

import csv
import re
import sys

import requests
from bs4 import BeautifulSoup


# =========================================================
# ĐƯỜNG DẪN PROJECT
#
# File:
# D:\DATN1\scripts\update_bo_thu_y_nghia.py
#
# Project:
# D:\DATN1
# =========================================================

SCRIPT_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

PROJECT_ROOT = (
    SCRIPT_DIR
    .parent
)


# =========================================================
# CHO PHÉP IMPORT database.py Ở THƯ MỤC GỐC
# =========================================================

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


from database import get_connection


# =========================================================
# CẤU HÌNH
# =========================================================

SOURCE_URL = (
    "https://mychinese.vn/"
    "214-bo-thu-tieng-trung.html"
)


# =========================================================
# THƯ MỤC BACKUP
# =========================================================

BACKUP_DIR = (
    SCRIPT_DIR
    / "backups"
)

BACKUP_DIR.mkdir(
    parents=True,
    exist_ok=True
)


DATABASE_BACKUP_FILE = (
    BACKUP_DIR
    / "bo_thu_before_update_y_nghia.csv"
)


SOURCE_SNAPSHOT_FILE = (
    BACKUP_DIR
    / "bo_thu_source_214.csv"
)


# =========================================================
# CHUẨN HÓA TEXT
# =========================================================

def clean_text(value):

    if value is None:

        return ""

    value = str(value)

    value = value.replace(
        "\xa0",
        " "
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# =========================================================
# LẤY TẤT CẢ KÝ TỰ HÁN TRONG Ô "BỘ"
#
# Ví dụ:
#
# 人(亻)
# -> ["人", "亻"]
#
# 水(氵、氺)
# -> ["水", "氵", "氺"]
#
# 川、巛
# -> ["川", "巛"]
# =========================================================

def extract_hanzi_characters(text):

    text = clean_text(
        text
    )

    characters = re.findall(
        (
            r"[\u3400-\u4DBF"
            r"\u4E00-\u9FFF"
            r"\uF900-\uFAFF]"
        ),
        text
    )


    # =====================================================
    # LOẠI TRÙNG NHƯNG GIỮ THỨ TỰ
    # =====================================================

    result = []

    seen = set()


    for character in characters:

        if character not in seen:

            seen.add(
                character
            )

            result.append(
                character
            )


    return result


# =========================================================
# TẢI TRANG NGUỒN
# =========================================================

def download_source():

    print()
    print(
        "1. Dang tai du lieu 214 Bo Thu..."
    )


    headers = {

        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/154.0.0.0 "
            "Safari/537.36"
        ),

        "Accept-Language": (
            "vi-VN,vi;q=0.9,"
            "en-US;q=0.8,en;q=0.7"
        ),
    }


    response = requests.get(
        SOURCE_URL,
        headers=headers,
        timeout=30,
    )


    response.raise_for_status()


    response.encoding = (
        response.apparent_encoding
        or "utf-8"
    )


    html = response.text


    if not html.strip():

        raise RuntimeError(
            "Trang nguon tra ve noi dung rong."
        )


    print(
        "   -> Tai trang nguon thanh cong."
    )


    return html


# =========================================================
# ĐỌC TẤT CẢ CÁC DÒNG CÓ DẠNG BỘ THỦ TRÊN TRANG
#
# QUAN TRỌNG:
#
# KHÔNG cho rằng STT đầu tiên xuất hiện trên trang
# chính là thứ tự Khang Hy.
#
# Ta chỉ thu thập candidate.
#
# Sau đó sẽ đối chiếu:
#
# MaBoThu + KyHieu
#
# với:
#
# STT nguồn + ký hiệu nguồn.
# =========================================================

def parse_source_candidates(
    html
):

    print()
    print(
        "2. Dang doc cac dong Bo Thu "
        "tu trang nguon..."
    )


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    candidates = []


    for row in soup.find_all(
        "tr"
    ):

        cells = row.find_all(
            [
                "td",
                "th",
            ]
        )


        if not cells:

            continue


        raw_values = [
            clean_text(
                cell.get_text(
                    " ",
                    strip=True
                )
            )
            for cell in cells
        ]


        # =================================================
        # BỎ Ô HTML RỖNG
        # =================================================

        values = [
            value
            for value in raw_values
            if value
        ]


        if len(values) < 5:

            continue


        # =================================================
        # CỘT ĐẦU PHẢI LÀ STT
        # =================================================

        number_text = values[0]


        if not re.fullmatch(
            r"\d{1,3}",
            number_text
        ):

            continue


        number = int(
            number_text
        )


        if (
            number < 1
            or
            number > 214
        ):

            continue


        symbol_text = clean_text(
            values[1]
        )

        name = clean_text(
            values[2]
        )

        pinyin = clean_text(
            values[3]
        )

        meaning = clean_text(
            values[4]
        )


        symbols = (
            extract_hanzi_characters(
                symbol_text
            )
        )


        if not symbols:

            continue


        if not meaning:

            continue


        candidates.append(
            {
                "number": number,

                "symbol_text":
                    symbol_text,

                "symbols":
                    symbols,

                "name":
                    name,

                "pinyin":
                    pinyin,

                "meaning":
                    meaning,
            }
        )


    if not candidates:

        raise RuntimeError(
            "Khong doc duoc dong Bo Thu "
            "nao tu trang nguon."
        )


    print(
        "   -> Doc duoc "
        f"{len(candidates)} dong candidate."
    )


    return candidates


# =========================================================
# ĐỌC 214 BỘ THỦ TRONG SQL
# =========================================================

def load_database_radicals(
    cursor
):

    print()
    print(
        "3. Dang kiem tra dbo.BoThu..."
    )


    cursor.execute(
        """
        SELECT
            MaBoThu,
            KyHieu,
            TenBoThu,
            YNghia,
            SoNet,
            MoTa,
            MaTep,
            TrangThai

        FROM dbo.BoThu

        ORDER BY
            MaBoThu;
        """
    )


    rows = cursor.fetchall()


    if len(rows) != 214:

        raise RuntimeError(
            "dbo.BoThu hien co "
            f"{len(rows)} dong, "
            "khong phai 214."
        )


    # =====================================================
    # DATABASE HIỆN TẠI CỦA BẠN:
    # MaBoThu = 1 -> 214
    # =====================================================

    ids = [
        int(row[0])
        for row in rows
    ]


    expected_ids = list(
        range(
            1,
            215
        )
    )


    if ids != expected_ids:

        raise RuntimeError(
            "MaBoThu khong lien tuc "
            "tu 1 den 214. "
            "Khong cap nhat."
        )


    missing_meaning = sum(
        1
        for row in rows
        if not clean_text(
            row[3]
        )
    )


    print(
        "   -> Tong Bo Thu: "
        f"{len(rows)}"
    )

    print(
        "   -> Dang thieu YNghia: "
        f"{missing_meaning}"
    )


    return rows


# =========================================================
# MATCH SQL VỚI NGUỒN
#
# Điều kiện bắt buộc:
#
# 1. MaBoThu == STT nguồn
# 2. KyHieu SQL xuất hiện trong ô Bộ của nguồn
#
# Ví dụ:
#
# SQL:
# #9 人
#
# Nguồn:
# #9 人(亻)
#
# => MATCH
# =========================================================

def match_database_with_source(
    db_rows,
    candidates,
):

    print()
    print(
        "4. Dang ghep SQL voi nguon "
        "theo MaBoThu + KyHieu..."
    )


    matches = {}

    errors = []


    for row in db_rows:

        radical_id = int(
            row[0]
        )

        db_symbol = clean_text(
            row[1]
        )

        db_name = clean_text(
            row[2]
        )


        # =================================================
        # CHỈ LẤY DÒNG CÙNG STT
        # VÀ CHỨA ĐÚNG KÝ HIỆU SQL
        # =================================================

        possible = [
            item
            for item in candidates

            if (
                item["number"]
                == radical_id

                and

                db_symbol
                in item["symbols"]
            )
        ]


        # =================================================
        # LOẠI DÒNG TRÙNG HOÀN TOÀN
        # =================================================

        unique = {}


        for item in possible:

            key = (
                item["number"],
                item["symbol_text"],
                item["meaning"],
            )

            unique[key] = item


        possible = list(
            unique.values()
        )


        # =================================================
        # PHẢI MATCH CHÍNH XÁC MỘT DÒNG
        # =================================================

        if len(possible) != 1:

            errors.append(
                {
                    "id": radical_id,

                    "db_symbol":
                        db_symbol,

                    "db_name":
                        db_name,

                    "matches":
                        possible,
                }
            )

            continue


        matches[
            radical_id
        ] = possible[0]


    # =====================================================
    # PHẢI ĐỦ 214
    # =====================================================

    if len(matches) != 214:

        print()
        print(
            "KHONG MATCH DU 214 BO THU."
        )

        print(
            "Cac dong co van de:"
        )


        for error in errors[:30]:

            print(
                "   "
                f"#{error['id']} "
                f"SQL='{error['db_symbol']}' "
                f"{error['db_name']} "
                f"-> {len(error['matches'])} match"
            )


        raise RuntimeError(
            "Chi match duoc "
            f"{len(matches)}/214. "
            "KHONG cap nhat SQL."
        )


    print(
        "   -> MATCH THANH CONG 214/214."
    )


    return matches


# =========================================================
# HIỂN THỊ ĐỐI CHIẾU TRƯỚC KHI UPDATE
# =========================================================

def print_match_preview(
    db_rows,
    matches
):

    print()
    print(
        "5. Kiem tra 15 dong dau:"
    )


    print(
        "-" * 90
    )


    for row in db_rows[:15]:

        radical_id = int(
            row[0]
        )

        db_symbol = clean_text(
            row[1]
        )

        db_name = clean_text(
            row[2]
        )

        source = matches[
            radical_id
        ]


        print(
            f"#{radical_id:<3} "
            f"SQL {db_symbol} "
            f"({db_name}) "
            f"<-> "
            f"NGUON {source['symbol_text']} "
            f"({source['name']})"
        )

        print(
            "     Nghia: "
            f"{source['meaning']}"
        )


    print(
        "-" * 90
    )


# =========================================================
# BACKUP DATABASE
# =========================================================

def backup_database(
    rows
):

    print()
    print(
        "6. Dang backup dbo.BoThu..."
    )


    with open(
        DATABASE_BACKUP_FILE,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.writer(
            file
        )


        writer.writerow(
            [
                "MaBoThu",
                "KyHieu",
                "TenBoThu",
                "YNghia",
                "SoNet",
                "MoTa",
                "MaTep",
                "TrangThai",
            ]
        )


        for row in rows:

            writer.writerow(
                [
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                ]
            )


    print(
        "   -> Backup:"
    )

    print(
        f"      {DATABASE_BACKUP_FILE}"
    )


# =========================================================
# LƯU SNAPSHOT NGUỒN 214 DÒNG
# =========================================================

def save_source_snapshot(
    db_rows,
    matches
):

    with open(
        SOURCE_SNAPSHOT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.writer(
            file
        )


        writer.writerow(
            [
                "MaBoThu",
                "KyHieuSQL",
                "TenBoThuSQL",
                "KyHieuNguon",
                "TenNguon",
                "PinyinNguon",
                "YNghiaNguon",
            ]
        )


        for row in db_rows:

            radical_id = int(
                row[0]
            )

            source = matches[
                radical_id
            ]


            writer.writerow(
                [
                    radical_id,
                    row[1],
                    row[2],
                    source["symbol_text"],
                    source["name"],
                    source["pinyin"],
                    source["meaning"],
                ]
            )


    print()
    print(
        "   -> Snapshot nguon:"
    )

    print(
        f"      {SOURCE_SNAPSHOT_FILE}"
    )


# =========================================================
# UPDATE SQL
#
# QUAN TRỌNG:
#
# UPDATE theo CẢ:
#
# MaBoThu
# KyHieu
#
# và chỉ update nếu YNghia đang trống.
# =========================================================

def update_meanings(
    cursor,
    db_rows,
    matches
):

    print()
    print(
        "7. Dang cap nhat YNghia..."
    )


    updated_count = 0


    for row in db_rows:

        radical_id = int(
            row[0]
        )

        db_symbol = clean_text(
            row[1]
        )

        meaning = matches[
            radical_id
        ]["meaning"]


        cursor.execute(
            """
            UPDATE dbo.BoThu

            SET
                YNghia = ?

            WHERE
                MaBoThu = ?

                AND KyHieu = ?

                AND NULLIF(
                    LTRIM(
                        RTRIM(
                            YNghia
                        )
                    ),
                    N''
                ) IS NULL;
            """,

            meaning,

            radical_id,

            db_symbol,
        )


        if (
            cursor.rowcount
            and
            cursor.rowcount > 0
        ):

            updated_count += (
                cursor.rowcount
            )


    print(
        "   -> So dong update: "
        f"{updated_count}"
    )


    return updated_count


# =========================================================
# VERIFY SAU UPDATE
# =========================================================

def verify_result(
    cursor
):

    cursor.execute(
        """
        SELECT
            COUNT(*) AS TongBoThu,

            SUM(
                CASE

                    WHEN NULLIF(
                        LTRIM(
                            RTRIM(
                                YNghia
                            )
                        ),
                        N''
                    ) IS NULL

                    THEN 1

                    ELSE 0

                END
            ) AS ConThieuYNghia

        FROM dbo.BoThu;
        """
    )


    row = cursor.fetchone()


    return (
        int(
            row[0]
            or 0
        ),

        int(
            row[1]
            or 0
        ),
    )


# =========================================================
# HIỂN THỊ DỮ LIỆU SAU UPDATE
# =========================================================

def print_database_preview(
    cursor
):

    cursor.execute(
        """
        SELECT TOP (15)
            MaBoThu,
            KyHieu,
            TenBoThu,
            YNghia,
            SoNet

        FROM dbo.BoThu

        ORDER BY
            MaBoThu;
        """
    )


    rows = cursor.fetchall()


    print()
    print(
        "15 dong dau sau khi update:"
    )

    print(
        "-" * 90
    )


    for row in rows:

        print(
            f"#{row[0]:<3} "
            f"{row[1]} | "
            f"{row[2]} | "
            f"{row[3]} | "
            f"{row[4]} net"
        )


    print(
        "-" * 90
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "=" * 70
    )

    print(
        "CAP NHAT Y NGHIA 214 BO THU"
    )

    print(
        "MATCH THEO MaBoThu + KyHieu"
    )

    print(
        "=" * 70
    )


    # =====================================================
    # TẢI NGUỒN
    # =====================================================

    html = download_source()


    # =====================================================
    # ĐỌC TẤT CẢ CANDIDATE
    # =====================================================

    candidates = (
        parse_source_candidates(
            html
        )
    )


    # =====================================================
    # DATABASE
    # =====================================================

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:


                # =========================================
                # ĐỌC SQL
                # =========================================

                db_rows = (
                    load_database_radicals(
                        cursor
                    )
                )


                # =========================================
                # MATCH 214/214
                # =========================================

                matches = (
                    match_database_with_source(
                        db_rows,
                        candidates,
                    )
                )


                # =========================================
                # HIỂN THỊ ĐỐI CHIẾU
                # =========================================

                print_match_preview(
                    db_rows,
                    matches,
                )


                # =========================================
                # BACKUP SQL
                # =========================================

                backup_database(
                    db_rows
                )


                # =========================================
                # LƯU NGUỒN
                # =========================================

                save_source_snapshot(
                    db_rows,
                    matches,
                )


                # =========================================
                # XÁC NHẬN
                # =========================================

                print()
                print(
                    "=" * 70
                )

                print(
                    "DA MATCH CHINH XAC 214/214."
                )

                print()
                print(
                    "Script CHI cap nhat:"
                )

                print(
                    " - dbo.BoThu.YNghia"
                )

                print()
                print(
                    "Script KHONG sua:"
                )

                print(
                    " - MaBoThu"
                )

                print(
                    " - KyHieu"
                )

                print(
                    " - TenBoThu"
                )

                print(
                    " - SoNet"
                )

                print(
                    " - MoTa"
                )

                print(
                    " - MaTep"
                )

                print(
                    " - TrangThai"
                )

                print(
                    "=" * 70
                )


                confirm = input(
                    "\nNhap CAPNHAT de tiep tuc: "
                ).strip()


                if confirm != "CAPNHAT":

                    connection.rollback()

                    print()
                    print(
                        "Da huy."
                    )

                    print(
                        "SQL Server khong thay doi."
                    )

                    return


                # =========================================
                # UPDATE
                # =========================================

                updated_count = (
                    update_meanings(
                        cursor,
                        db_rows,
                        matches,
                    )
                )


                # =========================================
                # VERIFY
                # =========================================

                total, missing = (
                    verify_result(
                        cursor
                    )
                )


                if total != 214:

                    raise RuntimeError(
                        "TongBoThu sau update "
                        "khong bang 214."
                    )


                if missing != 0:

                    raise RuntimeError(
                        "Van con "
                        f"{missing} Bo Thu "
                        "chua co YNghia."
                    )


                # =========================================
                # TRONG TRƯỜNG HỢP BAN ĐẦU 214 ĐỀU TRỐNG
                # THÌ PHẢI UPDATE ĐỦ 214
                # =========================================

                initially_missing = sum(
                    1
                    for row in db_rows
                    if not clean_text(
                        row[3]
                    )
                )


                if (
                    initially_missing == 214
                    and
                    updated_count != 214
                ):

                    raise RuntimeError(
                        "Ban dau thieu 214 YNghia "
                        "nhung khong update du 214. "
                        "Rollback."
                    )


                # =========================================
                # XEM TRƯỚC
                # =========================================

                print_database_preview(
                    cursor
                )


            # =================================================
            # COMMIT CHỈ SAU KHI MỌI KIỂM TRA ĐỀU ĐÚNG
            # =================================================

            connection.commit()


        except Exception:

            connection.rollback()

            print()
            print(
                "=" * 70
            )

            print(
                "CO LOI -> DA ROLLBACK."
            )

            print(
                "SQL Server khong luu "
                "cac thay doi dang do."
            )

            print(
                "=" * 70
            )

            raise


    # =====================================================
    # HOÀN TẤT
    # =====================================================

    print()
    print(
        "=" * 70
    )

    print(
        "CAP NHAT THANH CONG!"
    )

    print(
        f"So dong update       : "
        f"{updated_count}"
    )

    print(
        "Tong Bo Thu          : 214"
    )

    print(
        "Con thieu YNghia     : 0"
    )

    print(
        "MoTa                 : GIU NGUYEN"
    )

    print(
        "Media                : GIU NGUYEN"
    )

    print(
        "TrangThai            : GIU NGUYEN"
    )

    print(
        "=" * 70
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    try:

        main()


    except requests.RequestException as error:

        print()
        print(
            "LOI KHI TAI TRANG NGUON:"
        )

        print(
            error
        )

        raise SystemExit(
            1
        )


    except Exception as error:

        print()
        print(
            "LOI:"
        )

        print(
            error
        )

        raise SystemExit(
            1
        )