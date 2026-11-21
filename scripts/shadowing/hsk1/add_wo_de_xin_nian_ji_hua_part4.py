
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1\scripts\shadowing\hsk1\previews")
SOURCE = ROOT / "wo_de_xin_nian_ji_hua_part3_preview.json"
OUTPUT = ROOT / "wo_de_xin_nian_ji_hua_part4_preview.json"

with SOURCE.open("r", encoding="utf-8") as f:
    data = json.load(f)

assert data["youtube_id"] == "o6ilprwO6w0"
assert len(data["sentences"]) == 41
assert data["sentences"][-1]["end"] == 238.15

# Phần 4: Chuyện tình cảm
# Timestamp dựa trên transcript Supadata.
# Chưa đối chiếu trực tiếp với audio YouTube.
rows = [
    (
        238.15, 241.38,
        "第三个计划是关于爱情的。",
        "Dì sān gè jìhuà shì guānyú àiqíng de.",
        "Kế hoạch thứ ba liên quan đến chuyện tình cảm."
    ),
    (
        241.38, 244.98,
        "这可能是我今年最期待的事情了。",
        "Zhè kěnéng shì wǒ jīnnián zuì qīdài de shìqing le.",
        "Đây có lẽ là điều tôi mong chờ nhất trong năm nay."
    ),
    (
        244.98, 254.64,
        "过去两年，我忙着学习，忙着适应工作，根本没有时间谈恋爱。",
        "Guòqù liǎng nián, wǒ mángzhe xuéxí, mángzhe shìyìng gōngzuò, gēnběn méiyǒu shíjiān tán liàn'ài.",
        "Hai năm qua, tôi bận học tập và thích nghi với công việc nên hoàn toàn không có thời gian yêu đương."
    ),
    (
        254.64, 260.18,
        "但是最近，我的生活里出现了一位特别的女孩。",
        "Dànshì zuìjìn, wǒ de shēnghuó lǐ chūxiàn le yí wèi tèbié de nǚhái.",
        "Nhưng gần đây, một cô gái đặc biệt đã xuất hiện trong cuộc sống của tôi."
    ),
    (
        260.18, 266.4,
        "她比我小两岁，长得非常漂亮，笑起来很甜。",
        "Tā bǐ wǒ xiǎo liǎng suì, zhǎng de fēicháng piàoliang, xiào qǐlái hěn tián.",
        "Cô ấy nhỏ hơn tôi hai tuổi, rất xinh đẹp và có nụ cười ngọt ngào."
    ),
    (
        266.4, 273.77,
        "我们已经一起出去吃过几次饭，也看过几次电影。",
        "Wǒmen yǐjīng yìqǐ chūqù chī guò jǐ cì fàn, yě kàn guò jǐ cì diànyǐng.",
        "Chúng tôi đã cùng nhau đi ăn vài lần và cũng đã xem phim cùng nhau vài lần."
    ),
    (
        273.77, 279.0,
        "在这个过程中，我发现我们的性格非常合适。",
        "Zài zhège guòchéng zhōng, wǒ fāxiàn wǒmen de xìnggé fēicháng héshì.",
        "Trong quá trình tìm hiểu, tôi nhận ra tính cách của chúng tôi rất hợp nhau."
    ),
    (
        279.0, 286.0,
        "跟她在一起的时候，我总是感到很放松，很开心。",
        "Gēn tā zài yìqǐ de shíhou, wǒ zǒng shì gǎndào hěn fàngsōng, hěn kāixīn.",
        "Khi ở bên cô ấy, tôi luôn cảm thấy rất thoải mái và vui vẻ."
    ),
    (
        286.0, 290.49,
        "我心里有一个小秘密。",
        "Wǒ xīn lǐ yǒu yí gè xiǎo mìmì.",
        "Trong lòng tôi có một bí mật nhỏ."
    ),
    (
        290.49, 297.08,
        "我打算在接下来的一两个月里，找一个合适的机会向她表白。",
        "Wǒ dǎsuàn zài jiē xiàlái de yì liǎng gè yuè lǐ, zhǎo yí gè héshì de jīhuì xiàng tā biǎobái.",
        "Tôi dự định trong một hai tháng tới sẽ tìm cơ hội thích hợp để tỏ tình với cô ấy."
    ),
    (
        297.08, 300.0,
        "希望她也喜欢我。",
        "Xīwàng tā yě xǐhuan wǒ.",
        "Hy vọng cô ấy cũng thích tôi."
    ),
    (
        300.0, 303.5,
        "希望我们能真的走到一起。",
        "Xīwàng wǒmen néng zhēn de zǒu dào yìqǐ.",
        "Hy vọng chúng tôi thực sự có thể đến với nhau."
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

# Kiểm tra dữ liệu trước khi xuất
assert new_sentences[0]["start"] >= data["sentences"][-1]["end"]

data["sentences"].extend(new_sentences)

assert len(data["sentences"]) == 53

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

print("===== TAO PHAN 4 THANH CONG =====")
print("YouTube ID:", data["youtube_id"])
print("So cau moi:", len(new_sentences))
print("Tong so cau:", len(data["sentences"]))
print("Thoi gian ket thuc:", data["sentences"][-1]["end"])
print("File:", OUTPUT)
print("Chua thay doi SQL Server")
