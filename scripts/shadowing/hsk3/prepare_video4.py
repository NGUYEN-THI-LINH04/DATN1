
import json
import math
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==================================================
# 1. CAU HINH
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk3")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video4_zh_preview.json"
OUTPUT = DATA / "video4_translated_full.json"
REPORT = DATA / "video4_review_report.txt"

VIDEO_ID = "yaeECV1JRjM"
EXPECTED_COUNT = 396


# ==================================================
# 2. BAN DICH TIENG VIET - 396 DOAN
#
# Moi dong co dang: STT|Ban dich
# So thu tu trung voi transcript Supadata.
# ==================================================

TRANSLATION_TEXT = """
001|Lý Minh, mau nhìn điện thoại này,
002|bạn xem thời tiết cuối tuần này đi!
003|Ừm? Để tôi xem nào... Cuối tuần,
004|trời nắng, hai mươi lăm độ.
005|Khá đẹp đấy chứ. Sao vậy?
006|Chỉ là "khá đẹp" thôi sao?
007|Phải là "rất tuyệt" mới đúng!
008|Bạn xem, mặt trời rực rỡ như thế, bầu trời xanh như vậy.
009|Chúng ta cứ làm việc suốt,
010|cuối tuần này nên ra ngoài chơi!
011|Ra ngoài chơi à?
012|Nghe cũng hay đấy.
013|Lâu rồi chúng ta chưa đi chơi.
014|Bạn muốn đi đâu?
015|Chúng ta đi dã ngoại nhé!
016|Tìm một công viên đẹp, hoặc lên núi,
017|mang thật nhiều đồ ăn ngon rồi ngồi trên bãi cỏ cả ngày.
018|Chỉ nghĩ thôi đã thấy vui rồi!
019|Dã ngoại à? Ừm... Ý hay đấy.
020|Tôi thích ý tưởng này.
021|Cuối tuần ra ngoài đi dạo, ngắm nhìn thế giới bên ngoài, thật tốt.
022|Tuyệt quá!
023|Tôi biết ngay là bạn sẽ thích mà.
024|Vậy bây giờ chúng ta bắt đầu chuẩn bị nhé!
025|Chúng ta sẽ đi đâu?
026|Đừng vội, đừng vội.
027|Bạn lúc nào cũng nhanh như vậy.
028|Chúng ta phải suy nghĩ kỹ trước đã.
029|Đi đâu? Đi lúc nào?
030|Đi bằng gì? Cần mang những thứ gì?
031|Đó đều là những vấn đề cần tính.
032|[Cười] Bạn xem bạn kìa,
033|tôi vừa nói đi chơi,
034|là bạn đã bắt đầu làm việc rồi.
035|Được rồi, được rồi,
036|thầy Lý,
037|chúng ta cùng "làm việc" một chút,
038|nói về kế hoạch dã ngoại của chúng ta nhé.
039|Được.
040|Câu hỏi đầu tiên,
041|cũng là câu hỏi quan trọng nhất:
042|Điểm đến của chúng ta là đâu?
043|Bạn muốn đến công viên
044|hay lên núi?
045|Tôi muốn đến một nơi rất đẹp,
046|có ít người.
047|Lần trước tôi thấy một địa điểm trên mạng,
048|tên là "Núi Bách Hoa",
049|chỉ nghe tên thôi đã thấy đẹp rồi.
050|Chúng ta đến đó, bạn thấy sao?
051|Núi Bách Hoa à?
052|Tôi từng nghe nói đến.
053|Nhưng tôi phải tra thử đã.
054|Bạn đợi một chút,
055|tôi dùng điện thoại xem bản đồ.
056|Được chứ,
057|bạn tra nhanh đi.
058|Ở đó có nhiều hoa
059|và nhiều cây không?
060|Ừm...
061|Tôi thấy rồi.
062|Núi Bách Hoa đúng là rất đẹp,
063|nhưng...
064|nó cách chúng ta quá xa.
065|Bạn nhìn bản đồ đi,
066|chúng ta lái xe đến đó mất hơn ba tiếng.
067|Ba tiếng á?
068|Xa thế sao...
069|Vậy buổi sáng chúng ta phải dậy rất sớm.
070|Lúc trở về cũng sẽ rất muộn,
071|có lẽ sẽ rất mệt.
072|Đúng vậy.
073|Chúng ta đi dã ngoại là để thư giãn,
074|để vui vẻ.
075|Nếu mất quá nhiều thời gian trên đường,
076|thì sẽ quá mệt.
077|Tôi nghĩ lần đầu đi,
078|chúng ta có thể chọn một nơi gần hơn.
079|Ừm...
080|Bạn nói đúng.
081|Xa quá đúng là rất mệt.
082|Vậy... bạn có ý tưởng nào hay không?
083|Bạn có biết nơi nào đẹp không?
084|Để tôi nghĩ xem...
085|Phía tây thành phố chúng ta có một nơi gọi là "Công viên rừng Tây Sơn",
086|bạn thấy thế nào?
087|Công viên đó rất rộng,
088|bên trong có núi, có nước,
089|và cả những bãi cỏ rất lớn.
090|Công viên rừng Tây Sơn à?
091|Tôi từng nghe bạn mình nói đến,
092|cô ấy bảo ở đó rất đẹp.
093|Có xa chỗ chúng ta không?
094|Không xa.
095|Chúng ta có thể đi tàu điện ngầm đến đó.
096|Đi tàu điện ngầm khoảng một tiếng,
097|rất tiện.
098|Xuống tàu điện ngầm, đi bộ thêm mười phút
099|là đến cổng công viên rồi.
100|Đi tàu điện ngầm là đến được sao?
101|Vậy thì tuyệt quá!
102|Tôi ghét nhất là phải lái xe đến những nơi quá xa,
103|rất phiền phức.
104|Hơn nữa, đi tàu điện ngầm còn không phải tìm chỗ đỗ xe.
105|Đúng.
106|Và công viên đó rất rộng,
107|nếu chúng ta đi sớm một chút,
108|chắc chắn có thể tìm được một chỗ ít người và sạch sẽ.
109|Chúng ta có thể tìm một cây lớn,
110|ngồi dưới gốc cây sẽ rất dễ chịu.
111|Được!
112|Nghe bạn nói vậy,
113|tôi thấy Công viên rừng Tây Sơn này thật sự rất tuyệt.
114|Được!
115|Vậy chúng ta sẽ đến Công viên rừng Tây Sơn!
116|Địa điểm,
117|đã quyết định xong!
118|Tuyệt quá.
119|Vấn đề đầu tiên đã được giải quyết.
120|Vậy chúng ta đi thứ Bảy hay Chủ nhật?
121|Ừm...
122|Thứ Bảy đi!
123|Thứ Bảy đi chơi,
124|Chủ nhật có thể nghỉ ở nhà một ngày.
125|Như vậy lúc đi làm vào thứ Hai,
126|sẽ không cảm thấy quá mệt.
127|Bạn suy nghĩ chu đáo thật.
128|Được, vậy quyết định nhé,
129|thứ Bảy này chúng ta đến Công viên rừng Tây Sơn dã ngoại.
130|Yeah! Tuyệt vời!
131|Bây giờ tôi đã bắt đầu thấy vui rồi!
132|Được, giải quyết xong vấn đề đầu tiên,
133|bây giờ là vấn đề thứ hai.
134|Cũng là phần bạn thích nhất.
135|Tôi biết rồi!
136|Là chuẩn bị đồ ăn! Đúng không?
137|Chính xác.
138|Chúng ta cần mang đồ ăn gì?
139|Mang đồ uống gì?
140|Đồ ăn... để tôi nghĩ xem.
141|Trước tiên nhất định phải có bánh sandwich hoặc bánh mì.
142|Ăn rất tiện.
143|Chúng ta có thể đến cửa hàng mua ít bánh mì ngon.
144|Đồng ý. Bánh mì rất ổn.
145|Chúng ta còn có thể tự làm sandwich.
146|Chúng ta có thể mua một ít trứng,
147|một ít xà lách và cà chua.
148|Buổi sáng dậy làm, vừa tươi vừa ngon.
149|Tự làm à?
150|Nghe cũng hay, nhưng có phiền phức quá không?
151|Buổi sáng có lẽ tôi không dậy nổi...
152|Không phiền đâu, rất đơn giản.
153|Để tôi làm.
154|Tôi làm rất nhanh.
155|Bạn nghĩ xem, khi ăn sandwich do chính mình làm,
156|chúng ta sẽ cảm thấy đặc biệt ngon.
157|Ồ, bạn làm à?
158|Vậy thì tuyệt quá! Cảm ơn bạn!
159|Tôi thích ăn đồ bạn làm nhất.
160|Vậy tôi muốn ăn hai cái!
161|Một cái nhân trứng,
162|một cái nữa... ừm... bạn tự quyết định nhé,
163|bạn làm gì tôi cũng thích.
164|Không vấn đề gì.
165|Vậy về đồ ăn, chúng ta đã có sandwich.
166|Còn muốn ăn gì nữa?
167|Trái cây! Nhất định phải có trái cây!
168|Thời tiết đẹp như vậy,
169|ăn một chút trái cây ngọt ngọt,
170|sẽ đặc biệt dễ chịu.
171|Tôi muốn ăn dưa hấu!
172|Dưa hấu thật to và thật ngọt!
173|Dưa hấu à?
174|Vương Vũ, bạn nghĩ xem,
175|một quả dưa hấu to rất nặng,
176|chúng ta mang đến công viên bằng cách nào?
177|Chúng ta còn phải bổ ra nữa, rất phiền.
178|Ừ... bạn nói cũng đúng.
179|Dưa hấu rất ngon,
180|nhưng quá nặng và cũng khó mang theo.
181|Vậy... chúng ta đổi loại trái cây khác nhé?
182|Đúng. Chúng ta có thể mua một ít táo,
183|hoặc chuối.
184|Những loại trái cây này rửa sạch là có thể ăn,
185|rất tiện.
186|Chúng ta cũng có thể mua một ít nho,
187|hoặc dâu tây,
188|đựng trong hộp nhỏ.
189|Ý hay! Tôi thích ăn dâu tây!
190|Vậy chúng ta mua dâu tây và táo nhé.
191|Vừa đẹp mắt vừa ngon,
192|lại tiện mang theo.
193|Được.
194|Vậy là chúng ta có sandwich,
195|có trái cây rồi.
196|Còn thiếu đồ ăn vặt,
197|tức là những món ăn nhẹ.
198|Bạn muốn ăn đồ ăn vặt gì?
199|Khoai tây chiên!
200|Tôi rất muốn ăn khoai tây chiên!
201|Còn muốn ăn một ít bánh quy,
202|và sô-cô-la.
203|Được thôi.
204|Nhưng tôi nghĩ,
205|chúng ta cũng có thể chuẩn bị vài món ăn vặt tốt cho sức khỏe.
206|Ví dụ như,
207|một ít các loại hạt,
208|hoặc tự làm một ít salad đơn giản,
209|đựng trong hộp nhỏ.
210|Salad à? Được đấy!
211|Tôi thích ăn salad.
212|Vậy món này ai làm?
213|Không phải lại là bạn đấy chứ?
214|Tất nhiên là tôi.
215|Làm salad rất đơn giản,
216|chỉ cần rửa sạch rau và trái cây,
217|rồi trộn chúng với nhau.
218|Năm phút là làm xong.
219|Lý Minh, bạn tốt quá!
220|Tôi phát hiện ra rằng,
221|đi chơi cùng bạn,
222|tôi chẳng cần làm gì cả,
223|chỉ cần nghĩ xem muốn ăn gì là được.
224|Vì tôi thích lên kế hoạch,
225|thích chuẩn bị.
226|Chuẩn bị đi chơi,
227|cũng giống như nấu ăn vậy.
228|Chúng ta phải chuẩn bị mọi thứ trước,
229|rồi mới có thể làm ra món ăn ngon,
230|và có một chuyến đi vui vẻ.
231|Ừm,
232|tôi thích cách nói này.
233|Vậy chúng ta uống gì?
234|Có cần mang nước không?
235|Nhất định phải mang nước.
236|Mỗi người chúng ta mang một chai lớn.
237|Ngoài nước lọc,
238|bạn còn muốn uống gì?
239|Nước ép trái cây?
240|Coca?
241|Tôi muốn uống trà chanh do chính mình pha.
242|Hôm kia tôi vừa mua một chiếc cốc mới,
243|tôi có thể pha một cốc thật lớn,
244|rồi hai chúng ta cùng uống.
245|Trà chanh do bạn tự pha à?
246|Vậy chắc chắn sẽ ngon lắm.
247|Được, đồ uống cũng đã quyết định.
248|Chúng ta tổng kết danh sách đồ ăn nhé:
249|Sandwich,
250|táo,
251|dâu tây,
252|một ít đồ ăn vặt,
253|salad,
254|nước lọc,
255|và trà chanh của bạn nữa.
256|Bạn thấy đủ chưa?
257|Tôi thấy đủ rồi!
258|Nhiều quá thì chúng ta cũng không ăn hết.
259|Ôi,
260|nhiều đồ ăn ngon như vậy,
261|tôi thật sự mong ngày mai đã là thứ Bảy!
262|Đừng vội,
263|chuẩn bị nhiều thứ như thế,
264|tôi thấy hơi phiền phức,
265|và hơi mệt.
266|Tôi hiểu.
267|Nhưng bạn nghĩ xem,
268|nếu chúng ta chuẩn bị tốt,
269|thì khi đến đó sẽ rất vui,
270|và rất thoải mái.
271|Cái gì cũng có,
272|món gì cũng ngon.
273|Bạn xem,
274|chúng ta có thể viết một danh sách,
275|ghi lại tất cả những thứ cần mua,
276|ngày mai lúc đi siêu thị,
277|cứ nhìn theo danh sách mà mua,
278|như vậy sẽ không quên.
279|Cách này hay đấy!
280|Chúng ta viết danh sách ngay bây giờ đi.
281|Bạn đọc,
282|tôi ghi.
283|Được!
284|Tôi cần mua...
285|Được rồi,
286|đồ ăn và đồ uống,
287|chúng ta đều đã ghi vào danh sách rồi.
288|Chiều mai sau khi tan làm,
289|chúng ta sẽ cùng đi siêu thị mua.
290|Không vấn đề gì.
291|Vậy ngoài đồ ăn,
292|chúng ta còn cần mang thứ gì khác không?
293|Tất nhiên là có.
294|Chúng ta đi dã ngoại mà,
295|một trong những thứ quan trọng nhất là một tấm thảm,
296|chúng ta gọi nó là "thảm dã ngoại".
297|Chúng ta trải nó trên bãi cỏ,
298|rồi có thể ngồi lên trên, rất sạch sẽ.
299|Đúng đúng, cái này rất quan trọng!
300|Hình như nhà tôi có một tấm, lần trước bạn tôi tặng,
301|màu đỏ trắng, rất đẹp.
302|Để tôi tìm thử.
303|Được, vậy bạn phụ trách mang thảm dã ngoại.
304|Chúng ta còn cần mang ít khăn giấy và khăn ướt,
305|để lau tay sau khi ăn.
306|Ừm, cái này tôi cũng mang.
307|Trong túi tôi lúc nào cũng có rất nhiều khăn giấy.
308|Còn cần một túi đựng rác.
309|Sau khi ăn xong,
310|chúng ta phải mang tất cả rác đi,
311|không được để lại trong công viên.
312|Bảo vệ môi trường rất quan trọng.
313|Bạn nói rất đúng.
314|Tôi ghi lại rồi, nhất định sẽ mang.
315|Chúng ta phải là những người biết bảo vệ môi trường.
316|Đúng. Còn gì nữa không?
317|À, đúng rồi, bạn muốn làm gì ở đó?
318|Ý là ngoài ăn uống, chúng ta còn làm gì?
319|Ừm... tôi muốn đọc sách.
320|Trong thời tiết đẹp như vậy,
321|ngồi dưới cây lớn, yên tĩnh đọc sách một lát,
322|chắc chắn sẽ rất dễ chịu.
323|Tôi sẽ mang theo cuốn sách mình thích nhất.
324|Đọc sách, rất hay.
325|Vậy tôi mang máy ảnh nhé.
326|Công viên đó rất đẹp, tôi có thể chụp vài bức ảnh.
327|Chụp phong cảnh và chụp cả bạn nữa.
328|Được chứ! Bạn nhất định phải chụp tôi đẹp một chút nhé!
329|Tôi còn có thể mang chiếc loa nhỏ của mình,
330|chúng ta có thể nghe một chút nhạc.
331|Mở âm lượng nhỏ thôi, không làm phiền người khác.
332|Được. Vậy chúng ta cũng đã có các hoạt động:
333|ăn uống, đọc sách, chụp ảnh và nghe nhạc.
334|Rất thư giãn, tôi thích lắm.
335|Tôi cũng vậy.
336|Vậy câu hỏi cuối cùng, thầy Lý,
337|sáng mai chúng ta xuất phát lúc mấy giờ?
338|Ừm, câu hỏi này rất quan trọng.
339|Tôi đề nghị chúng ta đi sớm một chút.
340|Ví dụ tám giờ rưỡi sáng, chúng ta ra khỏi nhà.
341|Tám giờ rưỡi á?
342|Có sớm quá không?
343|Cuối tuần tôi muốn ngủ thêm một chút.
344|Chín giờ rưỡi, được không?
345|Chín giờ rưỡi cũng được.
346|Nhưng bạn nghĩ xem, chúng ta đi tàu điện ngầm mất một tiếng,
347|đến công viên đã là mười giờ rưỡi rồi.
348|Lúc ấy trong công viên có thể đã rất đông người.
349|Nếu đi sớm hơn thì sẽ ít người hơn,
350|và cũng dễ tìm được một chỗ đẹp.
351|Thời tiết cũng không nóng như buổi trưa.
352|Ừm... bạn nói có lý.
353|Nếu đi muộn, những chỗ đẹp có lẽ đã bị người khác chiếm hết.
354|Được rồi, vậy chịu khó dậy sớm một chút,
355|chúng ta ra khỏi nhà lúc chín giờ, được không?
356|Tôi dậy lúc tám giờ.
357|Ra khỏi nhà lúc chín giờ, được.
358|Tôi không có vấn đề gì.
359|Vậy chúng ta quyết định như thế nhé.
360|Chín giờ sáng thứ Bảy, chúng ta xuất phát đúng giờ.
361|Tuyệt quá!
362|Mọi kế hoạch đều đã chuẩn bị xong!
363|Bây giờ tôi cảm thấy rất yên tâm và rất mong chờ!
364|Có một người bạn giỏi lên kế hoạch thật tốt!
365|Đi chơi cùng một người bạn nhiệt tình như bạn,
366|cũng rất tuyệt.
367|Bạn luôn nghĩ ra rất nhiều điều thú vị.
368|Được, vậy chúng ta xác nhận lần cuối nhé.
369|Thứ Bảy này, chúng ta ra khỏi nhà lúc chín giờ sáng,
370|đi tàu điện ngầm đến Công viên rừng Tây Sơn.
371|Chúng ta mang thảm dã ngoại, khăn giấy và túi rác.
372|Chúng ta còn chuẩn bị rất nhiều đồ ăn ngon.
373|Có những món ngon gì nhỉ?
374|Bạn giúp mọi người tổng kết một chút đi.
375|Được.
376|Đồ ăn chúng ta chuẩn bị gồm có: sandwich,
377|táo, dâu tây, salad và một ít đồ ăn vặt.
378|Đồ uống có nước lọc,
379|và trà chanh do chính tay Vương Vũ pha.
380|Chỉ nghe thôi đã thấy ngon rồi!
381|Tôi không đợi nổi nữa!
382|Lý Minh, cảm ơn bạn đã lên kế hoạch,
383|bây giờ tôi cảm thấy cuối tuần của chúng ta chắc chắn sẽ rất, rất vui.
384|Tôi chắc chắn cũng sẽ rất vui.
385|Được rồi, các bạn đang nghe podcast của chúng tôi thì sao?
386|Cuối tuần này các bạn có kế hoạch gì?
387|Các bạn có thích đi dã ngoại không?
388|Nếu đi dã ngoại,
389|các bạn thích mang theo món ngon gì nhất?
390|Hãy kể cho chúng tôi biết nhé.
391|Đúng vậy, hoan nghênh mọi người để lại bình luận,
392|chia sẻ kế hoạch cuối tuần và những món ăn dã ngoại yêu thích!
393|Được rồi, hôm nay chúng ta trò chuyện đến đây thôi.
394|Chúc mọi người có một cuối tuần thư giãn và vui vẻ.
395|Hẹn gặp lại lần sau!
396|Tạm biệt mọi người! Bye bye!
""".strip()


# ==================================================
# 3. KIEM TRA DU 396 BAN DICH
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
                f"Sai dinh dang ban dich tai dong {line_no}"
            )

        number = int(number_text)

        if number in translations:
            raise ValueError(
                f"Trung so thu tu {number}"
            )

        if not vi.strip():
            raise ValueError(
                f"Thieu ban dich o doan {number}"
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
# 5. GHEP CHU HAN, PINYIN, TIENG VIET
# ==================================================

def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError(
            "JSON nguon khong hop le."
        )

    if data.get("module") != "shadowing":
        raise ValueError(
            "Sai module Shadowing."
        )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "YouTube ID khong khop video 4."
        )

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
                f"Timestamp khong hop le o doan {i}"
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}"
            )

        if i > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Timestamp chong nhau o doan {i}"
            )

        hanzi = str(item["hanzi"]).strip()
        pinyin = make_pinyin(hanzi)
        vi = translations[i]

        if not hanzi or not pinyin or not vi:
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
            long_segments.append(i)

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

        previous_end = end

    # ==================================================
    # 6. LUU JSON HOAN CHINH
    # ==================================================

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
    # 7. TAO BAO CAO
    # ==================================================

    lines = [
        "SHADOWING HSK3 - VIDEO 4",
        f"YouTube: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"So ban dich: {len(translations)}",
        f"Doan ngan < 0.8s: {len(short_segments)}",
        f"Doan dai > 10s: {len(long_segments)}",
        "Timestamp chong nhau: 0",
        "",
        "===== CAC DOAN NGAN ====="
    ]

    for item in short_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "===== CAN RA SOAT =====",
        "032: Ky hieu tieng cuoi.",
        "039, 114, 273, 283: Doan rat ngan.",
        "Kiem tra cac tu da am trong pinyin.",
        "Ban dich can duoc doi chieu voi am thanh.",
        "Khong tu dong ghep cac doan phu de.",
        "",
        "CHUA CAP NHAT SQL SERVER."
    ])

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ==================================================
    # 8. DOC LAI FILE DE XAC MINH
    # ==================================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if saved["youtube_id"] != VIDEO_ID:
        raise RuntimeError(
            "YouTube ID sai."
        )

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError(
            "So doan sau khi luu khong dung."
        )

    for i, (old, new) in enumerate(
        zip(original, saved["sentences"]), 1
    ):
        if float(old["start"]) != new["start"]:
            raise RuntimeError(
                f"Start thay doi o doan {i}"
            )

        if float(old["end"]) != new["end"]:
            raise RuntimeError(
                f"End thay doi o doan {i}"
            )

        if old["hanzi"].strip() != new["hanzi"]:
            raise RuntimeError(
                f"Hanzi thay doi o doan {i}"
            )

        if not new["pinyin"] or not new["vi"]:
            raise RuntimeError(
                f"Thieu pinyin/vi o doan {i}"
            )

    # ==================================================
    # 9. HIEN THI KET QUA
    # ==================================================

    print("===== HSK3 VIDEO 4 - PINYIN VA DICH =====")
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
