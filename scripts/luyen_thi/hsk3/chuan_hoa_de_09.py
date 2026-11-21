
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 09 - BUOC 3: CHUAN HOA H31327

- Lay JSON HSK3 De 1 lam mau, giu nguyen cac de cu.
- Doc lai 80 dap an va cum tu 71-75 tu PDF goc (16 trang).
- Doi chieu JSON buoc 1 va manifest buoc 2.
- Kiem tra 70 anh cau hoi + 6 bang lua chon.
- Sao chep 76 anh va MP3 sang static, tao de_09.json.
- KHONG ket noi SQL; KHONG ghi de file khac noi dung.
"""

from collections import Counter
from copy import deepcopy
from itertools import permutations
from pathlib import Path

import filecmp
import json
import os
import re
import shutil
import unicodedata

import fitz
from mutagen.mp3 import MP3


# =====================================================
# 1. DUONG DAN VA MA DE GOC
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
    / "HSK3" / "ĐỀ 9"
)

DATA = HSK3 / "data" / "de_09"
OUTPUT = HSK3 / "output" / "de_09"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk3"
)

MEDIA = MEDIA_ROOT / "de_09"

TEMPLATE = (
    HSK3 / "data" / "de_01" / "de_01.json"
)

ANSWER_JSON = (
    DATA / "de_09_dap_an.json"
)

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

FINAL_JSON = DATA / "de_09.json"

# Dung ma tren bia PDF, KHONG phai H31009.
CODE = "H31327"


# =====================================================
# 2. SO DO TRANG / NHOM LUA CHON
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
# 3. HAM CHUNG
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


def load_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def norm(value):

    return unicodedata.normalize(
        "NFKC",
        str(value)
    )


def compact(value):

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        norm(value)
    )


# =====================================================
# 4. DOI THAM CHIEU DE 1 SANG DE 9
# =====================================================

def change_refs(value):

    if isinstance(value, str):

        return (
            value
            .replace("H31001", CODE)
            .replace("de_01", "de_09")
            .replace("Đề 1", "Đề 9")
            .replace("ĐỀ 1", "ĐỀ 9")
        )

    if isinstance(value, list):

        return [
            change_refs(v)
            for v in value
        ]

    if isinstance(value, dict):

        return {
            k: change_refs(v)
            for k, v in value.items()
        }

    return value


# =====================================================
# 5. XAC DINH TRANG PDF
# =====================================================

def page_for(n):

    for page, numbers in PAGES.items():

        if n in numbers:
            return page

    raise RuntimeError(
        f"Khong co trang PDF cho cau {n}"
    )


# =====================================================
# 6. XAC DINH NHOM LUA CHON
# =====================================================

def group_for(n):

    for name, (
        _page,
        first,
        last,
        _labels
    ) in GROUPS.items():

        if first <= n <= last:
            return name

    return None


# =====================================================
# 7. XAC DINH KY NANG
# =====================================================

def skill_for(n):

    if n <= 40:
        return "nghe"

    if n <= 70:
        return "doc"

    return "viet"


# =====================================================
# 8. XAC DINH LOAI CAU HOI
# =====================================================

def kind_for(n):

    if n <= 10:
        return "chon_hinh"

    if n <= 20:
        return "dung_sai"

    if n <= 40:
        return "chon_mot"

    if n <= 60:
        return "ghep_lua_chon"

    if n <= 70:
        return "chon_mot"

    if n <= 75:
        return "sap_xep"

    return "dien_tu"


# =====================================================
# 9. XAC DINH PHAN THI
# =====================================================

def part_for(n):

    if n <= 40:

        part_number = (
            (n - 1) // 10 + 1
        )

        return f"Nghe - Phần {part_number}"

    if n <= 50:
        return "Đọc - Phần 1"

    if n <= 60:
        return "Đọc - Phần 2"

    if n <= 70:
        return "Đọc - Phần 3"

    if n <= 75:
        return "Viết - Phần 1"

    return "Viết - Phần 2"


# =====================================================
# 10. TAO LUA CHON
# =====================================================

def choices_for(n, tokens):

    if n <= 5:
        return list("ABCDEF")

    if n <= 10:
        return list("ABCDE")

    if n <= 20:
        return ["√", "×"]

    if n <= 40:
        return list("ABC")

    if n <= 45:
        return list("ABCDEF")

    if n <= 50:
        return list("ABCDE")

    if n <= 60:
        return list("ABCDEF")

    if n <= 70:
        return list("ABC")

    if n <= 75:
        return tokens[n]

    return []


# =====================================================
# 11. DOI CHIEU DAP AN TRUC TIEP TU PDF
# =====================================================

def read_pdf_data(pdf_path):

    with fitz.open(pdf_path) as doc:

        if len(doc) != 16:

            raise RuntimeError(
                "PDF H31327 can 16 trang, "
                f"hien co {len(doc)}"
            )

        cover = norm(
            doc[0].get_text("text")
        )

        answer_page = norm(
            doc[14].get_text("text")
        )

        writing_page = (
            doc[15].get_text("text")
        )

        if (
            CODE not in cover
            or CODE not in answer_page
        ):
            raise RuntimeError(
                "Ma de goc tren PDF "
                "khong phai H31327"
            )

        if (
            "答案" not in answer_page
            or "书" not in writing_page
        ):
            raise RuntimeError(
                "Trang 15-16 "
                "khong phai trang dap an"
            )

        # ============================================
        # 12. LAY 70 DAP AN NGHE/DOC
        # ============================================

        objective = {}

        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.．、]"
            r"\s*([A-F√×])(?=\s|$)"
        )

        for match in pattern.finditer(
            answer_page
        ):

            n = int(
                match.group(1)
            )

            value = match.group(2)

            if not 1 <= n <= 70:
                continue

            if n in objective:
                raise RuntimeError(
                    f"Trung dap an cau {n}"
                )

            objective[n] = value

        if set(objective) != set(
            range(1, 71)
        ):
            raise RuntimeError(
                "Trang 15 khong du "
                "70 dap an Nghe/Doc"
            )

        # ============================================
        # 13. LAY 10 DAP AN VIET
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

            n = int(
                match.group(1)
            )

            value = (
                match.group(2).strip()
            )

            if n in writing:
                raise RuntimeError(
                    f"Trung dap an Viet cau {n}"
                )

            if "/" in value:
                raise RuntimeError(
                    f"Cau {n} co dap an thay the, "
                    "can xu ly rieng"
                )

            writing[n] = value

        if set(writing) != set(
            range(71, 81)
        ):
            raise RuntimeError(
                "Trang 16 khong du "
                "10 dap an Viet"
            )

        # ============================================
        # 14. DOC CUM TU SAP XEP CAU 71-75
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

            match = pattern.match(
                line
            )

            if not match:
                continue

            n = int(
                match.group(1)
            )

            if n in tokens:
                raise RuntimeError(
                    f"Trung cum tu cau {n}"
                )

            tokens[n] = [
                x.strip()

                for x in re.split(
                    r"\s{2,}",
                    match.group(2)
                )

                if x.strip()
            ]

        if set(tokens) != set(
            range(71, 76)
        ):
            raise RuntimeError(
                "Khong doc du cum tu "
                "cau 71-75"
            )

        # ============================================
        # 15. KIEM TRA DAP AN SAP XEP
        # ============================================

        for n in range(71, 76):

            values = tokens[n]

            if not 3 <= len(values) <= 8:

                raise RuntimeError(
                    f"So cum tu cau {n} sai: "
                    f"{values}"
                )

            valid = any(
                compact("".join(order))
                == compact(writing[n])

                for order in permutations(
                    values
                )
            )

            if not valid:

                raise RuntimeError(
                    f"Cau {n}: dap an "
                    "khong ghep duoc tu PDF"
                )

        # ============================================
        # 16. KIEM TRA CAU 76-80
        # ============================================

        for n in range(76, 81):

            if len(
                compact(writing[n])
            ) != 1:

                raise RuntimeError(
                    f"Cau {n}: phai dien "
                    "mot chu Han"
                )

        return {
            **objective,
            **writing
        }, tokens


# =====================================================
# 17. KIEM TRA MEDIA TRUOC KHI SAO CHEP
# =====================================================

def check_copy_pairs(pairs):

    for source, destination in pairs:

        require_file(source)

        # Kiem tra anh PNG.
        if source.suffix.lower() == ".png":

            if not source.read_bytes().startswith(
                b"\x89PNG\r\n\x1a\n"
            ):

                raise RuntimeError(
                    f"Anh PNG khong hop le: {source}"
                )

        # Khong ghi de file khac noi dung.
        if destination.exists():

            if not filecmp.cmp(
                source,
                destination,
                shallow=False
            ):

                raise RuntimeError(
                    "Khong ghi de media "
                    "khac noi dung:\n"
                    + str(destination)
                )


# =====================================================
# 18. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 09 - BUOC 3")
    print("MA DE GOC H31327")
    print("=" * 60)

    # ================================================
    # 19. DOC JSON TU CAC BUOC TRUOC
    # ============================================

    template = load_json(
        TEMPLATE
    )

    source = load_json(
        ANSWER_JSON
    )

    manifest = load_json(
        MANIFEST_JSON
    )

    if (
        template.get("ma_de_goc") != "H31001"
        or len(
            template.get("cau_hoi", [])
        ) != 80
    ):
        raise RuntimeError(
            "JSON mau HSK3 De 1 khong hop le"
        )

    if (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    ) != (3, 9, CODE):

        raise RuntimeError(
            "JSON buoc 1 khong phai "
            "De 9 - H31327"
        )

    if (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau")
    ) != (3, 9, CODE, 80):

        raise RuntimeError(
            "Manifest buoc 2 khong phai "
            "De 9 - H31327"
        )

    # ================================================
    # 20. KIEM TRA BO CUC PDF
    # ============================================

    if (
        manifest.get("so_trang_pdf") != 16
        or manifest.get("trang_dap_an")
        != [15, 16]
        or manifest.get("trang_loi_thoai")
        != []
    ):

        raise RuntimeError(
            "Manifest sai bo cuc PDF 16 trang"
        )

    # ================================================
    # 21. KIEM TRA DAP AN THAY THE
    # ============================================

    if (
        source.get("dap_an_thay_the") != {}
        or manifest.get("dap_an_thay_the")
        != {}
    ):

        raise RuntimeError(
            "Co dap an thay the "
            "chua duoc xu ly"
        )

    # ================================================
    # 22. TIM PDF VA MP3
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
            "Thu muc DE 9 can dung "
            "1 PDF va 1 MP3"
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
            "PDF buoc 1 khong khop PDF goc"
        )

    if source.get("file_mp3"):

        if (
            Path(
                source["file_mp3"]
            ).resolve() != mp3_file.resolve()
        ):

            raise RuntimeError(
                "MP3 buoc 1 khong khop "
                "file goc"
            )

    # ================================================
    # 23. DOI CHIEU 80 DAP AN
    # ============================================

    answers, tokens = read_pdf_data(
        pdf_file
    )

    source_answers = source.get(
        "dap_an", {}
    )

    if set(source_answers) != {
        str(n)
        for n in range(1, 81)
    }:

        raise RuntimeError(
            "JSON buoc 1 khong du 80 dap an"
        )

    for n in range(1, 81):

        if compact(
            source_answers[str(n)]
        ) != compact(
            answers[n]
        ):

            raise RuntimeError(
                f"Dap an cau {n} "
                "khong khop PDF"
            )

    # ================================================
    # 24. DOI CHIEU CUM TU SAP XEP
    # ============================================

    expected_tokens = {
        str(n): tokens[n]
        for n in range(71, 76)
    }

    if (
        source.get("cum_tu_sap_xep")
        != expected_tokens
    ):

        raise RuntimeError(
            "Cum tu 71-75 khong khop PDF"
        )

    print("\n===== KIEM TRA DAP AN =====")
    print("Nghe/Doc: 70/70")
    print("Viet: 10/10")
    print("Cum tu sap xep: 5/5")
    print("Tong dap an: 80/80")

    # ================================================
    # 25. KIEM TRA MANIFEST 80 CAU
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
            "Manifest khong du 80 cau"
        )

    if set(group_manifest) != set(
        GROUPS
    ):

        raise RuntimeError(
            "Manifest khong du 6 bang"
        )

    # ================================================
    # 26. KIEM TRA 70 ANH CAU HOI
    # ============================================

    copies = []

    for n in range(1, 81):

        item = question_manifest[
            str(n)
        ]

        if (
            item.get("trang_pdf")
            != page_for(n)
            or item.get("nhom_lua_chon")
            != group_for(n)
        ):

            raise RuntimeError(
                f"Manifest sai trang/nhom cau {n}"
            )

        if n <= 10:

            if item.get("anh") is not None:

                raise RuntimeError(
                    f"Cau {n} khong duoc "
                    "co anh rieng"
                )

            continue

        relative = (
            f"questions/cau_{n:02d}.png"
        )

        if item.get("anh") != relative:

            raise RuntimeError(
                f"Manifest sai anh cau {n}"
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
                f"Manifest sai bang {name}"
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

    if not 0 < duration < 99999999:

        raise RuntimeError(
            "MP3 khong co thoi luong hop le"
        )

    print("\n===== KIEM TRA MEDIA =====")
    print("Anh cau hoi: 70/70")
    print("Bang lua chon: 6/6")
    print(f"MP3: {duration} giay")

    # ================================================
    # 29. TAO JSON TU MAU DE 1
    # ============================================

    result = change_refs(
        deepcopy(template)
    )

    result.update({
        "ma_de_goc": CODE,

        "cap_hsk": 3,
        "so_de": 9,
        "thu_tu": 9,

        "ten_hien_thi": "Đề 9",

        "so_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_phut": 85,

        "so_trang_pdf_de": 16,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        # PDF De 9 khong co transcript.
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
            "JSON mau De 1 thieu audio"
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

    for n, original in enumerate(
        template["cau_hoi"],
        start=1
    ):

        if original.get("so_cau") != n:

            raise RuntimeError(
                f"JSON mau sai so cau {n}"
            )

        question = change_refs(
            deepcopy(original)
        )

        group = group_for(n)

        choices = choices_for(
            n,
            tokens
        )

        if (
            n <= 70
            and answers[n] not in choices
        ):

            raise RuntimeError(
                f"Dap an cau {n} "
                "khong nam trong lua chon"
            )

        question.update({
            "so_cau": n,

            "ky_nang": skill_for(n),

            "phan": part_for(n),

            "loai_cau_hoi": kind_for(n),

            # Noi dung cau hoi da co trong anh.
            "noi_dung": None,

            "trang_pdf": page_for(n),

            "dap_an_dung": answers[n],

            "lua_chon_json": [
                {
                    "ma": value,
                    "nhan": value,
                }
                for value in choices
            ],

            "da_duyet": False,

            "anh_cau_hoi": (
                None
                if n <= 10
                else (
                    "/static/media/luyen_thi/"
                    "hsk3/de_09/questions/"
                    f"cau_{n:02d}.png"
                )
            ),

            "anh_nhom_lua_chon": (
                None
                if not group
                else (
                    "/static/media/luyen_thi/"
                    "hsk3/de_09/groups/"
                    f"{group}.png"
                )
            ),
        })

        # Dong bo truong loai cau neu co.
        for key in (
            "dang",
            "dang_cau_hoi",
            "kieu_cau_hoi"
        ):

            if key in question:
                question[key] = kind_for(n)

        # Khong ke thua dap an thay the
        # va ghi chu cua de khac.
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
    # 32. KIEM TRA SO CAU THEO KY NANG
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
            "Sai so cau theo ky nang"
        )

    result["cau_hoi"] = questions

    # ================================================
    # 33. KIEM TRA JSON TRUOC KHI LUU
    # ============================================

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    raw = json_content.decode(
        "utf-8"
    )

    # Khong duoc ke thua ma De 1
    # hoac dung nham ma H31009.
    for old_ref in (
        "H31001",
        "/hsk3/de_01/",
        "de_01.json",
        "H31009"
    ):

        if old_ref in raw:

            raise RuntimeError(
                "JSON con tham chieu "
                "ma de khac: "
                + old_ref
            )

    if FINAL_JSON.exists():

        if (
            FINAL_JSON.read_bytes()
            != json_content
        ):

            raise RuntimeError(
                "JSON De 9 da ton tai "
                "voi noi dung khac.\n"
                "KHONG ghi de:\n"
                + str(FINAL_JSON)
            )

    # ================================================
    # 34. KIEM TRA MEDIA DICH
    # ============================================

    copies.append((
        mp3_file,
        MEDIA_ROOT / f"{CODE}.mp3"
    ))

    check_copy_pairs(
        copies
    )

    # ================================================
    # 35. SAO CHEP 76 ANH VA MP3
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
    # 36. LUU JSON
    # ============================================

    if not FINAL_JSON.exists():

        FINAL_JSON.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_JSON.write_bytes(
            json_content
        )

    # ================================================
    # 37. KET QUA
    # ============================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH CHUAN HOA HSK3 DE 09"
    )

    print("=" * 60)

    print(f"Ma de goc: {CODE}")
    print("Ten tren website: De 9")

    print(
        "Tong cau: 80 "
        "(Nghe 40, Doc 30, Viet 10)"
    )

    print("Dap an: 80/80")
    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")
    print("Tong anh: 76")

    print(
        "PDF: 16 trang, "
        "dap an trang 15-16"
    )

    print(
        "Dap an thay the trong PDF: khong co"
    )

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 85 phut")

    print(f"\nJSON: {FINAL_JSON}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
