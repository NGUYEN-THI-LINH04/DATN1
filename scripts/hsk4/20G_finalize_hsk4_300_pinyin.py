# -*- coding: utf-8 -*-

"""
BUOC 20G - CHOT PINYIN 300 CHU HAN HSK4

Muc tieu:
- Doc output Buoc 20F.
- Xac minh snapshot.
- Chot truong hop cuoi cung:
      H4-0751 | 呀 | ya
- Dam bao 300/300 chu deu co Pinyin.
- Khong sua nghia.
- Khong sua cau truc.
- Khong ghi SQL.
- Khong gan bai hoc.
- Khong tao audio.
"""

import csv
import hashlib
import io
import json
from pathlib import Path


ROOT = Path(r"D:\DATN1")

PROCESSED = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

SOURCE = (
    PROCESSED
    / "hanzi_hsk4_300_meaning_pinyin_merged_20F.csv"
)

OUTPUT = (
    PROCESSED
    / "hanzi_hsk4_300_pinyin_final_20G.csv"
)

SUMMARY = (
    PROCESSED
    / "hanzi_hsk4_300_pinyin_final_20G_summary.json"
)


EXPECTED_SOURCE_SHA256 = (
    "a59a279855c51192286a11afba03a9180e24674ab65d09c9bfa26a5cbdf94834"
)

TARGET_ID = "H4-0751"
TARGET_CHAR = "呀"
TARGET_PINYIN = "ya"


def clean(value):
    return (value or "").strip()


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def render_csv_bytes(fields, rows):

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


def main():

    print("=" * 78)
    print("BUOC 20G - CHOT PINYIN 300 CHU HAN HSK4")
    print("=" * 78)

    print(
        "KHONG GHI SQL - "
        "KHONG GAN BAI HOC - "
        "KHONG TAO AUDIO - "
        "KHONG SUA CAU TRUC"
    )

    # ========================================================
    # 1. KIEM TRA SNAPSHOT
    # ========================================================

    print("\n[1] KIEM TRA SNAPSHOT 20F")

    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay:\n{SOURCE}"
        )

    source_hash = sha256_file(SOURCE)

    print("SOURCE SHA256:")
    print(source_hash)

    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            "FAIL: snapshot 20F khong khop.\n"
            f"Expected: {EXPECTED_SOURCE_SHA256}\n"
            f"Actual:   {source_hash}"
        )

    print("PASS: snapshot 20F hop le.")

    # ========================================================
    # 2. DOC DU LIEU
    # ========================================================

    print("\n[2] DOC 300 DONG")

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        fields = list(reader.fieldnames or [])
        rows = list(reader)

    if len(rows) != 300:
        raise RuntimeError(
            f"FAIL: can 300 dong, thuc te {len(rows)}"
        )

    required = {
        "MaChuHanTam",
        "KyTu",
        "PinyinChot20F",
        "NghiaTiengVietChot20F",
        "CanKiemTraPinyinSau20F",
        "PinyinDeXuat",
        "PinyinGFDon",
        "PinyinUnihanRaw",
        "PinyinMakeMeAHanzi",
        "CacCachDocCEDICT",
    }

    missing = required - set(fields)

    if missing:
        raise RuntimeError(
            "FAIL: thieu cot:\n"
            + "\n".join(sorted(missing))
        )

    ids = [
        clean(r["MaChuHanTam"])
        for r in rows
    ]

    chars = [
        clean(r["KyTu"])
        for r in rows
    ]

    if len(set(ids)) != 300:
        raise RuntimeError(
            "FAIL: MaChuHanTam khong duy nhat."
        )

    if len(set(chars)) != 300:
        raise RuntimeError(
            "FAIL: KyTu khong duy nhat."
        )

    print("PASS: 300 ID duy nhat.")
    print("PASS: 300 KyTu duy nhat.")

    # ========================================================
    # 3. TIM TARGET 呀
    # ========================================================

    print("\n[3] KIEM TRA TARGET CUOI CUNG")

    targets = [
        r
        for r in rows
        if clean(r["MaChuHanTam"]) == TARGET_ID
    ]

    if len(targets) != 1:
        raise RuntimeError(
            f"FAIL: {TARGET_ID} phai xuat hien dung 1 lan."
        )

    target = targets[0]

    if clean(target["KyTu"]) != TARGET_CHAR:
        raise RuntimeError(
            f"FAIL: {TARGET_ID} khong phai chu {TARGET_CHAR}."
        )

    print("MaChuHanTam:", clean(target["MaChuHanTam"]))
    print("KyTu:", clean(target["KyTu"]))
    print("PinyinDeXuat:", clean(target["PinyinDeXuat"]))
    print("PinyinGFDon:", clean(target["PinyinGFDon"]))
    print("PinyinUnihanRaw:", clean(target["PinyinUnihanRaw"]))
    print(
        "PinyinMakeMeAHanzi:",
        clean(target["PinyinMakeMeAHanzi"]),
    )
    print(
        "CacCachDocCEDICT:",
        clean(target["CacCachDocCEDICT"]),
    )

    if clean(target["PinyinDeXuat"]) != "ya":
        raise RuntimeError(
            "FAIL: PinyinDeXuat cua 呀 khong phai ya."
        )

    if clean(target["PinyinGFDon"]) != "ya":
        raise RuntimeError(
            "FAIL: GF0025 cua 呀 khong phai ya."
        )

    if clean(target["PinyinUnihanRaw"]) != "ya":
        raise RuntimeError(
            "FAIL: Unihan cua 呀 khong phai ya."
        )

    if clean(target["PinyinMakeMeAHanzi"]) != "ya":
        raise RuntimeError(
            "FAIL: Make Me a Hanzi cua 呀 khong phai ya."
        )

    cedict_readings = clean(
        target["CacCachDocCEDICT"]
    )

    if "ya5" not in cedict_readings:
        raise RuntimeError(
            "FAIL: CC-CEDICT khong co ya5 "
            "de doi chieu thanh nhe."
        )

    print(
        "PASS: du nguon de chot 呀 = ya "
        "(thanh nhe cho muc HSK4 nay)."
    )

    # ========================================================
    # 4. THEM CAC COT 20G
    # ========================================================

    print("\n[4] CHOT PINYIN 300 DONG")

    extra_fields = [
        "PinyinChot20G",
        "TrangThaiPinyin20G",
        "NguonChotPinyin20G",
        "GhiChuPinyin20G",
    ]

    output_fields = list(fields)

    for field in extra_fields:
        if field not in output_fields:
            output_fields.append(field)

    output_rows = []

    patched = 0

    for source_row in rows:

        row = dict(source_row)

        mid = clean(
            row["MaChuHanTam"]
        )

        char = clean(
            row["KyTu"]
        )

        if mid == TARGET_ID:

            if char != TARGET_CHAR:
                raise RuntimeError(
                    f"FAIL: target {TARGET_ID} sai KyTu."
                )

            row["PinyinChot20G"] = TARGET_PINYIN

            row["TrangThaiPinyin20G"] = (
                "DA_CHOT_20G"
            )

            row["NguonChotPinyin20G"] = (
                "GF0025 + Unihan + Make Me a Hanzi "
                "+ CC-CEDICT ya5"
            )

            row["GhiChuPinyin20G"] = (
                "Chot ya thanh nhe theo muc HSK4 cua du an. "
                "CC-CEDICT co ya1 va ya5; "
                "GF0025, Unihan va Make Me a Hanzi "
                "deu ho tro ya."
            )

            patched += 1

        else:

            old_pinyin = clean(
                row["PinyinChot20F"]
            )

            if not old_pinyin:
                raise RuntimeError(
                    f"FAIL: thieu Pinyin tai {mid}|{char}"
                )

            row["PinyinChot20G"] = old_pinyin

            row["TrangThaiPinyin20G"] = (
                "GIU_NGUYEN_20F"
            )

            row["NguonChotPinyin20G"] = (
                "Ke thua PinyinChot20F"
            )

            row["GhiChuPinyin20G"] = (
                "Khong thay doi tai Buoc 20G."
            )

        output_rows.append(row)

    if patched != 1:
        raise RuntimeError(
            f"FAIL: so dong patch = {patched}, mong doi 1."
        )

    print("PASS: chi patch 1 dong H4-0751 | 呀.")

    # ========================================================
    # 5. KIEM TRA SAU CHOT
    # ========================================================

    print("\n[5] KIEM TRA 300/300")

    missing_pinyin = []

    for row in output_rows:

        if not clean(
            row["PinyinChot20G"]
        ):
            missing_pinyin.append(
                f"{clean(row['MaChuHanTam'])}"
                f"|{clean(row['KyTu'])}"
            )

    if missing_pinyin:
        raise RuntimeError(
            "FAIL: con thieu Pinyin:\n"
            + "\n".join(missing_pinyin)
        )

    unresolved = [
        r
        for r in output_rows
        if clean(
            r["TrangThaiPinyin20G"]
        ) == "CAN_REVIEW"
    ]

    if unresolved:
        raise RuntimeError(
            "FAIL: van con dong CAN_REVIEW sau 20G."
        )

    final_target = [
        r
        for r in output_rows
        if clean(r["MaChuHanTam"]) == TARGET_ID
    ][0]

    if clean(
        final_target["PinyinChot20G"]
    ) != TARGET_PINYIN:
        raise RuntimeError(
            "FAIL: target 呀 chua duoc chot thanh ya."
        )

    print("PASS: 300/300 co Pinyin chot.")
    print("PASS: 呀 = ya.")
    print("PASS: khong con Pinyin can review.")

    # ========================================================
    # 6. DAM BAO KHONG SUA NGHIA
    # ========================================================

    print("\n[6] KIEM TRA NGHIA KHONG BI SUA")

    missing_meaning = []

    for row in output_rows:

        meaning = clean(
            row["NghiaTiengVietChot20F"]
        )

        if not meaning:
            missing_meaning.append(
                f"{clean(row['MaChuHanTam'])}"
                f"|{clean(row['KyTu'])}"
            )

    if missing_meaning:
        raise RuntimeError(
            "FAIL: thieu nghia:\n"
            + "\n".join(missing_meaning)
        )

    print("PASS: 300/300 van co nghia.")
    print("PASS: 20G khong thay doi cot nghia 20F.")

    # ========================================================
    # 7. CHUAN BI OUTPUT
    # ========================================================

    print("\n[7] CHUAN BI OUTPUT")

    output_bytes = render_csv_bytes(
        output_fields,
        output_rows,
    )

    new_hash = sha256_bytes(
        output_bytes
    )

    # ========================================================
    # 8. GHI OUTPUT AN TOAN
    # ========================================================

    print("\n[8] GHI OUTPUT")

    if OUTPUT.exists():

        existing_bytes = OUTPUT.read_bytes()

        if existing_bytes != output_bytes:

            raise RuntimeError(
                "FAIL: output 20G da ton tai "
                "nhung noi dung khac.\n"
                f"Existing SHA256: "
                f"{sha256_bytes(existing_bytes)}\n"
                f"Current SHA256:  {new_hash}\n"
                "KHONG GHI DE."
            )

        print(
            "PASS: output da ton tai va giong het, "
            "khong ghi lai."
        )

    else:

        with OUTPUT.open("xb") as f:
            f.write(output_bytes)

        print("PASS: da tao output moi.")

    final_hash = sha256_file(OUTPUT)

    if final_hash != new_hash:
        raise RuntimeError(
            "FAIL: hash output sau ghi khong khop."
        )

    # ========================================================
    # 9. SUMMARY
    # ========================================================

    summary_data = {

        "buoc": "20G",

        "status": "PASS",

        "tong": 300,

        "pinyin_day_du": 300,

        "nghia_day_du": 300,

        "pinyin_can_review_con_lai": 0,

        "patch": {
            "MaChuHanTam": TARGET_ID,
            "KyTu": TARGET_CHAR,
            "PinyinCu": clean(
                target["PinyinChot20F"]
            ),
            "PinyinChot": TARGET_PINYIN,
            "ly_do": (
                "GF0025=ya; Unihan=ya; "
                "Make Me a Hanzi=ya; "
                "CC-CEDICT co ya5 "
                "(thanh nhe) va ya1."
            ),
        },

        "source20f_sha256": source_hash,

        "output": str(OUTPUT),

        "output_sha256": final_hash,

        "ghi_sql": False,

        "gan_bai_hoc": False,

        "tao_audio": False,

        "xu_ly_cau_truc": False,
    }

    summary_text = (
        json.dumps(
            summary_data,
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )

    if SUMMARY.exists():

        existing_summary = SUMMARY.read_text(
            encoding="utf-8"
        )

        if existing_summary != summary_text:
            raise RuntimeError(
                "FAIL: summary 20G da ton tai "
                "nhung noi dung khac. "
                "KHONG GHI DE."
            )

        print("PASS: summary da ton tai va khop.")

    else:

        SUMMARY.write_text(
            summary_text,
            encoding="utf-8",
        )

        print("PASS: da tao summary.")

    # ========================================================
    # 10. KET THUC
    # ========================================================

    print("\n" + "=" * 78)
    print("PASS: BUOC 20G HOAN THANH")
    print("=" * 78)

    print("Tong chu:", 300)
    print("Pinyin day du:", 300)
    print("Nghia day du:", 300)
    print("Pinyin can review con lai:", 0)

    print("\nDA CHOT:")
    print("H4-0751 | 呀 | ya")

    print("\nOUTPUT:")
    print(OUTPUT)

    print("SHA256:")
    print(final_hash)

    print("\nSUMMARY:")
    print(SUMMARY)

    print("\nKHONG GHI SQL.")
    print("KHONG GAN BAI HOC.")
    print("KHONG TAO AUDIO.")
    print("CHUA XU LY 28 VAN DE CAU TRUC.")

    print("=" * 78)


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print("\nFAIL:", exc)

        raise SystemExit(1)