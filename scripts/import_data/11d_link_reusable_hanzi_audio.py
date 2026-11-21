from __future__ import annotations

import sys
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

EXPECTED_REUSABLE = 197

MIN_VALID_MP3_BYTES = 500


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
        and path.stat().st_size
        >= MIN_VALID_MP3_BYTES
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
# TÌM AUDIO TỪ VỰNG CÓ CÙNG CHỮ
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
            t.LoaiTep,
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
            row[5]
        )

        audio_file = (
            project_file_from_public_path(
                public_path
            )
        )

        result.append(
            {
                "vocab_id":
                    int(row[0]),

                "text":
                    clean(row[1]),

                "pinyin":
                    clean(row[2]),

                "media_id":
                    int(row[3]),

                "type":
                    clean(row[4]),

                "public_path":
                    public_path,

                "audio_file":
                    audio_file,

                "file_ok":
                    is_valid_audio_file(
                        audio_file
                    ),
            }
        )

    return result


# ============================================================
# TÌM AUDIO REUSE AN TOÀN
# ============================================================

def find_exact_reusable_audio(
    cursor,
    *,
    text: str,
    pinyin: str,
):

    expected_pinyin = normalize_pinyin(
        pinyin
    )

    if not expected_pinyin:
        return None


    matches = find_vocab_matches(
        cursor,
        text,
    )


    exact_matches = [
        item
        for item in matches
        if (
            item["file_ok"]
            and normalize_pinyin(
                item["pinyin"]
            )
            == expected_pinyin
        )
    ]


    # Không có từ phù hợp.
    if not exact_matches:
        return None


    # Nếu có nhiều dòng nhưng cùng MaTep
    # thì vẫn là cùng một audio.
    media_ids = {
        item["media_id"]
        for item in exact_matches
    }


    if len(media_ids) != 1:
        return None


    return exact_matches[0]


# ============================================================
# KIỂM TRA MEDIA
# ============================================================

def verify_media(
    cursor,
    media_id: int,
):

    cursor.execute(
        """
        SELECT
            MaTep,
            LoaiTep,
            DuongDanTep

        FROM dbo.TepDaPhuongTien

        WHERE MaTep = ?;
        """,
        media_id,
    )

    row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            f"MaTep={media_id} "
            "khong ton tai."
        )


    if clean(row[1]) != "am_thanh":
        raise RuntimeError(
            f"MaTep={media_id} "
            "khong phai am_thanh."
        )


    audio_file = (
        project_file_from_public_path(
            clean(row[2])
        )
    )


    if not is_valid_audio_file(
        audio_file
    ):
        raise RuntimeError(
            f"MaTep={media_id} "
            "co file MP3 khong hop le."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 110)

    print(
        "11D - GAN AUDIO TU VUNG "
        "CHO CHU HAN HSK1"
    )

    print("=" * 110)

    print(
        "KHONG GOI ELEVENLABS."
    )

    print(
        "KHONG TAO MP3 MOI."
    )

    print(
        "CHI CAP NHAT ChuHan.MaTep "
        "KHI CHU + PINYIN KHOP CHINH XAC."
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
            # LẤY CHỮ HÁN
            # =================================================

            hanzi = get_hanzi(
                cursor
            )


            print(
                "Tong ChuHan HSK1:",
                len(hanzi)
            )


            if (
                len(hanzi)
                != EXPECTED_HANZI
            ):
                raise RuntimeError(
                    "So luong ChuHan "
                    "khong dung 301."
                )


            # =================================================
            # TẠO KẾ HOẠCH TRƯỚC KHI UPDATE
            # =================================================

            plan = []

            already_linked = []

            no_exact_match = []


            for item in hanzi:

                # Đã có MaTep thì không động vào.
                if item["media_id"] is not None:

                    already_linked.append(
                        item
                    )

                    continue


                reusable = (
                    find_exact_reusable_audio(
                        cursor,
                        text=item["text"],
                        pinyin=item["pinyin"],
                    )
                )


                if reusable is None:

                    no_exact_match.append(
                        item
                    )

                    continue


                plan.append(
                    {
                        "hanzi":
                            item,

                        "vocab":
                            reusable,
                    }
                )


            # =================================================
            # KIỂM TRA SỐ LƯỢNG
            # =================================================

            print()

            print("=" * 110)

            print(
                "KE HOACH TRUOC KHI UPDATE"
            )

            print("=" * 110)


            print(
                "Da co MaTep          :",
                len(already_linked)
            )

            print(
                "Se dung lai TuVung   :",
                len(plan)
            )

            print(
                "Chua xu ly           :",
                len(no_exact_match)
            )


            total = (
                len(already_linked)
                + len(plan)
                + len(no_exact_match)
            )


            print(
                "Tong                 :",
                total,
                "/",
                EXPECTED_HANZI,
            )


            if (
                len(plan)
                != EXPECTED_REUSABLE
            ):
                raise RuntimeError(
                    "So luong audio co the "
                    "reuse khong con la 197. "
                    f"Hien tai = {len(plan)}. "
                    "DUNG LAI, KHONG UPDATE."
                )


            if total != EXPECTED_HANZI:
                raise RuntimeError(
                    "Tong phan loai "
                    "khong bang 301."
                )


            # =================================================
            # HIỆN DANH SÁCH SẼ UPDATE
            # =================================================

            print()

            print("=" * 110)

            print(
                "BAT DAU GAN 197 AUDIO"
            )

            print("=" * 110)


            linked_count = 0


            try:

                for index, entry in enumerate(
                    plan,
                    start=1,
                ):

                    hanzi_item = (
                        entry["hanzi"]
                    )

                    vocab_item = (
                        entry["vocab"]
                    )


                    media_id = int(
                        vocab_item[
                            "media_id"
                        ]
                    )


                    # Kiểm tra lần cuối.
                    verify_media(
                        cursor,
                        media_id,
                    )


                    print(
                        f"[{index}/"
                        f"{len(plan)}] "
                        f"ChuHanID="
                        f"{hanzi_item['id']:<4} "
                        f"Bai="
                        f"{hanzi_item['lesson']:<2} "
                        f"{hanzi_item['text']} "
                        f"| "
                        f"{hanzi_item['pinyin']:<12} "
                        f"-> "
                        f"TuVungID="
                        f"{vocab_item['vocab_id']:<4} "
                        f"MaTep="
                        f"{media_id}"
                    )


                    cursor.execute(
                        """
                        UPDATE dbo.ChuHan

                        SET MaTep = ?

                        WHERE MaChuHan = ?
                          AND MaTep IS NULL;
                        """,
                        media_id,
                        hanzi_item["id"],
                    )


                    if cursor.rowcount != 1:

                        raise RuntimeError(
                            "UPDATE that bai tai "
                            f"ChuHanID="
                            f"{hanzi_item['id']}."
                        )


                    linked_count += 1


                # =================================================
                # KIỂM TRA TRƯỚC COMMIT
                # =================================================

                if (
                    linked_count
                    != EXPECTED_REUSABLE
                ):
                    raise RuntimeError(
                        "So luong UPDATE "
                        "khong du 197."
                    )


                connection.commit()


            except Exception:

                connection.rollback()

                raise


            # =================================================
            # KIỂM TRA SAU COMMIT
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)

                FROM dbo.ChuHan AS ch

                INNER JOIN dbo.BaiHoc AS bh
                    ON ch.MaBaiHoc =
                       bh.MaBaiHoc

                INNER JOIN dbo.KhoaHoc AS kh
                    ON bh.MaKhoaHoc =
                       kh.MaKhoaHoc

                WHERE kh.MaKyHieu = ?
                  AND ch.MaTep IS NOT NULL;
                """,
                COURSE_CODE,
            )


            total_linked_after = int(
                cursor.fetchone()[0]
            )


            print()

            print("=" * 110)

            print(
                "HOAN TAT 11D"
            )

            print("=" * 110)


            print(
                "Audio vua dung lai    :",
                linked_count
            )

            print(
                "ChuHan co MaTep       :",
                total_linked_after,
                "/",
                EXPECTED_HANZI,
            )

            print(
                "ChuHan con thieu      :",
                (
                    EXPECTED_HANZI
                    - total_linked_after
                ),
            )


            if total_linked_after != 202:

                print()

                print(
                    "CANH BAO:"
                )

                print(
                    "Sau 11D du kien "
                    "202/301 ChuHan "
                    "co MaTep."
                )

                print(
                    "Hien tai:",
                    total_linked_after,
                )


            print()

            print(
                "KHONG CO CUOC GOI "
                "ELEVENLABS NAO "
                "TRONG BUOC 11D."
            )


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