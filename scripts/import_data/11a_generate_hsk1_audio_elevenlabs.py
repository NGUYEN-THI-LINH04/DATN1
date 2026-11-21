from __future__ import annotations

import argparse
import os
import sys
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


# ============================================================
# XÁC ĐỊNH THƯ MỤC GỐC PROJECT
# ============================================================

ROOT_DIR = (
    Path(__file__).resolve().parents[2]
    if Path(__file__).resolve().parent.name == "import_data"
    else Path(__file__).resolve().parents[1]
)

# Khi file nằm tại:
# D:\DATN1\scripts\import_data\11a_generate_hsk1_audio_elevenlabs.py
#
# ROOT_DIR phải là:
# D:\DATN1

if not (ROOT_DIR / "database.py").exists():
    candidate = Path.cwd()

    if (candidate / "database.py").exists():
        ROOT_DIR = candidate


if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from database import get_connection


# ============================================================
# CẤU HÌNH HSK1
# ============================================================

COURSE_CODE = "HSK1-CORE"

EXPECTED_VOCAB = 501
EXPECTED_HANZI = 301

MODEL_ID = "eleven_v4"

OUTPUT_FORMAT = "mp3_44100_128"

# File nhỏ hơn mức này xem như audio lỗi/rỗng.
MIN_VALID_MP3_BYTES = 500


# ============================================================
# THƯ MỤC AUDIO
# ============================================================

VOCAB_DIR = (
    ROOT_DIR
    / "static"
    / "audio"
    / "hsk1"
    / "tu_vung"
)

HANZI_DIR = (
    ROOT_DIR
    / "static"
    / "audio"
    / "hsk1"
    / "chu_han"
)


# ============================================================
# ĐỌC .ENV
# ============================================================

load_dotenv(
    ROOT_DIR / ".env",
    interpolate=False,
)

API_KEY = os.getenv(
    "ELEVENLABS_API_KEY",
    "",
).strip()

VOICE_ID = os.getenv(
    "ELEVENLABS_VOICE_ID",
    "",
).strip()


# ============================================================
# HÀM PHỤ
# ============================================================

def clean(value) -> str:
    if value is None:
        return ""

    return str(value).strip()


def fail(message: str):
    raise RuntimeError(message)


def normalize_pinyin(value: str) -> str:
    """
    Chuẩn hóa Pinyin để so sánh.

    Ví dụ:
        "nǐ"      -> "nǐ"
        "  nǐ  "  -> "nǐ"
        "Hànzì"   -> "hànzì"
    """

    return " ".join(
        clean(value).lower().split()
    )


def project_file_from_public_path(
    public_path: str,
) -> Path | None:

    value = clean(
        public_path
    ).replace(
        "\\",
        "/",
    )

    if value.startswith("/static/"):
        return ROOT_DIR / value.lstrip("/")

    if value.startswith("static/"):
        return ROOT_DIR / value

    return None


def is_valid_audio_file(
    path: Path,
) -> bool:

    return (
        path.exists()
        and path.is_file()
        and path.stat().st_size
        >= MIN_VALID_MP3_BYTES
    )


# ============================================================
# ELEVENLABS TTS
# ============================================================

def generate_mp3(
    client: ElevenLabs,
    text: str,
    output_file: Path,
):

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # File tạm.
    # Chỉ đổi thành .mp3 thật khi tạo thành công.
    temp_file = output_file.with_suffix(
        output_file.suffix + ".part"
    )

    if temp_file.exists():
        temp_file.unlink()

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        output_format=OUTPUT_FORMAT,
    )

    try:

        with temp_file.open("wb") as file:

            for chunk in audio:

                if chunk:
                    file.write(chunk)

        if not is_valid_audio_file(
            temp_file
        ):

            size = (
                temp_file.stat().st_size
                if temp_file.exists()
                else 0
            )

            fail(
                "File MP3 tao ra "
                "khong hop le: "
                f"{size} bytes"
            )

        # Tạo thành công mới thay file chính.
        temp_file.replace(
            output_file
        )

    finally:

        if temp_file.exists():
            temp_file.unlink()


# ============================================================
# LẤY 501 TỪ VỰNG HSK1
# ============================================================

def get_hsk1_vocab(cursor):

    cursor.execute(
        """
        SELECT
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tv.MaAmThanh,
            bh.SoThuTuBai,
            tvbh.ThuTu

        FROM dbo.TuVungBaiHoc AS tvbh

        INNER JOIN dbo.TuVung AS tv
            ON tvbh.MaTuVung = tv.MaTuVung

        INNER JOIN dbo.BaiHoc AS bh
            ON tvbh.MaBaiHoc = bh.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON bh.MaKhoaHoc = kh.MaKhoaHoc

        WHERE kh.MaKyHieu = ?

        ORDER BY
            bh.SoThuTuBai,
            tvbh.ThuTu,
            tv.MaTuVung;
        """,
        COURSE_CODE,
    )

    items = []

    seen = set()

    for row in cursor.fetchall():

        ma_tu_vung = int(
            row[0]
        )

        # Tránh trường hợp một từ bị
        # liên kết nhiều lần trong TuVungBaiHoc.
        if ma_tu_vung in seen:
            continue

        seen.add(
            ma_tu_vung
        )

        items.append(
            {
                "id": ma_tu_vung,

                "text":
                    clean(row[1]),

                "pinyin":
                    clean(row[2]),

                "media_id":
                    row[3],

                "lesson":
                    int(row[4]),

                "order":
                    int(row[5]),
            }
        )

    return items


# ============================================================
# LẤY 301 CHỮ HÁN HSK1
# ============================================================

def get_hsk1_hanzi(cursor):

    cursor.execute(
        """
        SELECT
            ch.MaChuHan,
            ch.KyTu,
            ch.Pinyin,
            ch.MaTep,
            bh.SoThuTuBai,
            ch.ThuTu

        FROM dbo.ChuHan AS ch

        INNER JOIN dbo.BaiHoc AS bh
            ON ch.MaBaiHoc = bh.MaBaiHoc

        INNER JOIN dbo.KhoaHoc AS kh
            ON bh.MaKhoaHoc = kh.MaKhoaHoc

        WHERE kh.MaKyHieu = ?

        ORDER BY
            bh.SoThuTuBai,
            ch.ThuTu,
            ch.MaChuHan;
        """,
        COURSE_CODE,
    )

    return [
        {
            "id":
                int(row[0]),

            "text":
                clean(row[1]),

            "pinyin":
                clean(row[2]),

            "media_id":
                row[3],

            "lesson":
                int(row[4]),

            "order":
                int(row[5]),
        }

        for row in cursor.fetchall()
    ]


# ============================================================
# LẤY MEDIA ĐÃ CÓ
# ============================================================

def get_media(
    cursor,
    media_id: int,
):

    cursor.execute(
        """
        SELECT
            MaTep,
            LoaiTep,
            DuongDanTep,
            TieuDe,
            LoiThoai

        FROM dbo.TepDaPhuongTien

        WHERE MaTep = ?;
        """,
        media_id,
    )

    return cursor.fetchone()


# ============================================================
# TÌM AUDIO TỪ VỰNG CÓ THỂ DÙNG CHUNG CHO CHỮ HÁN
# ============================================================

def find_reusable_vocab_audio(
    cursor,
    text: str,
    pinyin: str,
):
    """
    Tìm audio từ vựng đã tồn tại để dùng chung
    cho chữ Hán.

    Điều kiện bắt buộc:

    1. TuVung.ChuHan = ChuHan.KyTu
    2. Pinyin giống nhau
    3. TuVung.MaAmThanh đã có
    4. TepDaPhuongTien.LoaiTep = 'am_thanh'
    5. File MP3 thật sự tồn tại và hợp lệ

    Việc kiểm tra cả Pinyin rất quan trọng
    vì có chữ Hán đa âm.
    """

    cursor.execute(
        """
        SELECT
            tv.MaAmThanh,
            tv.PhienAm,
            t.DuongDanTep

        FROM dbo.TuVung AS tv

        INNER JOIN dbo.TepDaPhuongTien AS t
            ON tv.MaAmThanh = t.MaTep

        WHERE tv.ChuHan = ?
          AND tv.MaAmThanh IS NOT NULL
          AND t.LoaiTep = 'am_thanh'

        ORDER BY tv.MaTuVung;
        """,
        text,
    )

    expected_pinyin = normalize_pinyin(
        pinyin
    )

    # Không reuse nếu chữ Hán không có Pinyin.
    # Làm vậy để tránh dùng sai cách đọc.
    if not expected_pinyin:
        return None

    for row in cursor.fetchall():

        media_id = int(
            row[0]
        )

        vocab_pinyin = normalize_pinyin(
            row[1]
        )

        public_path = clean(
            row[2]
        )

        if not vocab_pinyin:
            continue

        # Chỉ dùng lại khi Pinyin khớp.
        if expected_pinyin != vocab_pinyin:
            continue

        audio_file = (
            project_file_from_public_path(
                public_path
            )
        )

        if (
            audio_file is not None
            and is_valid_audio_file(
                audio_file
            )
        ):
            return media_id

    return None


# ============================================================
# GẮN AUDIO TỪ VỰNG CŨ CHO CHỮ HÁN
# ============================================================

def link_existing_vocab_audio_to_hanzi(
    connection,
    cursor,
    *,
    hanzi_id: int,
    media_id: int,
):

    cursor.execute(
        """
        UPDATE dbo.ChuHan

        SET MaTep = ?

        WHERE MaChuHan = ?
          AND MaTep IS NULL;
        """,
        media_id,
        hanzi_id,
    )

    if cursor.rowcount != 1:

        connection.rollback()

        fail(
            "Khong gan duoc "
            "audio tu vung dung chung "
            f"cho ChuHan ID={hanzi_id}"
        )

    connection.commit()


# ============================================================
# INSERT MEDIA + GẮN FK
# ============================================================

def insert_and_link_media(
    connection,
    cursor,
    *,
    kind: str,
    item_id: int,
    text: str,
    public_path: str,
):

    if kind == "vocab":

        title = (
            "Phat am tu vung: "
            f"{text}"
        )

    else:

        title = (
            "Phat am chu Han: "
            f"{text}"
        )


    # --------------------------------------------------------
    # INSERT TEP DA PHUONG TIEN
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO dbo.TepDaPhuongTien
        (
            LoaiTep,
            DuongDanTep,
            TieuDe,
            LoiThoai,
            MaNguon
        )

        OUTPUT INSERTED.MaTep

        VALUES
        (
            'am_thanh',
            ?,
            ?,
            ?,
            NULL
        );
        """,
        public_path,
        title,
        text,
    )

    media_id = int(
        cursor.fetchone()[0]
    )


    # --------------------------------------------------------
    # GẮN AUDIO CHO TỪ VỰNG
    # --------------------------------------------------------

    if kind == "vocab":

        cursor.execute(
            """
            UPDATE dbo.TuVung

            SET MaAmThanh = ?

            WHERE MaTuVung = ?
              AND MaAmThanh IS NULL;
            """,
            media_id,
            item_id,
        )


    # --------------------------------------------------------
    # GẮN AUDIO CHO CHỮ HÁN
    # --------------------------------------------------------

    else:

        cursor.execute(
            """
            UPDATE dbo.ChuHan

            SET MaTep = ?

            WHERE MaChuHan = ?
              AND MaTep IS NULL;
            """,
            media_id,
            item_id,
        )


    # Nếu UPDATE không đúng 1 bản ghi
    # thì rollback để không tạo media rác.
    if cursor.rowcount != 1:

        connection.rollback()

        fail(
            "Khong cap nhat duoc FK "
            f"cho {kind} "
            f"ID={item_id}. "
            "Da ROLLBACK."
        )

    connection.commit()

    return media_id


# ============================================================
# XỬ LÝ MỘT TỪ / MỘT CHỮ
# ============================================================

def process_item(
    connection,
    cursor,
    client,
    *,
    kind: str,
    item: dict,
):

    item_id = item["id"]

    text = item["text"]

    pinyin = item["pinyin"]

    current_media_id = (
        item["media_id"]
    )


    if not text:

        fail(
            f"{kind} ID={item_id} "
            "khong co noi dung "
            "tieng Trung."
        )


    # ========================================================
    # ĐƯỜNG DẪN AUDIO MẶC ĐỊNH
    # ========================================================

    if kind == "vocab":

        output_file = (
            VOCAB_DIR
            / f"tv_{item_id:04d}.mp3"
        )

        public_path = (
            "/static/audio/hsk1/"
            "tu_vung/"
            f"tv_{item_id:04d}.mp3"
        )

    else:

        output_file = (
            HANZI_DIR
            / f"ch_{item_id:04d}.mp3"
        )

        public_path = (
            "/static/audio/hsk1/"
            "chu_han/"
            f"ch_{item_id:04d}.mp3"
        )


    print(
        f"  ID={item_id:<5} "
        f"Bai={item['lesson']:<2} "
        f"Text={text} | "
        f"Pinyin={pinyin or '-'}"
    )


    # ========================================================
    # TRƯỜNG HỢP SQL ĐÃ CÓ MEDIA
    # ========================================================

    if current_media_id is not None:

        media = get_media(
            cursor,
            int(current_media_id),
        )

        if media is None:

            fail(
                "FK MaTep/MaAmThanh="
                f"{current_media_id} "
                "khong ton tai trong "
                "TepDaPhuongTien."
            )


        if clean(media[1]) != "am_thanh":

            fail(
                "Media ID="
                f"{current_media_id} "
                "co LoaiTep="
                f"{clean(media[1])}, "
                "khong phai am_thanh."
            )


        existing_file = (
            project_file_from_public_path(
                clean(media[2])
            )
        )


        if existing_file is None:

            fail(
                "DuongDanTep hien tai "
                "khong thuoc /static "
                "cua project: "
                f"{media[2]}"
            )


        # SQL đã có link và file còn tốt
        # => bỏ qua.
        if is_valid_audio_file(
            existing_file
        ):

            print(
                "    SKIP: SQL da lien ket "
                "va file MP3 hop le "
                f"(MaTep="
                f"{current_media_id})."
            )

            return "skip_linked"


        # SQL có link nhưng file bị mất
        # => tạo lại đúng file đó.
        print(
            "    File bi thieu/"
            "khong hop le "
            "-> tao lai..."
        )


        generate_mp3(
            client,
            text,
            existing_file,
        )


        print(
            "    OK: da khoi phuc "
            f"{existing_file.name}"
        )


        return "repaired"


    # ========================================================
    # SQL CHƯA CÓ MEDIA
    # ========================================================

    # ========================================================
    # CHỮ HÁN:
    # THỬ DÙNG LẠI AUDIO TỪ VỰNG
    # ========================================================

    if kind == "hanzi":

        reusable_media_id = (
            find_reusable_vocab_audio(
                cursor,
                text,
                pinyin,
            )
        )

        if reusable_media_id is not None:

            link_existing_vocab_audio_to_hanzi(
                connection,
                cursor,
                hanzi_id=item_id,
                media_id=reusable_media_id,
            )

            print(
                "    REUSE VOCAB AUDIO: "
                f"MaTep={reusable_media_id}. "
                "Khong goi ElevenLabs."
            )

            return "reused_vocab"


    # ========================================================
    # KHÔNG CÓ AUDIO DÙNG CHUNG
    # ========================================================

    # Nếu file đã tồn tại do lần chạy trước
    # bị dừng sau khi TTS xong nhưng chưa kịp ghi SQL,
    # thì dùng lại file.
    if is_valid_audio_file(
        output_file
    ):

        print(
            "    REUSE FILE: "
            "file MP3 da ton tai, "
            "khong goi ElevenLabs lai."
        )


    else:

        print(
            "    TTS: dang tao audio "
            "bang ElevenLabs..."
        )


        generate_mp3(
            client,
            text,
            output_file,
        )


        print(
            "    OK file: "
            f"{output_file.name} "
            "("
            f"{output_file.stat().st_size}"
            " bytes)"
        )


    # ========================================================
    # GHI SQL
    # ========================================================

    try:

        media_id = (
            insert_and_link_media(
                connection,
                cursor,
                kind=kind,
                item_id=item_id,
                text=text,
                public_path=public_path,
            )
        )

    except Exception:

        connection.rollback()

        raise


    print(
        "    OK SQL: "
        "TepDaPhuongTien.MaTep="
        f"{media_id} "
        "da duoc lien ket."
    )


    return "created"


# ============================================================
# THAM SỐ CHẠY SCRIPT
# ============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Tao audio ElevenLabs "
            "cho TuVung + ChuHan HSK1, "
            "ghi TepDaPhuongTien "
            "va cap nhat FK."
        )
    )


    parser.add_argument(
        "--full",
        action="store_true",
        help=(
            "Chay toan bo "
            "501 tu vung + "
            "301 Chu Han. "
            "Mac dinh test 5 + 5."
        ),
    )


    parser.add_argument(
        "--vocab-limit",
        type=int,
        default=5,
        help=(
            "So tu vung test "
            "khi khong dung --full."
        ),
    )


    parser.add_argument(
        "--hanzi-limit",
        type=int,
        default=5,
        help=(
            "So Chu Han test "
            "khi khong dung --full."
        ),
    )


    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main():

    args = parse_args()


    print(
        "=" * 100
    )

    print(
        "11A - ELEVENLABS AUDIO HSK1"
    )

    print(
        "=" * 100
    )


    print(
        "Mode:",
        (
            "FULL"
            if args.full
            else (
                f"TEST "
                f"{args.vocab_limit} TU + "
                f"{args.hanzi_limit} CHU"
            )
        )
    )


    print(
        "Model:",
        MODEL_ID
    )


    print(
        "Output:",
        OUTPUT_FORMAT
    )


    print()


    # ========================================================
    # KIỂM TRA API KEY
    # ========================================================

    if not API_KEY:

        fail(
            "Khong tim thay "
            "ELEVENLABS_API_KEY "
            "trong .env"
        )


    if not VOICE_ID:

        fail(
            "Khong tim thay "
            "ELEVENLABS_VOICE_ID "
            "trong .env"
        )


    # ========================================================
    # TẠO FOLDER AUDIO
    # ========================================================

    VOCAB_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    HANZI_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ========================================================
    # ELEVENLABS CLIENT
    # ========================================================

    client = ElevenLabs(
        api_key=API_KEY
    )


    # ========================================================
    # SQL SERVER
    # ========================================================

    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # ------------------------------------------------
            # KIỂM TRA ĐÚNG DATABASE
            # ------------------------------------------------

            cursor.execute(
                "SELECT DB_NAME();"
            )


            db_name = clean(
                cursor.fetchone()[0]
            )


            print(
                "Database:",
                db_name
            )


            if (
                db_name.lower()
                != "hoctiengtrungdb"
            ):

                fail(
                    "Dang ket noi "
                    "nham database."
                )


            # ------------------------------------------------
            # LẤY DỮ LIỆU
            # ------------------------------------------------

            vocab = get_hsk1_vocab(
                cursor
            )


            hanzi = get_hsk1_hanzi(
                cursor
            )


            print(
                "HSK1 TuVung: "
                f"{len(vocab)} / "
                f"{EXPECTED_VOCAB}"
            )


            print(
                "HSK1 ChuHan : "
                f"{len(hanzi)} / "
                f"{EXPECTED_HANZI}"
            )


            # ------------------------------------------------
            # BẮT BUỘC ĐÚNG SỐ LƯỢNG
            # ------------------------------------------------

            if (
                len(vocab)
                != EXPECTED_VOCAB
            ):

                fail(
                    "So luong TuVung "
                    "HSK1 khong dung "
                    "501. "
                    "Dung lai de "
                    "kiem tra DB."
                )


            if (
                len(hanzi)
                != EXPECTED_HANZI
            ):

                fail(
                    "So luong ChuHan "
                    "HSK1 khong dung "
                    "301. "
                    "Dung lai de "
                    "kiem tra DB."
                )


            # ------------------------------------------------
            # MODE TEST
            # ------------------------------------------------

            if not args.full:

                vocab = vocab[
                    :
                    max(
                        0,
                        args.vocab_limit
                    )
                ]


                hanzi = hanzi[
                    :
                    max(
                        0,
                        args.hanzi_limit
                    )
                ]


            # =================================================
            # THỐNG KÊ
            # =================================================

            stats = {
                "created": 0,
                "skip_linked": 0,
                "repaired": 0,
                "reused_vocab": 0,
                "failed": 0,
            }


            # =================================================
            # 1. TỪ VỰNG
            # =================================================

            print()

            print(
                "[1] TU VUNG"
            )

            print(
                "-" * 100
            )


            for index, item in enumerate(
                vocab,
                start=1,
            ):

                print(
                    f"[{index}/"
                    f"{len(vocab)}]"
                )


                try:

                    result = (
                        process_item(
                            connection,
                            cursor,
                            client,
                            kind="vocab",
                            item=item,
                        )
                    )


                    stats[result] += 1


                except Exception as error:

                    connection.rollback()

                    stats["failed"] += 1


                    print(
                        "    LOI:",
                        error
                    )


                    raise


            # =================================================
            # 2. CHỮ HÁN
            # =================================================

            print()

            print(
                "[2] CHU HAN"
            )

            print(
                "-" * 100
            )


            for index, item in enumerate(
                hanzi,
                start=1,
            ):

                print(
                    f"[{index}/"
                    f"{len(hanzi)}]"
                )


                try:

                    result = (
                        process_item(
                            connection,
                            cursor,
                            client,
                            kind="hanzi",
                            item=item,
                        )
                    )


                    stats[result] += 1


                except Exception as error:

                    connection.rollback()

                    stats["failed"] += 1


                    print(
                        "    LOI:",
                        error
                    )


                    raise


    # ========================================================
    # KẾT QUẢ
    # ========================================================

    print()

    print(
        "=" * 100
    )

    print(
        "HOAN TAT"
    )

    print(
        "=" * 100
    )


    print(
        "Tao + lien ket moi :",
        stats["created"]
    )


    print(
        "Da co, bo qua      :",
        stats["skip_linked"]
    )


    print(
        "Dung lai audio TV  :",
        stats["reused_vocab"]
    )


    print(
        "Khoi phuc file     :",
        stats["repaired"]
    )


    print(
        "Loi                :",
        stats["failed"]
    )


    if not args.full:

        print()

        print(
            "DAY MOI LA CHE DO TEST."
        )

        print(
            "Chua chay --full "
            "neu chua kiem tra audio."
        )


# ============================================================
# CHẠY CHƯƠNG TRÌNH
# ============================================================

if __name__ == "__main__":

    try:

        main()


    except KeyboardInterrupt:

        print(
            "\nDa dung theo "
            "yeu cau nguoi dung."
        )

        raise SystemExit(130)


    except Exception as error:

        print(
            "\nCHUONG TRINH "
            "DUNG VI LOI:"
        )

        print(
            error
        )

        raise SystemExit(1)