
import json
import math
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==================================================
# 1. CAU HINH VIDEO HSK3 SO 3
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk3")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video3_zh_preview.json"
OUTPUT = DATA / "video3_translated_full.json"
REPORT = DATA / "video3_review_report.txt"

VIDEO_ID = "GFPOvOvFgQI"
EXPECTED_COUNT = 274


# ==================================================
# 2. BAN DICH TIENG VIET
# Moi dong: STT|Ban dich
# ==================================================

TRANSLATION_TEXT = """
001|Xin chào mọi người, chào mừng đến với chương trình Tiếng Trung mỗi ngày.
002|Tôi là Lý Minh.
003|Xin chào mọi người, tôi là Vương Vũ.
004|Rất vui được gặp lại mọi người.
005|Đúng vậy, Vương Vũ, chúng ta lại gặp nhau rồi.
006|Tôi ngửi thấy một mùi hương trên người bạn.
007|Mùi hương? Mùi gì cơ?
008|Sáng nay tôi ra khỏi nhà rất vội, không dùng nước hoa mà.
009|Không phải nước hoa.
010|Là mùi cà phê.
011|Sáng nay chắc chắn bạn đã uống cà phê, đúng không?
012|[Cười] Lý Minh, mũi bạn thính thật đấy!
013|Đúng vậy, sáng nào tôi cũng phải uống một cốc cà phê.
014|Không có cà phê, tôi cảm thấy cả ngày không thể bắt đầu được.
015|Còn bạn? Buổi sáng bạn uống gì?
016|Tôi à? Tôi hoàn toàn ngược lại với bạn.
017|Buổi sáng tôi thích từ từ pha một ấm trà.
018|Hương trà khiến tôi cảm thấy rất dễ chịu và yên tĩnh.
019|Trà và cà phê, đúng là một chủ đề thú vị.
020|Ở Trung Quốc, ngày càng nhiều người bắt đầu thích cà phê,
021|nhưng trà đã có lịch sử hàng nghìn năm.
022|Bạn nói đúng.
023|Vì thế hôm nay chúng ta cùng trò chuyện về chủ đề này nhé:
024|Trà hay cà phê?
025|Tại sao bạn lại chọn thức uống đó?
026|Ý hay đấy!
027|Tôi rất muốn nghe lý do bạn thích uống trà đến vậy.
028|Tôi cũng muốn kể cho bạn nghe thế giới cà phê thú vị biết bao!
029|Được, vậy hãy bắt đầu từ lựa chọn của mỗi người nhé.
030|Được, Lý Minh, bạn nói trước đi.
031|Thời gian uống trà mỗi sáng của bạn diễn ra như thế nào?
032|Buổi sáng của tôi rất đơn giản và thong thả.
033|Tôi thường thức dậy lúc bảy giờ sáng.
034|Sau đó tôi vào bếp đun nước trước.
035|Trong lúc đợi nước sôi, tôi chọn loại trà sẽ uống hôm nay.
036|Chọn trà à? Bạn có nhiều loại trà sao?
037|Đúng, tôi có trà xanh, hồng trà và cả trà Phổ Nhĩ.
038|Khi trời nóng, tôi thích uống trà xanh vì cảm giác rất thanh mát.
039|Khi trời lạnh, tôi thích uống hồng trà vì cảm giác rất ấm áp.
040|Nghe chuyên nghiệp thật. Rồi sao nữa?
041|Sau khi nước sôi, tôi dùng nước nóng tráng qua chén và ấm trà để làm chúng ấm lên.
042|Sau đó cho lá trà vào ấm và rót nước nóng vào.
043|Đợi một hai phút là có thể uống rồi.
044|Ồ, nghe bạn kể thì tôi thấy uống trà tốn khá nhiều thời gian.
045|Đúng, cần một chút thời gian, nhưng tôi không thấy đó là lãng phí.
046|Trong lúc ấy tôi có thể không nghĩ gì cả, chỉ nhìn những lá trà từ từ nở ra trong nước.
047|Quá trình này khiến tôi cảm thấy rất thư giãn.
048|Sau đó tôi cầm tách trà ngồi bên cửa sổ, vừa uống trà vừa đọc sách,
049|hoặc nghĩ xem hôm nay mình cần làm những việc gì.
050|Tuyệt vời quá.
051|Nghe giống cuộc sống trong phim vậy.
052|Buổi sáng của tôi hoàn toàn khác bạn.
053|Ồ? Kể tôi nghe đi.
054|Thời gian uống cà phê của bạn như thế nào?
055|Buổi sáng của tôi có thể gói gọn trong một chữ: nhanh!
056|Tôi thường dậy lúc bảy giờ rưỡi, sau đó rửa mặt, thay quần áo,
057|tám giờ là phải ra khỏi nhà.
058|Tôi không có thời gian pha cà phê ở nhà.
059|Vậy bạn uống cà phê ở đâu?
060|Ngay dưới nhà tôi có một quán cà phê.
061|Mỗi ngày khi ra khỏi nhà, tôi đều ghé đó mua một cốc latte.
062|Tôi thích vừa đi bộ vừa uống cà phê.
063|Cà phê nóng khiến tôi cảm thấy rất tỉnh táo.
064|Vậy ngày nào bạn cũng đến cùng một quán cà phê sao?
065|Đúng. Nhân viên quán đó đều quen mặt tôi rồi.
066|Hễ thấy tôi, họ hỏi: “Cô Vương, hôm nay vẫn là một ly latte nóng chứ?”
067|Tôi thấy như vậy rất thân thiện, lại nhanh chóng và tiện lợi.
068|Tôi hiểu rồi.
069|Vậy tôi chọn trà vì thích nhịp sống chậm rãi vào buổi sáng.
070|Còn bạn chọn cà phê vì cần sự nhanh chóng và tiện lợi.
071|Có thể nói như vậy.
072|Tôi thấy cà phê rất giống nhịp sống ở thành phố hiện đại, rất nhanh.
073|Còn trà giống một lối sống truyền thống hơn, cần từ từ thưởng thức.
074|Vương Vũ, vừa rồi bạn nói mình uống cà phê để tỉnh táo.
075|Ngoài điều đó ra còn lý do nào khác không?
076|Vì sao bạn thích cà phê đến vậy?
077|Ừm, câu hỏi hay đấy.
078|Tôi nghĩ thứ nhất là tôi thật sự rất thích hương vị cà phê.
079|Hơi đắng nhưng lại rất thơm.
080|Đặc biệt là latte, vì có sữa nên hương vị ngon hơn.
081|Tôi từng uống cà phê Americano một lần, đắng quá nên không thích lắm.
082|[Cười] Americano đúng là khá đắng.
083|Bạn có thể thử latte hoặc cappuccino.
084|Thứ hai, như tôi vừa nói, cà phê giúp tôi nhanh chóng tỉnh táo để bắt đầu một ngày làm việc.
085|Bạn biết đấy, công việc của tôi cần nghĩ ra nhiều ý tưởng mới, cà phê có thể giúp tôi.
086|Tôi hiểu.
087|Còn một lý do rất quan trọng: tôi thích không gian quán cà phê.
088|Cuối tuần, tôi thường đến quán cà phê gặp bạn bè.
089|Các bạn làm gì ở quán cà phê?
090|Trò chuyện chứ!
091|Hoặc cùng nhau đọc sách,
092|hay dùng máy tính làm việc.
093|Không gian quán cà phê rất đẹp, có ghế ngồi thoải mái và âm nhạc dễ nghe.
094|Mọi người đều làm việc riêng của mình ở đó, cảm giác rất tự do và dễ chịu.
095|Tôi thấy quán cà phê giờ là nơi giao lưu được nhiều người trẻ yêu thích.
096|Điều này đúng thật.
097|Bây giờ trên các con phố ở Bắc Kinh, Thượng Hải, đâu đâu cũng có quán cà phê.
098|Thỉnh thoảng đi ngang qua, tôi cũng thấy bên trong đầy người trẻ.
099|Vậy để tôi hỏi bạn, bạn có nghĩ uống trà chỉ là việc của người lớn tuổi không?
100|Trước đây có lẽ tôi đã nghĩ vậy.
101|Nhưng sau khi quen bạn, tôi không còn nghĩ thế nữa.
102|Bạn có già đâu, haha.
103|Còn bạn thì sao?
104|Lý Minh, vì sao bạn thích trà đến vậy?
105|Chỉ vì trà giúp bạn thư giãn thôi sao?
106|Thư giãn là một lý do.
107|Còn một lý do rất quan trọng nữa, tôi nghĩ uống trà tốt cho sức khỏe.
108|Tốt cho sức khỏe à? Ý bạn là sao?
109|Nhiều sách nói rằng lá trà chứa nhiều chất có lợi cho cơ thể.
110|Ví dụ, trà xanh có thể giúp làm chậm quá trình lão hóa.
111|Tất nhiên, phải uống trong thời gian dài mới có tác dụng.
112|Hơn nữa, uống trà không thêm đường hay sữa nên không có nhiều calo và không dễ khiến bạn tăng cân.
113|Ừm, điều đó cũng đúng.
114|Latte tôi uống có khá nhiều sữa, có lẽ lượng calo không thấp.
115|Ngoài ra tôi thấy uống trà còn là một nét văn hóa.
116|Trà đã có lịch sử hàng nghìn năm ở Trung Quốc.
117|Các văn nhân thời xưa thích vừa uống trà vừa viết chữ, vẽ tranh.
118|Tôi cảm thấy khi uống trà, mình có thể cảm nhận được nét văn hóa Trung Hoa ấy.
119|Ồ, bạn kể chuyện uống trà thú vị quá.
120|Trước đây tôi nghĩ uống trà chỉ là uống một cốc nước nóng.
121|Không giống nhau đâu.
122|Mỗi loại trà có hương vị khác nhau, cần nhiệt độ nước khác nhau,
123|và thời gian pha cũng khác nhau.
124|Trong đó có rất nhiều kiến thức.
125|Tôi thấy bản thân việc tìm hiểu những kiến thức ấy đã rất thú vị rồi.
126|Nghe có vẻ bạn thật sự yêu trà.
127|Cũng giống như tôi rất yêu cà phê.
128|Đúng vậy.
129|Chúng ta đều đã tìm được thức uống mình yêu thích.
130|Lý Minh, vừa rồi bạn nói trà là nét văn hóa hàng nghìn năm của Trung Quốc.
131|Nhưng hiện nay tôi thấy cà phê cũng đang trở nên rất, rất phổ biến ở Trung Quốc.
132|Bạn nghĩ sao?
133|Tôi hoàn toàn đồng ý.
134|Đặc biệt trong mười năm gần đây, quán cà phê ở Trung Quốc mở ra ngày càng nhiều.
135|Thời bố mẹ tôi, rất ít người uống cà phê.
136|Họ nghĩ thức uống đó vừa đen vừa đắng, không ngon.
137|Đúng, mẹ tôi cũng vậy.
138|Khi mẹ đến Bắc Kinh thăm tôi, tôi đưa mẹ đến quán cà phê, mẹ gọi một cốc latte,
139|uống một ngụm rồi bảo: “Đây là cái gì thế? Không ngon.”
140|[Cười] Có lẽ mẹ chúng ta giống nhau thật.
141|Nhưng bạn thấy đấy, thế hệ chúng ta và cả những người trẻ hơn,
142|nhiều người đã bắt đầu chấp nhận và yêu thích cà phê.
143|Tôi nghĩ điều đó cho thấy Trung Quốc ngày càng cởi mở và hội nhập quốc tế hơn.
144|Chúng ta sẵn sàng tìm hiểu và tiếp nhận văn hóa, lối sống của các nước khác.
145|Tôi đồng ý.
146|Quán cà phê cũng trở thành một không gian giao lưu mới.
147|Trước đây, mọi người gặp bạn bè có thể đến quán trà hoặc nhà hàng.
148|Bây giờ nhiều người sẽ nói: “Chúng ta tìm quán cà phê ngồi chơi nhé.”
149|Đúng vậy.
150|Nhưng dù cà phê rất phổ biến,
151|trà vẫn giữ vị trí rất quan trọng trong lòng người Trung Quốc.
152|Ở nhà tôi, khi có khách đến, việc đầu tiên bố mẹ tôi làm là pha trà mời khách.
153|Đúng, đó là phép lịch sự của người Trung Quốc.
154|Đúng vậy.
155|Dùng một tách trà ngon để chào đón bạn bè,
156|thể hiện sự tôn trọng và lòng hiếu khách của chúng ta.
157|Hơn nữa, ở một số nơi miền Nam Trung Quốc, uống trà là một thói quen sinh hoạt rất quan trọng.
158|Ví dụ ở Quảng Đông, mọi người buổi sáng đến trà lâu để “uống trà sáng”.
159|Tôi từng nghe nói đến “uống trà sáng”!
160|Có phải có thể vừa uống trà vừa ăn nhiều món điểm tâm ngon không?
161|Hoàn toàn chính xác!
162|“Uống trà sáng” không chỉ là uống trà, quan trọng hơn là ở bên gia đình và bạn bè,
163|thong thả ăn uống và trò chuyện.
164|Đó là một lối sống rất dễ chịu.
165|Hay quá, sau này nhất định tôi phải đến Quảng Đông thử một lần.
166|Nhắc đến văn hóa trà, tôi từng nghe một từ gọi là “trà công phu”.
167|Chữ “công phu” ở đây có giống võ công Trung Quốc mà chúng ta thường nói không?
168|[Cười] Đây là một câu hỏi rất hay!
169|Nhiều bạn học tiếng Trung có lẽ cũng có thắc mắc này.
170|“Công phu” ở đây không phải công phu đánh võ.
171|Ở đây, “công phu” có nghĩa là thời gian và công sức.
172|Thời gian và công sức ư?
173|Đúng.
174|“Trà công phu” nghĩa là bạn cần bỏ ra rất nhiều thời gian và tâm sức,
175|để pha một tách trà thật cẩn thận.
176|Bộ dụng cụ pha trà của nó rất nhỏ, chén trà cũng nhỏ xíu,
177|có lẽ chỉ một ngụm là uống hết.
178|Quy trình pha trà cũng khá phức tạp.
179|Sao phải cầu kỳ như vậy?
180|Vì chính quá trình đó đã là một sự tận hưởng.
181|Mọi người ngồi cùng nhau, nhìn một người thong thả tráng bộ trà cụ,
182|pha trà rồi rót trà.
183|Quá trình ấy rất yên tĩnh, khiến con người tĩnh tâm lại.
184|Đây là một cách giao lưu rất truyền thống. Cùng bạn bè uống “trà công phu”,
185|có thể trò chuyện rất lâu.
186|Tôi hiểu rồi.
187|Vậy trọng tâm của “trà công phu” không phải ở việc uống, mà là quá trình pha và thời gian cùng nhau trò chuyện.
188|Đúng là một nét văn hóa rất thú vị.
189|Đúng vậy.
190|Vì thế bạn thấy đấy, cà phê đại diện cho một phương thức giao lưu mới, mang tính quốc tế,
191|với nhịp sống nhanh.
192|Còn trà, đặc biệt là trà công phu, đại diện cho một phương thức giao lưu truyền thống,
193|yên tĩnh và có nhịp độ chậm.
194|Hiện nay cả hai hình thức đều tồn tại ở Trung Quốc, tôi thấy điều đó rất tốt.
195|Lý Minh, hôm nay trò chuyện với bạn nhiều điều về trà và cà phê, tôi đã học được rất nhiều.
196|Tôi cũng rất vui.
197|Thật ra, Vương Vũ, tôi thấy chuyện uống trà, uống cà phê
198|cũng có vài điểm giống với việc chúng ta học tiếng Trung.
199|Ồ? Ý bạn là sao? Nghe thú vị đấy.
200|Tôi thấy quá trình học tiếng Trung giống như pha một tách trà công phu.
201|Giống pha trà công phu ư? Tại sao?
202|Bạn nghĩ xem, để pha trà công phu, bạn cần kiên nhẫn, cần thời gian,
203|phải làm từng bước một, không thể vội vàng.
204|Nếu quá vội, nước nóng quá thì trà sẽ không ngon.
205|Nếu thời gian pha quá ngắn, hương vị trà chưa kịp ngấm ra.
206|Học tiếng Trung chẳng phải cũng vậy sao?
207|Hình như tôi đã hiểu được một chút rồi.
208|Bạn không thể hy vọng hôm nay học thì ngày mai tiếng Trung đã trở nên cực kỳ giỏi.
209|Bạn cần dành một ít thời gian mỗi ngày, giống như hằng ngày tráng trà cụ,
210|đun nước và pha trà vậy.
211|Hôm nay nhớ năm chữ Hán, ngày mai luyện một câu.
212|Mỗi ngày làm một chút, dần dần theo thời gian,
213|thì tách “trà tiếng Trung” của bạn mới có thể cho ra hương vị ngon.
214|Đó chính là “công phu”.
215|Bạn so sánh hay quá!
216|Học tiếng Trung thật sự cần “công phu”.
217|Đôi khi tôi thật sự cảm thấy rất sốt ruột.
218|Tôi nghĩ mình đã học lâu như thế, sao vẫn nói chưa tốt, nghe vẫn không hiểu.
219|Tôi cứ mong bản thân tiến bộ nhanh hơn, nhanh hơn nữa.
220|Tôi rất hiểu.
221|Có lẽ ai học tiếng Trung cũng từng trải qua giai đoạn như thế.
222|Sẽ cảm thấy rất mệt mỏi, không nhìn thấy tiến bộ của mình.
223|Đúng! Chính là cảm giác đó!
224|Tôi ước việc học tiếng Trung giống như uống cà phê, uống vào là tỉnh táo ngay,
225|và lập tức nhìn thấy kết quả.
226|Nhưng tôi biết chuyện ấy là không thể.
227|Lý Minh, bạn có lời khuyên nào hay không?
228|Tôi nghĩ khi cảm thấy sốt ruột, bạn đừng quá khắt khe với bản thân.
229|Bạn có thể nghỉ ngơi một chút.
230|Hoặc thay đổi phương pháp học.
231|Ví dụ, nếu cứ đọc sách mãi khiến bạn thấy chán, bạn có thể thử xem một
232|bộ phim Trung Quốc đơn giản hoặc nghe một bài hát tiếng Trung.
233|Ừm, đó là cách hay.
234|Quan trọng nhất là phải tin vào sức mạnh của “công phu”.
235|Hãy tin rằng thời gian và công sức bạn bỏ ra mỗi ngày đều không lãng phí.
236|Giống như pha trà, mỗi bước bạn làm cuối cùng đều ảnh hưởng đến hương vị trà.
237|Vậy nên đừng vội, cứ từ từ. Hãy tận hưởng quá trình học tiếng Trung,
238|giống như tận hưởng quá trình pha trà vậy.
239|Cảm ơn bạn, Lý Minh.
240|Nghe bạn nói như vậy, tôi cảm thấy tốt hơn nhiều rồi.
241|Sau này tôi sẽ coi việc học tiếng Trung như đang pha cho mình một tách “trà công phu”.
242|Cần kiên nhẫn và cũng phải tận hưởng quá trình ấy.
243|Đúng. Chúng ta có thể lựa chọn
244|sống nhanh như khi uống cà phê.
245|Nhưng cũng cần dành cho mình những khoảng thời gian chậm lại như khi uống trà,
246|đặc biệt là lúc học tập.
247|Bạn nói hay quá.
248|Được rồi, hôm nay chúng ta đã nói nhiều về trà và cà phê, cũng gần hết giờ rồi.
249|Đúng vậy, thời gian trôi nhanh thật.
250|Hôm nay chúng ta đã trò chuyện về trà và cà phê.
251|Vương Vũ thích cà phê vì nó đại diện cho lối sống hiện đại, nhanh chóng, hơn nữa
252|quán cà phê cũng là một không gian giao lưu rất tốt.
253|Tôi thích trà vì nó tốt cho sức khỏe và đại diện cho nét văn hóa truyền thống Trung Quốc, biết sống chậm lại,
254|và tận hưởng quá trình.
255|Đúng! Quan trọng nhất là chúng ta nhận ra rằng,
256|học tiếng Trung giống như pha một tách “trà công phu” Trung Quốc.
257|Việc đó cần thời gian, cần kiên nhẫn và cần chúng ta tận hưởng quá trình,
258|chứ không chỉ nghĩ đến một kết quả thật nhanh.
259|Đúng!
260|Nếu mọi người muốn xem toàn bộ nội dung cuộc trò chuyện hôm nay,
261|có thể ghé blog của chúng tôi.
262|Địa chỉ blog của chúng tôi là
263|chinesedailypodcast.blogspot.com.
264|Đúng vậy, rất hoan nghênh mọi người ghé xem.
265|Vậy còn các thính giả đang nghe chúng tôi, các bạn thì sao?
266|Các bạn thích uống trà hay cà phê?
267|Hoặc các bạn thấy học tiếng Trung giống với điều gì hơn?
268|Hãy để lại bình luận bên dưới blog và cho chúng tôi biết nhé!
269|Chúng tôi rất muốn nghe câu chuyện của các bạn.
270|Được rồi, chương trình Tiếng Trung mỗi ngày hôm nay đến đây thôi.
271|Cảm ơn mọi người đã lắng nghe.
272|Tôi là Vương Vũ.
273|Tôi là Lý Minh.
274|Hẹn gặp lại lần sau! Tạm biệt!
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
                f"Ban dich sai dinh dang tai dong {line_no}"
            )

        number = int(number_text)

        if number in translations:
            raise ValueError(
                f"Trung so thu tu {number}"
            )

        if not vi.strip():
            raise ValueError(
                f"Thieu ban dich doan {number}"
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
# 4. TAO PINYIN CO DAU
# ==================================================

def make_pinyin(hanzi):

    # Giu nguyen website neu doan la dia chi blog
    if "chinesedailypodcast.blogspot.com" in hanzi:
        return "chinesedailypodcast.blogspot.com"

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
            f"Khong tim thay: {SOURCE}"
        )

    source = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(source, dict):
        raise ValueError("JSON nguon khong hop le.")

    if source.get("module") != "shadowing":
        raise ValueError("Sai module Shadowing.")

    if source.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "YouTube ID khong khop video 3."
        )

    original = source.get("sentences")

    if not isinstance(original, list):
        raise ValueError("sentences phai la list.")

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can 274 doan, hien co {len(original)}."
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
        vi = translations[i]
        pinyin = make_pinyin(hanzi)

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
    # 6. LUU JSON MOI
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
    # 7. BAO CAO KIEM TRA
    # ==================================================

    lines = [
        "SHADOWING HSK3 - VIDEO 3",
        f"YouTube: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"So ban dich: {len(translations)}",
        f"Doan ngan < 0.8s: {len(short_segments)}",
        f"Doan dai > 10s: {len(long_segments)}",
        "Timestamp chong nhau: 0",
        "",
        "CAC DOAN NGAN:"
    ]

    for item in short_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "CAC VI TRI CAN DOI CHIEU:",
        "012, 082, 140, 168: ky hieu (笑).",
        "048-049: cau bi chia thanh hai doan.",
        "197-198: cau bi chia thanh hai doan.",
        "231-232: cau bi chia thanh hai doan.",
        "263: dia chi blog.",
        "Kiem tra 5 doan duoi 0.8 giay.",
        "Kiem tra cac tu da am trong pinyin.",
        "Ban dich can duoc doi chieu am thanh goc.",
        "",
        "CHUA CAP NHAT SQL SERVER."
    ])

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ==================================================
    # 8. DOC LAI VA XAC MINH
    # ==================================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    assert saved["youtube_id"] == VIDEO_ID
    assert len(saved["sentences"]) == EXPECTED_COUNT

    for old, new in zip(
        original,
        saved["sentences"]
    ):
        assert float(old["start"]) == new["start"]
        assert float(old["end"]) == new["end"]
        assert old["hanzi"].strip() == new["hanzi"]
        assert new["pinyin"]
        assert new["vi"]

    # ==================================================
    # 9. IN KET QUA
    # ==================================================

    print("===== HSK3 VIDEO 3 - PINYIN VA DICH =====")
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
