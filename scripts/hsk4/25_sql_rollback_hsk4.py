# -*- coding: utf-8 -*-

"""
BUOC 25 - SQL DRY-RUN HSK4 BANG TRANSACTION + ROLLBACK

Muc tieu:
1. Kiem tra 4 snapshot dau vao.
2. Kiem tra KhoaHoc HSK4.
3. Kiem tra 1000 TuVungHSKChuan da co trong SQL.
4. Anh xa 1000 muc CSV -> dbo.TuVung mot cach an toan.
5. Trong transaction:
   - Tao 20 BaiHoc
   - Tao 1000 TuVungBaiHoc
   - Tao 114 NguPhap
   - Tao 300 ChuHan
6. Kiem tra so luong.
7. BAT BUOC ROLLBACK.
8. Kiem tra sau rollback SQL tro ve trang thai ban dau.

KHONG COMMIT.
KHONG TAO AUDIO.
"""

import csv
import hashlib
import sys
import unicodedata
from collections import defaultdict
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
        newline="",
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
    """
    Normalize nhe de so sanh Pinyin / Unicode.
    KHONG xoa dau thanh.
    KHONG bien doi noi dung.
    """
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
    """
    Lay cot dau tien ton tai va co gia tri.
    Dung cho file Hanzi vi file 20G co cac cot da chot
    qua nhieu buoc 20E/20F/20G.
    """
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

    print("=" * 92)
    print("BUOC 25 - SQL DRY-RUN HSK4 / TRANSACTION + ROLLBACK")
    print("TUYET DOI KHONG COMMIT")
    print("=" * 92)

    # ========================================================
    # 1. SNAPSHOT
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

    lesson_fields, lessons = read_csv(LESSONS)
    vocab_fields, vocab = read_csv(VOCAB)
    grammar_fields, grammar = read_csv(GRAMMAR)
    hanzi_fields, hanzi = read_csv(HANZI)

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
    # 3. CONNECT
    # ========================================================

    print("\n[3] KET NOI SQL SERVER")

    conn = get_connection()

    if conn is None:
        raise RuntimeError(
            "FAIL: get_connection() tra ve None."
        )

    cursor = conn.cursor()

    # Bao dam moi thao tac ghi sau day nam trong transaction.
    try:
        conn.autocommit = False
    except Exception:
        pass

    print("PASS: da ket noi database.")

    rolled_back = False

    try:

        # ====================================================
        # 4. KIEM TRA KHOA HOC
        # ====================================================

        print("\n[4] KIEM TRA KHOA HOC HSK4")

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

        course_rows = cursor.fetchall()

        if len(course_rows) != 1:
            raise RuntimeError(
                "FAIL: khong tim thay dung 1 KhoaHoc MaKhoaHoc=4."
            )

        course = course_rows[0]

        print("MaKhoaHoc :", course[0])
        print("MaCapDo   :", course[1])
        print("MaKyHieu  :", course[2])
        print("TrangThai :", course[3])

        if int(course[1]) != 4:
            raise RuntimeError(
                "FAIL: MaCapDo cua khoa HSK4 khong phai 4."
            )

        if str(course[2]).strip() != EXPECTED_COURSE_CODE:
            raise RuntimeError(
                "FAIL: MaKyHieu khong phai HSK4-CORE."
            )

        if str(course[3]).strip() != "ban_nhap":
            raise RuntimeError(
                "FAIL: HSK4 khong o trang thai ban_nhap."
            )

        print("PASS: KhoaHoc HSK4 dung.")

        # ====================================================
        # 5. SQL TRANG THAI BAN DAU
        # ====================================================

        print("\n[5] SNAPSHOT SQL TRUOC DRY-RUN")

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

        # Hien tai pipeline yeu cau HSK4 chua co bai.
        # Neu da co du lieu thi khong tu y chen tiep.
        if before_lessons != 0:
            raise RuntimeError(
                "FAIL: HSK4 da co BaiHoc trong SQL. "
                "Khong tiep tuc de tranh trung du lieu."
            )

        if before_links != 0:
            raise RuntimeError(
                "FAIL: HSK4 da co TuVungBaiHoc."
            )

        if before_grammar != 0:
            raise RuntimeError(
                "FAIL: HSK4 da co NguPhap."
            )

        if before_hanzi != 0:
            raise RuntimeError(
                "FAIL: HSK4 da co ChuHan."
            )

        print("PASS: SQL HSK4 chua co noi dung bai hoc.")

        # ====================================================
        # 6. KIEM TRA 1000 TUVUNGHSKCHUAN
        # ====================================================

        print("\n[6] KIEM TRA 1000 TuVungHSKChuan")

        cursor.execute(
            """
            SELECT
                MaTuHSK,
                MaMucNoiBo,
                ChuHan,
                PhienAm,
                NghiaTiengVietThamChieu
            FROM dbo.TuVungHSKChuan
            WHERE MaCapDo = 4
            """
        )

        standard_rows = cursor.fetchall()

        print("SQL HSK4 standard vocab:", len(standard_rows))

        if len(standard_rows) != 1000:
            raise RuntimeError(
                "FAIL: dbo.TuVungHSKChuan MaCapDo=4 "
                f"co {len(standard_rows)} dong, can 1000."
            )

        by_ma_tu_hsk = {
            int(r[0]): r
            for r in standard_rows
        }

        if len(by_ma_tu_hsk) != 1000:
            raise RuntimeError(
                "FAIL: trung MaTuHSK trong SQL."
            )

        for row in vocab:

            ma_tu_hsk = as_int(
                row["MaTuHSK"],
                "MaTuHSK"
            )

            sql_row = by_ma_tu_hsk.get(ma_tu_hsk)

            if sql_row is None:
                raise RuntimeError(
                    f"FAIL: MaTuHSK={ma_tu_hsk} "
                    "khong co trong SQL."
                )

            if norm(sql_row[1]) != norm(row["MaMucNoiBo"]):
                raise RuntimeError(
                    f"FAIL: MaMucNoiBo khac SQL "
                    f"tai MaTuHSK={ma_tu_hsk}."
                )

            if norm(sql_row[2]) != norm(row["ChuHan"]):
                raise RuntimeError(
                    f"FAIL: ChuHan khac SQL "
                    f"tai MaTuHSK={ma_tu_hsk}."
                )

            if norm(sql_row[3]) != norm(row["PhienAm"]):
                raise RuntimeError(
                    f"FAIL: PhienAm khac SQL "
                    f"tai MaTuHSK={ma_tu_hsk}."
                )

        print("PASS: 1000/1000 vocab CSV khop TuVungHSKChuan.")

        # ====================================================
        # 7. ANH XA CSV -> dbo.TuVung
        # ====================================================

        print("\n[7] ANH XA 1000 TU -> dbo.TuVung")

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

        # Index uu tien cao nhat:
        # Hanzi + Pinyin + Nghia + TuLoai
        exact_pos_index = defaultdict(list)

        # Fallback:
        # Hanzi + Pinyin + Nghia
        exact_index = defaultdict(list)

        # Fallback cuoi:
        # Hanzi + Pinyin
        hp_index = defaultdict(list)

        for r in sql_vocab_rows:

            ma_tu_vung = int(r[0])

            chu_han = norm(r[1])
            pinyin = norm(r[2])
            meaning = norm(r[3])
            tu_loai = norm(r[4])

            exact_pos_index[
                (chu_han, pinyin, meaning, tu_loai)
            ].append(ma_tu_vung)

            exact_index[
                (chu_han, pinyin, meaning)
            ].append(ma_tu_vung)

            hp_index[
                (chu_han, pinyin)
            ].append(ma_tu_vung)

        vocab_to_sql = {}

        mapping_method = defaultdict(int)

        ambiguous = []
        missing = []

        for row in vocab:

            source_id = row["MaMucNoiBo"]

            chu_han = norm(row["ChuHan"])
            pinyin = norm(row["PhienAm"])
            meaning = norm(row["NghiaTiengViet"])
            tu_loai = norm(row["TuLoai"])

            # =================================================
            # 1. UU TIEN: Hanzi + Pinyin + Nghia + TuLoai
            # =================================================

            key_exact_pos = (
                chu_han,
                pinyin,
                meaning,
                tu_loai,
            )

            candidates = exact_pos_index.get(
                key_exact_pos,
                []
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

            # =================================================
            # 2. FALLBACK: Hanzi + Pinyin + Nghia
            # =================================================

            key_exact = (
                chu_han,
                pinyin,
                meaning,
            )

            candidates = exact_index.get(
                key_exact,
                []
            )

            if len(candidates) == 1:
                vocab_to_sql[source_id] = candidates[0]
                mapping_method[
                    "HANZI_PINYIN_NGHIA"
                ] += 1
                continue

            # Neu exact bi trung thi KHONG ket luan ambiguous ngay.
            # Thu dung TuLoai de loc trong nhom trung.
            if len(candidates) > 1:

                filtered = []

                for ma_tu_vung in candidates:
                    sql_matches = [
                        r for r in sql_vocab_rows
                        if int(r[0]) == ma_tu_vung
                    ]

                    if len(sql_matches) != 1:
                        continue

                    sql_pos = norm(sql_matches[0][4])

                    if sql_pos == tu_loai:
                        filtered.append(ma_tu_vung)

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

            # =================================================
            # 3. FALLBACK CUOI: Hanzi + Pinyin
            # =================================================

            key_hp = (
                chu_han,
                pinyin,
            )

            candidates = hp_index.get(
                key_hp,
                []
            )

            if len(candidates) == 1:
                vocab_to_sql[source_id] = candidates[0]
                mapping_method[
                    "HANZI_PINYIN_UNIQUE"
                ] += 1
                continue

            if len(candidates) > 1:

                filtered = []

                for ma_tu_vung in candidates:

                    sql_matches = [
                        r for r in sql_vocab_rows
                        if int(r[0]) == ma_tu_vung
                    ]

                    if len(sql_matches) != 1:
                        continue

                    sql_pos = norm(sql_matches[0][4])

                    if sql_pos == tu_loai:
                        filtered.append(ma_tu_vung)

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

        print("Anh xa thanh cong:", len(vocab_to_sql))

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
            print("\n10 missing dau tien:")
            for item in missing[:10]:
                print(" ", item)

        if ambiguous:
            print("\n10 ambiguous dau tien:")
            for item in ambiguous[:10]:
                print(" ", item)

        if missing or ambiguous:
            raise RuntimeError(
                "FAIL: chua anh xa an toan duoc "
                "1000/1000 CSV -> dbo.TuVung. "
                "KHONG ghi SQL."
            )

        if len(vocab_to_sql) != 1000:
            raise RuntimeError(
                "FAIL: mapping dbo.TuVung khong du 1000."
            )

        print("PASS: 1000/1000 tu anh xa an toan.")

        # ====================================================
        # 8. BAT DAU DRY-RUN
        # ====================================================

        print("\n[8] BAT DAU TRANSACTION DRY-RUN")

        print(
            "LUU Y: tat ca INSERT sau day se bi ROLLBACK."
        )

        lesson_ids = {}

        # ====================================================
        # 9. INSERT 20 BAI HOC
        # ====================================================

        print("\n[9] INSERT TAM 20 BaiHoc")

        lesson_rows = sorted(
            lessons,
            key=lambda r: int(r["SoThuTuBai"])
        )

        for row in lesson_rows:

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

            inserted = cursor.fetchone()

            if inserted is None:
                raise RuntimeError(
                    f"FAIL: khong lay duoc MaBaiHoc "
                    f"bai {lesson_no:02d}."
                )

            lesson_ids[lesson_no] = int(
                inserted[0]
            )

        if len(lesson_ids) != 20:
            raise RuntimeError(
                "FAIL: khong tao du 20 BaiHoc."
            )

        print("PASS: INSERT tam 20 BaiHoc.")

        # ====================================================
        # 10. INSERT 1000 LINK
        # ====================================================

        print("\n[10] INSERT TAM 1000 TuVungBaiHoc")

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

            ma_bai_hoc = lesson_ids[lesson_no]

            ma_tu_vung = vocab_to_sql[
                row["MaMucNoiBo"]
            ]

            pair = (
                ma_bai_hoc,
                ma_tu_vung,
            )

            if pair in link_pairs:
                raise RuntimeError(
                    "FAIL: trung cap "
                    f"MaBaiHoc/MaTuVung: {pair}"
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
                "FAIL: khong tao du 1000 link."
            )

        print("PASS: INSERT tam 1000 TuVungBaiHoc.")

        # ====================================================
        # 11. INSERT 114 NGU PHAP
        # ====================================================

        print("\n[11] INSERT TAM 114 NguPhap")

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

            status = first_value(
                row,
                [
                    "TrangThai",
                    "TrangThaiKiemDuyet",
                ],
                default="ban_nhap",
            )

            # Toan bo HSK4 van la ban nhap.
            status = "ban_nhap"

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
                    status,
                ),
            )

            grammar_count += 1

        if grammar_count != 114:
            raise RuntimeError(
                "FAIL: khong INSERT du 114 NguPhap."
            )

        print("PASS: INSERT tam 114 NguPhap.")

        # ====================================================
        # 12. INSERT 300 CHU HAN
        # ====================================================

        print("\n[12] INSERT TAM 300 ChuHan")

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

            ky_tu = text(row.get("KyTu"))

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
                        f"cho chu {ky_tu}: {so_net_raw!r}"
                    )

            cach_ghi_nho = first_value(
                row,
                [
                    "CachGhiNho",
                ],
            )

            vi_du_trung = first_value(
                row,
                [
                    "ViDuTiengTrung",
                ],
            )

            vi_du_pinyin = first_value(
                row,
                [
                    "ViDuPinyin",
                ],
            )

            vi_du_viet = first_value(
                row,
                [
                    "ViDuTiengViet",
                ],
            )

            ma_nguon = first_value(
                row,
                [
                    "MaNguon",
                ],
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

        print("PASS: INSERT tam 300 ChuHan.")

        # ====================================================
        # 13. VALIDATE TRONG TRANSACTION
        # ====================================================

        print("\n[13] VALIDATE DU LIEU TRONG TRANSACTION")

        during_lessons = query_scalar(
            cursor,
            """
            SELECT COUNT(*)
            FROM dbo.BaiHoc
            WHERE MaKhoaHoc = ?
            """,
            (MA_KHOA_HOC,),
        )

        during_links = query_scalar(
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

        during_grammar = query_scalar(
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

        during_hanzi = query_scalar(
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

        print("BaiHoc       :", during_lessons)
        print("TuVungBaiHoc :", during_links)
        print("NguPhap      :", during_grammar)
        print("ChuHan       :", during_hanzi)

        if during_lessons != 20:
            raise RuntimeError(
                "FAIL: transaction khong co 20 BaiHoc."
            )

        if during_links != 1000:
            raise RuntimeError(
                "FAIL: transaction khong co 1000 TuVungBaiHoc."
            )

        if during_grammar != 114:
            raise RuntimeError(
                "FAIL: transaction khong co 114 NguPhap."
            )

        if during_hanzi != 300:
            raise RuntimeError(
                "FAIL: transaction khong co 300 ChuHan."
            )

        # Bao dam moi BaiHoc co ca 3 thanh phan.
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
                "FAIL: query per-lesson khong du 20."
            )

        print()
        print(
            f"{'Bai':<6}"
            f"{'TuVung':>10}"
            f"{'NguPhap':>10}"
            f"{'ChuHan':>10}"
        )
        print("-" * 36)

        for r in per_lesson:

            lesson_no = int(r[0])
            v_count = int(r[1])
            g_count = int(r[2])
            h_count = int(r[3])

            print(
                f"{lesson_no:02d}"
                f"{v_count:>14}"
                f"{g_count:>10}"
                f"{h_count:>10}"
            )

            if v_count <= 0:
                raise RuntimeError(
                    f"FAIL: Bai {lesson_no:02d} khong co vocab."
                )

            if g_count <= 0:
                raise RuntimeError(
                    f"FAIL: Bai {lesson_no:02d} khong co grammar."
                )

            if h_count <= 0:
                raise RuntimeError(
                    f"FAIL: Bai {lesson_no:02d} khong co Hanzi."
                )

        print()
        print("PASS: transaction co dung 20 / 1000 / 114 / 300.")
        print("PASS: 20/20 bai co du 3 thanh phan.")

        # ====================================================
        # 14. ROLLBACK BAT BUOC
        # ====================================================

        print("\n[14] ROLLBACK BAT BUOC")

        conn.rollback()
        rolled_back = True

        print("PASS: DA ROLLBACK.")
        print("KHONG CO DU LIEU BUOC 25 DUOC COMMIT.")

        # ====================================================
        # 15. VERIFY SAU ROLLBACK
        # ====================================================

        print("\n[15] KIEM TRA SAU ROLLBACK")

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

        print("BaiHoc HSK4       :", after_lessons)
        print("TuVungBaiHoc HSK4 :", after_links)
        print("NguPhap HSK4      :", after_grammar)
        print("ChuHan HSK4       :", after_hanzi)

        if after_lessons != before_lessons:
            raise RuntimeError(
                "FAIL: BaiHoc khong tro ve snapshot ban dau."
            )

        if after_links != before_links:
            raise RuntimeError(
                "FAIL: TuVungBaiHoc khong tro ve snapshot ban dau."
            )

        if after_grammar != before_grammar:
            raise RuntimeError(
                "FAIL: NguPhap khong tro ve snapshot ban dau."
            )

        if after_hanzi != before_hanzi:
            raise RuntimeError(
                "FAIL: ChuHan khong tro ve snapshot ban dau."
            )

        print("PASS: SQL da tro ve dung trang thai truoc dry-run.")

        print("\n" + "=" * 92)
        print("PASS: BUOC 25 ROLLBACK HOAN THANH")
        print("=" * 92)
        print("Dry-run thanh cong:")
        print("  BaiHoc       : 20")
        print("  TuVungBaiHoc : 1000")
        print("  NguPhap      : 114")
        print("  ChuHan       : 300")
        print()
        print("ROLLBACK: DA THUC HIEN")
        print("COMMIT: KHONG")
        print("AUDIO: KHONG")
        print("HSK4: VAN ban_nhap")
        print("=" * 92)

    except Exception:

        # Neu bat ky cho nao FAIL thi van rollback.
        if not rolled_back:
            try:
                conn.rollback()
                print(
                    "\nSAFETY: da ROLLBACK transaction sau khi gap loi."
                )
            except Exception as rollback_error:
                print(
                    "\nCANH BAO: rollback gap loi:",
                    rollback_error,
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