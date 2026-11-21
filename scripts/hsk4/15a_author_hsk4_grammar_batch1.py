# -*- coding: utf-8 -*-
"""
BUOC 15A - BIEN SOAN NGU PHAP HSK4 BATCH 1

Pham vi:
- 20 don vi giang day dau tien / 114.
- Nguon pham vi: GF0025-2021.
- MoTa/CachDung/ViDu: noi dung giang day Moc Han bien soan.

CHI TAO CSV PREVIEW.
KHONG GHI SQL.
KHONG GAN BAI HOC.
"""

import csv
import hashlib
import json
import re

from pathlib import Path


# ==========================================================
# 1. CAU HINH
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

SOURCE = (
    DATA_DIR
    / "grammar_hsk4_teaching_units_plan.csv"
)

OUTPUT = (
    DATA_DIR
    / "grammar_hsk4_teaching_draft_batch01.csv"
)

SUMMARY = (
    DATA_DIR
    / "grammar_hsk4_teaching_draft_batch01_summary.json"
)


EXPECTED_PLAN_SHA256 = (
    "5a213b92fe25c2947c25bb4d00536425"
    "aa0a4d315f454b462f4b4fd59835088f"
)

EXPECTED_PLAN_TOTAL = 114
EXPECTED_BATCH_TOTAL = 20

SOURCE_ID = 1004


OUTPUT_FIELDS = [
    "MaDonViGiangDay",
    "MaMucNguPhapChuan",
    "SoThuTuChuan",
    "SoThuTuNguon",

    "NhanDonViNguonTrung",
    "DuongDanNguon",

    "TenCauTruc",
    "MoTa",
    "CachDung",

    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",

    "MaNguon",
    "TrangThai",
    "TrangThaiKiemDuyet",
    "GhiChuNguon",
]


# ==========================================================
# 2. NOI DUNG BIEN SOAN BATCH 1
# ==========================================================
#
# Key:
# MaDonViGiangDay
#
# Value:
# (
#   TenCauTruc,
#   MoTa,
#   CachDung,
#   ViDuTiengTrung,
#   ViDuPinyin,
#   ViDuTiengViet,
# )
#
# Day la NOI DUNG GIANG DAY MOC HAN,
# khong phai nguyen van GF0025.
# ==========================================================

CONTENT = {

    # ------------------------------------------------------
    # GF4-001 得
    # ------------------------------------------------------

    "GF4-001-T01": (
        "得（děi）+ động từ",
        (
            "得 đọc là děi khi làm động từ năng nguyện, "
            "biểu thị sự cần thiết hoặc bắt buộc phải làm "
            "một hành động."
        ),
        (
            "Chủ ngữ + 得（děi）+ động từ/cụm động từ. "
            "Có thể hiểu là “phải, cần phải”."
        ),
        "你得先休息一下。",
        "Nǐ děi xiān xiūxi yíxià.",
        "Bạn phải nghỉ một lát trước.",
    ),

    # ------------------------------------------------------
    # GF4-002 人家
    # ------------------------------------------------------

    "GF4-002-T01": (
        "人家（đại từ）",
        (
            "人家 có thể dùng để chỉ người khác hoặc mọi người "
            "trong ngữ cảnh giao tiếp. Trong khẩu ngữ, tùy ngữ cảnh "
            "nó cũng có thể được người nói dùng để tự xưng với "
            "sắc thái biểu cảm."
        ),
        (
            "人家 + vị ngữ; cần xác định đối tượng mà 人家 "
            "thay thế dựa vào ngữ cảnh."
        ),
        "人家都走了，你还在等什么？",
        "Rénjiā dōu zǒu le, nǐ hái zài děng shénme?",
        "Mọi người đã đi hết rồi, bạn còn đang đợi gì vậy?",
    ),

    # ------------------------------------------------------
    # GF4-003: 名量词
    # ------------------------------------------------------

    "GF4-003-T01": (
        "打（dǎ）— lượng từ",
        (
            "打 là lượng từ dùng để đếm một nhóm gồm mười hai "
            "đơn vị của một số loại đồ vật."
        ),
        "Số từ + 打 + danh từ; 一打 tương ứng một tá.",
        "我买了一打铅笔。",
        "Wǒ mǎi le yì dǎ qiānbǐ.",
        "Tôi đã mua một tá bút chì.",
    ),

    "GF4-003-T02": (
        "袋 — lượng từ",
        (
            "袋 dùng để đếm đồ vật hoặc vật chất được đựng "
            "trong túi hoặc bao."
        ),
        "Số từ + 袋 + danh từ.",
        "他买了一袋米。",
        "Tā mǎi le yí dài mǐ.",
        "Anh ấy đã mua một bao gạo.",
    ),

    "GF4-003-T03": (
        "根 — lượng từ",
        (
            "根 thường dùng cho những vật dài, mảnh hoặc "
            "có hình dạng giống que, sợi."
        ),
        "Số từ + 根 + danh từ.",
        "这里有一根绳子。",
        "Zhèlǐ yǒu yì gēn shéngzi.",
        "Ở đây có một sợi dây.",
    ),

    "GF4-003-T04": (
        "卷 — lượng từ",
        (
            "卷 dùng để đếm những vật được cuộn lại thành "
            "cuộn hoặc cuốn."
        ),
        "Số từ + 卷 + danh từ.",
        "桌上有一卷纸。",
        "Zhuō shàng yǒu yì juǎn zhǐ.",
        "Trên bàn có một cuộn giấy.",
    ),

    "GF4-003-T05": (
        "棵 — lượng từ",
        (
            "棵 là lượng từ thường dùng để đếm cây cối "
            "hoặc thực vật có thân."
        ),
        "Số từ + 棵 + danh từ chỉ cây.",
        "门口有一棵大树。",
        "Ménkǒu yǒu yì kē dà shù.",
        "Trước cửa có một cây lớn.",
    ),

    "GF4-003-T06": (
        "批 — lượng từ",
        (
            "批 dùng để đếm một nhóm hoặc một lô người, "
            "hàng hóa hay sự vật được xử lý cùng đợt."
        ),
        "Số từ + 批 + danh từ.",
        "这批货明天到。",
        "Zhè pī huò míngtiān dào.",
        "Lô hàng này ngày mai sẽ đến.",
    ),

    # ------------------------------------------------------
    # GF4-004: 借用量词
    # ------------------------------------------------------

    "GF4-004-T01": (
        "碗 — danh từ dùng như lượng từ",
        (
            "碗 vốn có nghĩa là “bát”, khi được mượn làm "
            "lượng từ thì biểu thị một bát đầy thức ăn "
            "hoặc đồ uống."
        ),
        "Số từ + 碗 + danh từ.",
        "我吃了一碗面条。",
        "Wǒ chī le yì wǎn miàntiáo.",
        "Tôi đã ăn một bát mì.",
    ),

    "GF4-004-T02": (
        "脸 — danh từ dùng như lượng từ",
        (
            "脸 có thể được dùng sau 一 để biểu thị trạng thái "
            "hoặc biểu cảm hiện rõ trên toàn khuôn mặt."
        ),
        "一脸 + danh từ/trạng thái biểu cảm.",
        "他一脸笑容地走进来。",
        "Tā yì liǎn xiàoróng de zǒu jìnlái.",
        "Anh ấy bước vào với khuôn mặt đầy nụ cười.",
    ),

    "GF4-004-T03": (
        "手 — danh từ dùng như lượng từ",
        (
            "手 có thể được mượn để biểu thị một khả năng, "
            "kỹ năng hoặc thành quả thể hiện bằng tay."
        ),
        (
            "一手 + thành phần miêu tả kỹ năng; "
            "thường gặp trong 一手好字, 一手好菜."
        ),
        "他写得一手好字。",
        "Tā xiě de yì shǒu hǎo zì.",
        "Anh ấy viết chữ rất đẹp.",
    ),

    "GF4-004-T04": (
        "屋子 — danh từ dùng như lượng từ",
        (
            "屋子 có thể được dùng sau 一 để biểu thị "
            "một căn phòng đầy người hoặc đồ vật."
        ),
        "一屋子 + danh từ.",
        "屋里坐了一屋子人。",
        "Wūli zuò le yì wūzi rén.",
        "Trong phòng có cả một phòng đầy người đang ngồi.",
    ),

    "GF4-004-T05": (
        "桌子 — danh từ dùng như lượng từ",
        (
            "桌子 có thể được dùng sau 一 để biểu thị "
            "một bàn đầy đồ vật, thường là thức ăn."
        ),
        "一桌子 + danh từ.",
        "她做了一桌子菜。",
        "Tā zuò le yì zhuōzi cài.",
        "Cô ấy đã làm cả một bàn đầy món ăn.",
    ),

    "GF4-004-T06": (
        "刀 — động lượng từ",
        (
            "刀 vốn là danh từ “dao”, khi dùng như động lượng từ "
            "thì chỉ một lần thực hiện động tác bằng dao."
        ),
        "Động từ + 一刀.",
        "他在西瓜上切了一刀。",
        "Tā zài xīguā shàng qiē le yì dāo.",
        "Anh ấy đã cắt một nhát vào quả dưa hấu.",
    ),

    "GF4-004-T07": (
        "针 — động lượng từ",
        (
            "针 vốn có nghĩa là “kim”, khi dùng như động lượng từ "
            "thì thường biểu thị một lần tiêm hoặc châm."
        ),
        "Động từ + 一针; thường gặp: 打一针.",
        "医生给他打了一针。",
        "Yīshēng gěi tā dǎ le yì zhēn.",
        "Bác sĩ đã tiêm cho anh ấy một mũi.",
    ),

    # ------------------------------------------------------
    # GF4-005: 程度副词
    # ------------------------------------------------------

    "GF4-005-T01": (
        "格外 + tính từ",
        (
            "格外 là phó từ chỉ mức độ, dùng để nhấn mạnh "
            "mức độ nổi bật hoặc khác thường."
        ),
        "格外 + tính từ/cụm tính từ.",
        "今天的天气格外好。",
        "Jīntiān de tiānqì géwài hǎo.",
        "Thời tiết hôm nay đặc biệt đẹp.",
    ),

    "GF4-005-T02": (
        "极 + tính từ",
        (
            "极 dùng làm phó từ mức độ với nghĩa "
            "“cực kỳ, hết sức”, thường mang sắc thái tương đối "
            "trang trọng."
        ),
        "极 + tính từ.",
        "这个问题极重要。",
        "Zhège wèntí jí zhòngyào.",
        "Vấn đề này cực kỳ quan trọng.",
    ),

    "GF4-005-T03": (
        "极其 + tính từ",
        (
            "极其 là phó từ chỉ mức độ rất cao, nghĩa là "
            "“cực kỳ, vô cùng”, thường dùng trong văn viết "
            "hoặc cách nói trang trọng."
        ),
        "极其 + tính từ/cụm tính từ.",
        "情况极其复杂。",
        "Qíngkuàng jíqí fùzá.",
        "Tình hình cực kỳ phức tạp.",
    ),

    # ------------------------------------------------------
    # GF4-006 共
    # ------------------------------------------------------

    "GF4-006-T01": (
        "共 + số lượng",
        (
            "共 là phó từ biểu thị tổng số hoặc tổng cộng "
            "của người, sự vật hay số lượng."
        ),
        (
            "共 + động từ/số lượng; thường gặp các dạng "
            "共有、共计..."
        ),
        "这本书共有十章。",
        "Zhè běn shū gòng yǒu shí zhāng.",
        "Cuốn sách này có tổng cộng mười chương.",
    ),

    # ------------------------------------------------------
    # GF4-007-T01 按时
    # ------------------------------------------------------

    "GF4-007-T01": (
        "按时 + động từ",
        (
            "按时 biểu thị hành động được thực hiện đúng "
            "thời gian đã quy định hoặc đã dự định."
        ),
        "按时 + động từ/cụm động từ.",
        "请按时交作业。",
        "Qǐng ànshí jiāo zuòyè.",
        "Hãy nộp bài tập đúng giờ.",
    ),
}


# ==========================================================
# 3. HAM HO TRO
# ==========================================================

def clean(value):

    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open("rb") as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(block)

    return digest.hexdigest()


def read_csv(path):

    if not path.is_file():

        raise FileNotFoundError(
            f"Khong tim thay:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

        fields = (
            reader.fieldnames
            or []
        )

    return fields, rows


def write_csv(
    path,
    rows,
):

    if path.exists():

        raise FileExistsError(
            f"Da ton tai file:\n{path}\n"
            "Khong tu dong ghi de."
        )

    with path.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_FIELDS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


# ==========================================================
# 4. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 15A - BIEN SOAN NGU PHAP "
        "HSK4 BATCH 1"
    )

    print("=" * 80)

    print(
        "NOI DUNG MOC HAN - KHONG GHI SQL"
    )

    # ======================================================
    # 1. KIEM TRA PLAN BUOC 14
    # ======================================================

    print(
        "\n[1] KIEM TRA PLAN BUOC 14"
    )

    plan_hash = sha256_file(
        SOURCE
    )

    print(
        "PLAN SHA256:"
    )

    print(
        plan_hash
    )

    if (
        plan_hash
        != EXPECTED_PLAN_SHA256
    ):

        raise RuntimeError(
            "Plan Buoc 14 da thay doi."
        )

    fields, plan = read_csv(
        SOURCE
    )

    print(
        "Tong plan:",
        len(plan),
    )

    if (
        len(plan)
        != EXPECTED_PLAN_TOTAL
    ):

        raise RuntimeError(
            "Plan khong con dung 114 muc."
        )

    # ======================================================
    # 2. LAY 20 DON VI DAU
    # ======================================================

    print(
        "\n[2] LAY BATCH 1"
    )

    batch = plan[
        :EXPECTED_BATCH_TOTAL
    ]

    print(
        "So muc:",
        len(batch),
    )

    if (
        len(batch)
        != EXPECTED_BATCH_TOTAL
    ):

        raise RuntimeError(
            "Khong lay duoc du 20 muc."
        )

    plan_ids = [
        clean(
            row.get(
                "MaDonViGiangDay"
            )
        )
        for row in batch
    ]

    content_ids = list(
        CONTENT.keys()
    )

    if (
        plan_ids
        != content_ids
    ):

        print(
            "\nID trong PLAN:"
        )

        for value in plan_ids:
            print(
                " ",
                value,
            )

        print(
            "\nID trong CONTENT:"
        )

        for value in content_ids:
            print(
                " ",
                value,
            )

        raise RuntimeError(
            "Thu tu/content batch 1 "
            "khong khop Plan Buoc 14."
        )

    print(
        "PASS: 20 ID khop plan."
    )

    print(
        "Tu:",
        plan_ids[0],
    )

    print(
        "Den:",
        plan_ids[-1],
    )

    # ======================================================
    # 3. TAO NOI DUNG
    # ======================================================

    print(
        "\n[3] TAO NOI DUNG GIANG DAY"
    )

    result = []

    for row in batch:

        teaching_id = clean(
            row.get(
                "MaDonViGiangDay"
            )
        )

        (
            title,
            description,
            usage,
            example_zh,
            example_py,
            example_vi,
        ) = CONTENT[
            teaching_id
        ]

        values = [
            title,
            description,
            usage,
            example_zh,
            example_py,
            example_vi,
        ]

        if any(
            not clean(value)
            for value in values
        ):

            raise RuntimeError(
                f"{teaching_id}: "
                "noi dung bien soan chua day du."
            )

        result.append({

            "MaDonViGiangDay":
                teaching_id,

            "MaMucNguPhapChuan":
                clean(
                    row.get(
                        "MaMucNguPhapChuan"
                    )
                ),

            "SoThuTuChuan":
                clean(
                    row.get(
                        "SoThuTuChuan"
                    )
                ),

            "SoThuTuNguon":
                clean(
                    row.get(
                        "SoThuTuNguon"
                    )
                ),

            "NhanDonViNguonTrung":
                clean(
                    row.get(
                        "NhanDonViNguonTrung"
                    )
                ),

            "DuongDanNguon":
                clean(
                    row.get(
                        "DuongDanNguon"
                    )
                ),

            "TenCauTruc":
                clean(title),

            "MoTa":
                clean(description),

            "CachDung":
                clean(usage),

            "ViDuTiengTrung":
                clean(example_zh),

            "ViDuPinyin":
                clean(example_py),

            "ViDuTiengViet":
                clean(example_vi),

            "MaNguon":
                SOURCE_ID,

            "TrangThai":
                "ban_nhap",

            "TrangThaiKiemDuyet":
                "CHO_REVIEW",

            "GhiChuNguon":
                (
                    "Pham vi theo GF0025-2021; "
                    "MoTa/CachDung/ViDu la noi dung "
                    "giang day do Moc Han bien soan."
                ),
        })

    # ======================================================
    # 4. VALIDATE
    # ======================================================

    print(
        "\n[4] KIEM TRA NOI DUNG"
    )

    if (
        len(result)
        != EXPECTED_BATCH_TOTAL
    ):

        raise RuntimeError(
            "Batch khong dung 20 muc."
        )

    if len({
        row[
            "MaDonViGiangDay"
        ]
        for row in result
    }) != EXPECTED_BATCH_TOTAL:

        raise RuntimeError(
            "MaDonViGiangDay bi trung."
        )

    required_content_fields = [
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
    ]

    missing_content = []

    for row in result:

        missing = [
            field
            for field in required_content_fields
            if not clean(
                row.get(field)
            )
        ]

        if missing:

            missing_content.append(
                (
                    row[
                        "MaDonViGiangDay"
                    ],
                    missing,
                )
            )

    if missing_content:

        raise RuntimeError(
            "Con noi dung rong: "
            + str(
                missing_content
            )
        )

    # ----------------------------------------------
    # Kiem tra vi du Trung ket thuc bang dau cau.
    # ----------------------------------------------

    bad_zh = [
        row[
            "MaDonViGiangDay"
        ]
        for row in result
        if not re.search(
            r"[。！？!?]$",
            row[
                "ViDuTiengTrung"
            ],
        )
    ]

    if bad_zh:

        raise RuntimeError(
            "Vi du Trung thieu dau cau: "
            + ", ".join(bad_zh)
        )

    # ----------------------------------------------
    # Pinyin khong duoc chua chu Han.
    # ----------------------------------------------

    bad_pinyin = [
        row[
            "MaDonViGiangDay"
        ]
        for row in result
        if re.search(
            r"[\u3400-\u9fff]",
            row[
                "ViDuPinyin"
            ],
        )
    ]

    if bad_pinyin:

        raise RuntimeError(
            "Pinyin con chu Han: "
            + ", ".join(
                bad_pinyin
            )
        )

    print(
        "PASS: 20/20 day du "
        "TenCauTruc/MoTa/CachDung/ViDu."
    )

    # ======================================================
    # 5. IN PREVIEW
    # ======================================================

    print(
        "\n[5] PREVIEW 20 MUC"
    )

    for index, row in enumerate(
        result,
        start=1,
    ):

        print(
            "\n"
            + "-" * 80
        )

        print(
            f"[{index:02d}] "
            f"{row['MaDonViGiangDay']}"
        )

        print(
            "Nguon:",
            row[
                "NhanDonViNguonTrung"
            ],
        )

        print(
            "Ten:",
            row[
                "TenCauTruc"
            ],
        )

        print(
            "Mo ta:",
            row[
                "MoTa"
            ],
        )

        print(
            "Cach dung:",
            row[
                "CachDung"
            ],
        )

        print(
            "VD:",
            row[
                "ViDuTiengTrung"
            ],
        )

        print(
            "PY:",
            row[
                "ViDuPinyin"
            ],
        )

        print(
            "VI:",
            row[
                "ViDuTiengViet"
            ],
        )

    # ======================================================
    # 6. GHI FILE
    # ======================================================

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        OUTPUT,
        result,
    )

    output_hash = sha256_file(
        OUTPUT
    )

    summary = {

        "status":
            "PASS",

        "batch":
            1,

        "tong_plan":
            len(plan),

        "tong_batch":
            len(result),

        "ma_dau":
            result[0][
                "MaDonViGiangDay"
            ],

        "ma_cuoi":
            result[-1][
                "MaDonViGiangDay"
            ],

        "day_du_noi_dung":
            len(result),

        "ma_nguon":
            SOURCE_ID,

        "trang_thai":
            "ban_nhap",

        "trang_thai_kiem_duyet":
            "CHO_REVIEW",

        "plan_sha256":
            plan_hash,

        "output_sha256":
            output_hash,

        "da_ghi_sql":
            False,

        "da_gan_bai_hoc":
            False,

        "ghi_chu":
            (
                "Pham vi Trung van theo GF0025-2021. "
                "Noi dung Viet/Pinyin/vi du la "
                "noi dung giang day Moc Han bien soan."
            ),
    }

    if SUMMARY.exists():

        raise FileExistsError(
            f"Da ton tai file:\n"
            f"{SUMMARY}"
        )

    SUMMARY.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # 7. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "BIEN SOAN HSK4 BATCH 1 THANH CONG"
    )

    print("=" * 80)

    print(
        "Da bien soan:",
        len(result),
        "/ 114",
    )

    print(
        "Tu:",
        result[0][
            "MaDonViGiangDay"
        ],
    )

    print(
        "Den:",
        result[-1][
            "MaDonViGiangDay"
        ],
    )

    print(
        "Noi dung day du:",
        len(result),
        "/ 20",
    )

    print(
        "Trang thai: ban_nhap / CHO_REVIEW"
    )

    print(
        "\nOUTPUT:"
    )

    print(
        " ",
        OUTPUT,
    )

    print(
        "\nOUTPUT SHA256:"
    )

    print(
        output_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY,
    )

    print(
        "\nKHONG GHI SQL."
    )

    print(
        "CHUA GAN BAI HOC."
    )

    print("=" * 80)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)