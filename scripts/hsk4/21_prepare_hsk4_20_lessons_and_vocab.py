# -*- coding: utf-8 -*-

"""
BUOC 21 - TAO 20 BAI HSK4 VA PHAN 1000 TU VUNG THEO CHU DE

MUC TIEU
--------
1. Doc dung 1000 tu HSK4 tu dbo.TuVungHSKChuan.
2. Xac minh khoa HSK4 MaKhoaHoc = 4.
3. Xac minh HSK4 chua co BaiHoc trong SQL.
4. Tao 20 bai hoc HSK4 o dang BAN NHAP.
5. Phan 1000 tu vao 20 bai theo CHU DE / NGU NGHIA.
6. Khong chia deu may moc.
7. Cac truong hop diem chu de yeu / mo ho se duoc gan CanReview=CO.
8. Xuat CSV de review.

TUYET DOI KHONG:
- INSERT SQL
- UPDATE SQL
- DELETE SQL
- COMMIT SQL
- TAO AUDIO
- GAN MaBaiHoc THAT

Sau Buoc 21:
- review ket qua chia 1000 tu;
- sau do moi chia 114 ngu phap;
- chia 300 chu Han;
- preview SQL;
- rollback test;
- xin xac nhan truoc COMMIT;
- cuoi cung moi tao audio ElevenLabs.
"""

import csv
import hashlib
import io
import json
import re
import sys
import unicodedata

from collections import Counter, defaultdict
from contextlib import closing
from pathlib import Path


# ============================================================
# DUONG DAN PROJECT
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT))

from database import get_connection


DATA_DIR = (
    ROOT
    / "scripts"
    / "hsk4"
    / "data"
    / "processed"
)

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


LESSONS_OUTPUT = (
    DATA_DIR
    / "lessons_hsk4_draft_20.csv"
)

VOCAB_OUTPUT = (
    DATA_DIR
    / "vocabulary_hsk4_by_lesson_draft_21.csv"
)

REVIEW_OUTPUT = (
    DATA_DIR
    / "vocabulary_hsk4_by_lesson_review_21.csv"
)

SUMMARY_OUTPUT = (
    DATA_DIR
    / "hsk4_lessons_vocab_summary_21.json"
)


COURSE_ID = 4
LEVEL_ID = 4
EXPECTED_VOCAB = 1000
EXPECTED_LESSONS = 20

# Chi dung de dieu tiet cac truong hop FALLBACK / HOA DIEM.
# Khong ep moi bai dung 50 tu.
SOFT_MAX = 60


# ============================================================
# DINH NGHIA 20 BAI HSK4
# ============================================================

LESSONS = [

    {
        "SoThuTuBai": 1,
        "TieuDe": "人与关系 - Con người và các mối quan hệ",
        "TomTat": (
            "Học từ vựng về con người, bạn bè, quan hệ xã hội, "
            "gặp gỡ, giúp đỡ và cách ứng xử với người khác."
        ),
        "strong": [
            "朋友", "关系", "同学", "同事", "客人",
            "邻居", "亲戚", "伙伴", "主人", "同伴",
            "友情", "交往", "联系", "见面", "认识",
        ],
        "keywords": [
            "bạn bè", "bạn", "quan hệ", "người",
            "đồng nghiệp", "đồng học", "hàng xóm",
            "khách", "chủ nhà", "quen biết",
            "gặp gỡ", "giúp đỡ", "quan tâm",
            "tôn trọng", "tin tưởng", "hợp tác",
            "liên hệ", "giao tiếp xã hội", "đối xử",
            "mời", "thăm", "chào", "chia tay",
        ],
    },

    {
        "SoThuTuBai": 2,
        "TieuDe": "家庭与生活 - Gia đình và cuộc sống",
        "TomTat": (
            "Học từ vựng về gia đình, tình yêu, hôn nhân, "
            "người thân và các sự kiện trong đời sống gia đình."
        ),
        "strong": [
            "家庭", "父母", "父亲", "母亲",
            "丈夫", "妻子", "夫妻", "结婚",
            "婚礼", "孩子", "儿子", "女儿",
            "爷爷", "奶奶", "姥姥", "姥爷",
        ],
        "keywords": [
            "gia đình", "cha", "mẹ", "bố", "con",
            "anh trai", "chị gái", "em trai", "em gái",
            "vợ", "chồng", "hôn nhân", "kết hôn",
            "đám cưới", "tình yêu", "yêu nhau",
            "người thân", "họ hàng", "sinh con",
            "nuôi con", "ly hôn", "ông", "bà",
        ],
    },

    {
        "SoThuTuBai": 3,
        "TieuDe": "学习让我们进步 - Học tập và giáo dục",
        "TomTat": (
            "Học từ vựng về trường học, học tập, thi cử, "
            "kiến thức, phương pháp học và giáo dục."
        ),
        "strong": [
            "学习", "学校", "大学", "学生", "老师",
            "教师", "教育", "考试", "成绩", "作业",
            "课", "课程", "毕业", "知识", "专业",
            "研究生", "博士", "教授",
        ],
        "keywords": [
            "học tập", "học", "trường học", "đại học",
            "giáo dục", "giáo viên", "học sinh",
            "sinh viên", "thi", "kỳ thi", "điểm số",
            "thành tích học tập", "bài tập",
            "bài học", "khóa học", "kiến thức",
            "chuyên ngành", "tốt nghiệp",
            "nghiên cứu sinh", "giảng viên",
            "giảng dạy", "đọc sách",
        ],
    },

    {
        "SoThuTuBai": 4,
        "TieuDe": "工作与职业 - Công việc và nghề nghiệp",
        "TomTat": (
            "Học từ vựng về công việc, nghề nghiệp, tuyển dụng, "
            "năng lực, kinh nghiệm và môi trường làm việc."
        ),
        "strong": [
            "工作", "职业", "公司", "办公室",
            "经理", "员工", "老板", "工资",
            "招聘", "面试", "经验", "加班",
            "任务", "事业", "职位",
        ],
        "keywords": [
            "công việc", "nghề nghiệp", "đi làm",
            "nhân viên", "quản lý", "giám đốc",
            "sếp", "văn phòng", "lương",
            "tuyển dụng", "phỏng vấn", "kinh nghiệm",
            "tăng ca", "nhiệm vụ", "sự nghiệp",
            "chức vụ", "nghỉ việc", "thất nghiệp",
            "năng lực làm việc", "xin việc",
        ],
    },

    {
        "SoThuTuBai": 5,
        "TieuDe": "商业与金钱 - Kinh doanh và tài chính",
        "TomTat": (
            "Học từ vựng về doanh nghiệp, kinh doanh, thị trường, "
            "ngân hàng, tiền bạc, giá cả và hoạt động tài chính."
        ),
        "strong": [
            "商业", "生意", "市场", "银行",
            "钱", "现金", "价格", "费用",
            "收入", "利润", "投资", "经济",
            "产品", "顾客", "客户", "合同",
        ],
        "keywords": [
            "kinh doanh", "thương mại", "thị trường",
            "ngân hàng", "tiền", "tiền mặt",
            "giá", "giá cả", "chi phí", "thu nhập",
            "lợi nhuận", "đầu tư", "kinh tế",
            "sản phẩm", "khách hàng", "hợp đồng",
            "mua bán", "thanh toán", "tài chính",
            "doanh nghiệp", "công ty", "quảng cáo",
        ],
    },

    {
        "SoThuTuBai": 6,
        "TieuDe": "表达自己的看法 - Giao tiếp và quan điểm",
        "TomTat": (
            "Học cách diễn đạt ý kiến, trao đổi thông tin, "
            "giải thích, thảo luận, đồng ý và phản đối."
        ),
        "strong": [
            "意见", "看法", "观点", "认为",
            "觉得", "说明", "解释", "讨论",
            "交流", "表达", "同意", "反对",
            "建议", "回答", "问题", "消息",
        ],
        "keywords": [
            "ý kiến", "quan điểm", "cho rằng",
            "nghĩ rằng", "giải thích", "thảo luận",
            "trao đổi", "biểu đạt", "diễn đạt",
            "đồng ý", "phản đối", "đề nghị",
            "gợi ý", "trả lời", "câu hỏi",
            "tin tức", "thông tin", "nói chuyện",
            "phát biểu", "thông báo", "trình bày",
        ],
    },

    {
        "SoThuTuBai": 7,
        "TieuDe": "心情与性格 - Cảm xúc, tính cách và thái độ",
        "TomTat": (
            "Học từ vựng mô tả cảm xúc, tâm trạng, tính cách, "
            "thái độ và phản ứng của con người."
        ),
        "strong": [
            "心情", "感情", "高兴", "开心",
            "难过", "伤心", "生气", "害怕",
            "紧张", "担心", "性格", "态度",
            "勇敢", "耐心", "骄傲", "失望",
        ],
        "keywords": [
            "cảm xúc", "tâm trạng", "vui", "buồn",
            "tức giận", "giận", "sợ", "lo lắng",
            "căng thẳng", "thất vọng", "tự hào",
            "tính cách", "thái độ", "dũng cảm",
            "kiên nhẫn", "ngạc nhiên", "hạnh phúc",
            "đau khổ", "bình tĩnh", "ngại",
            "xấu hổ", "hối hận",
        ],
    },

    {
        "SoThuTuBai": 8,
        "TieuDe": "健康最重要 - Sức khỏe và y tế",
        "TomTat": (
            "Học từ vựng về cơ thể, sức khỏe, bệnh tật, "
            "bệnh viện, điều trị và thói quen sống khỏe."
        ),
        "strong": [
            "健康", "身体", "医院", "医生",
            "病", "生病", "治疗", "药",
            "疼", "痛", "检查", "护士",
            "生命", "死", "死亡",
        ],
        "keywords": [
            "sức khỏe", "cơ thể", "bệnh viện",
            "bác sĩ", "bệnh", "ốm", "điều trị",
            "thuốc", "đau", "kiểm tra sức khỏe",
            "y tế", "y học", "y tá", "sinh mạng",
            "tử vong", "chết", "chữa bệnh",
            "triệu chứng", "thể lực", "mệt",
            "nghỉ ngơi", "tập thể dục",
        ],
    },

    {
        "SoThuTuBai": 9,
        "TieuDe": "日常生活与服务 - Sinh hoạt hằng ngày và dịch vụ",
        "TomTat": (
            "Học từ vựng về nhà cửa, sinh hoạt, đồ dùng, "
            "dịch vụ và những việc thường gặp trong đời sống."
        ),
        "strong": [
            "生活", "房子", "房间", "家",
            "家具", "服务", "宾馆", "酒店",
            "洗", "打扫", "修理", "钥匙",
            "门", "窗户",
        ],
        "keywords": [
            "cuộc sống", "sinh hoạt", "nhà cửa",
            "căn nhà", "phòng", "đồ dùng",
            "đồ gia dụng", "dịch vụ", "khách sạn",
            "nhà hàng", "sửa chữa", "dọn dẹp",
            "giặt", "rửa", "chìa khóa", "cửa",
            "cửa sổ", "thuê nhà", "hàng ngày",
            "hằng ngày", "tiện lợi",
        ],
    },

    {
        "SoThuTuBai": 10,
        "TieuDe": "吃饭与购物 - Ăn uống, mua sắm và tiêu dùng",
        "TomTat": (
            "Học từ vựng về món ăn, đồ uống, nhà hàng, "
            "mua sắm, cửa hàng, quần áo và tiêu dùng."
        ),
        "strong": [
            "吃", "喝", "食品", "食物", "饭",
            "菜", "水果", "蔬菜", "商店",
            "超市", "买", "卖", "衣服",
            "购物", "菜单", "味道",
        ],
        "keywords": [
            "ăn", "uống", "thức ăn", "đồ ăn",
            "thực phẩm", "món ăn", "rau", "hoa quả",
            "trái cây", "nhà hàng", "thực đơn",
            "hương vị", "mua", "bán", "mua sắm",
            "cửa hàng", "siêu thị", "quần áo",
            "giày", "tiêu dùng", "đồ uống",
        ],
    },

    {
        "SoThuTuBai": 11,
        "TieuDe": "出发吧！ - Giao thông và du lịch",
        "TomTat": (
            "Học từ vựng về phương tiện, giao thông, chuyến đi, "
            "du lịch, vé, sân bay, tàu xe và hành trình."
        ),
        "strong": [
            "旅行", "旅游", "飞机", "机场",
            "火车", "汽车", "公交", "地铁",
            "车站", "票", "出发", "到达",
            "开车", "司机", "交通", "行李",
        ],
        "keywords": [
            "du lịch", "chuyến đi", "đi lại",
            "máy bay", "sân bay", "tàu hỏa",
            "ô tô", "xe buýt", "tàu điện ngầm",
            "nhà ga", "vé", "khởi hành",
            "đến nơi", "lái xe", "tài xế",
            "giao thông", "hành lý", "hộ chiếu",
            "khách du lịch", "chuyến bay",
        ],
    },

    {
        "SoThuTuBai": 12,
        "TieuDe": "城市、地点与方向 - Thành phố, địa điểm và phương hướng",
        "TomTat": (
            "Học từ vựng về thành phố, địa điểm, vị trí, "
            "phương hướng, khoảng cách và không gian."
        ),
        "strong": [
            "城市", "地方", "地点", "位置",
            "方向", "距离", "附近", "东",
            "西", "南", "北", "路",
            "街", "中心", "农村",
        ],
        "keywords": [
            "thành phố", "địa điểm", "nơi", "vị trí",
            "phương hướng", "khoảng cách", "gần",
            "xa", "phía đông", "phía tây",
            "phía nam", "phía bắc", "đường phố",
            "trung tâm", "nông thôn", "khu vực",
            "địa phương", "bên cạnh", "xung quanh",
        ],
    },

    {
        "SoThuTuBai": 13,
        "TieuDe": "时间、计划与变化 - Thời gian, kế hoạch và thay đổi",
        "TomTat": (
            "Học cách nói về thời gian, lịch trình, kế hoạch, "
            "quá trình, sự bắt đầu, kết thúc và thay đổi."
        ),
        "strong": [
            "时间", "计划", "安排", "开始",
            "结束", "变化", "改变", "继续",
            "过程", "以前", "以后", "最近",
            "将来", "过去", "未来", "按时",
        ],
        "keywords": [
            "thời gian", "kế hoạch", "sắp xếp",
            "bắt đầu", "kết thúc", "thay đổi",
            "tiếp tục", "quá trình", "trước đây",
            "sau này", "gần đây", "tương lai",
            "quá khứ", "đúng giờ", "trì hoãn",
            "sớm", "muộn", "lịch trình",
            "giai đoạn", "dần dần",
        ],
    },

    {
        "SoThuTuBai": 14,
        "TieuDe": "天气、自然与环境 - Thời tiết, thiên nhiên và môi trường",
        "TomTat": (
            "Học từ vựng về thời tiết, khí hậu, động thực vật, "
            "thiên nhiên, tài nguyên và môi trường."
        ),
        "strong": [
            "天气", "气候", "环境", "自然",
            "空气", "雨", "雪", "风",
            "太阳", "河", "海", "山",
            "森林", "动物", "植物", "地球",
        ],
        "keywords": [
            "thời tiết", "khí hậu", "môi trường",
            "thiên nhiên", "không khí", "mưa",
            "tuyết", "gió", "mặt trời", "sông",
            "biển", "núi", "rừng", "động vật",
            "thực vật", "trái đất", "ô nhiễm",
            "tài nguyên", "nhiệt độ", "mùa",
        ],
    },

    {
        "SoThuTuBai": 15,
        "TieuDe": "科技改变生活 - Khoa học, công nghệ và Internet",
        "TomTat": (
            "Học từ vựng về khoa học, công nghệ, máy tính, "
            "điện thoại, Internet, thiết bị và kỹ thuật."
        ),
        "strong": [
            "科学", "技术", "电脑", "计算机",
            "手机", "网络", "互联网", "网站",
            "软件", "机器", "设备", "电子",
            "发明", "研究",
        ],
        "keywords": [
            "khoa học", "công nghệ", "máy tính",
            "điện thoại", "internet", "mạng",
            "trang web", "phần mềm", "máy móc",
            "thiết bị", "điện tử", "phát minh",
            "kỹ thuật", "nghiên cứu khoa học",
            "dữ liệu", "thông tin điện tử",
        ],
    },

    {
        "SoThuTuBai": 16,
        "TieuDe": "文化、艺术与媒体 - Văn hóa, nghệ thuật và truyền thông",
        "TomTat": (
            "Học từ vựng về văn hóa, nghệ thuật, phim ảnh, "
            "âm nhạc, sách báo, truyền hình và truyền thông."
        ),
        "strong": [
            "文化", "艺术", "电影", "音乐",
            "电视", "新闻", "报纸", "杂志",
            "节目", "演员", "记者", "小说",
            "故事", "表演", "歌", "画",
        ],
        "keywords": [
            "văn hóa", "nghệ thuật", "phim",
            "điện ảnh", "âm nhạc", "truyền hình",
            "tin tức", "báo", "tạp chí", "chương trình",
            "diễn viên", "phóng viên", "tiểu thuyết",
            "câu chuyện", "biểu diễn", "bài hát",
            "hội họa", "tranh", "tác phẩm",
        ],
    },

    {
        "SoThuTuBai": 17,
        "TieuDe": "运动与休闲 - Thể thao và giải trí",
        "TomTat": (
            "Học từ vựng về thể thao, thi đấu, luyện tập, "
            "sở thích, nghỉ ngơi và hoạt động giải trí."
        ),
        "strong": [
            "运动", "体育", "比赛", "足球",
            "篮球", "游泳", "跑步", "训练",
            "冠军", "娱乐", "游戏", "休息",
            "兴趣", "爱好",
        ],
        "keywords": [
            "thể thao", "thi đấu", "bóng đá",
            "bóng rổ", "bơi", "chạy bộ",
            "huấn luyện", "luyện tập", "vô địch",
            "giải trí", "trò chơi", "nghỉ ngơi",
            "sở thích", "hoạt động", "cuộc thi",
        ],
    },

    {
        "SoThuTuBai": 18,
        "TieuDe": "社会、法律与安全 - Xã hội, pháp luật và an toàn",
        "TomTat": (
            "Học từ vựng về xã hội, pháp luật, quy định, "
            "an toàn, tai nạn, cảnh sát và các vấn đề cộng đồng."
        ),
        "strong": [
            "社会", "法律", "规定", "规则",
            "安全", "危险", "警察", "事故",
            "政府", "国家", "犯罪", "责任",
            "制度", "保护",
        ],
        "keywords": [
            "xã hội", "pháp luật", "luật", "quy định",
            "quy tắc", "an toàn", "nguy hiểm",
            "cảnh sát", "tai nạn", "chính phủ",
            "quốc gia", "tội phạm", "trách nhiệm",
            "chế độ", "bảo vệ", "công dân",
            "cộng đồng", "chính sách",
        ],
    },

    {
        "SoThuTuBai": 19,
        "TieuDe": "数量、程度与比较 - Số lượng, mức độ và so sánh",
        "TomTat": (
            "Học từ vựng về số lượng, đơn vị, mức độ, "
            "kích thước, chất lượng, so sánh và đánh giá."
        ),
        "strong": [
            "数量", "数字", "增加", "减少",
            "倍", "百分之", "程度", "比较",
            "大小", "长度", "重量", "高度",
            "质量", "部分", "全部",
        ],
        "keywords": [
            "số lượng", "con số", "tăng", "giảm",
            "phần trăm", "mức độ", "so sánh",
            "kích thước", "chiều dài", "trọng lượng",
            "chiều cao", "chất lượng", "một phần",
            "toàn bộ", "đa số", "thiểu số",
            "khoảng", "xấp xỉ", "gấp", "lượng từ",
            "đơn vị",
        ],
    },

    {
        "SoThuTuBai": 20,
        "TieuDe": "把话说清楚 - Từ chức năng và diễn đạt tổng hợp",
        "TomTat": (
            "Học các phó từ, liên từ, giới từ, trợ từ, "
            "từ nối và các từ chức năng giúp diễn đạt câu HSK4 chính xác hơn."
        ),
        "strong": [
            "虽然", "但是", "而且", "不过",
            "因此", "所以", "既然", "否则",
            "即使", "尽管", "由于", "关于",
            "根据", "按照", "除了", "甚至",
        ],
        "keywords": [
            "liên từ", "phó từ", "giới từ", "trợ từ",
            "đại từ", "thán từ", "từ nối",
            "mặc dù", "nhưng", "do đó", "vì vậy",
            "nếu", "cho dù", "ngoài ra",
            "thậm chí", "theo", "căn cứ",
            "liên quan đến", "về việc",
            "logic", "ngữ khí",
        ],
    },
]


# ============================================================
# HAM HO TRO
# ============================================================

def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_text(value):
    """
    Bo dau tieng Viet nhung van giu Hanzi.
    Vi du:
        "giá cả" -> "gia ca"
        "健康" -> "健康"
    """

    text = clean(value).lower()

    text = text.replace("đ", "d")

    text = unicodedata.normalize(
        "NFD",
        text,
    )

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def contains_cjk(text):
    return bool(
        re.search(
            r"[\u3400-\u4dbf\u4e00-\u9fff]",
            text,
        )
    )


def keyword_match(text, keyword):
    text_norm = normalize_text(text)
    key_norm = normalize_text(keyword)

    if not key_norm:
        return False

    # Hanzi co the tim substring truc tiep.
    if contains_cjk(key_norm):
        return key_norm in text_norm

    # Cum tu Latin/Vietnamese:
    # dung boundary de tranh match linh tinh.
    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(key_norm)
        + r"(?![a-z0-9])"
    )

    return bool(
        re.search(
            pattern,
            text_norm,
        )
    )


def rows(cursor, sql, *params):

    cursor.execute(
        sql,
        *params,
    )

    columns = [
        item[0]
        for item in cursor.description
    ]

    return [
        dict(
            zip(
                columns,
                row,
            )
        )
        for row in cursor.fetchall()
    ]


def sha256_bytes(data):

    return hashlib.sha256(
        data
    ).hexdigest()


def sha256_file(path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def render_csv_bytes(
    fieldnames,
    data_rows,
):

    buffer = io.StringIO(
        newline=""
    )

    writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
    )

    writer.writeheader()
    writer.writerows(data_rows)

    return buffer.getvalue().encode(
        "utf-8-sig"
    )


def safe_write_bytes(
    path,
    data,
):

    """
    Khong tu dong ghi de file da ton tai neu noi dung khac.
    """

    if path.exists():

        old = path.read_bytes()

        if old == data:

            print(
                f"PASS: file da ton tai va giong het: {path.name}"
            )

            return

        raise RuntimeError(
            "FAIL: file output da ton tai "
            "nhung noi dung khac.\n"
            f"{path}\n"
            "KHONG TU DONG GHI DE."
        )

    with path.open("xb") as f:
        f.write(data)

    print(
        f"PASS: da tao {path.name}"
    )


# ============================================================
# TINH DIEM CHU DE
# ============================================================

def build_search_text(row):

    return " | ".join([
        clean(
            row.get("TuGoc")
        ),
        clean(
            row.get("ChuHan")
        ),
        clean(
            row.get("TuLoai")
        ),
        clean(
            row.get(
                "NghiaTiengVietThamChieu"
            )
        ),
    ])


def score_lesson(
    row,
    lesson,
):

    text = build_search_text(row)

    score = 0
    matches = []

    # Tu khoa manh.
    for keyword in lesson["strong"]:

        if keyword_match(
            text,
            keyword,
        ):

            score += 10

            matches.append(
                f"MANH:{keyword}"
            )

    # Tu khoa thuong.
    for keyword in lesson["keywords"]:

        if keyword_match(
            text,
            keyword,
        ):

            # Cum dai duoc uu tien hon.
            key_len = len(
                normalize_text(keyword)
            )

            weight = 3

            if (
                " " in keyword
                or key_len >= 5
            ):
                weight = 5

            score += weight

            matches.append(
                f"KW:{keyword}"
            )

    # ========================================================
    # GOI Y THEO TU LOAI
    # ========================================================

    pos = clean(
        row.get("TuLoai")
    )

    pos_norm = normalize_text(pos)

    lesson_no = int(
        lesson["SoThuTuBai"]
    )

    # Luong tu / so tu -> bai 19
    if lesson_no == 19:

        if (
            "量" in pos
            or "数" in pos
            or "luong tu" in pos_norm
            or "so tu" in pos_norm
        ):

            score += 5
            matches.append(
                "POS:SO_LUONG"
            )

    # Tu chuc nang -> bai 20.
    if lesson_no == 20:

        function_signals = [
            "副",
            "连",
            "介",
            "助",
            "代",
            "叹",
            "pho tu",
            "lien tu",
            "gioi tu",
            "tro tu",
            "dai tu",
            "than tu",
        ]

        if any(
            signal in pos_norm
            for signal in function_signals
        ):

            score += 4

            matches.append(
                "POS:TU_CHUC_NANG"
            )

    return (
        score,
        matches,
    )


def fallback_candidates(row):

    """
    Chi dung khi khong co bat ky tu khoa chu de nao khop.

    Day KHONG phai ket qua chot.
    Dong fallback se co CanReview=CO.
    """

    pos = normalize_text(
        row.get("TuLoai")
    )

    if (
        "量" in clean(row.get("TuLoai"))
        or "数" in clean(row.get("TuLoai"))
        or "luong tu" in pos
        or "so tu" in pos
    ):

        return [19]

    function_signals = [
        "副",
        "连",
        "介",
        "助",
        "代",
        "叹",
        "pho tu",
        "lien tu",
        "gioi tu",
        "tro tu",
        "dai tu",
        "than tu",
    ]

    if any(
        item in pos
        for item in function_signals
    ):

        return [20]

    # Nhung bai rong co the tiep nhan tu tong quat.
    return [
        1,
        6,
        7,
        9,
        13,
        19,
        20,
    ]


def choose_lowest_load(
    lesson_numbers,
    counts,
):

    available = [
        n
        for n in lesson_numbers
        if counts[n] < SOFT_MAX
    ]

    if not available:
        available = list(
            lesson_numbers
        )

    return min(
        available,
        key=lambda n: (
            counts[n],
            n,
        ),
    )


# ============================================================
# PHAN TU VUNG
# ============================================================

def assign_vocabulary(
    vocab_rows,
):

    counts = Counter()

    assignments = []

    for row in vocab_rows:

        scored = []

        score_details = {}

        for lesson in LESSONS:

            lesson_no = int(
                lesson["SoThuTuBai"]
            )

            score, matches = score_lesson(
                row,
                lesson,
            )

            scored.append(
                (
                    lesson_no,
                    score,
                )
            )

            score_details[
                lesson_no
            ] = matches

        scored.sort(
            key=lambda item: (
                -item[1],
                item[0],
            )
        )

        top_score = scored[0][1]

        top_lessons = [
            lesson_no
            for lesson_no, score
            in scored
            if score == top_score
        ]

        second_score = 0

        distinct_scores = sorted(
            {
                score
                for _, score
                in scored
            },
            reverse=True,
        )

        if len(distinct_scores) >= 2:

            second_score = (
                distinct_scores[1]
            )

        # ====================================================
        # CO TU KHOA CHU DE
        # ====================================================

        if top_score > 0:

            chosen = choose_lowest_load(
                top_lessons,
                counts,
            )

            gap = (
                top_score
                - second_score
            )

            matches = (
                score_details[
                    chosen
                ]
            )

            # Neu bang diem hoac chenhlech qua thap -> review.
            if (
                len(top_lessons) > 1
                or gap <= 2
            ):

                can_review = "CO"

                method = (
                    "CHU_DE_NHUNG_MO_HO"
                )

            else:

                can_review = "KHONG"

                method = (
                    "CHU_DE_RO"
                )

        # ====================================================
        # KHONG CO TU KHOA
        # ====================================================

        else:

            candidates = (
                fallback_candidates(
                    row
                )
            )

            chosen = choose_lowest_load(
                candidates,
                counts,
            )

            matches = []

            gap = 0

            can_review = "CO"

            method = (
                "FALLBACK_CAN_REVIEW"
            )

        counts[
            chosen
        ] += 1

        lesson = next(
            item
            for item in LESSONS
            if int(
                item["SoThuTuBai"]
            ) == chosen
        )

        assignments.append({

            "MaTuHSK":
                clean(
                    row.get(
                        "MaTuHSK"
                    )
                ),

            "MaMucNoiBo":
                clean(
                    row.get(
                        "MaMucNoiBo"
                    )
                ),

            "SoThuTuNguon":
                clean(
                    row.get(
                        "SoThuTuNguon"
                    )
                ),

            "TuGoc":
                clean(
                    row.get(
                        "TuGoc"
                    )
                ),

            "ChuHan":
                clean(
                    row.get(
                        "ChuHan"
                    )
                ),

            "PhienAm":
                clean(
                    row.get(
                        "PhienAm"
                    )
                ),

            "TuLoai":
                clean(
                    row.get(
                        "TuLoai"
                    )
                ),

            "NghiaTiengViet":
                clean(
                    row.get(
                        "NghiaTiengVietThamChieu"
                    )
                ),

            # Chua phai MaBaiHoc SQL.
            "MaBaiHocTam":
                f"H4-L{chosen:02d}",

            "SoThuTuBai":
                chosen,

            "TieuDeBaiHoc":
                lesson["TieuDe"],

            "ThuTuTrongBai":
                "",

            "DiemChuDe":
                top_score,

            "DiemChuDeThuHai":
                second_score,

            "DoChenhDiem":
                (
                    top_score
                    - second_score
                ),

            "TuKhoaKhop":
                " | ".join(
                    matches
                ),

            "CachPhan":
                method,

            "CanReview":
                can_review,
        })

    return (
        assignments,
        counts,
    )


# ============================================================
# GAN THU TU TRONG TUNG BAI
# ============================================================

def assign_order_in_lesson(
    assignments,
):

    grouped = defaultdict(
        list
    )

    for row in assignments:

        grouped[
            int(
                row["SoThuTuBai"]
            )
        ].append(row)

    for lesson_no in range(
        1,
        EXPECTED_LESSONS + 1,
    ):

        items = grouped[
            lesson_no
        ]

        # Giu thu tu nguon HSK de de truy vet.
        def sort_key(row):

            source_order = clean(
                row.get(
                    "SoThuTuNguon"
                )
            )

            try:
                source_order_int = int(
                    source_order
                )
            except Exception:
                source_order_int = 999999

            return (
                source_order_int,
                clean(
                    row.get(
                        "MaMucNoiBo"
                    )
                ),
            )

        items.sort(
            key=sort_key
        )

        for index, row in enumerate(
            items,
            start=1,
        ):

            row[
                "ThuTuTrongBai"
            ] = index


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 86)

    print(
        "BUOC 21 - TAO 20 BAI HSK4 "
        "VA PHAN 1000 TU VUNG THEO CHU DE"
    )

    print("=" * 86)

    print(
        "CHI SELECT SQL - "
        "KHONG INSERT / UPDATE / DELETE / COMMIT"
    )

    # ========================================================
    # 1. KIEM TRA SQL HSK4
    # ========================================================

    print(
        "\n[1] KIEM TRA KHOA HSK4"
    )

    with closing(
        get_connection()
    ) as conn:

        with closing(
            conn.cursor()
        ) as cur:

            courses = rows(
                cur,
                """
                SELECT
                    MaKhoaHoc,
                    MaCapDo,
                    MaKyHieu,
                    TieuDe,
                    TrangThai
                FROM dbo.KhoaHoc
                WHERE MaKhoaHoc = ?
                """,
                COURSE_ID,
            )

            if len(courses) != 1:

                raise RuntimeError(
                    "FAIL: khong tim thay "
                    "dung 1 khoa HSK4 MaKhoaHoc=4."
                )

            course = courses[0]

            print(
                "MaKhoaHoc:",
                course["MaKhoaHoc"],
            )

            print(
                "MaCapDo:",
                course["MaCapDo"],
            )

            print(
                "MaKyHieu:",
                course["MaKyHieu"],
            )

            print(
                "TieuDe:",
                course["TieuDe"],
            )

            print(
                "TrangThai:",
                course["TrangThai"],
            )

            if int(
                course["MaCapDo"]
            ) != LEVEL_ID:

                raise RuntimeError(
                    "FAIL: MaCapDo HSK4 "
                    "khong bang 4."
                )

            if clean(
                course["MaKyHieu"]
            ) != "HSK4-CORE":

                raise RuntimeError(
                    "FAIL: MaKyHieu khong phai HSK4-CORE."
                )

            print(
                "PASS: khoa HSK4 dung."
            )

            # =================================================
            # 2. HSK4 CHUA CO BAI HOC
            # =================================================

            print(
                "\n[2] KIEM TRA BAI HOC HSK4 HIEN TAI"
            )

            existing_lessons = rows(
                cur,
                """
                SELECT
                    MaBaiHoc,
                    SoThuTuBai,
                    TieuDe,
                    TrangThai
                FROM dbo.BaiHoc
                WHERE MaKhoaHoc = ?
                ORDER BY
                    SoThuTuBai,
                    MaBaiHoc
                """,
                COURSE_ID,
            )

            print(
                "So BaiHoc HSK4 hien co:",
                len(existing_lessons),
            )

            if existing_lessons:

                print(
                    "\nCAC BAI DA TON TAI:"
                )

                for item in existing_lessons:

                    print(
                        item["MaBaiHoc"],
                        "|",
                        item["SoThuTuBai"],
                        "|",
                        item["TieuDe"],
                        "|",
                        item["TrangThai"],
                    )

                raise RuntimeError(
                    "FAIL: HSK4 da co BaiHoc trong SQL. "
                    "DUNG LAI de tranh tao plan trung."
                )

            print(
                "PASS: HSK4 chua co BaiHoc."
            )

            # =================================================
            # 3. DOC 1000 TU HSK4
            # =================================================

            print(
                "\n[3] DOC TU VUNG HSK4 CHUAN"
            )

            vocab_rows = rows(
                cur,
                """
                SELECT
                    MaTuHSK,
                    MaMucNoiBo,
                    MaCapDo,
                    SoThuTuNguon,
                    TuGoc,
                    ChuHan,
                    BienThe,
                    PhienAmNguon,
                    PhienAm,
                    TuLoai,
                    NghiaTiengVietThamChieu,
                    DaKiemTraNguon,
                    GhiChu
                FROM dbo.TuVungHSKChuan
                WHERE MaCapDo = ?
                ORDER BY
                    CASE
                        WHEN SoThuTuNguon IS NULL
                        THEN 2147483647
                        ELSE SoThuTuNguon
                    END,
                    MaTuHSK
                """,
                LEVEL_ID,
            )

            # Read-only.
            conn.rollback()

    print(
        "Tong tu HSK4:",
        len(vocab_rows),
    )

    if len(
        vocab_rows
    ) != EXPECTED_VOCAB:

        raise RuntimeError(
            "FAIL: can dung 1000 tu HSK4, "
            f"hien co {len(vocab_rows)}."
        )

    ids = [
        clean(
            item["MaTuHSK"]
        )
        for item in vocab_rows
    ]

    internal_ids = [
        clean(
            item["MaMucNoiBo"]
        )
        for item in vocab_rows
    ]

    if len(
        set(ids)
    ) != EXPECTED_VOCAB:

        raise RuntimeError(
            "FAIL: MaTuHSK HSK4 khong duy nhat."
        )

    if len(
        set(internal_ids)
    ) != EXPECTED_VOCAB:

        raise RuntimeError(
            "FAIL: MaMucNoiBo HSK4 khong duy nhat."
        )

    bad_internal_ids = [
        value
        for value in internal_ids
        if not value.startswith(
            "L4-"
        )
    ]

    if bad_internal_ids:

        raise RuntimeError(
            "FAIL: co MaMucNoiBo "
            "khong bat dau bang L4-: "
            + str(
                bad_internal_ids[:10]
            )
        )

    missing_hanzi = [
        item
        for item in vocab_rows
        if not clean(
            item.get(
                "ChuHan"
            )
        )
    ]

    missing_pinyin = [
        item
        for item in vocab_rows
        if not clean(
            item.get(
                "PhienAm"
            )
        )
    ]

    if missing_hanzi:

        raise RuntimeError(
            "FAIL: co tu HSK4 thieu ChuHan."
        )

    if missing_pinyin:

        raise RuntimeError(
            "FAIL: co tu HSK4 thieu PhienAm."
        )

    print(
        "PASS: 1000 MaTuHSK duy nhat."
    )

    print(
        "PASS: 1000 MaMucNoiBo duy nhat."
    )

    print(
        "PASS: 1000/1000 co ChuHan."
    )

    print(
        "PASS: 1000/1000 co PhienAm."
    )

    # ========================================================
    # 4. KIEM TRA DINH NGHIA 20 BAI
    # ========================================================

    print(
        "\n[4] KIEM TRA 20 BAI HSK4"
    )

    lesson_numbers = [
        int(
            item["SoThuTuBai"]
        )
        for item in LESSONS
    ]

    if lesson_numbers != list(
        range(
            1,
            EXPECTED_LESSONS + 1,
        )
    ):

        raise RuntimeError(
            "FAIL: 20 bai phai co SoThuTuBai 1-20."
        )

    titles = [
        clean(
            item["TieuDe"]
        )
        for item in LESSONS
    ]

    if len(
        set(titles)
    ) != EXPECTED_LESSONS:

        raise RuntimeError(
            "FAIL: TieuDe bai hoc bi trung."
        )

    print(
        "PASS: 20 bai thu tu 1-20."
    )

    print(
        "PASS: 20 tieu de duy nhat."
    )

    # ========================================================
    # 5. PHAN 1000 TU
    # ========================================================

    print(
        "\n[5] PHAN 1000 TU THEO CHU DE"
    )

    assignments, counts = (
        assign_vocabulary(
            vocab_rows
        )
    )

    if len(
        assignments
    ) != EXPECTED_VOCAB:

        raise RuntimeError(
            "FAIL: khong phan du 1000 tu."
        )

    assigned_ids = [
        clean(
            item["MaTuHSK"]
        )
        for item in assignments
    ]

    if len(
        set(assigned_ids)
    ) != EXPECTED_VOCAB:

        raise RuntimeError(
            "FAIL: co MaTuHSK bi lap "
            "sau khi phan bai."
        )

    invalid_lessons = [
        item
        for item in assignments
        if int(
            item["SoThuTuBai"]
        ) not in range(1, 21)
    ]

    if invalid_lessons:

        raise RuntimeError(
            "FAIL: co tu gan sai SoThuTuBai."
        )

    assign_order_in_lesson(
        assignments
    )

    print(
        "PASS: 1000/1000 tu da co bai."
    )

    # ========================================================
    # 6. THONG KE
    # ========================================================

    print(
        "\n[6] THONG KE 20 BAI"
    )

    review_rows = [
        item
        for item in assignments
        if clean(
            item["CanReview"]
        ) == "CO"
    ]

    clear_rows = [
        item
        for item in assignments
        if clean(
            item["CanReview"]
        ) == "KHONG"
    ]

    methods = Counter(
        clean(
            item["CachPhan"]
        )
        for item in assignments
    )

    lesson_rows = []

    for lesson in LESSONS:

        lesson_no = int(
            lesson["SoThuTuBai"]
        )

        lesson_items = [
            item
            for item in assignments
            if int(
                item["SoThuTuBai"]
            ) == lesson_no
        ]

        lesson_review = [
            item
            for item in lesson_items
            if clean(
                item["CanReview"]
            ) == "CO"
        ]

        lesson_row = {

            "MaBaiHocTam":
                f"H4-L{lesson_no:02d}",

            "MaKhoaHoc":
                COURSE_ID,

            "SoThuTuBai":
                lesson_no,

            "TieuDe":
                lesson["TieuDe"],

            "TomTat":
                lesson["TomTat"],

            "TrangThai":
                "ban_nhap",

            "SoTuVungDuKien":
                len(
                    lesson_items
                ),

            "SoTuCanReview":
                len(
                    lesson_review
                ),
        }

        lesson_rows.append(
            lesson_row
        )

        print(
            f"Bai {lesson_no:02d} | "
            f"{len(lesson_items):3d} tu | "
            f"review={len(lesson_review):3d} | "
            f"{lesson['TieuDe']}"
        )

    if sum(
        int(
            item["SoTuVungDuKien"]
        )
        for item in lesson_rows
    ) != EXPECTED_VOCAB:

        raise RuntimeError(
            "FAIL: tong SoTuVungDuKien "
            "khong bang 1000."
        )

    empty_lessons = [
        item
        for item in lesson_rows
        if int(
            item["SoTuVungDuKien"]
        ) == 0
    ]

    if empty_lessons:

        raise RuntimeError(
            "FAIL: co bai khong co tu vung."
        )

    print(
        "\nTu phan theo chu de ro:",
        len(clear_rows),
    )

    print(
        "Tu can review:",
        len(review_rows),
    )

    print(
        "Cach phan:"
    )

    for key, value in sorted(
        methods.items()
    ):

        print(
            f"  {key}: {value}"
        )

    # ========================================================
    # 7. CHUAN BI CSV BAI HOC
    # ========================================================

    print(
        "\n[7] GHI lessons_hsk4_draft_20.csv"
    )

    lesson_fields = [
        "MaBaiHocTam",
        "MaKhoaHoc",
        "SoThuTuBai",
        "TieuDe",
        "TomTat",
        "TrangThai",
        "SoTuVungDuKien",
        "SoTuCanReview",
    ]

    lesson_bytes = render_csv_bytes(
        lesson_fields,
        lesson_rows,
    )

    safe_write_bytes(
        LESSONS_OUTPUT,
        lesson_bytes,
    )

    # ========================================================
    # 8. GHI 1000 TU DA PHAN BAI
    # ========================================================

    print(
        "\n[8] GHI vocabulary_hsk4_by_lesson_draft_21.csv"
    )

    vocab_fields = [
        "MaTuHSK",
        "MaMucNoiBo",
        "SoThuTuNguon",
        "TuGoc",
        "ChuHan",
        "PhienAm",
        "TuLoai",
        "NghiaTiengViet",
        "MaBaiHocTam",
        "SoThuTuBai",
        "TieuDeBaiHoc",
        "ThuTuTrongBai",
        "DiemChuDe",
        "DiemChuDeThuHai",
        "DoChenhDiem",
        "TuKhoaKhop",
        "CachPhan",
        "CanReview",
    ]

    vocab_bytes = render_csv_bytes(
        vocab_fields,
        assignments,
    )

    safe_write_bytes(
        VOCAB_OUTPUT,
        vocab_bytes,
    )

    # ========================================================
    # 9. GHI FILE CAC TU CAN REVIEW
    # ========================================================

    print(
        "\n[9] GHI vocabulary_hsk4_by_lesson_review_21.csv"
    )

    review_rows_sorted = sorted(
        review_rows,
        key=lambda item: (
            int(
                item["SoThuTuBai"]
            ),
            int(
                item["ThuTuTrongBai"]
            ),
        ),
    )

    review_bytes = render_csv_bytes(
        vocab_fields,
        review_rows_sorted,
    )

    safe_write_bytes(
        REVIEW_OUTPUT,
        review_bytes,
    )

    # ========================================================
    # 10. HASH OUTPUT
    # ========================================================

    lessons_hash = sha256_file(
        LESSONS_OUTPUT
    )

    vocab_hash = sha256_file(
        VOCAB_OUTPUT
    )

    review_hash = sha256_file(
        REVIEW_OUTPUT
    )

    # ========================================================
    # 11. SUMMARY JSON
    # ========================================================

    print(
        "\n[10] GHI SUMMARY"
    )

    summary = {

        "buoc": "21",

        "status": "PASS",

        "MaKhoaHoc": COURSE_ID,

        "MaCapDo": LEVEL_ID,

        "so_bai": EXPECTED_LESSONS,

        "tong_tu_vung_hsk4":
            EXPECTED_VOCAB,

        "tu_chu_de_ro":
            len(clear_rows),

        "tu_can_review":
            len(review_rows),

        "cach_phan":
            dict(methods),

        "phan_bo_bai": [
            {
                "SoThuTuBai":
                    item[
                        "SoThuTuBai"
                    ],

                "TieuDe":
                    item[
                        "TieuDe"
                    ],

                "SoTuVung":
                    item[
                        "SoTuVungDuKien"
                    ],

                "SoTuCanReview":
                    item[
                        "SoTuCanReview"
                    ],
            }
            for item in lesson_rows
        ],

        "outputs": {

            "lessons": {
                "path":
                    str(
                        LESSONS_OUTPUT
                    ),
                "sha256":
                    lessons_hash,
            },

            "vocabulary": {
                "path":
                    str(
                        VOCAB_OUTPUT
                    ),
                "sha256":
                    vocab_hash,
            },

            "review": {
                "path":
                    str(
                        REVIEW_OUTPUT
                    ),
                "sha256":
                    review_hash,
            },
        },

        "ghi_sql": False,

        "tao_bai_hoc_sql": False,

        "gan_tuvungbaihoc_sql": False,

        "tao_audio": False,
    }

    summary_text = (
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    ).encode(
        "utf-8"
    )

    safe_write_bytes(
        SUMMARY_OUTPUT,
        summary_text,
    )

    # ========================================================
    # 12. KET QUA CUOI
    # ========================================================

    print(
        "\n" + "=" * 86
    )

    print(
        "PASS: BUOC 21 HOAN THANH"
    )

    print(
        "=" * 86
    )

    print(
        "So bai:",
        EXPECTED_LESSONS,
    )

    print(
        "Tong tu HSK4:",
        EXPECTED_VOCAB,
    )

    print(
        "Da phan vao bai:",
        len(assignments),
    )

    print(
        "Tu chu de ro:",
        len(clear_rows),
    )

    print(
        "Tu can review:",
        len(review_rows),
    )

    print(
        "\nLESSONS:"
    )

    print(
        LESSONS_OUTPUT
    )

    print(
        "SHA256:"
    )

    print(
        lessons_hash
    )

    print(
        "\nVOCABULARY:"
    )

    print(
        VOCAB_OUTPUT
    )

    print(
        "SHA256:"
    )

    print(
        vocab_hash
    )

    print(
        "\nREVIEW:"
    )

    print(
        REVIEW_OUTPUT
    )

    print(
        "SHA256:"
    )

    print(
        review_hash
    )

    print(
        "\nSUMMARY:"
    )

    print(
        SUMMARY_OUTPUT
    )

    print(
        "\nKHONG GHI SQL."
    )

    print(
        "KHONG TAO AUDIO."
    )

    print(
        "CHUA GAN MaBaiHoc THAT."
    )

    print(
        "CHUA INSERT TuVungBaiHoc."
    )

    print(
        "=" * 86
    )


if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print(
            "\nFAIL:",
            exc,
        )

        raise SystemExit(1)