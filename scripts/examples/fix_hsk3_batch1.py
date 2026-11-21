
import csv
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
SOURCE = DATA_DIR / "offline_preview_hsk3.csv"
OUTPUT = DATA_DIR / "offline_preview_hsk3_batch1.csv"

EXAMPLES = """
1502|她经常帮助老人，是一个很有爱心的人。|Cô ấy thường giúp đỡ người già, là một người rất giàu lòng nhân ái.
1503|老师已经安排好了明天的活动。|Giáo viên đã sắp xếp xong hoạt động ngày mai.
1504|我昨天在电脑上安装了一个新软件。|Hôm qua tôi cài một phần mềm mới trên máy tính.
1505|请按一下这个按钮。|Hãy nhấn nút này một cái.
1506|请按照老师的要求完成作业。|Hãy hoàn thành bài tập theo yêu cầu của giáo viên.
1507|请把书放在桌子上。|Hãy đặt sách lên bàn.
1508|我买了一把新椅子。|Tôi mua một chiếc ghế mới.
1509|我没有把握通过这次考试。|Tôi không chắc mình sẽ vượt qua kỳ thi lần này.
1510|妈妈买了一棵新鲜的白菜。|Mẹ mua một cây cải thảo tươi.
1511|我们班级一共有三十名学生。|Lớp chúng tôi có tổng cộng ba mươi học sinh.
1512|请帮我把箱子搬到楼上。|Hãy giúp tôi chuyển chiếc thùng lên tầng trên.
1513|下个月我们准备搬家。|Tháng sau chúng tôi dự định chuyển nhà.
1514|爸爸用一块木板做了一张桌子。|Bố dùng một tấm ván gỗ làm một chiếc bàn.
1515|我明天去银行办理手续。|Ngày mai tôi đến ngân hàng làm thủ tục.
1516|天气冷了，出门要注意保暖。|Trời lạnh rồi, ra ngoài phải chú ý giữ ấm.
1517|小区门口有一位保安。|Ở cổng khu dân cư có một nhân viên bảo vệ.
1518|我们应该保持教室干净。|Chúng ta nên giữ lớp học sạch sẽ.
1519|写完文件以后记得保存。|Sau khi viết xong tài liệu nhớ lưu lại.
1520|我们要一起保护环境。|Chúng ta phải cùng nhau bảo vệ môi trường.
1521|我想保留这张旧照片。|Tôi muốn giữ lại bức ảnh cũ này.
1522|出国旅游前最好买一份保险。|Trước khi đi du lịch nước ngoài tốt nhất nên mua bảo hiểm.
1523|我保证明天不会迟到。|Tôi bảo đảm ngày mai sẽ không đến muộn.
1524|爷爷每天早上都看报。|Ông đọc báo mỗi sáng.
1525|新生今天要到学校报到。|Hôm nay sinh viên mới phải đến trường đăng ký nhập học.
1526|电视正在报道昨天的比赛。|Truyền hình đang đưa tin về trận đấu hôm qua.
1527|他正在准备一份工作报告。|Anh ấy đang chuẩn bị một bản báo cáo công việc.
1528|弟弟每天背着书包去学校。|Em trai mỗi ngày đeo cặp sách đến trường.
1529|中国北部冬天比较冷。|Miền bắc Trung Quốc mùa đông tương đối lạnh.
1530|他站在我的背后。|Anh ấy đứng phía sau lưng tôi.
1531|我的手机被弟弟拿走了。|Điện thoại của tôi bị em trai lấy đi.
1532|天气冷了，晚上要盖好被子。|Trời lạnh rồi, buổi tối phải đắp chăn cẩn thận.
1533|我本来想去公园，可是下雨了。|Ban đầu tôi định đi công viên, nhưng trời mưa.
1534|他有修理电脑的本领。|Anh ấy có kỹ năng sửa máy tính.
1535|你真有本事，自己修好了电脑。|Bạn thật giỏi, tự sửa được máy tính.
1536|今天的天气比较凉快。|Thời tiết hôm nay tương đối mát mẻ.
1537|这个班男女学生的比例差不多。|Tỷ lệ học sinh nam và nữ của lớp này gần bằng nhau.
1538|明天下午我们有一场篮球比赛。|Chiều mai chúng tôi có một trận bóng rổ.
1539|只要认真练习，进步是必然的。|Chỉ cần luyện tập nghiêm túc, tiến bộ là điều tất yếu.
1540|没有必要为这件小事生气。|Không cần thiết phải tức giận vì chuyện nhỏ này.
1541|这几年城市发生了很大的变化。|Mấy năm nay thành phố đã có những thay đổi lớn.
1542|雨水可以变为河里的水。|Nước mưa có thể trở thành nước trong sông.
1543|请给这篇文章写一个标题。|Hãy đặt một tiêu đề cho bài viết này.
1544|这家饭馆的卫生标准很高。|Tiêu chuẩn vệ sinh của nhà hàng này rất cao.
1545|我不知道怎么表达自己的想法。|Tôi không biết diễn đạt suy nghĩ của mình thế nào.
1546|请先把这张表格填好。|Hãy điền xong biểu mẫu này trước.
1547|桌子的表面很干净。|Bề mặt chiếc bàn rất sạch.
1548|他的回答表明他已经明白了。|Câu trả lời của anh ấy cho thấy anh ấy đã hiểu.
1549|她今天在比赛中的表现很好。|Hôm nay cô ấy thể hiện rất tốt trong cuộc thi.
1550|孩子们正在舞台上表演节目。|Bọn trẻ đang biểu diễn tiết mục trên sân khấu.
1551|我并不觉得这个问题很难。|Tôi hoàn toàn không thấy vấn đề này khó.
1552|这本书很有意思，并且不贵。|Quyển sách này rất thú vị, hơn nữa không đắt.
1553|这个节目每天晚上八点播出。|Chương trình này phát sóng lúc tám giờ tối mỗi ngày.
1554|老师正在播放一段中文录音。|Giáo viên đang phát một đoạn ghi âm tiếng Trung.
1555|你不必担心，我会帮你的。|Bạn không cần lo, tôi sẽ giúp bạn.
1556|通过不断练习，他的汉语进步很快。|Thông qua luyện tập không ngừng, tiếng Trung của anh ấy tiến bộ rất nhanh.
1557|不论天气怎么样，我都要去上课。|Bất kể thời tiết thế nào, tôi vẫn phải đi học.
1558|这件衣服破了，妈妈帮我补好了。|Bộ quần áo này bị rách, mẹ đã vá giúp tôi.
1559|你还有什么需要补充的吗？|Bạn còn điều gì cần bổ sung không?
1560|听到这个消息，我心里有些不安。|Nghe tin này, trong lòng tôi hơi bất an.
1561|雨下得太大，我们不得不回家。|Mưa quá lớn, chúng tôi đành phải về nhà.
1562|他不光会说汉语，还会说英语。|Anh ấy không chỉ biết nói tiếng Trung mà còn biết nói tiếng Anh.
1563|她不仅学习好，而且很乐于助人。|Cô ấy không những học giỏi mà còn rất thích giúp đỡ người khác.
1564|妈妈买了一块蓝色的布。|Mẹ mua một tấm vải màu xanh.
1565|他向前走了几步。|Anh ấy bước về phía trước vài bước.
1566|昨天我看了一部中国电影。|Hôm qua tôi xem một bộ phim Trung Quốc.
1567|我在公司的销售部门工作。|Tôi làm việc ở bộ phận kinh doanh của công ty.
1568|部长今天上午参加了会议。|Bộ trưởng tham dự cuộc họp sáng nay.
1569|他很有音乐才能。|Anh ấy rất có tài năng âm nhạc.
1570|学校采取了新的安全措施。|Nhà trường đã áp dụng các biện pháp an toàn mới.
1571|我们决定采用这个学习方法。|Chúng tôi quyết định áp dụng phương pháp học này.
1572|妹妹喜欢穿彩色的衣服。|Em gái thích mặc quần áo nhiều màu sắc.
1573|我曾经在北京学习过一年。|Tôi từng học ở Bắc Kinh một năm.
1574|这件事产生了很大的影响。|Việc này đã tạo ra ảnh hưởng rất lớn.
1575|我一直想去看看中国的长城。|Tôi luôn muốn đến thăm Vạn Lý Trường Thành của Trung Quốc.
1576|每个人都有自己的长处。|Mỗi người đều có điểm mạnh riêng.
1577|长期熬夜对身体不好。|Thức khuya trong thời gian dài không tốt cho sức khỏe.
1578|我爸爸在一家工厂工作。|Bố tôi làm việc ở một nhà máy.
1579|在正式场合应该穿得整齐一点。|Trong dịp trang trọng nên ăn mặc chỉnh tề một chút.
1580|图书馆是一个安静的学习场所。|Thư viện là một nơi học tập yên tĩnh.
1581|今天的比赛超级精彩。|Trận đấu hôm nay cực kỳ hấp dẫn.
1582|请朝前走，然后向左转。|Hãy đi về phía trước, sau đó rẽ trái.
1583|外面太吵了，我没办法学习。|Bên ngoài quá ồn, tôi không thể học được.
1584|他们因为一点小事吵架了。|Họ cãi nhau vì một chuyện nhỏ.
1585|我买了一件白色的衬衫。|Tôi mua một chiếc áo sơ mi trắng.
1586|这件蓝色衬衣很适合你。|Chiếc áo sơ mi xanh này rất hợp với bạn.
1587|这座城市被称为花城。|Thành phố này được gọi là thành phố hoa.
1588|经过努力，他终于成功了。|Sau khi nỗ lực, cuối cùng anh ấy đã thành công.
1589|老师对我们的学习成果很满意。|Giáo viên rất hài lòng với thành quả học tập của chúng tôi.
1590|她在科学研究方面取得了很大成就。|Cô ấy đạt được thành tựu lớn trong nghiên cứu khoa học.
1591|这家公司成立于十年前。|Công ty này được thành lập mười năm trước.
1592|这些苹果已经成熟了。|Những quả táo này đã chín.
1593|我们小组一共有六名成员。|Nhóm chúng tôi có tổng cộng sáu thành viên.
1594|孩子们在快乐地成长。|Bọn trẻ đang lớn lên vui vẻ.
1595|这座古城有几百年的历史。|Thành cổ này có lịch sử vài trăm năm.
1596|我很喜欢这座安静的城市。|Tôi rất thích thành phố yên tĩnh này.
1597|他的汉语已经达到很高的程度。|Tiếng Trung của anh ấy đã đạt trình độ rất cao.
1598|大雨持续了三个小时。|Mưa lớn kéo dài ba tiếng đồng hồ.
1599|房间里充满了花香。|Căn phòng tràn ngập hương hoa.
1600|这道题做错了，请重做一遍。|Bài này làm sai rồi, hãy làm lại một lần.
1601|我第一次见他是在今年年初。|Lần đầu tôi gặp anh ấy là vào đầu năm nay.
"""
EXAMPLES += """
1602|我妹妹今年上初一。|Em gái tôi năm nay học lớp 7.
1603|我们已经有了一个初步的计划。|Chúng tôi đã có một kế hoạch sơ bộ.
1604|这是一本初级汉语教材。|Đây là một giáo trình tiếng Trung sơ cấp.
1605|我弟弟正在上初中。|Em trai tôi đang học trung học cơ sở.
1606|除了汉语，我还会说英语。|Ngoài tiếng Trung, tôi còn biết nói tiếng Anh.
1607|这个问题需要马上处理。|Vấn đề này cần được xử lý ngay.
1608|请把这个消息传给大家。|Hãy truyền tin này cho mọi người.
1609|互联网让信息传播得更快。|Internet làm cho thông tin lan truyền nhanh hơn.
1610|教室外面传来了音乐声。|Từ bên ngoài lớp học truyền đến tiếng nhạc.
1611|这个村子里有一个古老的传说。|Trong ngôi làng này có một truyền thuyết cổ.
1612|公司鼓励年轻人不断创新。|Công ty khuyến khích người trẻ không ngừng đổi mới.
1613|大学毕业后，他决定创业。|Sau khi tốt nghiệp đại học, anh ấy quyết định khởi nghiệp.
1614|我们要努力创造更好的生活。|Chúng ta phải cố gắng tạo ra cuộc sống tốt đẹp hơn.
1615|这位作家正在创作一部新小说。|Nhà văn này đang sáng tác một cuốn tiểu thuyết mới.
1616|我从来没有去过那里。|Tôi chưa bao giờ đến đó.
1617|从前这里是一个小村子。|Trước đây nơi này là một ngôi làng nhỏ.
1618|她一直从事教育工作。|Cô ấy luôn làm công việc giáo dục.
1619|我爷爷住在一个安静的小村里。|Ông tôi sống trong một ngôi làng nhỏ yên tĩnh.
1620|我想把这些钱存进银行。|Tôi muốn gửi số tiền này vào ngân hàng.
1621|这个问题还存在。|Vấn đề này vẫn còn tồn tại.
1622|我发现了自己的错误。|Tôi đã phát hiện ra lỗi của mình.
1623|今天气温达到三十五度。|Hôm nay nhiệt độ đạt đến 35 độ.
1624|弟弟不小心打破了杯子。|Em trai không cẩn thận làm vỡ chiếc cốc.
1625|我想向你打听一个人的情况。|Tôi muốn hỏi thăm bạn về tình hình của một người.
1626|他大概十分钟以后到。|Có lẽ anh ấy sẽ đến sau khoảng mười phút.
1627|我明天要去中国大使馆。|Ngày mai tôi phải đến Đại sứ quán Trung Quốc.
1628|从这里到机场大约需要一个小时。|Từ đây đến sân bay mất khoảng một tiếng.
1629|大夫让我多休息。|Bác sĩ bảo tôi nghỉ ngơi nhiều hơn.
1630|今天我代老师通知大家一件事。|Hôm nay tôi thay giáo viên thông báo cho mọi người một việc.
1631|他代表我们班参加比赛。|Anh ấy đại diện lớp chúng tôi tham gia cuộc thi.
1632|代表团明天上午到达北京。|Đoàn đại biểu sẽ đến Bắc Kinh vào sáng mai.
1633|旅游业带动了当地经济的发展。|Ngành du lịch đã thúc đẩy sự phát triển kinh tế địa phương.
1634|老师带领我们参观博物馆。|Giáo viên dẫn chúng tôi tham quan bảo tàng.
1635|我们今天学习第三单元。|Hôm nay chúng tôi học bài thứ ba.
1636|当初我并不知道这件事。|Ban đầu tôi không hề biết việc này.
1637|我们品尝了很多当地的美食。|Chúng tôi đã thưởng thức nhiều món ăn địa phương.
1638|你当然可以和我们一起去。|Tất nhiên bạn có thể đi cùng chúng tôi.
1639|这些学生当中，他的汉语最好。|Trong số những học sinh này, tiếng Trung của anh ấy tốt nhất.
1640|切水果的时候要小心用刀。|Khi cắt trái cây phải cẩn thận khi dùng dao.
1641|这部电影的导演很有名。|Đạo diễn của bộ phim này rất nổi tiếng.
1642|火车将在下午三点到达上海。|Tàu sẽ đến Thượng Hải lúc ba giờ chiều.
1643|你到底想说什么？|Rốt cuộc bạn muốn nói gì?
1644|他在比赛中得分最高。|Anh ấy ghi được số điểm cao nhất trong trận đấu.
1645|请在这里等待几分钟。|Hãy chờ ở đây vài phút.
1646|猫躲在桌子底下。|Con mèo trốn dưới bàn.
1647|这个地区冬天经常下雪。|Khu vực này mùa đông thường có tuyết.
1648|妈妈晚上喜欢看电视剧。|Buổi tối mẹ thích xem phim truyền hình.
1649|这家电视台每天播出新闻。|Đài truyền hình này phát tin tức mỗi ngày.
1650|爸爸每天开车时听电台。|Bố nghe đài mỗi ngày khi lái xe.
1651|我已经给老师发了电子邮件。|Tôi đã gửi email cho giáo viên.
1652|公司把他调到上海工作了。|Công ty đã điều anh ấy đến Thượng Hải làm việc.
1653|我们正在做一项学生调查。|Chúng tôi đang thực hiện một cuộc khảo sát sinh viên.
1654|我已经在网上订了两张票。|Tôi đã đặt hai vé trên mạng.
1655|汽车需要定期检查。|Ô tô cần được kiểm tra định kỳ.
1656|这个城市位于中国东部。|Thành phố này nằm ở miền đông Trung Quốc.
1657|家人的支持是我学习的动力。|Sự ủng hộ của gia đình là động lực học tập của tôi.
1658|这个故事非常动人。|Câu chuyện này rất cảm động.
1659|这本书很受年轻读者欢迎。|Quyển sách này rất được độc giả trẻ yêu thích.
1660|每个人都有长处，也有短处。|Mỗi người đều có điểm mạnh và cũng có điểm yếu.
1661|夏天我常穿短裤。|Mùa hè tôi thường mặc quần short.
1662|他来北京参加一个短期培训班。|Anh ấy đến Bắc Kinh tham gia một khóa đào tạo ngắn hạn.
1663|这根绳子突然断了。|Sợi dây này đột nhiên bị đứt.
1664|所有队员都参加了今天的训练。|Tất cả thành viên trong đội đều tham gia buổi tập hôm nay.
1665|我们应该认真对待每一次考试。|Chúng ta nên nghiêm túc đối với mỗi kỳ thi.
1666|我听不清电话里对方说的话。|Tôi không nghe rõ lời người bên kia nói trong điện thoại.
1667|今天的对手实力很强。|Đối thủ hôm nay có thực lực rất mạnh.
1668|这次调查的对象是大学生。|Đối tượng của cuộc khảo sát lần này là sinh viên đại học.
1669|我们一起吃了一顿丰盛的晚饭。|Chúng tôi cùng ăn một bữa tối thịnh soạn.
1670|他在杂志上发表了一篇文章。|Anh ấy đã đăng một bài viết trên tạp chí.
1671|手机突然发出了声音。|Điện thoại đột nhiên phát ra âm thanh.
1672|这里的交通很发达。|Giao thông ở đây rất phát triển.
1673|天气太冷，汽车发动不了。|Trời quá lạnh nên ô tô không khởi động được.
1674|电话是谁发明的？|Điện thoại do ai phát minh?
1675|昨天这里发生了一起交通事故。|Hôm qua ở đây xảy ra một vụ tai nạn giao thông.
1676|请把文件发送到我的邮箱。|Hãy gửi tài liệu vào hộp thư của tôi.
1677|他代表小组在会上发言。|Anh ấy đại diện nhóm phát biểu tại cuộc họp.
1678|这个城市发展得很快。|Thành phố này phát triển rất nhanh.
1679|我不反对你的决定。|Tôi không phản đối quyết định của bạn.
1680|这篇课文我反复读了好几遍。|Bài khóa này tôi đã đọc đi đọc lại nhiều lần.
1681|听到这个消息，他没有什么反应。|Nghe tin này, anh ấy không có phản ứng gì.
1682|反正明天不上课，我们晚一点儿起床吧。|Dù sao ngày mai cũng không học, chúng ta dậy muộn một chút nhé.
1683|这家医院的服务范围很广。|Phạm vi phục vụ của bệnh viện này rất rộng.
1684|我们应该找到适合自己的学习方式。|Chúng ta nên tìm phương thức học phù hợp với bản thân.
1685|这件外套可以防风。|Chiếc áo khoác này có thể chắn gió.
1686|为了防止迟到，我每天都早一点儿出门。|Để tránh đến muộn, mỗi ngày tôi đều ra khỏi nhà sớm hơn một chút.
1687|房东说明天来检查房子。|Chủ nhà nói ngày mai sẽ đến kiểm tra căn nhà.
1688|这里的房屋都很漂亮。|Nhà cửa ở đây đều rất đẹp.
1689|这个月的房租我已经付了。|Tiền thuê nhà tháng này tôi đã trả rồi.
1690|代表团正在访问我们学校。|Đoàn đại biểu đang đến thăm trường chúng tôi.
1691|请把水果放到冰箱里。|Hãy đặt trái cây vào tủ lạnh.
1692|飞机正在高空飞行。|Máy bay đang bay trên cao.
1693|修电脑很费时间。|Sửa máy tính rất tốn thời gian.
1694|这次旅行的费用不高。|Chi phí chuyến đi lần này không cao.
1695|会议结束后，我们分别回家了。|Sau khi cuộc họp kết thúc, chúng tôi lần lượt về nhà.
1696|老师给每个小组分配了不同的任务。|Giáo viên phân công nhiệm vụ khác nhau cho từng nhóm.
1697|老师让我们分组讨论这个问题。|Giáo viên yêu cầu chúng tôi chia nhóm thảo luận vấn đề này.
1698|这本书的内容很丰富。|Nội dung quyển sách này rất phong phú.
1699|投资有一定的风险。|Đầu tư có một mức độ rủi ro nhất định.
1700|不能因为一次失败就否定自己。|Không thể vì một lần thất bại mà phủ định bản thân.
1701|他否认自己说过这句话。|Anh ấy phủ nhận mình từng nói câu này.
"""
def normalize_target(raw_word):
    word = (raw_word or "").strip()

    # Ví dụ:
    # 初（初一） -> 初一
    match = re.search(r"（([^（）]+)）", word)
    if match:
        return match.group(1).strip()

    # Phòng trường hợp có dạng từ như 面1, 面2...
    return re.sub(r"\d+$", "", word).strip()


def parse_examples():
    fixes = {}

    for line in EXAMPLES.strip().splitlines():
        line = line.strip()

        if not line:
            continue

        parts = line.split("|")

        if len(parts) != 3:
            raise ValueError(
                f"Dòng EXAMPLES sai định dạng:\n{line}"
            )

        word_id = int(parts[0])
        chinese = parts[1].strip()
        vietnamese = parts[2].strip()

        if word_id in fixes:
            raise ValueError(
                f"Trùng MaTuVung trong EXAMPLES: {word_id}"
            )

        fixes[word_id] = (chinese, vietnamese)

    return fixes


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"\nKhông tìm thấy file nguồn:\n{SOURCE}"
        )

    fixes = parse_examples()

    # =====================================================
    # Batch 1 bắt buộc đúng 200 từ:
    # 1502 -> 1701
    # =====================================================

    expected_ids = set(range(1502, 1702))

    actual_ids = set(fixes)

    missing_in_code = expected_ids - actual_ids
    extra_in_code = actual_ids - expected_ids

    if missing_in_code or extra_in_code:

        print("\nMaTuVung còn thiếu trong code:")
        print(sorted(missing_in_code))

        print("\nMaTuVung thừa trong code:")
        print(sorted(extra_in_code))

        raise ValueError(
            "\nBATCH 1 KHÔNG ĐỦ ĐÚNG 200 MÃ."
        )

    if len(fixes) != 200:
        raise ValueError(
            f"Cần đúng 200 câu, hiện có {len(fixes)}."
        )

    # =====================================================
    # Đọc preview gốc
    # =====================================================

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    csv_by_id = {
        int(row["MaTuVung"]): row
        for row in rows
    }

    # Kiểm tra tất cả ID thực sự tồn tại trong CSV
    not_found = expected_ids - set(csv_by_id)

    if not_found:
        raise ValueError(
            f"Không tìm thấy MaTuVung trong CSV: "
            f"{sorted(not_found)}"
        )

    # =====================================================
    # Cập nhật
    # =====================================================

    updated = []

    for word_id in sorted(expected_ids):

        row = csv_by_id[word_id]

        if row["TrangThaiImport"] != "NEED_REVIEW":
            raise ValueError(
                f"\nKHÔNG GHI ĐÈ DỮ LIỆU ĐÃ DUYỆT\n"
                f"MaTuVung: {word_id}\n"
                f"ChuHan: {row['ChuHan']}\n"
                f"TrangThaiImport: "
                f"{row['TrangThaiImport']}"
            )

        chinese, vietnamese = fixes[word_id]

        target = normalize_target(
            row["ChuHan"]
        )

        # Mỗi câu Trung bắt buộc chứa từ đang học
        if target not in chinese:
            raise ValueError(
                f"\nCÂU KHÔNG CHỨA TỪ MỤC TIÊU\n"
                f"MaTuVung: {word_id}\n"
                f"ChuHan: {row['ChuHan']}\n"
                f"Target kiểm tra: {target}\n"
                f"Câu: {chinese}"
            )

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

        updated.append(word_id)

    if len(updated) != 200:
        raise ValueError(
            f"Dự kiến cập nhật 200 nhưng thực tế "
            f"chỉ cập nhật {len(updated)}."
        )

    # =====================================================
    # Thống kê
    # =====================================================

    ready = sum(
        row["TrangThaiImport"] == "READY"
        for row in rows
    )

    remaining = sum(
        row["TrangThaiImport"] == "NEED_REVIEW"
        for row in rows
    )

    # Ban đầu:
    # READY = 1
    # NEED_REVIEW = 960
    #
    # Sau batch 1:
    # READY = 201
    # NEED_REVIEW = 760

    if remaining != 760:
        raise ValueError(
            f"\nSố NEED_REVIEW không như dự kiến.\n"
            f"Dự kiến: 760\n"
            f"Thực tế: {remaining}\n"
            f"Chưa ghi file output."
        )

    # =====================================================
    # Chỉ ghi file sau khi toàn bộ kiểm tra PASS
    # =====================================================

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

    print()
    print("=" * 60)
    print("HSK3 - BATCH 1")
    print(f"Đã sửa thêm: {len(updated)} câu")
    print(f"Tổng READY trong CSV: {ready}")
    print(f"Còn NEED_REVIEW: {remaining}")
    print()
    print(f"File mới: {OUTPUT}")
    print()
    print("CHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 60)


if __name__ == "__main__":
    main()

