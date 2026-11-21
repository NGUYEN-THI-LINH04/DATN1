
from pathlib import Path
import json
import re

from pypinyin import lazy_pinyin, Style


# ==================================================
# 1. CAU HINH VIDEO 5
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video5_zh_preview.json"
OUTPUT = DATA / "video5_translated_full.json"
REPORT = DATA / "video5_review_report.txt"

VIDEO_ID = "MYQrQvbR8Vk"
EXPECTED_COUNT = 121


# ==================================================
# 2. BAN DICH TIENG VIET
# Moi so thu tu ung voi mot doan phu de goc.
# ==================================================

TRANSLATIONS = {
    1: "Xin chào mọi người! Chào mừng đến với số mới của chương trình 'Tiếng Trung mỗi ngày'. Tôi là Lý Minh.",
    2: "Xin chào mọi người! Tôi là Vương Vũ. Rất vui được gặp lại mọi người!",
    3: "Vương Vũ, xin chào!",
    4: "Lý Minh, xin chào!",
    5: "Hôm nay trông bạn rất vui, có chuyện gì tốt à?",
    6: "Haha, cũng không có gì đặc biệt.",
    7: "Chỉ là hôm nay công việc rất thuận lợi nên tâm trạng khá tốt.",
    8: "Còn bạn thì sao? Hôm nay bạn thế nào?",
    9: "Hôm nay tôi rất bận, cảm giác thời gian trôi qua đặc biệt nhanh.",
    10: "Sáng lúc tôi ra khỏi nhà trời vẫn chưa sáng rõ, tối tan làm về nhà thì trời đã tối rồi.",

    11: "Đúng vậy, một ngày của rất nhiều người đều như thế.",
    12: "Điều này khiến tôi nghĩ đến việc ngày nào chúng ta cũng nói 'Hôm nay rất bận' hoặc 'Hôm nay rất mệt',",
    13: "nhưng cụ thể một ngày của chúng ta diễn ra như thế nào nhỉ?",
    14: "Có lẽ các thính giả của chúng ta cũng rất tò mò.",
    15: "Ừm, ý tưởng này hay đấy!",
    16: "Hôm nay chúng ta cùng trò chuyện về chủ đề 'Một ngày của tôi' nhé!",
    17: "Chúng ta có thể chia sẻ xem một ngày bình thường của mình diễn ra như thế nào.",
    18: "Được thôi, không vấn đề gì. Như vậy mọi người cũng có thể học một số từ vựng và câu tiếng Trung về cuộc sống hằng ngày.",
    19: "Được, vậy chúng ta bắt đầu từ buổi sáng nhé. Vương Vũ, bình thường bạn thức dậy lúc mấy giờ?",
    20: "Ừm... Câu hỏi này hơi khó trả lời.",

    21: "Tôi mong ngày nào mình cũng dậy lúc bảy giờ, nhưng... haha, đôi khi tôi ngủ đến bảy giờ rưỡi, thậm chí tám giờ.",
    22: "Ồ? Ngủ đến tám giờ à? Vậy có kịp giờ làm không?",
    23: "Thế nên tôi rất vội! Sau khi thức dậy, tôi phải nhanh chóng rửa mặt, đánh răng, rồi tìm quần áo để mặc.",
    24: "Tôi thường không có thời gian ăn sáng.",
    25: "Không ăn sáng không tốt cho sức khỏe lắm đâu.",
    26: "Tôi biết, tôi biết. Vì vậy trên đường đến công ty, tôi thường mua chút gì đó để ăn, chẳng hạn một cái bánh bao hoặc một cốc sữa đậu nành.",
    27: "Còn bạn thì sao, Lý Minh? Nhìn bạn là biết kiểu người dậy rất sớm.",
    28: "Haha, bạn đoán đúng rồi. Tôi khá quen với việc dậy sớm. Bình thường sáu giờ rưỡi sáng tôi đã thức dậy.",
    29: "Sáu giờ rưỡi? Sớm thế! Sau khi thức dậy bạn làm gì?",
    30: "Tôi sẽ uống một cốc nước trước, sau đó tập vài động tác đơn giản ở nhà, khoảng hai mươi phút.",

    31: "Sau khi tập thể dục, cơ thể sẽ rất dễ chịu và cả ngày đều tràn đầy năng lượng.",
    32: "Ôi, lành mạnh thật đấy! Tôi rất muốn học theo bạn, nhưng buổi sáng tôi thật sự không dậy nổi.",
    33: "Vậy bạn tự làm bữa sáng à?",
    34: "Đúng vậy, bữa sáng của tôi rất đơn giản.",
    35: "Bình thường là một quả trứng, một cốc sữa, thêm một lát bánh mì.",
    36: "Chuẩn bị rất nhanh, chỉ năm phút là xong.",
    37: "Hay thật. Ăn sáng xong, các bạn đến công ty bằng cách nào?",
    38: "Tôi lái xe đi làm. Nhà tôi hơi xa công ty, lái xe mất khoảng bốn mươi phút. Còn bạn?",
    39: "Tôi đi tàu điện ngầm. Ngay dưới tòa nhà tôi ở có ga tàu điện ngầm, rất tiện.",
    40: "Nhưng buổi sáng rất đông người, trong tàu điện ngầm đặc biệt chen chúc.",

    41: "Đúng vậy, tàu điện ngầm ở Bắc Kinh sáng và tối đều rất đông người. Đường đi làm cũng khá vất vả.",
    42: "Đúng thế, sáng nào cũng giống như một 'trận chiến'.",
    43: "Đến công ty, tôi thường cảm thấy mình đã hơi mệt rồi.",
    44: "Haha, có thể hiểu được. Vậy có lẽ khoảng thời gian dài nhất trong ngày của chúng ta là làm việc ở công ty.",
    45: "Buổi sáng bạn thường làm những gì?",
    46: "Công việc của tôi cần sử dụng máy tính.",
    47: "Vì vậy khi đến công ty, việc đầu tiên tôi làm là bật máy tính lên rồi bắt đầu làm việc.",
    48: "Tôi phải đọc rất nhiều thứ và cũng phải viết rất nhiều.",
    49: "Đôi khi còn phải họp cùng đồng nghiệp.",
    50: "Công việc của tôi cũng gần giống vậy. Phần lớn thời gian tôi nhìn màn hình máy tính, trả lời email và gọi điện thoại.",

    51: "Thời gian trôi rất nhanh, chớp mắt đã đến buổi trưa.",
    52: "Đúng! Nhắc đến buổi trưa, câu hỏi tôi quan tâm nhất đây rồi: Trưa nay ăn gì?",
    53: "Haha, đây là một câu hỏi quan trọng nhất mỗi ngày. Các bạn ăn trưa thế nào? Ăn ở công ty à?",
    54: "Công ty chúng tôi không có nhà ăn.",
    55: "Vì vậy chúng tôi thường cùng đồng nghiệp đặt đồ ăn giao đến.",
    56: "Bây giờ đặt đồ ăn bằng điện thoại rất tiện, muốn ăn gì cũng được.",
    57: "Đúng vậy, đặt đồ ăn giao đến rất phổ biến.",
    58: "Chúng ta có thể ăn món Trung Quốc, món Nhật Bản và nhiều món của các nước khác.",
    59: "Bạn thích ăn gì?",
    60: "Tôi thích ăn cơm và các món ăn kèm.",

    61: "Ví dụ như trứng xào cà chua, thêm một món cá nữa.",
    62: "Lý Minh, còn bạn? Bạn cũng đặt đồ ăn giao đến à?",
    63: "Đôi khi tôi cũng đặt đồ ăn giao đến.",
    64: "Nhưng dưới công ty chúng tôi có vài quán ăn nhỏ, đồ ăn ngon mà giá cũng không đắt.",
    65: "Vì vậy tôi thích cùng hai, ba đồng nghiệp đến quán ăn hơn.",
    66: "Đến quán ăn cũng tốt, có thể rời văn phòng và nghỉ ngơi một chút.",
    67: "Các bạn thường ăn trong bao lâu?",
    68: "Chúng tôi thường đi ăn lúc mười hai giờ, ăn trong một tiếng và khoảng một giờ chiều thì về công ty.",
    69: "Ăn xong, có người nghỉ ngơi một lát, có người uống một cốc cà phê rồi chuẩn bị cho công việc buổi chiều.",
    70: "Tôi cũng vậy! Buổi chiều tôi nhất định phải uống một cốc cà phê. Không uống cà phê là tôi sẽ buồn ngủ.",

    71: "Haha, nhiều người đều như vậy. Thời gian làm việc buổi chiều cũng gần giống buổi sáng, nhưng cảm giác sẽ mệt hơn một chút.",
    72: "Đợi đến năm giờ rưỡi, sáu giờ chiều, cuối cùng cũng được tan làm về nhà!",
    73: "Đúng vậy! Lúc tan làm là vui nhất!",
    74: "Sau khi tan làm, bạn thường làm gì? Có về nhà ngay không?",
    75: "Ừm, phần lớn thời gian tôi về nhà thẳng. Vì làm việc cả ngày đã rất mệt nên muốn về nhà nghỉ ngơi thật nhanh.",
    76: "Trên đường về nhà, tôi thích nghe nhạc hoặc nghe podcast 'Tiếng Trung mỗi ngày' của chúng ta.",
    77: "Haha, cảm ơn bạn đã ủng hộ.",
    78: "Vậy bạn giải quyết bữa tối thế nào?",
    79: "Nếu tôi về nhà sớm, mẹ sẽ nấu xong bữa tối và đợi tôi.",
    80: "Tôi rất thích ăn những món mẹ nấu. Nếu về nhà muộn, tôi sẽ tự làm một ít mì đơn giản để ăn.",

    81: "Ăn tối cùng gia đình thật là một cảm giác tuyệt vời.",
    82: "Đúng vậy. Còn bạn? Sau khi tan làm bạn làm gì?",
    83: "Sau khi tan làm, nếu không mệt, đôi khi tôi sẽ đến phòng tập thể hình để tập một tiếng.",
    84: "Ôi! Bạn tập thể dục buổi sáng, tối tan làm lại còn tập nữa. Bạn giỏi quá!",
    85: "Haha, chỉ là một thói quen thôi. Tập xong về nhà cảm thấy rất thư giãn.",
    86: "Bữa tối tôi thường tự nấu, nấu khá đơn giản và ăn ít hơn một chút.",
    87: "Được rồi. Vậy sau bữa tối cho đến trước khi ngủ, trong khoảng thời gian đó các bạn thường làm gì?",
    88: "Có lẽ đây là khoảng thời gian thư giãn nhất trong ngày của tôi.",
    89: "Tất nhiên rồi! Tôi sẽ ngồi trên ghế sofa, xem tivi hoặc lướt Douyin bằng điện thoại, xem hôm nay bạn bè đã làm những gì.",
    90: "Đôi khi tôi cũng trò chuyện với bạn bè qua WeChat.",

    91: "Ừm, nghe rất thư giãn. Buổi tối tôi không thích xem điện thoại lắm, vì đã nhìn máy tính cả ngày nên mắt rất mỏi. Tôi thích đọc sách.",
    92: "Đọc sách à? Đúng là một thói quen tốt. Bạn thường đọc sách gì?",
    93: "Tôi đọc nhiều loại sách. Đôi khi đọc lịch sử Trung Quốc, đôi khi cũng đọc tiểu thuyết.",
    94: "Đọc sách giúp tôi học được nhiều điều mới và cũng khiến tâm trí bình yên hơn.",
    95: "Hay thật. Thật ra tôi cũng mua rất nhiều sách nhưng hiếm khi có thời gian đọc. Chúng đều đang nằm ngủ trong phòng tôi đấy.",
    96: "Haha, mỗi ngày có thể đọc một chút, chẳng hạn đọc mười trang.",
    97: "Được rồi, câu hỏi cuối cùng nhé. Mỗi tối bạn đi ngủ lúc mấy giờ?",
    98: "Tôi luôn tự nhủ phải ngủ sớm. Nhưng tôi thường mải xem tivi hoặc chơi điện thoại rồi quên mất thời gian.",
    99: "Bình thường phải đến mười một giờ rưỡi, đôi khi thậm chí mười hai giờ tôi mới đi ngủ.",
    100: "Như vậy sáng hôm sau sẽ rất buồn ngủ đúng không?",

    101: "Đúng vậy! Vì thế buổi sáng tôi không dậy nổi. Chắc chắn bạn ngủ rất sớm nhỉ?",
    102: "Đúng, để hôm sau có tinh thần tốt, bình thường mười giờ rưỡi tôi đã chuẩn bị đi ngủ.",
    103: "Tôi sẽ nằm trên giường nghe nhạc một lát, sau đó nhất định đi ngủ trước mười một giờ.",
    104: "Được, bắt đầu từ ngày mai tôi cũng sẽ đi ngủ trước mười một giờ!",
    105: "Haha, hy vọng bạn làm được.",
    106: "Được rồi, cũng gần hết giờ rồi.",
    107: "Hôm nay chúng ta đã trò chuyện về một ngày của mỗi người, từ lúc thức dậy buổi sáng đến lúc đi ngủ buổi tối.",
    108: "Đúng vậy, nghe có vẻ một ngày của chúng ta rất khác nhau.",
    109: "Lý Minh, lối sống của bạn rất lành mạnh và điều độ.",
    110: "Còn tôi thì hơi lộn xộn một chút, haha.",

    111: "Không đâu, không đâu. Lối sống của mỗi người đều khác nhau.",
    112: "Điều quan trọng là chúng ta có thể tìm thấy niềm vui của riêng mình trong một ngày bận rộn.",
    113: "Có thể là một bữa trưa ngon miệng, một khoảng thời gian trò chuyện cùng bạn bè hoặc một cuốn sách hay.",
    114: "Bạn nói đúng. Các bạn thính giả thân mến, một ngày của các bạn diễn ra như thế nào?",
    115: "Buổi sáng bạn thức dậy lúc mấy giờ? Buổi tối bạn thích làm gì?",
    116: "Mời mọi người để lại bình luận và dùng tiếng Trung chia sẻ một ngày của mình với chúng tôi.",
    117: "Chúng tôi rất mong được xem những chia sẻ của các bạn.",
    118: "Được rồi, số 'Tiếng Trung mỗi ngày' hôm nay đến đây thôi. Cảm ơn mọi người đã lắng nghe.",
    119: "Hẹn gặp lại mọi người ở số tiếp theo!",
    120: "Tạm biệt!",
    121: "Bye bye!"
}


# ==================================================
# 3. TAO PINYIN
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
            "YouTube ID khong khop video 5."
        )

    original = data.get("sentences")

    if not isinstance(original, list):
        raise ValueError(
            "Khong tim thay danh sach sentences."
        )

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can 121 doan, nhung co {len(original)}."
        )

    if set(TRANSLATIONS) != set(
        range(1, EXPECTED_COUNT + 1)
    ):
        raise ValueError(
            "Ban dich thieu hoac trung so thu tu."
        )

    result = []
    short_segments = []
    previous_end = 0.0

    for i, item in enumerate(original, 1):
        start = round(float(item["start"]), 3)
        end = round(float(item["end"]), 3)

        # Giu nguyen chu Han goc.
        hanzi = str(item["hanzi"]).strip()
        vi = TRANSLATIONS[i].strip()

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
                f"Timestamp chong o doan {i}."
            )

        duration = round(end - start, 3)

        if duration < 0.8:
            short_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        result.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": make_pinyin(hanzi),
            "vi": vi
        })

        previous_end = end

    # Khong ghi de file phu de goc.
    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": result
    }

    OUTPUT.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    report_lines = [
        "SHADOWING HSK2 - VIDEO 5",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(result)}",
        "",
        "DOAN NGAN HON 0.8 GIAY:"
    ]

    for item in short_segments:
        report_lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    report_lines.extend([
        "",
        "Luu y:",
        "- Ban dich duoc bien soan tu transcript.",
        "- Pinyin duoc tao tu dong, can ra soat tu da am.",
        "- Chua doi chieu tat ca cau voi am thanh.",
        "- Chua cap nhat SQL Server."
    ])

    REPORT.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    # Doc lai JSON
    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    assert saved["youtube_id"] == VIDEO_ID
    assert len(saved["sentences"]) == EXPECTED_COUNT

    assert all(
        s["hanzi"] and s["pinyin"] and s["vi"]
        for s in saved["sentences"]
    )

    print("===== VIDEO 5 - PINYIN VA BAN DICH =====")
    print("YouTube ID:", VIDEO_ID)
    print("So doan:", len(result))
    print("So ban dich:", len(TRANSLATIONS))
    print("So doan ngan < 0.8s:", len(short_segments))

    print("\n===== 5 DOAN DAU =====")

    for i, item in enumerate(result[:5], 1):
        print(f"\n{i:03d} [{item['start']:.2f} - "
              f"{item['end']:.2f}]")
        print("Han:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("VI:", item["vi"])

    print("\n===== FILE =====")
    print("JSON:", OUTPUT)
    print("Bao cao:", REPORT)

    print("\nKIEM TRA CAU TRUC JSON: OK")
    print("CHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
