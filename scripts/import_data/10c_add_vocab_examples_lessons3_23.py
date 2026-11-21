from pathlib import Path
import argparse
import csv
import sys


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

SOURCE_FILE = (
    ROOT_DIR
    / "data_sources"
    / "hsk1_tuvung_501.csv"
)

OUTPUT_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "hsk1_vocab_examples_3_23.csv"
)

COURSE_CODE = "HSK1-CORE"

FIRST_LESSON = 3
LAST_LESSON = 23

EXPECTED_TOTAL_HSK1 = 501
EXPECTED_TARGET = 459


EXPECTED_COUNTS = {
    3: 23,
    4: 26,
    5: 20,
    6: 24,
    7: 28,
    8: 25,
    9: 22,
    10: 24,
    11: 23,
    12: 22,
    13: 30,
    14: 22,
    15: 11,
    16: 12,
    17: 25,
    18: 22,
    19: 23,
    20: 23,
    21: 20,
    22: 18,
    23: 16,
}


# ============================================================
# HELPER
# ============================================================

def clean(value):

    if value is None:
        return ""

    value = str(value).strip()

    if value.upper() == "NULL":
        return ""

    return value


def first_meaning(value):

    value = clean(value)

    for separator in [
        ";",
        "/",
    ]:

        if separator in value:
            value = value.split(
                separator,
                1,
            )[0].strip()

    return value


# ============================================================
# VÍ DỤ ĐẶC BIỆT
#
# Những từ không nên sinh bằng công thức chung
# được đặt ở đây.
# ============================================================

SPECIAL = {

    # --------------------------------------------------------
    # BÀI 3
    # --------------------------------------------------------

    (3, "家"):
        (
            "这是我的家。",
            "Đây là nhà của tôi.",
        ),

    (3, "家里"):
        (
            "我妈妈在家里。",
            "Mẹ tôi ở nhà.",
        ),

    (3, "家人"):
        (
            "我的家人都很好。",
            "Người nhà của tôi đều khỏe.",
        ),

    (3, "孩子"):
        (
            "那个孩子很高兴。",
            "Đứa trẻ kia rất vui.",
        ),

    (3, "老人"):
        (
            "那个老人是我爷爷。",
            "Người cao tuổi kia là ông nội tôi.",
        ),

    (3, "们（朋友们）"):
        (
            "朋友们，你们好！",
            "Các bạn, xin chào!",
        ),

    (3, "男孩儿"):
        (
            "那个男孩儿是我弟弟。",
            "Cậu bé kia là em trai tôi.",
        ),

    (3, "女孩儿"):
        (
            "那个女孩儿是我妹妹。",
            "Cô bé kia là em gái tôi.",
        ),

    (3, "小孩儿"):
        (
            "那个小孩儿很高兴。",
            "Đứa trẻ kia rất vui.",
        ),

    (3, "小朋友"):
        (
            "小朋友们，你们好！",
            "Các em nhỏ, xin chào!",
        ),


    # --------------------------------------------------------
    # BÀI 4
    # --------------------------------------------------------

    (4, "八"):
        ("我今年八岁。", "Năm nay tôi tám tuổi."),

    (4, "百"):
        ("这里有一百个人。", "Ở đây có một trăm người."),

    (4, "半"):
        ("我喝半杯水。", "Tôi uống nửa cốc nước."),

    (4, "杯"):
        ("我喝一杯水。", "Tôi uống một cốc nước."),

    (4, "本"):
        ("我有两本书。", "Tôi có hai quyển sách."),

    (4, "次"):
        ("我去过两次。", "Tôi đã đi hai lần."),

    (4, "第（第二）"):
        ("这是第二课。", "Đây là bài thứ hai."),

    (4, "多"):
        ("这里有很多人。", "Ở đây có rất nhiều người."),

    (4, "多少"):
        ("你有多少本书？", "Bạn có bao nhiêu quyển sách?"),

    (4, "二"):
        ("二加二等于四。", "Hai cộng hai bằng bốn."),

    (4, "个"):
        ("我有一个朋友。", "Tôi có một người bạn."),

    (4, "几"):
        ("你今年几岁？", "Năm nay bạn bao nhiêu tuổi?"),

    (4, "九"):
        ("他九岁。", "Cậu ấy chín tuổi."),

    (4, "块"):
        ("这个十块钱。", "Cái này mười tệ."),

    (4, "两"):
        ("我有两个朋友。", "Tôi có hai người bạn."),

    (4, "零"):
        ("现在八点零五分。", "Bây giờ là tám giờ năm phút."),

    (4, "六"):
        ("我弟弟六岁。", "Em trai tôi sáu tuổi."),

    (4, "七"):
        ("今天星期七。", "Hôm nay là ngày thứ bảy."),

    (4, "三"):
        ("我有三本书。", "Tôi có ba quyển sách."),

    (4, "少"):
        ("这里人很少。", "Ở đây có rất ít người."),

    (4, "十"):
        ("我有十块钱。", "Tôi có mười tệ."),

    (4, "四"):
        ("我有四本书。", "Tôi có bốn quyển sách."),

    (4, "岁"):
        ("我今年二十岁。", "Năm nay tôi hai mươi tuổi."),

    (4, "五"):
        ("我们有五个人。", "Chúng tôi có năm người."),

    (4, "一"):
        ("我有一个姐姐。", "Tôi có một chị gái."),

    (4, "一半"):
        ("我吃了一半。", "Tôi đã ăn một nửa."),


    # --------------------------------------------------------
    # BÀI 5
    # --------------------------------------------------------

    (5, "半年"):
        ("我学习汉语半年了。", "Tôi học tiếng Trung được nửa năm rồi."),

    (5, "号"):
        ("今天是十月一号。", "Hôm nay là ngày 1 tháng 10."),

    (5, "后天"):
        ("后天我去学校。", "Ngày mốt tôi đi học."),

    (5, "今年"):
        ("我今年二十岁。", "Năm nay tôi hai mươi tuổi."),

    (5, "今天"):
        ("今天我上课。", "Hôm nay tôi đi học."),

    (5, "明年"):
        ("明年我去中国。", "Năm sau tôi đi Trung Quốc."),

    (5, "明天"):
        ("明天见！", "Hẹn gặp ngày mai!"),

    (5, "年"):
        ("一年有十二个月。", "Một năm có mười hai tháng."),

    (5, "前天"):
        ("前天我在家。", "Hôm kia tôi ở nhà."),

    (5, "去年"):
        ("去年我在北京。", "Năm ngoái tôi ở Bắc Kinh."),

    (5, "日"):
        ("今天是十月一日。", "Hôm nay là ngày 1 tháng 10."),

    (5, "日期"):
        ("请写日期。", "Hãy viết ngày tháng."),

    (5, "生日"):
        ("今天是我的生日。", "Hôm nay là sinh nhật của tôi."),

    (5, "天"):
        ("我学习了三天。", "Tôi đã học ba ngày."),

    (5, "新年"):
        ("新年快乐！", "Chúc mừng năm mới!"),

    (5, "星期"):
        ("今天星期几？", "Hôm nay là thứ mấy?"),

    (5, "星期日"):
        ("星期日我休息。", "Chủ nhật tôi nghỉ."),

    (5, "星期天"):
        ("星期天我在家。", "Chủ nhật tôi ở nhà."),

    (5, "月"):
        ("一年有十二个月。", "Một năm có mười hai tháng."),

    (5, "昨天"):
        ("昨天我很忙。", "Hôm qua tôi rất bận."),


    # --------------------------------------------------------
    # BÀI 6
    # --------------------------------------------------------

    (6, "白天"):
        ("白天我上班。", "Ban ngày tôi đi làm."),

    (6, "半天"):
        ("我学习了半天。", "Tôi học nửa ngày."),

    (6, "常"):
        ("我常去图书馆。", "Tôi thường đi thư viện."),

    (6, "常常"):
        ("我常常学习汉语。", "Tôi thường xuyên học tiếng Trung."),

    (6, "点"):
        ("现在八点。", "Bây giờ là tám giờ."),

    (6, "分"):
        ("现在八点十分。", "Bây giờ là tám giờ mười phút."),

    (6, "马上"):
        ("我马上来。", "Tôi đến ngay."),

    (6, "上次"):
        ("上次我们一起吃饭。", "Lần trước chúng tôi ăn cơm cùng nhau."),

    (6, "上午"):
        ("上午我上课。", "Buổi sáng tôi đi học."),

    (6, "时候"):
        ("你什么时候来？", "Khi nào bạn đến?"),

    (6, "时间"):
        ("我没有时间。", "Tôi không có thời gian."),

    (6, "晚"):
        ("今天我来晚了。", "Hôm nay tôi đến muộn."),

    (6, "晚上"):
        ("晚上我看电影。", "Buổi tối tôi xem phim."),

    (6, "下次"):
        ("下次见！", "Hẹn gặp lần sau!"),

    (6, "下午"):
        ("下午我学习汉语。", "Buổi chiều tôi học tiếng Trung."),

    (6, "先"):
        ("我先吃饭。", "Tôi ăn cơm trước."),

    (6, "现在"):
        ("我现在在学校。", "Bây giờ tôi đang ở trường."),

    (6, "小时"):
        ("我学习两个小时。", "Tôi học hai tiếng."),

    (6, "一会儿"):
        ("请等一会儿。", "Vui lòng đợi một lát."),

    (6, "有时候"):
        ("我有时候看电影。", "Đôi khi tôi xem phim."),

    (6, "早"):
        ("今天我来得很早。", "Hôm nay tôi đến rất sớm."),

    (6, "早上"):
        ("早上我吃早饭。", "Buổi sáng tôi ăn sáng."),

    (6, "中午"):
        ("中午我吃午饭。", "Buổi trưa tôi ăn trưa."),

    (6, "最后"):
        ("最后我们回家。", "Cuối cùng chúng tôi về nhà."),


    # --------------------------------------------------------
    # BÀI 7
    # --------------------------------------------------------

    (7, "班"):
        ("我在一班。", "Tôi học lớp một."),

    (7, "放假"):
        ("明天我们放假。", "Ngày mai chúng tôi được nghỉ."),

    (7, "放学"):
        ("下午五点放学。", "Năm giờ chiều tan học."),

    (7, "教"):
        ("老师教我们汉语。", "Giáo viên dạy chúng tôi tiếng Trung."),

    (7, "考"):
        ("明天我要考汉语。", "Ngày mai tôi phải thi tiếng Trung."),

    (7, "考试"):
        ("今天有汉语考试。", "Hôm nay có bài thi tiếng Trung."),

    (7, "课"):
        ("这是汉语课。", "Đây là tiết tiếng Trung."),

    (7, "请假"):
        ("我今天请假。", "Hôm nay tôi xin nghỉ."),

    (7, "认真"):
        ("他学习很认真。", "Anh ấy học rất nghiêm túc."),

    (7, "上课"):
        ("我们上午上课。", "Chúng tôi học vào buổi sáng."),

    (7, "上学"):
        ("我每天上学。", "Tôi đi học mỗi ngày."),

    (7, "下课"):
        ("现在下课。", "Bây giờ tan học."),

    (7, "学"):
        ("我学汉语。", "Tôi học tiếng Trung."),

    (7, "学习"):
        ("我学习汉语。", "Tôi học tiếng Trung."),

    (7, "知识"):
        ("学习可以得到知识。", "Học tập có thể giúp có được kiến thức."),


    # --------------------------------------------------------
    # BÀI 8
    # --------------------------------------------------------

    (8, "本子"):
        ("这是我的本子。", "Đây là quyển vở của tôi."),

    (8, "打开"):
        ("请打开课本。", "Hãy mở sách giáo khoa."),

    (8, "读"):
        ("请读这个字。", "Hãy đọc chữ này."),

    (8, "读书"):
        ("我喜欢读书。", "Tôi thích đọc sách."),

    (8, "关上"):
        ("请关上门。", "Hãy đóng cửa."),

    (8, "回答"):
        ("请回答问题。", "Hãy trả lời câu hỏi."),

    (8, "记"):
        ("我记这个汉字。", "Tôi ghi nhớ chữ Hán này."),

    (8, "记得"):
        ("我记得他的名字。", "Tôi nhớ tên của anh ấy."),

    (8, "记住"):
        ("请记住这个汉字。", "Hãy nhớ kỹ chữ Hán này."),

    (8, "课本"):
        ("请打开课本。", "Hãy mở sách giáo khoa."),

    (8, "课文"):
        ("我们一起读课文。", "Chúng ta cùng đọc bài khóa."),

    (8, "试"):
        ("你试一下。", "Bạn thử một chút đi."),

    (8, "书"):
        ("这是我的书。", "Đây là sách của tôi."),

    (8, "书包"):
        ("书在书包里。", "Sách ở trong cặp."),

    (8, "说"):
        ("请说中文。", "Hãy nói tiếng Trung."),

    (8, "说话"):
        ("他们在说话。", "Họ đang nói chuyện."),

    (8, "听"):
        ("请听老师说。", "Hãy nghe giáo viên nói."),

    (8, "听写"):
        ("今天我们听写。", "Hôm nay chúng tôi viết chính tả."),

    (8, "忘"):
        ("别忘了。", "Đừng quên nhé."),

    (8, "忘记"):
        ("我忘记他的名字了。", "Tôi quên tên của anh ấy rồi."),

    (8, "问"):
        ("我想问老师。", "Tôi muốn hỏi giáo viên."),

    (8, "写"):
        ("我写汉字。", "Tôi viết chữ Hán."),

    (8, "页"):
        ("请看这一页。", "Hãy xem trang này."),

    (8, "字"):
        ("这个字怎么读？", "Chữ này đọc thế nào?"),

    (8, "子（桌子）"):
        ("这是桌子。", "Đây là cái bàn."),


    # --------------------------------------------------------
    # BÀI 9
    # --------------------------------------------------------

    (9, "穿"):
        ("我穿新衣服。", "Tôi mặc quần áo mới."),

    (9, "等"):
        ("请等我一会儿。", "Hãy đợi tôi một lát."),

    (9, "动"):
        ("别动！", "Đừng động đậy!"),

    (9, "动作"):
        ("这个动作很简单。", "Động tác này rất đơn giản."),

    (9, "干"):
        ("你在干什么？", "Bạn đang làm gì?"),

    (9, "工人"):
        ("我爸爸是工人。", "Bố tôi là công nhân."),

    (9, "工作"):
        ("我每天工作。", "Tôi làm việc mỗi ngày."),

    (9, "回家"):
        ("我下午回家。", "Buổi chiều tôi về nhà."),

    (9, "开会"):
        ("我们上午开会。", "Chúng tôi họp vào buổi sáng."),

    (9, "累"):
        ("今天我很累。", "Hôm nay tôi rất mệt."),

    (9, "忙"):
        ("今天我很忙。", "Hôm nay tôi rất bận."),

    (9, "起"):
        ("请起。", "Mời đứng dậy."),

    (9, "起床"):
        ("我每天六点起床。", "Tôi thức dậy lúc sáu giờ mỗi ngày."),

    (9, "起来"):
        ("请站起来。", "Hãy đứng dậy."),

    (9, "上班"):
        ("我每天八点上班。", "Tôi đi làm lúc tám giờ mỗi ngày."),

    (9, "睡"):
        ("孩子在睡。", "Đứa trẻ đang ngủ."),

    (9, "睡觉"):
        ("我晚上十一点睡觉。", "Tôi đi ngủ lúc mười một giờ tối."),

    (9, "洗"):
        ("我洗衣服。", "Tôi giặt quần áo."),

    (9, "下班"):
        ("我下午五点下班。", "Tôi tan làm lúc năm giờ chiều."),

    (9, "休息"):
        ("我想休息一会儿。", "Tôi muốn nghỉ một lát."),

    (9, "在家"):
        ("今天我在家。", "Hôm nay tôi ở nhà."),

    (9, "做"):
        ("你在做什么？", "Bạn đang làm gì?"),


    # --------------------------------------------------------
    # BÀI 10
    # --------------------------------------------------------

    (10, "吃"):
        ("我喜欢吃米饭。", "Tôi thích ăn cơm."),

    (10, "吃饭"):
        ("我们一起吃饭。", "Chúng ta cùng ăn cơm."),

    (10, "饿"):
        ("我饿了。", "Tôi đói rồi."),

    (10, "饭店"):
        ("我们在饭店吃饭。", "Chúng tôi ăn cơm ở nhà hàng."),

    (10, "好吃"):
        ("这个包子很好吃。", "Bánh bao này rất ngon."),

    (10, "喝"):
        ("我喝水。", "Tôi uống nước."),

    (10, "渴"):
        ("我渴了。", "Tôi khát rồi."),


    # --------------------------------------------------------
    # BÀI 11
    # --------------------------------------------------------

    (11, "别的"):
        ("我想看别的。", "Tôi muốn xem cái khác."),

    (11, "东西"):
        ("我去商店买东西。", "Tôi đi cửa hàng mua đồ."),

    (11, "贵"):
        ("这个太贵了。", "Cái này đắt quá."),

    (11, "买"):
        ("我想买衣服。", "Tôi muốn mua quần áo."),

    (11, "哪"):
        ("你要哪一个？", "Bạn muốn cái nào?"),

    (11, "哪些"):
        ("你喜欢哪些？", "Bạn thích những cái nào?"),

    (11, "那"):
        ("我要那个。", "Tôi muốn cái đó."),

    (11, "那些"):
        ("那些是我的书。", "Những cái đó là sách của tôi."),

    (11, "钱"):
        ("我没有钱。", "Tôi không có tiền."),

    (11, "钱包"):
        ("这是我的钱包。", "Đây là ví của tôi."),

    (11, "商场"):
        ("我去商场买衣服。", "Tôi đi trung tâm thương mại mua quần áo."),

    (11, "商店"):
        ("我去商店买东西。", "Tôi đi cửa hàng mua đồ."),

    (11, "书店"):
        ("我去书店买书。", "Tôi đi nhà sách mua sách."),

    (11, "新"):
        ("这是我的新衣服。", "Đây là quần áo mới của tôi."),

    (11, "一点儿"):
        ("我想喝一点儿水。", "Tôi muốn uống một ít nước."),

    (11, "一些"):
        ("我买了一些水果。", "Tôi mua một ít hoa quả."),

    (11, "有的"):
        ("有的很贵。", "Một số cái rất đắt."),

    (11, "有（一）些"):
        ("这里有一些书。", "Ở đây có một số quyển sách."),

    (11, "元"):
        ("这个十元。", "Cái này mười tệ."),

    (11, "这"):
        ("这是我的。", "Cái này là của tôi."),

    (11, "这些"):
        ("这些是我的书。", "Những cái này là sách của tôi."),


    # --------------------------------------------------------
    # BÀI 12
    # --------------------------------------------------------

    (12, "地上"):
        ("书在地上。", "Sách ở trên sàn."),

    (12, "房间"):
        ("我在房间里。", "Tôi ở trong phòng."),

    (12, "房子"):
        ("这是我的房子。", "Đây là nhà của tôi."),

    (12, "干净"):
        ("房间很干净。", "Căn phòng rất sạch."),

    (12, "间"):
        ("我家有三间房。", "Nhà tôi có ba gian phòng."),

    (12, "里"):
        ("书在包里。", "Sách ở trong túi."),

    (12, "里边"):
        ("他在房间里边。", "Anh ấy ở bên trong phòng."),

    (12, "楼"):
        ("我住在这座楼。", "Tôi sống trong tòa nhà này."),

    (12, "楼上"):
        ("他在楼上。", "Anh ấy ở tầng trên."),

    (12, "楼下"):
        ("我在楼下等你。", "Tôi đợi bạn ở tầng dưới."),

    (12, "门"):
        ("请关上门。", "Hãy đóng cửa."),

    (12, "门口"):
        ("我在门口等你。", "Tôi đợi bạn ở cửa."),

    (12, "上"):
        ("书在桌子上。", "Sách ở trên bàn."),

    (12, "上边"):
        ("书在桌子上边。", "Sách ở phía trên bàn."),

    (12, "外"):
        ("他在门外。", "Anh ấy ở ngoài cửa."),

    (12, "外边"):
        ("外边有人。", "Bên ngoài có người."),

    (12, "洗手间"):
        ("洗手间在哪儿？", "Nhà vệ sinh ở đâu?"),

    (12, "下"):
        ("书在桌子下。", "Sách ở dưới bàn."),

    (12, "下边"):
        ("书在桌子下边。", "Sách ở phía dưới bàn."),

    (12, "住"):
        ("我住在北京。", "Tôi sống ở Bắc Kinh."),

    (12, "桌子"):
        ("书在桌子上。", "Sách ở trên bàn."),


    # --------------------------------------------------------
    # BÀI 13
    # --------------------------------------------------------

    (13, "北"):
        ("向北走。", "Đi về phía bắc."),

    (13, "北边"):
        ("学校在北边。", "Trường học ở phía bắc."),

    (13, "地"):
        ("书在地上。", "Sách ở trên mặt đất."),

    (13, "地点"):
        ("请告诉我地点。", "Hãy cho tôi biết địa điểm."),

    (13, "地方"):
        ("这个地方很好。", "Nơi này rất tốt."),

    (13, "东"):
        ("向东走。", "Đi về phía đông."),

    (13, "东边"):
        ("学校在东边。", "Trường học ở phía đông."),

    (13, "后"):
        ("他在我后面。", "Anh ấy ở phía sau tôi."),

    (13, "后边"):
        ("学校在后边。", "Trường học ở phía sau."),

    (13, "那边"):
        ("商店在那边。", "Cửa hàng ở đằng kia."),

    (13, "那里"):
        ("我在那里等你。", "Tôi đợi bạn ở đó."),

    (13, "那儿"):
        ("他在那儿。", "Anh ấy ở đó."),

    (13, "南"):
        ("向南走。", "Đi về phía nam."),

    (13, "南边"):
        ("学校在南边。", "Trường học ở phía nam."),

    (13, "旁边"):
        ("商店在学校旁边。", "Cửa hàng ở bên cạnh trường."),

    (13, "前"):
        ("他在我前面。", "Anh ấy ở phía trước tôi."),

    (13, "前边"):
        ("车站在前边。", "Nhà ga ở phía trước."),

    (13, "西"):
        ("向西走。", "Đi về phía tây."),

    (13, "西边"):
        ("学校在西边。", "Trường học ở phía tây."),

    (13, "一边"):
        ("他站在一边。", "Anh ấy đứng ở một bên."),

    (13, "右"):
        ("向右走。", "Đi về bên phải."),

    (13, "右边"):
        ("商店在右边。", "Cửa hàng ở bên phải."),

    (13, "这边"):
        ("请来这边。", "Mời đến bên này."),

    (13, "这儿"):
        ("我在这儿。", "Tôi ở đây."),

    (13, "这里"):
        ("这里很好。", "Ở đây rất tốt."),

    (13, "正"):
        ("他正看书。", "Anh ấy đang đọc sách."),

    (13, "中"):
        ("他站在两个人中。", "Anh ấy đứng giữa hai người."),

    (13, "中间"):
        ("桌子在中间。", "Cái bàn ở chính giữa."),

    (13, "左"):
        ("向左走。", "Đi về bên trái."),

    (13, "左边"):
        ("车站在左边。", "Nhà ga ở bên trái."),


    # --------------------------------------------------------
    # BÀI 14
    # --------------------------------------------------------

    (14, "车"):
        ("这是我的车。", "Đây là xe của tôi."),

    (14, "车上"):
        ("我在车上。", "Tôi đang ở trên xe."),

    (14, "车站"):
        ("车站在哪儿？", "Nhà ga ở đâu?"),

    (14, "从"):
        ("我从学校回家。", "Tôi từ trường về nhà."),

    (14, "打车"):
        ("我们打车去机场。", "Chúng tôi bắt taxi đi sân bay."),

    (14, "地图"):
        ("我看一下地图。", "Tôi xem bản đồ một chút."),

    (14, "开车"):
        ("我爸爸会开车。", "Bố tôi biết lái xe."),

    (14, "路"):
        ("这条路很长。", "Con đường này rất dài."),

    (14, "路口"):
        ("车站在路口旁边。", "Nhà ga ở cạnh ngã tư."),

    (14, "路上"):
        ("我在路上。", "Tôi đang trên đường."),

    (14, "马路"):
        ("不要在马路上跑。", "Đừng chạy trên đường."),

    (14, "哪里"):
        ("你去哪里？", "Bạn đi đâu?"),

    (14, "哪儿"):
        ("你去哪儿？", "Bạn đi đâu?"),

    (14, "跑"):
        ("他每天跑。", "Anh ấy chạy mỗi ngày."),

    (14, "汽车"):
        ("这是汽车。", "Đây là ô tô."),

    (14, "请问"):
        ("请问，车站在哪儿？", "Cho hỏi, nhà ga ở đâu?"),

    (14, "上车"):
        ("请上车。", "Mời lên xe."),

    (14, "下车"):
        ("我在下一站下车。", "Tôi xuống xe ở trạm tiếp theo."),

    (14, "远"):
        ("学校离我家很远。", "Trường học cách nhà tôi rất xa."),

    (14, "站"):
        ("下一站是北京站。", "Trạm tiếp theo là ga Bắc Kinh."),

    (14, "走"):
        ("我们走吧。", "Chúng ta đi thôi."),

    (14, "走路"):
        ("我每天走路上学。", "Tôi đi bộ đến trường mỗi ngày."),


    # --------------------------------------------------------
    # BÀI 15
    # --------------------------------------------------------

    (15, "白"):
        ("这件衣服是白的。", "Bộ quần áo này màu trắng."),

    (15, "风"):
        ("今天风很大。", "Hôm nay gió rất mạnh."),

    (15, "干"):
        ("天气很干。", "Thời tiết rất khô."),

    (15, "花"):
        ("这朵花很好看。", "Bông hoa này rất đẹp."),

    (15, "冷"):
        ("今天很冷。", "Hôm nay rất lạnh."),

    (15, "热"):
        ("今天很热。", "Hôm nay rất nóng."),

    (15, "山"):
        ("那边有一座山。", "Đằng kia có một ngọn núi."),

    (15, "树"):
        ("那里有很多树。", "Ở đó có rất nhiều cây."),

    (15, "天气"):
        ("今天天气很好。", "Thời tiết hôm nay rất đẹp."),

    (15, "下雨"):
        ("今天下雨了。", "Hôm nay trời mưa."),

    (15, "雨"):
        ("外边有雨。", "Bên ngoài có mưa."),


    # --------------------------------------------------------
    # BÀI 16
    # --------------------------------------------------------

    (16, "病"):
        ("他有病。", "Anh ấy bị bệnh."),

    (16, "病人"):
        ("他是病人。", "Anh ấy là bệnh nhân."),

    (16, "看病"):
        ("我去医院看病。", "Tôi đi bệnh viện khám bệnh."),

    (16, "口"):
        ("请张开口。", "Hãy mở miệng."),

    (16, "毛"):
        ("这只狗的毛很白。", "Lông của con chó này rất trắng."),

    (16, "身上"):
        ("我身上有点儿冷。", "Tôi cảm thấy hơi lạnh trên người."),

    (16, "身体"):
        ("我的身体很好。", "Sức khỏe của tôi rất tốt."),

    (16, "生病"):
        ("我生病了。", "Tôi bị ốm rồi."),

    (16, "生气"):
        ("别生气。", "Đừng tức giận."),

    (16, "手"):
        ("我的手很冷。", "Tay tôi rất lạnh."),

    (16, "医生"):
        ("她是医生。", "Cô ấy là bác sĩ."),

    (16, "医院"):
        ("医院在那边。", "Bệnh viện ở đằng kia."),


    # --------------------------------------------------------
    # BÀI 17
    # --------------------------------------------------------

    (17, "爱"):
        ("我爱我的家人。", "Tôi yêu gia đình của tôi."),

    (17, "爱好"):
        ("我的爱好是看电影。", "Sở thích của tôi là xem phim."),

    (17, "唱"):
        ("她会唱中文歌。", "Cô ấy biết hát bài hát tiếng Trung."),

    (17, "唱歌"):
        ("我喜欢唱歌。", "Tôi thích hát."),

    (17, "打球"):
        ("我们一起打球。", "Chúng tôi cùng chơi bóng."),

    (17, "电"):
        ("这里没有电。", "Ở đây không có điện."),

    (17, "电脑"):
        ("这是我的电脑。", "Đây là máy tính của tôi."),

    (17, "电视"):
        ("我晚上看电视。", "Buổi tối tôi xem TV."),

    (17, "电视机"):
        ("家里有一台电视机。", "Trong nhà có một chiếc tivi."),

    (17, "电影"):
        ("我喜欢看电影。", "Tôi thích xem phim."),

    (17, "电影院"):
        ("我们去电影院。", "Chúng tôi đi rạp chiếu phim."),

    (17, "歌"):
        ("这首歌很好听。", "Bài hát này rất hay."),

    (17, "好看"):
        ("这部电影很好看。", "Bộ phim này rất hay."),

    (17, "好听"):
        ("这首歌很好听。", "Bài hát này nghe rất hay."),

    (17, "好玩儿"):
        ("这个游戏很好玩儿。", "Trò chơi này rất thú vị."),

    (17, "觉得"):
        ("我觉得这部电影很好看。", "Tôi thấy bộ phim này rất hay."),

    (17, "开玩笑"):
        ("我跟你开玩笑呢。", "Tôi đang đùa với bạn thôi."),

    (17, "看"):
        ("我看电影。", "Tôi xem phim."),

    (17, "球"):
        ("这是一个球。", "Đây là một quả bóng."),

    (17, "上网"):
        ("我晚上上网。", "Buổi tối tôi lên mạng."),

    (17, "玩儿"):
        ("孩子们在玩儿。", "Bọn trẻ đang chơi."),

    (17, "网上"):
        ("我在网上学习汉语。", "Tôi học tiếng Trung trên mạng."),

    (17, "网友"):
        ("他是我的网友。", "Anh ấy là bạn trên mạng của tôi."),

    (17, "喜欢"):
        ("我喜欢学习汉语。", "Tôi thích học tiếng Trung."),

    (17, "笑"):
        ("她笑了。", "Cô ấy cười rồi."),


    # --------------------------------------------------------
    # BÀI 18
    # --------------------------------------------------------

    (18, "北京"):
        ("我想去北京。", "Tôi muốn đi Bắc Kinh."),

    (18, "车票"):
        ("我买了两张车票。", "Tôi mua hai vé xe."),

    (18, "到"):
        ("我八点到学校。", "Tôi đến trường lúc tám giờ."),

    (18, "飞"):
        ("飞机在天上飞。", "Máy bay đang bay trên trời."),

    (18, "飞机"):
        ("我们坐飞机去北京。", "Chúng tôi đi máy bay đến Bắc Kinh."),

    (18, "回到"):
        ("我下午回到家。", "Buổi chiều tôi trở về nhà."),

    (18, "火车"):
        ("我们坐火车去北京。", "Chúng tôi đi tàu hỏa đến Bắc Kinh."),

    (18, "机场"):
        ("我去机场。", "Tôi đi sân bay."),

    (18, "机票"):
        ("我买了机票。", "Tôi đã mua vé máy bay."),

    (18, "来"):
        ("明天你来吗？", "Ngày mai bạn đến không?"),

    (18, "来到"):
        ("我来到北京。", "Tôi đến Bắc Kinh."),

    (18, "门票"):
        ("我买了两张门票。", "Tôi mua hai vé vào cửa."),

    (18, "票"):
        ("这是我的票。", "Đây là vé của tôi."),

    (18, "去"):
        ("我去学校。", "Tôi đi đến trường."),

    (18, "送"):
        ("我送你去机场。", "Tôi tiễn bạn ra sân bay."),

    (18, "行"):
        ("这样行吗？", "Như vậy có được không?"),

    (18, "一块儿"):
        ("我们一块儿去。", "Chúng ta cùng đi."),

    (18, "一起"):
        ("我们一起学习。", "Chúng ta cùng học."),

    (18, "找"):
        ("我在找我的书。", "Tôi đang tìm sách của mình."),

    (18, "找到"):
        ("我找到书了。", "Tôi tìm thấy sách rồi."),

    (18, "坐"):
        ("我坐飞机去北京。", "Tôi đi máy bay đến Bắc Kinh."),

    (18, "坐下"):
        ("请坐下。", "Mời ngồi xuống."),


    # --------------------------------------------------------
    # BÀI 19
    # --------------------------------------------------------

    (19, "帮"):
        ("我帮你。", "Tôi giúp bạn."),

    (19, "帮忙"):
        ("请帮忙。", "Xin hãy giúp một tay."),

    (19, "出"):
        ("他出门了。", "Anh ấy ra khỏi nhà rồi."),

    (19, "出来"):
        ("请出来。", "Hãy đi ra đây."),

    (19, "出去"):
        ("我想出去。", "Tôi muốn ra ngoài."),

    (19, "打"):
        ("我给他打电话。", "Tôi gọi điện cho anh ấy."),

    (19, "放"):
        ("请把书放在桌子上。", "Hãy đặt sách lên bàn."),

    (19, "干什么"):
        ("你在干什么？", "Bạn đang làm gì?"),

    (19, "关"):
        ("请关门。", "Hãy đóng cửa."),

    (19, "回"):
        ("我下午回家。", "Buổi chiều tôi về nhà."),

    (19, "回来"):
        ("你什么时候回来？", "Khi nào bạn quay về?"),

    (19, "回去"):
        ("我要回去了。", "Tôi phải quay về rồi."),

    (19, "进"):
        ("请进。", "Mời vào."),

    (19, "进来"):
        ("请进来。", "Mời vào đây."),

    (19, "进去"):
        ("他走进去了。", "Anh ấy đi vào trong rồi."),

    (19, "开"):
        ("请开门。", "Hãy mở cửa."),

    (19, "拿"):
        ("请拿这本书。", "Hãy cầm quyển sách này."),

    (19, "一下儿"):
        ("请等一下儿。", "Vui lòng đợi một chút."),

    (19, "再"):
        ("请再说一次。", "Hãy nói lại một lần nữa."),

    (19, "在"):
        ("我在学校。", "Tôi ở trường."),

    (19, "着"):
        ("门开着。", "Cửa đang mở."),

    (19, "正在"):
        ("我正在学习汉语。", "Tôi đang học tiếng Trung."),

    (19, "准备"):
        ("我准备去学校。", "Tôi chuẩn bị đi học."),


    # --------------------------------------------------------
    # BÀI 20
    # --------------------------------------------------------

    (20, "不对"):
        ("这个答案不对。", "Đáp án này không đúng."),

    (20, "错"):
        ("这个字写错了。", "Chữ này viết sai rồi."),

    (20, "得到"):
        ("我得到了一本书。", "Tôi nhận được một quyển sách."),

    (20, "对"):
        ("你的答案对了。", "Đáp án của bạn đúng rồi."),

    (20, "过"):
        ("我去过北京。", "Tôi đã từng đến Bắc Kinh."),

    (20, "还"):
        ("我还在学习。", "Tôi vẫn đang học."),

    (20, "会"):
        ("我会说中文。", "Tôi biết nói tiếng Trung."),

    (20, "就"):
        ("我马上就来。", "Tôi sẽ đến ngay."),

    (20, "看到"):
        ("我看到老师了。", "Tôi nhìn thấy giáo viên rồi."),

    (20, "看见"):
        ("我看见他了。", "Tôi nhìn thấy anh ấy rồi."),

    (20, "了"):
        ("我吃饭了。", "Tôi ăn cơm rồi."),

    (20, "没有"):
        ("我没有时间。", "Tôi không có thời gian."),

    (20, "明白"):
        ("我明白了。", "Tôi hiểu rồi."),

    (20, "能"):
        ("我能帮助你。", "Tôi có thể giúp bạn."),

    (20, "听到"):
        ("我听到声音了。", "Tôi nghe thấy âm thanh rồi."),

    (20, "听见"):
        ("我听见他说话了。", "Tôi nghe thấy anh ấy nói chuyện."),

    (20, "想"):
        ("我想学习汉语。", "Tôi muốn học tiếng Trung."),

    (20, "要"):
        ("我要一杯水。", "Tôi muốn một cốc nước."),

    (20, "用"):
        ("我用电脑学习。", "Tôi dùng máy tính để học."),

    (20, "有"):
        ("我有一本书。", "Tôi có một quyển sách."),

    (20, "有用"):
        ("这个很有用。", "Cái này rất hữu ích."),

    (20, "知道"):
        ("我知道他的名字。", "Tôi biết tên của anh ấy."),


    # --------------------------------------------------------
    # BÀI 21
    # --------------------------------------------------------

    (21, "比"):
        ("他比我高。", "Anh ấy cao hơn tôi."),

    (21, "不大"):
        ("这个房间不大。", "Căn phòng này không lớn lắm."),

    (21, "差"):
        ("这个比较差。", "Cái này khá kém."),

    (21, "非常"):
        ("我非常喜欢汉语。", "Tôi rất thích tiếng Trung."),

    (21, "太"):
        ("这个太贵了。", "Cái này đắt quá."),

    (21, "一样"):
        ("这两个一样。", "Hai cái này giống nhau."),

    (21, "真"):
        ("你真好！", "Bạn thật tốt!"),

    (21, "真的"):
        ("这是真的吗？", "Điều này có thật không?"),

    (21, "最"):
        ("我最喜欢汉语。", "Tôi thích tiếng Trung nhất."),

    (21, "最好"):
        ("这个最好。", "Cái này tốt nhất."),


    # --------------------------------------------------------
    # BÀI 22
    # --------------------------------------------------------

    (22, "不客气"):
        ("谢谢！——不客气。", "Cảm ơn! — Không có gì."),

    (22, "打电话"):
        ("我给你打电话。", "Tôi gọi điện cho bạn."),

    (22, "电话"):
        ("这是我的电话。", "Đây là điện thoại của tôi."),

    (22, "对不起"):
        ("对不起，我来晚了。", "Xin lỗi, tôi đến muộn."),

    (22, "告诉"):
        ("请告诉我你的名字。", "Hãy cho tôi biết tên của bạn."),

    (22, "给"):
        ("我给你一本书。", "Tôi đưa bạn một quyển sách."),

    (22, "话"):
        ("我有话跟你说。", "Tôi có chuyện muốn nói với bạn."),

    (22, "见"):
        ("明天见！", "Hẹn gặp ngày mai!"),

    (22, "见面"):
        ("我们明天见面。", "Ngày mai chúng ta gặp nhau."),

    (22, "没关系"):
        ("没关系，别担心。", "Không sao, đừng lo."),

    (22, "没事儿"):
        ("我没事儿。", "Tôi không sao."),

    (22, "请"):
        ("请进。", "Mời vào."),

    (22, "请进"):
        ("请进！", "Mời vào!"),

    (22, "请坐"):
        ("请坐！", "Mời ngồi!"),

    (22, "事"):
        ("我有一件事。", "Tôi có một việc."),

    (22, "手机"):
        ("这是我的手机。", "Đây là điện thoại của tôi."),

    (22, "谢谢"):
        ("谢谢你的帮助。", "Cảm ơn sự giúp đỡ của bạn."),

    (22, "再见"):
        ("老师，再见！", "Tạm biệt thầy/cô!"),


    # --------------------------------------------------------
    # BÀI 23
    # --------------------------------------------------------

    (23, "吧"):
        ("我们走吧！", "Chúng ta đi thôi!"),

    (23, "别"):
        ("别说话。", "Đừng nói chuyện."),

    (23, "别人"):
        ("这是别人的书。", "Đây là sách của người khác."),

    (23, "不用"):
        ("你不用来。", "Bạn không cần đến."),

    (23, "不"):
        ("我不去。", "Tôi không đi."),

    (23, "地"):
        ("他认真地学习。", "Anh ấy học một cách nghiêm túc."),

    (23, "的"):
        ("这是我的书。", "Đây là sách của tôi."),

    (23, "都"):
        ("我们都是学生。", "Chúng tôi đều là học sinh."),

    (23, "跟"):
        ("我跟朋友一起去。", "Tôi đi cùng bạn."),

    (23, "还是"):
        ("你喝茶还是喝水？", "Bạn uống trà hay uống nước?"),

    (23, "还有"):
        ("我还有一本书。", "Tôi còn một quyển sách nữa."),

    (23, "和"):
        ("我和他是朋友。", "Tôi và anh ấy là bạn."),

    (23, "没"):
        ("我没去。", "Tôi chưa đi."),

    (23, "没什么"):
        ("没什么，不用担心。", "Không có gì, đừng lo."),

    (23, "是不是"):
        ("你是不是学生？", "Bạn có phải là học sinh không?"),

    (23, "怎么"):
        ("这个字怎么读？", "Chữ này đọc thế nào?"),
}


# ============================================================
# CÁC NHÓM DÙNG ĐỂ TẠO VÍ DỤ CHUNG
# ============================================================

SCHOOL_PLACES = {
    "大学",
    "教学楼",
    "图书馆",
    "小学",
    "学校",
    "学院",
    "中学",
}

SCHOOL_PEOPLE = {
    "大学生",
    "老师",
    "同学",
    "小学生",
    "学生",
    "中学生",
}

FOOD_EAT = {
    "包子",
    "菜",
    "饭",
    "鸡蛋",
    "米饭",
    "面包",
    "面条儿",
    "肉",
    "水果",
    "晚饭",
    "午饭",
    "早饭",
}

FOOD_DRINK = {
    "茶",
    "奶",
    "牛奶",
    "水",
}

SHOP_ITEMS = {
    "包",
    "衣服",
}

HOME_ITEMS = {
    "床",
    "桌子",
}

ADJECTIVE_WORDS = {
    "大",
    "高",
    "坏",
    "快",
    "老",
    "慢",
    "难",
    "小",
    "重",
    "重要",
}


# ============================================================
# SINH VÍ DỤ
# ============================================================

def generate_example(row):

    lesson = row["SoThuTuBai"]
    word = row["ChuHan"]
    meaning = first_meaning(
        row["NghiaTiengViet"]
    )
    pos = row["TuLoai"]


    # --------------------------------------------------------
    # ƯU TIÊN DỮ LIỆU VIẾT RIÊNG
    # --------------------------------------------------------

    special = SPECIAL.get(
        (lesson, word)
    )

    if special is not None:
        return special


    # --------------------------------------------------------
    # BÀI 3 - GIA ĐÌNH
    # --------------------------------------------------------

    if lesson == 3:

        return (
            f"这是我的{word}。",
            f"Đây là {meaning} của tôi.",
        )


    # --------------------------------------------------------
    # BÀI 7 - TRƯỜNG HỌC
    # --------------------------------------------------------

    if lesson == 7:

        if word in SCHOOL_PLACES:

            return (
                f"我在{word}学习。",
                f"Tôi học ở {meaning}.",
            )


        if word in SCHOOL_PEOPLE:

            return (
                f"他是{word}。",
                f"Anh ấy là {meaning}.",
            )


        return (
            f"我学习{word}。",
            f"Tôi học về {meaning}.",
        )


    # --------------------------------------------------------
    # BÀI 10 - ĂN UỐNG
    # --------------------------------------------------------

    if lesson == 10:

        if word in FOOD_EAT:

            return (
                f"我喜欢吃{word}。",
                f"Tôi thích ăn {meaning}.",
            )


        if word in FOOD_DRINK:

            return (
                f"我喜欢喝{word}。",
                f"Tôi thích uống {meaning}.",
            )


        if word == "杯子":

            return (
                "这是我的杯子。",
                "Đây là cái cốc của tôi.",
            )


        return (
            f"我喜欢{word}。",
            f"Tôi thích {meaning}.",
        )


    # --------------------------------------------------------
    # BÀI 11 - MUA SẮM
    # --------------------------------------------------------

    if lesson == 11:

        if word in SHOP_ITEMS:

            return (
                f"我想买{word}。",
                f"Tôi muốn mua {meaning}.",
            )


        return (
            f"这个{word}很好。",
            f"{meaning.capitalize()} này rất tốt.",
        )


    # --------------------------------------------------------
    # BÀI 12 - NHÀ CỬA
    # --------------------------------------------------------

    if lesson == 12:

        if word in HOME_ITEMS:

            return (
                f"这是我的{word}。",
                f"Đây là {meaning} của tôi.",
            )


    # --------------------------------------------------------
    # BÀI 21 - TÍNH TỪ
    # --------------------------------------------------------

    if lesson == 21:

        if word in ADJECTIVE_WORDS:

            return (
                f"这个很{word}。",
                f"Cái này rất {meaning}.",
            )


    # --------------------------------------------------------
    # FALLBACK THEO TỪ LOẠI
    # --------------------------------------------------------

    if "Danh từ" in pos:

        return (
            f"这是{word}。",
            f"Đây là {meaning}.",
        )


    if "Tính từ" in pos:

        return (
            f"这个很{word}。",
            f"Cái này rất {meaning}.",
        )


    if "Động từ" in pos:

        return (
            f"我{word}。",
            f"Tôi {meaning}.",
        )


    if "Phó từ" in pos:

        return (
            f"我{word}学习汉语。",
            f"Tôi {meaning} học tiếng Trung.",
        )


    return (
        f"这里有“{word}”这个词。",
        f"Ở đây có từ “{word}”.",
    )


# ============================================================
# ĐỌC FILE 501 TỪ
#
# File SSMS của bạn không có header.
# ============================================================

def load_source():

    if not SOURCE_FILE.exists():

        raise FileNotFoundError(
            f"Không tìm thấy file:\n"
            f"{SOURCE_FILE}"
        )


    rows = []


    with SOURCE_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.reader(file)


        for line_number, columns in enumerate(
            reader,
            start=1,
        ):

            if len(columns) != 12:

                raise RuntimeError(
                    f"Dòng {line_number} "
                    f"không có đúng 12 cột. "
                    f"Thực tế: {len(columns)}"
                )


            row = {
                "SoThuTuBai":
                    int(columns[0]),

                "MaBaiHoc":
                    int(columns[1]),

                "ThuTu":
                    int(columns[2]),

                "MaTuVung":
                    int(columns[3]),

                "ChuHan":
                    clean(columns[4]),

                "PhienAm":
                    clean(columns[5]),

                "NghiaTiengViet":
                    clean(columns[6]),

                "TuLoai":
                    clean(columns[7]),

                "ViDuTiengTrung":
                    clean(columns[8]),

                "ViDuTiengViet":
                    clean(columns[9]),

                "MaNguon":
                    clean(columns[10]),

                "DaDuyet":
                    clean(columns[11]),
            }


            rows.append(row)


    if len(rows) != EXPECTED_TOTAL_HSK1:

        raise RuntimeError(
            "File phải có đúng "
            f"{EXPECTED_TOTAL_HSK1} từ. "
            f"Thực tế: {len(rows)}"
        )


    return rows


# ============================================================
# TẠO 459 VÍ DỤ BÀI 3 -> 23
# ============================================================

def build_examples(source_rows):

    target = [
        row
        for row in source_rows
        if (
            FIRST_LESSON
            <= row["SoThuTuBai"]
            <= LAST_LESSON
        )
    ]


    if len(target) != EXPECTED_TARGET:

        raise RuntimeError(
            "Bài 3 -> 23 phải có đúng "
            f"{EXPECTED_TARGET} từ. "
            f"Thực tế: {len(target)}"
        )


    result = []


    for row in target:

        zh, vi = generate_example(
            row
        )


        if not clean(zh):

            raise RuntimeError(
                f"{row['ChuHan']} "
                "không có ví dụ tiếng Trung."
            )


        if not clean(vi):

            raise RuntimeError(
                f"{row['ChuHan']} "
                "không có ví dụ tiếng Việt."
            )


        result.append(
            {
                **row,

                "ViDuTiengTrung":
                    clean(zh),

                "ViDuTiengViet":
                    clean(vi),
            }
        )


    return result


# ============================================================
# KIỂM TRA SỐ TỪ TỪNG BÀI
# ============================================================

def validate_counts(rows):

    counts = {}


    for row in rows:

        lesson = row["SoThuTuBai"]

        counts[lesson] = (
            counts.get(
                lesson,
                0,
            )
            + 1
        )


    print()
    print(
        "[2] Kiểm tra số lượng từng bài"
    )

    print("-" * 90)


    for lesson in range(
        FIRST_LESSON,
        LAST_LESSON + 1,
    ):

        actual = counts.get(
            lesson,
            0,
        )

        expected = EXPECTED_COUNTS[
            lesson
        ]


        print(
            f"Bài {lesson:>2}: "
            f"{actual:>3}/{expected:<3}"
        )


        if actual != expected:

            raise RuntimeError(
                f"Bài {lesson} "
                f"phải có {expected} từ, "
                f"thực tế {actual}."
            )


# ============================================================
# XUẤT FILE PREVIEW
# ============================================================

def write_preview(rows):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    fields = [
        "SoThuTuBai",
        "MaBaiHoc",
        "ThuTu",
        "MaTuVung",
        "ChuHan",
        "PhienAm",
        "NghiaTiengViet",
        "TuLoai",
        "ViDuTiengTrung",
        "ViDuTiengViet",
        "MaNguon",
        "DaDuyet",
    ]


    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


    print()
    print(
        "[3] Đã tạo file preview"
    )

    print(
        OUTPUT_FILE
    )


# ============================================================
# KIỂM TRA LIVE DATABASE
# ============================================================

def validate_live_database(
    cursor,
    rows,
):

    print()
    print(
        "[4] Kiểm tra 459 từ với live database"
    )

    print("-" * 90)


    cursor.execute(
        """
        SELECT
            kh.MaKhoaHoc

        FROM dbo.KhoaHoc kh

        WHERE kh.MaKyHieu = ?
        """,
        COURSE_CODE,
    )


    course = cursor.fetchone()


    if course is None:

        raise RuntimeError(
            f"Không tìm thấy {COURSE_CODE}."
        )


    ma_khoa_hoc = course.MaKhoaHoc


    cursor.execute(
        """
        SELECT
            COUNT(*)

        FROM dbo.TuVung tv

        INNER JOIN dbo.TuVungBaiHoc tvbh
            ON tvbh.MaTuVung = tv.MaTuVung

        INNER JOIN dbo.BaiHoc bh
            ON bh.MaBaiHoc = tvbh.MaBaiHoc

        WHERE bh.MaKhoaHoc = ?
        """,
        ma_khoa_hoc,
    )


    total = cursor.fetchone()[0]


    print(
        "Tổng từ HSK1 trong DB:",
        total,
    )


    if total != EXPECTED_TOTAL_HSK1:

        raise RuntimeError(
            "HSK1 phải có 501 từ. "
            f"Thực tế: {total}"
        )


    for index, row in enumerate(
        rows,
        start=1,
    ):

        cursor.execute(
            """
            SELECT
                tv.MaTuVung,
                tv.ChuHan,
                bh.SoThuTuBai,
                tvbh.ThuTu,
                tv.ViDuTiengTrung,
                tv.ViDuTiengViet

            FROM dbo.TuVung tv

            INNER JOIN dbo.TuVungBaiHoc tvbh
                ON tvbh.MaTuVung = tv.MaTuVung

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc = tvbh.MaBaiHoc

            WHERE tv.MaTuVung = ?
              AND tv.ChuHan = ?
              AND bh.MaKhoaHoc = ?
              AND bh.SoThuTuBai = ?
              AND tvbh.ThuTu = ?
            """,
            row["MaTuVung"],
            row["ChuHan"],
            ma_khoa_hoc,
            row["SoThuTuBai"],
            row["ThuTu"],
        )


        db_row = cursor.fetchone()


        if db_row is None:

            raise RuntimeError(
                "Không khớp DB: "
                f"Bài {row['SoThuTuBai']} | "
                f"MaTuVung={row['MaTuVung']} | "
                f"{row['ChuHan']}"
            )


        if (
            index % 50 == 0
            or index == len(rows)
        ):

            print(
                f"Đã kiểm tra "
                f"{index}/{len(rows)} từ..."
            )


    return ma_khoa_hoc


# ============================================================
# UPDATE DATABASE
# ============================================================

def apply_database(
    conn,
    cursor,
    rows,
    ma_khoa_hoc,
):

    print()
    print(
        "[5] UPDATE Bài 3 -> 23"
    )

    print("-" * 90)


    updated = 0
    skipped = 0


    try:

        for index, row in enumerate(
            rows,
            start=1,
        ):

            # ------------------------------------------------
            # Không ghi đè dữ liệu đã có.
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    ViDuTiengTrung,
                    ViDuTiengViet

                FROM dbo.TuVung

                WHERE MaTuVung = ?
                  AND ChuHan = ?
                """,
                row["MaTuVung"],
                row["ChuHan"],
            )


            current = cursor.fetchone()


            if current is None:

                raise RuntimeError(
                    "Không tìm thấy "
                    f"{row['MaTuVung']} "
                    f"{row['ChuHan']}"
                )


            old_zh = clean(
                current.ViDuTiengTrung
            )

            old_vi = clean(
                current.ViDuTiengViet
            )


            if old_zh and old_vi:

                skipped += 1

                continue


            cursor.execute(
                """
                UPDATE dbo.TuVung

                SET
                    ViDuTiengTrung = ?,
                    ViDuTiengViet = ?

                WHERE MaTuVung = ?
                  AND ChuHan = ?
                """,
                row["ViDuTiengTrung"],
                row["ViDuTiengViet"],
                row["MaTuVung"],
                row["ChuHan"],
            )


            if cursor.rowcount != 1:

                raise RuntimeError(
                    "UPDATE không đúng 1 dòng: "
                    f"{row['MaTuVung']} "
                    f"{row['ChuHan']}"
                )


            updated += 1


            if (
                index % 50 == 0
                or index == len(rows)
            ):

                print(
                    f"Đã xử lý "
                    f"{index}/{len(rows)} từ..."
                )


        # ====================================================
        # AUDIT TOÀN BỘ 501
        # ====================================================

        cursor.execute(
            """
            SELECT
                COUNT(*) AS TongTu,

                SUM(
                    CASE
                        WHEN
                            tv.ViDuTiengTrung IS NULL
                            OR LTRIM(
                                RTRIM(
                                    tv.ViDuTiengTrung
                                )
                            ) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuTrung,

                SUM(
                    CASE
                        WHEN
                            tv.ViDuTiengViet IS NULL
                            OR LTRIM(
                                RTRIM(
                                    tv.ViDuTiengViet
                                )
                            ) = ''
                        THEN 1
                        ELSE 0
                    END
                ) AS ThieuViet

            FROM dbo.TuVung tv

            INNER JOIN dbo.TuVungBaiHoc tvbh
                ON tvbh.MaTuVung = tv.MaTuVung

            INNER JOIN dbo.BaiHoc bh
                ON bh.MaBaiHoc = tvbh.MaBaiHoc

            WHERE bh.MaKhoaHoc = ?
            """,
            ma_khoa_hoc,
        )


        audit = cursor.fetchone()


        tong = audit.TongTu or 0
        thieu_zh = audit.ThieuTrung or 0
        thieu_vi = audit.ThieuViet or 0


        print()
        print("=" * 90)
        print(
            "AUDIT TOÀN BỘ HSK1"
        )
        print("=" * 90)


        print(
            "Tổng từ HSK1:",
            tong,
        )

        print(
            "Đã UPDATE lần này:",
            updated,
        )

        print(
            "Bỏ qua vì đã có ví dụ:",
            skipped,
        )

        print(
            "Thiếu ví dụ Trung:",
            thieu_zh,
        )

        print(
            "Thiếu ví dụ Việt:",
            thieu_vi,
        )


        if (
            tong != EXPECTED_TOTAL_HSK1
            or thieu_zh != 0
            or thieu_vi != 0
        ):

            raise RuntimeError(
                "Audit chưa sạch. "
                "Không COMMIT."
            )


        conn.commit()


        print()
        print(
            "✅ 501/501 TỪ VỰNG HSK1 "
            "ĐÃ CÓ VÍ DỤ."
        )

        print(
            "✅ COMMIT THÀNH CÔNG."
        )


    except Exception:

        conn.rollback()

        print()
        print(
            "❌ ĐÃ ROLLBACK."
        )

        print(
            "Database không giữ "
            "các thay đổi của lần chạy lỗi."
        )

        raise


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Thực sự cập nhật database. "
            "Nếu không có --apply thì chỉ preview."
        ),
    )

    args = parser.parse_args()


    conn = None


    try:

        print("=" * 100)
        print(
            "HSK1 - BỔ SUNG VÍ DỤ "
            "TỪ VỰNG BÀI 3 -> 23"
        )
        print("=" * 100)


        # ====================================================
        # 1. LOAD SOURCE
        # ====================================================

        print()
        print(
            "[1] Đọc file 501 từ"
        )


        source_rows = load_source()


        print(
            "Tổng dòng nguồn:",
            len(source_rows),
        )


        target_rows = build_examples(
            source_rows
        )


        print(
            "Bài 3 -> 23:",
            len(target_rows),
        )


        # ====================================================
        # 2. CHECK COUNTS
        # ====================================================

        validate_counts(
            target_rows
        )


        # ====================================================
        # 3. PREVIEW CSV
        # ====================================================

        write_preview(
            target_rows
        )


        # ====================================================
        # 4. DATABASE
        # ====================================================

        print()
        print(
            "Đang kết nối database..."
        )


        conn = get_connection()

        conn.autocommit = False

        cursor = conn.cursor()


        print(
            "Kết nối database: OK"
        )


        ma_khoa_hoc = validate_live_database(
            cursor,
            target_rows,
        )


        # ====================================================
        # DRY RUN
        # ====================================================

        if not args.apply:

            conn.rollback()

            print()
            print("=" * 100)
            print(
                "✅ DRY-RUN THÀNH CÔNG"
            )
            print("=" * 100)

            print(
                "459 từ Bài 3 -> 23 "
                "đã được tạo và kiểm tra."
            )

            print()
            print(
                "DATABASE CHƯA BỊ SỬA."
            )

            print()
            print(
                "File preview:"
            )

            print(
                OUTPUT_FILE
            )

            print()
            print(
                "Nếu kết quả này sạch, "
                "chạy lại với --apply."
            )

            return


        # ====================================================
        # APPLY
        # ====================================================

        apply_database(
            conn,
            cursor,
            target_rows,
            ma_khoa_hoc,
        )


    except Exception as error:

        if conn is not None:

            try:
                conn.rollback()

            except Exception:
                pass


        print()
        print("=" * 100)
        print(
            "❌ CÓ LỖI"
        )
        print("=" * 100)

        print(error)


    finally:

        if conn is not None:

            conn.close()


        print()
        print(
            "Đã đóng kết nối database."
        )


if __name__ == "__main__":
    main()