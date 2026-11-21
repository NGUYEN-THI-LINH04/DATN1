
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# 1. CAU HINH DU AN
# ============================================================

PROJECT = Path(r"D:\DATN1")
TARGET = PROJECT / "scripts" / "shadowing" / "hsk2"

PART3 = (
    TARGET / "previews" /
    "video_1_part3_0933_to_end.json"
)

OUTPUT = (
    TARGET / "data" / "processed" /
    "video_1_corrected_from_user_transcript.json"
)

BACKUP = TARGET / "data" / "backups"

VIDEO = "nxAfRmACtZs"
MA_NOI_DUNG = 8
MA_BAI_HOC = 25

# ============================================================
# 2. PHU DE CHUAN 00:06 - 09:33
# Nguon: hoi thoai nguoi dung da cung cap
# Dinh dang: thoi gian | Hanzi | tieng Viet
# ============================================================

FIRST = r'''
00:06|啊……我有点儿困了，李明。|À... tôi hơi buồn ngủ rồi, Lý Minh.
00:09|困了？王雨，你看，现在时间还早呢，天还没黑。|Buồn ngủ rồi sao? Vương Vũ, cậu xem, bây giờ còn sớm, trời còn chưa tối mà.
00:15|我知道。但是我昨天晚上睡得不太好。|Tôi biết. Nhưng tối qua tôi ngủ không được ngon lắm.
00:20|是吗？为什么？工作太忙了？|Thế à? Tại sao? Công việc bận quá sao?
00:24|也不是。我昨天晚上睡觉以前，想找一个故事来听。|Cũng không phải. Trước khi ngủ tối qua, tôi muốn tìm một câu chuyện để nghe.
00:32|你知道吗？就是那种……让人很放松的，可以帮助睡觉的故事。|Cậu biết không? Kiểu chuyện khiến người ta thư giãn và dễ ngủ ấy.
00:41|我明白，你说的是“睡前故事”。|Tôi hiểu rồi, ý cậu là truyện kể trước giờ ngủ.
00:46|对！就是睡前故事。但是我找了很久，都没有找到一个我喜欢的。|Đúng! Chính là truyện trước giờ ngủ. Nhưng tôi tìm rất lâu mà chẳng thấy chuyện nào mình thích.
00:55|所以，我睡得很晚。|Vì thế tôi ngủ rất muộn.
00:58|原来是这样。睡前故事……这是一个很有意思的话题。|Ra là vậy. Truyện trước giờ ngủ... đúng là một chủ đề thú vị.
01:04|你很喜欢听故事吗？|Cậu rất thích nghe kể chuyện à?
01:07|非常喜欢！特别是小时候。|Rất thích! Đặc biệt là hồi nhỏ.
01:10|我也是。那我们今天就聊一聊这个吧？聊一聊“故事”。|Tôi cũng vậy. Thế hôm nay chúng ta nói về chuyện này nhé? Nói về những câu chuyện.
01:16|也许我们的听众朋友们今天晚上也可以听着我们的播客，安静地睡觉。|Biết đâu tối nay thính giả có thể vừa nghe podcast của chúng ta vừa nhẹ nhàng chìm vào giấc ngủ.
01:23|这个主意太好了！我喜欢！|Ý tưởng này tuyệt quá! Tôi thích đấy!
01:26|王雨，你刚才说，你小时候特别喜欢听故事。|Vương Vũ, vừa rồi cậu nói hồi nhỏ cậu đặc biệt thích nghe kể chuyện.
01:31|是你爸爸妈妈给你讲故事吗？|Có phải bố mẹ kể chuyện cho cậu không?
01:34|不是我爸爸妈妈。是我奶奶。|Không phải bố mẹ, mà là bà nội tôi.
01:37|你奶奶？|Bà nội cậu à?
01:38|对。我很小的时候，每天晚上，我奶奶都会坐在我的床边，|Đúng. Khi tôi còn rất nhỏ, tối nào bà cũng ngồi bên giường tôi,
01:46|给我讲故事。她的声音特别温柔，特别好听。|kể chuyện cho tôi nghe. Giọng bà vô cùng dịu dàng và dễ nghe.
01:51|你还记得她给你讲了什么故事吗？|Cậu còn nhớ bà đã kể những chuyện gì không?
01:56|嗯……我不记得所有的故事了。|Ừm... tôi không nhớ hết mọi câu chuyện nữa.
02:00|故事太多了。但是我记得那个感觉。|Có quá nhiều chuyện. Nhưng tôi nhớ cảm giác lúc ấy.
02:07|感觉？是什么样的感觉？|Cảm giác ư? Là cảm giác như thế nào?
02:10|就是……很安全，很暖和的感觉。|Chính là... cảm giác rất an toàn và ấm áp.
02:16|外面可能很冷，但是在房间里，听着奶奶的声音，我觉得非常非常舒服。|Ngoài trời có thể rất lạnh, nhưng trong phòng, nghe giọng bà, tôi cảm thấy vô cùng dễ chịu.
02:26|有时候，故事还没有讲完，我就已经睡着了。|Đôi khi chuyện chưa kể xong tôi đã ngủ thiếp đi.
02:32|我完全明白。那个感觉比故事本身更重要。|Tôi hoàn toàn hiểu. Cảm giác ấy còn quan trọng hơn chính câu chuyện.
02:37|对！你呢，李明？你小时候，有人给你讲故事吗？|Đúng! Còn cậu, Lý Minh? Hồi nhỏ có ai kể chuyện cho cậu không?
02:45|有。是我爸爸。但是我爸爸和你奶奶不太一样。|Có, là bố tôi. Nhưng bố tôi hơi khác bà của cậu.
02:50|哦？怎么不一样？|Ồ? Khác thế nào?
02:52|我爸爸也给我讲故事，但是他每次讲完一个故事，都会问我一个问题。|Bố cũng kể chuyện cho tôi, nhưng lần nào kể xong ông cũng hỏi tôi một câu.
02:59|什么问题？|Câu hỏi gì?
03:00|他会问：“李明，听完这个故事，你学到了什么？”（笑）你爸爸像一个老师。|Ông hỏi: “Lý Minh, nghe xong chuyện này con học được gì?” (Cười) Bố cậu giống một thầy giáo thật.
03:09|是啊。他觉得，每个故事都有它的意思，有它的道理。|Đúng vậy. Ông cho rằng câu chuyện nào cũng có ý nghĩa và bài học riêng.
03:16|所以，我小时候听故事，不只是听，我还要想。要想这个故事告诉了我什么。|Vì thế hồi nhỏ tôi không chỉ nghe mà còn phải suy nghĩ xem câu chuyện muốn nói điều gì.
03:23|那也很好啊。你还记得你爸爸给你讲过什么故事吗？|Như vậy cũng hay mà. Cậu còn nhớ bố đã kể chuyện gì không?
03:29|记得。他给我讲了很多关于动物的故事。|Nhớ chứ. Ông kể rất nhiều chuyện về động vật.
03:33|故事里，有聪明的动物，也有点儿笨的动物。有好人，也有坏人。|Trong chuyện có con vật thông minh, có con hơi ngốc; có người tốt, có người xấu.
03:40|我奶奶也喜欢讲动物的故事！我觉得小孩子都喜欢听动物的故事。|Bà tôi cũng thích kể chuyện động vật! Tôi nghĩ trẻ con đều thích nghe chuyện về động vật.
03:48|因为很简单，也很有意思。|Vì chúng đơn giản mà thú vị.
03:51|没错。简单的故事，有意思的故事，最适合在睡觉前听。|Đúng vậy. Những câu chuyện đơn giản, thú vị thích hợp nhất để nghe trước khi ngủ.
03:57|它们不会让你的脑子太累。|Chúng không khiến đầu óc cậu quá mệt.
03:59|是的。说到动物故事，我马上就想到了一个。一个非常非常有名的故事。|Đúng thế. Nhắc đến chuyện động vật, tôi lập tức nhớ ra một chuyện rất nổi tiếng.
04:07|哦？我们想的是同一个吗？|Ồ? Có phải chúng ta đang nghĩ đến cùng một chuyện không?
04:11|这个故事里，是不是有一个跑得很快的动物，还有一个跑得很慢的动物？|Trong chuyện có một con vật chạy rất nhanh và một con chạy rất chậm, đúng không?
04:18|对！就是那个！《龟兔赛跑》！|Đúng! Chính là chuyện đó! “Rùa và Thỏ”!
04:21|看来我们想的是同一个。|Xem ra chúng ta nghĩ đến cùng một chuyện.
04:24|这个故事，我觉得，在中国，每个小孩子都听过。|Tôi nghĩ ở Trung Quốc đứa trẻ nào cũng từng nghe chuyện này.
04:29|那我们现在给我们的听众朋友们也讲一遍这个故事，好不好？|Vậy bây giờ chúng ta kể lại chuyện ấy cho thính giả nghe nhé?
04:36|用最简单的中文。|Bằng tiếng Trung đơn giản nhất.
04:38|好主意。我们可以一起讲。|Ý hay đấy. Chúng ta có thể cùng kể.
04:40|好的，那我开始。|Được, vậy tôi bắt đầu nhé.
04:42|我们的故事，开始了。|Câu chuyện của chúng ta bắt đầu.
04:46|很久很久以前，森林里住着很多动物。|Ngày xửa ngày xưa, trong rừng có rất nhiều loài vật sinh sống.
04:52|有一只兔子。|Có một chú thỏ.
04:54|这只兔子，他有一个特点。|Chú thỏ này có một đặc điểm.
04:56|他跑得非常非常快。|Nó chạy rất, rất nhanh.
04:59|对，他是森林里跑得最快的动物。|Đúng, nó là con vật chạy nhanh nhất khu rừng.
05:04|所以，他有点儿骄傲。|Vì thế nó hơi kiêu ngạo.
05:07|他常常对别的动物说：“你们看我，我跑得多快啊！”森林里还有一只乌龟。|Nó thường khoe với các con vật khác: “Nhìn tôi này, tôi chạy nhanh biết bao!” Trong rừng còn có một chú rùa.
05:17|这只乌龟呢，他也有一个特点。|Chú rùa này cũng có một đặc điểm.
05:20|他走得非常非常慢。|Nó đi rất, rất chậm.
05:24|对。他做什么事情都很慢。|Đúng. Nó làm việc gì cũng chậm.
05:26|吃饭很慢，走路也很慢。|Ăn chậm, đi bộ cũng chậm.
05:30|有一天，兔子看见了正在走路的乌龟。|Một hôm, thỏ nhìn thấy rùa đang đi.
05:35|兔子笑着对乌龟说：“乌龟，乌龟，你太慢了！|Thỏ cười và nói với rùa: “Rùa ơi, rùa ơi, cậu chậm quá!
05:42|你看你走路的样子，真的太慢了！”乌龟听了，他不高兴。|Nhìn dáng đi của cậu kìa, chậm thật đấy!” Rùa nghe xong thì không vui.
05:50|他对兔子说：“你很快，我知道。|Rùa nói với thỏ: “Tôi biết cậu rất nhanh.
05:54|但是，我们比赛，你可能不会赢。”兔子听了，哈哈大笑。|Nhưng nếu chúng ta thi, chưa chắc cậu đã thắng.” Thỏ nghe vậy liền cười ha hả.
06:02|他说：“什么？你说我不会赢？|Nó nói: “Cái gì? Cậu bảo tôi sẽ không thắng sao?
06:07|太有意思了！|Thú vị thật đấy!
06:08|好！我们明天就比赛！|Được! Ngày mai chúng ta thi!
06:11|让森林里所有的动物都来看！”|Hãy để tất cả các con vật trong rừng đến xem!”
06:15|乌龟说：“好。明天见。”第二天，天气很好。|Rùa nói: “Được. Hẹn mai gặp.” Hôm sau trời rất đẹp.
06:23|森林里的动物都来了。|Các con vật trong rừng đều đến.
06:26|小鸟来了，小狗来了，小猫也来了。|Chim nhỏ, chó con và mèo con đều đến.
06:30|他们都想看兔子和乌龟的比赛。|Chúng đều muốn xem cuộc thi giữa thỏ và rùa.
06:35|兔子和乌龟站在起点。|Thỏ và rùa đứng ở vạch xuất phát.
06:38|一只小鸟说：“预备，开始！”兔子像风一样跑了出去。非常快！|Một chú chim hô: “Chuẩn bị, bắt đầu!” Thỏ lao đi như gió, cực kỳ nhanh!
06:47|一转眼，就看不见了。|Chỉ chớp mắt đã không thấy nó đâu.
06:51|乌龟呢？他也在努力地跑。|Còn rùa thì sao? Nó cũng đang cố gắng chạy.
06:55|但是，我们知道，他跑得很慢。|Nhưng chúng ta biết nó chạy rất chậm.
06:57|他一步一步，慢慢地向前走。|Nó từng bước chậm rãi tiến về phía trước.
07:02|兔子跑了很远。|Thỏ đã chạy được rất xa.
07:05|他回头看。他看不到乌龟。|Nó ngoái lại nhìn nhưng không thấy rùa.
07:08|一点儿也看不到。|Hoàn toàn không nhìn thấy.
07:11|兔子想：“乌龟太慢了。|Thỏ nghĩ: “Rùa chậm quá.
07:14|他可能明天早上才能到这里。|Có khi đến sáng mai nó mới tới đây.
07:18|天气这么好，我想在这里睡一会儿。|Trời đẹp thế này, mình muốn ngủ ở đây một lát.
07:23|我睡醒了，再跑也来得及。”于是，兔子就在一棵大树下面，开始睡觉了。|Ngủ dậy rồi chạy tiếp vẫn kịp.” Thế là thỏ nằm ngủ dưới một gốc cây lớn.
07:32|他睡得很香。|Nó ngủ rất ngon.
07:35|这个时候，乌龟在哪里呢？|Lúc ấy rùa đang ở đâu?
07:38|乌龟还在路上。|Rùa vẫn đang trên đường.
07:41|他很累，也很热。|Nó rất mệt và nóng.
07:44|但是他没有休息。|Nhưng nó không nghỉ ngơi.
07:46|他心里想：“我一定要坚持。|Nó tự nhủ: “Mình nhất định phải kiên trì.
07:50|我不能停。”所以，乌龟一直走，一直走。|Mình không được dừng lại.” Vì thế rùa cứ đi mãi, đi mãi.
07:56|他走得很慢，但是他没有停。|Nó đi rất chậm nhưng không dừng lại.
08:00|过了一会儿，乌龟走到了那棵大树下面。|Một lúc sau, rùa đi đến dưới gốc cây lớn ấy.
08:06|他看到了谁？|Nó nhìn thấy ai?
08:07|他看到了正在睡觉的兔子。|Nó nhìn thấy thỏ đang ngủ.
08:11|对。兔子睡得正香呢。|Đúng vậy. Thỏ đang ngủ rất say.
08:15|乌龟看了看兔子，他什么也没说，继续一步一步，慢慢地向前走。|Rùa nhìn thỏ, không nói gì, tiếp tục từng bước chậm rãi đi về phía trước.
08:24|又过了很久很久，兔子醒了。|Rất lâu sau, thỏ tỉnh dậy.
08:28|他睁开眼睛，伸了一个懒腰。|Nó mở mắt, vươn vai.
08:31|他说：“啊，我睡得真好！|Nó nói: “A, mình ngủ ngon quá!
08:34|现在，乌龟到哪里了？”他向后看，没有乌龟。|Giờ rùa đến đâu rồi?” Nó nhìn ra sau nhưng không thấy rùa.
08:41|他又向前看……他看到了什么？|Nó lại nhìn phía trước... và đã thấy gì?
08:45|他看到，乌龟已经快要到终点了！|Nó thấy rùa sắp đến đích rồi!
08:50|兔子非常着急！|Thỏ vô cùng sốt ruột!
08:52|他马上开始跑。|Nó lập tức chạy.
08:54|他跑得很快很快，比以前更快！|Nó chạy thật nhanh, còn nhanh hơn trước!
08:58|但是，太晚了。|Nhưng đã quá muộn.
09:02|是的，太晚了。|Đúng vậy, quá muộn rồi.
09:04|就在兔子快要追上的时候，乌龟慢慢地走过了终点线。|Ngay khi thỏ sắp đuổi kịp, rùa chậm rãi bước qua vạch đích.
09:11|所以，比赛结束了。|Thế là cuộc thi kết thúc.
09:14|谁是第一名？|Ai về nhất?
09:16|是那只走得很慢，但是一直没有放弃的乌龟。|Chính là chú rùa đi rất chậm nhưng không bao giờ bỏ cuộc.
09:23|这个故事讲完了。|Câu chuyện đến đây là hết.
09:26|虽然我们都知道这个故事，但是现在再说一遍，还是觉得很有意思。|Dù chúng ta đều biết chuyện này, kể lại lần nữa vẫn thấy rất thú vị.
'''

# ============================================================
# 3. HAM CHUYEN DOI THOI GIAN
# ============================================================

def sec(t):
    m, s = map(int, t.split(":"))
    return m * 60 + s


# ============================================================
# 4. DOC PHU DE 00:06 - 09:33
# ============================================================

def read_first():
    result = []

    for n, line in enumerate(
        FIRST.strip().splitlines(), 1
    ):
        fields = line.split("|", 2)

        if len(fields) != 3:
            raise ValueError(
                f"Sai dinh dang dong {n}"
            )

        t, hanzi, vi = fields

        result.append({
            "start": float(sec(t)),
            "hanzi": hanzi.strip(),
            "vi": vi.strip()
        })

    return result


# ============================================================
# 5. DOC PHAN 09:33 - 19:05 DA TAO TRUOC DO
# ============================================================

def read_last():
    if not PART3.exists():
        raise FileNotFoundError(
            f"Khong tim thay part3: {PART3}"
        )

    with PART3.open(
        "r",
        encoding="utf-8-sig"
    ) as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) != 119:
        raise ValueError(
            "Part3 phai co dung 119 muc"
        )

    return [
        {
            "start": float(x["start"]),
            "hanzi": x["hanzi"].strip(),
            "vi": x["vi"].strip()
        }
        for x in data
    ]


# ============================================================
# 6. TAO PINYIN TU HANZI
# ============================================================

def pinyin_for(hanzi):
    try:
        from pypinyin import lazy_pinyin, Style
    except ImportError as e:
        raise RuntimeError(
            "Chay: python -m pip install pypinyin"
        ) from e

    return " ".join(
        lazy_pinyin(
            hanzi,
            style=Style.TONE,
            errors=lambda s: list(s)
        )
    )


# ============================================================
# 7. TAO FILE JSON MOI
# ============================================================

def build():
    first = read_first()
    last = read_last()

    if last[0]["start"] != 573.0:
        raise ValueError(
            "Part3 khong bat dau tai 09:33"
        )

    rows = first + last

    for row in rows:
        if not row["hanzi"] or not row["vi"]:
            raise ValueError(
                "Co cau thieu Hanzi hoac tieng Viet"
            )

    # Xu ly nhung cau trung moc thoi gian.
    # Day chi la moc du kien tu phu de.

    i = 0
    same_start_groups = []

    while i < len(rows):
        j = i + 1

        while (
            j < len(rows)
            and rows[j]["start"] == rows[i]["start"]
        ):
            j += 1

        if j - i > 1:
            next_time = (
                rows[j]["start"]
                if j < len(rows)
                else 1147.55
            )

            original = rows[i]["start"]

            same_start_groups.append(
                (original, j - i)
            )

            for k in range(i, j):
                rows[k]["start"] = round(
                    original
                    + (next_time - original)
                    * (k - i) / (j - i),
                    3
                )

        i = j

    # Tao end va pinyin cho tung cau.
    for i, row in enumerate(rows):

        row["end"] = round(
            rows[i + 1]["start"]
            if i + 1 < len(rows)
            else 1147.55,
            3
        )

        row["start"] = round(
            row["start"], 3
        )

        row["pinyin"] = pinyin_for(
            row["hanzi"]
        )

        if row["end"] <= row["start"]:
            raise ValueError(
                f"Thoi gian khong hop le tai cau {i+1}"
            )

    # Chi xuat cac truong web can.
    sentences = [
        {
            "start": row["start"],
            "end": row["end"],
            "hanzi": row["hanzi"],
            "pinyin": row["pinyin"],
            "vi": row["vi"]
        }
        for row in rows
    ]

    result = {
        "module": "shadowing",
        "youtube_id": VIDEO,
        "sentences": sentences
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n=== TAO JSON DA SUA ===")
    print("Phan dau:", len(first), "cau")
    print("Phan cuoi:", len(last), "cau")
    print("Tong:", len(sentences), "cau")
    print(
        "Cac moc trung:",
        same_start_groups
    )
    print("File:", OUTPUT)

    print(
        "Luu y: timestamp theo phu de, "
        "chua xac minh audio."
    )

    print(
        "Luu y: pinyin tu dong, "
        "can ra soat chu da am."
    )

    return result


# ============================================================
# 8. CAP NHAT SQL SERVER
# ============================================================

def sql_update(data, commit):

    sys.path.insert(
        0, str(PROJECT)
    )

    from database import get_connection

    conn = get_connection()
    conn.autocommit = False

    try:
        cur = conn.cursor()

        # Kiem tra dung ban ghi video.
        cur.execute("""
            SELECT
                MaBaiHoc,
                TieuDe,
                NoiDung
            FROM dbo.NoiDungBaiHoc
            WITH (UPDLOCK, HOLDLOCK)
            WHERE MaNoiDung = ?
        """, MA_NOI_DUNG)

        old = cur.fetchone()

        if (
            not old
            or old[0] != MA_BAI_HOC
            or VIDEO not in str(old[2])
        ):
            raise RuntimeError(
                "MaNoiDung=8 khong khop video. "
                "Khong thay doi SQL."
            )

        # Tao JSON Unicode.
        payload = json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":")
        )

        # Mac dinh chi xem truoc.
        if not commit:
            print("\n=== SQL PREVIEW ===")
            print("MaNoiDung:", MA_NOI_DUNG)
            print("Tieu de:", old[1])
            print(
                "So cau moi:",
                len(data["sentences"])
            )
            print("CHUA THAY DOI SQL.")

            conn.rollback()
            return

        # Sao luu SQL cu.
        BACKUP.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        backup = BACKUP / (
            f"video_1_before_fix_{timestamp}.json"
        )

        backup.write_text(
            json.dumps(
                {
                    "MaNoiDung": MA_NOI_DUNG,
                    "MaBaiHoc": old[0],
                    "TieuDe": old[1],
                    "NoiDung": old[2]
                },
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print("\nDa sao luu:", backup)

        # Chia nho JSON de tranh loi ODBC
        # khi truyen chuoi Unicode dai.
        chunks = [
            payload[i:i + 700]
            for i in range(
                0, len(payload), 700
            )
        ]

        if not chunks:
            raise ValueError(
                "JSON rong, khong cap nhat"
            )

        # Ghi doan dau.
        cur.execute("""
            UPDATE dbo.NoiDungBaiHoc
            SET NoiDung =
                CAST(? AS NVARCHAR(MAX))
            WHERE MaNoiDung = ?
              AND MaBaiHoc = ?
        """,
            chunks[0],
            MA_NOI_DUNG,
            MA_BAI_HOC
        )

        if cur.rowcount != 1:
            raise RuntimeError(
                "Cap nhat khong dung 1 ban ghi"
            )

        # Noi cac doan con lai.
        for index, chunk in enumerate(
            chunks[1:], 2
        ):
            cur.execute("""
                UPDATE dbo.NoiDungBaiHoc
                SET NoiDung =
                    CAST(NoiDung AS NVARCHAR(MAX))
                    + CAST(? AS NVARCHAR(MAX))
                WHERE MaNoiDung = ?
                  AND MaBaiHoc = ?
            """,
                chunk,
                MA_NOI_DUNG,
                MA_BAI_HOC
            )

            if cur.rowcount != 1:
                raise RuntimeError(
                    f"Loi khi ghi doan {index}"
                )

            if index % 20 == 0:
                print(
                    f"Da ghi {index}/{len(chunks)} doan"
                )

        # Doc lai SQL de doi chieu.
        cur.execute("""
            SELECT NoiDung
            FROM dbo.NoiDungBaiHoc
            WHERE MaNoiDung = ?
        """, MA_NOI_DUNG)

        saved_row = cur.fetchone()

        if not saved_row:
            raise RuntimeError(
                "Khong doc duoc du lieu vua luu"
            )

        saved = json.loads(saved_row[0])

        if saved != data:
            raise RuntimeError(
                "JSON SQL khong khop JSON goc. "
                "Huy giao dich."
            )

        # Chi commit khi moi thu chinh xac.
        conn.commit()

        print("\n==============================")
        print("CAP NHAT SQL THANH CONG")
        print("==============================")
        print("MaNoiDung:", MA_NOI_DUNG)
        print("MaBaiHoc:", MA_BAI_HOC)
        print(
            "So cau:",
            len(saved["sentences"])
        )
        print("YouTube:", VIDEO)
        print("Backup:", backup)
        print("Khong sua bai 差不多.")
        print("Khong sua HSK1.")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ============================================================
# 9. MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Sua Shadowing HSK2 theo "
            "phu de nguoi dung cung cap"
        )
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Sao luu va cap nhat SQL"
    )

    args = parser.parse_args()

    data = build()

    sql_update(
        data,
        args.commit
    )


if __name__ == "__main__":
    main()
