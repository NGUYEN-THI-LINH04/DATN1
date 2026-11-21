from pathlib import Path
import csv


# ============================================================
# 1. DUONG DAN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "grammar_hsk2_draft.csv"


# ============================================================
# 2. DU LIEU NGU PHAP HSK2
#
# Chua gan MaBaiHoc o buoc nay.
# Sau khi tao BaiHoc HSK2 moi chia cac muc ngu phap vao bai.
# ============================================================

GRAMMAR_DATA = [

    {
        "TenCauTruc": "已经……了 - đã... rồi",
        "MoTa": "已经 (yǐjīng) biểu thị một hành động hoặc trạng thái đã xảy ra trước thời điểm nói.",
        "CachDung": "Thường dùng: Chủ ngữ + 已经 + động từ/tính từ + 了.",
        "ViDuTiengTrung": "已经八点了。",
        "ViDuPinyin": "Yǐjīng bā diǎn le.",
        "ViDuTiengViet": "Đã tám giờ rồi."
    },

    {
        "TenCauTruc": "正在……呢 - đang...",
        "MoTa": "正在 (zhèngzài) biểu thị hành động đang diễn ra tại thời điểm nói.",
        "CachDung": "Chủ ngữ + 正在 + động từ + tân ngữ + 呢. Có thể lược 正 hoặc 在 tùy ngữ cảnh.",
        "ViDuTiengTrung": "我正在做作业呢。",
        "ViDuPinyin": "Wǒ zhèngzài zuò zuòyè ne.",
        "ViDuTiengViet": "Tôi đang làm bài tập."
    },

    {
        "TenCauTruc": "Động từ + 过 - từng...",
        "MoTa": "过 (guo) đặt sau động từ để biểu thị kinh nghiệm đã từng trải qua.",
        "CachDung": "Chủ ngữ + động từ + 过 + tân ngữ. Phủ định thường dùng 没有 + động từ + 过.",
        "ViDuTiengTrung": "我去过北京。",
        "ViDuPinyin": "Wǒ qùguo Běijīng.",
        "ViDuTiengViet": "Tôi đã từng đến Bắc Kinh."
    },

    {
        "TenCauTruc": "Động từ + 着 - trạng thái đang duy trì",
        "MoTa": "着 (zhe) biểu thị một trạng thái hoặc kết quả đang được duy trì.",
        "CachDung": "Động từ + 着. Cấu trúc này thường dùng để mô tả trạng thái của người hoặc sự vật.",
        "ViDuTiengTrung": "门开着。",
        "ViDuPinyin": "Mén kāizhe.",
        "ViDuTiengViet": "Cửa đang mở."
    },

    {
        "TenCauTruc": "快要 / 就要……了 - sắp...",
        "MoTa": "快要 và 就要 dùng để biểu thị một hành động hoặc sự việc sắp xảy ra.",
        "CachDung": "Chủ ngữ + 快要/就要 + động từ + 了.",
        "ViDuTiengTrung": "电影快要开始了。",
        "ViDuPinyin": "Diànyǐng kuàiyào kāishǐ le.",
        "ViDuTiengViet": "Bộ phim sắp bắt đầu rồi."
    },

    {
        "TenCauTruc": "一……就…… - vừa... là...",
        "MoTa": "Cấu trúc 一……就…… biểu thị hành động thứ hai xảy ra ngay sau hành động thứ nhất.",
        "CachDung": "Chủ ngữ + 一 + động từ 1 + 就 + động từ 2.",
        "ViDuTiengTrung": "我一到家就给你打电话。",
        "ViDuPinyin": "Wǒ yí dào jiā jiù gěi nǐ dǎ diànhuà.",
        "ViDuTiengViet": "Tôi vừa về đến nhà là sẽ gọi điện cho bạn."
    },

    {
        "TenCauTruc": "先……再…… - trước... rồi...",
        "MoTa": "先……再…… dùng để nói thứ tự thực hiện hai hành động.",
        "CachDung": "先 + hành động 1, 再 + hành động 2.",
        "ViDuTiengTrung": "我们先吃饭，再去看电影。",
        "ViDuPinyin": "Wǒmen xiān chīfàn, zài qù kàn diànyǐng.",
        "ViDuTiengViet": "Chúng ta ăn cơm trước, sau đó đi xem phim."
    },

    {
        "TenCauTruc": "又……又…… - vừa... vừa...",
        "MoTa": "又……又…… dùng để nối hai đặc điểm hoặc trạng thái cùng tồn tại.",
        "CachDung": "又 + tính từ/động từ 1 + 又 + tính từ/động từ 2.",
        "ViDuTiengTrung": "她又聪明又漂亮。",
        "ViDuPinyin": "Tā yòu cōngming yòu piàoliang.",
        "ViDuTiengViet": "Cô ấy vừa thông minh vừa xinh đẹp."
    },

    {
        "TenCauTruc": "一边……一边…… - vừa... vừa...",
        "MoTa": "一边……一边…… biểu thị hai hành động được thực hiện đồng thời.",
        "CachDung": "Chủ ngữ + 一边 + động từ 1 + 一边 + động từ 2.",
        "ViDuTiengTrung": "他一边听音乐一边做作业。",
        "ViDuPinyin": "Tā yìbiān tīng yīnyuè yìbiān zuò zuòyè.",
        "ViDuTiengViet": "Anh ấy vừa nghe nhạc vừa làm bài tập."
    },

    {
        "TenCauTruc": "越来越…… - ngày càng...",
        "MoTa": "越来越 biểu thị mức độ của một đặc điểm thay đổi dần theo thời gian.",
        "CachDung": "Chủ ngữ + 越来越 + tính từ.",
        "ViDuTiengTrung": "天气越来越冷了。",
        "ViDuPinyin": "Tiānqì yuèláiyuè lěng le.",
        "ViDuTiengViet": "Thời tiết ngày càng lạnh."
    },

    {
        "TenCauTruc": "越……越…… - càng... càng...",
        "MoTa": "越……越…… biểu thị hai mức độ thay đổi có liên quan đến nhau.",
        "CachDung": "越 + động từ/tính từ 1 + 越 + tính từ/động từ 2.",
        "ViDuTiengTrung": "汉语越学越有意思。",
        "ViDuPinyin": "Hànyǔ yuè xué yuè yǒu yìsi.",
        "ViDuTiengViet": "Tiếng Trung càng học càng thú vị."
    },

    {
        "TenCauTruc": "A + 比 + B + tính từ",
        "MoTa": "比 (bǐ) được dùng để so sánh sự khác nhau giữa hai đối tượng.",
        "CachDung": "A + 比 + B + tính từ.",
        "ViDuTiengTrung": "今天比昨天冷。",
        "ViDuPinyin": "Jīntiān bǐ zuótiān lěng.",
        "ViDuTiengViet": "Hôm nay lạnh hơn hôm qua."
    },

    {
        "TenCauTruc": "A + 没有 + B + tính từ",
        "MoTa": "没有 được dùng trong câu so sánh để biểu thị A không bằng B về một đặc điểm.",
        "CachDung": "A + 没有 + B + tính từ.",
        "ViDuTiengTrung": "我没有他高。",
        "ViDuPinyin": "Wǒ méiyǒu tā gāo.",
        "ViDuTiengViet": "Tôi không cao bằng anh ấy."
    },

    {
        "TenCauTruc": "A + 跟 / 和 + B + 一样",
        "MoTa": "一样 (yíyàng) biểu thị hai đối tượng giống nhau về một đặc điểm.",
        "CachDung": "A + 跟/和 + B + 一样 + tính từ.",
        "ViDuTiengTrung": "我的书跟你的一样。",
        "ViDuPinyin": "Wǒ de shū gēn nǐ de yíyàng.",
        "ViDuTiengViet": "Sách của tôi giống sách của bạn."
    },

    {
        "TenCauTruc": "更 + tính từ - càng / hơn nữa",
        "MoTa": "更 (gèng) đứng trước tính từ để biểu thị mức độ cao hơn.",
        "CachDung": "Chủ ngữ + 更 + tính từ.",
        "ViDuTiengTrung": "这件衣服更便宜。",
        "ViDuPinyin": "Zhè jiàn yīfu gèng piányi.",
        "ViDuTiengViet": "Bộ quần áo này rẻ hơn."
    },

    {
        "TenCauTruc": "最 + tính từ - nhất",
        "MoTa": "最 (zuì) biểu thị mức độ cao nhất trong một phạm vi.",
        "CachDung": "Chủ ngữ + 最 + tính từ.",
        "ViDuTiengTrung": "他跑得最快。",
        "ViDuPinyin": "Tā pǎo de zuì kuài.",
        "ViDuTiengViet": "Anh ấy chạy nhanh nhất."
    },

    {
        "TenCauTruc": "有点儿 + tính từ - hơi...",
        "MoTa": "有点儿 thường biểu thị mức độ nhẹ và thường mang sắc thái không như mong muốn.",
        "CachDung": "有点儿 + tính từ.",
        "ViDuTiengTrung": "今天有点儿冷。",
        "ViDuPinyin": "Jīntiān yǒudiǎnr lěng.",
        "ViDuTiengViet": "Hôm nay hơi lạnh."
    },

    {
        "TenCauTruc": "Tính từ + 一点儿 - ... một chút",
        "MoTa": "一点儿 đứng sau tính từ để yêu cầu hoặc biểu thị thay đổi mức độ.",
        "CachDung": "Tính từ + 一点儿.",
        "ViDuTiengTrung": "请说慢一点儿。",
        "ViDuPinyin": "Qǐng shuō màn yìdiǎnr.",
        "ViDuTiengViet": "Xin hãy nói chậm một chút."
    },

    {
        "TenCauTruc": "这么 / 那么 + tính từ",
        "MoTa": "这么 và 那么 dùng để chỉ mức độ: như thế này hoặc như thế kia.",
        "CachDung": "这么/那么 + tính từ.",
        "ViDuTiengTrung": "这个苹果这么大。",
        "ViDuPinyin": "Zhège píngguǒ zhème dà.",
        "ViDuTiengViet": "Quả táo này lớn như vậy."
    },

    {
        "TenCauTruc": "每……都…… - mỗi... đều...",
        "MoTa": "每……都…… biểu thị tất cả các thành viên trong một phạm vi đều có cùng đặc điểm hoặc hành động.",
        "CachDung": "每 + danh từ/lượng từ + 都 + vị ngữ.",
        "ViDuTiengTrung": "每个学生都来了。",
        "ViDuPinyin": "Měi ge xuésheng dōu lái le.",
        "ViDuTiengViet": "Mỗi học sinh đều đã đến."
    },

    {
        "TenCauTruc": "谁 / 什么 / 哪儿 + 都……",
        "MoTa": "Từ nghi vấn kết hợp với 都 có thể biểu thị phạm vi toàn bộ như ai cũng, cái gì cũng, đâu cũng.",
        "CachDung": "谁/什么/哪儿 + 都 + vị ngữ.",
        "ViDuTiengTrung": "谁都知道这件事。",
        "ViDuPinyin": "Shéi dōu zhīdào zhè jiàn shì.",
        "ViDuTiengViet": "Ai cũng biết chuyện này."
    },

    {
        "TenCauTruc": "只 + động từ - chỉ...",
        "MoTa": "只 (zhǐ) dùng để giới hạn phạm vi hoặc số lượng.",
        "CachDung": "Chủ ngữ + 只 + động từ/cụm động từ.",
        "ViDuTiengTrung": "我只喝茶。",
        "ViDuPinyin": "Wǒ zhǐ hē chá.",
        "ViDuTiengViet": "Tôi chỉ uống trà."
    },

    {
        "TenCauTruc": "才 - mãi mới / chỉ mới",
        "MoTa": "才 (cái) có thể biểu thị một hành động xảy ra muộn hoặc điều kiện phải đạt được trước khi hành động xảy ra.",
        "CachDung": "Chủ ngữ + thời gian/điều kiện + 才 + động từ.",
        "ViDuTiengTrung": "他九点才来。",
        "ViDuPinyin": "Tā jiǔ diǎn cái lái.",
        "ViDuTiengViet": "Mãi chín giờ anh ấy mới đến."
    },

    {
        "TenCauTruc": "就 - đã / liền / ngay",
        "MoTa": "就 (jiù) thường biểu thị hành động xảy ra sớm, nhanh hoặc ngay sau một điều kiện.",
        "CachDung": "Chủ ngữ + thời gian/điều kiện + 就 + động từ.",
        "ViDuTiengTrung": "我马上就来。",
        "ViDuPinyin": "Wǒ mǎshàng jiù lái.",
        "ViDuTiengViet": "Tôi đến ngay."
    },

    {
        "TenCauTruc": "再 + động từ - lại, lần nữa trong tương lai",
        "MoTa": "再 (zài) thường biểu thị một hành động sẽ được lặp lại hoặc tiếp tục.",
        "CachDung": "再 + động từ.",
        "ViDuTiengTrung": "明天再说吧。",
        "ViDuPinyin": "Míngtiān zài shuō ba.",
        "ViDuTiengViet": "Ngày mai nói tiếp nhé."
    },

    {
        "TenCauTruc": "又 + động từ - lại, một lần nữa",
        "MoTa": "又 (yòu) thường dùng khi một hành động đã lặp lại hoặc một tình huống lại xảy ra.",
        "CachDung": "Chủ ngữ + 又 + động từ.",
        "ViDuTiengTrung": "他昨天又迟到了。",
        "ViDuPinyin": "Tā zuótiān yòu chídào le.",
        "ViDuTiengViet": "Hôm qua anh ấy lại đến muộn."
    },

    {
        "TenCauTruc": "还 - vẫn / còn / cũng",
        "MoTa": "还 (hái) có thể biểu thị trạng thái tiếp tục hoặc bổ sung thêm thông tin.",
        "CachDung": "还 thường đứng trước động từ hoặc tính từ.",
        "ViDuTiengTrung": "我还想买一本书。",
        "ViDuPinyin": "Wǒ hái xiǎng mǎi yì běn shū.",
        "ViDuTiengViet": "Tôi còn muốn mua thêm một quyển sách."
    },

    {
        "TenCauTruc": "还是 / 或者 - hay / hoặc",
        "MoTa": "还是 thường dùng để đưa ra lựa chọn trong câu hỏi; 或者 thường dùng trong câu trần thuật.",
        "CachDung": "A 还是 B？; hoặc A 或者 B.",
        "ViDuTiengTrung": "你喝茶还是喝咖啡？",
        "ViDuPinyin": "Nǐ hē chá háishi hē kāfēi?",
        "ViDuTiengViet": "Bạn uống trà hay uống cà phê?"
    },

    {
        "TenCauTruc": "因为……所以…… - bởi vì... nên...",
        "MoTa": "因为 nêu nguyên nhân và 所以 nêu kết quả.",
        "CachDung": "因为 + nguyên nhân, 所以 + kết quả.",
        "ViDuTiengTrung": "因为下雨，所以我没去。",
        "ViDuPinyin": "Yīnwèi xiàyǔ, suǒyǐ wǒ méi qù.",
        "ViDuTiengViet": "Vì trời mưa nên tôi không đi."
    },

    {
        "TenCauTruc": "虽然……但是…… - mặc dù... nhưng...",
        "MoTa": "虽然……但是…… dùng để biểu thị quan hệ nhượng bộ giữa hai vế câu.",
        "CachDung": "虽然 + tình huống 1, 但是 + tình huống trái ngược.",
        "ViDuTiengTrung": "虽然很累，但是他还在学习。",
        "ViDuPinyin": "Suīrán hěn lèi, dànshì tā hái zài xuéxí.",
        "ViDuTiengViet": "Mặc dù rất mệt nhưng anh ấy vẫn đang học."
    },

    {
        "TenCauTruc": "如果……就…… - nếu... thì...",
        "MoTa": "如果……就…… dùng để biểu thị điều kiện và kết quả.",
        "CachDung": "如果 + điều kiện, 就 + kết quả.",
        "ViDuTiengTrung": "如果明天下雨，我们就不去。",
        "ViDuPinyin": "Rúguǒ míngtiān xiàyǔ, wǒmen jiù bú qù.",
        "ViDuTiengViet": "Nếu ngày mai trời mưa thì chúng tôi sẽ không đi."
    },

    {
        "TenCauTruc": "除了……以外，还 / 也……",
        "MoTa": "Cấu trúc này dùng để thêm thông tin ngoài một đối tượng hoặc phạm vi đã nêu.",
        "CachDung": "除了 + A + 以外, chủ ngữ + 还/也 + B.",
        "ViDuTiengTrung": "除了汉语以外，她还会说英语。",
        "ViDuPinyin": "Chúle Hànyǔ yǐwài, tā hái huì shuō Yīngyǔ.",
        "ViDuTiengViet": "Ngoài tiếng Trung ra, cô ấy còn biết nói tiếng Anh."
    },

    {
        "TenCauTruc": "从……到…… - từ... đến...",
        "MoTa": "从……到…… dùng để biểu thị điểm bắt đầu và điểm kết thúc về thời gian hoặc địa điểm.",
        "CachDung": "从 + điểm bắt đầu + 到 + điểm kết thúc.",
        "ViDuTiengTrung": "从学校到我家很近。",
        "ViDuPinyin": "Cóng xuéxiào dào wǒ jiā hěn jìn.",
        "ViDuTiengViet": "Từ trường đến nhà tôi rất gần."
    },

    {
        "TenCauTruc": "A + 离 + B + khoảng cách / tính từ",
        "MoTa": "离 (lí) dùng để nói khoảng cách giữa hai địa điểm.",
        "CachDung": "A + 离 + B + 很近/很远 hoặc khoảng cách.",
        "ViDuTiengTrung": "我家离学校很近。",
        "ViDuPinyin": "Wǒ jiā lí xuéxiào hěn jìn.",
        "ViDuTiengViet": "Nhà tôi rất gần trường."
    },

    {
        "TenCauTruc": "往 / 向 + phương hướng + động từ",
        "MoTa": "往 và 向 dùng để chỉ hướng của một hành động.",
        "CachDung": "往/向 + phương hướng/địa điểm + động từ.",
        "ViDuTiengTrung": "请往前走。",
        "ViDuPinyin": "Qǐng wǎng qián zǒu.",
        "ViDuTiengViet": "Xin hãy đi về phía trước."
    },

    {
        "TenCauTruc": "给 + người + động từ",
        "MoTa": "给 (gěi) có thể giới thiệu đối tượng nhận hoặc người mà hành động hướng tới.",
        "CachDung": "Chủ ngữ + 给 + người + động từ + tân ngữ.",
        "ViDuTiengTrung": "我给妈妈打电话。",
        "ViDuPinyin": "Wǒ gěi māma dǎ diànhuà.",
        "ViDuTiengViet": "Tôi gọi điện cho mẹ."
    },

    {
        "TenCauTruc": "让 / 叫 + người + động từ",
        "MoTa": "让 và 叫 có thể dùng để biểu thị yêu cầu hoặc khiến một người thực hiện hành động.",
        "CachDung": "Chủ ngữ + 让/叫 + người + động từ.",
        "ViDuTiengTrung": "老师让我们读课文。",
        "ViDuPinyin": "Lǎoshī ràng wǒmen dú kèwén.",
        "ViDuTiengViet": "Giáo viên yêu cầu chúng tôi đọc bài khóa."
    },

    {
        "TenCauTruc": "对……感兴趣 - có hứng thú với...",
        "MoTa": "对……感兴趣 dùng để nói một người có hứng thú với sự vật hoặc lĩnh vực nào đó.",
        "CachDung": "Chủ ngữ + 对 + đối tượng + 感兴趣.",
        "ViDuTiengTrung": "我对中国历史很感兴趣。",
        "ViDuPinyin": "Wǒ duì Zhōngguó lìshǐ hěn gǎn xìngqù.",
        "ViDuTiengViet": "Tôi rất hứng thú với lịch sử Trung Quốc."
    },

    {
        "TenCauTruc": "对……来说 - đối với...",
        "MoTa": "对……来说 dùng để nêu góc nhìn hoặc đối tượng mà nhận xét áp dụng.",
        "CachDung": "对 + người/đối tượng + 来说, + nhận xét.",
        "ViDuTiengTrung": "对我来说，汉字有点儿难。",
        "ViDuPinyin": "Duì wǒ láishuō, Hànzì yǒudiǎnr nán.",
        "ViDuTiengViet": "Đối với tôi, chữ Hán hơi khó."
    },

    {
        "TenCauTruc": "Động từ + 得 + bổ ngữ mức độ",
        "MoTa": "得 (de) nối động từ với phần bổ sung mô tả mức độ hoặc trạng thái của hành động.",
        "CachDung": "Chủ ngữ + động từ + 得 + tính từ/cụm miêu tả.",
        "ViDuTiengTrung": "他说汉语说得很好。",
        "ViDuPinyin": "Tā shuō Hànyǔ shuō de hěn hǎo.",
        "ViDuTiengViet": "Anh ấy nói tiếng Trung rất tốt."
    },

    {
        "TenCauTruc": "Động từ + 不 + bổ ngữ khả năng",
        "MoTa": "不 đứng giữa động từ và bổ ngữ để biểu thị không thể đạt được kết quả của hành động.",
        "CachDung": "Động từ + 不 + bổ ngữ kết quả.",
        "ViDuTiengTrung": "这个字我看不懂。",
        "ViDuPinyin": "Zhège zì wǒ kàn bu dǒng.",
        "ViDuTiengViet": "Chữ này tôi đọc mà không hiểu."
    },

    {
        "TenCauTruc": "Động từ + 完 - làm xong",
        "MoTa": "完 (wán) làm bổ ngữ kết quả, biểu thị hành động đã hoàn thành.",
        "CachDung": "Động từ + 完 + tân ngữ.",
        "ViDuTiengTrung": "我做完作业了。",
        "ViDuPinyin": "Wǒ zuòwán zuòyè le.",
        "ViDuTiengViet": "Tôi làm xong bài tập rồi."
    },

    {
        "TenCauTruc": "Động từ + 到 - đạt được kết quả",
        "MoTa": "到 (dào) sau động từ biểu thị hành động đã đạt đến mục tiêu hoặc kết quả.",
        "CachDung": "Động từ + 到 + tân ngữ.",
        "ViDuTiengTrung": "我买到票了。",
        "ViDuPinyin": "Wǒ mǎidào piào le.",
        "ViDuTiengViet": "Tôi mua được vé rồi."
    },

    {
        "TenCauTruc": "Động từ + 见 - nhìn / nghe thấy",
        "MoTa": "见 (jiàn) làm bổ ngữ kết quả sau một số động từ như 看 hoặc 听.",
        "CachDung": "看见: nhìn thấy; 听见: nghe thấy.",
        "ViDuTiengTrung": "我看见老师了。",
        "ViDuPinyin": "Wǒ kànjiàn lǎoshī le.",
        "ViDuTiengViet": "Tôi nhìn thấy giáo viên rồi."
    },

    {
        "TenCauTruc": "Động từ + 懂 - hiểu được",
        "MoTa": "懂 (dǒng) làm bổ ngữ kết quả, biểu thị đạt được sự hiểu sau hành động nghe hoặc đọc.",
        "CachDung": "听懂: nghe hiểu; 看懂: đọc/xem hiểu.",
        "ViDuTiengTrung": "你听懂了吗？",
        "ViDuPinyin": "Nǐ tīngdǒng le ma?",
        "ViDuTiengViet": "Bạn nghe hiểu chưa?"
    },

    {
        "TenCauTruc": "Động từ + 好 - làm xong và sẵn sàng",
        "MoTa": "好 (hǎo) làm bổ ngữ kết quả, biểu thị một việc đã được hoàn thành tốt hoặc đã sẵn sàng.",
        "CachDung": "准备好, 做好, 写好...",
        "ViDuTiengTrung": "我准备好材料了。",
        "ViDuPinyin": "Wǒ zhǔnbèi hǎo cáiliào le.",
        "ViDuTiengViet": "Tôi đã chuẩn bị xong tài liệu."
    },

    {
        "TenCauTruc": "Động từ + 来 / 去 - bổ ngữ phương hướng",
        "MoTa": "来 biểu thị chuyển động hướng về phía người nói; 去 biểu thị chuyển động rời xa người nói.",
        "CachDung": "Động từ chuyển động + 来/去, ví dụ 进来, 出去, 回来.",
        "ViDuTiengTrung": "他跑进来了。",
        "ViDuPinyin": "Tā pǎo jìnlái le.",
        "ViDuTiengViet": "Anh ấy chạy vào đây rồi."
    },

    {
        "TenCauTruc": "是……的 - nhấn mạnh thông tin",
        "MoTa": "是……的 có thể dùng để nhấn mạnh thời gian, địa điểm, phương thức hoặc người thực hiện của một sự việc đã xảy ra.",
        "CachDung": "Chủ ngữ + 是 + phần cần nhấn mạnh + động từ + 的.",
        "ViDuTiengTrung": "我是昨天来的。",
        "ViDuPinyin": "Wǒ shì zuótiān lái de.",
        "ViDuTiengViet": "Tôi đến vào ngày hôm qua."
    },

]


# ============================================================
# 3. GHI CSV
# ============================================================

FIELDS = [
    "MaNguPhapTam",
    "MaBaiHoc",
    "TenCauTruc",
    "MoTa",
    "CachDung",
    "ViDuTiengTrung",
    "ViDuPinyin",
    "ViDuTiengViet",
    "MaTep",
    "MaNguon",
    "ThuTuTam",
    "TrangThai",
]


def main():

    print("=" * 64)
    print("BUOC 5 - CHUAN BI NGU PHAP HSK2")
    print("KHONG GHI VAO SQL SERVER")
    print("=" * 64)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"File da ton tai:\n{OUTPUT_FILE}\n"
            "Khong tu dong ghi de de tranh mat du lieu da sua."
        )

    rows = []

    for index, grammar in enumerate(
        GRAMMAR_DATA,
        start=1
    ):

        rows.append({
            "MaNguPhapTam": f"G2-{index:03d}",

            # Chua co BaiHoc HSK2 nen de trong
            "MaBaiHoc": "",

            "TenCauTruc":
                grammar["TenCauTruc"],

            "MoTa":
                grammar["MoTa"],

            "CachDung":
                grammar["CachDung"],

            "ViDuTiengTrung":
                grammar["ViDuTiengTrung"],

            "ViDuPinyin":
                grammar["ViDuPinyin"],

            "ViDuTiengViet":
                grammar["ViDuTiengViet"],

            # Sau nay moi gan audio/nguon
            "MaTep": "",
            "MaNguon": "",

            "ThuTuTam": index,

            # Chua gan vao bai nen chua xuat ban
            "TrangThai": "ban_nhap",
        })

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print(
        f"Tong so cau truc ngu phap HSK2: "
        f"{len(rows)}"
    )

    print()
    print("Da tao:")
    print(OUTPUT_FILE)

    print()
    print("Trang thai: ban_nhap")
    print("MaBaiHoc: CHUA GAN")
    print("KHONG INSERT/UPDATE/DELETE SQL.")


if __name__ == "__main__":
    main()