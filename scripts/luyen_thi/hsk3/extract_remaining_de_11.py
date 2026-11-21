
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 11 (H31330) - BUOC 2

- Tach 70 anh cau 11-80.
- Tach 4 bang lua chon chung phan Doc.
- Giu nguyen 2 bang hinh Nghe buoc 1.
- Kiem tra A/B/C va Pinyin cau 76-80.
- Tao JSON manifest va HTML xem truoc.

KHONG ghi SQL Server.
KHONG sua cac de thi cu.
KHONG hien thi dap an trong HTML.
"""

from pathlib import Path
import hashlib
import json
import os
import re
import unicodedata

import fitz


# =====================================================
# 1. CAU HINH
# =====================================================

ROOT = Path(
    os.environ.get(
        "MOC_HAN_ROOT",
        r"D:\DATN1"
    )
)

BASE = ROOT / "scripts" / "luyen_thi"

SOURCE_DIR = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 11"
)

DATA = BASE / "hsk3" / "data" / "de_11"

OUTPUT = BASE / "hsk3" / "output" / "de_11"

QUESTIONS = OUTPUT / "questions"

GROUPS = OUTPUT / "groups"

ANSWER_JSON = DATA / "de_11_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

PREVIEW_HTML = (
    OUTPUT / "kiem_tra_80_cau.html"
)

CODE = "H31330"

ZOOM = 2.5


# =====================================================
# 2. SO DO TRANG CAU 11-80
# =====================================================

PAGE_QUESTIONS = {
    4: list(range(11, 21)),
    5: list(range(21, 31)),
    6: list(range(31, 41)),

    7: list(range(41, 46)),
    8: list(range(46, 51)),

    9: list(range(51, 56)),
    10: list(range(56, 61)),

    11: list(range(61, 65)),
    12: list(range(65, 71)),

    13: list(range(71, 76)),
    14: list(range(76, 81)),
}


# =====================================================
# 3. SAU BANG LUA CHON CHUNG
# =====================================================

# (trang PDF, cau tu, cau den, lua chon)

GROUP_INFO = {
    "nghe_01_05": (2, 1, 5, "ABCDEF"),
    "nghe_06_10": (3, 6, 10, "ABCDE"),

    "doc_41_45": (7, 41, 45, "ABCDEF"),
    "doc_46_50": (8, 46, 50, "ABCDE"),

    "doc_51_55": (9, 51, 55, "ABCDEF"),
    "doc_56_60": (10, 56, 60, "ABCDEF"),
}


# =====================================================
# 4. PINYIN CAU 76-80
# =====================================================

PINYIN_EXPECTED = {
    76: "hui",
    77: "geng",
    78: "che",
    79: "nian",
    80: "wei",
}


# =====================================================
# 5. HAM HO TRO
# =====================================================

def require_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong: {path}"
        )

    return path


def read_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def no_tones(text):

    value = unicodedata.normalize(
        "NFD",
        str(text)
    ).lower()

    return "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    ).strip()


def checksum(path):

    return hashlib.sha256(
        require_file(path).read_bytes()
    ).hexdigest()


# =====================================================
# 6. LUU FILE AN TOAN
# =====================================================

def safe_write(path, content):

    if path.exists():

        if path.read_bytes() != content:

            raise RuntimeError(
                "Khong ghi de file da co "
                "noi dung khac:\n"
                + str(path)
            )

        return

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_bytes(content)


# =====================================================
# 7. XAC DINH NHOM LUA CHON
# =====================================================

def group_for(number):

    for name, (
        _page,
        first,
        last,
        _labels
    ) in GROUP_INFO.items():

        if first <= number <= last:
            return name

    return None


# =====================================================
# 8. XAC DINH TRANG PDF
# =====================================================

def page_for(number):

    if number <= 5:
        return 2

    if number <= 10:
        return 3

    for page_num, numbers in (
        PAGE_QUESTIONS.items()
    ):

        if number in numbers:
            return page_num

    raise RuntimeError(
        f"Khong co trang PDF cau {number}"
    )


# =====================================================
# 9. KIEM TRA JSON BUOC 1
# =====================================================

def check_source():

    source = read_json(ANSWER_JSON)

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc"),
    )

    if identity != (3, 11, CODE):

        raise RuntimeError(
            "JSON buoc 1 khong phai "
            "HSK3 De 11 H31330"
        )

    counts = (
        source.get("tong_cau"),
        source.get("so_cau_nghe"),
        source.get("so_cau_doc"),
        source.get("so_cau_viet"),
    )

    if counts != (80, 40, 30, 10):

        raise RuntimeError(
            "JSON buoc 1 sai so cau"
        )

    # ================================================
    # 10. KIEM TRA 80 DAP AN
    # ================================================

    answers = source.get(
        "dap_an", {}
    )

    expected = {
        str(n)
        for n in range(1, 81)
    }

    if (
        set(answers) != expected
        or any(
            not str(value).strip()
            for value in answers.values()
        )
    ):

        raise RuntimeError(
            "JSON buoc 1 thieu dap an"
        )

    if source.get(
        "dap_an_thay_the"
    ) != {}:

        raise RuntimeError(
            "De 11 co dap an thay the "
            "chua xu ly"
        )

    if set(
        source.get(
            "cum_tu_sap_xep", {}
        )
    ) != {
        str(n)
        for n in range(71, 76)
    }:

        raise RuntimeError(
            "Thieu cum tu sap xep 71-75"
        )

    # ================================================
    # 11. KIEM TRA PDF GOC
    # ================================================

    pdf_path = require_file(
        Path(
            source.get("file_pdf") or ""
        )
    )

    if (
        pdf_path.parent.resolve()
        != SOURCE_DIR.resolve()
    ):

        raise RuntimeError(
            "PDF khong thuoc thu muc "
            "HSK3 DE 11"
        )

    # ================================================
    # 12. BAO VE HAI BANG HINH NGHE
    # ================================================

    old_hashes = {}

    for name in (
        "nghe_01_05",
        "nghe_06_10"
    ):

        path = (
            GROUPS / f"{name}.png"
        )

        old_hashes[name] = checksum(path)

    return source, pdf_path, old_hashes


# =====================================================
# 13. LAY DONG VAN BAN TU PDF
# =====================================================

def lines_of(page):

    lines = []

    blocks = page.get_text(
        "dict"
    )["blocks"]

    for block in blocks:

        for line in block.get(
            "lines", []
        ):

            text = "".join(
                span.get("text", "")

                for span in line.get(
                    "spans", []
                )
            ).strip()

            if text:

                lines.append((
                    text,
                    fitz.Rect(line["bbox"])
                ))

    return lines


# =====================================================
# 14. TIM VI TRI SO CAU
# =====================================================

def positions_of(
    page,
    numbers,
    page_no
):

    hits = {}

    lines = lines_of(page)

    for text, rect in lines:

        match = re.match(
            r"^\s*(\d{1,2})\s*[.．、]",
            text
        )

        if not match:
            continue

        number = int(
            match.group(1)
        )

        if (
            number in numbers
            and rect.x0 < 135
            and rect.y0 < 760
        ):

            hits.setdefault(
                number, []
            ).append(
                rect.y0
            )

    # ================================================
    # 15. KIEM TRA DU SO CAU
    # ================================================

    missing = sorted(
        set(numbers) - set(hits)
    )

    duplicates = sorted(
        number

        for number, points in hits.items()

        if len(points) != 1
    )

    if missing or duplicates:

        raise RuntimeError(
            f"Trang {page_no} sai so cau."
            f"\nThieu: {missing}"
            f"\nTrung: {duplicates}"
        )

    positions = {
        number: hits[number][0]
        for number in numbers
    }

    for first, second in zip(
        numbers,
        numbers[1:]
    ):

        if (
            positions[first]
            >= positions[second]
        ):

            raise RuntimeError(
                f"Trang {page_no} "
                "sai thu tu cau"
            )

    return positions, lines


# =====================================================
# 16. TIM PINYIN CAU 76-80
# =====================================================

def locate_pinyin(
    lines,
    positions
):

    result = {}

    for number, expected in (
        PINYIN_EXPECTED.items()
    ):

        candidates = [
            rect

            for text, rect in lines

            if (
                no_tones(text) == expected

                and positions[number] - 25
                <= rect.y0
                < positions[number]

                and 130 < rect.x0 < 460
            )
        ]

        if len(candidates) != 1:

            raise RuntimeError(
                f"Khong tim dung Pinyin "
                f"cau {number}: "
                f"{len(candidates)} ung vien"
            )

        result[number] = candidates[0]

    return result


# =====================================================
# 17. CAT 70 ANH CAU HOI
# =====================================================

def crop_questions(doc):

    images = {}
    metadata = {}

    for page_no, numbers in (
        PAGE_QUESTIONS.items()
    ):

        page = doc[
            page_no - 1
        ]

        positions, lines = positions_of(
            page,
            numbers,
            page_no
        )

        # Chi trang 14 co Pinyin o
        # phia tren cac cau 76-80.
        if page_no == 14:

            pinyin_rects = locate_pinyin(
                lines,
                positions
            )

        else:
            pinyin_rects = {}

        # ============================================
        # 18. XAC DINH DINH TREN CUA CAU
        # ============================================

        tops = {}

        for number in numbers:

            if number in pinyin_rects:

                tops[number] = (
                    pinyin_rects[number].y0
                    - 10
                )

            else:

                tops[number] = (
                    positions[number] - 9
                )

        # ============================================
        # 19. CAT TUNG CAU
        # ============================================

        for index, number in enumerate(
            numbers
        ):

            if index + 1 < len(numbers):

                next_number = numbers[index + 1]

                bottom = (
                    tops[next_number] - 6
                )

            else:

                # Cau cuoi trang:
                # Lay het noi dung nhung bo footer.
                endings = [
                    rect.y1

                    for text, rect in lines

                    if (
                        positions[number] - 2
                        <= rect.y0 < 760

                        and rect.x0 < 535
                    )
                ]

                bottom = min(
                    755,

                    max(
                        endings,
                        default=positions[number] + 20
                    ) + 12
                )

            rect = fitz.Rect(
                75,
                max(0, tops[number]),
                530,
                min(
                    page.rect.height,
                    bottom
                )
            )

            if (
                rect.is_empty
                or rect.height < 22
                or not page.rect.contains(rect)
            ):

                raise RuntimeError(
                    f"Khung cau {number} "
                    f"khong hop le: {rect}"
                )

            # ========================================
            # 20. KIEM TRA SO CAU
            # ========================================

            clip = page.get_text(
                "text",
                clip=rect
            )

            if not re.search(
                rf"(?<!\d){number}\s*[.．、]",
                clip
            ):

                raise RuntimeError(
                    f"Anh cau {number} "
                    "bi mat so cau"
                )

            # ========================================
            # 21. KIEM TRA A/B/C
            # ========================================

            if (
                21 <= number <= 40
                or 61 <= number <= 70
            ):

                labels = {
                    str(word[4]).strip()

                    for word in page.get_text(
                        "words"
                    )

                    if (
                        str(word[4]).strip()
                        in ("A", "B", "C")

                        and rect.contains(
                            fitz.Rect(word[:4])
                        )
                    )
                }

                if labels != set("ABC"):

                    raise RuntimeError(
                        f"Anh cau {number} "
                        "mat A/B/C: "
                        f"{sorted(labels)}"
                    )

            # ========================================
            # 22. KIEM TRA PINYIN
            # ========================================

            if number in pinyin_rects:

                expected = (
                    PINYIN_EXPECTED[number]
                )

                if expected not in no_tones(
                    clip
                ):

                    raise RuntimeError(
                        f"Anh cau {number} "
                        f"mat Pinyin {expected}"
                    )

                if not rect.contains(
                    pinyin_rects[number]
                ):

                    raise RuntimeError(
                        f"Anh cau {number} "
                        "cat mat Pinyin"
                    )

                if (
                    number < 80
                    and rect.intersects(
                        pinyin_rects[number + 1]
                    )
                ):

                    raise RuntimeError(
                        f"Anh cau {number} "
                        "dinh Pinyin cau sau"
                    )

            # ========================================
            # 23. XUAT ANH PNG
            # ========================================

            pix = page.get_pixmap(
                matrix=fitz.Matrix(
                    ZOOM,
                    ZOOM
                ),
                clip=rect,
                alpha=False
            )

            relative = (
                f"questions/cau_{number:02d}.png"
            )

            images[
                OUTPUT / relative
            ] = pix.tobytes("png")

            metadata[str(number)] = {
                "trang_pdf": page_no,

                "anh": relative,

                "nhom_lua_chon": (
                    group_for(number)
                ),

                "toa_do": [
                    round(value, 2)
                    for value in rect
                ],
            }

        print(
            f"Trang PDF {page_no}: "
            f"{len(numbers)} cau"
        )

    if len(images) != 70:

        raise RuntimeError(
            f"Anh cau 11-80: "
            f"{len(images)}/70"
        )

    return images, metadata


# =====================================================
# 24. CAT 4 BANG LUA CHON PHAN DOC
# =====================================================

def crop_reading_groups(doc):

    images = {}
    group_info = {}

    for name, (
        page_no,
        first,
        last,
        labels
    ) in GROUP_INFO.items():

        if not name.startswith("doc_"):
            continue

        page = doc[
            page_no - 1
        ]

        words = page.get_text(
            "words"
        )

        # Tim nhan A-F/A-E dau tien
        # nam trong phan bang lua chon.
        eligible = [
            word

            for word in words

            if (
                135 < word[1] < 380

                and word[0] >= 80

                and word[4] in labels
            )
        ]

        selected = {}

        for letter in labels:

            candidates = sorted(
                [
                    word

                    for word in eligible

                    if word[4] == letter
                ],
                key=lambda word: word[1]
            )

            if not candidates:

                raise RuntimeError(
                    f"Bang {name} "
                    f"thieu lua chon {letter}"
                )

            selected[letter] = (
                candidates[0]
            )

        # ============================================
        # 25. TINH TOA DO BANG DOC
        # ============================================

        ys = [
            word[1]
            for word in selected.values()
        ]

        if max(ys) - min(ys) > 190:

            raise RuntimeError(
                f"Bang {name} co "
                "toa do bat thuong"
            )

        rect = fitz.Rect(
            75,
            min(ys) - 14,
            532,
            max(ys) + 29
        )

        if not page.rect.contains(rect):

            raise RuntimeError(
                f"Bang {name} "
                "nam ngoai trang PDF"
            )

        clipped = page.get_text(
            "text",
            clip=rect
        )

        # Quan trong:
        # Khong lay nham dong vi du.
        if "例如" in clipped:

            raise RuntimeError(
                f"Bang {name} "
                "bi dinh dong vi du"
            )

        # ============================================
        # 26. KIEM TRA NHAN VA CHU HAN
        # ============================================

        actual = {
            str(word[4]).strip()

            for word in words

            if (
                str(word[4]).strip()
                in labels

                and rect.contains(
                    fitz.Rect(word[:4])
                )
            )
        }

        if (
            actual != set(labels)
            or not re.search(
                r"[\u3400-\u9fff]",
                clipped
            )
        ):

            raise RuntimeError(
                f"Bang {name} thieu "
                "A-F/A-E hoac chu Han"
            )

        # ============================================
        # 27. XUAT ANH BANG DOC
        # ============================================

        pix = page.get_pixmap(
            matrix=fitz.Matrix(
                ZOOM,
                ZOOM
            ),
            clip=rect,
            alpha=False
        )

        relative = (
            f"groups/{name}.png"
        )

        images[
            OUTPUT / relative
        ] = pix.tobytes("png")

        group_info[name] = {
            "trang_pdf": page_no,
            "cau_tu": first,
            "cau_den": last,

            "lua_chon": labels,

            "anh": relative,

            "toa_do": [
                round(value, 2)
                for value in rect
            ],
        }

        print(
            f"{name}: {labels} "
            f"(trang {page_no})"
        )

    return images, group_info


# =====================================================
# 28. TAO HTML XEM TRUOC
# =====================================================

def create_preview():

    sections = []

    for number in range(1, 81):

        if number == 1:
            sections.append(
                "<h2>I. Nghe – Câu 1–40</h2>"
            )

        elif number == 41:
            sections.append(
                "<h2>II. Đọc – Câu 41–70</h2>"
            )

        elif number == 71:
            sections.append(
                "<h2>III. Viết – Câu 71–80</h2>"
            )

        group = group_for(number)

        # ============================================
        # 29. HIEN THI BANG CHUNG MOT LAN
        # ============================================

        if (
            group
            and number
            == GROUP_INFO[group][1]
        ):

            last = GROUP_INFO[group][2]

            section = (
                '<section class="group">'
                f'<h3>Câu {number}–{last}</h3>'
                f'<img src="groups/{group}.png" '
                f'alt="Bảng lựa chọn {number}–{last}">'
            )

            # Chi hien cac o so cau o phan Nghe.
            # Phan Doc KHONG co cac nut thua.
            if number <= 10:

                numbers = "".join(
                    f"<span>Câu {n}</span>"

                    for n in range(
                        number,
                        last + 1
                    )
                )

                section += (
                    '<div class="nums">'
                    + numbers
                    + "</div>"
                )

            section += "</section>"

            sections.append(section)

        # ============================================
        # 30. ANH CAU 11-80
        # ============================================

        if number > 10:

            sections.append(
                '<section class="question">'
                f'<h3>Câu {number}</h3>'
                '<img '
                'src="questions/'
                f'cau_{number:02d}.png" '
                f'alt="Câu {number}">'
                '</section>'
            )

    template = """
<!doctype html>
<html lang="vi">

<head>
<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>HSK3 Đề 11 – Kiểm tra 80 câu</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #f3f5fa;
    color: #172b4d;
    font-family: Arial, sans-serif;
}

main {
    max-width: 980px;
    margin: auto;
}

h1 {
    font-size: 26px;
}

h2 {
    margin: 32px 0 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #dce4ed;
}

section {
    background: white;
    border: 1px solid #dae3ef;
    border-radius: 14px;
    margin: 16px 0;
    padding: 22px;
}

section.group {
    background: #f7faff;
}

h3 {
    font-size: 19px;
    margin: 0 0 16px;
}

img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: 0 auto;
}

.nums {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 20px;
}

.nums span {
    border: 1px solid #ccd8e7;
    border-radius: 8px;
    padding: 12px 18px;
}

.question img {
    margin-left: 0;
}

.note {
    color: #66758b;
    line-height: 1.5;
}

</style>
</head>

<body>

<main>

<h1>HSK3 – Đề 11 (H31330)</h1>

<p class="note">
Kiểm tra hình ảnh câu 1–80.
Không hiển thị đáp án.
Chưa thay đổi SQL Server.
</p>

__SECTIONS__

</main>

</body>
</html>
"""

    return template.replace(
        "__SECTIONS__",
        "\n".join(sections)
    ).encode("utf-8")


# =====================================================
# 31. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 11 - BUOC 2")
    print("MA DE GOC H31330")
    print("=" * 60)

    source, pdf_path, old_hashes = (
        check_source()
    )

    # ================================================
    # 32. DOC PDF VA TACH ANH
    # ================================================

    with fitz.open(pdf_path) as doc:

        if (
            len(doc) != 16
            or CODE not in doc[0].get_text("text")
            or CODE not in doc[14].get_text("text")
        ):

            raise RuntimeError(
                "PDF khong phai H31330 "
                "16 trang"
            )

        print("\n===== TACH 70 ANH =====")

        question_images, questions = (
            crop_questions(doc)
        )

        print("\n===== TACH 4 BANG DOC =====")

        reading_images, reading_info = (
            crop_reading_groups(doc)
        )

    # ================================================
    # 33. GHI NHAN CAU 1-10
    # ================================================

    for number in range(1, 11):

        questions[str(number)] = {
            "trang_pdf": page_for(number),

            "anh": None,

            "nhom_lua_chon": (
                group_for(number)
            ),
        }

    # ================================================
    # 34. GHI NHAN 2 BANG NGHE
    # ================================================

    group_manifest = {}

    for name in (
        "nghe_01_05",
        "nghe_06_10"
    ):

        page, first, last, labels = (
            GROUP_INFO[name]
        )

        group_manifest[name] = {
            "trang_pdf": page,

            "cau_tu": first,
            "cau_den": last,

            "lua_chon": labels,

            "anh": f"groups/{name}.png",
        }

    group_manifest.update(
        reading_info
    )

    # ================================================
    # 35. KIEM TRA MANIFEST
    # ================================================

    if set(questions) != {
        str(n)
        for n in range(1, 81)
    }:

        raise RuntimeError(
            "Manifest khong du 80 cau"
        )

    if set(group_manifest) != set(
        GROUP_INFO
    ):

        raise RuntimeError(
            "Manifest khong du 6 bang"
        )

    manifest = {
        "cap_hsk": 3,
        "so_de": 11,
        "ma_de_goc": CODE,

        "so_trang_pdf": 16,
        "so_cau": 80,

        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": [],

        "trang_dap_an": [15, 16],

        "cau_hoi": {
            str(n): questions[str(n)]
            for n in range(1, 81)
        },

        "bang_lua_chon": (
            group_manifest
        ),

        "dap_an_thay_the": (
            source["dap_an_thay_the"]
        ),
    }

    # ================================================
    # 36. CHUAN BI FILE DAU RA
    # ================================================

    outputs = {
        **question_images,
        **reading_images,

        MANIFEST_JSON: json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8"),

        PREVIEW_HTML: create_preview(),
    }

    if (
        len(question_images) != 70
        or len(reading_images) != 4
    ):

        raise RuntimeError(
            "So anh moi khong hop le"
        )

    # ================================================
    # 37. KHONG GHI DE FILE CU KHAC NOI DUNG
    # ================================================

    for path, content in outputs.items():

        if (
            path.exists()
            and path.read_bytes() != content
        ):

            raise RuntimeError(
                "Khong ghi de file "
                "co noi dung khac:\n"
                + str(path)
            )

    # Hai bang Nghe phai giu nguyen.
    for name, old_hash in (
        old_hashes.items()
    ):

        path = (
            GROUPS / f"{name}.png"
        )

        if checksum(path) != old_hash:

            raise RuntimeError(
                "Bang hinh Nghe "
                "da bi thay doi"
            )

    # ================================================
    # 38. LUU ANH, JSON VA HTML
    # ================================================

    for path, content in outputs.items():

        safe_write(
            path,
            content
        )

    # ================================================
    # 39. KIEM TRA SAU KHI LUU
    # ================================================

    for name, old_hash in (
        old_hashes.items()
    ):

        path = (
            GROUPS / f"{name}.png"
        )

        if checksum(path) != old_hash:

            raise RuntimeError(
                "Bang Nghe bi thay doi "
                "sau buoc 2"
            )

    # ================================================
    # 40. KET QUA
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH HSK3 DE 11 - BUOC 2"
    )

    print("=" * 60)

    print("Ma de goc: H31330")

    print("Anh cau 11-80: 70/70")

    print(
        "Bang chung: 6/6 "
        "(2 Nghe + 4 Doc)"
    )

    print(
        "Cau 21-40, 61-70: A/B/C DAY DU"
    )

    print(
        "Cau 76-80: Pinyin DAY DU"
    )

    print(
        "Khong hien dap an trong HTML"
    )

    print(f"\nManifest: {MANIFEST_JSON}")
    print(f"HTML: {PREVIEW_HTML}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
