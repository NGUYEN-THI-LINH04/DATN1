
import csv
from collections import Counter
from pathlib import Path

# ==========================================================
# HSK4 - BATCH 1
# MaTuVung: 2502 -> 2701
# 200 câu Trung - Việt
#
# Chỉ tạo CSV, KHÔNG thay đổi SQL Server.
# ==========================================================

DATA_DIR = Path(__file__).resolve().parent / "data"
SOURCE = DATA_DIR / "offline_preview_hsk4.csv"
OUTPUT = DATA_DIR / "offline_preview_hsk4_batch1.csv"

# MaTuVung | Câu tiếng Trung | Bản dịch tiếng Việt
EXAMPLES = """
2502|我阿姨住在上海，每年春节都会来看我们。|Dì tôi sống ở Thượng Hải, Tết nào cũng đến thăm chúng tôi.
2503|啊，原来你也认识我的哥哥！|Ồ, hóa ra bạn cũng quen anh trai tôi!
2504|这张桌子太矮了，坐着写字不舒服。|Chiếc bàn này thấp quá, ngồi viết không thoải mái.
2505|虽然他身材矮小，但是跑得非常快。|Tuy vóc người thấp bé nhưng anh ấy chạy rất nhanh.
2506|爷爷常常给我们讲一些爱国故事。|Ông thường kể cho chúng tôi những câu chuyện yêu nước.
2507|我们应该爱护学校里的公共设施。|Chúng ta nên giữ gìn các thiết bị công cộng trong trường.
2508|一家人都平安，我的心就安了。|Cả gia đình đều bình an thì tôi mới yên lòng.
2509|政府为受灾的居民安置了临时住所。|Chính quyền đã bố trí nơi ở tạm thời cho người dân bị thiên tai.
2510|我们必须按时完成老师布置的作业。|Chúng tôi phải hoàn thành bài tập giáo viên giao đúng hạn.
2511|天色渐渐暗了下来，街上的灯也亮了。|Trời dần tối xuống, đèn đường cũng sáng lên.
2512|他没有直接拒绝，只是暗示自己很忙。|Anh ấy không từ chối trực tiếp mà chỉ ngụ ý rằng mình rất bận.
2513|我们坐巴士去机场，比打车便宜多了。|Chúng tôi đi xe buýt đến sân bay, rẻ hơn taxi nhiều.
2514|这家百货商店的商品种类非常丰富。|Cửa hàng bách hóa này có rất nhiều loại hàng hóa.
2515|妈妈把洗好的水果摆在餐桌上。|Mẹ bày trái cây đã rửa lên bàn ăn.
2516|窗外的树枝随着风轻轻摆动。|Cành cây ngoài cửa sổ đung đưa nhẹ theo gió.
2517|他终于摆脱了以前的不良习惯。|Cuối cùng anh ấy đã bỏ được những thói quen xấu trước đây.
2518|我们的球队在最后一分钟反败为胜。|Đội bóng chúng tôi lội ngược dòng giành chiến thắng vào phút cuối.
2519|爸爸今天去银行办事，下午才回来。|Hôm nay bố đến ngân hàng giải quyết công việc, chiều mới về.
2520|我在网上买的包裹已经送到了。|Bưu kiện tôi mua trên mạng đã được giao đến.
2521|这份套餐包含一杯饮料和一份甜点。|Suất ăn này bao gồm một đồ uống và một món tráng miệng.
2522|参加活动的人包括老师和学生。|Những người tham gia hoạt động bao gồm giáo viên và học sinh.
2523|这件外套太薄了，冬天穿会冷。|Chiếc áo khoác này mỏng quá, mặc vào mùa đông sẽ lạnh.
2524|奶奶说，健康才是最重要的宝。|Bà nói sức khỏe mới là báu vật quan trọng nhất.
2525|宝宝睡着了，请把电视声音调小一点。|Em bé ngủ rồi, hãy vặn nhỏ tiếng tivi một chút.
2526|妈妈把这张全家福当作宝贝一样保存着。|Mẹ gìn giữ bức ảnh gia đình này như báu vật.
2527|这次实习让我获得了宝贵的工作经验。|Đợt thực tập này giúp tôi có được kinh nghiệm làm việc quý báu.
2528|她戴着一条镶有蓝色宝石的项链。|Cô ấy đeo một chiếc vòng cổ đính đá quý màu xanh.
2529|客户要求我们对这些资料严格保密。|Khách hàng yêu cầu chúng tôi giữ bí mật nghiêm ngặt những tài liệu này.
2530|爷爷的思想比较保守，不太接受新事物。|Tư tưởng của ông khá bảo thủ, không dễ chấp nhận điều mới.
2531|小女孩跑过来，紧紧抱住了妈妈。|Cô bé chạy tới và ôm chặt lấy mẹ.
2532|拍照之前，我们先选择一个干净的背景。|Trước khi chụp ảnh, chúng tôi chọn một phông nền sạch đẹp.
2533|今年的游客数量是去年的两倍。|Số du khách năm nay gấp đôi năm ngoái.
2534|因为天气恶劣，我们被迫取消了旅行。|Vì thời tiết xấu, chúng tôi buộc phải hủy chuyến đi.
2535|她本科毕业后决定继续读研究生。|Sau khi tốt nghiệp đại học, cô ấy quyết định học tiếp cao học.
2536|我太笨了，竟然把钥匙忘在家里。|Tôi vụng về quá, vậy mà lại để quên chìa khóa ở nhà.
2537|比赛结束时，双方的比分是二比二。|Khi trận đấu kết thúc, tỷ số hai bên là hai đều.
2538|哥哥明年六月就要大学毕业了。|Anh trai tôi sẽ tốt nghiệp đại học vào tháng sáu năm sau.
2539|公司今年计划招聘二十名应届毕业生。|Năm nay công ty dự định tuyển hai mươi sinh viên mới tốt nghiệp.
2540|为了避开早高峰，我们提前出发了。|Để tránh giờ cao điểm buổi sáng, chúng tôi xuất phát sớm.
2541|开车时要保持距离，避免发生事故。|Khi lái xe phải giữ khoảng cách để tránh xảy ra tai nạn.
2542|奶奶会用竹条编篮子。|Bà biết dùng nan tre đan giỏ.
2543|两组同学正在辩论是否应该带手机上学。|Hai nhóm học sinh đang tranh luận về việc có nên mang điện thoại đến trường hay không.
2544|看到这个标志，就知道前面不能停车。|Nhìn thấy biển báo này là biết phía trước không được đỗ xe.
2545|听到好消息后，她脸上露出了开心的表情。|Nghe tin tốt, trên mặt cô ấy hiện lên vẻ vui mừng.
2546|因为帮助了同学，他受到了老师的表扬。|Vì giúp đỡ bạn học, anh ấy được giáo viên khen ngợi.
2547|冬天湖面上结了一层厚厚的冰。|Mùa đông mặt hồ đóng một lớp băng dày.
2548|买回来的牛奶应该放进冰箱保存。|Sữa mua về nên được bảo quản trong tủ lạnh.
2549|山上的冰雪到了春天才慢慢融化。|Băng tuyết trên núi đến mùa xuân mới dần tan.
2550|那位老兵给孩子们讲过去的故事。|Người lính già ấy kể cho bọn trẻ nghe chuyện ngày xưa.
2551|只是擦破了一点皮，不要紧。|Chỉ bị trầy da một chút thôi, không sao đâu.
2552|他不在乎别人怎么评价自己的选择。|Anh ấy không quan tâm người khác đánh giá lựa chọn của mình thế nào.
2553|不管遇到什么困难，我们都要坚持下去。|Bất kể gặp khó khăn gì, chúng ta đều phải kiên trì.
2554|快点出门吧，不然就赶不上公交车了。|Mau ra khỏi nhà đi, nếu không sẽ lỡ xe buýt đấy.
2555|老师已经布置了下周要交的作业。|Giáo viên đã giao bài tập phải nộp vào tuần sau.
2556|学校离我家不远，步行十五分钟就到了。|Trường cách nhà tôi không xa, đi bộ mười lăm phút là tới.
2557|吃完饭以后，我帮妈妈擦桌子。|Ăn cơm xong, tôi giúp mẹ lau bàn.
2558|做这个实验之前，要先准备好材料。|Trước khi làm thí nghiệm này phải chuẩn bị đủ vật liệu.
2559|他把自己的大部分财产留给了孩子。|Ông ấy để lại phần lớn tài sản cho các con.
2560|对我来说，健康和家人才是真正的财富。|Đối với tôi, sức khỏe và gia đình mới là của cải thực sự.
2561|记者正在采访参加比赛的运动员。|Phóng viên đang phỏng vấn vận động viên tham gia thi đấu.
2562|写报告时可以参考这些研究资料。|Khi viết báo cáo có thể tham khảo những tài liệu nghiên cứu này.
2563|很多学生主动参与了学校的环保活动。|Nhiều học sinh chủ động tham gia hoạt động bảo vệ môi trường của trường.
2564|下课以后，同学们在操场上踢足球。|Tan học, các bạn chơi bóng đá trên sân trường.
2565|使用这台机器之前，请先了解操作方法。|Trước khi dùng máy này, hãy tìm hiểu cách vận hành.
2566|医生给他测了体温，发现有点发烧。|Bác sĩ đo nhiệt độ cho anh ấy và phát hiện hơi sốt.
2567|工人正在测量这间房子的面积。|Công nhân đang đo diện tích căn phòng này.
2568|新软件上线前需要经过多次测试。|Phần mềm mới cần trải qua nhiều lần kiểm thử trước khi đưa vào sử dụng.
2569|我曾在北京生活过一年。|Tôi từng sống ở Bắc Kinh một năm.
2570|爸爸喜欢用新鲜的茶叶泡茶。|Bố thích dùng lá trà tươi để pha trà.
2571|这家公司的新产品很受年轻人欢迎。|Sản phẩm mới của công ty này rất được giới trẻ yêu thích.
2572|坐长途汽车时，最好每隔一段时间休息一下。|Khi đi xe khách đường dài, tốt nhất nên nghỉ sau mỗi khoảng thời gian.
2573|出门前检查门窗是基本的安全常识。|Kiểm tra cửa ra vào và cửa sổ trước khi ra ngoài là kiến thức an toàn cơ bản.
2574|爸爸收藏了很多年轻时买的唱片。|Bố sưu tầm nhiều đĩa nhạc mua từ thời trẻ.
2575|考试时不能抄别人的答案。|Khi thi không được chép đáp án của người khác.
2576|老师让我们把黑板上的句子抄写下来。|Giáo viên yêu cầu chúng tôi chép lại những câu trên bảng.
2577|下了几天雨，房间里有点潮。|Mưa mấy ngày liền nên trong phòng hơi ẩm.
2578|这种衣服的设计很符合今年的潮流。|Thiết kế của loại quần áo này rất hợp xu hướng năm nay.
2579|雨季的天气比较潮湿，衣服很难干。|Thời tiết mùa mưa khá ẩm ướt, quần áo rất khó khô.
2580|我们必须彻底解决这个问题。|Chúng ta phải giải quyết triệt để vấn đề này.
2581|石头太重了，一放进水里就沉了下去。|Hòn đá nặng quá, vừa thả xuống nước đã chìm.
2582|听完这个消息以后，大家都沉默了。|Nghe xong tin này, mọi người đều im lặng.
2583|他背着一个沉重的书包走进教室。|Anh ấy đeo chiếc cặp nặng trĩu bước vào lớp.
2584|老师称赞她在比赛中的出色表现。|Giáo viên khen ngợi màn thể hiện xuất sắc của cô ấy trong cuộc thi.
2585|这部电影不适合儿童，只有成人才能观看。|Bộ phim này không phù hợp với trẻ em, chỉ người lớn mới được xem.
2586|他是一个诚实的人，从来不说谎。|Anh ấy là người thành thật, chưa bao giờ nói dối.
2587|做生意最重要的是诚信。|Điều quan trọng nhất khi kinh doanh là sự trung thực và uy tín.
2588|作为组长，他愿意承担更多责任。|Là trưởng nhóm, anh ấy sẵn lòng gánh vác thêm trách nhiệm.
2589|他终于承认自己忘记了开会时间。|Cuối cùng anh ấy thừa nhận đã quên giờ họp.
2590|这张旧桌子承受不了这么重的东西。|Chiếc bàn cũ này không chịu nổi vật nặng như vậy.
2591|安装这个程序大约需要十分钟。|Cài đặt chương trình này mất khoảng mười phút.
2592|听到他突然辞职的消息，我非常吃惊。|Nghe tin anh ấy đột nhiên nghỉ việc, tôi rất ngạc nhiên.
2593|今天路上堵车，所以我上课迟到了。|Hôm nay đường kẹt xe nên tôi đến lớp muộn.
2594|爸爸用一把尺量了桌子的长度。|Bố dùng một cây thước đo chiều dài của bàn.
2595|买衣服前最好先确认尺寸是否合适。|Trước khi mua quần áo, tốt nhất nên kiểm tra kích thước có phù hợp không.
2596|我的尺子借给同桌了，还没拿回来。|Tôi đã cho bạn cùng bàn mượn thước kẻ và chưa lấy lại.
2597|妈妈让我用热水冲一杯牛奶。|Mẹ bảo tôi dùng nước nóng pha một cốc sữa.
2598|手机快没电了，我得先充电。|Điện thoại sắp hết pin rồi, tôi phải sạc trước.
2599|出门时我忘记带手机充电器了。|Khi ra ngoài tôi quên mang bộ sạc điện thoại.
2600|我们已经为明天的会议做了充分准备。|Chúng tôi đã chuẩn bị đầy đủ cho cuộc họp ngày mai.
2601|菜叶上有几只绿色的小虫子。|Trên lá rau có vài con sâu nhỏ màu xanh.
2602|他从书架上抽出一本旧相册。|Anh ấy rút một cuốn album ảnh cũ từ giá sách.
2603|超市正在举办购物抽奖活动。|Siêu thị đang tổ chức chương trình rút thăm trúng thưởng khi mua sắm.
2604|医生建议他尽快戒掉抽烟的习惯。|Bác sĩ khuyên anh ấy sớm bỏ thói quen hút thuốc.
2605|她在这次演讲比赛中表现得非常出色。|Cô ấy thể hiện rất xuất sắc trong cuộc thi diễn thuyết lần này.
2606|这家商店正在出售一些二手家具。|Cửa hàng này đang bán một số đồ nội thất cũ.
2607|校长将出席明天的毕业典礼。|Hiệu trưởng sẽ tham dự lễ tốt nghiệp ngày mai.
2608|这家公司目前处于快速发展的阶段。|Công ty này hiện đang trong giai đoạn phát triển nhanh.
2609|这份文件有几处错误，需要修改。|Tài liệu này có vài chỗ sai, cần sửa lại.
2610|外面很冷，出门前记得穿上外套。|Bên ngoài rất lạnh, nhớ mặc áo khoác trước khi ra ngoài.
2611|春节是中国最重要的传统节日之一。|Tết Nguyên đán là một trong những lễ hội truyền thống quan trọng nhất của Trung Quốc.
2612|睡觉之前别忘了关好窗户。|Trước khi ngủ đừng quên đóng cửa sổ.
2613|妈妈在窗台上放了几盆花。|Mẹ đặt vài chậu hoa trên bệ cửa sổ.
2614|下雨了，快把那扇窗子关上。|Mưa rồi, mau đóng cánh cửa sổ kia lại.
2615|春季天气变化比较大，出门要注意保暖。|Thời tiết mùa xuân thay đổi khá nhiều, ra ngoài cần giữ ấm.
2616|这瓶果汁是纯苹果汁，没有加糖。|Chai nước ép này là nước táo nguyên chất, không thêm đường.
2617|爬山时我们每人带了两瓶纯净水。|Khi leo núi, mỗi người chúng tôi mang theo hai chai nước tinh khiết.
2618|每天阅读中文文章可以扩大词汇量。|Đọc bài viết tiếng Trung mỗi ngày có thể mở rộng vốn từ vựng.
2619|此事关系到大家的安全，不能大意。|Việc này liên quan đến an toàn của mọi người, không được chủ quan.
2620|这家酒店位置很好，此外服务也很周到。|Khách sạn này có vị trí tốt, ngoài ra dịch vụ cũng rất chu đáo.
2621|摘玫瑰花时要小心枝上的刺。|Khi hái hoa hồng phải cẩn thận gai trên cành.
2622|这部电影的情节很刺激，我看得特别紧张。|Tình tiết bộ phim này rất gay cấn, tôi xem mà vô cùng hồi hộp.
2623|搬到新城市以后，他从此开始了新的生活。|Sau khi chuyển đến thành phố mới, từ đó anh ấy bắt đầu cuộc sống mới.
2624|这棵树的树干很粗，两个人才能抱住。|Thân cây này rất to, phải hai người mới ôm xuể.
2625|因为太粗心，他把考试日期记错了。|Vì quá bất cẩn, anh ấy nhớ nhầm ngày thi.
2626|运动可以促进身体健康。|Vận động có thể thúc đẩy sức khỏe thể chất.
2627|这次失败促使他重新考虑自己的计划。|Thất bại lần này khiến anh ấy suy nghĩ lại kế hoạch của mình.
2628|这家商场周末经常举办促销活动。|Trung tâm thương mại này thường tổ chức khuyến mãi vào cuối tuần.
2629|学校采取了新的措施来保证学生安全。|Nhà trường đã áp dụng biện pháp mới để bảo đảm an toàn cho học sinh.
2630|我去市场买了一打鸡蛋。|Tôi ra chợ mua một tá trứng.
2631|老师公布答案后，我才发现自己做错了。|Sau khi giáo viên công bố đáp án, tôi mới phát hiện mình làm sai.
2632|我们的球队终于打败了对手。|Cuối cùng đội bóng chúng tôi đã đánh bại đối thủ.
2633|外面开始打雷了，可能马上就要下雨。|Bên ngoài bắt đầu có sấm, có lẽ sắp mưa.
2634|每个星期天，我们都会一起打扫房间。|Chủ nhật hằng tuần, chúng tôi đều cùng nhau dọn phòng.
2635|这双鞋正在打折，比原来便宜很多。|Đôi giày này đang giảm giá, rẻ hơn ban đầu rất nhiều.
2636|孩子一听说要打针，就紧张起来了。|Đứa trẻ vừa nghe nói phải tiêm đã căng thẳng.
2637|我们明天早上坐大巴去旅游。|Sáng mai chúng tôi đi du lịch bằng xe khách.
2638|参加活动的学生大多来自附近的学校。|Phần lớn học sinh tham gia hoạt động đến từ các trường gần đó.
2639|她性格大方，第一次见面也不会紧张。|Cô ấy có tính cách tự nhiên, thoải mái nên gặp lần đầu cũng không căng thẳng.
2640|我大哥已经工作五年了。|Anh cả tôi đã đi làm được năm năm.
2641|政府正在进行大规模的道路建设。|Chính phủ đang tiến hành xây dựng đường sá trên quy mô lớn.
2642|学校大会将于下周一上午举行。|Đại hội của trường sẽ diễn ra vào sáng thứ hai tuần sau.
2643|大姐每次回家都会给我们带礼物。|Chị cả mỗi lần về nhà đều mang quà cho chúng tôi.
2644|这座大楼一共有二十五层。|Tòa nhà này có tổng cộng hai mươi lăm tầng.
2645|这座岛距离大陆有几十公里。|Hòn đảo này cách đất liền vài chục kilômét.
2646|楼下的大妈每天早上都去公园锻炼。|Bác gái ở tầng dưới sáng nào cũng đến công viên tập thể dục.
2647|这家大型超市每天都有很多顾客。|Siêu thị lớn này ngày nào cũng có nhiều khách hàng.
2648|一位大爷主动给我们指路。|Một bác lớn tuổi chủ động chỉ đường cho chúng tôi.
2649|这部纪录片向大众介绍了环保知识。|Bộ phim tài liệu này giới thiệu kiến thức bảo vệ môi trường cho công chúng.
2650|没有任何东西能够代替家人的关爱。|Không có thứ gì có thể thay thế tình yêu thương của gia đình.
2651|这家公司待遇不错，所以很多人想来工作。|Công ty này có chế độ đãi ngộ khá tốt nên nhiều người muốn vào làm.
2652|我买了一袋大米和两袋面粉。|Tôi mua một bao gạo và hai bao bột mì.
2653|骑摩托车时一定要戴头盔。|Khi đi xe máy nhất định phải đội mũ bảo hiểm.
2654|银行要求申请人提供一位担保人。|Ngân hàng yêu cầu người đăng ký cung cấp một người bảo lãnh.
2655|他毕业后在学校担任中文老师。|Sau khi tốt nghiệp, anh ấy đảm nhiệm công việc giáo viên tiếng Trung ở trường.
2656|妈妈一直担心我一个人在外面生活。|Mẹ luôn lo lắng khi tôi sống một mình ở bên ngoài.
2657|服务员把账单放在桌子上。|Nhân viên phục vụ đặt hóa đơn lên bàn.
2658|他帮助别人并不是单纯为了得到回报。|Anh ấy giúp người khác không đơn thuần vì muốn được báo đáp.
2659|每天做同样的工作，有时会觉得很单调。|Ngày nào cũng làm cùng một công việc, đôi khi cảm thấy rất đơn điệu.
2660|老师希望和我单独谈一谈。|Giáo viên muốn nói chuyện riêng với tôi.
2661|这碗汤味道太淡了，可以加一点盐。|Bát canh này nhạt quá, có thể thêm một chút muối.
2662|导游向游客介绍了这座古城的历史。|Hướng dẫn viên giới thiệu lịch sử thành cổ này cho du khách.
2663|长期熬夜可能导致身体出现问题。|Thức khuya lâu ngày có thể dẫn đến vấn đề sức khỏe.
2664|由于生意不好，这家小店去年倒闭了。|Vì kinh doanh không tốt, cửa hàng nhỏ này đã đóng cửa năm ngoái.
2665|去机场需要倒车一次，不能直接到。|Đến sân bay phải chuyển xe một lần, không thể đi thẳng.
2666|停车场太窄了，他倒车时特别小心。|Bãi đỗ xe quá hẹp nên anh ấy rất cẩn thận khi lùi xe.
2667|考试得了第一名，他显得有些得意。|Đạt hạng nhất kỳ thi, anh ấy tỏ ra hơi đắc ý.
2668|时间不早了，我们得马上出发。|Không còn sớm nữa, chúng ta phải xuất phát ngay.
2669|舞台上的灯光突然暗了下来。|Ánh đèn trên sân khấu đột nhiên tối xuống.
2670|我们打算明天一早登上山顶。|Chúng tôi dự định sáng sớm mai leo lên đỉnh núi.
2671|入住酒店时需要先登记个人信息。|Khi nhận phòng khách sạn cần đăng ký thông tin cá nhân trước.
2672|忘记密码以后，我无法登录自己的账号。|Sau khi quên mật khẩu, tôi không thể đăng nhập tài khoản của mình.
2673|登山之前一定要检查好装备。|Trước khi leo núi nhất định phải kiểm tra kỹ trang bị.
2674|这道题的确有点难，我想了很久。|Câu hỏi này quả thực hơi khó, tôi suy nghĩ rất lâu.
2675|故事里的主人公最后原谅了敌人。|Cuối cùng nhân vật chính trong câu chuyện đã tha thứ cho kẻ thù.
2676|孩子在箱子底发现了一张旧照片。|Đứa trẻ tìm thấy một tấm ảnh cũ ở đáy chiếc hộp.
2677|政府正在支持地方经济的发展。|Chính phủ đang hỗ trợ phát triển kinh tế địa phương.
2678|下雨以后，地面变得很滑。|Sau cơn mưa, mặt đất trở nên rất trơn.
2679|教育在社会发展中有重要地位。|Giáo dục có vị trí quan trọng trong sự phát triển xã hội.
2680|这座城市正在建设新的地下停车场。|Thành phố này đang xây dựng bãi đỗ xe ngầm mới.
2681|请把收货地址写清楚，以免寄错。|Hãy viết rõ địa chỉ nhận hàng để tránh gửi nhầm.
2682|这是一种典型的南方建筑风格。|Đây là một kiểu kiến trúc miền nam điển hình.
2683|老师每天上课前都会先点名。|Giáo viên ngày nào cũng điểm danh trước khi bắt đầu tiết học.
2684|房间里的电灯坏了，需要换一个新的。|Đèn điện trong phòng hỏng rồi, cần thay chiếc mới.
2685|姐姐每天骑电动车去上班。|Chị gái tôi mỗi ngày đi làm bằng xe điện.
2686|我们住在十二楼，平时都坐电梯。|Chúng tôi sống ở tầng mười hai, bình thường đều đi thang máy.
2687|修理电脑之前，请先切断电源。|Trước khi sửa máy tính, hãy ngắt nguồn điện.
2688|他今天戴了一顶黑色的帽子。|Hôm nay anh ấy đội một chiếc mũ màu đen.
2689|我们先定好见面的时间和地点。|Chúng ta hãy ấn định thời gian và địa điểm gặp nhau trước.
2690|这个城市冬季很冷，经常下雪。|Mùa đông ở thành phố này rất lạnh, thường có tuyết.
2691|弟弟最喜欢看关于动物的动画片。|Em trai thích xem phim hoạt hình về động vật nhất.
2692|虽然遇到困难，他的决心从未动摇。|Dù gặp khó khăn, quyết tâm của anh ấy chưa từng lung lay.
2693|妈妈今天做的豆腐特别好吃。|Món đậu phụ mẹ nấu hôm nay đặc biệt ngon.
2694|大学毕业以后，我想独立生活。|Sau khi tốt nghiệp đại học, tôi muốn sống tự lập.
2695|这家餐厅的装修风格非常独特。|Phong cách trang trí của nhà hàng này rất độc đáo.
2696|她第一次独自去国外旅行。|Đây là lần đầu cô ấy đi du lịch nước ngoài một mình.
2697|一辆坏车堵住了小区的大门。|Một chiếc xe hỏng đã chặn cổng khu dân cư.
2698|今天早上堵车很严重，我差点迟到。|Sáng nay kẹt xe nghiêm trọng, tôi suýt đến muộn.
2699|吃完饭以后，我的肚子有点疼。|Ăn cơm xong, bụng tôi hơi đau.
2700|我们在海边度过了一个愉快的周末。|Chúng tôi đã trải qua một cuối tuần vui vẻ bên bờ biển.
2701|为了保持健康，爸爸每天早上都去锻炼。|Để giữ sức khỏe, bố mỗi sáng đều đi tập thể dục.
"""


def parse_examples():
    result = {}

    for line_no, raw in enumerate(EXAMPLES.strip().splitlines(), 1):
        parts = raw.strip().split("|")

        if len(parts) != 3:
            raise ValueError(
                f"Dòng ví dụ {line_no} không có đúng 3 phần: {raw}"
            )

        word_id = int(parts[0].strip())
        chinese = parts[1].strip()
        vietnamese = parts[2].strip()

        if word_id in result:
            raise ValueError(f"Trùng ID trong EXAMPLES: {word_id}")

        if not chinese or not vietnamese:
            raise ValueError(f"Câu rỗng tại ID {word_id}")

        result[word_id] = (chinese, vietnamese)

    return result


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Không tìm thấy CSV: {SOURCE}")

    fixes = parse_examples()
    expected = set(range(2502, 2702))

    if set(fixes) != expected:
        raise ValueError(
            f"Thiếu ID: {sorted(expected - set(fixes))}\n"
            f"Thừa ID: {sorted(set(fixes) - expected)}"
        )

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    required = {
        "MaTuVung",
        "HSK",
        "ChuHan",
        "ViDuTiengTrung",
        "ViDuTiengViet",
        "LoaiCau",
        "TrangThaiImport",
    }

    if not fields or not required.issubset(fields):
        raise ValueError("CSV thiếu cột bắt buộc.")

    if len(rows) != 988:
        raise ValueError(
            f"CSV HSK4 dự kiến 988 dòng, thực tế {len(rows)}"
        )

    by_id = {}

    for row in rows:
        word_id = int(row["MaTuVung"])
        if word_id in by_id:
            raise ValueError(f"CSV trùng MaTuVung={word_id}")
        by_id[word_id] = row

    errors = []

    for word_id in sorted(expected):
        row = by_id.get(word_id)

        if row is None:
            errors.append(f"Thiếu ID {word_id} trong CSV")
            continue

        chinese, vietnamese = fixes[word_id]
        word = row["ChuHan"].strip()
        status = row["TrangThaiImport"].strip()

        if row["HSK"].strip() != "4":
            errors.append(f"{word_id}: HSK không phải 4")

        if status != "NEED_REVIEW":
            errors.append(
                f"{word_id}: trạng thái {status}, "
                "không được ghi đè"
            )

        if word not in chinese:
            errors.append(
                f"{word_id} {word}: câu không chứa từ mục tiêu"
            )

        if chinese == row["ViDuTiengTrung"].strip():
            errors.append(f"{word_id}: vẫn dùng câu cũ")

    if errors:
        print("\n".join(errors))
        raise ValueError(
            "VALIDATION FAILED - CHƯA GHI FILE"
        )

    # Kiểm tra câu mới không trùng nhau hoặc trùng câu READY.
    existing_ready = [
        row for row in rows
        if row["TrangThaiImport"].strip() == "READY"
    ]

    all_chinese = [
        fixes[word_id][0] for word_id in sorted(expected)
    ] + [
        row["ViDuTiengTrung"].strip()
        for row in existing_ready
    ]

    all_vietnamese = [
        fixes[word_id][1] for word_id in sorted(expected)
    ] + [
        row["ViDuTiengViet"].strip()
        for row in existing_ready
    ]

    dup_cn = [
        sentence for sentence, count
        in Counter(all_chinese).items()
        if sentence and count > 1
    ]

    dup_vi = [
        sentence for sentence, count
        in Counter(all_vietnamese).items()
        if sentence and count > 1
    ]

    if dup_cn or dup_vi:
        raise ValueError(
            f"Câu Trung trùng: {dup_cn}\n"
            f"Câu Việt trùng: {dup_vi}\n"
            "CHƯA GHI FILE"
        )

    # Chỉ sửa 200 dòng đã kiểm tra.
    for word_id in sorted(expected):
        row = by_id[word_id]
        chinese, vietnamese = fixes[word_id]

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

    if ready != 201 or review != 787:
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
    print("HSK4 - BATCH 1")
    print("VALIDATION PASS")
    print("Đã sửa thêm: 200 câu")
    print(f"Tổng READY trong CSV: {ready}")
    print(f"Còn NEED_REVIEW: {review}")
    print()
    print(f"File mới: {OUTPUT}")
    print()
    print("CHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 60)


if __name__ == "__main__":
    main()
