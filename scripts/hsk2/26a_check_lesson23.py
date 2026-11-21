
"""
BUOC 26A - KIEM TRA TU VUNG HSK2 BAI 23
Chi doc SQL, khong thay doi du lieu.
"""

import sys
from pathlib import Path
from contextlib import closing
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

# Tai su dung bo loc cua script 26
from importlib.util import spec_from_file_location, module_from_spec

script_path = (
    ROOT / "scripts" / "hsk2"
    / "26_generate_import_exercises_hsk2.py"
)

spec = spec_from_file_location("step26", script_path)
step26 = module_from_spec(spec)
spec.loader.exec_module(step26)


def main():
    print("=" * 65)
    print("BUOC 26A - KIEM TRA HSK2 BAI 23")
    print("=" * 65)

    with closing(get_connection()) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute("""
                SELECT MaBaiHoc, TieuDe
                FROM dbo.BaiHoc
                WHERE MaKhoaHoc = 2
                  AND SoThuTuBai = 23
            """)

            lesson = cur.fetchone()

            if lesson is None:
                raise ValueError("Khong tim thay bai 23")

            lesson_id = lesson[0]

            vocabulary = step26.load_vocabulary(
                cur, lesson_id
            )

        conn.rollback()

    accepted = []
    rejected = []
    meanings = defaultdict(list)

    for word in vocabulary:
        meaning = step26.clean_meaning(
            word["NghiaTiengViet"]
        )

        if (
            not meaning
            or not word["ChuHan"]
            or not word["PhienAm"]
        ):
            rejected.append(word)
            continue

        accepted.append(word)

        meanings[
            step26.normalize(meaning)
        ].append(word["ChuHan"])

    print("Ten bai:", lesson[1])
    print("MaBaiHoc:", lesson_id)
    print("Tong tu:", len(vocabulary))
    print("Tu duoc chap nhan:", len(accepted))
    print("Tu bi loai:", len(rejected))
    print("So nghia khac nhau:", len(meanings))

    print("\nCAC TU BI LOAI:")
    for word in rejected:
        print(
            word["ChuHan"],
            "|",
            word["NghiaTiengViet"]
        )

    print("\nCAC NHOM NGHIA TRUNG:")
    for meaning, words in meanings.items():
        if len(words) > 1:
            print(
                meaning,
                "=>",
                ", ".join(words)
            )

    print("\nHOAN TAT - KHONG GHI SQL")


if __name__ == "__main__":
    main()
