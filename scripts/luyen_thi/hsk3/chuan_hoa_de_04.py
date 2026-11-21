
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 04 - H31004

BUOC 3: CHUAN HOA DE THI

- Lay JSON HSK3 De 1 lam mau.
- Doc va doi chieu 80 dap an H31004.
- Kiem tra 70 anh cau hoi.
- Kiem tra 6 bang lua chon chung.
- Chuan hoa Nghe 40, Doc 30, Viet 10.
- Giu hai dap an dung cua cau 75.
- Sao chep 76 anh vao static.
- Sao chep MP3 H31004.
- Tao JSON de_04.json.

KHONG ket noi SQL Server.
KHONG ghi de file khac noi dung.
KHONG sua cac de cu.
"""

from collections import Counter
from copy import deepcopy
from itertools import permutations
from pathlib import Path

import filecmp
import json
import re
import shutil
import unicodedata

import fitz
from mutagen.mp3 import MP3


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

BASE = ROOT / "scripts" / "luyen_thi"

HSK3 = BASE / "hsk3"

SOURCE = (
    BASE / "source" / "De_HSK"
    / "HSK3" / "ĐỀ 4"
)

DATA = HSK3 / "data" / "de_04"

OUTPUT = HSK3 / "output" / "de_04"

TEMPLATE = (
    HSK3 / "data" / "de_01" / "de_01.json"
)

ANSWER_JSON = DATA / "de_04_dap_an.json"

MANIFEST_JSON = (
    DATA / "hinh_80_cau_ung_vien.json"
)

FINAL_JSON = DATA / "de_04.json"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk3"
)

MEDIA = MEDIA_ROOT / "de_04"

CODE = "H31004"


# =====================================================
# 2. CUM TU SAP XEP CAU 71-75
# =====================================================

# Lay dung theo PDF H31004.
# Khong sao chep tu H31001.

TOKENS = {
    71: [
        "我的包",
        "药",
        "在",
        "里",
    ],

    72: [
        "接女朋友",
        "他",
        "去",
        "要",
        "机场",
    ],

    73: [
        "还",
        "你",
        "脚下的路",
        "长",
        "很",
    ],

    74: [
        "她",
        "用铅笔写字",
        "不",
        "喜欢",
    ],

    75: [
        "怎么了",
        "鼻子",
        "你",
        "的",
        "丈夫",
    ],
}


# =====================================================
# 3. SAU BANG LUA CHON CHUNG
# =====================================================

# Ten nhom: (trang, cau dau, cau cuoi, lua chon)

GROUPS = {
    "nghe_01_05": (2, 1, 5, "ABCDEF"),
    "nghe_06_10": (3, 6, 10, "ABCDE"),

    "doc_41_45": (7, 41, 45, "ABCDEF"),
    "doc_46_50": (8, 46, 50, "ABCDE"),
    "doc_51_55": (9, 51, 55, "ABCDEF"),
    "doc_56_60": (10, 56, 60, "ABCDEF"),
}


# =====================================================
# 4. SO DO TRANG CAU HOI
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
# 5. CAC HAM DOC FILE
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


def load(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def norm(text):

    return unicodedata.normalize(
        "NFKC",
        str(text)
    )


def compact(text):

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        norm(text)
    )


# =====================================================
# 6. DOI THAM CHIEU DE 1 THANH DE 4
# =====================================================

def new_refs(value):

    if isinstance(value, str):

        return (
            value
            .replace("H31001", CODE)
            .replace("de_01", "de_04")
            .replace("Đề 1", "Đề 4")
            .replace("ĐỀ 1", "ĐỀ 4")
        )

    if isinstance(value, list):

        return [
            new_refs(v)
            for v in value
        ]

    if isinstance(value, dict):

        return {
            k: new_refs(v)
            for k, v in value.items()
        }

    return value


# =====================================================
# 7. XAC DINH KY NANG
# =====================================================

def skill(n):

    if n <= 40:
        return "nghe"

    if n <= 70:
        return "doc"

    return "viet"


# =====================================================
# 8. XAC DINH LOAI CAU HOI
# =====================================================

def kind(n):

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

def part(n):

    if n <= 40:

        number = (n - 1) // 10 + 1

        return f"Nghe - Phần {number}"

    if n <= 50:
        return "Đọc - Phần 1"

    if n <= 60:
        return "Đọc - Phần 2"

    if n <= 70:
        return "Đọc - Phần 3"

    if n <= 75:
        return "Viết - Phần 1"

    return "Viết - Phần 2"


def page_of(n):

    for page, items in PAGES.items():

        if n in items:
            return page

    raise RuntimeError(
        f"Khong tim thay trang cau {n}."
    )


def group_of(n):

    for name, (
        page,
        first,
        last,
        labels
    ) in GROUPS.items():

        if first <= n <= last:
            return name

    return None


# =====================================================
# 10. TAO LUA CHON CAU HOI
# =====================================================

def choices(n):

    if n <= 5:
        values = list("ABCDEF")

    elif n <= 10:
        values = list("ABCDE")

    elif n <= 20:
        values = ["√", "×"]

    elif n <= 40:
        values = list("ABC")

    elif n <= 45:
        values = list("ABCDEF")

    elif n <= 50:
        values = list("ABCDE")

    elif n <= 60:
        values = list("ABCDEF")

    elif n <= 70:
        values = list("ABC")

    elif n <= 75:
        values = TOKENS[n]

    else:
        values = []

    return [
        {
            "ma": value,
            "nhan": value,
        }
        for value in values
    ]


# =====================================================
# 11. DOC DAP AN TRUC TIEP TU PDF
# =====================================================

def answers_from_pdf(pdf_path):

    with fitz.open(pdf_path) as doc:

        if len(doc) != 22:
            raise RuntimeError(
                "PDF H31004 phai co 22 trang."
            )

        for page_no in (1, 21, 22):

            text = norm(
                doc[page_no - 1].get_text(
                    "text"
                )
            )

            if CODE not in text:
                raise RuntimeError(
                    f"Trang {page_no} sai ma de."
                )

        page21 = norm(
            doc[20].get_text("text")
        )

        page22 = norm(
            doc[21].get_text("text")
        )

        if (
            "答案" not in page21
            or "书" not in page22
        ):
            raise RuntimeError(
                "Trang 21-22 khong phai "
                "bang dap an."
            )

        # ============================================
        # 12. LAY 70 DAP AN NGHE/DOC
        # ============================================

        objective = {}

        pattern = re.compile(
            r"(?<!\d)(\d{1,2})\s*[.、]"
            r"\s*([A-F√×])(?=\s|$)"
        )

        for match in pattern.finditer(page21):

            n = int(match.group(1))

            if not 1 <= n <= 70:
                continue

            if n in objective:
                raise RuntimeError(
                    f"Trung dap an cau {n}."
                )

            objective[n] = match.group(2)

        if set(objective) != set(range(1, 71)):
            raise RuntimeError(
                "Trang 21 khong du 70 dap an."
            )

        # ============================================
        # 13. LAY 10 DAP AN VIET
        # ============================================

        writing = {}

        writing_pattern = re.compile(
            r"^\s*(7[1-9]|80)\s*[.、]"
            r"\s*([^\n]+)",
            re.MULTILINE
        )

        for match in writing_pattern.finditer(
            page22
        ):

            n = int(match.group(1))

            if n in writing:
                raise RuntimeError(
                    f"Trung dap an Viet cau {n}."
                )

            # Cau 75 co hai dap an
            # ngan cach bang dau /.
            writing[n] = [
                value.strip()
                for value in (
                    match.group(2).split("/")
                )
                if value.strip()
            ]

        if set(writing) != set(range(71, 81)):
            raise RuntimeError(
                "Trang 22 khong du 10 dap an."
            )

        # Chi cau 75 co hai dap an.
        for n, values in writing.items():

            expected_count = (
                2 if n == 75 else 1
            )

            if len(values) != expected_count:
                raise RuntimeError(
                    f"Cau Viet {n} sai "
                    "so luong dap an."
                )

        if (
            compact(writing[75][0])
            == compact(writing[75][1])
        ):
            raise RuntimeError(
                "Hai dap an cau 75 bi trung."
            )

        # Dap an dau tien la dap an chinh.
        answers = {
            **objective,

            **{
                n: values[0]
                for n, values in writing.items()
            },
        }

        # Dap an thu hai duoc bao toan.
        alternatives = {
            "75": writing[75][1:]
        }

        return answers, alternatives


# =====================================================
# 14. DOI CHIEU CUM TU SAP XEP
# =====================================================

def check_writing_tokens(
    answers,
    alternatives
):

    for n in range(71, 76):

        valid_sentences = [
            answers[n]
        ]

        valid_sentences += (
            alternatives.get(str(n), [])
        )

        combinations = {
            compact("".join(order))

            for order in permutations(
                TOKENS[n]
            )
        }

        for sentence in valid_sentences:

            if compact(sentence) not in combinations:

                raise RuntimeError(
                    f"Cau {n} khong ghep duoc "
                    f"dap an: {sentence}"
                )

    # Cau 76-80 chi dien mot chu Han.
    for n in range(76, 81):

        if len(compact(answers[n])) != 1:
            raise RuntimeError(
                f"Cau {n} khong phai "
                "dien mot chu Han."
            )


# =====================================================
# 15. KIEM TRA FILE DICH TRUOC KHI COPY
# =====================================================

def check_media_before_copy(pairs):

    for source, destination in pairs:

        require_file(source)

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
# 16. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)
    print("MOC HAN - HSK3 DE 04")
    print("BUOC 3: CHUAN HOA H31004")
    print("=" * 60)

    # ================================================
    # 17. DOC JSON MAU VA JSON NGUON
    # ================================================

    template = load(TEMPLATE)

    source = load(ANSWER_JSON)

    manifest = load(MANIFEST_JSON)

    if (
        template.get("ma_de_goc") != "H31001"
        or len(template.get("cau_hoi", [])) != 80
    ):
        raise RuntimeError(
            "JSON mau H31001 khong hop le."
        )

    if (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    ) != (3, 4, CODE):
        raise RuntimeError(
            "JSON dap an buoc 1 "
            "khong phai H31004."
        )

    if (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau")
    ) != (3, 4, CODE, 80):
        raise RuntimeError(
            "Manifest buoc 2 "
            "khong phai H31004."
        )

    # ================================================
    # 18. TIM PDF VA MP3
    # ================================================

    pdfs = sorted(
        SOURCE.glob("*.pdf")
    )

    mp3s = sorted(
        SOURCE.glob("*.mp3")
    )

    if len(pdfs) != 1 or len(mp3s) != 1:
        raise RuntimeError(
            "Thu muc DE 4 phai co "
            "dung 1 PDF va 1 MP3."
        )

    pdf_file = require_file(
        pdfs[0]
    )

    mp3_file = require_file(
        mp3s[0]
    )

    source_pdf = Path(
        source.get("file_pdf", "")
    )

    if (
        source_pdf.resolve()
        != pdf_file.resolve()
    ):
        raise RuntimeError(
            "PDF buoc 1 khong khop "
            "PDF trong thu muc goc."
        )

    # ================================================
    # 19. DOI CHIEU 80 DAP AN
    # ================================================

    pdf_answers, pdf_alt = (
        answers_from_pdf(pdf_file)
    )

    answers = source.get(
        "dap_an", {}
    )

    if set(answers) != {
        str(n) for n in range(1, 81)
    }:
        raise RuntimeError(
            "JSON buoc 1 khong du 80 dap an."
        )

    for n in range(1, 81):

        if compact(
            answers[str(n)]
        ) != compact(
            pdf_answers[n]
        ):
            raise RuntimeError(
                f"Dap an cau {n} "
                "khong khop PDF."
            )

    # ================================================
    # 20. KIEM TRA DAP AN THAY THE CAU 75
    # ================================================

    source_alt = source.get(
        "dap_an_thay_the", {}
    )

    if (
        set(source_alt) != {"75"}
        or len(source_alt["75"]) != 1
        or compact(source_alt["75"][0])
        != compact(pdf_alt["75"][0])
    ):
        raise RuntimeError(
            "Dap an thay the cau 75 "
            "khong khop PDF."
        )

    check_writing_tokens(
        pdf_answers,
        pdf_alt
    )

    print("\n===== DAP AN =====")
    print("Nghe/Doc: 70/70")
    print("Viet: 10/10")
    print("Cau 75: 2 dap an hop le")

    # ================================================
    # 21. KIEM TRA MANIFEST 80 CAU
    # ================================================

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

    # ================================================
    # 22. KIEM TRA 70 ANH CAU HOI
    # ================================================

    copies = []

    for n in range(1, 81):

        info = question_manifest[
            str(n)
        ]

        if (
            info.get("trang_pdf") != page_of(n)
            or info.get("nhom_lua_chon")
            != group_of(n)
        ):
            raise RuntimeError(
                f"Manifest sai trang/"
                f"nhom cau {n}."
            )

        if n <= 10:

            if info.get("anh") is not None:
                raise RuntimeError(
                    f"Cau {n} khong duoc "
                    "co anh rieng."
                )

            continue

        relative = (
            f"questions/cau_{n:02d}.png"
        )

        if info.get("anh") != relative:
            raise RuntimeError(
                f"Manifest sai anh cau {n}."
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 23. KIEM TRA 6 BANG LUA CHON
    # ================================================

    for name, (
        page,
        first,
        last,
        labels
    ) in GROUPS.items():

        info = group_manifest[name]

        actual = (
            info.get("trang_pdf"),
            info.get("cau_tu"),
            info.get("cau_den"),
            info.get("lua_chon")
        )

        expected = (
            page,
            first,
            last,
            labels
        )

        if actual != expected:
            raise RuntimeError(
                f"Manifest sai bang {name}."
            )

        relative = (
            f"groups/{name}.png"
        )

        if info.get("anh") != relative:
            raise RuntimeError(
                f"Manifest sai file bang {name}."
            )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    if len(copies) != 76:
        raise RuntimeError(
            "Khong du 76 anh."
        )

    print("\n===== HINH ANH =====")
    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")

    # ================================================
    # 24. DOC THOI LUONG MP3
    # ================================================

    duration = round(
        float(
            MP3(str(mp3_file)).info.length
        ),
        2
    )

    if not 0 < duration < 99999999:
        raise RuntimeError(
            "Thoi luong MP3 khong hop le."
        )

    # ================================================
    # 25. TAO JSON TU MAU H31001
    # ================================================

    result = new_refs(
        deepcopy(template)
    )

    result.update({
        "cap_hsk": 3,
        "so_de": 4,
        "ma_de_goc": CODE,

        "ten_hien_thi": "Đề 4",
        "thu_tu": 4,

        "so_cau": 80,
        "so_cau_nghe": 40,
        "so_cau_doc": 30,
        "so_cau_viet": 10,

        "thoi_gian_phut": 85,
        "so_trang_pdf_de": 22,

        "trang_cau_hoi": list(
            range(2, 15)
        ),

        "trang_loi_thoai": list(
            range(15, 21)
        ),

        "trang_dap_an": [21, 22],

        "nguon_dap_an": "pdf_chung",

        "file_pdf": str(pdf_file),
        "file_mp3": str(mp3_file),

        # Luu dap an thay the tu PDF.
        "dap_an_thay_the": pdf_alt,
    })

    result.pop(
        "file_dap_an",
        None
    )

    # ================================================
    # 26. CAP NHAT AUDIO
    # ================================================

    if not isinstance(
        result.get("audio"),
        dict
    ):
        raise RuntimeError(
            "JSON mau H31001 thieu audio."
        )

    result["audio"]["duong_dan"] = (
        "/static/media/luyen_thi/"
        f"hsk3/{CODE}.mp3"
    )

    result["audio"]["thoi_luong_giay"] = (
        duration
    )

    # ================================================
    # 27. TAO 80 CAU HOI
    # ================================================

    questions = []

    for n, original in enumerate(
        template["cau_hoi"],
        start=1
    ):

        if original.get("so_cau") != n:
            raise RuntimeError(
                f"Mau H31001 sai cau {n}."
            )

        question = new_refs(
            deepcopy(original)
        )

        group = group_of(n)

        if n <= 10:
            question_image = None

        else:
            question_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_04/questions/"
                f"cau_{n:02d}.png"
            )

        if group:
            group_image = (
                "/static/media/luyen_thi/"
                "hsk3/de_04/groups/"
                f"{group}.png"
            )

        else:
            group_image = None

        question.update({
            "so_cau": n,

            "ky_nang": skill(n),
            "phan": part(n),

            "loai_cau_hoi": kind(n),

            # Noi dung goc da co trong anh.
            # Khong ke thua text De 1.
            "noi_dung": None,

            "trang_pdf": page_of(n),

            "dap_an_dung": (
                pdf_answers[n]
            ),

            "lua_chon_json": choices(n),

            "da_duyet": False,

            "anh_cau_hoi": question_image,

            "anh_nhom_lua_chon": group_image,
        })

        # Dong bo cac truong loai cau.
        for field in (
            "dang",
            "dang_cau_hoi",
            "kieu_cau_hoi"
        ):

            if field in question:
                question[field] = kind(n)

        question.pop(
            "dap_an_thay_the",
            None
        )

        # Cau 75 co hai dap an.
        if n == 75:
            question["dap_an_thay_the"] = list(
                pdf_alt["75"]
            )

        # Dap an trac nghiem phai nam
        # trong cac lua chon.
        if n <= 70:

            allowed = {
                item["ma"]
                for item in choices(n)
            }

            if pdf_answers[n] not in allowed:
                raise RuntimeError(
                    f"Cau {n} sai phuong an."
                )

        questions.append(question)

    result["cau_hoi"] = questions

    # ================================================
    # 28. KIEM TRA KY NANG
    # ================================================

    counts = Counter(
        question["ky_nang"]
        for question in questions
    )

    if counts != {
        "nghe": 40,
        "doc": 30,
        "viet": 10,
    }:
        raise RuntimeError(
            "Sai so cau theo ky nang."
        )

    # ================================================
    # 29. KIEM TRA JSON MOI
    # ================================================

    json_content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    raw = json_content.decode("utf-8")

    for old_ref in (
        "H31001",
        "/hsk3/de_01/",
        "de_01.json",
    ):

        if old_ref in raw:
            raise RuntimeError(
                "JSON van tham chieu De 1: "
                + old_ref
            )

    if FINAL_JSON.exists():

        if (
            FINAL_JSON.read_bytes()
            != json_content
        ):
            raise RuntimeError(
                "JSON De 4 da ton tai "
                "voi noi dung khac.\n"
                "Khong ghi de:\n"
                + str(FINAL_JSON)
            )

    # ================================================
    # 30. KIEM TRA MEDIA DICH
    # ================================================

    copies.append((
        mp3_file,
        MEDIA_ROOT / f"{CODE}.mp3"
    ))

    check_media_before_copy(
        copies
    )

    # ================================================
    # 31. SAO CHEP 76 ANH VA MP3
    # ================================================

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
    # 32. LUU JSON
    # ================================================

    if not FINAL_JSON.exists():

        FINAL_JSON.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_JSON.write_bytes(
            json_content
        )

    # ================================================
    # 33. KET QUA
    # ================================================

    print("\n" + "=" * 60)
    print("HOAN THANH CHUAN HOA HSK3 DE 04")
    print("=" * 60)

    print("Ma de: H31004")
    print("Cap: HSK3")

    print("Tong cau: 80")
    print("Nghe: 40")
    print("Doc: 30")
    print("Viet: 10")

    print("Dap an: 80/80")
    print("Anh cau hoi: 70/70")
    print("Bang chung: 6/6")

    print("Cau 75: da luu 2 dap an trong JSON")

    print(f"MP3: {duration} giay")
    print("Thoi gian thi: 85 phut")

    print(f"\nJSON: {FINAL_JSON}")

    print("\nCHUA thay doi SQL Server.")


if __name__ == "__main__":
    main()
