from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# THANH MAU - NOI DUNG HOC DO DO AN BIEN SOAN
# =========================================================
INITIALS = {
    "b": (
        "Âm hai môi, không bật hơi; đọc ngắn và nhẹ.",
        "bā (八)"
    ),
    "p": (
        "Âm hai môi, bật hơi rõ.",
        "pà (怕)"
    ),
    "m": (
        "Âm mũi hai môi, gần âm m trong tiếng Việt.",
        "mā (妈)"
    ),
    "f": (
        "Môi dưới chạm nhẹ răng trên, luồng hơi đi qua khe hẹp.",
        "fàn (饭)"
    ),
    "d": (
        "Đầu lưỡi chạm lợi trên, không bật hơi.",
        "dà (大)"
    ),
    "t": (
        "Đầu lưỡi chạm lợi trên, bật hơi rõ.",
        "tā (他)"
    ),
    "n": (
        "Âm mũi đầu lưỡi, gần âm n tiếng Việt.",
        "nǐ (你)"
    ),
    "l": (
        "Đầu lưỡi chạm lợi trên, hơi thoát hai bên lưỡi.",
        "lái (来)"
    ),
    "g": (
        "Âm phát ở phía sau khoang miệng, không bật hơi.",
        "gē (哥)"
    ),
    "k": (
        "Âm phát ở phía sau khoang miệng, bật hơi rõ.",
        "kàn (看)"
    ),
    "h": (
        "Hơi đi qua khe hẹp ở phía sau khoang miệng; mạnh hơn h tiếng Việt.",
        "hǎo (好)"
    ),
    "j": (
        "Mặt lưỡi trước nâng gần ngạc cứng, không bật hơi.",
        "jiā (家)"
    ),
    "q": (
        "Mặt lưỡi trước nâng gần ngạc cứng, bật hơi rõ.",
        "qù (去)"
    ),
    "x": (
        "Mặt lưỡi trước nâng gần ngạc cứng, hơi ma sát nhẹ.",
        "xiǎo (小)"
    ),
    "zh": (
        "Đầu lưỡi cong nhẹ về phía sau, âm tắc-xát không bật hơi.",
        "zhè (这)"
    ),
    "ch": (
        "Đầu lưỡi cong nhẹ về phía sau, âm tắc-xát bật hơi.",
        "chī (吃)"
    ),
    "sh": (
        "Đầu lưỡi cong nhẹ về phía sau, tạo âm ma sát.",
        "shì (是)"
    ),
    "r": (
        "Đầu lưỡi cong nhẹ về phía sau; âm ma sát/hữu thanh đặc trưng tiếng Phổ thông.",
        "rén (人)"
    ),
    "z": (
        "Đầu lưỡi gần lợi trên, âm tắc-xát không bật hơi.",
        "zǎo (早)"
    ),
    "c": (
        "Đầu lưỡi gần lợi trên, âm tắc-xát bật hơi.",
        "cài (菜)"
    ),
    "s": (
        "Đầu lưỡi gần lợi trên, tạo âm ma sát s.",
        "sān (三)"
    ),
}


# =========================================================
# 35 VAN MAU
# =========================================================
FINALS = {
    "a": (
        "Mở miệng khá rộng, phát âm a rõ.",
        "mā (妈)"
    ),
    "o": (
        "Môi tròn, phát âm o.",
        "bō (波)"
    ),
    "e": (
        "Lưỡi hơi lùi về sau; đây không phải âm e tiếng Việt.",
        "hē (喝)"
    ),
    "ai": (
        "Bắt đầu từ a rồi chuyển nhanh sang i.",
        "lái (来)"
    ),
    "ei": (
        "Bắt đầu ở âm giữa rồi chuyển sang i.",
        "hēi (黑)"
    ),
    "ao": (
        "Bắt đầu từ a rồi chuyển sang âm tròn phía sau.",
        "hǎo (好)"
    ),
    "ou": (
        "Bắt đầu từ o rồi chuyển dần về u.",
        "dōu (都)"
    ),
    "an": (
        "Vận mẫu a kết thúc bằng âm mũi n.",
        "kàn (看)"
    ),
    "en": (
        "Âm giữa kết thúc bằng âm mũi n.",
        "hěn (很)"
    ),
    "ang": (
        "Vận mẫu a kết thúc bằng âm mũi ng.",
        "máng (忙)"
    ),
    "eng": (
        "Âm giữa kết thúc bằng âm mũi ng.",
        "lěng (冷)"
    ),
    "ong": (
        "Môi tròn, kết thúc bằng âm mũi ng.",
        "dōng (东)"
    ),

    "i": (
        "Âm i. Sau z, c, s, zh, ch, sh, r cách phát âm sẽ thay đổi.",
        "nǐ (你)"
    ),
    "ia": (
        "Chuyển nhanh từ i sang a.",
        "jiā (家)"
    ),
    "ie": (
        "Chuyển từ i sang âm e/ê ngắn.",
        "xiè (谢)"
    ),
    "iao": (
        "Tổ hợp i + ao, phát âm liền mạch.",
        "xiǎo (小)"
    ),
    "iu": (
        "Dạng viết rút gọn của iou khi đứng sau thanh mẫu.",
        "liù (六)"
    ),
    "ian": (
        "Tổ hợp i + an; đọc liền thành một vận mẫu.",
        "tiān (天)"
    ),
    "in": (
        "Âm i kết thúc bằng âm mũi n.",
        "xīn (新)"
    ),
    "iang": (
        "Tổ hợp i + ang.",
        "xiǎng (想)"
    ),
    "ing": (
        "Âm i kết thúc bằng âm mũi ng.",
        "qǐng (请)"
    ),
    "iong": (
        "Tổ hợp i + ong, môi tròn khi phát âm phần cuối.",
        "xiōng (兄)"
    ),

    "u": (
        "Âm u với môi tròn.",
        "bù (不)"
    ),
    "ua": (
        "Chuyển từ u sang a.",
        "huā (花)"
    ),
    "uo": (
        "Chuyển từ u sang o.",
        "guó (国)"
    ),
    "uai": (
        "Tổ hợp u + ai.",
        "kuài (快)"
    ),
    "ui": (
        "Dạng viết rút gọn của uei khi đứng sau thanh mẫu.",
        "shuǐ (水)"
    ),
    "uan": (
        "Tổ hợp u + an.",
        "guān (关)"
    ),
    "un": (
        "Dạng viết rút gọn của uen khi đứng sau thanh mẫu.",
        "chūn (春)"
    ),
    "uang": (
        "Tổ hợp u + ang.",
        "huáng (黄)"
    ),
    "ueng": (
        "Tổ hợp u + eng; khi đứng độc lập thường được viết với w.",
        "wēng (翁)"
    ),

    "ü": (
        "Giữ vị trí lưỡi gần âm i nhưng làm tròn môi như khi đọc u.",
        "nǚ (女)"
    ),
    "üe": (
        "Bắt đầu bằng ü rồi chuyển sang e; sau j, q, x, y dấu hai chấm thường được bỏ.",
        "xué (学)"
    ),
    "üan": (
        "Tổ hợp ü + an; sau j, q, x, y dấu hai chấm được lược khi viết.",
        "yuán (元)"
    ),
    "ün": (
        "Âm ü kết thúc bằng n; sau j, q, x, y dấu hai chấm được lược khi viết.",
        "yún (云)"
    ),
}


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 80)
        print("BO SUNG NOI DUNG HOC CHO BANG PINYIN")
        print("=" * 80)

        conn = get_connection()
        conn.autocommit = False

        cursor = conn.cursor()

        # -------------------------------------------------
        # 1. DOC DU LIEU HIEN TAI
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaPinyin,
                LoaiAm,
                KyHieu,
                CachDoc,
                ViDu,
                MaNguon,
                ThuTu,
                TrangThai
            FROM dbo.BangPinyin
            ORDER BY LoaiAm, ThuTu
            """
        )

        rows = cursor.fetchall()

        print()
        print("Tong BangPinyin hien tai:", len(rows))

        if len(rows) != 56:
            raise RuntimeError(
                "BangPinyin phai co 56 dong truoc khi cap nhat. "
                f"Thuc te: {len(rows)}"
            )

        # -------------------------------------------------
        # 2. KIEM TRA SO LUONG
        # -------------------------------------------------
        initials_db = {
            row.KyHieu
            for row in rows
            if row.LoaiAm == "thanh_mau"
        }

        finals_db = {
            row.KyHieu
            for row in rows
            if row.LoaiAm == "van_mau"
        }

        compound_db = {
            row.KyHieu
            for row in rows
            if row.LoaiAm == "am_ghep"
        }

        print(
            "Thanh mau:",
            len(initials_db)
        )

        print(
            "Van mau:",
            len(finals_db)
        )

        print(
            "Am ghep:",
            len(compound_db)
        )

        # -------------------------------------------------
        # 3. KIEM TRA DANH SACH 21 THANH MAU
        # -------------------------------------------------
        expected_initials = set(
            INITIALS.keys()
        )

        if initials_db != expected_initials:

            print()
            print(
                "Thanh mau trong DB:",
                sorted(initials_db)
            )

            print(
                "Thanh mau script:",
                sorted(expected_initials)
            )

            raise RuntimeError(
                "Danh sach thanh mau khong khop."
            )

        # -------------------------------------------------
        # 4. KIEM TRA DANH SACH 35 VAN MAU
        # -------------------------------------------------
        expected_finals = set(
            FINALS.keys()
        )

        if finals_db != expected_finals:

            print()
            print(
                "Van mau trong DB:",
                sorted(finals_db)
            )

            print(
                "Van mau script:",
                sorted(expected_finals)
            )

            print()
            print(
                "Thieu trong script:",
                sorted(
                    finals_db
                    - expected_finals
                )
            )

            print(
                "Thua trong script:",
                sorted(
                    expected_finals
                    - finals_db
                )
            )

            raise RuntimeError(
                "Danh sach van mau khong khop. "
                "CHUA CAP NHAT DATABASE."
            )

        # -------------------------------------------------
        # 5. KHONG TU Y TAO AM GHEP
        # -------------------------------------------------
        if compound_db:

            raise RuntimeError(
                "DB hien da co am_ghep. "
                "Can kiem tra rieng truoc khi cap nhat."
            )

        # -------------------------------------------------
        # 6. KIEM TRA NGUON
        # -------------------------------------------------
        invalid_source = [
            row
            for row in rows
            if row.MaNguon != 5
        ]

        if invalid_source:

            raise RuntimeError(
                "Co BangPinyin khong dung MaNguon=5."
            )

        # -------------------------------------------------
        # 7. CAP NHAT
        #
        # Dua ve ban_nhap vi CachDoc + ViDu
        # la noi dung hoc vua duoc bo sung.
        # -------------------------------------------------
        updated = 0

        for row in rows:

            if row.LoaiAm == "thanh_mau":

                cach_doc, vi_du = (
                    INITIALS[
                        row.KyHieu
                    ]
                )

            elif row.LoaiAm == "van_mau":

                cach_doc, vi_du = (
                    FINALS[
                        row.KyHieu
                    ]
                )

            else:
                continue

            cursor.execute(
                """
                UPDATE dbo.BangPinyin
                SET
                    CachDoc = ?,
                    ViDu = ?,
                    TrangThai = 'ban_nhap'
                WHERE MaPinyin = ?
                """,
                cach_doc,
                vi_du,
                row.MaPinyin,
            )

            updated += 1

        if updated != 56:

            raise RuntimeError(
                "So dong UPDATE khong dung 56."
            )

        # -------------------------------------------------
        # 8. VERIFY
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                COUNT(*) AS Tong,
                SUM(
                    CASE
                        WHEN CachDoc IS NULL
                          OR LTRIM(RTRIM(CachDoc)) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuCachDoc,

                SUM(
                    CASE
                        WHEN ViDu IS NULL
                          OR LTRIM(RTRIM(ViDu)) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuViDu,

                SUM(
                    CASE
                        WHEN TrangThai = 'ban_nhap'
                        THEN 1
                        ELSE 0
                    END
                ) AS BanNhap

            FROM dbo.BangPinyin
            """
        )

        verify = cursor.fetchone()

        if verify.Tong != 56:
            raise RuntimeError(
                "Verify Tong != 56."
            )

        if verify.ThieuCachDoc != 0:
            raise RuntimeError(
                "Van con Pinyin thieu CachDoc."
            )

        if verify.ThieuViDu != 0:
            raise RuntimeError(
                "Van con Pinyin thieu ViDu."
            )

        if verify.BanNhap != 56:
            raise RuntimeError(
                "TrangThai sau cap nhat khong dung."
            )

        # -------------------------------------------------
        # 9. COMMIT
        # -------------------------------------------------
        conn.commit()

        print()
        print("=" * 80)
        print("KET QUA")
        print("=" * 80)

        print(
            "Tong BangPinyin:",
            verify.Tong
        )

        print(
            "Thieu CachDoc:",
            verify.ThieuCachDoc
        )

        print(
            "Thieu ViDu:",
            verify.ThieuViDu
        )

        print(
            "TrangThai ban_nhap:",
            verify.BanNhap
        )

        print()
        print(
            "DA BO SUNG NOI DUNG CHO "
            "21 THANH MAU + 35 VAN MAU."
        )

        print()
        print(
            "CHUA TAO am_ghep."
        )

        print(
            "CHUA SUA QuyTacPhatAm."
        )

        print()
        print("=" * 80)
        print("HOAN TAT")
        print("=" * 80)

        cursor.close()

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 80)
        print("THAT BAI - DA ROLLBACK")
        print("=" * 80)

        print(
            "Loi:",
            e
        )

        print()
        print(
            "Database khong giu cap nhat dang do."
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()