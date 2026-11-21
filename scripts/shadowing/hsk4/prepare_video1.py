
import json
import math
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==================================================
# 1. CAU HINH VIDEO HSK4 SO 1
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk4")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video1_zh_preview.json"
OUTPUT = DATA / "video1_translated_full.json"
REPORT = DATA / "video1_review_report.txt"

VIDEO_ID = "qAbVNWgPRJE"
EXPECTED_COUNT = 314


# ==================================================
# 2. BAN DICH TIENG VIET - 314 DOAN
#
# Moi dong: STT|Ban dich
# STT khop voi transcript Supadata.
# ==================================================

TRANSLATION_TEXT = """
001|Xin chào mọi người, chào mừng đến với số mới của chương trình "Tiếng Trung mỗi ngày".
002|Tôi là Lý Minh.
003|Xin chào mọi người, tôi là Vương Vũ.
004|Lý Minh, dạo này bạn thế nào?
005|Trông tâm trạng bạn khá tốt đấy.
006|[Cười] Vậy sao? Dạo này tôi khá ổn, chỉ là công việc hơi bận.
007|Còn bạn thì sao, Vương Vũ? Tôi cũng gần như vậy,
008|nhưng vẫn tranh thủ chút thời gian rảnh giữa lúc bận rộn,
009|mấy hôm trước tôi cùng bạn bè phát hiện một
010|nhà hàng có món ăn đặc biệt ngon, tâm trạng lập tức tốt lên.
011|Sức mạnh của đồ ăn ngon thật sự rất lớn.
012|Tôi hoàn toàn đồng ý. Nói thật nhé,
013|được ăn những món ngon
014|thật sự là một điều vô cùng hạnh phúc trong cuộc sống.
015|"Tiếng Trung mỗi ngày" chính là một chương trình podcast như vậy,
016|chúng tôi hy vọng thông qua những cuộc trò chuyện thoải mái và chân thực,
017|có thể giúp những người bạn đang học tiếng Trung
018|tìm thấy niềm vui học tập trong cuộc sống hằng ngày,
019|để tiếng Trung trở thành một phần cuộc sống của bạn, giống như đồ ăn ngon vậy.
020|Bạn nói hay quá!
021|Chúng tôi hy vọng mọi người có thể nghe chương trình
022|một cách thư giãn, giống như đang nghe bạn bè trò chuyện.
023|Vậy nên, bạn đang nghe chương trình của chúng tôi hôm nay,
024|bây giờ bạn đang làm gì?
025|Bạn đang đi dạo, nấu ăn hay đang trên đường đi làm?
026|Dù bạn ở đâu, chúng tôi cũng rất vui vì có bạn đồng hành.
027|Nhắc đến đồ ăn ngon và nhà hàng, tôi chợt có một ý tưởng.
028|Vương Vũ, vừa rồi bạn nói đã phát hiện một nhà hàng mới.
029|Tôi nghĩ,
030|đối với nhiều người bạn đang học tiếng Trung,
031|việc tự mình đến một nhà hàng Trung Quốc đúng kiểu địa phương
032|có thể là một thử thách không nhỏ.
033|Từ lúc bước vào cửa, gọi món cho đến thanh toán,
034|có thể gặp đủ loại vấn đề.
035|Đúng, đúng! Tôi hoàn toàn hiểu.
036|Khi mới bắt đầu tự ra ngoài ăn,
037|tôi cũng thường cầm thực đơn mà không biết gọi món gì, rất căng thẳng.
038|Hay là chúng ta dành tặng các thính giả
039|một "cẩm nang sinh tồn tại nhà hàng Trung Quốc" nhé?
040|Ý tưởng này tuyệt quá.
041|"Cẩm nang sinh tồn", nghe thú vị thật.
042|Vậy hôm nay chúng ta cùng nói về cách thoải mái
043|và tự tin thưởng thức một bữa ăn ngon ở nhà hàng Trung Quốc nhé.
044|Được, Vương Vũ.
045|Vậy bước đầu tiên trong "cẩm nang sinh tồn"
046|của chúng ta nên bắt đầu từ đâu?
047|Ừm... tôi nghĩ nên bắt đầu từ trước khi đến nhà hàng?
048|Ví dụ, có cần đặt bàn trước không?
049|Lần trước chính vì tôi không đặt bàn,
050|nên phải đợi gần hai tiếng trước một nhà hàng lẩu rất nổi tiếng!
051|Trải nghiệm lần đó thật khó quên.
052|[Cười] Xem ra bạn đã dùng trải nghiệm thực tế để cho chúng ta biết câu trả lời rồi.
053|Đúng vậy, bước đầu tiên chính là "đặt bàn",
054|đặc biệt ở những "nhà hàng nổi tiếng trên mạng" rất được yêu thích,
055|hoặc vào cuối tuần và các ngày lễ.
056|Nếu bạn không muốn mất quá nhiều thời gian xếp hàng,
057|tốt nhất nên gọi điện trước
058|hoặc dùng ứng dụng trên điện thoại để đặt chỗ.
059|Vậy khi gọi điện đặt bàn, chúng ta nên nói thế nào?
060|Rất đơn giản.
061|Sau khi có người nghe máy, bạn có thể nói ngay: "Xin chào,
062|tôi muốn đặt một bàn."
063|Sau đó họ sẽ hỏi:
064|"Mấy người? Khi nào đến?"
065|Bạn chỉ cần nói cho họ số người và thời gian,
066|ví dụ: "Chúng tôi có hai người, tối nay bảy giờ đến."
067|Cuối cùng,
068|họ có thể hỏi họ của bạn và số điện thoại,
069|để tiện liên lạc. Ồ, đơn giản thật!
070|"Xin chào, tôi muốn đặt bàn. Hai người, bảy giờ tối."
071|Chỉ cần nói rõ như vậy là được.
072|Vậy nếu chúng ta không đặt trước mà đến thẳng nhà hàng,
073|sau khi bước vào cửa thì nên làm gì?
074|Khi bước vào nhà hàng, thông thường sẽ có nhân viên phục vụ đón bạn ở cửa.
075|Họ sẽ mỉm cười hỏi: "Xin chào, xin hỏi có mấy người?"
076|Bạn chỉ cần nói cho họ biết số người,
077|ví dụ giơ hai ngón tay lên,
078|rồi nói: "Hai người."
079|Nhân viên phục vụ sẽ dẫn bạn đến bàn,
080|rồi nói: "Mời đi lối này." Tình huống này tôi quá quen rồi.
081|Sau đó nhân viên phục vụ sẽ đưa thực đơn cho chúng ta, đúng không?
082|Tiếp theo mới là phần khó nhất...
083|Đừng vội, chúng ta làm từng bước một.
084|Ngồi vào bàn thuận lợi tức là đã thành công bước đầu tiên.
085|Giống như chơi trò chơi, chúng ta đã vượt qua cửa ải đầu tiên.
086|Được rồi, thầy Lý Minh,
087|bây giờ chúng ta bước vào cửa ải khó nhất: gọi món!
088|Mở thực đơn ra, bên trên toàn chữ Hán dày đặc,
089|đôi khi có hình ảnh thì còn đỡ,
090|nhưng nếu không có hình, tôi thật
091|sự cảm thấy như đang đọc một cuốn "sách trời" không hiểu nổi.
092|Có rất nhiều chữ tôi đều biết,
093|nhưng khi chúng kết hợp lại thành tên một món ăn,
094|thì tôi hoàn toàn không biết đó là món gì.
095|Tôi rất hiểu cảm giác đó,
096|đây có lẽ là một trong những
097|vấn đề khó khăn lớn mà tất cả các bạn học
098|tiếng Trung đều gặp phải. Nhưng thật ra gọi món cũng có mẹo.
099|Trước tiên, bạn có thể
100|tìm xem trên thực đơn có dòng chữ "món được đề xuất"
101|hoặc "món đặc trưng của nhà hàng" hay không.
102|"Món đặc trưng" à? Nghĩa là gì?
103|"Món đặc trưng" là món mà nhà hàng nấu ngon nhất,
104|nổi tiếng nhất và được nhiều người yêu thích nhất.
105|Nói chung, gọi món đặc trưng thường sẽ không sai.
106|Giống như khi bạn đi du lịch đến một thành phố,
107|chắc chắn sẽ đến địa điểm tham quan nổi tiếng nhất ở đó.
108|Vì vậy, khi không biết nên gọi món gì,
109|bạn có thể hỏi thẳng nhân viên phục vụ: "Xin chào,
110|xin hỏi món đặc trưng của nhà hàng mình là gì?"
111|Họ sẽ rất sẵn lòng giới thiệu cho bạn.
112|Ồ, đây là một mẹo vô cùng hữu ích!
113|Hỏi trực tiếp nhân viên phục vụ!
114|Như vậy sẽ không phải đau đầu nhìn thực đơn nữa.
115|Trước đây tôi luôn ngại hỏi,
116|vì sợ họ nghĩ rằng tôi chẳng hiểu gì cả.
117|Hoàn toàn không cần lo lắng.
118|Thật ra khi bạn là người nước ngoài
119|và dùng tiếng Trung để hỏi han, tìm hiểu,
120|đa số mọi người sẽ rất thân thiện và kiên nhẫn giúp đỡ bạn.
121|Ừm, nghe bạn nói vậy, tôi thấy tự tin hơn rồi.
122|Thật ra các bạn đang nghe chúng tôi trò chuyện,
123|nếu có một vài từ hoặc câu
124|mà bạn chưa hiểu ngay thì cũng không sao cả.
125|Bạn có thể dựa vào ngữ điệu và cách chúng tôi nói
126|để đoán ý chính, hoặc bật phụ đề YouTube lên xem.
127|Trên blog của chương trình cũng có toàn bộ nội dung lời thoại,
128|đừng lo, cứ từ từ, học ngôn ngữ chính là một quá trình như vậy.
129|Vương Vũ nói đúng.
130|Quay lại chủ đề gọi món, ngoài việc hỏi nhân viên phục vụ,
131|còn có một cách hay nữa.
132|Bạn có thể kín đáo nhìn xem những vị khách ở bàn bên cạnh đã gọi món gì.
133|Nếu thấy một món trông đặc biệt ngon,
134|thậm chí bạn có thể chỉ vào món đó,
135|rồi hỏi nhân viên phục vụ: "Xin hỏi, đó là món gì?"
136|[Cười] Cách này tôi từng dùng rồi!
137|Thật sự rất hiệu quả!
138|Có lần tôi thấy một đĩa cá ở bàn bên cạnh
139|trông rất thơm ngon nên đã hỏi nhân viên phục vụ,
140|sau đó cũng gọi một phần,
141|kết quả ngon cực kỳ! Đúng không? Cách này gọi là
142|"Cứ ăn theo người địa phương thì thường không sai."
143|Thật ra, gọi món giống như một đạo diễn
144|đang sắp xếp một bộ phim, bạn cần chú ý phối hợp các món trên bàn.
145|Một bữa ăn Trung Quốc hoàn hảo
146|tốt nhất nên có thịt, rau và canh. Về hương vị thì
147|cũng nên có sự thay đổi, ví dụ một món cay,
148|một món không cay.
149|Ồ, hóa ra gọi món cũng có nhiều điều cần học như vậy!
150|Sắp xếp cả bàn ăn như đạo diễn dàn dựng phim, phép so sánh này thú vị đấy.
151|Vậy nếu tôi có một số món không ăn được,
152|ví dụ tôi không ăn cay hoặc không ăn rau mùi,
153|thì nên nói với nhân viên phục vụ thế nào?
154|Điều này rất quan trọng, chúng ta gọi trường hợp đó là "kiêng ăn".
155|Bạn có thể nói rõ với nhân viên phục vụ ngay khi gọi món.
156|Ví dụ khi gọi món "gà xào Cung Bảo", bạn có thể nói:
157|"Món gà xào Cung Bảo, xin đừng cho ớt."
158|Hoặc nói đơn giản hơn:
159|"Món này tôi không muốn ăn cay."
160|Nếu bạn không ăn rau mùi,
161|thì nói: "Xin đừng cho rau mùi." Ồ,
162|"Kiêng ăn", tôi nhớ từ này rồi.
163|Ví dụ: "Tôi có một số thứ phải kiêng,
164|tôi không ăn hải sản." Như vậy nhân viên phục vụ sẽ hiểu.
165|Hoàn toàn chính xác.
166|Chỉ cần bạn nói rõ từ trước,
167|nhà bếp sẽ cố gắng đáp ứng yêu cầu của bạn.
168|Vậy chúng ta tổng kết các mẹo gọi món nhé:
169|Thứ nhất, hỏi nhân viên phục vụ về "món đặc trưng";
170|thứ hai, xem các bàn khác gọi món gì;
171|thứ ba, chú ý kết hợp món mặn và món rau;
172|thứ tư, nói cho nhân viên phục vụ biết những món bạn "kiêng ăn".
173|Nắm được những điểm này, việc gọi món sẽ không còn đáng sợ nữa.
174|Được rồi, chúng ta đã gọi món xong, các món ăn nóng hổi cũng được mang lên.
175|Trong quá trình ăn,
176|có thể chúng ta sẽ cần thêm một vài thứ,
177|ví dụ muốn lấy thêm một bát cơm hoặc thêm nước,
178|lúc ấy nên gọi nhân viên phục vụ thế nào?
179|Tôi không thể cứ liên tục vẫy tay với họ được chứ? [Cười]
180|Tất nhiên bạn có thể vẫy tay.
181|Nhưng cách lịch sự và phổ biến hơn là
182|bạn có thể nói lớn hơn một chút, gọi "Nhân viên phục vụ ơi!".
183|Khi nghe thấy, họ sẽ đến.
184|Chỉ cần gọi ba chữ "nhân viên phục vụ" thôi sao?
185|Đúng vậy. Hoặc bạn cũng có thể nói "Xin chào",
186|chỉ cần thu hút được sự chú ý của họ là được.
187|Sau khi họ đến, bạn có thể nói thẳng nhu cầu của mình.
188|Ví dụ: "Xin chào, cho tôi thêm một bát cơm."
189|Hoặc: "Xin chào,
190|có thể thêm nước giúp chúng tôi không?"
191|Tôi hiểu rồi. "Nhân viên ơi, thêm nước."
192|"Nhân viên ơi, cho thêm một bát cơm." Nói như vậy rất rõ ràng.
193|Vậy nếu tôi muốn dùng khăn giấy ăn thì sao?
194|Bạn có thể hỏi: "Xin hỏi có khăn giấy ăn không?"
195|Thông thường trên bàn ở nhà hàng đều có sẵn,
196|nếu không có, họ sẽ mang đến cho bạn.
197|Đây đều là những cách giao tiếp rất đơn giản và trực tiếp,
198|không cần nghĩ quá phức tạp.
199|Ừm, đúng thật.
200|Khi ăn, điều quan trọng nhất là thư giãn và thưởng thức.
201|Có bất kỳ nhu cầu gì, cứ lịch sự và trực tiếp nói với nhân viên phục vụ là được.
202|Đúng vậy. Thưởng thức món ngon, tận hưởng khoảng thời gian ở
203|bên bạn bè mới là điều quan trọng nhất.
204|Được rồi, sau khi ăn một bữa thật no và thỏa mãn,
205|đến bước cuối cùng, chính là thanh toán.
206|Ở Trung Quốc, tôi phát hiện việc thanh toán là một chuyện
207|đặc biệt thú vị,
208|nhất là khi ăn cùng bạn bè. Ồ?
209|Có gì thú vị vậy?
210|Tôi thường thấy mọi người trong nhà hàng
211|"tranh cãi" xem ai sẽ trả tiền,
212|ai cũng tranh nhau nói: "Để tôi! Để tôi!",
213|rồi lấy điện thoại ra quét mã.
214|Cảnh tượng đó thật sự rất thú vị,
215|cảm giác như mọi người không phải đang tiêu tiền mà đang tranh giành một phần thưởng.
216|[Cười] Bạn quan sát kỹ thật đấy.
217|Đây quả thực là một
218|hiện tượng văn hóa rất đặc trưng trên bàn ăn Trung Quốc, gọi là "tranh nhau trả tiền".
219|Đằng sau đó là cách thể hiện sự hiếu khách và tình bạn.
220|Mọi người đều muốn "mời khách", thông qua việc mời người khác ăn
221|để bày tỏ lòng cảm ơn hoặc tình cảm của mình.
222|Hóa ra là như vậy!
223|Đó là một cách thể hiện tình cảm.
224|Vậy nếu chúng ta ăn cùng bạn bè,
225|và muốn mỗi người tự trả phần của mình thì nói thế nào?
226|Rất đơn giản. Hiện nay khi người trẻ ở Trung Quốc đi ăn cùng nhau,
227|việc ai trả phần người ấy đã rất phổ biến.
228|Bạn có thể nói trực tiếp với bạn bè hoặc nhân viên phục vụ:
229|"Chúng ta mỗi người tự trả phần của mình nhé."
230|Ồ, chỉ cần nói "ai trả phần người ấy" là được, tiện thật!
231|Ngày nay ở Trung Quốc, thanh toán bằng điện thoại rất tiện lợi, ở
232|khắp nơi đều có thể dùng WeChat hoặc Alipay.
233|Đúng vậy, vì thế khi thanh toán,
234|bạn chỉ cần nói với nhân viên phục vụ "Tính tiền",
235|rồi lấy điện thoại ra,
236|họ sẽ mang một mã QR đến để bạn quét,
237|toàn bộ quá trình rất nhanh, chỉ vài giây là hoàn thành.
238|Bạn cũng có thể nói "Thanh toán", nghĩa giống như "Tính tiền".
239|Ừm, "tính tiền" hoặc "thanh toán".
240|Sau đó dùng điện thoại quét mã để trả tiền.
241|Nghe bạn giải thích từng bước như vậy, từ khi bước vào, gọi món,
242|ăn uống cho đến lúc cuối cùng thanh toán,
243|cả quá trình dường như đã trở nên rõ ràng và đơn giản hơn.
244|Đúng vậy. Thật ra khi đến nhà hàng ăn,
245|về bản chất đó là một lần giao tiếp và trải nghiệm.
246|Ngôn ngữ chỉ là một công cụ,
247|quan trọng nhất là dám mở miệng nói và dám hỏi.
248|Dù nói sai hoặc phát âm chưa chuẩn cũng không sao.
249|Hãy dũng cảm bước bước đầu tiên, bạn sẽ nhận ra rằng
250|thưởng thức một bữa ăn Trung Quốc đúng kiểu địa phương thật ra chẳng khó chút nào.
251|Vương Vũ,
252|hôm nay chúng ta đã trò chuyện về toàn bộ quá trình đi ăn nhà hàng,
253|trong đó có một vài từ
254|mà tôi nghĩ rất hữu ích đối với các thính giả.
255|Chúng ta cùng ôn tập một chút nhé?
256|Được chứ! / Lý Minh: Từ đầu tiên là "món đặc trưng". Nếu
257|một thính giả nhìn thấy ba chữ này trên thực đơn,
258|thì chúng có nghĩa là gì?
259|"Món đặc trưng" có nghĩa rất đơn giản,
260|chính là món ngon nhất và nổi tiếng nhất của nhà hàng đó.
261|Nếu bạn không biết gọi món gì thì gọi món đặc trưng chắc chắn không sai!
262|Bạn nói rất hay.
263|Từ thứ hai,
264|là "đúng kiểu địa phương". Chúng ta thường nói nhà hàng này rất "chuẩn vị",
265|vậy "chuẩn vị" có nghĩa là gì?
266|Ừm, "chuẩn vị" có nghĩa là
267|món ăn ở nơi này được chế biến theo cách rất truyền thống,
268|hương vị đặc biệt ngon, giống hệt món người địa phương thường ăn.
269|Đó là một lời đánh giá rất cao.
270|Hoàn toàn chính xác.
271|Từ tiếp theo là "kiêng ăn".
272|Từ này rất quan trọng khi gọi món.
273|"Kiêng ăn" chỉ việc vì lý do sức
274|khỏe hoặc thói quen cá nhân,
275|mà có những món bạn không thể ăn hoặc không thích ăn.
276|Ví dụ có người không ăn cay, có người không ăn thịt,
277|đó đều là những món bạn cần "kiêng ăn".
278|Khi gọi món, nhất định phải nói với nhân viên phục vụ.
279|Bạn giải thích rất rõ ràng.
280|Từ cuối cùng là "tính tiền".
281|"Tính tiền" có nghĩa là trả tiền sau khi ăn xong.
282|Trong nhà hàng bạn cũng có thể nói "thanh toán",
283|hai cách nói có cùng ý nghĩa.
284|Tuyệt quá. Hy vọng những từ này sẽ giúp mọi người
285|tự tin sử dụng hơn trong lần tới đến nhà hàng Trung Quốc.
286|Được rồi, chương trình "Cẩm nang sinh tồn tại nhà hàng Trung Quốc"
287|hôm nay gần đến đây là kết thúc rồi.
288|Chúng ta bắt đầu từ việc đặt bàn, rồi nói về cách gọi món,
289|cách yêu cầu phục vụ trong bữa ăn và cuối cùng là cách thanh toán.
290|Hy vọng nội dung hôm nay mang đến cho mọi người những điều hữu ích.
291|Đúng vậy, hy vọng lần
292|sau khi bước vào một nhà hàng Trung Quốc,
293|mọi người sẽ tự tin hơn và thoải mái thưởng thức những món ngon.
294|Nếu bạn muốn xem toàn bộ
295|lời thoại hôm nay, có thể truy cập blog của chúng tôi.
296|Nếu nội dung hôm nay hữu ích với bạn,
297|hãy nhớ nhấn thích, chia sẻ và đăng ký kênh của chúng tôi.
298|Sự ủng hộ của các bạn
299|là động lực lớn nhất để chúng tôi tiếp tục sáng tạo nội dung,
300|điều đó thật sự rất quan trọng đối với chúng tôi.
301|Chúng tôi cũng rất muốn nghe câu chuyện của mọi người!
302|Chúng tôi muốn hỏi mọi người một câu:
303|Khi đến nhà hàng Trung Quốc,
304|bạn thích gọi món ăn nào nhất?
305|Hoan nghênh mọi người để lại bình luận bên dưới,
306|chia sẻ món Trung Quốc bạn yêu thích nhất và câu chuyện của mình.
307|Nếu bạn có bất kỳ câu hỏi nào về việc học tiếng Trung,
308|cũng có thể hỏi chúng tôi bất cứ lúc nào,
309|chúng tôi sẽ đọc và trả lời từng bình luận một cách nghiêm túc.
310|Biết đâu câu hỏi bạn đưa ra
311|sẽ trở thành chủ đề cho số chương trình tiếp theo của chúng tôi!
312|Mong nhận được những chia sẻ của mọi người.
313|Vậy chương trình hôm nay đến đây thôi.
314|Hẹn gặp lại lần sau! Tạm biệt!
""".strip()


# ==================================================
# 3. DOC BAN DICH THEO SO THU TU
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
                f"Sai dinh dang ban dich o dong {line_no}"
            )

        number = int(number_text)

        if number in translations:
            raise ValueError(
                f"Trung ban dich doan {number}"
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
    # Loai dau cau khoi cach hien thi pinyin,
    # nhung khong thay doi chu Han goc.
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
# 5. DOC PHU DE VA GHEP BAN DICH
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
        raise ValueError("JSON khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module Shadowing.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "Sai YouTube ID cua HSK4 video 1."
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

    translations = load_translations()

    sentences = []
    short_segments = []
    long_segments = []
    previous_end = 0.0

    for i, item in enumerate(original, 1):
        if not isinstance(item, dict):
            raise ValueError(
                f"Doan {i} khong hop le."
            )

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
                f"Doan {i} thieu noi dung."
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

        # Giu nguyen timestamp Supadata
        # va chu Han cua transcript.
        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

        previous_end = end

    # ==================================================
    # 6. LUU JSON MOI - KHONG GHI DE FILE GOC
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
    # 7. BAO CAO CAC DOAN CAN RA SOAT
    # ==================================================

    lines = [
        "SHADOWING HSK4 - VIDEO 1",
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
        "===== CAN DOI CHIEU AM THANH =====",
        "006, 052, 136, 179, 216: Ky hieu (笑).",
        "038-039: Mot y bi cat thanh hai doan.",
        "090-091: Cau bi cat giua hai doan.",
        "096-098: Mot cau bi chia thanh nhieu doan.",
        "256: Phu de co ten nguoi noi.",
        "273-275: Tu bi cat giua hai doan.",
        "Kiem tra 3 doan duoi 0.8 giay.",
        "Kiem tra tu da am trong pinyin.",
        "Ban dich chua doi chieu het voi am thanh.",
        "",
        "CHUA CAP NHAT SQL SERVER."
    ])

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ==================================================
    # 8. DOC LAI VA KIEM TRA KET QUA
    # ==================================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if saved["youtube_id"] != VIDEO_ID:
        raise RuntimeError(
            "Sai YouTube ID sau khi luu."
        )

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError(
            "So doan sau khi luu khong bang 314."
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
                f"Doan {i} thay doi hanzi."
            )

        if not new["pinyin"] or not new["vi"]:
            raise RuntimeError(
                f"Doan {i} thieu pinyin/vi."
            )

    # ==================================================
    # 9. IN KET QUA
    # ==================================================

    print("===== HSK4 VIDEO 1 - PINYIN VA DICH =====")
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
