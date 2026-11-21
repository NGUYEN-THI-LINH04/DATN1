
import json
import math
from pathlib import Path


# ==================================================
# 1. CAU HINH HSK4 - VIDEO 4
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk4")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video4_with_pinyin.json"
OUTPUT = DATA / "video4_translated_full.json"
REPORT = DATA / "video4_translation_report.txt"

VIDEO_ID = "xdULRJN_RZM"
MA_BAI_HOC = 2050
EXPECTED_COUNT = 233


# ==================================================
# 2. BAN DICH TIENG VIET - 233 DOAN
# Dinh dang: STT|Ban dich
# ==================================================

TRANSLATION_TEXT = """
001|Xin chào mọi người, chào mừng đến với số mới của chương trình "Tiếng Trung mỗi ngày".
002|Tôi là Lý Minh.
003|Xin chào mọi người, tôi là Vương Vũ.
004|Sau khi chương trình kỳ trước được phát sóng,
005|chúng tôi đã nhận được rất nhiều bình luận của các bạn.
006|Đọc những bình luận ấy, chúng tôi thực sự rất vui!
007|Đúng vậy, vô cùng cảm ơn mọi người đã ủng hộ.
008|Tôi nhận thấy nhiều bạn đã chia sẻ thói quen uống trà
009|hoặc uống cà phê của mình.
010|Trong đó có một bình luận khiến tôi đặc biệt ấn tượng.
011|Ồ? Là bình luận nào vậy?
012|Đúng thế, tôi thấy một bình luận khiến mình rất ấn tượng.
013|Có một bạn đã dùng tiếng Trung để chia sẻ thói quen của mình.
014|Bạn ấy nói: "Mỗi sáng tôi thích uống một tách cà phê,
015|sau bữa trưa tôi cùng gia đình uống trà đen."
016|Ồ, thói quen sinh hoạt này nghe hay thật đấy!
017|Buổi sáng bắt đầu ngày mới bằng cà phê,
018|buổi chiều cùng gia đình tận hưởng thời gian thư thái bên tách trà.
019|Đúng vậy.
020|Khi đọc bình luận đó,
021|tôi chợt nảy ra một ý tưởng mới.
022|Bạn xem, buổi sáng uống cà phê một mình để chuẩn bị làm việc và học tập,
023|điều này giống một trạng thái "ở một mình" hơn, đúng không?
024|Ừm, đúng là như vậy.
025|Nhưng buổi chiều cùng gia đình uống trà và trò chuyện,
026|lại trở thành một hoạt động "giao tiếp xã hội" ấm áp.
027|Nghe bạn nói vậy tôi mới nhận ra!
028|Hóa ra đằng sau lựa chọn uống trà hay cà phê
029|còn ẩn chứa vấn đề chúng ta thích ở một mình
030|hay thích ở bên cạnh người khác.
031|Chính xác là như vậy.
032|Vì thế hôm nay, nhân bình luận của bạn ấy,
033|chúng tôi muốn cùng mọi người trò chuyện sâu hơn về chủ đề:
034|Ở một mình hay giao tiếp xã hội?
035|Bạn nghĩ điều nào quan trọng hơn đối với chúng ta?
036|Chủ đề này hay quá!
037|Tôi nghĩ rất nhiều người cảm thấy băn khoăn về vấn đề này.
038|Vậy hôm nay chúng ta hãy cùng trò chuyện thật kỹ nhé!
039|Được rồi, tôi hiểu rồi.
040|Chúng ta sẽ chuyển sang một chủ đề hoàn toàn mới, nhưng vẫn
041|tuân theo tất cả các thông số và cấu trúc mà bạn đã cung cấp,
042|từ chủ đề "Trà và cà phê" của tập trước
043|chuyển tiếp một cách tự nhiên sang đây. Được rồi.
044|Vậy để mọi người hiểu chúng ta hơn,
045|hay trước tiên chúng ta nói về bản thân mình nhé.
046|Vương Vũ, bạn thấy mình là người thích không khí náo nhiệt,
047|hay là người thích sự yên tĩnh?
048|Điều này quá rõ rồi!
049|Tôi chắc chắn là người thích náo nhiệt.
050|Tôi đặc biệt thích cảm giác được ở cùng một nhóm bạn đông người,
051|mọi người cùng ăn uống, trò chuyện, ca hát,
052|cảm thấy vô cùng tràn đầy sức sống.
053|Dùng một từ đang thịnh hành để nói,
054|có lẽ tôi là người "hướng ngoại".
055|Hướng ngoại.
056|Ừm, từ này rất chính xác.
057|Nghĩa là bạn nhận được năng lượng thông qua giao tiếp với người khác.
058|Đúng, đúng, đúng! Chính là ý đó.
059|Mỗi lần tụ tập với bạn bè xong, tôi đều cảm thấy rất vui,
060|cảm giác như mình lại được "sạc đầy pin".
061|Còn bạn thì sao, Lý Minh?
062|Trông bạn lúc nào cũng rất bình tĩnh và điềm đạm.
063|[Cười] Bạn quan sát rất chính xác.
064|Có lẽ tôi hoàn toàn ngược lại với bạn.
065|Tôi thích sự yên tĩnh hơn.
066|Dùng từ vừa rồi để nói,
067|tôi là một người khá "hướng nội".
068|Không phải tôi không thích ở cùng bạn bè,
069|nhưng tôi thích những buổi gặp mặt ít người hơn,
070|chẳng hạn chỉ hai hoặc ba người,
071|tìm một nơi yên tĩnh rồi trò chuyện sâu với nhau.
072|Ồ, trò chuyện sâu với nhau.
073|Đúng vậy.
074|Nếu tham gia một bữa tiệc có rất đông người,
075|xung quanh ai cũng đang nói chuyện, tôi sẽ cảm thấy rất mệt,
076|cảm giác năng lượng của mình nhanh chóng cạn kiệt.
077|Vì thế đối với tôi, việc ở một mình,
078|chẳng hạn ở nhà một mình đọc sách hoặc xem phim,
079|chính là cách giúp tôi "sạc lại năng lượng".
080|Ra là vậy!
081|Một người nạp năng lượng bằng giao tiếp, một người nạp năng lượng bằng ở một mình.
082|Điều này thú vị thật đấy.
083|Điều đó khiến tôi nghĩ đến phương tiện giao tiếp phổ biến nhất hiện nay: điện thoại.
084|Bạn nghĩ việc giao tiếp qua điện thoại
085|có được xem là giao tiếp xã hội thật sự không?
086|Đây chính là điều tôi muốn thảo luận tiếp theo.
087|Điện thoại và Internet đã thay đổi hoàn toàn cách chúng ta giao tiếp.
088|Đúng vậy!
089|Bây giờ chúng ta có WeChat,
090|có thể nhắn tin, gọi điện cho bạn bè mọi lúc mọi nơi.
091|Đúng là tiện lợi hơn rất nhiều, nhưng tôi luôn cảm thấy
092|dường như vẫn thiếu một điều gì đó.
093|Thiếu điều gì?
094|Bạn nói cụ thể hơn xem nào.
095|Thiếu sự "ấm áp".
096|Khi trò chuyện qua điện thoại, bạn không nhìn thấy nét mặt đối phương,
097|cũng không nghe được ngữ điệu khi họ nói.
098|Đôi khi cùng một câu nói, nhưng được nói bằng ngữ điệu khác nhau,
099|thì ý nghĩa có thể hoàn toàn khác nhau.
100|Tôi đồng ý.
101|Chữ viết đôi khi thực sự dễ gây hiểu lầm. Đúng vậy!
102|Tôi từng có một trải nghiệm như thế.
103|Tôi nhắn tin cho một người bạn, đùa với bạn ấy một câu.
104|Kết quả là có lẽ bạn ấy tưởng tôi đang rất tức giận,
105|nên suốt một thời gian dài không trả lời tin nhắn.
106|Sau đó chúng tôi gọi điện giải thích rõ ràng mới phát hiện đó chỉ là hiểu lầm.
107|Nếu nói trực tiếp khi gặp nhau thì chắc chắn sẽ không có vấn đề như vậy.
108|Tôi hiểu.
109|Nhưng giao tiếp trực tuyến cũng có ưu điểm của nó, đúng không?
110|Ví dụ có những người bạn ở thành phố rất xa,
111|chúng ta không thể thường xuyên gặp mặt.
112|Thông qua Internet, chúng ta có thể giữ liên lạc,
113|chia sẻ cuộc sống của nhau.
114|Điều đó thì đúng thật.
115|Trong danh sách bạn bè của tôi có nhiều bạn học cũ đã nhiều năm chưa gặp,
116|thấy họ bây giờ sống tốt, tôi cũng rất vui.
117|Hơn nữa, tôi cảm thấy giao tiếp trực tuyến mang lại cho người hướng nội như tôi
118|một không gian rất tốt.
119|Đôi khi những điều không biết nói thế nào khi gặp trực tiếp
120|lại có thể dễ dàng bày tỏ bằng cách gõ chữ.
121|Đối với tôi, điều này giúp giảm áp lực rất nhiều.
122|Ừm, bạn nói cũng có lý.
123|Hơn nữa, bây giờ "sticker và ảnh biểu cảm" trên WeChat rất phổ biến.
124|Mọi người dùng đủ loại hình ảnh thú vị để thể hiện tâm trạng,
125|cũng giúp cuộc trò chuyện vui vẻ và ấm áp hơn một chút.
126|Đúng vậy, ảnh biểu cảm bây giờ đã trở thành một ngôn ngữ mới.
127|Nhưng nói đến đây, tôi lại nghĩ đến một vấn đề khác.
128|Vì giao tiếp qua mạng quá tiện lợi,
129|liệu nó có khiến chúng ta ngày càng lười hơn,
130|lười ra ngoài gặp những người bạn ngoài đời thực không?
131|Tôi nghĩ là có!
132|Đôi khi vào cuối tuần, bạn bè rủ tôi ra ngoài ăn,
133|nghĩ đến việc phải thay quần áo, đi xe, tôi đã thấy phiền phức,
134|và tự nhủ hay cứ trò chuyện qua mạng là được rồi.
135|Bạn xem, vấn đề nằm ở đó đấy.
136|Chúng ta tiết kiệm được thời gian,
137|nhưng có lẽ cũng đánh mất một vài điều quý giá hơn.
138|Ví dụ khi ăn cùng bạn bè ngoài đời,
139|niềm vui được chia sẻ món ăn với nhau,
140|sự ấm áp khi nhìn thấy nụ cười thật của đối phương.
141|Tôi hoàn toàn đồng ý.
142|Những trải nghiệm chân thực như vậy
143|không một ảnh biểu cảm nào có thể thay thế được.
144|Hơn nữa, dù giao tiếp trực tuyến hay trực tiếp,
145|đôi khi việc giao tiếp cũng mang lại áp lực cho chúng ta.
146|Bạn nghĩ sao?
147|Tất nhiên rồi! Điều này được gọi là "áp lực giao tiếp xã hội".
148|Ví dụ đôi khi tôi làm việc cả ngày, tối đến thực sự rất mệt,
149|chỉ muốn ở một mình thật yên tĩnh.
150|Nhưng nếu lúc đó
151|có bạn bè gọi điện rủ tôi ra ngoài tụ tập,
152|đôi khi tôi không biết phải từ chối thế nào.
153|Tại sao vậy?
154|Tôi sợ rằng nếu mình từ chối,
155|bạn bè sẽ nghĩ tôi không thích họ,
156|hoặc lần sau họ sẽ không rủ tôi nữa.
157|Hơn nữa, khi thấy mọi người đăng ảnh đi chơi cùng nhau lên mạng xã hội,
158|chỉ có mình không tham gia, trong lòng tôi sẽ hơi khó chịu.
159|Tôi rất hiểu cảm giác đó.
160|Dường như chúng ta sợ bị mọi người quên mất,
161|sợ bỏ lỡ những chuyện quan trọng.
162|Đây có lẽ là nỗi phiền muộn chung của nhiều người hiện đại.
163|Đúng vậy, bạn có lúc nào như thế không?
164|Tất nhiên là có. Nhưng sau đó tôi dần nghĩ thông suốt.
165|Tôi cảm thấy năng lượng giao tiếp giống như pin điện thoại.
166|Có những hoạt động giúp sạc pin, khiến bạn vui vẻ;
167|cũng có những hoạt động làm hao pin, khiến bạn mệt mỏi.
168|Bạn cần hiểu rõ hoạt động nào giúp mình nạp năng lượng,
169|và hoạt động nào tiêu hao năng lượng.
170|Ồ!
171|Ví dụ này hay quá!
172|Năng lượng giao tiếp giống như pin điện thoại. Đúng vậy.
173|Vì vậy khi bạn cảm thấy mệt,
174|việc từ chối một hoạt động giao tiếp khiến bạn hao năng lượng
175|thực ra chính là bảo vệ "pin" của bản thân.
176|Những người bạn tốt thật sự sẽ hiểu cho bạn.
177|Điều họ quan tâm là bạn có vui vẻ hay không,
178|chứ không phải bạn có tham gia mọi buổi tụ tập hay không.
179|Bạn nói đúng.
180|Chúng ta nên quan tâm nhiều hơn đến chất lượng giao tiếp thay vì số lượng.
181|Thay vì tham gia mười bữa tiệc nhàm chán, chi bằng cùng một hoặc hai
182|người bạn thân có một cuộc trò chuyện sâu sắc.
183|Hoàn toàn chính xác.
184|Ở một mình cũng như vậy.
185|Ở một mình có chất lượng không phải là tự nhốt mình trong phòng để chơi điện thoại,
186|mà là tận dụng khoảng thời gian đó làm những việc thực sự giúp mình thư giãn
187|và phát triển bản thân, chẳng hạn đọc sách,
188|tập thể dục hoặc học một kỹ năng mới.
189|Đó mới là ý nghĩa thực sự của việc ở một mình.
190|Tôi hiểu rồi.
191|Dù lựa chọn giao tiếp hay ở một mình,
192|điều quan trọng nhất không phải là hình thức, mà là
193|chúng ta có thể tìm được niềm vui và năng lượng thật sự từ đó hay không.
194|Đúng vậy, hãy tìm điểm cân bằng khiến bản thân thoải mái nhất.
195|Được rồi, hôm nay chúng ta đã xoay quanh chủ đề "Ở một mình
196|hay giao tiếp xã hội",
197|thảo luận từ nhiều góc độ khác nhau.
198|Chúng ta hãy tóm tắt ngắn gọn một vài
199|điểm chính đã nói hôm nay nhé. Được thôi.
200|Thứ nhất, mỗi người có nhu cầu giao tiếp và ở một mình khác nhau,
201|điều này liên quan đến tính cách hướng nội hay hướng ngoại,
202|không có tốt hay xấu.
203|Điều quan trọng là hiểu bản thân,
204|biết điều gì giúp mình "sạc lại năng lượng".
205|Thứ hai, giao tiếp trực tuyến hiện đại rất tiện lợi,
206|nhưng thiếu sự "ấm áp" của việc giao tiếp trực tiếp,
207|chúng ta không thể hoàn toàn phụ thuộc vào nó mà bỏ qua những cuộc gặp thật.
208|Thứ ba, cũng là điều quan trọng nhất,
209|chúng ta cần học cách đối diện với "áp lực giao tiếp xã hội",
210|dũng cảm lựa chọn cách khiến bản thân thoải mái.
211|Ý nghĩa của giao tiếp nằm ở chất lượng, không phải số lượng.
212|Bạn tổng kết rất rõ ràng!
213|Hy vọng cuộc thảo luận của chúng tôi
214|có thể mang đến cho mọi người những suy nghĩ mới.
215|Ừm!
216|Nếu mọi người muốn xem lại nội dung trò chuyện hôm nay,
217|có thể ghé xem blog của chúng tôi.
218|Chúng tôi đã đăng toàn bộ lời thoại của mỗi số lên đó
219|để mọi người tiện học tập.
220|Địa chỉ blog là
221|chinesedailypodcast.blogspot.com.
222|Đúng vậy, hoan nghênh mọi người đến đọc và ôn tập.
223|Cuối cùng, chúng tôi cũng muốn hỏi các bạn đang lắng nghe:
224|Bạn thích ở một mình hơn,
225|hay thích ở bên bạn bè hơn?
226|Cách giao tiếp bạn yêu thích nhất là gì?
227|Rất hoan nghênh mọi người để lại bình luận bên dưới,
228|chia sẻ suy nghĩ và câu chuyện của mình!
229|Chúng tôi mong được đọc những chia sẻ của mọi người.
230|Được rồi, số "Tiếng Trung mỗi ngày" hôm nay đến đây thôi.
231|Cảm ơn mọi người đã lắng nghe,
232|hẹn gặp lại ở số tiếp theo!
233|Tạm biệt!
""".strip()


# ==================================================
# 3. DOC BAN DICH VA KIEM TRA STT
# ==================================================

def load_translations():

    translations = {}

    for line_number, line in enumerate(
        TRANSLATION_TEXT.splitlines(), 1
    ):

        line = line.strip()

        if not line:
            continue

        number_text, sep, vi = line.partition("|")

        if not sep or not number_text.isdigit():
            raise ValueError(
                f"Sai dinh dang ban dich dong {line_number}"
            )

        number = int(number_text)
        vi = vi.strip()

        if number in translations:
            raise ValueError(
                f"Trung STT ban dich {number}"
            )

        if not vi:
            raise ValueError(
                f"Ban dich {number} bi trong"
            )

        translations[number] = vi

    expected = set(range(1, EXPECTED_COUNT + 1))
    actual = set(translations)

    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    if missing or extra:
        raise ValueError(
            f"Thieu STT: {missing}\n"
            f"Thua STT: {extra}"
        )

    return translations


# ==================================================
# 4. GHEP BAN DICH VAO JSON
# ==================================================

def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError("JSON khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module Shadowing.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID.")

    original = data.get("sentences")

    if not isinstance(original, list):
        raise ValueError("Khong co sentences.")

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(original)}."
        )

    translations = load_translations()

    sentences = []
    previous_end = 0.0

    for i, item in enumerate(original, 1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Doan {i} khong hop le."
            )

        hanzi = str(item.get("hanzi", "")).strip()
        pinyin = str(item.get("pinyin", "")).strip()
        vi = translations[i]

        if not hanzi or not pinyin or not vi:
            raise ValueError(
                f"Thieu noi dung o doan {i}."
            )

        try:
            start = float(item["start"])
            end = float(item["end"])
        except (KeyError, ValueError, TypeError):
            raise ValueError(
                f"Timestamp sai o doan {i}."
            )

        if not (
            math.isfinite(start)
            and math.isfinite(end)
        ):
            raise ValueError(
                f"Timestamp khong hop le o doan {i}."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Thoi gian sai o doan {i}."
            )

        if i > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Timestamp chong nhau o doan {i}."
            )

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

        previous_end = end

    # Chi luu vao file moi, khong sua file pinyin goc.

    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": sentences
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

    # ==================================================
    # 5. DOC LAI KIEM TRA
    # ==================================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if saved != document:
        raise RuntimeError(
            "JSON doc lai khong khop."
        )

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError(
            "So doan sau luu khong bang 233."
        )

    for i, (old, new) in enumerate(
        zip(original, saved["sentences"]), 1
    ):

        if (
            float(old["start"]) != new["start"]
            or float(old["end"]) != new["end"]
            or old["hanzi"].strip() != new["hanzi"]
            or old["pinyin"].strip() != new["pinyin"]
        ):
            raise RuntimeError(
                f"Du lieu goc thay doi tai doan {i}."
            )

        if not new["vi"]:
            raise RuntimeError(
                f"Thieu ban dich doan {i}."
            )

    # ==================================================
    # 6. BAO CAO
    # ==================================================

    report_lines = [
        "SHADOWING HSK4 - VIDEO 4",
        f"YouTube ID: {VIDEO_ID}",
        f"MaBaiHoc: {MA_BAI_HOC}",
        f"So doan: {len(sentences)}",
        f"So ban dich: {len(translations)}",
        "Timestamp va noi dung goc: OK",
        "JSON: OK",
        "",
        "===== CAC DOAN CAN RA SOAT =====",
        "039-043: Loi thoai co noi dung bat thuong.",
        "Can doi chieu 5 doan nay voi am thanh goc.",
        "Kiem tra cac doan ngan duoi 0.8 giay.",
        "Kiem tra pinyin cua cac tu da am.",
        "",
        "CHUA CAP NHAT SQL SERVER."
    ]

    REPORT.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    # ==================================================
    # 7. HIEN THI KET QUA
    # ==================================================

    print(
        "===== HSK4 VIDEO 4 - DICH TIENG VIET ====="
    )

    print("YouTube:", VIDEO_ID)
    print("MaBaiHoc:", MA_BAI_HOC)
    print("So doan:", len(sentences))
    print("Da dich:", len(translations))

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
