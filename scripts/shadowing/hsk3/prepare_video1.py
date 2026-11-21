
import json
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==================================================
# 1. CAU HINH
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk3")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video1_zh_preview.json"
OUTPUT = DATA / "video1_translated_full.json"
REPORT = DATA / "video1_review_report.txt"

VIDEO_ID = "wZDej3Logc4"
EXPECTED_COUNT = 244


# ==================================================
# 2. BAN DICH TIENG VIET - 244 DOAN
#
# Moi so thu tu khop voi mot doan phu de goc.
# Cac doan bi cat giua cau duoc giu rieng.
# ==================================================

VI = {
    # 001 - 020
    1: "Xin chào mọi người, chào mừng đến với 'Tiếng Trung mỗi ngày'. Tôi là Lý Minh.",
    2: "Xin chào mọi người, tôi là Vương Vũ.",
    3: "Lý Minh, xin chào!",
    4: "Vương Vũ, xin chào!",
    5: "Hôm nay trông bạn rất vui. Trưa nay bạn ăn món gì ngon thế?",
    6: "Haha, bị bạn phát hiện rồi.",
    7: "Trưa nay tôi ăn ở một nhà hàng món Thượng Hải mới mở, hương vị đặc biệt ngon.",
    8: "Ồ? Thật vậy sao?",
    9: "Vậy bạn ăn nhanh không?",
    10: "Ý tôi là, món ăn ngon như thế, bạn ăn hết rất nhanh hay ăn từ từ?",
    11: "Ừm... Đây là một câu hỏi hay.",
    12: "Hình như tôi... ăn rất nhanh.",
    13: "Vì món ăn quá ngon nên tôi cứ ăn liên tục. Chẳng mấy chốc, đĩa của tôi đã hết sạch.",
    14: "Haha, tôi hiểu rồi.",
    15: "Thật ra hôm nay chúng ta có thể trò chuyện về chủ đề này: tốc độ ăn uống.",
    16: "Tốc độ ăn uống à?",
    17: "Chủ đề này thú vị đấy! Tôi chưa từng nghĩ đến.",
    18: "Được thôi, hôm nay chúng ta cùng nói xem ăn nhanh tốt hơn hay ăn chậm tốt hơn.",
    19: "Đúng vậy. Đây cũng là chủ đề liên quan rất nhiều đến cuộc sống hằng ngày của chúng ta.",
    20: "Đúng, mỗi người chúng ta đều phải ăn cơm mỗi ngày.",

    # 021 - 040
    21: "Được, vậy chúng ta bắt đầu ngay nhé!",
    22: "Được, Vương Vũ. Vừa rồi bạn nói trưa nay bạn ăn rất nhanh.",
    23: "Vậy bình thường bạn cũng ăn nhanh như thế à?",
    24: "Vì thế câu hỏi đầu tiên của tôi là: Bạn ăn nhanh không?",
    25: "Ừm, để tôi nghĩ xem. Tôi thấy mình ăn khá nhanh.",
    26: "Đặc biệt vào những ngày đi làm, buổi trưa chỉ có một tiếng nghỉ,",
    27: "tôi phải đến nhà hàng, xếp hàng và đợi đồ ăn được làm xong.",
    28: "Vì vậy thời gian thực sự ngồi xuống ăn không nhiều nên tôi ăn rất nhanh.",
    29: "Tôi rất hiểu. Có lẽ nhiều người đi làm cũng giống bạn. Thời gian quá ít.",
    30: "Đúng vậy. Còn bạn thì sao, Lý Minh? Bạn ăn nhanh không?",
    31: "Tôi à? Bây giờ tôi ăn rất chậm. Nhưng trước đây tôi cũng giống bạn, ăn rất nhanh.",
    32: "Hồi học đại học, tôi thường mua một chiếc bánh mì, vừa đi vừa ăn. Có lẽ chỉ mất năm phút",
    33: "là ăn xong rồi.",
    34: "Năm phút? Trời ơi, nhanh quá! Sao bạn ăn nhanh như vậy?",
    35: "Vì lúc đó lúc nào cũng bận, có rất nhiều tiết học và nhiều hoạt động.",
    36: "Tôi thấy chuyện ăn uống không quan trọng đến thế. Ăn xong nhanh thì có thể làm những việc khác,",
    37: "ví dụ như đến thư viện đọc sách hoặc đi chơi bóng rổ.",
    38: "Đúng, đúng. Hồi đi học tôi cũng vậy. Dường như lúc nào cũng có việc làm không hết.",
    39: "Vì vậy, nếu hỏi 'Bạn ăn nhanh không?', thì lúc đó câu trả lời của tôi chắc chắn là: 'Có, tôi ăn rất",
    40: "nhanh.'",

    # 041 - 060
    41: "Vậy từ khi nào bạn bắt đầu cảm thấy ăn nhanh có lẽ không tốt?",
    42: "Hay nói cách khác, bạn bắt đầu chú ý đến vấn đề này từ khi nào?",
    43: "Tôi nghĩ là sau khi đi làm. Mẹ tôi luôn nói với tôi một câu.",
    44: "Ồ? Mẹ bạn nói gì?",
    45: "Mỗi lần thấy tôi ăn nhanh như vậy, mẹ đều nói: 'Vương Vũ, ăn chậm lại một chút.'",
    46: "Ban đầu tôi không thấy có vấn đề gì vì đã quen rồi. Nhưng có một lần tôi ăn quá nhanh,",
    47: "đến buổi chiều dạ dày tôi hơi khó chịu.",
    48: "À, dạ dày khó chịu à?",
    49: "Đúng vậy. Sau hôm đó tôi mới bắt đầu nghĩ rằng lời mẹ nói 'Ăn chậm lại một chút'",
    50: "có lẽ là đúng.",
    51: "Xem ra lời mẹ nói lúc nào cũng có lý.",
    52: "Thật ra tôi thay đổi thói quen cũng là nhờ bố tôi.",
    53: "Ồ? Bố bạn cũng nói như vậy à?",
    54: "Đúng. Bố tôi cũng là người ăn rất chậm.",
    55: "Bố thường nói với tôi: 'Lý Minh, phải ăn chậm một chút. Ăn uống không phải nhiệm vụ, mà là một sự tận hưởng.'",
    56: "Một sự tận hưởng.",
    57: "'Ăn uống không phải nhiệm vụ, mà là một sự tận hưởng.' Câu này nói hay thật.",
    58: "Đúng vậy. Vì thế, các thính giả thân mến, các bạn cũng có thể tự hỏi mình hoặc hỏi những người xung quanh",
    59: "rằng: Bạn ăn nhanh không?",
    60: "Nếu câu trả lời là 'Có', có lẽ các bạn nên nghe cuộc trò chuyện tiếp theo của chúng tôi.",

    # 061 - 080
    61: "Chúng ta thường nghe người thân, bạn bè nhắc rằng 'Ăn chậm lại một chút'. Thật ra đằng sau lời nhắc đó",
    62: "có rất nhiều lý do.",
    63: "Ừm, tôi rất muốn nghe.",
    64: "Được, vừa rồi chúng ta đã nói về thói quen ăn nhanh trước đây.",
    65: "Vương Vũ, vừa rồi bạn nói mẹ bạn bảo 'Ăn chậm lại một chút'.",
    66: "Vậy bạn có biết tại sao phải ăn chậm hơn không?",
    67: "Ừm, tôi cũng không biết giải thích thế nào.",
    68: "Tôi chỉ biết lần đó mình ăn quá nhanh nên dạ dày khó chịu.",
    69: "Vì vậy tôi nghĩ, ăn từ từ có lẽ tốt cho dạ dày?",
    70: "Bạn nói rất đúng!",
    71: "Có lẽ đây là điều quan trọng nhất.",
    72: "Người xưa có một câu nói như thế này:",
    73: "Ăn từ từ tốt cho sức khỏe.",
    74: "Ăn từ từ tốt cho sức khỏe.",
    75: "Ừm, hình như tôi cũng từng nghe câu này.",
    76: "Đúng vậy. Bạn nghĩ xem, dạ dày của chúng ta cần thời gian để hoạt động.",
    77: "Nếu chúng ta ăn quá nhanh,",
    78: "nhiều thức ăn chưa được nhai kỹ đã đi vào dạ dày.",
    79: "Như vậy dạ dày sẽ rất mệt.",
    80: "Tôi hiểu rồi. Giống như một nhà máy,",

    # 081 - 100
    81: "đột nhiên có quá nhiều việc phải làm,",
    82: "công nhân sẽ rất, rất mệt.",
    83: "Dạ dày của chúng ta chính là nhà máy đó.",
    84: "Phép so sánh này hay quá! Chính là ý đó.",
    85: "Vì vậy, ăn từ từ tốt cho sức khỏe,",
    86: "đặc biệt là tốt cho dạ dày.",
    87: "Ừm, có lý.",
    88: "Ngoài tốt cho dạ dày, còn có lợi ích nào khác không?",
    89: "Tất nhiên là có.",
    90: "Bạn thử nghĩ xem, món Thượng Hải bạn ăn trưa nay,",
    91: "bạn còn nhớ hương vị của nó không?",
    92: "Tôi... để tôi nghĩ xem.",
    93: "Có một món thịt kho tàu và một món rau xanh.",
    94: "Vì tôi ăn quá nhanh,",
    95: "bây giờ tôi chỉ nhớ là nó rất ngon,",
    96: "nhưng cụ thể hương vị như thế nào thì hình như tôi hơi quên rồi.",
    97: "Haha, bạn thấy chưa, vấn đề chính là ở đó.",
    98: "Nếu bạn ăn chậm hơn một chút,",
    99: "bạn sẽ thưởng thức hương vị món ăn tốt hơn.",
    100: "Mỗi miếng ăn, bạn đều có thể cảm nhận được",

    # 101 - 120
    101: "món này ngọt hay mặn,",
    102: "mềm hay giòn.",
    103: "Đúng! Có những lúc,",
    104: "tôi đi cùng bạn bè đến một nhà hàng rất ngon,",
    105: "và tốn rất nhiều tiền.",
    106: "Nếu tôi ăn quá nhanh,",
    107: "tôi cảm thấy hơi lãng phí tiền,",
    108: "vì tôi chưa thực sự thưởng thức hương vị ấy.",
    109: "Chính xác.",
    110: "Khi một món ăn bạn đặc biệt yêu thích được đặt trước mặt,",
    111: "trong lòng bạn chắc chắn sẽ nghĩ:",
    112: "Ôi, món này ngon quá!",
    113: "Đúng! Chắc chắn sẽ nghĩ vậy!",
    114: "Đặc biệt là món thịt kho tàu ấy,",
    115: "khi ăn miếng đầu tiên, trong lòng tôi đã nói:",
    116: "Ôi, món này ngon quá!",
    117: "Vậy thì, khi bạn nói",
    118: "'Món này ngon quá!'",
    119: "chẳng phải bạn nên ăn chậm lại",
    120: "để cảm nhận hương vị thơm ngon của nó nhiều hơn sao?",

    # 121 - 140
    121: "Từng miếng một, ăn từ từ.",
    122: "Bạn nói đúng!",
    123: "Nếu một món ngon đến vậy,",
    124: "tôi nên dành thêm thời gian cho nó.",
    125: "Tôi nên từ từ thưởng thức.",
    126: "Như thế, ăn uống mới thực sự trở thành niềm vui.",
    127: "Đúng vậy.",
    128: "Vì thế, ăn từ từ tốt cho sức khỏe,",
    129: "đồng thời giúp chúng ta thưởng thức món ngon tốt hơn.",
    130: "Lần sau khi bạn lại được ăn một món ngon,",
    131: "đừng quên tự nhắc mình rằng,",
    132: "chậm lại một chút, rồi chậm thêm chút nữa.",
    133: "Tôi nhớ rồi.",
    134: "Thứ nhất, ăn từ từ tốt cho sức khỏe.",
    135: "Thứ hai, có thể thưởng thức hương vị món ăn tốt hơn.",
    136: "Khi tôi cảm thấy",
    137: "'Món này ngon quá!'",
    138: "thì đó là tín hiệu nhắc tôi phải chậm lại.",
    139: "Bạn tổng kết rất hay.",
    140: "Lý Minh, những điều chúng ta vừa nói hình như đều là khi ăn một mình.",

    # 141 - 160
    141: "Nhưng nhiều lúc, chúng ta ăn cùng gia đình và bạn bè.",
    142: "Bạn vừa nhắc đến một điều rất quan trọng.",
    143: "Ở Trung Quốc, nhiều khi ăn uống không chỉ để no bụng,",
    144: "mà còn là một hoạt động giao tiếp rất quan trọng.",
    145: "Đúng vậy, mỗi tuần ăn cơm cùng gia đình một lần,",
    146: "hoặc hẹn ăn cùng người bạn lâu ngày không gặp.",
    147: "Đúng. Những lúc như vậy, bạn nghĩ mọi người ăn nhanh hay chậm?",
    148: "Tôi nghĩ chắc chắn là chậm, vì mọi người còn trò chuyện nữa!",
    149: "Vừa ăn vừa nói chuyện, thời gian trôi qua rất nhanh,",
    150: "nhưng mọi người lại ăn khá chậm.",
    151: "Hoàn toàn chính xác. Ví dụ khi ăn ở nhà cùng bố mẹ,",
    152: "mẹ thường gắp một món vào bát tôi rồi nói...",
    153: "Mẹ sẽ nói: 'Ăn thêm chút nữa đi!'",
    154: "Haha, đúng. Mẹ còn nói: 'Lý Minh, con ăn thử món cá này đi, hôm nay cá rất tươi.'",
    155: "Đúng, đúng! Mẹ tôi cũng giống hệt vậy!",
    156: "Mẹ nói: 'Vương Vũ, con nếm thử món canh này đi, mẹ nấu lâu lắm đấy.'",
    157: "Người trong gia đình lúc nào cũng vậy.",
    158: "Đúng thế. Bạn bè cũng vậy.",
    159: "Khi chúng tôi cùng nhau đi ăn lẩu,",
    160: "tôi thường nói với bạn: 'Này, bạn thử thịt bò này đi, ngon lắm!'",

    # 161 - 180
    161: "Chính xác! Rồi bạn tôi có thể nói:",
    162: "'Được chứ! Bạn cũng thử món này đi, món này cũng ngon lắm!'",
    163: "Cứ như vậy, mọi người chia sẻ đồ ăn và chia sẻ cả niềm vui.",
    164: "Bạn thấy đấy, trong bầu không khí như vậy, tốc độ ăn tự nhiên sẽ chậm lại.",
    165: "Không ai chỉ cúi đầu ăn thật nhanh cho xong.",
    166: "Mọi người đều đang giao lưu với nhau.",
    167: "Tôi hiểu rồi.",
    168: "Vì vậy, khi ăn cùng người khác,",
    169: "điều quan trọng không chỉ là thức ăn mà còn là người đang ăn cùng chúng ta.",
    170: "Ăn chậm lại thì chúng ta mới có thời gian quan tâm và trò chuyện với nhau.",
    171: "Đúng vậy. Nếu một người bạn nói với bạn rằng 'Gần đây công việc của tôi không vui',",
    172: "thì bạn đâu thể vừa ăn thật nhanh vừa nói",
    173: "'Ừ, ừ, ừ.' Bạn phải dừng lại, nhìn họ và lắng nghe họ nói.",
    174: "Có lý. Tốc độ ăn uống cũng thể hiện thái độ của bạn đối với buổi gặp mặt.",
    175: "Chậm lại thể hiện rằng tôi rất trân trọng thời gian được ở cùng mọi người.",
    176: "Chính là như vậy.",
    177: "Vì thế bạn thấy đấy, dù là vì sức khỏe hay để thưởng thức món ăn ngon hơn,",
    178: "hoặc khi giao tiếp với mọi người, ăn chậm hơn đều là lựa chọn tốt hơn.",
    179: "Lần sau ăn cùng bạn bè, khi một món ăn được mang lên,",
    180: "bạn có thể nói trước: 'Ôi, món này ngon quá!'",

    # 181 - 200
    181: "Sau đó chia cho bạn mình và nói: 'Bạn thử món này đi.'",
    182: "Haha, tôi học được rồi.",
    183: "Như vậy, bầu không khí sẽ rất vui vẻ,",
    184: "và tốc độ ăn của mọi người cũng tự nhiên chậm lại.",
    185: "Đúng vậy.",
    186: "Được rồi, Vương Vũ, hôm nay chúng ta bắt đầu từ câu 'Bạn ăn nhanh không?'",
    187: "và đã trò chuyện rất nhiều về tốc độ ăn uống.",
    188: "Đúng vậy, thời gian trôi nhanh thật. Tôi đã học được rất nhiều.",
    189: "Trước đây tôi thật sự không nghĩ đây là một vấn đề.",
    190: "Hôm nay khi trò chuyện, thực ra chúng ta đã lặp lại một số câu tiếng Trung rất hữu ích.",
    191: "Tôi nghĩ các câu này đều có thể sử dụng trong những bữa ăn hằng ngày.",
    192: "Ừm, đúng thế! Chúng ta cùng tổng kết nhé?",
    193: "Như vậy các thính giả cũng có thể học lại một lần nữa.",
    194: "Ý hay đấy. Câu đầu tiên chúng ta học hôm nay, cũng là câu mở đầu,",
    195: "chính là câu hỏi người khác về thói quen ăn uống.",
    196: "Câu đó là gì?",
    197: "Là: Bạn ăn nhanh không?",
    198: "Đúng. Bạn ăn nhanh không?",
    199: "Bạn có thể hỏi bạn bè hoặc người thân.",
    200: "Được. Thế câu thứ hai là gì?",

    # 201 - 220
    201: "Thông thường đó là một lời khuyên của gia đình hoặc bạn bè.",
    202: "Lời khuyên ấy là: Phải ăn chậm lại một chút.",
    203: "Ừm. Phải ăn chậm lại một chút. Mẹ tôi thường nói thế.",
    204: "Câu thứ ba cho chúng ta biết vì sao cần ăn chậm.",
    205: "Tôi nhớ ra rồi, câu đó là: Ăn từ từ tốt cho sức khỏe.",
    206: "Hoàn toàn đúng. Ăn từ từ tốt cho sức khỏe.",
    207: "Đây là một trong những lý do quan trọng nhất.",
    208: "Thế câu thứ tư thì sao?",
    209: "Là lời cảm thán trong lòng khi chúng ta ăn được một món ngon.",
    210: "Đúng, câu cảm thán đó là: Món này ngon quá!",
    211: "Món này ngon quá! Tôi hy vọng ngày nào cũng có cơ hội nói câu này!",
    212: "Haha, tôi cũng vậy.",
    213: "Vậy câu cuối cùng là gì?",
    214: "Thường được nói khi chia sẻ món ăn ngon với người khác.",
    215: "Tôi biết rồi! Là: Bạn thử món này đi.",
    216: "Chính xác. Bạn thử món này đi. Một lời mời rất thân thiện và nhiệt tình.",
    217: "Tuyệt quá. Chúng ta cùng đọc nhanh lại năm câu này một lần nữa nhé.",
    218: "Được. Câu thứ nhất: Bạn ăn nhanh không?",
    219: "Câu thứ hai: Phải ăn chậm lại một chút.",
    220: "Câu thứ ba: Ăn từ từ tốt cho sức khỏe.",

    # 221 - 244
    221: "Câu thứ tư: Món này ngon quá!",
    222: "Câu thứ năm: Bạn thử món này đi.",
    223: "Tôi thấy cả năm câu này đều rất hữu ích!",
    224: "Tối nay về nhà ăn cơm, tôi sẽ dùng thử. Tôi sẽ ăn từ từ,",
    225: "nếu mẹ tôi nấu một món ngon, tôi sẽ nói thật to:",
    226: "'Mẹ ơi, món này ngon quá!'",
    227: "Haha, nghe vậy chắc chắn mẹ bạn sẽ rất vui.",
    228: "Được rồi, chương trình 'Tiếng Trung mỗi ngày' hôm nay cũng sắp kết thúc.",
    229: "Hy vọng qua chương trình hôm nay, mọi người",
    230: "sẽ quan tâm hơn đến thói quen ăn uống của mình.",
    231: "Đúng vậy. Ăn uống là một việc nhỏ chúng ta làm mỗi ngày,",
    232: "nhưng trong những việc nhỏ cũng có nhiều điều đáng học hỏi.",
    233: "Hy vọng mọi người đều ăn uống lành mạnh và vui vẻ.",
    234: "Vậy cuối cùng chúng tôi cũng muốn hỏi các bạn đang nghe podcast:",
    235: "Bạn ăn nhanh không?",
    236: "Xung quanh bạn có ai luôn nhắc bạn 'Ăn chậm lại một chút' không?",
    237: "Hãy để lại bình luận bên dưới kênh của chúng tôi,",
    238: "và chia sẻ câu chuyện của bạn.",
    239: "Chúng tôi rất mong được đọc những chia sẻ của mọi người.",
    240: "Được rồi, chương trình hôm nay đến đây thôi.",
    241: "Cảm ơn mọi người đã lắng nghe!",
    242: "Tôi là Lý Minh.",
    243: "Tôi là Vương Vũ.",
    244: "Hẹn gặp lại mọi người ở số tiếp theo!"
}


# ==================================================
# 3. TAO PINYIN CO DAU THANH
# ==================================================

def make_pinyin(hanzi):
    tokens = re.findall(
        r"[\u3400-\u9fff]+|[A-Za-z0-9]+",
        hanzi
    )

    result = []

    for token in tokens:
        if re.fullmatch(
            r"[\u3400-\u9fff]+",
            token
        ):
            result.extend(
                lazy_pinyin(
                    token,
                    style=Style.TONE
                )
            )
        else:
            result.append(token)

    return " ".join(result).strip()


# ==================================================
# 4. KIEM TRA VA GHEP DU LIEU
# ==================================================

def main():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "YouTube ID khong khop HSK3 video 1."
        )

    original = data.get("sentences")

    if not isinstance(original, list):
        raise ValueError(
            "Khong tim thay danh sach sentences."
        )

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"nhung co {len(original)}."
        )

    expected_keys = set(
        range(1, EXPECTED_COUNT + 1)
    )

    if set(VI) != expected_keys:
        missing = sorted(expected_keys - set(VI))
        extra = sorted(set(VI) - expected_keys)

        raise ValueError(
            f"Ban dich sai STT. "
            f"Thieu: {missing}; Thua: {extra}"
        )

    sentences = []
    short_segments = []
    previous_end = 0.0

    for i, item in enumerate(original, 1):
        start = round(float(item["start"]), 3)
        end = round(float(item["end"]), 3)

        hanzi = str(item["hanzi"]).strip()
        vi = VI[i].strip()

        if not hanzi or not vi:
            raise ValueError(
                f"Doan {i} thieu noi dung."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}."
            )

        if i > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Timestamp chong nhau o doan {i}."
            )

        duration = round(end - start, 3)

        if duration < 0.8:
            short_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": make_pinyin(hanzi),
            "vi": vi
        })

        previous_end = end

    # File moi, khong ghi de preview goc.
    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": sentences
    }

    OUTPUT.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # ======================================
    # 5. BAO CAO KIEM TRA
    # ======================================

    report_lines = [
        "SHADOWING HSK3 - VIDEO 1",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"So doan ngan < 0.8 giay: {len(short_segments)}",
        "",
        "DOAN QUA NGAN:"
    ]

    for item in short_segments:
        report_lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    report_lines.extend([
        "",
        "CAC VI TRI CAN DOI CHIEU:",
        "39-40: Cau bi cat giua hai doan.",
        "49-50: Cau bi cat giua hai doan.",
        "55-56: Co loi noi duoc lap lai.",
        "161-162: Can kiem tra loi phu de.",
        "",
        "Luu y:",
        "- Pinyin duoc tao tu dong.",
        "- Ban dich dua tren transcript tieng Trung.",
        "- Chua doi chieu tat ca am thanh.",
        "- Chua cap nhat SQL Server."
    ])

    REPORT.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    # ======================================
    # 6. DOC LAI FILE
    # ======================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    assert saved["youtube_id"] == VIDEO_ID
    assert len(saved["sentences"]) == EXPECTED_COUNT

    assert all(
        s["hanzi"] and s["pinyin"] and s["vi"]
        for s in saved["sentences"]
    )

    # ======================================
    # 7. IN KET QUA
    # ======================================

    print("===== HSK3 VIDEO 1 - PINYIN VA DICH =====")
    print("YouTube ID:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("So ban dich:", len(VI))
    print("Doan ngan < 0.8s:", len(short_segments))

    print("\n===== 5 DOAN DAU =====")

    for i, item in enumerate(sentences[:5], 1):
        print(
            f"\n{i:03d} "
            f"[{item['start']:.2f} - "
            f"{item['end']:.2f}]"
        )
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("VI:", item["vi"])

    print("\n===== FILE DA LUU =====")
    print("JSON:", OUTPUT)
    print("Bao cao:", REPORT)

    print("\nKIEM TRA JSON: OK")
    print("CHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
