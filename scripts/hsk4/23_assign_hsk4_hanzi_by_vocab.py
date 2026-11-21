
# -*- coding: utf-8 -*-

"""
BUOC 23 - GAN 300 CHU HAN HSK4 VAO 20 BAI

Nguyen tac:
- Moi chu Han chi duoc gan vao mot bai.
- Chon bai dau tien co tu vung chua chu Han do.
- Trong bai, chon tu xuat hien som nhat.
- Luu ma tu vung va tu dai dien lam bang chung.
- Giu nguyen toan bo noi dung nguon 20G.
- Khong ghi SQL, khong tao audio.
"""

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(r"D:\DATN1\scripts\hsk4\data\processed")

VOCAB = BASE / "vocabulary_hsk4_by_lesson_draft_21B.csv"
HANZI = BASE / "hanzi_hsk4_300_pinyin_final_20G.csv"

OUTPUT = BASE / "hanzi_hsk4_by_lesson_draft_23.csv"
EVIDENCE = BASE / "hanzi_hsk4_first_vocab_evidence_23.csv"
SUMMARY = BASE / "hsk4_hanzi_summary_23.json"

EXPECTED_VOCAB_SHA = (
    "79716ce75ee23b869626a546017d5e744a6b0e40d8b214dace8851c009cdc1f2"
)
EXPECTED_HANZI_SHA = (
    "869384a0bda7976a1ae09e14763f41545822b3ac2d665ec5224cbfbebf3f12ba"
)


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
            "FAIL: file da ton tai nhung noi dung khac: " + str(path)
        )

    with path.open("xb") as f:
        f.write(content)

    print("PASS: da tao", path.name)


def number(value, field):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise RuntimeError(
            f"FAIL: gia tri khong hop le o {field}: {value!r}"
        )


def main():
    print("=" * 82)
    print("BUOC 23 - GAN 300 CHU HAN HSK4 THEO TU VUNG DA PHAN BAI")
    print("KHONG GHI SQL - KHONG TAO AUDIO")
    print("=" * 82)

    print("\n[1] KIEM TRA SNAPSHOT")

    for path, expected in [
        (VOCAB, EXPECTED_VOCAB_SHA),
        (HANZI, EXPECTED_HANZI_SHA),
    ]:
        if not path.is_file():
            raise FileNotFoundError(path)

        actual = sha256(path)
        print(path.name, actual)

        if actual != expected:
            raise RuntimeError(
                "FAIL: SHA256 khong khop: " + path.name
            )

    print("PASS: hai snapshot hop le.")

    print("\n[2] DOC VA KIEM TRA DU LIEU")

    vocab_fields, vocab = read_csv(VOCAB)
    hanzi_fields, hanzi = read_csv(HANZI)

    if len(vocab) != 1000:
        raise RuntimeError(
            f"FAIL: can 1000 tu vung, co {len(vocab)}."
        )

    if len(hanzi) != 300:
        raise RuntimeError(
            f"FAIL: can 300 chu Han, co {len(hanzi)}."
        )

    vocab_ids = [r["MaMucNoiBo"] for r in vocab]
    hanzi_ids = [r["MaChuHanTam"] for r in hanzi]
    characters = [r["KyTu"] for r in hanzi]

    if len(set(vocab_ids)) != 1000:
        raise RuntimeError("FAIL: trung MaMucNoiBo.")

    if len(set(hanzi_ids)) != 300:
        raise RuntimeError("FAIL: trung MaChuHanTam.")

    if len(set(characters)) != 300:
        raise RuntimeError("FAIL: trung KyTu.")

    if any(len(ch) != 1 for ch in characters):
        raise RuntimeError("FAIL: KyTu khong phai mot chu Han.")

    if any(
        not r["PinyinChot20G"].strip()
        or not r["NghiaTiengVietChot20F"].strip()
        for r in hanzi
    ):
        raise RuntimeError("FAIL: co chu Han thieu Pinyin/nghia chot.")

    for row in vocab:
        lesson = number(row["SoThuTuBai"], "SoThuTuBai")
        order = number(row["ThuTuTrongBai"], "ThuTuTrongBai")

        if not 1 <= lesson <= 20 or order < 1:
            raise RuntimeError(
                "FAIL: thu tu bai/tu vung khong hop le."
            )

        if not row["ChuHan"].strip():
            raise RuntimeError("FAIL: tu vung thieu ChuHan.")

    print("PASS: 1000 tu vung duy nhat.")
    print("PASS: 300 chu Han duy nhat.")
    print("PASS: 300/300 chu co Pinyin va nghia.")

    print("\n[3] LAP CHI MUC CHU HAN -> TU VUNG")

    # Chi lap chi muc mot lan, tranh quet 1000 tu
    # lap lai cho tung chu Han.
    vocab_by_char = defaultdict(list)

    for row in vocab:
        # set(...) de mot chu lap lai trong mot tu
        # khong tao ra hai lan xuat hien.
        for ch in set(row["ChuHan"]):
            vocab_by_char[ch].append(row)

    for ch in vocab_by_char:
        vocab_by_char[ch].sort(
            key=lambda r: (
                number(r["SoThuTuBai"], "SoThuTuBai"),
                number(r["ThuTuTrongBai"], "ThuTuTrongBai"),
                number(r["SoThuTuNguon"], "SoThuTuNguon"),
                r["MaMucNoiBo"],
            )
        )

    missing = sorted(
        ch for ch in characters if ch not in vocab_by_char
    )

    if missing:
        raise RuntimeError(
            "FAIL: chu Han khong co trong 1000 tu: "
            + ", ".join(missing)
        )

    print("PASS: 300/300 chu Han co tu vung chua chu do.")

    print("\n[4] GAN BAI THEO LAN XUAT HIEN DAU TIEN")

    assigned = []
    evidence = []

    for original in hanzi:
        row = dict(original)
        ch = row["KyTu"]

        occurrences = vocab_by_char[ch]
        first = occurrences[0]

        lesson = number(first["SoThuTuBai"], "SoThuTuBai")
        vocab_order = number(
            first["ThuTuTrongBai"], "ThuTuTrongBai"
        )

        row["SoThuTuBai"] = lesson
        row["MaBaiHocTam"] = first["MaBaiHocTam"]
        row["TieuDeBaiHoc"] = first["TieuDeBaiHoc"]

        row["MaTuHSKDauTien"] = first["MaTuHSK"]
        row["MaMucNoiBoDauTien"] = first["MaMucNoiBo"]
        row["TuVungDauTien"] = first["ChuHan"]
        row["PinyinTuVungDauTien"] = first["PhienAm"]
        row["NghiaTuVungDauTien"] = first["NghiaTiengViet"]
        row["ThuTuTuVungDauTien"] = vocab_order

        row["SoTuVungHSK4ChuaChu"] = len(occurrences)
        row["SoBaiCoChu"] = len({
            number(r["SoThuTuBai"], "SoThuTuBai")
            for r in occurrences
        })

        row["QuyTacGanBai23"] = "TU_VUNG_XUAT_HIEN_DAU_TIEN"
        row["CanReviewPhanBai23"] = (
            "CO" if first.get("CanReview21B") == "CO"
            else "KHONG"
        )

        row["GhiChuBuoc23"] = (
            "Gan theo bai cua tu vung dau tien; "
            "ke thua tinh trang review phan bai tu 21B."
        )

        assigned.append(row)

        evidence.append({
            "MaChuHanTam": row["MaChuHanTam"],
            "KyTu": ch,
            "SoThuTuBai": lesson,
            "TieuDeBaiHoc": first["TieuDeBaiHoc"],
            "MaTuHSKDauTien": first["MaTuHSK"],
            "MaMucNoiBoDauTien": first["MaMucNoiBo"],
            "TuVungDauTien": first["ChuHan"],
            "PinyinTuVungDauTien": first["PhienAm"],
            "ThuTuTuVungDauTien": vocab_order,
            "SoTuVungHSK4ChuaChu": len(occurrences),
            "SoBaiCoChu": row["SoBaiCoChu"],
            "CanReviewPhanBai23": row["CanReviewPhanBai23"],
        })

    assigned.sort(
        key=lambda r: (
            int(r["SoThuTuBai"]),
            int(r["ThuTuTuVungDauTien"]),
            r["MaMucNoiBoDauTien"],
            r["MaChuHanTam"],
        )
    )

    counts = Counter()

    for row in assigned:
        lesson = int(row["SoThuTuBai"])
        counts[lesson] += 1
        row["ThuTuTrongBai"] = counts[lesson]

    print("PASS: da gan 300/300 chu Han.")

    print("\n[5] VALIDATE")

    if len(assigned) != 300:
        raise RuntimeError("FAIL: mat chu Han.")

    if set(r["MaChuHanTam"] for r in assigned) != set(hanzi_ids):
        raise RuntimeError("FAIL: mat/them MaChuHanTam.")

    if set(r["KyTu"] for r in assigned) != set(characters):
        raise RuntimeError("FAIL: mat/them KyTu.")

    original_by_id = {
        r["MaChuHanTam"]: r for r in hanzi
    }

    # Toan bo cac cot nguon phai giu nguyen.
    for row in assigned:
        original = original_by_id[row["MaChuHanTam"]]
        for field in hanzi_fields:
            if row[field] != original[field]:
                raise RuntimeError(
                    "FAIL: noi dung nguon bi sua: "
                    + row["MaChuHanTam"] + " / " + field
                )

        # Chung minh tu dau tien that su chua chu Han.
        first_id = row["MaMucNoiBoDauTien"]
        matches = [
            v for v in vocab
            if v["MaMucNoiBo"] == first_id
        ]

        if len(matches) != 1:
            raise RuntimeError(
                "FAIL: khong tim thay tu dai dien: " + first_id
            )

        if row["KyTu"] not in matches[0]["ChuHan"]:
            raise RuntimeError(
                "FAIL: tu dai dien khong chua chu Han."
            )

        if int(row["SoThuTuBai"]) != int(
            matches[0]["SoThuTuBai"]
        ):
            raise RuntimeError(
                "FAIL: bai chu Han khac bai tu dau tien."
            )

    for lesson in range(1, 21):
        orders = sorted(
            int(r["ThuTuTrongBai"])
            for r in assigned
            if int(r["SoThuTuBai"]) == lesson
        )

        if orders != list(range(1, len(orders) + 1)):
            raise RuntimeError(
                f"FAIL: thu tu chu Han bai {lesson}."
            )

    if sum(counts.values()) != 300:
        raise RuntimeError("FAIL: tong phan bo khong bang 300.")

    print("PASS: 300/300 chu, khong mat, khong trung.")
    print("PASS: giu nguyen tat ca cot nguon 20G.")
    print("PASS: moi chu co tu vung dau tien lam bang chung.")
    print("PASS: thu tu trong tung bai lien tuc.")

    print("\n[6] THONG KE 20 BAI")

    for lesson in range(1, 21):
        print(
            f"Bai {lesson:02d} | "
            f"{counts[lesson]:3d} chu Han"
        )

    review_count = sum(
        r["CanReviewPhanBai23"] == "CO"
        for r in assigned
    )

    print("Tong:", len(assigned))
    print("Can review phan bai theo 21B:", review_count)

    print("\n[7] SPOT CHECK")

    for ch in ["阿", "姨", "矮", "摆", "脱"]:
        matches = [
            r for r in assigned
            if r["KyTu"] == ch
        ]
        if len(matches) == 1:
            row = matches[0]
            print(
                f"{ch} -> Bai {int(row['SoThuTuBai']):02d}"
                f" | Tu dau tien: {row['TuVungDauTien']}"
                f" | Pinyin: {row['PinyinChot20G']}"
            )

    print("\n[8] XUAT FILE")

    extra_fields = [
        "SoThuTuBai",
        "MaBaiHocTam",
        "TieuDeBaiHoc",
        "ThuTuTrongBai",
        "MaTuHSKDauTien",
        "MaMucNoiBoDauTien",
        "TuVungDauTien",
        "PinyinTuVungDauTien",
        "NghiaTuVungDauTien",
        "ThuTuTuVungDauTien",
        "SoTuVungHSK4ChuaChu",
        "SoBaiCoChu",
        "QuyTacGanBai23",
        "CanReviewPhanBai23",
        "GhiChuBuoc23",
    ]

    output_fields = hanzi_fields + [
        f for f in extra_fields
        if f not in hanzi_fields
    ]

    evidence_fields = [
        "MaChuHanTam",
        "KyTu",
        "SoThuTuBai",
        "TieuDeBaiHoc",
        "MaTuHSKDauTien",
        "MaMucNoiBoDauTien",
        "TuVungDauTien",
        "PinyinTuVungDauTien",
        "ThuTuTuVungDauTien",
        "SoTuVungHSK4ChuaChu",
        "SoBaiCoChu",
        "CanReviewPhanBai23",
    ]

    safe_write(
        OUTPUT,
        csv_bytes(output_fields, assigned),
    )

    safe_write(
        EVIDENCE,
        csv_bytes(evidence_fields, evidence),
    )

    summary = {
        "buoc": 23,
        "trang_thai": "BAN_NHAP",
        "tong_chu_han": 300,
        "so_bai": 20,
        "quy_tac": "TU_VUNG_XUAT_HIEN_DAU_TIEN",
        "vocab_source_sha256": EXPECTED_VOCAB_SHA,
        "hanzi_source_sha256": EXPECTED_HANZI_SHA,
        "phan_bo": {
            str(n): counts[n]
            for n in range(1, 21)
        },
        "can_review_phan_bai": review_count,
        "output_sha256": sha256(OUTPUT),
        "evidence_sha256": sha256(EVIDENCE),
        "ghi_sql": False,
        "tao_audio": False,
    }

    safe_write(
        SUMMARY,
        (
            json.dumps(
                summary,
                ensure_ascii=False,
                indent=2,
            ) + "\n"
        ).encode("utf-8"),
    )

    print("\n" + "=" * 82)
    print("PASS: BUOC 23 HOAN THANH")
    print("=" * 82)
    print("300/300 chu Han da duoc gan bai.")
    print("OUTPUT:", OUTPUT)
    print("SHA256:", sha256(OUTPUT))
    print("EVIDENCE:", EVIDENCE)
    print("SUMMARY:", SUMMARY)
    print("KHONG GHI SQL.")
    print("KHONG TAO AUDIO.")
    print("CHUA DUYET NOI DUNG DE XUAT BAN.")
    print("=" * 82)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nFAIL:", exc)
        raise SystemExit(1)
