
import json
from pathlib import Path

ROOT = Path(r"D:\DATN1\scripts\shadowing\hsk1\previews")
OUTPUT = ROOT / "wo_de_xin_nian_ji_hua_part1_preview.json"

YOUTUBE_ID = "o6ilprwO6w0"

# Thời gian tính bằng giây, dựa trên transcript Supadata.
# Các mốc cần kiểm tra lại khi phát video thực tế.
rows = [
    (
        0.0, 3.8,
        "大家好，欢迎回到我的频道。",
        "Dàjiā hǎo, huānyíng huídào wǒ de píndào.",
        "Xin chào mọi người, chào mừng quay trở lại kênh của tôi."
    ),
    (
        3.8, 9.7,
        "今天是2026年第一个星期，大家都过得好吗？",
        "Jīntiān shì èr líng èr liù nián dì yī gè xīngqī, dàjiā dōu guò de hǎo ma?",
        "Hôm nay là tuần đầu tiên của năm 2026, mọi người vẫn ổn chứ?"
    ),
    (
        9.7, 15.6,
        "我现在正坐在上海的公寓里，看着窗外的风景。",
        "Wǒ xiànzài zhèng zuò zài Shànghǎi de gōngyù lǐ, kànzhe chuāngwài de fēngjǐng.",
        "Bây giờ tôi đang ngồi trong căn hộ ở Thượng Hải, ngắm nhìn cảnh vật ngoài cửa sổ."
    ),
    (
        15.6, 24.1,
        "虽然大家都沉浸在迎接新年的喜悦中，但在几天前，我其实一点也不开心。",
        "Suīrán dàjiā dōu chénjìn zài yíngjiē xīnnián de xǐyuè zhōng, dàn zài jǐ tiān qián, wǒ qíshí yìdiǎn yě bù kāixīn.",
        "Mặc dù mọi người đều đang đắm chìm trong niềm vui đón năm mới, nhưng vài ngày trước, thực ra tôi chẳng vui chút nào."
    ),
    (
        24.1, 31.5,
        "我是个地地道道的成都人，今年25岁。",
        "Wǒ shì ge dìdìdàodào de Chéngdū rén, jīnnián èrshíwǔ suì.",
        "Tôi là người Thành Đô chính gốc, năm nay 25 tuổi."
    ),
    (
        31.5, 36.0,
        "大学毕业后，我选择了留在上海打拼。",
        "Dàxué bìyè hòu, wǒ xuǎnzé le liú zài Shànghǎi dǎpīn.",
        "Sau khi tốt nghiệp đại học, tôi chọn ở lại Thượng Hải để lập nghiệp."
    ),
    (
        36.0, 43.9,
        "说实话，刚刚过去的2025年对我来说并不是很友好，",
        "Shuō shíhuà, gānggāng guòqù de èr líng èr wǔ nián duì wǒ lái shuō bìng bú shì hěn yǒuhǎo,",
        "Nói thật, năm 2025 vừa qua không phải là một năm dễ dàng đối với tôi,"
    ),
    (
        43.9, 47.3,
        "甚至可以说有些糟糕。",
        "Shènzhì kěyǐ shuō yǒuxiē zāogāo.",
        "thậm chí có thể nói là khá tồi tệ."
    ),
    (
        51.9, 54.3,
        "给了我不少压力。",
        "Gěi le wǒ bù shǎo yālì.",
        "Điều đó khiến tôi chịu không ít áp lực."
    ),
    (
        54.3, 61.8,
        "但是新的一年来了，我告诉自己，不能一直难过下去。",
        "Dànshì xīn de yì nián lái le, wǒ gàosu zìjǐ, bù néng yìzhí nánguò xiàqù.",
        "Nhưng năm mới đã đến, tôi tự nhủ rằng mình không thể cứ buồn mãi như vậy."
    ),
    (
        61.8, 67.9,
        "我相信2026年我会更幸运。",
        "Wǒ xiāngxìn èr líng èr liù nián wǒ huì gèng xìngyùn.",
        "Tôi tin rằng năm 2026 mình sẽ may mắn hơn."
    ),
    (
        67.9, 73.5,
        "今天我想跟朋友们聊聊我的新年计划。",
        "Jīntiān wǒ xiǎng gēn péngyou men liáoliao wǒ de xīnnián jìhuà.",
        "Hôm nay tôi muốn chia sẻ với mọi người về kế hoạch năm mới của mình."
    ),
    (
        73.5, 77.1,
        "虽然这些计划听起来很普通，",
        "Suīrán zhèxiē jìhuà tīng qǐlái hěn pǔtōng,",
        "Mặc dù những kế hoạch này nghe có vẻ rất bình thường,"
    ),
    (
        77.1, 82.3,
        "但对我来说，却是通往幸福的小步骤。",
        "Dàn duì wǒ lái shuō, què shì tōngwǎng xìngfú de xiǎo bùzhòu.",
        "nhưng đối với tôi, đó là những bước nhỏ dẫn đến hạnh phúc."
    ),
]

sentences = [
    {
        "start": start,
        "end": end,
        "hanzi": hanzi,
        "pinyin": pinyin,
        "vi": vi,
    }
    for start, end, hanzi, pinyin, vi in rows
]

data = {
    "module": "shadowing",
    "youtube_id": YOUTUBE_ID,
    "sentences": sentences,
}

# Kiểm tra cấu trúc và thứ tự timestamp.
assert len(sentences) == 14

for i, sentence in enumerate(sentences):
    assert sentence["start"] < sentence["end"], f"Lỗi thời gian câu {i + 1}"
    assert all(
        sentence[key].strip()
        for key in ("hanzi", "pinyin", "vi")
    ), f"Thiếu nội dung câu {i + 1}"

    if i > 0:
        assert (
            sentence["start"] >= sentences[i - 1]["end"]
        ), f"Thời gian chồng lấn ở câu {i + 1}"

ROOT.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("===== TAO PREVIEW THANH CONG =====")
print("Video:", YOUTUBE_ID)
print("So cau:", len(sentences))
print("Thoi gian:", sentences[0]["start"], "-", sentences[-1]["end"])
print("File:", OUTPUT)
print("Chua thay doi SQL Server")
