
import json
import math
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==================================================
# 1. CAU HINH HSK4 - VIDEO 2
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk4")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video2_zh_preview.json"
OUTPUT = DATA / "video2_translated_full.json"
REPORT = DATA / "video2_review_report.txt"

VIDEO_ID = "rTOwIJeG7sM"
EXPECTED_COUNT = 528


# ==================================================
# 2. BAN DICH TIENG VIET - 528 DOAN
# Moi dong: STT|Ban dich
# ==================================================

TRANSLATION_TEXT = """
001|Xin chào tất cả các thính giả!
002|Chào mừng đến với số mới của chương trình "Tiếng Trung mỗi ngày".
003|Tôi là Lý Minh.
004|Xin chào mọi người! Tôi là Vương Vũ.
005|Rất vui lại được gặp mọi người qua sóng phát thanh.
006|Lý Minh, dạo này bạn thế nào?
007|Hình như bạn đặc biệt bận rộn.
008|Đúng vậy, gần đây tôi có một dự án nhỏ đang làm,
009|lúc nào cũng muốn lên kế hoạch cho nó thật hoàn hảo,
010|nên đã dành rất nhiều thời gian cho việc chuẩn bị.
011|Đôi khi tôi cảm thấy càng chuẩn bị nhiều,
012|thì càng ít can đảm để bắt đầu.
013|Tôi hiểu cảm giác này quá!
014|Điều đó làm tôi nhớ đến chủ đề chúng ta muốn trò chuyện hôm nay.
015|Thật ra rất nhiều người trong chúng ta, dù trong học tập,
016|công việc hay cuộc sống,
017|đều có thể từng có những suy nghĩ tương tự:
018|Đợi đến khi chuẩn bị xong, tôi sẽ bắt đầu;
019|đợi đến khi thời cơ chín muồi, tôi sẽ làm.
020|Đúng vậy. Vì thế chủ đề hôm nay là:
021|Đừng chờ đợi thời điểm hoàn hảo.
022|Chúng tôi muốn cùng mọi người thảo luận
023|tại sao chúng ta luôn chờ đợi,
024|và làm thế nào để can đảm bước bước đầu tiên.
025|Đúng! Đây là chủ đề rất gần gũi với cuộc sống.
026|Chương trình âm thanh "Tiếng Trung mỗi ngày" của chúng tôi
027|được dành cho những bạn đang học tiếng Trung ở trình độ trung cấp.
028|Chúng tôi hy vọng thông qua hình thức trò chuyện,
029|giúp mọi người ở trong một môi trường thoải mái, tự nhiên,
030|dần dần nâng cao khả năng nghe tiếng Trung mà không hay biết.
031|Đúng vậy, nên mọi người cứ nghe như đang nghe bạn bè trò chuyện,
032|cứ thư giãn mà nghe thôi.
033|Nội dung chúng tôi nói có thể khiến bạn đồng cảm từ trải nghiệm của mình.
034|Bạn có chuyện gì luôn muốn làm
035|nhưng lại cảm thấy "chưa đến thời điểm" không?
036|Bạn có thể vừa nghe vừa suy nghĩ. Ừm, nói hay lắm.
037|Trước khi bắt đầu,
038|tôi muốn nói một câu với những người bạn mới đến,
039|tốc độ nói trong cuộc trò chuyện của chúng tôi
040|sẽ chậm hơn tốc độ thông thường một chút,
041|nhưng chúng tôi cố gắng giữ cách giao tiếp tự nhiên.
042|Nếu trong lúc nghe có một vài từ chưa hiểu,
043|bạn hoàn toàn không cần căng thẳng,
044|hãy thử dựa vào ngữ cảnh để đoán nghĩa.
045|Tất nhiên, nghe lại vài lần cũng là một cách tốt.
046|Nếu thật sự muốn hiểu rõ, bạn có thể vào blog của chúng tôi xem
047|toàn bộ lời thoại, liên kết nằm trong phần mô tả bên dưới.
048|Được rồi, bây giờ chúng ta chính thức đi vào chủ đề hôm nay nhé.
049|Vương Vũ, bạn nói trước đi,
050|bạn nghĩ tại sao chúng ta luôn có thói quen
051|chờ đợi một cái gọi là "thời điểm hoàn hảo"?
052|Tôi nghĩ đằng sau đó có rất nhiều nguyên nhân tâm lý.
053|Nguyên nhân chính có lẽ là sợ thất bại.
054|Chúng ta mong ngay từ khi xuất hiện đã là người giỏi nhất,
055|vừa bắt tay làm là thành công ngay.
056|Ví dụ nếu tôi muốn học vẽ, tôi có thể nghĩ
057|đợi đến khi mua đầy đủ những cây bút vẽ tốt nhất,
058|màu vẽ, giấy vẽ và tìm được giáo viên giỏi nhất,
059|đợi có một khoảng thời gian dài không bị làm phiền, rồi mới bắt đầu.
060|Nhưng kết quả thì sao?
061|Có thể một năm trôi qua, những cây bút vẽ vẫn nằm trong hộp.
062|Điều bạn nói chính là "chuẩn bị quá mức".
063|Tôi thừa nhận mình là người như vậy.
064|Tôi có khuynh hướng "chủ nghĩa hoàn hảo".
065|Trước khi làm bất kỳ việc gì,
066|tôi đều phải lập kế hoạch chi tiết,
067|phân tích mọi khả năng,
068|dự đoán tất cả vấn đề có thể gặp và chuẩn bị phương án giải quyết.
069|Ví dụ vài năm trước, tôi muốn làm một trang web cá nhân về lịch
070|sử Trung Quốc.
071|Tôi mất ba tháng nghiên cứu nên dùng công nghệ nào,
072|chọn máy chủ ra sao, thiết kế cấu trúc website thế nào,
073|nội dung cần chia thành bao nhiêu phần...
074|Kết quả thế nào? Website đã được đưa lên mạng chưa?
075|Chưa. Vì tôi luôn cảm thấy
076|kiến thức lịch sử của mình chưa đủ hệ thống,
077|thiết kế website chưa đủ thu hút,
078|bài viết đầu tiên chưa đủ sâu sắc.
079|Tôi cứ nghĩ đợi đọc thêm vài chục cuốn sách,
080|đợi học được phần mềm thiết kế cao cấp hơn,
081|đợi khả năng viết tốt hơn rồi mới đăng.
082|Cuối cùng, kế hoạch đó cứ thế không đi đến đâu.
083|Bây giờ nghĩ lại, thực ra tôi đã bị
084|chính tưởng tượng về sự "hoàn hảo" của mình trói buộc.
085|Đúng vậy, "thời điểm hoàn hảo" giống như đường chân trời,
086|bạn thấy nó ở ngay phía trước nhưng đuổi mãi không tới.
087|Bởi vì thực ra nó không tồn tại.
088|Cuộc sống đầy những điều không chắc chắn.
089|Bạn sẽ không bao giờ đợi được một thời điểm
090|mà mọi điều kiện đều đáp ứng hoàn toàn một trăm phần trăm.
091|Nói đến đây,
092|tôi nhớ đến một câu nói rất nổi tiếng,
093|dịch sang tiếng Trung đại khái là:
094|"Hoàn thành quan trọng hơn hoàn hảo."
095|Có nghĩa là một việc bình thường đã làm xong
096|có giá trị hơn nhiều so với một việc hoàn hảo nhưng mãi không hoàn thành.
097|Câu này hay quá!
098|Tôi cảm thấy trong văn hóa của chúng ta,
099|đôi khi người ta quá tôn sùng sự "hoàn hảo".
100|Từ nhỏ chúng ta được dạy phải đạt điểm tuyệt đối,
101|phải làm tốt nhất và không được phạm lỗi.
102|Cách giáo dục này tất nhiên có mặt tốt, nhưng đồng thời
103|cũng có thể khiến chúng ta khi đối mặt với điều không chắc chắn
104|sẽ có phản ứng tự nhiên là lùi bước.
105|Bạn đã nhắc đến một điểm rất sâu sắc.
106|Nỗi sợ thất bại này
107|thực ra được hình thành về sau, không phải bẩm sinh đã có.
108|Bạn xem trẻ nhỏ học đi, ngã thì đứng dậy,
109|chưa bao giờ vì ngã vài lần mà từ bỏ học đi. Đúng!
110|Trong thế giới của trẻ nhỏ
111|không có suy nghĩ "đợi con chuẩn bị xong rồi mới đi".
112|Chúng chỉ không ngừng thử, không ngừng ngã,
113|rồi không ngừng đứng dậy.
114|Đến một thời điểm nào đó, chúng ta học được cách "sợ hãi",
115|học cách đánh đồng "thất bại" với "bản thân mình kém cỏi".
116|Nhận xét này rất thú vị.
117|Vậy chúng ta nói tiếp,
118|ngoài sợ thất bại và chủ nghĩa hoàn hảo,
119|tôi nghĩ còn có một nguyên nhân nữa,
120|đó là chúng ta đặt "ngưỡng bắt đầu" quá cao.
121|Ví dụ có người muốn tập thể dục,
122|trong đầu họ, "bắt đầu" có thể là
123|đăng ký một thẻ phòng tập đắt tiền,
124|thuê huấn luyện viên riêng chuyên nghiệp, tập hai tiếng mỗi ngày.
125|Ngưỡng này quá cao, chỉ nghĩ thôi đã mệt và muốn lùi bước.
126|Vì thế họ cứ đợi, đợi khi có nhiều tiền và thời gian hơn.
127|Chính xác!
128|Nhưng thật ra ngưỡng để "bắt đầu tập thể dục" có thể rất thấp.
129|Ví dụ hôm nay sau bữa tối ra ngoài đi bộ mười lăm phút,
130|hoặc ở nhà tập giãn cơ mười phút theo video.
131|Đó đã là một khởi đầu rất tốt.
132|Chúng ta thường bị chính những tưởng tượng quá lớn lao về "sự bắt đầu" làm cho sợ.
133|Chúng ta luôn nghĩ phải tạo nên thành tích vang dội,
134|mà bỏ qua việc mọi thành tựu lớn
135|đều bắt đầu từ một điểm khởi đầu nhỏ bé không đáng kể.
136|Tôi hoàn toàn đồng ý.
137|Sự chờ đợi này, về bản chất, là một dạng trì hoãn.
138|Chúng ta lấy "chuẩn bị" làm cái cớ
139|để né tránh những thử thách và điều không chắc chắn phải thật sự đối mặt.
140|Có lẽ điều chúng ta sợ không phải chính công việc,
141|mà là khó khăn và thất bại có thể gặp sau khi bắt đầu hành động.
142|Đúng vậy, ngoài ra còn có một hiện tượng tâm lý rất thú vị.
143|Khi chúng ta không làm một việc,
144|ta có thể mãi tưởng tượng nó sẽ tốt đẹp thế nào khi thành công.
145|Ví dụ website lịch sử của bạn, trong tưởng tượng của bạn,
146|nó có nội dung phong phú, thiết kế đẹp, khách truy cập liên tục.
147|Nhưng một khi bắt tay vào làm, bạn phải đối mặt thực tế:
148|không có nổi khách truy cập đầu tiên, nội dung viết ra còn bị chê.
149|Để bảo vệ "hình dung hoàn hảo" đó,
150|chúng ta thà chọn không bắt đầu.
151|Bạn phân tích quá thấu đáo rồi.
152|Đây quả thực là một cơ chế tự vệ về mặt tâm lý.
153|Không bắt đầu thì sẽ không thất bại.
154|Chờ đợi cho chúng ta một lý do để tiếp tục mơ mộng.
155|Nhưng cái giá phải trả là
156|chúng ta mãi giậm chân tại chỗ, chẳng đạt được gì.
157|Trong tâm lý học
158|có một thuật ngữ chuyên mô tả trạng thái này,
159|gọi là "tê liệt vì phân tích".
160|Nghĩa là bạn suy nghĩ quá nhiều, phân tích quá sâu,
161|đến mức không thể hành động, giống như bị tê liệt.
162|"Tê liệt vì phân tích", từ này rất chính xác!
163|Tôi đã từng trải qua trạng thái này.
164|Đôi khi tôi mở một tài liệu, chuẩn bị viết gì đó,
165|nhưng cuối cùng mất hai tiếng để nghĩ tiêu đề nên
166|đặt thế nào, dùng phông chữ nào, chia đoạn ra sao...
167|Cuối cùng chẳng viết được gì,
168|rồi đóng tài liệu lại. [Cười] Tôi cũng từng như vậy!
169|Ban đầu muốn nấu một món ăn, cuối cùng lại mất một tiếng
170|để so sánh năm công thức nấu ăn khác nhau trên mạng,
171|cuối cùng mệt quá nên gọi đồ ăn giao đến.
172|Đây chính là biểu hiện điển hình nhất của "tê liệt vì phân tích".
173|Quá nhiều lựa chọn và thông tin khiến người ta không biết bắt đầu từ đâu.
174|Vì vậy điều này dẫn đến quan điểm thứ hai của chúng ta:
175|Một sự khởi đầu không hoàn hảo vẫn
176|tốt hơn rất nhiều so với việc chờ đợi hoàn hảo không biết đến bao giờ.
177|Bản thân hành động còn quan trọng hơn kết quả.
178|Bạn có thể nói cụ thể hơn không?
179|Tại sao bản thân hành động lại quan trọng đến vậy?
180|Bởi vì chỉ sau khi bạn bắt đầu làm,
181|bạn mới nhận được phản hồi thực tế nhất.
182|Bạn mới biết kế hoạch của mình có vấn đề ở đâu,
183|hướng đi có đúng không và mình còn cần học gì.
184|Giống như học bơi vậy.
185|Bạn không thể đứng trên bờ đọc một trăm cuốn sách dạy bơi là biết bơi.
186|Bạn phải xuống nước, cảm nhận sức nổi của nước,
187|sặc vài ngụm nước rồi dần dần mới tìm được cảm giác.
188|Ví dụ này của bạn rất sinh động.
189|Website lịch sử của tôi chính là điển hình của việc "đứng trên bờ học bơi".
190|Dù tôi nghiên cứu nhiều đến đâu,
191|cũng không bằng trực tiếp dùng công cụ đơn giản nhất
192|để đăng một bài viết chưa hoàn hảo,
193|rồi xem phản ứng của độc giả.
194|Có thể độc giả sẽ cho tôi biết
195|họ đặc biệt hứng thú với một triều đại nào đó,
196|hoặc cảm thấy bài viết của tôi quá dài.
197|Những phản hồi đó quý giá hơn rất nhiều so với việc tôi ngồi tự làm một mình suốt ba tháng.
198|Chính là như vậy!
199|Bắt đầu hành động
200|giống như đem ý tưởng của bạn vào một thế
201|giới thực tế để kiểm nghiệm.
202|Bạn sẽ phát hiện nhiều "vấn đề lớn" từng lo lắng
203|thực ra hoàn toàn không phải vấn đề.
204|Ngược lại, những khó khăn chưa từng nghĩ đến lại bất ngờ xuất hiện.
205|Đó chính là trưởng thành.
206|Ví dụ tôi luôn rất thích làm bánh ngọt,
207|và luôn muốn quay lại quá trình làm bánh của mình
208|thành video ngắn rồi chia sẻ lên mạng.
209|Nhưng tôi luôn lo mình quay không chuyên nghiệp,
210|bếp ở nhà không đủ đẹp, món làm ra cũng không có gì đặc biệt.
211|Vậy khi đó bạn đã vượt qua như thế nào?
212|Một người bạn lúc ấy nói với tôi:
213|"Đừng nghĩ đến việc quay một video hoàn hảo.
214|Cứ dùng điện thoại, quay một cách đơn
215|giản quá trình làm bánh quy dài một phút,
216|rồi chỉ gửi vào nhóm trò chuyện có vài người chúng ta,
217|xem mọi người phản ứng ra sao." Tôi đã làm như vậy.
218|Video đó rất đơn giản, ánh sáng cũng chưa hoàn hảo.
219|Nhưng sau khi gửi đi,
220|bạn bè đều nói trông rất ngon và động viên tôi rất nhiều.
221|Họ cũng đưa ra một số góp ý nhỏ,
222|ví dụ "lần sau có thể ghi lượng nguyên liệu bằng chữ lên màn hình".
223|"Khởi đầu không hoàn hảo" này đã mang đến cho tôi sự tự tin rất lớn.
224|Tôi biết mình có thể làm được việc này,
225|và có thể cải thiện để làm tốt hơn.
226|Cách này rất hay, gọi là tư duy "sản phẩm khả thi tối thiểu".
227|Nó rất phổ biến trong ngành công nghệ, nghĩa là
228|bạn đừng nghĩ ngay từ đầu
229|phải tạo ra sản phẩm có chức năng hoàn hảo, mà hãy làm trước phiên bản cốt lõi
230|và đơn giản nhất, đưa ra thị trường,
231|rồi dựa vào phản hồi của người dùng
232|để từng bước hoàn thiện. Quá trình này gọi là "lặp cải tiến".
233|Thật ra chúng ta có thể áp dụng tư duy này vào bất cứ việc gì.
234|Đúng! Từ "lặp cải tiến" rất hay.
235|Cuộc sống và sự trưởng thành của chúng ta
236|chẳng phải cũng là quá trình liên tục cải tiến sao?
237|Phiên bản đầu tiên của bạn chắc chắn không hoàn hảo.
238|Nhưng thông qua không ngừng học hỏi, thử nghiệm, mắc lỗi,
239|sửa chữa, bạn từ từ "cập nhật" bản thân thành phiên bản tốt hơn.
240|Nếu cứ đợi đến khi thành "phiên bản hoàn hảo" mới công bố,
241|thì bạn sẽ chẳng bao giờ có cơ hội.
242|Đúng là như vậy.
243|Hơn nữa, một khi đã bắt đầu,
244|bạn sẽ có được một thứ gọi là "động lực".
245|Khi công việc đang tiến triển, nó sẽ thúc đẩy bạn tiến lên.
246|Ví dụ bạn quyết định chạy bộ hằng ngày.
247|Ngày đầu tiên có thể khó khăn, nhưng bạn vẫn kiên trì.
248|Ngày thứ hai, nhờ thành công hôm qua, bạn sẽ tự tin hơn.
249|Sau một tuần kiên trì, chạy bộ có thể trở thành thói quen.
250|Vòng tuần hoàn tích cực do hành động tạo ra này
251|là điều bạn sẽ không bao giờ cảm nhận được khi chỉ đứng nhìn và chờ đợi.
252|Đúng vậy, bắt đầu hành động sẽ phá vỡ vòng lặp tiêu cực của "trì hoãn".
253|Chúng ta thường trì hoãn vì cảm thấy nhiệm vụ quá khó,
254|trì hoãn lại khiến chúng ta thấy tội lỗi và lo âu,
255|những cảm xúc tiêu cực này khiến chúng ta càng không muốn bắt đầu.
256|Nhưng chỉ cần bước bước đầu tiên,
257|dù đó chỉ là bước rất nhỏ,
258|ví dụ đặt giày chạy bộ cạnh cửa, bạn đã phá vỡ vòng lặp ấy.
259|Bạn sẽ cảm thấy mình có một chút khả năng kiểm soát cuộc sống
260|của mình. Tôi nhớ có một nghiên cứu tâm lý học nói rằng,
261|bản thân hành động có thể thay đổi cảm nhận của chúng ta,
262|chứ không phải cảm nhận thay đổi hành động.
263|Nhiều người nghĩ phải có hứng, có động lực rồi mới hành động.
264|Nhưng thực tế thường ngược lại: bạn hành động trước,
265|động lực mới theo đó mà đến.
266|Điều này thật sự làm thay đổi cách nghĩ của nhiều người.
267|Chúng ta luôn đợi cảm giác "muốn làm",
268|nhưng cảm giác ấy có thể sẽ không tự xuất hiện.
269|Tôi nghĩ có thể dùng một ví dụ:
270|Lò sưởi không thể cho bạn hơi ấm trước rồi mới bảo bạn thêm củi.
271|Bạn phải cho củi vào trước, lửa mới cháy và mới có hơi ấm.
272|Ví dụ này hay quá!
273|Tôi phải ghi lại mới được.
274|Được rồi, chúng ta đã phân tích nguyên nhân của sự chờ đợi,
275|cũng đã hiểu tầm quan trọng của việc bắt đầu hành động.
276|Tiếp theo, hãy nói về những điều thực tế hơn.
277|Đối với những người giống tôi trước đây,
278|luôn chờ đợi một "thời điểm hoàn hảo",
279|chúng ta có lời khuyên cụ thể nào không? Tất nhiên là có.
280|Trước tiên, tôi nghĩ điều quan trọng nhất là:
281|giảm kỳ vọng đối với "bước đầu tiên".
282|Đừng nghĩ "Tôi phải viết một cuốn sách",
283|mà hãy nghĩ "Hôm nay tôi chỉ viết một trăm chữ".
284|Đừng nghĩ "Tôi phải học giỏi tiếng Trung",
285|mà hãy nghĩ "Hôm nay tôi học thuộc năm từ mới".
286|Chia một mục tiêu lớn thành vô số hành động
287|nhỏ có thể thực hiện ngay lập tức.
288|Phương pháp này rất hiệu quả, gọi là "chia nhỏ nhiệm vụ".
289|Nó có thể giảm đáng kể rào cản tâm lý khi hành
290|động. Khi nhiệm vụ nhỏ đến mức "không thể
291|thất bại", bạn sẽ khó tìm thêm lý do để trì hoãn.
292|Ví dụ tập thể dục,
293|nếu mục tiêu là "mỗi ngày chống đẩy một cái",
294|thì ai mà không làm được chứ?
295|Điều kỳ diệu là sau khi làm xong một cái,
296|bạn rất có thể sẽ nghĩ "hay làm thêm một cái nữa".
297|Đây chính là sức mạnh kỳ diệu của hành động.
298|Nói đến đây,
299|tôi dường như nghe thấy tiếng lòng của một số thính giả.
300|Họ có thể nghĩ:
301|"Tôi biết mình nên chia nhỏ mục tiêu,
302|tôi cũng biết nên bắt đầu,
303|nhưng tôi thật sự rất sợ bước đầu tiên,
304|sợ làm không tốt rồi bị người khác cười chê,
305|thì phải làm sao?" Cảm giác này thật ra rất phổ biến.
306|Tôi rất hiểu nỗi lo đó.
307|Đối với vấn đề này,
308|lời khuyên của tôi là đặt ra một "giai đoạn thử nghiệm".
309|Hãy nói với bản thân: tôi không phải muốn "trở thành" nhà văn
310|hay họa sĩ,
311|mà chỉ đang "thử" viết hoặc vẽ trong vòng một tháng.
312|Trong một tháng ấy, không chạy theo kết quả, chỉ tập trung vào quá trình.
313|Cho phép bản thân mắc lỗi, cho phép bản thân làm chưa tốt.
314|Hãy xem nó như trò chơi chứ không phải một kỳ thi.
315|Như vậy tâm lý sẽ thoải mái hơn rất nhiều.
316|Đánh giá của người khác cũng không còn quan trọng đến vậy,
317|bởi vì bạn chỉ đang "chơi" thôi.
318|Tâm thế "giai đoạn thử nghiệm" này thật tuyệt!
319|Nó tạo cho chúng ta một không gian an toàn để khám phá và mắc lỗi.
320|Tôi còn muốn chia sẻ thêm một mẹo,
321|gọi là "quy tắc năm phút".
322|Nếu có việc gì đó bạn không muốn làm,
323|hãy tự nói: "Tôi chỉ làm năm phút thôi,
324|năm phút sau sẽ dừng."
325|Ví dụ không muốn dọn phòng thì cứ dọn trước năm phút.
326|Không muốn đọc sách thì cứ đọc trước năm phút.
327|Nhiều khi sau khi thật sự bắt đầu trong năm phút ấy,
328|bạn sẽ phát hiện việc đó không khó như tưởng tượng,
329|và rất có thể sẽ tiếp tục làm.
330|Đúng vậy, khoảnh khắc khởi động là khó nhất.
331|Một khi cỗ máy đã vận hành, phần sau sẽ trơn tru hơn nhiều.
332|"Quy tắc năm phút" chính là tia lửa giúp bạn khởi động động cơ.
333|Ngoài ra, tạo một môi trường và nghi thức
334|cho việc "bắt đầu" cũng rất quan trọng.
335|Ví dụ bạn muốn hình thành thói quen đọc sách,
336|có thể bố trí riêng ở nhà một góc đọc sách thoải
337|mái, đặt ghế êm và đèn bàn.
338|Mỗi tối pha một tách trà, ngồi ở đó,
339|dù không đọc sách mà chỉ ngồi năm phút, cũng là một khởi đầu tích cực.
340|Ừm, môi trường quả thực ảnh hưởng đến hành vi con người.
341|Tôi còn muốn bổ sung một điểm: tìm một người đồng hành,
342|tức là tìm người có cùng mục tiêu để cùng hành động.
343|Ví dụ bạn muốn học tiếng Trung,
344|có thể tìm một người bạn cũng đang học tiếng Trung,
345|hẹn mỗi tuần báo cáo tiến độ cho nhau.
346|Đôi khi sức mạnh thúc đẩy chúng ta hành động
347|không phải là khao khát thành công,
348|mà là một chút trách nhiệm không muốn thất hứa trước mặt bạn
349|bè. Phương pháp này thật sự hiệu quả!
350|Trách nhiệm xã hội là một động lực rất mạnh.
351|Làm một việc một mình rất dễ bỏ cuộc,
352|vì không ai biết cũng không ai quan tâm.
353|Nhưng nếu bạn công khai cam kết, nói cho bạn bè biết,
354|thậm chí đăng lên mạng xã hội,
355|việc từ bỏ sẽ trở nên hơi "mất mặt",
356|và bạn lại kiên trì hơn. Đúng,
357|trong tâm lý học điều này gọi là nguyên tắc "cam kết và nhất quán".
358|Khi bạn công khai đưa ra lời cam kết,
359|bên trong bạn sẽ có một sức mạnh thúc đẩy bạn thực hiện,
360|bởi con người vốn mong hành vi của mình
361|nhất quán với những lời mình đã nói.
362|Vì vậy nếu hiện tại bạn có một việc luôn muốn làm
363|nhưng vẫn chưa bắt đầu,
364|hãy thử viết xuống phần bình luận của chúng tôi để công khai cam kết.
365|Như vậy mọi người sẽ cùng ở đây đợi
366|xem tiến độ của bạn và cổ vũ cho bạn.
367|[Cười] Ý tưởng này hay quá!
368|Phần bình luận của chúng ta sẽ trở thành một "bức tường cam kết" nhỏ.
369|Tóm lại,
370|các cách khắc phục tâm lý "chờ đợi sự hoàn hảo" gồm: thứ nhất,
371|chia nhỏ nhiệm vụ,
372|để bước đầu tiên nhỏ đến mức khó mà thất bại; thứ hai,
373|điều chỉnh tâm thế,
374|cho bản thân một "giai đoạn thử nghiệm" không quan tâm kết quả; thứ ba,
375|dùng "quy tắc năm phút" để bắt đầu nhiệm vụ khó;
376|thứ tư,
377|tạo môi trường thuận lợi cho việc bắt đầu hành động;
378|thứ năm, tìm người đồng hành và công khai cam kết,
379|dùng trách nhiệm xã hội để thúc đẩy mình tiến lên.
380|Nói rất hay. Tôi muốn bổ sung điểm cuối cùng,
381|cũng là điểm quan trọng nhất: chấp nhận sự không hoàn hảo.
382|Bạn phải thật lòng chấp nhận
383|rằng mọi khởi đầu đều không hoàn hảo, thậm chí vụng về.
384|Học ngôn ngữ, ban đầu nói còn lắp bắp;
385|học nhạc cụ, ban đầu chơi nghe như tiếng ồn.
386|Đó đều là chuyện bình thường.
387|Không hoàn hảo là con đường bắt buộc để tiến đến hoàn hảo.
388|Sự hoàn hảo thật sự không phải ngay từ đầu đã không có khuyết điểm,
389|mà là dù chưa hoàn hảo vẫn có can đảm không ngừng tiến lên.
390|Bạn nói hay quá!
391|Ngoài ra tôi muốn nói rằng,
392|những người mà bây giờ bạn cảm thấy họ làm rất giỏi
393|không phải vì họ sinh ra đã hoàn hảo,
394|mà vì họ bắt đầu sớm hơn bạn,
395|tích lũy nhiều trải nghiệm "không hoàn hảo" hơn bạn.
396|Họ từng sặc nước nhiều hơn bạn nên giờ bơi giỏi hơn.
397|Đây là một lời nhắc rất hay.
398|Khi nhìn thành quả của người khác, chúng ta dễ bỏ qua
399|những khó khăn và thất bại họ đã trải qua.
400|Chúng ta chỉ thấy đích đến thành công mà quên rằng họ
401|cũng xuất phát từ điểm khởi đầu không hoàn hảo.
402|Đúng, trong tâm lý học điều này gọi là "thiên lệch sống sót".
403|Chúng ta chỉ có thể thấy các câu chuyện thành công mà không thấy những người thất bại
404|và bỏ cuộc.
405|Vì vậy chúng ta hình thành một ảo tưởng,
406|nghĩ rằng thành công là việc dễ dàng,
407|rằng những người thành công ngay từ đầu đã thể hiện rất tốt.
408|Nhưng sự thật hoàn toàn không phải vậy. Được rồi,
409|tôi nghĩ nội dung chúng ta trò chuyện hôm nay đã rất
410|phong phú. Vương Vũ, trong cuộc thảo luận hôm nay,
411|chúng ta đã dùng vài từ có thể hơi khó với người học trung cấp.
412|Giờ chúng ta cùng ôn lại,
413|giúp mọi người hiểu và ghi nhớ tốt hơn.
414|Từ đầu tiên là từ do chính tôi nhắc đến: "thói quen trì hoãn".
415|Bạn có thể giải thích bằng lời đơn giản không?
416|Được.
417|"Thói quen trì hoãn" thực ra là cách gọi rất phổ biến.
418|Nó chỉ một thói quen hành vi,
419|tức là bạn rõ ràng biết có một việc
420|quan trọng cần làm,
421|nhưng lại không muốn bắt đầu, cứ kéo dài hết lần này đến lần khác,
422|tự nhủ "để mai làm".
423|Thói quen này được gọi là "trì hoãn".
424|Bạn giải thích rất rõ. Được rồi,
425|từ thứ hai là "ngưỡng" bắt đầu mà chúng ta đã nói đến.
426|"Ngưỡng" ở đây nghĩa là gì?
427|Ừm, "ngưỡng cửa" vốn chỉ thanh gỗ
428|hoặc đá nằm phía dưới cánh cửa.
429|Ở đây chúng ta dùng nó để ví von
430|độ khó hoặc tiêu chuẩn khi làm một việc.
431|Nếu nói "ngưỡng làm việc gì đó rất cao",
432|nghĩa là muốn bắt đầu phải đáp ứng điều kiện rất cao,
433|rất khó đạt được.
434|Ví dụ nói "ngưỡng mở một nhà hàng rất cao",
435|có nghĩa là cần nhiều tiền và nhiều kinh nghiệm.
436|Tôi hiểu rồi. Từ thứ ba là một thành ngữ,
437|gọi là "tuần tự tiến bước".
438|"Tuần tự tiến bước" có nghĩa là
439|trong học tập hoặc công việc,
440|phải tuân theo trình tự và các bước nhất định,
441|tiến từng bước, không được nóng vội.
442|Ví dụ khi học tiếng Trung, chúng ta nên học theo từng bước,
443|trước học pinyin, rồi học chữ Hán,
444|sau đó học từ và câu thì nền tảng mới vững chắc.
445|Rất tốt. Từ thứ tư là từ tôi đã nhắc đến cuối cùng,
446|những "điều lo ngại" mọi người có thể gặp.
447|"Lo ngại" nghĩa là gì?
448|"Lo ngại" chính là những điều khiến bạn lo lắng, sợ hãi.
449|Khi bạn chuẩn bị đưa ra quyết định,
450|những suy nghĩ trong lòng như "Lỡ thất bại thì sao?"
451|"Người khác sẽ nhìn mình thế nào?"
452|Những suy nghĩ khiến bạn do dự ấy chính là điều lo ngại của bạn.
453|Rất tốt.
454|Hôm nay chúng ta còn dùng hai từ mới, muốn giải thích riêng.
455|Từ đầu tiên là "tê liệt vì phân tích".
456|"Tê liệt vì phân tích" nghĩa là
457|khi đối mặt với một quyết định,
458|bạn suy nghĩ quá nhiều, phân tích quá nhiều,
459|đến mức không thể bước nổi một bước,
460|như thể bị chính suy nghĩ của mình trói chặt,
461|không thể cử động. "Tê liệt" vốn là thuật ngữ y học,
462|chỉ một bộ phận cơ thể không thể cử động.
463|Ở đây chúng ta mượn hình ảnh ấy
464|để mô tả trạng thái "không thể hành động" trong suy nghĩ.
465|Bạn giải thích rất chính xác.
466|Từ thứ hai là "thiên lệch sống sót".
467|"Thiên lệch sống sót"
468|là một khái niệm trong thống kê và tâm lý học,
469|nghĩa là khi phân tích một việc,
470|chúng ta thường chỉ nhìn thấy "những trường hợp thành công",
471|mà không thấy "những trường hợp thất bại",
472|vì các trường hợp thất bại thường không được ghi lại
473|và cũng không được lan truyền rộng rãi.
474|Vì vậy, chúng ta sẽ đánh giá sai
475|mức độ khó của việc đó, tưởng rằng thành công dễ hơn thực tế.
476|Rất tuyệt.
477|Hy vọng những giải thích này giúp ích cho mọi người.
478|Những từ chúng ta thảo luận hôm nay như "trì hoãn",
479|"ngưỡng", "tuần tự tiến bước",
480|"lo ngại", "tê liệt vì phân tích" và "thiên lệch sống sót",
481|mọi người cũng có thể thử sử dụng trong bài viết tiếng Trung
482|hoặc khi luyện nói.
483|Được rồi, cuộc thảo luận hôm nay
484|về chủ đề "Đừng chờ đợi thời điểm hoàn hảo"
485|cũng gần đến lúc kết thúc.
486|Tóm tắt ngắn gọn nhé,
487|hôm nay chúng ta chủ yếu nói ba điểm:
488|Thứ nhất, chúng ta luôn chờ thời điểm hoàn hảo,
489|chủ yếu vì sợ thất bại, chủ nghĩa hoàn hảo,
490|"tê liệt vì phân tích",
491|và đặt ngưỡng bắt đầu quá cao;
492|thứ hai, một khởi đầu không hoàn hảo
493|có giá trị hơn nhiều so với việc chờ đợi sự hoàn hảo,
494|vì bản thân hành động mang lại phản hồi,
495|động lực, sự trưởng thành,
496|và hành động thường là nguồn gốc của động lực,
497|chứ không phải kết quả; thứ ba, thông qua chia nhỏ nhiệm vụ,
498|điều chỉnh tâm thế, dùng quy tắc năm phút, tạo
499|môi trường và tìm người đồng hành để công khai cam kết,
500|chúng ta có thể giúp bản thân dũng cảm bước bước đầu tiên.
501|Ừm, tổng kết hay lắm!
502|Hy vọng cuộc trò chuyện hôm nay mang đến cho mọi người chút cảm hứng và can đảm.
503|Nếu muốn xem lại nội dung hôm nay,
504|bạn có thể truy cập blog của chúng tôi,
505|đường dẫn blog nằm trong
506|phần mô tả của số chương trình này, ở đó bạn có thể tìm thấy
507|toàn bộ lời thoại của số này.
508|Đúng vậy. Nếu mọi người cảm thấy chương trình hôm nay
509|hữu ích, hy vọng các bạn nhấn thích,
510|đăng ký kênh và chia sẻ cho bạn bè.
511|Điều đó sẽ giúp đỡ chúng tôi rất nhiều,
512|mang đến động lực để làm thêm những nội dung tốt hơn.
513|Chính xác!
514|Cuối cùng, chúng tôi muốn để lại một câu hỏi cho mọi người.
515|Trong cuộc sống của bạn,
516|có việc gì bạn luôn muốn làm
517|nhưng mãi vẫn chưa bắt đầu không?
518|Điều gì khiến bạn do dự?
519|Hoan nghênh mọi người để lại bình luận bên dưới,
520|chia sẻ câu chuyện hoặc suy nghĩ của mình.
521|Chúng tôi rất mong được đọc chia sẻ của các bạn,
522|và sẽ đọc, trả lời từng bình luận một cách nghiêm túc.
523|Biết đâu câu hỏi của bạn
524|hoặc câu chuyện bạn chia sẻ
525|sẽ trở thành chủ đề của chương trình tiếp theo!
526|Mong chờ bình luận của mọi người.
527|Vậy chương trình hôm nay đến đây thôi.
528|Cảm ơn mọi người đã lắng nghe, hẹn gặp lại ở số sau! Tạm biệt!
""".strip()


# ==================================================
# 3. DOC VA KIEM TRA BAN DICH
# ==================================================

def load_translations():
    translations = {}

    for line_no, line in enumerate(
        TRANSLATION_TEXT.splitlines(), 1
    ):
        line = line.strip()

        if not line:
            continue

        number_text, separator, vi = line.partition("|")

        if not separator or not number_text.isdigit():
            raise ValueError(
                f"Sai dinh dang ban dich dong {line_no}"
            )

        number = int(number_text)

        if number in translations:
            raise ValueError(
                f"Trung STT {number}"
            )

        if not vi.strip():
            raise ValueError(
                f"Doan {number} thieu ban dich"
            )

        translations[number] = vi.strip()

    expected = set(range(1, EXPECTED_COUNT + 1))

    missing = sorted(expected - set(translations))
    extra = sorted(set(translations) - expected)

    if missing or extra:
        raise ValueError(
            f"Ban dich thieu {missing}, thua {extra}"
        )

    return translations


# ==================================================
# 4. TAO PINYIN CO DAU THANH
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
# 5. GHEP CHU HAN, PINYIN VA BAN DICH
# ==================================================

def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if data.get("module") != "shadowing":
        raise ValueError("Sai module Shadowing.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID video 2.")

    original = data.get("sentences")

    if not isinstance(original, list):
        raise ValueError(
            "sentences phai la danh sach."
        )

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(original)}."
        )

    translations = load_translations()

    sentences = []
    short_segments = []
    long_segments = []
    previous_end = 0.0

    for i, item in enumerate(original, 1):

        start = float(item["start"])
        end = float(item["end"])

        if not (
            math.isfinite(start)
            and math.isfinite(end)
        ):
            raise ValueError(
                f"Timestamp khong hop le doan {i}"
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}"
            )

        if i > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Timestamp chong nhau doan {i}"
            )

        hanzi = str(item["hanzi"]).strip()
        pinyin = make_pinyin(hanzi)
        vi = translations[i]

        if not all([hanzi, pinyin, vi]):
            raise ValueError(
                f"Thieu noi dung o doan {i}"
            )

        duration = round(end - start, 3)

        if duration < 0.8:
            short_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        if duration > 10:
            long_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

        previous_end = end

    # Luu file JSON moi, khong ghi de preview goc.
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
    # 6. BAO CAO KIEM TRA
    # ==================================================

    lines = [
        "SHADOWING HSK4 - VIDEO 2",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"So ban dich: {len(translations)}",
        f"Doan < 0.8s: {len(short_segments)}",
        f"Doan > 10s: {len(long_segments)}",
        "Timestamp chong nhau: 0",
        "",
        "===== DOAN NGAN ====="
    ]

    for item in short_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "===== DOAN DAI ====="
    ])

    for item in long_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "===== CAC VI TRI CAN RA SOAT =====",
        "039-040: Tu 语速 bi cat giua doan.",
        "069-070: Tu 历史 bi cat giua doan.",
        "165-166: Tu 应该 bi cat giua doan.",
        "214-215: Tu 简单 bi cat giua doan.",
        "259-260: Tu 掌控感 bi cat giua doan.",
        "289-291: Cum 心理阻力 bi cat giua doan.",
        "336-337: Tu 舒适 bi cat giua doan.",
        "Kiem tra 4 doan ngan duoi 0.8 giay.",
        "Kiem tra tu da am va thanh dieu pinyin.",
        "Ban dich can doi chieu voi am thanh goc.",
        "",
        "CHUA CAP NHAT SQL SERVER."
    ])

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ==================================================
    # 7. DOC LAI DE XAC MINH
    # ==================================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if saved["youtube_id"] != VIDEO_ID:
        raise RuntimeError("Sai YouTube ID.")

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError(
            "So doan sau luu khong bang 528."
        )

    for i, (old, new) in enumerate(
        zip(original, saved["sentences"]), 1
    ):
        for field in ("start", "end"):
            if float(old[field]) != new[field]:
                raise RuntimeError(
                    f"Doan {i} thay doi {field}"
                )

        if old["hanzi"].strip() != new["hanzi"]:
            raise RuntimeError(
                f"Doan {i} thay doi hanzi"
            )

        if not new["pinyin"] or not new["vi"]:
            raise RuntimeError(
                f"Doan {i} thieu pinyin/vi"
            )

    # ==================================================
    # 8. HIEN THI KET QUA
    # ==================================================

    print("===== HSK4 VIDEO 2 - PINYIN VA DICH =====")
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("Da dich:", len(translations))
    print("Doan ngan < 0.8s:", len(short_segments))
    print("Doan dai > 10s:", len(long_segments))

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
