
import csv
from pathlib import Path
from collections import Counter

DATA = Path(__file__).resolve().parent / "data"
SOURCE = DATA / "offline_preview_hsk4.csv"
OUTPUT = DATA / "offline_preview_hsk4_batch4.csv"

# MaTuVung | ViDuTiengTrung | ViDuTiengViet
EXAMPLES = """
3102|每天早上，爷爷都会把院子扫得干干净净。|Mỗi sáng ông đều quét sân thật sạch sẽ.
3103|这块布的色很淡，适合做夏天的衣服。|Màu của tấm vải này rất nhạt, thích hợp may quần áo mùa hè.
3104|秋天的山林有着丰富的色彩。|Rừng núi mùa thu có màu sắc rất phong phú.
3105|我们在森林里看到了许多野生动物。|Chúng tôi nhìn thấy nhiều động vật hoang dã trong rừng.
3106|天气很好，妈妈把被子拿出去晒太阳。|Trời đẹp nên mẹ mang chăn ra phơi nắng.
3107|一道亮光突然从窗外闪过。|Một luồng sáng bất ngờ lóe lên ngoài cửa sổ.
3108|闪电划过天空后，响起了一阵雷声。|Sau khi tia chớp lóe ngang bầu trời, một tiếng sấm vang lên.
3109|她是一个善良的人，经常帮助有困难的邻居。|Cô ấy là người tốt bụng, thường giúp những hàng xóm gặp khó khăn.
3110|他善于发现问题，也善于解决问题。|Anh ấy giỏi phát hiện vấn đề và cũng giỏi giải quyết vấn đề.
3111|开玩笑也要注意，不要伤害别人的感情。|Khi đùa cũng phải chú ý, đừng làm tổn thương tình cảm của người khác.
3112|他下周要去上海参加一个商务会议。|Tuần sau anh ấy sẽ đến Thượng Hải dự một cuộc họp thương mại.
3113|春天我们一起去公园赏花吧。|Mùa xuân chúng ta cùng đến công viên ngắm hoa nhé.
3114|上个月我和朋友一起去了北京旅游。|Tháng trước tôi cùng bạn đi du lịch Bắc Kinh.
3115|电梯正在维修，我们只能走楼梯上楼。|Thang máy đang sửa nên chúng tôi chỉ có thể đi cầu thang lên tầng.
3116|这家店提供上门维修电脑的服务。|Cửa hàng này cung cấp dịch vụ đến tận nhà sửa máy tính.
3117|爸爸正在厨房里烧水泡茶。|Bố đang đun nước trong bếp để pha trà.
3118|这所学校的体育设施非常完善。|Cơ sở vật chất thể thao của trường này rất đầy đủ.
3119|你可以在手机里设置每天的提醒时间。|Bạn có thể cài đặt giờ nhắc nhở hằng ngày trên điện thoại.
3120|我准备申请明年的交换生项目。|Tôi chuẩn bị đăng ký chương trình trao đổi sinh viên năm sau.
3121|她身材高挑，穿这件大衣很好看。|Cô ấy có vóc dáng cao thanh mảnh, mặc chiếc áo khoác này rất đẹp.
3122|进入考场前，工作人员会检查考生的身份。|Trước khi vào phòng thi, nhân viên sẽ kiểm tra danh tính thí sinh.
3123|他的身高是一米八二。|Chiều cao của anh ấy là một mét tám mươi hai.
3124|两国人民之间有着深厚的友谊。|Nhân dân hai nước có tình hữu nghị sâu sắc.
3125|小时候，奶奶经常给我讲古代神话。|Hồi nhỏ bà thường kể cho tôi nghe thần thoại cổ đại.
3126|这座古老的城堡充满了神秘的气息。|Tòa lâu đài cổ này mang một vẻ bí ẩn.
3127|他工作太忙，甚至没有时间吃午饭。|Anh ấy bận làm việc đến mức thậm chí không có thời gian ăn trưa.
3128|虽然第一次尝试失败了，我们还是没有放弃。|Tuy lần thử đầu thất bại, chúng tôi vẫn không bỏ cuộc.
3129|听说旅行取消了，孩子们都很失望。|Nghe tin chuyến du lịch bị hủy, bọn trẻ đều rất thất vọng.
3130|公司倒闭以后，他失业了三个月。|Sau khi công ty đóng cửa, anh ấy thất nghiệp ba tháng.
3131|这首诗描写了春天美丽的景色。|Bài thơ này miêu tả cảnh đẹp mùa xuân.
3132|这位诗人的作品深受年轻读者喜爱。|Tác phẩm của nhà thơ này được độc giả trẻ rất yêu thích.
3133|衣服还很湿，先别收进衣柜。|Quần áo vẫn còn ướt, đừng cất vào tủ vội.
3134|学校将从下周开始实施新的管理规定。|Nhà trường sẽ bắt đầu thực hiện quy định quản lý mới từ tuần sau.
3135|这个软件操作简单，而且非常实用。|Phần mềm này dễ sử dụng và rất thiết thực.
3136|中午我们通常在学校食堂吃饭。|Buổi trưa chúng tôi thường ăn tại căng tin trường.
3137|门有点重，你得使劲推才能打开。|Cánh cửa hơi nặng, bạn phải đẩy mạnh mới mở được.
3138|士兵们正在进行野外训练。|Những người lính đang huấn luyện ngoài trời.
3139|我家离市区比较远，坐车需要一个小时。|Nhà tôi khá xa trung tâm thành phố, đi xe mất một giờ.
3140|他高兴得像个孩子似的跳了起来。|Anh ấy vui đến mức nhảy lên như một đứa trẻ.
3141|孩子们对周围的新鲜事物充满好奇。|Trẻ em rất tò mò về những sự vật mới lạ xung quanh.
3142|参加活动之前，请事先了解相关规定。|Trước khi tham gia hoạt động, hãy tìm hiểu trước các quy định liên quan.
3143|考试结束后，老师把试卷收了上去。|Sau khi thi xong, giáo viên thu bài thi lại.
3144|请确认你是否已经收到我的邮件。|Hãy xác nhận xem bạn đã nhận được email của tôi chưa.
3145|老师发现题目有错误，决定收回试卷重新印。|Giáo viên phát hiện đề có lỗi nên quyết định thu hồi đề thi để in lại.
3146|这次实习让我收获了很多宝贵经验。|Đợt thực tập này giúp tôi thu được nhiều kinh nghiệm quý báu.
3147|这家小店今年的收益比去年增加了不少。|Lợi nhuận năm nay của cửa hàng nhỏ này tăng khá nhiều so với năm ngoái.
3148|这些漂亮的花瓶都是手工制作的。|Những chiếc bình hoa đẹp này đều được làm thủ công.
3149|他手里拿着一束花，站在门口等她。|Anh ấy cầm một bó hoa trong tay, đứng ở cửa đợi cô ấy.
3150|医生说这次手术进行得很顺利。|Bác sĩ nói ca phẫu thuật lần này diễn ra thuận lợi.
3151|冬天骑自行车时，我总会戴上手套。|Mùa đông khi đạp xe tôi luôn đeo găng tay.
3152|我们答应过的事情，就应该守信用。|Những điều đã hứa thì chúng ta nên giữ chữ tín.
3153|她在毕业典礼上唱了一首中文歌。|Cô ấy hát một bài hát tiếng Trung trong lễ tốt nghiệp.
3154|这里的噪音太大了，我实在受不了。|Tiếng ồn ở đây lớn quá, tôi thực sự không chịu nổi.
3155|售货员耐心地向我介绍了这款手机。|Nhân viên bán hàng kiên nhẫn giới thiệu mẫu điện thoại này cho tôi.
3156|周末叔叔带我去参观了科技馆。|Cuối tuần chú đưa tôi đi tham quan bảo tàng khoa học.
3157|这家酒店的房间干净又舒适。|Phòng của khách sạn này vừa sạch vừa thoải mái.
3158|经过几个月练习，她已经能熟练地使用这个软件。|Sau vài tháng luyện tập, cô ấy đã có thể sử dụng phần mềm này thành thạo.
3159|今年暑假，我打算参加一个志愿者活动。|Kỳ nghỉ hè năm nay, tôi định tham gia một hoạt động tình nguyện.
3160|小路穿过树林，一直通向山脚。|Con đường nhỏ xuyên qua rừng cây, dẫn thẳng đến chân núi.
3161|秋风吹过，黄色的树叶纷纷落下。|Gió thu thổi qua, những chiếc lá vàng lần lượt rơi xuống.
3162|分析这些数据后，我们发现了一个有趣的现象。|Sau khi phân tích những dữ liệu này, chúng tôi phát hiện một hiện tượng thú vị.
3163|我想买一台轻便的数码相机。|Tôi muốn mua một chiếc máy ảnh kỹ thuật số nhỏ gọn.
3164|做饭之前，先把这些土豆刷干净。|Trước khi nấu ăn, hãy chà sạch những củ khoai tây này.
3165|医生提醒我们每天至少刷牙两次。|Bác sĩ nhắc chúng tôi đánh răng ít nhất hai lần mỗi ngày.
3166|这把刷子太硬了，不适合清洗玻璃杯。|Chiếc bàn chải này cứng quá, không thích hợp để rửa cốc thủy tinh.
3167|他穿上新西装以后，看起来特别帅。|Sau khi mặc bộ vest mới, anh ấy trông đặc biệt đẹp trai.
3168|那个帮我们搬行李的帅哥很有礼貌。|Chàng trai đẹp trai giúp chúng tôi chuyển hành lý rất lịch sự.
3169|这所学校率先推出了新的教学方式。|Trường này đã đi đầu trong việc áp dụng phương pháp giảng dạy mới.
3170|孩子听着妈妈讲故事，很快就睡着了。|Đứa trẻ nghe mẹ kể chuyện rồi nhanh chóng ngủ thiếp đi.
3171|请按照正确的顺序排列这些图片。|Hãy sắp xếp những bức tranh này theo đúng thứ tự.
3172|明天说不定会下雨，出门记得带伞。|Ngày mai có lẽ trời sẽ mưa, ra ngoài nhớ mang ô.
3173|我花了半个小时才说服他接受这个建议。|Tôi mất nửa tiếng mới thuyết phục được anh ấy chấp nhận đề xuất này.
3174|回答之前，请先认真思考这个问题。|Trước khi trả lời, hãy suy nghĩ kỹ về vấn đề này.
3175|他今天似乎不太高兴，一直没有说话。|Hôm nay hình như anh ấy không vui lắm, cứ im lặng.
3176|这颗螺丝有点松，需要再拧紧一些。|Con ốc vít này hơi lỏng, cần vặn chặt thêm một chút.
3177|山坡上种着许多高大的松树。|Trên sườn núi trồng rất nhiều cây thông cao lớn.
3178|为了保护环境，我们应该减少使用塑料。|Để bảo vệ môi trường, chúng ta nên giảm sử dụng nhựa.
3179|买菜的时候，我会自己带袋子，少用塑料袋。|Khi mua rau, tôi tự mang túi để dùng ít túi nhựa hơn.
3180|这个柠檬太酸了，我吃不下。|Quả chanh này chua quá, tôi không ăn nổi.
3181|早餐我通常吃面包，喝一杯酸奶。|Bữa sáng tôi thường ăn bánh mì và uống một cốc sữa chua.
3182|离开教室时，请随手关灯。|Khi rời khỏi lớp học, hãy tiện tay tắt đèn.
3183|奶奶正在教孙女做纸花。|Bà đang dạy cháu gái làm hoa giấy.
3184|爷爷每天都会陪孙子在公园散步。|Ông ngày nào cũng đi dạo trong công viên cùng cháu trai.
3185|新技术可以大大缩短产品的生产时间。|Công nghệ mới có thể rút ngắn đáng kể thời gian sản xuất sản phẩm.
3186|经过多次沟通，双方逐渐缩小了分歧。|Sau nhiều lần trao đổi, hai bên dần thu hẹp bất đồng.
3187|下雨以后，门口的台阶有点滑。|Sau khi mưa, bậc thềm ở cửa hơi trơn.
3188|演员站在台上，向观众表示感谢。|Diễn viên đứng trên sân khấu cảm ơn khán giả.
3189|工作累了，他喜欢躺在沙发上休息。|Khi làm việc mệt, anh ấy thích nằm trên ghế sofa nghỉ ngơi.
3190|这家餐厅的午餐套餐价格很实惠。|Suất ăn trưa theo combo của nhà hàng này có giá rất hợp lý.
3191|今天超市有特价活动，很多商品都便宜了。|Hôm nay siêu thị có chương trình giá đặc biệt, nhiều mặt hàng rẻ hơn.
3192|因为情况特殊，学校允许他晚一天交作业。|Vì hoàn cảnh đặc biệt, nhà trường cho phép anh ấy nộp bài muộn một ngày.
3193|这种动物最明显的特征是耳朵很长。|Đặc điểm rõ nhất của loài động vật này là tai rất dài.
3194|学校为学生提供了免费的学习资料。|Nhà trường cung cấp tài liệu học tập miễn phí cho học sinh.
3195|请提醒我明天上午给老师打电话。|Hãy nhắc tôi gọi điện cho giáo viên vào sáng mai.
3196|妹妹从小就喜欢练习体操。|Em gái từ nhỏ đã thích luyện tập thể dục dụng cụ.
3197|公司每年都会安排员工进行一次体检。|Công ty mỗi năm đều sắp xếp cho nhân viên khám sức khỏe một lần.
3198|坚持运动以后，他的体重下降了五公斤。|Sau khi kiên trì tập thể dục, cân nặng của anh ấy giảm năm kilôgam.
3199|我今天有事，你能替我参加会议吗？|Hôm nay tôi có việc, bạn có thể dự họp thay tôi không?
3200|电子邮件已经逐渐替代了很多传统信件。|Email đã dần thay thế nhiều loại thư truyền thống.
3201|小孩子的问题有时很天真，却让人认真思考。|Câu hỏi của trẻ nhỏ đôi khi rất ngây thơ nhưng khiến người lớn suy nghĩ nghiêm túc.
3202|请把你的姓名和电话号码填在这张表上。|Hãy điền họ tên và số điện thoại của bạn vào mẫu này.
3203|这次考试有十道填空题。|Bài thi lần này có mười câu điền vào chỗ trống.
3204|你可以从这几本书里挑一本自己喜欢的。|Bạn có thể chọn một cuốn mình thích trong số những cuốn sách này.
3205|妈妈正在市场里挑选新鲜的蔬菜。|Mẹ đang lựa chọn rau tươi ở chợ.
3206|这个孩子虽然有点调皮，但很懂礼貌。|Đứa trẻ này tuy hơi nghịch ngợm nhưng rất lễ phép.
3207|他用筷子把碗里的面条挑起来。|Anh ấy dùng đũa khều mì trong bát lên.
3208|第一次独自旅行，对她来说是一个挑战。|Lần đầu du lịch một mình là một thử thách đối với cô ấy.
3209|她把一张旅行照片贴在了墙上。|Cô ấy dán một bức ảnh du lịch lên tường.
3210|听到有人叫他，他马上停下了脚步。|Nghe có người gọi, anh ấy lập tức dừng bước.
3211|她昨天收到了大学录取通知书。|Hôm qua cô ấy nhận được giấy báo trúng tuyển đại học.
3212|大家都很同情那位失去家园的老人。|Mọi người đều rất cảm thông với cụ già mất nhà cửa ấy.
3213|小时候，我最喜欢听妈妈讲童话故事。|Hồi nhỏ tôi thích nhất nghe mẹ kể chuyện cổ tích.
3214|这张照片让我想起了快乐的童年。|Bức ảnh này khiến tôi nhớ lại tuổi thơ vui vẻ.
3215|老师正在统计参加活动的学生人数。|Giáo viên đang thống kê số học sinh tham gia hoạt động.
3216|学校要求所有班级统一使用新的课程表。|Nhà trường yêu cầu tất cả lớp thống nhất sử dụng thời khóa biểu mới.
3217|考试结束后，我们痛快地玩了一下午。|Sau khi thi xong, chúng tôi vui chơi thỏa thích cả buổi chiều.
3218|比赛最后一分钟，他投进了一个三分球。|Ở phút cuối trận đấu, anh ấy ném vào một quả ba điểm.
3219|为了完成项目，团队投入了大量时间和精力。|Để hoàn thành dự án, nhóm đã đầu tư rất nhiều thời gian và công sức.
3220|如果商品有质量问题，顾客可以向商家投诉。|Nếu hàng hóa có vấn đề về chất lượng, khách hàng có thể khiếu nại với người bán.
3221|他计划投资一家新的咖啡店。|Anh ấy dự định đầu tư vào một quán cà phê mới.
3222|雨水透过窗户的缝隙流进了房间。|Nước mưa thấm qua khe cửa sổ chảy vào phòng.
3223|这个玻璃杯是透明的，可以看到里面的水。|Chiếc cốc thủy tinh này trong suốt, có thể nhìn thấy nước bên trong.
3224|这件衣服上的花朵图案很漂亮。|Hoa văn hình hoa trên chiếc áo này rất đẹp.
3225|旅行途中，我们在一个小镇休息了一会儿。|Trên đường du lịch, chúng tôi nghỉ một lát tại thị trấn nhỏ.
3226|农民在这片土地上种植了很多蔬菜。|Nông dân trồng rất nhiều rau trên mảnh đất này.
3227|因为天气不好，运动会推迟到下周举行。|Vì thời tiết xấu, hội thao được hoãn đến tuần sau.
3228|他在商场里向顾客推销新产品。|Anh ấy giới thiệu bán sản phẩm mới cho khách hàng trong trung tâm thương mại.
3229|进屋之前，请先脱鞋。|Trước khi vào nhà, hãy cởi giày.
3230|这双袜子洗过以后变小了。|Đôi tất này sau khi giặt đã bị co nhỏ.
3231|这家银行提供外汇兑换服务。|Ngân hàng này cung cấp dịch vụ đổi ngoại tệ.
3232|他的梦想是成为一名外交官。|Ước mơ của anh ấy là trở thành một nhà ngoại giao.
3233|外面很冷，出门时别忘了穿外套。|Bên ngoài rất lạnh, ra ngoài đừng quên mặc áo khoác.
3234|这条山路弯很多，开车一定要小心。|Con đường núi này có nhiều khúc cua, lái xe nhất định phải cẩn thận.
3235|由于大雨，今天的火车晚点了半个小时。|Do mưa lớn, tàu hôm nay đến muộn nửa tiếng.
3236|你最好保存一份文件，万一电脑坏了也不怕。|Tốt nhất bạn nên lưu một bản tài liệu, phòng khi máy tính hỏng cũng không lo.
3237|古代的王通常住在皇宫里。|Vua thời xưa thường sống trong hoàng cung.
3238|学校的无线网络今天有点慢。|Mạng không dây của trường hôm nay hơi chậm.
3239|请把报名网址发给我，我想参加这个活动。|Hãy gửi cho tôi địa chỉ trang web đăng ký, tôi muốn tham gia hoạt động này.
3240|看到孩子平安回来，妈妈露出了微笑。|Thấy con trở về an toàn, mẹ nở nụ cười.
3241|我们平时通过微信联系，也会分享照片。|Chúng tôi thường liên lạc qua WeChat và chia sẻ ảnh.
3242|天气冷了，妈妈给我织了一条围巾。|Trời lạnh rồi, mẹ đan cho tôi một chiếc khăn quàng.
3243|为了维持健康，他每天坚持散步半小时。|Để duy trì sức khỏe, anh ấy kiên trì đi bộ nửa tiếng mỗi ngày.
3244|每个人都有责任维护公共环境。|Mỗi người đều có trách nhiệm gìn giữ môi trường công cộng.
3245|这台打印机坏了，需要请人来维修。|Máy in này hỏng rồi, cần nhờ người đến sửa chữa.
3246|小狗看到主人回来，高兴地摇着尾巴。|Chú chó thấy chủ về liền vui vẻ vẫy đuôi.
3247|价格高的东西未必质量就好。|Đồ đắt tiền chưa chắc chất lượng đã tốt.
3248|我希望未来能够从事自己喜欢的工作。|Tôi hy vọng tương lai có thể làm công việc mình yêu thích.
3249|这座博物馆位于城市的中心。|Bảo tàng này nằm ở trung tâm thành phố.
3250|请把桌子搬到靠窗的位置。|Hãy chuyển bàn đến vị trí gần cửa sổ.
3251|厨房里有一股奇怪的味儿，你闻到了吗？|Trong bếp có một mùi lạ, bạn có ngửi thấy không?
3252|这张桌子不太稳，你别把电脑放上去。|Chiếc bàn này không vững lắm, bạn đừng đặt máy tính lên.
3253|经过一段时间治疗，他的病情逐渐稳定了。|Sau một thời gian điều trị, tình trạng bệnh của anh ấy dần ổn định.
3254|见到老师时，我们应该主动问候。|Khi gặp giáo viên, chúng ta nên chủ động chào hỏi.
3255|这次活动对所有学生免费，无须报名费。|Hoạt động lần này miễn phí cho mọi học sinh, không cần phí đăng ký.
3256|因为没有网络，我暂时无法提交作业。|Vì không có mạng, tôi tạm thời không thể nộp bài tập.
3257|一个人在家待了一整天，我觉得很无聊。|Ở nhà một mình cả ngày, tôi cảm thấy rất chán.
3258|无论遇到什么困难，我们都要坚持下去。|Dù gặp khó khăn đến đâu, chúng tôi vẫn sẽ tiếp tục cố gắng.
3259|夜晚的天空中有无数颗星星。|Trên bầu trời đêm có vô số ngôi sao.
3260|你想坐哪里都可以，我无所谓。|Bạn muốn ngồi đâu cũng được, tôi không quan trọng.
3261|老师的鼓励给了我们无限的信心。|Lời động viên của giáo viên mang đến cho chúng tôi niềm tin vô hạn.
3262|花园里开满了五颜六色的花。|Trong vườn nở đầy những bông hoa đủ màu sắc.
3263|对不起，我误会了你的意思。|Xin lỗi, tôi đã hiểu lầm ý của bạn.
3264|夏天吃一块冰凉的西瓜，感觉特别舒服。|Mùa hè ăn một miếng dưa hấu mát lạnh cảm thấy rất dễ chịu.
3265|他用吸尘器把地上的灰尘吸干净了。|Anh ấy dùng máy hút bụi hút sạch bụi trên sàn.
3266|喝这杯饮料的时候，可以不用吸管。|Khi uống cốc đồ uống này, bạn có thể không cần ống hút.
3267|植物通过根部吸收土壤中的水分。|Thực vật hấp thụ nước trong đất qua rễ.
3268|医院里禁止吸烟，请到室外去。|Trong bệnh viện cấm hút thuốc, vui lòng ra ngoài.
3269|这部电影的故事情节吸引了很多观众。|Cốt truyện của bộ phim này thu hút nhiều khán giả.
3270|这位作家的小说深受年轻人喜爱。|Tiểu thuyết của nhà văn này được giới trẻ rất yêu thích.
3271|这家出版社推出了一系列儿童读物。|Nhà xuất bản này phát hành một loạt sách dành cho trẻ em.
3272|学校正在升级学生信息管理系统。|Nhà trường đang nâng cấp hệ thống quản lý thông tin học sinh.
3273|她的头发又长又细，很容易打结。|Tóc cô ấy vừa dài vừa mảnh, rất dễ bị rối.
3274|写报告时，要注意每一个重要细节。|Khi viết báo cáo, phải chú ý từng chi tiết quan trọng.
3275|她做事非常细致，很少出现错误。|Cô ấy làm việc rất tỉ mỉ, hiếm khi xảy ra sai sót.
3276|下个月我们班要组织一次校外活动。|Tháng sau lớp chúng tôi sẽ tổ chức một hoạt động ngoại khóa.
3277|最近几天，气温明显下降了。|Mấy ngày gần đây nhiệt độ đã giảm rõ rệt.
3278|听到门铃响了，他赶紧下楼开门。|Nghe chuông cửa reo, anh ấy vội xuống tầng mở cửa.
3279|请先下载这个软件，再按照说明安装。|Hãy tải phần mềm này xuống trước rồi cài đặt theo hướng dẫn.
3280|夏季天气炎热，外出要注意防晒。|Mùa hè thời tiết nóng, ra ngoài cần chú ý chống nắng.
3281|这家市场的鱼很鲜，很多人一早就来买。|Cá ở khu chợ này rất tươi, nhiều người đến mua từ sáng sớm.
3282|她收到了一束漂亮的鲜花。|Cô ấy nhận được một bó hoa tươi rất đẹp.
3283|这两种设计的风格形成了鲜明的对比。|Phong cách của hai thiết kế này tạo nên sự tương phản rõ nét.
3284|这碗汤有点咸，可以加一点水。|Bát canh này hơi mặn, có thể thêm chút nước.
3285|经过训练，队员们的成绩有了显著提高。|Sau khi tập luyện, thành tích của các thành viên đã cải thiện đáng kể.
3286|这个县以种植茶叶而闻名。|Huyện này nổi tiếng với việc trồng chè.
3287|为了保证安全，这条路限制大型货车通行。|Để bảo đảm an toàn, con đường này hạn chế xe tải lớn đi qua.
3288|我们一起工作多年，一直相处得很好。|Chúng tôi làm việc cùng nhau nhiều năm và luôn hòa hợp.
3289|我喜欢热闹的城市，他却相反，更喜欢安静的乡村。|Tôi thích thành phố náo nhiệt, còn anh ấy thì ngược lại, thích nông thôn yên tĩnh hơn.
3290|他从仓库搬来了两箱矿泉水。|Anh ấy chuyển hai thùng nước khoáng từ kho đến.
3291|这个箱子太重了，我一个人搬不动。|Chiếc thùng này nặng quá, một mình tôi không chuyển nổi.
3292|出国留学以后，我常常想念家乡的朋友。|Sau khi đi du học, tôi thường nhớ những người bạn ở quê.
3293|很难想象十年后的生活会是什么样子。|Thật khó hình dung cuộc sống mười năm sau sẽ như thế nào.
3294|老师给我们安排了三项课外任务。|Giáo viên giao cho chúng tôi ba nhiệm vụ ngoại khóa.
3295|这个项目预计需要六个月才能完成。|Dự án này dự kiến cần sáu tháng mới hoàn thành.
3296|我把小时候的相片整理成了一本相册。|Tôi sắp xếp những bức ảnh hồi nhỏ thành một cuốn album.
3297|吃完饭以后，散步有助于消化。|Sau khi ăn, đi bộ giúp tiêu hóa tốt hơn.
3298|这家公司的产品主要通过网络销售。|Sản phẩm của công ty này chủ yếu được bán qua mạng.
3299|来到成都以后，我尝了很多当地小吃。|Sau khi đến Thành Đô, tôi đã thử nhiều món ăn vặt địa phương.
3300|那个小伙子主动帮老人提行李。|Chàng trai trẻ ấy chủ động giúp cụ già xách hành lý.
3301|他们在学校附近开了一家小型咖啡店。|Họ mở một quán cà phê quy mô nhỏ gần trường.
"""


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Không tìm thấy: {SOURCE}")

    fixes = {}

    for line_no, line in enumerate(EXAMPLES.strip().splitlines(), 1):
        parts = line.strip().split("|")

        if len(parts) != 3:
            raise ValueError(f"Sai định dạng dòng {line_no}")

        word_id = int(parts[0])
        chinese = parts[1].strip()
        vietnamese = parts[2].strip()

        if word_id in fixes:
            raise ValueError(f"Trùng ID: {word_id}")

        if not chinese or not vietnamese:
            raise ValueError(f"Câu ví dụ rỗng: {word_id}")

        fixes[word_id] = (chinese, vietnamese)

    expected = set(range(3102, 3302))

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
        "MaTuVung", "HSK", "ChuHan",
        "ViDuTiengTrung", "ViDuTiengViet",
        "LoaiCau", "TrangThaiImport",
    }

    if not fields or not required.issubset(fields):
        raise ValueError("CSV thiếu cột bắt buộc")

    if len(rows) != 988:
        raise ValueError(f"CSV cần 988 dòng, hiện có {len(rows)}")

    by_id = {}

    for row in rows:
        word_id = int(row["MaTuVung"])

        if word_id in by_id:
            raise ValueError(f"CSV trùng ID {word_id}")

        by_id[word_id] = row

    for word_id, (chinese, vietnamese) in fixes.items():
        row = by_id.get(word_id)

        if row is None:
            raise ValueError(f"Không tìm thấy ID {word_id}")

        if row["HSK"].strip() != "4":
            raise ValueError(f"ID {word_id} không thuộc HSK4")

        if row["TrangThaiImport"].strip() != "NEED_REVIEW":
            raise ValueError(f"ID {word_id} đã được xử lý")

        word = row["ChuHan"].strip()

        if word not in chinese:
            raise ValueError(
                f"ID {word_id}: câu không chứa từ {word}"
            )

    # Kiểm tra trùng với tất cả câu READY đã có.
    ready_rows = [
        row for row in rows
        if row["TrangThaiImport"].strip() == "READY"
    ]

    cn = [pair[0] for pair in fixes.values()] + [
        row["ViDuTiengTrung"].strip()
        for row in ready_rows
    ]

    vi = [pair[1] for pair in fixes.values()] + [
        row["ViDuTiengViet"].strip()
        for row in ready_rows
    ]

    duplicate_cn = [
        sentence for sentence, count in Counter(cn).items()
        if sentence and count > 1
    ]

    duplicate_vi = [
        sentence for sentence, count in Counter(vi).items()
        if sentence and count > 1
    ]

    if duplicate_cn or duplicate_vi:
        raise ValueError(
            f"Trùng câu Trung: {duplicate_cn}\n"
            f"Trùng câu Việt: {duplicate_vi}"
        )

    # Chỉ thay đổi đúng 200 từ của Batch 4.
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

    if ready != 801 or review != 187:
        raise ValueError(
            f"Sai thống kê: READY={ready}, "
            f"NEED_REVIEW={review}"
        )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 60)
    print("HSK4 - BATCH 4")
    print("VALIDATION PASS")
    print("Đã sửa thêm: 200 câu")
    print(f"Tổng READY: {ready}")
    print(f"Còn NEED_REVIEW: {review}")
    print(f"File mới: {OUTPUT}")
    print("CHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 60)


if __name__ == "__main__":
    main()
