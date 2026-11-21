import csv
import re
from pathlib import Path


DATA = Path(__file__).resolve().parent / "data"

SOURCE = DATA / "offline_preview_hsk2_batch3.csv"
OUTPUT = DATA / "offline_preview_hsk2_batch4.csv"


# ==========================================================
# HSK2 - BATCH 4
# 100 từ tiếp theo
#
# Phạm vi:
#   842 -> 943
#
# Bỏ:
#   859 旅行  -> đã REAL/READY
#   893 努力  -> đã REAL/READY
#
# Tổng cộng: 102 - 2 = 100 từ
# ==========================================================

FIXES = {

    842: (
        "老师给我们举了一个简单的例子。",
        "Giáo viên đã đưa ra cho chúng tôi một ví dụ đơn giản."
    ),

    843: (
        "她洗完脸就去上学了。",
        "Cô ấy rửa mặt xong thì đi học."
    ),

    844: (
        "我每天早上练汉语发音。",
        "Mỗi sáng tôi luyện phát âm tiếng Trung."
    ),

    845: (
        "我每天做汉语听力练习。",
        "Mỗi ngày tôi làm bài luyện nghe tiếng Trung."
    ),

    846: (
        "晚上的风有点儿凉。",
        "Gió buổi tối hơi lạnh."
    ),

    847: (
        "下雨以后天气凉快多了。",
        "Sau khi mưa, thời tiết mát mẻ hơn nhiều."
    ),

    848: (
        "房间里的灯很亮。",
        "Đèn trong phòng rất sáng."
    ),

    849: (
        "门口停着三辆汽车。",
        "Trước cửa đang đỗ ba chiếc ô tô."
    ),

    850: (
        "今天晚上气温会到零下五度。",
        "Tối nay nhiệt độ sẽ xuống âm năm độ."
    ),

    851: (
        "请给我留一个座位。",
        "Hãy giữ lại cho tôi một chỗ ngồi."
    ),

    852: (
        "他决定留下来再住两天。",
        "Anh ấy quyết định ở lại thêm hai ngày."
    ),

    853: (
        "学校里有很多外国留学生。",
        "Trong trường có rất nhiều du học sinh nước ngoài."
    ),

    854: (
        "河里的水慢慢地流向南方。",
        "Nước trong sông từ từ chảy về phía nam."
    ),

    855: (
        "她汉语说得很流利。",
        "Cô ấy nói tiếng Trung rất lưu loát."
    ),

    856: (
        "这首歌最近很流行。",
        "Bài hát này gần đây rất thịnh hành."
    ),

    857: (
        "路边有一家小咖啡店。",
        "Ven đường có một quán cà phê nhỏ."
    ),

    858: (
        "旅客们正在排队上车。",
        "Các hành khách đang xếp hàng lên xe."
    ),

    # 859 旅行 đã REAL/READY nên bỏ qua

    860: (
        "暑假我想去北京旅游。",
        "Kỳ nghỉ hè tôi muốn đi du lịch Bắc Kinh."
    ),

    861: (
        "春天来了，树叶都变绿了。",
        "Mùa xuân đến rồi, lá cây đều chuyển xanh."
    ),

    862: (
        "我最喜欢绿色的书包。",
        "Tôi thích nhất chiếc cặp màu xanh lá."
    ),

    863: (
        "这家商店卖很多水果。",
        "Cửa hàng này bán rất nhiều trái cây."
    ),

    864: (
        "公交车上已经坐满了人。",
        "Trên xe buýt đã đầy người."
    ),

    865: (
        "我对这次考试成绩很满意。",
        "Tôi rất hài lòng với kết quả kỳ thi lần này."
    ),

    866: (
        "那只猫正在桌子下面睡觉。",
        "Con mèo đó đang ngủ dưới bàn."
    ),

    867: (
        "我家离学校有两千米。",
        "Nhà tôi cách trường hai nghìn mét."
    ),

    # 面1: dùng 面 với nghĩa lượng từ
    868: (
        "墙上有一面镜子。",
        "Trên tường có một chiếc gương."
    ),

    # 面2: dùng 面 với nghĩa mì
    869: (
        "我中午吃了一碗牛肉面。",
        "Buổi trưa tôi đã ăn một bát mì bò."
    ),

    870: (
        "老师站在我们面前讲话。",
        "Giáo viên đứng trước mặt chúng tôi nói chuyện."
    ),

    871: (
        "我们班有二十名学生。",
        "Lớp chúng tôi có hai mươi học sinh."
    ),

    872: (
        "请在这里写上学校的名称。",
        "Hãy viết tên của trường vào đây."
    ),

    873: (
        "老师把学生名单放在桌子上。",
        "Giáo viên đặt danh sách học sinh lên bàn."
    ),

    874: (
        "她最喜欢的明星是一位歌手。",
        "Ngôi sao cô ấy thích nhất là một ca sĩ."
    ),

    875: (
        "我这次来北京的目的是学习汉语。",
        "Mục đích lần này tôi đến Bắc Kinh là học tiếng Trung."
    ),

    876: (
        "请拿出你的学生证。",
        "Hãy lấy thẻ học sinh của bạn ra."
    ),

    877: (
        "我终于拿到考试成绩了。",
        "Cuối cùng tôi đã nhận được kết quả thi."
    ),

    878: (
        "我那会儿还在上小学。",
        "Lúc đó tôi vẫn còn học tiểu học."
    ),

    879: (
        "外面那么冷，你多穿一点儿吧。",
        "Bên ngoài lạnh như vậy, bạn mặc thêm một chút đi."
    ),

    880: (
        "那时候我每天骑自行车上学。",
        "Lúc đó tôi đi xe đạp đến trường mỗi ngày."
    ),

    881: (
        "请不要那样说话。",
        "Xin đừng nói chuyện như vậy."
    ),

    882: (
        "冬天南方比北方暖和一些。",
        "Mùa đông miền Nam ấm hơn miền Bắc một chút."
    ),

    883: (
        "听到这个消息以后，她很难过。",
        "Sau khi nghe tin này, cô ấy rất buồn."
    ),

    884: (
        "这件衣服的颜色有点儿难看。",
        "Màu của bộ quần áo này hơi xấu."
    ),

    885: (
        "我今天感冒了，身体很难受。",
        "Hôm nay tôi bị cảm nên cơ thể rất khó chịu."
    ),

    886: (
        "这道数学题对我来说是个难题。",
        "Bài toán này đối với tôi là một bài khó."
    ),

    887: (
        "这个声音太难听了。",
        "Âm thanh này khó nghe quá."
    ),

    888: (
        "我希望明年能够去中国学习。",
        "Tôi hy vọng năm sau có thể đến Trung Quốc học."
    ),

    889: (
        "我妹妹今年上五年级。",
        "Em gái tôi năm nay học lớp năm."
    ),

    890: (
        "王老师很年轻。",
        "Thầy Vương rất trẻ."
    ),

    891: (
        "树上有两只小鸟。",
        "Trên cây có hai con chim nhỏ."
    ),

    892: (
        "别弄坏我的电脑。",
        "Đừng làm hỏng máy tính của tôi."
    ),

    # 893 努力 đã REAL/READY nên bỏ qua

    894: (
        "小孩子正在地上爬。",
        "Đứa trẻ đang bò trên mặt đất."
    ),

    895: (
        "周末我们一起去爬山吧。",
        "Cuối tuần chúng ta cùng đi leo núi nhé."
    ),

    896: (
        "我妹妹很怕狗。",
        "Em gái tôi rất sợ chó."
    ),

    897: (
        "教室里有三排桌子。",
        "Trong lớp học có ba hàng bàn."
    ),

    898: (
        "买票的人正在门口排队。",
        "Những người mua vé đang xếp hàng ở cửa."
    ),

    899: (
        "下午我们去打排球。",
        "Buổi chiều chúng tôi đi chơi bóng chuyền."
    ),

    900: (
        "小心，别碰桌子上的杯子。",
        "Cẩn thận, đừng chạm vào chiếc cốc trên bàn."
    ),

    901: (
        "我昨天在超市碰到了一位老朋友。",
        "Hôm qua tôi tình cờ gặp một người bạn cũ ở siêu thị."
    ),

    902: (
        "我刚才在楼下碰见王老师。",
        "Vừa nãy tôi tình cờ gặp thầy Vương ở dưới tầng."
    ),

    903: (
        "老师让我们写一篇短文。",
        "Giáo viên yêu cầu chúng tôi viết một bài văn ngắn."
    ),

    904: (
        "这件衣服又好看又便宜。",
        "Bộ quần áo này vừa đẹp vừa rẻ."
    ),

    905: (
        "我想吃一片面包。",
        "Tôi muốn ăn một lát bánh mì."
    ),

    906: (
        "这个公园春天很漂亮。",
        "Công viên này vào mùa xuân rất đẹp."
    ),

    907: (
        "这条路很平。",
        "Con đường này rất bằng phẳng."
    ),

    908: (
        "祝你一路平安。",
        "Chúc bạn thượng lộ bình an."
    ),

    909: (
        "我平常七点起床。",
        "Bình thường tôi thức dậy lúc bảy giờ."
    ),

    910: (
        "在我们班，大家都是平等的。",
        "Trong lớp chúng tôi, mọi người đều bình đẳng."
    ),

    911: (
        "我平时喜欢在家看书。",
        "Bình thường tôi thích đọc sách ở nhà."
    ),

    912: (
        "请给我一瓶水。",
        "Hãy cho tôi một chai nước."
    ),

    913: (
        "桌子上有一个空瓶子。",
        "Trên bàn có một chiếc chai rỗng."
    ),

    914: (
        "这只是一家普通的小商店。",
        "Đây chỉ là một cửa hàng nhỏ bình thường."
    ),

    915: (
        "她的普通话说得很好。",
        "Cô ấy nói tiếng Phổ thông rất tốt."
    ),

    916: (
        "这个问题我懂，其他问题还不懂。",
        "Vấn đề này tôi hiểu, những vấn đề khác thì vẫn chưa hiểu."
    ),

    917: (
        "我买了三本书，其中一本是汉语书。",
        "Tôi mua ba quyển sách, trong đó một quyển là sách tiếng Trung."
    ),

    918: (
        "他每天骑自行车去上班。",
        "Anh ấy đi xe đạp đi làm mỗi ngày."
    ),

    919: (
        "下雨天骑车要小心。",
        "Ngày mưa đi xe đạp phải cẩn thận."
    ),

    920: (
        "飞机十分钟以后起飞。",
        "Máy bay sẽ cất cánh sau mười phút."
    ),

    921: (
        "这个气球里没有气了。",
        "Quả bóng này hết hơi rồi."
    ),

    922: (
        "今天的气温是二十五度。",
        "Nhiệt độ hôm nay là hai mươi lăm độ."
    ),

    923: (
        "这台电脑三千块钱。",
        "Chiếc máy tính này giá ba nghìn tệ."
    ),

    924: (
        "这个西瓜有五千克。",
        "Quả dưa hấu này nặng năm ki-lô-gam."
    ),

    925: (
        "前年我第一次去了上海。",
        "Năm kia tôi lần đầu tiên đến Thượng Hải."
    ),

    926: (
        "墙上挂着一张全家照片。",
        "Trên tường treo một bức ảnh gia đình."
    ),

    927: (
        "很多青年喜欢来这里运动。",
        "Nhiều thanh niên thích đến đây tập thể thao."
    ),

    928: (
        "这个活动很适合青少年参加。",
        "Hoạt động này rất phù hợp cho thanh thiếu niên tham gia."
    ),

    929: (
        "这个箱子很轻，我一个人能拿。",
        "Chiếc vali này rất nhẹ, một mình tôi có thể cầm được."
    ),

    930: (
        "老师讲得很清楚。",
        "Giáo viên giảng rất rõ ràng."
    ),

    931: (
        "雨停了，天晴了。",
        "Mưa đã tạnh, trời đã quang."
    ),

    932: (
        "晴天的时候我们常去公园。",
        "Khi trời nắng chúng tôi thường đi công viên."
    ),

    933: (
        "今天我生日，我请客。",
        "Hôm nay là sinh nhật tôi, tôi mời mọi người."
    ),

    934: (
        "老师接受了我的请求。",
        "Giáo viên đã chấp nhận yêu cầu của tôi."
    ),

    935: (
        "我最喜欢北京的秋天。",
        "Tôi thích nhất mùa thu ở Bắc Kinh."
    ),

    936: (
        "他来求我帮他一次。",
        "Anh ấy đến cầu xin tôi giúp anh ấy một lần."
    ),

    937: (
        "学生们正在球场上踢足球。",
        "Các học sinh đang đá bóng trên sân."
    ),

    938: (
        "我哥哥参加了学校的球队。",
        "Anh trai tôi đã tham gia đội bóng của trường."
    ),

    939: (
        "我买了一双新的球鞋。",
        "Tôi đã mua một đôi giày thể thao mới."
    ),

    940: (
        "我下午去银行取钱。",
        "Buổi chiều tôi đến ngân hàng rút tiền."
    ),

    941: (
        "她在比赛中取得了好成绩。",
        "Cô ấy đã đạt được thành tích tốt trong cuộc thi."
    ),

    942: (
        "我们班的学生全来了。",
        "Học sinh lớp chúng tôi đều đến hết rồi."
    ),

    943: (
        "今天的作业我已经全部做完了。",
        "Bài tập hôm nay tôi đã làm xong toàn bộ rồi."
    ),
}


def clean_target(raw_word):
    """
    Chuẩn hóa từ mục tiêu.

    Ví dụ:
        面1 -> 面
        面2 -> 面
        家（科学家） -> 科学家
        老（老王） -> 老王
    """

    word = (raw_word or "").strip()

    # Nếu có phần trong ngoặc Trung Quốc thì lấy phần đó
    match = re.search(r"（([^（）]+)）", word)

    if match:
        return match.group(1).strip()

    # Xóa số ở cuối: 面1 -> 面
    word = re.sub(r"\d+$", "", word)

    return word.strip()


def main():

    # ------------------------------------------------------
    # 1. Kiểm tra file nguồn
    # ------------------------------------------------------

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"\nKhông tìm thấy file nguồn:\n{SOURCE}\n"
            f"Hãy kiểm tra offline_preview_hsk2_batch3.csv."
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

    updated = []

    # ------------------------------------------------------
    # 3. Cập nhật 100 câu
    # ------------------------------------------------------

    for row in rows:

        word_id = int(row["MaTuVung"])

        if word_id not in FIXES:
            continue

        # Không cho phép ghi đè những câu đã hoàn thành
        if row["TrangThaiImport"] != "NEED_REVIEW":

            raise ValueError(
                f"\nMã {word_id} - {row['ChuHan']}\n"
                f"không còn NEED_REVIEW.\n"
                f"Trạng thái hiện tại: "
                f"{row['TrangThaiImport']}"
            )

        chinese, vietnamese = FIXES[word_id]

        target = clean_target(
            row["ChuHan"]
        )

        # --------------------------------------------------
        # Bắt buộc câu ví dụ phải chứa từ cần học
        # --------------------------------------------------

        if target not in chinese:

            raise ValueError(
                f"\nLỖI TỪ VỰNG\n"
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

    # ------------------------------------------------------
    # 4. Kiểm tra xem có ID nào trong FIXES không tồn tại
    # ------------------------------------------------------

    missing = set(FIXES) - set(updated)

    if missing:

        raise ValueError(
            "\nKhông cập nhật được các MaTuVung:\n"
            f"{sorted(missing)}"
        )

    # ------------------------------------------------------
    # 5. Batch 4 bắt buộc phải đúng 100 câu
    # ------------------------------------------------------

    if len(updated) != 100:

        raise ValueError(
            f"\nBATCH 4 KHÔNG ĐÚNG SỐ LƯỢNG.\n"
            f"Dự kiến: 100\n"
            f"Thực tế: {len(updated)}"
        )

    # ------------------------------------------------------
    # 6. Ghi CSV mới
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
    # 7. Thống kê số từ còn lại
    # ------------------------------------------------------

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
    print("HSK2 - BATCH 4")
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