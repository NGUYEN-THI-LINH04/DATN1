
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 10 (H31328)
BUOC 3 - CHUAN HOA DU LIEU

- Dung JSON HSK3 De 1 lam mau.
- Doi chieu 80 dap an voi PDF goc.
- Kiem tra 5 cau sap xep 71-75.
- Kiem tra 70 anh cau hoi, 6 bang lua chon.
- SU DUNG ANH DA SUA, KHONG CAT LAI.
- Sao chep 76 anh va MP3 vao static.
- Tao de_10.json.

KHONG ket noi SQL Server.
KHONG thay doi 29 de da nhap.
KHONG ghi de file khac noi dung.
"""

from pathlib import Path
from copy import deepcopy
from collections import Counter
from itertools import permutations

import filecmp
import json
import os
import re
import shutil
import unicodedata

import fitz
from mutagen.mp3 import MP3


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
HSK3 = BASE / "hsk3"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 10"
)

DATA = HSK3 / "data" / "de_10"
OUTPUT = HSK3 / "output" / "de_10"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk3"
)

MEDIA = MEDIA_ROOT / "de_10"

TEMPLATE_FILE = (
    HSK3 / "data" / "de_01" / "de_01.json"
)

ANSWER_FILE = DATA / "de_10_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_80_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_10.json"

# Ma goc tren PDF.
CODE = "H31328"


# =====================================================
# 2. CAC BANG LUA CHON CHUNG
# =====================================================

# (trang PDF, cau tu, cau den, lua chon)

GROUPS = {
    "nghe_01_05": (2, 1, 5, "ABCDEF"),
    "nghe_06_10": (3, 6, 10, "ABCDE"),

    "doc_41_45": (7, 41, 45, "ABCDEF"),
    "doc_46_50": (8, 46, 50, "ABCDE"),

    "doc_51_55": (9, 51, 55, "ABCDEF"),
    "doc_56_60": (10, 56, 60, "ABCDEF"),
}


# =====================================================
# 3. SO DO TRANG PDF
# =====================================================

PAGES = {
    2: range(1, 6),
    3: range(6, 11),

    4: range(11, 21),
    5: range(21, 31),
    6: range(31, 41),

    7: range(41, 46),
    8: range(46, 51),

    9: range(51, 56),
    10: range(56, 61),

    11: range(61, 65),
    12: range(65, 71),

    13: range(71, 76),
    14: range(76, 81),
}


# =====================================================
# 4. HAM HO TRO
# =====================================================

def require_file(path):

    if (
        not path.is_file()
        or path.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Thieu file hoac file rong:\n{path}"
        )

    return path


def read_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def normalize(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    )


def compact(value):

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        normalize(value)
    )


# =====================================================
# 5. DOI THAM CHIEU DE 1 SANG DE 10
# =====================================================

def replace_refs(value):

    if isinstance(value, str):

        return (
            value
            .replace("H31001", CODE)
            .replace("de_01", "de_10")
            .replace("Đề 1", "Đề 10")
            .replace("ĐỀ 1", "ĐỀ 10")
        )

    if isinstance(value, list):

        return [
            replace_refs(item)
            for item in value
        ]

    if isinstance(value, dict):

        return {
            key: replace_refs(item)
            for key, item in value.items()
        }

    return value


# =====================================================
# 6. XAC DINH TRANG PDF
# =====================================================

def page_for(number):

    for page, numbers in PAGES.items():

        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong co trang PDF cho cau {number}"
    )


# =====================================================
# 7. NHOM LUA CHON
# =====================================================

def group_for(number):

    for name, (
        _page,
        first,
        last,
        _labels
    ) in GROUPS.items():

        if first <= number <= last:
            return name

    return None


# =====================================================
# 8. KY NANG
# =====================================================

def skill_for(number):

    if number <= 40:
        return "nghe"

    if number <= 70:
        return "doc"

    return "viet"


# =====================================================
# 9. LOAI CAU HOI
# =====================================================

def kind_for(number):

    if number <= 10:
        return "chon_hinh"

    if number <= 20:
        return "dung_sai"

    if number <= 40:
        return "chon_mot"

    if number <= 60:
        return "ghep_lua_chon"

    if number <= 70:
        return "chon_mot"

    if number <= 75:
        return "sap_xep"

    return "dien_tu"


# =====================================================
# 10. PHAN THI
# =====================================================

def part_for(number):

    if number <= 40:

        part = (number - 1) // 10 + 1

        return f"Nghe - Phần {part}"

    if number <= 50:
        return "Đọc - Phần 1"

    if number <= 60:
        return "Đọc - Phần 2"

    if number <= 70:
        return "Đọc - Phần 3"

    if number <= 75:
        return "Viết - Phần 1"

    return "Viết - Phần 2"


# =====================================================
# 11. LUA CHON CHO MOI CAU
# =====================================================

def choices_for(number, tokens):

    if number <= 5:
        return list("ABCDEF")

    if number <= 10:
        return list("ABCDE")

    if number <= 20:
        return ["√", "×"]

    if number <= 40:
        return list("ABC")

    if number <= 45:
        return list("ABCDEF")

    if number <= 50:
        return list("ABCDE")

    if number <= 60:
        return list("ABCDEF")

    if number <= 70:
        return list("ABC")

    if number <= 75:
        return tokens[number]

    return []


# =====================================================
# 12. DOC LAI DAP AN TU PDF
# =====================================================

def read_pdf_data(pdf_path):

    with fitz.open(pdf_path) as doc:

        if len(doc) != 16:

            raise RuntimeError(
                "PDF H31328 phai co 16 trang."
            )

        cover = normalize(
            doc[0].get_text("text")
        )

        answer_page = normalize(
            doc[14].get_text("text")
        )

        writing_page = doc[15].get_text(
            "text"
        )

        if (
            CODE not in cover
            or CODE not in answer_page
        ):

            raise RuntimeError(
                "PDF khong phai H31328."
            )

        if (
            "答案" not in answer_page
            or "书" not in writing_page
        ):

            raise RuntimeError(
                "Trang 15-16 khong phai dap an."
            )

        # ============================================
        # 13. DAP AN NGHE / DOC
        # ============================================

        objective = {}

        pattern = re.compile(
            r"(?<!\d)(\d{1,2})"
            r"\s*[.．、]\s*"
            r"([A-F√×])(?=\s|$)"
        )

        for match in pattern.finditer(
            answer_page
        ):

            number = int(
                match.group(1)
            )

            if not 1 <= number <= 70:
                continue

            if number in objective:

                raise RuntimeError(
                    f"Trung dap an cau {number}"
                )

            objective[number] = (
                match.group(2)
            )

        if set(objective) != set(
            range(1, 71)
        ):

            raise RuntimeError(
                "PDF khong du 70 dap an Nghe/Doc."
            )

        # ============================================
        # 14. DAP AN VIET
        # ============================================

        writing = {}

        pattern = re.compile(
            r"^\s*(7[1-9]|80)"
            r"\s*[.．、]\s*([^\n]+)",
            re.MULTILINE
        )

        for match in pattern.finditer(
            writing_page
        ):

            number = int(
                match.group(1)
            )

            if number in writing:

                raise RuntimeError(
                    f"Trung dap an Viet {number}"
                )

            answer = (
                match.group(2).strip()
            )

            if "/" in answer:

                raise RuntimeError(
                    f"Cau {number} co dap an "
                    "thay the can xu ly rieng."
                )

            writing[number] = answer

        if set(writing) != set(
            range(71, 81)
        ):

            raise RuntimeError(
                "PDF khong du 10 dap an Viet."
            )

        # ============================================
        # 15. DOC CUM TU CAU 71-75
        # ============================================

        tokens = {}

        pattern = re.compile(
            r"^\s*(7[1-5])"
            r"\s*[.．、]\s*(.+)"
        )

        text = doc[12].get_text(
            "text"
        )

        for line in text.splitlines():

            match = pattern.match(line)

            if not match:
                continue

            number = int(
                match.group(1)
            )

            if number in tokens:

                raise RuntimeError(
                    f"Trung cum tu cau {number}"
                )

            tokens[number] = [
                value.strip()

                for value in re.split(
                    r"\s{2,}",
                    match.group(2)
                )

                if value.strip()
            ]

        if set(tokens) != set(
            range(71, 76)
        ):

            raise RuntimeError(
                "Khong du cum tu cau 71-75."
            )

        # ============================================
        # 16. KIEM TRA CAU SAP XEP
        # ============================================

        for number in range(71, 76):

            values = tokens[number]

            if not 3 <= len(values) <= 8:

                raise RuntimeError(
                    f"Cau {number} co "
                    "so cum tu khong hop le."
                )

            valid = any(
                compact("".join(order))
                == compact(writing[number])

                for order in permutations(
                    values
                )
            )

            if not valid:

                raise RuntimeError(
                    f"Cau {number} khong "
                    "ghep duoc dap an tu PDF."
                )

        # ============================================
        # 17. KIEM TRA CAU DIEN TU
        # ============================================

        for number in range(76, 81):

            if len(
                compact(writing[number])
            ) != 1:

                raise RuntimeError(
                    f"Cau {number} phai "
                    "dien mot chu Han."
                )

        return {
            **objective,
            **writing
        }, tokens


# =====================================================
# 18. KIEM TRA ANH VA MEDIA
# =====================================================

def check_copies(pairs):

    for source, destination in pairs:

        require_file(source)

        if source.suffix.lower() == ".png":

            if not source.read_bytes().startswith(
                b"\x89PNG\r\n\x1a\n"
            ):

                raise RuntimeError(
                    f"Anh PNG khong hop le:\n{source}"
                )

        if destination.exists():

            if not filecmp.cmp(
                source,
                destination,
                shallow=False
            ):

                raise RuntimeError(
                    "Media da ton tai voi "
                    "noi dung khac:\n"
                    + str(destination)
                )


# =====================================================
# 19. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)

    print("MOC HAN - HSK3 DE 10")
    print("BUOC 3 - CHUAN HOA H31328")

    print("=" * 60)

    # ================================================
    # 20. DOC DU LIEU CAC BUOC TRUOC
    # ============================================

    template = read_json(
        TEMPLATE_FILE
    )

    source = read_json(
        ANSWER_FILE
    )

    manifest = read_json(
        MANIFEST_FILE
    )

    if (
        template.get("ma_de_goc") != "H31001"
        or len(
            template.get("cau_hoi", [])
        ) != 80
    ):

        raise RuntimeError(
            "JSON mau HSK3 De 1 khong hop le."
        )

    if (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc"),
    ) != (3, 10, CODE):

        raise RuntimeError(
            "JSON buoc 1 khong phai H31328."
        )

    if (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau"),
    ) != (3, 10, CODE, 80):

        raise RuntimeError(
            "Manifest buoc 2 khong hop le."
        )

    # ================================================
    # 21. KIEM TRA PDF 16 TRANG
    # ============================================

    if (
        manifest.get("so_trang_pdf") != 16
        or manifest.get("trang_dap_an")
        != [15, 16]
        or manifest.get("trang_loi_thoai")
        != []
    ):

        raise RuntimeError(
            "Manifest sai bo cuc PDF H31328."
        )

    # ================================================
    # 22. KIEM TRA DAP AN THAY THE
    # ============================================

    if (
        source.get("dap_an_thay_the") != {}
        or manifest.get("dap_an_thay_the")
        != {}
    ):

        raise RuntimeError(
            "Co dap an thay the "
            "chua duoc xu ly."
        )

    # ================================================
    # 23. TIM PDF VA MP3
    # ============================================

    pdfs = sorted(
        SOURCE.glob("*.pdf")
    )

    mp3s = sorted(
        SOURCE.glob("*.mp3")
    )

    if (
        len(pdfs) != 1
        or len(mp3s) != 1
    ):

        raise RuntimeError(
            "Thu muc DE 10 can dung "
            "1 PDF va 1 MP3."
        )

    pdf_file = require_file(
        pdfs[0]
    )

    mp3_file = require_file(
        mp3s[0]
    )

    if (
        not source.get("file_pdf")
        or Path(
            source["file_pdf"]
        ).resolve() != pdf_file.resolve()
    ):

        raise RuntimeError(
            "PDF buoc 1 khong khop PDF goc."
        )

    if source.get("file_mp3"):

        if (
            Path(
                source["file_mp3"]
            ).resolve() != mp3_file.resolve()
        ):

            raise RuntimeError(
                "MP3 khong khop file goc."
            )

    # ================================================
    # 24. DOI CHIEU DAP AN
    # ============================================

    answers, tokens = read_pdf_data(
        pdf_file
    )

    source_answers = source.get(
        "dap_an", {}
    )

    if set(source_answers) != {
        str(n) for n in range(1, 81)
    }:

        raise RuntimeError(
            "JSON buoc 1 thieu 80 dap an."
        )

    for number in range(1, 81):

        if compact(
            source_answers[str(number)]
        ) != compact(
            answers[number]
        ):

            raise RuntimeError(
                f"Dap an cau {number} "
                "khong khop PDF."
            )

    expected_tokens = {
        str(number): tokens[number]
        for number in range(71, 76)
    }

    if (
        source.get("cum_tu_sap_xep")
        != expected_tokens
    ):

        raise RuntimeError(
            "Cum tu 71-75 khong khop PDF."
        )

    print("\n===== KIEM TRA DAP AN =====")

    print("Nghe/Doc: 70/70")
    print("Viet: 10/10")
    print("Cum tu sap xep: 5/5")
    print("Tong dap an: 80/80")

    # ================================================
    # 25. KIEM TRA MANIFEST ANH
    # ============================================

    question_manifest = manifest.get(
        "cau_hoi", {}
    )

    group_manifest = manifest.get(
        "bang_lua_chon", {}
    )

    if set(question_manifest) != {
        str(n) for n in range(1, 81)
    }:

        raise RuntimeError(
            "Manifest khong du 80 cau."
        )

    if set(group_manifest) != set(GROUPS):

        raise RuntimeError(
            "Manifest khong du 6 bang."
        )

    copies = []

    # ================================================
    # 26. KIEM TRA 70 ANH CAU HOI
    # ============================================

    for number in range(1, 81):

        item = question_manifest[
            str(number)
        ]

        if (
            item.get("trang_pdf")
            != page_for(number)
            or item.get("nhom_lua_chon")
            != group_for(number)
        ):

            raise RuntimeError(
                f"Manifest sai cau {number}."
            )

        if number <= 10:

            if item.get("anh") is not None:

                raise RuntimeError(
                    f"Cau {number} "
                    "khong dung anh rieng."
                )

            continue

        relative = (
            f"questions/cau_{number:02d}.png"
        )

        if item.get("anh") != relative:

            raise RuntimeError(
                f"Manifest sai anh cau {number}."
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 27. KIEM TRA 6 BANG LUA CHON
    # ============================================

    for name, (
        page,
        first,
        last,
        labels
    ) in GROUPS.items():

        item = group_manifest[name]

        actual = (
            item.get("trang_pdf"),
            item.get("cau_tu"),
            item.get("cau_den"),
            item.get("lua_chon"),
            item.get("anh")
        )

        expected = (
            page,
            first,
            last,
            labels,
            f"groups/{name}.png"
        )

        if actual != expected:

            raise RuntimeError(
                f"Manifest sai bang {name}."
            )

        relative = (
            f"groups/{name}.png"
        )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    if len(copies) != 76:

        raise RuntimeError(
            f"Thieu anh: {len(copies)}/76"
        )

    # Quan trong:
    # Su dung truc tiep cac anh da duoc sua
    # trong OUTPUT, KHONG goi ham cat PDF.

    # ================================================
    # 28. DOC THOI LUONG MP3
    # ============================================

    try:

        duration = round(
            float(
                MP3(str(mp3_file)).info.length
            ),
            2
        )

    except Exception as exc:

        raise RuntimeError(
            f"Khong doc duoc MP3: {exc}"
        ) from exc

    if duration <= 0:

        raise RuntimeError(
            "MP3 khong hop le."
        )

    print("\n===== KIEM TRA MEDIA =====")

    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")
    print("Tong anh: 76")
    print(f"MP3: {duration} giay")

    # ================================================
    # 29. TAO JSON TU MAU DE 1
    # ============================================

    result = replace_refs(
        deepcopy(template)
    )

    result.update({
        "ma_de_goc": CODE,

        "cap_hsk": 3,
        "so_de": 10,
        "thu_tu": 10,

        "ten_hien_thi": "Đề 10",

        "so_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_phut": 85,

        "so_trang_pdf_de": 16,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": [],

        "trang_dap_an": [15, 16],

        "nguon_dap_an": "pdf_chung",

        "file_pdf": str(pdf_file),
        "file_mp3": str(mp3_file),

        "dap_an_thay_the": {},
    })

    result.pop(
        "file_dap_an",
        None
    )

    result.pop(
        "can_ra_soat",
        None
    )

    # ================================================
    # 30. CAP NHAT AUDIO
    # ============================================

    if not isinstance(
        result.get("audio"),
        dict
    ):

        raise RuntimeError(
            "JSON mau De 1 thieu audio."
        )

    result["audio"].update({
        "duong_dan": (
            "/static/media/luyen_thi/"
            f"hsk3/{CODE}.mp3"
        ),

        "thoi_luong_giay": duration,
    })

    # ================================================
    # 31. TAO 80 CAU HOI
    # ============================================

    questions = []

    for number, original in enumerate(
        template["cau_hoi"],
        start=1
    ):

        if original.get("so_cau") != number:

            raise RuntimeError(
                f"JSON mau sai cau {number}."
            )

        question = replace_refs(
            deepcopy(original)
        )

        group = group_for(number)

        choices = choices_for(
            number,
            tokens
        )

        if (
            number <= 70
            and answers[number] not in choices
        ):

            raise RuntimeError(
                f"Dap an cau {number} "
                "khong nam trong lua chon."
            )

        # ============================================
        # 32. ANH CAU HOI
        # ============================================

        if number <= 10:

            question_image = None

        else:

            question_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_10/questions/"
                f"cau_{number:02d}.png"
            )

        if group:

            group_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_10/groups/"
                f"{group}.png"
            )

        else:

            group_image = None

        # ============================================
        # 33. CAP NHAT THONG TIN
        # ============================================

        question.update({
            "so_cau": number,

            "ky_nang": skill_for(number),

            "phan": part_for(number),

            "loai_cau_hoi": kind_for(number),

            "noi_dung": None,

            "trang_pdf": page_for(number),

            "dap_an_dung": (
                answers[number]
            ),

            "lua_chon_json": [
                {
                    "ma": value,
                    "nhan": value,
                }
                for value in choices
            ],

            "da_duyet": False,

            "anh_cau_hoi": question_image,

            "anh_nhom_lua_chon": group_image,
        })

        # Dong bo cac truong dang cau.
        for field in (
            "dang",
            "dang_cau_hoi",
            "kieu_cau_hoi"
        ):

            if field in question:

                question[field] = kind_for(
                    number
                )

        question.pop(
            "dap_an_thay_the",
            None
        )

        question.pop(
            "ghi_chu_dieu_chinh_dap_an",
            None
        )

        questions.append(
            question
        )

    # ================================================
    # 34. KIEM TRA SO CAU
    # ============================================

    counts = Counter(
        question["ky_nang"]
        for question in questions
    )

    if counts != {
        "nghe": 40,
        "doc": 30,
        "viet": 10
    }:

        raise RuntimeError(
            "Sai so cau theo ky nang."
        )

    result["cau_hoi"] = questions

    # ================================================
    # 35. KIEM TRA JSON TRUOC KHI LUU
    # ============================================

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    raw = json_content.decode(
        "utf-8"
    )

    for old_ref in (
        "H31001",
        "H31010",
        "/hsk3/de_01/",
        "de_01.json"
    ):

        if old_ref in raw:

            raise RuntimeError(
                "JSON con tham chieu "
                "ma de khac: "
                + old_ref
            )

    if FINAL_FILE.exists():

        if (
            FINAL_FILE.read_bytes()
            != json_content
        ):

            raise RuntimeError(
                "JSON De 10 da ton tai voi "
                "noi dung khac.\n"
                "KHONG ghi de:\n"
                + str(FINAL_FILE)
            )

    # ================================================
    # 36. KIEM TRA MEDIA TRUOC KHI COPY
    # ============================================

    copies.append((
        mp3_file,
        MEDIA_ROOT / f"{CODE}.mp3"
    ))

    check_copies(
        copies
    )

    # ================================================
    # 37. SAO CHEP 76 ANH VA MP3
    # ============================================

    print("\n===== SAO CHEP MEDIA =====")

    for source_file, destination in copies:

        if not destination.exists():

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(
                source_file,
                destination
            )

    # ================================================
    # 38. LUU JSON
    # ============================================

    if not FINAL_FILE.exists():

        FINAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_FILE.write_bytes(
            json_content
        )

    # ================================================
    # 39. HOAN THANH
    # ============================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH CHUAN HOA HSK3 DE 10"
    )

    print("=" * 60)

    print(f"Ma de goc: {CODE}")
    print("Ten tren website: De 10")

    print("Tong cau: 80")
    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")

    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")
    print("Tong anh: 76")

    print(
        "Da su dung cac anh da sua, "
        "khong cat lai PDF."
    )

    print("PDF: 16 trang")
    print("Dap an: trang 15-16")

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 85 phut")

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
