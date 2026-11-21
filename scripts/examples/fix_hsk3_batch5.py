import csv
import re
from pathlib import Path

# ==========================================================
# HSK3 - BATCH 5 (FINAL)
#
# Phạm vi: MaTuVung 2302 -> 2462
# Bỏ qua : 2313 - 压力 (đã READY từ trước)
#
# Số câu mới: 160
#
# Input : offline_preview_hsk3.csv
# Output: offline_preview_hsk3_batch5.csv
#
# Script CHỈ tạo CSV mới.
# KHÔNG cập nhật SQL Server.
# ==========================================================

DATA_DIR = Path(__file__).resolve().parent / "data"

SOURCE = DATA_DIR / "offline_preview_hsk3.csv"
OUTPUT = DATA_DIR / "offline_preview_hsk3_batch5.csv"

# MaTuVung | Câu tiếng Trung | Dịch tiếng Việt
EXAMPLES = """
2302|她性格开朗，很容易和别人交朋友。|Cô ấy có tính cách cởi mở, rất dễ kết bạn với người khác.
2303|我的自行车坏了，下午我要去修。|Xe đạp của tôi hỏng rồi, chiều nay tôi phải đi sửa.
2304|老师让我修改这篇作文。|Giáo viên yêu cầu tôi sửa bài văn này.
2305|公司正在调查年轻消费者的需求。|Công ty đang khảo sát nhu cầu của người tiêu dùng trẻ.
2306|如果需要帮助，可以随时联系我。|Nếu cần giúp đỡ, bạn có thể liên hệ với tôi bất cứ lúc nào.
2307|学校宣布下周开始放假。|Nhà trường thông báo tuần sau bắt đầu nghỉ.
2308|学校举办活动宣传环保知识。|Nhà trường tổ chức hoạt động tuyên truyền kiến thức bảo vệ môi trường.
2309|这位选手第一次参加国际比赛。|Vận động viên này lần đầu tham gia một cuộc thi quốc tế.
2310|这所大学一年的学费是多少？|Học phí một năm của trường đại học này là bao nhiêu?
2311|运动员每天都要进行严格的训练。|Vận động viên mỗi ngày đều phải trải qua huấn luyện nghiêm khắc.
2312|请不要用手压这个盒子。|Xin đừng dùng tay đè lên chiếc hộp này.
2314|厨房里冒出了很多烟。|Trong bếp bốc ra rất nhiều khói.
2315|眼前的困难并没有让他放弃。|Những khó khăn trước mắt không khiến anh ấy bỏ cuộc.
2316|他在这部电影里演一名医生。|Anh ấy đóng vai một bác sĩ trong bộ phim này.
2317|她将在晚会上演唱一首中文歌。|Cô ấy sẽ hát một bài tiếng Trung trong buổi liên hoan.
2318|周末我们一起去看演唱会吧。|Cuối tuần chúng ta cùng đi xem buổi hòa nhạc nhé.
2319|今晚的演出七点半开始。|Buổi biểu diễn tối nay bắt đầu lúc bảy giờ rưỡi.
2320|这位演员在中国很有名。|Diễn viên này rất nổi tiếng ở Trung Quốc.
2321|山坡上有一群羊。|Trên sườn núi có một đàn cừu.
2322|冬天坐在阳光下很舒服。|Mùa đông ngồi dưới ánh nắng rất dễ chịu.
2323|要是明天下雨，我们就不去爬山了。|Nếu ngày mai trời mưa thì chúng ta sẽ không đi leo núi nữa.
2324|我把外套挂在衣架上。|Tôi treo áo khoác lên móc quần áo.
2325|别担心，一切都会好起来的。|Đừng lo, mọi chuyện rồi sẽ tốt lên.
2326|会议已于上午十点结束。|Cuộc họp đã kết thúc lúc mười giờ sáng.
2327|大学毕业以来，他一直在这家公司工作。|Kể từ khi tốt nghiệp đại học, anh ấy luôn làm việc tại công ty này.
2328|一方面这份工作工资高，另一方面压力也很大。|Một mặt công việc này có lương cao, mặt khác áp lực cũng rất lớn.
2329|她从小就对艺术很感兴趣。|Từ nhỏ cô ấy đã rất hứng thú với nghệ thuật.
2330|这次意外没有造成严重后果。|Sự cố lần này không gây ra hậu quả nghiêm trọng.
2331|这次活动对年轻人很有意义。|Hoạt động lần này rất có ý nghĩa đối với người trẻ.
2332|今天下大雨，因此比赛被取消了。|Hôm nay mưa lớn, vì vậy trận đấu đã bị hủy.
2333|这条项链是银做的。|Chiếc vòng cổ này được làm bằng bạc.
2334|她在比赛中获得了一枚银牌。|Cô ấy đã giành được một huy chương bạc trong cuộc thi.
2335|这个城市给我留下了很好的印象。|Thành phố này để lại cho tôi ấn tượng rất tốt.
2336|学生应当按时完成作业。|Học sinh nên hoàn thành bài tập đúng hạn.
2337|大家站在门口迎接新同学。|Mọi người đứng ở cửa chào đón học sinh mới.
2338|蔬菜和水果含有丰富的营养。|Rau và trái cây chứa nhiều chất dinh dưỡng.
2339|只要坚持训练，我们就有机会赢。|Chỉ cần kiên trì luyện tập, chúng ta sẽ có cơ hội thắng.
2340|她毕业以后想从事影视工作。|Sau khi tốt nghiệp, cô ấy muốn làm công việc liên quan đến điện ảnh và truyền hình.
2341|这种技术已经应用到日常生活中。|Công nghệ này đã được ứng dụng vào cuộc sống hằng ngày.
2342|每个人都有自己的优点和缺点。|Mỗi người đều có ưu điểm và khuyết điểm riêng.
2343|这家公司在价格方面很有优势。|Công ty này có lợi thế về mặt giá cả.
2344|这次活动由学生会组织。|Hoạt động lần này do hội sinh viên tổ chức.
2345|由于天气不好，飞机晚点了。|Do thời tiết xấu nên máy bay bị trễ.
2346|我已经把会议资料通过邮件发给你了。|Tôi đã gửi tài liệu cuộc họp cho bạn qua email.
2347|爷爷年轻时喜欢收集邮票。|Ông khi còn trẻ thích sưu tầm tem.
2348|请把你的邮箱地址告诉我。|Hãy cho tôi biết địa chỉ email của bạn.
2349|我们坐船游了西湖。|Chúng tôi đi thuyền tham quan Tây Hồ.
2350|孩子们正在房间里玩游戏。|Bọn trẻ đang chơi trò chơi trong phòng.
2351|夏天我经常去游泳。|Mùa hè tôi thường đi bơi.
2352|别担心时间，我们有的是时间。|Đừng lo về thời gian, chúng ta còn rất nhiều thời gian.
2353|经常运动有利于身体健康。|Thường xuyên vận động có lợi cho sức khỏe.
2354|这个办法简单而且有效。|Phương pháp này đơn giản và hiệu quả.
2355|天气预报说明天可能下雨。|Dự báo thời tiết nói ngày mai có thể mưa.
2356|勤洗手可以预防一些疾病。|Rửa tay thường xuyên có thể phòng ngừa một số bệnh.
2357|火车预计下午五点到达。|Tàu dự kiến đến lúc năm giờ chiều.
2358|我每天晚上都会预习第二天的课文。|Mỗi tối tôi đều chuẩn bị trước bài học của ngày hôm sau.
2359|服务员给我们送来了菜单。|Nhân viên phục vụ đã mang thực đơn đến cho chúng tôi.
2360|公司为新员工安排了培训。|Công ty đã sắp xếp đào tạo cho nhân viên mới.
2361|我的愿望是有一天去中国旅行。|Nguyện vọng của tôi là một ngày nào đó được du lịch Trung Quốc.
2362|我和朋友约在地铁站见面。|Tôi hẹn gặp bạn ở ga tàu điện ngầm.
2363|这个乐队下个月要来这里演出。|Ban nhạc này tháng sau sẽ đến đây biểu diễn.
2364|这些水果每天从南方运输到这里。|Những loại trái cây này mỗi ngày được vận chuyển từ miền nam tới đây.
2365|我每个月都会买一本中文杂志。|Mỗi tháng tôi đều mua một cuốn tạp chí tiếng Trung.
2366|他早已知道这件事了。|Anh ấy đã biết việc này từ lâu rồi.
2367|这座桥花了三年才造好。|Cây cầu này mất ba năm mới xây xong.
2368|大雨给交通造成了很大影响。|Mưa lớn đã gây ảnh hưởng lớn đến giao thông.
2369|保护环境是每个人的责任。|Bảo vệ môi trường là trách nhiệm của mỗi người.
2370|今年学校增加了很多新课程。|Năm nay nhà trường đã tăng thêm nhiều môn học mới.
2371|这个城市的人口增长得很快。|Dân số thành phố này tăng rất nhanh.
2372|双方就这个问题展开了讨论。|Hai bên đã tiến hành thảo luận về vấn đề này.
2373|我买了两张电影票。|Tôi đã mua hai vé xem phim.
2374|请照老师说的方法练习。|Hãy luyện tập theo phương pháp giáo viên đã nói.
2375|很多志愿者参加了这次环保活动。|Nhiều tình nguyện viên đã tham gia hoạt động bảo vệ môi trường lần này.
2376|这个故事是根据真实事件写的。|Câu chuyện này được viết dựa trên sự kiện có thật.
2377|两个孩子正在争同一个玩具。|Hai đứa trẻ đang tranh nhau cùng một món đồ chơi.
2378|我们要努力争取更多学习机会。|Chúng ta phải cố gắng giành thêm nhiều cơ hội học tập.
2379|我在这里整整等了两个小时。|Tôi đã đợi ở đây tròn hai tiếng.
2380|整个教室都安静下来了。|Cả lớp học đều trở nên yên tĩnh.
2381|周末我在家整理房间。|Cuối tuần tôi ở nhà dọn dẹp phòng.
2382|同学们排着整齐的队伍进入会场。|Các học sinh xếp thành hàng ngay ngắn đi vào hội trường.
2383|从整体来看，这个计划很不错。|Xét về tổng thể, kế hoạch này khá tốt.
2384|他整天坐在电脑前工作。|Anh ấy ngồi trước máy tính làm việc suốt ngày.
2385|为了完成报告，我整整忙了三天。|Để hoàn thành báo cáo, tôi đã bận rộn suốt ba ngày.
2386|明天我们将正式开始上课。|Ngày mai chúng tôi sẽ chính thức bắt đầu học.
2387|进入学校时请出示学生证。|Khi vào trường hãy xuất trình thẻ sinh viên.
2388|办理手续时需要带有效证件。|Khi làm thủ tục cần mang giấy tờ hợp lệ.
2389|警察正在寻找更多证据。|Cảnh sát đang tìm thêm bằng chứng.
2390|这个实验可以证明他的想法是对的。|Thí nghiệm này có thể chứng minh suy nghĩ của anh ấy là đúng.
2391|桌子上放着三支笔。|Trên bàn có ba cây bút.
2392|父母一直支持我的决定。|Cha mẹ luôn ủng hộ quyết định của tôi.
2393|现在可以用手机支付车费。|Bây giờ có thể dùng điện thoại để thanh toán tiền xe.
2394|树上停着两只小鸟。|Trên cây có hai con chim nhỏ đang đậu.
2395|这条路又长又直。|Con đường này vừa dài vừa thẳng.
2396|这场比赛将在网上直播。|Trận đấu này sẽ được phát trực tiếp trên mạng.
2397|我一直学习到晚上十一点，直到做完作业才休息。|Tôi học đến tận mười một giờ tối, mãi đến khi làm xong bài tập mới nghỉ.
2398|这台电脑值五千元。|Chiếc máy tính này trị giá năm nghìn tệ.
2399|这本书很值得一读。|Quyển sách này rất đáng đọc.
2400|工厂为职工提供免费的午餐。|Nhà máy cung cấp bữa trưa miễn phí cho công nhân viên.
2401|医生是一个需要耐心的职业。|Bác sĩ là một nghề nghiệp đòi hỏi sự kiên nhẫn.
2402|最后一班公交车走了，我们只好打车回家。|Chuyến xe buýt cuối cùng đã đi nên chúng tôi đành bắt taxi về nhà.
2403|我不是不想去，只是今天没有时间。|Không phải tôi không muốn đi, chỉ là hôm nay không có thời gian.
2404|只有坚持练习，才能提高口语水平。|Chỉ khi kiên trì luyện tập mới có thể nâng cao trình độ nói.
2405|他指着地图告诉我怎么走。|Anh ấy chỉ vào bản đồ và nói cho tôi biết phải đi thế nào.
2406|老师指出了我作文中的几个错误。|Giáo viên đã chỉ ra vài lỗi trong bài văn của tôi.
2407|在老师的指导下，我完成了这个项目。|Dưới sự hướng dẫn của giáo viên, tôi đã hoàn thành dự án này.
2408|这首歌至今仍然很受欢迎。|Bài hát này đến nay vẫn rất được yêu thích.
2409|每天至少要睡七个小时。|Mỗi ngày ít nhất phải ngủ bảy tiếng.
2410|高考以后，他认真填写了大学志愿。|Sau kỳ thi đại học, anh ấy nghiêm túc điền nguyện vọng đại học.
2411|周末我去社区当志愿者。|Cuối tuần tôi đến khu dân cư làm tình nguyện viên.
2412|公司制定了明年的发展计划。|Công ty đã xây dựng kế hoạch phát triển cho năm sau.
2413|学校建立了新的管理制度。|Nhà trường đã xây dựng chế độ quản lý mới.
2414|这家工厂主要制造汽车零件。|Nhà máy này chủ yếu sản xuất linh kiện ô tô.
2415|妈妈教我制作中国饺子。|Mẹ dạy tôi làm bánh chẻo Trung Quốc.
2416|这个国家的中部有很多山区。|Khu vực miền trung của quốc gia này có nhiều vùng núi.
2417|中华民族有着悠久的历史和文化。|Dân tộc Trung Hoa có lịch sử và văn hóa lâu đời.
2418|经过几个小时的努力，我们终于完成了任务。|Sau vài giờ cố gắng, cuối cùng chúng tôi đã hoàn thành nhiệm vụ.
2419|墙上的钟已经停了。|Chiếc đồng hồ trên tường đã dừng chạy.
2420|超市里有很多种水果。|Trong siêu thị có rất nhiều loại trái cây.
2421|春天到了，农民开始播种种子。|Mùa xuân đến, nông dân bắt đầu gieo hạt giống.
2422|公司刚刚宣布了一项重大决定。|Công ty vừa công bố một quyết định quan trọng.
2423|学校周围有很多饭店和商店。|Xung quanh trường có nhiều nhà hàng và cửa hàng.
2424|农场里养了很多猪。|Trang trại nuôi rất nhiều lợn.
2425|这次会议由王老师主持。|Cuộc họp lần này do thầy Vương chủ trì.
2426|遇到问题时，我们应该主动想办法解决。|Khi gặp vấn đề, chúng ta nên chủ động tìm cách giải quyết.
2427|办公室主任正在开会。|Trưởng phòng đang họp.
2428|这个主意听起来不错，我们试试吧。|Ý tưởng này nghe khá hay, chúng ta thử nhé.
2429|他主张通过和平方式解决问题。|Anh ấy chủ trương giải quyết vấn đề bằng phương thức hòa bình.
2430|过马路时一定要注意安全。|Khi qua đường nhất định phải chú ý an toàn.
2431|祝你生日快乐，天天开心！|Chúc bạn sinh nhật vui vẻ và mỗi ngày đều hạnh phúc.
2432|小猫一直用爪子抓沙发。|Con mèo cứ dùng móng cào ghế sofa.
2433|过马路时，妈妈紧紧抓住孩子的手。|Khi qua đường, người mẹ nắm chặt tay đứa trẻ.
2434|医院请来了几位医学专家。|Bệnh viện đã mời một số chuyên gia y học.
2435|我今天专门来向你表示感谢。|Hôm nay tôi đặc biệt đến để cảm ơn bạn.
2436|电视台正在制作一个环保专题节目。|Đài truyền hình đang sản xuất một chương trình chuyên đề về môi trường.
2437|我的大学专业是计算机科学。|Chuyên ngành đại học của tôi là khoa học máy tính.
2438|到前面的路口向右转。|Đến ngã tư phía trước thì rẽ phải.
2439|互联网改变了人们的生活方式，也带来了很多转变。|Internet đã thay đổi cách sống của con người và cũng mang lại nhiều chuyển biến.
2440|医生正在了解病人的身体状况。|Bác sĩ đang tìm hiểu tình trạng sức khỏe của bệnh nhân.
2441|他今天的精神状态很好。|Trạng thái tinh thần của anh ấy hôm nay rất tốt.
2442|孩子看到小狗以后马上追了过去。|Đứa trẻ nhìn thấy chú chó rồi lập tức đuổi theo.
2443|你猜得真准，答案就是这个。|Bạn đoán rất chính xác, đáp án chính là cái này.
2444|你已经取得参加比赛的资格。|Bạn đã đạt đủ tư cách tham gia cuộc thi.
2445|公司需要更多资金来完成这个项目。|Công ty cần thêm vốn để hoàn thành dự án này.
2446|父母都希望子女健康快乐地成长。|Cha mẹ đều mong con cái lớn lên khỏe mạnh và vui vẻ.
2447|自从来到中国以后，我的汉语进步了很多。|Kể từ khi đến Trung Quốc, tiếng Trung của tôi đã tiến bộ rất nhiều.
2448|门靠近以后会自动打开。|Cánh cửa sẽ tự động mở khi đến gần.
2449|学生应该自觉遵守学校规定。|Học sinh nên tự giác tuân thủ quy định của trường.
2450|周末我们喜欢去自然环境好的地方散步。|Cuối tuần chúng tôi thích đi dạo ở những nơi có môi trường tự nhiên đẹp.
2451|学习语言也能提高自身能力。|Học ngôn ngữ cũng có thể nâng cao năng lực của bản thân.
2452|大学生应该培养自主学习的能力。|Sinh viên đại học nên rèn luyện năng lực tự học.
2453|他总喜欢在睡觉前看一会儿书。|Anh ấy luôn thích đọc sách một lúc trước khi ngủ.
2454|会议结束后，经理总结了今天的工作。|Sau khi cuộc họp kết thúc, quản lý đã tổng kết công việc hôm nay.
2455|她总是提前十分钟到教室。|Cô ấy luôn đến lớp sớm mười phút.
2456|这些食物足够我们吃三天。|Số thức ăn này đủ cho chúng ta ăn ba ngày.
2457|弟弟每个周末都和朋友踢足球。|Em trai mỗi cuối tuần đều đá bóng với bạn.
2458|我们可以把这些图片组合成一张海报。|Chúng ta có thể kết hợp những hình ảnh này thành một tấm áp phích.
2459|从学校到我家大约需要二十分钟左右。|Từ trường đến nhà tôi mất khoảng hai mươi phút.
2460|这幅画是这位艺术家最有名的作品。|Bức tranh này là tác phẩm nổi tiếng nhất của nghệ sĩ này.
2461|这本小说的作者是一位年轻作家。|Tác giả của cuốn tiểu thuyết này là một nhà văn trẻ.
2462|这个周末我们去老师家做客。|Cuối tuần này chúng tôi đến nhà giáo viên làm khách.
"""


def normalize_target(word):
    """
    Chuẩn hóa từ mục tiêu để kiểm tra câu ví dụ.

    Ví dụ:
        员（服务员） -> 服务员
        者（志愿者） -> 志愿者
        称1 -> 称
    """
    word = (word or "").strip()

    # Nếu ChuHan có ví dụ trong ngoặc Trung Quốc:
    # 员（服务员） -> 服务员
    match = re.search(r"（([^（）]+)）", word)
    if match:
        return match.group(1).strip()

    # Bỏ số đánh dấu đồng hình nếu có.
    word = re.sub(r"\d+$", "", word)

    return word.strip()


def parse_examples():
    result = {}

    for line_number, raw_line in enumerate(
        EXAMPLES.strip().splitlines(),
        start=1
    ):
        line = raw_line.strip()

        if not line:
            continue

        parts = line.split("|")

        if len(parts) != 3:
            raise ValueError(
                f"EXAMPLES dòng {line_number} sai định dạng:\n"
                f"{raw_line}"
            )

        word_id_text, chinese, vietnamese = parts

        word_id = int(word_id_text.strip())
        chinese = chinese.strip()
        vietnamese = vietnamese.strip()

        if word_id in result:
            raise ValueError(
                f"EXAMPLES bị trùng MaTuVung={word_id}"
            )

        if not chinese:
            raise ValueError(
                f"MaTuVung={word_id}: câu tiếng Trung rỗng"
            )

        if not vietnamese:
            raise ValueError(
                f"MaTuVung={word_id}: câu tiếng Việt rỗng"
            )

        result[word_id] = (chinese, vietnamese)

    return result


def main():
    print()
    print("=" * 62)
    print("HSK3 - BATCH 5 (FINAL)")
    print("=" * 62)

    # ------------------------------------------------------
    # 1. Kiểm tra file nguồn
    # ------------------------------------------------------
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file nguồn:\n{SOURCE}"
        )

    fixes = parse_examples()

    # 2302 -> 2462 có 161 ID.
    # 2313 đã READY từ đầu nên Batch 5 chỉ sửa 160 ID.
    expected = set(range(2302, 2463))
    expected.remove(2313)

    actual = set(fixes)

    missing = expected - actual
    extra = actual - expected

    if missing or extra:
        raise ValueError(
            "\nDanh sách EXAMPLES không đúng.\n"
            f"Thiếu ID: {sorted(missing)}\n"
            f"Thừa ID: {sorted(extra)}"
        )

    if len(fixes) != 160:
        raise ValueError(
            f"Batch 5 phải có đúng 160 câu, "
            f"hiện có {len(fixes)} câu."
        )

    # ------------------------------------------------------
    # 2. Đọc CSV
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
        raise ValueError("Không đọc được header của CSV.")

    required_columns = {
        "MaTuVung",
        "HSK",
        "ChuHan",
        "NghiaTiengViet",
        "TuLoai",
        "ViDuTiengTrung",
        "ViDuTiengViet",
        "LoaiCau",
        "TrangThaiImport",
    }

    missing_columns = required_columns - set(fields)

    if missing_columns:
        raise ValueError(
            "CSV thiếu các cột bắt buộc: "
            f"{sorted(missing_columns)}"
        )

    if len(rows) != 961:
        raise ValueError(
            "Số dòng HSK3 không đúng.\n"
            f"Dự kiến: 961\n"
            f"Thực tế : {len(rows)}"
        )

    # ------------------------------------------------------
    # 3. Lập index theo MaTuVung
    # ------------------------------------------------------
    by_id = {}

    for row in rows:
        word_id = int(row["MaTuVung"])

        if word_id in by_id:
            raise ValueError(
                f"CSV có MaTuVung bị trùng: {word_id}"
            )

        by_id[word_id] = row

    missing_in_csv = expected - set(by_id)

    if missing_in_csv:
        raise ValueError(
            f"CSV thiếu các MaTuVung: "
            f"{sorted(missing_in_csv)}"
        )

    # ------------------------------------------------------
    # 4. Đảm bảo 2313 vẫn là READY
    # ------------------------------------------------------
    row_2313 = by_id.get(2313)

    if row_2313 is None:
        raise ValueError(
            "Không tìm thấy MaTuVung=2313 (压力)."
        )

    if row_2313["ChuHan"].strip() != "压力":
        raise ValueError(
            "MaTuVung=2313 không phải từ 压力."
        )

    if row_2313["TrangThaiImport"].strip() != "READY":
        raise ValueError(
            "MaTuVung=2313 (压力) lẽ ra phải READY.\n"
            "Dừng để tránh ghi sai dữ liệu."
        )

    # ------------------------------------------------------
    # 5. Kiểm tra 160 dòng trước khi sửa
    # ------------------------------------------------------
    errors = []

    for word_id in sorted(expected):
        row = by_id[word_id]

        chinese, vietnamese = fixes[word_id]

        raw_word = row["ChuHan"].strip()
        target = normalize_target(raw_word)

        status = row["TrangThaiImport"].strip()

        if row["HSK"].strip() != "3":
            errors.append(
                f"{word_id}: HSK không phải 3"
            )

        if status != "NEED_REVIEW":
            errors.append(
                f"{word_id} {raw_word}: "
                f"status={status}, dự kiến NEED_REVIEW"
            )

        if not target:
            errors.append(
                f"{word_id}: không xác định được từ mục tiêu"
            )

        elif target not in chinese:
            errors.append(
                f"{word_id} {raw_word}: "
                f"câu không chứa '{target}' -> {chinese}"
            )

        if chinese in {
            row["ViDuTiengTrung"].strip()
        }:
            errors.append(
                f"{word_id} {raw_word}: "
                "câu mới trùng câu template cũ"
            )

        if not vietnamese:
            errors.append(
                f"{word_id}: bản dịch tiếng Việt rỗng"
            )

    if errors:
        print()
        print("PHÁT HIỆN LỖI:")
        print("-" * 62)

        for error in errors:
            print(error)

        print("-" * 62)

        raise ValueError(
            "DỪNG: dữ liệu Batch 5 chưa hợp lệ. "
            "CHƯA ghi file."
        )

    # ------------------------------------------------------
    # 6. Cập nhật 160 câu
    # ------------------------------------------------------
    for word_id in sorted(expected):
        row = by_id[word_id]

        chinese, vietnamese = fixes[word_id]

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

    # ------------------------------------------------------
    # 7. Kiểm tra kết quả cuối cùng
    # ------------------------------------------------------
    ready_rows = [
        row for row in rows
        if row["TrangThaiImport"].strip() == "READY"
    ]

    review_rows = [
        row for row in rows
        if row["TrangThaiImport"].strip() == "NEED_REVIEW"
    ]

    template_rows = [
        row for row in rows
        if row["LoaiCau"].strip() == "TEMPLATE"
    ]

    ready_count = len(ready_rows)
    review_count = len(review_rows)

    if ready_count != 961:
        raise ValueError(
            f"READY phải bằng 961, "
            f"hiện tại = {ready_count}. "
            "CHƯA ghi file."
        )

    if review_count != 0:
        raise ValueError(
            f"NEED_REVIEW phải bằng 0, "
            f"hiện tại = {review_count}. "
            "CHƯA ghi file."
        )

    if template_rows:
        ids = [
            row["MaTuVung"]
            for row in template_rows[:20]
        ]

        raise ValueError(
            "Vẫn còn câu TEMPLATE sau Batch 5.\n"
            f"Ví dụ MaTuVung: {ids}\n"
            "CHƯA ghi file."
        )

    # ------------------------------------------------------
    # 8. Ghi CSV mới
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
    # 9. Báo cáo
    # ------------------------------------------------------
    print()
    print("VALIDATION PASS")
    print()
    print("Đã sửa thêm              : 160 câu")
    print("Bỏ qua 2313 压力          : READY từ trước")
    print(f"Tổng READY               : {ready_count}")
    print(f"Còn NEED_REVIEW          : {review_count}")
    print(f"Còn TEMPLATE             : {len(template_rows)}")
    print()
    print(f"File mới:\n{OUTPUT}")
    print()
    print("CHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 62)


if __name__ == "__main__":
    main()