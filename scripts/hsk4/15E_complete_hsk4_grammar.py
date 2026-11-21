# -*- coding: utf-8 -*-
"""
BUOC 15E - HOAN THIEN TOAN BO NOI DUNG NGU PHAP HSK4

Muc tieu:
- Khoa plan 114 don vi giang day tu Buoc 14.
- Khoa 20 muc Batch 01 da review.
- Khoa 20 muc Batch 02 da review.
- Bien soan + review 74 muc con lai.
- Ghep thanh 114/114 muc.
- Kiem tra toan bo truoc khi chuyen sang Chu Han / BaiHoc.

QUAN TRONG:
- 76 = diem chuan GF0025-2021 HSK4.
- 114 = don vi giang day cua Moc Han sau khi tach.
- Noi dung Trung trong plan truy vet GF0025.
- MoTa/CachDung/ViDu la noi dung giang day Moc Han bien soan.

KHONG GHI SQL.
KHONG GAN BAI HOC.
KHONG PUBLISH.
"""

import csv
import hashlib
import json
import re
from collections import Counter
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

BATCH01_FILE = (
    DATA_DIR
    / "grammar_hsk4_teaching_reviewed_batch01.csv"
)

BATCH02_FILE = (
    DATA_DIR
    / "grammar_hsk4_teaching_reviewed_batch02.csv"
)

REMAINING_FILE = (
    DATA_DIR
    / "grammar_hsk4_teaching_reviewed_remaining74.csv"
)

FINAL_FILE = (
    DATA_DIR
    / "grammar_hsk4_teaching_final_114.csv"
)

SUMMARY_FILE = (
    DATA_DIR
    / "grammar_hsk4_teaching_final_114_summary.json"
)


EXPECTED_PLAN_SHA256 = (
    "5a213b92fe25c2947c25bb4d00536425"
    "aa0a4d315f454b462f4b4fd59835088f"
)

EXPECTED_BATCH01_SHA256 = (
    "81e6f0fcb9ddf8e16a71abb3b1aa5094"
    "fb3c0671f5063b25c01c2c7b311b23e6"
)

EXPECTED_BATCH02_SHA256 = (
    "1e9c53fa5192a1ceaf4e89b1a9e3441f"
    "ad52f15bbc22d93250b8f09c383f6f6f"
)


EXPECTED_PLAN_TOTAL = 114
EXPECTED_STANDARD_POINTS = 76
EXPECTED_REVIEWED_PREVIOUS = 40
EXPECTED_REMAINING = 74

SOURCE_ID = 1004


OUTPUT_FIELDS = [
    "MaDonViGiangDay",
    "MaMucNguPhapChuan",
    "SoThuTuChuan",
    "SoThuTuNguon",

    "ThuTuTrongDiemChuan",
    "SoMucGiangDayCuaDiemChuan",

    "QuyetDinhCuoi",
    "LoaiTach",

    "NhomLonTrung",
    "NhomConTrung",
    "ChiTietTrung",
    "NoiDungChuanTrung",

    "DuongDanNguon",
    "NhanDonViNguonTrung",
    "CanhBaoNguon",

    "TenCauTruc",
    "MoTa",
    "CachDung",

    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",

    "MaNguon",
    "TrangThai",
    "TrangThaiKiemDuyet",

    "KetQuaReview",
    "GhiChuReview",
]


# ==========================================================
# 2. NOI DUNG 74 MUC CON LAI
# ==========================================================
#
# Bat dau:
#   GF4-018-T01
#
# Ket thuc:
#   GF4-076-T01
#
# Thu tu PHẢI trung voi dong 41 -> 114
# trong plan Buoc 14.
#
# ==========================================================

CONTENT_REMAINING = {

    # ======================================================
    # GF4-018
    # ======================================================

    "GF4-018-T01": (
        "作为 + thân phận/vai trò",

        (
            "作为 là giới từ dùng để nêu thân phận, tư cách "
            "hoặc vai trò mà một người hay sự vật đảm nhiệm."
        ),

        (
            "作为 + danh từ/cụm danh từ chỉ thân phận hoặc "
            "vai trò, sau đó là mệnh đề chính."
        ),

        "作为老师，他很关心学生。",

        "Zuòwéi lǎoshī, tā hěn guānxīn xuéshēng.",

        (
            "Là một giáo viên, anh ấy rất quan tâm "
            "đến học sinh."
        ),
    ),

    # ======================================================
    # GF4-019
    # ======================================================

    "GF4-019-T01": (
        "A 并 B",

        (
            "并 là liên từ dùng để nối hai động tác, tính chất "
            "hoặc nội dung có quan hệ song song hay bổ sung."
        ),

        (
            "A + 并 + B; A và B thường có chức năng "
            "ngữ pháp tương đương."
        ),

        "我们要认真研究并解决这个问题。",

        (
            "Wǒmen yào rènzhēn yánjiū bìng "
            "jiějué zhège wèntí."
        ),

        (
            "Chúng ta cần nghiêm túc nghiên cứu và "
            "giải quyết vấn đề này."
        ),
    ),

    "GF4-019-T02": (
        "A、B以及C",

        (
            "以及 là liên từ dùng để nối các từ hoặc cụm từ "
            "trong quan hệ liệt kê, thường đặt trước thành phần cuối."
        ),

        "A、B + 以及 + C.",

        "会议讨论了时间、地点以及人员安排。",

        (
            "Huìyì tǎolùn le shíjiān, dìdiǎn "
            "yǐjí rényuán ānpái."
        ),

        (
            "Cuộc họp đã thảo luận về thời gian, địa điểm "
            "và việc sắp xếp nhân sự."
        ),
    ),

    # ======================================================
    # GF4-020
    # ======================================================

    "GF4-020-T01": (
        "此外，……",

        (
            "此外 dùng để bổ sung thêm một thông tin hoặc "
            "một ý bên cạnh nội dung đã nêu trước đó."
        ),

        (
            "Mệnh đề trước. 此外，+ mệnh đề bổ sung."
        ),

        "此外，我们还需要准备一些材料。",

        (
            "Cǐwài, wǒmen hái xūyào "
            "zhǔnbèi yìxiē cáiliào."
        ),

        (
            "Ngoài ra, chúng ta còn cần chuẩn bị "
            "một số tài liệu."
        ),
    ),

    "GF4-020-T02": (
        "而（liên từ）",

        (
            "而 dùng để nối hai vế có quan hệ đối chiếu, "
            "chuyển ý hoặc song song tùy ngữ cảnh."
        ),

        (
            "Vế 1 + 而 + vế 2; quan hệ cụ thể được xác định "
            "theo nghĩa của hai vế."
        ),

        "北方比较干燥，而南方比较湿润。",

        (
            "Běifāng bǐjiào gānzào, "
            "ér nánfāng bǐjiào shīrùn."
        ),

        (
            "Miền Bắc tương đối khô, còn miền Nam "
            "tương đối ẩm."
        ),
    ),

    "GF4-020-T03": (
        "而是 + thành phần được khẳng định",

        (
            "而是 thường xuất hiện sau một thành phần phủ định "
            "để chuyển sang nội dung được khẳng định."
        ),

        (
            "Thường gặp: 不是A，而是B."
        ),

        "这不是运气，而是努力的结果。",

        (
            "Zhè bú shì yùnqi, érshì "
            "nǔlì de jiéguǒ."
        ),

        (
            "Đây không phải là may mắn, mà là kết quả "
            "của sự nỗ lực."
        ),
    ),

    "GF4-020-T04": (
        "既然 + mệnh đề（liên từ）",

        (
            "既然 đưa ra một sự thật hoặc điều kiện đã được "
            "thừa nhận để làm cơ sở cho nhận xét hay "
            "hành động tiếp theo."
        ),

        (
            "既然 + mệnh đề; thường đi với 就、也、那么 "
            "ở vế sau."
        ),

        "既然你决定了，就去做吧。",

        (
            "Jìrán nǐ juédìng le, "
            "jiù qù zuò ba."
        ),

        (
            "Vì bạn đã quyết định rồi thì hãy làm đi."
        ),
    ),

    "GF4-020-T05": (
        "可见（liên từ）",

        (
            "可见 dùng để dẫn ra một kết luận có thể suy ra "
            "từ thông tin hoặc hiện tượng đã nêu trước đó."
        ),

        (
            "Vế nêu căn cứ + 可见 + kết luận."
        ),

        "他没来，可见他还不知道这件事。",

        (
            "Tā méi lái, kějiàn tā hái "
            "bù zhīdào zhè jiàn shì."
        ),

        (
            "Anh ấy không đến, có thể thấy là anh ấy "
            "vẫn chưa biết việc này."
        ),
    ),

    "GF4-020-T06": (
        "甚至（liên từ）",

        (
            "甚至 dùng để bổ sung một trường hợp có mức độ "
            "cao hơn hoặc bất ngờ hơn so với nội dung trước."
        ),

        (
            "Nội dung trước + 甚至 + "
            "thành phần/mệnh đề được nhấn mạnh."
        ),

        "这个问题很难，甚至老师也要想一想。",

        (
            "Zhège wèntí hěn nán, shènzhì "
            "lǎoshī yě yào xiǎng yì xiǎng."
        ),

        (
            "Vấn đề này rất khó, đến cả giáo viên "
            "cũng phải suy nghĩ một chút."
        ),
    ),

    "GF4-020-T07": (
        "假如（liên từ）",

        (
            "假如 dùng để nêu một giả thiết làm điều kiện "
            "cho kết quả hoặc hành động ở vế sau."
        ),

        (
            "假如 + mệnh đề giả thiết; "
            "vế sau thường có 就、那么..."
        ),

        "假如明天下雨，我们就不去爬山。",

        (
            "Jiǎrú míngtiān xiàyǔ, "
            "wǒmen jiù bú qù páshān."
        ),

        (
            "Nếu ngày mai trời mưa, chúng ta sẽ "
            "không đi leo núi."
        ),
    ),

    "GF4-020-T08": (
        "总之，……",

        (
            "总之 dùng để tổng kết hoặc khái quát lại "
            "những điều đã trình bày trước đó."
        ),

        (
            "总之 thường đứng đầu câu hoặc đầu vế kết luận."
        ),

        "总之，我们应该先把问题解决。",

        (
            "Zǒngzhī, wǒmen yīnggāi "
            "xiān bǎ wèntí jiějué."
        ),

        (
            "Tóm lại, chúng ta nên giải quyết vấn đề trước."
        ),
    ),

    # ======================================================
    # GF4-021
    # ======================================================

    "GF4-021-T01": (
        "像……似的",

        (
            "似的 là trợ từ dùng sau từ hoặc cụm từ để biểu thị "
            "sự giống nhau, thường xuất hiện trong cấu trúc so sánh."
        ),

        "像/好像 + danh từ/cụm từ + 似的.",

        "天上的云像棉花似的。",

        "Tiānshàng de yún xiàng miánhua shìde.",

        "Mây trên trời giống như bông vậy.",
    ),

    # ======================================================
    # GF4-022
    # ======================================================

    "GF4-022-T01": (
        "啊（thán từ）",

        (
            "啊 khi dùng làm thán từ có thể biểu thị sự ngạc nhiên, "
            "nhận ra, cảm thán hoặc phản ứng tức thời của người nói."
        ),

        (
            "啊 có thể đứng độc lập hoặc ở đầu câu; sắc thái "
            "cụ thể phụ thuộc ngữ cảnh và ngữ điệu."
        ),

        "啊，原来是你！",

        "À, yuánlái shì nǐ!",

        "À, hóa ra là bạn!",
    ),

    # ======================================================
    # GF4-023
    # ======================================================

    "GF4-023-T01": (
        "大A大B",

        (
            "大A大B là kiểu cấu trúc bốn âm tiết, trong đó 大 "
            "kết hợp với hai động từ hoặc tính chất để nhấn mạnh "
            "mức độ hoặc cách thức mạnh."
        ),

        (
            "大 + A + 大 + B; "
            "A và B thường có quan hệ song song."
        ),

        "过节时大家大吃大喝。",

        "Guòjié shí dàjiā dàchī dàhē.",

        (
            "Vào dịp lễ mọi người ăn uống rất thịnh soạn."
        ),
    ),

    # ======================================================
    # GF4-024
    # ======================================================

    "GF4-024-T01": (
        "一A一B",

        (
            "一A一B là kiểu cấu trúc bốn âm tiết gồm hai "
            "thành phần song song, thường miêu tả hai hành động "
            "hoặc trạng thái luân phiên hay phối hợp."
        ),

        (
            "一 + A + 一 + B; "
            "ý nghĩa cụ thể phụ thuộc vào cặp A/B."
        ),

        "他们一唱一和，配合得很好。",

        (
            "Tāmen yí chàng yí hè, "
            "pèihé de hěn hǎo."
        ),

        (
            "Họ kẻ xướng người họa, phối hợp rất ăn ý."
        ),
    ),

    # ======================================================
    # GF4-025
    # ======================================================

    "GF4-025-T01": (
        "看来 + mệnh đề",

        (
            "看来 dùng để đưa ra nhận định hoặc suy đoán "
            "của người nói dựa trên tình hình quan sát được."
        ),

        (
            "看来 + mệnh đề; có thể hiểu là "
            "“xem ra, có vẻ”."
        ),

        "看来今天要下雨了。",

        "Kànlái jīntiān yào xiàyǔ le.",

        "Xem ra hôm nay trời sắp mưa.",
    ),

    # ======================================================
    # GF4-026
    # ======================================================

    "GF4-026-T01": (
        "来得及 / 来不及 + động từ",

        (
            "来得及 biểu thị còn đủ thời gian để làm một việc; "
            "来不及 biểu thị không còn đủ thời gian."
        ),

        (
            "来得及/来不及 + động từ hoặc cụm động từ; "
            "cũng có thể dùng độc lập theo ngữ cảnh."
        ),

        "现在出发还来得及，再晚十分钟就来不及了。",

        (
            "Xiànzài chūfā hái láidejí, "
            "zài wǎn shí fēnzhōng jiù láibují le."
        ),

        (
            "Bây giờ xuất phát vẫn còn kịp, muộn thêm "
            "mười phút nữa thì sẽ không kịp."
        ),
    ),

    # ======================================================
    # GF4-027
    # ======================================================

    "GF4-027-T01": (
        "说不定 + mệnh đề",

        (
            "说不定 biểu thị khả năng chưa chắc chắn, "
            "tương đương với “có lẽ, biết đâu”."
        ),

        "说不定 + mệnh đề hoặc thành phần vị ngữ.",

        "他今天说不定会来。",

        "Tā jīntiān shuōbudìng huì lái.",

        "Hôm nay biết đâu anh ấy sẽ đến.",
    ),

    # ======================================================
    # GF4-028
    # ======================================================

    "GF4-028-T01": (
        "一般来说，……",

        (
            "一般来说 dùng để nêu một nhận xét mang tính "
            "khái quát hoặc tình hình thường thấy."
        ),

        (
            "一般来说 thường đặt ở đầu câu, "
            "sau đó là nhận định chung."
        ),

        "一般来说，早睡早起对身体有好处。",

        (
            "Yìbān lái shuō, zǎo shuì zǎo qǐ "
            "duì shēntǐ yǒu hǎochu."
        ),

        (
            "Nói chung, ngủ sớm dậy sớm có lợi cho sức khỏe."
        ),
    ),

    # ======================================================
    # GF4-029
    # ======================================================

    "GF4-029-T01": (
        "一+量词+比+一+量词",

        (
            "Cấu trúc này biểu thị mức độ thay đổi tăng dần "
            "hoặc giảm dần qua từng đơn vị."
        ),

        (
            "一 + lượng từ + 比 + 一 + lượng từ "
            "+ tính từ/cụm vị ngữ."
        ),

        "天气一天比一天冷。",

        "Tiānqì yì tiān bǐ yì tiān lěng.",

        "Thời tiết ngày càng lạnh hơn.",
    ),

    # ======================================================
    # GF4-030
    # ======================================================

    "GF4-030-T01": (
        "（自）……以来",

        (
            "以来 biểu thị khoảng thời gian tính từ một mốc "
            "trong quá khứ cho đến hiện tại hoặc một mốc "
            "được nói đến."
        ),

        (
            "（自）+ mốc thời gian + 以来 + mệnh đề."
        ),

        "自去年以来，他一直住在北京。",

        (
            "Zì qùnián yǐlái, "
            "tā yìzhí zhù zài Běijīng."
        ),

        (
            "Kể từ năm ngoái, anh ấy vẫn luôn sống ở Bắc Kinh."
        ),
    ),

    # ======================================================
    # GF4-031
    # ======================================================

    "GF4-031-T01": (
        "由……组成",

        (
            "由……组成 dùng để nói một chỉnh thể được "
            "cấu thành bởi những thành phần nào."
        ),

        "Chủ thể + 由 + thành phần + 组成.",

        "这个小组由五名学生组成。",

        (
            "Zhège xiǎozǔ yóu wǔ míng "
            "xuéshēng zǔchéng."
        ),

        "Nhóm này gồm năm học sinh.",
    ),

    # ======================================================
    # GF4-032
    # ======================================================

    "GF4-032-T01": (
        "在……方面",

        (
            "在……方面 dùng để giới hạn nhận xét hoặc "
            "hành động trong một phương diện cụ thể."
        ),

        (
            "在 + danh từ/cụm danh từ + 方面 + mệnh đề."
        ),

        "他在语言学习方面很有经验。",

        (
            "Tā zài yǔyán xuéxí fāngmiàn "
            "hěn yǒu jīngyàn."
        ),

        (
            "Anh ấy rất có kinh nghiệm trong phương diện "
            "học ngôn ngữ."
        ),
    ),

    # ======================================================
    # GF4-033
    # ======================================================

    "GF4-033-T01": (
        "在……上/下/中",

        (
            "Cấu trúc 在……上/下/中 có thể dùng để xác định "
            "phạm vi, phương diện, điều kiện hoặc hoàn cảnh "
            "mà nhận xét được áp dụng."
        ),

        (
            "在 + danh từ/cụm danh từ + 上/下/中 + mệnh đề; "
            "lựa chọn 上、下、中 phụ thuộc cách kết hợp "
            "và ngữ cảnh."
        ),

        "在学习上，他一直很认真。",

        (
            "Zài xuéxí shàng, "
            "tā yìzhí hěn rènzhēn."
        ),

        (
            "Trong học tập, anh ấy luôn rất nghiêm túc."
        ),
    ),

    # ======================================================
    # GF4-034
    # ======================================================

    "GF4-034-T01": (
        "Cụm chủ-vị làm chủ ngữ",

        (
            "Một cụm có quan hệ chủ ngữ-vị ngữ có thể đứng "
            "ở vị trí chủ ngữ của cả câu."
        ),

        (
            "Cụm chủ-vị + vị ngữ của câu chính."
        ),

        "身体健康最重要。",

        "Shēntǐ jiànkāng zuì zhòngyào.",

        "Sức khỏe tốt là điều quan trọng nhất.",
    ),

    # ======================================================
    # GF4-035
    # ======================================================

    "GF4-035-T01": (
        "Chủ ngữ chịu tác động（受事主语）",

        (
            "Trong một số câu, chủ ngữ là đối tượng chịu "
            "tác động của hành động chứ không phải người "
            "thực hiện hành động."
        ),

        (
            "Chủ ngữ chịu tác động + động từ/cụm động từ; "
            "câu có thể không dùng 被."
        ),

        "作业写完了。",

        "Zuòyè xiěwán le.",

        "Bài tập đã được làm xong.",
    ),

    # ======================================================
    # GF4-036
    # ======================================================

    "GF4-036-T01": (
        "Nhiều định ngữ trước danh từ（多项定语）",

        (
            "Một danh từ có thể đồng thời nhận nhiều định ngữ "
            "để bổ sung các thông tin như thời gian, sở hữu, "
            "chỉ định, số lượng hoặc đặc điểm."
        ),

        (
            "Nhiều định ngữ + 的/ lượng từ + danh từ trung tâm; "
            "trật tự cần dựa vào quan hệ nghĩa tự nhiên "
            "của các định ngữ."
        ),

        "我昨天买的那本中文书很有意思。",

        (
            "Wǒ zuótiān mǎi de nà běn "
            "Zhōngwén shū hěn yǒuyìsi."
        ),

        (
            "Cuốn sách tiếng Trung mà tôi mua hôm qua "
            "rất thú vị."
        ),
    ),

    # ======================================================
    # GF4-037
    # ======================================================

    "GF4-037-T01": (
        "V + 上/出/起/下（nghĩa kết quả）",

        (
            "Một số bổ ngữ xu hướng như 上、出、起、下 có thể "
            "được dùng với nghĩa mở rộng để biểu thị kết quả "
            "của hành động thay vì hướng di chuyển thực tế."
        ),

        (
            "Động từ + 上/出/起/下; cần học nghĩa kết hợp "
            "cụ thể của từng động từ."
        ),

        "我终于想出了一个好办法。",

        (
            "Wǒ zhōngyú xiǎngchū le "
            "yí ge hǎo bànfǎ."
        ),

        (
            "Cuối cùng tôi đã nghĩ ra một cách hay."
        ),
    ),

    # ======================================================
    # GF4-038 - BA
    # ======================================================

    "GF4-038-T01": (
        "把字句2（1）：V（+一/了）V",

        (
            "Mẫu này dùng 把 để đưa đối tượng bị xử lý lên trước "
            "và vị ngữ dùng dạng động từ lặp lại hoặc V一V/V了V."
        ),

        (
            "Chủ ngữ + 把 + tân ngữ + "
            "động từ（+一/了）+ động từ."
        ),

        "请把这篇文章读一读。",

        (
            "Qǐng bǎ zhè piān wénzhāng "
            "dú yi dú."
        ),

        (
            "Hãy đọc bài viết này một lượt."
        ),
    ),

    "GF4-038-T02": (
        "把字句2（2）：（给）+V+了/着",

        (
            "Mẫu này dùng 把 để nêu đối tượng bị xử lý; "
            "trước động từ có thể thêm 给 để tăng sắc thái "
            "khẩu ngữ, và cuối cụm động từ có 了 hoặc 着 "
            "theo cấu trúc."
        ),

        (
            "Chủ ngữ + 把 + tân ngữ（+给）+ "
            "động từ + 了/着."
        ),

        "我把钥匙给丢了。",

        "Wǒ bǎ yàoshi gěi diū le.",

        "Tôi làm mất chìa khóa rồi.",
    ),

    "GF4-038-T03": (
        "把字句2（3）：V + động lượng/thời lượng",

        (
            "Mẫu này dùng 把 khi sau động từ có bổ ngữ "
            "số lượng chỉ số lần hoặc thời lượng của hành động."
        ),

        (
            "Chủ ngữ + 把 + tân ngữ + động từ + "
            "động lượng bổ ngữ/thời lượng bổ ngữ."
        ),

        "我把这篇文章读了两遍。",

        (
            "Wǒ bǎ zhè piān wénzhāng "
            "dú le liǎng biàn."
        ),

        (
            "Tôi đã đọc bài viết này hai lần."
        ),
    ),

    # ======================================================
    # GF4-039
    # ======================================================

    "GF4-039-T01": (
        "S + 被 + V + thành phần khác",

        (
            "被动句2 dùng 被 để nhấn mạnh đối tượng chịu tác động; "
            "tác nhân gây ra hành động có thể không xuất hiện."
        ),

        (
            "Chủ ngữ chịu tác động + 被 + "
            "động từ + thành phần khác."
        ),

        "我的手机被偷了。",

        "Wǒ de shǒujī bèi tōu le.",

        "Điện thoại của tôi bị lấy trộm.",
    ),

    # ======================================================
    # GF4-040 - TON HIEN
    # ======================================================

    "GF4-040-T01": (
        "存现句2：biểu thị sự xuất hiện",

        (
            "Mẫu tồn hiện này dùng địa điểm ở đầu câu để nói "
            "một người hoặc vật xuất hiện tại nơi đó."
        ),

        (
            "Từ chỉ nơi chốn + động từ + "
            "bổ ngữ xu hướng/kết quả +（了）+ "
            "cụm số lượng + người/vật."
        ),

        "门口走进来一个人。",

        "Ménkǒu zǒu jìnlái yí ge rén.",

        "Ở cửa có một người đi vào.",
    ),

    "GF4-040-T02": (
        "存现句2：biểu thị sự biến mất",

        (
            "Mẫu tồn hiện này dùng địa điểm ở đầu câu để nói "
            "một người hoặc vật rời đi hoặc biến mất khỏi nơi đó."
        ),

        (
            "Từ chỉ nơi chốn + động từ + bổ ngữ kết quả + "
            "（了）+ cụm số lượng + người/vật."
        ),

        "院子里跑掉了一只猫。",

        (
            "Yuànzi li pǎodiào le "
            "yì zhī māo."
        ),

        (
            "Trong sân có một con mèo chạy mất."
        ),
    ),

    # ======================================================
    # GF4-041 - KIEM NGU
    # ======================================================

    "GF4-041-T01": (
        "兼语句2：biểu thị khen/chê",

        (
            "Trong mẫu kiêm ngữ này, tân ngữ của động từ như "
            "表扬、批评 đồng thời là chủ thể của thành phần "
            "vị ngữ phía sau."
        ),

        (
            "Chủ ngữ + 表扬/批评 + tân ngữ 1 + "
            "động từ/cụm vị ngữ + tân ngữ 2 nếu có."
        ),

        "老师表扬他学习认真。",

        (
            "Lǎoshī biǎoyáng tā "
            "xuéxí rènzhēn."
        ),

        (
            "Giáo viên khen anh ấy học tập nghiêm túc."
        ),
    ),

    "GF4-041-T02": (
        "兼语句2：biểu thị gọi tên/xác định",

        (
            "Trong mẫu này, một người hoặc vật được gọi, coi, "
            "chọn hay xác định là một thân phận hoặc vai trò nào đó."
        ),

        (
            "Chủ ngữ + 叫/称（呼）/说/收/选 + "
            "tân ngữ 1 + 做/为/当/是 + tân ngữ 2."
        ),

        "大家选他当班长。",

        "Dàjiā xuǎn tā dāng bānzhǎng.",

        "Mọi người chọn anh ấy làm lớp trưởng.",
    ),

    # ======================================================
    # GF4-042
    # ======================================================

    "GF4-042-T01": (
        "是……的（nhấn mạnh quan điểm/thái độ）",

        (
            "Mẫu 是……的 ở điểm này dùng để nhấn mạnh hoặc "
            "xác nhận quan điểm, thái độ của người nói "
            "đối với một sự việc."
        ),

        (
            "Chủ ngữ + 是 + thành phần biểu thị "
            "quan điểm/thái độ + 的."
        ),

        "我是赞成这个办法的。",

        "Wǒ shì zànchéng zhège bànfǎ de.",

        "Tôi tán thành cách này.",
    ),

    # ======================================================
    # GF4-043
    # ======================================================

    "GF4-043-T01": (
        "不是……，而是……",

        (
            "Cấu trúc này phủ định khả năng hoặc cách hiểu A "
            "và khẳng định B là nội dung đúng."
        ),

        "不是 + A，+ 而是 + B.",

        "他不是不想去，而是没有时间。",

        (
            "Tā bú shì bù xiǎng qù, "
            "érshì méiyǒu shíjiān."
        ),

        (
            "Không phải anh ấy không muốn đi, "
            "mà là không có thời gian."
        ),
    ),

    # ======================================================
    # GF4-044
    # ======================================================

    "GF4-044-T01": (
        "既……，又/也……",

        (
            "既……又/也…… dùng để nêu hai đặc điểm, "
            "trạng thái hoặc hành động cùng tồn tại."
        ),

        "既 + A，+ 又/也 + B.",

        "这家饭店的菜既好吃又便宜。",

        (
            "Zhè jiā fàndiàn de cài "
            "jì hǎochī yòu piányi."
        ),

        (
            "Món ăn của nhà hàng này vừa ngon vừa rẻ."
        ),
    ),

    # ======================================================
    # GF4-045
    # ======================================================

    "GF4-045-T01": (
        "首先……，其次……",

        (
            "首先……其次…… dùng để sắp xếp hai bước, "
            "hai lý do hoặc hai mặt theo thứ tự trình bày."
        ),

        (
            "首先 + nội dung thứ nhất，"
            "其次 + nội dung thứ hai."
        ),

        "首先我们要了解情况，其次再决定怎么办。",

        (
            "Shǒuxiān wǒmen yào liǎojiě qíngkuàng, "
            "qícì zài juédìng zěnme bàn."
        ),

        (
            "Trước tiên chúng ta cần tìm hiểu tình hình, "
            "tiếp theo mới quyết định làm thế nào."
        ),
    ),

    # ======================================================
    # GF4-046
    # ======================================================

    "GF4-046-T01": (
        "……，于是……",

        (
            "于是 nối kết quả với tình huống hoặc nguyên nhân "
            "đã xảy ra trước đó, thường nhấn mạnh diễn biến tiếp theo."
        ),

        "Vế trước，+ 于是 + vế kết quả.",

        "天突然下起雨来，于是我们回家了。",

        (
            "Tiān tūrán xià qǐ yǔ lái, "
            "yúshì wǒmen huí jiā le."
        ),

        (
            "Trời đột nhiên đổ mưa, vì thế chúng tôi về nhà."
        ),
    ),

    # ======================================================
    # GF4-047
    # ======================================================

    "GF4-047-T01": (
        "……，甚至……",

        (
            "Mẫu này biểu thị quan hệ tăng tiến: vế sau với "
            "甚至 nêu trường hợp có mức độ cao hơn hoặc "
            "đáng chú ý hơn."
        ),

        "Vế 1，+ 甚至 + vế 2.",

        "他每天都很忙，周末甚至也要工作。",

        (
            "Tā měitiān dōu hěn máng, "
            "zhōumò shènzhì yě yào gōngzuò."
        ),

        (
            "Ngày nào anh ấy cũng rất bận, "
            "thậm chí cuối tuần cũng phải làm việc."
        ),
    ),

    # ======================================================
    # GF4-048
    # ======================================================

    "GF4-048-T01": (
        "或者……，或者……",

        (
            "或者……或者…… dùng để nêu hai hoặc nhiều "
            "khả năng lựa chọn."
        ),

        "或者 + A，或者 + B.",

        "周末我们或者去爬山，或者在家休息。",

        (
            "Zhōumò wǒmen huòzhě qù páshān, "
            "huòzhě zài jiā xiūxi."
        ),

        (
            "Cuối tuần chúng ta hoặc đi leo núi, "
            "hoặc nghỉ ở nhà."
        ),
    ),

    # ======================================================
    # GF4-049
    # ======================================================

    "GF4-049-T01": (
        "……，然而……",

        (
            "然而 biểu thị quan hệ chuyển ý hoặc đối lập "
            "với nội dung vế trước, thường mang sắc thái văn viết."
        ),

        "Vế 1，+ 然而 + vế 2.",

        "他准备得很充分，然而结果并不理想。",

        (
            "Tā zhǔnbèi de hěn chōngfèn, "
            "rán'ér jiéguǒ bìng bù lǐxiǎng."
        ),

        (
            "Anh ấy chuẩn bị rất kỹ, tuy nhiên kết quả "
            "không được như mong muốn."
        ),
    ),

    # ======================================================
    # GF4-050
    # ======================================================

    "GF4-050-T01": (
        "……，否则……",

        (
            "否则 đưa ra kết quả bất lợi sẽ xảy ra nếu "
            "điều kiện hoặc yêu cầu ở vế trước không được thực hiện."
        ),

        (
            "Vế yêu cầu/điều kiện，+ 否则 + kết quả."
        ),

        "你得早点出发，否则会迟到。",

        (
            "Nǐ děi zǎodiǎn chūfā, "
            "fǒuzé huì chídào."
        ),

        (
            "Bạn phải xuất phát sớm hơn, nếu không sẽ bị muộn."
        ),
    ),

    # ======================================================
    # GF4-051
    # ======================================================

    "GF4-051-T01": (
        "假如……，（就）……",

        (
            "Cấu trúc này nêu một giả thiết bằng 假如 "
            "và đưa ra kết quả tương ứng ở vế sau."
        ),

        (
            "假如 + điều kiện giả định，"
            "（就）+ kết quả."
        ),

        "假如你有时间，就来找我吧。",

        (
            "Jiǎrú nǐ yǒu shíjiān, "
            "jiù lái zhǎo wǒ ba."
        ),

        (
            "Nếu bạn có thời gian thì hãy đến tìm tôi."
        ),
    ),

    # ======================================================
    # GF4-052
    # ======================================================

    "GF4-052-T01": (
        "万一……，（就）……",

        (
            "万一 dùng để nêu một khả năng không mong muốn "
            "hoặc có xác suất thấp nhưng cần tính đến."
        ),

        (
            "万一 + tình huống，"
            "（就）+ cách xử lý/kết quả."
        ),

        "万一明天下雨，我们就改天再去。",

        (
            "Wànyī míngtiān xiàyǔ, "
            "wǒmen jiù gǎitiān zài qù."
        ),

        (
            "Nhỡ ngày mai trời mưa thì chúng ta "
            "sẽ đi vào hôm khác."
        ),
    ),

    # ======================================================
    # GF4-053
    # ======================================================

    "GF4-053-T01": (
        "不管……，都/也……",

        (
            "不管……都/也…… biểu thị kết quả ở vế sau "
            "không thay đổi dù điều kiện hoặc tình huống "
            "phía trước là gì."
        ),

        (
            "不管 + điều kiện hoặc từ nghi vấn，"
            "+ 都/也 + kết quả."
        ),

        "不管遇到什么困难，我们都不能放弃。",

        (
            "Bùguǎn yùdào shénme kùnnan, "
            "wǒmen dōu bù néng fàngqì."
        ),

        (
            "Dù gặp khó khăn gì, chúng ta cũng "
            "không được bỏ cuộc."
        ),
    ),

    # ======================================================
    # GF4-054
    # ======================================================

    "GF4-054-T01": (
        "无论……，都/也……",

        (
            "无论……都/也…… biểu thị kết quả không thay đổi "
            "trong mọi trường hợp được nêu; sắc thái thường "
            "trang trọng hơn 不管."
        ),

        (
            "无论 + điều kiện/từ nghi vấn，"
            "+ 都/也 + kết quả."
        ),

        "无论多忙，他都坚持运动。",

        (
            "Wúlùn duō máng, "
            "tā dōu jiānchí yùndòng."
        ),

        (
            "Dù bận đến đâu, anh ấy vẫn kiên trì tập thể dục."
        ),
    ),

    # ======================================================
    # GF4-055
    # ======================================================

    "GF4-055-T01": (
        "既然……，就……",

        (
            "既然……就…… nêu một sự thật đã được thừa nhận "
            "và từ đó đưa ra kết luận, đề nghị hoặc "
            "hành động hợp lý."
        ),

        (
            "既然 + sự thật/tiền đề，"
            "+ 就 + kết luận/hành động."
        ),

        "既然来了，就多待几天吧。",

        (
            "Jìrán lái le, "
            "jiù duō dāi jǐ tiān ba."
        ),

        (
            "Đã đến rồi thì ở thêm vài ngày đi."
        ),
    ),

    # ======================================================
    # GF4-056
    # ======================================================

    "GF4-056-T01": (
        "……，可见……（câu nhân quả）",

        (
            "Mẫu này dùng 可见 để dẫn ra kết luận "
            "được suy luận từ căn cứ ở vế trước."
        ),

        (
            "Căn cứ/hiện tượng，+ 可见 + kết luận."
        ),

        "地上都是湿的，可见刚才下过雨。",

        (
            "Dìshang dōu shì shī de, "
            "kějiàn gāngcái xià guo yǔ."
        ),

        (
            "Mặt đất đều ướt, có thể thấy vừa rồi đã mưa."
        ),
    ),

    # ======================================================
    # GF4-057
    # ======================================================

    "GF4-057-T01": (
        "哪怕……，也/还……",

        (
            "哪怕……也/还…… biểu thị dù điều kiện phía trước "
            "rất bất lợi hoặc cực đoan thì kết quả, ý chí "
            "ở vế sau vẫn không thay đổi."
        ),

        (
            "哪怕 + điều kiện，+ 也/还 + kết quả."
        ),

        "哪怕只有一天时间，我也想去看看。",

        (
            "Nǎpà zhǐyǒu yì tiān shíjiān, "
            "wǒ yě xiǎng qù kànkan."
        ),

        (
            "Dù chỉ có một ngày, tôi vẫn muốn đi xem thử."
        ),
    ),

    # ======================================================
    # GF4-058
    # ======================================================

    "GF4-058-T01": (
        "……，好 + mục đích",

        (
            "好 có thể đứng ở đầu vế sau để giới thiệu "
            "mục đích thuận lợi cho hành động ở vế trước."
        ),

        (
            "Vế hành động，+ 好 + "
            "cụm động từ/mệnh đề chỉ mục đích."
        ),

        "你把地址发给我，好让我找到你。",

        (
            "Nǐ bǎ dìzhǐ fā gěi wǒ, "
            "hǎo ràng wǒ zhǎodào nǐ."
        ),

        (
            "Bạn gửi địa chỉ cho tôi để tôi có thể tìm được bạn."
        ),
    ),

    # ======================================================
    # GF4-059
    # ======================================================

    "GF4-059-T01": (
        "紧缩复句（không dùng từ liên kết）",

        (
            "Một số quan hệ giữa hai vế có thể được diễn đạt "
            "bằng câu ghép rút gọn mà không dùng từ liên kết "
            "rõ ràng; quan hệ nghĩa được suy ra từ ngữ cảnh."
        ),

        (
            "Vế 1 + vế 2, không nhất thiết có关联词; "
            "cần dựa vào nghĩa để hiểu quan hệ giữa hai vế."
        ),

        "你不去我去。",

        "Nǐ bú qù wǒ qù.",

        "Bạn không đi thì tôi đi.",
    ),

    # ======================================================
    # GF4-060
    # ======================================================

    "GF4-060-T01": (
        "不……也……",

        (
            "Mẫu rút gọn 不……也…… biểu thị ngay cả khi "
            "điều kiện phủ định ở vế trước xảy ra, "
            "kết quả ở vế sau vẫn tồn tại."
        ),

        "不 + A，+ 也 + B.",

        "你不说我也知道。",

        "Nǐ bù shuō wǒ yě zhīdào.",

        "Bạn không nói thì tôi cũng biết.",
    ),

    # ======================================================
    # GF4-061
    # ======================================================

    "GF4-061-T01": (
        "Số từ + 来 + lượng từ",

        (
            "来 đặt sau số từ để biểu thị số lượng xấp xỉ, "
            "thường gần với con số được nêu."
        ),

        (
            "Số từ + 来 + lượng từ + danh từ."
        ),

        "今天来了十来个人。",

        (
            "Jīntiān lái le shí lái ge rén."
        ),

        (
            "Hôm nay có khoảng hơn mười người đến."
        ),
    ),

    # ======================================================
    # GF4-062 - SO
    # ======================================================

    "GF4-062-T01": (
        "Cách biểu đạt số thập phân",

        (
            "Số thập phân trong tiếng Trung thường dùng 点 "
            "giữa phần nguyên và phần thập phân, các chữ số "
            "sau 点 được đọc lần lượt."
        ),

        (
            "Phần nguyên + 点 + các chữ số phần thập phân."
        ),

        "这个箱子重三点五公斤。",

        (
            "Zhège xiāngzi zhòng "
            "sān diǎn wǔ gōngjīn."
        ),

        (
            "Chiếc vali này nặng 3,5 ki-lô-gam."
        ),
    ),

    "GF4-062-T02": (
        "Cách biểu đạt phân số",

        (
            "Phân số thường được biểu đạt theo thứ tự "
            "mẫu số + 分之 + tử số."
        ),

        "Mẫu số + 分之 + tử số.",

        "三分之一的学生住在学校。",

        (
            "Sān fēn zhī yī de xuéshēng "
            "zhù zài xuéxiào."
        ),

        (
            "Một phần ba số học sinh sống ở trường."
        ),
    ),

    "GF4-062-T03": (
        "Cách biểu đạt phần trăm",

        (
            "Phần trăm dùng 百分之 đứng trước con số chỉ tỷ lệ."
        ),

        "百分之 + số.",

        "百分之八十的学生通过了考试。",

        (
            "Bǎifēnzhī bāshí de xuéshēng "
            "tōngguò le kǎoshì."
        ),

        (
            "Tám mươi phần trăm học sinh đã "
            "vượt qua kỳ thi."
        ),
    ),

    "GF4-062-T04": (
        "Cách biểu đạt bội số",

        (
            "倍 dùng để biểu thị quan hệ bội số "
            "giữa hai số lượng."
        ),

        (
            "A + 是 + B + 的 + số + 倍; "
            "cách diễn đạt cụ thể có thể thay đổi "
            "theo loại so sánh."
        ),

        "这条河的长度是那条河的两倍。",

        (
            "Zhè tiáo hé de chángdù shì "
            "nà tiáo hé de liǎng bèi."
        ),

        (
            "Chiều dài con sông này gấp hai lần "
            "con sông kia."
        ),
    ),

    # ======================================================
    # GF4-063
    # ======================================================

    "GF4-063-T01": (
        "Câu hỏi tu từ bằng đại từ nghi vấn",

        (
            "Đại từ nghi vấn như 谁、什么、怎么 có thể dùng "
            "trong câu hỏi tu từ để nhấn mạnh một khẳng định "
            "hoặc phủ định, không nhất thiết yêu cầu câu trả lời."
        ),

        (
            "Dùng đại từ nghi vấn trong câu có ngữ điệu hỏi; "
            "ý nghĩa thực tế được hiểu theo ngữ cảnh tu từ."
        ),

        "谁不知道这件事呢？",

        "Shéi bù zhīdào zhè jiàn shì ne?",

        "Ai mà chẳng biết việc này?",
    ),

    # ======================================================
    # GF4-064
    # ======================================================

    "GF4-064-T01": (
        "Phủ định kép để nhấn mạnh",

        (
            "Hai yếu tố phủ định cùng xuất hiện có thể tạo nghĩa "
            "khẳng định mạnh hoặc biểu thị sự bắt buộc."
        ),

        (
            "Các dạng thường gặp gồm 不能不、不可能不、没有不...; "
            "cần hiểu toàn bộ câu thay vì dịch từng phủ định riêng."
        ),

        "这么重要的会议，我不能不参加。",

        (
            "Zhème zhòngyào de huìyì, "
            "wǒ bù néng bù cānjiā."
        ),

        (
            "Cuộc họp quan trọng thế này, "
            "tôi không thể không tham gia."
        ),
    ),

    # ======================================================
    # GF4-065
    # ======================================================

    "GF4-065-T01": (
        "一+量词（+名词）+也/都+不/没……",

        (
            "Cấu trúc này nhấn mạnh số lượng bằng không "
            "hoặc phủ định hoàn toàn, tương đương "
            "“không một... nào”."
        ),

        (
            "一 + lượng từ（+ danh từ）+ "
            "也/都 + 不/没 + vị ngữ."
        ),

        "我一个字也没说。",

        "Wǒ yí ge zì yě méi shuō.",

        "Tôi không nói một chữ nào.",
    ),

    # ======================================================
    # GF4-066
    # ======================================================

    "GF4-066-T01": (
        "连……也/都……",

        (
            "连……也/都…… đưa ra một trường hợp cực đoan "
            "hoặc ít ngờ tới để tăng mức độ nhấn mạnh."
        ),

        (
            "连 + thành phần được nhấn mạnh + "
            "也/都 + vị ngữ."
        ),

        "他连自己的名字都写错了。",

        (
            "Tā lián zìjǐ de míngzi "
            "dōu xiěcuò le."
        ),

        (
            "Anh ấy đến cả tên của mình cũng viết sai."
        ),
    ),

    # ======================================================
    # GF4-067
    # ======================================================

    "GF4-067-T01": (
        "不X白不X",

        (
            "Không X thì phí, vì vậy người nói cho rằng "
            "nên làm X khi cơ hội hoặc điều kiện đã có sẵn."
        ),

        (
            "不 + X + 白 + 不 + X; "
            "hai X là cùng một động từ hoặc cụm động từ."
        ),

        "电影是免费的，不看白不看。",

        (
            "Diànyǐng shì miǎnfèi de, "
            "bú kàn bái bú kàn."
        ),

        (
            "Phim miễn phí, không xem thì phí."
        ),
    ),

    # ======================================================
    # GF4-068
    # ======================================================

    "GF4-068-T01": (
        "Động từ + 一X是一X",

        (
            "Cấu trúc này biểu thị làm được từng phần nào "
            "thì tính phần đó, nhấn mạnh tiến hành từng bước "
            "hoặc cố gắng tích lũy dần."
        ),

        (
            "Động từ + 一 + lượng từ/đơn vị X + "
            "是 + 一 + X; hình thức cụ thể phụ thuộc "
            "nội dung được đếm."
        ),

        "事情太多了，能做一件是一件吧。",

        (
            "Shìqing tài duō le, "
            "néng zuò yí jiàn shì yí jiàn ba."
        ),

        (
            "Việc nhiều quá, làm được việc nào "
            "thì tính việc đó vậy."
        ),
    ),

    # ======================================================
    # GF4-069
    # ======================================================

    "GF4-069-T01": (
        "（没）有什么（好）X的",

        (
            "Mẫu này dùng để nói một hành động hoặc cảm xúc "
            "không cần thiết, không đáng phải quá bận tâm."
        ),

        (
            "（没）有什么（好）+ "
            "động từ/tính từ + 的."
        ),

        "失败一次有什么好难过的？",

        (
            "Shībài yí cì yǒu shénme "
            "hǎo nánguò de?"
        ),

        (
            "Thất bại một lần thì có gì đáng buồn đâu?"
        ),
    ),

    # ======================================================
    # GF4-070
    # ======================================================

    "GF4-070-T01": (
        "X是X，Y是Y",

        (
            "Mẫu này tách rõ hai sự việc, phạm vi hoặc đối tượng, "
            "nhấn mạnh rằng chúng không nên bị lẫn với nhau."
        ),

        "X + 是 + X，Y + 是 + Y.",

        "工作是工作，生活是生活，别混在一起。",

        (
            "Gōngzuò shì gōngzuò, "
            "shēnghuó shì shēnghuó, "
            "bié hùn zài yìqǐ."
        ),

        (
            "Công việc là công việc, cuộc sống là cuộc sống, "
            "đừng trộn lẫn hai việc."
        ),
    ),

    # ======================================================
    # GF4-071
    # ======================================================

    "GF4-071-T01": (
        "X也得X，不X也得X",

        (
            "Mẫu này biểu thị dù muốn hay không, "
            "hành động X vẫn bắt buộc phải thực hiện."
        ),

        (
            "X + 也得 + X，不 + X + 也得 + X; "
            "các vị trí X dùng cùng một động từ/cụm động từ."
        ),

        "做也得做，不做也得做。",

        (
            "Zuò yě děi zuò, "
            "bù zuò yě děi zuò."
        ),

        (
            "Làm cũng phải làm, không muốn làm "
            "cũng vẫn phải làm."
        ),
    ),

    # ======================================================
    # GF4-072
    # ======================================================

    "GF4-072-T01": (
        "X就是了",

        (
            "X就是了 biểu thị chỉ cần làm X là đủ "
            "hoặc giải pháp đơn giản là thực hiện X."
        ),

        (
            "Cụm động từ/tính từ X + 就是了."
        ),

        "你按时来就是了。",

        "Nǐ ànshí lái jiù shì le.",

        "Bạn chỉ cần đến đúng giờ là được.",
    ),

    # ======================================================
    # GF4-073
    # ======================================================

    "GF4-073-T01": (
        "还X呢",

        (
            "还X呢 là mẫu khẩu ngữ dùng để phản bác hoặc "
            "mỉa mai một cách gọi hay đánh giá X, hàm ý "
            "thực tế không xứng như vậy."
        ),

        (
            "还 + X + 呢; X thường là danh từ, danh hiệu "
            "hoặc cách đánh giá đang bị người nói nghi ngờ/phản bác."
        ),

        "还专家呢，这么简单的问题都不会。",

        (
            "Hái zhuānjiā ne, "
            "zhème jiǎndān de wèntí dōu bú huì."
        ),

        (
            "Chuyên gia gì chứ, vấn đề đơn giản thế này "
            "mà cũng không biết."
        ),
    ),

    # ======================================================
    # GF4-074
    # ======================================================

    "GF4-074-T01": (
        "你X你的吧",

        (
            "Mẫu này cho phép hoặc bảo người nghe cứ tiếp tục "
            "việc của mình, đồng thời hàm ý không cần bận tâm "
            "đến người nói hay việc khác."
        ),

        (
            "你 + X + 你的 + 吧; "
            "X là động từ/cụm động từ."
        ),

        "你忙你的吧，不用管我。",

        (
            "Nǐ máng nǐ de ba, "
            "bú yòng guǎn wǒ."
        ),

        (
            "Bạn cứ lo việc của bạn đi, "
            "không cần để ý đến tôi."
        ),
    ),

    # ======================================================
    # GF4-075
    # ======================================================

    "GF4-075-T01": (
        "让/叫你X你就X",

        (
            "Mẫu này nhấn mạnh rằng khi đã được yêu cầu làm X "
            "thì người nghe nên làm X ngay, không cần tranh luận "
            "hay chần chừ."
        ),

        (
            "让/叫 + 你 + X，+ 你 + 就 + X; "
            "hai X là cùng một hành động."
        ),

        "让你坐你就坐吧，别客气。",

        (
            "Ràng nǐ zuò nǐ jiù zuò ba, "
            "bié kèqi."
        ),

        (
            "Bảo bạn ngồi thì cứ ngồi đi, đừng khách sáo."
        ),
    ),

    # ======================================================
    # GF4-076
    # ======================================================

    "GF4-076-T01": (
        "说什么/怎么（着）也得X",

        (
            "Mẫu này biểu thị dù có trở ngại hay ý kiến gì "
            "thì hành động X vẫn nhất định phải làm, thể hiện "
            "sự cần thiết hoặc quyết tâm mạnh."
        ),

        (
            "说什么/怎么（着）+ 也得 + động từ/cụm động từ X; "
            "得 ở đây đọc là děi."
        ),

        "这次说什么我也得去。",

        (
            "Zhè cì shuō shénme "
            "wǒ yě děi qù."
        ),

        (
            "Lần này dù thế nào tôi cũng phải đi."
        ),
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


def normalize(value):

    return clean(
        value
    ).casefold()


def sha256_file(path):

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as file:

        while True:

            block = file.read(
                1024 * 1024
            )

            if not block:
                break

            digest.update(
                block
            )

    return digest.hexdigest()


def read_csv(path):

    if not path.is_file():

        raise FileNotFoundError(
            f"Khong tim thay file:\n{path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        fields = (
            reader.fieldnames
            or []
        )

        rows = list(
            reader
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

        writer.writerows(
            rows
        )


def validate_snapshot(
    path,
    expected_hash,
    label,
):

    actual = sha256_file(
        path
    )

    print(
        f"{label} SHA256:"
    )

    print(
        actual
    )

    if actual != expected_hash:

        raise RuntimeError(
            f"{label} da thay doi.\n"
            f"Expected: {expected_hash}\n"
            f"Actual  : {actual}"
        )

    return actual


def content_from_reviewed(row):

    required = [
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
    ]

    teaching_id = clean(
        row.get(
            "MaDonViGiangDay"
        )
    )

    for field in required:

        if not clean(
            row.get(field)
        ):

            raise RuntimeError(
                f"{teaching_id}: "
                f"reviewed batch rong {field}"
            )

    return {

        "TenCauTruc":
            clean(
                row.get(
                    "TenCauTruc"
                )
            ),

        "MoTa":
            clean(
                row.get(
                    "MoTa"
                )
            ),

        "CachDung":
            clean(
                row.get(
                    "CachDung"
                )
            ),

        "ViDuTiengTrung":
            clean(
                row.get(
                    "ViDuTiengTrung"
                )
            ),

        "ViDuPinyin":
            clean(
                row.get(
                    "ViDuPinyin"
                )
            ),

        "ViDuTiengViet":
            clean(
                row.get(
                    "ViDuTiengViet"
                )
            ),

        "TrangThaiKiemDuyet":
            (
                clean(
                    row.get(
                        "TrangThaiKiemDuyet"
                    )
                )
                or "DA_REVIEW"
            ),

        "KetQuaReview":
            (
                clean(
                    row.get(
                        "KetQuaReview"
                    )
                )
                or "PASS"
            ),

        "GhiChuReview":
            (
                clean(
                    row.get(
                        "GhiChuReview"
                    )
                )
                or "Da review truoc Buoc 15E."
            ),
    }


def build_final_row(
    plan_row,
    content,
):

    return {

        "MaDonViGiangDay":
            clean(
                plan_row.get(
                    "MaDonViGiangDay"
                )
            ),

        "MaMucNguPhapChuan":
            clean(
                plan_row.get(
                    "MaMucNguPhapChuan"
                )
            ),

        "SoThuTuChuan":
            clean(
                plan_row.get(
                    "SoThuTuChuan"
                )
            ),

        "SoThuTuNguon":
            clean(
                plan_row.get(
                    "SoThuTuNguon"
                )
            ),

        "ThuTuTrongDiemChuan":
            clean(
                plan_row.get(
                    "ThuTuTrongDiemChuan"
                )
            ),

        "SoMucGiangDayCuaDiemChuan":
            clean(
                plan_row.get(
                    "SoMucGiangDayCuaDiemChuan"
                )
            ),

        "QuyetDinhCuoi":
            clean(
                plan_row.get(
                    "QuyetDinhCuoi"
                )
            ),

        "LoaiTach":
            clean(
                plan_row.get(
                    "LoaiTach"
                )
            ),

        "NhomLonTrung":
            clean(
                plan_row.get(
                    "NhomLonTrung"
                )
            ),

        "NhomConTrung":
            clean(
                plan_row.get(
                    "NhomConTrung"
                )
            ),

        "ChiTietTrung":
            clean(
                plan_row.get(
                    "ChiTietTrung"
                )
            ),

        "NoiDungChuanTrung":
            clean(
                plan_row.get(
                    "NoiDungChuanTrung"
                )
            ),

        "DuongDanNguon":
            clean(
                plan_row.get(
                    "DuongDanNguon"
                )
            ),

        "NhanDonViNguonTrung":
            clean(
                plan_row.get(
                    "NhanDonViNguonTrung"
                )
            ),

        "CanhBaoNguon":
            clean(
                plan_row.get(
                    "CanhBaoNguon"
                )
            ),

        "TenCauTruc":
            clean(
                content.get(
                    "TenCauTruc"
                )
            ),

        "MoTa":
            clean(
                content.get(
                    "MoTa"
                )
            ),

        "CachDung":
            clean(
                content.get(
                    "CachDung"
                )
            ),

        "ViDuTiengTrung":
            clean(
                content.get(
                    "ViDuTiengTrung"
                )
            ),

        "ViDuPinyin":
            clean(
                content.get(
                    "ViDuPinyin"
                )
            ),

        "ViDuTiengViet":
            clean(
                content.get(
                    "ViDuTiengViet"
                )
            ),

        "MaNguon":
            SOURCE_ID,

        "TrangThai":
            "ban_nhap",

        "TrangThaiKiemDuyet":
            clean(
                content.get(
                    "TrangThaiKiemDuyet"
                )
            ),

        "KetQuaReview":
            clean(
                content.get(
                    "KetQuaReview"
                )
            ),

        "GhiChuReview":
            clean(
                content.get(
                    "GhiChuReview"
                )
            ),
    }


# ==========================================================
# 4. MAIN
# ==========================================================

def main():

    print("=" * 84)

    print(
        "BUOC 15E - HOAN THIEN TOAN BO "
        "NOI DUNG NGU PHAP HSK4"
    )

    print("=" * 84)

    print(
        "BIEN SOAN + REVIEW 74 MUC CON LAI "
        "- KHONG GHI SQL"
    )

    # ======================================================
    # 1. SNAPSHOT
    # ======================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT"
    )

    plan_hash = validate_snapshot(
        PLAN_FILE,
        EXPECTED_PLAN_SHA256,
        "PLAN",
    )

    batch01_hash = validate_snapshot(
        BATCH01_FILE,
        EXPECTED_BATCH01_SHA256,
        "BATCH01 REVIEWED",
    )

    batch02_hash = validate_snapshot(
        BATCH02_FILE,
        EXPECTED_BATCH02_SHA256,
        "BATCH02 REVIEWED",
    )

    print(
        "PASS: 3 snapshot khong thay doi."
    )

    # ======================================================
    # 2. DOC FILE
    # ======================================================

    print(
        "\n[2] DOC CAC FILE"
    )

    plan_fields, plan = read_csv(
        PLAN_FILE
    )

    _, batch01 = read_csv(
        BATCH01_FILE
    )

    _, batch02 = read_csv(
        BATCH02_FILE
    )

    print(
        "Plan:",
        len(plan),
    )

    print(
        "Batch 01 reviewed:",
        len(batch01),
    )

    print(
        "Batch 02 reviewed:",
        len(batch02),
    )

    if (
        len(plan)
        != EXPECTED_PLAN_TOTAL
    ):

        raise RuntimeError(
            "Plan khong con dung 114 muc."
        )

    if len(batch01) != 20:

        raise RuntimeError(
            "Batch 01 khong con dung 20 muc."
        )

    if len(batch02) != 20:

        raise RuntimeError(
            "Batch 02 khong con dung 20 muc."
        )

    required_plan_fields = {
        "MaDonViGiangDay",
        "MaMucNguPhapChuan",
        "SoThuTuChuan",
        "SoThuTuNguon",
        "ThuTuTrongDiemChuan",
        "SoMucGiangDayCuaDiemChuan",
        "QuyetDinhCuoi",
        "LoaiTach",
        "NhomLonTrung",
        "NhomConTrung",
        "ChiTietTrung",
        "NoiDungChuanTrung",
        "DuongDanNguon",
        "NhanDonViNguonTrung",
        "CanhBaoNguon",
    }

    missing = (
        required_plan_fields
        - set(plan_fields)
    )

    if missing:

        raise RuntimeError(
            "Plan thieu cot: "
            + ", ".join(
                sorted(missing)
            )
        )

    # ======================================================
    # 3. 40 MUC CU
    # ======================================================

    print(
        "\n[3] KIEM TRA 40 MUC DA REVIEW"
    )

    reviewed_rows = (
        batch01
        + batch02
    )

    reviewed_ids = [
        clean(
            row.get(
                "MaDonViGiangDay"
            )
        )
        for row in reviewed_rows
    ]

    if (
        len(reviewed_ids)
        != EXPECTED_REVIEWED_PREVIOUS
    ):

        raise RuntimeError(
            "Tong reviewed truoc do "
            "khong bang 40."
        )

    if (
        len(set(reviewed_ids))
        != EXPECTED_REVIEWED_PREVIOUS
    ):

        raise RuntimeError(
            "40 muc reviewed bi trung ID."
        )

    reviewed_map = {

        clean(
            row.get(
                "MaDonViGiangDay"
            )
        ):
        row

        for row in reviewed_rows
    }

    plan_ids = [
        clean(
            row.get(
                "MaDonViGiangDay"
            )
        )
        for row in plan
    ]

    if (
        plan_ids[:40]
        != reviewed_ids
    ):

        raise RuntimeError(
            "40 ID reviewed khong con khop "
            "40 dong dau cua plan."
        )

    print(
        "PASS: 40/40 reviewed khop plan."
    )

    # ======================================================
    # 4. 74 MUC CON LAI
    # ======================================================

    print(
        "\n[4] KIEM TRA 74 MUC CON LAI"
    )

    remaining_plan = (
        plan[40:]
    )

    remaining_plan_ids = [
        clean(
            row.get(
                "MaDonViGiangDay"
            )
        )
        for row in remaining_plan
    ]

    content_ids = list(
        CONTENT_REMAINING.keys()
    )

    print(
        "Con lai trong plan:",
        len(remaining_plan),
    )

    print(
        "Noi dung hard-code:",
        len(content_ids),
    )

    if (
        len(remaining_plan)
        != EXPECTED_REMAINING
    ):

        raise RuntimeError(
            "Plan con lai khong bang 74."
        )

    if (
        len(content_ids)
        != EXPECTED_REMAINING
    ):

        raise RuntimeError(
            "CONTENT_REMAINING khong bang 74."
        )

    if (
        remaining_plan_ids
        != content_ids
    ):

        print(
            "\nID plan con lai:"
        )

        for value in remaining_plan_ids:

            print(
                " ",
                value,
            )

        print(
            "\nID CONTENT_REMAINING:"
        )

        for value in content_ids:

            print(
                " ",
                value,
            )

        raise RuntimeError(
            "74 ID noi dung khong khop "
            "thu tu plan."
        )

    print(
        "PASS:",
        remaining_plan_ids[0],
        "->",
        remaining_plan_ids[-1],
    )

    # ======================================================
    # 5. TAO 74 MUC
    # ======================================================

    print(
        "\n[5] TAO 74 MUC NOI DUNG"
    )

    remaining_rows = []

    for plan_row in remaining_plan:

        teaching_id = clean(
            plan_row.get(
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
        ) = CONTENT_REMAINING[
            teaching_id
        ]

        content = {

            "TenCauTruc":
                title,

            "MoTa":
                description,

            "CachDung":
                usage,

            "ViDuTiengTrung":
                example_zh,

            "ViDuPinyin":
                example_py,

            "ViDuTiengViet":
                example_vi,

            "TrangThaiKiemDuyet":
                "DA_REVIEW_15E",

            "KetQuaReview":
                "PASS",

            "GhiChuReview":
                (
                    "Bien soan va review noi dung "
                    "tai Buoc 15E; pham vi truy vet "
                    "theo MaMucNguPhapChuan GF0025."
                ),
        }

        remaining_rows.append(
            build_final_row(
                plan_row,
                content,
            )
        )

    print(
        "Da tao:",
        len(remaining_rows),
        "/ 74",
    )

    # ======================================================
    # 6. GHEP 114
    # ======================================================

    print(
        "\n[6] GHEP 40 + 74 = 114"
    )

    final_rows = []

    for plan_row in plan[:40]:

        teaching_id = clean(
            plan_row.get(
                "MaDonViGiangDay"
            )
        )

        reviewed_content = (
            content_from_reviewed(
                reviewed_map[
                    teaching_id
                ]
            )
        )

        final_rows.append(
            build_final_row(
                plan_row,
                reviewed_content,
            )
        )

    final_rows.extend(
        remaining_rows
    )

    if (
        len(final_rows)
        != EXPECTED_PLAN_TOTAL
    ):

        raise RuntimeError(
            "Tong final khong bang 114."
        )

    if [
        row[
            "MaDonViGiangDay"
        ]
        for row in final_rows
    ] != plan_ids:

        raise RuntimeError(
            "Thu tu final khong khop plan."
        )

    print(
        "PASS: 114/114 dung thu tu plan."
    )

    # ======================================================
    # 7. VALIDATE TOAN BO
    # ======================================================

    print(
        "\n[7] VALIDATE TOAN BO 114"
    )

    required_text_fields = [
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
    ]

    for row in final_rows:

        code = row[
            "MaDonViGiangDay"
        ]

        for field in required_text_fields:

            if not clean(
                row.get(field)
            ):

                raise RuntimeError(
                    f"{code}: rong {field}"
                )

        if (
            row[
                "MaNguon"
            ]
            != SOURCE_ID
        ):

            raise RuntimeError(
                f"{code}: "
                f"MaNguon != {SOURCE_ID}"
            )

        if (
            row[
                "TrangThai"
            ]
            != "ban_nhap"
        ):

            raise RuntimeError(
                f"{code}: "
                "TrangThai != ban_nhap"
            )

        if (
            row[
                "KetQuaReview"
            ]
            not in {
                "PASS",
                "PASS_SAU_HIEU_CHINH",
            }
        ):

            raise RuntimeError(
                f"{code}: "
                "KetQuaReview khong hop le."
            )

        # ----------------------------------------------
        # Vi du Trung phai co dau cau.
        # ----------------------------------------------

        if not re.search(
            r"[。！？!?]$",
            row[
                "ViDuTiengTrung"
            ],
        ):

            raise RuntimeError(
                f"{code}: "
                "ViDuTiengTrung thieu dau cau."
            )

        # ----------------------------------------------
        # Pinyin khong duoc con Hanzi.
        # ----------------------------------------------

        if re.search(
            r"[\u3400-\u9fff]",
            row[
                "ViDuPinyin"
            ],
        ):

            raise RuntimeError(
                f"{code}: "
                "Pinyin con Hanzi."
            )

    # ======================================================
    # 8. ID DUY NHAT
    # ======================================================

    teaching_ids = [
        row[
            "MaDonViGiangDay"
        ]
        for row in final_rows
    ]

    if (
        len(
            set(
                teaching_ids
            )
        )
        != EXPECTED_PLAN_TOTAL
    ):

        raise RuntimeError(
            "MaDonViGiangDay final bi trung."
        )

    # ======================================================
    # 9. PHU 76 GF4
    # ======================================================

    source_point_ids = {
        row[
            "MaMucNguPhapChuan"
        ]
        for row in final_rows
    }

    if (
        len(source_point_ids)
        != EXPECTED_STANDARD_POINTS
    ):

        raise RuntimeError(
            "Final khong phu dung 76 GF4."
        )

    # ======================================================
    # 10. SO DON VI CUA TUNG GF4
    # ======================================================

    actual_per_source = Counter(
        row[
            "MaMucNguPhapChuan"
        ]
        for row in final_rows
    )

    expected_per_source = {}

    for row in plan:

        code = clean(
            row.get(
                "MaMucNguPhapChuan"
            )
        )

        try:

            expected = int(
                clean(
                    row.get(
                        "SoMucGiangDayCuaDiemChuan"
                    )
                )
            )

        except ValueError:

            raise RuntimeError(
                f"{code}: "
                "SoMucGiangDayCuaDiemChuan "
                "khong hop le."
            )

        if code in expected_per_source:

            if (
                expected_per_source[
                    code
                ]
                != expected
            ):

                raise RuntimeError(
                    f"{code}: "
                    "plan co so muc mau thuan."
                )

        else:

            expected_per_source[
                code
            ] = expected

    if (
        dict(
            actual_per_source
        )
        != expected_per_source
    ):

        raise RuntimeError(
            "So don vi theo GF4 "
            "khong khop plan."
        )

    # ======================================================
    # 11. TEN CAU TRUC KHONG TRUNG
    # ======================================================

    title_counts = Counter(
        normalize(
            row[
                "TenCauTruc"
            ]
        )
        for row in final_rows
    )

    duplicate_titles = [
        value
        for value, count
        in title_counts.items()
        if count > 1
    ]

    if duplicate_titles:

        raise RuntimeError(
            "TenCauTruc trung toan bo: "
            + str(
                duplicate_titles
            )
        )

    # ======================================================
    # 12. VI DU KHONG TRUNG
    # ======================================================

    example_counts = Counter(
        clean(
            row[
                "ViDuTiengTrung"
            ]
        )
        for row in final_rows
    )

    duplicate_examples = [
        value
        for value, count
        in example_counts.items()
        if count > 1
    ]

    if duplicate_examples:

        raise RuntimeError(
            "ViDuTiengTrung trung toan bo: "
            + str(
                duplicate_examples
            )
        )

    print(
        "PASS: 114 ID duy nhat."
    )

    print(
        "PASS: phu du 76/76 GF4."
    )

    print(
        "PASS: so don vi tung GF4 khop plan."
    )

    print(
        "PASS: 114/114 noi dung day du."
    )

    print(
        "PASS: 114/114 TrangThai=ban_nhap."
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
    # 13. THONG KE REVIEW
    # ======================================================

    print(
        "\n[8] THONG KE REVIEW"
    )

    review_status_counts = Counter(
        row[
            "TrangThaiKiemDuyet"
        ]
        for row in final_rows
    )

    review_result_counts = Counter(
        row[
            "KetQuaReview"
        ]
        for row in final_rows
    )

    for key, value in (
        review_status_counts.items()
    ):

        print(
            f"  {key}: {value}"
        )

    print(
        "Ket qua:"
    )

    for key, value in (
        review_result_counts.items()
    ):

        print(
            f"  {key}: {value}"
        )

    # ======================================================
    # 14. GHI FILE
    # ======================================================

    print(
        "\n[9] GHI FILE"
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    write_csv(
        REMAINING_FILE,
        remaining_rows,
    )

    write_csv(
        FINAL_FILE,
        final_rows,
    )

    remaining_hash = sha256_file(
        REMAINING_FILE
    )

    final_hash = sha256_file(
        FINAL_FILE
    )

    # ======================================================
    # 15. SUMMARY
    # ======================================================

    summary = {

        "status":
            "PASS",

        "gf0025_hsk4_standard_points":
            EXPECTED_STANDARD_POINTS,

        "tong_don_vi_giang_day":
            len(
                final_rows
            ),

        "da_review_batch01":
            len(
                batch01
            ),

        "da_review_batch02":
            len(
                batch02
            ),

        "bien_soan_review_15e":
            len(
                remaining_rows
            ),

        "phu_gf4":
            len(
                source_point_ids
            ),

        "trang_thai_sql_tuong_lai":
            "ban_nhap",

        "review_status_counts":
            dict(
                review_status_counts
            ),

        "review_result_counts":
            dict(
                review_result_counts
            ),

        "plan_sha256":
            plan_hash,

        "batch01_sha256":
            batch01_hash,

        "batch02_sha256":
            batch02_hash,

        "remaining74_sha256":
            remaining_hash,

        "final114_sha256":
            final_hash,

        "da_gan_bai_hoc":
            False,

        "da_ghi_sql":
            False,

        "da_publish":
            False,

        "ghi_chu":
            (
                "76 la diem chuan GF0025 HSK4; "
                "114 la don vi giang day Moc Han. "
                "File final nay van la hoc lieu ban_nhap, "
                "chua gan BaiHoc va chua ghi SQL."
            ),
    }

    if SUMMARY_FILE.exists():

        raise FileExistsError(
            f"Da ton tai file:\n"
            f"{SUMMARY_FILE}"
        )

    SUMMARY_FILE.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    # ======================================================
    # 16. KET QUA
    # ======================================================

    print(
        "\n" + "=" * 84
    )

    print(
        "HOAN THIEN NOI DUNG "
        "NGU PHAP HSK4 THANH CONG"
    )

    print("=" * 84)

    print(
        "Diem chuan GF0025:",
        EXPECTED_STANDARD_POINTS,
    )

    print(
        "Don vi giang day:",
        len(
            final_rows
        ),
        "/ 114",
    )

    print(
        "Batch 01 reviewed:",
        len(
            batch01
        ),
    )

    print(
        "Batch 02 reviewed:",
        len(
            batch02
        ),
    )

    print(
        "Bien soan + review trong 15E:",
        len(
            remaining_rows
        ),
    )

    print(
        "Phu GF4:",
        len(
            source_point_ids
        ),
        "/ 76",
    )

    print(
        "Trang thai: ban_nhap"
    )

    print(
        "\nREMAINING 74:"
    )

    print(
        " ",
        REMAINING_FILE,
    )

    print(
        "SHA256:"
    )

    print(
        remaining_hash
    )

    print(
        "\nFINAL 114:"
    )

    print(
        " ",
        FINAL_FILE,
    )

    print(
        "SHA256:"
    )

    print(
        final_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        " ",
        SUMMARY_FILE,
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

    print("=" * 84)


if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print(
            "\nLOI:"
        )

        print(
            error
        )

        raise SystemExit(1)