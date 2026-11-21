
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1\scripts\shadowing\hsk1\previews")
SOURCE = ROOT / "wo_de_xin_nian_ji_hua_part1_preview.json"
OUTPUT = ROOT / "wo_de_xin_nian_ji_hua_part2_preview.json"

with SOURCE.open("r", encoding="utf-8") as f:
    data = json.load(f)

assert data["youtube_id"] == "o6ilprwO6w0"
assert len(data["sentences"]) == 14

# Phần 2: Kế hoạch chuyển nhà
# Timestamp dựa trên transcript Supadata, cần kiểm tra lại với video.
rows = [
    (
        82.3, 86.9,
        "第一个计划是关于家的。",
        "Dì yī gè jìhuà shì guānyú jiā de.",
        "Kế hoạch đầu tiên của tôi liên quan đến chuyện nhà ở."
    ),
    (
        86.9, 91.8,
        "我现在一个人住在一个很小的公寓里。",
        "Wǒ xiànzài yí gè rén zhù zài yí gè hěn xiǎo de gōngyù lǐ.",
        "Hiện tại tôi sống một mình trong một căn hộ rất nhỏ."
    ),
    (
        91.8, 96.0,
        "虽然我很爱在这个城市的独立生活，",
        "Suīrán wǒ hěn ài zài zhège chéngshì de dúlì shēnghuó,",
        "Mặc dù tôi rất thích cuộc sống tự lập ở thành phố này,"
    ),
    (
        96.0, 100.7,
        "但是这里的房租实在太高了。",
        "Dànshì zhèlǐ de fángzū shízài tài gāo le.",
        "nhưng tiền thuê nhà ở đây thực sự quá cao."
    ),
    (
        100.7, 109.9,
        "大家可能不相信，我每个月的房租是五千五百块人民币。",
        "Dàjiā kěnéng bù xiāngxìn, wǒ měi gè yuè de fángzū shì wǔ qiān wǔ bǎi kuài rénmínbì.",
        "Có lẽ mọi người sẽ không tin, tiền thuê nhà mỗi tháng của tôi là 5.500 nhân dân tệ."
    ),
    (
        109.9, 115.0,
        "对年轻人来说，真的是一笔巨大的开销。",
        "Duì niánqīng rén lái shuō, zhēn de shì yì bǐ jùdà de kāixiāo.",
        "Đối với người trẻ, đây thực sự là một khoản chi phí rất lớn."
    ),
    (
        115.0, 121.6,
        "好消息是，下个月我的租房合同就要到期了。",
        "Hǎo xiāoxi shì, xià gè yuè wǒ de zūfáng hétong jiù yào dàoqī le.",
        "Tin tốt là hợp đồng thuê nhà của tôi sẽ hết hạn vào tháng sau."
    ),
    (
        121.6, 127.0,
        "所以我决定要在这个月找到一个新的住处。",
        "Suǒyǐ wǒ juédìng yào zài zhège yuè zhǎodào yí gè xīn de zhùchù.",
        "Vì vậy tôi quyết định sẽ tìm một chỗ ở mới ngay trong tháng này."
    ),
    (
        127.0, 134.0,
        "我的目标是找到一个租金在三千五百块左右的房子。",
        "Wǒ de mùbiāo shì zhǎodào yí gè zūjīn zài sān qiān wǔ bǎi kuài zuǒyòu de fángzi.",
        "Mục tiêu của tôi là tìm một căn nhà có giá thuê khoảng 3.500 tệ."
    ),
    (
        134.0, 137.1,
        "虽然可能会远一点，或者是合租，",
        "Suīrán kěnéng huì yuǎn yìdiǎn, huòzhě shì hézū,",
        "Dù có thể sẽ xa hơn một chút hoặc phải ở ghép,"
    ),
    (
        137.1, 144.8,
        "但只要能省下两千块钱，我觉得也是值得的。",
        "Dàn zhǐyào néng shěng xià liǎng qiān kuài qián, wǒ juéde yě shì zhíde de.",
        "nhưng chỉ cần tiết kiệm được 2.000 tệ, tôi thấy cũng rất đáng."
    ),
]

for start, end, hanzi, pinyin, vi in rows:
    data["sentences"].append({
        "start": start,
        "end": end,
        "hanzi": hanzi,
        "pinyin": pinyin,
        "vi": vi,
    })

# Kiểm tra tính hợp lệ
assert len(data["sentences"]) == 25

for i, sentence in enumerate(data["sentences"]):
    assert sentence["start"] < sentence["end"], f"Lỗi câu {i + 1}"

    if i > 0:
        assert (
            sentence["start"] >= data["sentences"][i - 1]["end"]
        ), f"Timestamp chồng lấn tại câu {i + 1}"

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("===== TAO PHAN 2 THANH CONG =====")
print("YouTube ID:", data["youtube_id"])
print("Tong so cau:", len(data["sentences"]))
print("Thoi gian ket thuc:", data["sentences"][-1]["end"])
print("File:", OUTPUT)
print("Chua thay doi SQL Server")
