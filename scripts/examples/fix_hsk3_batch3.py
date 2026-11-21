
import csv
from pathlib import Path

# HSK3 - BATCH 3: 1902 -> 2101 (200 câu)
# Chỉ tạo CSV mới, KHÔNG ghi vào SQL Server.

DATA = Path(__file__).resolve().parent / "data"
SOURCE = DATA / "offline_preview_hsk3.csv"
OUTPUT = DATA / "offline_preview_hsk3_batch3.csv"

# MaTuVung | Câu tiếng Trung | Nghĩa tiếng Việt
EXAMPLES = """
1902|我每天早上喝一杯咖啡。|Mỗi sáng tôi uống một cốc cà phê.
1903|公司正在开发一个新的手机应用。|Công ty đang phát triển một ứng dụng điện thoại mới.
1904|图书馆周末也对学生开放。|Thư viện cuối tuần cũng mở cửa cho sinh viên.
1905|会议九点开始。|Cuộc họp bắt đầu lúc chín giờ.
1906|那家新饭店下周开业。|Nhà hàng mới đó sẽ khai trương vào tuần sau.
1907|学校正在开展环保活动。|Nhà trường đang triển khai hoạt động bảo vệ môi trường.
1908|他今天看起来很累。|Hôm nay trông anh ấy rất mệt.
1909|这件衣服看上去很适合你。|Bộ quần áo này trông rất hợp với bạn.
1910|这次比赛是对我们能力的一次考验。|Cuộc thi lần này là một thử thách đối với năng lực của chúng tôi.
1911|现代科技改变了我们的生活。|Khoa học công nghệ hiện đại đã thay đổi cuộc sống của chúng ta.
1912|他是一个很可靠的朋友。|Anh ấy là một người bạn rất đáng tin cậy.
1913|我不常喝可乐。|Tôi không thường uống cola.
1914|我们要努力克服学习中的困难。|Chúng ta phải cố gắng khắc phục những khó khăn trong học tập.
1915|我们应该客观地看待这个问题。|Chúng ta nên nhìn nhận vấn đề này một cách khách quan.
1916|这学期我选了五门课程。|Học kỳ này tôi chọn năm môn học.
1917|教室里一个人也没有，很空。|Trong lớp không có ai, rất trống.
1918|天太热了，请打开空调。|Trời nóng quá, hãy bật điều hòa.
1919|今天恐怕要下雨。|Hôm nay e rằng trời sẽ mưa.
1920|你有空儿的时候给我打电话。|Khi có thời gian rảnh, bạn hãy gọi cho tôi.
1921|这条裤子有点儿长。|Chiếc quần này hơi dài.
1922|城市正在快速发展。|Thành phố đang phát triển nhanh chóng.
1923|昨晚没睡好，我现在很困。|Tối qua tôi ngủ không ngon nên bây giờ rất buồn ngủ.
1924|遇到困难不要轻易放弃。|Khi gặp khó khăn đừng dễ dàng bỏ cuộc.
1925|不要浪费时间。|Đừng lãng phí thời gian.
1926|这个政策给老百姓带来了方便。|Chính sách này mang lại sự thuận tiện cho người dân.
1927|老板今天不在公司。|Hôm nay ông chủ không có ở công ty.
1928|那位老太太每天早上来公园散步。|Bà lão đó mỗi sáng đều đến công viên đi dạo.
1929|门口坐着一个老头儿。|Ở cửa có một ông lão đang ngồi.
1930|听到这个好消息，大家都乐了。|Nghe tin tốt này, mọi người đều vui.
1931|她一直保持乐观的态度。|Cô ấy luôn giữ thái độ lạc quan.
1932|这里有很多类商品。|Ở đây có rất nhiều loại hàng hóa.
1933|我以前遇到过类似的问题。|Trước đây tôi từng gặp vấn đề tương tự.
1934|他们去年离婚了。|Họ đã ly hôn vào năm ngoái.
1935|包里面有一本书。|Bên trong túi có một quyển sách.
1936|我下午去理发。|Chiều nay tôi đi cắt tóc.
1937|谢谢你理解我的想法。|Cảm ơn bạn đã hiểu suy nghĩ của tôi.
1938|学习理论以后还要多实践。|Sau khi học lý thuyết còn phải thực hành nhiều.
1939|你迟到有什么理由吗？|Bạn có lý do gì cho việc đến muộn không?
1940|他使出全身的力推开了门。|Anh ấy dùng hết sức đẩy cánh cửa ra.
1941|团结就是力量。|Đoàn kết chính là sức mạnh.
1942|听到消息后，他立刻赶来了。|Sau khi nghe tin, anh ấy lập tức chạy đến.
1943|我们要充分利用时间。|Chúng ta phải tận dụng tốt thời gian.
1944|他太忙了，连午饭都没吃。|Anh ấy quá bận, đến cả bữa trưa cũng không ăn.
1945|孩子摔倒了，妈妈连忙跑过去。|Đứa trẻ bị ngã, mẹ lập tức chạy tới.
1946|他连续工作了八个小时。|Anh ấy làm việc liên tục tám tiếng.
1947|奶奶每天晚上都看连续剧。|Bà mỗi tối đều xem phim truyền hình nhiều tập.
1948|两家公司决定联合开发新产品。|Hai công ty quyết định cùng phát triển sản phẩm mới.
1949|联合国总部在纽约。|Trụ sở Liên Hợp Quốc ở New York.
1950|到北京以后请联系我。|Sau khi đến Bắc Kinh hãy liên lạc với tôi.
1951|运动以后不要马上喝太多凉水。|Sau khi vận động không nên uống quá nhiều nước lạnh ngay.
1952|他终于了却了多年的心愿。|Cuối cùng anh ấy đã hoàn thành tâm nguyện nhiều năm.
1953|我去办公室领新教材。|Tôi đến văn phòng nhận giáo trình mới.
1954|领导正在开会。|Lãnh đạo đang họp.
1955|我们队现在领先两分。|Đội chúng tôi hiện đang dẫn trước hai điểm.
1956|我买了苹果，另外还买了香蕉。|Tôi mua táo, ngoài ra còn mua chuối.
1957|这份工作工资高，另一方面压力也很大。|Công việc này lương cao, mặt khác áp lực cũng rất lớn.
1958|她明年准备去中国留学。|Năm sau cô ấy dự định sang Trung Quốc du học.
1959|中国文化中常常可以看到龙的形象。|Trong văn hóa Trung Quốc thường thấy hình tượng rồng.
1960|请帮我把这段声音录下来。|Hãy giúp tôi ghi lại đoạn âm thanh này.
1961|我每天听中文录音练习听力。|Mỗi ngày tôi nghe bản ghi âm tiếng Trung để luyện nghe.
1962|我们先查一下去机场的路线。|Trước tiên chúng ta hãy xem tuyến đường đến sân bay.
1963|我们在火车站附近找了一家旅馆。|Chúng tôi tìm một khách sạn gần ga tàu.
1964|这家旅行社安排了我们的行程。|Công ty du lịch này đã sắp xếp hành trình cho chúng tôi.
1965|我喜欢喝不加糖的绿茶。|Tôi thích uống trà xanh không đường.
1966|房间太乱了，你收拾一下吧。|Phòng bừa bộn quá, bạn dọn một chút đi.
1967|这种技术已经落后了。|Công nghệ này đã lạc hậu rồi.
1968|麻烦你帮我开一下门。|Phiền bạn giúp tôi mở cửa.
1969|草地上有几匹马。|Trên bãi cỏ có vài con ngựa.
1970|这个结果不能满足大家的要求。|Kết quả này không thể đáp ứng yêu cầu của mọi người.
1971|别着急，慢慢说。|Đừng vội, hãy nói từ từ.
1972|这台电脑出了点儿毛病。|Máy tính này gặp một chút trục trặc.
1973|现在后悔也没用。|Bây giờ hối hận cũng vô ích.
1974|这件事受到了媒体的关注。|Việc này đã nhận được sự quan tâm của truyền thông.
1975|我每天七点起床。|Mỗi ngày tôi thức dậy lúc bảy giờ.
1976|春天的校园真美。|Khuôn viên trường vào mùa xuân thật đẹp.
1977|我希望大家都有美好的未来。|Tôi hy vọng mọi người đều có tương lai tốt đẹp.
1978|这个海边城市非常美丽。|Thành phố ven biển này rất đẹp.
1979|这里有很多当地美食。|Ở đây có rất nhiều món ngon địa phương.
1980|妹妹从小就喜欢美术。|Em gái từ nhỏ đã thích mỹ thuật.
1981|这本书十美元。|Quyển sách này giá mười đô la Mỹ.
1982|他是一个足球迷。|Anh ấy là một người hâm mộ bóng đá.
1983|面对困难时要保持冷静。|Khi đối mặt với khó khăn phải giữ bình tĩnh.
1984|这个房间的面积是二十平方米。|Diện tích căn phòng này là hai mươi mét vuông.
1985|这个故事来自民间传说。|Câu chuyện này bắt nguồn từ truyền thuyết dân gian.
1986|中国有很多民族。|Trung Quốc có nhiều dân tộc.
1987|老师明确说明了考试要求。|Giáo viên đã nói rõ yêu cầu của kỳ thi.
1988|他的汉语进步很明显。|Tiếng Trung của anh ấy tiến bộ rất rõ rệt.
1989|我们要努力改变自己的命运。|Chúng ta phải cố gắng thay đổi vận mệnh của mình.
1990|某公司正在招聘新员工。|Một công ty nào đó đang tuyển nhân viên mới.
1991|我的母亲是一名老师。|Mẹ tôi là một giáo viên.
1992|这张桌子是用木头做的。|Chiếc bàn này được làm bằng gỗ.
1993|我的目标是通过HSK考试。|Mục tiêu của tôi là vượt qua kỳ thi HSK.
1994|目前一切都很顺利。|Hiện tại mọi việc đều rất thuận lợi.
1995|她喜欢喝热奶茶。|Cô ấy thích uống trà sữa nóng.
1996|一名男子正在路边等车。|Một người đàn ông đang đợi xe bên đường.
1997|这个国家南部气候温暖。|Phần phía nam của quốc gia này có khí hậu ấm áp.
1998|难道你忘了今天的考试吗？|Chẳng lẽ bạn quên kỳ thi hôm nay rồi sao?
1999|这道题的难度比较大。|Mức độ khó của câu này tương đối cao.
2000|请在三天内完成这项工作。|Hãy hoàn thành công việc này trong ba ngày.
2001|这篇文章的内容很有意思。|Nội dung bài viết này rất thú vị.
2002|听到这个消息，我内心很激动。|Nghe tin này, trong lòng tôi rất xúc động.
2003|你能不能再说一遍？|Bạn có thể nói lại một lần nữa không?
2004|她有很强的工作能力。|Cô ấy có năng lực làm việc rất tốt.
2005|公司在年初制定了新的计划。|Công ty đã lập kế hoạch mới vào đầu năm.
2006|这首歌在九十年代很流行。|Bài hát này rất thịnh hành vào những năm 1990.
2007|这个项目计划在年底完成。|Dự án này dự kiến hoàn thành vào cuối năm.
2008|他年纪虽然大，但是身体很好。|Tuy tuổi ông ấy cao nhưng sức khỏe rất tốt.
2009|老师让我们一起念这段课文。|Giáo viên yêu cầu chúng tôi cùng đọc đoạn bài khóa này.
2010|农场里养了很多牛。|Trong trang trại nuôi rất nhiều bò.
2011|我的爷爷奶奶住在农村。|Ông bà tôi sống ở nông thôn.
2012|这些农民每天很早就开始工作。|Những người nông dân này mỗi ngày bắt đầu làm việc rất sớm.
2013|这个地区主要发展农业。|Khu vực này chủ yếu phát triển nông nghiệp.
2014|那名女子正在向警察问路。|Người phụ nữ đó đang hỏi đường cảnh sát.
2015|今天比昨天暖和多了。|Hôm nay ấm hơn hôm qua nhiều.
2016|我想给你拍一张照片。|Tôi muốn chụp cho bạn một bức ảnh.
2017|这所大学的排名很高。|Thứ hạng của trường đại học này rất cao.
2018|商店门口挂着一个大牌子。|Trước cửa hàng treo một tấm biển lớn.
2019|公司派我去上海出差。|Công ty cử tôi đi Thượng Hải công tác.
2020|我们不能只根据外表判断一个人。|Chúng ta không thể chỉ dựa vào bề ngoài để phán đoán một người.
2021|他最近胖了一点儿。|Gần đây anh ấy béo lên một chút.
2022|我每天早上去公园跑步。|Mỗi sáng tôi đến công viên chạy bộ.
2023|这条裤子很配你的鞋。|Chiếc quần này rất hợp với đôi giày của bạn.
2024|谢谢大家配合我们的工作。|Cảm ơn mọi người đã phối hợp với công việc của chúng tôi.
2025|老师没有批评他，而是耐心地帮助他。|Giáo viên không phê bình anh ấy mà kiên nhẫn giúp đỡ.
2026|经理已经批准了我的请假申请。|Quản lý đã phê duyệt đơn xin nghỉ của tôi.
2027|苹果的皮可以吃。|Vỏ táo có thể ăn được.
2028|她手里拿着一个黑色皮包。|Cô ấy đang cầm một chiếc túi da màu đen.
2029|爸爸晚饭时喝了一杯啤酒。|Bố uống một cốc bia trong bữa tối.
2030|这趟火车的票价不贵。|Giá vé chuyến tàu này không đắt.
2031|大家对这部电影的评价很高。|Mọi người đánh giá bộ phim này rất cao.
2032|我每天吃一个苹果。|Mỗi ngày tôi ăn một quả táo.
2033|我的鞋破了，需要换一双新的。|Giày của tôi bị rách rồi, cần đổi một đôi mới.
2034|请不要破坏公共设施。|Xin đừng phá hoại các công trình công cộng.
2035|这种学习方法很普遍。|Phương pháp học này rất phổ biến.
2036|智能手机已经非常普及。|Điện thoại thông minh đã trở nên rất phổ biến.
2037|这期杂志介绍了很多旅游景点。|Số tạp chí kỳ này giới thiệu nhiều địa điểm du lịch.
2038|大家都到齐了，我们开始吧。|Mọi người đã đến đủ rồi, chúng ta bắt đầu nhé.
2039|首先要保证质量，其次才考虑价格。|Trước hết phải bảo đảm chất lượng, tiếp theo mới cân nhắc giá cả.
2040|其实这个问题没有那么难。|Thực ra vấn đề này không khó đến vậy.
2041|今天他没来上课，真奇怪。|Hôm nay anh ấy không đến học, thật kỳ lạ.
2042|这里的气候四季都很温和。|Khí hậu ở đây ôn hòa quanh năm.
2043|下雨天开车千万要小心。|Khi lái xe ngày mưa nhất định phải cẩn thận.
2044|搬家前后我们都很忙。|Trước và sau khi chuyển nhà chúng tôi đều rất bận.
2045|队伍继续前进。|Đội ngũ tiếp tục tiến về phía trước.
2046|前面就是地铁站。|Phía trước chính là ga tàu điện ngầm.
2047|明天我们将前往北京。|Ngày mai chúng tôi sẽ đi đến Bắc Kinh.
2048|他的身体很强。|Cơ thể anh ấy rất khỏe.
2049|团结让我们的团队更加强大。|Sự đoàn kết khiến đội của chúng tôi mạnh mẽ hơn.
2050|老师再次强调了安全问题。|Giáo viên một lần nữa nhấn mạnh vấn đề an toàn.
2051|我强烈建议你早点休息。|Tôi rất khuyên bạn nên nghỉ sớm.
2052|河上有一座老桥。|Trên sông có một cây cầu cũ.
2053|真巧，我们又在这里见面了。|Thật trùng hợp, chúng ta lại gặp nhau ở đây.
2054|她是我的亲姐姐。|Cô ấy là chị ruột của tôi.
2055|新老师说话很亲切。|Giáo viên mới nói chuyện rất thân thiện.
2056|春节时大家都想和亲人团聚。|Vào Tết mọi người đều muốn đoàn tụ với người thân.
2057|经理亲自来接我们。|Quản lý đích thân đến đón chúng tôi.
2058|音乐可以表达丰富的情感。|Âm nhạc có thể biểu đạt những cảm xúc phong phú.
2059|请告诉我现在的情况。|Hãy cho tôi biết tình hình hiện tại.
2060|我想向老师请教一个问题。|Tôi muốn hỏi giáo viên để được chỉ dẫn về một vấn đề.
2061|我们一起吃饭庆祝考试通过。|Chúng tôi cùng ăn cơm để ăn mừng việc thi đỗ.
2062|体育场里来了很多球迷。|Có rất nhiều người hâm mộ bóng đến sân vận động.
2063|这个区有三所大学。|Khu vực này có ba trường đại học.
2064|这两个词有什么区别？|Hai từ này có gì khác nhau?
2065|因为下雨，比赛取消了。|Vì trời mưa nên trận đấu đã bị hủy.
2066|他的爷爷去年去世了。|Ông của anh ấy đã qua đời năm ngoái.
2067|比赛结束后，全场观众都站起来鼓掌。|Sau khi trận đấu kết thúc, toàn bộ khán giả đứng dậy vỗ tay.
2068|医生给他做了全面检查。|Bác sĩ đã kiểm tra toàn diện cho anh ấy.
2069|这个品牌在全球都有商店。|Thương hiệu này có cửa hàng trên toàn cầu.
2070|我们现在缺两个人。|Hiện tại chúng tôi thiếu hai người.
2071|每个人都有自己的缺点。|Mỗi người đều có khuyết điểm riêng.
2072|这个计划还缺少一些重要信息。|Kế hoạch này vẫn thiếu một số thông tin quan trọng.
2073|请提前出发，确保不会迟到。|Hãy xuất phát sớm để bảo đảm không đến muộn.
2074|我还没有确定出发时间。|Tôi vẫn chưa xác định thời gian xuất phát.
2075|这本书确实很好看。|Quyển sách này thực sự rất hay.
2076|她今天穿了一条红裙子。|Hôm nay cô ấy mặc một chiếc váy đỏ.
2077|门口站着一群学生。|Trước cửa có một nhóm học sinh đang đứng.
2078|他从小就热爱音乐。|Anh ấy từ nhỏ đã rất yêu âm nhạc.
2079|大家用热烈的掌声欢迎老师。|Mọi người dùng tràng pháo tay nồng nhiệt chào đón giáo viên.
2080|公司需要更多专业人才。|Công ty cần thêm nhiều nhân tài chuyên môn.
2081|这个湖是人工建成的。|Hồ này được xây dựng nhân tạo.
2082|保护环境是全人类的责任。|Bảo vệ môi trường là trách nhiệm của toàn nhân loại.
2083|人民的生活越来越好。|Cuộc sống của nhân dân ngày càng tốt hơn.
2084|这件衣服要二百元人民币。|Bộ quần áo này có giá hai trăm nhân dân tệ.
2085|他在人群中找到了朋友。|Anh ấy đã tìm thấy bạn mình trong đám đông.
2086|每个人都有自己的人生目标。|Mỗi người đều có mục tiêu cuộc đời riêng.
2087|工作人员正在检查设备。|Nhân viên đang kiểm tra thiết bị.
2088|我一眼就认出了小学老师。|Tôi vừa nhìn đã nhận ra giáo viên tiểu học của mình.
2089|你还认得我吗？|Bạn vẫn nhận ra tôi chứ?
2090|他的工作得到了大家的认可。|Công việc của anh ấy đã nhận được sự công nhận của mọi người.
2091|他连任了两任校长。|Ông ấy đã đảm nhiệm hai nhiệm kỳ hiệu trưởng liên tiếp.
2092|任你怎么说，我都不会改变决定。|Dù bạn nói thế nào, tôi cũng sẽ không thay đổi quyết định.
2093|有任何问题都可以问我。|Có bất kỳ vấn đề gì đều có thể hỏi tôi.
2094|我们已经完成今天的任务。|Chúng tôi đã hoàn thành nhiệm vụ hôm nay.
2095|天已经黑了，他仍在工作。|Trời đã tối nhưng anh ấy vẫn đang làm việc.
2096|下着大雨，他仍然坚持去上课。|Trời đang mưa lớn nhưng anh ấy vẫn kiên trì đi học.
2097|这些都是我的日常工作。|Đây đều là công việc hằng ngày của tôi.
2098|这道题比我想的容易。|Câu này dễ hơn tôi nghĩ.
2099|我们正在讨论如何解决这个问题。|Chúng tôi đang thảo luận cách giải quyết vấn đề này.
2100|晚饭后我们去公园散步。|Sau bữa tối chúng tôi đi công viên dạo bộ.
2101|爸爸坐在沙发上看电视。|Bố ngồi trên ghế sofa xem tivi.
"""


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Không tìm thấy: {SOURCE}")

    fixes = {}
    for line in EXAMPLES.strip().splitlines():
        parts = line.strip().split("|")
        if len(parts) != 3:
            raise ValueError(f"Sai định dạng: {line}")

        word_id = int(parts[0])
        if word_id in fixes:
            raise ValueError(f"Trùng MaTuVung: {word_id}")

        fixes[word_id] = (parts[1].strip(), parts[2].strip())

    expected = set(range(1902, 2102))
    if set(fixes) != expected:
        raise ValueError(
            f"Thiếu ID: {sorted(expected - set(fixes))}; "
            f"Thừa ID: {sorted(set(fixes) - expected)}"
        )

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    if len(rows) != 961:
        raise ValueError(f"CSV phải có 961 dòng, hiện có {len(rows)}")

    by_id = {int(r["MaTuVung"]): r for r in rows}
    if len(by_id) != len(rows):
        raise ValueError("CSV có MaTuVung trùng nhau")

    if not expected.issubset(by_id):
        raise ValueError(f"CSV thiếu ID: {sorted(expected - set(by_id))}")

    for word_id in sorted(expected):
        row = by_id[word_id]
        chinese, vietnamese = fixes[word_id]
        word = row["ChuHan"].strip()

        if row["TrangThaiImport"] != "NEED_REVIEW":
            raise ValueError(f"ID {word_id} không còn NEED_REVIEW")

        if word not in chinese:
            raise ValueError(
                f"ID {word_id}: câu không chứa từ '{word}': {chinese}"
            )

        if not chinese or not vietnamese:
            raise ValueError(f"ID {word_id}: câu rỗng")

    for word_id in sorted(expected):
        row = by_id[word_id]
        chinese, vietnamese = fixes[word_id]

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

    ready = sum(r["TrangThaiImport"] == "READY" for r in rows)
    review = sum(r["TrangThaiImport"] == "NEED_REVIEW" for r in rows)

    if ready != 601 or review != 360:
        raise ValueError(
            f"Số lượng không đúng: READY={ready}, NEED_REVIEW={review}. "
            "Chưa ghi file."
        )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 60)
    print("HSK3 - BATCH 3")
    print("Đã sửa thêm: 200 câu")
    print(f"Tổng READY trong CSV: {ready}")
    print(f"Còn NEED_REVIEW: {review}")
    print(f"\nFile mới: {OUTPUT}")
    print("\nCHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 60)


if __name__ == "__main__":
    main()
