import csv
import re
from pathlib import Path


DATA = Path(__file__).resolve().parent / "data"

SOURCE = DATA / "offline_preview_hsk2_batch5.csv"
OUTPUT = DATA / "offline_preview_hsk2_batch6.csv"


# ==========================================================
# HSK2 - BATCH 6
# MaTuVung 1044 -> 1143
# Tổng cộng: 100 từ
# ==========================================================

FIXES = {

    1044: (
        "我的腿有点儿疼。",
        "Chân tôi hơi đau."
    ),

    1045: (
        "他从外地来北京工作。",
        "Anh ấy từ nơi khác đến Bắc Kinh làm việc."
    ),

    1046: (
        "今天晚上我想点外卖。",
        "Tối nay tôi muốn gọi đồ ăn giao tận nơi."
    ),

    1047: (
        "这本书我已经看完了。",
        "Tôi đã đọc xong quyển sách này rồi."
    ),

    1048: (
        "我已经完成今天的作业了。",
        "Tôi đã hoàn thành bài tập hôm nay rồi."
    ),

    1049: (
        "我完全同意你的看法。",
        "Tôi hoàn toàn đồng ý với quan điểm của bạn."
    ),

    1050: (
        "时间不早了，晚安！",
        "Không còn sớm nữa, chúc ngủ ngon!"
    ),

    1051: (
        "爷爷每天晚上都看晚报。",
        "Ông tôi tối nào cũng đọc báo chiều."
    ),

    1052: (
        "我们七点一起吃晚餐。",
        "Chúng tôi cùng ăn tối lúc bảy giờ."
    ),

    1053: (
        "学校今晚举行新年晚会。",
        "Tối nay trường tổ chức buổi liên hoan năm mới."
    ),

    1054: (
        "我早上喝了一碗粥。",
        "Buổi sáng tôi đã ăn một bát cháo."
    ),

    1055: (
        "这个城市有一百多万人。",
        "Thành phố này có hơn một triệu dân."
    ),

    1056: (
        "这张网是用来抓鱼的。",
        "Chiếc lưới này dùng để bắt cá."
    ),

    1057: (
        "周末我们一起去打网球。",
        "Cuối tuần chúng ta cùng đi chơi quần vợt."
    ),

    1058: (
        "我每天都看这个学习网站。",
        "Tôi xem trang web học tập này mỗi ngày."
    ),

    1059: (
        "从这里一直往前走就到了。",
        "Từ đây cứ đi thẳng về phía trước là tới."
    ),

    1060: (
        "妈妈为我准备了生日礼物。",
        "Mẹ đã chuẩn bị quà sinh nhật cho tôi."
    ),

    1061: (
        "你为什么学习汉语？",
        "Tại sao bạn học tiếng Trung?"
    ),

    1062: (
        "那位老师是我的汉语老师。",
        "Vị giáo viên đó là giáo viên tiếng Trung của tôi."
    ),

    1063: (
        "这个菜的味道很好。",
        "Món ăn này có hương vị rất ngon."
    ),

    1064: (
        "喂，你好，请问王老师在吗？",
        "A lô, xin chào, cho hỏi thầy Vương có ở đó không?"
    ),

    1065: (
        "今天的温度是二十八度。",
        "Nhiệt độ hôm nay là hai mươi tám độ."
    ),

    1066: (
        "我闻到了咖啡的香味。",
        "Tôi ngửi thấy mùi thơm của cà phê."
    ),

    1067: (
        "我第一次来这里，所以向警察问路。",
        "Tôi lần đầu đến đây nên hỏi đường cảnh sát."
    ),

    1068: (
        "这个问题我还不明白。",
        "Vấn đề này tôi vẫn chưa hiểu."
    ),

    1069: (
        "我们中午十二点吃午餐。",
        "Chúng tôi ăn trưa lúc mười hai giờ."
    ),

    1070: (
        "我每天中午午睡半个小时。",
        "Mỗi trưa tôi ngủ trưa nửa tiếng."
    ),

    1071: (
        "中国的西北冬天很冷。",
        "Vùng tây bắc Trung Quốc mùa đông rất lạnh."
    ),

    1072: (
        "这家饭店既有中餐，也有西餐。",
        "Nhà hàng này có cả món Trung Quốc lẫn món Tây."
    ),

    1073: (
        "很多西方人喜欢学习汉语。",
        "Nhiều người phương Tây thích học tiếng Trung."
    ),

    1074: (
        "这个城市在中国西南。",
        "Thành phố này nằm ở tây nam Trung Quốc."
    ),

    1075: (
        "这家医院有中医，也有西医。",
        "Bệnh viện này có cả Đông y lẫn Tây y."
    ),

    1076: (
        "我已经习惯这里的生活了。",
        "Tôi đã quen với cuộc sống ở đây rồi."
    ),

    1077: (
        "我家的洗衣机坏了。",
        "Máy giặt nhà tôi bị hỏng rồi."
    ),

    1078: (
        "运动以后我想先洗澡。",
        "Sau khi tập thể dục tôi muốn tắm trước."
    ),

    1079: (
        "天气预报说明天会下雪。",
        "Dự báo thời tiết nói ngày mai sẽ có tuyết."
    ),

    1080: (
        "下周我们要进行汉语考试。",
        "Tuần sau chúng tôi sẽ thi tiếng Trung."
    ),

    1081: (
        "我最喜欢夏天，因为可以游泳。",
        "Tôi thích mùa hè nhất vì có thể bơi."
    ),

    1082: (
        "这两个问题的答案完全相同。",
        "Đáp án của hai câu hỏi này hoàn toàn giống nhau."
    ),

    1083: (
        "我相信你一定能做好。",
        "Tôi tin bạn nhất định có thể làm tốt."
    ),

    1084: (
        "电话响了，你去接一下吧。",
        "Điện thoại reo rồi, bạn đi nghe đi."
    ),

    1085: (
        "说到北京，我马上想到长城。",
        "Nhắc đến Bắc Kinh, tôi lập tức nghĩ đến Vạn Lý Trường Thành."
    ),

    1086: (
        "我有一个新的想法。",
        "Tôi có một ý tưởng mới."
    ),

    1087: (
        "我突然想起今天是妈妈的生日。",
        "Tôi đột nhiên nhớ ra hôm nay là sinh nhật mẹ."
    ),

    1088: (
        "他向老师问了一个问题。",
        "Anh ấy hỏi giáo viên một câu hỏi."
    ),

    1089: (
        "我用相机拍了很多照片。",
        "Tôi dùng máy ảnh chụp rất nhiều ảnh."
    ),

    1090: (
        "妹妹长得很像妈妈。",
        "Em gái trông rất giống mẹ."
    ),

    1091: (
        "小王今天没有来上课。",
        "Tiểu Vương hôm nay không đến lớp."
    ),

    1092: (
        "请小声一点儿，孩子在睡觉。",
        "Xin nói nhỏ một chút, đứa trẻ đang ngủ."
    ),

    1093: (
        "我小时候住在农村。",
        "Khi còn nhỏ tôi sống ở nông thôn."
    ),

    1094: (
        "我正在看一本中文小说。",
        "Tôi đang đọc một cuốn tiểu thuyết tiếng Trung."
    ),

    1095: (
        "下雨路滑，走路要小心。",
        "Trời mưa đường trơn, đi bộ phải cẩn thận."
    ),

    1096: (
        "老师把我们分成了五个小组。",
        "Giáo viên chia chúng tôi thành năm nhóm."
    ),

    1097: (
        "我们的校园里有很多树。",
        "Trong khuôn viên trường chúng tôi có rất nhiều cây."
    ),

    1098: (
        "校长正在会议室开会。",
        "Hiệu trưởng đang họp trong phòng họp."
    ),

    1099: (
        "他给我们讲了一个笑话。",
        "Anh ấy kể cho chúng tôi một câu chuyện cười."
    ),

    1100: (
        "这个笑话儿把大家都逗笑了。",
        "Câu chuyện cười này làm mọi người đều bật cười."
    ),

    1101: (
        "我想买一双新的运动鞋。",
        "Tôi muốn mua một đôi giày thể thao mới."
    ),

    1102: (
        "听到这个消息，我心里很高兴。",
        "Nghe tin này, trong lòng tôi rất vui."
    ),

    1103: (
        "今天天气很好，我的心情也很好。",
        "Hôm nay thời tiết rất đẹp, tâm trạng tôi cũng rất tốt."
    ),

    1104: (
        "这件事我一直记在心中。",
        "Việc này tôi luôn ghi nhớ trong lòng."
    ),

    1105: (
        "爸爸每天晚上看电视新闻。",
        "Bố tôi tối nào cũng xem tin tức trên TV."
    ),

    1106: (
        "我昨天收到朋友的一封信。",
        "Hôm qua tôi nhận được một lá thư của bạn."
    ),

    1107: (
        "这里手机信号不太好。",
        "Tín hiệu điện thoại ở đây không được tốt lắm."
    ),

    1108: (
        "请把你的信息发给我。",
        "Hãy gửi thông tin của bạn cho tôi."
    ),

    1109: (
        "我对这次考试很有信心。",
        "Tôi rất tự tin về kỳ thi lần này."
    ),

    1110: (
        "我可以用信用卡付款吗？",
        "Tôi có thể thanh toán bằng thẻ tín dụng không?"
    ),

    1111: (
        "今天晚上天上有很多星星。",
        "Tối nay trên trời có rất nhiều ngôi sao."
    ),

    1112: (
        "我们不能只说，应该马上行动。",
        "Chúng ta không thể chỉ nói, nên hành động ngay."
    ),

    1113: (
        "过马路时，行人要注意汽车。",
        "Khi qua đường, người đi bộ phải chú ý ô tô."
    ),

    1114: (
        "在公共场所大声说话是不好的行为。",
        "Nói lớn tiếng ở nơi công cộng là hành vi không tốt."
    ),

    1115: (
        "我姓李，你姓什么？",
        "Tôi họ Lý, bạn họ gì?"
    ),

    1116: (
        "请在这里写下你的姓名。",
        "Hãy viết họ tên của bạn vào đây."
    ),

    1117: (
        "爸爸下个月要休假一周。",
        "Bố tôi tháng sau sẽ nghỉ phép một tuần."
    ),

    1118: (
        "公园里有许多人在运动。",
        "Trong công viên có rất nhiều người đang tập thể dục."
    ),

    1119: (
        "你可以选一个自己喜欢的颜色。",
        "Bạn có thể chọn một màu mình thích."
    ),

    1120: (
        "这个学期我们有六门课。",
        "Học kỳ này chúng tôi có sáu môn học."
    ),

    1121: (
        "山上的雪还没有化。",
        "Tuyết trên núi vẫn chưa tan."
    ),

    1122: (
        "你最喜欢什么颜色？",
        "Bạn thích màu gì nhất?"
    ),

    1123: (
        "我一眼就看见了他。",
        "Tôi vừa nhìn một cái đã thấy anh ấy."
    ),

    1124: (
        "看电脑时间太长对眼睛不好。",
        "Nhìn máy tính quá lâu không tốt cho mắt."
    ),

    1125: (
        "我奶奶在家里养了两只猫。",
        "Bà tôi nuôi hai con mèo ở nhà."
    ),

    1126: (
        "这个蛋糕的样子很漂亮。",
        "Hình dáng chiếc bánh này rất đẹp."
    ),

    1127: (
        "老师要求我们按时完成作业。",
        "Giáo viên yêu cầu chúng tôi hoàn thành bài tập đúng hạn."
    ),

    1128: (
        "生病了要按时吃药。",
        "Bị bệnh thì phải uống thuốc đúng giờ."
    ),

    1129: (
        "学校旁边有一家药店。",
        "Bên cạnh trường có một nhà thuốc."
    ),

    1130: (
        "医生让我每天吃两次药片。",
        "Bác sĩ bảo tôi mỗi ngày uống thuốc viên hai lần."
    ),

    1131: (
        "这瓶药水一天喝三次。",
        "Chai thuốc nước này uống ba lần mỗi ngày."
    ),

    1132: (
        "他今天没来，也许生病了。",
        "Hôm nay anh ấy không đến, có lẽ bị ốm."
    ),

    1133: (
        "夜已经深了，我们回家吧。",
        "Đêm đã khuya rồi, chúng ta về nhà thôi."
    ),

    1134: (
        "昨天夜里下了很大的雨。",
        "Đêm qua trời mưa rất to."
    ),

    1135: (
        "这些书中有一部分是中文书。",
        "Trong số những quyển sách này có một phần là sách tiếng Trung."
    ),

    1136: (
        "明天考试，你一定要早点儿睡。",
        "Ngày mai thi, bạn nhất định phải ngủ sớm."
    ),

    1137: (
        "我们班一共有三十个学生。",
        "Lớp chúng tôi tổng cộng có ba mươi học sinh."
    ),

    1138: (
        "祝你一路平安，到了给我打电话。",
        "Chúc bạn thượng lộ bình an, đến nơi thì gọi cho tôi."
    ),

    1139: (
        "明天你要坐飞机回国了，祝你一路顺风！",
        "Ngày mai bạn sẽ đi máy bay về nước, chúc bạn lên đường thuận lợi!"
    ),

    1140: (
        "我已经吃过晚饭了。",
        "Tôi đã ăn tối rồi."
    ),

    1141: (
        "毕业以后我想留在北京工作。",
        "Sau khi tốt nghiệp tôi muốn ở lại Bắc Kinh làm việc."
    ),

    1142: (
        "我以前在上海住过两年。",
        "Trước đây tôi từng sống ở Thượng Hải hai năm."
    ),

    1143: (
        "十八岁以上的人可以买这张票。",
        "Người từ mười tám tuổi trở lên có thể mua vé này."
    ),
}


def clean_target(raw_word):
    word = (raw_word or "").strip()

    # 小（小王） -> 小王
    match = re.search(r"（([^（）]+)）", word)

    if match:
        return match.group(1).strip()

    # Nếu có dạng 面1, 面2...
    word = re.sub(r"\d+$", "", word)

    return word.strip()


def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"\nKhông tìm thấy file nguồn:\n{SOURCE}\n"
        )

    with SOURCE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    # Kiểm tra dictionary trước
    if len(FIXES) != 100:
        raise ValueError(
            f"Batch 6 phải có đúng 100 câu, "
            f"nhưng FIXES hiện có {len(FIXES)}."
        )

    updated = []

    for row in rows:

        word_id = int(row["MaTuVung"])

        if word_id not in FIXES:
            continue

        # Không ghi đè câu đã hoàn thành
        if row["TrangThaiImport"] != "NEED_REVIEW":
            raise ValueError(
                f"\nMaTuVung {word_id} - {row['ChuHan']}\n"
                f"không ở trạng thái NEED_REVIEW.\n"
                f"Hiện tại: {row['TrangThaiImport']}"
            )

        chinese, vietnamese = FIXES[word_id]

        target = clean_target(row["ChuHan"])

        # Câu Trung bắt buộc phải chứa từ đang học
        if target not in chinese:
            raise ValueError(
                f"\nCÂU KHÔNG CHỨA TỪ MỤC TIÊU\n"
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

    missing = set(FIXES) - set(updated)

    if missing:
        raise ValueError(
            f"\nKhông cập nhật được các MaTuVung:\n"
            f"{sorted(missing)}"
        )

    if len(updated) != 100:
        raise ValueError(
            f"Dự kiến sửa 100 câu, "
            f"thực tế sửa {len(updated)} câu."
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

    ready = sum(
        1
        for row in rows
        if row["TrangThaiImport"] == "READY"
    )

    remaining = sum(
        1
        for row in rows
        if row["TrangThaiImport"] == "NEED_REVIEW"
    )

    print()
    print("=" * 60)
    print("HSK2 - BATCH 6")
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