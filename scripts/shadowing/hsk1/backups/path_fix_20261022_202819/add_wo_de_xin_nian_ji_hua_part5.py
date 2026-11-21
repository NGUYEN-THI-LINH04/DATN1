
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1\scripts\shadowing\previews")
SOURCE = ROOT / "wo_de_xin_nian_ji_hua_part4_preview.json"
OUTPUT = ROOT / "wo_de_xin_nian_ji_hua_final_preview.json"

with SOURCE.open("r", encoding="utf-8") as f:
    data = json.load(f)

assert data["youtube_id"] == "o6ilprwO6w0"
assert len(data["sentences"]) == 53
assert data["sentences"][-1]["end"] == 303.5

# Phần 5: Phát triển bản thân, du lịch và lời kết.
# Thời gian ước lượng theo transcript Supadata.
rows = [
    (
        303.5, 309.0,
        "最后一个计划是关于自我提升和旅行的。",
        "Zuìhòu yí gè jìhuà shì guānyú zìwǒ tíshēng hé lǚxíng de.",
        "Kế hoạch cuối cùng liên quan đến việc phát triển bản thân và đi du lịch."
    ),
    (
        309.0, 315.0,
        "既然工作和生活那么辛苦，我们也要学会奖励自己，对吗？",
        "Jìrán gōngzuò hé shēnghuó nàme xīnkǔ, wǒmen yě yào xuéhuì jiǎnglì zìjǐ, duì ma?",
        "Vì công việc và cuộc sống vất vả như vậy, chúng ta cũng cần học cách tự thưởng cho bản thân, đúng không?"
    ),
    (
        315.0, 322.0,
        "今年，我计划去两个国家旅行，日本和泰国。",
        "Jīnnián, wǒ jìhuà qù liǎng gè guójiā lǚxíng, Rìběn hé Tàiguó.",
        "Năm nay, tôi dự định đi du lịch hai quốc gia là Nhật Bản và Thái Lan."
    ),
    (
        322.0, 332.0,
        "为了这个计划，我给自己定了一个目标，今年要存够两万块的旅游基金。",
        "Wèile zhège jìhuà, wǒ gěi zìjǐ dìng le yí gè mùbiāo, jīnnián yào cún gòu liǎng wàn kuài de lǚyóu jījīn.",
        "Để thực hiện kế hoạch này, tôi đặt mục tiêu tiết kiệm đủ 20.000 tệ làm quỹ du lịch trong năm nay."
    ),
    (
        332.0, 339.0,
        "我想去日本，是因为我还是个大男孩，我特别喜欢看日本的动漫。",
        "Wǒ xiǎng qù Rìběn, shì yīnwèi wǒ hái shì ge dà nánhái, wǒ tèbié xǐhuan kàn Rìběn de dòngmàn.",
        "Tôi muốn đến Nhật Bản vì dù đã lớn, tôi vẫn rất thích xem anime Nhật Bản."
    ),
    (
        339.0, 347.0,
        "我想去东京，去看看那些在动画片里出现的场景。",
        "Wǒ xiǎng qù Dōngjīng, qù kànkan nàxiē zài dònghuàpiàn lǐ chūxiàn de chǎngjǐng.",
        "Tôi muốn đến Tokyo để tận mắt nhìn thấy những khung cảnh xuất hiện trong phim hoạt hình."
    ),
    (
        347.0, 354.0,
        "如果到时候我能带着那个女孩一起去，那真的是太幸福了。",
        "Rúguǒ dào shíhou wǒ néng dàizhe nàge nǚhái yìqǐ qù, nà zhēn de shì tài xìngfú le.",
        "Nếu lúc đó tôi có thể đưa cô gái ấy đi cùng thì thật sự quá hạnh phúc."
    ),
    (
        354.0, 360.0,
        "我也想去泰国，特别是曼谷。",
        "Wǒ yě xiǎng qù Tàiguó, tèbié shì Màngǔ.",
        "Tôi cũng muốn đến Thái Lan, đặc biệt là Bangkok."
    ),
    (
        360.0, 370.0,
        "我是个吃货，太想念正宗的泰国菜了，酸酸辣辣的味道，想一想都要流口水了。",
        "Wǒ shì ge chīhuò, tài xiǎngniàn zhèngzōng de Tàiguó cài le, suānsuān làlà de wèidào, xiǎng yi xiǎng dōu yào liú kǒushuǐ le.",
        "Tôi là người mê ăn uống, rất nhớ món Thái chính gốc. Hương vị chua chua cay cay ấy chỉ nghĩ đến thôi đã chảy nước miếng."
    ),
    (
        370.0, 375.0,
        "这就是我2026年的全部计划。",
        "Zhè jiù shì wǒ èr líng èr liù nián de quánbù jìhuà.",
        "Đó là toàn bộ kế hoạch của tôi trong năm 2026."
    ),
    (
        375.0, 384.0,
        "搬个便宜点的新家，换个高薪的好工作，谈一场恋爱，去两个国家旅行。",
        "Bān ge piányi diǎn de xīn jiā, huàn ge gāoxīn de hǎo gōngzuò, tán yì chǎng liàn'ài, qù liǎng gè guójiā lǚxíng.",
        "Chuyển đến nơi ở mới rẻ hơn, tìm một công việc lương cao, yêu một người và đi du lịch hai quốc gia."
    ),
    (
        384.0, 389.0,
        "听起来是不是很简单？",
        "Tīng qǐlái shì bú shì hěn jiǎndān?",
        "Nghe có vẻ rất đơn giản phải không?"
    ),
    (
        389.0, 397.0,
        "但是，如果这些都能实现，我觉得我就已经是世界上最幸福的人了。",
        "Dànshì, rúguǒ zhèxiē dōu néng shíxiàn, wǒ juéde wǒ jiù yǐjīng shì shìjiè shàng zuì xìngfú de rén le.",
        "Nhưng nếu tất cả những điều đó thành hiện thực, tôi nghĩ mình đã là người hạnh phúc nhất thế giới rồi."
    ),
    (
        397.0, 401.0,
        "屏幕前的你们呢？",
        "Píngmù qián de nǐmen ne?",
        "Còn các bạn đang xem trước màn hình thì sao?"
    ),
    (
        401.0, 407.0,
        "你们的新年计划是什么？欢迎在评论区告诉我。",
        "Nǐmen de xīnnián jìhuà shì shénme? Huānyíng zài pínglùn qū gàosu wǒ.",
        "Kế hoạch năm mới của các bạn là gì? Hãy chia sẻ với tôi ở phần bình luận nhé."
    ),
    (
        407.0, 413.0,
        "谢谢大家的收听，如果你喜欢我的分享，请订阅我的频道。",
        "Xièxie dàjiā de shōutīng, rúguǒ nǐ xǐhuan wǒ de fēnxiǎng, qǐng dìngyuè wǒ de píndào.",
        "Cảm ơn mọi người đã lắng nghe. Nếu thích những chia sẻ của tôi, hãy đăng ký kênh nhé."
    ),
    (
        413.0, 415.0,
        "我们下期再见！",
        "Wǒmen xià qī zàijiàn!",
        "Hẹn gặp lại mọi người trong video tiếp theo!"
    ),
]

new_sentences = [
    {
        "start": start,
        "end": end,
        "hanzi": hanzi,
        "pinyin": pinyin,
        "vi": vi,
    }
    for start, end, hanzi, pinyin, vi in rows
]

data["sentences"].extend(new_sentences)

assert len(new_sentences) == 17
assert len(data["sentences"]) == 70

for i, sentence in enumerate(data["sentences"]):
    assert sentence["start"] < sentence["end"], f"Lỗi thời gian câu {i + 1}"

    assert all(
        sentence[key].strip()
        for key in ("hanzi", "pinyin", "vi")
    ), f"Thiếu nội dung câu {i + 1}"

    if i > 0:
        assert (
            sentence["start"] >= data["sentences"][i - 1]["end"]
        ), f"Timestamp chồng lấn tại câu {i + 1}"

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("===== HOAN THANH VIDEO 5 =====")
print("YouTube ID:", data["youtube_id"])
print("So cau phan 5:", len(new_sentences))
print("Tong so cau:", len(data["sentences"]))
print("Thoi gian ket thuc:", data["sentences"][-1]["end"])
print("File:", OUTPUT)
print("Chua thay doi SQL Server")
