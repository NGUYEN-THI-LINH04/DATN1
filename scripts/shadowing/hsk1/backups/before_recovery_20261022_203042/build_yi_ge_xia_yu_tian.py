
import json
from pathlib import Path
from pypinyin import pinyin, Style

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "scripts" / "shadowing" / "previews"
OUT.mkdir(parents=True, exist_ok=True)

YOUTUBE_ID = "QwlhcsAMhT0"

# start | end | Hanzi | Tiếng Việt
# Mốc thời gian căn theo offset Supadata, cần rà soát với video.
DATA = """
0.00|1.50|大家好！|Xin chào mọi người!
1.56|6.00|今天外面下着很大的雨，天气非常不好。|Hôm nay bên ngoài đang mưa rất to, thời tiết rất xấu.
6.06|11.30|你们有没有遇到过这样的雨天，不知道该做什么的时候？|Các bạn đã bao giờ gặp một ngày mưa như thế này, không biết nên làm gì chưa?
11.30|17.90|如果你们想知道我在雨天通常做什么，就听我分享吧。|Nếu các bạn muốn biết tôi thường làm gì vào ngày mưa thì hãy nghe tôi chia sẻ nhé.
18.00|22.90|我一个人住在广东一个小小的公寓里。|Tôi sống một mình trong một căn hộ nhỏ ở Quảng Đông.
23.16|25.25|外面下着很大的雨。|Bên ngoài đang mưa rất to.
25.30|28.85|天气预报说，这几天会有暴风雨。|Dự báo thời tiết nói rằng mấy ngày tới sẽ có mưa bão.
28.88|30.60|风也很大。|Gió cũng rất mạnh.
30.64|34.38|大家都建议少出门，注意安全。|Mọi người đều khuyên nên hạn chế ra ngoài và chú ý an toàn.
34.54|39.95|前几天我去超市买好了足够一周吃的东西。|Mấy hôm trước tôi đã đi siêu thị mua đủ đồ ăn cho cả tuần.
40.04|46.50|有米饭、面条、蔬菜、水果，还有一些零食和方便面。|Có cơm, mì, rau, trái cây, cùng một ít đồ ăn vặt và mì ăn liền.
46.98|50.70|因为知道天气不好，出门很不方便。|Vì biết thời tiết không tốt, ra ngoài rất bất tiện.
50.74|56.90|所以我准备了很多东西，这样不用担心吃饭的问题。|Vì vậy tôi đã chuẩn bị nhiều thứ để không phải lo chuyện ăn uống.
57.81|62.90|公司也通知我们在家工作，不能去办公室。|Công ty cũng thông báo chúng tôi làm việc ở nhà, không được đến văn phòng.
63.39|65.70|虽然在家工作很方便。|Mặc dù làm việc ở nhà rất thuận tiện.
65.73|71.90|但是一个人在家工作，感觉有点孤单，也有点无聊。|Nhưng làm việc một mình ở nhà khiến tôi cảm thấy hơi cô đơn và buồn chán.
72.13|77.50|没有同事在身边聊天，也没有外面的阳光和新鲜空气。|Không có đồng nghiệp bên cạnh để trò chuyện, cũng không có ánh nắng và không khí trong lành bên ngoài.
77.57|82.65|早上，我打开电脑准备工作。|Buổi sáng, tôi mở máy tính chuẩn bị làm việc.
82.70|85.90|窗外下着大雨。|Ngoài cửa sổ đang mưa rất to.
86.26|91.65|雨水打在窗户上，发出啪啪的声音。|Nước mưa đập vào cửa sổ, phát ra tiếng lộp bộp.
91.70|98.20|我打开电视看新闻和天气预报，知道暴风雨的情况。|Tôi bật tivi xem tin tức và dự báo thời tiết để biết tình hình mưa bão.
98.30|102.30|然后我给我的好朋友打电话。|Sau đó tôi gọi điện cho bạn thân của mình.
102.36|105.70|我们聊天，聊生活和工作。|Chúng tôi trò chuyện về cuộc sống và công việc.
105.78|109.50|听朋友的声音让我觉得好一点。|Nghe giọng nói của bạn khiến tôi cảm thấy khá hơn một chút.
110.59|113.20|中午，我做了简单的饭菜。|Buổi trưa, tôi nấu một bữa ăn đơn giản.
113.25|116.90|吃完饭休息了一会儿。|Ăn xong, tôi nghỉ ngơi một lát.
117.03|121.60|我看手机上的短视频，放松自己。|Tôi xem các video ngắn trên điện thoại để thư giãn.
121.73|125.90|外面还是下着雨，天空很灰。|Bên ngoài trời vẫn mưa, bầu trời rất xám xịt.
126.37|129.30|我觉得有点寂寞。|Tôi cảm thấy hơi cô đơn.
129.43|133.50|我给男朋友发了信息，告诉他我吃饭了。|Tôi nhắn tin cho bạn trai, nói với anh ấy rằng tôi đã ăn cơm rồi.
133.59|137.30|也问他天气怎么样。|Tôi cũng hỏi thời tiết chỗ anh ấy thế nào.
137.52|143.60|我的男朋友现在在重庆工作，那边也下大雨。|Bạn trai tôi hiện đang làm việc ở Trùng Khánh, bên đó cũng mưa rất to.
143.78|149.20|他每天都打电话给我，问我冷不冷、吃没吃饭。|Ngày nào anh ấy cũng gọi cho tôi, hỏi tôi có lạnh không và đã ăn cơm chưa.
149.36|152.70|还说他很想我。|Anh ấy còn nói rằng rất nhớ tôi.
152.86|156.75|看见他的笑脸，我觉得不孤单了。|Nhìn thấy nụ cười của anh ấy, tôi không còn cảm thấy cô đơn nữa.
156.88|163.90|虽然不能见面，但他的关心让我觉得很温暖。|Dù không thể gặp nhau, sự quan tâm của anh ấy vẫn khiến tôi cảm thấy rất ấm áp.
164.17|167.25|下午，我参加了一个线上会议。|Buổi chiều, tôi tham gia một cuộc họp trực tuyến.
167.39|173.90|虽然大家都在家里，但通过电脑我们还能见面、讨论工作。|Dù mọi người đều ở nhà, chúng tôi vẫn có thể gặp nhau và thảo luận công việc qua máy tính.
174.05|181.90|会议中，我认真听大家发言，也积极发表自己的意见。|Trong cuộc họp, tôi chăm chú nghe mọi người phát biểu và tích cực đưa ra ý kiến của mình.
182.09|188.90|会议结束后，我完成了今天的工作任务，感觉很有成就感。|Sau khi cuộc họp kết thúc, tôi hoàn thành công việc hôm nay và cảm thấy rất có thành tựu.
189.22|195.95|我的老板还特别表扬了我，说我工作做得很好，效率很高。|Sếp còn đặc biệt khen tôi làm việc rất tốt và có hiệu suất cao.
196.32|199.90|听到这些话，我心里非常高兴。|Nghe những lời đó, trong lòng tôi rất vui.
201.64|208.15|晚上，我打开手机，看着我和男朋友过去一起拍的照片。|Buổi tối, tôi mở điện thoại xem những bức ảnh trước đây chụp cùng bạn trai.
208.26|215.60|回想起我们一起散步、吃饭的时光，心里充满了期待。|Nhớ lại những lúc cùng nhau đi dạo và ăn cơm, lòng tôi tràn đầy mong đợi.
215.76|220.35|我希望暴风雨快点过去，天气变好。|Tôi mong cơn bão sớm qua đi và thời tiết tốt lên.
220.51|229.00|我们可以一起出去散步，一起吃饭，一起享受阳光。|Chúng tôi có thể cùng nhau đi dạo, ăn cơm và tận hưởng ánh nắng.
229.05|235.85|今天天气又冷又下大雨，所以我很早就想睡觉了。|Hôm nay trời vừa lạnh vừa mưa to nên tôi muốn đi ngủ sớm.
236.01|240.25|平时我都是晚上十一点才睡。|Bình thường phải đến 11 giờ tối tôi mới ngủ.
240.37|245.55|但今天九点我就觉得很困，准备早点休息。|Nhưng hôm nay mới 9 giờ tôi đã thấy buồn ngủ và chuẩn bị nghỉ sớm.
245.68|253.65|我关了灯，盖好被子，听着窗外的雨声慢慢入睡。|Tôi tắt đèn, đắp chăn, lắng nghe tiếng mưa ngoài cửa sổ rồi dần chìm vào giấc ngủ.
253.82|257.20|谢谢大家听我分享我的雨天生活。|Cảm ơn mọi người đã lắng nghe tôi chia sẻ về cuộc sống trong ngày mưa.
257.38|263.60|希望你们也能在阴雨天找到属于自己的温暖和快乐。|Hy vọng các bạn cũng tìm thấy sự ấm áp và niềm vui của riêng mình trong những ngày mưa.
263.74|267.50|祝大家身体健康，心情愉快！|Chúc mọi người mạnh khỏe và luôn vui vẻ!
267.60|270.98|我们下次再见！|Hẹn gặp lại mọi người lần sau!
""".strip()


def make_pinyin(text):
    result = pinyin(
        text,
        style=Style.TONE,
        heteronym=False,
        errors=lambda x: [x],
    )
    return " ".join(part[0] for part in result)


def main():
    sentences = []

    for line_number, line in enumerate(
        DATA.splitlines(), start=1
    ):
        parts = line.split("|", 3)

        if len(parts) != 4:
            raise ValueError(
                f"Dong {line_number}: sai dinh dang"
            )

        start, end, hanzi, vi = parts

        start = float(start)
        end = float(end)

        if start < 0 or end <= start:
            raise ValueError(
                f"Dong {line_number}: timestamp sai"
            )

        if not hanzi.strip() or not vi.strip():
            raise ValueError(
                f"Dong {line_number}: thieu noi dung"
            )

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi.strip(),
            "pinyin": make_pinyin(hanzi.strip()),
            "vi": vi.strip(),
        })

    for i in range(1, len(sentences)):
        previous = sentences[i - 1]
        current = sentences[i]

        if current["start"] < previous["end"]:
            raise ValueError(
                f"Cau {i + 1} chong len cau {i}"
            )

    payload = {
        "module": "shadowing",
        "youtube_id": YOUTUBE_ID,
        "sentences": sentences,
    }

    output = (
        OUT / "yi_ge_xia_yu_tian_final_preview.json"
    )

    with output.open("w", encoding="utf-8") as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("===== MOT NGAY MUA =====")
    print("Video:", YOUTUBE_ID)
    print("So cau:", len(sentences))
    print("Thoi gian cuoi:", sentences[-1]["end"])
    print("File:", output)
    print("Da co Hanzi, pinyin, tieng Viet.")
    print("Chua doi chieu audio toan bo.")
    print("Chua thay doi SQL Server.")
    print("Khong goi Supadata.")


if __name__ == "__main__":
    main()
