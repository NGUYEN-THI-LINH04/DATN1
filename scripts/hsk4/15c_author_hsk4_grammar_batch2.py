# -*- coding: utf-8 -*-
"""
BUOC 15C - BIEN SOAN NGU PHAP HSK4 BATCH 2

Pham vi:
- Don vi 21 -> 40 trong plan 114 muc.
- Tu GF4-007-T02 den GF4-017-T01.

Nguon pham vi:
- GF0025-2021.

MoTa/CachDung/ViDu:
- Noi dung giang day do Moc Han bien soan.

Bao ve:
- Khoa PLAN Buoc 14 bang SHA256.
- Khoa reviewed Batch 01 bang SHA256.
- Chi xuat CSV preview.
- KHONG ghi SQL.
- KHONG gan BaiHoc.
- KHONG publish.
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

PLAN_FILE = (
    DATA_DIR
    / "grammar_hsk4_teaching_units_plan.csv"
)

BATCH01_REVIEWED = (
    DATA_DIR
    / "grammar_hsk4_teaching_reviewed_batch01.csv"
)

OUTPUT = (
    DATA_DIR
    / "grammar_hsk4_teaching_draft_batch02.csv"
)

SUMMARY = (
    DATA_DIR
    / "grammar_hsk4_teaching_draft_batch02_summary.json"
)


EXPECTED_PLAN_SHA256 = (
    "5a213b92fe25c2947c25bb4d00536425"
    "aa0a4d315f454b462f4b4fd59835088f"
)

EXPECTED_BATCH01_SHA256 = (
    "81e6f0fcb9ddf8e16a71abb3b1aa5094"
    "fb3c0671f5063b25c01c2c7b311b23e6"
)

EXPECTED_PLAN_TOTAL = 114
EXPECTED_PREVIOUS_TOTAL = 20
EXPECTED_BATCH_TOTAL = 20

BATCH_START = 20
BATCH_END = 40

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
# 2. NOI DUNG GIANG DAY BATCH 2
# ==========================================================

CONTENT = {

    # ======================================================
    # GF4-007 - 时间副词
    # ======================================================

    "GF4-007-T02": (
        "即将 + động từ",
        (
            "即将 là phó từ thời gian, biểu thị một hành động "
            "hoặc sự việc sắp xảy ra trong thời gian rất gần."
        ),
        (
            "即将 + động từ/cụm động từ. "
            "Thường dùng trong văn viết hoặc cách nói "
            "tương đối trang trọng."
        ),
        "飞机即将起飞。",
        "Fēijī jíjiāng qǐfēi.",
        "Máy bay sắp cất cánh.",
    ),

    "GF4-007-T03": (
        "急忙 + động từ",
        (
            "急忙 biểu thị việc thực hiện hành động một cách "
            "vội vàng do tình huống khẩn cấp hoặc cần xử lý ngay."
        ),
        "急忙 + động từ/cụm động từ.",
        "听到这个消息，他急忙赶回家。",
        "Tīngdào zhège xiāoxi, tā jímáng gǎn huí jiā.",
        "Nghe tin này, anh ấy vội vàng chạy về nhà.",
    ),

    "GF4-007-T04": (
        "渐渐 + động từ/tính từ",
        (
            "渐渐 biểu thị một sự thay đổi diễn ra từ từ "
            "theo thời gian."
        ),
        (
            "渐渐 + động từ/tính từ. "
            "Có thể hiểu là “dần dần”."
        ),
        "天气渐渐冷了。",
        "Tiānqì jiànjiàn lěng le.",
        "Thời tiết dần dần lạnh đi.",
    ),

    "GF4-007-T05": (
        "尽快 + động từ",
        (
            "尽快 biểu thị yêu cầu hoặc mong muốn thực hiện "
            "một hành động trong thời gian sớm nhất có thể."
        ),
        (
            "尽快 + động từ/cụm động từ. "
            "Có thể hiểu là “càng sớm càng tốt”."
        ),
        "请尽快回复我。",
        "Qǐng jǐnkuài huífù wǒ.",
        "Hãy trả lời tôi sớm nhất có thể.",
    ),

    # ======================================================
    # GF4-008 - 频率、重复副词
    # ======================================================

    "GF4-008-T01": (
        "一再 + động từ",
        (
            "一再 biểu thị cùng một hành động hoặc tình huống "
            "xảy ra nhiều lần."
        ),
        (
            "一再 + động từ/cụm động từ. "
            "Thường nhấn mạnh sự lặp lại nhiều lần."
        ),
        "他一再强调这个问题的重要性。",
        "Tā yízài qiángdiào zhège wèntí de zhòngyàoxìng.",
        "Anh ấy nhiều lần nhấn mạnh tầm quan trọng của vấn đề này.",
    ),

    "GF4-008-T02": (
        "再三 + động từ",
        (
            "再三 biểu thị một hành động được thực hiện nhiều lần, "
            "thường mang sắc thái cân nhắc, nhắc nhở hoặc yêu cầu "
            "lặp đi lặp lại."
        ),
        "再三 + động từ/cụm động từ.",
        "我再三提醒他注意安全。",
        "Wǒ zàisān tíxǐng tā zhùyì ānquán.",
        "Tôi đã nhiều lần nhắc anh ấy chú ý an toàn.",
    ),

    # ======================================================
    # GF4-009 - 关联副词 却
    # ======================================================

    "GF4-009-T01": (
        "……，却……",
        (
            "却 dùng để biểu thị kết quả hoặc tình huống "
            "trái với điều được dự đoán từ vế trước."
        ),
        (
            "Vế 1 + 却 + vế 2. "
            "Có thể dịch là “nhưng, thế mà, lại”."
        ),
        "他很累，却没有休息。",
        "Tā hěn lèi, què méiyǒu xiūxi.",
        "Anh ấy rất mệt nhưng lại không nghỉ ngơi.",
    ),

    # ======================================================
    # GF4-010 - 否定副词 未必
    # ======================================================

    "GF4-010-T01": (
        "未必 + vị ngữ",
        (
            "未必 biểu thị người nói cho rằng một nhận định "
            "hoặc kết quả chưa chắc đã đúng hoặc sẽ xảy ra."
        ),
        (
            "Chủ ngữ + 未必 + động từ/tính từ/cụm vị ngữ. "
            "Có nghĩa là “chưa chắc”."
        ),
        "他未必会同意这个办法。",
        "Tā wèibì huì tóngyì zhège bànfǎ.",
        "Anh ấy chưa chắc sẽ đồng ý với cách này.",
    ),

    # ======================================================
    # GF4-011 - 情态副词
    # ======================================================

    "GF4-011-T01": (
        "几乎 + động từ/tính từ",
        (
            "几乎 biểu thị một tình huống rất gần với việc "
            "xảy ra hoặc đạt đến một mức độ nào đó, "
            "nhưng không hoàn toàn."
        ),
        (
            "几乎 + động từ/tính từ/cụm vị ngữ. "
            "Có thể hiểu là “gần như, hầu như”."
        ),
        "我几乎忘了今天的会议。",
        "Wǒ jīhū wàng le jīntiān de huìyì.",
        "Tôi gần như quên mất cuộc họp hôm nay.",
    ),

    "GF4-011-T02": (
        "似乎 + vị ngữ",
        (
            "似乎 biểu thị sự phỏng đoán của người nói dựa trên "
            "những gì quan sát hoặc cảm nhận được, nhưng chưa "
            "khẳng định chắc chắn."
        ),
        (
            "似乎 + động từ/tính từ/cụm vị ngữ. "
            "Có thể hiểu là “dường như, hình như”."
        ),
        "他似乎不太高兴。",
        "Tā sìhū bú tài gāoxìng.",
        "Anh ấy dường như không được vui lắm.",
    ),

    # ======================================================
    # GF4-012 - 语气副词
    # ======================================================

    "GF4-012-T01": (
        "的确 + vị ngữ",
        (
            "的确 dùng để xác nhận rằng một sự việc hoặc nhận định "
            "là đúng với thực tế."
        ),
        (
            "的确 thường đứng trước động từ hoặc tính từ, "
            "có nghĩa là “quả thật, đúng là”."
        ),
        "这件事的确很重要。",
        "Zhè jiàn shì díquè hěn zhòngyào.",
        "Việc này quả thật rất quan trọng.",
    ),

    "GF4-012-T02": (
        "反而 + vị ngữ",
        (
            "反而 biểu thị kết quả thực tế trái với điều thông thường "
            "hoặc trái với điều người nói mong đợi."
        ),
        (
            "Vế nêu tình huống + 反而 + kết quả trái dự kiến. "
            "Có thể hiểu là “trái lại, ngược lại”."
        ),
        "我想帮他，反而给他添了麻烦。",
        "Wǒ xiǎng bāng tā, fǎn'ér gěi tā tiān le máfan.",
        "Tôi định giúp anh ấy, trái lại còn gây thêm phiền phức cho anh ấy.",
    ),

    "GF4-012-T03": (
        "还（ngữ khí）+ VP/AP",
        (
            "还 trong cách dùng này là phó từ ngữ khí, "
            "không phải nghĩa “vẫn/còn”. Nó có thể biểu thị "
            "một tình huống vượt ngoài dự kiến hoặc tăng sắc thái "
            "nhấn mạnh của người nói."
        ),
        (
            "还 + động từ/tính từ; thường gặp dạng "
            "还真 + VP/AP khi người nói nhận thấy kết quả "
            "khá bất ngờ hoặc đáng nhấn mạnh."
        ),
        "这个办法还真有效。",
        "Zhège bànfǎ hái zhēn yǒuxiào.",
        "Cách này quả thật lại hiệu quả đấy.",
    ),

    "GF4-012-T04": (
        "竟然 + vị ngữ",
        (
            "竟然 biểu thị người nói cảm thấy bất ngờ vì sự việc "
            "thực tế xảy ra ngoài dự đoán."
        ),
        (
            "竟然 + động từ/tính từ/cụm vị ngữ. "
            "Có thể dịch là “không ngờ, vậy mà”."
        ),
        "他竟然忘了今天的会议。",
        "Tā jìngrán wàng le jīntiān de huìyì.",
        "Không ngờ anh ấy lại quên cuộc họp hôm nay.",
    ),

    "GF4-012-T05": (
        "究竟 + câu hỏi",
        (
            "究竟 dùng trong câu nghi vấn để nhấn mạnh yêu cầu "
            "làm rõ sự thật, nguyên nhân hoặc kết quả cuối cùng."
        ),
        (
            "究竟 thường đứng trước thành phần được hỏi. "
            "Có thể hiểu là “rốt cuộc, cho cùng”."
        ),
        "你究竟想说什么？",
        "Nǐ jiūjìng xiǎng shuō shénme?",
        "Rốt cuộc bạn muốn nói gì?",
    ),

    # ======================================================
    # GF4-013 - 介词 自
    # ======================================================

    "GF4-013-T01": (
        "自 + thời gian/nơi chốn",
        (
            "自 là giới từ mang sắc thái tương đối trang trọng, "
            "dùng để đưa ra điểm bắt đầu về thời gian hoặc nơi chốn."
        ),
        (
            "自 + thời gian/nơi chốn + thành phần còn lại. "
            "Khi chỉ thời gian thường có nghĩa “từ, kể từ”."
        ),
        "本规定自明天起实行。",
        "Běn guīdìng zì míngtiān qǐ shíxíng.",
        "Quy định này bắt đầu được thực hiện từ ngày mai.",
    ),

    # ======================================================
    # GF4-014 - 对于
    # ======================================================

    "GF4-014-T01": (
        "对于 + đối tượng",
        (
            "对于 dùng để đưa ra đối tượng mà một thái độ, "
            "nhận xét, cách xử lý hoặc hành động hướng tới."
        ),
        (
            "对于 + danh từ/cụm danh từ + chủ ngữ + vị ngữ. "
            "Có thể hiểu là “đối với”."
        ),
        "对于这个问题，我们还需要讨论。",
        "Duìyú zhège wèntí, wǒmen hái xūyào tǎolùn.",
        "Đối với vấn đề này, chúng ta vẫn cần thảo luận thêm.",
    ),

    # ======================================================
    # GF4-015 - 关于
    # ======================================================

    "GF4-015-T01": (
        "关于 + chủ đề",
        (
            "关于 dùng để đưa ra chủ đề hoặc nội dung mà lời nói, "
            "văn bản hay cuộc thảo luận đề cập đến."
        ),
        (
            "关于 + danh từ/cụm danh từ + mệnh đề. "
            "Có thể hiểu là “về, liên quan đến”."
        ),
        "关于这件事，我想再说明一下。",
        "Guānyú zhè jiàn shì, wǒ xiǎng zài shuōmíng yíxià.",
        "Về việc này, tôi muốn giải thích thêm một chút.",
    ),

    # ======================================================
    # GF4-016 - 替
    # ======================================================

    "GF4-016-T01": (
        "替 + người + động từ",
        (
            "替 là giới từ dùng để đưa ra người mà chủ thể "
            "thực hiện hành động thay hoặc làm giúp."
        ),
        (
            "Chủ ngữ + 替 + người + động từ/cụm động từ. "
            "Có thể hiểu là “thay cho, giúp cho”."
        ),
        "我替你去一趟吧。",
        "Wǒ tì nǐ qù yí tàng ba.",
        "Để tôi đi thay bạn một chuyến nhé.",
    ),

    # ======================================================
    # GF4-017 - 根据
    # ======================================================

    "GF4-017-T01": (
        "根据 + căn cứ",
        (
            "根据 dùng để đưa ra căn cứ, thông tin hoặc cơ sở "
            "mà một phán đoán, quyết định hay hành động dựa vào."
        ),
        (
            "根据 + danh từ/cụm danh từ + mệnh đề. "
            "Có thể hiểu là “căn cứ vào, dựa theo”."
        ),
        "根据天气预报，明天会下雨。",
        "Gēnjù tiānqì yùbào, míngtiān huì xiàyǔ.",
        "Theo dự báo thời tiết, ngày mai sẽ có mưa.",
    ),
}


# ==========================================================
# 3. ANCHOR KIEM TRA VI DU
# ==========================================================

EXPECTED_ANCHORS = {

    "GF4-007-T02": ["即将"],
    "GF4-007-T03": ["急忙"],
    "GF4-007-T04": ["渐渐"],
    "GF4-007-T05": ["尽快"],

    "GF4-008-T01": ["一再"],
    "GF4-008-T02": ["再三"],

    "GF4-009-T01": ["却"],
    "GF4-010-T01": ["未必"],

    "GF4-011-T01": ["几乎"],
    "GF4-011-T02": ["似乎"],

    "GF4-012-T01": ["的确"],
    "GF4-012-T02": ["反而"],
    "GF4-012-T03": ["还"],
    "GF4-012-T04": ["竟然"],
    "GF4-012-T05": ["究竟"],

    "GF4-013-T01": ["自"],
    "GF4-014-T01": ["对于"],
    "GF4-015-T01": ["关于"],
    "GF4-016-T01": ["替"],
    "GF4-017-T01": ["根据"],
}


# ==========================================================
# 4. HAM HO TRO
# ==========================================================

def clean(value):

    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def normalize(value):

    return clean(value).casefold()


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

        fields = (
            reader.fieldnames
            or []
        )

        rows = list(reader)

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
# 5. MAIN
# ==========================================================

def main():

    print("=" * 80)

    print(
        "BUOC 15C - BIEN SOAN NGU PHAP "
        "HSK4 BATCH 2"
    )

    print("=" * 80)

    print(
        "NOI DUNG MOC HAN - KHONG GHI SQL"
    )

    # ======================================================
    # 1. KHOA CAC SNAPSHOT
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT"
    )

    plan_hash = sha256_file(
        PLAN_FILE
    )

    batch01_hash = sha256_file(
        BATCH01_REVIEWED
    )

    print(
        "PLAN SHA256:"
    )

    print(
        plan_hash
    )

    print(
        "BATCH 01 REVIEWED SHA256:"
    )

    print(
        batch01_hash
    )

    if (
        plan_hash
        != EXPECTED_PLAN_SHA256
    ):

        raise RuntimeError(
            "Plan Buoc 14 da thay doi."
        )

    if (
        batch01_hash
        != EXPECTED_BATCH01_SHA256
    ):

        raise RuntimeError(
            "Reviewed Batch 01 da thay doi."
        )

    print(
        "PASS: cac snapshot khong thay doi."
    )

    # ======================================================
    # 2. DOC PLAN
    # ======================================================

    print(
        "\n[2] DOC PLAN 114 MUC"
    )

    fields, plan = read_csv(
        PLAN_FILE
    )

    if (
        len(plan)
        != EXPECTED_PLAN_TOTAL
    ):

        raise RuntimeError(
            "Plan khong con dung 114 muc."
        )

    print(
        "Tong plan:",
        len(plan),
    )

    # ======================================================
    # 3. KIEM TRA BATCH 01
    # ======================================================

    _, previous_rows = read_csv(
        BATCH01_REVIEWED
    )

    if (
        len(previous_rows)
        != EXPECTED_PREVIOUS_TOTAL
    ):

        raise RuntimeError(
            "Reviewed Batch 01 "
            "khong con dung 20 muc."
        )

    previous_ids = {
        clean(
            row.get(
                "MaDonViGiangDay"
            )
        )
        for row in previous_rows
    }

    print(
        "Batch 01 da review:",
        len(previous_ids),
    )

    # ======================================================
    # 4. LAY DON VI 21 -> 40
    # ======================================================

    print(
        "\n[3] LAY BATCH 2"
    )

    batch = plan[
        BATCH_START:BATCH_END
    ]

    if (
        len(batch)
        != EXPECTED_BATCH_TOTAL
    ):

        raise RuntimeError(
            "Khong lay duoc du 20 muc batch 2."
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

    print(
        "So muc:",
        len(batch),
    )

    print(
        "Tu:",
        plan_ids[0],
    )

    print(
        "Den:",
        plan_ids[-1],
    )

    if (
        plan_ids
        != content_ids
    ):

        print(
            "\nID PLAN:"
        )

        for value in plan_ids:
            print(
                " ",
                value
            )

        print(
            "\nID CONTENT:"
        )

        for value in content_ids:
            print(
                " ",
                value
            )

        raise RuntimeError(
            "CONTENT batch 2 "
            "khong khop plan."
        )

    if (
        set(plan_ids)
        & previous_ids
    ):

        raise RuntimeError(
            "Batch 2 bi giao voi Batch 1."
        )

    print(
        "PASS: 20 ID dung va "
        "khong trung Batch 1."
    )

    # ======================================================
    # 5. TAO NOI DUNG
    # ======================================================

    print(
        "\n[4] TAO NOI DUNG GIANG DAY"
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
                "noi dung chua day du."
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
    # 6. VALIDATE
    # ======================================================

    print(
        "\n[5] KIEM TRA NOI DUNG"
    )

    if len(result) != EXPECTED_BATCH_TOTAL:

        raise RuntimeError(
            "Batch 2 khong dung 20 muc."
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

    required_fields = [
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
    ]

    for row in result:

        code = row[
            "MaDonViGiangDay"
        ]

        for field in required_fields:

            if not clean(
                row.get(field)
            ):

                raise RuntimeError(
                    f"{code}: rong {field}"
                )

        if (
            clean(
                row.get("MaNguon")
            )
            != "1004"
        ):

            raise RuntimeError(
                f"{code}: MaNguon != 1004."
            )

    # ------------------------------------------------------
    # Vi du phai co anchor
    # ------------------------------------------------------

    anchor_errors = []

    for row in result:

        code = row[
            "MaDonViGiangDay"
        ]

        sentence = row[
            "ViDuTiengTrung"
        ]

        anchors = (
            EXPECTED_ANCHORS[
                code
            ]
        )

        if not any(
            anchor in sentence
            for anchor in anchors
        ):

            anchor_errors.append(
                code
            )

    if anchor_errors:

        raise RuntimeError(
            "Vi du khong chua anchor: "
            + ", ".join(
                anchor_errors
            )
        )

    # ------------------------------------------------------
    # Vi du Trung phai co dau cau
    # ------------------------------------------------------

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
            + ", ".join(
                bad_zh
            )
        )

    # ------------------------------------------------------
    # Pinyin khong duoc co Hanzi
    # ------------------------------------------------------

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
            "Pinyin con Hanzi: "
            + ", ".join(
                bad_pinyin
            )
        )

    # ------------------------------------------------------
    # TenCauTruc khong trung trong batch
    # ------------------------------------------------------

    normalized_titles = [
        normalize(
            row[
                "TenCauTruc"
            ]
        )
        for row in result
    ]

    if len(
        set(normalized_titles)
    ) != EXPECTED_BATCH_TOTAL:

        raise RuntimeError(
            "TenCauTruc bi trung trong Batch 2."
        )

    # ------------------------------------------------------
    # Vi du khong trung
    # ------------------------------------------------------

    examples = [
        clean(
            row[
                "ViDuTiengTrung"
            ]
        )
        for row in result
    ]

    if len(
        set(examples)
    ) != EXPECTED_BATCH_TOTAL:

        raise RuntimeError(
            "ViDuTiengTrung bi trung."
        )

    print(
        "PASS: 20/20 noi dung day du."
    )

    print(
        "PASS: 20/20 vi du "
        "co anchor ngu phap."
    )

    print(
        "PASS: Pinyin khong co Hanzi."
    )

    print(
        "PASS: TenCauTruc khong trung."
    )

    print(
        "PASS: ViDuTiengTrung khong trung."
    )

    # ======================================================
    # 7. PREVIEW
    # ======================================================

    print(
        "\n[6] PREVIEW BATCH 2"
    )

    for index, row in enumerate(
        result,
        start=21,
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
    # 8. GHI FILE
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

    # ======================================================
    # 9. SUMMARY
    # ======================================================

    summary = {

        "status":
            "PASS",

        "batch":
            2,

        "vi_tri_plan":
            "21-40",

        "tong_plan":
            len(plan),

        "da_review_truoc_do":
            len(previous_ids),

        "tong_batch":
            len(result),

        "tong_da_bien_soan_sau_batch":
            (
                len(previous_ids)
                + len(result)
            ),

        "con_lai":
            (
                len(plan)
                - len(previous_ids)
                - len(result)
            ),

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

        "batch01_reviewed_sha256":
            batch01_hash,

        "output_sha256":
            output_hash,

        "da_ghi_sql":
            False,

        "da_gan_bai_hoc":
            False,

        "da_publish":
            False,
    }

    if SUMMARY.exists():

        raise FileExistsError(
            f"Da ton tai file:\n{SUMMARY}"
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
    # 10. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 80
    )

    print(
        "BIEN SOAN HSK4 BATCH 2 THANH CONG"
    )

    print("=" * 80)

    print(
        "Batch 1 da review:",
        len(previous_ids),
        "/ 114",
    )

    print(
        "Batch 2 vua bien soan:",
        len(result),
        "/ 20",
    )

    print(
        "Tong da co noi dung:",
        len(previous_ids)
        + len(result),
        "/ 114",
    )

    print(
        "Con lai:",
        len(plan)
        - len(previous_ids)
        - len(result),
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
        "Trang thai: "
        "ban_nhap / CHO_REVIEW"
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

    print(
        "CHUA PUBLISH."
    )

    print("=" * 80)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print("\nLOI:")
        print(error)

        raise SystemExit(1)