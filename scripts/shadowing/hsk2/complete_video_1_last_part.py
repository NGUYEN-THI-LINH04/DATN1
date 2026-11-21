
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "previews" / "video_1_part3_0933_to_end.json"

# Mỗi dòng: thời gian | tiếng Trung | tiếng Việt
# Thời gian dựa trên phụ đề YouTube người dùng cung cấp.
DATA = """
09:33|是啊。一个简单的故事，但是有一个很重要的道理。|Đúng vậy. Một câu chuyện đơn giản nhưng chứa đựng một bài học rất quan trọng.
09:39|你觉得，为什么我们，不管是小孩子还是大人，都喜欢在睡觉前听故事呢？|Bạn nghĩ tại sao cả trẻ con lẫn người lớn đều thích nghe kể chuyện trước khi ngủ?
09:48|嗯……这是一个好问题。|Ừm... Đây là một câu hỏi hay.
09:51|对我来说，我觉得，睡觉前听故事，就像在睡觉前喝一杯热牛奶一样。|Đối với tôi, nghe chuyện trước khi ngủ giống như uống một cốc sữa nóng trước khi đi ngủ.
09:59|哦？像一杯热牛奶？|Ồ? Giống một cốc sữa nóng sao?
10:01|这个比喻很好。|Cách so sánh này rất hay.
10:03|是的。它不一定能解决你白天的所有问题，|Đúng vậy. Nó không nhất thiết giải quyết được mọi vấn đề của bạn trong ngày,
10:09|但是它可以让你的心，你的身体，都觉得很暖和，很舒服。|nhưng có thể khiến cả tâm hồn và cơ thể bạn cảm thấy ấm áp, dễ chịu.
10:16|可以让你忘记一天的疲劳。|Nó có thể giúp bạn quên đi mệt mỏi cả ngày.
10:20|我同意。|Tôi đồng ý.
10:21|白天，我们工作，学习，可能会遇到很多不开心的事，会觉得很累。|Ban ngày, chúng ta làm việc, học tập, có thể gặp nhiều chuyện không vui và cảm thấy rất mệt.
10:28|晚上，听一个简单的故事，就好像进入了另一个世界。|Buổi tối, nghe một câu chuyện đơn giản giống như bước vào một thế giới khác.
10:34|在那个世界里，没有工作，没有问题，只有兔子和乌龟。|Trong thế giới ấy không có công việc, không có vấn đề, chỉ có thỏ và rùa.
10:41|对！就是这个感觉！|Đúng! Chính là cảm giác đó!
10:44|可以让我们的大脑休息一下。|Nó giúp bộ não của chúng ta nghỉ ngơi một chút.
10:47|不过，王雨，我有一个问题。|Nhưng này Vương Vũ, tôi có một câu hỏi.
10:50|我们的播客是“每天中文”，听众朋友们都在学习中文。|Podcast của chúng ta là “Tiếng Trung mỗi ngày”, các thính giả đều đang học tiếng Trung.
10:56|嗯。|Ừ.
10:56|他们中的一些人，可能是初学者，他们的中文水平可能还不是很高。|Một số người trong số họ có thể mới bắt đầu, trình độ tiếng Trung còn chưa cao.
11:03|他们可能会觉得，“听一个完整的故事，太难了。|Họ có thể nghĩ: “Nghe cả một câu chuyện hoàn chỉnh khó quá.
11:08|我听不懂。”我完全理解。|Tôi nghe không hiểu.” Tôi hoàn toàn hiểu điều đó.
11:12|李明，你知道吗，我以前学习别的语言的时候，也是这样想的。|Lý Minh, bạn biết không, trước đây khi học ngoại ngữ khác, tôi cũng từng nghĩ như vậy.
11:19|我觉得读一篇文章，听一个故事，是不可能完成的任务。|Tôi cảm thấy đọc một bài văn hay nghe một câu chuyện là nhiệm vụ không thể hoàn thành.
11:25|那你后来是怎么做的呢？|Vậy sau đó bạn đã làm thế nào?
11:27|后来，我的老师告诉我，开始的时候，听不懂是完全正常的。|Sau đó, giáo viên nói với tôi rằng lúc mới bắt đầu, nghe không hiểu là hoàn toàn bình thường.
11:34|最重要的事情不是听懂每一个汉字，而是去“感受”。|Điều quan trọng nhất không phải hiểu từng chữ Hán, mà là cảm nhận.
11:41|感受？|Cảm nhận sao?
11:42|对。|Đúng.
11:43|感受这个语言的声音，它的节奏，它的音乐感。|Cảm nhận âm thanh, nhịp điệu và tính nhạc của ngôn ngữ ấy.
11:49|就像我们刚才说的，感受那种“暖和”、“舒服”的感觉。|Giống như chúng ta vừa nói, cảm nhận sự ấm áp và dễ chịu ấy.
11:56|你把自己放在这个语言环境里，就像在用温水洗澡一样，|Bạn đặt mình vào môi trường ngôn ngữ đó, giống như đang tắm bằng nước ấm,
12:02|慢慢地，你的身体和大脑就会习惯它。|dần dần, cơ thể và bộ não sẽ quen với nó.
12:08|这个方法很好。|Phương pháp này rất hay.
12:09|先不要有压力，先感受。|Trước tiên đừng tạo áp lực, hãy cảm nhận đã.
12:12|然后呢？|Rồi sau đó?
12:13|然后，可以选择一个非常非常简单的故事，比如《龟兔赛跑》。|Sau đó, có thể chọn một câu chuyện thật đơn giản, chẳng hạn “Rùa và Thỏ”.
12:22|你可以听很多遍。|Bạn có thể nghe nhiều lần.
12:25|第一遍，你可能只听懂了“兔子”、“乌龟”、“快”、“慢”。|Lần đầu, có thể bạn chỉ hiểu các từ “thỏ”, “rùa”, “nhanh”, “chậm”.
12:33|没关系！|Không sao cả!
12:34|第二遍，你可能会听懂更多。|Lần thứ hai, có thể bạn sẽ hiểu nhiều hơn.
12:38|第三遍，第四遍……慢慢地，你就会发现，你能听懂整个故事了。|Lần thứ ba, thứ tư... dần dần bạn sẽ nhận ra mình có thể hiểu toàn bộ câu chuyện.
12:45|那个时候，你会非常有成就感。|Khi ấy bạn sẽ cảm thấy rất thành tựu.
12:49|说得太好了。|Bạn nói hay quá.
12:51|所以，听众朋友们，如果你们觉得听不懂，请不要担心。|Vì vậy, các thính giả thân mến, nếu cảm thấy nghe không hiểu, xin đừng lo lắng.
12:56|这是学习任何语言都会有的阶段。|Đó là giai đoạn ai học ngôn ngữ nào cũng sẽ trải qua.
12:59|请放松，像王雨说的那样，先感受，然后重复听。|Hãy thư giãn, như Vương Vũ nói, cảm nhận trước rồi nghe đi nghe lại.
13:06|在中国，我们有非常非常多这样简单的故事。|Ở Trung Quốc có rất nhiều câu chuyện đơn giản như vậy.
13:11|很多故事来自古代，我们叫它们“成语故事”。|Nhiều câu chuyện bắt nguồn từ thời xưa, chúng tôi gọi đó là truyện thành ngữ.
13:16|是的，比如“画蛇添足”，“守株待兔”……这些故事都很短，也很有名。|Đúng vậy, ví dụ “Vẽ rắn thêm chân”, “Ôm cây đợi thỏ”... Những chuyện này ngắn và rất nổi tiếng.
13:25|没错。|Đúng thế.
13:25|以后有机会，我们也可以给大家讲更多的成语故事。|Sau này có dịp, chúng ta có thể kể thêm nhiều truyện thành ngữ cho mọi người.
13:30|李明，我们刚才讲了一个有名的故事。|Lý Minh, vừa rồi chúng ta đã kể một câu chuyện nổi tiếng.
13:35|现在，我们自己也来创造一个很短、很简单的故事，好不好？|Bây giờ chúng ta tự sáng tác một câu chuyện thật ngắn và đơn giản nhé?
13:41|现在？我们自己创造？|Bây giờ sao? Tự chúng ta sáng tác à?
13:43|对啊！给我们的听众朋友做一个示范。|Đúng vậy! Làm mẫu cho các thính giả.
13:47|一个专门为今天晚上写的，独一无二的睡前故事。|Một câu chuyện trước giờ ngủ độc nhất, được viết riêng cho tối nay.
13:53|好啊，这个挑战很有意思。|Được đấy, thử thách này thú vị thật.
13:56|那……我们的故事，主角是谁？|Vậy... nhân vật chính của câu chuyện là ai?
14:00|嗯……我想一想。不如，是一只小猫和一条小鱼，怎么样？|Ừm... để tôi nghĩ xem. Hay là một chú mèo con và một chú cá nhỏ, được không?
14:07|小猫和小鱼？|Mèo con và cá nhỏ sao?
14:09|可是，猫喜欢吃鱼啊。他们能成为朋友吗？|Nhưng mèo thích ăn cá mà. Chúng có thể trở thành bạn không?
14:15|这就要看我们的故事怎么写了。好，我先来。|Điều đó còn tùy chúng ta viết câu chuyện thế nào. Được, tôi bắt đầu trước.
14:20|请。|Xin mời.
14:21|在一个安静的晚上，有一只叫“毛毛”的小猫。|Vào một đêm yên tĩnh, có một chú mèo tên là Mao Mao.
14:25|他有白色的毛，蓝色的眼睛，非常可爱。|Chú có bộ lông trắng, đôi mắt xanh, vô cùng đáng yêu.
14:31|好的。这个晚上，毛毛觉得有点儿饿。|Được rồi. Tối hôm ấy, Mao Mao cảm thấy hơi đói.
14:35|他想吃东西。他走到了一个小小的河边。|Chú muốn ăn gì đó nên đi đến bên một dòng sông nhỏ.
14:41|在河里，他看到了一条小鱼。|Dưới sông, chú nhìn thấy một con cá nhỏ.
14:44|这条小鱼有金色的身体，在月光下，看起来非常漂亮。|Con cá nhỏ có thân màu vàng, dưới ánh trăng trông rất đẹp.
14:51|毛毛看到了小鱼，他想：“啊，一条鱼！我的晚餐来了！”他准备去抓这条小鱼。|Mao Mao nhìn thấy cá và nghĩ: “A, một con cá! Bữa tối của mình đến rồi!” Chú chuẩn bị bắt cá.
15:00|但是，就在这个时候，小鱼开口说话了。|Nhưng đúng lúc ấy, cá nhỏ bỗng lên tiếng.
15:05|小鱼对毛毛说：“你好，可爱的小猫。你晚上好。”|Cá nhỏ nói với Mao Mao: “Xin chào chú mèo đáng yêu. Chúc buổi tối tốt lành.”
15:11|毛毛愣住了。他从来没有听过鱼说话。|Mao Mao sững người. Chú chưa từng nghe cá nói chuyện.
15:15|他说：“你……你好。你会说话？”|Chú nói: “Cậu... xin chào. Cậu biết nói chuyện à?”
15:21|小鱼笑着说：“是啊。我看到你一个人，你是不是很孤单？”|Cá nhỏ mỉm cười: “Đúng vậy. Tôi thấy cậu ở một mình, có phải cậu rất cô đơn không?”
15:28|毛毛想了想，说：“是有一点儿。我的朋友们都回家睡觉了。只有我一个人。”|Mao Mao suy nghĩ rồi nói: “Cũng hơi cô đơn. Các bạn tôi đều về nhà ngủ rồi, chỉ còn mình tôi.”
15:36|小鱼说：“我也没有朋友。水里的其他鱼都游得很快，他们不喜欢和我玩儿。|Cá nhỏ nói: “Tôi cũng không có bạn. Những con cá khác bơi rất nhanh, chúng không thích chơi với tôi.
15:45|我愿意做你的朋友，但是，你是不是想吃我？”|Tôi muốn làm bạn với cậu, nhưng có phải cậu định ăn tôi không?”
15:51|毛毛看着小鱼漂亮的金色身体，又看了看她真诚的眼睛。|Mao Mao nhìn thân hình vàng óng xinh đẹp của cá nhỏ, rồi nhìn đôi mắt chân thành của cô ấy.
15:57|他突然觉得，自己不那么饿了。|Đột nhiên chú cảm thấy mình không còn đói đến thế nữa.
16:01|他说：“不，我不想吃你了。|Chú nói: “Không, tôi không muốn ăn cậu nữa.
16:05|有一个朋友，比一顿晚餐更重要。|Có một người bạn còn quan trọng hơn một bữa tối.
16:09|我叫毛毛，你叫什么名字？”|Tôi tên Mao Mao, cậu tên gì?”
16:13|小鱼高兴地说：“我叫‘闪闪’，因为我的身体会发光。很高兴认识你，毛毛！”|Cá nhỏ vui vẻ nói: “Tôi tên Thiểm Thiểm, vì cơ thể tôi có thể phát sáng. Rất vui được gặp cậu, Mao Mao!”
16:22|毛毛也高兴地说：“我也很高兴认识你，闪闪！”|Mao Mao cũng vui vẻ nói: “Tôi cũng rất vui được gặp cậu, Thiểm Thiểm!”
16:27|从那天晚上开始，小猫毛毛和小鱼闪闪成了最好的朋友。|Từ tối hôm ấy, mèo Mao Mao và cá Thiểm Thiểm trở thành đôi bạn thân nhất.
16:34|毛毛每天晚上都会去河边，不是为了吃鱼，而是为了和闪闪聊天，|Tối nào Mao Mao cũng đến bờ sông, không phải để ăn cá mà để trò chuyện với Thiểm Thiểm,
16:41|讲一讲白天发生的事情。|kể cho nhau nghe những chuyện xảy ra ban ngày.
16:44|我们的故事，讲完了。|Câu chuyện của chúng ta đã kể xong.
16:47|你觉得怎么样？|Bạn thấy thế nào?
16:49|我觉得很好。一个关于友谊的，温暖的故事。非常适合在睡觉前听。|Tôi thấy rất hay. Một câu chuyện ấm áp về tình bạn, rất thích hợp nghe trước khi ngủ.
16:56|我也希望听众朋友们会喜欢我们这个新的、简单的故事。|Tôi cũng mong các thính giả sẽ thích câu chuyện mới, đơn giản này.
17:02|好了，王雨，今天我们聊了很多关于故事的话题。|Được rồi Vương Vũ, hôm nay chúng ta đã trò chuyện rất nhiều về chủ đề kể chuyện.
17:08|从你奶奶的故事，到《龟兔赛跑》，再到我们自己创造的毛毛和闪闪的故事。|Từ chuyện của bà bạn, đến “Rùa và Thỏ”, rồi câu chuyện Mao Mao và Thiểm Thiểm do chúng ta tự sáng tác.
17:17|是啊，感觉时间过得真快。希望大家今天晚上能有一个好梦。|Đúng vậy, thời gian trôi nhanh thật. Mong mọi người tối nay có một giấc mơ đẹp.
17:23|在结束以前，我们还是像往常一样，|Trước khi kết thúc, chúng ta vẫn như thường lệ,
17:27|总结一下今天播客里出现的一些重要的词语吧。|hãy tổng kết một số từ quan trọng xuất hiện trong podcast hôm nay.
17:31|好的。|Được.
17:32|首先，我们今天的主题是“故事”，睡觉前听的故事，叫“睡前故事”。|Trước hết, chủ đề hôm nay là “câu chuyện”; câu chuyện nghe trước khi ngủ gọi là “truyện trước giờ ngủ”.
17:41|我们用“听”这个动词，听故事。|Chúng ta dùng động từ “nghe”: nghe kể chuyện.
17:45|然后，我们讲了一个有名的故事，叫《龟兔赛跑》。|Sau đó, chúng ta kể một câu chuyện nổi tiếng tên là “Rùa và Thỏ”.
17:51|里面有两个主角，一个是“兔子”，一个是“乌龟”。|Trong đó có hai nhân vật chính, một là “thỏ”, một là “rùa”.
17:56|兔子跑得非常“快”，而乌龟走得非常“慢”。|Thỏ chạy rất “nhanh”, còn rùa đi rất “chậm”.
18:01|对，“快”和“慢”。|Đúng, “nhanh” và “chậm”.
18:04|但是最后，慢的乌龟赢了，因为他一直“坚持”。|Nhưng cuối cùng rùa chậm chạp đã thắng vì nó luôn “kiên trì”.
18:10|我们还创造了一个故事，主角是“小猫”和“小鱼”，他们成了好“朋友”。|Chúng ta còn sáng tác một câu chuyện với nhân vật chính là “mèo con” và “cá nhỏ”; chúng trở thành “bạn tốt”.
18:18|总结得真好！这些都是非常基础和有用的词。|Tổng kết hay quá! Đây đều là những từ rất cơ bản và hữu ích.
18:23|希望大家今天晚上，不只是听了一个故事，也学习到了一些东西。|Mong rằng tối nay mọi người không chỉ nghe một câu chuyện mà còn học được điều gì đó.
18:30|希望如此。|Hy vọng là vậy.
18:31|那么，听众朋友们，在你们准备睡觉的时候，|Vậy thì, các thính giả thân mến, khi chuẩn bị đi ngủ,
18:36|我们也想问你们一个问题：你喜欢睡前听故事吗？|chúng tôi muốn hỏi các bạn một câu: Bạn có thích nghe kể chuyện trước khi ngủ không?
18:41|你最喜欢的，或者你还记得的第一个故事是什么呢？|Câu chuyện bạn thích nhất, hoặc câu chuyện đầu tiên bạn còn nhớ là gì?
18:46|如果你愿意，可以用你学到的简单的中文，|Nếu muốn, bạn có thể dùng tiếng Trung đơn giản đã học,
18:50|在我们的频道下面留言，和我们分享。|để bình luận bên dưới kênh và chia sẻ với chúng tôi.
18:54|我们很期待看到你们的故事。|Chúng tôi rất mong được đọc những câu chuyện của các bạn.
18:56|好了，今天就到这里吧。时间不早了。|Được rồi, hôm nay đến đây thôi. Cũng không còn sớm nữa.
19:01|祝大家有一个好梦。晚安。|Chúc mọi người có một giấc mơ đẹp. Ngủ ngon.
19:04|晚安。|Ngủ ngon.
19:05|下次再见。|Hẹn gặp lại lần sau.
"""

def to_seconds(value):
    minute, second = map(int, value.split(":"))
    return minute * 60 + second

def make_pinyin(hanzi):
    try:
        from pypinyin import pinyin, Style
    except ImportError as exc:
        raise RuntimeError(
            "Chua cai pypinyin. Chay: python -m pip install pypinyin"
        ) from exc

    result = pinyin(
        hanzi,
        style=Style.TONE,
        heteronym=False,
        errors=lambda text: list(text)
    )
    return " ".join(part[0] for part in result)

def main():
    parsed = []

    for line_number, line in enumerate(DATA.strip().splitlines(), 1):
        parts = line.strip().split("|", 2)

        if len(parts) != 3:
            raise ValueError(f"Dong {line_number} sai dinh dang")

        timecode, hanzi, vi = parts

        parsed.append({
            "start": float(to_seconds(timecode)),
            "hanzi": hanzi.strip(),
            "vi": vi.strip()
        })

    # Mốc phụ đề trùng nhau được giữ nguyên để kiểm tra,
    # không tạo câu có thời lượng bằng 0.
    result = []

    for i, item in enumerate(parsed):
        start = item["start"]

        next_later = next(
            (
                row["start"]
                for row in parsed[i + 1:]
                if row["start"] > start
            ),
            None
        )

        # Mốc cuối Supadata gốc: 1147.55 giây.
        end = next_later if next_later is not None else 1147.55

        # Hai phụ đề có cùng mốc sẽ được đánh dấu cần rà soát.
        same_start = sum(
            1 for row in parsed
            if row["start"] == start
        ) > 1

        result.append({
            "start": start,
            "end": end,
            "hanzi": item["hanzi"],
            "pinyin": make_pinyin(item["hanzi"]),
            "vi": item["vi"],
            "_timing_status": "chua_xac_minh_audio",
            "_timing_source": "youtube_subtitle_reference",
            "_same_start_needs_review": same_start
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("=== HOAN THANH PHAN 09:33 - 19:05 ===")
    print(f"So muc: {len(result)}")
    print(f"Bat dau: {result[0]['start']}s")
    print(f"Ket thuc: {result[-1]['end']}s")
    print(f"File: {OUTPUT}")
    print("Da co Hanzi, Pinyin va tieng Viet.")
    print("Timestamp van la moc tham chieu, chua xac minh audio.")
    print("Khong goi Supadata.")
    print("Khong thay doi SQL Server.")
    print("Khong thay doi HSK1.")

if __name__ == "__main__":
    main()
