from pathlib import Path
import sys


# =========================================================
# THU MUC GOC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database import get_connection


# =========================================================
# VI DU TIENG TRUNG
#
# Luu y:
# - Quy tac goc van giu MaNguon = 5
# - Cac vi du duoi day la vi du minh hoa hoc tap
#   do do an bo sung.
# - Khong coi day la noi dung trich nguyen van tu nguon.
# =========================================================
RULE_EXAMPLES = {
    1: {
        "name": "Thanh 1 - Âm bình (阴平)",
        "chinese": "妈",
    },

    2: {
        "name": "Thanh 2 - Dương bình (阳平)",
        "chinese": "麻",
    },

    3: {
        "name": "Thanh 3 - Thượng thanh (上声)",
        "chinese": "马",
    },

    4: {
        "name": "Thanh 4 - Khứ thanh (去声)",
        "chinese": "骂",
    },

    5: {
        "name": "Thanh nhẹ (轻声)",
        "chinese": "吗",
    },

    6: {
        "name": "Cách viết iou, uei, uen sau thanh mẫu",
        "chinese": "六、贵、轮",
    },

    7: {
        "name": "Cách viết âm tiết bắt đầu bằng i",
        "chinese": "一、牙、也、要、有、眼、音、羊、英、用",
    },

    8: {
        "name": "Cách viết âm tiết bắt đầu bằng u",
        "chinese": "五、娃、我、外、位、万、王、文、翁",
    },

    9: {
        "name": "Cách viết nhóm ü khi không có thanh mẫu",
        "chinese": "鱼、月、元、云",
    },

    10: {
        "name": "Cách viết ü sau j, q, x",
        "chinese": "居、去、许",
    },

    11: {
        "name": "Dấu cách âm (隔音符号)",
        "chinese": "皮袄",
    },
}


# =========================================================
# MAIN
# =========================================================
def main():

    conn = None

    try:

        print("=" * 90)
        print(
            "BO SUNG VI DU TIENG TRUNG "
            "CHO QUY TAC PHAT AM"
        )
        print("=" * 90)

        conn = get_connection()
        conn.autocommit = False

        cursor = conn.cursor()

        # -------------------------------------------------
        # 1. DOC 11 QUY TAC
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaQuyTac,
                TenQuyTac,
                LoaiQuyTac,
                NoiDung,
                ViDuTiengTrung,
                ViDuPinyin,
                NghiaTiengViet,
                MaNguon,
                ThuTu,
                TrangThai
            FROM dbo.QuyTacPhatAm
            ORDER BY ThuTu
            """
        )

        rows = cursor.fetchall()

        print()
        print(
            "Tong quy tac hien tai:",
            len(rows)
        )

        if len(rows) != 11:

            raise RuntimeError(
                "QuyTacPhatAm phai co dung "
                f"11 dong. Thuc te: {len(rows)}"
            )

        # -------------------------------------------------
        # 2. KIEM TRA ID 1 -> 11
        # -------------------------------------------------
        db_ids = {
            row.MaQuyTac
            for row in rows
        }

        expected_ids = set(
            RULE_EXAMPLES.keys()
        )

        if db_ids != expected_ids:

            raise RuntimeError(
                "Danh sach MaQuyTac "
                "khong khop 1 -> 11."
            )

        # -------------------------------------------------
        # 3. KIEM TRA TEN QUY TAC
        #
        # Tranh cap nhat sai dong neu DB thay doi.
        # -------------------------------------------------
        for row in rows:

            expected_name = (
                RULE_EXAMPLES[
                    row.MaQuyTac
                ]["name"]
            )

            if row.TenQuyTac != expected_name:

                raise RuntimeError(
                    "Ten quy tac khong khop.\n"
                    f"MaQuyTac: {row.MaQuyTac}\n"
                    f"DB: {row.TenQuyTac}\n"
                    f"Script: {expected_name}"
                )

        # -------------------------------------------------
        # 4. KIEM TRA PINYIN + NGHIA VIET
        # -------------------------------------------------
        missing_existing_data = []

        for row in rows:

            if (
                row.ViDuPinyin is None
                or not str(
                    row.ViDuPinyin
                ).strip()
            ):

                missing_existing_data.append(
                    f"{row.MaQuyTac}: "
                    "thieu ViDuPinyin"
                )

            if (
                row.NghiaTiengViet is None
                or not str(
                    row.NghiaTiengViet
                ).strip()
            ):

                missing_existing_data.append(
                    f"{row.MaQuyTac}: "
                    "thieu NghiaTiengViet"
                )

            if row.MaNguon != 5:

                missing_existing_data.append(
                    f"{row.MaQuyTac}: "
                    f"MaNguon={row.MaNguon}, "
                    "khong phai 5"
                )

        if missing_existing_data:

            print()

            for error in missing_existing_data:
                print("-", error)

            raise RuntimeError(
                "Du lieu quy tac goc "
                "chua hop le."
            )

        # -------------------------------------------------
        # 5. IN DU LIEU SE CAP NHAT
        # -------------------------------------------------
        print()
        print("-" * 90)
        print("DU LIEU SE CAP NHAT")
        print("-" * 90)

        for row in rows:

            example = (
                RULE_EXAMPLES[
                    row.MaQuyTac
                ]["chinese"]
            )

            print()
            print(
                f"{row.MaQuyTac:02d}"
                f" | {row.TenQuyTac}"
            )

            print(
                "   Trung :",
                example
            )

            print(
                "   Pinyin:",
                row.ViDuPinyin
            )

            print(
                "   Nghia :",
                row.NghiaTiengViet
            )

        # -------------------------------------------------
        # 6. UPDATE
        #
        # Dua TrangThai ve ban_nhap
        # vi da bo sung noi dung hoc moi.
        # -------------------------------------------------
        updated = 0

        for row in rows:

            example = (
                RULE_EXAMPLES[
                    row.MaQuyTac
                ]["chinese"]
            )

            cursor.execute(
                """
                UPDATE dbo.QuyTacPhatAm
                SET
                    ViDuTiengTrung = ?,
                    TrangThai = 'ban_nhap'
                WHERE MaQuyTac = ?
                """,
                example,
                row.MaQuyTac,
            )

            updated += (
                cursor.rowcount
            )

        if updated != 11:

            raise RuntimeError(
                "So dong UPDATE khong dung 11. "
                f"Thuc te: {updated}"
            )

        # -------------------------------------------------
        # 7. VERIFY
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                COUNT(*) AS Tong,

                SUM(
                    CASE
                        WHEN ViDuTiengTrung IS NULL
                          OR LTRIM(
                              RTRIM(
                                  ViDuTiengTrung
                              )
                          ) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuViDuTrung,

                SUM(
                    CASE
                        WHEN ViDuPinyin IS NULL
                          OR LTRIM(
                              RTRIM(
                                  ViDuPinyin
                              )
                          ) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuPinyin,

                SUM(
                    CASE
                        WHEN NghiaTiengViet IS NULL
                          OR LTRIM(
                              RTRIM(
                                  NghiaTiengViet
                              )
                          ) = N''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuNghiaViet,

                SUM(
                    CASE
                        WHEN TrangThai = 'ban_nhap'
                        THEN 1
                        ELSE 0
                    END
                ) AS BanNhap,

                SUM(
                    CASE
                        WHEN MaTep IS NULL
                        THEN 1
                        ELSE 0
                    END
                ) AS ChuaCoAudio

            FROM dbo.QuyTacPhatAm
            """
        )

        verify = cursor.fetchone()

        if verify.Tong != 11:
            raise RuntimeError(
                "Verify Tong != 11."
            )

        if verify.ThieuViDuTrung != 0:
            raise RuntimeError(
                "Van con quy tac "
                "thieu ViDuTiengTrung."
            )

        if verify.ThieuPinyin != 0:
            raise RuntimeError(
                "Van con quy tac "
                "thieu ViDuPinyin."
            )

        if verify.ThieuNghiaViet != 0:
            raise RuntimeError(
                "Van con quy tac "
                "thieu NghiaTiengViet."
            )

        if verify.BanNhap != 11:
            raise RuntimeError(
                "TrangThai khong dung."
            )

        # -------------------------------------------------
        # 8. DOC LAI DE HIEN THI
        # -------------------------------------------------
        cursor.execute(
            """
            SELECT
                MaQuyTac,
                TenQuyTac,
                ViDuTiengTrung,
                ViDuPinyin,
                NghiaTiengViet,
                TrangThai
            FROM dbo.QuyTacPhatAm
            ORDER BY ThuTu
            """
        )

        final_rows = (
            cursor.fetchall()
        )

        # -------------------------------------------------
        # 9. COMMIT
        # -------------------------------------------------
        conn.commit()

        # -------------------------------------------------
        # 10. KET QUA
        # -------------------------------------------------
        print()
        print("=" * 90)
        print("KET QUA")
        print("=" * 90)

        for row in final_rows:

            print(
                f"{row.MaQuyTac:02d}"
                f" | {row.TenQuyTac}"
            )

            print(
                f"   {row.ViDuTiengTrung}"
                f" | {row.ViDuPinyin}"
            )

        print()
        print(
            "Tong quy tac:",
            verify.Tong
        )

        print(
            "Thieu ViDuTiengTrung:",
            verify.ThieuViDuTrung
        )

        print(
            "Thieu ViDuPinyin:",
            verify.ThieuPinyin
        )

        print(
            "Thieu NghiaTiengViet:",
            verify.ThieuNghiaViet
        )

        print(
            "TrangThai ban_nhap:",
            verify.BanNhap
        )

        print(
            "Chua co audio:",
            verify.ChuaCoAudio
        )

        print()
        print(
            "DA HOAN THIEN NOI DUNG "
            "11 QUY TAC PHAT AM."
        )

        print()
        print(
            "AUDIO SE LAM O GIAI DOAN "
            "LUYEN NGHE / PHAT AM."
        )

        print()
        print("=" * 90)
        print("HOAN TAT")
        print("=" * 90)

        cursor.close()

    except Exception as e:

        if conn:
            conn.rollback()

        print()
        print("=" * 90)
        print(
            "THAT BAI - DA ROLLBACK"
        )
        print("=" * 90)

        print(
            "Loi:",
            e
        )

        print()
        print(
            "Database khong giu "
            "du lieu dang do."
        )

    finally:

        if conn:
            conn.close()


if __name__ == "__main__":
    main()