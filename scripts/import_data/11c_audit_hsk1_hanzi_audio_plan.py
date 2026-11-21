from __future__ import annotations

import sys
from collections import defaultdict
from contextlib import closing
from pathlib import Path


# ============================================================
# ROOT PROJECT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from database import get_connection


# ============================================================
# CẤU HÌNH
# ============================================================

COURSE_CODE = "HSK1-CORE"

EXPECTED_HANZI = 301


# ============================================================
# HÀM PHỤ
# ============================================================

def clean(value) -> str:
    if value is None:
        return ""

    return str(value).strip()


def normalize_pinyin(value: str) -> str:
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
    path: Path | None,
) -> bool:

    if path is None:
        return False

    return (
        path.exists()
        and path.is_file()
        and path.stat().st_size >= 500
    )


# ============================================================
# LẤY 301 CHỮ HÁN HSK1
# ============================================================

def get_hanzi(cursor):

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
            "id": int(row[0]),
            "text": clean(row[1]),
            "pinyin": clean(row[2]),
            "media_id": row[3],
            "lesson": int(row[4]),
            "order": int(row[5]),
        }

        for row in cursor.fetchall()
    ]


# ============================================================
# AUDIO HIỆN TẠI CỦA CHỮ HÁN
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
# TÌM AUDIO TỪ VỰNG TRÙNG CHỮ + PINYIN
# ============================================================

def find_vocab_matches(
    cursor,
    text: str,
):

    cursor.execute(
        """
        SELECT
            tv.MaTuVung,
            tv.ChuHan,
            tv.PhienAm,
            tv.MaAmThanh,
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

    result = []

    for row in cursor.fetchall():

        public_path = clean(
            row[4]
        )

        audio_file = (
            project_file_from_public_path(
                public_path
            )
        )

        result.append(
            {
                "vocab_id": int(row[0]),
                "text": clean(row[1]),
                "pinyin": clean(row[2]),
                "media_id": int(row[3]),
                "public_path": public_path,
                "file_ok": is_valid_audio_file(
                    audio_file
                ),
            }
        )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 110)

    print(
        "11C - AUDIT KE HOACH AUDIO "
        "301 CHU HAN HSK1"
    )

    print("=" * 110)

    print(
        "CHE DO CHI DOC DU LIEU."
    )

    print(
        "KHONG SUA SQL."
    )

    print(
        "KHONG GOI ELEVENLABS."
    )

    print()


    with closing(
        get_connection()
    ) as connection:

        with closing(
            connection.cursor()
        ) as cursor:


            # =================================================
            # DATABASE
            # =================================================

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
                raise RuntimeError(
                    "Dang ket noi nham database."
                )


            # =================================================
            # CHỮ HÁN
            # =================================================

            hanzi = get_hanzi(
                cursor
            )

            print(
                "Tong ChuHan HSK1:",
                len(hanzi)
            )

            if len(hanzi) != EXPECTED_HANZI:

                raise RuntimeError(
                    f"ChuHan HSK1 phai la "
                    f"{EXPECTED_HANZI}, "
                    f"nhung hien co "
                    f"{len(hanzi)}."
                )


            # =================================================
            # THỐNG KÊ
            # =================================================

            linked_ok = []

            linked_broken = []

            reusable = []

            needs_tts = []

            ambiguous = []

            no_pinyin = []


            # =================================================
            # KIỂM TRA TỪNG CHỮ
            # =================================================

            for item in hanzi:

                item_id = item["id"]

                text = item["text"]

                pinyin = item["pinyin"]

                expected_pinyin = (
                    normalize_pinyin(
                        pinyin
                    )
                )


                # ---------------------------------------------
                # KHÔNG CÓ PINYIN
                # ---------------------------------------------

                if not expected_pinyin:

                    no_pinyin.append(
                        item
                    )

                    continue


                # ---------------------------------------------
                # ĐÃ CÓ MaTep
                # ---------------------------------------------

                if item["media_id"] is not None:

                    media = get_media(
                        cursor,
                        int(
                            item["media_id"]
                        ),
                    )

                    if media is None:

                        linked_broken.append(
                            {
                                **item,
                                "reason":
                                    "MaTep khong ton tai",
                            }
                        )

                        continue


                    public_path = clean(
                        media[2]
                    )

                    audio_file = (
                        project_file_from_public_path(
                            public_path
                        )
                    )


                    if (
                        clean(media[1])
                        == "am_thanh"
                        and is_valid_audio_file(
                            audio_file
                        )
                    ):

                        linked_ok.append(
                            {
                                **item,
                                "path":
                                    public_path,
                            }
                        )

                    else:

                        linked_broken.append(
                            {
                                **item,
                                "reason":
                                    (
                                        "LoaiTep/file "
                                        "khong hop le"
                                    ),
                            }
                        )

                    continue


                # ---------------------------------------------
                # CHƯA CÓ MaTep:
                # TÌM AUDIO TỪ VỰNG CÙNG CHỮ
                # ---------------------------------------------

                matches = find_vocab_matches(
                    cursor,
                    text,
                )


                # Chỉ giữ file thật sự hợp lệ
                matches = [
                    x
                    for x in matches
                    if x["file_ok"]
                ]


                # ---------------------------------------------
                # PINYIN TRÙNG CHÍNH XÁC
                # ---------------------------------------------

                exact_matches = [
                    x
                    for x in matches
                    if normalize_pinyin(
                        x["pinyin"]
                    )
                    == expected_pinyin
                ]


                if len(
                    exact_matches
                ) == 1:

                    reusable.append(
                        {
                            **item,
                            "vocab":
                                exact_matches[0],
                        }
                    )

                    continue


                # ---------------------------------------------
                # NHIỀU AUDIO CÙNG CHỮ + PINYIN
                # ---------------------------------------------

                if len(
                    exact_matches
                ) > 1:

                    media_ids = {
                        x["media_id"]
                        for x in exact_matches
                    }

                    # Nếu tất cả thực chất cùng MaTep
                    # thì vẫn an toàn.
                    if len(media_ids) == 1:

                        reusable.append(
                            {
                                **item,
                                "vocab":
                                    exact_matches[0],
                            }
                        )

                    else:

                        ambiguous.append(
                            {
                                **item,
                                "reason":
                                    (
                                        "Nhieu TuVung "
                                        "cung chu + pinyin "
                                        "nhung khac MaTep"
                                    ),
                                "matches":
                                    exact_matches,
                            }
                        )

                    continue


                # ---------------------------------------------
                # CÓ CÙNG CHỮ NHƯNG PINYIN KHÁC
                # => ĐA ÂM / KHÔNG ĐƯỢC REUSE
                # ---------------------------------------------

                if matches:

                    ambiguous.append(
                        {
                            **item,
                            "reason":
                                (
                                    "Co TuVung cung chu "
                                    "nhung Pinyin khac"
                                ),
                            "matches":
                                matches,
                        }
                    )

                    continue


                # ---------------------------------------------
                # KHÔNG CÓ AUDIO TỪ VỰNG PHÙ HỢP
                # => PHẢI TTS MỚI
                # ---------------------------------------------

                needs_tts.append(
                    item
                )


            # =================================================
            # KẾT QUẢ
            # =================================================

            print()

            print("=" * 110)

            print(
                "TONG KET"
            )

            print("=" * 110)


            print(
                "Da co audio hop le      :",
                len(linked_ok)
            )

            print(
                "Co the dung lai TuVung  :",
                len(reusable)
            )

            print(
                "Can tao audio moi       :",
                len(needs_tts)
            )

            print(
                "Can kiem tra da am      :",
                len(ambiguous)
            )

            print(
                "MaTep/file dang loi     :",
                len(linked_broken)
            )

            print(
                "Khong co Pinyin         :",
                len(no_pinyin)
            )


            total = (
                len(linked_ok)
                + len(reusable)
                + len(needs_tts)
                + len(ambiguous)
                + len(linked_broken)
                + len(no_pinyin)
            )


            print(
                "Tong da phan loai       :",
                total,
                "/",
                EXPECTED_HANZI,
            )


            # =================================================
            # DANH SÁCH REUSE
            # =================================================

            print()

            print("=" * 110)

            print(
                "A. CHU HAN CO THE "
                "DUNG LAI AUDIO TU VUNG"
            )

            print("=" * 110)


            if not reusable:

                print(
                    "(khong co)"
                )

            else:

                for item in reusable:

                    vocab = item["vocab"]

                    print(
                        f"ChuHanID={item['id']:<4} "
                        f"Bai={item['lesson']:<2} "
                        f"{item['text']} "
                        f"| {item['pinyin']:<15} "
                        f"-> "
                        f"TuVungID="
                        f"{vocab['vocab_id']:<4} "
                        f"MaTep="
                        f"{vocab['media_id']}"
                    )


            # =================================================
            # DANH SÁCH ĐA ÂM / MƠ HỒ
            # =================================================

            print()

            print("=" * 110)

            print(
                "B. CAN KIEM TRA "
                "CHU DA AM / MO HO"
            )

            print("=" * 110)


            if not ambiguous:

                print(
                    "(khong co)"
                )

            else:

                for item in ambiguous:

                    print()

                    print(
                        f"ChuHanID="
                        f"{item['id']} "
                        f"| Bai="
                        f"{item['lesson']} "
                        f"| {item['text']} "
                        f"| Pinyin can dung="
                        f"{item['pinyin']}"
                    )

                    print(
                        "  Ly do:",
                        item["reason"]
                    )

                    for match in (
                        item["matches"]
                    ):

                        print(
                            "   - "
                            f"TuVungID="
                            f"{match['vocab_id']} "
                            f"| Pinyin="
                            f"{match['pinyin']} "
                            f"| MaTep="
                            f"{match['media_id']}"
                        )


            # =================================================
            # DANH SÁCH PHẢI TẠO MỚI
            # =================================================

            print()

            print("=" * 110)

            print(
                "C. CHU HAN PHAI "
                "TAO AUDIO MOI"
            )

            print("=" * 110)


            if not needs_tts:

                print(
                    "(khong co)"
                )

            else:

                for item in needs_tts:

                    print(
                        f"ChuHanID="
                        f"{item['id']:<4} "
                        f"Bai="
                        f"{item['lesson']:<2} "
                        f"{item['text']} "
                        f"| "
                        f"{item['pinyin']}"
                    )


            # =================================================
            # LỖI
            # =================================================

            if linked_broken:

                print()

                print("=" * 110)

                print(
                    "D. MEDIA DANG LOI"
                )

                print("=" * 110)

                for item in linked_broken:

                    print(
                        f"ChuHanID="
                        f"{item['id']} "
                        f"| {item['text']} "
                        f"| MaTep="
                        f"{item['media_id']} "
                        f"| "
                        f"{item['reason']}"
                    )


            if no_pinyin:

                print()

                print("=" * 110)

                print(
                    "E. CHU HAN "
                    "KHONG CO PINYIN"
                )

                print("=" * 110)

                for item in no_pinyin:

                    print(
                        f"ChuHanID="
                        f"{item['id']} "
                        f"| {item['text']}"
                    )


            print()

            print("=" * 110)

            print(
                "AUDIT HOAN TAT - "
                "KHONG CO DU LIEU NAO "
                "BI THAY DOI"
            )

            print("=" * 110)


if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()

        print(
            "LOI:",
            error,
        )

        raise SystemExit(1)