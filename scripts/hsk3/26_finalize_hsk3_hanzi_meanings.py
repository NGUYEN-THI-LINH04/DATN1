
# -*- coding: utf-8 -*-
"""
BUOC 62 - CHINH NGHIA 55 CHU HAN HSK3

Nguon:
- hanzi_hsk3_300_meanings_draft.csv
- hanzi_hsk3_55_multiple_meanings_review.csv

Ket qua:
- hanzi_hsk3_300_meanings_cleaned.csv
- hanzi_hsk3_55_meanings_corrected.csv

An toan:
- Chi chinh cot NghiaTiengViet cua 55 chu.
- Giu nguyen 245 chu con lai.
- Khong thay Pinyin, SoNet, MaBaiHoc.
- Khong ghi de file goc.
- Khong ghi SQL.
- Van la du lieu ban nhap cho kiem duyet.
"""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA = (
    ROOT / "scripts" / "hsk3"
    / "data" / "processed"
)

SOURCE = DATA / "hanzi_hsk3_300_meanings_draft.csv"
REVIEW_SOURCE = (
    DATA / "hanzi_hsk3_55_multiple_meanings_review.csv"
)

OUTPUT = DATA / "hanzi_hsk3_300_meanings_cleaned.csv"
REVIEW_OUTPUT = DATA / "hanzi_hsk3_55_meanings_corrected.csv"
REPORT = DATA / "hanzi_hsk3_meanings_cleaned_report.json"

# Nghia chinh de xuat, duoc rut gon tu cac muc CVDICT
# co Pinyin khop trong file 55 chu nguoi dung gui.
# Chua duoc kiem duyet chinh thuc.

RAW_MEANINGS = """
立|Đứng; thành lập; lập tức
程|Quá trình; trình tự; hành trình
展|Mở rộng; triển khai; trưng bày
卫|Bảo vệ; phòng vệ
杂|Tạp; hỗn hợp; pha trộn
志|Ý chí; chí hướng; ghi chép
采|Hái; thu thập; lựa chọn
达|Đạt tới; đạt được
神|Thần; tinh thần; thần kỳ
民|Người dân; nhân dân
农|Nông nghiệp; làm nông
世|Đời; thế hệ; thế giới
裙|Váy
验|Kiểm tra; kiểm nghiệm
章|Chương; điều khoản; huy hiệu
华|Trung Hoa; hoa lệ
专|Chuyên; chuyên môn; tập trung
哈|Ha; tiếng cười; tiếng cảm thán
效|Hiệu quả; tác dụng; bắt chước
制|Chế tạo; quy định; chế độ
木|Cây; gỗ
据|Dựa vào; căn cứ; chiếm giữ
武|Võ; quân sự
宣|Tuyên bố; công bố
冒|Mạo hiểm; liều lĩnh; giả mạo
李|Quả mận; cây mận; họ Lý
范|Khuôn mẫu; kiểu mẫu
注|Chú ý; ghi chú; rót vào
察|Quan sát; kiểm tra; xem xét
容|Chứa đựng; cho phép; dung mạo
易|Dễ; thay đổi; trao đổi
创|Sáng tạo; khởi xướng
裤|Quần
规|Quy tắc; quy định; khuôn phép
危|Nguy hiểm; nguy cấp
概|Khái quát; đại thể; ước chừng
石|Đá; hòn đá
娘|Mẹ; cô gái
众|Đám đông; quần chúng; đông đảo
散|Phân tán; giải tán; xua tan
戏|Kịch; trò chơi; biểu diễn
历|Trải qua; lịch; lịch sử
似|Giống; tương tự; dường như
麻|Cây gai; sợi gai; tê
暖|Ấm; ấm áp; làm ấm
怪|Kỳ lạ; quái lạ; trách móc
何|Gì; tại sao; như thế nào
幸|May mắn; hạnh phúc
义|Ý nghĩa; chính nghĩa; công lý
沙|Cát; khàn giọng
丰|Phong phú; dồi dào
绝|Cắt đứt; tuyệt; hoàn toàn
苹|Chữ dùng trong 苹果 (quả táo)
望|Hy vọng; mong đợi; nhìn xa
景|Phong cảnh; cảnh vật; tình cảnh
"""


def clean(value):
    return str(value or "").strip()


def load_meanings():
    result = {}

    for number, line in enumerate(
        RAW_MEANINGS.strip().splitlines(),
        start=1,
    ):
        if "|" not in line:
            raise ValueError(
                f"Dong {number}: sai dinh dang."
            )

        char, meaning = line.split("|", 1)

        char = clean(char)
        meaning = clean(meaning)

        if len(char) != 1 or not meaning:
            raise ValueError(
                f"Dong {number}: du lieu khong hop le."
            )

        if char in result:
            raise ValueError(
                f"Trung ky tu: {char}"
            )

        result[char] = meaning

    if len(result) != 55:
        raise ValueError(
            f"Can dung 55 chu, hien co {len(result)}."
        )

    return result


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Khong tim thay file: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)

        fields = reader.fieldnames or []
        rows = list(reader)

    return rows, fields


def write_csv(path, fields, rows):
    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fields,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 68)
    print("BUOC 62 - CHINH NGHIA 55 CHU HAN HSK3")
    print("=" * 68)
    print("CHE DO: KHONG GHI SQL")

    # Tuyet doi khong ghi de file da co.
    for path in (
        OUTPUT,
        REVIEW_OUTPUT,
        REPORT,
    ):
        if path.exists():
            raise FileExistsError(
                f"File da ton tai: {path}"
            )

    meanings = load_meanings()

    all_rows, fields = read_csv(SOURCE)
    review_rows, review_fields = read_csv(
        REVIEW_SOURCE
    )

    required = {
        "KyTu",
        "MaBaiHoc",
        "Pinyin",
        "SoNet",
        "NghiaTiengViet",
    }

    for name, available in (
        ("Nguon 300 chu", fields),
        ("Nguon 55 chu", review_fields),
    ):
        missing = required - set(available)

        if missing:
            raise ValueError(
                f"{name} thieu cot: {sorted(missing)}"
            )

    if len(all_rows) != 300:
        raise ValueError(
            f"Nguon 300 chu co {len(all_rows)} dong."
        )

    if len(review_rows) != 55:
        raise ValueError(
            f"Nguon review co {len(review_rows)} dong."
        )

    all_chars = [clean(r["KyTu"]) for r in all_rows]
    review_chars = [
        clean(r["KyTu"]) for r in review_rows
    ]

    if len(set(all_chars)) != 300:
        raise ValueError("Nguon 300 chu bi trung.")

    if len(set(review_chars)) != 55:
        raise ValueError("Nguon 55 chu bi trung.")

    # Bat buoc khop chinh xac danh sach 55 chu.
    if set(review_chars) != set(meanings):
        missing = set(review_chars) - set(meanings)
        extra = set(meanings) - set(review_chars)

        raise ValueError(
            "Danh sach 55 chu khong khop.\n"
            f"Thieu trong code: {sorted(missing)}\n"
            f"Du trong code: {sorted(extra)}"
        )

    if not set(review_chars).issubset(all_chars):
        raise ValueError(
            "Co chu trong file review "
            "khong thuoc file 300 chu."
        )

    review_by_char = {
        clean(row["KyTu"]): row
        for row in review_rows
    }

    extra_fields = [
        "NguonNghiaCuoi",
        "TrangThaiKiemDuyetCuoi",
    ]

    output_fields = fields + [
        field for field in extra_fields
        if field not in fields
    ]

    result = []
    corrected = []

    for original in all_rows:
        row = dict(original)
        char = clean(row["KyTu"])

        # Kiem tra cac thong tin goc.
        for field in (
            "MaBaiHoc",
            "Pinyin",
            "SoNet",
        ):
            if not clean(row[field]):
                raise ValueError(
                    f"{char}: thieu {field}"
                )

        if char in meanings:
            review_row = review_by_char[char]

            # Nguon 55 chu va nguon 300 chu
            # phai co cung MaBaiHoc / Pinyin / SoNet.
            for field in (
                "MaBaiHoc",
                "Pinyin",
                "SoNet",
            ):
                if clean(original[field]) != clean(
                    review_row[field]
                ):
                    raise ValueError(
                        f"{char}: {field} khong khop "
                        "giua hai file."
                    )

            # Chi thay nghia cua 55 chu.
            row["NghiaTiengViet"] = meanings[char]

            row["NguonNghiaCuoi"] = (
                "CVDICT_RUT_GON_DE_XUAT"
            )
            row["TrangThaiKiemDuyetCuoi"] = (
                "CHUA_DUYET"
            )

            corrected.append(row)

        else:
            # Giu nguyen 245 chu khac.
            if not clean(row["NghiaTiengViet"]):
                raise ValueError(
                    f"{char}: chu khac van thieu nghia."
                )

            row["NguonNghiaCuoi"] = (
                clean(row.get("NguonNghiaHienTai"))
                or "NGUON_CU"
            )
            row["TrangThaiKiemDuyetCuoi"] = (
                "CHUA_XAC_NHAN_DUYET"
            )

        # Bao ve cac truong du lieu.
        protected = (
            "KyTu",
            "MaBaiHoc",
            "SoThuTuBai",
            "ThuTuTam",
            "Pinyin",
            "SoNet",
            "MaChuHanTam",
            "MaBoThu",
        )

        for field in protected:
            if (
                field in original
                and row.get(field) != original[field]
            ):
                raise RuntimeError(
                    f"{char}: da thay doi cot {field}."
                )

        result.append(row)

    if len(result) != 300 or len(corrected) != 55:
        raise RuntimeError(
            "Tong so chu sau xu ly khong khop."
        )

    missing = sum(
        not clean(r["NghiaTiengViet"])
        for r in result
    )

    if missing:
        raise RuntimeError(
            f"Con {missing} chu thieu nghia."
        )

    report = {
        "tong_chu_hsk3": 300,
        "giu_nguyen": 245,
        "chinh_nghia_theo_cvdict": 55,
        "con_thieu_nghia": 0,
        "trang_thai": "BAN_NHAP_CAN_KIEM_DUYET",
        "ghi_sql": False,
    }

    write_csv(
        OUTPUT,
        output_fields,
        result,
    )

    write_csv(
        REVIEW_OUTPUT,
        output_fields,
        corrected,
    )

    with REPORT.open(
        "x",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("\nKET QUA")
    print("Tong chu Han:", len(result))
    print("Giu nguyen:", 245)
    print("Da chinh nghia de xuat:", len(corrected))
    print("Con thieu nghia:", missing)

    print("\nFILE 300 CHU:")
    print(OUTPUT)

    print("\nFILE 55 CHU DA CHINH:")
    print(REVIEW_OUTPUT)

    print("\nHOAN THANH")
    print("CHUA GHI SQL")
    print("CHUA XUAT BAN")


if __name__ == "__main__":
    main()
