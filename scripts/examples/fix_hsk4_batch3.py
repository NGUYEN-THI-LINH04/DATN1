
import csv
from pathlib import Path
from collections import Counter

DATA = Path(__file__).resolve().parent / "data"
SOURCE = DATA / "offline_preview_hsk4.csv"
OUTPUT = DATA / "offline_preview_hsk4_batch3.csv"

# ID | Tiếng Trung | Tiếng Việt
EXAMPLES = """
2902|虽然任务很难，但我会尽力完成。|Dù nhiệm vụ rất khó nhưng tôi sẽ cố gắng hết sức hoàn thành.
2903|这家商店出售的水果大部分是进口的。|Phần lớn trái cây bán tại cửa hàng này là hàng nhập khẩu.
2904|我们正在学习中国近代历史。|Chúng tôi đang học lịch sử cận đại Trung Quốc.
2905|图书馆里禁止大声说话。|Trong thư viện cấm nói chuyện lớn tiếng.
2906|这部经典电影我已经看过三遍了。|Tôi đã xem bộ phim kinh điển này ba lần rồi.
2907|工作了一整天，他已经没有精力做别的事了。|Làm việc cả ngày, anh ấy không còn sức để làm việc khác.
2908|他竟然一个人完成了所有工作。|Không ngờ anh ấy đã hoàn thành toàn bộ công việc một mình.
2909|摄影师调整镜头，准备拍摄。|Nhiếp ảnh gia điều chỉnh ống kính để chuẩn bị chụp ảnh.
2910|出门前，她对着镜子整理头发。|Trước khi ra ngoài, cô ấy chỉnh lại tóc trước gương.
2911|这件事情究竟是谁负责的？|Rốt cuộc ai chịu trách nhiệm về chuyện này?
2912|那家酒吧晚上经常有现场音乐表演。|Quán bar đó thường có biểu diễn nhạc sống vào buổi tối.
2913|附近的居民希望这里能建一个公园。|Cư dân gần đây mong nơi này có thể xây một công viên.
2914|我的祖父母一直居住在农村。|Ông bà tôi vẫn luôn sinh sống ở nông thôn.
2915|这局比赛我们虽然输了，但学到了很多。|Tuy thua ván đấu này nhưng chúng tôi học được nhiều điều.
2916|这项工程需要投入巨大的资金。|Công trình này cần đầu tư một khoản vốn rất lớn.
2917|申请这个职位需要具备一定的工作经验。|Ứng tuyển vị trí này cần có kinh nghiệm làm việc nhất định.
2918|学校距离我家只有两公里。|Trường học chỉ cách nhà tôi hai kilômét.
2919|春节期间，亲戚们都聚在爷爷家。|Dịp Tết, họ hàng đều tụ họp tại nhà ông.
2920|周末我们准备举行一次同学聚会。|Cuối tuần chúng tôi định tổ chức một buổi họp lớp.
2921|她把画卷起来，放进了纸筒。|Cô ấy cuộn bức tranh lại rồi cho vào ống giấy.
2922|老师让我们完成这份试卷的第二部分。|Giáo viên yêu cầu chúng tôi làm phần hai của đề thi này.
2923|他在电影中扮演一位医生的角色。|Anh ấy đóng vai một bác sĩ trong bộ phim.
2924|春天到了，院子里的桃树开始开花。|Mùa xuân đến, cây đào trong sân bắt đầu nở hoa.
2925|天气冷的时候，我喜欢喝一杯开水。|Khi trời lạnh, tôi thích uống một cốc nước đun sôi.
2926|我们不能因为别人贫穷就看不起他们。|Chúng ta không thể coi thường người khác vì họ nghèo.
2927|天空越来越暗，看来马上要下雨了。|Trời ngày càng tối, xem ra sắp mưa rồi.
2928|星期天，我打算去医院看望生病的朋友。|Chủ nhật tôi định đến bệnh viện thăm người bạn bị ốm.
2929|专家来到村里考察当地的农业发展。|Các chuyên gia đến làng khảo sát tình hình phát triển nông nghiệp địa phương.
2930|我需要认真考虑一下你的建议。|Tôi cần cân nhắc kỹ đề xuất của bạn.
2931|爷爷在院子里种了三棵苹果树。|Ông trồng ba cây táo trong sân.
2932|他每天坚持练习，可见他很重视这次比赛。|Anh ấy kiên trì luyện tập mỗi ngày, có thể thấy anh ấy rất coi trọng cuộc thi này.
2933|这个房间空间不大，但布置得很舒服。|Không gian căn phòng này không lớn nhưng được bố trí rất thoải mái.
2934|明天下午你有空的话，我们一起去图书馆吧。|Nếu chiều mai bạn rảnh, chúng ta cùng đến thư viện nhé.
2935|我在外套口袋里找到了一张车票。|Tôi tìm thấy một tấm vé xe trong túi áo khoác.
2936|想提高中文口语，就要多和别人交流。|Muốn nâng cao tiếng Trung giao tiếp thì phải trò chuyện với người khác nhiều hơn.
2937|这杯咖啡太苦了，我想加一点糖。|Cốc cà phê này đắng quá, tôi muốn thêm chút đường.
2938|姐姐在一家贸易公司做会计。|Chị gái tôi làm kế toán tại một công ty thương mại.
2939|我昨天寄的快递今天已经到了。|Bưu kiện chuyển phát nhanh tôi gửi hôm qua hôm nay đã đến.
2940|这条路很宽，两辆汽车可以同时通过。|Con đường này rất rộng, hai ô tô có thể đi qua cùng lúc.
2941|站在山顶，可以看到宽广的草原。|Đứng trên đỉnh núi có thể nhìn thấy thảo nguyên rộng lớn.
2942|爬山之前，我们每人买了一瓶矿泉水。|Trước khi leo núi, mỗi người chúng tôi mua một chai nước khoáng.
2943|学校计划扩大图书馆的阅读区域。|Nhà trường dự định mở rộng khu đọc sách của thư viện.
2944|这家公司准备把业务扩展到其他城市。|Công ty này chuẩn bị mở rộng hoạt động kinh doanh sang các thành phố khác.
2945|请把需要补充的内容写在括号里。|Hãy viết nội dung cần bổ sung vào trong dấu ngoặc.
2946|请把垃圾扔进门口的垃圾桶。|Hãy bỏ rác vào thùng rác ở cửa.
2947|他轻轻拉开窗帘，让阳光照进房间。|Anh ấy nhẹ nhàng kéo rèm ra để ánh nắng chiếu vào phòng.
2948|这道菜太辣了，我吃不了。|Món này cay quá, tôi không ăn được.
2949|快点走吧，不然就来不及赶火车了。|Đi nhanh lên, nếu không sẽ không kịp bắt tàu.
2950|现在出发还来得及，不用太着急。|Bây giờ xuất phát vẫn kịp, không cần quá vội.
2951|写论文时一定要注明资料来源。|Khi viết luận văn nhất định phải ghi rõ nguồn tài liệu.
2952|她老公每天都会接孩子放学。|Chồng cô ấy ngày nào cũng đón con tan học.
2953|放假的时候，我喜欢回老家看亲戚。|Khi nghỉ học, tôi thích về quê thăm họ hàng.
2954|他老婆是一名小学老师。|Vợ anh ấy là giáo viên tiểu học.
2955|这个孩子很老实，从来不欺负同学。|Đứa trẻ này rất thật thà, chưa bao giờ bắt nạt bạn học.
2956|读书不仅能增长知识，还能带来乐趣。|Đọc sách không chỉ tăng kiến thức mà còn mang lại niềm vui.
2957|听到这个消息，她的眼里含着泪。|Nghe tin này, mắt cô ấy ngấn lệ.
2958|告别家人时，他忍不住流下了泪水。|Khi tạm biệt gia đình, anh ấy không kìm được nước mắt.
2959|图书馆把书籍按照不同类型分类。|Thư viện phân loại sách theo từng loại khác nhau.
2960|遇到突发情况时，首先要保持冷静。|Khi gặp tình huống bất ngờ, trước hết phải giữ bình tĩnh.
2961|这张桌子比原来那张长十厘米。|Chiếc bàn này dài hơn chiếc cũ mười xentimét.
2962|现在的生活已经离不开互联网了。|Cuộc sống hiện nay đã không thể tách rời Internet.
2963|搬完这些箱子，我一点力气都没有了。|Chuyển xong những chiếc thùng này, tôi chẳng còn chút sức lực nào.
2964|我对这座城市的历史很感兴趣。|Tôi rất quan tâm đến lịch sử của thành phố này.
2965|发现问题后，工作人员立即采取了行动。|Sau khi phát hiện vấn đề, nhân viên lập tức hành động.
2966|银行每个月都会计算存款利息。|Ngân hàng tính lãi tiền gửi mỗi tháng.
2967|做决定时，我们应该考虑大家的利益。|Khi đưa ra quyết định, chúng ta nên cân nhắc lợi ích của mọi người.
2968|我们俩从小学开始就是好朋友。|Hai chúng tôi là bạn thân từ thời tiểu học.
2969|保持良好的生活习惯有助于身体健康。|Duy trì thói quen sinh hoạt tốt có lợi cho sức khỏe.
2970|妈妈用尺子量了一下窗户的宽度。|Mẹ dùng thước đo chiều rộng cửa sổ.
2971|农民正在把收获的粮食运回仓库。|Nông dân đang vận chuyển lương thực thu hoạch về kho.
2972|这条街道两边开满了鲜花。|Hai bên con phố này đầy hoa nở.
2973|医生建议爷爷去安静的地方疗养一段时间。|Bác sĩ khuyên ông đến nơi yên tĩnh dưỡng bệnh một thời gian.
2974|她能同时说四种语言，真了不起！|Cô ấy có thể nói bốn ngôn ngữ, thật đáng khâm phục!
2975|旅行之前，我想先了解当地的文化。|Trước khi đi du lịch, tôi muốn tìm hiểu văn hóa địa phương.
2976|请把这些数字列成一个表格。|Hãy liệt kê các con số này thành một bảng.
2977|开往北京的列车将在五分钟后出发。|Chuyến tàu đi Bắc Kinh sẽ xuất phát sau năm phút.
2978|这项工作已经被列入下个月的计划。|Công việc này đã được đưa vào kế hoạch tháng sau.
2979|学校把安全教育列为重要工作。|Nhà trường xếp giáo dục an toàn vào công việc quan trọng.
2980|因为下雨，比赛临时改到了室内。|Vì trời mưa, cuộc thi tạm thời chuyển vào trong nhà.
2981|弟弟喜欢吃零食，但妈妈不让他吃太多。|Em trai thích ăn vặt nhưng mẹ không cho ăn quá nhiều.
2982|这个故事在当地流传了几百年。|Câu chuyện này đã lưu truyền ở địa phương hàng trăm năm.
2983|电梯坏了，我们只能走楼梯上去。|Thang máy hỏng rồi, chúng tôi chỉ có thể đi cầu thang bộ.
2984|这种动物既能在水里生活，也能在陆地上活动。|Loài động vật này vừa sống dưới nước vừa hoạt động trên đất liền.
2985|会议结束后，大家陆续离开了教室。|Sau khi cuộc họp kết thúc, mọi người lần lượt rời khỏi lớp.
2986|他被自己最想去的大学录取了。|Anh ấy đã được trường đại học mình mong muốn nhất nhận vào.
2987|遇到法律问题时，可以向律师咨询。|Khi gặp vấn đề pháp lý, có thể hỏi ý kiến luật sư.
2988|第二轮比赛将于明天上午开始。|Vòng thi thứ hai sẽ bắt đầu vào sáng mai.
2989|我们坐轮船从这个港口出发。|Chúng tôi đi tàu thủy xuất phát từ cảng này.
2990|医院为行动不便的病人准备了轮椅。|Bệnh viện chuẩn bị xe lăn cho bệnh nhân đi lại khó khăn.
2991|自行车的后轮子需要修理。|Bánh sau của xe đạp cần được sửa chữa.
2992|为了完成毕业论文，他查阅了很多资料。|Để hoàn thành luận văn tốt nghiệp, anh ấy đã tra cứu nhiều tài liệu.
2993|秋天到了，树叶一片片落下来。|Mùa thu đến, lá cây rơi xuống từng chiếc.
2994|洗完脸以后，请用干净的毛巾擦干。|Sau khi rửa mặt, hãy dùng khăn sạch lau khô.
2995|天气变冷了，妈妈给我买了一件毛衣。|Trời trở lạnh, mẹ mua cho tôi một chiếc áo len.
2996|太阳很大，出门最好戴一顶帽子。|Nắng rất gắt, ra ngoài tốt nhất nên đội mũ.
2997|你说得没错，这个办法确实更简单。|Bạn nói đúng, cách này thực sự đơn giản hơn.
2998|外面雨太大了，我们没法儿出去。|Bên ngoài mưa lớn quá, chúng tôi không thể ra ngoài.
2999|真没想到，你也参加了这次比赛！|Thật không ngờ bạn cũng tham gia cuộc thi này!
3000|这件商品的价格是五十美金。|Giá của món hàng này là năm mươi đô la Mỹ.
3001|大家都夸新来的女演员是个美女。|Mọi người đều khen nữ diễn viên mới đến là một người đẹp.
3002|昨晚我做了一个很奇怪的梦。|Tối qua tôi có một giấc mơ rất kỳ lạ.
3003|昨天晚上，我梦见了多年没见的朋友。|Tối qua tôi mơ thấy người bạn nhiều năm không gặp.
3004|我的梦想是成为一名中文老师。|Ước mơ của tôi là trở thành giáo viên tiếng Trung.
3005|这是我们之间的秘密，请不要告诉别人。|Đây là bí mật giữa chúng ta, xin đừng kể cho người khác.
3006|经理让秘书安排明天的会议。|Giám đốc yêu cầu thư ký sắp xếp cuộc họp ngày mai.
3007|森林里的树长得很密，阳光很难照进来。|Cây trong rừng mọc rất dày nên ánh nắng khó chiếu vào.
3008|为了安全，最好定期修改账号密码。|Để an toàn, tốt nhất nên thay đổi mật khẩu tài khoản định kỳ.
3009|这两个部门之间一直保持密切联系。|Hai bộ phận này luôn giữ liên lạc mật thiết.
3010|这家博物馆每周三免费开放。|Bảo tàng này mở cửa miễn phí vào thứ tư hằng tuần.
3011|毕业以后，很多学生都会面临找工作的压力。|Sau khi tốt nghiệp, nhiều sinh viên phải đối mặt với áp lực tìm việc.
3012|明天下午我要去一家公司参加面试。|Chiều mai tôi sẽ đến một công ty tham gia phỏng vấn.
3013|请你描述一下昨天发生的事情。|Hãy mô tả sự việc xảy ra hôm qua.
3014|这篇作文生动地描写了家乡的春天。|Bài văn này miêu tả sinh động mùa xuân quê hương.
3015|他的书包上挂着一个写有姓名的名牌儿。|Trên cặp của anh ấy có treo một thẻ tên ghi họ tên.
3016|第一次见面时，他递给我一张名片。|Khi gặp lần đầu, anh ấy đưa cho tôi một tấm danh thiếp.
3017|这位名人经常参加公益活动。|Người nổi tiếng này thường tham gia hoạt động vì cộng đồng.
3018|请不要随便摸博物馆里的展品。|Xin đừng tùy tiện chạm vào hiện vật trong bảo tàng.
3019|这位模特儿正在为新服装拍广告。|Người mẫu này đang chụp quảng cáo cho trang phục mới.
3020|学生们一起制作了一座桥的模型。|Các học sinh cùng làm mô hình một cây cầu.
3021|本世纪末，这座城市可能会有很大变化。|Đến cuối thế kỷ này, thành phố có thể thay đổi rất nhiều.
3022|父亲一直在背后默默支持着我。|Bố luôn âm thầm ủng hộ tôi phía sau.
3023|哪怕只有一点希望，我们也不会放弃。|Dù chỉ còn một chút hy vọng, chúng tôi cũng không từ bỏ.
3024|这件衣服真好看哪！|Chiếc áo này đẹp thật đấy!
3025|这次活动的男女参加人数差不多。|Số người nam và nữ tham gia hoạt động lần này gần bằng nhau.
3026|那位穿蓝色西装的男士是我们的老师。|Quý ông mặc vest xanh kia là giáo viên của chúng tôi.
3027|第一次做这项工作，难免会犯错误。|Lần đầu làm công việc này, khó tránh khỏi mắc lỗi.
3028|他不小心撞到了脑袋，赶紧去了医院。|Anh ấy vô tình va đầu nên vội đến bệnh viện.
3029|孩子们在教室里闹得太厉害了。|Bọn trẻ làm ồn trong lớp quá mức.
3030|我每天早上六点都被闹钟叫醒。|Mỗi sáng sáu giờ tôi đều được đồng hồ báo thức đánh thức.
3031|这份资料只供公司内部使用。|Tài liệu này chỉ dùng trong nội bộ công ty.
3032|她身体不舒服，去医院挂了内科。|Cô ấy không khỏe nên đến bệnh viện khám nội khoa.
3033|姐姐很能干，一个人就能处理这些工作。|Chị gái rất có năng lực, một mình có thể xử lý những công việc này.
3034|夜晚的乡村十分宁静。|Làng quê về đêm vô cùng yên tĩnh.
3035|这杯茶泡得太浓了，我想加一点水。|Cốc trà này pha đặc quá, tôi muốn thêm chút nước.
3036|前台的那位女士正在接待客人。|Quý cô ở quầy lễ tân đang tiếp đón khách.
3037|冬天屋里开着暖气，一点也不冷。|Mùa đông trong nhà bật hệ thống sưởi nên không lạnh chút nào.
3038|这里风景很好，我们一起拍照吧。|Phong cảnh ở đây rất đẹp, chúng ta cùng chụp ảnh nhé.
3039|请把这些文件按照日期排列。|Hãy sắp xếp những tài liệu này theo ngày tháng.
3040|门口的牌上写着“禁止停车”。|Trên tấm biển ở cửa có ghi “Cấm đỗ xe”.
3041|服务员端来了一盘热腾腾的饺子。|Nhân viên phục vụ mang đến một đĩa sủi cảo nóng hổi.
3042|吃完饭后，我把盘子放进了水槽。|Ăn xong, tôi đặt đĩa vào bồn rửa.
3043|他小时候是个胖子，长大后瘦了很多。|Hồi nhỏ anh ấy là một cậu bé mập, lớn lên đã gầy đi nhiều.
3044|公司每年都会培训新员工。|Công ty mỗi năm đều đào tạo nhân viên mới.
3045|我报名参加了一个中文口语培训班。|Tôi đăng ký tham gia một lớp đào tạo tiếng Trung giao tiếp.
3046|老师鼓励我们从小培养阅读习惯。|Giáo viên khuyến khích chúng tôi rèn luyện thói quen đọc sách từ nhỏ.
3047|学校正在努力培育更多优秀人才。|Nhà trường đang nỗ lực đào tạo thêm nhiều nhân tài xuất sắc.
3048|经理批完这些文件以后才能下班。|Giám đốc phải phê duyệt xong những tài liệu này mới có thể tan làm.
3049|这批新书已经送到了学校图书馆。|Lô sách mới này đã được chuyển đến thư viện trường.
3050|只听一方的意见，容易得出片面的结论。|Chỉ nghe ý kiến một phía rất dễ đưa ra kết luận phiến diện.
3051|这家公司的产品品质一直很稳定。|Chất lượng sản phẩm của công ty này luôn ổn định.
3052|这间教室的面积是六十平方米。|Diện tích phòng học này là sáu mươi mét vuông.
3053|听完解释以后，他的心情渐渐平静下来。|Nghe giải thích xong, tâm trạng anh ấy dần bình tĩnh lại.
3054|我们班学生的平均年龄是二十岁。|Tuổi trung bình của học sinh lớp chúng tôi là hai mươi.
3055|飞机起飞后，飞行逐渐变得平稳。|Sau khi máy bay cất cánh, chuyến bay dần trở nên êm ổn.
3056|现在最迫切的问题是找到安全的饮用水。|Vấn đề cấp bách nhất hiện nay là tìm nguồn nước uống an toàn.
3057|由于经营不善，那家公司去年破产了。|Do quản lý kinh doanh kém, công ty đó đã phá sản năm ngoái.
3058|他的妻子是一名医院护士。|Vợ anh ấy là một y tá bệnh viện.
3059|孩子们都很期待下个月的春游。|Bọn trẻ đều rất mong chờ chuyến dã ngoại tháng sau.
3060|考试期间，图书馆每天都会延长开放时间。|Trong thời gian thi, thư viện sẽ kéo dài giờ mở cửa mỗi ngày.
3061|期末考试结束以后，我们就可以放假了。|Sau khi kỳ thi cuối kỳ kết thúc, chúng tôi có thể nghỉ học.
3062|这份合同的有效期限是一年。|Thời hạn hiệu lực của hợp đồng này là một năm.
3063|下周学校将举行期中考试。|Tuần sau trường sẽ tổ chức thi giữa kỳ.
3064|我们已经完成了大部分工作，其余的明天再做。|Chúng tôi đã hoàn thành phần lớn công việc, phần còn lại ngày mai làm tiếp.
3065|政府出台了支持小型企业的新政策。|Chính phủ ban hành chính sách mới hỗ trợ doanh nghiệp nhỏ.
3066|生日会上，孩子们拿着五颜六色的气球。|Trong tiệc sinh nhật, bọn trẻ cầm những quả bóng bay đủ màu.
3067|我不喜欢太甜的汽水，更喜欢喝茶。|Tôi không thích nước ngọt có ga quá ngọt, thích uống trà hơn.
3068|汽车快没汽油了，我们得去加油站。|Ô tô sắp hết xăng rồi, chúng ta phải đến trạm xăng.
3069|心脏是人体非常重要的器官。|Tim là một cơ quan rất quan trọng của cơ thể.
3070|你先往前走，前头就是公共汽车站。|Bạn cứ đi thẳng, phía trước là trạm xe buýt.
3071|只要认真学习，未来就会有更好的前途。|Chỉ cần học tập chăm chỉ, tương lai sẽ có triển vọng tốt hơn.
3072|这条河比较浅，小孩子也能在岸边玩水。|Con sông này khá nông, trẻ nhỏ cũng có thể chơi nước gần bờ.
3073|妹妹最喜欢吃草莓味的巧克力。|Em gái thích ăn sô-cô-la vị dâu nhất.
3074|妈妈把西红柿切成了小块。|Mẹ cắt cà chua thành những miếng nhỏ.
3075|亲爱的妈妈，祝您生日快乐！|Mẹ yêu quý, con chúc mẹ sinh nhật vui vẻ!
3076|她们从小一起长大，关系非常亲密。|Họ lớn lên cùng nhau từ nhỏ, quan hệ rất thân thiết.
3077|青春只有一次，我们应该珍惜时间。|Tuổi trẻ chỉ có một lần, chúng ta nên trân trọng thời gian.
3078|完成考试以后，我感觉轻松多了。|Sau khi thi xong, tôi cảm thấy nhẹ nhõm hơn nhiều.
3079|遇到困难时，不要轻易放弃自己的目标。|Khi gặp khó khăn, đừng dễ dàng từ bỏ mục tiêu của mình.
3080|睡了一觉以后，他的头脑终于清醒了。|Sau một giấc ngủ, đầu óc anh ấy cuối cùng đã tỉnh táo.
3081|老师让我们描述图片中的情景。|Giáo viên yêu cầu chúng tôi mô tả tình huống trong tranh.
3082|虽然小时候家里很穷，他仍然坚持上学。|Tuy hồi nhỏ gia đình rất nghèo, anh ấy vẫn kiên trì đi học.
3083|这个组织经常为穷人提供免费的食物。|Tổ chức này thường cung cấp thức ăn miễn phí cho người nghèo.
3084|秋季天气凉爽，很适合外出旅游。|Thời tiết mùa thu mát mẻ, rất thích hợp đi du lịch.
3085|越来越多人选择网上购物，这是一个明显的趋势。|Ngày càng nhiều người chọn mua sắm trực tuyến, đây là một xu hướng rõ rệt.
3086|孩子们围着操场跑了三圈。|Bọn trẻ chạy ba vòng quanh sân thể thao.
3087|每个人都有表达自己意见的权利。|Mỗi người đều có quyền bày tỏ ý kiến của mình.
3088|他看起来很年轻，却已经工作十年了。|Anh ấy trông rất trẻ nhưng đã làm việc mười năm rồi.
3089|提交申请前，请再次确认个人信息。|Trước khi nộp đơn, hãy xác nhận lại thông tin cá nhân.
3090|我们已经做好准备，然而比赛还是被取消了。|Chúng tôi đã chuẩn bị xong, tuy nhiên cuộc thi vẫn bị hủy.
3091|这种汽车使用电力作为主要燃料。|Loại ô tô này sử dụng điện làm nguồn nhiên liệu chính.
3092|火灾发生时，仓库里的木材正在燃烧。|Khi hỏa hoạn xảy ra, gỗ trong nhà kho đang cháy.
3093|春节期间，街道上到处都很热闹。|Trong dịp Tết, đường phố khắp nơi đều rất náo nhiệt.
3094|邻居阿姨很热心，经常帮助老人。|Cô hàng xóm rất nhiệt tình, thường giúp đỡ người già.
3095|人家已经道歉了，你就别再生气了。|Người ta đã xin lỗi rồi, bạn đừng giận nữa.
3096|我习惯每天晚上写几句日记。|Tôi có thói quen viết vài dòng nhật ký mỗi tối.
3097|我在日历上标出了考试的日期。|Tôi đã đánh dấu ngày thi trên lịch.
3098|如今，越来越多的学生通过网络学习中文。|Ngày nay, ngày càng nhiều học sinh học tiếng Trung qua mạng.
3099|他的身体比较弱，需要多休息。|Sức khỏe anh ấy khá yếu, cần nghỉ ngơi nhiều.
3100|出门时记得带伞，今天可能下雨。|Khi ra ngoài nhớ mang ô, hôm nay có thể mưa.
3101|电影结束以后，观众们慢慢散了。|Sau khi phim kết thúc, khán giả dần giải tán.
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
            raise ValueError(f"Trùng ID {word_id}")

        fixes[word_id] = (chinese, vietnamese)

    expected = set(range(2902, 3102))

    if set(fixes) != expected:
        raise ValueError(
            f"Thiếu: {sorted(expected - set(fixes))}\n"
            f"Thừa: {sorted(set(fixes) - expected)}"
        )

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    if len(rows) != 988:
        raise ValueError(f"CSV có {len(rows)} dòng, cần 988")

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

        if not vietnamese:
            raise ValueError(f"ID {word_id}: thiếu bản dịch")

    ready_rows = [
        r for r in rows
        if r["TrangThaiImport"].strip() == "READY"
    ]

    cn = [pair[0] for pair in fixes.values()] + [
        r["ViDuTiengTrung"].strip() for r in ready_rows
    ]

    vi = [pair[1] for pair in fixes.values()] + [
        r["ViDuTiengViet"].strip() for r in ready_rows
    ]

    duplicate_cn = [
        s for s, count in Counter(cn).items()
        if s and count > 1
    ]

    duplicate_vi = [
        s for s, count in Counter(vi).items()
        if s and count > 1
    ]

    if duplicate_cn or duplicate_vi:
        raise ValueError(
            f"Trùng câu Trung: {duplicate_cn}\n"
            f"Trùng câu Việt: {duplicate_vi}"
        )

    for word_id, (chinese, vietnamese) in fixes.items():
        row = by_id[word_id]
        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

    ready = sum(
        r["TrangThaiImport"].strip() == "READY"
        for r in rows
    )

    review = sum(
        r["TrangThaiImport"].strip() == "NEED_REVIEW"
        for r in rows
    )

    if ready != 601 or review != 387:
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
    print("HSK4 - BATCH 3")
    print("VALIDATION PASS")
    print("Đã sửa thêm: 200 câu")
    print(f"Tổng READY: {ready}")
    print(f"Còn NEED_REVIEW: {review}")
    print(f"File mới: {OUTPUT}")
    print("CHƯA THAY ĐỔI SQL SERVER.")
    print("=" * 60)


if __name__ == "__main__":
    main()
