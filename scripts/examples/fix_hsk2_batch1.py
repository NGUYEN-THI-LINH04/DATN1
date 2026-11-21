
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

SOURCE = DATA_DIR / "offline_preview_hsk2.csv"
OUTPUT = DATA_DIR / "offline_preview_hsk2_batch1.csv"

# MaTuVung: (Câu tiếng Trung, Bản dịch tiếng Việt)
# Dùng MaTuVung thay vì ChuHan để phân biệt từ đồng hình.
FIXES = {
    563: ("大家都称他为李老师。", "Mọi người đều gọi ông ấy là thầy Lý."),
    564: ("这件事终于办成了。", "Cuối cùng việc này cũng đã làm xong."),
    579: ("外面的风吹得很大。", "Gió bên ngoài thổi rất mạnh."),
    582: ("我不认识这个词。", "Tôi không biết từ này."),
    584: ("这个词语是什么意思？", "Từ ngữ này có nghĩa là gì."),
    591: ("他的汉语水平大大提高了。", "Trình độ tiếng Trung của anh ấy đã tiến bộ rất nhiều."),
    592: ("大多数学生都按时到了。", "Đại đa số học sinh đều đến đúng giờ."),
    595: ("图书馆里有大量的书。", "Trong thư viện có rất nhiều sách."),
    597: ("小孩子应该尊重大人。", "Trẻ nhỏ nên tôn trọng người lớn."),
    598: ("请不要在图书馆大声说话。", "Xin đừng nói lớn tiếng trong thư viện."),
    599: ("这两件衣服大小不一样。", "Hai bộ quần áo này có kích cỡ khác nhau."),
    600: ("冬天我经常穿这件大衣。", "Mùa đông tôi thường mặc chiếc áo khoác dài này."),
    601: ("我们应该保护大自然。", "Chúng ta nên bảo vệ thiên nhiên."),
    602: ("出门的时候别忘了带手机。", "Khi ra ngoài đừng quên mang điện thoại."),
    603: ("这本书给我带来了很多快乐。", "Cuốn sách này mang lại cho tôi nhiều niềm vui."),
    604: ("米是长度单位。", "Mét là đơn vị đo chiều dài."),
    605: ("我很累，但还想继续学习。", "Tôi rất mệt nhưng vẫn muốn tiếp tục học."),
    606: ("今天很冷，但是没有下雨。", "Hôm nay rất lạnh nhưng không mưa."),
    607: ("我早上吃了一个鸡蛋。", "Buổi sáng tôi đã ăn một quả trứng gà."),
    608: ("我长大以后想当医生。", "Khi lớn lên tôi muốn làm bác sĩ."),
    609: ("当时我不知道发生了什么。", "Lúc đó tôi không biết chuyện gì đã xảy ra."),
    610: ("他不小心摔倒了。", "Anh ấy không cẩn thận nên bị ngã."),
    611: ("春天到处都是鲜花。", "Mùa xuân khắp nơi đều có hoa tươi."),
    612: ("请给我倒一杯水。", "Hãy rót cho tôi một cốc nước."),
    613: ("这道题我不会做。", "Tôi không biết làm câu hỏi này."),
    614: ("你说的话很有道理。", "Những lời bạn nói rất có lý."),
    615: ("这条道路很宽。", "Con đường này rất rộng."),
    616: ("我得到了老师的帮助。", "Tôi đã nhận được sự giúp đỡ của giáo viên."),
    617: ("我们得出了同样的结论。", "Chúng tôi đã đi đến cùng một kết luận."),
    618: ("你有时间的话，我们一起去吧。", "Nếu bạn có thời gian thì chúng ta cùng đi nhé."),
    619: ("他跑得很快。", "Anh ấy chạy rất nhanh."),
    620: ("请把房间里的灯打开。", "Hãy bật đèn trong phòng lên."),
    621: ("等到下课以后我们再讨论。", "Đợi đến khi tan học rồi chúng ta thảo luận tiếp."),
    622: ("二加三等于五。", "Hai cộng ba bằng năm."),
    623: ("这张桌子有点儿低。", "Chiếc bàn này hơi thấp."),
    624: ("我们都生活在地球上。", "Tất cả chúng ta đều sống trên Trái Đất."),
    626: ("地铁站离我家很近。", "Ga tàu điện ngầm rất gần nhà tôi."),
    627: ("老师问我时，我点了点头。", "Khi giáo viên hỏi, tôi đã gật đầu."),
    628: ("这家店的东西很便宜。", "Đồ ở cửa hàng này rất rẻ."),
    629: ("我的手机掉在地上了。", "Điện thoại của tôi rơi xuống đất rồi."),
    630: ("冬天东北的天气很冷。", "Mùa đông thời tiết vùng Đông Bắc rất lạnh."),
    631: ("太阳从东方升起。", "Mặt trời mọc từ phía đông."),
    632: ("我们的学校在城市的东南方向。", "Trường chúng tôi nằm ở phía đông nam thành phố."),
    633: ("冬天我喜欢喝热茶。", "Mùa đông tôi thích uống trà nóng."),
    634: ("老师说的话我都懂。", "Những điều giáo viên nói tôi đều hiểu."),
    635: ("他从小就懂得帮助别人。", "Từ nhỏ anh ấy đã biết giúp đỡ người khác."),
    636: ("我最喜欢的动物是熊猫。", "Động vật tôi thích nhất là gấu trúc."),
    638: ("这个汉字的读音是什么？", "Cách phát âm của chữ Hán này là gì?"),
    639: ("今天的气温是三十度。", "Nhiệt độ hôm nay là ba mươi độ."),
    640: ("这条裤子太短了。", "Chiếc quần này quá ngắn."),
    641: ("我刚收到妈妈发来的短信。", "Tôi vừa nhận được tin nhắn mẹ gửi."),
    642: ("请读一下这段文章。", "Hãy đọc đoạn văn này."),
    643: ("我们队今天赢了比赛。", "Đội chúng tôi hôm nay đã thắng trận đấu."),
    644: ("队长正在安排今天的训练。", "Đội trưởng đang sắp xếp buổi tập hôm nay."),
    645: ("请两个人练习这段对话。", "Hai người hãy luyện tập đoạn hội thoại này."),
    646: ("银行就在学校对面。", "Ngân hàng nằm ngay đối diện trường học."),
    647: ("从这里到机场要多久？", "Từ đây đến sân bay mất bao lâu?"),
    648: ("今天的天气多么好啊！", "Thời tiết hôm nay đẹp biết bao!"),
    649: ("我们班多数学生喜欢运动。", "Phần lớn học sinh lớp chúng tôi thích vận động."),
    650: ("明天多云，可能不会下雨。", "Ngày mai nhiều mây, có thể sẽ không mưa."),
}

def main():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Không tìm thấy: {SOURCE}")

    with SOURCE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    updated = []
    for row in rows:
        word_id = int(row["MaTuVung"])

        if word_id not in FIXES:
            continue

        # Không ghi đè câu đã duyệt.
        if row["LoaiCau"] != "TEMPLATE":
            continue

        chinese, vietnamese = FIXES[word_id]
        word = row["ChuHan"].strip()

        # Kiểm tra câu Trung chứa chữ Hán cần học.
        # Với mục từ có số thứ tự như 称1, bỏ số ở cuối.
        import re
        clean_word = re.sub(r"\d+$", "", word)

        if clean_word not in chinese:
            raise ValueError(
                f"Mã {word_id}: câu không chứa từ '{clean_word}'"
            )

        row["ViDuTiengTrung"] = chinese
        row["ViDuTiengViet"] = vietnamese
        row["LoaiCau"] = "REAL"
        row["TrangThaiImport"] = "READY"
        updated.append(word_id)

    missing = set(FIXES) - set(updated)
    if missing:
        raise ValueError(
            f"Các mã không cập nhật được: {sorted(missing)}"
        )

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Đã sửa {len(updated)} câu HSK2.")
    print(f"File mới: {OUTPUT}")
    print(f"Tổng dòng: {len(rows)}")
    print("CHƯA THAY ĐỔI SQL SERVER.")

if __name__ == "__main__":
    main()
