
import csv
from collections import Counter
from pathlib import Path

# =========================================================
# HSK4 - BATCH 2
# MaTuVung 2702 -> 2901
# 200 câu ví dụ Trung - Việt
# KHÔNG thay đổi SQL Server
# =========================================================

DATA_DIR = Path(__file__).resolve().parent / "data"
SOURCE = DATA_DIR / "offline_preview_hsk4.csv"
OUTPUT = DATA_DIR / "offline_preview_hsk4_batch2.csv"

EXAMPLES = """
2702|把这两张照片放在一起对比，区别就很明显了。|Đặt hai bức ảnh này cạnh nhau so sánh thì sẽ thấy sự khác biệt rất rõ.
2703|面对这样的困难，我们必须想办法对付。|Đối mặt với khó khăn như vậy, chúng ta phải nghĩ cách giải quyết.
2704|对于这个问题，每个人都有不同的看法。|Đối với vấn đề này, mỗi người đều có cách nhìn khác nhau.
2705|他多次尝试以后，终于解决了这个问题。|Sau nhiều lần thử, cuối cùng anh ấy đã giải quyết được vấn đề.
2706|我们已经是多年的好朋友了。|Chúng tôi đã là bạn tốt của nhau nhiều năm rồi.
2707|学校开展了形式多样的文化活动。|Nhà trường tổ chức các hoạt động văn hóa với hình thức đa dạng.
2708|这家餐厅提供多种不同口味的面条。|Nhà hàng này phục vụ nhiều loại mì với các hương vị khác nhau.
2709|坐车时看手机让我觉得有点恶心。|Xem điện thoại khi đi xe khiến tôi hơi buồn nôn.
2710|这个公园专门设置了儿童游乐区。|Công viên này có khu vui chơi dành riêng cho trẻ em.
2711|成功不是靠运气，而是靠长期的努力。|Thành công không dựa vào may mắn mà dựa vào nỗ lực lâu dài.
2712|我不是不想参加，而是今天实在没有时间。|Không phải tôi không muốn tham gia mà là hôm nay thực sự không có thời gian.
2713|我的耳机坏了，只能用手机听音乐。|Tai nghe của tôi hỏng rồi nên chỉ có thể nghe nhạc bằng điện thoại.
2714|为了省钱，他买了一辆二手自行车。|Để tiết kiệm tiền, anh ấy mua một chiếc xe đạp cũ.
2715|比赛时他充分发挥了自己的优势。|Trong cuộc thi, anh ấy đã phát huy tối đa thế mạnh của mình.
2716|买完电脑后，请记得向商家索要发票。|Sau khi mua máy tính, hãy nhớ yêu cầu người bán xuất hóa đơn.
2717|妹妹昨晚发烧了，今天没有去学校。|Em gái tối qua bị sốt nên hôm nay không đến trường.
2718|解决这个问题还有没有别的法子？|Có còn cách nào khác để giải quyết vấn đề này không?
2719|法官认真听取了双方的意见。|Thẩm phán đã chăm chú lắng nghe ý kiến của hai bên.
2720|每个人都应该遵守国家的法律。|Mọi người đều nên tuân thủ pháp luật của đất nước.
2721|法院将在下个月审理这起案件。|Tòa án sẽ xét xử vụ án này vào tháng sau.
2722|他把书翻到最后一页，找到了答案。|Anh ấy lật sách đến trang cuối và tìm thấy đáp án.
2723|这份中文合同需要翻译成越南语。|Hợp đồng tiếng Trung này cần được dịch sang tiếng Việt.
2724|外面一直有人说话，真让人烦。|Bên ngoài cứ có người nói chuyện, thật khiến người ta phiền lòng.
2725|你把这件衣服穿反了，快换过来吧。|Bạn mặc ngược chiếc áo này rồi, mau mặc lại đi.
2726|他没有生气，反而笑了起来。|Anh ấy không tức giận mà ngược lại còn bật cười.
2727|这份报告反映了学生的真实需求。|Báo cáo này phản ánh nhu cầu thực tế của học sinh.
2728|我们可以从不同的方向观察这个问题。|Chúng ta có thể quan sát vấn đề này từ những phương hướng khác nhau.
2729|经理提出了一个新的工作方案。|Giám đốc đã đưa ra một phương án làm việc mới.
2730|公司根据新的发展方针调整了计划。|Công ty đã điều chỉnh kế hoạch theo phương châm phát triển mới.
2731|考试结束后，我想去海边放松一下。|Sau khi thi xong, tôi muốn ra biển thư giãn một chút.
2732|这件事情非你亲自去办不可。|Việc này nhất định phải do chính bạn đi giải quyết.
2733|这块肉太肥了，我不太喜欢吃。|Miếng thịt này nhiều mỡ quá, tôi không thích ăn lắm.
2734|这些学校主要分布在城市的东部。|Những trường học này chủ yếu phân bố ở phía đông thành phố.
2735|请大家不要分散注意力，认真听讲。|Mọi người đừng phân tán sự chú ý, hãy chăm chú nghe giảng.
2736|他们因为性格不合，最后决定分手。|Vì tính cách không hợp, cuối cùng họ quyết định chia tay.
2737|这次比赛分为初赛和决赛两个阶段。|Cuộc thi lần này được chia thành hai giai đoạn vòng loại và chung kết.
2738|全班三分之二的学生参加了这次活动。|Hai phần ba số học sinh trong lớp đã tham gia hoạt động lần này.
2739|下课铃一响，同学们纷纷走出教室。|Chuông tan học vừa reo, các bạn học sinh lần lượt đi ra khỏi lớp.
2740|为了实现自己的梦想，他一直努力奋斗。|Để thực hiện ước mơ, anh ấy luôn nỗ lực phấn đấu.
2741|这家咖啡馆的装修风格很特别。|Phong cách trang trí của quán cà phê này rất đặc biệt.
2742|从山顶往下看，风景非常美丽。|Từ đỉnh núi nhìn xuống, phong cảnh vô cùng đẹp.
2743|每个地方都有自己独特的风俗习惯。|Mỗi địa phương đều có những phong tục tập quán riêng.
2744|由于道路施工，这条街暂时封闭了。|Do thi công đường, con phố này tạm thời bị phong tỏa.
2745|请按时出发，否则会错过火车。|Hãy xuất phát đúng giờ, nếu không sẽ lỡ tàu.
2746|那对老夫妇每天傍晚都会一起散步。|Đôi vợ chồng già ấy chiều nào cũng cùng nhau đi dạo.
2747|这对夫妻结婚十年了，感情一直很好。|Đôi vợ chồng này kết hôn mười năm rồi, tình cảm vẫn rất tốt.
2748|王先生和他的夫人一起参加了晚宴。|Ông Vương và phu nhân cùng tham dự tiệc tối.
2749|地图上的红色符号代表医院。|Ký hiệu màu đỏ trên bản đồ đại diện cho bệnh viện.
2750|你的申请符合这次招聘的基本条件。|Đơn ứng tuyển của bạn đáp ứng các điều kiện cơ bản của đợt tuyển dụng này.
2751|父母为孩子的成长付出了很多心血。|Cha mẹ đã bỏ ra rất nhiều tâm sức vì sự trưởng thành của con cái.
2752|房租越来越贵，给年轻人带来了很大负担。|Tiền thuê nhà ngày càng đắt, tạo ra gánh nặng lớn cho người trẻ.
2753|我家附近新开了一家书店。|Gần nhà tôi vừa mở một hiệu sách mới.
2754|请先复制这份文件，再进行修改。|Hãy sao chép tài liệu này trước rồi mới chỉnh sửa.
2755|我们正在努力改善学校的学习环境。|Chúng tôi đang nỗ lực cải thiện môi trường học tập của trường.
2756|发现错误以后，他马上改正了。|Sau khi phát hiện lỗi, anh ấy đã sửa ngay.
2757|出门前记得把锅盖盖好。|Trước khi ra ngoài nhớ đậy nắp nồi cho kỹ.
2758|请用几句话概括这篇文章的主要内容。|Hãy dùng vài câu tóm tắt nội dung chính của bài viết này.
2759|我对中国历史很感兴趣。|Tôi rất hứng thú với lịch sử Trung Quốc.
2760|故事到了最高潮时，大家都紧张起来。|Khi câu chuyện đến cao trào, mọi người đều căng thẳng.
2761|这家商店不允许商家以高价出售普通口罩。|Cửa hàng này không cho phép người bán bán khẩu trang thông thường với giá cao.
2762|她主动帮助陌生人，表现出高尚的品格。|Cô ấy chủ động giúp người lạ, thể hiện phẩm chất cao đẹp.
2763|从北京到上海坐高铁非常方便。|Đi tàu cao tốc từ Bắc Kinh đến Thượng Hải rất thuận tiện.
2764|今天的天气格外晴朗，适合出去走走。|Hôm nay trời đặc biệt quang đãng, thích hợp ra ngoài dạo chơi.
2765|我的座位和他的座位只隔了一条走道。|Chỗ ngồi của tôi và anh ấy chỉ cách nhau một lối đi.
2766|工作人员用一块板把两个区域隔开了。|Nhân viên dùng một tấm ván ngăn hai khu vực ra.
2767|大部分同学都同意，只有个别同学反对。|Phần lớn học sinh đều đồng ý, chỉ có một vài bạn phản đối.
2768|我们应该尊重每一个个体的选择。|Chúng ta nên tôn trọng lựa chọn của mỗi cá nhân.
2769|各个部门都需要提交本月的工作报告。|Các bộ phận đều cần nộp báo cáo công việc tháng này.
2770|他从地上捡起一根细长的木棍。|Anh ấy nhặt một thanh gỗ dài và nhỏ dưới đất.
2771|根据天气预报，明天可能会下雨。|Theo dự báo thời tiết, ngày mai có thể mưa.
2772|这项工程预计明年年底完工。|Công trình này dự kiến hoàn thành vào cuối năm sau.
2773|公元二〇〇八年，北京举办了奥运会。|Năm 2008 Công nguyên, Bắc Kinh đã tổ chức Thế vận hội.
2774|这家公司负责向学校供应新鲜蔬菜。|Công ty này phụ trách cung cấp rau tươi cho các trường học.
2775|我们一共买了六张电影票。|Chúng tôi đã mua tổng cộng sáu vé xem phim.
2776|空气主要由氮气和氧气构成。|Không khí chủ yếu được cấu thành từ nitơ và oxy.
2777|这座桥的构造十分特别。|Kết cấu của cây cầu này rất đặc biệt.
2778|购买电子产品时，最好先比较价格。|Khi mua sản phẩm điện tử, tốt nhất nên so sánh giá trước.
2779|周末我喜欢和朋友一起去购物。|Cuối tuần tôi thích đi mua sắm cùng bạn bè.
2780|他摔倒后觉得腿上的骨头很疼。|Sau khi ngã, anh ấy cảm thấy xương chân rất đau.
2781|请把这张桌子固定在墙边。|Hãy cố định chiếc bàn này sát tường.
2782|夏天我喜欢吃西瓜，也喜欢吃其他的瓜。|Mùa hè tôi thích ăn dưa hấu và các loại dưa khác.
2783|今天他一直不说话，感觉有点怪。|Hôm nay anh ấy cứ im lặng, cảm giác hơi kỳ lạ.
2784|离开办公室之前，请关闭所有电脑。|Trước khi rời văn phòng, hãy tắt tất cả máy tính.
2785|关于这次旅行的安排，我们明天再讨论。|Về việc sắp xếp chuyến đi lần này, ngày mai chúng ta sẽ bàn tiếp.
2786|古代的地方官负责管理当地事务。|Quan địa phương thời xưa phụ trách quản lý công việc ở địa phương.
2787|请以官方发布的通知为准。|Hãy căn cứ vào thông báo do phía chính thức công bố.
2788|欢迎各位光临我们的新店！|Chào mừng quý khách đến với cửa hàng mới của chúng tôi!
2789|我在书柜里找到了一张旧光盘。|Tôi tìm thấy một chiếc đĩa CD cũ trong tủ sách.
2790|吃完晚饭后，我们去商场逛了一会儿。|Sau bữa tối, chúng tôi đi dạo trung tâm thương mại một lát.
2791|这本书应该归图书馆所有。|Cuốn sách này thuộc sở hữu của thư viện.
2792|只要仔细观察，就能发现其中的规律。|Chỉ cần quan sát kỹ là có thể phát hiện quy luật trong đó.
2793|这家公司近几年不断扩大经营规模。|Những năm gần đây công ty này không ngừng mở rộng quy mô kinh doanh.
2794|参加比赛之前，请先了解比赛规则。|Trước khi tham gia thi đấu, hãy tìm hiểu luật thi đấu.
2795|秋天到了，树上的果实渐渐成熟了。|Mùa thu đến, trái trên cây dần chín.
2796|你不用过分担心，事情没有那么严重。|Bạn không cần lo lắng quá mức, sự việc không nghiêm trọng đến vậy.
2797|这里的海水非常清澈，可以看到海底。|Nước biển ở đây rất trong, có thể nhìn thấy đáy biển.
2798|这家餐厅的海鲜很新鲜。|Hải sản ở nhà hàng này rất tươi.
2799|这种饮料含少量咖啡因。|Loại đồ uống này chứa một lượng nhỏ caffeine.
2800|买食品时，我会注意包装上的糖含量。|Khi mua thực phẩm, tôi chú ý đến hàm lượng đường trên bao bì.
2801|这个手势在不同文化中有不同的含义。|Cử chỉ này mang ý nghĩa khác nhau trong các nền văn hóa.
2802|这种水果含有丰富的维生素。|Loại trái cây này chứa nhiều vitamin.
2803|今年寒假，我打算回老家看爷爷奶奶。|Kỳ nghỉ đông năm nay, tôi định về quê thăm ông bà.
2804|北方的冬天十分寒冷，出门要穿厚衣服。|Mùa đông miền bắc rất lạnh, ra ngoài phải mặc quần áo dày.
2805|她毕业以后进入了旅游行业。|Sau khi tốt nghiệp, cô ấy bước vào ngành du lịch.
2806|因为天气原因，今天有几个航班延误了。|Vì thời tiết, hôm nay có vài chuyến bay bị hoãn.
2807|他一直梦想成为一名航空工程师。|Anh ấy luôn mơ ước trở thành kỹ sư hàng không.
2808|这张纸的厚度不到一毫米。|Độ dày của tờ giấy này chưa đến một milimét.
2809|请往杯子里倒入二百毫升牛奶。|Hãy đổ hai trăm mililít sữa vào cốc.
2810|虽然毕业多年，我们几个好友还经常联系。|Dù đã tốt nghiệp nhiều năm, mấy người bạn thân chúng tôi vẫn thường liên lạc.
2811|请留下你的电话号码，方便我们联系。|Hãy để lại số điện thoại để chúng tôi tiện liên lạc.
2812|这件事情已经处理好了，你放心吧。|Việc này đã được xử lý xong rồi, bạn cứ yên tâm.
2813|签合同之前，一定要仔细阅读所有条款。|Trước khi ký hợp đồng, nhất định phải đọc kỹ tất cả điều khoản.
2814|突然停电了，整个房间陷入黑暗。|Điện đột nhiên mất, cả căn phòng chìm trong bóng tối.
2815|过年的时候，长辈会给孩子们发红包。|Vào dịp Tết, người lớn sẽ lì xì cho trẻ em.
2816|我坐在教室前面，他坐在后头。|Tôi ngồi phía trước lớp, còn anh ấy ngồi phía sau.
2817|这本书很厚，我一个星期也看不完。|Cuốn sách này rất dày, tôi đọc cả tuần cũng không hết.
2818|跑步以后，他停下来慢慢调整呼吸。|Sau khi chạy, anh ấy dừng lại điều chỉnh nhịp thở.
2819|我们不能忽视孩子们的心理健康。|Chúng ta không thể xem nhẹ sức khỏe tinh thần của trẻ em.
2820|这栋楼一共有三十户居民。|Tòa nhà này có tổng cộng ba mươi hộ dân.
2821|护士正在给病人测量血压。|Y tá đang đo huyết áp cho bệnh nhân.
2822|孩子们在湖上划船，玩得很开心。|Bọn trẻ chèo thuyền trên hồ, chơi rất vui.
2823|请先划出文章中的重点句子。|Hãy gạch ra những câu trọng tâm trong bài viết trước.
2824|离开家乡以后，我常常怀念小时候的生活。|Sau khi xa quê, tôi thường nhớ cuộc sống thời thơ ấu.
2825|我怀疑他把开会的时间记错了。|Tôi nghi anh ấy đã nhớ nhầm giờ họp.
2826|听音乐可以帮助我缓解工作压力。|Nghe nhạc có thể giúp tôi giảm căng thẳng công việc.
2827|妈妈用黄瓜做了一道凉菜。|Mẹ dùng dưa chuột làm một món rau trộn.
2828|这条项链是用黄金做的。|Chiếc vòng cổ này được làm bằng vàng.
2829|我已经收到邮件，今晚会给你回复。|Tôi đã nhận được email và tối nay sẽ trả lời bạn.
2830|来自各地的河流最终汇入这片湖。|Các dòng sông từ nhiều nơi cuối cùng đổ vào hồ này.
2831|明天上午，我要向经理汇报工作进度。|Sáng mai tôi phải báo cáo tiến độ công việc với giám đốc.
2832|出国旅行之前，最好先了解当地汇率。|Trước khi du lịch nước ngoài, tốt nhất nên tìm hiểu tỷ giá địa phương.
2833|他们的婚礼将在下个月举行。|Đám cưới của họ sẽ được tổ chức vào tháng sau.
2834|这伙年轻人经常一起踢足球。|Nhóm thanh niên này thường cùng nhau chơi bóng đá.
2835|我们不仅是同事，也是互相支持的伙伴。|Chúng tôi không chỉ là đồng nghiệp mà còn là những người bạn đồng hành hỗ trợ nhau.
2836|他今天没来，或许是因为身体不舒服。|Hôm nay anh ấy không đến, có lẽ vì không khỏe.
2837|这批货明天早上就能送到。|Lô hàng này sáng mai sẽ được giao đến.
2838|这次比赛我们获了不少奖。|Cuộc thi lần này chúng tôi đã giành được khá nhiều giải thưởng.
2839|经过努力，她终于获得了奖学金。|Sau nhiều nỗ lực, cuối cùng cô ấy đã nhận được học bổng.
2840|听说自己获奖了，他高兴得跳了起来。|Nghe tin mình đoạt giải, anh ấy vui đến mức nhảy cẫng lên.
2841|你可以通过官方网站获取最新消息。|Bạn có thể lấy thông tin mới nhất qua trang web chính thức.
2842|昨天晚上我几乎没有睡觉。|Tối qua tôi hầu như không ngủ.
2843|这家机构专门为老人提供服务。|Tổ chức này chuyên cung cấp dịch vụ cho người cao tuổi.
2844|这次实习给我带来了难得的机遇。|Đợt thực tập này mang đến cho tôi một cơ hội hiếm có.
2845|学习语言需要长期积累词汇和经验。|Học ngôn ngữ cần tích lũy từ vựng và kinh nghiệm lâu dài.
2846|听到自己被录取的消息，她非常激动。|Nghe tin mình được nhận, cô ấy vô cùng xúc động.
2847|双方进行了十分激烈的讨论。|Hai bên đã có cuộc thảo luận rất sôi nổi.
2848|这次考试只要达到六十分就算及格。|Kỳ thi này chỉ cần đạt sáu mươi điểm là được tính là đỗ.
2849|这件事极有可能影响我们的计划。|Việc này rất có thể ảnh hưởng đến kế hoạch của chúng ta.
2850|这条山路极其危险，晚上不要走。|Con đường núi này cực kỳ nguy hiểm, đừng đi vào ban đêm.
2851|比赛即将开始，请大家尽快入场。|Cuộc thi sắp bắt đầu, mọi người hãy nhanh chóng vào chỗ.
2852|听到有人求救，他急忙跑了过去。|Nghe có người kêu cứu, anh ấy vội vàng chạy đến.
2853|请所有同学八点在学校门口集合。|Mời tất cả học sinh tập trung ở cổng trường lúc tám giờ.
2854|这本书详细记载了当地的历史。|Cuốn sách này ghi chép chi tiết lịch sử địa phương.
2855|上课时要遵守课堂纪律。|Khi học phải tuân thủ kỷ luật lớp học.
2856|掌握正确的学习技巧可以提高效率。|Nắm vững kỹ năng học tập đúng cách có thể nâng cao hiệu quả.
2857|出发前请把安全带系好。|Trước khi xuất phát hãy thắt dây an toàn cho kỹ.
2858|春天是我最喜欢的一季。|Mùa xuân là mùa tôi yêu thích nhất.
2859|公司每个季度都会总结一次工作情况。|Công ty mỗi quý đều tổng kết tình hình công việc một lần.
2860|这个季节天气变化很大，要注意身体。|Mùa này thời tiết thay đổi nhiều, cần chú ý sức khỏe.
2861|他既认真又负责，大家都很信任他。|Anh ấy vừa nghiêm túc vừa có trách nhiệm nên mọi người rất tin tưởng.
2862|既然已经决定了，就不要轻易放弃。|Đã quyết định rồi thì đừng dễ dàng bỏ cuộc.
2863|我昨天寄了一封信给远方的朋友。|Hôm qua tôi gửi một lá thư cho người bạn ở xa.
2864|最近项目比较忙，我们经常需要加班。|Gần đây dự án khá bận nên chúng tôi thường phải làm thêm giờ.
2865|欢迎更多同学加入我们的学习小组。|Hoan nghênh thêm nhiều bạn tham gia nhóm học tập của chúng tôi.
2866|前面有一家加油站，我们可以在那里休息。|Phía trước có một trạm xăng, chúng ta có thể nghỉ ở đó.
2867|周末我会帮父母做一些家务。|Cuối tuần tôi sẽ giúp bố mẹ làm một số việc nhà.
2868|假如明天下雨，我们就改在室内活动。|Giả sử ngày mai trời mưa, chúng ta sẽ chuyển sang hoạt động trong nhà.
2869|这座桥非常坚固，可以承受很大的重量。|Cây cầu này rất vững chắc, có thể chịu được trọng lượng lớn.
2870|工作人员正在检测饮用水的质量。|Nhân viên đang kiểm tra chất lượng nước uống.
2871|今年的生活费用比去年减了一些。|Chi phí sinh hoạt năm nay đã giảm một chút so với năm ngoái.
2872|为了减肥，他开始控制饮食并坚持运动。|Để giảm cân, anh ấy bắt đầu kiểm soát ăn uống và kiên trì tập thể dục.
2873|使用电子文件可以减少纸张浪费。|Sử dụng tài liệu điện tử có thể giảm lãng phí giấy.
2874|申请这份工作时，需要提交个人简历。|Khi ứng tuyển công việc này, cần nộp sơ yếu lý lịch cá nhân.
2875|下班后，他经常去健身房健身。|Sau giờ làm, anh ấy thường đến phòng tập để rèn luyện sức khỏe.
2876|天渐渐黑了，我们应该回家了。|Trời dần tối rồi, chúng ta nên về nhà thôi.
2877|这条江流经好几个城市。|Con sông này chảy qua nhiều thành phố.
2878|这家餐厅很讲究食材的新鲜程度。|Nhà hàng này rất chú trọng độ tươi của nguyên liệu.
2879|学校邀请了一位专家来做讲座。|Nhà trường mời một chuyên gia đến tổ chức buổi nói chuyện chuyên đề.
2880|她在比赛中获得了一等奖。|Cô ấy giành giải nhất trong cuộc thi.
2881|公司决定给表现优秀的员工发奖金。|Công ty quyết định thưởng tiền cho nhân viên có thành tích tốt.
2882|因为成绩优秀，他申请到了奖学金。|Vì thành tích học tập xuất sắc, anh ấy đã xin được học bổng.
2883|夜里气温突然降了好几度。|Ban đêm nhiệt độ đột nhiên giảm vài độ.
2884|我们应该采取措施降低生产成本。|Chúng ta nên áp dụng biện pháp để giảm chi phí sản xuất.
2885|这款手机下个月可能会降价。|Mẫu điện thoại này có thể giảm giá vào tháng sau.
2886|飞机将在十分钟后降落。|Máy bay sẽ hạ cánh sau mười phút nữa.
2887|天气预报说明天会明显降温。|Dự báo thời tiết cho biết ngày mai nhiệt độ sẽ giảm rõ rệt.
2888|我们互相交换了联系方式。|Chúng tôi đã trao đổi thông tin liên lạc với nhau.
2889|多参加集体活动有助于提高交际能力。|Tham gia nhiều hoạt động tập thể giúp nâng cao khả năng giao tiếp.
2890|这位教授正在研究中国古代文学。|Vị giáo sư này đang nghiên cứu văn học Trung Quốc cổ đại.
2891|这次失败给了我一个深刻的教训。|Thất bại lần này cho tôi một bài học sâu sắc.
2892|项目目前已经进入最后一个阶段。|Dự án hiện đã bước vào giai đoạn cuối cùng.
2893|这条街道两旁种了很多树。|Hai bên con đường này trồng rất nhiều cây.
2894|自己做饭可以节省不少生活费。|Tự nấu ăn có thể tiết kiệm khá nhiều chi phí sinh hoạt.
2895|她把长头发结成了一个辫子。|Cô ấy tết mái tóc dài thành một bím tóc.
2896|这篇文章的结构很清楚，读起来很容易理解。|Cấu trúc bài viết này rất rõ ràng nên đọc khá dễ hiểu.
2897|经过认真分析，我们得出了相同的结论。|Sau khi phân tích kỹ, chúng tôi đã đi đến cùng một kết luận.
2898|她们虽然不是亲姐妹，却像一家人一样亲密。|Tuy không phải chị em ruột nhưng họ thân thiết như người một nhà.
2899|老师耐心地解释了这道题的解法。|Giáo viên kiên nhẫn giải thích cách giải bài này.
2900|请尽快把修改后的文件发给我。|Hãy gửi cho tôi tài liệu đã sửa trong thời gian sớm nhất.
2901|这两个部门保持着紧密的合作关系。|Hai bộ phận này duy trì mối quan hệ hợp tác chặt chẽ.
"""


def load_examples():
    fixes = {}

    for number, raw in enumerate(EXAMPLES.strip().splitlines(), 1):
        parts = raw.strip().split("|")

        if len(parts) != 3:
            raise ValueError(f"Sai định dạng dòng {number}: {raw}")

        word_id = int(parts[0])
        chinese = parts[1].strip()
        vietnamese = parts[2].strip()

        if word_id in fixes:
            raise ValueError(f"Trùng ID trong dữ liệu mới: {word_id}")

        if not chinese or not vietnamese:
            raise ValueError(f"Câu ví dụ rỗng: {word_id}")

        fixes[word_id] = (chinese, vietnamese)

    expected = set(range(2702, 2902))

    if set(fixes) != expected:
        raise ValueError(
            f"Thiếu ID: {sorted(expected - set(fixes))}\n"
            f"Thừa ID: {sorted(set(fixes) - expected)}"
        )

    return fixes


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Không tìm thấy {SOURCE}")

    fixes = load_examples()

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    required = {
        "MaTuVung", "HSK", "ChuHan",
        "ViDuTiengTrung", "ViDuTiengViet",
        "LoaiCau", "TrangThaiImport",
    }

    if not fields or not required.issubset(fields):
        raise ValueError("CSV thiếu cột bắt buộc.")

    if len(rows) != 988:
        raise ValueError(
            f"CSV cần có 988 dòng, hiện có {len(rows)}"
        )

    by_id = {}

    for row in rows:
        word_id = int(row["MaTuVung"])

        if word_id in by_id:
            raise ValueError(f"Trùng MaTuVung={word_id}")

        by_id[word_id] = row

    errors = []

    for word_id, (chinese, vietnamese) in fixes.items():
        row = by_id.get(word_id)

        if row is None:
            errors.append(f"Thiếu ID {word_id}")
            continue

        word = row["ChuHan"].strip()
        status = row["TrangThaiImport"].strip()

        if row["HSK"].strip() != "4":
            errors.append(f"{word_id}: Sai cấp HSK")

        if status != "NEED_REVIEW":
            errors.append(
                f"{word_id}: Đang là {status}, "
                "không được ghi đè"
            )

        # Cấu trúc phân số có dạng 三分之二.
        if word_id == 2738:
            valid = "分之" in chinese
        else:
            valid = word in chinese

        if not valid:
            errors.append(
                f"{word_id} {word}: Câu không chứa từ mục tiêu"
            )

    if errors:
        print("\n".join(errors))
        raise ValueError("VALIDATION FAILED - CHƯA GHI FILE")

    # Kiểm tra trùng với toàn bộ câu READY hiện có,
    # bao gồm 201 câu đã hoàn thành của Batch 1.
    ready_rows = [
        row for row in rows
        if row["TrangThaiImport"].strip() == "READY"
    ]

    all_chinese = [
        pair[0] for pair in fixes.values()
    ] + [
        row["ViDuTiengTrung"].strip()
        for row in ready_rows
    ]

    all_vietnamese = [
        pair[1] for pair in fixes.values()
    ] + [
        row["ViDuTiengViet"].strip()
        for row in ready_rows
    ]

    duplicate_cn = [
        sentence for sentence, count
        in Counter(all_chinese).items()
        if sentence and count > 1
    ]

    duplicate_vi = [
        sentence for sentence, count
        in Counter(all_vietnamese).items()
        if sentence and count > 1
    ]

    if duplicate_cn or duplicate_vi:
        raise ValueError(
            f"Trùng câu Trung: {duplicate_cn}\n"
            f"Trùng câu Việt: {duplicate_vi}\n"
            "CHƯA GHI FILE"
        )

    # Cập nhật đúng 200 dòng của Batch 2.
    for word_id, (chinese, vietnamese) in fixes.items():
        row = by_id[word_id]

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

    ready = sum(
        row["TrangThaiImport"].strip() == "READY"
        for row in rows
    )

    review = sum(
        row["TrangThaiImport"].strip() == "NEED_REVIEW"
        for row in rows
    )

    if ready != 401 or review != 587:
        raise ValueError(
            f"Sai thống kê: READY={ready}, "
            f"NEED_REVIEW={review}. CHƯA GHI FILE"
        )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 60)
    print("HSK4 - BATCH 2")
    print("VALIDATION PASS")
    print("Đã sửa thêm: 200 câu")
    print(f"Tổng READY: {ready}")
    print(f"Còn NEED_REVIEW: {review}")
    print(f"File mới: {OUTPUT}")
    print("CHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 60)


if __name__ == "__main__":
    main()
