
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK4 DE 01 (H41001)
BUOC 3 - CHUAN HOA DE THI

- Kiem tra JSON dap an buoc 1.
- Kiem tra manifest 100 cau buoc 2.
- Kiem tra 10 cau sap xep Viet 86-95.
- Giu dap an thay the cau 86, 91, 95.
- Luu dap an tham khao Viet mo 96-100.
- Sao chep 100 anh, 2 bang chung va MP3.
- Tao JSON chuan de_01.json.

CHUA NHAP SQL.
CHUA SUA DE THI CU.
CAN NANG CAP CHAM DIEM TRUOC KHI NHAP HSK4.
"""

from pathlib import Path
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

SOURCE = BASE / "source" / "De_HSK" / "HSK4"
DATA = BASE / "hsk4" / "data" / "de_01"
OUTPUT = BASE / "hsk4" / "output" / "de_01"

MEDIA_ROOT = (
    ROOT / "static" / "media"
    / "luyen_thi" / "hsk4"
)

MEDIA = MEDIA_ROOT / "de_01"

PDF_FILE = SOURCE / "H41001.pdf"
MP3_FILE = SOURCE / "H41001.mp3"

ANSWER_FILE = DATA / "de_01_dap_an.json"

MANIFEST_FILE = (
    DATA / "hinh_100_cau_ung_vien.json"
)

FINAL_FILE = DATA / "de_01.json"

CODE = "H41001"


# =====================================================
# 2. BANG DOC CHUNG
# =====================================================

GROUPS = {
    "doc_46_50": (7, 46, 50, "ABCDEF"),
    "doc_51_55": (8, 51, 55, "ABCDEF"),
}


# =====================================================
# 3. SO DO TRANG PDF
# =====================================================

PAGE_MAP = {
    2: range(1, 11),
    3: range(11, 21),
    4: range(21, 26),
    5: range(26, 35),
    6: range(35, 46),

    7: range(46, 51),
    8: range(51, 56),

    9: range(56, 60),
    10: range(60, 66),

    11: range(66, 70),
    12: range(70, 76),
    13: range(76, 82),
    14: range(82, 86),

    15: range(86, 96),
    16: range(96, 101),
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
            f"Thieu file hoac file rong: {path}"
        )

    return path


def read_json(path):

    return json.loads(
        require_file(path).read_text(
            encoding="utf-8-sig"
        )
    )


def compact(value):

    value = unicodedata.normalize(
        "NFKC",
        str(value)
    )

    return re.sub(
        r"[\s，。！？!?、,.;；：:]",
        "",
        value
    )


# =====================================================
# 5. XAC DINH TRANG PDF
# =====================================================

def page_for(number):

    for page, numbers in PAGE_MAP.items():

        if number in numbers:
            return page

    raise RuntimeError(
        f"Khong co trang cho cau {number}"
    )


# =====================================================
# 6. XAC DINH PHAN THI
# =====================================================

def part_for(number):

    if number <= 10:
        return "Nghe - Phần 1"

    if number <= 25:
        return "Nghe - Phần 2"

    if number <= 45:
        return "Nghe - Phần 3"

    if number <= 55:
        return "Đọc - Phần 1"

    if number <= 65:
        return "Đọc - Phần 2"

    if number <= 85:
        return "Đọc - Phần 3"

    if number <= 95:
        return "Viết - Phần 1"

    return "Viết - Phần 2"


# =====================================================
# 7. XAC DINH DANG CAU HOI
# =====================================================

def kind_for(number):

    if number <= 10:
        return "dung_sai"

    if number <= 45:
        return "chon_mot"

    if number <= 55:
        return "ghep_lua_chon"

    if number <= 65:
        return "sap_xep_abc"

    if number <= 85:
        return "chon_mot"

    if number <= 95:
        return "sap_xep"

    return "viet_cau_theo_tranh"


# =====================================================
# 8. XAC DINH KY NANG
# =====================================================

def skill_for(number):

    if number <= 45:
        return "nghe"

    if number <= 85:
        return "doc"

    return "viet"


# =====================================================
# 9. CAC LUA CHON
# =====================================================

def choice_labels(number):

    if number <= 10:
        return ["√", "×"]

    if number <= 45:
        return list("ABCD")

    if number <= 55:
        return list("ABCDEF")

    if number <= 65:
        return list("ABC")

    if number <= 85:
        return list("ABCD")

    return []


# =====================================================
# 10. DOC CUM TU SAP XEP 86-95
# =====================================================

def parse_writing_tokens(doc):

    text = doc[14].get_text("text")

    tokens = {}

    for line in text.splitlines():

        match = re.match(
            r"^\s*(8[6-9]|9[0-5])"
            r"\s*[.．、]\s*(.*)$",
            line
        )

        if not match:
            continue

        number = int(
            match.group(1)
        )

        if number in tokens:

            raise RuntimeError(
                f"Trung cau Viet {number}"
            )

        words = [
            word.strip()

            for word in re.split(
                r"\s+",
                match.group(2)
            )

            if word.strip()
        ]

        tokens[number] = words

    if set(tokens) != set(
        range(86, 96)
    ):

        raise RuntimeError(
            "Trang 15 khong tach du "
            "cum tu cau 86-95.\n"
            f"Da tim: {sorted(tokens)}"
        )

    return tokens


# =====================================================
# 11. KIEM TRA JSON DAP AN BUOC 1
# =====================================================

def check_answer_source(source):

    identity = (
        source.get("cap_hsk"),
        source.get("so_de"),
        source.get("ma_de_goc")
    )

    if identity != (4, 1, CODE):

        raise RuntimeError(
            "Sai JSON dap an buoc 1."
        )

    counts = (
        source.get("tong_cau"),
        source.get("so_cau_nghe"),
        source.get("so_cau_doc"),
        source.get("so_cau_viet")
    )

    if counts != (100, 45, 40, 15):

        raise RuntimeError(
            "Sai so cau buoc 1."
        )

    if (
        Path(
            source.get("file_pdf") or ""
        ).resolve()
        != PDF_FILE.resolve()
    ):

        raise RuntimeError(
            "PDF JSON khong khop PDF goc."
        )

    if (
        Path(
            source.get("file_mp3") or ""
        ).resolve()
        != MP3_FILE.resolve()
    ):

        raise RuntimeError(
            "MP3 JSON khong khop MP3 goc."
        )

    answers = source.get(
        "dap_an"
    ) or {}

    expected = {
        str(n)
        for n in range(1, 101)
    }

    if set(answers) != expected:

        raise RuntimeError(
            "Khong du 100 khoa dap an."
        )

    # ================================================
    # 12. KIEM TRA 85 DAP AN NGHE/DOC
    # ================================================

    for number in range(1, 86):

        answer = answers[
            str(number)
        ]

        if 56 <= number <= 65:

            valid = (
                isinstance(answer, str)
                and len(answer) == 3
                and set(answer) == set("ABC")
            )

        else:

            valid = (
                answer in choice_labels(number)
            )

        if not valid:

            raise RuntimeError(
                f"Sai dap an cau {number}: "
                f"{answer}"
            )

    # ================================================
    # 13. KIEM TRA 10 DAP AN SAP XEP VIET
    # ================================================

    for number in range(86, 96):

        answer = answers[
            str(number)
        ]

        if (
            not isinstance(answer, str)
            or not answer.strip()
        ):

            raise RuntimeError(
                f"Thieu dap an Viet {number}"
            )

    # ================================================
    # 14. KIEM TRA 5 CAU VIET MO
    # ================================================

    for number in range(96, 101):

        if answers[str(number)] is not None:

            raise RuntimeError(
                f"Cau Viet mo {number} "
                "khong duoc co "
                "mot dap an duy nhat."
            )

    # ================================================
    # 15. DAP AN THAY THE
    # ================================================

    alternatives = source.get(
        "dap_an_thay_the"
    ) or {}

    if set(alternatives) != {
        "86", "91", "95"
    }:

        raise RuntimeError(
            "Thieu dap an thay the "
            "cau 86, 91 hoac 95."
        )

    for number, values in (
        alternatives.items()
    ):

        if (
            not isinstance(values, list)
            or not values
        ):

            raise RuntimeError(
                f"Dap an thay the cau "
                f"{number} khong hop le."
            )

    # ================================================
    # 16. DAP AN THAM KHAO 96-100
    # ================================================

    references = source.get(
        "dap_an_tham_khao_viet_mo"
    ) or {}

    words = source.get(
        "tu_cho_san_viet_mo"
    ) or {}

    expected_open = {
        str(n)
        for n in range(96, 101)
    }

    if (
        set(references) != expected_open
        or set(words) != expected_open
    ):

        raise RuntimeError(
            "Thieu dap an tham khao "
            "hoac tu cho san 96-100."
        )

    for number in range(96, 101):

        key = str(number)

        if (
            not isinstance(
                references[key],
                list
            )
            or not references[key]
            or not words[key]
        ):

            raise RuntimeError(
                f"Sai du lieu Viet mo "
                f"cau {number}."
            )

    if source.get(
        "cau_can_cham_thu_cong"
    ) != list(range(96, 101)):

        raise RuntimeError(
            "Thieu danh dau cham "
            "thu cong 96-100."
        )

    return (
        answers,
        alternatives,
        references,
        words
    )


# =====================================================
# 17. KIEM TRA MANIFEST BUOC 2
# =====================================================

def check_manifest(manifest):

    identity = (
        manifest.get("cap_hsk"),
        manifest.get("so_de"),
        manifest.get("ma_de_goc"),
        manifest.get("so_cau")
    )

    if identity != (4, 1, CODE, 100):

        raise RuntimeError(
            "Manifest sai ma de/so cau."
        )

    structure = (
        manifest.get("so_trang_pdf"),
        manifest.get("trang_dap_an"),
        manifest.get("trang_loi_thoai")
    )

    if structure != (
        24,
        [23, 24],
        list(range(17, 23))
    ):

        raise RuntimeError(
            "Manifest sai cau truc PDF."
        )

    items = manifest.get(
        "cau_hoi"
    ) or {}

    expected = {
        str(n)
        for n in range(1, 101)
    }

    if set(items) != expected:

        raise RuntimeError(
            "Manifest khong du 100 cau."
        )

    group_data = manifest.get(
        "bang_lua_chon"
    ) or {}

    if set(group_data) != set(GROUPS):

        raise RuntimeError(
            "Manifest khong du 2 bang Doc."
        )

    copies = []

    # ================================================
    # 18. KIEM TRA 100 ANH CAU HOI
    # ================================================

    for number in range(1, 101):

        item = items[
            str(number)
        ]

        relative = (
            "questions/"
            f"cau_{number:03d}.png"
        )

        if (
            item.get("trang_pdf")
            != page_for(number)
            or item.get("anh") != relative
        ):

            raise RuntimeError(
                f"Manifest sai anh/trang "
                f"cau {number}."
            )

        if 46 <= number <= 50:

            expected_group = "doc_46_50"

        elif 51 <= number <= 55:

            expected_group = "doc_51_55"

        else:

            expected_group = None

        if (
            item.get("nhom_lua_chon")
            != expected_group
        ):

            raise RuntimeError(
                f"Manifest sai nhom "
                f"cau {number}."
            )

        # Cac cau Doc dung chung doan van.
        if 80 <= number <= 85:

            if number <= 81:
                shared = "80-81"

            elif number <= 83:
                shared = "82-83"

            else:
                shared = "84-85"

            if (
                item.get("nhom_doc_chung")
                != shared
            ):

                raise RuntimeError(
                    f"Cau {number} thieu "
                    f"nhom Doc chung {shared}."
                )

        copies.append((
            OUTPUT / relative,
            MEDIA / relative
        ))

    # ================================================
    # 19. KIEM TRA HAI BANG DOC
    # ================================================

    for name, (
        page,
        first,
        last,
        labels
    ) in GROUPS.items():

        item = group_data[name]

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

    if len(copies) != 102:

        raise RuntimeError(
            "Thieu 100 anh va 2 bang."
        )

    return items, copies


# =====================================================
# 20. KIEM TRA MEDIA TRUOC KHI COPY
# =====================================================

def check_files(copies):

    for source_file, destination in copies:

        require_file(source_file)

        if source_file.suffix.lower() == ".png":

            signature = (
                b"\x89PNG\r\n\x1a\n"
            )

            if not source_file.read_bytes().startswith(
                signature
            ):

                raise RuntimeError(
                    f"PNG khong hop le: "
                    f"{source_file}"
                )

        if destination.exists():

            if not filecmp.cmp(
                source_file,
                destination,
                shallow=False
            ):

                raise RuntimeError(
                    "Media da ton tai voi "
                    "noi dung khac:\n"
                    + str(destination)
                )


# =====================================================
# 21. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)

    print(
        "MOC HAN - HSK4 DE 01 - BUOC 3"
    )

    print("CHUAN HOA H41001")

    print("=" * 60)

    source = read_json(
        ANSWER_FILE
    )

    manifest = read_json(
        MANIFEST_FILE
    )

    require_file(PDF_FILE)
    require_file(MP3_FILE)

    (
        answers,
        alternatives,
        references,
        words
    ) = check_answer_source(source)

    items, copies = check_manifest(
        manifest
    )

    # ================================================
    # 22. KIEM TRA PDF VA CUM TU VIET
    # ================================================

    with fitz.open(PDF_FILE) as doc:

        if (
            len(doc) != 24
            or CODE not in doc[0].get_text("text")
            or CODE not in doc[22].get_text("text")
        ):

            raise RuntimeError(
                "PDF khong phai H41001 "
                "24 trang."
            )

        tokens = parse_writing_tokens(
            doc
        )

    # ================================================
    # 23. KIEM TRA SAP XEP CAU 86-95
    # ================================================

    for number in range(86, 96):

        values = tokens[number]

        if not 3 <= len(values) <= 9:

            raise RuntimeError(
                f"Cau {number} sai "
                f"so cum tu: {values}"
            )

        valid_answers = [
            answers[str(number)]
        ] + alternatives.get(
            str(number),
            []
        )

        for answer in valid_answers:

            valid = any(
                compact("".join(order))
                == compact(answer)

                for order in permutations(
                    values
                )
            )

            if not valid:

                raise RuntimeError(
                    f"Cau {number} khong "
                    "ghep duoc dap an.\n"
                    f"Dap an: {answer}\n"
                    f"Cum tu: {values}"
                )

    print("\n===== KIEM TRA DAP AN =====")

    print("Nghe: 45/45")
    print("Doc: 40/40")

    print("Viet sap xep: 10/10")

    print(
        "Dap an thay the: 86, 91, 95"
    )

    print(
        "Viet mo: 5/5 dap an tham khao"
    )

    # ================================================
    # 24. DOC THOI LUONG MP3
    # ================================================

    try:

        duration = round(
            float(
                MP3(str(MP3_FILE)).info.length
            ),
            2
        )

    except Exception as exc:

        raise RuntimeError(
            f"Khong doc duoc MP3: {exc}"
        ) from exc

    if not 0 < duration < 10000:

        raise RuntimeError(
            "Thoi luong MP3 khong hop le."
        )

    copies.append((
        MP3_FILE,
        MEDIA_ROOT / f"{CODE}.mp3"
    ))

    check_files(copies)

    # ================================================
    # 25. TAO 100 CAU HOI
    # ================================================

    questions = []

    for number in range(1, 101):

        item = items[
            str(number)
        ]

        labels = choice_labels(number)

        alternative_answers = (
            alternatives.get(
                str(number),
                []
            )
        )

        reference = references.get(
            str(number)
        )

        # ============================================
        # 26. LOAI DAP AN THEO DANG CAU
        # ============================================

        if 86 <= number <= 95:

            labels = tokens[number]

            if alternative_answers:

                answer = [
                    answers[str(number)]
                ] + alternative_answers

            else:

                answer = answers[
                    str(number)
                ]

        elif number >= 96:

            # Cau Viet mo khong co dap an duy nhat.
            # Luu cau truc de xu ly cham rieng.
            answer = {
                "che_do": "cham_thu_cong",
                "tu_cho_san": words[str(number)],
                "dap_an_tham_khao": reference
            }

        else:

            answer = answers[
                str(number)
            ]

        # ============================================
        # 27. LUA CHON JSON
        # ============================================

        if 86 <= number <= 95:

            options = [
                {
                    "ma": str(index + 1),
                    "nhan": value
                }

                for index, value
                in enumerate(labels)
            ]

        else:

            options = [
                {
                    "ma": value,
                    "nhan": value
                }

                for value in labels
            ]

        group = item.get(
            "nhom_lua_chon"
        )

        # ============================================
        # 28. THONG TIN CAU HOI
        # ============================================

        question = {
            "so_cau": number,

            "ky_nang": skill_for(number),

            "phan": part_for(number),

            "loai_cau_hoi": kind_for(number),

            "noi_dung": (
                "Nhìn tranh và đặt câu "
                "với từ: " + words[str(number)]
                if number >= 96
                else None
            ),

            "trang_pdf": item["trang_pdf"],

            "anh_cau_hoi": (
                "/static/media/luyen_thi/"
                "hsk4/de_01/"
                + item["anh"]
            ),

            "anh_nhom_lua_chon": (
                "/static/media/luyen_thi/"
                "hsk4/de_01/groups/"
                f"{group}.png"
                if group
                else None
            ),

            "lua_chon_json": options,

            "dap_an_dung": answer,

            "dap_an_thay_the": (
                alternative_answers
            ),

            "nhom_doc_chung": item.get(
                "nhom_doc_chung"
            ),

            "cham_thu_cong": (
                number >= 96
            ),

            "da_duyet": False
        }

        if number >= 96:

            question["dap_an_tham_khao"] = (
                reference
            )

            question["tu_cho_san"] = (
                words[str(number)]
            )

        questions.append(
            question
        )

    # ================================================
    # 29. TAO JSON HOAN CHINH
    # ================================================

    result = {
        "ma_de_goc": CODE,

        "cap_hsk": 4,

        "so_de": 1,
        "thu_tu": 1,

        "ten_hien_thi": "Đề 1",

        "so_cau": 100,

        "so_cau_nghe": 45,
        "so_cau_doc": 40,
        "so_cau_viet": 15,

        "thoi_gian_phut": 100,
        "thoi_gian_pdf_phut": 105,

        "so_trang_pdf_de": 24,

        "trang_cau_hoi": list(
            range(2, 17)
        ),

        "trang_loi_thoai": list(
            range(17, 23)
        ),

        "trang_dap_an": [23, 24],

        "nguon_dap_an": "pdf_chung",

        "file_pdf": str(PDF_FILE),
        "file_mp3": str(MP3_FILE),

        "audio": {
            "duong_dan": (
                "/static/media/luyen_thi/"
                f"hsk4/{CODE}.mp3"
            ),

            "thoi_luong_giay": duration
        },

        "dap_an_thay_the": alternatives,

        "dap_an_tham_khao_viet_mo": (
            references
        ),

        "cau_can_cham_thu_cong": (
            list(range(96, 101))
        ),

        # Phai kiem tra backend cham diem
        # truoc khi nhap SQL.
        "san_sang_nhap_sql": False,

        "ly_do_chua_nhap": (
            "Can ho tro sap_xep_abc, "
            "dap an thay the va cham thu cong "
            "Viet theo tranh."
        ),

        "cau_hoi": questions
    }

    # ================================================
    # 30. KIEM TRA FILE JSON DA TON TAI
    # ================================================

    content = json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ).encode("utf-8")

    if FINAL_FILE.exists():

        if (
            FINAL_FILE.read_bytes()
            != content
        ):

            raise RuntimeError(
                "JSON De 1 da ton tai "
                "voi noi dung khac.\n"
                "KHONG ghi de:\n"
                + str(FINAL_FILE)
            )

    # ================================================
    # 31. SAO CHEP MEDIA
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

        if not filecmp.cmp(
            source_file,
            destination,
            shallow=False
        ):

            raise RuntimeError(
                "Sao chep media bi loi:\n"
                + str(destination)
            )

    # ================================================
    # 32. LUU JSON
    # ================================================

    if not FINAL_FILE.exists():

        FINAL_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        FINAL_FILE.write_bytes(
            content
        )

    # ================================================
    # 33. HOAN THANH
    # ================================================

    print("\n" + "=" * 60)

    print(
        "HOAN THANH CHUAN HOA HSK4 DE 01"
    )

    print("=" * 60)

    print("Ma de goc: H41001")
    print("Ten hien thi: De 1")

    print("Tong cau: 100")

    print("Nghe: 45")
    print("Doc: 40")
    print("Viet: 15")

    print("Dap an Nghe/Doc: 85/85")

    print("Viet sap xep: 10/10")

    print("Viet mo: 5 cau cham rieng")

    print("Dap an thay the: 86, 91, 95")

    print("Anh cau hoi: 100/100")
    print("Bang lua chon: 2/2")

    print(f"MP3: {duration} giay")

    print(
        "Thoi gian du kien: 100 phut"
    )

    print(f"\nJSON: {FINAL_FILE}")

    print("\nCHUA thay doi SQL Server.")

    print(
        "CHUA nhap SQL truoc khi "
        "kiem tra va nang cap cham diem."
    )


if __name__ == "__main__":
    main()
