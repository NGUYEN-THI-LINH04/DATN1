
import csv
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
SOURCE = DATA / "offline_preview_hsk2_batch6.csv"
OUTPUT = DATA / "offline_preview_hsk2_batch7.csv"

# Mỗi dòng: MaTuVung | Câu tiếng Trung | Dịch tiếng Việt
EXAMPLES = """
651|这家饭馆的菜好吃，而且不贵。|Món ăn ở nhà hàng này ngon, hơn nữa không đắt.
652|请把这张照片发给我。|Hãy gửi bức ảnh này cho tôi.
653|我发现自己忘了带钥匙。|Tôi phát hiện mình quên mang chìa khóa.
654|学校旁边有一家小饭馆。|Bên cạnh trường có một quán ăn nhỏ.
655|坐地铁去机场很方便。|Đi tàu điện ngầm đến sân bay rất thuận tiện.
656|今天太忙了，我只吃了一碗方便面。|Hôm nay quá bận, tôi chỉ ăn một bát mì ăn liền.
657|老师教了我们一个学习汉语的好方法。|Giáo viên dạy chúng tôi một phương pháp học tiếng Trung hay.
658|他在学习方面进步很快。|Anh ấy tiến bộ rất nhanh trong việc học.
659|请问，去医院应该走哪个方向？|Xin hỏi, đi bệnh viện phải đi theo hướng nào?
660|请先放下书，听我说。|Hãy đặt sách xuống trước và nghe tôi nói.
661|你放心，我会准时到。|Bạn yên tâm, tôi sẽ đến đúng giờ.
662|请把这些衣服和鞋子分开。|Hãy để riêng những bộ quần áo và giày này.
663|这次考试我的分数比上次高。|Điểm thi lần này của tôi cao hơn lần trước.
664|请等我五分钟。|Hãy đợi tôi năm phút.
665|我给妈妈准备了一份生日礼物。|Tôi chuẩn bị một món quà sinh nhật cho mẹ.
666|昨天我收到了一封信。|Hôm qua tôi nhận được một lá thư.
667|这家酒店的服务很好。|Dịch vụ của khách sạn này rất tốt.
668|明天考试，今晚我要认真复习。|Ngày mai thi, tối nay tôi phải ôn tập chăm chỉ.
669|天冷了，你该穿外套了。|Trời lạnh rồi, bạn nên mặc áo khoác.
670|这个字写错了，请改一下。|Chữ này viết sai rồi, hãy sửa lại.
671|来到中国以后，我的生活改变了很多。|Sau khi đến Trung Quốc, cuộc sống của tôi thay đổi rất nhiều.
672|大家举起杯子说：“干杯！”|Mọi người nâng cốc và nói: “Cạn ly!”
673|听到这个消息，我感到很高兴。|Nghe tin này, tôi cảm thấy rất vui.
674|她的故事让我很感动。|Câu chuyện của cô ấy khiến tôi rất xúc động.
675|我感觉今天比昨天冷。|Tôi cảm thấy hôm nay lạnh hơn hôm qua.
676|非常感谢你的帮助。|Vô cùng cảm ơn sự giúp đỡ của bạn.
677|爸爸每天都在花园里干活儿。|Bố làm việc trong vườn mỗi ngày.
678|我刚到家，还没吃饭。|Tôi vừa về đến nhà, vẫn chưa ăn cơm.
679|刚才是谁给我打电话？|Vừa nãy ai gọi điện cho tôi?
680|他刚刚从学校回来。|Anh ấy vừa mới từ trường về.
681|她正在学习高级汉语。|Cô ấy đang học tiếng Trung trình độ cao cấp.
682|我哥哥今年上高中。|Anh trai tôi năm nay học trung học phổ thông.
683|我弟弟的个子比我高。|Em trai tôi cao hơn tôi.
684|今天比昨天更热。|Hôm nay nóng hơn hôm qua.
685|我每天坐公共汽车去学校。|Tôi đi xe buýt đến trường mỗi ngày.
686|这辆公交车可以到火车站。|Chiếc xe buýt này có thể đến ga tàu.
687|这个西瓜有三公斤重。|Quả dưa hấu này nặng ba ki-lô-gam.
688|我家离学校有五公里。|Nhà tôi cách trường năm ki-lô-mét.
689|这条公路一直通到海边。|Con đường quốc lộ này chạy thẳng đến bờ biển.
690|老师对每个学生都很公平。|Giáo viên rất công bằng với mọi học sinh.
691|我爸爸在一家中国公司工作。|Bố tôi làm việc tại một công ty Trung Quốc.
692|周末我们一起去公园散步。|Cuối tuần chúng tôi cùng đi dạo trong công viên.
693|邻居家有一只可爱的小狗。|Nhà hàng xóm có một chú chó nhỏ đáng yêu.
694|这些水果够我们吃两天了。|Số trái cây này đủ cho chúng tôi ăn hai ngày.
695|奶奶每天晚上给我讲故事。|Bà kể chuyện cho tôi mỗi tối.
696|他不是故意打破杯子的。|Anh ấy không cố ý làm vỡ cốc.
697|这家商店每天都有很多顾客。|Cửa hàng này mỗi ngày đều có rất nhiều khách hàng.
698|上飞机前请先关机。|Trước khi lên máy bay, vui lòng tắt điện thoại.
699|妈妈很关心我的学习。|Mẹ rất quan tâm đến việc học của tôi.
700|我同意你的观点。|Tôi đồng ý với quan điểm của bạn.
701|晚上广场上有很多人跳舞。|Buổi tối có rất nhiều người nhảy múa ở quảng trường.
702|我在电视上看到了这家商店的广告。|Tôi nhìn thấy quảng cáo của cửa hàng này trên TV.
703|这是一所国际学校。|Đây là một trường quốc tế.
704|你快过来看看这张照片。|Bạn mau lại đây xem bức ảnh này.
705|今年我们回老家过年。|Năm nay chúng tôi về quê ăn Tết.
1144|除了汉语以外，我还学习英语。|Ngoài tiếng Trung, tôi còn học tiếng Anh.
1145|我以为今天是星期五，原来是星期四。|Tôi tưởng hôm nay là thứ Sáu, hóa ra là thứ Năm.
1146|十岁以下的孩子可以免费进公园。|Trẻ em dưới mười tuổi có thể vào công viên miễn phí.
1147|教室里还有一把空椅子。|Trong lớp vẫn còn một chiếc ghế trống.
1148|我一般早上七点起床。|Tôi thường thức dậy lúc bảy giờ sáng.
1149|杯子里还有一点点水。|Trong cốc vẫn còn một chút nước.
1150|他一生都喜欢读书。|Ông ấy thích đọc sách suốt đời.
1151|我一直在这里等你。|Tôi vẫn luôn đợi bạn ở đây.
1152|中国有十几亿人口。|Trung Quốc có dân số hơn một tỷ người.
1153|你对这个计划有什么意见？|Bạn có ý kiến gì về kế hoạch này?
1154|这个汉字是什么意思？|Chữ Hán này có nghĩa là gì?
1155|因为今天下雨，所以我们没有出去。|Vì hôm nay trời mưa nên chúng tôi không ra ngoài.
1156|今天是阴天，太阳没有出来。|Hôm nay trời âm u, mặt trời không xuất hiện.
1157|阴天的时候，我喜欢在家看书。|Khi trời nhiều mây, tôi thích đọc sách ở nhà.
1158|这个汉字有两个音节吗？|Chữ Hán này có hai âm tiết không?
1159|我每天晚上都听音乐。|Tôi nghe nhạc mỗi tối.
1160|星期六我们一起去听音乐会。|Thứ Bảy chúng tôi cùng đi nghe hòa nhạc.
1161|我下午要去银行取钱。|Buổi chiều tôi phải đến ngân hàng rút tiền.
1162|我把银行卡忘在家里了。|Tôi để quên thẻ ngân hàng ở nhà.
1163|你应该多喝水，早点儿休息。|Bạn nên uống nhiều nước và nghỉ ngơi sớm.
1164|这本书有中文和英文两种版本。|Quyển sách này có hai phiên bản tiếng Trung và tiếng Anh.
1165|我妹妹正在学校学习英语。|Em gái tôi đang học tiếng Anh ở trường.
1166|这部影片讲的是一个家庭的故事。|Bộ phim này kể câu chuyện về một gia đình.
1167|睡得太晚会影响第二天的学习。|Ngủ quá muộn sẽ ảnh hưởng đến việc học ngày hôm sau.
1168|我永远不会忘记这一天。|Tôi sẽ không bao giờ quên ngày này.
1169|炒菜的时候不要放太多油。|Khi xào rau đừng cho quá nhiều dầu.
1170|长城每天都有很多游客。|Vạn Lý Trường Thành mỗi ngày có rất nhiều du khách.
1171|这里的人对外国朋友很友好。|Người ở đây rất thân thiện với bạn bè nước ngoài.
1172|明天你有空儿吗？我们一起吃饭吧。|Ngày mai bạn có rảnh không? Chúng ta cùng ăn cơm nhé.
1173|教室里有人正在唱歌。|Trong lớp có người đang hát.
1174|今天有一点儿冷，你多穿点儿。|Hôm nay hơi lạnh, bạn mặc thêm một chút nhé.
1175|这本书很有意思，你可以看看。|Quyển sách này rất thú vị, bạn có thể đọc thử.
1176|他昨天迟到了，今天又迟到了。|Hôm qua anh ấy đến muộn, hôm nay lại đến muộn.
1177|妈妈今天买了一条大鱼。|Hôm nay mẹ mua một con cá lớn.
1178|汉语是一种很有意思的语言。|Tiếng Trung là một ngôn ngữ rất thú vị.
1179|原来你也住在这附近！|Hóa ra bạn cũng sống gần đây!
1180|你知道他没来上课的原因吗？|Bạn có biết lý do anh ấy không đến lớp không?
1181|医院的院里有很多树。|Trong sân bệnh viện có rất nhiều cây.
1182|院长正在和医生们开会。|Viện trưởng đang họp với các bác sĩ.
1183|孩子们正在院子里玩。|Bọn trẻ đang chơi trong sân.
1184|如果你愿意，我们可以一起学习。|Nếu bạn sẵn lòng, chúng ta có thể học cùng nhau.
1185|你最喜欢哪个月份？|Bạn thích tháng nào nhất?
1186|今天晚上的月亮又大又圆。|Mặt trăng tối nay vừa to vừa tròn.
1187|我越学习汉语，越觉得有意思。|Tôi càng học tiếng Trung càng thấy thú vị.
1188|天气越来越冷了。|Thời tiết ngày càng lạnh.
1189|天上有几朵白云。|Trên trời có vài đám mây trắng.
1190|每天运动对身体很好。|Tập thể dục mỗi ngày rất tốt cho sức khỏe.
1191|咱明天一起去吧。|Ngày mai chúng ta cùng đi nhé.
1192|咱们星期天去公园吧。|Chủ nhật chúng ta đi công viên nhé.
1193|这件衣服脏了，需要洗。|Bộ quần áo này bẩn rồi, cần giặt.
1194|我每天七点吃早餐。|Tôi ăn sáng lúc bảy giờ mỗi ngày.
1195|早晨的空气很新鲜。|Không khí buổi sáng rất trong lành.
1196|我早就知道这个消息了。|Tôi đã biết tin này từ lâu rồi.
1197|我的手机丢了，怎么办？|Điện thoại của tôi mất rồi, phải làm sao đây?
1198|你觉得这家饭馆怎么样？|Bạn thấy nhà hàng này thế nào?
1199|你想怎样学习汉语？|Bạn muốn học tiếng Trung như thế nào?
1200|这张桌子占了房间很大一部分地方。|Chiếc bàn này chiếm một phần lớn diện tích căn phòng.
1201|警察大声喊：“站住！”|Cảnh sát hét lớn: “Đứng lại!”
1202|春天到了，小树开始长新叶子。|Mùa xuân đến, cây nhỏ bắt đầu mọc lá mới.
1203|我长大以后想当老师。|Khi lớn lên tôi muốn làm giáo viên.
1204|请从文章中找出正确答案。|Hãy tìm ra đáp án đúng trong bài đọc.
1205|妈妈生病了，我在家照顾她。|Mẹ bị ốm, tôi ở nhà chăm sóc mẹ.
1206|这是我们去年旅行时拍的照片。|Đây là bức ảnh chúng tôi chụp khi đi du lịch năm ngoái.
1207|我们在公园门口照相吧。|Chúng ta chụp ảnh ở cổng công viên nhé.
1208|这道题怎么这么难？|Sao bài này lại khó như vậy?
1209|我正准备出门，这时候电话响了。|Tôi đang chuẩn bị ra ngoài thì lúc này điện thoại reo.
1210|请不要这样做。|Xin đừng làm như vậy.
1211|他是我真正的好朋友。|Anh ấy là người bạn tốt thực sự của tôi.
1212|我的电脑现在可以正常使用了。|Máy tính của tôi bây giờ đã có thể sử dụng bình thường.
1213|你来得正好，我们正要吃饭。|Bạn đến vừa đúng lúc, chúng tôi đang định ăn cơm.
1214|请写出正确的答案。|Hãy viết ra đáp án chính xác.
1215|这正是我想找的那本书。|Đây chính là quyển sách tôi muốn tìm.
1216|你可以直接问老师。|Bạn có thể hỏi trực tiếp giáo viên.
1217|我只买了一本书。|Tôi chỉ mua một quyển sách.
1218|今天下雨，我们只能待在家里。|Hôm nay trời mưa, chúng tôi chỉ có thể ở nhà.
1219|只要每天练习，你就会进步。|Chỉ cần luyện tập mỗi ngày, bạn sẽ tiến bộ.
1220|请给我一张纸。|Hãy đưa cho tôi một tờ giấy.
1221|这家饭馆主要卖中餐。|Nhà hàng này chủ yếu bán món Trung Quốc.
1222|他正在学习中级汉语。|Anh ấy đang học tiếng Trung trình độ trung cấp.
1223|那位中年男人是我的叔叔。|Người đàn ông trung niên đó là chú tôi.
1224|这个活动欢迎中小学的学生参加。|Hoạt động này chào đón học sinh tiểu học và trung học tham gia.
1225|市中心有一家大书店。|Ở trung tâm thành phố có một hiệu sách lớn.
1226|我爷爷喜欢看中医。|Ông tôi thích khám bằng Đông y.
1227|老师告诉我们考试的重点。|Giáo viên cho chúng tôi biết trọng tâm của kỳ thi.
1228|我们应该重视身体健康。|Chúng ta nên coi trọng sức khỏe.
1229|我每周去游泳两次。|Tôi đi bơi hai lần mỗi tuần.
1230|这个周末你有什么计划？|Cuối tuần này bạn có kế hoạch gì?
1231|今年是我们学校成立十周年。|Năm nay là kỷ niệm mười năm thành lập trường.
1232|这只小狗的主人是我朋友。|Chủ của chú chó nhỏ này là bạn tôi.
1233|我来这里的主要目的是学习。|Mục đích chính tôi đến đây là học tập.
1234|这个城市的住房比较贵。|Nhà ở thành phố này tương đối đắt.
1235|他生病住院三天了。|Anh ấy bị bệnh nhập viện ba ngày rồi.
1236|请把这些书装进箱子里。|Hãy xếp những quyển sách này vào thùng.
1237|请准确地告诉我时间。|Hãy nói cho tôi biết thời gian một cách chính xác.
1238|这件事我想自己做。|Việc này tôi muốn tự mình làm.
1239|我每天骑自行车去学校。|Tôi đạp xe đến trường mỗi ngày.
1240|每个人都有自由选择的权利。|Mỗi người đều có quyền tự do lựa chọn.
1242|我每天上学都会走过这个公园。|Mỗi ngày đi học tôi đều đi ngang qua công viên này.
1246|老师把我们分成了四组。|Giáo viên chia chúng tôi thành bốn nhóm.
1247|我们小组由五名学生组成。|Nhóm chúng tôi gồm năm học sinh.
1254|运动对身体健康有很大的作用。|Tập thể dục có tác dụng rất lớn đối với sức khỏe.
1255|山上有一座古老的寺庙。|Trên núi có một ngôi chùa cổ.
1257|我相信自己一定能做到。|Tôi tin bản thân nhất định có thể làm được.
1258|我觉得你的做法很正确。|Tôi thấy cách làm của bạn rất đúng.
"""


def normalize_word(word):
    word = word.strip()

    # 有（一）点儿 -> 有一点儿
    word = word.replace("（一）", "一")

    # 小（小王） -> 小王
    match = re.search(r"（([^（）]+)）", word)
    if match:
        return match.group(1)

    # 面1 -> 面
    return re.sub(r"\d+$", "", word)


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Không tìm thấy: {SOURCE}")

    fixes = {}

    for line in EXAMPLES.strip().splitlines():
        parts = line.strip().split("|")

        if len(parts) != 3:
            raise ValueError(f"Dòng dữ liệu sai định dạng: {line}")

        word_id = int(parts[0])
        chinese = parts[1].strip()
        vietnamese = parts[2].strip()

        if word_id in fixes:
            raise ValueError(f"Trùng MaTuVung: {word_id}")

        fixes[word_id] = (chinese, vietnamese)

    if len(fixes) != 159:
        raise ValueError(
            f"Cần 159 câu, nhưng EXAMPLES có {len(fixes)} câu."
        )

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    # Chỉ chấp nhận đúng 159 mã đang NEED_REVIEW.
    review_ids = {
        int(row["MaTuVung"])
        for row in rows
        if row["TrangThaiImport"] == "NEED_REVIEW"
    }

    missing = review_ids - set(fixes)
    unexpected = set(fixes) - review_ids

    if missing or unexpected:
        print("Mã còn thiếu:", sorted(missing))
        print("Mã không thuộc NEED_REVIEW:", sorted(unexpected))
        raise ValueError(
            "Danh sách 159 từ không khớp CSV. "
            "Chưa tạo file mới và chưa cập nhật SQL."
        )

    for row in rows:
        word_id = int(row["MaTuVung"])

        if word_id not in fixes:
            continue

        chinese, vietnamese = fixes[word_id]
        target = normalize_word(row["ChuHan"])

        if target not in chinese:
            raise ValueError(
                f"Câu không chứa từ mục tiêu: "
                f"{word_id} - {row['ChuHan']} - {chinese}"
            )

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

    remaining = sum(
        row["TrangThaiImport"] == "NEED_REVIEW"
        for row in rows
    )

    if remaining != 0:
        raise ValueError(f"Vẫn còn {remaining} từ NEED_REVIEW")

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 60)
    print("HSK2 - BATCH 7 CUỐI CÙNG")
    print("Đã bổ sung: 159 câu")
    print("Còn NEED_REVIEW:", remaining)
    print("File:", OUTPUT)
    print("CHƯA THAY ĐỔI SQL SERVER")
    print("=" * 60)


if __name__ == "__main__":
    main()
