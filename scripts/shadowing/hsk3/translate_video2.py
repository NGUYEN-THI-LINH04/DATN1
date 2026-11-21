
import json
import math
from pathlib import Path


# ==================================================
# 1. CAU HINH
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk3")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video2_with_pinyin.json"
OUTPUT = DATA / "video2_translated_full.json"
REPORT = DATA / "video2_translation_report.txt"

VIDEO_ID = "tQKsIFE-Y0g"
EXPECTED_COUNT = 216


# ==================================================
# 2. BAN DICH TIENG VIET - 216 DOAN
#
# Dinh dang: STT|Ban dich
# Moi dong tuong ung voi dung mot doan phu de.
# Cac cau bi ngat giua 2 doan duoc giu rieng
# de khong lam sai timestamp.
# ==================================================

TRANSLATION_TEXT = """
001|Ôi, Lý Minh, tôi vừa đi dự một buổi họp mặt gia đình về, ăn no quá! Bụng tròn vo luôn rồi.
002|Nghe giọng bạn vui vẻ thế này là biết hôm nay chắc chắn đã ăn không ít món ngon.
003|Bạn đã ăn những món gì?
004|Ôi, nhiều lắm!
005|Có món thịt thăn sốt chua ngọt tôi thích nhất, còn có một con cá hấp rất to,
006|do chú tôi làm, ngon đặc biệt luôn.
007|Nhưng nói thật nhé, đôi khi tôi cảm thấy ở Trung Quốc,
008|tham gia những buổi họp mặt gia đình tương đối trang trọng như vậy còn mệt hơn cả việc ăn uống.
009|Ồ? Sao bạn lại nói thế?
010|Ăn uống chẳng phải là một việc rất thú vị và thoải mái sao?
011|Thoải mái thì cũng thoải mái, nhưng có quá nhiều quy tắc!
012|Hôm nay đứa con nhà cô tôi cắm đũa vào bát cơm, kết quả bị ông tôi mắng cho một trận.
013|Tôi ngồi bên cạnh mà cũng cảm thấy hơi căng thẳng.
014|[Cười] Đây quả thực là một quy tắc rất quan trọng trên bàn ăn Trung Quốc.
015|Xem ra hôm nay chúng ta có thể trò chuyện về chủ đề này rồi.
016|Ăn uống không chỉ để no bụng, mà thực ra còn là một nghệ thuật, một nét văn hóa.
017|Đúng, đúng! "Nghệ thuật trên bàn ăn", tôi thích cách nói này.
018|Tôi có rất nhiều câu hỏi muốn hỏi bạn đấy, chắc chắn bạn hiểu biết nhiều hơn tôi.
019|Đừng nói vậy, chúng ta cùng tìm hiểu nhé.
020|Chúng ta hãy bắt đầu từ lúc một bữa tiệc diễn ra nhé. Ví dụ, hôm nay bạn ngồi ở đâu?
021|Tôi à? Tôi tùy tiện tìm một chỗ trống rồi ngồi xuống.
022|Chẳng lẽ chuyện đó cũng có quy tắc sao?
023|Tất nhiên là có.
024|Đây chính là bước đầu tiên trong nghệ thuật bàn ăn.
025|Trời ơi, ngay cả ngồi ở đâu cũng có điều cần học à?
026|Mau kể cho tôi nghe đi.
027|Ở nhà tôi, ngoài ông bà có chỗ ngồi cố định ra thì những người khác đều ngồi tùy ý.
028|Trong những buổi họp mặt gia đình thoải mái, đúng là không cần quá câu nệ.
029|Nhưng nếu là tiệc trang trọng hoặc dịp có khách quan trọng thì việc sắp xếp chỗ ngồi rất quan trọng.
030|Điều đó thể hiện sự tôn trọng dành cho khách.
031|Vậy phải ngồi như thế nào?
032|Vị trí nào là quan trọng nhất?
033|Vị trí quan trọng nhất được gọi là "chủ vị".
034|Thông thường đó là vị trí đối diện cửa ra vào.
035|Vị trí này có tầm nhìn tốt nhất, có thể quan sát cả căn phòng, thuận tiện để chủ tiệc quan tâm đến từng vị khách.
036|Vị trí này thường được dành cho vị khách có địa vị cao nhất, được kính trọng nhất trong buổi tiệc hoặc người lớn tuổi trong gia đình.
037|Ồ! Tôi nhớ ra rồi, hôm nay ông tôi ngồi đúng vị trí đối diện cửa!
038|Hóa ra đó chính là "chủ vị".
039|Vậy chủ tiệc nên ngồi ở đâu?
040|Chủ tiệc thường ngồi đối diện chủ vị, tức là vị trí gần cửa nhất.
041|Như vậy sẽ thuận tiện cho việc phục vụ món ăn hoặc trao đổi với nhân viên nhà hàng.
042|Đôi khi chủ tiệc cũng ngồi cạnh chủ vị để tiện gắp thức ăn hoặc rót đồ uống cho vị khách quan trọng nhất.
043|Tôi hiểu rồi. Vậy chủ vị dành cho khách, còn vị trí của chủ tiệc là để thuận tiện phục vụ mọi người.
044|Thế còn những người trẻ như chúng ta, hoặc những vị khách bình thường, nên ngồi ở đâu?
045|Nói chung, vị trí càng gần chủ vị thì càng quan trọng.
046|Vì vậy, là người nhỏ tuổi hoặc khách bình thường, chọn chỗ ngồi xa chủ vị một chút thường sẽ không sai.
047|Đó là biểu hiện của sự khiêm tốn và tôn trọng.
048|Đúng là một kiến thức rất hữu ích!
049|Trước đây tôi thật sự chưa từng chú ý đến.
050|Đôi khi đi dự những bữa tiệc quan trọng, nhìn thấy chiếc bàn lớn như vậy,
051|có nhiều chỗ trống như thế, tôi hơi sợ, không biết mình nên ngồi đâu.
052|Tôi cảm thấy nếu ngồi sai chỗ sẽ rất ngượng.
053|Tôi hoàn toàn hiểu.
054|Đây quả thực là một khó khăn mà nhiều người chưa quen với văn hóa Trung Quốc thường gặp.
055|Thật ra có một cách rất đơn giản.
056|Cách gì vậy?
057|Đó chính là "đợi".
058|Nếu không chắc mình nên ngồi ở đâu thì đừng vội ngồi xuống.
059|Bạn có thể đứng bên cạnh đợi một lát, chủ tiệc hoặc người tổ chức thường sẽ chủ động sắp xếp chỗ ngồi cho bạn.
060|Như vậy sẽ tránh được việc ngồi sai chỗ.
061|Đúng rồi! Sao tôi lại không nghĩ ra nhỉ!
062|Đợi chủ tiệc sắp xếp, đúng là cách an toàn nhất.
063|Như vậy vừa không ngồi sai vị trí, vừa thể hiện sự lịch sự.
064|Nghe bạn nói thế, tôi thấy đỡ căng thẳng hơn rồi.
065|Đúng vậy, tuy phép tắc trên bàn ăn nghe có vẻ phức tạp, nhưng cốt lõi là tôn trọng và quan tâm đến người khác.
066|Chỉ cần trong lòng bạn có suy nghĩ ấy thì hành động sẽ tự nhiên thể hiện ra.
067|Được rồi, mọi người đều đã ngồi xuống, tiếp theo là đến lúc dùng đũa.
068|Nghệ thuật dùng đũa còn sâu sắc hơn nữa.
069|Nhắc đến đũa, từ nhỏ tôi đã nghe bà kể đủ loại quy tắc.
070|Ví dụ không được dùng đũa gõ vào bát, bà nói làm vậy sẽ trở thành ăn xin.
071|Dù biết đó chỉ là lời nói đùa nhưng tôi vẫn nhớ đến tận bây giờ.
072|[Cười] Bà bạn nói đúng đấy. Đây quả thực là một quan niệm rất phổ biến.
073|Dùng đũa gõ vào bát đĩa được coi là hành động bất lịch sự.
074|Những điều cần chú ý khi dùng đũa thật sự có thể viết thành cả một cuốn sách.
075|Vậy bạn kể cho tôi vài điều quan trọng nhất đi.
076|Ngoài việc không được gõ bát thì còn điều gì nữa?
077|Để tôi nghĩ xem... Điều đầu tiên, cũng là quan trọng nhất, chính là điều chúng ta đã nhắc đến lúc đầu,
078|không được cắm đũa thẳng đứng vào bát cơm.
079|Ừm, điều này tôi biết, vì trông giống như thắp hương cho người đã khuất, được coi là không may mắn.
080|Hoàn toàn chính xác.
081|Điều thứ hai là không được dùng đũa chỉ vào người khác khi nói chuyện.
082|Đũa giống như phần nối dài của ngón tay chúng ta,
083|dùng đũa chỉ vào người khác cũng giống như dùng ngón tay chỉ vào họ, là hành động rất bất lịch sự.
084|Điều này tôi cũng biết! Trước đây bố thường xuyên nhắc tôi.
085|Đôi khi tôi nói chuyện quá hào hứng, tay cầm đũa cứ vung qua vung lại, thậm chí còn chỉ vào người khác,
086|bố sẽ khẽ ho một tiếng để nhắc nhở tôi.
087|Điều đó cho thấy bạn được gia đình dạy dỗ rất tốt.
088|Còn một điều nữa là khi gắp thức ăn, không nên dùng đũa đảo qua đảo lại trong đĩa để tìm món mình thích.
089|Hành động này được gọi là "tìm bằng đũa" hoặc "bới thức ăn", cũng là hành vi bất lịch sự.
090|À, hình như đôi khi tôi cũng làm vậy...
091|Đặc biệt khi nhìn thấy trong một đĩa có món mình rất thích, chẳng hạn thịt, tôi lại muốn tìm thêm vài miếng.
092|Tôi hiểu. Nhưng xét về phép lịch sự, chúng ta nên gắp thức ăn ở phía trước mình, nhìn kỹ rồi mới đưa đũa xuống.
093|Nếu món muốn ăn ở quá xa, bạn có thể nhờ người khác giúp hoặc đợi mâm xoay quay đến trước mặt.
094|Điều này thể hiện sự công bằng và biết nghĩ cho người khác.
095|Bạn nói đúng. Mọi người ăn cùng một bàn thì quả thực phải quan tâm đến cảm nhận của tất cả. Sau này tôi nhất định chú ý.
096|Nghe bạn nói vậy, tôi thấy dùng đũa giống như... giống như đang luyện một môn võ công.
097|Phép so sánh này thú vị đấy.
098|Còn tôi lại thấy dùng đũa giống như viết chữ, đều có nét bút và quy tắc riêng.
099|Mỗi động tác đều thể hiện một thái độ.
100|Cách cầm đũa, động tác gắp thức ăn, vị trí đặt đũa,
101|đều giống như từng chữ Hán, kết hợp với nhau để thể hiện sự tu dưỡng của một người.
102|Ôi, bạn so sánh hay quá! "Dùng đũa giống như viết chữ". Tôi nhớ rồi.
103|Vậy tôi còn một câu hỏi: khi ăn xong hoặc muốn đặt đũa xuống giữa bữa, chúng ta nên đặt đũa như thế nào?
104|Câu hỏi hay. Đũa phải được đặt ngay ngắn bên cạnh bát của mình hoặc trên giá gác đũa.
105|Không được để một chiếc dài một chiếc ngắn, cũng không nên đặt chéo nhau trên bàn, vì những cách đó đều bị coi là không may mắn.
106|Phải đặt hai chiếc đũa song song, ngay ngắn.
107|Được, tôi hiểu rồi. Xem ra một đôi đũa nhỏ bé thật sự ẩn chứa cả một nền văn hóa lớn.
108|Được rồi, chúng ta đã ngồi đúng chỗ, cũng đã biết dùng đũa, vậy tiếp theo,
109|đến phần quan trọng nhất rồi: gọi món và ăn uống!
110|[Cười] Cuối cùng cũng đến phần bạn quan tâm nhất rồi. Gọi món quả thực là cả một nghệ thuật.
111|Đúng vậy! Điều tôi sợ nhất khi đi ăn với bạn bè là mọi người bảo tôi gọi món.
112|Tôi hoàn toàn không biết nên gọi món gì, gọi bao nhiêu. Gọi ít thì sợ mọi người không no, gọi nhiều lại sợ lãng phí.
113|Đó quả thực là điều chủ tiệc hoặc người gọi món cần cân nhắc. Người biết gọi món thường phải suy nghĩ rất nhiều mặt.
114|Chẳng hạn phải hỏi xem mọi người có kiêng món gì không, có ai không ăn cay không?
115|Có ai không ăn hải sản hoặc có người ăn chay không?
116|Ừm, điều này rất quan trọng, phải tôn trọng thói quen ăn uống của mỗi người.
117|Đúng vậy. Tiếp theo, việc kết hợp các món cũng rất quan trọng. Nói chung, một bàn ăn cần có món nguội và món nóng.
118|Trong các món nóng phải có cả món mặn và món rau, tốt nhất màu sắc, hương vị và cách chế biến đều được kết hợp hài hòa.
119|Ví dụ không nên gọi cả bàn toàn món kho hoặc toàn món chiên rán.
120|Tôi hiểu rồi. Phải giống như vẽ tranh, phối hợp nhiều màu sắc và phong cách khác nhau.
121|Ví dụ gọi một món cay thì nên kết hợp với một món thanh đạm; gọi một món thịt thì nên có thêm một món rau.
122|Chính là ý đó. Một bàn ăn như vậy mới khiến mọi người cảm thấy phong phú và dễ chịu.
123|Về số lượng, người Trung Quốc thích gọi món "có dư", tức là nhiều hơn nhu cầu thực tế một chút.
124|Điều đó tượng trưng cho sự nhiệt tình và hào phóng của chủ tiệc.
125|Đặc biệt là món cá, nhất định phải có, vì chữ "cá" và chữ "dư" trong tiếng Trung phát âm giống nhau,
126|tượng trưng cho "năm nào cũng dư dả", cuộc sống sung túc.
127|Ồ! Vậy nên mỗi lần họp mặt trên bàn ăn đều có một con cá! Hóa ra là vì lý do đó.
128|Tôi còn phát hiện nhiều khi đầu cá được quay về phía một người nhất định.
129|Bạn quan sát kỹ thật đấy. Đây lại là một phong tục văn hóa nữa.
130|Đầu cá và phần thịt ngon nhất trên lưng cá thường được hướng về vị khách được kính trọng nhất trên bàn để thể hiện sự tôn trọng.
131|Đôi khi chủ tiệc sẽ gắp một miếng cá cho vị khách ấy trước, rồi mọi người mới bắt đầu ăn món cá đó.
132|Ôi, nhiều chi tiết thật. Tôi cảm thấy ở Trung Quốc, ăn uống không chỉ là thưởng thức hương vị mà còn là tình cảm và các mối quan hệ.
133|Mọi người cùng chia sẻ thức ăn trên một bàn, cảm giác như mối quan hệ lập tức trở nên gần gũi hơn.
134|Tôi đặc biệt thích cảm giác chia sẻ này, không giống kiểu ăn phương Tây mà mỗi người có một đĩa riêng, ai ăn phần người ấy.
135|Đúng vậy, chia sẻ thức ăn là một phần rất quan trọng trong văn hóa của chúng ta.
136|Nó giúp kéo gần khoảng cách giữa người với người.
137|Vì vậy, khi gắp thức ăn cho người khác, cũng nên dùng "đũa chung",
138|tức là một đôi đũa sạch chuyên dùng để gắp thức ăn, như vậy vệ sinh hơn và cũng thể hiện sự tôn trọng người khác.
139|Ừm, hiện nay ngày càng nhiều nhà hàng cung cấp đũa chung, đây là một thói quen rất tốt.
140|Chúng ta đã nói về chỗ ngồi, về đũa và về việc gọi món.
141|Còn một tình huống nữa mà tôi cảm thấy là linh hồn của những bữa tiệc Trung Quốc,
142|nhưng cũng khiến nhiều người nước ngoài, thậm chí cả người trẻ như tôi, cảm thấy sợ.
143|Có phải bạn đang nói đến "mời rượu" không?
144|Chính là nó!
145|[Cười] Tôi biết ngay mà.
146|Văn hóa mời rượu quả thực là một phần rất đặc trưng và cũng khá phức tạp trong văn hóa bàn ăn Trung Quốc.
147|Đúng vậy! Mỗi lần thấy bố tôi và bạn bè của ông mời rượu qua lại, nói rất nhiều lời, tôi đều thấy đau đầu.
148|Tôi cảm giác có quá nhiều quy tắc trong đó, hoàn toàn không hiểu nổi.
149|Thật ra cốt lõi của việc mời rượu vẫn là "tôn trọng" và "biết ơn".
150|Đó là một cách thể hiện tình cảm.
151|Nói chung, việc mời rượu có thứ tự.
152|Đầu tiên là chủ tiệc mời tất cả khách, để thể hiện sự chào đón và cảm ơn.
153|Sau đó là người nhỏ tuổi mời người lớn tuổi, cấp dưới mời cấp trên.
154|Vậy nhất định phải là người có địa vị thấp hơn chủ động mời người có địa vị cao hơn trước, đúng không?
155|Đúng, đó là một phép lịch sự cơ bản.
156|Ví dụ nếu muốn mời một người lớn tuổi hoặc lãnh đạo, bạn cần đứng dậy, hai tay nâng ly rồi đến trước mặt họ.
157|Bạn nên cầm ly của mình thấp hơn ly của họ một chút để thể hiện sự khiêm tốn và tôn kính.
158|À, còn có cả chi tiết này nữa!
159|Khi chạm ly, miệng ly của mình phải thấp hơn miệng ly của đối phương.
160|Đúng vậy.
161|Sau đó, khi mời rượu thường phải nói vài lời chúc.
162|Ví dụ chúc đối phương sức khỏe tốt, công việc thuận lợi, vân vân.
163|Nói xong, người mời thường sẽ nói: "Tôi uống cạn, còn ngài cứ tùy ý."
164|Câu này tôi đã nghe vô số lần rồi!
165|"Tôi uống cạn, còn ngài cứ tùy ý."
166|Ý là tôi uống hết đồ uống trong ly, còn ngài uống bao nhiêu cũng được, để thể hiện thành ý của mình, đúng không?
167|Hoàn toàn chính xác.
168|Đó là một cách thể hiện sự tôn trọng.
169|Tất nhiên, người được mời, đặc biệt là người lớn tuổi, thường cũng sẽ uống hết ly để thể hiện sự công nhận đối với bạn.
170|Trời ơi, nghe mà thấy áp lực quá.
171|Nếu tôi không uống rượu giỏi hoặc hoàn toàn không uống rượu thì phải làm sao?
172|Trong những dịp như thế, dường như không uống rượu sẽ bị coi là không hòa đồng.
173|Câu hỏi này rất hay, cũng là điều nhiều người lo lắng.
174|Thật ra xã hội ngày nay ngày càng cởi mở và quan tâm đến sức khỏe hơn.
175|Nếu thật sự không thể uống rượu, bạn hoàn toàn có thể thay bằng trà, nước ép trái cây hoặc nước lọc.
176|Bạn có thể chân thành giải thích với đối phương,
177|rằng: "Xin lỗi, tôi không uống được rượu, xin dùng trà thay rượu để kính ngài một ly."
178|Thật sự có thể làm vậy sao?
179|Đối phương sẽ không cảm thấy tôi thiếu tôn trọng họ chứ?
180|Chắc chắn là không.
181|Uống rượu không phải mục đích, thể hiện tình cảm mới là điều quan trọng.
182|Chỉ cần thái độ của bạn chân thành, đối phương nhất định sẽ cảm nhận được tấm lòng ấy.
183|Điều mọi người coi trọng là "tình cảm", chứ không phải bạn đã uống bao nhiêu "rượu".
184|Vì vậy, tuyệt đối đừng vì chuyện này mà ép buộc bản thân.
185|Nghe bạn nói như vậy, tôi cảm thấy trút được gánh nặng trong lòng.
186|Trước đây tôi luôn nghĩ mời rượu là một nhiệm vụ giao tiếp rất đáng sợ.
187|Bây giờ tôi hiểu rồi, quan trọng nhất vẫn là sự chân thành.
188|Khi đã thể hiện được tấm lòng, uống gì cũng như nhau.
189|Đúng vậy. Thật ra dù là chỗ ngồi, dùng đũa, gọi món hay mời rượu,
190|tất cả những "quy tắc" và "nghệ thuật" ấy cuối cùng đều hướng đến sự ấm áp và tôn trọng giữa con người với nhau.
191|Khi hiểu được điều đó, bạn sẽ không còn cảm thấy chúng là gánh nặng,
192|mà ngược lại còn có thể cảm nhận được những nét đẹp trong văn hóa của chúng ta.
193|Nghe bạn kể nhiều như vậy, tôi cảm thấy như mình vừa tham gia một tiết học văn hóa rất sinh động.
194|Bữa ăn hôm nay đúng là "bổ dưỡng" quá!
195|[Cười] Hôm nay quả thực chúng ta đã trò chuyện khá nhiều về chủ đề "ăn uống".
196|Chúng ta cùng điểm lại nhé, hôm nay đã nói đến nhiều từ ngữ và khái niệm thú vị.
197|Ví dụ "chủ vị" trong cách sắp xếp chỗ ngồi, thể hiện sự tôn trọng dành cho khách.
198|Ừm! Còn có đủ loại "quy tắc" khi dùng đũa, chẳng hạn không được cắm vào cơm, không được chỉ vào người khác.
199|Tôi nhớ phép so sánh của bạn rồi: "Dùng đũa giống như viết chữ."
200|Đúng.
201|Chúng ta còn nói về cách "gọi món", cần có cả thịt lẫn rau, phối hợp món nóng với món nguội, và còn phải gọi món "cá" để cầu mong "năm nào cũng dư dả".
202|Cuối cùng còn có văn hóa "mời rượu", khiến người ta vừa thích vừa sợ.
203|Điều quan trọng nhất là có thể dùng trà thay rượu, vì điều muốn thể hiện là "tấm lòng".
204|Bạn tổng kết rất đầy đủ.
205|Xem ra hôm nay bạn học được không ít điều.
206|Đúng vậy!
207|Vậy tôi cũng muốn hỏi các bạn đang nghe podcast: ở đất nước của các bạn,
208|hoặc khi các bạn ăn uống ở Trung Quốc, các bạn có từng gặp phép tắc bàn ăn nào thú vị,
209|hoặc khiến các bạn cảm thấy hơi kỳ lạ không?
210|Mời mọi người để lại bình luận và chia sẻ câu chuyện của mình!
211|Ý kiến hay đấy.
212|Chúng tôi rất mong được đọc những chia sẻ của mọi người.
213|Được rồi, hôm nay chúng ta trò chuyện đến đây thôi.
214|Ừm, lần sau trò chuyện tiếp nhé!
215|Tạm biệt!
216|Bye bye!
""".strip()


# ==================================================
# 3. DOC BAN DICH THEO STT
# ==================================================

def load_translations():
    translations = {}

    for line_number, line in enumerate(
        TRANSLATION_TEXT.splitlines(), 1
    ):
        line = line.strip()

        if not line:
            continue

        number_text, separator, vietnamese = (
            line.partition("|")
        )

        if not separator or not number_text.isdigit():
            raise ValueError(
                f"Sai dinh dang ban dich, dong {line_number}"
            )

        number = int(number_text)

        if number in translations:
            raise ValueError(
                f"Trung ban dich doan {number}"
            )

        if not vietnamese.strip():
            raise ValueError(
                f"Doan {number} chua co ban dich"
            )

        translations[number] = vietnamese.strip()

    expected = set(range(1, EXPECTED_COUNT + 1))

    missing = sorted(expected - set(translations))
    extra = sorted(set(translations) - expected)

    if missing or extra:
        raise ValueError(
            f"Thieu: {missing}; Thua: {extra}"
        )

    return translations


# ==================================================
# 4. GHEP BAN DICH VAO FILE PINYIN
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
        raise ValueError(
            "YouTube ID khong khop video 2."
        )

    sentences = data.get("sentences")

    if not isinstance(sentences, list):
        raise ValueError(
            "sentences phai la danh sach."
        )

    if len(sentences) != EXPECTED_COUNT:
        raise ValueError(
            f"Can 216 doan, nhung co {len(sentences)}."
        )

    translations = load_translations()

    result_sentences = []
    short_segments = []
    previous_end = 0.0

    for i, item in enumerate(sentences, 1):

        start = float(item["start"])
        end = float(item["end"])

        hanzi = str(item["hanzi"]).strip()
        pinyin = str(item["pinyin"]).strip()
        vi = translations[i]

        if not all([hanzi, pinyin, vi]):
            raise ValueError(
                f"Doan {i} thieu noi dung."
            )

        if not (
            math.isfinite(start)
            and math.isfinite(end)
        ):
            raise ValueError(
                f"Timestamp khong phai so hop le: {i}"
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}"
            )

        if i > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Timestamp chong nhau o doan {i}"
            )

        duration = round(end - start, 3)

        if duration < 0.8:
            short_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi,
            })

        # Khong thay doi Hanzi, Pinyin, timestamp.
        # Chi bo sung truong dich tieng Viet.
        result_sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi,
        })

        previous_end = end

    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": result_sentences,
    }

    # ==================================================
    # 5. LUU FILE JSON MOI
    # ==================================================

    OUTPUT.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # ==================================================
    # 6. BAO CAO KIEM TRA
    # ==================================================

    report_lines = [
        "SHADOWING HSK3 - VIDEO 2",
        f"YouTube ID: {VIDEO_ID}",
        f"So doan: {len(result_sentences)}",
        f"So ban dich: {len(translations)}",
        f"Doan ngan duoi 0.8s: {len(short_segments)}",
        "",
        "===== DOAN QUA NGAN =====",
    ]

    for item in short_segments:
        report_lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    report_lines.extend([
        "",
        "===== CAN RA SOAT =====",
        "Doan 14, 72, 110, 145, 195: Co ky hieu (笑).",
        "Doan 83-86: Phu de co khoang trang xen giua tu.",
        "Doan 137-138: Cau noi ve dua chung bi ngat.",
        "Doan 215: Thoi gian rat ngan.",
        "Pinyin tu dong can kiem tra tu da am.",
        "Ban dich chua doi chieu toan bo voi am thanh.",
        "",
        "CHUA CAP NHAT SQL SERVER.",
    ])

    REPORT.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    # ==================================================
    # 7. DOC LAI FILE
    # ==================================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if saved["youtube_id"] != VIDEO_ID:
        raise RuntimeError("YouTube ID sai.")

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError("So doan sau luu bi sai.")

    for index, (old, new) in enumerate(
        zip(sentences, saved["sentences"]), 1
    ):
        for field in ("start", "end", "hanzi", "pinyin"):
            if old[field] != new[field]:
                raise RuntimeError(
                    f"Doan {index} bi thay doi {field}"
                )

        if not new["vi"]:
            raise RuntimeError(
                f"Doan {index} thieu ban dich"
            )

    # ==================================================
    # 8. IN KET QUA
    # ==================================================

    print("===== HSK3 VIDEO 2 - DICH TIENG VIET =====")
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(result_sentences))
    print("Da dich:", len(translations))
    print("Doan ngan < 0.8s:", len(short_segments))

    print("\n===== 5 DOAN DAU =====")

    for i, item in enumerate(result_sentences[:5], 1):
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
