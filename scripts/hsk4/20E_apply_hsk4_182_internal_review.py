# -*- coding: utf-8 -*-

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1")
PROCESSED = ROOT / "scripts" / "hsk4" / "data" / "processed"

SOURCE = PROCESSED / "hanzi_hsk4_182_meaning_review_proposed.csv"
OUTPUT = PROCESSED / "hanzi_hsk4_182_meaning_reviewed_internal.csv"
SUMMARY = PROCESSED / "hanzi_hsk4_182_meaning_reviewed_internal_summary.json"

EXPECTED_SOURCE_SHA256 = (
    "846848de877623616df2c956e8671e1834dbeb2dd4f35ff14be0ef00f1c9244e"
)

EXPECTED_OUTPUT_SHA256 = (
    "fd5c9c22ff8e4f2ab1d1dbf35934a7777de6df174405986d519bdc1a50bc94c2"
)

OVERRIDES = {
    "H4-0001": (
        "ā",
        "tiền tố thân mật trước tên hoặc cách gọi người thân",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 阿姨",
        "Không dịch chữ đơn 阿 thành 'dì'; trong 阿姨, 阿 là tiền tố/cấu tố thân mật.",
    ),

    "H4-0015": (
        "bā",
        "mong muốn; bám/dính; trong 巴士 là âm phiên âm/viết tắt xe buýt",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 巴士",
        "Không đồng nhất nghĩa chữ 巴 với toàn từ 巴士.",
    ),

    "H4-0016": (
        "shì",
        "học giả; binh sĩ; người có chuyên môn",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 巴士",
        "Trong 巴士, 士 tham gia cấu tạo từ mượn; nghĩa chữ độc lập không phải 'xe buýt'.",
    ),

    "H4-0028": (
        "kuò",
        "bao gồm; bao quát",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 包括",
        "Giữ cách đọc kuò theo 包括; không đưa guā vào nghĩa chính.",
    ),

    "H4-0042": (
        "pò",
        "ép buộc; thúc ép; cấp bách",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 被迫",
        "Loại nghĩa nhiễu từ mục biến thể 廹 迫 trong CVDICT.",
    ),

    "H4-0060": (
        "yáng",
        "nâng/giương; truyền bá; khen ngợi",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 表扬",
        "Chọn các nghĩa phổ biến, không lấy mục họ riêng.",
    ),

    "H4-0089": (
        "cāo",
        "vận hành; điều khiển; luyện tập",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 操场",
        "Loại cách đọc/nội dung tục không liên quan đến mục HSK4.",
    ),

    "H4-0097": (
        "yè",
        "lá; trang",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 茶叶",
        "CVDICT lệch sang xie2; chọn yè theo 茶叶 và nguồn chữ.",
    ),

    "H4-0122": (
        "chéng",
        "đảm nhận; gánh vác; tiếp nhận",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 承担",
        "Loại mục họ riêng.",
    ),

    "H4-0147": (
        "xí",
        "chiếu; chỗ ngồi; tiệc",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 出席",
        "Không dùng 'tham dự' làm nghĩa chữ đơn; đó là nghĩa của cụm 出席.",
    ),

    "H4-0177": (
        "shī",
        "thi hành; thực hiện; áp dụng",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 措施",
        "Loại mục họ riêng.",
    ),

    "H4-0190": (
        "mó",
        "mô hình; mẫu; khuôn mẫu",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 大规模",
        "Đa âm mó/mú; chọn mó theo 规模 guīmó.",
    ),

    "H4-0194": (
        "lù",
        "đất liền; lục địa",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 大陆",
        "Đa âm lù/liù; chọn lù theo 大陆 dàlù.",
    ),

    "H4-0273": (
        "lǜ",
        "luật; quy luật; quy tắc",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 法律",
        "Giữ lǜ; không dùng nghĩa thuộc cách đọc khác.",
    ),

    "H4-0289": (
        "dòu",
        "đấu tranh; chiến đấu",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 奋斗",
        "CVDICT chỉ có mục dǒu trong tập exact-char; chọn dòu theo 奋斗.",
    ),

    "H4-0297": (
        "fù",
        "phụ nữ; người vợ",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 夫妇",
        "Loại mục biến thể cũ.",
    ),

    "H4-0317": (
        "shàng",
        "vẫn còn; coi trọng; tôn trọng",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 高尚",
        "Loại mục họ riêng.",
    ),

    "H4-0369": (
        "hū",
        "gọi; hô; thở ra",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 呼吸",
        "Gộp nghĩa phổ biến tương ứng cách đọc hū.",
    ),

    "H4-0375": (
        "huái",
        "mang trong lòng; nhớ nghĩ; ôm ấp",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 怀念",
        "Loại mục họ riêng.",
    ),

    "H4-0384": (
        "lǜ",
        "tỷ lệ; suất",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 汇率",
        "Đa âm lǜ/shuài; chọn lǜ theo 汇率. Không giữ nghĩa 'dẫn dắt' vì thuộc shuài.",
    ),

    "H4-0406": (
        "zǎi",
        "ghi chép; ghi lại",
        "CC-CEDICT + ngữ cảnh 记载",
        "SỬA pinyin đề xuất zài -> zǎi theo 记载 jìzǎi; nghĩa chở/tải thuộc zài.",
    ),

    "H4-0464": (
        "jū",
        "cư trú; ở; nơi ở",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 居民",
        "Loại cách đọc cổ ji1 và mục họ.",
    ),

    "H4-0474": (
        "juǎn",
        "cuộn; cuộn lại; cuốn theo",
        "GF0025 + CC-CEDICT + Make Me a Hanzi + CVDICT + mục HSK4 卷",
        "Đa âm juǎn/juàn; chọn juǎn theo mục HSK4. Không giữ nghĩa 'quyển/sách' vì thuộc juàn.",
    ),

    "H4-0496": (
        "lā",
        "dùng trong 垃圾 (rác)",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 垃圾",
        "Chữ hầu như dùng như cấu tố trong 垃圾 ở ngữ cảnh này.",
    ),

    "H4-0497": (
        "jī",
        "dùng trong 垃圾 (rác)",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 垃圾",
        "Chữ hầu như dùng như cấu tố trong 垃圾 ở ngữ cảnh này.",
    ),

    "H4-0508": (
        "shǐ",
        "lịch sử; sử sách",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 历史",
        "Loại mục họ riêng.",
    ),

    "H4-0532": (
        "mào",
        "mũ; nón",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 帽子",
        "Loại mục biến thể cũ.",
    ),

    "H4-0559": (
        "níng",
        "yên ổn; yên tĩnh",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 宁静",
        "Đa âm níng/nìng; chọn níng theo 宁静.",
    ),

    "H4-0577": (
        "yú",
        "còn dư; phần còn lại; dư thừa",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 其余",
        "Ưu tiên nghĩa hiện đại phù hợp 其余; loại mục họ.",
    ),

    "H4-0621": (
        "shèn",
        "rất; quá mức; thậm chí",
        "CC-CEDICT + Make Me a Hanzi + ngữ cảnh 甚至",
        "SỬA pinyin trống -> shèn theo 甚至 shènzhì.",
    ),

    "H4-0659": (
        "sūn",
        "cháu; hậu duệ",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 孙女",
        "Không giới hạn nghĩa chữ đơn thành riêng 'cháu nội'.",
    ),

    "H4-0665": (
        "zhēng",
        "dấu hiệu; đặc trưng; chinh phạt; trưng thu",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 特征",
        "Giữ nghĩa 'dấu hiệu/đặc trưng' phù hợp 特征, đồng thời bảo lưu các nghĩa chữ phổ biến.",
    ),

    "H4-0670": (
        "tiāo",
        "chọn; lựa; gánh bằng đòn gánh; bới móc",
        "GF0025 + CC-CEDICT + Make Me a Hanzi + CVDICT + mục HSK4 挑",
        "Đa âm tiāo/tiǎo; chọn tiāo theo mục HSK4.",
    ),

    "H4-0696": (
        "wēi",
        "nhỏ bé; vi mô; hơi/nhẹ",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 微笑",
        "Loại mục họ riêng.",
    ),

    "H4-0724": (
        "zhù",
        "nổi bật; rõ rệt; viết; tác phẩm",
        "CC-CEDICT + Unihan + ngữ cảnh 显著",
        "SỬA pinyin zhe -> zhù theo 显著 xiǎnzhù; không dùng zhe cho mục này.",
    ),

    "H4-0749": (
        "yà",
        "châu Á; thứ hai/kém hơn; á-",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 亚运会",
        "Giữ yà theo 亚运会.",
    ),

    "H4-0752": (
        "yán",
        "kéo dài; trì hoãn",
        "CC-CEDICT + Make Me a Hanzi + CVDICT + ngữ cảnh 延长",
        "Loại mục họ riêng.",
    ),
}


EXTRA_FIELDS = [
    "PinyinChot20E",
    "NghiaTiengVietChot20E",
    "NguonChot20E",
    "TrangThai20E",
    "GhiChu20E",
]


def sha256_file(path):
    h = hashlib.sha256()

    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)

    return h.hexdigest()


def main():

    print("=" * 72)
    print("BUOC 20E - REVIEW NOI BO 182 CHU HAN HSK4")
    print("=" * 72)
    print("KHONG GHI SQL - KHONG GAN BAI HOC - KHONG TAO AUDIO")

    # ------------------------------------------------------------
    # 1. KIEM TRA INPUT
    # ------------------------------------------------------------

    print("\n[1] KIEM TRA INPUT")

    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    source_hash = sha256_file(SOURCE)

    print("SOURCE SHA256:")
    print(source_hash)

    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            "FAIL: hash input 20D khong khop"
        )

    print("PASS: input 20D dung snapshot.")

    # ------------------------------------------------------------
    # 2. DOC CSV
    # ------------------------------------------------------------

    print("\n[2] DOC 182 DONG")

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        fields = list(reader.fieldnames or [])

        rows = list(reader)

    if len(rows) != 182:
        raise RuntimeError(
            f"FAIL: can 182 dong, thuc te {len(rows)}"
        )

    required = {
        "MaChuHanTam",
        "KyTu",
        "PinyinDeXuat",
        "NghiaDeXuatBienTap",
    }

    missing = required - set(fields)

    if missing:
        raise RuntimeError(
            f"FAIL: thieu cot {sorted(missing)}"
        )

    ids = [
        r["MaChuHanTam"].strip()
        for r in rows
    ]

    chars = [
        r["KyTu"].strip()
        for r in rows
    ]

    if len(set(ids)) != 182:
        raise RuntimeError(
            "FAIL: MaChuHanTam khong duy nhat"
        )

    if len(set(chars)) != 182:
        raise RuntimeError(
            "FAIL: KyTu khong duy nhat"
        )

    for field in EXTRA_FIELDS:
        if field not in fields:
            fields.append(field)

    print("PASS: 182 ID va 182 KyTu duy nhat.")

    # ------------------------------------------------------------
    # 3. AP DUNG REVIEW
    # ------------------------------------------------------------

    print("\n[3] AP DUNG REVIEW NOI BO")

    priority_count = 0
    pinyin_changes = []

    for row in rows:

        mid = row["MaChuHanTam"].strip()

        old_py = (
            row.get("PinyinDeXuat") or ""
        ).strip()

        base_meaning = (
            row.get("NghiaDeXuatBienTap") or ""
        ).strip()

        if mid in OVERRIDES:

            (
                new_py,
                new_meaning,
                source_note,
                note,
            ) = OVERRIDES[mid]

            row["PinyinChot20E"] = new_py

            row["NghiaTiengVietChot20E"] = (
                new_meaning
            )

            row["NguonChot20E"] = source_note

            row["TrangThai20E"] = (
                "DA_REVIEW_UU_TIEN_NOI_BO"
            )

            row["GhiChu20E"] = note

            priority_count += 1

            if old_py != new_py:

                pinyin_changes.append({
                    "MaChuHanTam": mid,
                    "KyTu": row["KyTu"].strip(),
                    "PinyinCu": old_py,
                    "PinyinChot": new_py,
                })

        else:

            row["PinyinChot20E"] = old_py

            row["NghiaTiengVietChot20E"] = (
                base_meaning
            )

            row["NguonChot20E"] = (
                "Đối chiếu nội bộ: "
                "CC-CEDICT + Make Me a Hanzi + "
                "ngữ cảnh từ HSK4 + CVDICT nếu có"
            )

            row["TrangThai20E"] = (
                "DA_REVIEW_THUONG_NOI_BO"
            )

            row["GhiChu20E"] = (
                "Mức thường: nguồn/pinyin/ngữ cảnh "
                "không có xung đột lớn trong gói review."
            )

    if priority_count != 37:
        raise RuntimeError(
            f"FAIL: can 37 dong uu tien, "
            f"thuc te {priority_count}"
        )

    # ------------------------------------------------------------
    # 4. KIEM TRA KET QUA
    # ------------------------------------------------------------

    print("\n[4] KIEM TRA KET QUA")

    missing_py = [
        r["MaChuHanTam"]
        for r in rows
        if not r["PinyinChot20E"].strip()
    ]

    missing_meaning = [
        r["MaChuHanTam"]
        for r in rows
        if not r["NghiaTiengVietChot20E"].strip()
    ]

    if missing_py:
        raise RuntimeError(
            f"FAIL: con thieu Pinyin: {missing_py}"
        )

    if missing_meaning:
        raise RuntimeError(
            f"FAIL: con thieu nghia: {missing_meaning}"
        )

    print(
        "PASS: review uu tien:",
        priority_count
    )

    print(
        "PASS: review thuong:",
        182 - priority_count
    )

    print("PASS: thieu Pinyin = 0")
    print("PASS: thieu nghia = 0")

    # ------------------------------------------------------------
    # 5. GHI OUTPUT AN TOAN
    # ------------------------------------------------------------

    print("\n[5] GHI OUTPUT")

    if OUTPUT.exists():

        existing_hash = sha256_file(OUTPUT)

        if existing_hash == EXPECTED_OUTPUT_SHA256:

            print(
                "PASS: output da ton tai va dung hash, "
                "khong ghi lai."
            )

        else:

            raise RuntimeError(
                "FAIL: output da ton tai nhung hash khac.\n"
                f"Actual: {existing_hash}\n"
                "Khong ghi de."
            )

    else:

        with OUTPUT.open(
            "x",
            encoding="utf-8-sig",
            newline=""
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fields,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(rows)

        print("PASS: da tao output moi.")

    output_hash = sha256_file(OUTPUT)

    if output_hash != EXPECTED_OUTPUT_SHA256:

        raise RuntimeError(
            "FAIL: output hash khong khop.\n"
            f"Expected: {EXPECTED_OUTPUT_SHA256}\n"
            f"Actual:   {output_hash}"
        )

    # ------------------------------------------------------------
    # 6. SUMMARY
    # ------------------------------------------------------------

    summary = {

        "status": "PASS_INTERNAL_REVIEW",

        "total_rows": 182,

        "priority_reviewed": 37,

        "normal_reviewed": 145,

        "missing_final_pinyin": 0,

        "missing_final_meaning": 0,

        "pinyin_changes_in_182_pack": (
            pinyin_changes
        ),

        "source_file": str(SOURCE),

        "source_sha256": source_hash,

        "output_file": str(OUTPUT),

        "output_sha256": output_hash,

        "note": (
            "Review noi bo/model-assisted theo "
            "nguon du an; khong phai kiem dinh "
            "chuyen gia doc lap."
        ),
    }

    if SUMMARY.exists():

        print(
            "SUMMARY da ton tai, khong ghi de:",
            SUMMARY
        )

    else:

        SUMMARY.write_text(
            json.dumps(
                summary,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    # ------------------------------------------------------------
    # 7. PINYIN THAY DOI
    # ------------------------------------------------------------

    print("\n[6] CAC PINYIN DA SUA / BO SUNG")

    for x in pinyin_changes:

        print(
            f"{x['MaChuHanTam']} | "
            f"{x['KyTu']} | "
            f"{x['PinyinCu']} -> "
            f"{x['PinyinChot']}"
        )

    print("\n" + "=" * 72)

    print("PASS: BUOC 20E HOAN THANH")

    print("OUTPUT:")
    print(OUTPUT)

    print("SHA256:")
    print(output_hash)

    print("KHONG GHI SQL.")

    print("=" * 72)


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print("\nFAIL:", exc)

        raise SystemExit(1)