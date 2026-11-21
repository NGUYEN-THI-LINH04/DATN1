from pathlib import Path
import csv
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
# CONFIG
# =========================================================
SOURCE_ID = 1004
SOURCE_NAME = "GF0025-2021 - Ngữ pháp HSK"

OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "hsk1_48_grammar_standard.csv"
)


# =========================================================
# 48 MUC NGU PHAP CAP 1
#
# Chi luu PHAM VI / TEN MUC CHUAN.
#
# KHONG tu tao:
# - MoTa
# - CachDung
# - ViDuTiengTrung
# - ViDuPinyin
# - ViDuTiengViet
#
# Nhung noi dung hoc tap do se duoc
# bien soan + review o buoc sau.
# =========================================================
GRAMMAR_ITEMS = [

    # -----------------------------------------------------
    # I. TU LOAI - 词类
    # -----------------------------------------------------
    (
        1,
        "词类",
        "名词",
        "方位名词",
        (
            "方位名词：上、下、里、外、前、后、左、右、"
            "东、南、西、北；上边、下边、里边、外边、"
            "前边、后边、左边、右边、东边、南边、西边、北边"
        ),
    ),

    (
        2,
        "词类",
        "动词",
        "能愿动词",
        "能愿动词：会、能",
    ),

    (
        3,
        "词类",
        "动词",
        "能愿动词",
        "能愿动词：想、要",
    ),

    (
        4,
        "词类",
        "代词",
        "疑问代词",
        (
            "疑问代词：多、多少、几、哪、哪儿、哪里、"
            "哪些、什么、谁、怎么"
        ),
    ),

    (
        5,
        "词类",
        "代词",
        "人称代词",
        (
            "人称代词：我、你、您、他、她、"
            "我们、你们、他们、她们"
        ),
    ),

    (
        6,
        "词类",
        "代词",
        "指示代词",
        (
            "指示代词：这、那、这儿、那儿、这里、那里、"
            "这些、那些、别的、有的"
        ),
    ),

    (
        7,
        "词类",
        "数词",
        "数词",
        (
            "数词：一、二/两、三、四、五、六、七、八、九、"
            "零；十、百；半"
        ),
    ),

    (
        8,
        "词类",
        "量词",
        "名量词",
        "名量词：杯、本、个、家、间、口、块、页",
    ),

    (
        9,
        "词类",
        "副词",
        "程度副词",
        "程度副词：非常、很、太、真、最",
    ),

    (
        10,
        "词类",
        "副词",
        "范围、协同副词",
        "范围、协同副词：都、一块儿、一起",
    ),

    (
        11,
        "词类",
        "副词",
        "时间副词",
        "时间副词：马上、先、有时、在、正、正在",
    ),

    (
        12,
        "词类",
        "副词",
        "频率、重复副词",
        "频率、重复副词：常、常常、再",
    ),

    (
        13,
        "词类",
        "副词",
        "关联副词",
        "关联副词：还、也",
    ),

    (
        14,
        "词类",
        "副词",
        "否定副词",
        "否定副词：别、不、没、没有",
    ),

    (
        15,
        "词类",
        "介词",
        "介词",
        "介词：从",
    ),

    (
        16,
        "词类",
        "介词",
        "介词",
        "介词：在",
    ),

    (
        17,
        "词类",
        "介词",
        "介词",
        "介词：跟、和",
    ),

    (
        18,
        "词类",
        "介词",
        "介词",
        "介词：比",
    ),

    (
        19,
        "词类",
        "连词",
        "连接词或短语",
        "连接词或短语：跟、还是、和",
    ),

    (
        20,
        "词类",
        "助词",
        "结构助词",
        "结构助词：的、地",
    ),

    (
        21,
        "词类",
        "助词",
        "动态助词",
        "动态助词：了",
    ),

    (
        22,
        "词类",
        "助词",
        "语气助词",
        "语气助词：吧、了、吗、呢",
    ),

    # -----------------------------------------------------
    # II. CUM TU - 短语
    # -----------------------------------------------------
    (
        23,
        "短语",
        "结构类型",
        "数量短语",
        "数量短语",
    ),

    # -----------------------------------------------------
    # III. THANH PHAN CAU - 句子成分
    # -----------------------------------------------------
    (
        24,
        "句子成分",
        "主语",
        "主语",
        "名词、代词或名词性短语作主语",
    ),

    (
        25,
        "句子成分",
        "谓语",
        "谓语",
        (
            "动词或动词性短语、"
            "形容词或形容词性短语作谓语"
        ),
    ),

    (
        26,
        "句子成分",
        "宾语",
        "宾语",
        "名词、代词或名词性短语作宾语",
    ),

    (
        27,
        "句子成分",
        "定语",
        "定语",
        "名词性词语、形容词性词语、数量短语作定语",
    ),

    (
        28,
        "句子成分",
        "状语",
        "状语",
        (
            "副词、形容词作状语；"
            "表示时间、处所的词语作状语"
        ),
    ),

    # -----------------------------------------------------
    # IV. KIEU CAU - 句子的类型
    # -----------------------------------------------------
    (
        29,
        "句子的类型",
        "句型",
        "主谓句",
        "主谓句1：动词谓语句",
    ),

    (
        30,
        "句子的类型",
        "句型",
        "主谓句",
        "主谓句2：形容词谓语句",
    ),

    (
        31,
        "句子的类型",
        "句型",
        "非主谓句",
        "非主谓句",
    ),

    (
        32,
        "句子的类型",
        "句类",
        "陈述句",
        "陈述句",
    ),

    (
        33,
        "句子的类型",
        "句类",
        "疑问句",
        "疑问句",
    ),

    (
        34,
        "句子的类型",
        "句类",
        "祈使句",
        "祈使句",
    ),

    (
        35,
        "句子的类型",
        "句类",
        "感叹句",
        "感叹句",
    ),

    (
        36,
        "句子的类型",
        "特殊句型",
        "“是”字句",
        "“是”字句",
    ),

    (
        37,
        "句子的类型",
        "特殊句型",
        "“有”字句",
        "“有”字句1",
    ),

    (
        38,
        "句子的类型",
        "特殊句型",
        "比较句",
        "比较句1",
    ),

    (
        39,
        "句子的类型",
        "复句",
        "并列复句",
        "并列复句",
    ),

    # -----------------------------------------------------
    # V. TRANG THAI CUA HANH DONG - 动作的态
    # -----------------------------------------------------
    (
        40,
        "动作的态",
        "变化态",
        "变化态",
        "变化态：用语气助词“了2”表示",
    ),

    (
        41,
        "动作的态",
        "完成态",
        "完成态",
        "完成态：用动态助词“了1”表示",
    ),

    (
        42,
        "动作的态",
        "进行态",
        "进行态",
        "进行态",
    ),

    # -----------------------------------------------------
    # VI. BIEU DAT DAC BIET - 特殊表达法
    # -----------------------------------------------------
    (
        43,
        "特殊表达法",
        "数的表示法",
        "钱数表示法",
        "钱数表示法",
    ),

    (
        44,
        "特殊表达法",
        "时间表示法",
        "时间表示法",
        "时间表示法",
    ),

    # -----------------------------------------------------
    # VII. PHUONG PHAP DAT CAU HOI - 提问的方法
    # -----------------------------------------------------
    (
        45,
        "提问的方法",
        "提问",
        "用“吗”提问",
        "用“吗”提问",
    ),

    (
        46,
        "提问的方法",
        "提问",
        "用疑问代词提问",
        (
            "用“多、多少、几、哪、哪儿、哪里、哪些、"
            "什么、谁、怎么”提问"
        ),
    ),

    (
        47,
        "提问的方法",
        "提问",
        "用“还是”提问",
        "用“还是”提问",
    ),

    (
        48,
        "提问的方法",
        "提问",
        "正反问",
        "用正反问形式提问",
    ),
]


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 110)
    print(
        "09H4 - TAO FILE NGUON "
        "48 NGU PHAP HSK1 CHUAN"
    )
    print("=" * 110)

    print()
    print("CHE DO:")
    print("  CHI SELECT DATABASE")
    print("  TAO FILE CSV")
    print("  KHONG INSERT NGUPHAP")
    print("  KHONG UPDATE NGUPHAP")
    print("  KHONG DELETE")
    print("  KHONG SUA 7 NGU PHAP BAI 1")

    # =====================================================
    # 1. KIEM TRA DANH SACH TRONG SCRIPT
    # =====================================================
    print()
    print("[1] KIEM TRA 48 MUC TRONG SCRIPT")
    print("-" * 110)

    if len(GRAMMAR_ITEMS) != 48:

        fail(
            "GRAMMAR_ITEMS phai co dung 48 muc. "
            f"Thuc te: {len(GRAMMAR_ITEMS)}"
        )

    order_numbers = [
        item[0]
        for item in GRAMMAR_ITEMS
    ]

    expected_numbers = list(
        range(1, 49)
    )

    if order_numbers != expected_numbers:

        fail(
            "So thu tu ngu phap "
            "khong lien tuc 1 -> 48."
        )

    contents = [
        clean(item[4])
        for item in GRAMMAR_ITEMS
    ]

    if any(
        not content
        for content in contents
    ):

        fail(
            "Co muc NoiDungChuan bi trong."
        )

    print(
        "Tong muc:",
        len(GRAMMAR_ITEMS),
    )

    print(
        "So thu tu: 1 -> 48 OK"
    )

    print(
        "NoiDungChuan trong: 0"
    )

    # =====================================================
    # 2. VERIFY SOURCE 1004
    # =====================================================
    print()
    print("[2] VERIFY MaNguon=1004")
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
                        MaNguon,
                        Ten,
                        LienKetNguon,
                        GhiChu
                    FROM dbo.NguonDuLieu
                    WHERE MaNguon = ?;
                    """,
                    SOURCE_ID,
                )

                row = cursor.fetchone()

                if row is None:

                    fail(
                        "Khong tim thay "
                        "MaNguon=1004."
                    )

                source_id = int(
                    row[0]
                )

                source_name = clean(
                    row[1]
                )

                print(
                    "MaNguon:",
                    source_id,
                )

                print(
                    "Ten:",
                    source_name,
                )

                print(
                    "LienKetNguon:",
                    clean(row[2]),
                )

                if source_name != SOURCE_NAME:

                    fail(
                        "MaNguon=1004 khong phai "
                        "nguon ngu phap mong doi."
                    )

                print(
                    "NGUON: OK"
                )

        finally:

            try:
                connection.rollback()
            except Exception:
                pass

    # =====================================================
    # 3. CREATE OUTPUT FOLDER
    # =====================================================
    print()
    print("[3] TAO FILE CSV")
    print("-" * 110)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "MaMucNguPhapChuan",
        "CapDoHSK",
        "SoThuTuChuan",
        "NhomLonTrung",
        "NhomConTrung",
        "TenMucTrung",
        "NoiDungChuanTrung",
        "MaNguon",
        "TrangThaiReview",
        "GhiChu",
    ]

    rows = []

    for (
        order_no,
        main_group,
        sub_group,
        item_name,
        official_content,
    ) in GRAMMAR_ITEMS:

        rows.append(
            {
                "MaMucNguPhapChuan": (
                    f"GF1-{order_no:03d}"
                ),

                "CapDoHSK": 1,

                "SoThuTuChuan": (
                    order_no
                ),

                "NhomLonTrung": (
                    main_group
                ),

                "NhomConTrung": (
                    sub_group
                ),

                "TenMucTrung": (
                    item_name
                ),

                "NoiDungChuanTrung": (
                    official_content
                ),

                "MaNguon": (
                    SOURCE_ID
                ),

                "TrangThaiReview": (
                    "nguon_chuan"
                ),

                "GhiChu": (
                    "Phạm vi ngữ pháp HSK1; "
                    "chưa phải nội dung giảng dạy "
                    "của từng bài."
                ),
            }
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(
            rows
        )

    print(
        "Da tao:"
    )

    print(
        OUTPUT_FILE
    )

    # =====================================================
    # 4. VERIFY FILE
    # =====================================================
    print()
    print("[4] VERIFY FILE")
    print("-" * 110)

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        verify_rows = list(
            reader
        )

    if len(verify_rows) != 48:

        fail(
            "File CSV khong co dung 48 dong."
        )

    ids = [
        clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )
        for row in verify_rows
    ]

    if len(set(ids)) != 48:

        fail(
            "MaMucNguPhapChuan "
            "bi trung."
        )

    if ids[0] != "GF1-001":

        fail(
            "ID dau tien khong dung."
        )

    if ids[-1] != "GF1-048":

        fail(
            "ID cuoi cung khong dung."
        )

    wrong_source = [
        row
        for row in verify_rows
        if clean(
            row["MaNguon"]
        ) != "1004"
    ]

    if wrong_source:

        fail(
            "Co dong MaNguon "
            "khong bang 1004."
        )

    print(
        "Tong dong:",
        len(verify_rows),
    )

    print(
        "ID duy nhat:",
        len(set(ids)),
    )

    print(
        "GF1-001 -> GF1-048: OK"
    )

    print(
        "MaNguon=1004: 48/48 OK"
    )

    # =====================================================
    # 5. THONG KE
    # =====================================================
    print()
    print("[5] THONG KE NHOM")
    print("-" * 110)

    groups = {}

    for row in verify_rows:

        group = clean(
            row["NhomLonTrung"]
        )

        groups[group] = (
            groups.get(
                group,
                0,
            )
            + 1
        )

    for (
        group,
        count,
    ) in groups.items():

        print(
            f"{group}: {count}"
        )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 110)
    print(
        "KET QUA 09H4"
    )
    print("=" * 110)

    print(
        "Nguon:",
        SOURCE_ID,
        "-",
        SOURCE_NAME,
    )

    print(
        "Tong muc ngu phap HSK1:",
        len(verify_rows),
    )

    print(
        "File:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "DA TAO DANH SACH NGUON "
        "48 MUC NGU PHAP HSK1."
    )

    print()
    print(
        "CHUA SUA dbo.NguPhap."
    )

    print(
        "CHUA GAN MaNguon=1004 "
        "CHO 7 MUC BAI 1."
    )

    print(
        "CHUA INSERT NGU PHAP "
        "BAI 2 -> 23."
    )

    print()
    print("=" * 110)
    print("HOAN TAT")
    print("=" * 110)


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
            "09H4 THAT BAI"
        )
        print("=" * 110)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)