
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1\scripts\shadowing\hsk1\previews")
SOURCE = ROOT / "wo_de_xin_nian_ji_hua_part2_preview.json"
OUTPUT = ROOT / "wo_de_xin_nian_ji_hua_part3_preview.json"

with SOURCE.open("r", encoding="utf-8") as f:
    data = json.load(f)

assert data["youtube_id"] == "o6ilprwO6w0"
assert len(data["sentences"]) == 25

# Phần 3: Công việc và quyết định nghỉ việc.
# Thời gian dựa trên transcript Supadata, chưa xác minh bằng audio.
rows = [
    (
        144.82, 149.08,
        "第二个计划是关于工作的。",
        "Dì èr gè jìhuà shì guānyú gōngzuò de.",
        "Kế hoạch thứ hai liên quan đến công việc."
    ),
    (
        149.08, 153.32,
        "这也是我去年最头疼的事情。",
        "Zhè yě shì wǒ qùnián zuì tóuténg de shìqing.",
        "Đây cũng là chuyện khiến tôi đau đầu nhất trong năm ngoái."
    ),
    (
        153.32, 159.32,
        "毕业后，我在一家广告公司工作了整整一年。",
        "Bìyè hòu, wǒ zài yì jiā guǎnggào gōngsī gōngzuò le zhěngzhěng yì nián.",
        "Sau khi tốt nghiệp, tôi đã làm việc tại một công ty quảng cáo tròn một năm."
    ),
    (
        159.32, 165.31,
        "我知道在上海工作不容易，所以我非常努力。",
        "Wǒ zhīdào zài Shànghǎi gōngzuò bù róngyì, suǒyǐ wǒ fēicháng nǔlì.",
        "Tôi biết làm việc ở Thượng Hải không dễ dàng, vì vậy tôi đã rất cố gắng."
    ),
    (
        165.31, 170.07,
        "大家下班的时候，我经常还在加班。",
        "Dàjiā xiàbān de shíhou, wǒ jīngcháng hái zài jiābān.",
        "Khi mọi người tan làm, tôi thường vẫn đang tăng ca."
    ),
    (
        170.07, 176.15,
        "可是，我每个月拿到手的工资只有八千块。",
        "Kěshì, wǒ měi gè yuè ná dào shǒu de gōngzī zhǐyǒu bā qiān kuài.",
        "Nhưng lương thực nhận mỗi tháng của tôi chỉ có 8.000 tệ."
    ),
    (
        176.15, 183.33,
        "除去五千五百块的房租，我只剩下两千五百块生活。",
        "Chúqù wǔ qiān wǔ bǎi kuài de fángzū, wǒ zhǐ shèng xià liǎng qiān wǔ bǎi kuài shēnghuó.",
        "Trừ đi 5.500 tệ tiền thuê nhà, tôi chỉ còn 2.500 tệ để sinh hoạt."
    ),
    (
        183.33, 191.0,
        "在上海，这点钱连吃饭都得精打细算，根本存不下钱。",
        "Zài Shànghǎi, zhè diǎn qián lián chīfàn dōu děi jīngdǎxìsuàn, gēnběn cún bu xià qián.",
        "Ở Thượng Hải, với số tiền này ngay cả việc ăn uống cũng phải tính toán kỹ, hoàn toàn không thể tiết kiệm được."
    ),
    (
        192.62, 199.22,
        "去年年底，我鼓起勇气跟老板提了涨工资的要求。",
        "Qùnián niándǐ, wǒ gǔ qǐ yǒngqì gēn lǎobǎn tí le zhǎng gōngzī de yāoqiú.",
        "Cuối năm ngoái, tôi lấy hết can đảm đề nghị sếp tăng lương."
    ),
    (
        199.22, 208.02,
        "可是，老板说公司现在的经济情况很困难，拒绝了我。",
        "Kěshì, lǎobǎn shuō gōngsī xiànzài de jīngjì qíngkuàng hěn kùnnan, jùjué le wǒ.",
        "Nhưng sếp nói tình hình tài chính của công ty đang khó khăn nên đã từ chối tôi."
    ),
    (
        208.02, 211.24,
        "那一刻，我真的很难过。",
        "Nà yí kè, wǒ zhēn de hěn nánguò.",
        "Khoảnh khắc đó, tôi thực sự rất buồn."
    ),
    (
        211.24, 216.76,
        "所以，我做了一个勇敢的决定，我辞职了。",
        "Suǒyǐ, wǒ zuò le yí gè yǒnggǎn de juédìng, wǒ cízhí le.",
        "Vì vậy, tôi đã đưa ra một quyết định dũng cảm: tôi nghỉ việc."
    ),
    (
        217.93, 223.01,
        "下周我准备向几家大公司投简历。",
        "Xià zhōu wǒ zhǔnbèi xiàng jǐ jiā dà gōngsī tóu jiǎnlì.",
        "Tuần sau tôi dự định gửi hồ sơ xin việc đến một vài công ty lớn."
    ),
    (
        223.01, 230.69,
        "我的新年愿望是能收到一份月薪在一万二以上的新工作。",
        "Wǒ de xīnnián yuànwàng shì néng shōudào yí fèn yuèxīn zài yí wàn èr yǐshàng de xīn gōngzuò.",
        "Điều ước năm mới của tôi là tìm được công việc mới với mức lương trên 12.000 tệ mỗi tháng."
    ),
    (
        230.69, 235.8,
        "这样，我每个月就能存下一点钱了。",
        "Zhèyàng, wǒ měi gè yuè jiù néng cún xià yìdiǎn qián le.",
        "Như vậy, mỗi tháng tôi có thể tiết kiệm được một ít tiền."
    ),
    (
        235.8, 238.15,
        "祝我好运吧！",
        "Zhù wǒ hǎoyùn ba!",
        "Chúc tôi may mắn nhé!"
    ),
]

# Tránh ghi trùng khi chạy lại.
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

assert data["sentences"][-1]["end"] <= new_sentences[0]["start"]

data["sentences"].extend(new_sentences)

assert len(data["sentences"]) == 41

for i, sentence in enumerate(data["sentences"]):
    assert sentence["start"] < sentence["end"], f"Lỗi câu {i + 1}"
    assert all(
        sentence[key].strip()
        for key in ("hanzi", "pinyin", "vi")
    ), f"Thiếu nội dung câu {i + 1}"

    if i > 0:
        assert (
            sentence["start"] >= data["sentences"][i - 1]["end"]
        ), f"Timestamp chồng lấn ở câu {i + 1}"

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("===== TAO PHAN 3 THANH CONG =====")
print("YouTube ID:", data["youtube_id"])
print("So cau moi:", len(new_sentences))
print("Tong so cau:", len(data["sentences"]))
print("Thoi gian ket thuc:", data["sentences"][-1]["end"])
print("File:", OUTPUT)
print("Chua thay doi SQL Server")
