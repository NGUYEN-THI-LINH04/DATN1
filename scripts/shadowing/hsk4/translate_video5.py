
import json
import math
from pathlib import Path


# ==================================================
# 1. CAU HINH HSK4 - VIDEO 5
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk4")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video5_with_pinyin.json"
OUTPUT = DATA / "video5_translated_full.json"
REPORT = DATA / "video5_translation_report.txt"

VIDEO_ID = "Q1FO6dr5T_Y"
MA_KHOA_HOC = 4
MA_BAI_HOC = 2059
EXPECTED_COUNT = 313


# ==================================================
# 2. BAN DICH TIENG VIET - 313 DOAN
# Dinh dang: STT|Ban dich
# Giu thu tu theo transcript Supadata
# ==================================================

TRANSLATION_TEXT = """
001|Xin chào mọi người, chào mừng đến với số mới của chương trình "Tiếng Trung mỗi ngày".
002|Tôi là Lý Minh.
003|Xin chào mọi người, tôi là Vương Vũ.
004|Lý Minh, nhìn chiếc ốp điện thoại tôi mới mua này, có đẹp không?
005|Ừm, đẹp đấy, màu xanh lam, bên trên còn có một con mèo.
006|Dễ thương thật. Hôm nay hình như bạn cứ xem điện thoại suốt,
007|có chuyện gì thú vị à?
008|[Cười] Bị bạn phát hiện rồi.
009|Vừa rồi tôi đang xem những bài đăng của bạn bè trên WeChat.
010|Một người bạn của tôi đi du lịch Vân Nam, ảnh chụp rất đẹp.
011|Còn một người bạn khác làm bánh trông ngon quá!
012|Tôi cũng muốn học làm.
013|Nghe thú vị đấy.
014|Bây giờ,
015|cuộc sống của chúng ta dường như thật sự không thể thiếu điện thoại,
016|và cũng không thể thiếu mạng xã hội nữa.
017|Mỗi sáng thức dậy, việc đầu tiên của nhiều người là xem điện thoại.
018|Đúng vậy! Tôi cũng thế.
019|Tôi thấy mạng xã hội rất thú vị,
020|có thể biết bạn bè đang làm gì,
021|còn có thể biết nhiều tin tức và những chuyện vui.
022|Đúng vậy, nó mang lại cho chúng ta rất nhiều tiện ích.
023|Nhưng đôi khi tôi cũng cảm thấy
024|mạng xã hội mang đến một số vấn đề.
025|Nó đã thay đổi cuộc sống của chúng ta, có mặt tốt,
026|nhưng có lẽ cũng có mặt không tốt.
027|Ừm, bạn nói có lý.
028|Vậy hay hôm nay chúng ta cùng trò chuyện về
029|chủ đề này nhé: mạng xã hội và cuộc sống hiện đại.
030|Ý kiến hay đấy. Đây là chủ đề mà mỗi chúng ta
031|đều trải nghiệm hằng ngày.
032|Chúng ta có thể chia sẻ
033|cách mình sử dụng mạng xã hội,
034|cũng như ảnh hưởng của nó đối với chúng ta.
035|Hay quá! Vậy để tôi nói trước!
036|Được, Vương Vũ.
037|Bạn nói trước đi.
038|Mạng xã hội bạn thường dùng nhất là gì?
039|Bạn thường làm gì trên đó?
040|Tôi dùng WeChat nhiều nhất.
041|Ngày nào tôi cũng dùng WeChat để trò chuyện với gia đình, bạn bè,
042|và trao đổi công việc với đồng nghiệp.
043|Tất nhiên, tính năng tôi thích nhất vẫn là "Khoảnh khắc".
044|Khoảnh khắc, tính năng này đúng là rất phổ biến.
045|Bạn có thể giới thiệu sơ qua cho những thính giả chưa hiểu rõ không?
046|Tất nhiên. Khoảnh khắc là một tính năng trên WeChat,
047|bạn có thể chia sẻ ảnh,
048|video và những suy nghĩ của mình để bạn bè xem.
049|Bạn bè có thể nhấn thích bài đăng của bạn,
050|cũng có thể bình luận bên dưới và trò chuyện với bạn.
051|Ừm, bạn giải thích rất rõ.
052|Vậy bạn thích chia sẻ những nội dung gì trên Khoảnh khắc?
053|Tôi chia sẻ đủ thứ!
054|Ví dụ hôm nay ăn được món gì ngon,
055|tôi sẽ chụp ảnh rồi đăng lên.
056|Nếu đi đến một nơi thú vị,
057|tôi cũng chia sẻ ảnh và câu chuyện của mình.
058|Hoặc khi xem được phim hay, nghe được bài hát hay,
059|tôi đều chia sẻ cho mọi người.
060|Tôi thấy đây là một cách ghi lại cuộc sống.
061|Nghe vậy chắc trang Khoảnh khắc của bạn thú vị lắm,
062|tràn đầy sự nhiệt tình với cuộc sống.
063|Rất đúng với tính cách của bạn, Vương Vũ. Cảm ơn!
064|Còn bạn thì sao, Lý Minh?
065|Hình như bạn không mấy khi đăng lên Khoảnh khắc.
066|Bạn sử dụng mạng xã hội để làm gì?
067|[Cười] Đúng là tôi đăng rất ít.
068|Tôi dùng mạng xã hội chủ yếu để tìm kiếm thông tin.
069|Ví dụ, tôi sẽ xem một số tin tức,
070|để biết gần đây có những sự kiện quan trọng nào.
071|Ngoài ra,
072|tôi còn theo dõi một số chuyên gia trong những lĩnh vực
073|mình quan tâm, xem kiến thức và quan điểm họ chia sẻ. Ồ,
074|vậy đối với bạn, mạng xã hội giống một công cụ để học tập
075|và làm việc hơn?
076|Có thể nói như vậy.
077|Tôi cũng dùng nó để liên lạc với bạn bè, nhưng
078|rất ít khi chia sẻ cuộc sống cá nhân trên đó.
079|Tôi nghĩ cuộc sống là chuyện riêng của mình, không cần kể cho tất cả mọi người.
080|Hơn nữa, việc chuẩn bị nội dung để đăng, như chọn ảnh,
081|nghĩ lời viết, cũng khá tốn thời gian.
082|Tôi hiểu rồi.
083|Cách hai chúng ta sử dụng mạng xã hội thật sự rất khác nhau.
084|Tôi thích chia sẻ và tương tác, xem nó là một phần cuộc sống.
085|Còn bạn thích xem và học hỏi, coi nó là công cụ hữu ích.
086|Đúng vậy. Tôi nghĩ không có đúng hay sai,
087|chỉ là lựa chọn và thói quen của mỗi người khác nhau.
088|Nhưng dù cách dùng khác nhau,
089|chúng ta đều công nhận mạng xã hội có rất nhiều lợi ích.
090|Chính xác!
091|Vậy tiếp theo chúng ta nói về những lợi ích của nó nhé.
092|Được. Vương Vũ, bạn thấy lợi ích lớn nhất của mạng xã hội là gì?
093|Đối với tôi, lợi ích lớn nhất
094|là có thể giữ liên lạc với bạn bè,
095|đặc biệt là những người lâu ngày không gặp hoặc ở rất xa. Ồ?
096|Bạn có thể cho ví dụ không?
097|Tất nhiên. Tôi có một người bạn học đại học,
098|sau khi tốt nghiệp, cô ấy đến thành phố khác làm việc,
099|chúng tôi ở cách nhau rất xa.
100|Bình thường ai cũng bận làm việc nên ít khi gọi điện.
101|Nhưng ngày nào tôi cũng có thể xem cuộc sống của cô ấy qua Khoảnh khắc.
102|Tôi biết cô ấy đã đổi công việc mới,
103|nuôi một con mèo rất dễ thương, gần đây còn bắt đầu học vẽ.
104|Vậy nên dù hai bạn không thường xuyên trò chuyện,
105|bạn vẫn cảm thấy cô ấy luôn hiện diện trong cuộc sống của mình.
106|Đúng vậy!
107|Thấy cô ấy sống tốt, tôi cũng rất vui.
108|Đôi khi tôi bình luận dưới ảnh của cô ấy,
109|rồi chúng tôi trò chuyện vài câu.
110|Tôi cảm thấy tình bạn không bị xa cách vì khoảng cách địa lý.
111|Nếu không có mạng xã hội, có lẽ chúng tôi đã dần mất liên lạc.
112|Tôi hoàn toàn đồng ý.
113|Đây thực sự là một điểm tuyệt vời của mạng xã hội.
114|Nó giúp chúng ta duy trì mối quan hệ với bạn bè và gia đình.
115|Ví dụ bố mẹ tôi sống ở quê, cách tôi rất xa,
116|nhưng thông qua mạng xã hội,
117|ngày nào tôi cũng có thể xem ảnh của bố mẹ,
118|biết hôm nay họ đã đi dạo trong công viên,
119|hay ăn cơm cùng hàng xóm, điều đó khiến tôi rất yên tâm.
120|Đúng, đúng, đúng! Chính là cảm giác đó.
121|Còn một lợi ích nữa,
122|đó là có thể học được nhiều điều và quen biết nhiều người thú vị.
123|Tôi cũng rất đồng tình với điều này.
124|Như tôi vừa nói, tôi theo dõi một số người sáng tạo nội dung dạy nấu ăn.
125|Video của họ được quay rất tốt, hướng dẫn từng bước cách làm.
126|Làm theo họ, tôi cũng học được vài món ăn mới.
127|Ồ, giỏi quá!
128|Tôi theo dõi nhiều người hướng dẫn phối đồ và trang điểm.
129|Những điều họ chia sẻ đều rất thiết thực,
130|và còn giúp tôi trở nên tự tin hơn.
131|Đôi khi thấy những người mình không quen
132|chia sẻ kinh nghiệm trong phần bình luận,
133|tôi cũng thấy thú vị, như thể quen thêm nhiều bạn mới.
134|Đúng vậy. Thông qua mạng xã hội, chúng ta có thể rất dễ
135|dàng tìm được những người có cùng sở thích.
136|Dù sở thích của bạn là gì, như đọc sách, leo núi,
137|hay yêu động vật nhỏ, bạn đều có thể tìm được một "ngôi nhà" chung,
138|nơi mọi người giao lưu và chia sẻ niềm vui.
139|Chính xác. Tóm lại, mạng xã hội thực sự có rất nhiều lợi ích.
140|Nó giúp chúng ta gắn bó với bạn bè hơn,
141|giúp chúng ta học kiến thức và kỹ năng mới,
142|và còn tìm được những người bạn có chung sở thích.
143|Nó khiến thế giới của chúng ta trở nên rộng lớn hơn.
144|Bạn nói rất hay.
145|Nhưng chuyện gì cũng có hai mặt.
146|Trong khi tận hưởng những lợi ích đó, mạng xã hội
147|có phải cũng mang đến một số vấn đề không?
148|Ừm... đúng vậy.
149|Tôi nghĩ chúng ta nên thẳng thắn nói về mặt xấu của nó.
150|Được. Nói đến mặt xấu của mạng xã hội,
151|từ đầu tiên tôi nghĩ đến chính là "áp lực".
152|Áp lực? Ý bạn là sao?
153|Bạn thử nghĩ xem, những thứ chúng ta nhìn thấy trên mạng xã hội,
154|có phải phần lớn đều là những điều tốt đẹp nhất trong cuộc sống người khác không?
155|Ảnh họ đi du lịch, thành công trong công việc,
156|những khoảnh khắc vui vẻ bên gia đình và bạn bè.
157|Hình như... đúng vậy.
158|Rất ít người chia sẻ việc mình thất bại,
159|hoặc hôm nay tâm trạng rất buồn.
160|Mọi người luôn muốn cho người khác thấy mặt tốt nhất của mình.
161|Vấn đề nằm ở chính chỗ này.
162|Khi mỗi ngày chúng ta nhìn thấy những cuộc sống "hoàn hảo" ấy,
163|chúng ta rất dễ bắt đầu so sánh bản thân với họ.
164|Chúng ta sẽ nghĩ: "Tại sao cuộc sống của người ấy tốt thế?
165|Tại sao người ấy thành công như vậy?
166|Có phải mình chưa đủ tốt không?" À, tôi hoàn toàn hiểu ý bạn rồi.
167|Tôi từng có cảm giác như thế.
168|Đặc biệt khi thấy bạn bè mua xe mới hoặc nhà mới,
169|hay đi đến một nơi mà tôi rất muốn đến
170|nhưng không có tiền để đi, trong lòng tôi hơi khó chịu.
171|Tôi biết mình không nên như vậy, nhưng vẫn không nhịn được mà so sánh.
172|Đó là chuyện bình thường, nhiều người cũng có cảm giác ấy.
173|Mạng xã hội giống như một ô cửa sổ,
174|qua ô cửa ấy, chúng ta nhìn vào cuộc sống của người khác,
175|nhưng những gì chúng ta nhìn thấy
176|chỉ là phần khung cảnh họ muốn cho chúng ta thấy.
177|Chúng ta không nhìn thấy phía sau ô cửa,
178|rằng có lẽ họ cũng rất mệt mỏi và có nhiều phiền muộn.
179|Phép so sánh với "cửa sổ" của bạn hay quá.
180|Chúng ta chỉ thấy phong cảnh đẹp mà quên rằng đó không phải toàn bộ.
181|Áp lực từ việc so sánh này đúng là một vấn đề lớn.
182|Đúng vậy. Ngoài áp lực,
183|còn một vấn đề rất rõ ràng nữa,
184|đó là mạng xã hội làm chúng ta lãng phí rất nhiều thời gian.
185|Điều này tôi phải thừa nhận!
186|Đôi khi
187|tôi chỉ định xem một hai người bạn đăng gì,
188|nhưng rồi tôi bắt đầu xem một video,
189|sau đó lại xem video tiếp theo được đề xuất...
190|Chẳng mấy chốc, một tiếng đồng hồ đã trôi qua.
191|Tôi cũng từng trải qua chuyện như vậy.
192|Ban đầu dự định buổi tối sẽ đọc sách hoặc học bài,
193|nhưng cuối cùng phần lớn thời gian lại dành cho điện thoại.
194|Sáng hôm sau thức dậy, tôi thấy hơi hối hận.
195|Thời gian và sự chú ý của chúng ta cứ thế bị đánh cắp lúc nào không hay.
196|Đúng vậy. Hơn nữa, vì đã quen xem những video ngắn
197|và thú vị, nên bây giờ tôi cảm thấy
198|việc ngồi yên đọc một cuốn sách dường như khó hơn trước.
199|Tôi rất khó tập trung sự chú ý trong thời gian dài.
200|Bạn vừa nhắc đến một vấn đề rất quan trọng.
201|Mạng xã hội đang thay đổi bộ não và thói quen của chúng ta.
202|Nó khiến chúng ta quen với niềm vui nhanh chóng và đơn giản,
203|nhưng đối với những việc cần thời gian,
204|cần suy nghĩ sâu, chúng ta dần mất đi sự kiên nhẫn.
205|Trời ơi, nghe bạn nói vậy,
206|tôi thấy những mặt xấu này khá
207|nghiêm trọng: áp lực, so sánh, lãng phí thời gian,
208|không thể tập trung chú ý...
209|Chúng ta nên làm gì đây?
210|Đây là một câu hỏi rất hay.
211|Chúng ta không thể thiếu mạng xã hội,
212|nhưng cũng không thể để nó kiểm soát cuộc sống của mình.
213|Vì vậy chúng ta phải học cách sử dụng nó hợp lý hơn.
214|Lý Minh, bạn có đề xuất nào hay không?
215|Chúng ta nên làm thế nào
216|để tận hưởng lợi ích của mạng xã hội mà giảm bớt tác hại?
217|Tôi nghĩ bước đầu tiên,
218|cũng là bước quan trọng nhất, là phải sử dụng có ý thức.
219|Chúng ta cần biết rõ mình đang làm gì.
220|Có ý thức? Nghĩa là sao?
221|Nghĩa là trước khi bạn cầm điện thoại lên
222|và mở một ứng dụng mạng xã hội, hãy tự hỏi:
223|"Tại sao bây giờ mình lại muốn xem nó?
224|Mình muốn liên lạc với một người bạn,
225|hay muốn tìm kiếm thông tin,
226|hay chỉ đơn giản là đang thấy buồn chán?"
227|Khi hiểu rõ mục đích của mình, bạn sẽ không dễ bị cuốn vào đó.
228|Ừm, phương pháp này nghe có vẻ hay.
229|Nghĩ trước một chút thay vì mở ngay lập tức. Đúng vậy.
230|Thứ hai, chúng ta có thể tự đặt giới hạn thời gian.
231|Ví dụ, quy định mỗi ngày chỉ vào buổi sáng,
232|buổi trưa và buổi tối, mỗi lần dành mười lăm phút xem mạng xã hội.
233|Những thời gian còn lại thì đặt điện thoại sang một bên,
234|tập trung làm việc của mình.
235|Điều này hơi khó, nhưng tôi nghĩ có thể thử.
236|Giống như chúng ta sắp xếp thời gian làm việc và nghỉ ngơi,
237|cũng đặt thời gian dành cho điện thoại.
238|Đúng vậy. Thứ ba,
239|tôi nghĩ chúng ta có thể thay đổi cách mình "xem" mạng xã hội.
240|Đừng chỉ thụ động tiếp nhận thông tin.
241|Chúng ta có thể chủ động sử dụng nó hơn.
242|Ví dụ, tích cực nhấn thích và bình luận bài đăng của bạn bè thật sự,
243|rồi trò chuyện với họ.
244|Dành ít thời gian hơn cho những nội dung khiến bạn khó chịu
245|hoặc làm lãng phí thời gian.
246|Tôi đồng ý! Chúng ta có thể lựa chọn nội dung mình xem.
247|Nếu có những nội dung luôn khiến tôi cảm thấy áp lực,
248|hay khiến tôi nghĩ cuộc sống của mình chưa đủ tốt,
249|có lẽ tôi nên xem chúng ít hơn.
250|Bạn nói đúng. Điểm cuối cùng,
251|cũng là điều cá nhân tôi thấy quan trọng nhất,
252|chính là phải nhớ rằng:
253|Mạng xã hội không phải toàn bộ cuộc sống thực. Đúng vậy,
254|giống phép so sánh với "cửa sổ" mà bạn đã nói.
255|Đúng vậy. Chúng ta nên dành nhiều thời gian hơn
256|để quan tâm đến cuộc sống thực xung quanh mình.
257|Trò chuyện trực tiếp với gia đình nhiều hơn,
258|ra ngoài đi dạo cùng bạn bè nhiều hơn,
259|cảm nhận ánh nắng và không khí,
260|làm những việc thật sự khiến mình vui vẻ và có cảm giác đạt được thành tựu.
261|Khi cuộc sống của bạn phong phú và trọn vẹn,
262|bạn sẽ không còn quá quan tâm đến những điều
263|"hoàn hảo" trên mạng xã hội nữa. Bạn nói hay quá,
264|Lý Minh. Tôi nhớ có một lần,
265|tôi thấy người khác viết những đoạn văn rất dài bằng tiếng Trung,
266|liền cảm thấy tiếng Trung của mình kém, không dám đăng bài.
267|Nhưng sau đó một người bạn Trung Quốc nói với tôi:
268|Không sao, nói chưa tốt cũng cứ nói, điều quan trọng là giao tiếp.
269|Bạn của bạn nói rất đúng.
270|Đừng so sánh. Bạn có thể bắt đầu từ những điều đơn giản.
271|Ví dụ hôm nay thời tiết rất đẹp,
272|bạn có thể viết bằng tiếng Trung: "Hôm nay thời tiết rất đẹp".
273|Bạn ăn được một món gì đó ngon,
274|thì hãy chụp ảnh và viết: "Món này ngon lắm".
275|Điều quan trọng nhất là bắt đầu và thực sự sử dụng ngôn ngữ này.
276|Ừm! Tôi hiểu rồi.
277|Chúng ta không nên để mạng xã hội tạo ra áp lực trong việc
278|học tập, mà nên coi nó là một công cụ tốt để
279|luyện tập và kết bạn.
280|Đúng vậy. Hãy tìm được một sự cân bằng hợp lý,
281|để mạng xã hội phục vụ cuộc sống của chúng ta,
282|chứ không phải để chúng ta trở thành nô lệ của nó.
283|Được rồi, hôm nay chúng ta đã nói về mạng xã hội
284|và cuộc sống hiện đại.
285|Chúng ta bắt đầu từ những thói quen sử dụng khác nhau của hai người,
286|sau đó trò chuyện về lợi ích và tác hại, cuối cùng thảo luận
287|cách tìm được một sự cân bằng tốt.
288|Đúng vậy, hôm nay chúng ta đã trò chuyện rất sâu.
289|Tôi học được rất nhiều điều.
290|Hy vọng những điều này cũng hữu ích cho các thính giả.
291|Chúng ta cùng tóm tắt ngắn gọn một vài lời khuyên hôm nay nhé.
292|Thứ nhất, trước khi sử dụng mạng xã hội, hãy nghĩ rõ mục đích của mình.
293|Thứ hai, có thể thử đặt giới hạn thời gian sử dụng.
294|Thứ ba, chủ động lựa chọn nội dung xem và tương tác nhiều hơn với bạn bè thật.
295|Cuối cùng, cũng là điều quan trọng nhất,
296|hãy nhớ quan tâm nhiều hơn đến cuộc sống thực, vì đó mới là điều quan trọng nhất.
297|Bạn tổng kết rõ ràng quá!
298|Các thính giả thân mến, nếu muốn ôn lại
299|nội dung cuộc trò chuyện hôm nay, các bạn có thể ghé blog của chúng tôi.
300|Chúng tôi đã đăng toàn bộ lời thoại của mỗi số lên blog.
301|Địa chỉ blog là
302|chinesedailypodcast.blogspot.com.
303|Đúng vậy, hoan nghênh mọi người ghé xem và học tập.
304|Vậy thì, các thính giả thân mến,
305|hôm nay chúng tôi muốn hỏi các bạn:
306|Còn bạn thì sao? Bạn sử dụng mạng xã hội như thế nào?
307|Đối với bạn, nó có những lợi ích và tác hại gì?
308|Bạn có phương pháp hay nào để tìm được sự cân bằng không?
309|Hãy để lại bình luận bên dưới blog của chúng tôi nhé!
310|Chúng tôi rất muốn nghe suy nghĩ của các bạn.
311|Được rồi, số "Tiếng Trung mỗi ngày" hôm nay xin kết thúc tại đây.
312|Cảm ơn mọi người đã lắng nghe.
313|Hẹn gặp lại lần sau! Tạm biệt!
""".strip()


# ==================================================
# 3. KIEM TRA BAN DICH
# ==================================================

def load_translations():

    translations = {}

    for line_number, line in enumerate(
        TRANSLATION_TEXT.splitlines(), 1
    ):

        line = line.strip()

        if not line:
            continue

        number_text, separator, vi = (
            line.partition("|")
        )

        if not separator or not number_text.isdigit():
            raise ValueError(
                f"Sai dinh dang dong {line_number}: "
                f"{line[:80]}"
            )

        number = int(number_text)
        vi = vi.strip()

        if number in translations:
            raise ValueError(
                f"Trung STT {number}"
            )

        if not vi:
            raise ValueError(
                f"Thieu ban dich STT {number}"
            )

        translations[number] = vi

    expected = set(
        range(1, EXPECTED_COUNT + 1)
    )

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
# 4. DOC JSON CO PINYIN
# ==================================================

def load_source():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(
            encoding="utf-8"
        )
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
            "Sai YouTube ID."
        )

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError(
            "Khong co danh sach sentences."
        )

    if len(sentences) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(sentences)}."
        )

    return data


# ==================================================
# 5. GHEP BAN DICH VAO JSON
# ==================================================

def build_sentences(original, translations):

    sentences = []
    previous_end = 0.0

    for i, item in enumerate(original, 1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Doan {i} khong hop le."
            )

        hanzi = str(
            item.get("hanzi", "")
        ).strip()

        pinyin = str(
            item.get("pinyin", "")
        ).strip()

        vi = translations[i]

        if not hanzi or not pinyin or not vi:
            raise ValueError(
                f"Thieu noi dung doan {i}."
            )

        try:
            start = float(item["start"])
            end = float(item["end"])

        except (KeyError, TypeError, ValueError):
            raise ValueError(
                f"Timestamp sai doan {i}."
            )

        if not (
            math.isfinite(start)
            and math.isfinite(end)
        ):
            raise ValueError(
                f"Timestamp khong hop le "
                f"o doan {i}."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Thoi gian sai o doan {i}."
            )

        if (
            i > 1
            and start < previous_end - 0.001
        ):
            raise ValueError(
                f"Timestamp chong nhau "
                f"o doan {i}."
            )

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

        previous_end = end

    return sentences


# ==================================================
# 6. KIEM TRA DU LIEU DA LUU
# ==================================================

def verify_saved(original, document):

    saved = json.loads(
        OUTPUT.read_text(
            encoding="utf-8"
        )
    )

    if saved != document:
        raise RuntimeError(
            "JSON doc lai khong khop."
        )

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError(
            "So doan sau luu khong bang 313."
        )

    for i, (old, new) in enumerate(
        zip(
            original,
            saved["sentences"]
        ), 1
    ):

        if (
            float(old["start"]) != new["start"]
            or float(old["end"]) != new["end"]
            or old["hanzi"].strip() != new["hanzi"]
            or old["pinyin"].strip() != new["pinyin"]
        ):
            raise RuntimeError(
                f"Du lieu goc thay doi "
                f"tai doan {i}."
            )

        if not new["vi"].strip():
            raise RuntimeError(
                f"Thieu tieng Viet doan {i}."
            )


# ==================================================
# 7. MAIN
# ==================================================

def main():

    print(
        "===== HSK4 VIDEO 5 - DICH TIENG VIET ====="
    )

    data = load_source()

    translations = load_translations()

    original = data["sentences"]

    sentences = build_sentences(
        original,
        translations
    )

    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": sentences
    }

    # Luu ra file moi, khong sua JSON pinyin goc.
    OUTPUT.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2,
            allow_nan=False
        ),
        encoding="utf-8"
    )

    verify_saved(
        original,
        document
    )

    # Bao cao
    report_lines = [
        "SHADOWING HSK4 - VIDEO 5",
        "",
        f"YouTube ID: {VIDEO_ID}",
        f"MaKhoaHoc: {MA_KHOA_HOC}",
        f"MaBaiHoc: {MA_BAI_HOC}",
        f"So doan: {len(sentences)}",
        f"So ban dich: {len(translations)}",
        "",
        "JSON: OK",
        "Timestamp va du lieu goc: OK",
        "",
        "CAC DOAN CAN RA SOAT:",
        "072-073: Tu tieng Trung bi ngat.",
        "134-135: Tu tieng Trung bi ngat.",
        "277-279: Tu tieng Trung bi ngat.",
        "Kiem tra cac doan ngan duoi 0.8 giay.",
        "Kiem tra pinyin cua tu da am.",
        "Can doi chieu transcript voi am thanh.",
        "",
        "CHUA CAP NHAT SQL SERVER."
    ]

    REPORT.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    print("YouTube:", VIDEO_ID)
    print("MaKhoaHoc:", MA_KHOA_HOC)
    print("MaBaiHoc:", MA_BAI_HOC)
    print("So doan:", len(sentences))
    print("Da dich:", len(translations))

    print("\n===== 5 DOAN DAU =====")

    for i, item in enumerate(
        sentences[:5], 1
    ):

        print(
            f"\n{i:03d} "
            f"[{item['start']:.2f} - "
            f"{item['end']:.2f}]"
        )

        print(
            "Hanzi:",
            item["hanzi"]
        )

        print(
            "Pinyin:",
            item["pinyin"]
        )

        print(
            "VI:",
            item["vi"]
        )

    print("\n===== FILE DA LUU =====")
    print("JSON:", OUTPUT)
    print("Bao cao:", REPORT)

    print("\nKIEM TRA JSON: OK")
    print("CHUA CAP NHAT SQL SERVER.")


if __name__ == "__main__":
    main()
