import csv
import re
from pathlib import Path


DATA = Path(__file__).resolve().parent / "data"

SOURCE = DATA / "offline_preview_hsk2_batch4.csv"
OUTPUT = DATA / "offline_preview_hsk2_batch5.csv"


# ==========================================================
# HSK2 - BATCH 5
# MaTuVung 944 -> 1043
# Tổng cộng: 100 từ
# ==========================================================

FIXES = {

    944: (
        "这个比赛吸引了全国很多学生参加。",
        "Cuộc thi này thu hút rất nhiều học sinh trên toàn quốc tham gia."
    ),

    945: (
        "春节的时候我们全家一起吃饭。",
        "Vào dịp Tết, cả gia đình chúng tôi cùng ăn cơm."
    ),

    946: (
        "这个城市全年都有很多游客。",
        "Thành phố này có rất nhiều du khách quanh năm."
    ),

    947: (
        "跑完步以后，我全身都是汗。",
        "Sau khi chạy xong, toàn thân tôi đầy mồ hôi."
    ),

    948: (
        "全体学生明天上午八点到学校。",
        "Toàn thể học sinh sáng mai tám giờ đến trường."
    ),

    949: (
        "我先去银行，然后去超市。",
        "Tôi đi ngân hàng trước, sau đó đi siêu thị."
    ),

    950: (
        "妈妈不让我晚上一个人出去。",
        "Mẹ không cho tôi ra ngoài một mình vào buổi tối."
    ),

    951: (
        "这里的人都很热情。",
        "Người ở đây đều rất nhiệt tình."
    ),

    952: (
        "这个城市的人口有五百万。",
        "Dân số của thành phố này là năm triệu người."
    ),

    953: (
        "春天来了，人们都喜欢去公园。",
        "Mùa xuân đến rồi, mọi người đều thích đi công viên."
    ),

    954: (
        "参加这次活动的人数很多。",
        "Số người tham gia hoạt động lần này rất đông."
    ),

    955: (
        "我认为这个办法很好。",
        "Tôi cho rằng cách này rất tốt."
    ),

    956: (
        "爸爸每天早上都看日报。",
        "Bố tôi sáng nào cũng đọc báo hằng ngày."
    ),

    957: (
        "我们一起学习的日子很快乐。",
        "Những ngày chúng tôi cùng học với nhau rất vui."
    ),

    958: (
        "如果明天下雨，我们就不去爬山。",
        "Nếu ngày mai mưa, chúng tôi sẽ không đi leo núi."
    ),

    959: (
        "商场的入口在前面。",
        "Lối vào trung tâm thương mại ở phía trước."
    ),

    960: (
        "这件事我们再商量一下吧。",
        "Việc này chúng ta bàn bạc thêm một chút nhé."
    ),

    961: (
        "他的爸爸是一位商人。",
        "Bố của anh ấy là một doanh nhân."
    ),

    962: (
        "上周我和朋友去了上海。",
        "Tuần trước tôi và bạn đã đi Thượng Hải."
    ),

    963: (
        "只有少数学生没有来。",
        "Chỉ có một số ít học sinh không đến."
    ),

    964: (
        "那个少年每天都来这里打篮球。",
        "Thiếu niên đó ngày nào cũng đến đây chơi bóng rổ."
    ),

    965: (
        "我的朋友一直在我身边帮助我。",
        "Bạn tôi luôn ở bên cạnh giúp đỡ tôi."
    ),

    966: (
        "你喜欢什么样的电影？",
        "Bạn thích loại phim như thế nào?"
    ),

    967: (
        "她去年生了一个女儿。",
        "Năm ngoái cô ấy sinh một bé gái."
    ),

    968: (
        "这篇课文里有十个生词。",
        "Trong bài khóa này có mười từ mới."
    ),

    969: (
        "我很喜欢现在的大学生活。",
        "Tôi rất thích cuộc sống đại học hiện tại."
    ),

    970: (
        "请小声一点儿，你的声音太大了。",
        "Xin nói nhỏ một chút, giọng của bạn lớn quá."
    ),

    # 省 = tỉnh
    971: (
        "广东省在中国南方。",
        "Tỉnh Quảng Đông ở miền Nam Trung Quốc."
    ),

    # 省 = tiết kiệm
    972: (
        "坐公交车比坐出租车省钱。",
        "Đi xe buýt tiết kiệm tiền hơn đi taxi."
    ),

    973: (
        "我对这次旅行十分满意。",
        "Tôi rất hài lòng với chuyến đi lần này."
    ),

    974: (
        "实际情况和我们想的不一样。",
        "Tình hình thực tế không giống như chúng tôi nghĩ."
    ),

    975: (
        "我明年要去一家公司实习。",
        "Năm sau tôi sẽ đến một công ty thực tập."
    ),

    976: (
        "通过努力，他终于实现了自己的梦想。",
        "Nhờ nỗ lực, cuối cùng anh ấy đã thực hiện được ước mơ của mình."
    ),

    # 实在 - phó từ
    977: (
        "今天实在太冷了。",
        "Hôm nay thực sự quá lạnh."
    ),

    # 实在 - tính từ
    978: (
        "他是一个很实在的人。",
        "Anh ấy là một người rất thật thà."
    ),

    979: (
        "冰箱里还有很多食物。",
        "Trong tủ lạnh vẫn còn rất nhiều thực phẩm."
    ),

    980: (
        "请正确使用这台机器。",
        "Hãy sử dụng chiếc máy này đúng cách."
    ),

    981: (
        "这个市有很多漂亮的公园。",
        "Thành phố này có nhiều công viên đẹp."
    ),

    982: (
        "市长今天来我们学校参观。",
        "Hôm nay thị trưởng đến thăm trường chúng tôi."
    ),

    983: (
        "这件事情我已经告诉老师了。",
        "Việc này tôi đã nói với giáo viên rồi."
    ),

    984: (
        "服务员正在收桌子上的盘子。",
        "Nhân viên phục vụ đang thu các đĩa trên bàn."
    ),

    985: (
        "我昨天收到了一封朋友的邮件。",
        "Hôm qua tôi nhận được một email của bạn."
    ),

    986: (
        "他的每月收入不低。",
        "Thu nhập hàng tháng của anh ấy không thấp."
    ),

    987: (
        "这块手表是我爸爸送给我的。",
        "Chiếc đồng hồ đeo tay này là bố tặng tôi."
    ),

    988: (
        "他的作品受到很多人的欢迎。",
        "Tác phẩm của anh ấy được nhiều người yêu thích."
    ),

    989: (
        "这把椅子坐起来很舒服。",
        "Chiếc ghế này ngồi rất thoải mái."
    ),

    990: (
        "苹果已经熟了，可以吃了。",
        "Táo đã chín rồi, có thể ăn được."
    ),

    991: (
        "请数一数桌子上有几本书。",
        "Hãy đếm xem trên bàn có mấy quyển sách."
    ),

    992: (
        "请把你的电话号码用数字写下来。",
        "Hãy viết số điện thoại của bạn bằng chữ số."
    ),

    993: (
        "他的汉语水平提高得很快。",
        "Trình độ tiếng Trung của anh ấy tiến bộ rất nhanh."
    ),

    994: (
        "希望你明天考试顺利。",
        "Chúc bạn ngày mai thi thuận lợi."
    ),

    995: (
        "老师正在说明这道题怎么做。",
        "Giáo viên đang giải thích cách làm bài này."
    ),

    996: (
        "出租车司机把我们送到了酒店。",
        "Tài xế taxi đã đưa chúng tôi đến khách sạn."
    ),

    997: (
        "请把这些书送到教室。",
        "Hãy đưa những quyển sách này đến lớp học."
    ),

    998: (
        "我想把这本书送给妹妹。",
        "Tôi muốn tặng quyển sách này cho em gái."
    ),

    999: (
        "你帮我算一下这些东西多少钱。",
        "Bạn giúp tôi tính xem những thứ này bao nhiêu tiền."
    ),

    1000: (
        "虽然今天很冷，但是他还是去跑步了。",
        "Mặc dù hôm nay rất lạnh, nhưng anh ấy vẫn đi chạy bộ."
    ),

    1001: (
        "你想吃什么就随便点吧。",
        "Bạn muốn ăn gì thì cứ tùy ý gọi món."
    ),

    1002: (
        "有问题可以随时问我。",
        "Có vấn đề gì bạn có thể hỏi tôi bất cứ lúc nào."
    ),

    1003: (
        "今天下雨，所以我没有骑车。",
        "Hôm nay trời mưa nên tôi không đi xe đạp."
    ),

    1004: (
        "所有学生都已经到教室了。",
        "Tất cả học sinh đều đã đến lớp."
    ),

    1005: (
        "这只狗很可爱，我很喜欢它。",
        "Con chó này rất đáng yêu, tôi rất thích nó."
    ),

    1006: (
        "桌子上有几本书，它们都是我的。",
        "Trên bàn có vài quyển sách, chúng đều là của tôi."
    ),

    1007: (
        "王太太正在厨房做饭。",
        "Bà Vương đang nấu ăn trong bếp."
    ),

    1008: (
        "今天太阳很大，外面很热。",
        "Hôm nay mặt trời rất gắt, bên ngoài rất nóng."
    ),

    1009: (
        "他的工作态度很认真。",
        "Thái độ làm việc của anh ấy rất nghiêm túc."
    ),

    1010: (
        "我们正在讨论明天的旅行计划。",
        "Chúng tôi đang thảo luận kế hoạch du lịch ngày mai."
    ),

    1011: (
        "我买了一套新的运动服。",
        "Tôi đã mua một bộ đồ thể thao mới."
    ),

    1012: (
        "我特别喜欢中国菜。",
        "Tôi đặc biệt thích món ăn Trung Quốc."
    ),

    1013: (
        "这家饭店的特点是菜很好吃。",
        "Đặc điểm của nhà hàng này là món ăn rất ngon."
    ),

    1014: (
        "我的头有点儿疼。",
        "Đầu tôi hơi đau."
    ),

    1015: (
        "他手里提着一个很大的包。",
        "Anh ấy đang xách một chiếc túi rất lớn trong tay."
    ),

    1016: (
        "他在会上提出了一个新问题。",
        "Anh ấy đã nêu ra một vấn đề mới trong cuộc họp."
    ),

    1017: (
        "老师刚才提到明天要考试。",
        "Vừa nãy giáo viên nhắc đến việc ngày mai sẽ thi."
    ),

    1018: (
        "每天练习可以提高汉语水平。",
        "Luyện tập mỗi ngày có thể nâng cao trình độ tiếng Trung."
    ),

    1019: (
        "这道题我不会做。",
        "Bài này tôi không biết làm."
    ),

    1020: (
        "我最喜欢的体育运动是篮球。",
        "Môn thể thao tôi thích nhất là bóng rổ."
    ),

    1021: (
        "学校体育场里有很多学生。",
        "Trong sân vận động của trường có rất nhiều học sinh."
    ),

    1022: (
        "我们下午在体育馆打篮球。",
        "Buổi chiều chúng tôi chơi bóng rổ trong nhà thi đấu."
    ),

    1023: (
        "天上有很多白云。",
        "Trên trời có rất nhiều mây trắng."
    ),

    1024: (
        "我买了两条裤子。",
        "Tôi đã mua hai chiếc quần."
    ),

    1025: (
        "这个工作的条件很好。",
        "Điều kiện của công việc này rất tốt."
    ),

    1026: (
        "上课的时候大家要认真听讲。",
        "Trong giờ học mọi người phải chăm chú nghe giảng."
    ),

    1027: (
        "听说你明天要去北京。",
        "Nghe nói ngày mai bạn sẽ đi Bắc Kinh."
    ),

    1028: (
        "请在前面的车站停一下。",
        "Xin hãy dừng ở trạm phía trước."
    ),

    1029: (
        "这里不能停车。",
        "Ở đây không được đỗ xe."
    ),

    1030: (
        "商场后面有一个停车场。",
        "Phía sau trung tâm thương mại có một bãi đỗ xe."
    ),

    1031: (
        "这家饭店的菜挺好吃的。",
        "Món ăn của nhà hàng này khá ngon."
    ),

    1032: (
        "我最近身体挺好。",
        "Gần đây sức khỏe của tôi khá tốt."
    ),

    1033: (
        "这条路已经通了，可以开车过去。",
        "Con đường này đã thông, có thể lái xe qua."
    ),

    1034: (
        "我通过了这次汉语考试。",
        "Tôi đã vượt qua kỳ thi tiếng Trung lần này."
    ),

    1035: (
        "老师通知我们明天不上课。",
        "Giáo viên thông báo cho chúng tôi ngày mai nghỉ học."
    ),

    1036: (
        "他会说汉语，同时也会说英语。",
        "Anh ấy biết nói tiếng Trung, đồng thời cũng biết nói tiếng Anh."
    ),

    1037: (
        "下班以后我和同事一起吃饭。",
        "Sau giờ làm tôi ăn cơm cùng đồng nghiệp."
    ),

    1038: (
        "我们买了同样的手机。",
        "Chúng tôi đã mua cùng một loại điện thoại."
    ),

    1039: (
        "我的头有点儿不舒服。",
        "Đầu tôi hơi khó chịu."
    ),

    1040: (
        "她的头发很长。",
        "Tóc của cô ấy rất dài."
    ),

    # 头（里头） -> kiểm tra bằng 里头
    1041: (
        "书包里头有一本词典。",
        "Bên trong cặp sách có một quyển từ điển."
    ),

    1042: (
        "这张图片很漂亮。",
        "Bức ảnh này rất đẹp."
    ),

    1043: (
        "门打不开，你推一下吧。",
        "Cửa không mở được, bạn đẩy một chút đi."
    ),
}


def clean_target(raw_word):

    word = (raw_word or "").strip()

    # Ví dụ:
    # 头（里头） -> 里头
    # 家（科学家） -> 科学家
    match = re.search(r"（([^（）]+)）", word)

    if match:
        return match.group(1).strip()

    # Ví dụ 面1 -> 面
    word = re.sub(r"\d+$", "", word)

    return word.strip()


def main():

    if not SOURCE.exists():

        raise FileNotFoundError(
            f"\nKhông tìm thấy file:\n{SOURCE}\n"
        )

    # ======================================================
    # Đọc batch 4
    # ======================================================

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        fields = reader.fieldnames

        rows = list(reader)

    updated = []

    # ======================================================
    # Cập nhật
    # ======================================================

    for row in rows:

        word_id = int(row["MaTuVung"])

        if word_id not in FIXES:
            continue

        # Không được ghi đè dữ liệu đã duyệt
        if row["TrangThaiImport"] != "NEED_REVIEW":

            raise ValueError(
                f"\nMaTuVung {word_id}"
                f" ({row['ChuHan']}) "
                f"không phải NEED_REVIEW.\n"
                f"Hiện tại: {row['TrangThaiImport']}"
            )

        chinese, vietnamese = FIXES[word_id]

        target = clean_target(
            row["ChuHan"]
        )

        # Bắt buộc câu tiếng Trung có từ mục tiêu
        if target not in chinese:

            raise ValueError(
                f"\nLỖI CÂU VÍ DỤ\n"
                f"MaTuVung: {word_id}\n"
                f"ChuHan: {row['ChuHan']}\n"
                f"Target: {target}\n"
                f"Câu: {chinese}\n"
            )

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese

        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

        updated.append(word_id)

    # ======================================================
    # Kiểm tra ID
    # ======================================================

    missing = set(FIXES) - set(updated)

    if missing:

        raise ValueError(
            "\nKhông tìm thấy hoặc không cập nhật được:\n"
            f"{sorted(missing)}"
        )

    # ======================================================
    # Batch 5 bắt buộc đúng 100
    # ======================================================

    if len(FIXES) != 100:

        raise ValueError(
            f"FIXES phải có 100 câu, "
            f"hiện có {len(FIXES)}"
        )

    if len(updated) != 100:

        raise ValueError(
            f"\nDự kiến sửa 100 câu, "
            f"nhưng thực tế sửa {len(updated)}."
        )

    # ======================================================
    # Ghi batch 5
    # ======================================================

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

    # ======================================================
    # Thống kê
    # ======================================================

    remaining = sum(
        1
        for row in rows
        if row["TrangThaiImport"] == "NEED_REVIEW"
    )

    ready = sum(
        1
        for row in rows
        if row["TrangThaiImport"] == "READY"
    )

    print()
    print("=" * 60)
    print("HSK2 - BATCH 5")
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