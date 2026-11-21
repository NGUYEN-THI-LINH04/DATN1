from pathlib import Path
import csv
import sys
from collections import defaultdict
from contextlib import closing


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# CONFIG
# =========================================================
COURSE_CODE = "HSK1-CORE"

EXPECTED_LESSONS = 23
EXPECTED_VOCAB_LINKS = 501

# Ket qua ChuHan hien tai ma ta vua kiem tra trong SQL
EXPECTED_CURRENT_HANZI = 17
EXPECTED_CURRENT_HANZI_LESSON1 = 17


# =========================================================
# OUTPUT
# =========================================================
OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "hanzi"
    / "review"
)

CANDIDATE_FILE = (
    OUTPUT_DIR
    / "hsk1_hanzi_candidate_review.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR
    / "hsk1_hanzi_candidate_summary.csv"
)


# =========================================================
# HELPERS
# =========================================================
def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def fail(message):
    raise RuntimeError(message)


def is_hanzi(char):
    """
    Kiem tra ky tu CJK/Han.

    HSK1 chu yeu nam trong CJK Unified Ideographs,
    nhung giu them cac khoang pho bien de script an toan hon.
    """
    if not char:
        return False

    code = ord(char)

    ranges = [
        (0x3400, 0x4DBF),       # CJK Extension A
        (0x4E00, 0x9FFF),       # CJK Unified Ideographs
        (0xF900, 0xFAFF),       # CJK Compatibility Ideographs
        (0x20000, 0x2A6DF),     # Extension B
        (0x2A700, 0x2B73F),     # Extension C
        (0x2B740, 0x2B81F),     # Extension D
        (0x2B820, 0x2CEAF),     # Extension E/F
        (0x30000, 0x3134F),     # Extension G
    ]

    return any(
        start <= code <= end
        for start, end in ranges
    )


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "10B - PHAN TICH CHU HAN HSK1 "
        "TU 501 TU VUNG"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  DOC 501 TU VUNG HSK1")
    print("  TACH TUNG KY TU HAN")
    print("  LOAI TRUNG")
    print("  XAC DINH BAI XUAT HIEN DAU")
    print("  DOI CHIEU 17 CHU HAN HIEN CO")
    print("  TAO FILE REVIEW")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # CONNECT
    # =====================================================
    print()
    print("[1] KET NOI DATABASE")
    print("-" * 120)

    with closing(
        get_connection()
    ) as connection:

        try:

            with closing(
                connection.cursor()
            ) as cursor:

                cursor.execute(
                    """
                    SELECT
                        DB_NAME(),
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        ),
                        SUSER_SNAME();
                    """
                )

                database_name, server_name, login_name = (
                    cursor.fetchone()
                )

                print(
                    "Server:",
                    clean(server_name),
                )

                print(
                    "Database:",
                    clean(database_name),
                )

                print(
                    "Tai khoan:",
                    clean(login_name),
                )

                if (
                    clean(database_name).lower()
                    != "hoctiengtrungdb"
                ):
                    fail(
                        "Dang ket noi nham database."
                    )

                print(
                    "KET NOI: OK"
                )

                # =================================================
                # 2. VERIFY 23 LESSONS
                # =================================================
                print()
                print(
                    "[2] KIEM TRA 23 BAI HSK1"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        bh.MaBaiHoc,
                        bh.SoThuTuBai,
                        bh.TieuDe
                    FROM dbo.BaiHoc AS bh
                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc = kh.MaKhoaHoc
                    WHERE
                        kh.MaKyHieu = ?
                    ORDER BY
                        bh.SoThuTuBai;
                    """,
                    COURSE_CODE,
                )

                lesson_rows = (
                    cursor.fetchall()
                )

                if (
                    len(lesson_rows)
                    != EXPECTED_LESSONS
                ):
                    fail(
                        "HSK1 khong co dung 23 bai. "
                        f"Thuc te: {len(lesson_rows)}"
                    )

                lesson_map = {
                    int(row[1]): {
                        "MaBaiHoc": int(row[0]),
                        "TieuDe": clean(row[2]),
                    }
                    for row in lesson_rows
                }

                if (
                    set(lesson_map.keys())
                    != set(range(1, 24))
                ):
                    fail(
                        "SoThuTuBai khong du 1 -> 23."
                    )

                print(
                    "23/23 BAI: OK"
                )

                # =================================================
                # 3. READ 501 VOCAB LINKS
                # =================================================
                print()
                print(
                    "[3] DOC 501 TU VUNG HSK1"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        bh.SoThuTuBai,
                        bh.MaBaiHoc,
                        bh.TieuDe,

                        tvbh.ThuTu,

                        tv.MaTuVung,
                        tv.ChuHan,
                        tv.PhienAm,
                        tv.NghiaTiengViet,
                        tv.TuLoai,
                        tv.MaNguon,
                        tv.DaDuyet

                    FROM dbo.TuVungBaiHoc AS tvbh

                    INNER JOIN dbo.BaiHoc AS bh
                        ON tvbh.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    INNER JOIN dbo.TuVung AS tv
                        ON tvbh.MaTuVung
                        = tv.MaTuVung

                    WHERE
                        kh.MaKyHieu = ?

                    ORDER BY
                        bh.SoThuTuBai,
                        tvbh.ThuTu,
                        tv.MaTuVung;
                    """,
                    COURSE_CODE,
                )

                vocab_rows = (
                    cursor.fetchall()
                )

                print(
                    "Tong lien ket tu vung:",
                    len(vocab_rows),
                )

                if (
                    len(vocab_rows)
                    != EXPECTED_VOCAB_LINKS
                ):
                    fail(
                        "HSK1 khong co dung "
                        "501 lien ket tu vung."
                    )

                not_approved = [
                    row
                    for row in vocab_rows
                    if int(row[10]) != 1
                ]

                if not_approved:
                    fail(
                        "Van con tu vung "
                        "DaDuyet != 1."
                    )

                print(
                    "501/501 DaDuyet=1: OK"
                )

                # =================================================
                # 4. READ CURRENT ChuHan
                # =================================================
                print()
                print(
                    "[4] DOC ChuHan HIEN TAI"
                )
                print("-" * 120)

                cursor.execute(
                    """
                    SELECT
                        ch.MaChuHan,
                        bh.SoThuTuBai,
                        ch.MaBaiHoc,
                        bh.TieuDe,
                        ch.ThuTu,
                        ch.KyTu,
                        ch.Pinyin,
                        ch.NghiaTiengViet,
                        ch.MaBoThu,
                        ch.SoNet,
                        ch.MaNguon,
                        ch.TrangThai

                    FROM dbo.ChuHan AS ch

                    INNER JOIN dbo.BaiHoc AS bh
                        ON ch.MaBaiHoc
                        = bh.MaBaiHoc

                    INNER JOIN dbo.KhoaHoc AS kh
                        ON bh.MaKhoaHoc
                        = kh.MaKhoaHoc

                    WHERE
                        kh.MaKyHieu = ?

                    ORDER BY
                        bh.SoThuTuBai,
                        ch.ThuTu,
                        ch.MaChuHan;
                    """,
                    COURSE_CODE,
                )

                current_rows = (
                    cursor.fetchall()
                )

                print(
                    "Tong ChuHan hien tai:",
                    len(current_rows),
                )

                current_lesson1 = sum(
                    1
                    for row in current_rows
                    if int(row[1]) == 1
                )

                print(
                    "ChuHan Bai 1:",
                    current_lesson1,
                )

                if (
                    len(current_rows)
                    != EXPECTED_CURRENT_HANZI
                ):
                    fail(
                        "ChuHan hien tai "
                        "khong con dung 17 dong."
                    )

                if (
                    current_lesson1
                    != EXPECTED_CURRENT_HANZI_LESSON1
                ):
                    fail(
                        "Khong con dung "
                        "17 ChuHan o Bai 1."
                    )

                current_by_char = defaultdict(
                    list
                )

                for row in current_rows:

                    current_by_char[
                        clean(row[5])
                    ].append(
                        {
                            "MaChuHan": int(row[0]),
                            "SoThuTuBai": int(row[1]),
                            "MaBaiHoc": int(row[2]),
                            "TieuDeBai": clean(row[3]),
                            "ThuTu": int(row[4]),
                            "KyTu": clean(row[5]),
                            "Pinyin": clean(row[6]),
                            "NghiaTiengViet": clean(row[7]),
                            "MaBoThu": clean(row[8]),
                            "SoNet": clean(row[9]),
                            "MaNguon": clean(row[10]),
                            "TrangThai": clean(row[11]),
                        }
                    )

                duplicate_current = {
                    char: items
                    for char, items
                    in current_by_char.items()
                    if len(items) > 1
                }

                print(
                    "ChuHan bi trung KyTu:",
                    len(duplicate_current),
                )

                # =================================================
                # 5. SPLIT VOCAB INTO HANZI
                # =================================================
                print()
                print(
                    "[5] TACH 501 TU VUNG "
                    "THANH TUNG CHU HAN"
                )
                print("-" * 120)

                candidates = {}

                total_hanzi_occurrences = 0

                for row in vocab_rows:

                    lesson_no = int(row[0])
                    lesson_id = int(row[1])
                    lesson_title = clean(row[2])

                    vocab_order = int(row[3])

                    vocab_id = int(row[4])
                    word = clean(row[5])
                    word_pinyin = clean(row[6])
                    word_meaning = clean(row[7])
                    word_pos = clean(row[8])

                    for char_position, char in enumerate(
                        word,
                        start=1,
                    ):

                        if not is_hanzi(char):
                            continue

                        total_hanzi_occurrences += 1

                        first_key = (
                            lesson_no,
                            vocab_order,
                            char_position,
                            vocab_id,
                        )

                        if char not in candidates:

                            candidates[
                                char
                            ] = {
                                "KyTu": char,

                                "BaiXuatHienDau": (
                                    lesson_no
                                ),

                                "MaBaiHocDauTien": (
                                    lesson_id
                                ),

                                "TieuDeBaiDauTien": (
                                    lesson_title
                                ),

                                "ThuTuTuVungDauTien": (
                                    vocab_order
                                ),

                                "ViTriTrongTuDauTien": (
                                    char_position
                                ),

                                "MaTuVungDauTien": (
                                    vocab_id
                                ),

                                "TuVungDauTien": (
                                    word
                                ),

                                "PinyinTuDauTien": (
                                    word_pinyin
                                ),

                                "NghiaTuDauTien": (
                                    word_meaning
                                ),

                                "TuLoaiTuDauTien": (
                                    word_pos
                                ),

                                "_first_key": (
                                    first_key
                                ),

                                "_occurrences": 0,
                                "_words": [],
                                "_word_ids": set(),
                            }

                        candidate = candidates[
                            char
                        ]

                        candidate[
                            "_occurrences"
                        ] += 1

                        if (
                            vocab_id
                            not in candidate[
                                "_word_ids"
                            ]
                        ):
                            candidate[
                                "_word_ids"
                            ].add(
                                vocab_id
                            )

                            candidate[
                                "_words"
                            ].append(
                                word
                            )

                        # Neu co truong hop du lieu
                        # khong duoc ORDER nhu mong doi,
                        # van dam bao lay dung lan dau.
                        if (
                            first_key
                            < candidate[
                                "_first_key"
                            ]
                        ):

                            candidate[
                                "BaiXuatHienDau"
                            ] = lesson_no

                            candidate[
                                "MaBaiHocDauTien"
                            ] = lesson_id

                            candidate[
                                "TieuDeBaiDauTien"
                            ] = lesson_title

                            candidate[
                                "ThuTuTuVungDauTien"
                            ] = vocab_order

                            candidate[
                                "ViTriTrongTuDauTien"
                            ] = char_position

                            candidate[
                                "MaTuVungDauTien"
                            ] = vocab_id

                            candidate[
                                "TuVungDauTien"
                            ] = word

                            candidate[
                                "PinyinTuDauTien"
                            ] = word_pinyin

                            candidate[
                                "NghiaTuDauTien"
                            ] = word_meaning

                            candidate[
                                "TuLoaiTuDauTien"
                            ] = word_pos

                            candidate[
                                "_first_key"
                            ] = first_key

                print(
                    "Tong lan xuat hien ky tu Han:",
                    total_hanzi_occurrences,
                )

                print(
                    "Tong Chu Han khac nhau:",
                    len(candidates),
                )

                # =================================================
                # 6. BUILD REVIEW
                # =================================================
                print()
                print(
                    "[6] DOI CHIEU ChuHan HIEN CO"
                )
                print("-" * 120)

                review_rows = []

                status_counts = defaultdict(
                    int
                )

                first_lesson_counts = defaultdict(
                    int
                )

                for char, item in sorted(
                    candidates.items(),
                    key=lambda pair: (
                        pair[1][
                            "_first_key"
                        ],
                        ord(pair[0]),
                    ),
                ):

                    first_lesson = int(
                        item[
                            "BaiXuatHienDau"
                        ]
                    )

                    first_lesson_counts[
                        first_lesson
                    ] += 1

                    existing = (
                        current_by_char.get(
                            char,
                            [],
                        )
                    )

                    if len(existing) == 0:

                        status = (
                            "CHUA_CO_TRONG_CHUHAN"
                        )

                        existing_id = ""
                        existing_lesson = ""
                        existing_order = ""
                        existing_pinyin = ""
                        existing_meaning = ""
                        existing_radical = ""
                        existing_strokes = ""

                    elif len(existing) == 1:

                        existing_row = (
                            existing[0]
                        )

                        existing_id = (
                            existing_row[
                                "MaChuHan"
                            ]
                        )

                        existing_lesson = (
                            existing_row[
                                "SoThuTuBai"
                            ]
                        )

                        existing_order = (
                            existing_row[
                                "ThuTu"
                            ]
                        )

                        existing_pinyin = (
                            existing_row[
                                "Pinyin"
                            ]
                        )

                        existing_meaning = (
                            existing_row[
                                "NghiaTiengViet"
                            ]
                        )

                        existing_radical = (
                            existing_row[
                                "MaBoThu"
                            ]
                        )

                        existing_strokes = (
                            existing_row[
                                "SoNet"
                            ]
                        )

                        if (
                            existing_lesson
                            == first_lesson
                        ):

                            status = (
                                "DA_CO_DUNG_BAI"
                            )

                        else:

                            status = (
                                "DA_CO_KHAC_BAI"
                            )

                    else:

                        status = (
                            "TRUNG_KYTU_TRONG_CHUHAN"
                        )

                        existing_id = ";".join(
                            str(x["MaChuHan"])
                            for x in existing
                        )

                        existing_lesson = ";".join(
                            str(x["SoThuTuBai"])
                            for x in existing
                        )

                        existing_order = ""
                        existing_pinyin = ""
                        existing_meaning = ""
                        existing_radical = ""
                        existing_strokes = ""

                    status_counts[
                        status
                    ] += 1

                    words_text = " | ".join(
                        item["_words"]
                    )

                    review_rows.append(
                        {
                            "KyTu": char,

                            "BaiXuatHienDau": (
                                first_lesson
                            ),

                            "MaBaiHocDauTien": (
                                item[
                                    "MaBaiHocDauTien"
                                ]
                            ),

                            "TieuDeBaiDauTien": (
                                item[
                                    "TieuDeBaiDauTien"
                                ]
                            ),

                            "ThuTuTuVungDauTien": (
                                item[
                                    "ThuTuTuVungDauTien"
                                ]
                            ),

                            "ViTriTrongTuDauTien": (
                                item[
                                    "ViTriTrongTuDauTien"
                                ]
                            ),

                            "MaTuVungDauTien": (
                                item[
                                    "MaTuVungDauTien"
                                ]
                            ),

                            "TuVungDauTien": (
                                item[
                                    "TuVungDauTien"
                                ]
                            ),

                            "PinyinTuDauTien": (
                                item[
                                    "PinyinTuDauTien"
                                ]
                            ),

                            "NghiaTuDauTien": (
                                item[
                                    "NghiaTuDauTien"
                                ]
                            ),

                            "SoTuVungChuaChu": (
                                len(
                                    item[
                                        "_word_ids"
                                    ]
                                )
                            ),

                            "TongLanXuatHien": (
                                item[
                                    "_occurrences"
                                ]
                            ),

                            "CacTuVungChuaChu": (
                                words_text
                            ),

                            "TrangThaiDoiChieu": (
                                status
                            ),

                            "MaChuHanHienTai": (
                                existing_id
                            ),

                            "BaiHienTai": (
                                existing_lesson
                            ),

                            "ThuTuHienTai": (
                                existing_order
                            ),

                            "PinyinHienTai": (
                                existing_pinyin
                            ),

                            "NghiaHienTai": (
                                existing_meaning
                            ),

                            "MaBoThuHienTai": (
                                existing_radical
                            ),

                            "SoNetHienTai": (
                                existing_strokes
                            ),

                            # Chua tu dong phe duyet.
                            "DaKiemDuyetUngVien": 0,

                            "GhiChuKiemDuyet": "",
                        }
                    )

                print(
                    "DA_CO_DUNG_BAI:",
                    status_counts[
                        "DA_CO_DUNG_BAI"
                    ],
                )

                print(
                    "DA_CO_KHAC_BAI:",
                    status_counts[
                        "DA_CO_KHAC_BAI"
                    ],
                )

                print(
                    "CHUA_CO_TRONG_CHUHAN:",
                    status_counts[
                        "CHUA_CO_TRONG_CHUHAN"
                    ],
                )

                print(
                    "TRUNG_KYTU_TRONG_CHUHAN:",
                    status_counts[
                        "TRUNG_KYTU_TRONG_CHUHAN"
                    ],
                )

                # =================================================
                # 7. SUMMARY PER LESSON
                # =================================================
                print()
                print(
                    "[7] THONG KE CHU MOI "
                    "THEO BAI XUAT HIEN DAU"
                )
                print("-" * 120)

                current_counts = defaultdict(
                    int
                )

                for row in current_rows:

                    current_counts[
                        int(row[1])
                    ] += 1

                summary_rows = []

                for lesson_no in range(
                    1,
                    24,
                ):

                    new_char_count = (
                        first_lesson_counts.get(
                            lesson_no,
                            0,
                        )
                    )

                    current_count = (
                        current_counts.get(
                            lesson_no,
                            0,
                        )
                    )

                    exact_existing = sum(
                        1
                        for row in review_rows
                        if (
                            int(
                                row[
                                    "BaiXuatHienDau"
                                ]
                            )
                            == lesson_no
                            and row[
                                "TrangThaiDoiChieu"
                            ]
                            == "DA_CO_DUNG_BAI"
                        )
                    )

                    missing_count = sum(
                        1
                        for row in review_rows
                        if (
                            int(
                                row[
                                    "BaiXuatHienDau"
                                ]
                            )
                            == lesson_no
                            and row[
                                "TrangThaiDoiChieu"
                            ]
                            == "CHUA_CO_TRONG_CHUHAN"
                        )
                    )

                    summary_rows.append(
                        {
                            "SoThuTuBai": (
                                lesson_no
                            ),

                            "MaBaiHoc": (
                                lesson_map[
                                    lesson_no
                                ][
                                    "MaBaiHoc"
                                ]
                            ),

                            "TieuDeBai": (
                                lesson_map[
                                    lesson_no
                                ][
                                    "TieuDe"
                                ]
                            ),

                            "SoChuKhacNhauXuatHienDau": (
                                new_char_count
                            ),

                            "SoChuDangCoTrongSQL": (
                                current_count
                            ),

                            "SoChuDaCoDungBai": (
                                exact_existing
                            ),

                            "SoChuChuaCo": (
                                missing_count
                            ),
                        }
                    )

                    print(
                        f"Bai {lesson_no:>2}: "
                        f"Chu xuat hien dau="
                        f"{new_char_count:>3} | "
                        f"SQL hien co="
                        f"{current_count:>3} | "
                        f"Da co dung bai="
                        f"{exact_existing:>3} | "
                        f"Chua co="
                        f"{missing_count:>3}"
                    )

                # =================================================
                # 8. WRITE FILES
                # =================================================
                print()
                print(
                    "[8] TAO FILE REVIEW"
                )
                print("-" * 120)

                write_csv(
                    CANDIDATE_FILE,
                    [
                        "KyTu",
                        "BaiXuatHienDau",
                        "MaBaiHocDauTien",
                        "TieuDeBaiDauTien",
                        "ThuTuTuVungDauTien",
                        "ViTriTrongTuDauTien",
                        "MaTuVungDauTien",
                        "TuVungDauTien",
                        "PinyinTuDauTien",
                        "NghiaTuDauTien",
                        "SoTuVungChuaChu",
                        "TongLanXuatHien",
                        "CacTuVungChuaChu",
                        "TrangThaiDoiChieu",
                        "MaChuHanHienTai",
                        "BaiHienTai",
                        "ThuTuHienTai",
                        "PinyinHienTai",
                        "NghiaHienTai",
                        "MaBoThuHienTai",
                        "SoNetHienTai",
                        "DaKiemDuyetUngVien",
                        "GhiChuKiemDuyet",
                    ],
                    review_rows,
                )

                write_csv(
                    SUMMARY_FILE,
                    [
                        "SoThuTuBai",
                        "MaBaiHoc",
                        "TieuDeBai",
                        "SoChuKhacNhauXuatHienDau",
                        "SoChuDangCoTrongSQL",
                        "SoChuDaCoDungBai",
                        "SoChuChuaCo",
                    ],
                    summary_rows,
                )

                print(
                    "Candidate review:"
                )

                print(
                    CANDIDATE_FILE
                )

                print()
                print(
                    "Summary:"
                )

                print(
                    SUMMARY_FILE
                )

                # =================================================
                # FINAL
                # =================================================
                print()
                print("=" * 120)
                print(
                    "KET QUA 10B"
                )
                print("=" * 120)

                print(
                    "So bai HSK1:",
                    23,
                )

                print(
                    "Tu vung da phan tich:",
                    len(vocab_rows),
                )

                print(
                    "Tong lan ky tu Han "
                    "xuat hien:",
                    total_hanzi_occurrences,
                )

                print(
                    "Tong Chu Han khac nhau:",
                    len(candidates),
                )

                print(
                    "ChuHan hien co trong SQL:",
                    len(current_rows),
                )

                print(
                    "Da co dung bai xuat hien dau:",
                    status_counts[
                        "DA_CO_DUNG_BAI"
                    ],
                )

                print(
                    "Da co nhung khac bai:",
                    status_counts[
                        "DA_CO_KHAC_BAI"
                    ],
                )

                print(
                    "Chua co trong dbo.ChuHan:",
                    status_counts[
                        "CHUA_CO_TRONG_CHUHAN"
                    ],
                )

                print(
                    "KyTu bi trung trong dbo.ChuHan:",
                    status_counts[
                        "TRUNG_KYTU_TRONG_CHUHAN"
                    ],
                )

                print(
                    "DaKiemDuyetUngVien:",
                    0,
                )

                print()
                print(
                    "DATABASE KHONG BI SUA."
                )

                print(
                    "CHUA INSERT ChuHan."
                )

                print(
                    "CHUA INSERT NetChuHan."
                )

                print()
                print(
                    "BUOC TIEP THEO:"
                )

                print(
                    "KIEM TRA DANH SACH UNG VIEN "
                    "TRUOC KHI QUYET DINH "
                    "CHU NAO SE DUOC DAY "
                    "TRONG 23 BAI HSK1."
                )

                print()
                print("=" * 120)
                print("HOAN TAT")
                print("=" * 120)

        finally:

            try:
                connection.rollback()
            except Exception:
                pass


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 120)
        print(
            "10B THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)