
from pathlib import Path
import json

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2\data\processed")

SOURCE = BASE / "video3_translated_draft.json"
OUTPUT = BASE / "video3_translated_full.json"

# ==========================================
# BAN DICH TIENG VIET: CAU 51 - 259
# ==========================================

translations = {
    # --------------------------------------
    # PHAN 1: DUA TIENG TRUNG VAO CUOC SONG
    # --------------------------------------

    51: "Ngày nào cũng nhìn thấy thì bạn sẽ nhận biết được những chữ Hán này.",
    52: "Đúng vậy! Hơn nữa, bạn không chỉ nhìn mà còn phải sử dụng chúng.",
    53: "Khi muốn gọi điện, bạn phải tìm mục 'Điện thoại';",
    54: "khi muốn xem thời tiết, bạn phải tìm mục 'Thời tiết'.",
    55: "Học như vậy vừa nhanh vừa hiệu quả.",
    56: "Tôi còn một phương pháp nhỏ tương tự muốn chia sẻ với mọi người.",
    57: "Mau nói cho mọi người nghe đi!",
    58: "Đó là dán những mảnh giấy ghi tên tiếng Trung lên các đồ vật trong nhà.",
    59: "Haha, thú vị đấy! Ví dụ như thế nào?",
    60: "Ví dụ, bạn dán một mảnh giấy ghi chữ '桌子' lên chiếc bàn.",
    61: "Dán một mảnh giấy ghi chữ '椅子' lên chiếc ghế.",
    62: "Dán '电脑' lên máy tính, '电视' lên tivi và '门' lên cửa,",
    63: "dán chữ '床' lên giường.",
    64: "Đúng! Chính là như vậy.",
    65: "Mỗi sáng thức dậy, bạn nhìn thấy chữ 'Giường'; khi ngồi xuống làm việc, bạn nhìn thấy 'Bàn' và 'Ghế';",
    66: "khi xem tivi, bạn nhìn thấy chữ 'Tivi'. Những từ này đều là một phần trong cuộc sống của bạn,",
    67: "nên bạn không cần dành thời gian riêng để học thuộc. Nhìn nhiều lần rồi sẽ nhớ.",
    68: "Phương pháp này rất phù hợp với người mới bắt đầu! Toàn là những đồ vật cơ bản.",
    69: "Hơn nữa, bạn có thể vừa chỉ vào đồ vật vừa đọc thành tiếng. Chỉ vào bàn và nói: 'Đây là cái bàn.'",
    70: "Chỉ vào quả táo và nói: 'Đây là một quả táo.'",
    71: "Đúng vậy. Đây chính là điều đầu tiên chúng ta muốn nói: Hãy để tiếng Trung trở thành một phần cuộc sống của bạn.",
    72: "Bạn không cần làm điều gì khó khăn, chỉ cần thay đổi một chút thôi.",
    73: "Được rồi, Lý Minh, nói xong về 'nhìn', chúng ta nói sang điều khác nhé.",
    74: "Tôi thấy 'nghe' cũng rất quan trọng.",

    # --------------------------------------
    # PHAN 2: NGHE VA XEM TIENG TRUNG
    # --------------------------------------

    75: "Tôi đồng ý. Trước hết, ngôn ngữ được dùng để nghe và nói.",
    76: "Vậy về việc luyện nghe, bạn có lời khuyên nào không?",
    77: "Tất nhiên rồi! Phương pháp tôi thích nhất là nghe nhạc tiếng Trung.",
    78: "Ồ? Nghe nhạc sao?",
    79: "Nhiều bạn nói rằng ca sĩ hát quá nhanh nên họ không hiểu.",
    80: "Ban đầu nghe không hiểu cũng không sao.",
    81: "Chúng ta có thể tìm những bài hát chậm và đơn giản.",
    82: "Ví dụ như những bài hát dành cho trẻ nhỏ.",
    83: "Chẳng hạn bài 'Hai chú hổ'?",
    84: "Đúng rồi! Haha!",
    85: "'Hai chú hổ, hai chú hổ, chạy thật nhanh, chạy thật nhanh...' Những bài hát như vậy có lời đơn giản và rất thú vị.",
    86: "Hoặc có những bài hát khá cũ nhưng rất kinh điển, được hát tương đối chậm và rõ ràng.",
    87: "Bạn có thể giới thiệu cho chúng tôi một bài không?",
    88: "Ừm... Để tôi nghĩ xem.",
    89: "À, có một bài hát tên là 'Bạn bè'.",
    90: "Tôi nghĩ rất nhiều người Trung Quốc đều biết hát bài này.",
    91: "Lời bài hát không khó, lại rất gần gũi.",
    92: "Ví dụ trong bài có câu:",
    93: "'Bạn bè cùng nhau đi suốt một đời,",
    94: "những ngày tháng ấy sẽ không trở lại...'",
    95: "Nghe những bài hát như vậy, bạn sẽ cảm thấy rất ấm áp.",
    96: "Lời khuyên này rất hay.",
    97: "Ban đầu bạn có thể chỉ nghe mà chưa cần nhìn lời bài hát.",
    98: "Cảm nhận âm nhạc và cách phát âm tiếng Trung.",
    99: "Sau đó, bạn có thể vừa nhìn lời bài hát vừa nghe.",
    100: "Cuối cùng, bạn có thể thử tự hát theo.",
    101: "Đúng vậy! Ca hát là một cách học rất vui.",
    102: "Ngoài nghe nhạc, chúng ta còn có thể nghe gì nữa?",
    103: "Tất nhiên là podcast 'Tiếng Trung mỗi ngày' của chúng ta rồi!",
    104: "Haha, cảm ơn bạn đã giới thiệu!",
    105: "Đúng vậy, nghe những podcast có tốc độ nói tương đối chậm cũng là một phương pháp hay.",
    106: "Chúng tôi nói không nhanh và sử dụng những từ khá đơn giản.",
    107: "Đúng. Ngoài 'nghe' ra, còn có 'xem' nữa.",
    108: "Xem gì vậy?",
    109: "Tôi nghĩ chúng ta có thể xem những bộ phim hoạt hình dành cho trẻ nhỏ.",
    110: "Phim hoạt hình sao? Tại sao?",
    111: "Vì phim hoạt hình được làm cho trẻ em xem,",
    112: "nên các nhân vật thường nói rất chậm và rất rõ ràng.",
    113: "Từ vựng và câu nói trong đó cũng rất đơn giản.",
    114: "Ví dụ, Trung Quốc có một bộ phim hoạt hình rất nổi tiếng,",
    115: "tên là 'Con trai đầu to và bố đầu nhỏ'.",
    116: "À! Tôi biết! Hồi nhỏ tôi cũng xem!",
    117: "'Con trai đầu to, bố đầu nhỏ, đôi bạn thân thiết, hai bố con vui vẻ!'",
    118: "Đúng, chính là bộ phim đó. Những đoạn hội thoại trong phim rất đơn giản,",
    119: "ví dụ: 'Bố ơi, chúng ta đi đâu chơi đây?'",
    120: "'Chúng ta đi công viên nhé, được không?'",
    121: "Đó đều là những câu chúng ta sử dụng trong cuộc sống hằng ngày.",
    122: "Phương pháp này hay đấy. Hơn nữa, xem phim hoạt hình rất thú vị nên không có cảm giác đang học.",
    123: "Mỗi ngày xem mười phút cũng có thể học được rất nhiều câu hữu ích.",
    124: "Ngoài ra, hiện nay rất nhiều người thích xem video ngắn,",
    125: "chẳng hạn như trên Douyin. Ở đó cũng có nhiều video dạy tiếng Trung,",
    126: "hoặc video người Trung Quốc chia sẻ về cuộc sống của họ.",
    127: "Đúng vậy, những video đó rất ngắn, có khi chỉ một phút,",
    128: "nên bạn sẽ không cảm thấy mệt. Bạn có thể xem họ nấu ăn như thế nào,",
    129: "đi du lịch ra sao và nghe họ trò chuyện bằng tiếng Trung tự nhiên nhất.",
    130: "Tóm lại, phần thứ hai là: Nghe nhiều và xem nhiều.",
    131: "Nghe những bài hát tiếng Trung đơn giản, nghe podcast của chúng ta;",
    132: "xem phim hoạt hình dễ hiểu và những video ngắn thú vị.",
    133: "Để đôi tai và đôi mắt của bạn dần quen với tiếng Trung.",

    # --------------------------------------
    # PHAN 3: MANH DAN NOI TIENG TRUNG
    # --------------------------------------

    134: "Được rồi, chúng ta đã nói về 'xem' và 'nghe', đều là tiếp nhận ngôn ngữ. Giờ chúng ta nói đến việc sử dụng ngôn ngữ, tức là 'nói'.",
    135: "Đúng vậy, 'nói' vô cùng quan trọng.",
    136: "Nhiều bạn biết rất nhiều chữ Hán và nghe hiểu một số câu, nhưng lại không dám nói.",
    137: "Tôi hoàn toàn hiểu! Vì họ sợ nói sai, sợ người khác không hiểu hoặc cười nhạo mình.",
    138: "Trước đây tôi cũng gặp vấn đề này.",
    139: "Thật sao? Bạn kể cho chúng tôi nghe câu chuyện của bạn đi.",
    140: "Được. Tôi nhớ lần đầu tiên tự mình đến quán cà phê và muốn gọi món bằng tiếng Trung.",
    141: "Tim tôi đập rất nhanh.",
    142: "Bạn đã lo lắng rồi.",
    143: "Vô cùng căng thẳng! Trước khi đến đó, tôi đã luyện tập ở nhà rất nhiều lần:",
    144: "'Xin chào, tôi muốn một cốc cà phê.' Câu này rất đơn giản, đúng không?",
    145: "Đúng, rất đơn giản.",
    146: "Nhưng khi bước vào quán và nhìn thấy nhân viên phục vụ, tôi vẫn rất sợ. Tôi nói nhỏ:",
    147: "'Xin chào... Tôi... tôi muốn... cà phê.'",
    148: "Haha, rồi sao nữa? Nhân viên phục vụ nói gì?",
    149: "Nhân viên rất thân thiện. Anh ấy mỉm cười hỏi tôi: 'Vâng. Xin hỏi bạn muốn cỡ lớn, cỡ vừa,",
    150: "hay cỡ nhỏ? Bạn muốn cà phê nóng hay cà phê đá?'",
    151: "Ồ, anh ấy hỏi bạn nhiều câu quá.",
    152: "Đúng vậy! Lúc đó tôi đứng sững lại. Tôi chỉ chuẩn bị câu 'Tôi muốn một cốc cà phê', chứ chưa chuẩn bị",
    153: "để trả lời những câu hỏi này!",
    154: "Cuối cùng bạn đã làm thế nào?",
    155: "Tôi chỉ vào hình trên thực đơn và nói: 'Cái này... cỡ lớn... nóng.' Mặc dù tôi nói rất",
    156: "chưa tốt, nhưng nhân viên vẫn hiểu. Anh ấy đưa cho tôi một cốc cà",
    157: "phê.",
    158: "Khi nhận được cốc cà phê đó, tôi thực sự vô cùng vui sướng!",
    159: "Tôi hiểu rồi. Tuy nói chưa hoàn hảo nhưng bạn đã thành công. Bạn đã mua được",
    160: "cốc cà phê mình muốn uống.",
    161: "Đúng! Từ đó, tôi cảm thấy nói sai cũng không sao, nói chậm cũng không sao.",
    162: "Điều quan trọng nhất là bạn phải dám nói! Khi bạn nói ra, người khác mới có thể giúp bạn và bạn mới tiến bộ được.",
    163: "Câu chuyện của bạn thật tuyệt.",
    164: "Đó chính là điều tôi muốn nói: Đừng sợ mắc lỗi.",
    165: "Bất kỳ ai học ngoại ngữ cũng đều sẽ mắc lỗi.",
    166: "Khi học tiếng Anh, người Trung Quốc cũng mắc rất nhiều lỗi. Mắc lỗi là một phần của quá trình học.",
    167: "Đúng vậy. Ngoài việc đến cửa hàng mua đồ, còn phương pháp nào tốt để luyện nói không?",
    168: "Nếu xung quanh tôi không có người Trung Quốc thì phải làm sao?",
    169: "Đây là một câu hỏi hay.",
    170: "Nếu không có bạn bè người Trung Quốc ở bên cạnh, bạn có thể... tự nói chuyện với chính mình.",
    171: "Tự nói chuyện với mình sao?",
    172: "Đúng. Nghe có vẻ hơi kỳ lạ nhưng rất hữu ích.",
    173: "Ví dụ, khi thức dậy vào buổi sáng, bạn có thể",
    174: "nhìn mình trong gương rồi nói: 'Xin chào! Hôm nay thời tiết rất đẹp.",
    175: "Tôi phải đi làm. Hôm nay tôi rất vui.'",
    176: "Haha, phương pháp này thú vị thật.",
    177: "Hoặc khi nhìn thấy đồ vật nào đó, bạn hãy gọi tên nó bằng tiếng Trung.",
    178: "Bạn cầm một chiếc cốc lên,",
    179: "rồi nói: 'Đây là một chiếc cốc. Trong cốc có nước. Tôi muốn uống nước.'",
    180: "Tôi hiểu rồi. Tức là tự trò chuyện với bản thân, vừa làm giáo viên vừa làm học sinh của chính mình.",
    181: "Chính xác. Luyện tập như vậy bạn sẽ không căng thẳng vì không có ai khác nghe.",
    182: "Bạn có thể nói chậm, suy nghĩ một chút rồi nói.",
    183: "Điều này giúp miệng và bộ não của bạn quen với việc nói tiếng Trung.",
    184: "Lời khuyên này tuyệt quá! Dám mở miệng nói và không sợ mắc lỗi.",
    185: "Có thể nói chuyện với bạn bè, cũng có thể tự nói với chính mình.",

    # --------------------------------------
    # PHAN 4: TAP VIET MOI NGAY
    # --------------------------------------

    186: "Được rồi, chúng ta đã nói về nghe, nói và xem.",
    187: "Khi học ngôn ngữ còn có một kỹ năng rất quan trọng nữa, đó là 'viết'.",
    188: "À, 'viết' chữ Hán sao?",
    189: "Nhiều bạn cảm thấy viết chữ Hán là phần khó nhất khi học tiếng Trung.",
    190: "Đúng vậy, viết chữ Hán cần phải luyện tập.",
    191: "Nhưng việc 'viết' mà chúng ta nói ở đây không chỉ là viết đi viết lại một chữ Hán một trăm lần.",
    192: "Chúng ta đang nói đến một cách 'viết' thú vị hơn.",
    193: "Ý bạn là sao?",
    194: "Tôi khuyên mọi người mỗi ngày thử viết nhật ký bằng một câu thôi. Chỉ một câu.",
    195: "Nhật ký một câu sao? Nghe có vẻ rất đơn giản.",
    196: "Rất đơn giản. Ví dụ, hôm nay bạn đã làm gì?",
    197: "Hôm nay tâm trạng của bạn thế nào? Bạn có thể viết lại những điều đó.",
    198: "Ví dụ: 'Hôm nay là thứ Hai. Tôi đã đến trường.'",
    199: "Hoặc: 'Hôm nay tôi ăn món Trung Quốc, rất ngon.'",
    200: "'Hôm nay tôi quen một người bạn mới, tôi rất vui.'",
    201: "Đúng! Chỉ cần một câu đơn giản như thế. Bạn không cần viết bài văn dài. Mỗi ngày",
    202: "viết một câu,",
    203: "thứ nhất, bạn có thể luyện viết chữ Hán;",
    204: "thứ hai, bạn có thể luyện cách diễn đạt suy nghĩ bằng tiếng Trung.",
    205: "Tôi thích phương pháp này.",
    206: "Mỗi ngày chỉ cần dành năm phút là đủ.",
    207: "Nếu kiên trì, sau một tháng bạn có thể viết được ba mươi câu.",
    208: "Sau một năm, bạn sẽ có một cuốn nhật ký được viết bằng tiếng Trung.",
    209: "Đúng vậy. Khi nhìn lại, bạn sẽ nhận ra mình đã tiến bộ rất nhiều.",
    210: "Ngoài viết nhật ký, trong thời đại Internet ngày nay còn cách nào khác không?",
    211: "Tất nhiên rồi. Bạn có thể viết trên mạng xã hội.",
    212: "Ví dụ, dùng WeChat để gửi một tin nhắn cho người bạn Trung Quốc.",
    213: "Gửi gì đây?",
    214: "Chỉ cần một lời chào đơn giản nhất là được.",
    215: "Ví dụ, buổi sáng nhắn: 'Chào buổi sáng!' Đến giờ ăn thì hỏi: 'Bạn ăn cơm chưa?'",
    216: "Haha, đây là một trong những câu người Trung Quốc thích hỏi nhất.",
    217: "Đúng vậy. Hoặc nếu bạn tham gia một nhóm học tiếng Trung,",
    218: "bạn có thể chia sẻ một từ mới hay một câu mà mình học được hôm nay.",
    219: "Ví dụ, hôm nay bạn học từ 'Thời tiết', bạn có thể viết trong nhóm: 'Hôm nay thời tiết Bắc Kinh thế nào?'",
    220: "Tôi hiểu rồi. Thông qua việc viết những tin nhắn ngắn này, chúng ta đang sử dụng tiếng Trung.",
    221: "Mục đích của việc viết không phải để thi cử, mà là để giao tiếp.",
    222: "Hoàn toàn chính xác. Vì thế, phương pháp nhỏ thứ tư là: Mỗi ngày viết một chút.",
    223: "Có thể là một câu nhật ký,",
    224: "hoặc một tin nhắn gửi cho bạn bè.",
    225: "Hãy để việc 'viết' trở thành một hoạt động nhẹ nhàng và vui",
    226: "vẻ.",
    227: "Được rồi, thời gian trôi nhanh thật.",
    228: "Hôm nay chúng ta đã trò chuyện về bốn phương pháp học tiếng Trung giúp mọi người tiến bộ từng chút một mỗi ngày.",
    229: "Chúng ta cùng ôn lại ngắn gọn nhé.",
    230: "Được thôi.",
    231: "Thứ nhất, để tiếng Trung trở thành một phần trong cuộc sống.",
    232: "Ví dụ, đổi ngôn ngữ điện thoại sang tiếng Trung hoặc dán nhãn tiếng Trung lên đồ vật trong nhà.",
    233: "Thứ hai, nghe nhiều và xem nhiều.",
    234: "Nghe nhạc tiếng Trung, xem phim hoạt hình và video ngắn,",
    235: "để đôi tai và đôi mắt quen với tiếng Trung.",
    236: "Thứ ba, dám nói và không sợ sai.",
    237: "Mạnh dạn mở lời và giao tiếp với người khác,",
    238: "hoặc tự nói chuyện với chính mình.",
    239: "Thứ tư, mỗi ngày viết một chút.",
    240: "Có thể viết nhật ký một câu hoặc gửi một tin nhắn đơn giản bằng tiếng Trung.",

    # --------------------------------------
    # PHAN KET: TONG KET VA DONG VIEN
    # --------------------------------------

    241: "Đúng vậy. Những phương pháp này nghe đều rất đơn giản, đúng không?",
    242: "Đúng, đều rất đơn giản.",
    243: "Tôi cảm thấy điều quan trọng nhất khi học một ngôn ngữ",
    244: "có lẽ không phải là bạn thông minh đến mức nào,",
    245: "mà là bạn có thể kiên trì mỗi ngày hay không.",
    246: "Cho dù mỗi ngày chỉ có mười phút,",
    247: "chỉ cần bạn tiếp tục kiên trì,",
    248: "sau một năm,",
    249: "bạn chắc chắn sẽ nhìn thấy một bản thân hoàn toàn khác.",
    250: "Vương Vũ nói hay quá.",
    251: "Hy vọng cuộc trò chuyện hôm nay có thể giúp ích và động viên các bạn đang học tiếng Trung.",
    252: "Đúng vậy! Con đường học tập còn rất dài, nhưng chỉ cần mỗi ngày tiến một bước nhỏ, chúng ta nhất định sẽ đến đích.",
    253: "Mọi người cố lên!",
    254: "Được rồi, chương trình 'Tiếng Trung mỗi ngày' hôm nay đến đây thôi.",
    255: "Cảm ơn mọi người đã lắng nghe.",
    256: "Nếu yêu thích podcast của chúng tôi, các bạn nhớ theo dõi nhé.",
    257: "Hẹn gặp lại mọi người lần sau!",
    258: "Hẹn gặp lại!",
    259: "Tạm biệt!"
}

# ==========================================
# KIEM TRA DU LIEU
# ==========================================

if not SOURCE.exists():
    raise FileNotFoundError(
        f"Khong tim thay file: {SOURCE}"
    )

data = json.loads(
    SOURCE.read_text(encoding="utf-8")
)

sentences = data.get("sentences", [])

if data.get("youtube_id") != "uv8KNcXpels":
    raise ValueError("Sai video YouTube!")

if len(sentences) != 259:
    raise ValueError(
        f"Can 259 doan, hien co {len(sentences)}"
    )

expected = set(range(51, 260))
actual = set(translations)

if actual != expected:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    raise ValueError(
        f"Thieu cau: {missing}; "
        f"Thua cau: {extra}"
    )

# ==========================================
# GHEP BAN DICH
# ==========================================

for number, vi in translations.items():
    sentence = sentences[number - 1]

    if sentence.get("vi") and sentence["vi"] != vi:
        raise ValueError(
            f"Cau {number} da co ban dich khac. "
            "Dung lai de tranh ghi de."
        )

    sentence["vi"] = vi

# Kiem tra day du 259 doan.
for i, sentence in enumerate(sentences, 1):
    for field in ("start", "end", "hanzi", "pinyin", "vi"):
        if field not in sentence or sentence[field] in (None, ""):
            raise ValueError(
                f"Cau {i} thieu truong {field}"
            )

    if float(sentence["end"]) <= float(sentence["start"]):
        raise ValueError(
            f"Timestamp sai o cau {i}"
        )

# Cac nhom phu de bi cat giua cau hoac giua tu.
# Can ghep lai truoc khi dua len website.
merge_groups = [
    [149, 150],
    [152, 153],
    [155, 156, 157],
    [159, 160],
    [201, 202],
    [225, 226],
]

data["status"] = "translation_complete_needs_review"
data["translation_language"] = "vi"
data["needs_merge_groups"] = merge_groups

OUTPUT.write_text(
    json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    ),
    encoding="utf-8"
)

# ==========================================
# IN KET QUA
# ==========================================

translated = sum(
    bool(s.get("vi"))
    for s in sentences
)

print("===== HOAN THANH BAN DICH =====")
print("Video:", data["youtube_id"])
print("Tong so doan:", len(sentences))
print("Da dich:", translated, "/ 259")
print("File:", OUTPUT)

print("\n===== 5 CAU CUOI =====")

for i in range(254, 259):
    s = sentences[i]
    print(f"{i + 1:03d}. {s['hanzi']}")
    print("VI:", s["vi"])

print("\nSo nhom can ghep:", len(merge_groups))
print("CHUA CAP NHAT SQL SERVER.")
