
import csv
import re
from pathlib import Path

# ==========================================================
# HSK3 - BATCH 4
# MaTuVung: 2102 -> 2301 (200 từ)
#
# Input : offline_preview_hsk3.csv
# Output: offline_preview_hsk3_batch4.csv
#
# Chỉ tạo file CSV, KHÔNG cập nhật SQL Server.
# ==========================================================

DATA_DIR = Path(__file__).resolve().parent / "data"
SOURCE = DATA_DIR / "offline_preview_hsk3.csv"
OUTPUT = DATA_DIR / "offline_preview_hsk3_batch4.csv"

# MaTuVung | Câu tiếng Trung | Dịch tiếng Việt
EXAMPLES = """
2102|孩子们喜欢在沙子上画画。|Bọn trẻ thích vẽ trên cát.
2103|他踢足球时伤了脚。|Anh ấy bị thương ở chân khi đá bóng.
2104|听到这个消息，她很伤心。|Nghe tin này, cô ấy rất buồn.
2105|这家超市的商品种类很多。|Siêu thị này có rất nhiều loại hàng hóa.
2106|这个城市的商业发展得很快。|Hoạt động thương mại của thành phố này phát triển rất nhanh.
2107|快上来吧，我们在二楼等你。|Mau lên đây đi, chúng tôi đang đợi bạn ở tầng hai.
2108|桌子上面放着一本书。|Trên bàn có đặt một quyển sách.
2109|山上风景很好，我们一起走上去吧。|Phong cảnh trên núi rất đẹp, chúng ta cùng đi lên nhé.
2110|最近水果的价格有所上升。|Gần đây giá trái cây có tăng lên.
2111|这件蓝色上衣很适合你。|Chiếc áo màu xanh này rất hợp với bạn.
2112|学校买了一批新的教学设备。|Nhà trường đã mua một loạt thiết bị giảng dạy mới.
2113|这座桥是由中国工程师设计的。|Cây cầu này do các kỹ sư Trung Quốc thiết kế.
2114|学校决定设立一个新的图书室。|Nhà trường quyết định thành lập một phòng đọc sách mới.
2115|年轻人应该关心社会问题。|Người trẻ nên quan tâm đến các vấn đề xã hội.
2116|坐飞机时别忘了带身份证。|Khi đi máy bay đừng quên mang căn cước.
2117|这条河很深，不能下去游泳。|Con sông này rất sâu, không thể xuống bơi.
2118|这次旅行给我留下了深刻的印象。|Chuyến đi này để lại cho tôi ấn tượng sâu sắc.
2119|我们需要深入了解这个问题。|Chúng ta cần tìm hiểu kỹ vấn đề này.
2120|这瓶牛奶有一升。|Chai sữa này có một lít.
2121|这家工厂主要生产汽车。|Nhà máy này chủ yếu sản xuất ô tô.
2122|没有水，人类就无法生存。|Không có nước, con người không thể tồn tại.
2123|老师用生动的故事解释了这个道理。|Giáo viên dùng một câu chuyện sinh động để giải thích đạo lý này.
2124|医生每天都在努力保护病人的生命。|Bác sĩ mỗi ngày đều cố gắng bảo vệ tính mạng bệnh nhân.
2125|这家小店的生意越来越好。|Việc kinh doanh của cửa hàng nhỏ này ngày càng tốt.
2126|这种植物在温暖的地方生长得很好。|Loại cây này sinh trưởng tốt ở nơi ấm áp.
2127|公司发表了一份正式声明。|Công ty đã đưa ra một tuyên bố chính thức.
2128|我们队以三比一的比分获胜。|Đội chúng tôi giành chiến thắng với tỷ số ba một.
2129|大家一起庆祝比赛的胜利。|Mọi người cùng ăn mừng chiến thắng trong trận đấu.
2130|我不想失去这个学习机会。|Tôi không muốn đánh mất cơ hội học tập này.
2131|孩子捡起一块石头扔进河里。|Đứa trẻ nhặt một hòn đá ném xuống sông.
2132|这个国家有丰富的石油资源。|Quốc gia này có nguồn tài nguyên dầu mỏ phong phú.
2133|遇到困难时，我们应该保持冷静。|Khi gặp khó khăn, chúng ta nên giữ bình tĩnh.
2134|互联网改变了这个时代的生活方式。|Internet đã thay đổi cách sống của thời đại này.
2135|我永远不会忘记那个重要的时刻。|Tôi sẽ không bao giờ quên khoảnh khắc quan trọng đó.
2136|这件事看起来简单，实际上很复杂。|Việc này trông đơn giản nhưng thực ra rất phức tạp.
2137|这两支球队的实力差不多。|Thực lực của hai đội bóng này gần tương đương nhau.
2138|学校下个月开始实行新规定。|Tháng sau nhà trường bắt đầu thực hiện quy định mới.
2139|学生们正在做一个科学实验。|Các học sinh đang thực hiện một thí nghiệm khoa học.
2140|进入实验室以前要穿好实验服。|Trước khi vào phòng thí nghiệm phải mặc áo thí nghiệm.
2141|买食品时要注意生产日期。|Khi mua thực phẩm phải chú ý ngày sản xuất.
2142|这部电影使我想起了小时候的生活。|Bộ phim này khiến tôi nhớ đến cuộc sống thời thơ ấu.
2143|他始终相信自己能够成功。|Anh ấy luôn tin rằng mình có thể thành công.
2144|这座建筑建于上个世纪。|Tòa nhà này được xây dựng vào thế kỷ trước.
2145|我希望将来有机会环游世界。|Tôi hy vọng sau này có cơ hội đi vòng quanh thế giới.
2146|我们一家人一起看世界杯比赛。|Cả gia đình tôi cùng xem trận đấu World Cup.
2147|妈妈每天早上去市场买菜。|Mẹ mỗi sáng đều đi chợ mua rau.
2148|这次交通事故没有人受伤。|Vụ tai nạn giao thông lần này không có ai bị thương.
2149|老师让我们讨论最近发生的新闻事件。|Giáo viên yêu cầu chúng tôi thảo luận sự kiện thời sự gần đây.
2150|我们应该尊重事实，不随便猜测。|Chúng ta nên tôn trọng sự thật, không tùy tiện suy đoán.
2151|他看起来很严肃，事实上很幽默。|Anh ấy trông nghiêm túc nhưng thực ra rất hài hước.
2152|她希望把教育当作一生的事业。|Cô ấy muốn xem giáo dục là sự nghiệp cả đời.
2153|老师正在检查这次考试的试题。|Giáo viên đang kiểm tra đề thi lần này.
2154|工程师正在试验一种新材料。|Các kỹ sư đang thử nghiệm một loại vật liệu mới.
2155|这份工作很适合刚毕业的学生。|Công việc này rất phù hợp với sinh viên mới tốt nghiệp.
2156|刚到中国时，我还不太适应这里的天气。|Khi mới đến Trung Quốc, tôi chưa quen với thời tiết ở đây.
2157|这个方法并不适用于所有情况。|Phương pháp này không áp dụng được cho mọi trường hợp.
2158|老师走进办公室准备开会。|Giáo viên bước vào phòng làm việc để chuẩn bị họp.
2159|这个停车场按小时收费。|Bãi đỗ xe này thu phí theo giờ.
2160|我们全家晚上一起收看新闻节目。|Cả gia đình tôi cùng xem chương trình thời sự buổi tối.
2161|爷爷每天早上收听广播。|Ông mỗi sáng đều nghe chương trình phát thanh.
2162|奶奶的房间里有一台旧收音机。|Trong phòng bà có một chiếc radio cũ.
2163|出国以前要办好相关手续。|Trước khi ra nước ngoài phải hoàn tất các thủ tục liên quan.
2164|他的手指被纸划破了。|Ngón tay anh ấy bị giấy cứa rách.
2165|北京是中国的首都。|Bắc Kinh là thủ đô của Trung Quốc.
2166|首先检查答案，然后再交试卷。|Trước tiên kiểm tra đáp án, sau đó mới nộp bài thi.
2167|这家餐厅很受年轻人欢迎。|Nhà hàng này rất được người trẻ yêu thích.
2168|他骑自行车时不小心受伤了。|Anh ấy vô ý bị thương khi đi xe đạp.
2169|我把刚买的书放在书架上。|Tôi đặt những quyển sách vừa mua lên giá sách.
2170|虽然输了比赛，但我们没有放弃。|Tuy thua trận nhưng chúng tôi không bỏ cuộc.
2171|登录时需要输入用户名和密码。|Khi đăng nhập cần nhập tên người dùng và mật khẩu.
2172|在这个城市里，我遇到了一位熟人。|Ở thành phố này, tôi gặp một người quen.
2173|我属兔，你属什么？|Tôi tuổi Mão, còn bạn tuổi gì?
2174|这本书属于学校图书馆。|Quyển sách này thuộc thư viện của trường.
2175|他买了一束鲜花送给妈妈。|Anh ấy mua một bó hoa tươi tặng mẹ.
2176|这家工厂每天生产的商品数量很多。|Số lượng hàng hóa nhà máy này sản xuất mỗi ngày rất lớn.
2177|我买了一双新的运动鞋。|Tôi mua một đôi giày thể thao mới.
2178|经过讨论，双方终于达成了协议。|Sau khi thảo luận, hai bên cuối cùng đã đạt được thỏa thuận.
2179|每个人都有自己的思想和看法。|Mỗi người đều có tư tưởng và cách nhìn riêng.
2180|花园里的花因为缺水死了。|Hoa trong vườn đã chết vì thiếu nước.
2181|下雨天开车要降低速度。|Khi lái xe ngày mưa phải giảm tốc độ.
2182|气温会随季节变化。|Nhiệt độ thay đổi theo mùa.
2183|这所学校有一百多年的历史。|Ngôi trường này có lịch sử hơn một trăm năm.
2184|研究所的所长正在介绍新项目。|Viện trưởng viện nghiên cứu đang giới thiệu dự án mới.
2185|办公室新买了两台电脑。|Văn phòng vừa mua hai chiếc máy tính.
2186|我想和老师谈一下学习计划。|Tôi muốn trao đổi với giáo viên về kế hoạch học tập.
2187|老师找我谈话，了解最近的学习情况。|Giáo viên nói chuyện với tôi để tìm hiểu tình hình học tập gần đây.
2188|两家公司正在谈判合作条件。|Hai công ty đang đàm phán các điều kiện hợp tác.
2189|天气冷了，喝一碗热汤吧。|Trời lạnh rồi, hãy uống một bát canh nóng.
2190|我喝咖啡的时候不喜欢放糖。|Khi uống cà phê tôi không thích cho đường.
2191|这家餐厅的特色是四川菜。|Điểm đặc trưng của nhà hàng này là món Tứ Xuyên.
2192|为了赶飞机，我们提前两个小时出发。|Để kịp chuyến bay, chúng tôi xuất phát sớm hai tiếng.
2193|老师讲完课以后，同学们开始提问。|Sau khi giáo viên giảng xong, các bạn bắt đầu đặt câu hỏi.
2194|这道题目的答案是什么？|Đáp án của câu hỏi này là gì?
2195|通过这次旅行，我体会到了独立生活的重要性。|Qua chuyến đi này, tôi hiểu được tầm quan trọng của cuộc sống tự lập.
2196|他的行动体现了对家人的关心。|Hành động của anh ấy thể hiện sự quan tâm đối với gia đình.
2197|我想去中国体验当地人的生活。|Tôi muốn đến Trung Quốc trải nghiệm cuộc sống của người dân địa phương.
2198|雨后天空出现了一道彩虹。|Sau cơn mưa, trên bầu trời xuất hiện một cầu vồng.
2199|这个西瓜又大又甜。|Quả dưa hấu này vừa to vừa ngọt.
2200|这杯饮料太甜了，调一下味道吧。|Đồ uống này ngọt quá, hãy điều chỉnh vị một chút.
2201|老师根据我们的水平调整了教学计划。|Giáo viên đã điều chỉnh kế hoạch giảng dạy theo trình độ của chúng tôi.
2202|孩子高兴得跳了起来。|Đứa trẻ vui đến mức nhảy lên.
2203|他在学校的跳高比赛中得了第一名。|Anh ấy đạt giải nhất cuộc thi nhảy cao của trường.
2204|妹妹每个周末都去学习跳舞。|Em gái mỗi cuối tuần đều đi học nhảy.
2205|学校运动会有跳远比赛。|Hội thao của trường có môn nhảy xa.
2206|这座桥主要是用铁建成的。|Cây cầu này chủ yếu được xây bằng sắt.
2207|这条铁路连接了两个大城市。|Tuyến đường sắt này nối hai thành phố lớn.
2208|每天听中文新闻可以提高听力。|Nghe tin tức tiếng Trung mỗi ngày có thể cải thiện kỹ năng nghe.
2209|这位主持人很受年轻听众欢迎。|Người dẫn chương trình này rất được thính giả trẻ yêu thích.
2210|雨太大了，比赛不得不停止。|Mưa quá lớn nên trận đấu buộc phải dừng lại.
2211|我通常晚上八点开始复习。|Tôi thường bắt đầu ôn bài lúc tám giờ tối.
2212|山区的通信有时不太方便。|Việc liên lạc ở vùng núi đôi khi không thuận tiện lắm.
2213|父母同意我参加这次旅行。|Cha mẹ đồng ý cho tôi tham gia chuyến đi này.
2214|我的牙很痛，明天要去看医生。|Răng tôi rất đau, ngày mai phải đi khám bác sĩ.
2215|虽然训练很痛苦，他还是坚持下来了。|Tuy việc luyện tập rất gian khổ, anh ấy vẫn kiên trì.
2216|工作太累时，我的头脑就不太清楚。|Khi làm việc quá mệt, đầu óc tôi không còn minh mẫn.
2217|他的表现非常突出，老师表扬了他。|Biểu hiện của anh ấy rất nổi bật nên được giáo viên khen.
2218|天突然下起了大雨。|Trời đột nhiên đổ mưa lớn.
2219|请看这张图，然后回答问题。|Hãy xem hình này rồi trả lời câu hỏi.
2220|孩子画了一幅美丽的图画。|Đứa trẻ vẽ một bức tranh đẹp.
2221|种花以前先把土松一松。|Trước khi trồng hoa hãy xới đất cho tơi.
2222|旅游团明天早上七点出发。|Đoàn du lịch sẽ xuất phát lúc bảy giờ sáng mai.
2223|大家只有团结起来，才能完成任务。|Chỉ khi mọi người đoàn kết mới có thể hoàn thành nhiệm vụ.
2224|学校里有很多学生团体。|Trong trường có nhiều tổ chức sinh viên.
2225|新政策推动了当地经济的发展。|Chính sách mới đã thúc đẩy kinh tế địa phương phát triển.
2226|这家公司正在推广新的环保产品。|Công ty này đang quảng bá sản phẩm thân thiện môi trường mới.
2227|政府正在推进城市交通建设。|Chính phủ đang thúc đẩy xây dựng giao thông đô thị.
2228|他轻轻推开门，走进了房间。|Anh ấy nhẹ nhàng đẩy cửa rồi bước vào phòng.
2229|这件衣服不合适，我想退了。|Bộ quần áo này không phù hợp, tôi muốn trả lại.
2230|用完电脑以后记得退出账号。|Sau khi dùng máy tính hãy nhớ đăng xuất tài khoản.
2231|爷爷退休以后喜欢在家种花。|Sau khi nghỉ hưu, ông thích trồng hoa ở nhà.
2232|他大学毕业后开始从事外交工作。|Sau khi tốt nghiệp đại học, anh ấy bắt đầu làm công tác ngoại giao.
2233|外面正在下雨，出门记得带伞。|Bên ngoài đang mưa, khi ra ngoài nhớ mang ô.
2234|这家书店有不少外文书籍。|Hiệu sách này có khá nhiều sách ngoại văn.
2235|虽然计划不完美，但已经很不错了。|Tuy kế hoạch chưa hoàn hảo nhưng đã rất tốt rồi.
2236|我们还需要进一步完善这个系统。|Chúng ta vẫn cần tiếp tục hoàn thiện hệ thống này.
2237|请把完整的报告发给我。|Hãy gửi cho tôi bản báo cáo hoàn chỉnh.
2238|弟弟收到新玩具后非常高兴。|Em trai rất vui sau khi nhận được đồ chơi mới.
2239|他周末往往会去图书馆看书。|Cuối tuần anh ấy thường đến thư viện đọc sách.
2240|吸烟会危害身体健康。|Hút thuốc gây hại cho sức khỏe.
2241|晚上一个人走这条山路很危险。|Đi một mình trên con đường núi này vào ban đêm rất nguy hiểm.
2242|我们要以安全为第一原则。|Chúng ta phải lấy an toàn làm nguyên tắc hàng đầu.
2243|老师为我们准备了很多练习题。|Giáo viên đã chuẩn bị nhiều bài tập cho chúng tôi.
2244|孩子们围在老师身边听故事。|Bọn trẻ quây quanh giáo viên để nghe kể chuyện.
2245|他的父亲是一位伟大的科学家。|Cha của anh ấy là một nhà khoa học vĩ đại.
2246|饭前洗手是良好的卫生习惯。|Rửa tay trước khi ăn là thói quen vệ sinh tốt.
2247|请问卫生间在哪里？|Xin hỏi nhà vệ sinh ở đâu?
2248|为了提高汉语水平，我每天练习口语。|Để nâng cao trình độ tiếng Trung, tôi luyện nói mỗi ngày.
2249|冬天的一杯热茶让我感到温暖。|Một cốc trà nóng mùa đông khiến tôi cảm thấy ấm áp.
2250|学习语言也要了解当地文化。|Học ngôn ngữ cũng cần tìm hiểu văn hóa địa phương.
2251|请把这个文件保存到电脑里。|Hãy lưu tệp này vào máy tính.
2252|在公共场所保持安静是一种文明行为。|Giữ yên lặng ở nơi công cộng là một hành vi văn minh.
2253|她从小就对中国文学感兴趣。|Cô ấy từ nhỏ đã quan tâm đến văn học Trung Quốc.
2254|这篇文章介绍了中国的传统节日。|Bài viết này giới thiệu các ngày lễ truyền thống của Trung Quốc.
2255|这块石头上刻着古老的文字。|Trên hòn đá này có khắc chữ viết cổ.
2256|见面时，他们友好地握手。|Khi gặp nhau, họ thân thiện bắt tay.
2257|这个屋子虽然不大，但是很干净。|Căn phòng này tuy không lớn nhưng rất sạch sẽ.
2258|博物馆里展示着古代的武器。|Trong bảo tàng trưng bày các loại vũ khí cổ đại.
2259|哥哥从小就喜欢学习中国武术。|Anh trai từ nhỏ đã thích học võ thuật Trung Quốc.
2260|演员们已经走上舞台准备表演。|Các diễn viên đã bước lên sân khấu chuẩn bị biểu diễn.
2261|中国西部有许多美丽的自然风景。|Miền tây Trung Quốc có nhiều phong cảnh thiên nhiên đẹp.
2262|我希望明年能通过HSK考试。|Tôi hy vọng năm sau có thể vượt qua kỳ thi HSK.
2263|我哥哥在大学的中文系学习。|Anh trai tôi học tại khoa tiếng Trung của trường đại học.
2264|听到老师叫我的名字，我马上走下来。|Nghe giáo viên gọi tên, tôi lập tức đi xuống.
2265|猫躲在桌子下面睡觉。|Con mèo trốn dưới bàn để ngủ.
2266|这件事很重要，我们要继续做下去。|Việc này rất quan trọng, chúng ta phải tiếp tục làm.
2267|这家医院使用了先进的医疗设备。|Bệnh viện này sử dụng thiết bị y tế tiên tiến.
2268|穿上这件衣服后，他显得年轻多了。|Sau khi mặc bộ quần áo này, anh ấy trông trẻ hơn nhiều.
2269|他一直没有回答，显然还没想好。|Anh ấy vẫn chưa trả lời, rõ ràng là chưa nghĩ xong.
2270|手机屏幕上显示着今天的日期。|Trên màn hình điện thoại hiển thị ngày hôm nay.
2271|记者很快赶到了事故现场。|Phóng viên nhanh chóng đến hiện trường vụ tai nạn.
2272|现代科技让人们的生活更加方便。|Công nghệ hiện đại khiến cuộc sống thuận tiện hơn.
2273|这家小店只接受现金付款。|Cửa hàng nhỏ này chỉ nhận thanh toán bằng tiền mặt.
2274|我们应该勇敢面对现实。|Chúng ta nên dũng cảm đối mặt với thực tế.
2275|老师让我们观察这个自然现象。|Giáo viên yêu cầu chúng tôi quan sát hiện tượng tự nhiên này.
2276|妈妈用针和线缝好了我的衣服。|Mẹ dùng kim và chỉ khâu lại quần áo cho tôi.
2277|与去年相比，今年的游客更多。|So với năm ngoái, năm nay có nhiều du khách hơn.
2278|这道题相当难，我做了很久。|Câu này khá khó, tôi làm rất lâu.
2279|请把相关资料发给所有同学。|Hãy gửi tài liệu liên quan cho tất cả các bạn học.
2280|团队成员之间应该相互帮助。|Các thành viên trong nhóm nên giúp đỡ lẫn nhau.
2281|这两幅画的风格非常相似。|Phong cách của hai bức tranh này rất giống nhau.
2282|厨房里传来一阵很香的饭菜味。|Từ nhà bếp tỏa ra mùi thức ăn rất thơm.
2283|我每天早上吃一根香蕉。|Mỗi sáng tôi ăn một quả chuối.
2284|年轻人应该学会合理消费。|Người trẻ nên học cách chi tiêu hợp lý.
2285|太阳出来以后，山上的雾慢慢消失了。|Sau khi mặt trời lên, sương trên núi dần biến mất.
2286|我刚收到一个好消息。|Tôi vừa nhận được một tin tốt.
2287|每天坚持练习，学习效果会更好。|Kiên trì luyện tập mỗi ngày thì hiệu quả học tập sẽ tốt hơn.
2288|老师建议我们每天练习中文写作。|Giáo viên khuyên chúng tôi luyện viết tiếng Trung mỗi ngày.
2289|医生说他需要做一次血液检查。|Bác sĩ nói anh ấy cần làm xét nghiệm máu.
2290|听到这个消息，我的心终于放下了。|Nghe tin này, cuối cùng tôi cũng yên lòng.
2291|请把这封信放进信封里。|Hãy bỏ lá thư này vào phong bì.
2292|朋友之间应该相互信任。|Bạn bè nên tin tưởng lẫn nhau.
2293|我的行李太重了，你能帮我拿一下吗？|Hành lý của tôi nặng quá, bạn giúp tôi xách một chút được không?
2294|经过长期练习，他形成了良好的学习习惯。|Sau thời gian dài luyện tập, anh ấy đã hình thành thói quen học tập tốt.
2295|这次考试采用网上答题的形式。|Kỳ thi lần này sử dụng hình thức trả lời trực tuyến.
2296|这位演员在电影中的形象很有特点。|Hình tượng của diễn viên này trong phim rất đặc sắc.
2297|这个盒子的形状像一颗心。|Hình dạng chiếc hộp này giống một trái tim.
2298|和家人一起吃晚饭让我感到幸福。|Ăn tối cùng gia đình khiến tôi cảm thấy hạnh phúc.
2299|我很幸运，遇到了一位好老师。|Tôi rất may mắn khi gặp được một giáo viên tốt.
2300|老师的鼓励提高了学生的学习积极性。|Sự động viên của giáo viên đã nâng cao tính tích cực học tập của học sinh.
2301|填写表格时，请选择正确的性别。|Khi điền biểu mẫu, hãy chọn giới tính chính xác.
"""


def normalize_target(word):
    word = (word or "").strip()

    # Ví dụ: 性（积极性） -> 积极性
    match = re.search(r"（([^（）]+)）", word)
    if match:
        return match.group(1).strip()

    return re.sub(r"\d+$", "", word).strip()


def parse_examples():
    result = {}

    for number, line in enumerate(EXAMPLES.strip().splitlines(), 1):
        parts = line.strip().split("|")

        if len(parts) != 3:
            raise ValueError(
                f"EXAMPLES dòng {number} sai định dạng: {line}"
            )

        word_id = int(parts[0].strip())
        chinese = parts[1].strip()
        vietnamese = parts[2].strip()

        if word_id in result:
            raise ValueError(f"Trùng mã: {word_id}")

        if not chinese or not vietnamese:
            raise ValueError(f"Câu rỗng ở mã: {word_id}")

        result[word_id] = (chinese, vietnamese)

    return result


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Không tìm thấy CSV: {SOURCE}")

    fixes = parse_examples()
    expected = set(range(2102, 2302))

    if set(fixes) != expected:
        raise ValueError(
            f"Thiếu mã: {sorted(expected - set(fixes))}\n"
            f"Thừa mã: {sorted(set(fixes) - expected)}"
        )

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    if not fields:
        raise ValueError("Không đọc được header CSV")

    required = {
        "MaTuVung",
        "ChuHan",
        "ViDuTiengTrung",
        "ViDuTiengViet",
        "LoaiCau",
        "TrangThaiImport",
    }

    if not required.issubset(fields):
        raise ValueError(
            f"CSV thiếu cột: {sorted(required - set(fields))}"
        )

    if len(rows) != 961:
        raise ValueError(
            f"CSV phải có 961 dòng, hiện có {len(rows)}"
        )

    by_id = {int(r["MaTuVung"]): r for r in rows}

    if len(by_id) != len(rows):
        raise ValueError("CSV có MaTuVung bị trùng")

    missing = expected - set(by_id)
    if missing:
        raise ValueError(f"CSV thiếu mã: {sorted(missing)}")

    # Kiểm tra trước khi sửa bất kỳ dòng nào.
    errors = []

    for word_id in sorted(expected):
        row = by_id[word_id]
        chinese, vietnamese = fixes[word_id]
        target = normalize_target(row["ChuHan"])

        if row["TrangThaiImport"].strip() != "NEED_REVIEW":
            errors.append(
                f"{word_id}: không còn NEED_REVIEW"
            )

        if target not in chinese:
            errors.append(
                f"{word_id}: câu không chứa '{target}' "
                f"-> {chinese}"
            )

    if errors:
        print("\n".join(errors))
        raise ValueError(
            "DỪNG: Dữ liệu chưa hợp lệ. Chưa ghi file."
        )

    for word_id in sorted(expected):
        row = by_id[word_id]
        chinese, vietnamese = fixes[word_id]

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

    ready = sum(
        row["TrangThaiImport"] == "READY"
        for row in rows
    )
    remaining = sum(
        row["TrangThaiImport"] == "NEED_REVIEW"
        for row in rows
    )

    if ready != 801 or remaining != 160:
        raise ValueError(
            f"Thống kê không đúng: READY={ready}, "
            f"NEED_REVIEW={remaining}. Chưa ghi file."
        )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 60)
    print("HSK3 - BATCH 4")
    print("Đã sửa thêm: 200 câu")
    print(f"Tổng READY trong CSV: {ready}")
    print(f"Còn NEED_REVIEW: {remaining}")
    print()
    print(f"File mới: {OUTPUT}")
    print()
    print("CHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 60)


if __name__ == "__main__":
    main()
