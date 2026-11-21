from pathlib import Path
import csv
import hashlib
import sys


# =========================================================
# ROOT
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]


# =========================================================
# CONFIG
# =========================================================
EXPECTED_ROWS = 78
EXPECTED_LESSONS = 21

EXPECTED_INTRO = 38
EXPECTED_REVIEW = 40

SOURCE_ID = 1004

EXPECTED_DISTRIBUTION_SHA256 = (
    "3129d9d2f35ce885a9bdb2f619ef1576f2da32b527e6cc0406275821656ef0b7"
)


# =========================================================
# FILES
# =========================================================
DISTRIBUTION_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lessons3_23_grammar_distribution_review.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
    / "grammar"
    / "review"
    / "hsk1_lessons3_23_grammar_content_review.csv"
)


# =========================================================
# NOI DUNG HOC TAP DO DO AN BIEN SOAN
#
# GF0025-2021 / MaNguon=1004:
#   dung de xac dinh pham vi + diem ngu phap.
#
# MoTa / CachDung / ViDu:
#   do do an bien soan lai phuc vu nguoi hoc,
#   KHONG phai noi dung sao chep nguyen van tu nguon.
# =========================================================
GRAMMAR_CONTENT = {

    "GF1-001": {
        "TenCauTruc": "Từ chỉ phương vị",
        "MoTa": (
            "Từ chỉ phương vị dùng để diễn tả vị trí hoặc phương hướng "
            "của người và sự vật, ví dụ như 上, 下, 前边, 后边, 左边, 右边."
        ),
        "CachDung": (
            "Có thể dùng sau danh từ hoặc kết hợp với 在 để nói vị trí. "
            "Mẫu thường gặp: A + 在 + từ chỉ phương vị; "
            "hoặc A + 的 + từ chỉ phương vị."
        ),
        "ViDuTiengTrung": "桌子在左边。",
        "ViDuPinyin": "Zhuōzi zài zuǒbian.",
        "ViDuTiengViet": "Cái bàn ở bên trái.",
    },

    "GF1-002": {
        "TenCauTruc": "会 / 能 - biểu thị khả năng",
        "MoTa": (
            "会 và 能 đều có thể biểu thị khả năng. "
            "会 thường dùng cho kỹ năng đã học được; "
            "能 thường nhấn mạnh điều kiện hoặc khả năng thực hiện."
        ),
        "CachDung": (
            "Mẫu cơ bản: Chủ ngữ + 会/能 + động từ. "
            "Phủ định thường dùng 不会 hoặc 不能."
        ),
        "ViDuTiengTrung": "我会说中文。",
        "ViDuPinyin": "Wǒ huì shuō Zhōngwén.",
        "ViDuTiengViet": "Tôi biết nói tiếng Trung.",
    },

    "GF1-003": {
        "TenCauTruc": "想 / 要 - biểu thị mong muốn",
        "MoTa": (
            "想 và 要 có thể dùng để diễn tả mong muốn. "
            "想 thường mang sắc thái muốn hoặc dự định; "
            "要 có thể biểu thị nhu cầu hay ý định rõ hơn."
        ),
        "CachDung": (
            "Mẫu cơ bản: Chủ ngữ + 想/要 + động từ hoặc danh từ."
        ),
        "ViDuTiengTrung": "我想喝水。",
        "ViDuPinyin": "Wǒ xiǎng hē shuǐ.",
        "ViDuTiengViet": "Tôi muốn uống nước.",
    },

    "GF1-004": {
        "TenCauTruc": "Đại từ nghi vấn",
        "MoTa": (
            "Đại từ nghi vấn được dùng để hỏi thông tin chưa biết, "
            "ví dụ 谁, 什么, 哪, 哪儿, 几, 多少, 怎么."
        ),
        "CachDung": (
            "Đặt từ nghi vấn đúng vào vị trí của thông tin cần hỏi. "
            "Khi đã có đại từ nghi vấn thì thông thường không cần thêm 吗."
        ),
        "ViDuTiengTrung": "你去哪儿？",
        "ViDuPinyin": "Nǐ qù nǎr?",
        "ViDuTiengViet": "Bạn đi đâu?",
    },

    "GF1-005": {
        "TenCauTruc": "Đại từ nhân xưng",
        "MoTa": (
            "Đại từ nhân xưng dùng để chỉ người nói, người nghe "
            "hoặc người được nhắc đến, ví dụ 我, 你, 您, 他, 她, 我们, 你们."
        ),
        "CachDung": (
            "Đại từ nhân xưng có thể làm chủ ngữ hoặc tân ngữ. "
            "们 thường được thêm vào một số đại từ để biểu thị số nhiều."
        ),
        "ViDuTiengTrung": "他们是学生。",
        "ViDuPinyin": "Tāmen shì xuésheng.",
        "ViDuTiengViet": "Họ là học sinh.",
    },

    "GF1-006": {
        "TenCauTruc": "Đại từ chỉ thị",
        "MoTa": (
            "Đại từ chỉ thị dùng để chỉ người hoặc sự vật, "
            "thường gặp nhất là 这 và 那."
        ),
        "CachDung": (
            "Có thể dùng trực tiếp hoặc kết hợp với lượng từ và danh từ, "
            "ví dụ 这个人, 那本书."
        ),
        "ViDuTiengTrung": "这是我的书。",
        "ViDuPinyin": "Zhè shì wǒ de shū.",
        "ViDuTiengViet": "Đây là sách của tôi.",
    },

    "GF1-007": {
        "TenCauTruc": "Số từ",
        "MoTa": (
            "Số từ dùng để biểu thị số lượng, thứ tự, tuổi, "
            "ngày tháng, giờ giấc và nhiều thông tin có liên quan đến số."
        ),
        "CachDung": (
            "Số từ thường đứng trước lượng từ hoặc đơn vị đo đếm. "
            "Ví dụ: 三个人, 五本书."
        ),
        "ViDuTiengTrung": "我有三本书。",
        "ViDuPinyin": "Wǒ yǒu sān běn shū.",
        "ViDuTiengViet": "Tôi có ba quyển sách.",
    },

    "GF1-008": {
        "TenCauTruc": "Lượng từ danh từ",
        "MoTa": (
            "Trong tiếng Trung, giữa số từ hoặc từ chỉ định "
            "và danh từ thường có lượng từ."
        ),
        "CachDung": (
            "Mẫu thường gặp: số từ + lượng từ + danh từ; "
            "hoặc 这/那 + lượng từ + danh từ."
        ),
        "ViDuTiengTrung": "我买一本书。",
        "ViDuPinyin": "Wǒ mǎi yì běn shū.",
        "ViDuTiengViet": "Tôi mua một quyển sách.",
    },

    "GF1-009": {
        "TenCauTruc": "Phó từ mức độ",
        "MoTa": (
            "Các phó từ như 很, 非常, 太, 真, 最 "
            "được dùng để biểu thị mức độ của tính chất hoặc trạng thái."
        ),
        "CachDung": (
            "Phó từ mức độ thường đứng trước tính từ. "
            "Ví dụ: 很好, 非常忙, 太贵, 真漂亮."
        ),
        "ViDuTiengTrung": "今天天气很好。",
        "ViDuPinyin": "Jīntiān tiānqì hěn hǎo.",
        "ViDuTiengViet": "Thời tiết hôm nay rất đẹp.",
    },

    "GF1-010": {
        "TenCauTruc": "都 / 一起 / 一块儿",
        "MoTa": (
            "都 biểu thị phạm vi bao gồm tất cả; "
            "一起 và 一块儿 biểu thị nhiều người cùng thực hiện một hành động."
        ),
        "CachDung": (
            "都 thường đứng trước vị ngữ. "
            "一起 hoặc 一块儿 thường đứng trước động từ."
        ),
        "ViDuTiengTrung": "我们一起学习汉语。",
        "ViDuPinyin": "Wǒmen yìqǐ xuéxí Hànyǔ.",
        "ViDuTiengViet": "Chúng ta cùng học tiếng Trung.",
    },

    "GF1-011": {
        "TenCauTruc": "Phó từ thời gian và trạng thái đang diễn ra",
        "MoTa": (
            "马上, 先, 有时 diễn tả thời điểm hoặc trình tự; "
            "在, 正, 正在 có thể biểu thị hành động đang diễn ra."
        ),
        "CachDung": (
            "Các phó từ này thường đứng trước động từ hoặc cụm động từ."
        ),
        "ViDuTiengTrung": "我正在学习汉语。",
        "ViDuPinyin": "Wǒ zhèngzài xuéxí Hànyǔ.",
        "ViDuTiengViet": "Tôi đang học tiếng Trung.",
    },

    "GF1-012": {
        "TenCauTruc": "常 / 常常 / 再",
        "MoTa": (
            "常 và 常常 biểu thị hành động thường xuyên xảy ra; "
            "再 thường biểu thị hành động sẽ lặp lại hoặc tiếp tục."
        ),
        "CachDung": (
            "Các phó từ này thường đứng trước động từ."
        ),
        "ViDuTiengTrung": "我常常看电影。",
        "ViDuPinyin": "Wǒ chángcháng kàn diànyǐng.",
        "ViDuTiengViet": "Tôi thường xuyên xem phim.",
    },

    "GF1-013": {
        "TenCauTruc": "还 / 也",
        "MoTa": (
            "也 mang nghĩa 'cũng'; "
            "还 có thể biểu thị 'vẫn', 'còn' hoặc bổ sung thêm thông tin."
        ),
        "CachDung": (
            "也 và 还 thường đứng trước động từ hoặc tính từ làm vị ngữ."
        ),
        "ViDuTiengTrung": "我也喜欢中文。",
        "ViDuPinyin": "Wǒ yě xǐhuan Zhōngwén.",
        "ViDuTiengViet": "Tôi cũng thích tiếng Trung.",
    },

    "GF1-014": {
        "TenCauTruc": "别 / 不 / 没 / 没有 - phủ định",
        "MoTa": (
            "不 thường phủ định thói quen, ý muốn hoặc trạng thái; "
            "没/没有 thường phủ định sự việc đã xảy ra hoặc sự tồn tại; "
            "别 thường dùng để ngăn cản hoặc khuyên không làm."
        ),
        "CachDung": (
            "Đặt từ phủ định trước động từ hoặc tính từ cần phủ định."
        ),
        "ViDuTiengTrung": "我不喝咖啡。",
        "ViDuPinyin": "Wǒ bù hē kāfēi.",
        "ViDuTiengViet": "Tôi không uống cà phê.",
    },

    "GF1-015": {
        "TenCauTruc": "从 - từ...",
        "MoTa": (
            "介词 从 dùng để chỉ điểm bắt đầu về địa điểm hoặc thời gian."
        ),
        "CachDung": (
            "Mẫu thường gặp: Chủ ngữ + 从 + địa điểm/thời gian + động từ."
        ),
        "ViDuTiengTrung": "我从学校回家。",
        "ViDuPinyin": "Wǒ cóng xuéxiào huí jiā.",
        "ViDuTiengViet": "Tôi từ trường về nhà.",
    },

    "GF1-016": {
        "TenCauTruc": "在 - ở, tại",
        "MoTa": (
            "在 có thể dùng trước địa điểm để nói nơi xảy ra hành động."
        ),
        "CachDung": (
            "Mẫu thường gặp: Chủ ngữ + 在 + địa điểm + động từ."
        ),
        "ViDuTiengTrung": "我在学校学习。",
        "ViDuPinyin": "Wǒ zài xuéxiào xuéxí.",
        "ViDuTiengViet": "Tôi học ở trường.",
    },

    "GF1-017": {
        "TenCauTruc": "跟 / 和 - với, cùng với",
        "MoTa": (
            "跟 và 和 có thể dùng để biểu thị quan hệ cùng tham gia "
            "giữa người này với người khác."
        ),
        "CachDung": (
            "Mẫu thường gặp: A + 跟/和 + B + động từ."
        ),
        "ViDuTiengTrung": "我跟朋友去商店。",
        "ViDuPinyin": "Wǒ gēn péngyou qù shāngdiàn.",
        "ViDuTiengViet": "Tôi đi cửa hàng cùng bạn.",
    },

    "GF1-018": {
        "TenCauTruc": "比 - so với",
        "MoTa": (
            "介词 比 được dùng để đưa đối tượng so sánh vào câu."
        ),
        "CachDung": (
            "Mẫu cơ bản: A + 比 + B + tính từ."
        ),
        "ViDuTiengTrung": "今天比昨天热。",
        "ViDuPinyin": "Jīntiān bǐ zuótiān rè.",
        "ViDuTiengViet": "Hôm nay nóng hơn hôm qua.",
    },

    "GF1-019": {
        "TenCauTruc": "跟 / 和 / 还是 - nối thành phần",
        "MoTa": (
            "跟 và 和 có thể nối các thành phần song song; "
            "还是 thường nối các lựa chọn trong câu hỏi."
        ),
        "CachDung": (
            "Dùng 和/跟 để nối các thành phần cùng loại; "
            "dùng 还是 khi người nói yêu cầu chọn giữa các phương án."
        ),
        "ViDuTiengTrung": "我喜欢唱歌和看电影。",
        "ViDuPinyin": "Wǒ xǐhuan chànggē hé kàn diànyǐng.",
        "ViDuTiengViet": "Tôi thích hát và xem phim.",
    },

    "GF1-020": {
        "TenCauTruc": "的 / 地 - trợ từ kết cấu",
        "MoTa": (
            "的 thường nối định ngữ với danh từ; "
            "地 thường nối trạng ngữ với động từ hoặc cụm động từ."
        ),
        "CachDung": (
            "Mẫu: định ngữ + 的 + danh từ; "
            "hoặc trạng ngữ + 地 + động từ."
        ),
        "ViDuTiengTrung": "这是我的书。他认真地学习汉语。",
        "ViDuPinyin": (
            "Zhè shì wǒ de shū. "
            "Tā rènzhēn de xuéxí Hànyǔ."
        ),
        "ViDuTiengViet": (
            "Đây là sách của tôi. "
            "Anh ấy học tiếng Trung một cách nghiêm túc."
        ),
    },

    "GF1-021": {
        "TenCauTruc": "Trợ từ động thái 了",
        "MoTa": (
            "了 có thể đứng sau động từ để biểu thị một hành động "
            "đã được thực hiện hoặc hoàn thành."
        ),
        "CachDung": (
            "Mẫu thường gặp: Chủ ngữ + động từ + 了 + tân ngữ."
        ),
        "ViDuTiengTrung": "我买了三本书。",
        "ViDuPinyin": "Wǒ mǎi le sān běn shū.",
        "ViDuTiengViet": "Tôi đã mua ba quyển sách.",
    },

    "GF1-022": {
        "TenCauTruc": "吧 / 了 / 吗 / 呢 - trợ từ ngữ khí",
        "MoTa": (
            "Trợ từ ngữ khí thường đứng cuối câu để thể hiện "
            "câu hỏi, đề nghị, thay đổi tình trạng hoặc sắc thái giao tiếp."
        ),
        "CachDung": (
            "吗 thường tạo câu hỏi yes/no; 呢 có thể hỏi lại; "
            "吧 thường mang sắc thái đề nghị; 了 có thể báo sự thay đổi."
        ),
        "ViDuTiengTrung": "你是学生吗？",
        "ViDuPinyin": "Nǐ shì xuésheng ma?",
        "ViDuTiengViet": "Bạn là học sinh phải không?",
    },

    "GF1-023": {
        "TenCauTruc": "Cụm số lượng",
        "MoTa": (
            "Cụm số lượng thường gồm số từ và lượng từ, "
            "được dùng để xác định số lượng của danh từ."
        ),
        "CachDung": (
            "Mẫu cơ bản: số từ + lượng từ + danh từ."
        ),
        "ViDuTiengTrung": "我买三本书。",
        "ViDuPinyin": "Wǒ mǎi sān běn shū.",
        "ViDuTiengViet": "Tôi mua ba quyển sách.",
    },

    "GF1-024": {
        "TenCauTruc": "Chủ ngữ",
        "MoTa": (
            "Chủ ngữ là thành phần thường chỉ người hoặc sự vật "
            "mà câu đang nói đến."
        ),
        "CachDung": (
            "Trong câu cơ bản, chủ ngữ thường đứng trước vị ngữ."
        ),
        "ViDuTiengTrung": "我学习汉语。",
        "ViDuPinyin": "Wǒ xuéxí Hànyǔ.",
        "ViDuTiengViet": "Tôi học tiếng Trung.",
    },

    "GF1-025": {
        "TenCauTruc": "Vị ngữ",
        "MoTa": (
            "Vị ngữ cung cấp thông tin về hành động, trạng thái "
            "hoặc đặc điểm của chủ ngữ."
        ),
        "CachDung": (
            "Vị ngữ thường đứng sau chủ ngữ và có thể do động từ "
            "hoặc tính từ đảm nhiệm."
        ),
        "ViDuTiengTrung": "我学习汉语。",
        "ViDuPinyin": "Wǒ xuéxí Hànyǔ.",
        "ViDuTiengViet": "Tôi học tiếng Trung.",
    },

    "GF1-026": {
        "TenCauTruc": "Tân ngữ",
        "MoTa": (
            "Tân ngữ thường là đối tượng chịu tác động của động từ."
        ),
        "CachDung": (
            "Trong câu động từ cơ bản, tân ngữ thường đứng sau động từ."
        ),
        "ViDuTiengTrung": "我学习汉语。",
        "ViDuPinyin": "Wǒ xuéxí Hànyǔ.",
        "ViDuTiengViet": "Tôi học tiếng Trung.",
    },

    "GF1-027": {
        "TenCauTruc": "Định ngữ",
        "MoTa": (
            "Định ngữ bổ sung thông tin cho danh từ, "
            "giúp xác định người hoặc sự vật cụ thể hơn."
        ),
        "CachDung": (
            "Định ngữ đứng trước danh từ. "
            "Nhiều trường hợp dùng cấu trúc: định ngữ + 的 + danh từ."
        ),
        "ViDuTiengTrung": "我的朋友是学生。",
        "ViDuPinyin": "Wǒ de péngyou shì xuésheng.",
        "ViDuTiengViet": "Bạn của tôi là học sinh.",
    },

    "GF1-028": {
        "TenCauTruc": "Trạng ngữ",
        "MoTa": (
            "Trạng ngữ bổ sung thông tin về thời gian, nơi chốn, "
            "cách thức, mức độ hoặc phạm vi cho vị ngữ."
        ),
        "CachDung": (
            "Trạng ngữ thường đứng trước động từ hoặc tính từ làm vị ngữ."
        ),
        "ViDuTiengTrung": "我每天学习汉语。",
        "ViDuPinyin": "Wǒ měitiān xuéxí Hànyǔ.",
        "ViDuTiengViet": "Tôi học tiếng Trung mỗi ngày.",
    },

    "GF1-029": {
        "TenCauTruc": "Câu vị ngữ động từ",
        "MoTa": (
            "Câu vị ngữ động từ là câu có phần vị ngữ chính "
            "được tạo bởi động từ hoặc cụm động từ."
        ),
        "CachDung": (
            "Mẫu cơ bản: Chủ ngữ + động từ + tân ngữ."
        ),
        "ViDuTiengTrung": "我学习汉语。",
        "ViDuPinyin": "Wǒ xuéxí Hànyǔ.",
        "ViDuTiengViet": "Tôi học tiếng Trung.",
    },

    "GF1-030": {
        "TenCauTruc": "Câu vị ngữ tính từ",
        "MoTa": (
            "Trong tiếng Trung, tính từ có thể trực tiếp làm trung tâm vị ngữ. "
            "Ở câu khẳng định thông thường, trước tính từ thường xuất hiện 很."
        ),
        "CachDung": (
            "Mẫu cơ bản: Chủ ngữ + 很 + tính từ."
        ),
        "ViDuTiengTrung": "今天天气很热。",
        "ViDuPinyin": "Jīntiān tiānqì hěn rè.",
        "ViDuTiengViet": "Thời tiết hôm nay nóng.",
    },

    "GF1-031": {
        "TenCauTruc": "Câu không chủ - vị",
        "MoTa": (
            "Một số câu tiếng Trung không cần đầy đủ cấu trúc chủ ngữ - vị ngữ "
            "nhưng vẫn biểu đạt được ý nghĩa hoàn chỉnh trong ngữ cảnh."
        ),
        "CachDung": (
            "Thường gặp trong biểu đạt thời tiết, chào hỏi, "
            "mệnh lệnh hoặc câu ngắn trong giao tiếp."
        ),
        "ViDuTiengTrung": "下雨了。",
        "ViDuPinyin": "Xiàyǔ le.",
        "ViDuTiengViet": "Trời mưa rồi.",
    },

    "GF1-032": {
        "TenCauTruc": "Câu trần thuật",
        "MoTa": (
            "Câu trần thuật dùng để trình bày hoặc thông báo một sự việc."
        ),
        "CachDung": (
            "Ngữ điệu thường tương đối ổn định; "
            "cuối câu thường dùng dấu chấm khi viết."
        ),
        "ViDuTiengTrung": "我是学生。",
        "ViDuPinyin": "Wǒ shì xuésheng.",
        "ViDuTiengViet": "Tôi là học sinh.",
    },

    "GF1-033": {
        "TenCauTruc": "Câu nghi vấn",
        "MoTa": (
            "Câu nghi vấn dùng để yêu cầu người nghe cung cấp "
            "hoặc xác nhận thông tin."
        ),
        "CachDung": (
            "Có thể tạo câu hỏi bằng 吗, đại từ nghi vấn, "
            "还是 hoặc dạng chính - phản."
        ),
        "ViDuTiengTrung": "你喜欢中文吗？",
        "ViDuPinyin": "Nǐ xǐhuan Zhōngwén ma?",
        "ViDuTiengViet": "Bạn có thích tiếng Trung không?",
    },

    "GF1-034": {
        "TenCauTruc": "Câu cầu khiến",
        "MoTa": (
            "Câu cầu khiến dùng để yêu cầu, đề nghị, mời "
            "hoặc nhắc người khác thực hiện một hành động."
        ),
        "CachDung": (
            "Có thể dùng 请 để làm lời yêu cầu lịch sự hơn; "
            "dùng 别 để yêu cầu không làm một việc."
        ),
        "ViDuTiengTrung": "请打开课本。",
        "ViDuPinyin": "Qǐng dǎkāi kèběn.",
        "ViDuTiengViet": "Mời mở sách giáo khoa.",
    },

    "GF1-035": {
        "TenCauTruc": "Câu cảm thán",
        "MoTa": (
            "Câu cảm thán dùng để biểu thị cảm xúc hoặc mức độ nổi bật."
        ),
        "CachDung": (
            "Có thể kết hợp 真, 太...了 hoặc các cách diễn đạt "
            "mang sắc thái cảm thán."
        ),
        "ViDuTiengTrung": "今天天气真好！",
        "ViDuPinyin": "Jīntiān tiānqì zhēn hǎo!",
        "ViDuTiengViet": "Thời tiết hôm nay thật đẹp!",
    },

    "GF1-036": {
        "TenCauTruc": "Câu chữ 是",
        "MoTa": (
            "是 dùng để nối chủ ngữ với danh từ hoặc cụm danh từ "
            "nhằm xác định hoặc giới thiệu người, sự vật."
        ),
        "CachDung": (
            "Mẫu cơ bản: A + 是 + B."
        ),
        "ViDuTiengTrung": "她是老师。",
        "ViDuPinyin": "Tā shì lǎoshī.",
        "ViDuTiengViet": "Cô ấy là giáo viên.",
    },

    "GF1-037": {
        "TenCauTruc": "Câu chữ 有",
        "MoTa": (
            "有 được dùng để biểu thị sự sở hữu hoặc sự tồn tại."
        ),
        "CachDung": (
            "Mẫu sở hữu: A + 有 + B. "
            "Phủ định thường dùng 没有."
        ),
        "ViDuTiengTrung": "我家有三个人。",
        "ViDuPinyin": "Wǒ jiā yǒu sān ge rén.",
        "ViDuTiengViet": "Nhà tôi có ba người.",
    },

    "GF1-038": {
        "TenCauTruc": "Câu so sánh với 比",
        "MoTa": (
            "Câu so sánh với 比 được dùng để so sánh "
            "đặc điểm hoặc mức độ giữa hai đối tượng."
        ),
        "CachDung": (
            "Mẫu cơ bản: A + 比 + B + tính từ."
        ),
        "ViDuTiengTrung": "这个比那个好。",
        "ViDuPinyin": "Zhège bǐ nàge hǎo.",
        "ViDuTiengViet": "Cái này tốt hơn cái kia.",
    },

    "GF1-039": {
        "TenCauTruc": "Câu ghép song song",
        "MoTa": (
            "Câu ghép song song nối các nội dung có quan hệ ngang hàng "
            "hoặc bổ sung cho nhau."
        ),
        "CachDung": (
            "Có thể dùng các từ như 和, 也 hoặc cấu trúc tương ứng "
            "để kết nối các nội dung song song."
        ),
        "ViDuTiengTrung": "我喜欢唱歌，也喜欢看电影。",
        "ViDuPinyin": "Wǒ xǐhuan chànggē, yě xǐhuan kàn diànyǐng.",
        "ViDuTiengViet": "Tôi thích hát, cũng thích xem phim.",
    },

    "GF1-040": {
        "TenCauTruc": "了² - biểu thị sự thay đổi trạng thái",
        "MoTa": (
            "了 ở cuối câu có thể cho biết tình trạng hiện tại "
            "đã thay đổi so với trước."
        ),
        "CachDung": (
            "Thường đặt cuối câu sau nội dung diễn tả trạng thái mới."
        ),
        "ViDuTiengTrung": "天气冷了。",
        "ViDuPinyin": "Tiānqì lěng le.",
        "ViDuTiengViet": "Thời tiết trở lạnh rồi.",
    },

    "GF1-041": {
        "TenCauTruc": "Thể hoàn thành với 了¹",
        "MoTa": (
            "了 đặt sau động từ có thể đánh dấu một hành động "
            "đã được thực hiện hoặc hoàn tất."
        ),
        "CachDung": (
            "Mẫu thường gặp: Chủ ngữ + động từ + 了 + tân ngữ."
        ),
        "ViDuTiengTrung": "我买了书。",
        "ViDuPinyin": "Wǒ mǎi le shū.",
        "ViDuTiengViet": "Tôi đã mua sách.",
    },

    "GF1-042": {
        "TenCauTruc": "Thể tiếp diễn với 在 / 正 / 正在",
        "MoTa": (
            "在, 正 hoặc 正在 đứng trước động từ "
            "có thể cho biết hành động đang diễn ra."
        ),
        "CachDung": (
            "Mẫu thường gặp: Chủ ngữ + 正在/在 + động từ."
        ),
        "ViDuTiengTrung": "我正在看书。",
        "ViDuPinyin": "Wǒ zhèngzài kàn shū.",
        "ViDuTiengViet": "Tôi đang đọc sách.",
    },

    "GF1-043": {
        "TenCauTruc": "Cách biểu đạt số tiền",
        "MoTa": (
            "Số tiền trong tiếng Trung thường được biểu đạt "
            "bằng số từ kết hợp với đơn vị tiền như 元 hoặc 块."
        ),
        "CachDung": (
            "Mẫu cơ bản: số + đơn vị tiền. "
            "Trong giao tiếp hằng ngày, 块 thường được dùng thay 元."
        ),
        "ViDuTiengTrung": "这本书二十块钱。",
        "ViDuPinyin": "Zhè běn shū èrshí kuài qián.",
        "ViDuTiengViet": "Quyển sách này giá hai mươi tệ.",
    },

    "GF1-044": {
        "TenCauTruc": "Cách biểu đạt thời gian",
        "MoTa": (
            "Thời gian có thể được biểu đạt bằng năm, tháng, ngày, "
            "thứ trong tuần, giờ và phút."
        ),
        "CachDung": (
            "Khi nói thời điểm, các đơn vị thường được sắp xếp "
            "từ lớn đến nhỏ."
        ),
        "ViDuTiengTrung": "现在八点。",
        "ViDuPinyin": "Xiànzài bā diǎn.",
        "ViDuTiengViet": "Bây giờ là tám giờ.",
    },

    "GF1-045": {
        "TenCauTruc": "Dùng 吗 để đặt câu hỏi",
        "MoTa": (
            "吗 được đặt cuối câu trần thuật để tạo câu hỏi "
            "yêu cầu xác nhận đúng hoặc sai."
        ),
        "CachDung": (
            "Mẫu cơ bản: Câu trần thuật + 吗？"
        ),
        "ViDuTiengTrung": "你是学生吗？",
        "ViDuPinyin": "Nǐ shì xuésheng ma?",
        "ViDuTiengViet": "Bạn là học sinh phải không?",
    },

    "GF1-046": {
        "TenCauTruc": "Dùng đại từ nghi vấn để đặt câu hỏi",
        "MoTa": (
            "Các đại từ nghi vấn như 谁, 什么, 哪儿, 几, 多少, 怎么 "
            "được đặt vào vị trí thông tin mà người nói muốn hỏi."
        ),
        "CachDung": (
            "Giữ cấu trúc câu cơ bản và thay phần chưa biết "
            "bằng đại từ nghi vấn phù hợp."
        ),
        "ViDuTiengTrung": "你去哪儿？",
        "ViDuPinyin": "Nǐ qù nǎr?",
        "ViDuTiengViet": "Bạn đi đâu?",
    },

    "GF1-047": {
        "TenCauTruc": "Dùng 还是 để hỏi lựa chọn",
        "MoTa": (
            "还是 được dùng trong câu hỏi khi người nói "
            "đưa ra hai hoặc nhiều lựa chọn."
        ),
        "CachDung": (
            "Mẫu thường gặp: A + 还是 + B？"
        ),
        "ViDuTiengTrung": "你喝茶还是咖啡？",
        "ViDuPinyin": "Nǐ hē chá háishi kāfēi?",
        "ViDuTiengViet": "Bạn uống trà hay cà phê?",
    },

    "GF1-048": {
        "TenCauTruc": "Dạng chính - phản",
        "MoTa": (
            "Dạng chính - phản lặp lại động từ hoặc tính từ "
            "ở dạng khẳng định và phủ định để tạo câu hỏi."
        ),
        "CachDung": (
            "Một mẫu phổ biến: động từ + 不 + động từ."
        ),
        "ViDuTiengTrung": "你去不去学校？",
        "ViDuPinyin": "Nǐ qù bu qù xuéxiào?",
        "ViDuTiengViet": "Bạn có đi học không?",
    },
}


# =========================================================
# HELPERS
# =========================================================
def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def fail(message):

    raise RuntimeError(message)


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
                f"Khong doc duoc header:\n{path}"
            )

        return reader.fieldnames, list(reader)


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


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 120)
    print(
        "09H14 - TAO NOI DUNG HOC TAP "
        "NGU PHAP HSK1 BAI 3 -> 23"
    )
    print("=" * 120)

    print()
    print("CHE DO:")
    print("  DOC 78 PHAN BO DA KIEM DUYET")
    print("  SINH NOI DUNG HOC TAP TU BO 48 GF1")
    print("  TAO FILE CONTENT REVIEW")
    print("  KHONG KET NOI DATABASE")
    print("  KHONG INSERT dbo.NguPhap")
    print("  KHONG UPDATE DATABASE")

    # =====================================================
    # 1. VERIFY DISTRIBUTION FILE
    # =====================================================
    print()
    print("[1] VERIFY FILE PHAN BO DA KIEM DUYET")
    print("-" * 120)

    if not DISTRIBUTION_FILE.exists():

        fail(
            "Khong tim thay file:\n"
            f"{DISTRIBUTION_FILE}"
        )

    current_hash = sha256_file(
        DISTRIBUTION_FILE
    )

    print(
        "SHA256 hien tai:"
    )

    print(
        current_hash
    )

    print()
    print(
        "SHA256 mong doi:"
    )

    print(
        EXPECTED_DISTRIBUTION_SHA256
    )

    if (
        current_hash
        != EXPECTED_DISTRIBUTION_SHA256
    ):

        fail(
            "File phan bo da thay doi "
            "sau 09h13. KHONG tiep tuc."
        )

    print(
        "SHA256: OK"
    )

    # =====================================================
    # 2. READ DISTRIBUTION
    # =====================================================
    print()
    print("[2] DOC 78 DONG PHAN BO")
    print("-" * 120)

    fields, rows = load_csv(
        DISTRIBUTION_FILE
    )

    required_fields = {
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuNguPhapDeXuat",
        "MaMucNguPhapChuan",
        "TenMucChuan",
        "NoiDungChuan",
        "LoaiSuDung",
        "LyDoPhanBo",
        "MaNguon",
        "DaKiemDuyetPhanBo",
        "GhiChuKiemDuyet",
    }

    missing_fields = (
        required_fields
        - set(fields)
    )

    if missing_fields:

        fail(
            "File phan bo thieu cot: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if len(rows) != EXPECTED_ROWS:

        fail(
            "File phan bo phai co "
            "78 dong."
        )

    approved_count = sum(
        1
        for row in rows
        if clean(
            row[
                "DaKiemDuyetPhanBo"
            ]
        ) == "1"
    )

    if approved_count != 78:

        fail(
            "78 dong chua duoc "
            "kiem duyet day du."
        )

    intro_count = sum(
        1
        for row in rows
        if clean(
            row["LoaiSuDung"]
        ) == "gioi_thieu"
    )

    review_count = sum(
        1
        for row in rows
        if clean(
            row["LoaiSuDung"]
        ) == "on_tap_mo_rong"
    )

    if intro_count != EXPECTED_INTRO:

        fail(
            "So gioi_thieu khong bang 38."
        )

    if review_count != EXPECTED_REVIEW:

        fail(
            "So on_tap_mo_rong "
            "khong bang 40."
        )

    lessons = {
        int(
            clean(
                row["SoThuTuBai"]
            )
        )
        for row in rows
    }

    if lessons != set(
        range(3, 24)
    ):

        fail(
            "Khong du Bai 3 -> 23."
        )

    print(
        "Tong dong:",
        len(rows),
    )

    print(
        "Da kiem duyet:",
        approved_count,
    )

    print(
        "Gioi thieu:",
        intro_count,
    )

    print(
        "On tap/mo rong:",
        review_count,
    )

    print(
        "So bai:",
        len(lessons),
    )

    # =====================================================
    # 3. VERIFY CONTENT MASTER
    # =====================================================
    print()
    print(
        "[3] VERIFY BO NOI DUNG 48 GF1"
    )
    print("-" * 120)

    expected_ids = {
        f"GF1-{i:03d}"
        for i in range(1, 49)
    }

    actual_ids = set(
        GRAMMAR_CONTENT.keys()
    )

    missing_content_ids = (
        expected_ids
        - actual_ids
    )

    extra_content_ids = (
        actual_ids
        - expected_ids
    )

    if missing_content_ids:

        fail(
            "GRAMMAR_CONTENT thieu: "
            + ", ".join(
                sorted(
                    missing_content_ids
                )
            )
        )

    if extra_content_ids:

        fail(
            "GRAMMAR_CONTENT du ID: "
            + ", ".join(
                sorted(
                    extra_content_ids
                )
            )
        )

    if len(
        GRAMMAR_CONTENT
    ) != 48:

        fail(
            "GRAMMAR_CONTENT "
            "phai co dung 48 muc."
        )

    required_content_fields = {
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
    }

    blank_content = []

    for standard_id, content in (
        GRAMMAR_CONTENT.items()
    ):

        for field in (
            required_content_fields
        ):

            if not clean(
                content.get(field)
            ):

                blank_content.append(
                    (
                        standard_id,
                        field,
                    )
                )

    if blank_content:

        print(
            blank_content
        )

        fail(
            "Bo noi dung 48 GF1 "
            "co truong bi trong."
        )

    print(
        "48/48 GF1 co noi dung: OK"
    )

    # =====================================================
    # 4. VERIFY ALL DISTRIBUTION IDS
    # =====================================================
    print()
    print(
        "[4] DOI CHIEU 78 DONG "
        "VOI BO NOI DUNG"
    )
    print("-" * 120)

    missing_mapping = []

    for row in rows:

        standard_id = clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )

        if (
            standard_id
            not in GRAMMAR_CONTENT
        ):

            missing_mapping.append(
                (
                    row[
                        "SoThuTuBai"
                    ],
                    standard_id,
                )
            )

        if (
            clean(
                row["MaNguon"]
            )
            != str(
                SOURCE_ID
            )
        ):

            fail(
                f"Bai "
                f"{row['SoThuTuBai']} "
                f"{standard_id}: "
                "MaNguon khong bang 1004."
            )

    if missing_mapping:

        print(
            missing_mapping
        )

        fail(
            "Co GF1 khong co "
            "noi dung hoc tap."
        )

    print(
        "78/78 DONG: OK"
    )

    # =====================================================
    # 5. CREATE CONTENT ROWS
    # =====================================================
    print()
    print(
        "[5] SINH NOI DUNG 78 MUC"
    )
    print("-" * 120)

    output_rows = []

    for row in rows:

        standard_id = clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )

        content = (
            GRAMMAR_CONTENT[
                standard_id
            ]
        )

        usage_type = clean(
            row["LoaiSuDung"]
        )

        if (
            usage_type
            == "gioi_thieu"
        ):

            usage_note = (
                "Điểm ngữ pháp được giới thiệu "
                "lần đầu trong lộ trình HSK1 "
                "do đồ án thiết kế."
            )

        elif (
            usage_type
            == "on_tap_mo_rong"
        ):

            usage_note = (
                "Điểm ngữ pháp đã xuất hiện trước đó "
                "và được dùng lại để ôn tập hoặc "
                "mở rộng theo chủ đề của bài."
            )

        else:

            fail(
                "LoaiSuDung khong hop le: "
                f"{usage_type}"
            )

        output_rows.append(
            {
                "SoThuTuBai": clean(
                    row["SoThuTuBai"]
                ),

                "MaBaiHoc": clean(
                    row["MaBaiHoc"]
                ),

                "TieuDeBai": clean(
                    row["TieuDeBai"]
                ),

                "ThuTuTrongBai": clean(
                    row[
                        "ThuTuNguPhapDeXuat"
                    ]
                ),

                "MaMucNguPhapChuan": (
                    standard_id
                ),

                "TenMucChuan": clean(
                    row["TenMucChuan"]
                ),

                "NoiDungChuan": clean(
                    row["NoiDungChuan"]
                ),

                "LoaiSuDung": (
                    usage_type
                ),

                "TenCauTruc": clean(
                    content[
                        "TenCauTruc"
                    ]
                ),

                "MoTa": clean(
                    content[
                        "MoTa"
                    ]
                ),

                "CachDung": clean(
                    content[
                        "CachDung"
                    ]
                ),

                "ViDuTiengTrung": clean(
                    content[
                        "ViDuTiengTrung"
                    ]
                ),

                "ViDuPinyin": clean(
                    content[
                        "ViDuPinyin"
                    ]
                ),

                "ViDuTiengViet": clean(
                    content[
                        "ViDuTiengViet"
                    ]
                ),

                "MaNguon": (
                    SOURCE_ID
                ),

                "MaTep": "",

                "TrangThai": (
                    "ban_nhap"
                ),

                "LyDoPhanBo": clean(
                    row[
                        "LyDoPhanBo"
                    ]
                ),

                "GhiChuBienSoan": (
                    usage_note
                    + " Phạm vi/mục ngữ pháp "
                    "tham chiếu GF0025-2021; "
                    "mô tả, cách dùng và ví dụ "
                    "do đồ án biên soạn phục vụ học tập."
                ),

                "DaKiemDuyetNoiDung": (
                    0
                ),

                "GhiChuKiemDuyet": "",
            }
        )

    # =====================================================
    # 6. VERIFY ORDER
    # =====================================================
    print()
    print(
        "[6] VERIFY THU TU TUNG BAI"
    )
    print("-" * 120)

    for lesson_no in range(
        3,
        24,
    ):

        lesson_rows = [
            row
            for row in output_rows
            if int(
                row[
                    "SoThuTuBai"
                ]
            ) == lesson_no
        ]

        orders = [
            int(
                row[
                    "ThuTuTrongBai"
                ]
            )
            for row in lesson_rows
        ]

        expected_orders = list(
            range(
                1,
                len(
                    lesson_rows
                ) + 1,
            )
        )

        if (
            orders
            != expected_orders
        ):

            fail(
                f"Bai {lesson_no}: "
                "ThuTuTrongBai sai."
            )

        print(
            f"Bai {lesson_no:>2}: "
            f"{len(lesson_rows)} muc | OK"
        )

    # =====================================================
    # 7. WRITE FILE
    # =====================================================
    print()
    print(
        "[7] GHI FILE CONTENT REVIEW"
    )
    print("-" * 120)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "SoThuTuBai",
        "MaBaiHoc",
        "TieuDeBai",
        "ThuTuTrongBai",
        "MaMucNguPhapChuan",
        "TenMucChuan",
        "NoiDungChuan",
        "LoaiSuDung",
        "TenCauTruc",
        "MoTa",
        "CachDung",
        "ViDuTiengTrung",
        "ViDuPinyin",
        "ViDuTiengViet",
        "MaNguon",
        "MaTep",
        "TrangThai",
        "LyDoPhanBo",
        "GhiChuBienSoan",
        "DaKiemDuyetNoiDung",
        "GhiChuKiemDuyet",
    ]

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
            output_rows
        )

    print(
        "Da tao:"
    )

    print(
        OUTPUT_FILE
    )

    # =====================================================
    # 8. READ BACK
    # =====================================================
    print()
    print(
        "[8] VERIFY FILE SAU KHI GHI"
    )
    print("-" * 120)

    verify_fields, verify_rows = (
        load_csv(
            OUTPUT_FILE
        )
    )

    if (
        len(verify_rows)
        != EXPECTED_ROWS
    ):

        fail(
            "File content review "
            "khong co dung 78 dong."
        )

    required_output_fields = set(
        fieldnames
    )

    if (
        set(verify_fields)
        != required_output_fields
    ):

        missing = (
            required_output_fields
            - set(
                verify_fields
            )
        )

        extra = (
            set(
                verify_fields
            )
            - required_output_fields
        )

        fail(
            f"Header sai. "
            f"Thieu={missing}, "
            f"Du={extra}"
        )

    blank_errors = []

    for row in verify_rows:

        for field in [
            "TenCauTruc",
            "MoTa",
            "CachDung",
            "ViDuTiengTrung",
            "ViDuPinyin",
            "ViDuTiengViet",
            "GhiChuBienSoan",
        ]:

            if not clean(
                row[field]
            ):

                blank_errors.append(
                    (
                        row[
                            "SoThuTuBai"
                        ],
                        row[
                            "MaMucNguPhapChuan"
                        ],
                        field,
                    )
                )

    if blank_errors:

        print(
            blank_errors[:30]
        )

        fail(
            "Co noi dung hoc tap bi trong."
        )

    wrong_source = sum(
        1
        for row in verify_rows
        if clean(
            row["MaNguon"]
        ) != "1004"
    )

    wrong_status = sum(
        1
        for row in verify_rows
        if clean(
            row[
                "TrangThai"
            ]
        ) != "ban_nhap"
    )

    approved_content = sum(
        1
        for row in verify_rows
        if clean(
            row[
                "DaKiemDuyetNoiDung"
            ]
        ) == "1"
    )

    if wrong_source != 0:

        fail(
            "Co MaNguon sai."
        )

    if wrong_status != 0:

        fail(
            "Co TrangThai sai."
        )

    if approved_content != 0:

        fail(
            "File moi tao "
            "khong duoc tu dong "
            "kiem duyet noi dung."
        )

    print(
        "Tong muc:",
        len(verify_rows),
    )

    print(
        "Noi dung day du:",
        len(verify_rows),
    )

    print(
        "MaNguon=1004:",
        len(verify_rows),
    )

    print(
        "TrangThai=ban_nhap:",
        len(verify_rows),
    )

    print(
        "DaKiemDuyetNoiDung=1:",
        approved_content,
    )

    print(
        "Cho kiem duyet:",
        len(verify_rows),
    )

    # =====================================================
    # 9. COVERAGE
    # =====================================================
    print()
    print(
        "[9] KIEM TRA BAO PHU 48 GF1"
    )
    print("-" * 120)

    used_ids = {
        clean(
            row[
                "MaMucNguPhapChuan"
            ]
        )
        for row in verify_rows
    }

    print(
        "GF1 duy nhat "
        "trong Bai 3 -> 23:",
        len(used_ids),
    )

    if len(
         used_ids
    ) != 44:

        fail(
             "Du kien Bai 3 -> 23 "
             "phai su dung 44 GF1 duy nhat. "
             f"Thuc te: {len(used_ids)}"
        )

    print(
        "44 GF1 DUY NHAT: OK"
    )

    # =====================================================
    # 10. PRINT SUMMARY
    # =====================================================
    print()
    print(
        "[10] TOM TAT NOI DUNG TUNG BAI"
    )
    print("-" * 120)

    for lesson_no in range(
        3,
        24,
    ):

        lesson_rows = [
            row
            for row in verify_rows
            if int(
                clean(
                    row[
                        "SoThuTuBai"
                    ]
                )
            ) == lesson_no
        ]

        title = clean(
            lesson_rows[0][
                "TieuDeBai"
            ]
        )

        grammar_titles = [
            clean(
                row[
                    "TenCauTruc"
                ]
            )
            for row in lesson_rows
        ]

        print()
        print(
            f"Bai {lesson_no}: "
            f"{title}"
        )

        for index, title_text in enumerate(
            grammar_titles,
            start=1,
        ):

            print(
                f"  [{index}] "
                f"{title_text}"
            )

    # =====================================================
    # 11. HASH OUTPUT
    # =====================================================
    print()
    print(
        "[11] SHA256 FILE CONTENT REVIEW"
    )
    print("-" * 120)

    output_hash = sha256_file(
        OUTPUT_FILE
    )

    print(
        output_hash
    )

    # =====================================================
    # FINAL
    # =====================================================
    print()
    print("=" * 120)
    print(
        "KET QUA 09H14"
    )
    print("=" * 120)

    print(
        "Pham vi:",
        "Bai 3 -> Bai 23",
    )

    print(
        "So bai:",
        21,
    )

    print(
        "Tong noi dung ngu phap:",
        78,
    )

    print(
        "Gioi thieu moi:",
        38,
    )

    print(
        "On tap / mo rong:",
        40,
    )

    print(
        "Noi dung co du "
        "TenCauTruc/MoTa/CachDung/ViDu:",
        78,
    )

    print(
        "Da kiem duyet noi dung:",
        0,
    )

    print(
        "Cho kiem duyet noi dung:",
        78,
    )

    print()
    print(
        "FILE CONTENT REVIEW:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "SHA256:"
    )

    print(
        output_hash
    )

    print()
    print(
        "DATABASE KHONG BI SUA."
    )

    print(
        "CHUA INSERT NGU PHAP "
        "BAI 3 -> 23."
    )

    print()
    print(
        "LUU Y:"
    )

    print(
        "GF0025-2021 DUOC DUNG "
        "DE THAM CHIEU PHAM VI "
        "VA DIEM NGU PHAP."
    )

    print(
        "MoTa / CachDung / VI DU "
        "LA NOI DUNG HOC TAP "
        "DO DO AN BIEN SOAN."
    )

    print()
    print(
        "BUOC TIEP THEO:"
    )

    print(
        "09H15 AUDIT + KIEM DUYET "
        "78 NOI DUNG TRUOC KHI INSERT SQL."
    )

    print()
    print("=" * 120)
    print("HOAN TAT")
    print("=" * 120)


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":

    try:

        main()

    except Exception as error:

        print()
        print("=" * 120)
        print(
            "09H14 THAT BAI"
        )
        print("=" * 120)

        print()
        print("Loi:")
        print(error)

        print()
        print(
            "DATABASE KHONG BI SUA."
        )

        sys.exit(1)