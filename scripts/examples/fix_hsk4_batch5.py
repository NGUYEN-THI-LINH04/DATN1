
import csv
from pathlib import Path
from collections import Counter

DATA = Path(__file__).resolve().parent / "data"
SOURCE = DATA / "offline_preview_hsk4.csv"
OUTPUT = DATA / "offline_preview_hsk4_batch5.csv"

# Định dạng: MaTuVung | ViDuTiengViet | ViDuTiengTrung
EXAMPLES = """
3302|Làm việc theo nhóm giúp nâng cao hiệu suất.|团队合作有助于提高工作效率。
3303|Tôi mua ít trái cây mang đến thăm ông bà.|我买了些水果去看望爷爷奶奶。
3304|Trước kỳ thi, nhiều học sinh cảm thấy áp lực tâm lý.|考试之前，很多学生会感到心理压力。
3305|Chú rể đang đứng ở cửa đón khách.|新郎站在门口迎接客人。
3306|Cô dâu mặc một chiếc váy cưới màu trắng.|新娘穿着一件白色的婚纱。
3307|Rau ở khu chợ sáng này rất tươi.|这个早市的蔬菜很新鲜。
3308|Nhà máy vừa ra mắt một loại xe điện mới.|工厂刚推出了一款新型电动车。
3309|Nghe tin được nhận vào đại học, cô ấy phấn khích suốt cả ngày.|听说被大学录取了，她兴奋了一整天。
3310|Tôi khó có thể miêu tả cảnh đẹp này bằng lời.|我很难用语言形容这里的美景。
3311|Trước tình hình hiện nay, chúng ta cần điều chỉnh kế hoạch.|面对目前的形势，我们需要调整计划。
3312|Mẫu xe này có hai kiểu dáng để lựa chọn.|这款车有两种不同的车型可选。
3313|Bạn hãy ghi rõ mẫu máy tính trong phiếu bảo hành.|请在保修单上写清楚电脑的型号。
3314|Sáng nay tôi thức dậy muộn nên suýt lỡ xe buýt.|今天早上我醒得太晚，差点没赶上公交车。
3315|Em trai tôi rất hứng thú với thiên văn học.|弟弟对天文学很有兴趣。
3316|Hai loại vật liệu này có tính chất rất khác nhau.|这两种材料的性质很不一样。
3317|Hai anh em họ thường cùng nhau chăm sóc bố mẹ.|他们兄弟俩经常一起照顾父母。
3318|Sau khi bị ngã, anh ấy thấy đau vùng ngực.|摔倒以后，他感到胸部有些疼。
3319|Xe đạp bị hỏng nên tôi đem đến tiệm sửa chữa.|自行车坏了，我把它送去修理。
3320|Sau khi cân nhắc, tôi quyết định chọn công việc này.|考虑以后，我决定选择这份工作。
3321|Môn học này có ba tín chỉ.|这门课程有三个学分。
3322|Năm học mới bắt đầu vào tháng chín.|新的学年从九月开始。
3323|Khóa đào tạo này có tổng cộng hai mươi bốn tiết học.|这次培训一共安排了二十四个学时。
3324|Trường chúng tôi thường tổ chức các buổi giao lưu học thuật.|我们学校经常举办学术交流活动。
3325|Ông tôi có học vấn uyên bác và thích đọc sách.|爷爷很有学问，也很喜欢读书。
3326|Cảnh sát đang tìm kiếm đứa trẻ bị lạc.|警察正在寻找走失的孩子。
3327|Sau khi nhận được thông báo, mọi người nhanh chóng tập trung.|接到通知后，大家迅速集合起来。
3328|Nha sĩ nói răng này cần được điều trị sớm.|牙医说这颗牙需要尽快治疗。
3329|Nha sĩ khuyên tôi thay bàn chải đánh răng định kỳ.|牙医建议我定期更换牙刷。
3330|Anh trai muốn đến tận nơi xem các trận đấu Á vận hội.|哥哥想去现场观看亚运会比赛。
3331|Hôm nay bạn đến sớm thật đấy!|你今天来得真早呀！
3332|Để mọi người xem hết triển lãm, thời gian tham quan được kéo dài thêm một giờ.|为了让大家看完展览，参观时间延长了一个小时。
3333|Do bão, chuyến bay của chúng tôi phải hoãn lại.|受台风影响，我们的航班不得不延期。
3334|Cơn mưa lớn kéo dài đến tận nửa đêm.|这场大雨一直延续到半夜。
3335|Nhà máy này kiểm soát chất lượng sản phẩm rất nghiêm.|这家工厂对产品质量把关很严。
3336|Giáo viên yêu cầu nghiêm khắc về việc nộp bài đúng hạn.|老师严格要求我们按时交作业。
3337|Lần này máy tính bị hỏng khá nghiêm trọng.|这次电脑损坏得比较严重。
3338|Nhóm chúng tôi đang nghiên cứu cách nâng cao hiệu quả học tập.|我们小组正在研究如何提高学习效率。
3339|Sau khi tốt nghiệp đại học, chị ấy dự định học cao học.|大学毕业以后，姐姐打算继续读研究生。
3340|Nhóm kỹ sư đang nghiên cứu phát triển loại pin mới.|工程师团队正在研制一种新型电池。
3341|Canh hơi nhạt, bạn có thể thêm chút muối.|汤有点淡，你可以再加一点盐。
3342|Không có kính mắt, tôi không nhìn rõ chữ trên bảng.|不戴眼镜，我看不清黑板上的字。
3343|Nghe tin vui ấy, mẹ xúc động rơi nước mắt.|听到这个好消息，妈妈激动得流下了眼泪。
3344|Trong mắt bố mẹ, tôi vẫn là một đứa trẻ.|在父母眼里，我始终还是个孩子。
3345|Cô ấy sẽ phát biểu về bảo vệ môi trường vào ngày mai.|她明天要做一个关于环境保护的演讲。
3346|Mẹ trồng vài chậu hoa trên ban công.|妈妈在阳台上种了几盆花。
3347|Tôi muốn hình thành thói quen dậy sớm mỗi ngày.|我想养成每天早起的习惯。
3348|Ngồi máy tính quá lâu khiến lưng dưới tôi đau.|坐在电脑前太久，我的腰有点疼。
3349|Gió thổi làm cành cây đung đưa không ngừng.|风吹得树枝不停地摇。
3350|Không nên tự ý sử dụng thuốc khi chưa hỏi bác sĩ.|没有咨询医生之前，不应该随便使用药物。
3351|Ngoài giờ làm việc, anh ấy thích chơi cầu lông.|业余时间，他喜欢打羽毛球。
3352|Trên mặt đất có rất nhiều lá màu vàng.|地上落满了黄色的叶子。
3353|Vùng núi này còn thiếu nguồn lực y tế.|这个山区的医疗资源还不够充足。
3354|Em gái tôi quyết định theo học ngành y.|妹妹决定去大学学习医学。
3355|Chúng ta không thể chỉ dựa vào may mắn để thành công.|我们不能只依靠运气取得成功。
3356|Dù đã nhiều năm trôi qua, nơi đây vẫn đẹp như trước.|虽然过去了很多年，这里依然很美。
3357|Tất cả người tham dự đều phải xuất trình giấy tờ tùy thân.|所有参加者一律需要出示身份证件。
3358|Mẹ đã nhiều lần nhắc tôi đừng thức khuya.|妈妈一再提醒我不要熬夜。
3359|Cả nhóm đã nhất trí với đề xuất này.|大家一致同意这个建议。
3360|Hãy dịch chiếc ghế sang bên trái một chút.|请把椅子往左边移一点。
3361|Đừng di chuyển chiếc tủ này một mình.|不要一个人移动这个柜子。
3362|Gia đình họ di cư đến thành phố này từ mười năm trước.|他们一家十年前移民到了这座城市。
3363|Ngôi nhà cổ này là di sản mà ông để lại.|这座老房子是爷爷留下的遗产。
3364|Màu mắt của đứa trẻ được di truyền từ mẹ.|孩子的眼睛颜色遗传自母亲。
3365|Nếu còn thắc mắc, bạn có thể hỏi trực tiếp giáo viên.|如果还有疑问，你可以直接问老师。
3366|Khóa học bao gồm luyện nghe cũng như luyện nói.|这门课程包括听力练习以及口语练习。
3367|Vui lòng hoàn thành đăng ký trong vòng ba ngày.|请在三天以内完成报名。
3368|Nói chung, mùa thu ở đây khá mát mẻ.|一般来说，这里的秋天比较凉爽。
3369|Mỗi công dân đều có nghĩa vụ tuân thủ pháp luật.|每个公民都有遵守法律的义务。
3370|Sau cuộc họp, mọi người vẫn còn bàn luận về quyết định ấy.|会议结束后，大家还在议论那个决定。
3371|Hướng dẫn viên dẫn chúng tôi đi vào khu triển lãm.|导游引着我们走进了展览厅。
3372|Giáo viên khéo léo hướng dẫn học sinh tự tìm đáp án.|老师耐心引导学生自己寻找答案。
3373|Nhà máy đã đưa vào công nghệ sản xuất từ nước ngoài.|工厂引进了国外的生产技术。
3374|Tin tức này đã gây ra cuộc thảo luận sôi nổi.|这个消息引起了大家的热烈讨论。
3375|Trong trường hợp khẩn cấp, chúng ta nên giữ bình tĩnh.|遇到紧急情况，我们应保持冷静。
3376|Các chiến sĩ cứu hỏa đã thể hiện tinh thần anh dũng.|消防员们表现出了英勇的精神。
3377|Hiệu sách này bắt đầu kinh doanh từ chín giờ sáng.|这家书店每天上午九点开始营业。
3378|Anh ấy đã giành được sự tôn trọng của mọi người nhờ biểu hiện xuất sắc.|他凭借出色的表现赢得了大家的尊重。
3379|Dưới ánh đèn đường, cái bóng của anh ấy trông rất dài.|在路灯下，他的影子显得特别长。
3380|Cô ấy dũng cảm đứng lên bảo vệ bạn mình.|她勇敢地站出来保护朋友。
3381|Tôi phải lấy hết can đảm mới dám nói trước đông người.|我鼓起勇气，才敢在很多人面前讲话。
3382|Công dụng chính của thiết bị này là lọc không khí.|这台设备的主要用途是净化空气。
3383|Cửa hàng này nổi tiếng về chất lượng phục vụ tốt.|这家店以优良的服务质量闻名。
3384|Cảnh núi non ở đây vô cùng đẹp đẽ.|这里的山水风景十分优美。
3385|Cô ấy là một sinh viên xuất sắc của khoa chúng tôi.|她是我们学院的一名优秀学生。
3386|Tôi cần đến bưu điện gửi bưu kiện cho bạn.|我需要去邮局给朋友寄一个包裹。
3387|Nghỉ một lát xong, tôi lại có sức làm tiếp.|休息了一会儿，我又有劲儿继续干活了。
3388|Chương trình khoa học này rất thú vị, em trai tôi thích xem.|这个科学节目很有趣，弟弟很爱看。
3389|Thời gian có hạn, chúng ta hãy bàn những vấn đề quan trọng trước.|时间有限，我们先讨论最重要的问题吧。
3390|Con gái tôi bắt đầu đi mẫu giáo từ năm ba tuổi.|我女儿三岁的时候开始上幼儿园。
3391|Trời bỗng mưa to, thế là chúng tôi đổi kế hoạch.|天突然下起大雨，于是我们改变了计划。
3392|Ngữ pháp tiếng Trung đôi khi khác tiếng Việt khá nhiều.|汉语语法有时和越南语有很大不同。
3393|Bạn cứ gửi tin nhắn thoại cho tôi, tôi sẽ nghe sau.|你可以给我发语音消息，我晚点再听。
3394|Bà tặng tôi một mặt dây chuyền làm bằng ngọc.|奶奶送给我一个玉做的吊坠。
3395|Mỗi mùa hè, nhà ông đều trồng ngô.|每年夏天，爷爷家都会种玉米。
3396|Chuyên gia dự báo tuần sau nhiệt độ sẽ giảm.|专家预测下周气温会下降。
3397|Tôi đã đặt trước phòng khách sạn cho cuối tuần.|我已经预订了周末的酒店房间。
3398|Trong cuộc sống, ai cũng khó tránh gặp khó khăn.|生活中，谁都难免会遇上困难。
3399|Hôm qua trên đường về nhà, tôi gặp một người bạn cũ.|昨天回家的路上，我遇到了一位老朋友。
3400|Tôi rất vui khi gặp cô ấy tại hội sách.|能在书展上遇见她，我特别高兴。
3401|Nhà máy lựa chọn nguyên liệu chất lượng cao để sản xuất.|工厂选用高质量的原料进行生产。
3402|Làm việc gì cũng nên có nguyên tắc rõ ràng.|做事情应该有明确的原则。
3403|Mặt trăng tối nay rất tròn và sáng.|今晚的月亮又圆又亮。
3404|Buổi lễ tốt nghiệp đã kết thúc tốt đẹp.|毕业典礼圆满结束了。
3405|Tối thứ bảy, tôi có hẹn với một người bạn.|星期六晚上，我和一位朋友有个约会。
3406|Báo cáo này cần nộp trước cuối tháng.|这份报告需要在月底之前提交。
3407|Mỗi ngày tôi dành nửa tiếng để đọc sách tiếng Trung.|我每天花半个小时阅读中文书籍。
3408|Trường chúng tôi sẽ tổ chức hội thao vào tuần sau.|我们学校下周要举办运动会。
3409|Vận động viên ấy đang chuẩn bị cho giải đấu quốc tế.|那位运动员正在为国际比赛做准备。
3410|Hôm nay tôi khá may mắn, tìm lại được ví đã mất.|我今天运气很好，找回了丢失的钱包。
3411|Chúng ta nên vận dụng kiến thức đã học vào thực tế.|我们应该把学过的知识运用到实际生活中。
3412|Giáo viên nhắc đi nhắc lại rằng ngày mai có bài kiểm tra.|老师再三提醒我们明天有考试。
3413|Tôi không quá để ý người khác đánh giá lựa chọn của mình thế nào.|我不太在乎别人怎么评价我的选择。
3414|Thành công của kế hoạch này phụ thuộc vào sự hợp tác của cả nhóm.|这个计划能否成功，在于团队成员的合作。
3415|Hầu hết các thành viên đều tán thành kế hoạch mới.|大部分成员都赞成这个新计划。
3416|Giáo viên đánh giá cao thái độ học tập nghiêm túc của cô ấy.|老师很赞赏她认真学习的态度。
3417|Một doanh nghiệp địa phương đã tài trợ cho cuộc thi này.|一家当地企业赞助了这次比赛。
3418|Kiểu dáng của chiếc đèn này rất đặc biệt.|这盏灯的造型很特别。
3419|Các chiến sĩ tiếp tục chiến đấu bảo vệ quê hương.|战士们继续战斗，保卫家乡。
3420|Cuối cùng cô ấy đã vượt qua nỗi sợ nói trước đám đông.|她终于战胜了对公开演讲的恐惧。
3421|Những chiến sĩ trẻ đứng canh gác suốt đêm.|年轻的战士们整夜站岗。
3422|Chiến tranh đã khiến nhiều gia đình phải rời bỏ nhà cửa.|战争让许多家庭失去了家园。
3423|Chồng cô ấy là kỹ sư xây dựng.|她的丈夫是一名建筑工程师。
3424|Nhìn thấy giáo viên bước vào, các học sinh chủ động chào hỏi.|看到老师走进来，学生们主动打招呼。
3425|Tôi tìm mãi, cuối cùng cũng tìm thấy chìa khóa.|我找了半天，终于找着钥匙了。
3426|Trong lúc nấu ăn, dầu trong chảo bất ngờ bốc cháy.|做饭时，锅里的油突然着火了。
3427|Đừng lo lắng, bác sĩ nói tình trạng của mẹ đã ổn định.|别着急，医生说妈妈的情况已经稳定了。
3428|Nhà trường sẽ triệu tập cuộc họp phụ huynh vào thứ sáu.|学校将于星期五召开家长会。
3429|Anh ấy vô tình bẻ gãy cành cây nhỏ.|他不小心把一根树枝折断了。
3430|Bà đang dùng kim khâu lại chiếc áo bị rách.|奶奶正在用针缝补破了的衣服。
3431|Chúng tôi đã đưa ra biện pháp phù hợp để giải quyết vấn đề này.|我们针对这个问题提出了具体措施。
3432|Ngoài trời bỗng có một trận mưa lớn.|外面突然下了一阵大雨。
3433|Hai bên tranh luận rất lâu nhưng vẫn không thống nhất ý kiến.|双方争论了很久，还是没能达成一致。
3434|Đội leo núi cuối cùng đã chinh phục được ngọn núi cao ấy.|登山队终于征服了那座高山。
3435|Trước khi điều chỉnh nội quy, trường sẽ lấy ý kiến học sinh.|修改校规之前，学校会征求学生的意见。
3436|Chính phủ đang triển khai các biện pháp bảo vệ môi trường.|政府正在采取措施保护环境。
3437|Anh trai tôi đang học ngành khoa học chính trị.|哥哥正在大学学习政治学。
3438|Ăn trưa xong, chúng tôi tiếp tục tham quan bảo tàng.|午饭之后，我们继续参观博物馆。
3439|Giữa hai thành phố có tuyến tàu cao tốc chạy thẳng.|这两座城市之间有直达的高铁。
3440|Trước khi ngủ, tôi thường đọc sách khoảng hai mươi phút.|睡觉之前，我通常会看二十分钟书。
3441|Đây là một trong những cuốn sách tôi thích nhất.|这是我最喜欢的书之一。
3442|Loại thực vật này sinh trưởng tốt ở nơi ẩm ướt.|这种植物在潮湿的地方长得很好。
3443|Nhạc trưởng đang chỉ huy dàn nhạc biểu diễn.|指挥正在带领乐团演奏。
3444|Nhóm chúng tôi cùng xây dựng kế hoạch học tập cho học kỳ tới.|我们小组一起制订了下学期的学习计划。
3445|Chất lượng phục vụ của nhà hàng này đã cải thiện rõ rệt.|这家餐厅的服务质量有了明显提高。
3446|Bác sĩ nói bệnh này có thể chữa khỏi nếu phát hiện sớm.|医生说这种病如果发现得早，就比较容易治。
3447|Bệnh nhân đang được điều trị tại bệnh viện thành phố.|病人正在市医院接受治疗。
3448|Trò chơi này giúp trẻ phát triển trí thông minh.|这个游戏有助于提高孩子的智力。
3449|Gia đình tôi vừa lắp đặt hệ thống chiếu sáng thông minh.|我们家刚安装了一套智能照明系统。
3450|Cô ấy tìm được căn hộ phù hợp thông qua môi giới nhà đất.|她通过房屋中介找到了一套合适的公寓。
3451|Siêu thị có rất nhiều chủng loại trái cây.|超市里的水果种类非常丰富。
3452|Anh ấy mua một tờ vé số và không ngờ lại trúng thưởng.|他买了一张彩票，没想到真的中奖了。
3453|Mỗi mùa xuân ông tôi đều trồng vài cây ăn quả.|爷爷每年春天都种几棵果树。
3454|Nông dân ở đây chủ yếu trồng lúa.|当地农民主要种植水稻。
3456|Nhà trường sẽ từng bước cải thiện cơ sở vật chất.|学校将逐步改善教学设施。
3457|Sau khi luyện tập, khả năng phát âm của cô ấy dần cải thiện.|经过练习，她的发音逐渐变好了。
3458|Chủ đề của buổi tọa đàm hôm nay là học ngoại ngữ.|今天讲座的主题是外语学习。
3459|Chủ tịch cuộc họp mời từng đại diện phát biểu.|会议主席请各位代表依次发言。
3460|Trước khi lên đường, bố mẹ gửi đến tôi những lời chúc tốt đẹp.|出发之前，父母给了我最真诚的祝福。
3461|Thành phố này nổi tiếng với những công trình kiến trúc cổ.|这座城市以古老的建筑而著名。
3462|Thư viện lưu giữ nhiều tác phẩm của học giả này.|图书馆收藏了这位学者的多部著作。
3463|Thời gian không còn nhiều, chúng ta phải tranh thủ hoàn thành nhiệm vụ.|时间不多了，我们得抓紧完成任务。
3464|Khi đọc sách, em trai tôi thường rất tập trung.|弟弟看书的时候总是很专心。
3465|Gió mạnh khiến cánh quạt của cối xay gió quay nhanh hơn.|大风使风车的叶片转动得更快。
3466|Nếu gặp cô ấy, xin hãy chuyển lời rằng tôi sẽ đến muộn.|如果见到她，请转告她我会晚一点到。
3467|Nghe có người gọi, anh ấy lập tức quay người lại.|听见有人叫他，他立刻转身看过去。
3468|Đi đến ngã tư phía trước thì rẽ phải.|走到前面的路口再向右转弯。
3469|Bác sĩ quyết định chuyển bệnh nhân đến bệnh viện lớn hơn.|医生决定把病人转移到更大的医院。
3470|Chúng tôi đang sửa sang lại căn hộ trước khi chuyển đến.|搬进去之前，我们正在装修这套公寓。
3471|Thiết bị này có thể tự động đo nhiệt độ trong phòng.|这个装置能自动测量室内温度。
3472|Anh ấy luôn kiên trì theo đuổi ước mơ trở thành bác sĩ.|他一直努力追求成为医生的梦想。
3473|Xe buýt hôm nay đến đúng giờ.|今天公交车准时到了。
3474|Giáo viên đã gửi cho chúng tôi tài liệu ôn tập.|老师已经把复习资料发给我们了。
3475|Chúng ta nên tiết kiệm nước và bảo vệ tài nguyên thiên nhiên.|我们应该节约用水，保护自然资源。
3476|Từ năm ngoái đến nay, chị ấy luôn làm việc ở đây.|自去年以来，姐姐一直在这里工作。
3477|Cô ấy rất tự tin khi trình bày dự án trước lớp.|她在全班面前介绍项目时非常自信。
3478|Em trai tôi đang học các chữ cái tiếng Anh.|弟弟正在学习英语字母。
3479|Bài kiểm tra này đánh giá tổng hợp kỹ năng nghe, nói, đọc, viết.|这次考试综合考查听、说、读、写四项能力。
3480|Tổng cộng có ba mươi sinh viên tham gia hoạt động.|总共有三十名学生参加了这次活动。
3481|Thủ tướng sẽ tham dự hội nghị vào ngày mai.|总理将参加明天的会议。
3482|Tổng thống phát biểu trên truyền hình tối qua.|总统昨天晚上发表了电视讲话。
3483|Tóm lại, lần khảo sát này đã đạt được mục tiêu đề ra.|总之，这次调查达到了预期目标。
3484|Nhân viên bảo vệ kịp thời ngăn chặn người lạ vào khu vực cấm.|保安及时阻止了陌生人进入禁区。
3485|Em bé vừa ăn bánh vừa cười, miệng dính đầy vụn bánh.|小宝宝一边吃饼干一边笑，嘴巴上沾满了饼干屑。
3486|Ban đầu tôi không hiểu yêu cầu của giáo viên.|最初，我没有理解老师的要求。
3487|Ban quản lý đã đưa ra quyết định sau khi thảo luận.|管理人员讨论后作出了决定。
3488|Với tư cách lớp trưởng, anh ấy luôn chủ động giúp đỡ các bạn.|作为班长，他总是主动帮助同学。
3489|Tối qua tôi nằm mơ thấy mình đang đi dạo bên bờ biển.|我昨晚做梦，梦见自己在海边散步。
"""


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Không tìm thấy: {SOURCE}")

    fixes = {}

    for line_number, line in enumerate(
        EXAMPLES.strip().splitlines(), start=1
    ):
        parts = line.strip().split("|")

        if len(parts) != 3:
            raise ValueError(
                f"Sai định dạng dòng {line_number}: {line}"
            )

        word_id = int(parts[0])
        vietnamese = parts[1].strip()
        chinese = parts[2].strip()

        if word_id in fixes:
            raise ValueError(f"Trùng ID {word_id}")

        if not chinese or not vietnamese:
            raise ValueError(f"Thiếu câu ví dụ ID {word_id}")

        fixes[word_id] = (chinese, vietnamese)

    # Batch 5 có 188 mã, nhưng 3455 đã READY từ trước.
    expected = set(range(3302, 3490)) - {3455}

    if set(fixes) != expected:
        raise ValueError(
            f"Thiếu ID: {sorted(expected - set(fixes))}\n"
            f"Thừa ID: {sorted(set(fixes) - expected)}"
        )

    with SOURCE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
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
        raise ValueError("CSV thiếu các cột bắt buộc")

    if len(rows) != 988:
        raise ValueError(
            f"CSV phải có 988 dòng, thực tế có {len(rows)}"
        )

    by_id = {}

    for row in rows:
        word_id = int(row["MaTuVung"])

        if word_id in by_id:
            raise ValueError(f"CSV trùng ID {word_id}")

        by_id[word_id] = row

    # Kiểm tra từ đã có ví dụ, tuyệt đối không sửa.
    existing = by_id.get(3455)

    if (
        existing is None
        or existing["HSK"].strip() != "4"
        or existing["ChuHan"].strip() != "重量"
        or existing["TrangThaiImport"].strip() != "READY"
        or existing["LoaiCau"].strip() != "REAL"
    ):
        raise ValueError(
            "ID 3455 không đúng dữ liệu READY ban đầu. "
            "Dừng để kiểm tra, không ghi CSV."
        )

    for word_id, (chinese, vietnamese) in fixes.items():
        row = by_id.get(word_id)

        if row is None:
            raise ValueError(
                f"Không tìm thấy ID {word_id}"
            )

        if row["HSK"].strip() != "4":
            raise ValueError(
                f"ID {word_id} không thuộc HSK4"
            )

        if row["TrangThaiImport"].strip() != "NEED_REVIEW":
            raise ValueError(
                f"ID {word_id} đã được xử lý"
            )

        word = row["ChuHan"].strip()

        if word not in chinese:
            raise ValueError(
                f"ID {word_id}: câu không chứa từ {word}\n"
                f"Câu: {chinese}"
            )

    # Không cho phép trùng câu mới với các câu READY.
    ready_rows = [
        row for row in rows
        if row["TrangThaiImport"].strip() == "READY"
    ]

    old_ready_count = len(ready_rows)

    if old_ready_count != 801:
        raise ValueError(
            f"CSV hiện có {old_ready_count} READY, "
            "cần đúng 801 trước Batch 5."
        )

    chinese_sentences = [
        pair[0] for pair in fixes.values()
    ] + [
        row["ViDuTiengTrung"].strip()
        for row in ready_rows
    ]

    vietnamese_sentences = [
        pair[1] for pair in fixes.values()
    ] + [
        row["ViDuTiengViet"].strip()
        for row in ready_rows
    ]

    duplicate_cn = [
        sentence
        for sentence, count in Counter(
            chinese_sentences
        ).items()
        if sentence and count > 1
    ]

    duplicate_vi = [
        sentence
        for sentence, count in Counter(
            vietnamese_sentences
        ).items()
        if sentence and count > 1
    ]

    if duplicate_cn or duplicate_vi:
        raise ValueError(
            f"Trùng câu Trung: {duplicate_cn}\n"
            f"Trùng câu Việt: {duplicate_vi}"
        )

    # Chỉ cập nhật 187 dòng NEED_REVIEW trong bộ nhớ.
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

    if ready != 988 or review != 0:
        raise ValueError(
            f"Sai thống kê: READY={ready}, "
            f"NEED_REVIEW={review}"
        )

    with OUTPUT.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(
            f, fieldnames=fields
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 60)
    print("HSK4 - BATCH 5 (FINAL)")
    print("VALIDATION PASS")
    print("Đã sửa thêm: 187 câu")
    print("Giữ nguyên ví dụ ID 3455: 重量")
    print(f"Tổng READY: {ready}")
    print(f"Còn NEED_REVIEW: {review}")
    print(f"File mới: {OUTPUT}")
    print("CHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 60)


if __name__ == "__main__":
    main()
