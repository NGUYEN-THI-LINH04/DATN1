from pathlib import Path
import csv
import hashlib
import sys
from contextlib import closing


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# FILES
# =========================================================
BACKUP_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
    / "db_backup"
    / "hsk1_tuvung_before_review_apply_20260929_025148.csv"
)

APPLIED_REVIEW_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "review"
    / "db_backup"
    / "hsk1_review_applied_20260929_030228.csv"
)

EXPECTED_BACKUP_SHA256 = (
    "ca0e3fc574c53d51a35e70007bc2a707"
    "1563edc3a64a01eae869fc6446175512"
)

EXPECTED_REVIEW_SHA256 = (
    "d0e35702983cb95729462cac2d917011"
    "d22e6aae2cc45cbd03538567447fe41c"
)

EXPECTED_ROWS = 501


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def normalize_bit(value):
    """
    Chuan hoa gia tri BIT ve chuoi "0" hoac "1".

    Ho tro:
    - 0 / 1
    - False / True
    - false / true
    - No / Yes

    File backup 09g28 co the luu SQL BIT
    thanh False/True thay vi 0/1.
    """

    text = clean(value).lower()

    if text in {
        "1",
        "true",
        "yes",
    }:
        return "1"

    if text in {
        "0",
        "false",
        "no",
        "",
    }:
        return "0"

    raise RuntimeError(
        "Gia tri BIT khong hop le: "
        f"{value}"
    )


def fail(message):

    raise RuntimeError(message)


def sha256_file(path):

    digest = hashlib.sha256()

    with open(path, "rb") as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def load_csv(path):

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:

            fail(
                "Khong doc duoc header:\n"
                f"{path}"
            )

        fieldnames = reader.fieldnames
        rows = list(reader)

    return fieldnames, rows


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 110)
    print(
        "09G30 - AUDIT DATABASE HSK1 "
        "SAU KHI APPLY REVIEW"
    )
    print("=" * 110)

    print()
    print("CHE DO:")
    print("  CHI DOC FILE")
    print("  CHI SELECT DATABASE")
    print("  KHONG INSERT")
    print("  KHONG UPDATE")
    print("  KHONG DELETE")
    print("  KHONG COMMIT")

    # =====================================================
    # 1. VERIFY FILE BACKUP
    # =====================================================
    print()
    print("[1] VERIFY BACKUP TRUOC APPLY")
    print("-" * 110)

    if not BACKUP_FILE.exists():

        fail(
            "Khong tim thay backup:\n"
            f"{BACKUP_FILE}"
        )

    backup_hash = sha256_file(
        BACKUP_FILE
    )

    print("Backup:")
    print(BACKUP_FILE)

    print("SHA256:")
    print(backup_hash)

    if (
        backup_hash
        != EXPECTED_BACKUP_SHA256
    ):

        fail(
            "SHA256 backup bi thay doi.\n"
            "KHONG DUOC TIEP TUC AUDIT."
        )

    print("BACKUP: OK")

    # =====================================================
    # 2. VERIFY SNAPSHOT REVIEW
    # =====================================================
    print()
    print(
        "[2] VERIFY SNAPSHOT REVIEW DA APPLY"
    )
    print("-" * 110)

    if not APPLIED_REVIEW_FILE.exists():

        fail(
            "Khong tim thay snapshot review:\n"
            f"{APPLIED_REVIEW_FILE}"
        )

    review_hash = sha256_file(
        APPLIED_REVIEW_FILE
    )

    print("Snapshot:")
    print(APPLIED_REVIEW_FILE)

    print("SHA256:")
    print(review_hash)

    if (
        review_hash
        != EXPECTED_REVIEW_SHA256
    ):

        fail(
            "SHA256 snapshot review "
            "bi thay doi."
        )

    print("SNAPSHOT REVIEW: OK")

    # =====================================================
    # 3. LOAD FILES
    # =====================================================
    print()
    print("[3] DOC DU LIEU DOI CHIEU")
    print("-" * 110)

    (
        backup_fields,
        backup_rows,
    ) = load_csv(
        BACKUP_FILE
    )

    (
        review_fields,
        review_rows,
    ) = load_csv(
        APPLIED_REVIEW_FILE
    )

    if len(backup_rows) != EXPECTED_ROWS:

        fail(
            "Backup khong co dung "
            "501 dong.\n"
            f"Thuc te: {len(backup_rows)}"
        )

    if len(review_rows) != EXPECTED_ROWS:

        fail(
            "Snapshot review khong co "
            "dung 501 dong.\n"
            f"Thuc te: {len(review_rows)}"
        )

    # =====================================================
    # CAC COT BACKUP CAN CO
    # =====================================================
    required_backup_fields = {
        "MaTuVung",
        "ChuHan",
        "ChuPhonThe",
        "PhienAm",
        "NghiaTiengViet",
        "TuLoai",
        "ViDuTiengTrung",
        "ViDuTiengViet",
        "MaAmThanh",
        "MaNguon",
        "DaDuyet",
        "NgayTao",
    }

    # =====================================================
    # CAC COT REVIEW CAN CO
    # =====================================================
    required_review_fields = {
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "MaNguon",
        "TuLoaiHocTap",
        "NghiaHocTap",
        "DaKiemDuyet",
    }

    missing_backup = (
        required_backup_fields
        - set(backup_fields)
    )

    missing_review = (
        required_review_fields
        - set(review_fields)
    )

    if missing_backup:

        fail(
            "Backup thieu cot: "
            + ", ".join(
                sorted(missing_backup)
            )
        )

    if missing_review:

        fail(
            "Snapshot review thieu cot: "
            + ", ".join(
                sorted(missing_review)
            )
        )

    # =====================================================
    # KIEM TRA MaTuVung VA TRANG THAI REVIEW
    # =====================================================
    backup_by_id = {}

    for row in backup_rows:

        vocab_id_text = clean(
            row["MaTuVung"]
        )

        if not vocab_id_text.isdigit():

            fail(
                "MaTuVung backup "
                "khong hop le: "
                f"{vocab_id_text}"
            )

        vocab_id = int(
            vocab_id_text
        )

        if vocab_id in backup_by_id:

            fail(
                "MaTuVung bi lap "
                "trong backup: "
                f"{vocab_id}"
            )

        backup_by_id[
            vocab_id
        ] = row

    review_by_id = {}

    for row in review_rows:

        vocab_id_text = clean(
            row["MaTuVung"]
        )

        if not vocab_id_text.isdigit():

            fail(
                "MaTuVung review "
                "khong hop le: "
                f"{vocab_id_text}"
            )

        vocab_id = int(
            vocab_id_text
        )

        if vocab_id in review_by_id:

            fail(
                "MaTuVung bi lap "
                "trong review: "
                f"{vocab_id}"
            )

        if clean(
            row["DaKiemDuyet"]
        ) != "1":

            fail(
                "Snapshot review co dong "
                "chua DaKiemDuyet=1: "
                f"MaTuVung={vocab_id}"
            )

        review_by_id[
            vocab_id
        ] = row

    if len(backup_by_id) != 501:

        fail(
            "Backup khong co "
            "501 MaTuVung duy nhat."
        )

    if len(review_by_id) != 501:

        fail(
            "Review khong co "
            "501 MaTuVung duy nhat."
        )

    if (
        set(backup_by_id)
        != set(review_by_id)
    ):

        fail(
            "MaTuVung backup va review "
            "khong khop nhau."
        )

    print(
        "Backup:",
        len(backup_rows),
    )

    print(
        "Review:",
        len(review_rows),
    )

    print(
        "501 MaTuVung: OK"
    )

    # =====================================================
    # THONG KE DaDuyet TRONG BACKUP
    # =====================================================
    backup_approved = sum(
        1
        for row in backup_rows
        if normalize_bit(
            row["DaDuyet"]
        ) == "1"
    )

    backup_unapproved = sum(
        1
        for row in backup_rows
        if normalize_bit(
            row["DaDuyet"]
        ) == "0"
    )

    print(
        "Backup DaDuyet=1:",
        backup_approved,
    )

    print(
        "Backup DaDuyet=0:",
        backup_unapproved,
    )

    if backup_approved != 0:

        fail(
            "Backup truoc apply co "
            "ban ghi DaDuyet=1."
        )

    if backup_unapproved != 501:

        fail(
            "Backup truoc apply "
            "khong co dung "
            "501 ban ghi DaDuyet=0."
        )

    print(
        "TRANG THAI BACKUP TRUOC APPLY: OK"
    )

    # =====================================================
    # 4. CONNECT DATABASE
    # =====================================================
    print()
    print("[4] KET NOI DATABASE")
    print("-" * 110)

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
                        CONVERT(
                            nvarchar(128),
                            SERVERPROPERTY('ServerName')
                        ),
                        DB_NAME(),
                        SUSER_SNAME();
                    """
                )

                (
                    server_name,
                    database_name,
                    login_name,
                ) = cursor.fetchone()

                print(
                    "Server:",
                    server_name,
                )

                print(
                    "Database:",
                    database_name,
                )

                print(
                    "Tai khoan:",
                    login_name,
                )

                if clean(
                    database_name
                ).lower() != (
                    "hoctiengtrungdb"
                ):

                    fail(
                        "Dang ket noi nham "
                        "database.\n"
                        f"Thuc te: {database_name}"
                    )

                print(
                    "KET NOI DATABASE: OK"
                )

                # =========================================
                # 5. LOAD DATABASE
                # =========================================
                print()
                print("[5] DOC dbo.TuVung")
                print("-" * 110)

                cursor.execute(
                    """
                    SELECT
                        MaTuVung,
                        ChuHan,
                        ChuPhonThe,
                        PhienAm,
                        NghiaTiengViet,
                        TuLoai,
                        ViDuTiengTrung,
                        ViDuTiengViet,
                        MaAmThanh,
                        MaNguon,
                        DaDuyet,
                        NgayTao
                    FROM dbo.TuVung
                    ORDER BY MaTuVung;
                    """
                )

                db_rows_raw = (
                    cursor.fetchall()
                )

                if len(
                    db_rows_raw
                ) != 501:

                    fail(
                        "dbo.TuVung khong co "
                        "dung 501 dong.\n"
                        f"Thuc te: "
                        f"{len(db_rows_raw)}"
                    )

                db_by_id = {}

                for row in db_rows_raw:

                    vocab_id = int(
                        row[0]
                    )

                    if vocab_id in db_by_id:

                        fail(
                            "MaTuVung bi lap "
                            "trong database: "
                            f"{vocab_id}"
                        )

                    db_by_id[
                        vocab_id
                    ] = {
                        "MaTuVung": str(
                            vocab_id
                        ),

                        "ChuHan": clean(
                            row[1]
                        ),

                        "ChuPhonThe": clean(
                            row[2]
                        ),

                        "PhienAm": clean(
                            row[3]
                        ),

                        "NghiaTiengViet": clean(
                            row[4]
                        ),

                        "TuLoai": clean(
                            row[5]
                        ),

                        "ViDuTiengTrung": clean(
                            row[6]
                        ),

                        "ViDuTiengViet": clean(
                            row[7]
                        ),

                        "MaAmThanh": (
                            ""
                            if row[8] is None
                            else str(
                                int(row[8])
                            )
                        ),

                        "MaNguon": (
                            ""
                            if row[9] is None
                            else str(
                                int(row[9])
                            )
                        ),

                        "DaDuyet": (
                            "1"
                            if bool(
                                row[10]
                            )
                            else "0"
                        ),

                        "NgayTao": clean(
                            row[11]
                        ),
                    }

                if (
                    set(db_by_id)
                    != set(review_by_id)
                ):

                    fail(
                        "Danh sach MaTuVung DB "
                        "khong khop review."
                    )

                print(
                    "Tong dong DB:",
                    len(db_by_id),
                )

                print(
                    "501/501 MaTuVung: OK"
                )

                # =========================================
                # 6. SO SANH VOI REVIEW
                # =========================================
                print()
                print(
                    "[6] KIEM TRA NOI DUNG "
                    "DA APPLY"
                )
                print("-" * 110)

                review_errors = []

                for (
                    vocab_id,
                    review,
                ) in review_by_id.items():

                    db = db_by_id[
                        vocab_id
                    ]

                    expected_hanzi = clean(
                        review["ChuHan"]
                    )

                    expected_pinyin = clean(
                        review["PhienAm"]
                    )

                    expected_source = clean(
                        review["MaNguon"]
                    )

                    expected_meaning = clean(
                        review[
                            "NghiaHocTap"
                        ]
                    )

                    expected_pos = clean(
                        review[
                            "TuLoaiHocTap"
                        ]
                    )

                    if (
                        db["ChuHan"]
                        != expected_hanzi
                        or
                        db["PhienAm"]
                        != expected_pinyin
                        or
                        db["MaNguon"]
                        != expected_source
                        or
                        db[
                            "NghiaTiengViet"
                        ]
                        != expected_meaning
                        or
                        db["TuLoai"]
                        != expected_pos
                        or
                        normalize_bit(
                            db["DaDuyet"]
                        )
                        != "1"
                    ):

                        review_errors.append(
                            vocab_id
                        )

                print(
                    "Ban ghi khong khop "
                    "snapshot review:",
                    len(review_errors),
                )

                if review_errors:

                    print(
                        "ID loi:",
                        review_errors[:30],
                    )

                    fail(
                        "Database khong khop "
                        "snapshot review da apply."
                    )

                print(
                    "DATABASE <-> REVIEW: OK"
                )

                # =========================================
                # 7. KIEM TRA CAC COT KHONG DUOC SUA
                # =========================================
                print()
                print(
                    "[7] KIEM TRA CAC COT "
                    "KHONG DUOC PHEP THAY DOI"
                )
                print("-" * 110)

                immutable_columns = [
                    "MaTuVung",
                    "ChuHan",
                    "ChuPhonThe",
                    "PhienAm",
                    "ViDuTiengTrung",
                    "ViDuTiengViet",
                    "MaAmThanh",
                    "MaNguon",
                ]

                immutable_errors = []

                for (
                    vocab_id,
                    backup,
                ) in backup_by_id.items():

                    db = db_by_id[
                        vocab_id
                    ]

                    for column in (
                        immutable_columns
                    ):

                        if (
                            clean(
                                db[column]
                            )
                            != clean(
                                backup[column]
                            )
                        ):

                            immutable_errors.append(
                                (
                                    vocab_id,
                                    column,
                                    clean(
                                        backup[
                                            column
                                        ]
                                    ),
                                    clean(
                                        db[
                                            column
                                        ]
                                    ),
                                )
                            )

                print(
                    "Sai cot bat bien:",
                    len(
                        immutable_errors
                    ),
                )

                if immutable_errors:

                    for (
                        vocab_id,
                        column,
                        old_value,
                        new_value,
                    ) in immutable_errors[:30]:

                        print()
                        print(
                            f"MaTuVung="
                            f"{vocab_id}"
                        )

                        print(
                            f"  Cot: "
                            f"{column}"
                        )

                        print(
                            f"  Backup: "
                            f"{old_value}"
                        )

                        print(
                            f"  DB: "
                            f"{new_value}"
                        )

                    fail(
                        "Phat hien cot "
                        "khong duoc phep "
                        "bi thay doi."
                    )

                print(
                    "CAC COT BAT BIEN: OK"
                )

                # =========================================
                # 8. DOI CHIEU VOI BACKUP
                # =========================================
                print()
                print(
                    "[8] DOI CHIEU VOI BACKUP "
                    "TRUOC APPLY"
                )
                print("-" * 110)

                meaning_changed = 0
                pos_changed = 0
                approved_changed = 0

                unexpected_approved = 0

                for (
                    vocab_id,
                    backup,
                ) in backup_by_id.items():

                    db = db_by_id[
                        vocab_id
                    ]

                    # -------------------------------------
                    # NghiaTiengViet
                    # -------------------------------------
                    if (
                        clean(
                            db[
                                "NghiaTiengViet"
                            ]
                        )
                        != clean(
                            backup[
                                "NghiaTiengViet"
                            ]
                        )
                    ):

                        meaning_changed += 1

                    # -------------------------------------
                    # TuLoai
                    # -------------------------------------
                    if (
                        clean(
                            db["TuLoai"]
                        )
                        != clean(
                            backup["TuLoai"]
                        )
                    ):

                        pos_changed += 1

                    # -------------------------------------
                    # DaDuyet
                    #
                    # Backup co the la:
                    # False
                    #
                    # Database hien tai:
                    # 1
                    #
                    # Phai normalize truoc khi so sanh.
                    # -------------------------------------
                    backup_approved_value = (
                        normalize_bit(
                            backup[
                                "DaDuyet"
                            ]
                        )
                    )

                    db_approved_value = (
                        normalize_bit(
                            db[
                                "DaDuyet"
                            ]
                        )
                    )

                    if (
                        backup_approved_value
                        == "0"
                        and
                        db_approved_value
                        == "1"
                    ):

                        approved_changed += 1

                    if (
                        db_approved_value
                        != "1"
                    ):

                        unexpected_approved += 1

                print(
                    "NghiaTiengViet thay doi:",
                    meaning_changed,
                )

                print(
                    "TuLoai thay doi:",
                    pos_changed,
                )

                print(
                    "DaDuyet 0 -> 1:",
                    approved_changed,
                )

                print(
                    "DaDuyet khac 1 hien tai:",
                    unexpected_approved,
                )

                if meaning_changed != 450:

                    fail(
                        "So NghiaTiengViet "
                        "thay doi khong bang 450.\n"
                        f"Thuc te: "
                        f"{meaning_changed}"
                    )

                if pos_changed != 501:

                    fail(
                        "So TuLoai thay doi "
                        "khong bang 501.\n"
                        f"Thuc te: "
                        f"{pos_changed}"
                    )

                if approved_changed != 501:

                    fail(
                        "Khong co dung 501 "
                        "DaDuyet chuyen 0 -> 1.\n"
                        f"Thuc te: "
                        f"{approved_changed}"
                    )

                if unexpected_approved != 0:

                    fail(
                        "Van co tu "
                        "DaDuyet != 1.\n"
                        f"Thuc te: "
                        f"{unexpected_approved}"
                    )

                print(
                    "SO SANH BACKUP: OK"
                )

                # =========================================
                # 9. SPECIAL WORDS
                # =========================================
                print()
                print(
                    "[9] KIEM TRA TU DA AM "
                    "QUAN TRONG"
                )
                print("-" * 110)

                special_cases = [
                    (
                        "干",
                        "gàn",
                        "làm; làm việc",
                    ),

                    (
                        "干",
                        "gān",
                        "khô",
                    ),

                    (
                        "还",
                        "hái",
                        "vẫn; còn",
                    ),

                    (
                        "还",
                        "huán",
                        "trả lại; hoàn lại",
                    ),

                    (
                        "地",
                        "dì",
                        "đất; mặt đất",
                    ),

                    (
                        "地",
                        "de",
                        (
                            "trợ từ nối trạng ngữ "
                            "với động từ"
                        ),
                    ),
                ]

                for (
                    hanzi,
                    pinyin,
                    meaning,
                ) in special_cases:

                    matches = [
                        db
                        for db
                        in db_by_id.values()
                        if (
                            db["ChuHan"]
                            == hanzi
                            and
                            db["PhienAm"]
                            == pinyin
                        )
                    ]

                    if len(matches) != 1:

                        fail(
                            "Khong tim thay "
                            "dung 1 muc:\n"
                            f"{hanzi} "
                            f"[{pinyin}]"
                        )

                    actual_meaning = (
                        matches[0][
                            "NghiaTiengViet"
                        ]
                    )

                    if (
                        actual_meaning
                        != meaning
                    ):

                        fail(
                            "Sai nghia:\n"
                            f"{hanzi} "
                            f"[{pinyin}]\n"
                            f"Mong doi: "
                            f"{meaning}\n"
                            f"Thuc te: "
                            f"{actual_meaning}"
                        )

                    if (
                        normalize_bit(
                            matches[0][
                                "DaDuyet"
                            ]
                        )
                        != "1"
                    ):

                        fail(
                            f"{hanzi} "
                            f"[{pinyin}] "
                            "chua DaDuyet=1."
                        )

                    print(
                        f"{hanzi} "
                        f"[{pinyin}] "
                        f"-> {meaning} OK"
                    )

                # =========================================
                # 10. KIEM TRA TU BO SUNG VIET NAM
                # =========================================
                print()
                print(
                    "[10] KIEM TRA TU BO SUNG 越南"
                )
                print("-" * 110)

                vietnam_rows = [
                    db
                    for db
                    in db_by_id.values()
                    if db[
                        "ChuHan"
                    ] == "越南"
                ]

                if len(vietnam_rows) != 1:

                    fail(
                        "Phai co dung "
                        "1 muc 越南."
                    )

                vietnam = vietnam_rows[0]

                if (
                    vietnam["PhienAm"].casefold()
                    != "yuènán".casefold()
                ):

                    fail(
                        "PhienAm 越南 sai:\n"
                        f"{vietnam['PhienAm']}"
                    )

                if (
                    vietnam[
                        "NghiaTiengViet"
                    ]
                    != "Việt Nam"
                ):

                    fail(
                        "NghiaTiengViet "
                        "cua 越南 sai:\n"
                        f"{vietnam['NghiaTiengViet']}"
                    )

                if (
                    vietnam[
                        "MaNguon"
                    ]
                    != "2"
                ):

                    fail(
                        "MaNguon cua 越南 "
                        "phai bang 2."
                    )

                if (
                    normalize_bit(
                        vietnam[
                            "DaDuyet"
                        ]
                    )
                    != "1"
                ):

                    fail(
                        "越南 chua "
                        "DaDuyet=1."
                    )

                print(
                    "ChuHan:",
                    vietnam[
                        "ChuHan"
                    ],
                )

                print(
                    "PhienAm:",
                    vietnam[
                        "PhienAm"
                    ],
                )

                print(
                    "NghiaTiengViet:",
                    vietnam[
                        "NghiaTiengViet"
                    ],
                )

                print(
                    "MaNguon:",
                    vietnam[
                        "MaNguon"
                    ],
                )

                print(
                    "DaDuyet:",
                    normalize_bit(
                        vietnam[
                            "DaDuyet"
                        ]
                    ),
                )

                print(
                    "越南: OK"
                )

                # =========================================
                # 11. FINAL COUNTS
                # =========================================
                approved_total = sum(
                    1
                    for db
                    in db_by_id.values()
                    if normalize_bit(
                        db[
                            "DaDuyet"
                        ]
                    )
                    == "1"
                )

                unapproved_total = sum(
                    1
                    for db
                    in db_by_id.values()
                    if normalize_bit(
                        db[
                            "DaDuyet"
                        ]
                    )
                    != "1"
                )

                if approved_total != 501:

                    fail(
                        "Tong DaDuyet=1 "
                        "khong bang 501."
                    )

                if unapproved_total != 0:

                    fail(
                        "Van con "
                        "DaDuyet != 1."
                    )

                # =========================================
                # 12. FINAL RESULT
                # =========================================
                print()
                print("=" * 110)
                print(
                    "KET QUA AUDIT SAU APPLY"
                )
                print("=" * 110)

                print(
                    "Tong dong DB:",
                    len(db_by_id),
                )

                print(
                    "Khong khop review:",
                    len(review_errors),
                )

                print(
                    "Cot bat bien bi thay doi:",
                    len(
                        immutable_errors
                    ),
                )

                print(
                    "NghiaTiengViet thay doi:",
                    meaning_changed,
                )

                print(
                    "TuLoai thay doi:",
                    pos_changed,
                )

                print(
                    "DaDuyet 0 -> 1:",
                    approved_changed,
                )

                print(
                    "DaDuyet=1 hien tai:",
                    approved_total,
                )

                print(
                    "DaDuyet khac 1:",
                    unapproved_total,
                )

                print()
                print(
                    "AUDIT SAU APPLY "
                    "THANH CONG."
                )

                print(
                    "DATABASE KHOP 100% "
                    "VOI SNAPSHOT REVIEW "
                    "DA APPLY."
                )

                print(
                    "CAC COT KHONG DUOC SUA "
                    "VAN GIU NGUYEN."
                )

                print(
                    "501/501 TU VUNG "
                    "DA DaDuyet=1."
                )

                print()
                print(
                    "SCRIPT NAY CHI SELECT."
                )

                print(
                    "DATABASE KHONG BI SUA."
                )

                print()
                print("=" * 110)
                print("HOAN TAT")
                print("=" * 110)

        finally:

            # Script chi SELECT.
            # Rollback de dong transaction doc
            # ma khong commit bat ky thao tac nao.
            try:
                connection.rollback()
            except Exception:
                pass


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 110)
        print(
            "AUDIT SAU APPLY THAT BAI"
        )
        print("=" * 110)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "SCRIPT NAY CHI DOC "
            "VA SELECT."
        )

        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)