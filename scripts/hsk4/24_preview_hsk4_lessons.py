# -*- coding: utf-8 -*-

"""
BUOC 24 - TONG HOP PREVIEW 20 BAI HSK4

Input:
- lessons_hsk4_draft_20_21B.csv
- vocabulary_hsk4_by_lesson_draft_21B.csv
- grammar_hsk4_by_lesson_draft_22A.csv
- hanzi_hsk4_by_lesson_draft_23.csv

Output:
- hsk4_lessons_preview_24.csv
- hsk4_lessons_preview_24.md
- hsk4_preview_summary_24.json

CHI DOC VA TONG HOP.
KHONG GHI SQL.
KHONG TAO AUDIO.
"""

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(r"D:\DATN1\scripts\hsk4\data\processed")

LESSONS = BASE / "lessons_hsk4_draft_20_21B.csv"
VOCAB = BASE / "vocabulary_hsk4_by_lesson_draft_21B.csv"
GRAMMAR = BASE / "grammar_hsk4_by_lesson_draft_22A.csv"
HANZI = BASE / "hanzi_hsk4_by_lesson_draft_23.csv"

OUT_CSV = BASE / "hsk4_lessons_preview_24.csv"
OUT_MD = BASE / "hsk4_lessons_preview_24.md"
OUT_JSON = BASE / "hsk4_preview_summary_24.json"


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


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def csv_bytes(fields, rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


def safe_write(path, content):
    if path.exists():
        if path.read_bytes() == content:
            print("PASS: file da ton tai, noi dung giong:", path.name)
            return

        raise RuntimeError(
            "FAIL: file da ton tai nhung noi dung khac, "
            "khong ghi de: " + str(path)
        )

    with path.open("xb") as f:
        f.write(content)

    print("PASS: da tao", path.name)


def as_int(value, name):
    try:
        return int(value)
    except Exception:
        raise RuntimeError(
            f"FAIL: {name} khong phai so nguyen: {value!r}"
        )


def main():
    print("=" * 88)
    print("BUOC 24 - PREVIEW 20 BAI HSK4")
    print("1000 TU VUNG + 114 NGU PHAP + 300 CHU HAN")
    print("KHONG GHI SQL - KHONG TAO AUDIO")
    print("=" * 88)

    # ======================================================
    # 1. SNAPSHOT
    # ======================================================

    print("\n[1] KIEM TRA SNAPSHOT")

    for path, expected_hash in EXPECTED.items():

        if not path.is_file():
            raise FileNotFoundError(path)

        actual = sha256(path)

        print(path.name)
        print("  SHA256:", actual)

        if actual != expected_hash:
            raise RuntimeError(
                "FAIL: SHA256 khong khop: " + path.name
            )

    print("PASS: 4 snapshot hop le.")

    # ======================================================
    # 2. DOC DU LIEU
    # ======================================================

    print("\n[2] DOC DU LIEU")

    lesson_fields, lessons = read_csv(LESSONS)
    vocab_fields, vocab = read_csv(VOCAB)
    grammar_fields, grammar = read_csv(GRAMMAR)
    hanzi_fields, hanzi = read_csv(HANZI)

    print("Bai hoc :", len(lessons))
    print("Tu vung :", len(vocab))
    print("Ngu phap:", len(grammar))
    print("Chu Han :", len(hanzi))

    if len(lessons) != 20:
        raise RuntimeError("FAIL: khong du 20 bai.")

    if len(vocab) != 1000:
        raise RuntimeError("FAIL: khong du 1000 tu.")

    if len(grammar) != 114:
        raise RuntimeError("FAIL: khong du 114 ngu phap.")

    if len(hanzi) != 300:
        raise RuntimeError("FAIL: khong du 300 chu Han.")

    print("PASS: dung 20 / 1000 / 114 / 300.")

    # ======================================================
    # 3. KIEM TRA BAI HOC
    # ======================================================

    print("\n[3] KIEM TRA 20 BAI")

    lesson_map = {}

    for row in lessons:
        n = as_int(row["SoThuTuBai"], "SoThuTuBai")

        if n in lesson_map:
            raise RuntimeError(
                f"FAIL: trung bai {n}."
            )

        if not 1 <= n <= 20:
            raise RuntimeError(
                f"FAIL: so bai ngoai 1-20: {n}"
            )

        lesson_map[n] = row

    if set(lesson_map) != set(range(1, 21)):
        raise RuntimeError(
            "FAIL: danh sach bai khong du 1-20."
        )

    print("PASS: 20 bai duy nhat, du 01-20.")

    # ======================================================
    # 4. KIEM TRA PHAN BAI
    # ======================================================

    print("\n[4] KIEM TRA PHAN BAI CAC THANH PHAN")

    groups_vocab = defaultdict(list)
    groups_grammar = defaultdict(list)
    groups_hanzi = defaultdict(list)

    # ---------------- VOCAB ----------------

    vocab_ids = []

    for row in vocab:
        lesson = as_int(
            row["SoThuTuBai"],
            "vocab.SoThuTuBai"
        )

        if lesson not in lesson_map:
            raise RuntimeError(
                f"FAIL: vocab vao bai khong ton tai: {lesson}"
            )

        vocab_ids.append(row["MaMucNoiBo"])
        groups_vocab[lesson].append(row)

    if len(set(vocab_ids)) != 1000:
        raise RuntimeError(
            "FAIL: vocab trung MaMucNoiBo."
        )

    # ---------------- GRAMMAR ----------------

    grammar_ids = []

    for row in grammar:
        lesson = as_int(
            row["SoThuTuBai"],
            "grammar.SoThuTuBai"
        )

        if lesson not in lesson_map:
            raise RuntimeError(
                f"FAIL: grammar vao bai khong ton tai: {lesson}"
            )

        grammar_ids.append(row["MaDonViGiangDay"])
        groups_grammar[lesson].append(row)

    if len(set(grammar_ids)) != 114:
        raise RuntimeError(
            "FAIL: grammar trung MaDonViGiangDay."
        )

    # ---------------- HANZI ----------------

    hanzi_ids = []
    hanzi_chars = []

    for row in hanzi:
        lesson = as_int(
            row["SoThuTuBai"],
            "hanzi.SoThuTuBai"
        )

        if lesson not in lesson_map:
            raise RuntimeError(
                f"FAIL: Hanzi vao bai khong ton tai: {lesson}"
            )

        hanzi_ids.append(row["MaChuHanTam"])
        hanzi_chars.append(row["KyTu"])

        groups_hanzi[lesson].append(row)

    if len(set(hanzi_ids)) != 300:
        raise RuntimeError(
            "FAIL: trung MaChuHanTam."
        )

    if len(set(hanzi_chars)) != 300:
        raise RuntimeError(
            "FAIL: trung KyTu."
        )

    print("PASS: phan bai vocab hop le.")
    print("PASS: phan bai grammar hop le.")
    print("PASS: phan bai Hanzi hop le.")

    # ======================================================
    # 5. KIEM TRA MOI BAI
    # ======================================================

    print("\n[5] KIEM TRA NOI DUNG TUNG BAI")

    for lesson in range(1, 21):

        if len(groups_vocab[lesson]) == 0:
            raise RuntimeError(
                f"FAIL: bai {lesson:02d} khong co tu vung."
            )

        if len(groups_grammar[lesson]) == 0:
            raise RuntimeError(
                f"FAIL: bai {lesson:02d} khong co ngu phap."
            )

        if len(groups_hanzi[lesson]) == 0:
            raise RuntimeError(
                f"FAIL: bai {lesson:02d} khong co chu Han."
            )

    print("PASS: 20/20 bai co tu vung.")
    print("PASS: 20/20 bai co ngu phap.")
    print("PASS: 20/20 bai co chu Han.")

    # ======================================================
    # 6. KIEM TRA TEN BAI DONG BO
    # ======================================================

    print("\n[6] KIEM TRA TIEU DE BAI HOC")

    def verify_title(rows, component):
        for row in rows:
            lesson = as_int(
                row["SoThuTuBai"],
                component + ".SoThuTuBai"
            )

            expected_title = lesson_map[lesson]["TieuDe"]

            actual_title = row.get(
                "TieuDeBaiHoc", ""
            ).strip()

            if actual_title and actual_title != expected_title:
                raise RuntimeError(
                    f"FAIL: {component} bai {lesson:02d} "
                    f"co tieu de khong khop.\n"
                    f"Expected: {expected_title}\n"
                    f"Actual  : {actual_title}"
                )

    verify_title(vocab, "VOCAB")
    verify_title(grammar, "GRAMMAR")
    verify_title(hanzi, "HANZI")

    print("PASS: tieu de bai dong bo.")

    # ======================================================
    # 7. TAO BANG TONG HOP
    # ======================================================

    print("\n[7] TONG HOP 20 BAI")

    preview_rows = []

    total_vocab_review = 0
    total_hanzi_review = 0

    for lesson in range(1, 21):

        info = lesson_map[lesson]

        vocab_rows = sorted(
            groups_vocab[lesson],
            key=lambda r: as_int(
                r["ThuTuTrongBai"],
                "vocab.ThuTuTrongBai"
            )
        )

        grammar_rows = sorted(
            groups_grammar[lesson],
            key=lambda r: as_int(
                r["ThuTuTrongBai"],
                "grammar.ThuTuTrongBai"
            )
        )

        hanzi_rows = sorted(
            groups_hanzi[lesson],
            key=lambda r: as_int(
                r["ThuTuTrongBai"],
                "hanzi.ThuTuTrongBai"
            )
        )

        vocab_review = sum(
            r.get("CanReview21B", "") == "CO"
            for r in vocab_rows
        )

        hanzi_review = sum(
            r.get("CanReviewPhanBai23", "") == "CO"
            for r in hanzi_rows
        )

        total_vocab_review += vocab_review
        total_hanzi_review += hanzi_review

        vocab_sample = " | ".join(
            f"{r['ChuHan']} ({r['PhienAm']})"
            for r in vocab_rows[:8]
        )

        grammar_sample = " | ".join(
            r["TenCauTruc"]
            for r in grammar_rows[:5]
        )

        hanzi_sample = " ".join(
            r["KyTu"]
            for r in hanzi_rows[:15]
        )

        preview_rows.append({
            "SoThuTuBai": lesson,
            "MaBaiHocTam": info["MaBaiHocTam"],
            "TieuDe": info["TieuDe"],
            "SoTuVung": len(vocab_rows),
            "TuVungCanReview21B": vocab_review,
            "SoNguPhap": len(grammar_rows),
            "SoChuHanMoi": len(hanzi_rows),
            "ChuHanCanReview23": hanzi_review,
            "MauTuVung": vocab_sample,
            "MauNguPhap": grammar_sample,
            "MauChuHan": hanzi_sample,
            "TrangThai": info["TrangThai"],
        })

    print()
    print(
        f"{'Bai':<5}"
        f"{'TuVung':>8}"
        f"{'ReviewTV':>10}"
        f"{'NguPhap':>10}"
        f"{'ChuHan':>8}"
        f"{'ReviewCH':>10}"
    )

    print("-" * 55)

    for row in preview_rows:
        print(
            f"{row['SoThuTuBai']:02d}"
            f"{row['SoTuVung']:>11}"
            f"{row['TuVungCanReview21B']:>10}"
            f"{row['SoNguPhap']:>10}"
            f"{row['SoChuHanMoi']:>8}"
            f"{row['ChuHanCanReview23']:>10}"
        )

    print("-" * 55)

    print(
        f"{'TONG':<5}"
        f"{sum(r['SoTuVung'] for r in preview_rows):>8}"
        f"{total_vocab_review:>10}"
        f"{sum(r['SoNguPhap'] for r in preview_rows):>10}"
        f"{sum(r['SoChuHanMoi'] for r in preview_rows):>8}"
        f"{total_hanzi_review:>10}"
    )

    # ======================================================
    # 8. TAO MARKDOWN PREVIEW
    # ======================================================

    print("\n[8] TAO PREVIEW CHI TIET")

    md = []

    md.append("# HSK4 - Preview 20 bài")
    md.append("")
    md.append(
        "> Bản nháp trước SQL. "
        "Chưa tạo audio, chưa publish."
    )
    md.append("")

    for lesson in range(1, 21):

        info = lesson_map[lesson]

        vocab_rows = sorted(
            groups_vocab[lesson],
            key=lambda r: int(r["ThuTuTrongBai"])
        )

        grammar_rows = sorted(
            groups_grammar[lesson],
            key=lambda r: int(r["ThuTuTrongBai"])
        )

        hanzi_rows = sorted(
            groups_hanzi[lesson],
            key=lambda r: int(r["ThuTuTrongBai"])
        )

        md.append(
            f"## Bài {lesson:02d} - {info['TieuDe']}"
        )
        md.append("")

        md.append(
            f"- Từ vựng: **{len(vocab_rows)}**"
        )
        md.append(
            f"- Ngữ pháp: **{len(grammar_rows)}**"
        )
        md.append(
            f"- Chữ Hán mới: **{len(hanzi_rows)}**"
        )
        md.append("")

        # ---------------- vocab ----------------

        md.append("### Từ vựng")
        md.append("")

        for row in vocab_rows:
            md.append(
                f"{int(row['ThuTuTrongBai']):02d}. "
                f"**{row['ChuHan']}** "
                f"({row['PhienAm']}) — "
                f"{row['NghiaTiengViet']}"
            )

        md.append("")

        # ---------------- grammar ----------------

        md.append("### Ngữ pháp")
        md.append("")

        for row in grammar_rows:
            md.append(
                f"{int(row['ThuTuTrongBai']):02d}. "
                f"**{row['TenCauTruc']}**"
            )

            if row.get("MoTa", "").strip():
                md.append(
                    f"   - {row['MoTa'].strip()}"
                )

            if row.get("ViDuTiengTrung", "").strip():
                md.append(
                    f"   - Ví dụ: "
                    f"{row['ViDuTiengTrung'].strip()}"
                )

            if row.get("ViDuPinyin", "").strip():
                md.append(
                    f"   - Pinyin: "
                    f"{row['ViDuPinyin'].strip()}"
                )

            if row.get("ViDuTiengViet", "").strip():
                md.append(
                    f"   - Nghĩa: "
                    f"{row['ViDuTiengViet'].strip()}"
                )

        md.append("")

        # ---------------- hanzi ----------------

        md.append("### Chữ Hán mới")
        md.append("")

        for row in hanzi_rows:

            pinyin = row.get(
                "PinyinChot20G", ""
            ).strip()

            meaning = row.get(
                "NghiaTiengVietChot20F", ""
            ).strip()

            md.append(
                f"{int(row['ThuTuTrongBai']):02d}. "
                f"**{row['KyTu']}** "
                f"({pinyin}) — "
                f"{meaning}"
            )

        md.append("")
        md.append("---")
        md.append("")

    # ======================================================
    # 9. VALIDATE TONG CUOI
    # ======================================================

    print("\n[9] VALIDATE TONG CUOI")

    total_v = sum(
        len(groups_vocab[i])
        for i in range(1, 21)
    )

    total_g = sum(
        len(groups_grammar[i])
        for i in range(1, 21)
    )

    total_h = sum(
        len(groups_hanzi[i])
        for i in range(1, 21)
    )

    if total_v != 1000:
        raise RuntimeError(
            f"FAIL: tong vocab = {total_v}"
        )

    if total_g != 114:
        raise RuntimeError(
            f"FAIL: tong grammar = {total_g}"
        )

    if total_h != 300:
        raise RuntimeError(
            f"FAIL: tong Hanzi = {total_h}"
        )

    print("PASS: Tong vocab  = 1000")
    print("PASS: Tong grammar = 114")
    print("PASS: Tong Hanzi   = 300")

    # ======================================================
    # 10. XUAT FILE
    # ======================================================

    print("\n[10] XUAT FILE")

    preview_fields = [
        "SoThuTuBai",
        "MaBaiHocTam",
        "TieuDe",
        "SoTuVung",
        "TuVungCanReview21B",
        "SoNguPhap",
        "SoChuHanMoi",
        "ChuHanCanReview23",
        "MauTuVung",
        "MauNguPhap",
        "MauChuHan",
        "TrangThai",
    ]

    safe_write(
        OUT_CSV,
        csv_bytes(
            preview_fields,
            preview_rows
        )
    )

    safe_write(
        OUT_MD,
        (
            "\n".join(md).rstrip()
            + "\n"
        ).encode("utf-8")
    )

    summary = {
        "buoc": 24,
        "trang_thai": "PREVIEW_TRUOC_SQL",
        "so_bai": 20,
        "tong_tu_vung": 1000,
        "tong_ngu_phap": 114,
        "tong_chu_han_moi": 300,
        "tu_vung_can_review_21B": total_vocab_review,
        "chu_han_can_review_23": total_hanzi_review,
        "phan_bo": {
            str(row["SoThuTuBai"]): {
                "tu_vung": row["SoTuVung"],
                "ngu_phap": row["SoNguPhap"],
                "chu_han": row["SoChuHanMoi"],
            }
            for row in preview_rows
        },
        "inputs": {
            path.name: EXPECTED[path]
            for path in EXPECTED
        },
        "output_csv": str(OUT_CSV),
        "output_md": str(OUT_MD),
        "ghi_sql": False,
        "tao_audio": False,
    }

    safe_write(
        OUT_JSON,
        (
            json.dumps(
                summary,
                ensure_ascii=False,
                indent=2
            )
            + "\n"
        ).encode("utf-8")
    )

    print("\n" + "=" * 88)
    print("PASS: BUOC 24 HOAN THANH")
    print("=" * 88)

    print("20/20 bai da duoc tong hop.")
    print("Tu vung :", total_v)
    print("Ngu phap:", total_g)
    print("Chu Han :", total_h)

    print()
    print("CSV:")
    print(OUT_CSV)
    print("SHA256:")
    print(sha256(OUT_CSV))

    print()
    print("MARKDOWN:")
    print(OUT_MD)
    print("SHA256:")
    print(sha256(OUT_MD))

    print()
    print("SUMMARY:")
    print(OUT_JSON)

    print()
    print("KHONG GHI SQL.")
    print("KHONG TAO AUDIO.")
    print("HSK4 VAN O TRANG THAI BAN_NHAP.")
    print("=" * 88)


if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        print("\nFAIL:", exc)
        raise SystemExit(1)