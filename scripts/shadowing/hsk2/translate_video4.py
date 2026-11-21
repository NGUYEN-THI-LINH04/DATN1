
import json
from pathlib import Path

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2\data\processed")
SOURCE = BASE / "video4_with_pinyin.json"
OUTPUT = BASE / "video4_translated_full.json"

VIDEO_ID = "O_kkptuQPY8"

# Moi dong tuong ung voi mot doan phu de,
# theo thu tu 001 den 171 trong transcript.
TRANSLATIONS = [
    # 001 - 010
    "Lý Minh, tôi ngửi thấy mùi thơm quá trong văn phòng của bạn! Trưa nay bạn đi ăn món gì ngon phải không? Mau kể đi, bạn đã ăn gì thế?",
    "Haha, mũi bạn thính thật đấy. Trưa nay tôi đi ăn cùng một người bạn. Chúng tôi đến một quán mì mới.",
    "Quán mì à? Mì gì thế? Có gì đặc biệt không?",
    "Là mì bò. Nhưng thịt bò ở quán đó được chế biến rất ngon, miếng thịt vừa to vừa ngon. Nước dùng cũng rất ngon. Tôi đã uống rất nhiều nước dùng.",
    "Ôi, nghe bạn kể mà tôi đói rồi. Mặc dù tôi cũng rất thích ăn mì, nhưng tôi nghĩ món ăn yêu thích nhất của mình không phải là mì.",
    "Ồ? Vậy bạn thích ăn món gì nhất? Hình như tôi chưa từng hỏi bạn câu này.",
    "Ừm... Để tôi suy nghĩ một chút.",
    "Nghĩ xem món mình thích nhất là gì... Tôi nghĩ món ăn tôi thích nhất chắc chắn là món mẹ tôi nấu.",
    "Món mẹ nấu à? Câu trả lời thật ấm áp. Cụ thể là món nào vậy? Mẹ bạn chắc nấu ăn rất giỏi và biết làm nhiều món ngon nhỉ?",
    "Đúng vậy, mẹ tôi nấu được rất nhiều món. Nhưng nếu nói đến món thích nhất thì chắc chắn là cà chua xào trứng.",

    # 011 - 020
    "Cà chua xào trứng à? Đây là món ăn gia đình rất quen thuộc. Nhiều gia đình Trung Quốc đều biết làm. Tại sao đó lại là món bạn thích nhất?",
    "Đúng vậy, món này rất đơn giản và bình thường. Nhưng mỗi lần ăn, tôi đều cảm thấy vô cùng hạnh phúc.",
    "Còn bạn thì sao, Lý Minh? Đừng chỉ hỏi tôi chứ. Món ăn bạn thích nhất là gì?",
    "Tôi à? Tôi nghĩ món tôi thích nhất có lẽ là vịt quay Bắc Kinh ở một nhà hàng.",
    "Vịt quay Bắc Kinh! Ôi, đó là món ăn Trung Quốc rất nổi tiếng!",
    "Bạn thấy đấy, hai chúng ta thật khác nhau. Tôi thích món ăn gia đình đơn giản nhất, còn bạn thích món ăn thịnh soạn ở nhà hàng nổi tiếng.",
    "Haha, đúng vậy. Một món ăn ở nhà, một món ăn bên ngoài. Một món rất đơn giản, một món thì không.",
    "Hay hôm nay chúng ta cùng trò chuyện về những món ăn yêu thích và những câu chuyện đằng sau chúng, được không?",
    "Ý kiến hay quá! Tôi đã sẵn sàng nghe câu chuyện về vịt quay Bắc Kinh của bạn rồi.",
    "Được. Vậy trước tiên chúng ta nói xem tại sao mình lại thích hai món ăn rất khác nhau này nhé.",

    # 021 - 030
    "Vương Vũ, bạn nói trước nhé? Tại sao lại là cà chua xào trứng?",
    "Ừm, được thôi. Tôi thích cà chua xào trứng không chỉ vì hương vị của nó.",
    "Món này rất ngon, hơi chua và cũng hơi ngọt, ăn với cơm đặc biệt ngon. Tôi có thể ăn rất nhiều cơm.",
    "Tôi đồng ý. Cà chua xào trứng ăn cùng cơm quả thật rất ngon.",
    "Nhưng quan trọng hơn, món ăn này chứa đựng những ký ức thời thơ ấu của tôi.",
    "Tôi nhớ hồi nhỏ, nếu thi không tốt hoặc cãi nhau với bạn bè,",
    "tâm trạng rất tệ, mẹ tôi sẽ làm món cà chua xào trứng cho tôi.",
    "Ồ? Thật vậy sao?",
    "Đúng vậy. Mẹ không nói nhiều, chỉ đi vào bếp. Chẳng bao lâu sau, tôi đã ngửi thấy mùi thơm.",
    "Sau đó mẹ đặt trước mặt tôi một đĩa cà chua xào trứng nóng hổi, màu sắc rất đẹp và nói: 'Ăn nhanh đi, ăn xong tâm trạng sẽ tốt hơn.'",

    # 031 - 040
    "Ôi, đúng là một người mẹ tuyệt vời.",
    "Đúng vậy. Vì thế, đối với tôi, hương vị của cà chua xào trứng chính là hương vị tình yêu của mẹ. Nó rất ấm áp.",
    "Mỗi khi làm việc mệt mỏi hoặc gặp chuyện không vui, tôi đều rất muốn ăn món này.",
    "Ăn món ấy giống như có mẹ ở bên cạnh vậy.",
    "Vì thế, đây là món ngon nhất trong lòng tôi. Không ai có thể nấu ngon hơn mẹ tôi.",
    "Tôi hiểu rồi. Với bạn, món này không chỉ là thức ăn mà còn là một cảm giác, cảm giác về tình yêu và gia đình.",
    "Đúng! Bạn tổng kết hay quá. Chính là cảm giác đó.",
    "Thế còn vịt quay Bắc Kinh của bạn? Đằng sau món ấy có câu chuyện gì không? Hay bạn chỉ đơn thuần thích hương vị của nó?",
    "Tất nhiên là có câu chuyện rồi. Tôi cũng rất thích hương vị của nó. Lớp da được quay giòn, màu đỏ óng, trông rất đẹp.",
    "Còn phần thịt thì rất thơm.",

    # 041 - 050
    "Lấy một chiếc bánh mỏng, đặt thịt vịt lên, thêm chút dưa chuột, hành và nước sốt ngọt rồi cuốn lại ăn.",
    "Ôi, hương vị ấy thật phong phú.",
    "Bạn đừng kể nữa, tôi thật sự càng lúc càng đói rồi.",
    "Haha. Nhưng tôi không chỉ thích hương vị của nó. Tôi còn thích cả 'quá trình' ăn vịt quay Bắc Kinh.",
    "Nó không giống món ăn gia đình, nấu xong là có thể ăn ngay. Ăn vịt quay Bắc Kinh mang lại cảm giác rất trang trọng.",
    "Cảm giác trang trọng à? Ý bạn là sao?",
    "Bạn xem, chúng ta thường cùng gia đình hoặc bạn bè đến quán vịt quay chuyên biệt để ăn mừng một chuyện vui.",
    "Ví dụ như sinh nhật hoặc năm mới.",
    "Sau đó, đầu bếp sẽ đẩy cả con vịt đã quay đến bên bàn và trực tiếp thái thịt vịt cho bạn.",
    "Khung cảnh ấy khiến bạn cảm thấy đây là một khoảnh khắc rất đặc biệt.",

    # 051 - 060
    "À, tôi hiểu rồi. Bạn thích bầu không khí đặc biệt và trang trọng đó.",
    "Đúng vậy. Lần đầu tiên tôi ăn vịt quay Bắc Kinh chính hiệu là vào sinh nhật mười tuổi.",
    "Bố mẹ đưa tôi đến một nhà hàng lâu đời rất nổi tiếng ở Bắc Kinh.",
    "Đến tận bây giờ tôi vẫn nhớ, khi ấy tôi nhìn thấy con vịt quay bóng bẩy và đầu bếp thành thạo thái lớp da cùng thịt vịt,",
    "rồi xếp ngay ngắn lên đĩa. Tôi thấy thật kỳ diệu.",
    "Đó là lần đầu tiên tôi cảm nhận được rằng nấu ăn và thưởng thức món ăn cũng có thể giống như một môn nghệ thuật.",
    "Vậy với tôi, cà chua xào trứng tượng trưng cho 'gia đình' và 'tình yêu', còn với bạn, vịt quay Bắc Kinh tượng trưng cho 'sự ăn mừng' và 'nghệ thuật'.",
    "Có thể nói như vậy. Vai trò của thức ăn trong cuộc sống chúng ta thật sự rất thú vị.",
    "Đúng vậy. Nhưng Lý Minh này, bạn đâu thể ngày nào cũng đến nhà hàng ăn vịt quay Bắc Kinh được, đúng không?",
    "Vậy bình thường, chẳng hạn bữa sáng và bữa trưa, bạn thích ăn gì?",

    # 061 - 070
    "Tất nhiên là không rồi. Vịt quay Bắc Kinh quá đắt và cũng quá trang trọng. Tôi chỉ ăn vào những dịp thật đặc biệt.",
    "Bình thường tôi cũng ăn rất đơn giản. Chẳng hạn bữa sáng, tôi thích uống một cốc sữa và ăn hai lát bánh mì. Rất đơn giản và nhanh chóng. Còn bạn?",
    "Bữa sáng tôi thích ăn kiểu Trung Quốc. Tôi thích uống một bát cháo nóng hoặc ăn một chiếc bánh bao.",
    "Tôi cảm thấy buổi sáng ăn chút đồ nóng sẽ rất dễ chịu cho dạ dày.",
    "Ừm, nhiều người Trung Quốc có thói quen này. Thế bữa trưa thì sao? Bạn thường tự mang cơm hay ăn bên ngoài?",
    "Trước đây tôi thích tự mang cơm vì tôi nghĩ đồ mình nấu sẽ tốt cho sức khỏe hơn.",
    "Nhưng bây giờ công việc quá bận nên tôi thường ăn cùng đồng nghiệp ở gần công ty.",
    "Chúng tôi thường ăn suất cơm gồm một món ăn, một món canh và một bát cơm. Rất đơn giản.",
    "Tôi cũng vậy. Thời gian nghỉ trưa rất ngắn nên cứ cách nào tiện thì chọn cách đó.",
    "Nhưng nhắc đến ăn cùng bạn bè, gần đây tôi phát hiện một cách ăn rất thú vị.",

    # 071 - 080
    "Là gì vậy?",
    "Là lẩu.",
    "Lẩu! Tôi thích ăn lẩu lắm!",
    "Đặc biệt vào mùa đông, bên ngoài rất lạnh, còn trong nhà mọi người quây quần bên nồi lẩu nghi ngút khói. Cảm giác thật tuyệt!",
    "Đúng! Tôi nghĩ sức hấp dẫn của lẩu không chỉ nằm ở bản thân món ăn.",
    "Bạn có thể chọn đủ loại thịt tươi, hải sản và rau củ rồi cho vào loại nước lẩu mình thích.",
    "Có thể chọn nước lẩu cay hoặc không cay.",
    "Tôi thích cay! Còn bạn?",
    "Tôi cũng thích. Tôi thấy ăn cay rất đã. Nhưng điều tôi thích hơn là bầu không khí khi ăn lẩu.",
    "Mọi người ngồi cùng nhau, nhìn nước lẩu sôi liên tục và thức ăn dần dần chín trong nồi.",

    # 081 - 090
    "Muốn ăn gì thì tự cho vào. Quá trình ấy tràn đầy sự mong chờ và niềm vui.",
    "Đúng vậy, hơn nữa ăn lẩu có thể kéo dài rất lâu.",
    "Mọi người vừa ăn vừa trò chuyện, rất thư giãn. Không giống những món khác, ăn xong là kết thúc.",
    "Ăn lẩu giúp chúng ta có nhiều thời gian ở bên bạn bè hơn.",
    "Bạn nói đúng. Có lẽ đó chính là ý nghĩa văn hóa của lẩu.",
    "Nó biến việc ăn uống thành một hoạt động giao lưu.",
    "Nó đưa mọi người lại gần nhau. Vì thế, điều quan trọng không phải ăn gì mà là ăn cùng ai.",
    "Ừm, nhắc đến đây, tôi có một câu hỏi. Có lẽ đây cũng là điều nhiều bạn đang học tiếng Trung muốn hỏi.",
    "Câu hỏi gì? Bạn nói đi.",
    "Đó là đôi khi tôi muốn thử những món ăn Trung Quốc mới, như lẩu hoặc những món mình chưa từng nghe đến.",

    # 091 - 100
    "Nhưng khi bước vào nhà hàng và nhìn thực đơn có rất nhiều chữ Hán mà tôi không biết.",
    "Tôi cũng không biết món nào ngon. Lúc đó tôi hơi căng thẳng và sợ hãi.",
    "Tôi sợ gọi phải món không ngon hoặc không biết cách ăn. Bạn đã từng có cảm giác như vậy chưa?",
    "Tôi rất hiểu.",
    "Đây không chỉ là vấn đề mà những người nước ngoài học tiếng Trung gặp phải. Ngay cả người Trung Quốc chúng tôi,",
    "khi đến một nơi xa lạ và nhìn thấy tên món ăn chưa từng gặp cũng có những lo lắng tương tự.",
    "Đây là một vấn đề rất phổ biến.",
    "Vậy phải làm sao? Có cách nào hay không?",
    "Tất nhiên là có. Tôi nghĩ cách tốt nhất chính là 'hỏi'.",
    "Nếu đi cùng bạn người Trung Quốc, bạn có thể hỏi trực tiếp: 'Đây là món gì?",

    # 101 - 110
    "Có ngon không? Có cay không?' Bạn của bạn chắc chắn sẽ rất sẵn lòng giới thiệu.",
    "Thế nếu tôi đi một mình thì sao?",
    "Nếu đi một mình, hiện nay thực đơn của nhiều nhà hàng đều có hình ảnh.",
    "Bạn có thể nhìn hình, chỉ vào món trông hấp dẫn rồi nói với nhân viên phục vụ: 'Xin chào, tôi muốn món này.'",
    "'Cái này' là một từ rất hữu ích khi học tiếng Trung.",
    "À đúng rồi! 'Cái này'! Thực tế quá!",
    "Đúng vậy. Còn một cách nữa là tra cứu trước trên điện thoại.",
    "Ví dụ nếu muốn ăn lẩu, bạn có thể tìm trên mạng 'những món nhất định phải gọi khi ăn lẩu' để xem mọi người thường thích ăn gì.",
    "Như vậy bạn sẽ có sự chuẩn bị. Thật ra học ngôn ngữ rất giống với việc thưởng thức món ăn.",
    "Ồ? Giống như thế nào?",

    # 111 - 120
    "Cả hai đều cần lòng dũng cảm. Bạn cần can đảm thử những điều mình chưa biết.",
    "Có thể bạn sẽ gặp hương vị mình không thích hoặc nói sai một câu. Nhưng không sao cả.",
    "Chính nhờ những lần thử như vậy, bạn mới khám phá ra một thế giới hoàn toàn mới và tuyệt vời.",
    "Bạn có thể tìm thấy món ăn mình yêu thích nhất hoặc học được một từ hữu ích nhất.",
    "Vì vậy đừng sợ, hãy mạnh dạn thử.",
    "Lý Minh, phép so sánh của bạn hay quá! Học ngôn ngữ giống như thưởng thức món ăn.",
    "Đều cần dũng khí để thử. Tôi nhớ rồi.",
    "Lần sau muốn ăn món chưa từng thử, tôi nhất định sẽ mạnh dạn hơn một chút.",
    "Vừa rồi chúng ta đã nói về món ăn yêu thích và cách ăn uống.",
    "Giờ hãy nói về chính hương vị nhé.",

    # 121 - 130
    "Món ăn Trung Quốc có nhiều vị khác nhau: chua, ngọt, đắng, cay và mặn.",
    "Vương Vũ, bạn thích vị nào nhất?",
    "Ừm... Nếu chỉ được chọn một, có lẽ tôi sẽ chọn 'ngọt'. Tôi rất thích ăn đồ ngọt.",
    "Ví dụ như bánh ngọt, sô-cô-la và kem. Tôi nghĩ vị ngọt có thể khiến con người vui vẻ.",
    "Bạn không thấy vậy sao? Làm việc mệt mỏi cả ngày, ăn một miếng bánh ngọt nhỏ là tâm trạng lập tức tốt hơn.",
    "Haha, đúng vậy. Vị ngọt quả thật có tác dụng xoa dịu tinh thần.",
    "Nhiều cô gái đều thích đồ ngọt.",
    "Nhưng với tôi, có lẽ tôi thích vị 'cay' hơn.",
    "Cay à? Tại sao? Nhiều người rất sợ cay.",
    "Tôi thấy vị cay rất trực tiếp và mạnh mẽ. Nó kích thích vị giác ngay lập tức, khiến cả người tỉnh táo hơn.",

    # 131 - 140
    "Hơn nữa, khi ăn cay bạn sẽ đổ mồ hôi, cảm giác như những thứ không tốt trong cơ thể đều được thải ra ngoài, rất sảng khoái.",
    "Đặc biệt vào mùa hè, khi không muốn ăn cơm, ăn chút món cay là lập tức muốn ăn cơm ngay.",
    "Điều này tôi đồng ý. Món Tứ Xuyên và Hồ Nam đều rất nổi tiếng vì vị cay đặc trưng.",
    "Nhưng ngoài vị ngọt và cay, tôi nghĩ còn một vị cũng rất quan trọng.",
    "Là gì?",
    "Là vị 'tươi ngon', vị umami.",
    "Hình như vị này không thường được nhắc đến trong món ăn của những quốc gia khác.",
    "Bạn nói đúng. 'Vị tươi ngon' là điều rất được coi trọng trong ẩm thực Trung Quốc. Nó không phải vị mặn hay ngọt mà là hương vị tự nhiên, nguyên bản.",
    "Ví dụ như nước canh gà ngon hoặc cá vừa đánh bắt từ biển lên, chúng đều có vị tươi ngon.",
    "Đúng vậy, canh mẹ tôi nấu đặc biệt thơm ngon.",

    # 141 - 150
    "Mẹ tôi không bao giờ cho những loại gia vị linh tinh vào. Mẹ nói nguyên liệu tốt tự nó đã có vị ngon tự nhiên.",
    "Để đạt được vị 'tươi ngon' này, đầu bếp cần dùng nguyên liệu tốt nhất và phương pháp nấu phù hợp nhất.",
    "Chính xác. Vì vậy bạn thấy đấy, đằng sau những hương vị đơn giản thật ra có rất nhiều văn hóa và triết lý.",
    "Vị ngọt tượng trưng cho niềm vui và sự chữa lành. Vị cay tượng trưng cho đam mê và sự kích thích.",
    "Còn vị tươi ngon tượng trưng cho sự tự nhiên và chân thực.",
    "Mỗi hương vị đều tương ứng với một cảm xúc và thái độ sống.",
    "Ôi, hôm nay chúng ta bắt đầu từ câu hỏi đơn giản 'Bạn thích ăn gì?' mà lại trò chuyện được nhiều điều thú vị đến thế.",
    "Từ món ăn gia đình đến bữa ăn thịnh soạn ở nhà hàng, từ ký ức cá nhân đến văn hóa giao tiếp, giờ lại nói đến hương vị và triết lý.",
    "Đúng vậy. Vì thức ăn vốn không phải là chuyện đơn giản.",
    "Nó kết nối quá khứ, hiện tại và tương lai của chúng ta. Nó cũng kết nối chúng ta với gia đình, bạn bè, thậm chí cả thế giới.",

    # 151 - 160
    "Lý Minh, hôm nay trò chuyện với bạn, tôi thật sự rất vui.",
    "Không chỉ lại thấy đói một lần nữa mà tôi còn có thêm nhiều suy nghĩ mới về chuyện ăn uống.",
    "Haha, tôi cũng vậy. Hôm nay chúng ta còn nhắc đến rất nhiều từ tiếng Trung liên quan đến đồ ăn.",
    "Tôi sẽ tổng kết ngắn gọn để các bạn đang nghe chương trình tiện ôn tập.",
    "Được đấy!",
    "Chúng ta đã nói về món vịt quay Bắc Kinh tôi thích và món cà chua xào trứng bạn thích.",
    "Chúng ta còn nói về bữa sáng Trung Quốc như cháo, bánh bao và các món ăn chính như cơm, mì.",
    "Đúng, còn một món rất quan trọng nữa, đó là lẩu mà nhiều người cùng ăn!",
    "Đúng vậy, lẩu. Chúng ta cũng nói đến các vị như ngọt, chua, cay và tươi ngon.",
    "Tất nhiên, còn một từ quan trọng nhất khi gọi món ở nhà hàng, đó là 'cái này'!",

    # 161 - 171
    "Haha, đúng! Nhất định phải nhớ từ 'cái này'.",
    "Lý Minh, bạn tổng kết hay quá. Vậy các bạn đang nghe chương trình, bây giờ đến lượt các bạn rồi.",
    "Đúng vậy.",
    "Chúng tôi muốn hỏi mọi người: Món ăn Trung Quốc bạn thích nhất là gì? Tại sao bạn thích món đó?",
    "Đằng sau món ăn ấy có câu chuyện hoặc kỷ niệm đặc biệt nào không?",
    "Bạn thích vị ngọt, cay hay hương vị nào khác?",
    "Mời mọi người dùng những từ đã học hôm nay để bình luận và chia sẻ câu chuyện ẩm thực của mình.",
    "Chúng tôi rất mong được đọc những chia sẻ của các bạn.",
    "Được rồi, chương trình hôm nay đến đây thôi.",
    "Cảm ơn mọi người đã lắng nghe. Chúng tôi là 'Tiếng Trung mỗi ngày'. Hẹn gặp lại lần sau!",
    "Tạm biệt!"
]


def main():
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("Sai YouTube ID!")

    sentences = data.get("sentences", [])

    if len(sentences) != 171:
        raise ValueError(
            f"JSON co {len(sentences)} doan, can 171."
        )

    if len(TRANSLATIONS) != 171:
        raise ValueError(
            f"Ban dich co {len(TRANSLATIONS)} doan, can 171."
        )

    for index, (sentence, vi) in enumerate(
        zip(sentences, TRANSLATIONS), 1
    ):
        for key in ("start", "end", "hanzi", "pinyin"):
            if key not in sentence:
                raise ValueError(
                    f"Doan {index} thieu {key}"
                )

        if not vi.strip():
            raise ValueError(
                f"Doan {index} chua dich"
            )

        sentence["vi"] = vi.strip()

    # Bo trang thai tam cua buoc tao pinyin.
    # Chua danh dau la da kiem tra voi video.
    data.pop("status", None)

    OUTPUT.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    # Doc lai de kiem tra file da luu.
    check = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    assert check["youtube_id"] == VIDEO_ID
    assert len(check["sentences"]) == 171
    assert all(
        item["hanzi"].strip()
        and item["pinyin"].strip()
        and item["vi"].strip()
        for item in check["sentences"]
    )

    print("===== VIDEO 4 - HOAN THANH BAN DICH =====")
    print("YouTube:", VIDEO_ID)
    print("Tong so doan:", len(sentences))
    print("Da dich:", len(TRANSLATIONS))
    print("File:", OUTPUT)

    print("\n===== 5 DOAN DAU =====")
    for i, item in enumerate(sentences[:5], 1):
        print(f"\n{i}. {item['hanzi']}")
        print("VI:", item["vi"])

    print("\nCHUA CAP NHAT SQL SERVER.")
    print("CAN RA SOAT PINYIN VA CAC DOAN DAI.")


if __name__ == "__main__":
    main()
