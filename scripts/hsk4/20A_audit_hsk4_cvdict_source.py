# -*- coding: utf-8 -*-

"""
BUOC 20A - AUDIT NGUON CVDICT THUC TE CUA PROJECT

Muc dich:
1. Khoa output Buoc 20.
2. Kiem tra dbo.MucTuDien thuc te dang chua MaNguon nao.
3. Kiem tra MaNguon=1003 co record MucTuDien hay khong.
4. Tim file CVDICT tren data_sources.
5. Doc script HSK3:
   23_rebuild_hsk3_hanzi_from_cvdict.py
   de xem HSK3 da lay CVDICT bang cach nao.
6. Doc report CVDICT HSK3 neu con.
7. KHONG thay doi SQL.
"""

import hashlib
import json
import re
import sys

from contextlib import closing
from pathlib import Path


# ==========================================================
# 1. CONFIG
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(ROOT),
)

from database import get_connection


H4_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)


STEP20_FILE = (
    H4_DIR
    / "hanzi_hsk4_300_pinyin_meaning_draft.csv"
)


EXPECTED_STEP20_SHA256 = (
    "337f86d394a1fa5986439c1b4493bdd0153088414487bbd2231b89a89b6dadfb"
)


HSK3_SCRIPT = (
    ROOT
    / "scripts"
    / "hsk3"
    / "23_rebuild_hsk3_hanzi_from_cvdict.py"
)


HSK3_REPORT = (
    ROOT
    / "scripts"
    / "hsk3"
    / "data"
    / "processed"
    / "hanzi_hsk3_cvdict_report.json"
)


HSK3_REBUILT = (
    ROOT
    / "scripts"
    / "hsk3"
    / "data"
    / "processed"
    / "hanzi_hsk3_cvdict_rebuilt.csv"
)


HSK3_REVIEW = (
    ROOT
    / "scripts"
    / "hsk3"
    / "data"
    / "processed"
    / "hanzi_hsk3_cvdict_review.csv"
)


DATA_SOURCES = (
    ROOT
    / "data_sources"
)


OUTPUT_REPORT = (
    H4_DIR
    / "hsk4_cvdict_source_audit.json"
)


# ==========================================================
# 2. HELPERS
# ==========================================================

def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open("rb") as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def fetch_all(
    cursor,
    sql,
    *params,
):

    cursor.execute(
        sql,
        *params,
    )

    columns = [
        item[0]
        for item in cursor.description
    ]

    return [
        dict(
            zip(
                columns,
                row,
            )
        )
        for row in cursor.fetchall()
    ]


def count_csv_rows(path):

    if not path.is_file():
        return None

    count = 0

    with path.open(
        "r",
        encoding="utf-8-sig",
        errors="replace",
    ) as file:

        # tru header
        for _ in file:
            count += 1

    return max(
        count - 1,
        0,
    )


# ==========================================================
# 3. DOC CAC DONG QUAN TRONG CUA SCRIPT HSK3
# ==========================================================

def inspect_hsk3_script(path):

    if not path.is_file():

        return {
            "exists": False,
            "matches": [],
        }

    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lines = text.splitlines()

    patterns = [
        r"cvdict",
        r"data_sources",
        r"source",
        r"dictionary",
        r"\.json",
        r"\.csv",
        r"\.txt",
        r"nghiatiengviet",
        r"nghiagoc",
        r"phienam",
    ]

    regex = re.compile(
        "|".join(patterns),
        re.IGNORECASE,
    )

    selected_indexes = set()

    for index, line in enumerate(lines):

        if regex.search(line):

            # Lay context +/- 2 dong.
            for offset in range(
                max(
                    0,
                    index - 2,
                ),
                min(
                    len(lines),
                    index + 3,
                ),
            ):

                selected_indexes.add(
                    offset
                )

    matches = []

    previous = None

    for index in sorted(
        selected_indexes
    ):

        if (
            previous is not None
            and index > previous + 1
        ):

            matches.append(
                "..."
            )

        matches.append(
            f"{index + 1:04d}: "
            f"{lines[index]}"
        )

        previous = index

    return {
        "exists": True,
        "matches": matches,
    }


# ==========================================================
# 4. TIM FILE CVDICT
# ==========================================================

def find_cvdict_candidates():

    result = []

    if not DATA_SOURCES.exists():
        return result

    useful_extensions = {
        ".txt",
        ".csv",
        ".json",
        ".jsonl",
        ".tsv",
        ".xml",
        ".db",
        ".sqlite",
        ".sqlite3",
    }

    for path in DATA_SOURCES.rglob("*"):

        if not path.is_file():
            continue

        full_text = str(
            path
        ).lower()

        # Uu tien file/thu muc co ten CVDICT.
        if (
            "cvdict" not in full_text
            and "chinese-vietnamese"
            not in full_text
            and "chinese_vietnamese"
            not in full_text
        ):
            continue

        if (
            path.suffix.lower()
            not in useful_extensions
        ):
            continue

        try:

            size = path.stat().st_size

        except OSError:

            size = None

        result.append({
            "path": str(path),
            "suffix": path.suffix.lower(),
            "size_bytes": size,
        })

    result.sort(
        key=lambda row:
        row[
            "path"
        ].lower()
    )

    return result


# ==========================================================
# 5. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 20A - AUDIT NGUON CVDICT THUC TE"
    )

    print("=" * 80)

    print(
        "CHI DOC FILE + SELECT SQL"
    )

    print(
        "KHONG INSERT / UPDATE / DELETE"
    )

    # ======================================================
    # [1] LOCK BUOC 20
    # ======================================================

    print(
        "\n[1] KIEM TRA OUTPUT BUOC 20"
    )

    if not STEP20_FILE.is_file():

        raise FileNotFoundError(
            STEP20_FILE
        )

    step20_hash = (
        sha256_file(
            STEP20_FILE
        )
    )

    print(
        "SHA256:"
    )

    print(
        step20_hash
    )

    if (
        step20_hash
        != EXPECTED_STEP20_SHA256
    ):

        raise RuntimeError(
            "Output Buoc 20 da thay doi."
        )

    print(
        "PASS: output Buoc 20 dung snapshot."
    )

    # ======================================================
    # [2] SQL MucTuDien
    # ======================================================

    print(
        "\n[2] KIEM TRA dbo.MucTuDien THEO MaNguon"
    )

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:

            source_rows = fetch_all(
                cursor,
                """
                SELECT
                    nd.MaNguon,
                    nd.Ten,

                    COUNT(mtd.MaMucTu)
                        AS TongMucTu,

                    SUM(
                        CASE
                            WHEN mtd.NghiaTiengViet
                                 IS NOT NULL
                             AND LTRIM(RTRIM(
                                 mtd.NghiaTiengViet
                             )) <> N''
                            THEN 1
                            ELSE 0
                        END
                    )
                        AS CoNghiaTiengViet

                FROM dbo.NguonDuLieu nd

                LEFT JOIN dbo.MucTuDien mtd
                    ON mtd.MaNguon
                     = nd.MaNguon

                GROUP BY
                    nd.MaNguon,
                    nd.Ten

                ORDER BY
                    nd.MaNguon
                """
            )

            for row in source_rows:

                print(
                    f"{row['MaNguon']}: "
                    f"{row['Ten']} | "
                    f"MucTu={row['TongMucTu']} | "
                    f"CoNghiaViet="
                    f"{row['CoNghiaTiengViet']}"
                )

            cvdict_sql = fetch_all(
                cursor,
                """
                SELECT
                    COUNT(*) AS Tong,
                    SUM(
                        CASE
                            WHEN NghiaTiengViet
                                 IS NOT NULL
                             AND LTRIM(RTRIM(
                                 NghiaTiengViet
                             )) <> N''
                            THEN 1
                            ELSE 0
                        END
                    ) AS CoNghiaViet

                FROM dbo.MucTuDien

                WHERE MaNguon = 1003
                """
            )[0]

    print(
        "\nMaNguon=1003:"
    )

    print(
        "  Tong MucTuDien:",
        cvdict_sql[
            "Tong"
        ],
    )

    print(
        "  Co NghiaTiengViet:",
        cvdict_sql[
            "CoNghiaViet"
        ]
        or 0,
    )

    # ======================================================
    # [3] HSK3 OLD PIPELINE
    # ======================================================

    print(
        "\n[3] KIEM TRA PIPELINE CVDICT HSK3"
    )

    print(
        "Script:"
    )

    print(
        " ",
        HSK3_SCRIPT
    )

    print(
        "Ton tai:",
        HSK3_SCRIPT.is_file(),
    )

    print(
        "HSK3 rebuilt:"
    )

    print(
        " ",
        HSK3_REBUILT
    )

    print(
        "Rows:",
        count_csv_rows(
            HSK3_REBUILT
        ),
    )

    print(
        "HSK3 review:"
    )

    print(
        " ",
        HSK3_REVIEW
    )

    print(
        "Rows:",
        count_csv_rows(
            HSK3_REVIEW
        ),
    )

    script_info = (
        inspect_hsk3_script(
            HSK3_SCRIPT
        )
    )

    print(
        "\n--- CAC DONG QUAN TRONG "
        "TRONG SCRIPT HSK3 ---"
    )

    if not script_info[
        "exists"
    ]:

        print(
            "KHONG TIM THAY SCRIPT HSK3."
        )

    else:

        for line in script_info[
            "matches"
        ]:

            print(
                line
            )

    # ======================================================
    # [4] REPORT HSK3
    # ======================================================

    print(
        "\n[4] DOC REPORT CVDICT HSK3"
    )

    hsk3_report_data = None

    if HSK3_REPORT.is_file():

        try:

            hsk3_report_data = (
                json.loads(
                    HSK3_REPORT.read_text(
                        encoding="utf-8"
                    )
                )
            )

            print(
                json.dumps(
                    hsk3_report_data,
                    ensure_ascii=False,
                    indent=2,
                )
            )

        except Exception as error:

            print(
                "Khong parse duoc report:"
            )

            print(
                error
            )

    else:

        print(
            "Khong tim thay report."
        )

    # ======================================================
    # [5] TIM SOURCE CVDICT
    # ======================================================

    print(
        "\n[5] TIM FILE CVDICT TRONG data_sources"
    )

    candidates = (
        find_cvdict_candidates()
    )

    print(
        "Tong candidate:",
        len(
            candidates
        ),
    )

    for row in candidates:

        print(
            row[
                "path"
            ],
            "|",
            row[
                "suffix"
            ],
            "| bytes=",
            row[
                "size_bytes"
            ],
        )

    # ======================================================
    # [6] GHI REPORT
    # ======================================================

    print(
        "\n[6] GHI REPORT"
    )

    report = {

        "status":
            "PASS_AUDIT",

        "step20_sha256":
            step20_hash,

        "sql_sources":
            source_rows,

        "muctudien_maNguon_1003":
            cvdict_sql,

        "hsk3_script":
            str(
                HSK3_SCRIPT
            ),

        "hsk3_script_exists":
            HSK3_SCRIPT.is_file(),

        "hsk3_script_relevant_lines":
            script_info[
                "matches"
            ],

        "hsk3_rebuilt":
            str(
                HSK3_REBUILT
            ),

        "hsk3_rebuilt_rows":
            count_csv_rows(
                HSK3_REBUILT
            ),

        "hsk3_review":
            str(
                HSK3_REVIEW
            ),

        "hsk3_review_rows":
            count_csv_rows(
                HSK3_REVIEW
            ),

        "hsk3_report":
            hsk3_report_data,

        "cvdict_candidates":
            candidates,

        "sql_changed":
            False,
    }

    H4_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT_REPORT.exists():

        raise FileExistsError(
            f"Report da ton tai:\n"
            f"{OUTPUT_REPORT}"
        )

    OUTPUT_REPORT.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # FINAL
    # ======================================================

    print(
        "\n"
        + "=" * 80
    )

    print(
        "AUDIT CVDICT HOAN THANH"
    )

    print(
        "=" * 80
    )

    print(
        "MucTuDien MaNguon=1003:",
        cvdict_sql[
            "Tong"
        ],
    )

    print(
        "HSK3 rebuilt rows:",
        count_csv_rows(
            HSK3_REBUILT
        ),
    )

    print(
        "HSK3 review rows:",
        count_csv_rows(
            HSK3_REVIEW
        ),
    )

    print(
        "CVDICT file candidates:",
        len(
            candidates
        ),
    )

    print(
        "\nREPORT:"
    )

    print(
        " ",
        OUTPUT_REPORT
    )

    print(
        "\nKHONG THAY DOI SQL."
    )

    print("=" * 80)


if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print(
            "\nLOI:"
        )

        print(
            error
        )

        raise SystemExit(1)