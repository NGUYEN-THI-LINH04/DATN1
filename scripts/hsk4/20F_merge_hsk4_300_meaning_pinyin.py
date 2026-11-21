# -*- coding: utf-8 -*-

"""
BUOC 20F - GHEP 300 CHU HAN HSK4 SAU REVIEW NGHIA

Muc tieu:
1. Doc 300 dong tu Buoc 20B.
2. Doc 182 dong da review tai Buoc 20E.
3. Ghep:
   - 182 dong: dung Pinyin/Nghia da chot tai 20E.
   - 118 dong con lai: giu Pinyin/Nghia da co tu 20B.
4. Kiem tra 300/300 deu co nghia.
5. Tim Pinyin con can review nam NGOAI pack 182.

KHONG GHI SQL.
KHONG GAN BAI HOC.
KHONG TAO AUDIO.
KHONG SUA CAU TRUC CHU HAN.
"""

import csv
import hashlib
import io
import json
from pathlib import Path


# ============================================================
# DUONG DAN
# ============================================================

ROOT = Path(r"D:\DATN1")

PROCESSED = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

SOURCE_20B = (
    PROCESSED
    / "hanzi_hsk4_300_cvdict_rebuilt.csv"
)

SOURCE_20E = (
    PROCESSED
    / "hanzi_hsk4_182_meaning_reviewed_internal.csv"
)

OUTPUT = (
    PROCESSED
    / "hanzi_hsk4_300_meaning_pinyin_merged_20F.csv"
)

SUMMARY = (
    PROCESSED
    / "hanzi_hsk4_300_meaning_pinyin_merged_20F_summary.json"
)


# ============================================================
# SNAPSHOT DA PIN
# ============================================================

EXPECTED_20B_SHA256 = (
    "6c6530445117477bb27a2222fd358f30"
    "ee74f9c6ee54c3b9bbf65a00c8f68712"
)

EXPECTED_20E_SHA256 = (
    "fd5c9c22ff8e4f2ab1d1dbf35934a777"
    "7de6df174405986d519bdc1a50bc94c2"
)


# ============================================================
# HAM CHUNG
# ============================================================

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


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        fields = list(reader.fieldnames or [])
        rows = list(reader)

    return fields, rows


def clean(value):
    return (value or "").strip()


def render_csv_bytes(fields, rows):
    """
    Tao bytes CSV truoc trong RAM de:
    - co the so sanh neu output da ton tai
    - khong ghi de file cu ngoai y muon
    """

    buffer = io.StringIO(newline="")

    writer = csv.DictWriter(
        buffer,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )

    writer.writeheader()
    writer.writerows(rows)

    text = buffer.getvalue()

    # utf-8-sig = BOM + UTF-8
    return text.encode("utf-8-sig")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 78)
    print("BUOC 20F - GHEP 300 CHU HAN HSK4 SAU REVIEW NGHIA/PINYIN")
    print("=" * 78)

    print(
        "CHI DOC CSV NGUON - "
        "KHONG GHI SQL - "
        "KHONG GAN BAI HOC - "
        "KHONG TAO AUDIO"
    )

    # ========================================================
    # 1. KIEM TRA SNAPSHOT
    # ========================================================

    print("\n[1] KIEM TRA SNAPSHOT")

    if not SOURCE_20B.is_file():
        raise FileNotFoundError(
            f"Khong tim thay 20B:\n{SOURCE_20B}"
        )

    if not SOURCE_20E.is_file():
        raise FileNotFoundError(
            f"Khong tim thay 20E:\n{SOURCE_20E}"
        )

    hash20b = sha256_file(SOURCE_20B)
    hash20e = sha256_file(SOURCE_20E)

    print("STEP20B SHA256:")
    print(hash20b)

    print("STEP20E SHA256:")
    print(hash20e)

    if hash20b != EXPECTED_20B_SHA256:
        raise RuntimeError(
            "FAIL: snapshot 20B khong khop.\n"
            f"Expected: {EXPECTED_20B_SHA256}\n"
            f"Actual:   {hash20b}"
        )

    if hash20e != EXPECTED_20E_SHA256:
        raise RuntimeError(
            "FAIL: snapshot 20E khong khop.\n"
            f"Expected: {EXPECTED_20E_SHA256}\n"
            f"Actual:   {hash20e}"
        )

    print("PASS: 20B va 20E dung snapshot.")

    # ========================================================
    # 2. DOC DU LIEU
    # ========================================================

    print("\n[2] DOC DU LIEU")

    fields20b, rows20b = read_csv(SOURCE_20B)
    fields20e, rows20e = read_csv(SOURCE_20E)

    print("Buoc 20B:", len(rows20b))
    print("Buoc 20E:", len(rows20e))

    if len(rows20b) != 300:
        raise RuntimeError(
            f"FAIL: 20B phai co 300 dong, "
            f"thuc te {len(rows20b)}"
        )

    if len(rows20e) != 182:
        raise RuntimeError(
            f"FAIL: 20E phai co 182 dong, "
            f"thuc te {len(rows20e)}"
        )

    # ========================================================
    # 3. KIEM TRA CAC COT BAT BUOC
    # ========================================================

    print("\n[3] KIEM TRA HEADER")

    required20b = {
        "MaChuHanTam",
        "KyTu",
        "PinyinDeXuat",
        "TrangThaiPinyin",
        "CanKiemTraPinyin",
        "NghiaTiengVietSauCVDICT",
        "NguonNghiaSauCVDICT",
    }

    required20e = {
        "MaChuHanTam",
        "KyTu",
        "PinyinChot20E",
        "NghiaTiengVietChot20E",
        "NguonChot20E",
        "TrangThai20E",
        "GhiChu20E",
    }

    missing20b = required20b - set(fields20b)
    missing20e = required20e - set(fields20e)

    if missing20b:
        raise RuntimeError(
            "FAIL: 20B thieu cot:\n"
            + "\n".join(sorted(missing20b))
        )

    if missing20e:
        raise RuntimeError(
            "FAIL: 20E thieu cot:\n"
            + "\n".join(sorted(missing20e))
        )

    print("PASS: header 20B hop le.")
    print("PASS: header 20E hop le.")

    # ========================================================
    # 4. TAO MAP 20E
    # ========================================================

    print("\n[4] TAO MAP 182 DONG 20E")

    review_map = {}

    for row in rows20e:

        mid = clean(row["MaChuHanTam"])
        char = clean(row["KyTu"])

        if not mid:
            raise RuntimeError(
                "FAIL: 20E co MaChuHanTam rong."
            )

        if mid in review_map:
            raise RuntimeError(
                f"FAIL: trung MaChuHanTam trong 20E: {mid}"
            )

        if not char:
            raise RuntimeError(
                f"FAIL: KyTu rong tai {mid}"
            )

        if not clean(row["PinyinChot20E"]):
            raise RuntimeError(
                f"FAIL: PinyinChot20E rong tai {mid}"
            )

        if not clean(row["NghiaTiengVietChot20E"]):
            raise RuntimeError(
                f"FAIL: NghiaTiengVietChot20E rong tai {mid}"
            )

        review_map[mid] = row

    if len(review_map) != 182:
        raise RuntimeError(
            "FAIL: review_map khong du 182."
        )

    print("PASS: map 20E = 182.")

    # ========================================================
    # 5. KIEM TRA 20B <-> 20E
    # ========================================================

    print("\n[5] DOI CHIEU 20B <-> 20E")

    base_map = {}

    for row in rows20b:

        mid = clean(row["MaChuHanTam"])

        if not mid:
            raise RuntimeError(
                "FAIL: 20B co MaChuHanTam rong."
            )

        if mid in base_map:
            raise RuntimeError(
                f"FAIL: trung MaChuHanTam trong 20B: {mid}"
            )

        base_map[mid] = row

    if len(base_map) != 300:
        raise RuntimeError(
            "FAIL: 20B khong co 300 ID duy nhat."
        )

    for mid, r20e in review_map.items():

        if mid not in base_map:
            raise RuntimeError(
                f"FAIL: {mid} co trong 20E "
                "nhung khong co trong 20B."
            )

        char20b = clean(
            base_map[mid]["KyTu"]
        )

        char20e = clean(
            r20e["KyTu"]
        )

        if char20b != char20e:
            raise RuntimeError(
                f"FAIL: KyTu khong khop tai {mid}: "
                f"20B={char20b}, "
                f"20E={char20e}"
            )

    print("PASS: 182/182 mapping 20E khop 20B.")

    # ========================================================
    # 6. THEM COT KET QUA 20F
    # ========================================================

    print("\n[6] GHEP 300 DONG")

    extra_fields = [
        "PinyinChot20F",
        "NghiaTiengVietChot20F",
        "NguonNghiaChot20F",
        "NguonDong20F",
        "TrangThaiPinyinSau20F",
        "CanKiemTraPinyinSau20F",
        "GhiChu20F",
    ]

    output_fields = list(fields20b)

    for field in extra_fields:
        if field not in output_fields:
            output_fields.append(field)

    output_rows = []

    count_20e = 0
    count_preserved = 0

    for source_row in rows20b:

        row = dict(source_row)

        mid = clean(
            row["MaChuHanTam"]
        )

        if mid in review_map:

            r20e = review_map[mid]

            row["PinyinChot20F"] = clean(
                r20e["PinyinChot20E"]
            )

            row["NghiaTiengVietChot20F"] = clean(
                r20e["NghiaTiengVietChot20E"]
            )

            row["NguonNghiaChot20F"] = clean(
                r20e["NguonChot20E"]
            )

            row["NguonDong20F"] = (
                "REVIEW_20E"
            )

            row["TrangThaiPinyinSau20F"] = (
                "DA_CHOT_QUA_REVIEW_20E"
            )

            row["CanKiemTraPinyinSau20F"] = (
                "KHONG"
            )

            row["GhiChu20F"] = clean(
                r20e["GhiChu20E"]
            )

            count_20e += 1

        else:

            pinyin = clean(
                row["PinyinDeXuat"]
            )

            meaning = clean(
                row["NghiaTiengVietSauCVDICT"]
            )

            if not pinyin:
                raise RuntimeError(
                    f"FAIL: dong ngoai 20E thieu Pinyin: "
                    f"{mid} | {clean(row['KyTu'])}"
                )

            if not meaning:
                raise RuntimeError(
                    f"FAIL: dong ngoai 20E thieu nghia: "
                    f"{mid} | {clean(row['KyTu'])}"
                )

            row["PinyinChot20F"] = pinyin

            row["NghiaTiengVietChot20F"] = meaning

            row["NguonNghiaChot20F"] = clean(
                row["NguonNghiaSauCVDICT"]
            )

            row["NguonDong20F"] = (
                "GIU_NGUYEN_20B"
            )

            row["TrangThaiPinyinSau20F"] = clean(
                row["TrangThaiPinyin"]
            )

            row["CanKiemTraPinyinSau20F"] = clean(
                row["CanKiemTraPinyin"]
            )

            row["GhiChu20F"] = (
                "Giu nguyen dong da co nghia "
                "truoc pack review 182."
            )

            count_preserved += 1

        output_rows.append(row)

    if count_20e != 182:
        raise RuntimeError(
            f"FAIL: so dong lay tu 20E = {count_20e}, "
            "mong doi 182."
        )

    if count_preserved != 118:
        raise RuntimeError(
            f"FAIL: so dong giu tu 20B = "
            f"{count_preserved}, mong doi 118."
        )

    print("Lay ket qua 20E:", count_20e)
    print("Giu nguyen tu 20B:", count_preserved)

    # ========================================================
    # 7. KIEM TRA 300/300 NGHIA + PINYIN
    # ========================================================

    print("\n[7] KIEM TRA KET QUA 300")

    missing_pinyin = []
    missing_meaning = []

    for row in output_rows:

        mid = clean(
            row["MaChuHanTam"]
        )

        char = clean(
            row["KyTu"]
        )

        if not clean(
            row["PinyinChot20F"]
        ):
            missing_pinyin.append(
                f"{mid}|{char}"
            )

        if not clean(
            row["NghiaTiengVietChot20F"]
        ):
            missing_meaning.append(
                f"{mid}|{char}"
            )

    if missing_pinyin:
        raise RuntimeError(
            "FAIL: con thieu Pinyin:\n"
            + "\n".join(missing_pinyin)
        )

    if missing_meaning:
        raise RuntimeError(
            "FAIL: con thieu nghia:\n"
            + "\n".join(missing_meaning)
        )

    if len(output_rows) != 300:
        raise RuntimeError(
            f"FAIL: output co {len(output_rows)} dong."
        )

    chars = [
        clean(r["KyTu"])
        for r in output_rows
    ]

    if len(set(chars)) != 300:
        raise RuntimeError(
            "FAIL: KyTu trong output khong duy nhat."
        )

    print("PASS: 300/300 co Pinyin.")
    print("PASS: 300/300 co nghia.")
    print("PASS: 300 KyTu duy nhat.")

    # ========================================================
    # 8. TIM PINYIN CON CAN REVIEW NGOAI PACK 182
    # ========================================================

    print(
        "\n[8] TIM PINYIN CON CAN REVIEW NGOAI PACK 182"
    )

    unresolved = []

    for row in output_rows:

        if row["NguonDong20F"] != "GIU_NGUYEN_20B":
            continue

        flag = clean(
            row["CanKiemTraPinyinSau20F"]
        ).upper()

        if flag == "CO":

            unresolved.append(row)

    print(
        "So dong Pinyin con can review ngoai pack 182:",
        len(unresolved),
    )

    # Theo audit truoc:
    # tong Pinyin can review = 5
    # trong pack 182 = 4
    # nen ngoai pack 182 phai con 1
    if len(unresolved) != 1:

        print("\nCAC DONG PHAT HIEN:")

        for row in unresolved:

            print(
                clean(row["MaChuHanTam"]),
                "|",
                clean(row["KyTu"]),
                "|",
                clean(row["PinyinDeXuat"]),
                "|",
                clean(row["TrangThaiPinyin"]),
            )

        raise RuntimeError(
            "FAIL: mong doi dung 1 Pinyin "
            "can review ngoai pack 182."
        )

    print("\nPINYIN CAN REVIEW CUOI CUNG:")

    for row in unresolved:

        print(
            "MaChuHanTam:",
            clean(row["MaChuHanTam"]),
        )

        print(
            "KyTu:",
            clean(row["KyTu"]),
        )

        print(
            "PinyinDeXuat:",
            clean(row.get("PinyinDeXuat")),
        )

        print(
            "TrangThaiPinyin:",
            clean(row.get("TrangThaiPinyin")),
        )

        print(
            "CanKiemTraPinyin:",
            clean(row.get("CanKiemTraPinyin")),
        )

        print(
            "TuVungDaiDien:",
            clean(row.get("TuVungDaiDien")),
        )

        print(
            "PinyinTuDaiDien:",
            clean(row.get("PinyinTuDaiDien")),
        )

        print(
            "PinyinGFDon:",
            clean(row.get("PinyinGFDon")),
        )

        print(
            "PinyinUnihanRaw:",
            clean(row.get("PinyinUnihanRaw")),
        )

        print(
            "PinyinMakeMeAHanzi:",
            clean(row.get("PinyinMakeMeAHanzi")),
        )

        print(
            "CacCachDocCEDICT:",
            clean(row.get("CacCachDocCEDICT")),
        )

    # ========================================================
    # 9. TAO BYTES OUTPUT TRONG RAM
    # ========================================================

    print("\n[9] CHUAN BI OUTPUT")

    output_bytes = render_csv_bytes(
        output_fields,
        output_rows,
    )

    expected_new_hash = sha256_bytes(
        output_bytes
    )

    # ========================================================
    # 10. GHI FILE AN TOAN
    # ========================================================

    print("\n[10] GHI FILE")

    if OUTPUT.exists():

        existing_bytes = OUTPUT.read_bytes()

        existing_hash = sha256_bytes(
            existing_bytes
        )

        if existing_bytes != output_bytes:

            raise RuntimeError(
                "FAIL: output 20F da ton tai "
                "nhung noi dung khac.\n"
                f"Existing SHA256: {existing_hash}\n"
                f"Current  SHA256: {expected_new_hash}\n"
                "KHONG GHI DE."
            )

        print(
            "PASS: output da ton tai va "
            "noi dung giong het, khong ghi lai."
        )

    else:

        with OUTPUT.open("xb") as f:
            f.write(output_bytes)

        print("PASS: da tao output moi.")

    final_hash = sha256_file(
        OUTPUT
    )

    if final_hash != expected_new_hash:
        raise RuntimeError(
            "FAIL: hash output sau khi ghi khong khop."
        )

    # ========================================================
    # 11. SUMMARY
    # ========================================================

    candidate = unresolved[0]

    summary_data = {

        "buoc": "20F",

        "status": "PASS",

        "tong": 300,

        "lay_tu_20E": 182,

        "giu_nguyen_tu_20B": 118,

        "thieu_pinyin": 0,

        "thieu_nghia": 0,

        "pinyin_con_can_review_ngoai_182": 1,

        "candidate_pinyin_review": {
            "MaChuHanTam": clean(
                candidate["MaChuHanTam"]
            ),
            "KyTu": clean(
                candidate["KyTu"]
            ),
            "PinyinDeXuat": clean(
                candidate.get("PinyinDeXuat")
            ),
            "TrangThaiPinyin": clean(
                candidate.get("TrangThaiPinyin")
            ),
            "TuVungDaiDien": clean(
                candidate.get("TuVungDaiDien")
            ),
            "PinyinTuDaiDien": clean(
                candidate.get("PinyinTuDaiDien")
            ),
        },

        "source20b_sha256": hash20b,

        "source20e_sha256": hash20e,

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

        old_summary = SUMMARY.read_text(
            encoding="utf-8"
        )

        if old_summary != summary_text:

            raise RuntimeError(
                "FAIL: summary 20F da ton tai "
                "nhung noi dung khac. "
                "KHONG GHI DE."
            )

        print(
            "PASS: summary da ton tai va khop."
        )

    else:

        SUMMARY.write_text(
            summary_text,
            encoding="utf-8",
        )

        print("PASS: da tao summary.")

    # ========================================================
    # 12. KET THUC
    # ========================================================

    print("\n" + "=" * 78)
    print("PASS: BUOC 20F HOAN THANH")
    print("=" * 78)

    print("Tong:", 300)
    print("Lay tu review 20E:", 182)
    print("Giu nguyen 20B:", 118)
    print("Thieu Pinyin:", 0)
    print("Thieu nghia:", 0)

    print(
        "Pinyin con can review ngoai pack 182:",
        1,
    )

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