from pathlib import Path
import sys
import tarfile
import csv
import re
from collections import defaultdict


# =========================================================
# THU MUC GOC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# =========================================================
# THU MUC TATOEBA
# =========================================================
TATOEBA_DIR = (
    ROOT_DIR
    / "data_sources"
    / "tatoeba"
)


# =========================================================
# FILE OUTPUT
# =========================================================
OUTPUT_FILE = (
    TATOEBA_DIR
    / "lesson1_vocab_tatoeba_candidates.csv"
)


# =========================================================
# 13 TU CUA HSK1 - BAI 1
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
# MOI TU GIU TOI DA 10 CAU DE REVIEW
# =========================================================
MAX_PER_WORD = 10


# =========================================================
# GIOI HAN DO DAI
#
# Bai HSK1 nen uu tien cau ngan.
# =========================================================
MAX_TEXT_LENGTH = 30


# =========================================================
# TIM ARCHIVE SENTENCES
# =========================================================
def find_sentences_archive():

    if not TATOEBA_DIR.exists():
        raise FileNotFoundError(
            "Khong tim thay thu muc:\n"
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
            candidates.append(path)

    if len(candidates) == 0:
        raise RuntimeError(
            "Khong tim thay archive sentences cua Tatoeba."
        )

    if len(candidates) > 1:

        print(
            "Tim thay nhieu archive co the la sentences:"
        )

        for item in candidates:
            print("-", item)

        raise RuntimeError(
            "Co nhieu file sentences, "
            "can chon dung file truoc."
        )

    return candidates[0]


# =========================================================
# CHON FILE DU LIEU BEN TRONG TAR
#
# Thuong archive co 1 file chinh.
# =========================================================
def find_data_member(archive):

    members = [
        member
        for member in archive.getmembers()
        if member.isfile()
    ]

    if not members:
        raise RuntimeError(
            "Archive Tatoeba khong co file du lieu."
        )

    # Uu tien file lon nhat
    members.sort(
        key=lambda x: x.size,
        reverse=True,
    )

    return members[0]


# =========================================================
# CHUAN HOA CAU
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
# LOC CAU PHU HOP DE REVIEW
#
# Chi la loc ky thuat, CHUA coi la da chon.
# =========================================================
def is_candidate(text):

    if not text:
        return False

    if len(text) > MAX_TEXT_LENGTH:
        return False

    # Loai cau co xuong dong/ky tu control
    if any(
        ord(char) < 32
        for char in text
    ):
        return False

    return True


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 78)
    print(
        "TIM CAU TATOEBA CHO TU VUNG HSK1 - BAI 1"
    )
    print("=" * 78)

    archive_path = (
        find_sentences_archive()
    )

    print()
    print("Archive:")
    print(archive_path)

    results = defaultdict(list)

    chinese_count = 0
    total_lines = 0

    with tarfile.open(
        archive_path,
        "r:*",
    ) as archive:

        member = find_data_member(
            archive
        )

        print()
        print(
            "File ben trong archive:"
        )
        print(member.name)

        raw_file = archive.extractfile(
            member
        )

        if raw_file is None:
            raise RuntimeError(
                "Khong doc duoc file trong archive."
            )

        for raw_line in raw_file:

            total_lines += 1

            try:
                line = raw_line.decode(
                    "utf-8"
                ).rstrip("\r\n")

            except UnicodeDecodeError:
                continue

            # Tatoeba sentences:
            # sentence_id<TAB>language<TAB>text
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

            text = clean_text(
                parts[2]
            )

            # Mandarin Chinese
            if language != "cmn":
                continue

            chinese_count += 1

            if not is_candidate(
                text
            ):
                continue

            for word in TARGET_WORDS:

                if (
                    len(results[word])
                    >= MAX_PER_WORD
                ):
                    continue

                if word not in text:
                    continue

                # Tranh trung dung mot sentence
                # cho cung mot word.
                if any(
                    row["SentenceId"]
                    == sentence_id
                    for row in results[word]
                ):
                    continue

                results[word].append(
                    {
                        "TuVung": word,
                        "SentenceId": sentence_id,
                        "CauTiengTrung": text,
                        "DoDai": len(text),
                    }
                )

            # Neu da du 10 cau cho tat ca tu
            # thi dung som.
            if all(
                len(results[word])
                >= MAX_PER_WORD
                for word in TARGET_WORDS
            ):
                break

    # =====================================================
    # SORT:
    # cau ngan hon len truoc
    # =====================================================
    for word in TARGET_WORDS:

        results[word].sort(
            key=lambda row: (
                row["DoDai"],
                int(row["SentenceId"]),
            )
        )

        results[word] = (
            results[word][
                :MAX_PER_WORD
            ]
        )

    # =====================================================
    # GHI CSV
    # =====================================================
    rows = []

    for word in TARGET_WORDS:

        for index, row in enumerate(
            results[word],
            start=1,
        ):

            rows.append(
                {
                    "TuVung":
                        word,

                    "ThuTuDeXuat":
                        index,

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

                    # De trong.
                    # Buoc sau moi kiem tra va dich.
                    "BanDichTiengViet":
                        "",

                    "DaChon":
                        0,
                }
            )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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
                "ThuTuDeXuat",
                "SentenceId",
                "CauTiengTrung",
                "DoDai",
                "BanDichTiengViet",
                "DaChon",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    # =====================================================
    # KET QUA
    # =====================================================
    print()
    print("=" * 78)
    print("KET QUA")
    print("=" * 78)

    print(
        "Tong dong da doc:",
        total_lines,
    )

    print(
        "Tong cau cmn da gap:",
        chinese_count,
    )

    print()

    missing = []

    for word in TARGET_WORDS:

        count = len(
            results[word]
        )

        print(
            f"{word:<4}"
            f" : {count} cau"
        )

        if count == 0:
            missing.append(word)

    print()
    print(
        "Tong candidate:",
        len(rows),
    )

    print()
    print(
        "File review:"
    )

    print(
        OUTPUT_FILE
    )

    if missing:

        print()
        print(
            "CAC TU CHUA TIM DUOC CAU:"
        )

        for word in missing:
            print(
                "-",
                word,
            )

    else:

        print()
        print(
            "13/13 TU DEU CO CAU TATOEBA DE REVIEW."
        )

    print()
    print(
        "CHUA UPDATE dbo.TuVung."
    )

    print(
        "CHUA TU DONG CHON CAU."
    )

    print(
        "CHUA TU DONG TAO BAN DICH VIET."
    )

    print()
    print("=" * 78)
    print("HOAN TAT")
    print("=" * 78)


if __name__ == "__main__":
    main()