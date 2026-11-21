import csv
import re
from pathlib import Path


# ==========================================================
# HSK3 - BATCH 2
# 200 từ: MaTuVung 1702 -> 1901
#
# SOURCE:
#   offline_preview_hsk3.csv
#
# OUTPUT:
#   offline_preview_hsk3_batch2.csv
#
# Sau Batch 1:
#   READY       = 201
#   NEED_REVIEW = 760
#
# Sau Batch 2 dự kiến:
#   READY       = 401
#   NEED_REVIEW = 560
#
# KHÔNG thay đổi SQL Server.
# ==========================================================

DATA_DIR = Path(__file__).resolve().parent / "data"

SOURCE = DATA_DIR / "offline_preview_hsk3.csv"
OUTPUT = DATA_DIR / "offline_preview_hsk3_batch2.csv"


# ==========================================================
# 200 CÂU HSK3 THỰC TẾ
# Format:
# MaTuVung|Câu tiếng Trung|Dịch tiếng Việt
# ==========================================================

EXAMPLES = """
1702|这家商店主要卖年轻人的服装。|Cửa hàng này chủ yếu bán quần áo dành cho người trẻ.
1703|春节时人们常在门上贴“福”字。|Vào dịp Tết, mọi người thường dán chữ “Phúc” lên cửa.
1704|我的父母都很支持我学习汉语。|Cha mẹ tôi đều rất ủng hộ tôi học tiếng Trung.
1705|我的父亲是一名医生。|Cha tôi là một bác sĩ.
1706|这个月的房租我已经付了。|Tiền thuê nhà tháng này tôi đã trả rồi.
1707|王老师负责这次活动。|Thầy Vương phụ trách hoạt động lần này.
1708|请帮我复印这份文件。|Hãy giúp tôi photocopy tài liệu này.
1709|这个问题比我想的复杂。|Vấn đề này phức tạp hơn tôi nghĩ.
1710|这个村子现在越来越富。|Ngôi làng này hiện ngày càng giàu có.
1711|我们需要不断改进学习方法。|Chúng ta cần không ngừng cải thiện phương pháp học.
1712|这个旧工厂已经被改造了。|Nhà máy cũ này đã được cải tạo.
1713|老师正在给我们解释这个概念。|Giáo viên đang giải thích khái niệm này cho chúng tôi.
1714|我每天早上赶七点的公交车。|Mỗi sáng tôi vội bắt chuyến xe buýt lúc bảy giờ.
1715|医生很快赶到了医院。|Bác sĩ nhanh chóng đến bệnh viện.
1716|快下雨了，我们赶紧回家吧。|Sắp mưa rồi, chúng ta mau về nhà thôi.
1717|时间不早了，你赶快出发吧。|Không còn sớm nữa, bạn mau xuất phát đi.
1718|他不敢一个人走夜路。|Anh ấy không dám đi đường ban đêm một mình.
1719|我昨天感冒了，所以没有去上课。|Hôm qua tôi bị cảm nên không đi học.
1720|他们两个人的感情很好。|Tình cảm giữa hai người họ rất tốt.
1721|第一次来到这里，我有很多新的感受。|Lần đầu đến đây, tôi có rất nhiều cảm nhận mới.
1722|你站在门口干吗？|Bạn đứng ở cửa làm gì vậy?
1723|这列高速列车非常快。|Chuyến tàu cao tốc này rất nhanh.
1724|我们开车走高速公路去上海。|Chúng tôi lái xe theo đường cao tốc đến Thượng Hải.
1725|毕业那天，我们和老师告别。|Ngày tốt nghiệp, chúng tôi nói lời tạm biệt với giáo viên.
1726|门口站着很多年轻歌迷。|Ngoài cửa có rất nhiều người hâm mộ ca sĩ trẻ.
1727|我从房间里听到了她的歌声。|Tôi nghe thấy giọng hát của cô ấy từ trong phòng.
1728|她长大以后想成为一名歌手。|Sau khi lớn lên cô ấy muốn trở thành ca sĩ.
1729|这是我个人的意见。|Đây là ý kiến cá nhân của tôi.
1730|这个孩子很有个性。|Đứa trẻ này rất có cá tính.
1731|各班学生都要参加这次活动。|Học sinh của mỗi lớp đều phải tham gia hoạt động lần này.
1732|春节期间，各地都有很多游客。|Trong dịp Tết, khắp các vùng đều có nhiều du khách.
1733|各位同学，请安静一下。|Các bạn học sinh, xin hãy yên lặng một chút.
1734|超市里有各种水果。|Trong siêu thị có đủ loại trái cây.
1735|会议结束后，大家各自回家。|Sau khi cuộc họp kết thúc, mọi người tự về nhà mình.
1736|我根本不知道这件事。|Tôi hoàn toàn không biết việc này.
1737|经过练习，她的汉语更加流利了。|Sau khi luyện tập, tiếng Trung của cô ấy càng lưu loát hơn.
1738|我爸爸在一家工厂工作。|Bố tôi làm việc tại một nhà máy.
1739|我哥哥是一名工程师。|Anh trai tôi là một kỹ sư.
1740|做这件事需要花不少工夫。|Làm việc này cần tốn khá nhiều công sức.
1741|这些都是修理汽车的工具。|Đây đều là những dụng cụ sửa ô tô.
1742|这个城市的工业发展得很快。|Công nghiệp của thành phố này phát triển rất nhanh.
1743|公司每个月十号发工资。|Công ty trả lương vào ngày mười hằng tháng.
1744|学校明天公布考试成绩。|Ngày mai nhà trường sẽ công bố kết quả thi.
1745|请不要在公共场所大声说话。|Xin đừng nói lớn tiếng ở nơi công cộng.
1746|比赛结果已经公开了。|Kết quả cuộc thi đã được công khai.
1747|每个公民都应该遵守法律。|Mỗi công dân đều nên tuân thủ pháp luật.
1748|他毕业以后想当公务员。|Sau khi tốt nghiệp anh ấy muốn làm công chức.
1749|他从小就喜欢练中国功夫。|Từ nhỏ anh ấy đã thích luyện võ Trung Quốc.
1750|我做完功课以后才出去玩。|Tôi làm xong bài học rồi mới ra ngoài chơi.
1751|这个手机有很多新功能。|Điện thoại này có nhiều chức năng mới.
1752|保护环境是我们共同的责任。|Bảo vệ môi trường là trách nhiệm chung của chúng ta.
1753|我们班共有三十二名学生。|Lớp chúng tôi có tổng cộng ba mươi hai học sinh.
1754|那位姑娘正在等公交车。|Cô gái đó đang chờ xe buýt.
1755|这座古城有很长的历史。|Thành cổ này có lịch sử lâu đời.
1756|古代的人没有手机和电脑。|Người thời cổ đại không có điện thoại và máy tính.
1757|离开故乡以后，他经常想家。|Sau khi rời quê hương, anh ấy thường nhớ nhà.
1758|墙上挂着一张中国地图。|Trên tường treo một tấm bản đồ Trung Quốc.
1759|我和他的关系一直很好。|Mối quan hệ giữa tôi và anh ấy luôn rất tốt.
1760|越来越多的人开始关注健康问题。|Ngày càng nhiều người bắt đầu quan tâm đến vấn đề sức khỏe.
1761|老师让我们仔细观察这个现象。|Giáo viên yêu cầu chúng tôi quan sát hiện tượng này thật kỹ.
1762|很多人在网上观看这场比赛。|Rất nhiều người xem trận đấu này trên mạng.
1763|年轻人的生活观念发生了变化。|Quan niệm sống của người trẻ đã thay đổi.
1764|表演结束后，观众都站起来鼓掌。|Sau khi buổi biểu diễn kết thúc, khán giả đều đứng lên vỗ tay.
1765|这件事由王老师管。|Việc này do thầy Vương phụ trách.
1766|她负责管理这个部门。|Cô ấy phụ trách quản lý bộ phận này.
1767|早上的太阳光很温暖。|Ánh nắng buổi sáng rất ấm áp.
1768|我们对未来充满光明的希望。|Chúng tôi tràn đầy hy vọng tươi sáng về tương lai.
1769|我每天早上都听新闻广播。|Mỗi sáng tôi đều nghe chương trình phát thanh tin tức.
1770|这个产品受到广大顾客的欢迎。|Sản phẩm này được đông đảo khách hàng yêu thích.
1771|学校规定上课不能使用手机。|Nhà trường quy định không được dùng điện thoại trong giờ học.
1772|我们应该规范自己的行为。|Chúng ta nên điều chỉnh hành vi của mình theo đúng chuẩn mực.
1773|今年国内旅游的人很多。|Năm nay có rất nhiều người du lịch trong nước.
1774|国庆期间很多人出去旅游。|Trong dịp Quốc khánh, rất nhiều người đi du lịch.
1775|天气预报说会下雨，下午果然下雨了。|Dự báo thời tiết nói sẽ mưa, buổi chiều quả nhiên trời mưa.
1776|我想喝一杯橙子果汁。|Tôi muốn uống một cốc nước cam.
1777|学习汉语是一个长期的过程。|Học tiếng Trung là một quá trình lâu dài.
1778|听完这个笑话，大家都哈哈大笑。|Nghe xong câu chuyện cười này, mọi người đều cười ha ha.
1779|我们下飞机以后先过海关。|Sau khi xuống máy bay, chúng tôi làm thủ tục hải quan trước.
1780|妹妹很害怕一个人待在家里。|Em gái rất sợ ở nhà một mình.
1781|请在第一行写上你的名字。|Hãy viết tên của bạn ở dòng đầu tiên.
1782|考试前你应该好好复习。|Trước kỳ thi bạn nên ôn tập thật tốt.
1783|孩子们对外面的世界很好奇。|Bọn trẻ rất tò mò về thế giới bên ngoài.
1784|这个盒子的盖子合不上。|Nắp của chiếc hộp này không đóng lại được.
1785|他通过合法的方法解决了问题。|Anh ấy giải quyết vấn đề bằng phương pháp hợp pháp.
1786|只有考试合格才能毕业。|Chỉ khi thi đạt yêu cầu mới có thể tốt nghiệp.
1787|我觉得这个价格很合理。|Tôi thấy mức giá này rất hợp lý.
1788|两家公司决定继续合作。|Hai công ty quyết định tiếp tục hợp tác.
1789|大家都希望世界和平。|Mọi người đều mong thế giới hòa bình.
1790|我每天早上喜欢喝一杯红茶。|Mỗi sáng tôi thích uống một cốc trà đen.
1791|桌子上有一瓶红酒。|Trên bàn có một chai rượu vang đỏ.
1792|做事情以前要想一想后果。|Trước khi làm việc gì nên suy nghĩ về hậu quả.
1793|我的座位在教室后面。|Chỗ ngồi của tôi ở phía sau lớp học.
1794|我计划后年去中国留学。|Tôi dự định năm sau nữa sẽ sang Trung Quốc du học.
1795|现在人们可以通过互联网学习。|Ngày nay mọi người có thể học thông qua Internet.
1796|同学之间应该互相帮助。|Các bạn học nên giúp đỡ lẫn nhau.
1797|天气好的时候我们去湖上划船。|Khi thời tiết đẹp chúng tôi đi chèo thuyền trên hồ.
1798|这个城市生活着很多海外华人。|Thành phố này có nhiều người Hoa ở nước ngoài sinh sống.
1799|这个城市的交通越来越现代化。|Giao thông của thành phố này ngày càng hiện đại hóa.
1800|学校今晚有一场话剧表演。|Tối nay trường có một buổi biểu diễn kịch nói.
1801|大家正在讨论一个有意思的话题。|Mọi người đang thảo luận một chủ đề thú vị.
1802|孩子们度过了一个欢乐的周末。|Bọn trẻ đã trải qua một cuối tuần vui vẻ.
1803|她手上戴着一个银环。|Cô ấy đeo một chiếc vòng bạc trên tay.
1804|我们应该选择环保的生活方式。|Chúng ta nên lựa chọn lối sống thân thiện với môi trường.
1805|这里的学习环境很好。|Môi trường học tập ở đây rất tốt.
1806|今天下午三点有一个重要会议。|Ba giờ chiều nay có một cuộc họp quan trọng.
1807|我是这个体育馆的会员。|Tôi là thành viên của nhà thi đấu này.
1808|这条鱼还活着。|Con cá này vẫn còn sống.
1809|做饭的时候要小心火。|Khi nấu ăn phải cẩn thận với lửa.
1810|工人正在检查这台机器。|Công nhân đang kiểm tra chiếc máy này.
1811|她积极参加学校的各种活动。|Cô ấy tích cực tham gia các hoạt động của trường.
1812|我已经了解了基本情况。|Tôi đã hiểu tình hình cơ bản.
1813|这个问题基本上已经解决了。|Vấn đề này về cơ bản đã được giải quyết.
1814|学好发音是学习汉语的重要基础。|Học tốt phát âm là nền tảng quan trọng khi học tiếng Trung.
1815|幸好医生及时赶到了。|May mà bác sĩ đã đến kịp thời.
1816|今天的天气好极了。|Thời tiết hôm nay tuyệt vời vô cùng.
1817|这是我们集体讨论后的决定。|Đây là quyết định sau khi tập thể chúng tôi thảo luận.
1818|上课的时候要集中注意力。|Trong giờ học phải tập trung chú ý.
1819|请帮我计算一下总费用。|Hãy giúp tôi tính tổng chi phí.
1820|我把每天的学习情况记录下来。|Tôi ghi lại tình hình học tập mỗi ngày.
1821|那位记者正在采访运动员。|Phóng viên đó đang phỏng vấn vận động viên.
1822|他打破了学校的跑步纪录。|Anh ấy đã phá kỷ lục chạy của trường.
1823|我们拍了一张照片纪念这次旅行。|Chúng tôi chụp một bức ảnh để kỷ niệm chuyến đi này.
1824|这家公司需要很多技术人员。|Công ty này cần nhiều nhân viên kỹ thuật.
1825|休息十分钟以后我们继续学习。|Sau khi nghỉ mười phút chúng tôi tiếp tục học.
1826|这些水果会被加工成果汁。|Những loại trái cây này sẽ được chế biến thành nước ép.
1827|我们需要加快工作速度。|Chúng ta cần tăng nhanh tốc độ làm việc.
1828|学校决定加强安全管理。|Nhà trường quyết định tăng cường quản lý an toàn.
1829|新房子里的家具都是新的。|Đồ nội thất trong căn nhà mới đều là đồ mới.
1830|医院通知了病人的家属。|Bệnh viện đã thông báo cho người nhà của bệnh nhân.
1831|我的家乡是一个美丽的小城市。|Quê hương tôi là một thành phố nhỏ xinh đẹp.
1832|这件衣服的价格有点儿高。|Giá của bộ quần áo này hơi cao.
1833|我想问一下这台电脑的价钱。|Tôi muốn hỏi giá của chiếc máy tính này.
1834|这本书很有学习价值。|Quyển sách này có giá trị học tập rất lớn.
1835|机场里停着三架飞机。|Trong sân bay đang có ba chiếc máy bay.
1836|只要坚持练习，你一定会进步。|Chỉ cần kiên trì luyện tập, bạn nhất định sẽ tiến bộ.
1837|他坚决不同意这个计划。|Anh ấy kiên quyết không đồng ý với kế hoạch này.
1838|遇到困难的时候我们要坚强。|Khi gặp khó khăn chúng ta phải mạnh mẽ.
1839|这个问题其实很简单。|Vấn đề này thực ra rất đơn giản.
1840|这里的景色简直太美了。|Phong cảnh ở đây thật sự quá đẹp.
1841|他们准备在这里建一所新学校。|Họ chuẩn bị xây một ngôi trường mới ở đây.
1842|这座大桥去年已经建成了。|Cây cầu lớn này đã được xây xong năm ngoái.
1843|我们应该建立良好的学习习惯。|Chúng ta nên xây dựng thói quen học tập tốt.
1844|政府正在建设新的公路。|Chính phủ đang xây dựng một tuyến đường mới.
1845|老师给了我很多学习建议。|Giáo viên đã cho tôi nhiều lời khuyên học tập.
1846|会议开了将近三个小时。|Cuộc họp kéo dài gần ba tiếng.
1847|我希望将来能成为一名老师。|Tôi hy vọng trong tương lai có thể trở thành giáo viên.
1848|新学期开始前需要先交费。|Trước khi học kỳ mới bắt đầu cần đóng phí trước.
1849|路口有一位交警在指挥交通。|Ở ngã tư có một cảnh sát giao thông đang điều khiển giao thông.
1850|我经常和中国朋友交流学习经验。|Tôi thường trao đổi kinh nghiệm học tập với bạn Trung Quốc.
1851|和别人交往时应该互相尊重。|Khi giao tiếp với người khác nên tôn trọng lẫn nhau.
1852|这笔交易已经完成了。|Giao dịch này đã hoàn thành.
1853|今天的气温较昨天低。|Nhiệt độ hôm nay thấp hơn hôm qua.
1854|老师给我们发了新的汉语教材。|Giáo viên phát cho chúng tôi giáo trình tiếng Trung mới.
1855|教练正在教队员怎么训练。|Huấn luyện viên đang dạy các thành viên trong đội cách luyện tập.
1856|这张桌子很结实，可以用很多年。|Chiếc bàn này rất chắc chắn, có thể dùng nhiều năm.
1857|酒店工作人员正在接待客人。|Nhân viên khách sạn đang tiếp đón khách.
1858|考试时间越来越接近了。|Thời gian thi ngày càng đến gần.
1859|我们应该节约用水。|Chúng ta nên tiết kiệm nước.
1860|学习语言要把听和说结合起来。|Học ngôn ngữ phải kết hợp nghe và nói.
1861|他们准备明年结婚。|Họ chuẩn bị kết hôn vào năm sau.
1862|会议下午五点结束。|Cuộc họp kết thúc lúc năm giờ chiều.
1863|我们终于找到了解决这个问题的方法。|Cuối cùng chúng tôi đã tìm ra cách giải quyết vấn đề này.
1864|请帮我解开这个袋子。|Hãy giúp tôi mở chiếc túi này.
1865|她戴着一条金项链。|Cô ấy đang đeo một chiếc dây chuyền vàng.
1866|他在比赛中获得了一块金牌。|Anh ấy giành được một huy chương vàng trong cuộc thi.
1867|今天仅有十名学生来上课。|Hôm nay chỉ có mười học sinh đến lớp.
1868|我仅仅问了他一个问题。|Tôi chỉ hỏi anh ấy một câu hỏi.
1869|考试的时候请尽量认真一点儿。|Khi thi hãy cố gắng cẩn thận hết mức có thể.
1870|请把瓶盖拧紧。|Hãy vặn chặt nắp chai.
1871|发生紧急情况时请马上报警。|Khi xảy ra tình huống khẩn cấp hãy lập tức báo cảnh sát.
1872|明天要考试了，我有一点儿紧张。|Ngày mai thi rồi, tôi hơi căng thẳng.
1873|经过一个学期的学习，他进步很大。|Sau một học kỳ học tập, anh ấy tiến bộ rất nhiều.
1874|我们需要进一步了解情况。|Chúng ta cần tìm hiểu tình hình thêm một bước nữa.
1875|这个项目目前进展顺利。|Dự án này hiện đang tiến triển thuận lợi.
1876|我近期没有出国的计划。|Gần đây tôi không có kế hoạch ra nước ngoài.
1877|我的爷爷非常喜欢听京剧。|Ông tôi rất thích nghe Kinh kịch.
1878|旅游业对当地经济很重要。|Ngành du lịch rất quan trọng đối với kinh tế địa phương.
1879|这次旅行是一次难忘的经历。|Chuyến đi này là một trải nghiệm khó quên.
1880|他有很多教学经验。|Anh ấy có rất nhiều kinh nghiệm giảng dạy.
1881|他们一家经营着一家小饭馆。|Gia đình họ điều hành một nhà hàng nhỏ.
1882|昨天的足球比赛非常精彩。|Trận bóng đá hôm qua vô cùng精彩.
1883|我们应该学习他的认真精神。|Chúng ta nên học tinh thần nghiêm túc của anh ấy.
1884|他今天看起来很精神。|Hôm nay anh ấy trông rất khỏe khoắn.
1885|山上的景色非常漂亮。|Phong cảnh trên núi rất đẹp.
1886|我向警察问了去车站的路。|Tôi đã hỏi cảnh sát đường đến nhà ga.
1887|夜里四周非常静。|Ban đêm xung quanh rất yên tĩnh.
1888|我已经很久没有见到他了。|Tôi đã lâu rồi không gặp anh ấy.
1889|这台旧电脑还能使用。|Chiếc máy tính cũ này vẫn còn dùng được.
1890|消防员救出了房子里的人。|Lính cứu hỏa đã cứu những người trong căn nhà ra ngoài.
1891|我想找的人就是他。|Người tôi muốn tìm chính là anh ấy.
1892|学校为学生提供就业帮助。|Nhà trường cung cấp hỗ trợ việc làm cho sinh viên.
1893|学校下个月举办运动会。|Tháng sau trường sẽ tổ chức hội thao.
1894|请告诉我具体的时间和地点。|Hãy nói cho tôi thời gian và địa điểm cụ thể.
1895|这种植物具有很高的经济价值。|Loại thực vật này có giá trị kinh tế rất cao.
1896|我们晚上去剧场看表演。|Buổi tối chúng tôi đến nhà hát xem biểu diễn.
1897|据说这家饭馆已经开了三十年。|Nghe nói nhà hàng này đã mở được ba mươi năm.
1898|我决定明年去中国留学。|Tôi quyết định năm sau sang Trung Quốc du học.
1899|我们队已经进入了决赛。|Đội chúng tôi đã vào vòng chung kết.
1900|我下定决心每天学习两个小时。|Tôi quyết tâm học hai tiếng mỗi ngày.
1901|这个消息绝对是真的。|Tin này tuyệt đối là thật.
"""


# ==========================================================
# CHUẨN HÓA TỪ MỤC TIÊU
# ==========================================================

def normalize_target(raw_word):
    word = (raw_word or "").strip()

    # Ví dụ:
    # 化（现代化） -> 现代化
    match = re.search(r"（([^（）]+)）", word)

    if match:
        return match.group(1).strip()

    # Ví dụ:
    # …极了 -> 极了
    word = word.replace("…", "").strip()

    # Phòng trường hợp dạng từ có số cuối
    # ví dụ 面1 -> 面
    word = re.sub(r"\d+$", "", word)

    return word.strip()


# ==========================================================
# ĐỌC EXAMPLES
# ==========================================================

def parse_examples():

    fixes = {}

    for line_number, line in enumerate(
        EXAMPLES.strip().splitlines(),
        start=1
    ):

        line = line.strip()

        if not line:
            continue

        parts = line.split("|")

        if len(parts) != 3:

            raise ValueError(
                "\nDÒNG EXAMPLES SAI ĐỊNH DẠNG\n"
                f"Dòng: {line_number}\n"
                f"Nội dung: {line}"
            )

        word_id = int(parts[0].strip())

        chinese = parts[1].strip()
        vietnamese = parts[2].strip()

        if word_id in fixes:

            raise ValueError(
                f"Trùng MaTuVung: {word_id}"
            )

        if not chinese:

            raise ValueError(
                f"Câu Trung rỗng: {word_id}"
            )

        if not vietnamese:

            raise ValueError(
                f"Câu Việt rỗng: {word_id}"
            )

        fixes[word_id] = (
            chinese,
            vietnamese
        )

    return fixes


# ==========================================================
# MAIN
# ==========================================================

def main():

    # ------------------------------------------------------
    # 1. Kiểm tra SOURCE
    # ------------------------------------------------------

    if not SOURCE.exists():

        raise FileNotFoundError(
            "\nKhông tìm thấy:\n"
            f"{SOURCE}"
        )

    # ------------------------------------------------------
    # 2. Parse 200 câu
    # ------------------------------------------------------

    fixes = parse_examples()

    expected_ids = set(
        range(1702, 1902)
    )

    actual_ids = set(
        fixes.keys()
    )

    missing_ids = (
        expected_ids - actual_ids
    )

    extra_ids = (
        actual_ids - expected_ids
    )

    if missing_ids or extra_ids:

        print()
        print("Mã còn thiếu:")
        print(sorted(missing_ids))

        print()
        print("Mã bị thừa:")
        print(sorted(extra_ids))

        raise ValueError(
            "\nBATCH 2 KHÔNG ĐÚNG "
            "PHẠM VI 1702 -> 1901."
        )

    if len(fixes) != 200:

        raise ValueError(
            f"\nCần 200 câu, "
            f"hiện có {len(fixes)}."
        )

    # ------------------------------------------------------
    # 3. Đọc preview hiện tại
    # ------------------------------------------------------

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        fields = reader.fieldnames

        rows = list(reader)

    if not fields:

        raise ValueError(
            "Không đọc được header CSV."
        )

    required_columns = {
        "MaTuVung",
        "ChuHan",
        "ViDuTiengTrung",
        "ViDuTiengViet",
        "LoaiCau",
        "TrangThaiImport",
    }

    missing_columns = (
        required_columns - set(fields)
    )

    if missing_columns:

        raise ValueError(
            "\nCSV thiếu cột:\n"
            f"{sorted(missing_columns)}"
        )

    # ------------------------------------------------------
    # 4. Index CSV
    # ------------------------------------------------------

    csv_by_id = {}

    for row in rows:

        word_id = int(
            row["MaTuVung"]
        )

        if word_id in csv_by_id:

            raise ValueError(
                f"CSV trùng MaTuVung: {word_id}"
            )

        csv_by_id[word_id] = row

    # ------------------------------------------------------
    # 5. Kiểm tra 200 mã tồn tại
    # ------------------------------------------------------

    not_found = (
        expected_ids - set(csv_by_id)
    )

    if not_found:

        raise ValueError(
            "\nKhông tìm thấy trong CSV:\n"
            f"{sorted(not_found)}"
        )

    # ------------------------------------------------------
    # 6. Chỉ sửa NEED_REVIEW
    # ------------------------------------------------------

    invalid_status = []

    for word_id in sorted(expected_ids):

        row = csv_by_id[word_id]

        status = (
            row["TrangThaiImport"]
            or ""
        ).strip()

        if status != "NEED_REVIEW":

            invalid_status.append(
                (
                    word_id,
                    row["ChuHan"],
                    status
                )
            )

    if invalid_status:

        print()
        print(
            "Các từ không còn NEED_REVIEW:"
        )

        for item in invalid_status:
            print(item)

        raise ValueError(
            "\nDỪNG ĐỂ TRÁNH "
            "GHI ĐÈ DỮ LIỆU."
        )

    # ------------------------------------------------------
    # 7. Kiểm tra câu Trung chứa từ mục tiêu
    # ------------------------------------------------------

    target_errors = []

    for word_id in sorted(expected_ids):

        row = csv_by_id[word_id]

        chinese, vietnamese = (
            fixes[word_id]
        )

        target = normalize_target(
            row["ChuHan"]
        )

        if target not in chinese:

            target_errors.append(
                (
                    word_id,
                    row["ChuHan"],
                    target,
                    chinese
                )
            )

    if target_errors:

        print()
        print(
            "CÂU KHÔNG CHỨA TỪ MỤC TIÊU:"
        )

        for (
            word_id,
            chu_han,
            target,
            chinese
        ) in target_errors:

            print(
                f"{word_id} | "
                f"{chu_han} | "
                f"target={target} | "
                f"{chinese}"
            )

        raise ValueError(
            "\nCHƯA GHI FILE OUTPUT."
        )

    # ------------------------------------------------------
    # 8. Cập nhật Batch 2
    # ------------------------------------------------------

    updated = []

    for word_id in sorted(expected_ids):

        row = csv_by_id[word_id]

        chinese, vietnamese = (
            fixes[word_id]
        )

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese

        row["LoaiCau"] = "REAL"

        row["TrangThaiImport"] = "READY"

        updated.append(word_id)

    if len(updated) != 200:

        raise ValueError(
            f"Dự kiến 200, "
            f"thực tế {len(updated)}."
        )

    # ------------------------------------------------------
    # 9. Thống kê
    # ------------------------------------------------------

    ready = sum(
        1
        for row in rows
        if row["TrangThaiImport"] == "READY"
    )

    remaining = sum(
        1
        for row in rows
        if row["TrangThaiImport"] == "NEED_REVIEW"
    )

    # Sau Batch 1:
    # READY = 201
    # NEED_REVIEW = 760
    #
    # Sau Batch 2:
    # READY = 401
    # NEED_REVIEW = 560

    if ready != 401:

        raise ValueError(
            "\nREADY KHÔNG ĐÚNG.\n"
            "Dự kiến: 401\n"
            f"Thực tế: {ready}\n"
            "CHƯA GHI OUTPUT."
        )

    if remaining != 560:

        raise ValueError(
            "\nNEED_REVIEW KHÔNG ĐÚNG.\n"
            "Dự kiến: 560\n"
            f"Thực tế: {remaining}\n"
            "CHƯA GHI OUTPUT."
        )

    # ------------------------------------------------------
    # 10. Ghi output
    # ------------------------------------------------------

    with OUTPUT.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(rows)

    # ------------------------------------------------------
    # 11. Kết quả
    # ------------------------------------------------------

    print()
    print("=" * 60)
    print("HSK3 - BATCH 2")
    print(
        f"Đã sửa thêm: "
        f"{len(updated)} câu"
    )
    print(
        f"Tổng READY trong CSV: "
        f"{ready}"
    )
    print(
        f"Còn NEED_REVIEW: "
        f"{remaining}"
    )
    print()
    print(
        f"File mới: {OUTPUT}"
    )
    print()
    print(
        "CHƯA THAY ĐỔI SQL SERVER."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()