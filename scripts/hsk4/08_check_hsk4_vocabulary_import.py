# -*- coding: utf-8 -*-
"""
BUOC 08 - KIEM TRA HAU COMMIT TU VUNG HSK4

Muc dich:
1. Kiem tra file mapping 1000 muc.
2. Xac nhan:
   - 12 muc tai su dung
   - 988 muc INSERT moi
3. Kiem tra tat ca MaTuVung mapping deu ton tai trong SQL.
4. Kiem tra 988 tu moi:
   - ChuHan
   - Pinyin
   - NghiaTiengViet
   - TuLoai
   - DaDuyet = 0
5. Kiem tra 12 tu tai su dung van dung ChuHan + Pinyin.
6. Kiem tra 988 tu moi CHUA bi gan vao BaiHoc.
7. Bao ve HSK1-HSK3:
   - HSK1 = 501
   - HSK2 = 772
   - HSK3 = 973
8. Xac nhan HSK4 van chua co BaiHoc/TuVungBaiHoc.

CHI DOC SQL.
KHONG INSERT / UPDATE / DELETE.
"""

import csv
import json
import re
import sys
import unicodedata

from collections import Counter
from contextlib import closing
from pathlib import Path


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT),
)

from database import get_connection


COURSE_ID = 4

EXPECTED_TOTAL = 1000
EXPECTED_REUSE = 12
EXPECTED_INSERT = 988

EXPECTED_SQL_TOTAL = 3208

EXPECTED_OLD_LINKS = {
    1: 501,
    2: 772,
    3: 973,
}

DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

MAPPING_FILE = (
    DATA_DIR
    / "vocabulary_hsk4_import_result.csv"
)

REPORT_FILE = (
    DATA_DIR
    / "hsk4_vocabulary_post_commit_check.json"
)


# ==========================================================
# 2. HAM HO TRO
# ==========================================================

def clean(value):
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def pinyin_key(value):

    return (
        unicodedata.normalize(
            "NFC",
            clean(value).casefold(),
        )
        .replace(" ", "")
        .replace("'", "")
        .replace("’", "")
    )


def chunks(values, size=500):

    values = list(values)

    for start in range(
        0,
        len(values),
        size,
    ):

        yield values[
            start:start + size
        ]


def read_mapping():

    if not MAPPING_FILE.is_file():

        raise FileNotFoundError(
            "Khong tim thay mapping sau import:\n"
            + str(MAPPING_FILE)
        )

    with MAPPING_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    if len(rows) != EXPECTED_TOTAL:

        raise RuntimeError(
            f"Mapping phai co {EXPECTED_TOTAL} dong, "
            f"hien co {len(rows)}."
        )

    required = {
        "MaMucNoiBo",
        "MaTuHSK",
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "TuLoai",
        "NghiaTiengViet",
        "HanhDong",
    }

    missing = (
        required
        - set(rows[0].keys())
    )

    if missing:

        raise RuntimeError(
            "Mapping thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    return rows


def load_vocabulary_by_ids(
    cursor,
    ids,
):

    result = {}

    for part in chunks(
        ids,
        500,
    ):

        placeholders = ",".join(
            "?"
            for _ in part
        )

        cursor.execute(
            f"""
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm,
                NghiaTiengViet,
                TuLoai,
                DaDuyet
            FROM dbo.TuVung
            WHERE MaTuVung IN (
                {placeholders}
            );
            """,
            *part,
        )

        for row in cursor.fetchall():

            vocab_id = int(
                row[0]
            )

            result[vocab_id] = {

                "MaTuVung":
                    vocab_id,

                "ChuHan":
                    clean(row[1]),

                "PhienAm":
                    clean(row[2]),

                "NghiaTiengViet":
                    clean(row[3]),

                "TuLoai":
                    clean(row[4]),

                "DaDuyet":
                    row[5],
            }

    return result


def count_links_for_ids(
    cursor,
    ids,
):

    total = 0

    for part in chunks(
        ids,
        500,
    ):

        placeholders = ",".join(
            "?"
            for _ in part
        )

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc
            WHERE MaTuVung IN (
                {placeholders}
            );
            """,
            *part,
        )

        total += int(
            cursor.fetchone()[0]
        )

    return total


# ==========================================================
# 3. MAIN
# ==========================================================

def main():

    print("=" * 76)

    print(
        "BUOC 08 - KIEM TRA HAU COMMIT "
        "TU VUNG HSK4"
    )

    print("=" * 76)

    print(
        "CHI DOC SQL - "
        "KHONG INSERT / UPDATE / DELETE"
    )

    # ======================================================
    # 1. DOC MAPPING
    # ======================================================

    print(
        "\n[1] KIEM TRA FILE MAPPING"
    )

    mapping = read_mapping()

    actions = Counter(
        clean(
            row.get("HanhDong")
        )
        for row in mapping
    )

    print(
        "Tong mapping:",
        len(mapping),
    )

    print(
        "TAI_SU_DUNG:",
        actions["TAI_SU_DUNG"],
    )

    print(
        "INSERT_MOI:",
        actions["INSERT_MOI"],
    )

    if (
        actions["TAI_SU_DUNG"]
        != EXPECTED_REUSE
    ):

        raise RuntimeError(
            "Sai so luong TAI_SU_DUNG."
        )

    if (
        actions["INSERT_MOI"]
        != EXPECTED_INSERT
    ):

        raise RuntimeError(
            "Sai so luong INSERT_MOI."
        )

    if set(
        actions.keys()
    ) != {
        "TAI_SU_DUNG",
        "INSERT_MOI",
    }:

        raise RuntimeError(
            "Mapping con HanhDong "
            "khong hop le."
        )

    # ======================================================
    # 2. KIEM TRA ID
    # ======================================================

    source_codes = []
    vocab_ids = []

    for row in mapping:

        code = clean(
            row.get("MaMucNoiBo")
        )

        if not re.fullmatch(
            r"L4-\d{4}",
            code,
        ):

            raise RuntimeError(
                f"MaMucNoiBo khong hop le: {code}"
            )

        source_codes.append(
            code
        )

        raw_id = clean(
            row.get("MaTuVung")
        )

        if not raw_id:

            raise RuntimeError(
                f"{code}: thieu MaTuVung."
            )

        try:

            vocab_id = int(
                raw_id
            )

        except ValueError:

            raise RuntimeError(
                f"{code}: MaTuVung "
                "khong phai so."
            )

        vocab_ids.append(
            vocab_id
        )

    if (
        len(set(source_codes))
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "MaMucNoiBo bi trung."
        )

    if (
        len(set(vocab_ids))
        != EXPECTED_TOTAL
    ):

        raise RuntimeError(
            "1000 muc HSK4 khong map "
            "toi 1000 MaTuVung rieng."
        )

    print(
        "PASS: 1000 MaMucNoiBo duy nhat."
    )

    print(
        "PASS: 1000 MaTuVung mapping duy nhat."
    )

    insert_rows = [
        row
        for row in mapping
        if clean(
            row.get("HanhDong")
        )
        == "INSERT_MOI"
    ]

    reuse_rows = [
        row
        for row in mapping
        if clean(
            row.get("HanhDong")
        )
        == "TAI_SU_DUNG"
    ]

    inserted_ids = [
        int(
            clean(
                row["MaTuVung"]
            )
        )
        for row in insert_rows
    ]

    reuse_ids = [
        int(
            clean(
                row["MaTuVung"]
            )
        )
        for row in reuse_rows
    ]

    if (
        set(inserted_ids)
        & set(reuse_ids)
    ):

        raise RuntimeError(
            "ID INSERT va REUSE bi giao nhau."
        )

    # ======================================================
    # 3. KIEM TRA SQL
    # ======================================================

    print(
        "\n[2] KIEM TRA SQL"
    )

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            cursor.execute(
                "SELECT DB_NAME();"
            )

            db_name = clean(
                cursor.fetchone()[0]
            )

            print(
                "Database:",
                db_name,
            )

            if (
                db_name.casefold()
                !=
                "HocTiengTrungDB".casefold()
            ):

                raise RuntimeError(
                    "Dang ket noi nham database."
                )

            # ----------------------------------------------
            # Tong TuVung
            # ----------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.TuVung;
                """
            )

            sql_total = int(
                cursor.fetchone()[0]
            )

            print(
                "dbo.TuVung:",
                sql_total,
            )

            if (
                sql_total
                != EXPECTED_SQL_TOTAL
            ):

                raise RuntimeError(
                    "Tong dbo.TuVung "
                    "khong phai 3208."
                )

            # ----------------------------------------------
            # Reference HSK4
            # ----------------------------------------------

            cursor.execute(
                """
                SELECT
                    COUNT(*),
                    COUNT(
                        DISTINCT MaMucNoiBo
                    )
                FROM dbo.TuVungHSKChuan
                WHERE MaCapDo = 4;
                """
            )

            (
                ref_total,
                ref_unique,
            ) = cursor.fetchone()

            ref_total = int(
                ref_total
            )

            ref_unique = int(
                ref_unique
            )

            print(
                "TuVungHSKChuan HSK4:",
                ref_total,
            )

            if (
                ref_total
                != EXPECTED_TOTAL
                or
                ref_unique
                != EXPECTED_TOTAL
            ):

                raise RuntimeError(
                    "HSK4 reference "
                    "khong con dung 1000."
                )

            # ----------------------------------------------
            # Doc 1000 TuVung mapping
            # ----------------------------------------------

            sql_vocab = (
                load_vocabulary_by_ids(
                    cursor,
                    vocab_ids,
                )
            )

            print(
                "MaTuVung mapping tim thay:",
                len(sql_vocab),
            )

            if (
                len(sql_vocab)
                != EXPECTED_TOTAL
            ):

                missing_ids = (
                    set(vocab_ids)
                    - set(sql_vocab)
                )

                raise RuntimeError(
                    "Thieu MaTuVung trong SQL: "
                    + ", ".join(
                        str(value)
                        for value
                        in sorted(
                            missing_ids
                        )[:20]
                    )
                )

            # ==================================================
            # 4. KIEM TRA 988 TU MOI
            # ==================================================

            print(
                "\n[3] KIEM TRA 988 TU MOI"
            )

            bad_inserted = []

            approved_new = 0
            null_approval_new = 0

            for row in insert_rows:

                code = clean(
                    row["MaMucNoiBo"]
                )

                vocab_id = int(
                    clean(
                        row["MaTuVung"]
                    )
                )

                db = sql_vocab[
                    vocab_id
                ]

                problems = []

                if (
                    db["ChuHan"]
                    != clean(
                        row["ChuHan"]
                    )
                ):
                    problems.append(
                        "SAI_CHUHAN"
                    )

                if (
                    pinyin_key(
                        db["PhienAm"]
                    )
                    !=
                    pinyin_key(
                        row["PhienAm"]
                    )
                ):
                    problems.append(
                        "SAI_PINYIN"
                    )

                if (
                    db["NghiaTiengViet"]
                    != clean(
                        row[
                            "NghiaTiengViet"
                        ]
                    )
                ):
                    problems.append(
                        "SAI_NGHIA"
                    )

                if (
                    db["TuLoai"]
                    != clean(
                        row["TuLoai"]
                    )
                ):
                    problems.append(
                        "SAI_TULOAI"
                    )

                if (
                    db["DaDuyet"]
                    is None
                ):

                    null_approval_new += 1
                    problems.append(
                        "DADUYET_NULL"
                    )

                elif int(
                    db["DaDuyet"]
                ) != 0:

                    approved_new += 1
                    problems.append(
                        "DADUYET_KHONG_BANG_0"
                    )

                if problems:

                    bad_inserted.append({
                        "MaMucNoiBo":
                            code,

                        "MaTuVung":
                            vocab_id,

                        "Loi":
                            problems,
                    })

            print(
                "INSERT tim thay:",
                len(insert_rows),
            )

            print(
                "Sai du lieu:",
                len(bad_inserted),
            )

            print(
                "DaDuyet NULL:",
                null_approval_new,
            )

            print(
                "DaDuyet != 0:",
                approved_new,
            )

            if bad_inserted:

                print(
                    "\n20 loi dau:"
                )

                for item in (
                    bad_inserted[:20]
                ):
                    print(
                        " ",
                        item,
                    )

                raise RuntimeError(
                    "988 tu moi "
                    "chua khop mapping."
                )

            print(
                "PASS: 988/988 tu moi "
                "khop mapping va DaDuyet=0."
            )

            # ==================================================
            # 5. KIEM TRA 12 TU TAI SU DUNG
            # ==================================================

            print(
                "\n[4] KIEM TRA 12 TU TAI SU DUNG"
            )

            bad_reuse = []

            for row in reuse_rows:

                code = clean(
                    row["MaMucNoiBo"]
                )

                vocab_id = int(
                    clean(
                        row["MaTuVung"]
                    )
                )

                db = sql_vocab[
                    vocab_id
                ]

                problems = []

                # REUSE chi yeu cau cung
                # ChuHan + Pinyin.
                # Nghia/TuLoai co the rong hon
                # hoac khac cach phan loai.

                if (
                    db["ChuHan"]
                    != clean(
                        row["ChuHan"]
                    )
                ):

                    problems.append(
                        "SAI_CHUHAN"
                    )

                if (
                    pinyin_key(
                        db["PhienAm"]
                    )
                    !=
                    pinyin_key(
                        row["PhienAm"]
                    )
                ):

                    problems.append(
                        "SAI_PINYIN"
                    )

                if problems:

                    bad_reuse.append({
                        "MaMucNoiBo":
                            code,

                        "MaTuVung":
                            vocab_id,

                        "Loi":
                            problems,
                    })

            print(
                "REUSE tim thay:",
                len(reuse_rows),
            )

            print(
                "Sai:",
                len(bad_reuse),
            )

            if bad_reuse:

                raise RuntimeError(
                    "12 tu REUSE "
                    "khong con khop SQL."
                )

            print(
                "PASS: 12/12 "
                "tai su dung dung MaTuVung."
            )

            # ==================================================
            # 6. TU MOI CHUA DUOC GAN BAI HOC
            # ==================================================

            print(
                "\n[5] KIEM TRA LIEN KET BAI HOC"
            )

            inserted_links = (
                count_links_for_ids(
                    cursor,
                    inserted_ids,
                )
            )

            print(
                "Lien ket TuVungBaiHoc "
                "cua 988 tu moi:",
                inserted_links,
            )

            if inserted_links != 0:

                raise RuntimeError(
                    "Co tu HSK4 moi "
                    "da bi gan vao BaiHoc "
                    "truoc khi chia bai."
                )

            # ----------------------------------------------
            # HSK4 BaiHoc
            # ----------------------------------------------

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.BaiHoc
                WHERE MaKhoaHoc = ?;
                """,
                COURSE_ID,
            )

            hsk4_lessons = int(
                cursor.fetchone()[0]
            )

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM dbo.TuVungBaiHoc AS tvbh
                INNER JOIN dbo.BaiHoc AS bh
                    ON bh.MaBaiHoc =
                       tvbh.MaBaiHoc
                WHERE bh.MaKhoaHoc = ?;
                """,
                COURSE_ID,
            )

            hsk4_links = int(
                cursor.fetchone()[0]
            )

            print(
                "BaiHoc HSK4:",
                hsk4_lessons,
            )

            print(
                "TuVungBaiHoc HSK4:",
                hsk4_links,
            )

            if (
                hsk4_lessons != 0
                or
                hsk4_links != 0
            ):

                raise RuntimeError(
                    "HSK4 da co BaiHoc/link "
                    "ngoai ke hoach."
                )

            # ==================================================
            # 7. REGRESSION HSK1-3
            # ==================================================

            print(
                "\n[6] KIEM TRA HSK1-HSK3"
            )

            cursor.execute(
                """
                SELECT
                    bh.MaKhoaHoc,
                    COUNT(
                        DISTINCT
                        tvbh.MaTuVung
                    ) AS SoTu
                FROM dbo.BaiHoc AS bh
                INNER JOIN dbo.TuVungBaiHoc AS tvbh
                    ON tvbh.MaBaiHoc =
                       bh.MaBaiHoc
                WHERE bh.MaKhoaHoc
                    IN (1, 2, 3)
                GROUP BY
                    bh.MaKhoaHoc
                ORDER BY
                    bh.MaKhoaHoc;
                """
            )

            old_counts = {
                int(row[0]):
                    int(row[1])
                for row
                in cursor.fetchall()
            }

            for course_id, expected in (
                EXPECTED_OLD_LINKS.items()
            ):

                actual = (
                    old_counts.get(
                        course_id,
                        0,
                    )
                )

                print(
                    f"HSK{course_id}: "
                    f"{actual}"
                )

                if actual != expected:

                    raise RuntimeError(
                        f"HSK{course_id} "
                        f"da thay doi: "
                        f"{actual} "
                        f"(mong doi {expected})."
                    )

            print(
                "PASS: HSK1-HSK3 "
                "khong bi anh huong."
            )

            # SELECT only
            connection.rollback()

    # ======================================================
    # 8. REPORT
    # ======================================================

    report = {
        "status":
            "PASS",

        "hsk_level":
            4,

        "mapping_total":
            len(mapping),

        "reuse":
            len(reuse_rows),

        "inserted":
            len(insert_rows),

        "sql_tuvung_total":
            sql_total,

        "new_rows_da_duyet_0":
            EXPECTED_INSERT,

        "new_vocab_lesson_links":
            inserted_links,

        "hsk4_lessons":
            hsk4_lessons,

        "hsk4_vocab_links":
            hsk4_links,

        "old_course_vocab_counts":
            old_counts,
    }

    if REPORT_FILE.exists():

        raise FileExistsError(
            "Da ton tai report:\n"
            + str(REPORT_FILE)
        )

    REPORT_FILE.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # 9. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 76
    )

    print(
        "KIEM TRA HAU COMMIT HSK4: PASS"
    )

    print("=" * 76)

    print(
        "Mapping:",
        len(mapping),
        "/ 1000",
    )

    print(
        "Tai su dung:",
        len(reuse_rows),
        "/ 12",
    )

    print(
        "Tu moi:",
        len(insert_rows),
        "/ 988",
    )

    print(
        "dbo.TuVung:",
        sql_total,
    )

    print(
        "HSK4 BaiHoc:",
        hsk4_lessons,
    )

    print(
        "HSK4 TuVungBaiHoc:",
        hsk4_links,
    )

    print(
        "HSK1/2/3:",
        old_counts,
    )

    print(
        "\nBao cao:"
    )

    print(
        " ",
        REPORT_FILE,
    )

    print(
        "\nKHONG THAY DOI SQL."
    )

    print("=" * 76)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)