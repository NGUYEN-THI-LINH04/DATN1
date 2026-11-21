from pathlib import Path
import sys
import tarfile
import csv
import re
import zipfile
from collections import defaultdict


# =========================================================
# THU MUC GOC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# DUONG DAN
# =========================================================
TATOEBA_DIR = (
    ROOT_DIR
    / "data_sources"
    / "tatoeba"
)

UNICODE_DIR = (
    ROOT_DIR
    / "data_sources"
    / "unicode"
)

UNIHAN_ZIP = (
    UNICODE_DIR
    / "Unihan.zip"
)

OUTPUT_FILE = (
    TATOEBA_DIR
    / "lesson1_vocab_tatoeba_candidates_ranked.csv"
)


# =========================================================
# TU VUNG BAI 1
# =========================================================
TARGET_WORDS = [
    "你",
    "好",
    "我",
    "是",
    "叫",
    "什么",
    "名字",
    "很",
    "高兴",
    "认识",
    "吗",
    "呢",
    "也",
]


# =========================================================
# MOI TU GIU 10 CAU TOT NHAT
# =========================================================
TOP_N = 10


# =========================================================
# GIOI HAN DO DAI
# =========================================================
MAX_LENGTH = 30


# =========================================================
# HAM KIEM TRA CHU HAN
# =========================================================
def is_hanzi(char):

    code = ord(char)

    return (
        0x3400 <= code <= 0x4DBF
        or
        0x4E00 <= code <= 0x9FFF
    )


# =========================================================
# TIM FILE TATOEBA
# =========================================================
def find_sentences_archive():

    if not TATOEBA_DIR.exists():

        raise FileNotFoundError(
            "Khong tim thay:\n"
            f"{TATOEBA_DIR}"
        )

    candidates = []

    for path in TATOEBA_DIR.iterdir():

        name = path.name.lower()

        if (
            path.is_file()
            and "sentence" in name
            and "audio" not in name
            and (
                name.endswith(".tar.bz2")
                or name.endswith(".tar.gz")
                or name.endswith(".tgz")
                or name.endswith(".tar")
            )
        ):

            candidates.append(
                path
            )

    if len(candidates) != 1:

        print(
            "Cac archive tim thay:"
        )

        for path in candidates:
            print("-", path)

        raise RuntimeError(
            "Can co dung 1 archive sentences."
        )

    return candidates[0]


# =========================================================
# TIM DATA FILE TRONG TAR
# =========================================================
def find_data_member(archive):

    members = [
        member
        for member in archive.getmembers()
        if member.isfile()
    ]

    if not members:

        raise RuntimeError(
            "Archive khong co file du lieu."
        )

    members.sort(
        key=lambda item: item.size,
        reverse=True,
    )

    return members[0]


# =========================================================
# DOC KY TU PHON THE TU UNIHAN
#
# Neu mot character co kSimplifiedVariant,
# character do la traditional/variant co dang gian the.
#
# Dung de LOAI cac cau phon the.
# =========================================================
def load_traditional_chars():

    if not UNIHAN_ZIP.exists():

        raise FileNotFoundError(
            "Khong tim thay:\n"
            f"{UNIHAN_ZIP}"
        )

    result = set()

    self_mapping_count = 0

    with zipfile.ZipFile(
        UNIHAN_ZIP,
        "r",
    ) as archive:

        files = [
            name
            for name in archive.namelist()
            if (
                name.startswith("Unihan")
                and name.endswith(".txt")
            )
        ]

        for filename in files:

            with archive.open(
                filename,
                "r",
            ) as file:

                for raw_line in file:

                    try:

                        line = (
                            raw_line
                            .decode("utf-8")
                            .strip()
                        )

                    except UnicodeDecodeError:
                        continue

                    if (
                        not line
                        or line.startswith("#")
                    ):
                        continue

                    parts = line.split(
                        "\t",
                        2,
                    )

                    if len(parts) != 3:
                        continue

                    codepoint = parts[0]
                    property_name = parts[1]
                    property_value = parts[2]

                    if (
                        property_name
                        != "kSimplifiedVariant"
                    ):
                        continue

                    if not codepoint.startswith(
                        "U+"
                    ):
                        continue

                    try:

                        source_codepoint = int(
                            codepoint[2:],
                            16,
                        )

                        source_char = chr(
                            source_codepoint
                        )

                    except ValueError:
                        continue

                    # =====================================
                    # Doc cac U+XXXX trong
                    # kSimplifiedVariant
                    # =====================================
                    target_codepoints = []

                    for match in re.findall(
                        r"U\+([0-9A-Fa-f]+)",
                        property_value,
                    ):

                        try:

                            target_codepoints.append(
                                int(
                                    match,
                                    16,
                                )
                            )

                        except ValueError:
                            continue

                    if not target_codepoints:
                        continue

                    # =====================================
                    # QUAN TRONG:
                    #
                    # Neu kSimplifiedVariant chi tro ve
                    # CHINH KY TU DO thi KHONG coi no la
                    # chu phon the.
                    #
                    # Vi du:
                    #
                    # 么
                    # kSimplifiedVariant = U+4E48
                    #
                    # U+4E48 chinh la 么.
                    # =====================================
                    different_targets = [
                        cp
                        for cp in target_codepoints
                        if cp != source_codepoint
                    ]

                    if not different_targets:

                        self_mapping_count += 1
                        continue

                    # Co mot dang gian the KHAC voi
                    # ky tu hien tai -> moi coi ky tu
                    # hien tai la traditional/variant
                    # can loai khoi corpus gian the.
                    result.add(
                        source_char
                    )

    print(
        "So self-mapping kSimplifiedVariant bo qua:",
        self_mapping_count,
    )

    return result


# =========================================================
# LAY TAP KY TU HSK1 TU SQL
#
# Chi dung de XEP HANG cau:
# cau co it chu ngoai HSK1 se duoc uu tien.
# =========================================================
def load_hsk1_chars(cursor):

    cursor.execute(
        """
        SELECT
            ChuHan,
            BienThe
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = 1
        """
    )

    chars = set()

    for row in cursor.fetchall():

        for value in (
            row.ChuHan,
            row.BienThe,
        ):

            if not value:
                continue

            for char in value:

                if is_hanzi(char):

                    chars.add(
                        char
                    )

    if not chars:

        raise RuntimeError(
            "Khong lay duoc ky tu HSK1."
        )

    return chars


# =========================================================
# CHUAN HOA TEXT
# =========================================================
def clean_text(text):

    text = text.strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


# =========================================================
# KIEM TRA CAU CO PHON THE KHONG
# =========================================================
def contains_traditional(
    text,
    traditional_chars,
):

    return any(
        char in traditional_chars
        for char in text
    )


# =========================================================
# DEM CHU NGOAI HSK1
# =========================================================
def count_non_hsk1_hanzi(
    text,
    hsk1_chars,
):

    return sum(
        1
        for char in text
        if (
            is_hanzi(char)
            and char not in hsk1_chars
        )
    )


# =========================================================
# SCORE RIENG THEO TUNG TU
#
# SCORE CANG THAP CANG TOT.
# =========================================================
def target_bonus(
    word,
    text,
):

    bonus = 0

    # -----------------------------------------------------
    # 你
    # -----------------------------------------------------
    if word == "你":

        if text.startswith("你"):
            bonus -= 4

        if "你好" in text:
            bonus -= 8

    # -----------------------------------------------------
    # 好
    #
    # Uu tien nghia "tot/khoe".
    # Tranh 好 = rat / may / tot nhat...
    # -----------------------------------------------------
    elif word == "好":

        if "你好" in text:
            bonus -= 12

        if "很好" in text:
            bonus -= 10

        if "真好" in text:
            bonus -= 8

        bad_patterns = [
            "好胖",
            "好几",
            "最好",
            "好像",
            "好好",
        ]

        if any(
            pattern in text
            for pattern in bad_patterns
        ):
            bonus += 25

    # -----------------------------------------------------
    # 我
    # -----------------------------------------------------
    elif word == "我":

        if text.startswith("我"):
            bonus -= 4

    # -----------------------------------------------------
    # 是
    # -----------------------------------------------------
    elif word == "是":

        preferred = [
            "我是",
            "你是",
            "他是",
            "她是",
            "这是",
            "那是",
        ]

        if any(
            pattern in text
            for pattern in preferred
        ):
            bonus -= 8

    # -----------------------------------------------------
    # 叫
    #
    # Uu tien cach dung "ten la".
    # -----------------------------------------------------
    elif word == "叫":

        if re.search(
            r"[我你他她]叫",
            text,
        ):
            bonus -= 15

        if "叫做" in text:
            bonus += 8

        if "叫醒" in text:
            bonus += 15

    # -----------------------------------------------------
    # 什么
    #
    # Tranh cac cum ma 什么 khong con nghia
    # "gi/cai gi" doc lap.
    # -----------------------------------------------------
    elif word == "什么":

        bad_patterns = [
            "什么时候",
            "为什么",
            "没什么",
            "什么都",
            "什么也",
        ]

        if any(
            pattern in text
            for pattern in bad_patterns
        ):
            bonus += 30

        if text.endswith(
            "什么？"
        ):

            bonus -= 10

        if text.endswith(
            "什么?"
        ):

            bonus -= 10

    # -----------------------------------------------------
    # 名字
    # -----------------------------------------------------
    elif word == "名字":

        if "你的名字" in text:
            bonus -= 8

        if "叫什么名字" in text:
            bonus -= 15

    # -----------------------------------------------------
    # 很
    # -----------------------------------------------------
    elif word == "很":

        if "很好" in text:
            bonus -= 12

        if "很高兴" in text:
            bonus -= 12

    # -----------------------------------------------------
    # 高兴
    # -----------------------------------------------------
    elif word == "高兴":

        if "很高兴" in text:
            bonus -= 10

        if "我很高兴" in text:
            bonus -= 8

    # -----------------------------------------------------
    # 认识
    # -----------------------------------------------------
    elif word == "认识":

        if re.search(
            r"[我你他她]认识",
            text,
        ):
            bonus -= 6

    # -----------------------------------------------------
    # 吗
    # -----------------------------------------------------
    elif word == "吗":

        if (
            text.endswith("吗？")
            or text.endswith("吗?")
        ):
            bonus -= 12

    # -----------------------------------------------------
    # 呢
    #
    # Bai 1 dang day:
    # "con ... thi sao?"
    #
    # Uu tien rat manh:
    # 你呢？ / 我呢？ / 他呢？ / 她呢？
    # -----------------------------------------------------
    elif word == "呢":

        preferred = [
            "你呢",
            "我呢",
            "他呢",
            "她呢",
        ]

        if any(
            pattern in text
            for pattern in preferred
        ):
            bonus -= 30

        if (
            text.endswith("呢？")
            or text.endswith("呢?")
        ):
            bonus -= 6

    # -----------------------------------------------------
    # 也
    # -----------------------------------------------------
    elif word == "也":

        if re.search(
            r"[我你他她]也",
            text,
        ):
            bonus -= 10

    return bonus


# =========================================================
# TINH DIEM TOAN CAU
# =========================================================
def score_sentence(
    word,
    text,
    hsk1_chars,
):

    non_hsk = (
        count_non_hsk1_hanzi(
            text,
            hsk1_chars,
        )
    )

    score = 0

    # Cau ngan duoc uu tien
    score += len(text)

    # Moi chu ngoai HSK1 bi phat manh
    score += (
        non_hsk * 7
    )

    # Dieu chinh theo nghia/cau truc cua tung tu
    score += target_bonus(
        word,
        text,
    )

    return score, non_hsk


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 80)
        print(
            "QUET LAI TOAN BO TATOEBA "
            "CHO HSK1 - BAI 1"
        )
        print("=" * 80)

        archive_path = (
            find_sentences_archive()
        )

        print()
        print("Archive:")
        print(archive_path)

        print()
        print(
            "Dang doc danh sach "
            "ky tu phon the tu Unihan..."
        )

        traditional_chars = (
            load_traditional_chars()
        )

        print(
            "So ky tu co "
            "kSimplifiedVariant:",
            len(traditional_chars),
        )

        # -------------------------------------------------
        # HSK1 chars
        # -------------------------------------------------
        conn = get_connection()
        cursor = conn.cursor()

        hsk1_chars = (
            load_hsk1_chars(
                cursor
            )
        )

        print(
            "So ky tu Han trong kho HSK1:",
            len(hsk1_chars),
        )

        # -------------------------------------------------
        # Quet toan bo Tatoeba
        # -------------------------------------------------
        candidates = defaultdict(
            list
        )

        total_lines = 0
        cmn_count = 0
        simplified_count = 0

        with tarfile.open(
            archive_path,
            "r:*",
        ) as archive:

            member = find_data_member(
                archive
            )

            print()
            print(
                "File ben trong:"
            )
            print(member.name)

            raw_file = (
                archive.extractfile(
                    member
                )
            )

            if raw_file is None:

                raise RuntimeError(
                    "Khong doc duoc file."
                )

            for raw_line in raw_file:

                total_lines += 1

                try:

                    line = (
                        raw_line
                        .decode("utf-8")
                        .rstrip("\r\n")
                    )

                except UnicodeDecodeError:
                    continue

                parts = line.split(
                    "\t",
                    2,
                )

                if len(parts) != 3:
                    continue

                sentence_id = (
                    parts[0].strip()
                )

                language = (
                    parts[1].strip()
                )

                if language != "cmn":
                    continue

                cmn_count += 1

                text = clean_text(
                    parts[2]
                )

                if not text:
                    continue

                if len(text) > MAX_LENGTH:
                    continue

                # -----------------------------------------
                # Chi dung cau gian the
                # -----------------------------------------
                if contains_traditional(
                    text,
                    traditional_chars,
                ):
                    continue

                simplified_count += 1

                # -----------------------------------------
                # Tim tu muc tieu
                # -----------------------------------------
                for word in TARGET_WORDS:

                    if word not in text:
                        continue

                    score, non_hsk = (
                        score_sentence(
                            word,
                            text,
                            hsk1_chars,
                        )
                    )

                    candidates[
                        word
                    ].append(
                        {
                            "TuVung":
                                word,

                            "SentenceId":
                                sentence_id,

                            "CauTiengTrung":
                                text,

                            "DoDai":
                                len(text),

                            "SoChuNgoaiHSK1":
                                non_hsk,

                            "DiemXepHang":
                                score,
                        }
                    )

        # -------------------------------------------------
        # XEP HANG
        # -------------------------------------------------
        output_rows = []

        for word in TARGET_WORDS:

            unique = {}

            for row in candidates[word]:

                key = (
                    row[
                        "CauTiengTrung"
                    ]
                )

                current = (
                    unique.get(key)
                )

                if (
                    current is None
                    or row[
                        "DiemXepHang"
                    ]
                    < current[
                        "DiemXepHang"
                    ]
                ):

                    unique[key] = row

            ranked = sorted(
                unique.values(),
                key=lambda row: (
                    row[
                        "DiemXepHang"
                    ],
                    row[
                        "SoChuNgoaiHSK1"
                    ],
                    row[
                        "DoDai"
                    ],
                    int(
                        row[
                            "SentenceId"
                        ]
                    ),
                ),
            )

            ranked = ranked[
                :TOP_N
            ]

            candidates[word] = (
                ranked
            )

            for rank, row in enumerate(
                ranked,
                start=1,
            ):

                output_rows.append(
                    {
                        "TuVung":
                            word,

                        "XepHang":
                            rank,

                        "SentenceId":
                            row[
                                "SentenceId"
                            ],

                        "CauTiengTrung":
                            row[
                                "CauTiengTrung"
                            ],

                        "DoDai":
                            row[
                                "DoDai"
                            ],

                        "SoChuNgoaiHSK1":
                            row[
                                "SoChuNgoaiHSK1"
                            ],

                        "DiemXepHang":
                            row[
                                "DiemXepHang"
                            ],

                        "BanDichTiengViet":
                            "",

                        "DaChon":
                            0,
                    }
                )

        # -------------------------------------------------
        # GHI CSV
        # -------------------------------------------------
        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "TuVung",
                    "XepHang",
                    "SentenceId",
                    "CauTiengTrung",
                    "DoDai",
                    "SoChuNgoaiHSK1",
                    "DiemXepHang",
                    "BanDichTiengViet",
                    "DaChon",
                ],
            )

            writer.writeheader()
            writer.writerows(
                output_rows
            )

        # -------------------------------------------------
        # KET QUA
        # -------------------------------------------------
        print()
        print("=" * 80)
        print("KET QUA")
        print("=" * 80)

        print(
            "Tong dong archive:",
            total_lines,
        )

        print(
            "Tong cau cmn:",
            cmn_count,
        )

        print(
            "Cau ngan + gian the da xet:",
            simplified_count,
        )

        print()
        print(
            "TOP 3 MOI TU"
        )
        print("-" * 80)

        missing = []

        for word in TARGET_WORDS:

            ranked = (
                candidates[word]
            )

            print()
            print(
                f"[{word}]"
            )

            if not ranked:

                print(
                    "  KHONG TIM THAY"
                )

                missing.append(
                    word
                )

                continue

            for rank, row in enumerate(
                ranked[:3],
                start=1,
            ):

                print(
                    f"  {rank}. "
                    f"ID={row['SentenceId']}"
                    f" | ngoaiHSK1="
                    f"{row['SoChuNgoaiHSK1']}"
                    f" | score="
                    f"{row['DiemXepHang']}"
                )

                print(
                    "     "
                    + row[
                        "CauTiengTrung"
                    ]
                )

        print()
        print("-" * 80)

        print(
            "Tong dong file review:",
            len(output_rows),
        )

        print()
        print(
            "File:"
        )

        print(
            OUTPUT_FILE
        )

        if missing:

            print()
            print(
                "CAC TU CHUA CO CAU:"
            )

            for word in missing:
                print(
                    "-",
                    word,
                )

        else:

            print()
            print(
                "13/13 TU CO UNG VIEN."
            )

        print()
        print(
            "CHUA UPDATE dbo.TuVung."
        )

        print(
            "CHUA TU DONG CHON CAU."
        )

        print()
        print("=" * 80)
        print("HOAN TAT")
        print("=" * 80)

        cursor.close()

    except Exception as e:

        print()
        print("=" * 80)
        print("THUC HIEN THAT BAI")
        print("=" * 80)

        print(
            "Loi:",
            e,
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()