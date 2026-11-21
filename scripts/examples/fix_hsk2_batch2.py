
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
SOURCE = DATA / "offline_preview_hsk2_batch1.csv"
OUTPUT = DATA / "offline_preview_hsk2_batch2.csv"

FIXES = {
    706: ("过去我住在北京，现在住在上海。", "Trước đây tôi sống ở Bắc Kinh, bây giờ sống ở Thượng Hải."),
    707: ("我去过中国两次。", "Tôi đã từng đến Trung Quốc hai lần."),
    708: ("我第一次看见这么美丽的海。", "Đây là lần đầu tiên tôi nhìn thấy biển đẹp như vậy."),
    709: ("暑假我们打算去海边玩。", "Kỳ nghỉ hè chúng tôi dự định đi chơi ở bờ biển."),
    710: ("妈妈在门口喊我的名字。", "Mẹ gọi to tên tôi ở cửa."),
    711: ("每天运动对身体有很多好处。", "Tập thể dục hằng ngày có nhiều lợi ích cho sức khỏe."),
    712: ("今天超市里有好多新鲜水果。", "Hôm nay trong siêu thị có rất nhiều trái cây tươi."),
    713: ("我们已经好久没有见面了。", "Chúng ta đã lâu không gặp nhau rồi."),
    714: ("他经常帮助别人，是个好人。", "Anh ấy thường giúp đỡ người khác, là một người tốt."),
    715: ("帮助老人过马路是一件好事。", "Giúp người già qua đường là một việc tốt."),
    716: ("外面好像下雨了。", "Bên ngoài hình như trời mưa rồi."),
    717: ("这件衣服的大小很合适。", "Kích cỡ bộ quần áo này rất vừa vặn."),
    718: ("学校旁边有一条小河。", "Bên cạnh trường học có một con sông nhỏ."),
    719: ("天已经黑了，我们回家吧。", "Trời đã tối rồi, chúng ta về nhà thôi."),
    720: ("老师正在黑板上写汉字。", "Giáo viên đang viết chữ Hán lên bảng đen."),
    721: ("我买了一双黑色的鞋。", "Tôi đã mua một đôi giày màu đen."),
    722: ("她今天穿了一件红衣服。", "Hôm nay cô ấy mặc một bộ quần áo màu đỏ."),
    723: ("我妹妹最喜欢红色。", "Em gái tôi thích màu đỏ nhất."),
    724: ("开始我不明白，后来终于懂了。", "Ban đầu tôi không hiểu, sau đó cuối cùng cũng hiểu."),
    725: ("他忽然想起今天有考试。", "Anh ấy đột nhiên nhớ ra hôm nay có bài thi."),
    726: ("公园里有一个很大的湖。", "Trong công viên có một cái hồ rất lớn."),
    727: ("出国旅行的时候别忘了带护照。", "Khi đi du lịch nước ngoài đừng quên mang hộ chiếu."),
    728: ("奶奶每天早上都在花园里浇花。", "Bà nội tưới hoa trong vườn mỗi sáng."),
    729: ("妹妹正在画一只小猫。", "Em gái đang vẽ một con mèo nhỏ."),
    730: ("我的梦想是成为一名画家。", "Ước mơ của tôi là trở thành một họa sĩ."),
    731: ("墙上挂着一张漂亮的画儿。", "Trên tường treo một bức tranh đẹp."),
    732: ("晚上睡得太晚对身体有坏处。", "Ngủ quá muộn vào buổi tối có hại cho sức khỏe."),
    733: ("那个坏人偷走了我的钱包。", "Kẻ xấu đó đã lấy trộm ví của tôi."),
    734: ("欢迎大家来我们学校参观。", "Chào mừng mọi người đến tham quan trường chúng tôi."),
    735: ("这件衣服太小了，我想换一件。", "Bộ quần áo này quá nhỏ, tôi muốn đổi bộ khác."),
    736: ("秋天到了，树叶慢慢变黄了。", "Mùa thu đến rồi, lá cây dần chuyển vàng."),
    737: ("她买了一条黄色的裙子。", "Cô ấy đã mua một chiếc váy màu vàng."),
    738: ("他打算明年毕业以后回国工作。", "Anh ấy dự định sau khi tốt nghiệp năm sau sẽ về nước làm việc."),
    739: ("学校周末组织了一个有趣的活动。", "Cuối tuần trường tổ chức một hoạt động thú vị."),
    740: ("你可以坐公交车或地铁去机场。", "Bạn có thể đi xe buýt hoặc tàu điện ngầm đến sân bay."),
}

def main():
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    updated = []

    for row in rows:
        word_id = int(row["MaTuVung"])

        if word_id not in FIXES:
            continue

        if row["TrangThaiImport"] != "NEED_REVIEW":
            raise ValueError(f"Mã {word_id} không ở trạng thái NEED_REVIEW")

        chinese, vietnamese = FIXES[word_id]

        if row["ChuHan"].strip() not in chinese:
            raise ValueError(f"Câu không chứa từ của mã {word_id}")

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"
        updated.append(word_id)

    if set(updated) != set(FIXES):
        raise ValueError(
            f"Thiếu mã: {sorted(set(FIXES) - set(updated))}"
        )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Đã sửa thêm: {len(updated)} câu")
    print(f"File: {OUTPUT}")
    print("Chưa thay đổi SQL Server.")

if __name__ == "__main__":
    main()
