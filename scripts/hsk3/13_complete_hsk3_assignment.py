
# -*- coding: utf-8 -*-
"""
BUOC 48 - HOAN THIEN DE XUAT PHAN BAI HSK3

Nguon:
- 973 muc HSK3
- 772 muc HSK2 da phan bai
- Ket qua goi y HSK3 buoc 47

Muc tieu:
- Bao toan 973 muc
- Moi muc co 1 bai hoc DU KIEN
- Dua ra 3 chu de phu hop nhat
- Danh dau muc can kiem duyet
- Khong ghi SQL

Luu y:
Day la thuat toan goi y, KHONG phai
bo phan loai ngu nghia da duoc kiem chung.
"""

import csv
import math
import re
import unicodedata

from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

H2 = (
    ROOT / "scripts" / "hsk2" / "data"
    / "processed" / "vocabulary_hsk2_final_by_lesson.csv"
)

DATA = (
    ROOT / "scripts" / "hsk3"
    / "data" / "processed"
)

SOURCE = DATA / "vocabulary_hsk3_assignment_improved.csv"
LESSONS = DATA / "lessons_hsk3_draft.csv"

OUTPUT = DATA / "vocabulary_hsk3_assignment_complete.csv"
REVIEW = DATA / "vocabulary_hsk3_assignment_need_review.csv"

# Anh xa chu de HSK2 da doi chieu theo tieu de bai.
H2_TO_H3 = {
    1: 4,
    2: 2,
    3: 3,
    4: 5,
    5: 15,
    6: 13,
    7: 7,
    8: 9,
    9: 10,
    10: 11,
    11: 11,
    12: 12,
    13: 8,
    14: 16,
    15: 17,
    16: 19,
    17: 1,
    18: 10,
    19: 20,
    20: 19,
    21: 18,
    22: 17,
    23: 1,
}


def clean(value):
    return unicodedata.normalize(
        "NFC",
        re.sub(r"\s+", " ", str(value or "")).strip()
    )


def read_csv(path):
    if not path.is_file():
        raise FileNotFoundError(path)

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    if path.exists():
        raise FileExistsError(
            f"Da ton tai: {path}\n"
            "Khong ghi de file da xu ly."
        )

    with path.open(
        "x", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=fields, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)


def tokens(row):
    """
    Trich xuat dac trung:
    - Cum 2/3 chu Han
    - Nghia tieng Viet (cum tu va tu don)
    - Bo qua mot so tu noi thong dung
    """
    hanzi = clean(row.get("ChuHan"))
    meaning = clean(row.get("NghiaTiengViet")).casefold()

    chars = re.findall(r"[\u3400-\u9fff]", hanzi)

    result = set()

    for size in (1, 2, 3):
        for i in range(len(chars) - size + 1):
            result.add(
                "zh" + str(size) + ":" +
                "".join(chars[i:i + size])
            )

    parts = re.findall(
        r"[a-zA-ZÀ-ỹ0-9]+", meaning
    )

    stops = {
        "của", "cho", "một", "những", "các",
        "được", "dùng", "hoặc", "với", "trong",
        "để", "là", "như", "cái", "này",
        "đó", "thể", "biến", "tiếng",
        "làm", "người", "chỉ",
    }

    for word in parts:
        if len(word) >= 3 and word not in stops:
            result.add("vi:" + word)

    for i in range(len(parts) - 1):
        pair = parts[i:i + 2]

        if all(
            word not in stops
            for word in pair
        ):
            result.add("vipair:" + " ".join(pair))

    return result


def score(a, b, idf):
    common = a & b

    return sum(
        idf.get(token, 1.0) *
        (2.0 if token.startswith("vipair:") else 1.0)
        for token in common
    )


def main():
    print("=" * 68)
    print("BUOC 48 - DE XUAT PHAN BAI TOAN BO HSK3")
    print("=" * 68)

    hsk2 = read_csv(H2)
    hsk3 = read_csv(SOURCE)
    lessons = read_csv(LESSONS)

    if len(hsk2) != 772:
        raise ValueError("Du lieu HSK2 khong du 772 muc.")

    if len(hsk3) != 973:
        raise ValueError("Du lieu HSK3 khong du 973 muc.")

    if len(lessons) != 20:
        raise ValueError("Can dung 20 bai HSK3 du kien.")

    lesson_names = {
        int(x["SoThuTuBai"]): clean(
            x["TieuDeTiengViet"]
        )
        for x in lessons
    }

    if set(lesson_names) != set(range(1, 21)):
        raise ValueError("Thu tu bai HSK3 khong hop le.")

    # Tao du lieu tham chieu tu HSK2.
    reference = []

    for word in hsk2:
        old_lesson = int(word["SoThuTuBai"])

        if old_lesson not in H2_TO_H3:
            continue

        reference.append({
            "lesson": H2_TO_H3[old_lesson],
            "tokens": tokens(word),
        })

    # Bo sung nhung goi y HSK3 co san.
    for word in hsk3:
        lesson = clean(
            word.get("SoThuTuBaiDeXuat")
        )

        if lesson:
            number = int(lesson)

            if number not in lesson_names:
                raise ValueError("Ma bai HSK3 sai.")

            reference.append({
                "lesson": number,
                "tokens": tokens(word),
            })

    # Tinh tan suat dac trung.
    frequency = Counter()

    for item in reference:
        frequency.update(item["tokens"])

    n = len(reference)

    idf = {
        token: math.log(
            (n + 1) / (count + 1)
        ) + 1.0
        for token, count in frequency.items()
    }

    result = []

    for word in hsk3:
        current_tokens = tokens(word)

        by_lesson = defaultdict(list)

        for ref in reference:
            value = score(
                current_tokens,
                ref["tokens"],
                idf,
            )

            if value > 0:
                by_lesson[
                    ref["lesson"]
                ].append(value)

        ranked = []

        for number in range(1, 21):
            values = sorted(
                by_lesson[number],
                reverse=True,
            )[:3]

            # Lay trung binh cua cac mau phu hop
            # nhat, de giam anh huong cua chu de
            # co nhieu tu tham chieu.
            value = (
                sum(values) / len(values)
                if values else 0.0
            )

            ranked.append((value, number))

        ranked.sort(
            key=lambda x: (-x[0], x[1])
        )

        previous = clean(
            word.get("SoThuTuBaiDeXuat")
        )

        previous_method = clean(
            word.get("PhuongPhapGoiY")
        )

        if previous:
            selected = int(previous)
            method = "KE_THUA_GOI_Y_BUOC_47"

            if selected not in lesson_names:
                raise ValueError(
                    f"Bai goi y khong hop le: {selected}"
                )

        else:
            selected = ranked[0][1]
            method = "TU_DONG_DE_XUAT_CHUA_DUYET"

        best_score = ranked[0][0]
        second_score = ranked[1][0]

        if (
            previous
            and previous_method == "GOI_Y_BUOC_46"
        ):
            priority = "CAN_KIEM_TRA"

        elif (
            best_score >= 4.0
            and best_score - second_score >= 1.5
            and selected == ranked[0][1]
        ):
            priority = "GOI_Y_TUONG_DOI_RO"

        else:
            priority = "CAN_KIEM_TRA"

        output_row = dict(word)

        output_row.update({
            "SoThuTuBaiDuKien": selected,
            "TenBaiDuKien": lesson_names[selected],
            "ChuDeGoiY1": ranked[0][1],
            "ChuDeGoiY2": ranked[1][1],
            "ChuDeGoiY3": ranked[2][1],
            "DiemGoiY1": round(best_score, 3),
            "DiemGoiY2": round(second_score, 3),
            "PhuongPhapPhanBo": method,
            "MucCanKiemTra": priority,
            "DaDuyetPhanBai": "CHUA",
        })

        result.append(output_row)

    if len(result) != 973:
        raise RuntimeError("Thieu muc tu HSK3.")

    codes = [
        clean(x.get("MaMucNoiBo"))
        for x in result
    ]

    if (
        len(set(codes)) != 973
        or any(not code for code in codes)
    ):
        raise RuntimeError(
            "Ma HSK3 bi trung hoac rong."
        )

    review = [
        x for x in result
        if x["MucCanKiemTra"] == "CAN_KIEM_TRA"
    ]

    if OUTPUT.exists() or REVIEW.exists():
        raise FileExistsError(
            "File dau ra da ton tai. "
            "Khong tu dong ghi de."
        )

    fields = list(result[0].keys())

    write_csv(OUTPUT, fields, result)
    write_csv(REVIEW, fields, review)

    counts = Counter(
        int(x["SoThuTuBaiDuKien"])
        for x in result
    )

    print("\nTONG KET")
    print("Tong muc HSK3:", len(result))
    print("Da co bai du kien:", sum(counts.values()))
    print("Can kiem tra phan bo:", len(review))

    print("\nSO TU DU KIEN MOI BAI")

    for number in range(1, 21):
        print(
            f"Bai {number:02d}: "
            f"{lesson_names[number]} - "
            f"{counts[number]} muc"
        )

    print("\nFILE TONG HOP:")
    print(OUTPUT)

    print("\nFILE CAN RA SOAT:")
    print(REVIEW)

    print("\nCHUA GHI SQL")
    print("CHUA DUYET PHAN BO BAI HOC")


if __name__ == "__main__":
    main()
