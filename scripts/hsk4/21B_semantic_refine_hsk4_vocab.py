# -*- coding: utf-8 -*-

"""
BUOC 21B - TINH CHINH PHAN 1000 TU HSK4 THEO NGU NGHIA

INPUT:
    vocabulary_hsk4_by_lesson_draft_21A.csv
    lessons_hsk4_draft_20.csv

OUTPUT:
    vocabulary_hsk4_by_lesson_draft_21B.csv
    vocabulary_hsk4_by_lesson_review_21B.csv
    vocabulary_hsk4_by_lesson_changes_21B.csv
    lessons_hsk4_draft_20_21B.csv
    hsk4_lessons_vocab_summary_21B.json

NGUYEN TAC:
- Khong chia deu may moc.
- Khong ep bai ve 50 tu.
- Dung 434 dong Step21 da danh dau CHU_DE_RO lam seed.
- Dung Hanzi + nghia Viet + tu loai.
- Dung bo tu khoa chu de da mo rong.
- Sua cac truong hop sai ro rang bang MANUAL_OVERRIDES.
- Tu con mo ho van duoc gan bai TAM, nhung CanReview21B=CO.
- Khong sua file Step21/21A.
- KHONG GHI SQL.
- KHONG TAO AUDIO.
"""

import csv
import hashlib
import io
import json
import math
import re
import unicodedata

from collections import Counter, defaultdict
from pathlib import Path


# ============================================================
# PATH
# ============================================================

BASE = Path(
    r"D:\DATN1\scripts\hsk4\data\processed"
)

SOURCE = (
    BASE
    / "vocabulary_hsk4_by_lesson_draft_21A.csv"
)

LESSON_SOURCE = (
    BASE
    / "lessons_hsk4_draft_20.csv"
)

OUTPUT = (
    BASE
    / "vocabulary_hsk4_by_lesson_draft_21B.csv"
)

REVIEW_OUTPUT = (
    BASE
    / "vocabulary_hsk4_by_lesson_review_21B.csv"
)

CHANGES_OUTPUT = (
    BASE
    / "vocabulary_hsk4_by_lesson_changes_21B.csv"
)

LESSON_OUTPUT = (
    BASE
    / "lessons_hsk4_draft_20_21B.csv"
)

SUMMARY_OUTPUT = (
    BASE
    / "hsk4_lessons_vocab_summary_21B.json"
)


# ============================================================
# SNAPSHOT BAT BUOC
# ============================================================

EXPECTED_SOURCE_SHA256 = (
    "f991c2a26d0abe9e38b93fbb472f6e0269e62a4c31910ee58272c1bfcebf96ab"
)

EXPECTED_LESSON_SHA256 = (
    "a542e017dcc116451399258de617178d31dd91121440dbe64ad4efa27364ed0b"
)

EXPECTED_ROWS = 1000
EXPECTED_LESSONS = 20


# ============================================================
# TEN 20 BAI
# ============================================================

LESSON_TITLES = {
    1: "人与关系 - Con người và các mối quan hệ",
    2: "家庭与生活 - Gia đình và cuộc sống",
    3: "学习让我们进步 - Học tập và giáo dục",
    4: "工作与职业 - Công việc và nghề nghiệp",
    5: "商业与金钱 - Kinh doanh và tài chính",
    6: "表达自己的看法 - Giao tiếp và quan điểm",
    7: "心情与性格 - Cảm xúc, tính cách và thái độ",
    8: "健康最重要 - Sức khỏe và y tế",
    9: "日常生活与服务 - Sinh hoạt hằng ngày và dịch vụ",
    10: "吃饭与购物 - Ăn uống, mua sắm và tiêu dùng",
    11: "出发吧！ - Giao thông và du lịch",
    12: "城市、地点与方向 - Thành phố, địa điểm và phương hướng",
    13: "时间、计划与变化 - Thời gian, kế hoạch và thay đổi",
    14: "天气、自然与环境 - Thời tiết, thiên nhiên và môi trường",
    15: "科技改变生活 - Khoa học, công nghệ và Internet",
    16: "文化、艺术与媒体 - Văn hóa, nghệ thuật và truyền thông",
    17: "运动与休闲 - Thể thao và giải trí",
    18: "社会、法律与安全 - Xã hội, pháp luật và an toàn",
    19: "数量、程度与比较 - Số lượng, mức độ và so sánh",
    20: "把话说清楚 - Từ chức năng và diễn đạt tổng hợp",
}


# ============================================================
# CAC TRUONG HOP DA XAC DINH RO
# ============================================================

MANUAL_OVERRIDES = {

    # Gia dinh
    "阿姨": 2,
    "宝宝": 2,

    # Hoc tap
    "本科": 3,
    "毕业": 3,
    "毕业生": 3,
    "讲座": 3,
    "词汇": 3,

    # Tai chinh
    "财产": 5,
    "财富": 5,
    "利息": 5,

    # Suc khoe
    "打针": 8,
    "轮椅": 8,
    "发烧": 8,

    # Sinh hoat / dich vu
    "冰箱": 9,
    "包裹": 9,
    "快递": 9,
    "电梯": 9,
    "窗户": 9,
    "暖气": 9,
    "闹钟": 9,
    "装修": 9,
    "上楼": 9,
    "下楼": 9,

    # An uong / mua sam
    "瓜": 10,
    "西瓜": 10,
    "黄瓜": 10,
    "海鲜": 10,
    "豆腐": 10,
    "茶叶": 10,
    "百货": 10,
    "纯净水": 10,
    "矿泉水": 10,
    "开水": 10,

    # Giao thong
    "巴士": 11,
    "大巴": 11,
    "高铁": 11,
    "长途": 11,
    "航空": 11,
    "电动车": 11,
    "导游": 11,
    "倒车": 11,

    # Dia diem
    "地址": 12,

    # Thien nhien
    "打雷": 14,
    "闪电": 14,
    "冰雪": 14,

    # Cong nghe
    "登录": 15,
    "电源": 15,
    "充电器": 15,
    "充电": 15,
    "数据": 15,
    "网络": 15,
    "网址": 15,
    "密码": 15,
    "耳机": 15,

    # Van hoa
    "传统": 16,
    "动画片": 16,

    # The thao
    "操场": 17,
    "运动员": 17,
    "运动会": 17,
    "亚运会": 17,

    # Xa hoi / phap luat
    "爱国": 18,
    "禁止": 18,
    "法官": 18,
    "法律": 18,
    "律师": 18,
    "政府": 18,
    "总统": 18,

    # So luong
    "打": 19,

    # Tu chuc nang
    "啊": 20,
    "呀": 20,
}


# ============================================================
# SPOT CHECK BAT BUOC
# Neu 21B dua cac tu nay sai bai -> FAIL
# ============================================================

EXPECTED_SPOT_CHECKS = {
    "高铁": 11,
    "瓜": 10,
    "讲座": 3,
    "禁止": 18,
    "快递": 9,
    "利息": 5,
    "轮椅": 8,
    "充电器": 15,
    "法官": 18,
    "航空": 11,
    "冰箱": 9,
    "财产": 5,
    "打针": 8,
    "打雷": 14,
    "登录": 15,
    "百货": 10,
    "茶叶": 10,
    "长途": 11,
    "爱国": 18,
    "宝宝": 2,
    "传统": 16,
    "操场": 17,
    "电梯": 9,
    "电源": 15,
    "地址": 12,
}


# ============================================================
# TU KHOA HANZI
# ============================================================

HANZI_RULES = {

    1: """
朋友 同事 同学 邻居 亲戚 伙伴 友谊 关系
交往 联系 聚会 看望 约会 居民 亲密
""",

    2: """
阿姨 宝宝 宝贝 家庭 父母 父亲 母亲
丈夫 妻子 夫妻 结婚 婚姻 婚礼 孩子
儿子 女儿 爷爷 奶奶 姐妹 童年
幼儿园 大哥 大姐 大妈 大爷
""",

    3: """
学习 学校 大学 学生 老师 教师 教育
考试 成绩 作业 课程 毕业 知识 专业
本科 博士 教授 讲座 词汇 培训 阅读
参考 教材
""",

    4: """
工作 职业 公司 办公室 经理 员工 老板
工资 招聘 面试 加班 任务 事业 职位
待遇 担任 项目 就业
""",

    5: """
商业 生意 市场 银行 现金 价格 费用 收入
利润 投资 经济 产品 顾客 客户 合同
财产 财富 利息 促销 出售 倒闭 进口
出口 贸易 企业
""",

    6: """
意见 看法 观点 认为 觉得 说明 解释
讨论 交流 表达 同意 反对 建议 回答
问题 消息 辩论 采访 答案 结论 描写
概括 语音 说服
""",

    7: """
心情 感情 情绪 高兴 开心 难过 伤心
生气 害怕 紧张 担心 性格 态度 勇敢
耐心 骄傲 失望 表情 表扬 称赞 吃惊
得意 泪水 眼泪 怀念 喜爱 兴趣 心理
调皮 老实 诚实
""",

    8: """
健康 身体 医院 医生 病 生病 治疗 药
疼 痛 检查 护士 生命 打针 发烧 呼吸
轮椅 肚子 胸部 体重 减肥
""",

    9: """
生活 房子 房间 家 家具 服务 宾馆 酒店
洗 打扫 修理 钥匙 门 窗户 冰箱 电梯
暖气 闹钟 装修 快递 包裹 上楼 下楼
住宅
""",

    10: """
吃 喝 食品 食物 饭 菜 水果 蔬菜 商店
超市 买 卖 衣服 购物 菜单 味道 百货
茶叶 豆腐 瓜 西瓜 黄瓜 海鲜 矿泉水
纯净水 打折 套餐
""",

    11: """
旅行 旅游 飞机 机场 火车 汽车 公交
地铁 车站 票 出发 到达 开车 司机
交通 行李 巴士 大巴 高铁 长途 航空
导游 倒车 电动车
""",

    12: """
城市 地方 地点 位置 方向 距离 附近
东 西 南 北 路 街 中心 农村 地址
地面 地下 市区 陆地 大陆 街道 入口
""",

    13: """
时间 计划 安排 开始 结束 变化 改变
继续 过程 以前 以后 最近 将来 过去
未来 按时 推迟 期限 准时 延长 延期
延续 阶段 日历 下个月 来得及 来不及
事先
""",

    14: """
天气 气候 环境 自然 空气 雨 雪 风
太阳 河 海 山 森林 动物 植物 地球
冰雪 打雷 闪电 潮湿 寒冷 春季 夏季
秋季 冬季 风景 海水 树林 松树 资源
""",

    15: """
科学 技术 电脑 计算机 手机 网络 互联网
网站 软件 机器 设备 电子 发明 数据
登录 电源 充电 充电器 耳机 程序 操作
测试 数码 维修 装置 密码 型号
""",

    16: """
文化 艺术 电影 音乐 电视 新闻 报纸
杂志 节目 演员 记者 小说 故事 表演
歌 画 传统 动画片 唱片 镜头 角色
神话 著作
""",

    17: """
运动 体育 比赛 足球 篮球 游泳 跑步
训练 冠军 娱乐 游戏 操场 比分 运动员
运动会 亚运会 登山
""",

    18: """
社会 法律 规定 规则 安全 危险 警察
事故 政府 国家 犯罪 责任 制度 保护
爱国 法官 律师 禁止 纪律 官方 总统
外交官 战争 战斗 士兵 战士 敌人
""",

    19: """
数量 数字 增加 减少 倍 百分 程度 比较
大小 长度 重量 高度 质量 部分 全部
尺寸 毫米 毫升 厘米 含量 平均 规模
测量 尺 尺子 分之
""",

    20: """
虽然 但是 而且 不过 因此 所以 既然
否则 即使 尽管 由于 关于 根据 按照
除了 甚至 此外 对于 反而 或许 几乎
格外 极其 即将 急忙 渐渐 尽快 竟然
究竟 可见 立即 陆续 哪怕 是否 似乎
万一 未必 无论 相反 依然 一律 一再
以及 于是 再三 总之
""",
}


# ============================================================
# TU KHOA NGHIA TIENG VIET
# ============================================================

VI_RULES = {

    1: """
bạn bè|bạn thân|đồng nghiệp|đồng học|hàng xóm|
họ hàng|người quen|đối tác|bạn đồng hành|
gặp gỡ|tụ họp|hẹn hò|thăm ai|mối quan hệ|
giao tiếp xã hội|liên hệ|làm quen|chia tay tình cảm
""",

    2: """
gia đình|cha mẹ|bố mẹ|mẹ kế|bảo mẫu|em bé|
trẻ sơ sinh|trẻ em|vợ|chồng|hôn nhân|kết hôn|
đám cưới|anh trai|chị gái|em trai|em gái|
ông|bà|người thân|thời thơ ấu|nhà trẻ|mẫu giáo
""",

    3: """
học tập|giáo dục|trường học|đại học|khóa học|
tốt nghiệp|sinh viên|học sinh|giáo viên|
giảng viên|giảng dạy|bài giảng|bài tập|
thi cử|kỳ thi|điểm số|kiến thức|
tài liệu tham khảo|từ vựng|đào tạo|
bồi dưỡng|chuyên ngành|nghiên cứu sinh
""",

    4: """
công việc|nghề nghiệp|đi làm|nhân viên|
quản lý|giám đốc|sếp|văn phòng|lương|
tiền lương|đãi ngộ|tuyển dụng|
phỏng vấn xin việc|kinh nghiệm làm việc|
tăng ca|nhiệm vụ|sự nghiệp|chức vụ|
đảm nhiệm|phụ trách|thất nghiệp|việc làm
""",

    5: """
kinh doanh|thương mại|thị trường|ngân hàng|
tiền mặt|tài sản|của cải|giá cả|chi phí|
thu nhập|lợi nhuận|đầu tư|kinh tế|sản phẩm|
khách hàng|hợp đồng|thanh toán|tài chính|
doanh nghiệp|xuất khẩu|nhập khẩu|
lãi suất|tiền lãi|phá sản|bán hàng|khuyến mãi
""",

    6: """
ý kiến|quan điểm|cho rằng|nghĩ rằng|
giải thích|thảo luận|trao đổi|biểu đạt|
diễn đạt|đồng ý|phản đối|đề nghị|gợi ý|
trả lời|câu trả lời|câu hỏi|tin tức|
thông tin|nói chuyện|phát biểu|thuyết phục|
tranh luận|phỏng vấn|thông báo|miêu tả|
tóm tắt|kết luận|ngôn ngữ|phát âm
""",

    7: """
cảm xúc|tâm trạng|vui|buồn|tức giận|
giận dữ|sợ hãi|lo lắng|căng thẳng|
thất vọng|tự hào|tính cách|thái độ|
dũng cảm|kiên nhẫn|ngạc nhiên|hạnh phúc|
xấu hổ|hối hận|nước mắt|khen ngợi|
chân thành|thật thà|nghịch ngợm|
thích thú|hứng thú|tâm lý
""",

    8: """
sức khỏe|cơ thể|bệnh viện|bác sĩ|
bệnh nhân|y tá|bệnh|ốm|điều trị|thuốc|
đau|kiểm tra sức khỏe|y tế|y học|
sinh mạng|tử vong|chữa bệnh|triệu chứng|
thể lực|mệt|tiêm|sốt|thở|xe lăn|
bụng|ngực|cân nặng|giảm cân
""",

    9: """
sinh hoạt|nhà cửa|căn nhà|căn phòng|
đồ gia dụng|dịch vụ|khách sạn|
sửa chữa|dọn dẹp|giặt|rửa|chìa khóa|
cửa sổ|thuê nhà|tủ lạnh|thang máy|
đồng hồ báo thức|hệ thống sưởi|
trang trí nội thất|chuyển phát nhanh|
bưu kiện|kiện hàng|lên lầu|xuống lầu
""",

    10: """
thức ăn|đồ ăn|thực phẩm|món ăn|rau|
hoa quả|trái cây|dưa|hải sản|nhà hàng|
thực đơn|hương vị|mua sắm|cửa hàng|
siêu thị|quần áo|giày|tiêu dùng|
đồ uống|trà|đậu phụ|nước khoáng|
nước tinh khiết|giảm giá|hàng hóa tổng hợp
""",

    11: """
du lịch|chuyến đi|đi lại|xe buýt|xe khách|
máy bay|hàng không|sân bay|tàu hỏa|ô tô|
xe điện|tàu điện ngầm|nhà ga|khởi hành|
đến nơi|lái xe|tài xế|giao thông|hành lý|
hộ chiếu|khách du lịch|chuyến bay|
đường dài|đường sắt cao tốc|
hướng dẫn viên du lịch|lùi xe|đổi xe
""",

    12: """
thành phố|địa điểm|địa chỉ|vị trí|
phương hướng|khoảng cách|gần đó|lân cận|
phía đông|phía tây|phía nam|phía bắc|
đường phố|trung tâm thành phố|nông thôn|
khu vực|địa phương|mặt đất|dưới lòng đất|
lối ra|lối vào|đất liền|lục địa
""",

    13: """
thời gian|kế hoạch|lịch trình|đúng giờ|
thời hạn|hạn chót|trì hoãn|gia hạn|
thay đổi|trước đây|tương lai|quá khứ|
giai đoạn|dần dần|tháng sau|
trước thời hạn|kịp thời|kéo dài|rút ngắn
""",

    14: """
thời tiết|thiên nhiên|môi trường|khí hậu|
ẩm ướt|sấm|tuyết|băng|động vật|
thực vật|ô nhiễm|rừng|sông|biển|núi|
nước biển|tài nguyên thiên nhiên|
nhiệt độ|mùa xuân|mùa hè|mùa thu|
mùa đông|tia chớp|phong cảnh
""",

    15: """
công nghệ|máy tính|internet|đăng nhập|
phần mềm|nguồn điện|thiết bị|máy móc|
vận hành|thao tác|dữ liệu|mật khẩu|
sạc pin|bộ sạc|tai nghe|điện tử|
chương trình máy tính|cài đặt
""",

    16: """
văn hóa|truyền thống|nghệ thuật|điện ảnh|
phim hoạt hình|âm nhạc|truyền hình|
báo chí|tạp chí|diễn viên|phóng viên|
tiểu thuyết|câu chuyện|biểu diễn|
bài hát|hội họa|tác phẩm|văn học|
đĩa hát|album|cảnh quay|vai diễn|thần thoại
""",

    17: """
thể thao|thi đấu|tỷ số|bóng đá|bóng rổ|
bơi lội|chạy bộ|huấn luyện|luyện tập|
vô địch|giải trí|trò chơi|sân thể thao|
vận động viên|đại hội thể thao|
cuộc thi thể thao|môn leo núi
""",

    18: """
xã hội|pháp luật|luật sư|thẩm phán|
quy định|quy tắc|an toàn|nguy hiểm|
cảnh sát|tai nạn|chính phủ|quốc gia|
tội phạm|trách nhiệm|chế độ|bảo vệ|
công dân|cộng đồng|chính sách|kỷ luật|
quan chức|ngoại giao|tổng thống|
yêu nước|ngăn cấm|chiến tranh|
chiến đấu|lính|quân đội
""",

    19: """
số lượng|con số|phần trăm|phân số|
mức độ|so sánh|kích thước|chiều dài|
trọng lượng|chiều cao|chất lượng|
xấp xỉ|gấp bội|lượng từ|đơn vị|
milimét|mililit|xentimét|trung bình|
hàm lượng|quy mô|tỷ lệ|đo lường|
thước kẻ|số đo
""",

    20: """
liên từ|phó từ|giới từ|trợ từ|đại từ|
thán từ|từ nối|mặc dù|tuy nhiên|
do đó|vì vậy|nếu không|cho dù|
ngoài ra|thậm chí|căn cứ vào|
liên quan đến|bất kể|có lẽ|
dường như|tóm lại|tổng cộng|
ngược lại|ngay lập tức|lần lượt|
càng sớm càng tốt|không nhất thiết|
rốt cuộc|hầu như
""",
}


# ============================================================
# STOP WORDS CHO MO HINH NOI BO
# ============================================================

VI_STOPWORDS = set(
    """
    va cua cho mot nhung cac la co duoc trong tren voi
    tu den de do nay kia ve khi nhu hay khong da sau
    truoc vao ra bi lam hon rat su viec dieu cach
    nguoi cai loai dang phan hoac theo
    """.split()
)


# ============================================================
# HAM HO TRO
# ============================================================

def clean(value):

    if value is None:
        return ""

    return str(value).strip()


def sha256_file(path):

    h = hashlib.sha256()

    with path.open("rb") as f:

        for block in iter(
            lambda: f.read(1024 * 1024),
            b"",
        ):
            h.update(block)

    return h.hexdigest()


def read_csv(path):

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        fields = list(
            reader.fieldnames or []
        )

        rows = list(reader)

    return fields, rows


def csv_bytes(
    fields,
    rows,
):

    buffer = io.StringIO(
        newline=""
    )

    writer = csv.DictWriter(
        buffer,
        fieldnames=fields,
        extrasaction="ignore",
        lineterminator="\n",
    )

    writer.writeheader()
    writer.writerows(rows)

    return buffer.getvalue().encode(
        "utf-8-sig"
    )


def safe_write_bytes(
    path,
    data,
):

    if path.exists():

        old = path.read_bytes()

        if old == data:

            print(
                f"PASS: file da ton tai "
                f"va noi dung giong het: "
                f"{path.name}"
            )

            return

        raise RuntimeError(
            "Output da ton tai nhung "
            "noi dung khac. "
            "KHONG TU DONG GHI DE:\n"
            + str(path)
        )

    with path.open(
        "xb"
    ) as f:

        f.write(data)

    print(
        f"PASS: da tao {path.name}"
    )


def norm_vi(value):

    text = clean(
        value
    ).lower()

    text = text.replace(
        "đ",
        "d",
    )

    text = unicodedata.normalize(
        "NFD",
        text,
    )

    text = "".join(
        char
        for char in text
        if unicodedata.category(
            char
        ) != "Mn"
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def first_meaning(value):

    text = clean(value)

    # Bo metadata LT:
    text = text.split(
        "/ LT:"
    )[0]

    return text.strip()


def parse_int(
    value,
    default=999999,
):

    try:
        return int(
            clean(value)
        )

    except Exception:
        return default


# ============================================================
# CHUAN HOA RULE
# ============================================================

HANZI_KEYWORDS = {}

for lesson_no, text in (
    HANZI_RULES.items()
):

    HANZI_KEYWORDS[
        lesson_no
    ] = [
        item.strip()
        for item in text.split()
        if item.strip()
    ]


VI_KEYWORDS = {}

for lesson_no, text in (
    VI_RULES.items()
):

    cleaned = (
        text
        .replace("\n", "")
    )

    VI_KEYWORDS[
        lesson_no
    ] = [
        norm_vi(item)
        for item in cleaned.split("|")
        if norm_vi(item)
    ]


# ============================================================
# FEATURE CHO MO HINH NOI BO
# Khong dung API, khong download model.
# ============================================================

def extract_features(row):

    result = Counter()

    hanzi = clean(
        row.get("ChuHan")
    )

    chars = [
        char
        for char in hanzi
        if (
            "\u3400"
            <= char
            <= "\u9fff"
        )
    ]

    # Don ky tu.
    for char in chars:

        result[
            "H1:" + char
        ] += 1.0

    # Cap ky tu Han.
    for index in range(
        len(chars) - 1
    ):

        pair = (
            chars[index]
            + chars[index + 1]
        )

        result[
            "H2:" + pair
        ] += 2.0

    meaning = norm_vi(
        first_meaning(
            row.get(
                "NghiaTiengViet"
            )
        )
    )

    words = [
        word
        for word in meaning.split()
        if (
            len(word) >= 3
            and word not in VI_STOPWORDS
        )
    ]

    for word in words:

        result[
            "V:" + word
        ] += 1.0

    for index in range(
        len(words) - 1
    ):

        pair = (
            words[index]
            + "_"
            + words[index + 1]
        )

        result[
            "VB:" + pair
        ] += 1.5

    pos = clean(
        row.get("TuLoai")
    )

    for marker in (
        "名",
        "动",
        "形",
        "副",
        "连",
        "介",
        "助",
        "量",
        "数",
        "代",
        "叹",
    ):

        if marker in pos:

            result[
                "P:" + marker
            ] += 0.5

    return result


def build_vectors(rows):

    raw_features = [
        extract_features(row)
        for row in rows
    ]

    document_frequency = Counter()

    for feature_map in (
        raw_features
    ):

        for feature in feature_map:

            document_frequency[
                feature
            ] += 1

    total = len(rows)

    idf = {}

    for feature, count in (
        document_frequency.items()
    ):

        idf[
            feature
        ] = (
            math.log(
                (total + 1)
                / (count + 1)
            )
            + 1.0
        )

    vectors = []

    for feature_map in (
        raw_features
    ):

        vector = {}

        for feature, value in (
            feature_map.items()
        ):

            vector[
                feature
            ] = (
                value
                * idf[feature]
            )

        norm = math.sqrt(
            sum(
                value * value
                for value
                in vector.values()
            )
        )

        if norm <= 0:
            norm = 1.0

        vector = {
            feature:
                value / norm

            for feature, value
            in vector.items()
        }

        vectors.append(
            vector
        )

    return vectors


def build_centroids(
    rows,
    vectors,
):

    sums = {
        n: Counter()
        for n in range(1, 21)
    }

    counts = Counter()

    for index, row in enumerate(
        rows
    ):

        # 434 tu Step21 da duoc danh dau
        # CHU_DE_RO / CanReview=KHONG.
        if clean(
            row.get("CanReview")
        ) != "KHONG":

            continue

        lesson_no = parse_int(
            row.get(
                "SoThuTuBaiCu"
            ),
            0,
        )

        if lesson_no not in range(
            1,
            21,
        ):
            continue

        counts[
            lesson_no
        ] += 1

        for feature, value in (
            vectors[index].items()
        ):

            sums[
                lesson_no
            ][
                feature
            ] += value

    # Phai co seed o ca 20 bai.
    for lesson_no in range(
        1,
        21,
    ):

        if counts[
            lesson_no
        ] <= 0:

            raise RuntimeError(
                "Khong co seed Step21 "
                f"cho bai {lesson_no}."
            )

    centroids = {}

    for lesson_no in range(
        1,
        21,
    ):

        vector = {}

        count = counts[
            lesson_no
        ]

        for feature, value in (
            sums[
                lesson_no
            ].items()
        ):

            vector[
                feature
            ] = (
                value / count
            )

        norm = math.sqrt(
            sum(
                value * value
                for value
                in vector.values()
            )
        )

        if norm <= 0:
            norm = 1.0

        centroids[
            lesson_no
        ] = {
            feature:
                value / norm

            for feature, value
            in vector.items()
        }

    return (
        centroids,
        counts,
    )


def cosine(
    vector,
    centroid,
):

    return sum(
        value
        * centroid.get(
            feature,
            0.0,
        )

        for feature, value
        in vector.items()
    )


# ============================================================
# RULE SCORE
# ============================================================

def rule_score(
    row,
    lesson_no,
):

    hanzi = clean(
        row.get("ChuHan")
    )

    meaning = (
        " "
        + norm_vi(
            first_meaning(
                row.get(
                    "NghiaTiengViet"
                )
            )
        )
        + " "
    )

    score = 0.0

    evidence = []

    # ----------------------
    # Hanzi
    # ----------------------

    for keyword in (
        HANZI_KEYWORDS[
            lesson_no
        ]
    ):

        if hanzi == keyword:

            score += 20.0

            evidence.append(
                "HANZI_EXACT:"
                + keyword
            )

        elif (
            len(keyword) >= 2
            and keyword in hanzi
        ):

            score += 12.0

            evidence.append(
                "HANZI_PART:"
                + keyword
            )

    # ----------------------
    # Nghia Viet
    # ----------------------

    for keyword in (
        VI_KEYWORDS[
            lesson_no
        ]
    ):

        wrapped = (
            " "
            + keyword
            + " "
        )

        if wrapped in meaning:

            score += 8.0

            evidence.append(
                "NGHIA:"
                + keyword
            )

    # ----------------------
    # Tu loai
    # ----------------------

    pos = clean(
        row.get("TuLoai")
    )

    if lesson_no == 19:

        if (
            "量" in pos
            or "数" in pos
        ):

            score += 4.0

            evidence.append(
                "POS:SO_LUONG"
            )

    if lesson_no == 20:

        if any(
            marker in pos
            for marker in (
                "副",
                "连",
                "介",
                "助",
                "代",
                "叹",
            )
        ):

            score += 3.0

            evidence.append(
                "POS:TU_CHUC_NANG"
            )

    return (
        score,
        evidence,
    )


# ============================================================
# PHAN BAI 21B
# ============================================================

def classify_row(
    row,
    vector,
    centroids,
):

    hanzi = clean(
        row.get("ChuHan")
    )

    old_21 = parse_int(
        row.get(
            "SoThuTuBaiCu"
        ),
        0,
    )

    old_21a = parse_int(
        row.get(
            "SoThuTuBai"
        ),
        0,
    )

    # ========================================================
    # 1. MANUAL OVERRIDE
    # ========================================================

    if hanzi in MANUAL_OVERRIDES:

        lesson_no = (
            MANUAL_OVERRIDES[
                hanzi
            ]
        )

        return {
            "lesson": lesson_no,
            "rule_score": 100.0,
            "similarity": 1.0,
            "total_score": 100.0,
            "margin": 100.0,
            "confidence": "CAO",
            "reason": "MANUAL_OVERRIDE",
            "evidence": (
                "MANUAL:"
                + hanzi
                + "->"
                + str(lesson_no)
            ),
            "review": "KHONG",
        }

    # ========================================================
    # 2. RULE + CENTROID
    # ========================================================

    records = []

    for lesson_no in range(
        1,
        21,
    ):

        r_score, evidence = (
            rule_score(
                row,
                lesson_no,
            )
        )

        similarity = cosine(
            vector,
            centroids[
                lesson_no
            ],
        )

        total_score = (
            r_score
            + similarity * 12.0
        )

        # Step21 CHU_DE_RO la seed rat nhe.
        if (
            clean(
                row.get(
                    "CanReview"
                )
            )
            == "KHONG"
            and lesson_no == old_21
        ):

            total_score += 3.0

        # Step21A chi la prior rat nhe,
        # khong duoc phep dieu khien ket qua.
        if lesson_no == old_21a:

            total_score += 0.5

        records.append({
            "lesson":
                lesson_no,

            "rule_score":
                r_score,

            "similarity":
                similarity,

            "total":
                total_score,

            "evidence":
                evidence,
        })

    records.sort(
        key=lambda item: (
            -item["total"],
            item["lesson"],
        )
    )

    best = records[0]
    second = records[1]

    margin = (
        best["total"]
        - second["total"]
    )

    # ========================================================
    # 3. DO TIN CAY
    # ========================================================

    reason = "MODEL_NGU_NGHIA"

    review = "CO"

    confidence = "THAP"

    # Rule Hanzi/nghia rat ro.
    if (
        best["rule_score"] >= 12
        and margin >= 2
    ):

        confidence = "CAO"
        review = "KHONG"
        reason = "RULE_NGU_NGHIA_MANH"

    # Rule co nghia ro va cach biet kha tot.
    elif (
        best["rule_score"] >= 8
        and margin >= 4
    ):

        confidence = "TRUNG_BINH"
        review = "KHONG"
        reason = "RULE_NGU_NGHIA"

    # Seed Step21 van o dung bai sau khi doi chieu.
    elif (
        clean(
            row.get(
                "CanReview"
            )
        ) == "KHONG"
        and best["lesson"] == old_21
        and margin >= 1.5
    ):

        confidence = "TRUNG_BINH"
        review = "KHONG"
        reason = "GIU_SEED_STEP21"

    # Model noi bo tuong doi ro.
    elif (
        best["similarity"] >= 0.10
        and margin >= 1.5
    ):

        confidence = "TRUNG_BINH"
        review = "KHONG"
        reason = "MODEL_NGU_NGHIA_RO"

    evidence = list(
        best["evidence"]
    )

    if not evidence:

        evidence.append(
            "CENTROID="
            + format(
                best["similarity"],
                ".6f",
            )
        )

    return {
        "lesson":
            best["lesson"],

        "rule_score":
            best["rule_score"],

        "similarity":
            best["similarity"],

        "total_score":
            best["total"],

        "margin":
            margin,

        "confidence":
            confidence,

        "reason":
            reason,

        "evidence":
            " | ".join(
                evidence
            ),

        "review":
            review,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 86)

    print(
        "BUOC 21B - TINH CHINH "
        "1000 TU HSK4 THEO NGU NGHIA"
    )

    print(
        "KHONG GHI SQL - "
        "KHONG TAO AUDIO"
    )

    print("=" * 86)

    # ========================================================
    # 1. SNAPSHOT
    # ========================================================

    print(
        "\n[1] KIEM TRA SNAPSHOT"
    )

    if not SOURCE.is_file():

        raise FileNotFoundError(
            SOURCE
        )

    if not LESSON_SOURCE.is_file():

        raise FileNotFoundError(
            LESSON_SOURCE
        )

    source_hash = sha256_file(
        SOURCE
    )

    lesson_hash = sha256_file(
        LESSON_SOURCE
    )

    print(
        "21A SHA256:",
        source_hash,
    )

    print(
        "LESSONS SHA256:",
        lesson_hash,
    )

    if (
        source_hash
        != EXPECTED_SOURCE_SHA256
    ):

        raise RuntimeError(
            "FAIL: snapshot Step21A "
            "khong khop."
        )

    if (
        lesson_hash
        != EXPECTED_LESSON_SHA256
    ):

        raise RuntimeError(
            "FAIL: snapshot lessons Step21 "
            "khong khop."
        )

    print(
        "PASS: 2 snapshot hop le."
    )

    # ========================================================
    # 2. DOC DATA
    # ========================================================

    print(
        "\n[2] DOC 1000 TU"
    )

    fields, rows = read_csv(
        SOURCE
    )

    lesson_fields, lesson_rows = (
        read_csv(
            LESSON_SOURCE
        )
    )

    if len(
        rows
    ) != EXPECTED_ROWS:

        raise RuntimeError(
            "FAIL: can dung 1000 tu, "
            f"hien co {len(rows)}."
        )

    if len(
        lesson_rows
    ) != EXPECTED_LESSONS:

        raise RuntimeError(
            "FAIL: can dung 20 bai."
        )

    ids = [
        clean(
            row.get(
                "MaMucNoiBo"
            )
        )
        for row in rows
    ]

    if len(
        set(ids)
    ) != EXPECTED_ROWS:

        raise RuntimeError(
            "FAIL: MaMucNoiBo "
            "khong duy nhat."
        )

    print(
        "PASS: 1000 tu / "
        "1000 MaMucNoiBo duy nhat."
    )

    # ========================================================
    # 3. KIEM TRA 434 SEED STEP21
    # ========================================================

    print(
        "\n[3] KIEM TRA SEED STEP21"
    )

    seed_rows = [
        row
        for row in rows
        if clean(
            row.get(
                "CanReview"
            )
        ) == "KHONG"
    ]

    print(
        "Seed CHU_DE_RO:",
        len(seed_rows),
    )

    if len(
        seed_rows
    ) != 434:

        raise RuntimeError(
            "FAIL: Step21 phai co "
            "434 seed CHU_DE_RO."
        )

    seed_counts = Counter(
        parse_int(
            row.get(
                "SoThuTuBaiCu"
            ),
            0,
        )
        for row in seed_rows
    )

    missing_seed_lessons = [
        n
        for n in range(1, 21)
        if seed_counts[n] == 0
    ]

    if missing_seed_lessons:

        raise RuntimeError(
            "FAIL: thieu seed o cac bai: "
            + str(
                missing_seed_lessons
            )
        )

    print(
        "PASS: 434 seed, "
        "du ca 20 bai."
    )

    # ========================================================
    # 4. TAO VECTOR + CENTROID
    # ========================================================

    print(
        "\n[4] TAO MO HINH NGU NGHIA NOI BO"
    )

    vectors = build_vectors(
        rows
    )

    centroids, centroid_seed_counts = (
        build_centroids(
            rows,
            vectors,
        )
    )

    print(
        "PASS: da tao centroid "
        "cho 20 bai."
    )

    # ========================================================
    # 5. CLASSIFY
    # ========================================================

    print(
        "\n[5] PHAN LAI 1000 TU"
    )

    results = []

    for index, row in enumerate(
        rows
    ):

        classified = classify_row(
            row,
            vectors[index],
            centroids,
        )

        new_row = dict(row)

        old_21a = parse_int(
            row.get(
                "SoThuTuBai"
            ),
            0,
        )

        lesson_no = int(
            classified[
                "lesson"
            ]
        )

        new_row[
            "SoThuTuBai21A"
        ] = old_21a

        new_row[
            "SoThuTuBai21B"
        ] = lesson_no

        new_row[
            "DiemQuyTac21B"
        ] = format(
            classified[
                "rule_score"
            ],
            ".3f",
        )

        new_row[
            "DoTuongDong21B"
        ] = format(
            classified[
                "similarity"
            ],
            ".6f",
        )

        new_row[
            "DiemTong21B"
        ] = format(
            classified[
                "total_score"
            ],
            ".6f",
        )

        new_row[
            "DoChenh21B"
        ] = format(
            classified[
                "margin"
            ],
            ".6f",
        )

        new_row[
            "DoTinCay21B"
        ] = classified[
            "confidence"
        ]

        new_row[
            "LyDoGan21B"
        ] = classified[
            "reason"
        ]

        new_row[
            "BangChung21B"
        ] = classified[
            "evidence"
        ]

        new_row[
            "CanReview21B"
        ] = classified[
            "review"
        ]

        # Cap nhat cac cot bai hoc hien hanh.
        new_row[
            "SoThuTuBai"
        ] = lesson_no

        new_row[
            "MaBaiHocTam"
        ] = (
            f"H4-L{lesson_no:02d}"
        )

        new_row[
            "TieuDeBaiHoc"
        ] = (
            LESSON_TITLES[
                lesson_no
            ]
        )

        results.append(
            new_row
        )

    print(
        "PASS: da phan "
        "1000/1000 tu."
    )

    # ========================================================
    # 6. GAN THU TU TRONG TUNG BAI
    # ========================================================

    print(
        "\n[6] GAN THU TU TRONG BAI"
    )

    grouped = defaultdict(
        list
    )

    for row in results:

        grouped[
            int(
                row[
                    "SoThuTuBai"
                ]
            )
        ].append(row)

    for lesson_no in range(
        1,
        21,
    ):

        group = grouped[
            lesson_no
        ]

        group.sort(
            key=lambda row: (
                parse_int(
                    row.get(
                        "SoThuTuNguon"
                    ),
                    999999,
                ),
                clean(
                    row.get(
                        "MaMucNoiBo"
                    )
                ),
            )
        )

        for order, row in enumerate(
            group,
            start=1,
        ):

            row[
                "ThuTuTrongBai"
            ] = order

    # Sap xep output theo bai.
    results.sort(
        key=lambda row: (
            int(
                row[
                    "SoThuTuBai"
                ]
            ),
            int(
                row[
                    "ThuTuTrongBai"
                ]
            ),
        )
    )

    # ========================================================
    # 7. VALIDATE
    # ========================================================

    print(
        "\n[7] VALIDATE"
    )

    if len(
        results
    ) != EXPECTED_ROWS:

        raise RuntimeError(
            "FAIL: ket qua khong du "
            "1000 tu."
        )

    result_ids = [
        clean(
            row[
                "MaMucNoiBo"
            ]
        )
        for row in results
    ]

    if len(
        set(result_ids)
    ) != EXPECTED_ROWS:

        raise RuntimeError(
            "FAIL: trung MaMucNoiBo."
        )

    if set(
        result_ids
    ) != set(ids):

        raise RuntimeError(
            "FAIL: bi mat/them tu."
        )

    lesson_set = {
        int(
            row[
                "SoThuTuBai"
            ]
        )
        for row in results
    }

    if lesson_set != set(
        range(1, 21)
    ):

        raise RuntimeError(
            "FAIL: khong du 20 bai."
        )

    print(
        "PASS: 1000/1000, "
        "khong trung, khong mat."
    )

    print(
        "PASS: 20/20 bai co tu."
    )

    # ========================================================
    # 8. SPOT CHECK
    # ========================================================

    print(
        "\n[8] SPOT CHECK CAC TU "
        "DA BI XEP SAI O 21/21A"
    )

    by_hanzi = defaultdict(
        list
    )

    for row in results:

        by_hanzi[
            clean(
                row["ChuHan"]
            )
        ].append(row)

    for hanzi, expected_lesson in (
        EXPECTED_SPOT_CHECKS.items()
    ):

        matches = by_hanzi.get(
            hanzi,
            [],
        )

        if not matches:

            raise RuntimeError(
                f"FAIL: khong tim thay "
                f"spot check {hanzi}."
            )

        for row in matches:

            actual = int(
                row[
                    "SoThuTuBai"
                ]
            )

            if actual != expected_lesson:

                raise RuntimeError(
                    "FAIL spot check: "
                    f"{hanzi} -> bai {actual}, "
                    f"can bai {expected_lesson}."
                )

        print(
            f"PASS: {hanzi} "
            f"-> Bai {expected_lesson:02d}"
        )

    # ========================================================
    # 9. THONG KE
    # ========================================================

    print(
        "\n[9] THONG KE 20 BAI"
    )

    counts = Counter(
        int(
            row[
                "SoThuTuBai"
            ]
        )
        for row in results
    )

    review_counts = Counter(
        int(
            row[
                "SoThuTuBai"
            ]
        )
        for row in results
        if clean(
            row[
                "CanReview21B"
            ]
        ) == "CO"
    )

    confidence_counts = Counter(
        clean(
            row[
                "DoTinCay21B"
            ]
        )
        for row in results
    )

    reason_counts = Counter(
        clean(
            row[
                "LyDoGan21B"
            ]
        )
        for row in results
    )

    for lesson_no in range(
        1,
        21,
    ):

        print(
            f"Bai {lesson_no:02d} | "
            f"{counts[lesson_no]:3d} tu | "
            f"review="
            f"{review_counts[lesson_no]:3d} | "
            f"{LESSON_TITLES[lesson_no]}"
        )

    total_review = sum(
        review_counts.values()
    )

    print(
        "\nTong can review:",
        total_review,
    )

    print(
        "Do tin cay:"
    )

    for key, value in sorted(
        confidence_counts.items()
    ):

        print(
            f"  {key}: {value}"
        )

    print(
        "Cach gan:"
    )

    for key, value in sorted(
        reason_counts.items()
    ):

        print(
            f"  {key}: {value}"
        )

    # ========================================================
    # 10. CHANGES
    # ========================================================

    changes = [
        row
        for row in results
        if int(
            row[
                "SoThuTuBai21A"
            ]
        )
        != int(
            row[
                "SoThuTuBai21B"
            ]
        )
    ]

    print(
        "\nSo tu thay doi so voi 21A:",
        len(changes),
    )

    # ========================================================
    # 11. CAP NHAT FILE LESSON COUNTS
    # ========================================================

    lesson_result = []

    lesson_map = {
        int(
            row[
                "SoThuTuBai"
            ]
        ): dict(row)

        for row in lesson_rows
    }

    for lesson_no in range(
        1,
        21,
    ):

        if lesson_no not in lesson_map:

            raise RuntimeError(
                "FAIL: lessons_hsk4_draft_20 "
                f"thieu bai {lesson_no}."
            )

        row = lesson_map[
            lesson_no
        ]

        row[
            "SoTuVung21B"
        ] = counts[
            lesson_no
        ]

        row[
            "SoTuCanReview21B"
        ] = review_counts[
            lesson_no
        ]

        lesson_result.append(
            row
        )

    # ========================================================
    # 12. XUAT FILE
    # ========================================================

    print(
        "\n[10] XUAT FILE"
    )

    extra_fields = [
        "SoThuTuBai21A",
        "SoThuTuBai21B",
        "DiemQuyTac21B",
        "DoTuongDong21B",
        "DiemTong21B",
        "DoChenh21B",
        "DoTinCay21B",
        "LyDoGan21B",
        "BangChung21B",
        "CanReview21B",
    ]

    output_fields = list(
        fields
    )

    for field in extra_fields:

        if field not in output_fields:

            output_fields.append(
                field
            )

    review_rows = [
        row
        for row in results
        if clean(
            row[
                "CanReview21B"
            ]
        ) == "CO"
    ]

    output_data = csv_bytes(
        output_fields,
        results,
    )

    review_data = csv_bytes(
        output_fields,
        review_rows,
    )

    changes_data = csv_bytes(
        output_fields,
        changes,
    )

    lesson_output_fields = list(
        lesson_fields
    )

    for field in (
        "SoTuVung21B",
        "SoTuCanReview21B",
    ):

        if field not in (
            lesson_output_fields
        ):

            lesson_output_fields.append(
                field
            )

    lesson_data = csv_bytes(
        lesson_output_fields,
        lesson_result,
    )

    safe_write_bytes(
        OUTPUT,
        output_data,
    )

    safe_write_bytes(
        REVIEW_OUTPUT,
        review_data,
    )

    safe_write_bytes(
        CHANGES_OUTPUT,
        changes_data,
    )

    safe_write_bytes(
        LESSON_OUTPUT,
        lesson_data,
    )

    # ========================================================
    # 13. SUMMARY
    # ========================================================

    summary = {
        "status":
            "PASS",

        "buoc":
            "21B",

        "source":
            str(SOURCE),

        "source_sha256":
            source_hash,

        "lesson_source_sha256":
            lesson_hash,

        "tong_tu":
            len(results),

        "so_bai":
            20,

        "seed_step21":
            len(seed_rows),

        "manual_overrides":
            sum(
                1
                for row in results
                if clean(
                    row[
                        "LyDoGan21B"
                    ]
                )
                == "MANUAL_OVERRIDE"
            ),

        "thay_doi_so_voi_21A":
            len(changes),

        "tong_can_review":
            total_review,

        "do_tin_cay":
            dict(
                confidence_counts
            ),

        "cach_gan":
            dict(
                reason_counts
            ),

        "phan_bo": {
            str(n): {
                "so_tu":
                    counts[n],

                "can_review":
                    review_counts[n],
            }

            for n in range(
                1,
                21,
            )
        },

        "outputs": {
            "vocabulary":
                str(OUTPUT),

            "vocabulary_sha256":
                sha256_file(
                    OUTPUT
                ),

            "review":
                str(
                    REVIEW_OUTPUT
                ),

            "review_sha256":
                sha256_file(
                    REVIEW_OUTPUT
                ),

            "changes":
                str(
                    CHANGES_OUTPUT
                ),

            "changes_sha256":
                sha256_file(
                    CHANGES_OUTPUT
                ),

            "lessons":
                str(
                    LESSON_OUTPUT
                ),

            "lessons_sha256":
                sha256_file(
                    LESSON_OUTPUT
                ),
        },

        "ghi_sql":
            False,

        "tao_audio":
            False,
    }

    summary_bytes = (
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode(
        "utf-8"
    )

    safe_write_bytes(
        SUMMARY_OUTPUT,
        summary_bytes,
    )

    # ========================================================
    # KET QUA
    # ========================================================

    print(
        "\n" + "=" * 86
    )

    print(
        "PASS: BUOC 21B HOAN THANH"
    )

    print("=" * 86)

    print(
        "Tong tu:",
        len(results),
    )

    print(
        "So bai:",
        20,
    )

    print(
        "Seed Step21:",
        len(seed_rows),
    )

    print(
        "Thay doi so voi 21A:",
        len(changes),
    )

    print(
        "Tong can review:",
        total_review,
    )

    print(
        "\nVOCAB:"
    )

    print(
        OUTPUT
    )

    print(
        "SHA256:"
    )

    print(
        sha256_file(
            OUTPUT
        )
    )

    print(
        "\nREVIEW:"
    )

    print(
        REVIEW_OUTPUT
    )

    print(
        "\nCHANGES:"
    )

    print(
        CHANGES_OUTPUT
    )

    print(
        "\nLESSONS:"
    )

    print(
        LESSON_OUTPUT
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

    print("=" * 86)


if __name__ == "__main__":

    try:

        main()

    except Exception as exc:

        print(
            "\nFAIL:",
            exc,
        )

        raise SystemExit(1)