
import json
from pathlib import Path

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk4")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video3_with_pinyin.json"
OUTPUT = DATA / "video3_translated_full.json"
REPORT = DATA / "video3_translation_report.txt"

VIDEO_ID = "KIMnS86vgPE"
EXPECTED_COUNT = 312

# Moi dong tuong ung mot doan phu de,
# theo thu tu tu 001 den 312.

TRANSLATIONS = """
Hôm nay tôi muốn trò chuyện với bạn về một cuốn sách.
Hay nói đúng hơn,
tôi muốn nói về một vấn đề khiến rất nhiều người băn khoăn.
Bạn đã từng trải qua chuyện như thế này chưa?
Đã đọc cuốn Bí mật,
đã tìm hiểu về luật hấp dẫn,
ngày nào cũng gửi điều ước đến vũ trụ.
Tôi muốn có nhiều tiền hơn.
Tôi muốn có những mối quan hệ tốt đẹp hơn.
Tôi muốn có cuộc sống lý tưởng hơn.
Bạn cố gắng nghĩ về điều đó,
khao khát nó mãnh liệt.
Nhưng kết quả là tiền bạn muốn vẫn không đến.
Người bạn mong đợi cũng chẳng xuất hiện.
Ngược lại, bạn ngày càng lo lắng.
Thậm chí bắt đầu nghi ngờ,
có phải số mình không tốt?
Hay luật hấp dẫn vốn chỉ là một trò lừa bịp?
Trước đây tôi cũng từng như vậy.
Cho đến khi tôi gặp cuốn sách này.
Cuốn Thu hút phép màu của chính mình của tác giả Lư Dịch Lâm.
Trong quá trình thu âm cuốn sách,
tôi có một cảm nhận vô cùng sâu sắc.
Không phải luật hấp dẫn không có tác dụng,
mà là phần lớn chúng ta đã áp dụng sai cách.
Những nội dung về luật hấp dẫn trên thị trường
đa phần chỉ dạy bạn ba việc: yêu cầu,
tin tưởng và đón nhận.
Nói đơn giản là,
bạn cứ nghĩ thật mạnh mẽ,
rồi vũ trụ sẽ trao cho bạn.
Nhưng bạn có nhận ra không?
Khi bạn đặc biệt khao khát một điều gì đó,
bản thân sự khao khát ấy
thực ra mang theo một cảm giác rất tinh tế.
Đó là cảm giác mình chưa có được điều ấy.
Bạn không có tiền,
nên bạn khao khát tiền; bạn thiếu tình yêu,
nên bạn khao khát tình yêu.
Nhưng theo cách lý giải này, cảm giác thiếu thốn ấy
lại thu hút đến
chính những điều khiến bạn tiếp tục cảm thấy thiếu thốn.
Đó là lý do nhiều người càng học
luật hấp dẫn lại càng lo lắng.
Bởi vì sự chú ý của bạn chỉ tập trung vào điều mình thiếu,
chứ không phải những gì mình đang có.
Và cuốn sách của tác giả Lư Dịch Lâm
có một điểm khiến tôi ấn tượng nhất.
Sách không chỉ cho bạn biết phải làm thế nào,
mà còn chỉ cách điều chỉnh khi làm sai.
Sách không chỉ nói luật hấp dẫn hoạt động ra sao,
mà còn giải thích nếu nó không hiệu quả,
nguyên nhân nằm ở đâu,
và phải giải quyết như thế nào.
Hôm nay,
tôi sẽ chia sẻ với bạn những nội dung cốt lõi của cuốn sách.
Trước tiên, chúng ta hãy nói về
ba nguyên tắc đã thay đổi nhận thức của tôi nhiều nhất.
Nguyên tắc đầu tiên:
Hãy có một mong muốn mà không quá bám víu vào mong muốn ấy.
Nghe có vẻ mâu thuẫn phải không? Mong muốn mà không quá ham muốn?
Rốt cuộc điều đó có nghĩa là gì?
Tác giả giải thích trong sách rằng,
khi chúng ta tập trung quá mức vào điều mình muốn
đạt được,
nội tâm sẽ trở nên căng thẳng.
Ẩn sau sự căng thẳng ấy
là sự cố chấp của cái tôi và cảm giác thiếu thốn.
Bạn quá muốn làm tốt bài thi này,
kết quả là lúc thi lại lo âu, căng thẳng,
lòng bàn tay đổ mồ hôi,
đầu óc hoàn toàn trống rỗng.
Bạn quá muốn có được một người,
kết quả khi ở bên nhau lại luôn lo được lo mất,
vô tình càng đẩy người ấy ra xa.
Vì vậy, theo cuốn sách, điều quan trọng của luật hấp dẫn
không nằm ở ham muốn mãnh liệt,
mà là đặt ra cho mình một mục tiêu,
nhưng đừng đặt quá nhiều kỳ vọng vào nó.
Càng thư giãn, bạn càng dễ đạt được điều mình muốn.
Nguyên tắc thứ hai:
Bạn phải trở thành phiên bản con người ấy trước,
rồi mới có thể đạt được điều mình mong muốn.
Điều này tôi rất đồng cảm.
Cuốn sách nói rằng nếu bạn muốn trở thành người giàu,
thì trước tiên bạn cần khiến bản thân
có tâm thế của một người giàu.
Không có nghĩa là bạn phải tiêu tiền phung phí,
mà là cảm giác thoải mái và tự tin khi sử dụng tiền.
Đó là trạng thái không quá lo lắng về tiền bạc,
không luôn cảm thấy thiếu thốn.
Khi bạn đưa mình vào trạng thái ấy trước,
theo tác giả, bạn mới có thể thu hút sự giàu có.
Giống như khi bạn thích một người.
Nếu cả ngày bạn đều nghĩ mình không xứng đáng,
người ấy làm sao có thể thích mình?
Thì điều bạn thể hiện ra chính là sự tự ti.
Đối phương có thể cảm nhận được điều đó.
Nhưng nếu
trước tiên bạn trở thành người biết trân trọng giá trị của mình,
biết yêu thương bản thân,
thì sự tự tin và bình tĩnh ấy
có thể khiến đối phương muốn đến gần bạn hơn.
Nguyên tắc thứ ba:
Khi bạn không còn quá khao khát điều đó,
bạn lại có thể đạt được nó.
Đây là điều tôi đã suy ngẫm rất nhiều khi thu âm sách.
Trước đây tôi rất muốn bài viết được đăng.
Ngày nào cũng nhìn chằm chằm vào hộp thư,
lo lắng về các con số.
Kết quả là mãi vẫn không được đăng.
Sau đó tôi dần nghĩ thoáng hơn,
tập trung viết thật tốt những điều mình muốn viết,
không còn quá bận tâm đến kết quả.
Không ngờ tôi lại có được
cơ hội đăng bài. Tác giả Lư Dịch Lâm nói rằng,
khi bạn không còn cố chấp khao khát một điều gì đó,
điều ấy lại dễ dàng tự tìm đến bạn.
Bởi vì bạn đã buông bỏ sự cố chấp,
cảm giác thiếu thốn cũng biến mất.
Cuối cùng bạn có được tâm thế của người đã sở hữu điều đó.
Ba nguyên tắc này là nền tảng của cuốn sách.
Chỉ khi nắm vững chúng,
bạn mới có thể loại bỏ những rào cản tâm lý.
Khi ấy, việc vận dụng luật hấp dẫn
mới trở nên thuận lợi hơn.
Được rồi, chúng ta đã có các nguyên tắc.
Tiếp theo là phần thực hành.
Luật hấp dẫn truyền thống
nói đến ba bước: yêu cầu, tin tưởng
và đón nhận.
Nhưng điểm đặc biệt của cuốn sách này
là ngoài ba bước ấy,
tác giả còn bổ sung bước thứ tư:
giải tỏa cảm xúc do ham muốn gây ra và buông bỏ chính ham muốn ấy.
Chúng ta hãy cùng đi qua đầy đủ bốn bước.
Bước đầu tiên: yêu cầu.
Hãy gửi mong muốn của bạn đi,
giống như đặt một đơn hàng.
Bạn muốn điều gì?
Bao nhiêu tiền? Một mối quan hệ như thế nào?
Càng rõ ràng càng tốt.
Bước thứ hai: tin tưởng.
Tin rằng mục tiêu ấy chắc chắn có thể đạt được.
Tin rằng những điều bạn muốn đang dần diễn ra.
Tin rằng mọi sức mạnh trong vũ trụ đang đáp lại bạn.
Bước thứ ba: đón nhận.
Hãy điều chỉnh bản thân theo trạng thái của tương lai.
Đưa mình vào một trạng thái
phù hợp với điều mà bạn đang mong muốn.
Ba bước này đã được nhiều cuốn sách nhắc đến.
Nhưng điều quan trọng là bước thứ tư.
Bước thứ tư:
giải tỏa cảm xúc do ham muốn gây ra và buông bỏ chính ham muốn ấy.
Điều đó nghĩa là gì?
Tức là sau khi bạn đã gửi đi mong muốn,
bạn cần tự kiểm tra
mình có cảm giác gì về mục tiêu này.
Bạn cảm thấy thoải mái hay lo lắng?
Bạn thấy chắc chắn hay còn nghi ngờ?
Bạn có cảm giác mình thực sự không xứng đáng không?
Bạn có nghi ngờ liệu điều này có thành công không?
Những cảm xúc tiêu cực ấy
được cuốn sách xem là rào cản khiến luật hấp dẫn không hiệu quả.
Bạn cần từng bước giải tỏa chúng.
Trong sách có giới thiệu một phương pháp
gọi là phương pháp giải tỏa ba tầng.
Tôi sẽ diễn giải lại bằng lời của mình.
Ví dụ, mục tiêu năm nay của bạn là kiếm một triệu nhân dân tệ.
Sau khi đặt ra mục tiêu,
trước tiên bạn hãy cảm nhận
những phản ứng trong cơ thể và tâm trí mình.
Nếu bạn cảm thấy tốt,
thì rất tốt. Nhưng nếu bạn thấy lo lắng,
nghi ngờ hoặc căng thẳng,
thì bạn cần giải tỏa những cảm xúc đó.
Đây là tầng thứ nhất:
cảm xúc đối với chính mục tiêu.
Sau đó đến tầng thứ hai:
cảm xúc của bạn đối với những cảm xúc ấy.
Bạn hãy tự hỏi,
mình cảm thấy thế nào về sự lo lắng vừa rồi?
Có cảm thấy bất lực không?
Hay cảm thấy bản thân thật đáng chê cười?
Hãy tiếp tục giải tỏa những cảm giác ấy.
Tầng thứ ba
là cách bạn nhìn nhận bản thân đằng sau những cảm xúc đó.
Hãy tự hỏi: khi rơi vào những cảm xúc ấy,
mình nghĩ mình là người như thế nào?
Một kẻ thất bại?
Một người không có năng lực?
Hãy buông bỏ cả những nhãn dán ấy.
Từng tầng một,
cho đến khi nội tâm bạn thực sự bình tĩnh lại,
thực sự có được niềm tin vững vàng.
Phần tiếp theo
là điều tôi cho rằng quý giá nhất trong cuốn sách.
Nếu luật hấp dẫn không phát huy tác dụng,
làm sao tìm được nguyên nhân?
Và giải quyết như thế nào?
Tác giả Lư Dịch Lâm đưa ra trong sách rằng,
có ba loại sức mạnh ảnh hưởng đến luật hấp dẫn:
sức mạnh tích cực,
sức mạnh tiêu cực và sức mạnh chưa biết.
Trong đó, sức mạnh tiêu cực thường xuất phát từ tiềm thức.
Tôi sẽ kể cho bạn vài trở ngại thường gặp nhất.
Bạn thử xem mình có gặp phải không nhé.
Trở ngại đầu tiên:
cảm giác mình không xứng đáng.
Miệng nói muốn kiếm một triệu,
nhưng trong lòng lại nghĩ: Dựa vào đâu? Người như mình có xứng không?
Tiếng nói ấy giống như tiềm thức đang kéo phanh tay.
Bạn vừa đạp ga vừa kéo phanh,
mọi năng lượng đều tiêu hao vào sự giằng co nội tâm.
Vậy làm sao có thể tiến lên?
Trong sách có phương pháp riêng
giúp bạn giải tỏa cảm giác không đủ tư cách và không xứng đáng.
Trở ngại thứ hai:
những niềm tin giới hạn từ gia đình thời thơ ấu.
Bạn có nhận ra không?
Rất nhiều quan điểm của chúng ta về tiền bạc
và các mối quan hệ
thực ra được tiếp nhận từ cha mẹ.
Từ nhỏ, cha mẹ đã nói với bạn rằng kiếm tiền rất khó.
Cuộc sống vất vả, nhà mình không có số giàu sang.
Bề ngoài bạn có thể không tin,
nhưng sâu trong tiềm thức,
bạn đã tin điều đó từ lâu.
Cảm giác thiếu thốn được truyền lại trong gia đình
cũng có thể trở thành điều hạn chế bạn.
Trở ngại thứ ba:
năng lượng của bạn đã bị tiêu hao.
Điều này rất thực tế.
Mỗi ngày bạn lướt video ngắn hai tiếng,
xem đủ loại tin tức khiến mình lo lắng,
trò chuyện với những người luôn tiêu cực.
Năng lượng của bạn đã cạn kiệt từ lâu.
Làm sao còn sức để đón nhận những điều tốt đẹp?
Trong sách có riêng một phần
nói về những điều có thể cản trở luật hấp dẫn.
Tác giả nhắc bạn chú ý đến những hao tổn hằng ngày.
Nếu không giải quyết những trở ngại này,
bạn có gửi bao nhiêu điều ước cũng vô ích.
Giống như trồng hoa vậy.
Bạn chỉ chăm chăm tưới nước,
nhưng trong đất lại có sâu bọ,
có mầm bệnh, rễ cây đã mục nát,
thì làm sao hoa có thể nở?
Ngoài lý thuyết và phương pháp,
cuốn sách còn đưa ra nhiều
bài tập có thể thực hành ngay.
Chẳng hạn, mỗi ngày viết ba điều biết ơn.
Biết ơn món ăn ngon được thưởng thức hôm nay.
Biết ơn nụ cười gặp trên đường.
Biết ơn đồ ăn giao đến không bị đổ.
Cuốn sách cho rằng lòng biết ơn mang nguồn năng lượng tích cực rất cao.
Khi bắt đầu biết ơn,
bạn có cảm giác mình đang sở hữu những điều tốt đẹp,
thay vì luôn cảm thấy thiếu thốn.
Chẳng hạn, dành năm phút tưởng tượng trước khi ngủ.
Nhắm mắt lại,
tưởng tượng bạn đã có cuộc sống lý tưởng.
Bạn đang sống trong ngôi nhà như thế nào?
Trong phòng có mùi hương gì?
Bạn đang mặc bộ quần áo ra sao?
Bạn đang ở bên ai?
Theo lời người kể, não bộ khó phân biệt tưởng tượng với thực tế.
Khi bạn tưởng tượng đủ lâu,
nó sẽ giúp bạn biến điều đó thành hiện thực.
Ngoài ra còn có bài thiền riêng về sự giàu có.
Tên bài là Tôi yêu tiền bạc,
tiền bạc yêu tôi.
Khi thu âm đoạn này,
chính tôi cũng cảm thấy rất ấm áp.
Cảm giác xây dựng mối quan hệ thân thiện với tiền bạc
thực sự rất kỳ diệu.
Trong sách còn có một phần
chuyên nói về việc thu hút mối quan hệ tình cảm thân thiết.
Tác giả Lư Dịch Lâm nói rằng,
nhiều người không tìm được người bạn đời lý tưởng
vì trong lòng họ tồn tại một đối thủ tưởng tượng.
Hoặc họ nghĩ người khác giới đều không đáng tin,
hoặc cho rằng những người đàn ông tốt
và phụ nữ tốt đều đã có người yêu.
Những định kiến có sẵn ấy
chính là trở ngại lớn nhất.
Sau khi thu âm xong toàn bộ cuốn sách,
cảm nhận lớn nhất của tôi là:
luật hấp dẫn không phải một chiếc giếng ước.
Mà là hành trình trở thành con người bạn mong muốn.
Tác giả Trương Đức Phân viết lời tựa cho cuốn sách.
Bà có một câu nói mà tôi rất thích:
Bạn không thể đi qua một quá trình không có niềm vui
để đến được một đích đến tràn đầy niềm vui.
Những khuôn mẫu tính cách và niềm tin cũ
là trở ngại quan trọng khiến mong muốn khó thành hiện thực.
Khi bạn chuyển từ Tôi muốn sang Tôi chính là,
từ tìm kiếm bên ngoài sang điều chỉnh bên trong,
bạn sẽ nhận ra
những điều kỳ diệu đang âm thầm đến gần.
Tôi đã thu âm cuốn sách này thành một tuyển tập sách nói,
và phát hành trên nền tảng Himalaya.
Nếu bạn cũng muốn thực sự học cách áp dụng
luật hấp dẫn,
muốn biết phải tìm nguyên nhân thế nào khi không hiệu quả,
hãy đăng ký theo dõi tuyển tập của tôi.
Hãy để giọng nói của tôi đồng hành cùng bạn,
trở thành người có thể thu hút những điều kỳ diệu.
Mỗi suy nghĩ của bạn ngay lúc này
đều đang góp phần tạo nên tương lai.
Khi bạn bắt đầu tin vào những điều kỳ diệu,
bạn đã đứng ở điểm khởi đầu của chúng.
""".strip().splitlines()


def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if data.get("module") != "shadowing":
        raise ValueError("Sai module.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID.")

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError("Khong co sentences.")

    if len(sentences) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(sentences)}."
        )

    if len(TRANSLATIONS) != EXPECTED_COUNT:
        raise ValueError(
            f"So ban dich: {len(TRANSLATIONS)}. "
            f"Can dung {EXPECTED_COUNT}.\n"
            "Chua ghi file. Kiem tra lai "
            "so dong trong TRANSLATIONS."
        )

    result = []

    for i, (item, vi) in enumerate(
        zip(sentences, TRANSLATIONS), 1
    ):

        vi = vi.strip()

        if not vi:
            raise ValueError(
                f"Thieu ban dich doan {i}."
            )

        for field in ("hanzi", "pinyin"):
            if not str(item.get(field, "")).strip():
                raise ValueError(
                    f"Doan {i} thieu {field}."
                )

        start = float(item["start"])
        end = float(item["end"])

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}."
            )

        result.append({
            "start": start,
            "end": end,
            "hanzi": item["hanzi"],
            "pinyin": item["pinyin"],
            "vi": vi
        })

    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": result
    }

    OUTPUT.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2,
            allow_nan=False
        ),
        encoding="utf-8"
    )

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if saved != document:
        raise RuntimeError(
            "Du lieu doc lai khong khop."
        )

    report = [
        "SHADOWING HSK4 - VIDEO 3",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(result)}",
        f"Da dich: {len(result)}",
        "JSON: OK",
        "",
        "Can nghe ra soat phu de nhan dang sai.",
        "Chua cap nhat SQL Server."
    ]

    REPORT.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print(
        "===== HSK4 VIDEO 3 - DICH TIENG VIET ====="
    )
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(result))
    print("Da dich:", len(result))

    print("\n===== 5 DOAN DAU =====")

    for i, item in enumerate(result[:5], 1):

        print(f"\n{i:03d}")
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
