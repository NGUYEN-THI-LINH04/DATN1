# -*- coding: utf-8 -*-

"""
BUOC 25B - COMMIT CHINH THUC HSK4 VAO SQL SERVER

Ghi:
- 20 BaiHoc
- 1000 TuVungBaiHoc
- 114 NguPhap
- 300 ChuHan

AN TOAN:
- Kiem tra SHA256.
- Chi chay khi HSK4 chua co BaiHoc.
- Validate toan bo truoc COMMIT.
- Yeu cau xac nhan bang ban phim.
- Loi truoc COMMIT => ROLLBACK.
- KhoaHoc HSK4 van giu TrangThai = ban_nhap.
- KHONG TAO AUDIO.
"""

import csv
import hashlib
import sys
import unicodedata
from collections import defaultdict, Counter
from pathlib import Path


# ============================================================
# PROJECT
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection


BASE = ROOT / "scripts" / "hsk4" / "data" / "processed"

LESSONS = BASE / "lessons_hsk4_draft_20_21B.csv"
VOCAB = BASE / "vocabulary_hsk4_by_lesson_draft_21B.csv"
GRAMMAR = BASE / "grammar_hsk4_by_lesson_draft_22A.csv"
HANZI = BASE / "hanzi_hsk4_by_lesson_draft_23.csv"


EXPECTED = {
    LESSONS: (
        "32fb32a40a5aa8b60fd64556734e8a0be9b9a6902be865bf5cd5c11a244aa3ab"
    ),
    VOCAB: (
        "79716ce75ee23b869626a546017d5e744a6b0e40d8b214dace8851c009cdc1f2"
    ),
    GRAMMAR: (
        "9e71c5f903c88979c4169ec6a26f21dfbc6cb46b082dd18cb57381d21828a20d"
    ),
    HANZI: (
        "0aa6b58aee5ddd42adb67bdc3279727c5ec6d0f222eee67a3f06943039422fb9"
    ),
}


MA_KHOA_HOC = 4
EXPECTED_COURSE_CODE = "HSK4-CORE"


# ============================================================
# HELPERS
# ============================================================

def sha256(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def read_csv(path):
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.DictReader(f)

        return (
            list(reader.fieldnames or []),
            list(reader),
        )


def text(value):
    if value is None:
        return None

    value = str(value).strip()

    return value if value else None


def norm(value):
    if value is None:
        return ""

    return unicodedata.normalize(
        "NFC",
        str(value).strip()
    )


def as_int(value, name):
    try:
        return int(str(value).strip())
    except Exception:
        raise RuntimeError(
            f"FAIL: {name} khong phai so nguyen: {value!r}"
        )


def first_value(row, names, default=None):
    for name in names:
        if name in row:
            value = text(row.get(name))

            if value is not None:
                return value

    return default


def query_scalar(cursor, sql, params=()):
    cursor.execute(sql, params)

    row = cursor.fetchone()

    if row is None:
        return None

    return row[0]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 94)
    print("BUOC 25B - COMMIT CHINH THUC 20 BAI HSK4 VAO SQL")
    print("CO GHI DU LIEU THAT - KHONG TAO AUDIO")
    print("=" * 94)

    # ========================================================
    # 1. SNAPSHOT FILE
    # ========================================================

    print("\n[1] KIEM TRA 4 SNAPSHOT")

    for path, expected_hash in EXPECTED.items():

        if not path.is_file():
            raise FileNotFoundError(path)

        actual = sha256(path)

        print(path.name)
        print("  SHA256:", actual)

        if actual != expected_hash:
            raise RuntimeError(
                "FAIL: SHA256 khong khop: "
                + path.name
            )

    print("PASS: 4 snapshot hop le.")

    # ========================================================
    # 2. DOC CSV
    # ========================================================

    print("\n[2] DOC DU LIEU")

    _, lessons = read_csv(LESSONS)
    _, vocab = read_csv(VOCAB)
    _, grammar = read_csv(GRAMMAR)
    _, hanzi = read_csv(HANZI)

    if len(lessons) != 20:
        raise RuntimeError(
            f"FAIL: lessons = {len(lessons)}, can 20."
        )

    if len(vocab) != 1000:
        raise RuntimeError(
            f"FAIL: vocab = {len(vocab)}, can 1000."
        )

    if len(grammar) != 114:
        raise RuntimeError(
            f"FAIL: grammar = {len(grammar)}, can 114."
        )

    if len(hanzi) != 300:
        raise RuntimeError(
            f"FAIL: Hanzi = {len(hanzi)}, can 300."
        )

    print("PASS: 20 / 1000 / 114 / 300.")

    # ========================================================
    # 3. EXPECTED COUNTS PER LESSON
    # ========================================================

    print("\n[3] LAP THONG KE KY VONG THEO BAI")

    expected_vocab = Counter()
    expected_grammar = Counter()
    expected_hanzi = Counter()

    for row in vocab:
        n = as_int(
            row["SoThuTuBai"],
            "vocab.SoThuTuBai"
        )
        expected_vocab[n] += 1

    for row in grammar:
        n = as_int(
            row["SoThuTuBai"],
            "grammar.SoThuTuBai"
        )
        expected_grammar[n] += 1

    for row in hanzi:
        n = as_int(
            row["SoThuTuBai"],
            "hanzi.SoThuTuBai"
        )
        expected_hanzi[n] += 1

    for n in range(1, 21):

        if expected_vocab[n] <= 0:
            raise RuntimeError(
                f"FAIL: bai {n:02d} khong co vocab."
            )

        if expected_grammar[n] <= 0:
            raise RuntimeError(
                f"FAIL: bai {n:02d} khong co grammar."
            )

        if expected_hanzi[n] <= 0:
            raise RuntimeError(
                f"FAIL: bai {n:02d} khong co Hanzi."
            )

    print("PASS: 20/20 bai co du 3 thanh phan.")

    # ========================================================
    # 4. CONNECT DATABASE
    # ========================================================

    print("\n[4] KET NOI SQL SERVER")

    conn = get_connection()

    if conn is None:
        raise RuntimeError(
            "FAIL: get_connection() tra ve None."
        )

    cursor = conn.cursor()

    try:
        conn.autocommit = False
    except Exception:
        pass

    committed = False

    print("PASS: da ket noi database.")

    try:

        # ====================================================
        # 5. COURSE
        # ====================================================

        print("\n[5] KIEM TRA KHOA HOC HSK4")

        cursor.execute(
            """
            SELECT
                MaKhoaHoc,
                MaCapDo,
                MaKyHieu,
                TrangThai
            FROM dbo.KhoaHoc
            WHERE MaKhoaHoc = ?
            """,
            MA_KHOA_HOC,
        )

        rows = cursor.fetchall()

        if len(rows) != 1:
            raise RuntimeError(
                "FAIL: khong tim thay dung 1 khoa HSK4."
            )

        course = rows[0]

        print("MaKhoaHoc :", course[0])
        print("MaCapDo   :", course[1])
        print("MaKyHieu  :", course[2])
        print("TrangThai :", course[3])

        if int(course[1]) != 4:
            raise RuntimeError(
                "FAIL: MaCapDo != 4."
            )

        if norm(course[2]) != EXPECTED_COURSE_CODE:
            raise RuntimeError(
                "FAIL: MaKyHieu != HSK4-CORE."
            )

        if norm(course[3]) != "ban_nhap":
            raise RuntimeError(
                "FAIL: HSK4 khong o trang thai ban_nhap."
            )

        print("PASS: KhoaHoc HSK4 hop le.")

        # ====================================================
        # 6. PRE-COMMIT DATABASE STATE
        # ====================================================

        print("\n[6] KIEM TRA SQL TRUOC KHI INSERT")

        before_lessons = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        before_links = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc tvbh
            JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc = tvbh.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        before_grammar = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.NguPhap np
            JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc = np.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        before_hanzi = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.ChuHan ch
            JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc = ch.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        print("BaiHoc HSK4       :", before_lessons)
        print("TuVungBaiHoc HSK4 :", before_links)
        print("NguPhap HSK4      :", before_grammar)
        print("ChuHan HSK4       :", before_hanzi)

        if (
            before_lessons != 0
            or before_links != 0
            or before_grammar != 0
            or before_hanzi != 0
        ):
            raise RuntimeError(
                "FAIL: HSK4 da co noi dung trong SQL. "
                "DUNG LAI de tranh INSERT trung."
            )

        print("PASS: HSK4 chua co noi dung bai hoc.")

        # ====================================================
        # 7. STANDARD VOCAB
        # ====================================================

        print("\n[7] KIEM TRA 1000 TuVungHSKChuan")

        cursor.execute(
            """
            SELECT
                MaTuHSK,
                MaMucNoiBo,
                ChuHan,
                PhienAm,
                TuLoai
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = 4
            """
        )

        standard_rows = cursor.fetchall()

        if len(standard_rows) != 1000:
            raise RuntimeError(
                "FAIL: TuVungHSKChuan HSK4 "
                f"co {len(standard_rows)}, can 1000."
            )

        by_ma_tu_hsk = {
            int(r[0]): r
            for r in standard_rows
        }

        if len(by_ma_tu_hsk) != 1000:
            raise RuntimeError(
                "FAIL: trung MaTuHSK."
            )

        for row in vocab:

            ma_tu_hsk = as_int(
                row["MaTuHSK"],
                "MaTuHSK"
            )

            sql_row = by_ma_tu_hsk.get(
                ma_tu_hsk
            )

            if sql_row is None:
                raise RuntimeError(
                    f"FAIL: thieu MaTuHSK={ma_tu_hsk}."
                )

            if norm(sql_row[1]) != norm(row["MaMucNoiBo"]):
                raise RuntimeError(
                    f"FAIL: MaMucNoiBo sai tai {ma_tu_hsk}."
                )

            if norm(sql_row[2]) != norm(row["ChuHan"]):
                raise RuntimeError(
                    f"FAIL: ChuHan sai tai {ma_tu_hsk}."
                )

            if norm(sql_row[3]) != norm(row["PhienAm"]):
                raise RuntimeError(
                    f"FAIL: PhienAm sai tai {ma_tu_hsk}."
                )

            if norm(sql_row[4]) != norm(row["TuLoai"]):
                raise RuntimeError(
                    f"FAIL: TuLoai sai tai {ma_tu_hsk}."
                )

        print(
            "PASS: 1000/1000 CSV khop TuVungHSKChuan."
        )

        # ====================================================
        # 8. MAP dbo.TuVung
        # ====================================================

        print("\n[8] ANH XA 1000 TU -> dbo.TuVung")

        cursor.execute(
            """
            SELECT
                MaTuVung,
                ChuHan,
                PhienAm,
                NghiaTiengViet,
                TuLoai
            FROM dbo.TuVung
            """
        )

        sql_vocab_rows = cursor.fetchall()

        exact_pos_index = defaultdict(list)
        exact_index = defaultdict(list)
        hp_index = defaultdict(list)

        sql_vocab_by_id = {}

        for r in sql_vocab_rows:

            ma_tu_vung = int(r[0])

            sql_vocab_by_id[ma_tu_vung] = r

            chu_han = norm(r[1])
            pinyin = norm(r[2])
            meaning = norm(r[3])
            pos = norm(r[4])

            exact_pos_index[
                (
                    chu_han,
                    pinyin,
                    meaning,
                    pos,
                )
            ].append(ma_tu_vung)

            exact_index[
                (
                    chu_han,
                    pinyin,
                    meaning,
                )
            ].append(ma_tu_vung)

            hp_index[
                (
                    chu_han,
                    pinyin,
                )
            ].append(ma_tu_vung)

        vocab_to_sql = {}

        mapping_method = Counter()

        ambiguous = []
        missing = []

        for row in vocab:

            source_id = row["MaMucNoiBo"]

            chu_han = norm(row["ChuHan"])
            pinyin = norm(row["PhienAm"])
            meaning = norm(row["NghiaTiengViet"])
            pos = norm(row["TuLoai"])

            # ---------------------------------------------
            # 1. Hanzi + Pinyin + Nghia + TuLoai
            # ---------------------------------------------

            candidates = exact_pos_index.get(
                (
                    chu_han,
                    pinyin,
                    meaning,
                    pos,
                ),
                [],
            )

            if len(candidates) == 1:

                vocab_to_sql[source_id] = candidates[0]

                mapping_method[
                    "HANZI_PINYIN_NGHIA_TULOAI"
                ] += 1

                continue

            if len(candidates) > 1:

                ambiguous.append(
                    (
                        source_id,
                        row["ChuHan"],
                        row["PhienAm"],
                        row["TuLoai"],
                        "EXACT_POS_DUPLICATE",
                        candidates,
                    )
                )

                continue

            # ---------------------------------------------
            # 2. Hanzi + Pinyin + Nghia
            # ---------------------------------------------

            candidates = exact_index.get(
                (
                    chu_han,
                    pinyin,
                    meaning,
                ),
                [],
            )

            if len(candidates) == 1:

                vocab_to_sql[source_id] = candidates[0]

                mapping_method[
                    "HANZI_PINYIN_NGHIA"
                ] += 1

                continue

            if len(candidates) > 1:

                filtered = [
                    ma
                    for ma in candidates
                    if norm(
                        sql_vocab_by_id[ma][4]
                    ) == pos
                ]

                if len(filtered) == 1:

                    vocab_to_sql[source_id] = filtered[0]

                    mapping_method[
                        "EXACT_DUPLICATE_RESOLVED_BY_TULOAI"
                    ] += 1

                    continue

                ambiguous.append(
                    (
                        source_id,
                        row["ChuHan"],
                        row["PhienAm"],
                        row["TuLoai"],
                        "EXACT_DUPLICATE",
                        candidates,
                    )
                )

                continue

            # ---------------------------------------------
            # 3. Hanzi + Pinyin
            # ---------------------------------------------

            candidates = hp_index.get(
                (
                    chu_han,
                    pinyin,
                ),
                [],
            )

            if len(candidates) == 1:

                vocab_to_sql[source_id] = candidates[0]

                mapping_method[
                    "HANZI_PINYIN_UNIQUE"
                ] += 1

                continue

            if len(candidates) > 1:

                filtered = [
                    ma
                    for ma in candidates
                    if norm(
                        sql_vocab_by_id[ma][4]
                    ) == pos
                ]

                if len(filtered) == 1:

                    vocab_to_sql[source_id] = filtered[0]

                    mapping_method[
                        "HANZI_PINYIN_RESOLVED_BY_TULOAI"
                    ] += 1

                    continue

                ambiguous.append(
                    (
                        source_id,
                        row["ChuHan"],
                        row["PhienAm"],
                        row["TuLoai"],
                        "HANZI_PINYIN_AMBIGUOUS",
                        candidates,
                    )
                )

                continue

            missing.append(
                (
                    source_id,
                    row["ChuHan"],
                    row["PhienAm"],
                    row["TuLoai"],
                )
            )

        print(
            "Anh xa thanh cong:",
            len(vocab_to_sql)
        )

        print(
            "  Hanzi+Pinyin+Nghia+TuLoai:",
            mapping_method[
                "HANZI_PINYIN_NGHIA_TULOAI"
            ],
        )

        print(
            "  Exact duplicate -> TuLoai:",
            mapping_method[
                "EXACT_DUPLICATE_RESOLVED_BY_TULOAI"
            ],
        )

        print(
            "  Hanzi+Pinyin+Nghia:",
            mapping_method[
                "HANZI_PINYIN_NGHIA"
            ],
        )

        print(
            "  Hanzi+Pinyin -> TuLoai:",
            mapping_method[
                "HANZI_PINYIN_RESOLVED_BY_TULOAI"
            ],
        )

        print(
            "  Hanzi+Pinyin unique:",
            mapping_method[
                "HANZI_PINYIN_UNIQUE"
            ],
        )

        print("  Missing:", len(missing))
        print("  Ambiguous:", len(ambiguous))

        if missing:
            print("\nMissing:")
            for item in missing[:10]:
                print(" ", item)

        if ambiguous:
            print("\nAmbiguous:")
            for item in ambiguous[:10]:
                print(" ", item)

        if (
            len(vocab_to_sql) != 1000
            or missing
            or ambiguous
        ):
            raise RuntimeError(
                "FAIL: mapping TuVung khong an toan."
            )

        # Kiem tra rieng cap 批 da xac minh o Step25A.
        if vocab_to_sql.get("L4-0555") != 3048:
            raise RuntimeError(
                "FAIL: L4-0555 phai map MaTuVung=3048."
            )

        if vocab_to_sql.get("L4-0556") != 3049:
            raise RuntimeError(
                "FAIL: L4-0556 phai map MaTuVung=3049."
            )

        print("PASS: 1000/1000 tu anh xa an toan.")
        print("PASS: L4-0555 -> MaTuVung 3048 (动).")
        print("PASS: L4-0556 -> MaTuVung 3049 (量).")

        # ====================================================
        # 9. INSERT BAIHOC
        # ====================================================

        print("\n[9] INSERT 20 BaiHoc TRONG TRANSACTION")

        lesson_ids = {}

        for row in sorted(
            lessons,
            key=lambda r: int(r["SoThuTuBai"])
        ):

            lesson_no = as_int(
                row["SoThuTuBai"],
                "lesson.SoThuTuBai"
            )

            title = text(row["TieuDe"])

            summary = first_value(
                row,
                [
                    "TomTat",
                    "MoTa",
                ],
                default=None,
            )

            status = first_value(
                row,
                ["TrangThai"],
                default="ban_nhap",
            )

            if status != "ban_nhap":
                raise RuntimeError(
                    f"FAIL: Bai {lesson_no:02d} "
                    "khong o ban_nhap."
                )

            cursor.execute(
                """
                INSERT INTO dbo.BaiHoc
                (
                    MaKhoaHoc,
                    SoThuTuBai,
                    TieuDe,
                    TomTat,
                    TrangThai
                )
                OUTPUT INSERTED.MaBaiHoc
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    MA_KHOA_HOC,
                    lesson_no,
                    title,
                    summary,
                    "ban_nhap",
                ),
            )

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError(
                    f"FAIL: khong lay duoc MaBaiHoc "
                    f"cho bai {lesson_no:02d}."
                )

            lesson_ids[lesson_no] = int(
                result[0]
            )

        if len(lesson_ids) != 20:
            raise RuntimeError(
                "FAIL: khong INSERT du 20 BaiHoc."
            )

        print("PASS: INSERT 20 BaiHoc.")

        # ====================================================
        # 10. INSERT LINKS
        # ====================================================

        print("\n[10] INSERT 1000 TuVungBaiHoc")

        link_pairs = set()

        for row in vocab:

            lesson_no = as_int(
                row["SoThuTuBai"],
                "vocab.SoThuTuBai"
            )

            order_no = as_int(
                row["ThuTuTrongBai"],
                "vocab.ThuTuTrongBai"
            )

            ma_bai_hoc = lesson_ids[
                lesson_no
            ]

            ma_tu_vung = vocab_to_sql[
                row["MaMucNoiBo"]
            ]

            pair = (
                ma_bai_hoc,
                ma_tu_vung,
            )

            if pair in link_pairs:
                raise RuntimeError(
                    "FAIL: trung TuVungBaiHoc: "
                    + str(pair)
                )

            link_pairs.add(pair)

            cursor.execute(
                """
                INSERT INTO dbo.TuVungBaiHoc
                (
                    MaBaiHoc,
                    MaTuVung,
                    ThuTu
                )
                VALUES (?, ?, ?)
                """,
                (
                    ma_bai_hoc,
                    ma_tu_vung,
                    order_no,
                ),
            )

        if len(link_pairs) != 1000:
            raise RuntimeError(
                "FAIL: khong INSERT du 1000 link."
            )

        print("PASS: INSERT 1000 TuVungBaiHoc.")

        # ====================================================
        # 11. INSERT GRAMMAR
        # ====================================================

        print("\n[11] INSERT 114 NguPhap")

        grammar_count = 0

        for row in grammar:

            lesson_no = as_int(
                row["SoThuTuBai"],
                "grammar.SoThuTuBai"
            )

            order_no = as_int(
                row["ThuTuTrongBai"],
                "grammar.ThuTuTrongBai"
            )

            cursor.execute(
                """
                INSERT INTO dbo.NguPhap
                (
                    MaBaiHoc,
                    TenCauTruc,
                    MoTa,
                    CachDung,
                    ViDuTiengTrung,
                    ViDuPinyin,
                    ViDuTiengViet,
                    MaTep,
                    MaNguon,
                    ThuTu,
                    TrangThai
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lesson_ids[lesson_no],
                    text(row.get("TenCauTruc")),
                    text(row.get("MoTa")),
                    text(row.get("CachDung")),
                    text(row.get("ViDuTiengTrung")),
                    text(row.get("ViDuPinyin")),
                    text(row.get("ViDuTiengViet")),
                    None,
                    text(row.get("MaNguon")),
                    order_no,
                    "ban_nhap",
                ),
            )

            grammar_count += 1

        if grammar_count != 114:
            raise RuntimeError(
                "FAIL: khong INSERT du 114 NguPhap."
            )

        print("PASS: INSERT 114 NguPhap.")

        # ====================================================
        # 12. INSERT HANZI
        # ====================================================

        print("\n[12] INSERT 300 ChuHan")

        hanzi_count = 0

        for row in hanzi:

            lesson_no = as_int(
                row["SoThuTuBai"],
                "hanzi.SoThuTuBai"
            )

            order_no = as_int(
                row["ThuTuTrongBai"],
                "hanzi.ThuTuTrongBai"
            )

            ky_tu = text(
                row.get("KyTu")
            )

            pinyin = first_value(
                row,
                [
                    "PinyinChot20G",
                    "Pinyin",
                ],
            )

            meaning = first_value(
                row,
                [
                    "NghiaTiengVietChot20F",
                    "NghiaTiengViet",
                ],
            )

            ma_bo_thu = first_value(
                row,
                [
                    "MaBoThu",
                    "MaBoThuChot",
                ],
            )

            so_net_raw = first_value(
                row,
                [
                    "SoNetChot20E",
                    "SoNetChot",
                    "SoNet",
                ],
            )

            so_net = None

            if so_net_raw is not None:
                try:
                    so_net = int(so_net_raw)
                except Exception:
                    raise RuntimeError(
                        f"FAIL: SoNet khong hop le "
                        f"cho {ky_tu}: {so_net_raw!r}"
                    )

            cach_ghi_nho = first_value(
                row,
                ["CachGhiNho"],
            )

            vi_du_trung = first_value(
                row,
                ["ViDuTiengTrung"],
            )

            vi_du_pinyin = first_value(
                row,
                ["ViDuPinyin"],
            )

            vi_du_viet = first_value(
                row,
                ["ViDuTiengViet"],
            )

            ma_nguon = first_value(
                row,
                ["MaNguon"],
            )

            cursor.execute(
                """
                INSERT INTO dbo.ChuHan
                (
                    MaBaiHoc,
                    MaBoThu,
                    KyTu,
                    Pinyin,
                    NghiaTiengViet,
                    SoNet,
                    CachGhiNho,
                    ViDuTiengTrung,
                    ViDuPinyin,
                    ViDuTiengViet,
                    MaTep,
                    MaNguon,
                    ThuTu,
                    TrangThai
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lesson_ids[lesson_no],
                    ma_bo_thu,
                    ky_tu,
                    pinyin,
                    meaning,
                    so_net,
                    cach_ghi_nho,
                    vi_du_trung,
                    vi_du_pinyin,
                    vi_du_viet,
                    None,
                    ma_nguon,
                    order_no,
                    "ban_nhap",
                ),
            )

            hanzi_count += 1

        if hanzi_count != 300:
            raise RuntimeError(
                "FAIL: khong INSERT du 300 ChuHan."
            )

        print("PASS: INSERT 300 ChuHan.")

        # ====================================================
        # 13. VALIDATE BEFORE COMMIT
        # ====================================================

        print("\n[13] VALIDATE TRUOC COMMIT")

        current_lessons = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        current_links = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc tvbh
            JOIN dbo.BaiHoc bh
              ON bh.MaBaiHoc = tvbh.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        current_grammar = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.NguPhap np
            JOIN dbo.BaiHoc bh
              ON bh.MaBaiHoc = np.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        current_hanzi = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.ChuHan ch
            JOIN dbo.BaiHoc bh
              ON bh.MaBaiHoc = ch.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        print("BaiHoc       :", current_lessons)
        print("TuVungBaiHoc :", current_links)
        print("NguPhap      :", current_grammar)
        print("ChuHan       :", current_hanzi)

        if current_lessons != 20:
            raise RuntimeError(
                "FAIL: BaiHoc != 20."
            )

        if current_links != 1000:
            raise RuntimeError(
                "FAIL: TuVungBaiHoc != 1000."
            )

        if current_grammar != 114:
            raise RuntimeError(
                "FAIL: NguPhap != 114."
            )

        if current_hanzi != 300:
            raise RuntimeError(
                "FAIL: ChuHan != 300."
            )

        # ====================================================
        # 14. VALIDATE EXACT PER LESSON
        # ====================================================

        print("\n[14] KIEM TRA CHINH XAC TUNG BAI")

        cursor.execute(
            """
            SELECT
                bh.SoThuTuBai,

                (
                    SELECT COUNT(*)
                    FROM dbo.TuVungBaiHoc tvbh
                    WHERE tvbh.MaBaiHoc = bh.MaBaiHoc
                ) AS SoTuVung,

                (
                    SELECT COUNT(*)
                    FROM dbo.NguPhap np
                    WHERE np.MaBaiHoc = bh.MaBaiHoc
                ) AS SoNguPhap,

                (
                    SELECT COUNT(*)
                    FROM dbo.ChuHan ch
                    WHERE ch.MaBaiHoc = bh.MaBaiHoc
                ) AS SoChuHan

            FROM dbo.BaiHoc bh

            WHERE bh.MaKhoaHoc = ?

            ORDER BY bh.SoThuTuBai
            """,
            MA_KHOA_HOC,
        )

        per_lesson = cursor.fetchall()

        if len(per_lesson) != 20:
            raise RuntimeError(
                "FAIL: SQL khong tra ve 20 bai."
            )

        print(
            f"{'Bai':<6}"
            f"{'TuVung':>10}"
            f"{'NguPhap':>10}"
            f"{'ChuHan':>10}"
        )

        print("-" * 36)

        for r in per_lesson:

            n = int(r[0])
            v = int(r[1])
            g = int(r[2])
            h = int(r[3])

            print(
                f"{n:02d}"
                f"{v:>14}"
                f"{g:>10}"
                f"{h:>10}"
            )

            if v != expected_vocab[n]:
                raise RuntimeError(
                    f"FAIL: Bai {n:02d} vocab "
                    f"SQL={v}, expected={expected_vocab[n]}."
                )

            if g != expected_grammar[n]:
                raise RuntimeError(
                    f"FAIL: Bai {n:02d} grammar "
                    f"SQL={g}, expected={expected_grammar[n]}."
                )

            if h != expected_hanzi[n]:
                raise RuntimeError(
                    f"FAIL: Bai {n:02d} Hanzi "
                    f"SQL={h}, expected={expected_hanzi[n]}."
                )

        print()
        print(
            "PASS: 20/20 bai khop chinh xac snapshot Step24."
        )

        # ====================================================
        # 15. CHECK STATUS
        # ====================================================

        print("\n[15] KIEM TRA TRANG THAI BAN_NHAP")

        bad_lessons = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
              AND (
                    TrangThai IS NULL
                    OR TrangThai <> 'ban_nhap'
                  )
            """,
            (MA_KHOA_HOC,),
        )

        bad_grammar = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.NguPhap np
            JOIN dbo.BaiHoc bh
              ON bh.MaBaiHoc = np.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
              AND (
                    np.TrangThai IS NULL
                    OR np.TrangThai <> 'ban_nhap'
                  )
            """,
            (MA_KHOA_HOC,),
        )

        bad_hanzi = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.ChuHan ch
            JOIN dbo.BaiHoc bh
              ON bh.MaBaiHoc = ch.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
              AND (
                    ch.TrangThai IS NULL
                    OR ch.TrangThai <> 'ban_nhap'
                  )
            """,
            (MA_KHOA_HOC,),
        )

        if bad_lessons != 0:
            raise RuntimeError(
                "FAIL: co BaiHoc khong phai ban_nhap."
            )

        if bad_grammar != 0:
            raise RuntimeError(
                "FAIL: co NguPhap khong phai ban_nhap."
            )

        if bad_hanzi != 0:
            raise RuntimeError(
                "FAIL: co ChuHan khong phai ban_nhap."
            )

        course_status = query_scalar(
            cursor,
            """
            SELECT TrangThai
            FROM dbo.KhoaHoc
            WHERE MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        if norm(course_status) != "ban_nhap":
            raise RuntimeError(
                "FAIL: KhoaHoc bi doi TrangThai."
            )

        print("PASS: KhoaHoc = ban_nhap.")
        print("PASS: 20 BaiHoc = ban_nhap.")
        print("PASS: 114 NguPhap = ban_nhap.")
        print("PASS: 300 ChuHan = ban_nhap.")

        # ====================================================
        # 16. CONFIRM
        # ====================================================

        print("\n" + "=" * 94)
        print("SAN SANG COMMIT")
        print("=" * 94)

        print("Se ghi Vĩnh viễn:")
        print("  20 BaiHoc")
        print("  1000 TuVungBaiHoc")
        print("  114 NguPhap")
        print("  300 ChuHan")
        print()
        print("KhoaHoc HSK4 van giu: ban_nhap")
        print("KHONG tao audio.")
        print()

        confirm = input(
            "Nhap chinh xac COMMIT HSK4 de tiep tuc: "
        ).strip()

        if confirm != "COMMIT HSK4":

            conn.rollback()

            print()
            print("CANCEL: chuoi xac nhan khong dung.")
            print("PASS: DA ROLLBACK.")
            print("KHONG CO DU LIEU NAO DUOC COMMIT.")

            return

        # ====================================================
        # 17. COMMIT
        # ====================================================

        print("\n[17] COMMIT DATABASE")

        conn.commit()
        committed = True

        print("PASS: DA COMMIT SQL.")

        # ====================================================
        # 18. VERIFY AFTER COMMIT
        # ====================================================

        print("\n[18] KIEM TRA SAU COMMIT")

        after_lessons = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        after_links = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.TuVungBaiHoc tvbh
            JOIN dbo.BaiHoc bh
              ON bh.MaBaiHoc = tvbh.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        after_grammar = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.NguPhap np
            JOIN dbo.BaiHoc bh
              ON bh.MaBaiHoc = np.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        after_hanzi = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.ChuHan ch
            JOIN dbo.BaiHoc bh
              ON bh.MaBaiHoc = ch.MaBaiHoc
            WHERE bh.MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        after_course_status = query_scalar(
            cursor,
            """
            SELECT TrangThai
            FROM dbo.KhoaHoc
            WHERE MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        print("BaiHoc HSK4       :", after_lessons)
        print("TuVungBaiHoc HSK4 :", after_links)
        print("NguPhap HSK4      :", after_grammar)
        print("ChuHan HSK4       :", after_hanzi)
        print("KhoaHoc TrangThai :", after_course_status)

        if after_lessons != 20:
            raise RuntimeError(
                "POST-COMMIT FAIL: BaiHoc != 20."
            )

        if after_links != 1000:
            raise RuntimeError(
                "POST-COMMIT FAIL: TuVungBaiHoc != 1000."
            )

        if after_grammar != 114:
            raise RuntimeError(
                "POST-COMMIT FAIL: NguPhap != 114."
            )

        if after_hanzi != 300:
            raise RuntimeError(
                "POST-COMMIT FAIL: ChuHan != 300."
            )

        if norm(after_course_status) != "ban_nhap":
            raise RuntimeError(
                "POST-COMMIT FAIL: KhoaHoc khong con ban_nhap."
            )

        print()
        print("PASS: DU LIEU SAU COMMIT CHINH XAC.")

        # ====================================================
        # 19. FINAL
        # ====================================================

        print("\n" + "=" * 94)
        print("PASS: BUOC 25B COMMIT HSK4 HOAN THANH")
        print("=" * 94)

        print("DA COMMIT:")
        print("  BaiHoc       : 20")
        print("  TuVungBaiHoc : 1000")
        print("  NguPhap      : 114")
        print("  ChuHan       : 300")

        print()
        print("COMMIT: DA THUC HIEN")
        print("ROLLBACK: KHONG")
        print("AUDIO: CHUA TAO")
        print("KhoaHoc HSK4: ban_nhap")

        print()
        print("MaBaiHoc duoc tao:")

        for n in range(1, 21):
            print(
                f"  Bai {n:02d} -> "
                f"MaBaiHoc {lesson_ids[n]}"
            )

        print("=" * 94)

    except Exception:

        if not committed:

            try:
                conn.rollback()

                print(
                    "\nSAFETY: DA ROLLBACK DO GAP LOI "
                    "TRUOC COMMIT."
                )

            except Exception as rollback_error:

                print(
                    "\nCANH BAO: ROLLBACK GAP LOI:",
                    rollback_error,
                )

        else:

            print()
            print(
                "CANH BAO: loi xay ra SAU KHI COMMIT."
            )
            print(
                "Du lieu da duoc COMMIT, "
                "KHONG duoc chay lai script."
            )

        raise

    finally:

        try:
            cursor.close()
        except Exception:
            pass

        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print("\nFAIL:", exc)

        raise SystemExit(1)