import csv
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"

SOURCE = DATA / "offline_preview_hsk2_batch2.csv"
OUTPUT = DATA / "offline_preview_hsk2_batch3.csv"


# =========================================================
# BATCH 3: 100 CÂU HSK2
# 741 -> 841
# Bỏ 759 vì 健康 đã REAL/READY
# =========================================================

FIXES = {

    741: (
        "你可以坐公交车或者坐地铁去学校。",
        "Bạn có thể đi xe buýt hoặc tàu điện ngầm đến trường."
    ),

    742: (
        "我希望有机会去中国学习汉语。",
        "Tôi hy vọng có cơ hội đến Trung Quốc học tiếng Trung."
    ),

    743: (
        "奶奶家养了三只鸡。",
        "Nhà bà nuôi ba con gà."
    ),

    744: (
        "我弟弟现在上小学三年级。",
        "Em trai tôi hiện đang học lớp ba tiểu học."
    ),

    745: (
        "别急，我们还有时间。",
        "Đừng vội, chúng ta vẫn còn thời gian."
    ),

    746: (
        "我计划明年去北京旅行。",
        "Tôi dự định năm sau đi du lịch Bắc Kinh."
    ),

    747: (
        "学校的计算机都可以上网。",
        "Các máy tính của trường đều có thể truy cập Internet."
    ),

    748: (
        "咖啡里请不要加太多糖。",
        "Xin đừng cho quá nhiều đường vào cà phê."
    ),

    749: (
        "明天要考试了，大家加油！",
        "Ngày mai thi rồi, mọi người cố lên!"
    ),

    750: (
        "我的哥哥想成为一名科学家。",
        "Anh trai tôi muốn trở thành một nhà khoa học."
    ),

    751: (
        "她出生在一个幸福的家庭。",
        "Cô ấy sinh ra trong một gia đình hạnh phúc."
    ),

    752: (
        "开学第一天，很多家长送孩子来学校。",
        "Ngày đầu khai giảng, nhiều phụ huynh đưa con đến trường."
    ),

    753: (
        "这张票是假的，不能用。",
        "Tấm vé này là giả, không thể sử dụng."
    ),

    754: (
        "这个假期我想在家好好休息。",
        "Kỳ nghỉ này tôi muốn nghỉ ngơi thật tốt ở nhà."
    ),

    755: (
        "考试以后老师会检查我们的答案。",
        "Sau kỳ thi giáo viên sẽ kiểm tra đáp án của chúng tôi."
    ),

    756: (
        "今天很高兴见到你。",
        "Hôm nay rất vui được gặp bạn."
    ),

    757: (
        "我以前见过这位老师。",
        "Trước đây tôi đã từng gặp giáo viên này."
    ),

    758: (
        "我今天买了两件衣服。",
        "Hôm nay tôi đã mua hai bộ quần áo."
    ),

    760: (
        "老师正在给我们讲这个故事。",
        "Giáo viên đang kể câu chuyện này cho chúng tôi."
    ),

    761: (
        "上课的时候不要大声讲话。",
        "Trong giờ học đừng nói chuyện lớn tiếng."
    ),

    762: (
        "我已经把今天的作业交了。",
        "Tôi đã nộp bài tập hôm nay rồi."
    ),

    763: (
        "请把这本书交给王老师。",
        "Hãy đưa quyển sách này cho thầy Vương."
    ),

    764: (
        "我喜欢和不同国家的人交朋友。",
        "Tôi thích kết bạn với người từ các quốc gia khác nhau."
    ),

    765: (
        "这里的交通很方便。",
        "Giao thông ở đây rất thuận tiện."
    ),

    766: (
        "这支笔两块五角钱。",
        "Cây bút này giá hai tệ năm hào."
    ),

    767: (
        "从这个角度看，问题很简单。",
        "Nhìn từ góc độ này, vấn đề rất đơn giản."
    ),

    768: (
        "春节的时候我们全家一起吃饺子。",
        "Vào dịp Tết, cả gia đình tôi cùng ăn sủi cảo."
    ),

    769: (
        "我走了一天，脚有点儿疼。",
        "Tôi đi cả ngày nên chân hơi đau."
    ),

    770: (
        "这种水果叫作火龙果。",
        "Loại trái cây này được gọi là thanh long."
    ),

    771: (
        "我的妈妈是一名中学教师。",
        "Mẹ tôi là một giáo viên trung học."
    ),

    772: (
        "学生们正在教室里上课。",
        "Các học sinh đang học trong lớp."
    ),

    773: (
        "这位老师有十年的教学经验。",
        "Giáo viên này có mười năm kinh nghiệm giảng dạy."
    ),

    774: (
        "父母应该重视孩子的教育。",
        "Cha mẹ nên coi trọng việc giáo dục con cái."
    ),

    775: (
        "我下午去机场接朋友。",
        "Buổi chiều tôi ra sân bay đón bạn."
    ),

    776: (
        "我刚刚接到妈妈的电话。",
        "Tôi vừa nhận được điện thoại của mẹ."
    ),

    777: (
        "我很高兴接受你的邀请。",
        "Tôi rất vui khi nhận lời mời của bạn."
    ),

    778: (
        "接下来我们学习新的课文。",
        "Tiếp theo chúng ta học bài khóa mới."
    ),

    779: (
        "他喝了一口水，接着继续工作。",
        "Anh ấy uống một ngụm nước rồi tiếp tục làm việc."
    ),

    780: (
        "这条街晚上非常热闹。",
        "Con phố này buổi tối rất nhộn nhịp."
    ),

    781: (
        "今天上午我们有四节课。",
        "Sáng nay chúng tôi có bốn tiết học."
    ),

    782: (
        "这个电视节目很有意思。",
        "Chương trình truyền hình này rất thú vị."
    ),

    783: (
        "春节是中国很重要的节日。",
        "Tết Nguyên Đán là một ngày lễ rất quan trọng của Trung Quốc."
    ),

    784: (
        "我等了很久，结果他没有来。",
        "Tôi đã đợi rất lâu, cuối cùng anh ấy không đến."
    ),

    785: (
        "我可以借你的词典用一下吗？",
        "Tôi có thể mượn từ điển của bạn dùng một chút không?"
    ),

    786: (
        "我买了两斤苹果。",
        "Tôi đã mua hai cân táo."
    ),

    787: (
        "今后我要每天练习汉语。",
        "Từ nay về sau tôi sẽ luyện tiếng Trung mỗi ngày."
    ),

    788: (
        "请不要进入这个房间。",
        "Xin đừng đi vào căn phòng này."
    ),

    789: (
        "比赛正在进行，请大家安静。",
        "Trận đấu đang diễn ra, xin mọi người giữ yên lặng."
    ),

    790: (
        "我家离学校很近。",
        "Nhà tôi rất gần trường."
    ),

    791: (
        "我经常和朋友一起去图书馆。",
        "Tôi thường xuyên đi thư viện cùng bạn."
    ),

    792: (
        "每天上学我都要经过这个公园。",
        "Mỗi ngày đi học tôi đều đi qua công viên này."
    ),

    793: (
        "饭店经理正在和客人说话。",
        "Quản lý nhà hàng đang nói chuyện với khách."
    ),

    794: (
        "他不喝酒，只喝茶。",
        "Anh ấy không uống rượu, chỉ uống trà."
    ),

    795: (
        "我们晚上住在机场附近的酒店。",
        "Buổi tối chúng tôi ở khách sạn gần sân bay."
    ),

    796: (
        "电影就要开始了，我们进去吧。",
        "Bộ phim sắp bắt đầu rồi, chúng ta vào thôi."
    ),

    797: (
        "老师举了一个简单的例子。",
        "Giáo viên đã nêu một ví dụ đơn giản."
    ),

    798: (
        "知道答案的同学请举手。",
        "Bạn nào biết đáp án thì hãy giơ tay."
    ),

    799: (
        "学校明天要举行运动会。",
        "Ngày mai trường sẽ tổ chức hội thao."
    ),

    800: (
        "老师让我读第一句。",
        "Giáo viên bảo tôi đọc câu đầu tiên."
    ),

    801: (
        "这个句子我已经读懂了。",
        "Tôi đã đọc hiểu câu này rồi."
    ),

    802: (
        "这张卡是我的银行卡。",
        "Tấm thẻ này là thẻ ngân hàng của tôi."
    ),

    803: (
        "电脑开机以后有点儿慢。",
        "Máy tính sau khi khởi động hơi chậm."
    ),

    804: (
        "今天见到老朋友，我很开心。",
        "Hôm nay gặp lại bạn cũ, tôi rất vui."
    ),

    805: (
        "下星期学校就要开学了。",
        "Tuần sau trường sẽ bắt đầu học kỳ mới."
    ),

    806: (
        "我想听听你对这件事的看法。",
        "Tôi muốn nghe quan điểm của bạn về việc này."
    ),

    807: (
        "考生必须按时进入考场。",
        "Thí sinh phải vào phòng thi đúng giờ."
    ),

    808: (
        "他累了，靠在椅子上休息。",
        "Anh ấy mệt nên dựa vào ghế nghỉ ngơi."
    ),

    809: (
        "我今天上午要考两科。",
        "Sáng nay tôi phải thi hai môn."
    ),

    810: (
        "我弟弟对科学很感兴趣。",
        "Em trai tôi rất hứng thú với khoa học."
    ),

    811: (
        "这只小猫非常可爱。",
        "Chú mèo con này rất đáng yêu."
    ),

    812: (
        "今天下午可能会下雨。",
        "Chiều nay có thể trời sẽ mưa."
    ),

    813: (
        "晚上一个人走这条路有点儿可怕。",
        "Buổi tối đi một mình trên con đường này hơi đáng sợ."
    ),

    814: (
        "我很想去，可是今天没有时间。",
        "Tôi rất muốn đi, nhưng hôm nay không có thời gian."
    ),

    815: (
        "这里可以坐下吗？",
        "Ở đây có thể ngồi được không?"
    ),

    816: (
        "这个苹果大约两百克。",
        "Quả táo này nặng khoảng hai trăm gam."
    ),

    817: (
        "现在八点一刻，我们该出发了。",
        "Bây giờ là tám giờ mười lăm, chúng ta nên xuất phát rồi."
    ),

    818: (
        "家里来了几位客人。",
        "Nhà có vài vị khách đến."
    ),

    819: (
        "课堂上请认真听老师讲课。",
        "Trong lớp hãy chú ý nghe giáo viên giảng bài."
    ),

    820: (
        "早上的空气很新鲜。",
        "Không khí buổi sáng rất trong lành."
    ),

    821: (
        "小妹妹找不到妈妈，急得哭了。",
        "Cô bé không tìm thấy mẹ nên lo đến phát khóc."
    ),

    822: (
        "中午没时间，我只吃了一份快餐。",
        "Buổi trưa không có thời gian nên tôi chỉ ăn một suất đồ ăn nhanh."
    ),

    823: (
        "快点儿，我们马上要迟到了！",
        "Nhanh lên, chúng ta sắp muộn rồi!"
    ),

    824: (
        "祝你生日快乐！",
        "Chúc bạn sinh nhật vui vẻ!"
    ),

    825: (
        "火车快要开了，我们上车吧。",
        "Tàu sắp chạy rồi, chúng ta lên tàu thôi."
    ),

    826: (
        "中国人吃饭常常用筷子。",
        "Người Trung Quốc thường dùng đũa khi ăn cơm."
    ),

    827: (
        "请帮我把门拉开。",
        "Hãy giúp tôi kéo cửa ra."
    ),

    828: (
        "我来自越南，现在在北京学习。",
        "Tôi đến từ Việt Nam, hiện đang học ở Bắc Kinh."
    ),

    829: (
        "今天的天空很蓝。",
        "Bầu trời hôm nay rất xanh."
    ),

    830: (
        "他今天穿了一件蓝色的衣服。",
        "Hôm nay anh ấy mặc một bộ quần áo màu xanh lam."
    ),

    831: (
        "我哥哥每个周末都打篮球。",
        "Anh trai tôi chơi bóng rổ mỗi cuối tuần."
    ),

    832: (
        "老王每天骑自行车上班。",
        "Ông Vương đi xe đạp đi làm mỗi ngày."
    ),

    833: (
        "我们应该关心老年人的健康。",
        "Chúng ta nên quan tâm đến sức khỏe của người cao tuổi."
    ),

    834: (
        "昨天我见到了一位十年没见的老朋友。",
        "Hôm qua tôi gặp một người bạn cũ đã mười năm không gặp."
    ),

    835: (
        "他最近老是忘记带手机。",
        "Gần đây anh ấy cứ hay quên mang điện thoại."
    ),

    836: (
        "学校离我家只有两公里。",
        "Trường chỉ cách nhà tôi hai ki-lô-mét."
    ),

    837: (
        "他明天就要离开北京了。",
        "Ngày mai anh ấy sẽ rời Bắc Kinh."
    ),

    838: (
        "这是朋友送给我的生日礼物。",
        "Đây là quà sinh nhật bạn tặng tôi."
    ),

    839: (
        "我的钱包在书包里头。",
        "Ví của tôi ở bên trong cặp sách."
    ),

    840: (
        "我的理想是成为一名汉语老师。",
        "Lý tưởng của tôi là trở thành một giáo viên tiếng Trung."
    ),

    841: (
        "我喜欢很多运动，例如游泳和跑步。",
        "Tôi thích nhiều môn thể thao, ví dụ như bơi và chạy bộ."
    ),
}


def clean_target(raw_word):
    """
    Xử lý:
    家（科学家） -> 科学家
    老（老王）   -> 老王
    称1         -> 称
    面1         -> 面
    """

    word = (raw_word or "").strip()

    match = re.search(
        r"（([^（）]+)）",
        word
    )

    if match:
        return match.group(1).strip()

    word = re.sub(
        r"\d+$",
        "",
        word
    )

    return word.strip()


def main():

    if not SOURCE.exists():

        raise FileNotFoundError(
            f"Không tìm thấy:\n{SOURCE}"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        fields = reader.fieldnames
        rows = list(reader)

    updated = []

    for row in rows:

        word_id = int(
            row["MaTuVung"]
        )

        if word_id not in FIXES:
            continue

        # Chỉ sửa các câu chưa duyệt
        if row["TrangThaiImport"] != "NEED_REVIEW":

            raise ValueError(
                f"Mã {word_id} "
                f"({row['ChuHan']}) "
                f"không phải NEED_REVIEW: "
                f"{row['TrangThaiImport']}"
            )

        chinese, vietnamese = (
            FIXES[word_id]
        )

        target = clean_target(
            row["ChuHan"]
        )

        # Bảo đảm từ cần học có trong câu Trung
        if target not in chinese:

            raise ValueError(
                f"Mã {word_id}: "
                f"câu không chứa từ '{target}'\n"
                f"Câu: {chinese}"
            )

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese

        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"

        updated.append(
            word_id
        )

    missing = (
        set(FIXES)
        - set(updated)
    )

    if missing:

        raise ValueError(
            f"Các mã chưa sửa được: "
            f"{sorted(missing)}"
        )

    # Batch này phải đúng 100 câu
    if len(updated) != 100:

        raise ValueError(
            f"Dự kiến 100 câu "
            f"nhưng thực tế sửa "
            f"{len(updated)} câu."
        )

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

    remaining = sum(
        1
        for row in rows
        if row["TrangThaiImport"]
        == "NEED_REVIEW"
    )

    print()
    print("=" * 55)

    print(
        f"Đã sửa thêm: "
        f"{len(updated)} câu HSK2"
    )

    print(
        f"Còn NEED_REVIEW: "
        f"{remaining}"
    )

    print(
        f"File mới: {OUTPUT}"
    )

    print(
        "CHƯA THAY ĐỔI SQL SERVER."
    )

    print("=" * 55)


if __name__ == "__main__":
    main()