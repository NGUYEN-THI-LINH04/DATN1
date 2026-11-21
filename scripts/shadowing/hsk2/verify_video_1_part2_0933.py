
import json
from pathlib import Path

from .correct_video_1_part1 import make_pinyin

BASE = Path(__file__).resolve().parent
PREVIEWS = BASE / "previews"

INPUT = PREVIEWS / "video_1_part2_verified_0638.json"
OUTPUT = PREVIEWS / "video_1_part2_verified_0933.json"

# Mốc thời gian dựa trên thời điểm phụ đề xuất hiện.
# Chưa được kiểm chứng trực tiếp với audio.
# Không sử dụng các mốc này như timestamp cuối cùng.

LINES = [
    (398, "兔子像风一样跑了出去。非常快！",
     "Thỏ lao đi nhanh như gió. Nhanh vô cùng!"),
    (407, "一转眼，就看不见了。",
     "Chỉ trong chớp mắt đã không còn nhìn thấy nữa."),
    (411, "乌龟呢？他也在努力地跑。",
     "Còn rùa thì sao? Nó cũng đang cố gắng chạy."),
    (415, "但是，我们知道，他跑得很慢。",
     "Nhưng chúng ta biết nó chạy rất chậm."),
    (417, "他一步一步，慢慢地向前走。",
     "Nó từng bước, từng bước chậm rãi tiến về phía trước."),
    (422, "兔子跑了很远。",
     "Thỏ đã chạy được rất xa."),
    (425, "他回头看。他看不到乌龟。",
     "Nó ngoái đầu nhìn nhưng không thấy rùa."),
    (428, "一点儿也看不到。",
     "Hoàn toàn không nhìn thấy."),
    (431, "兔子想：“乌龟太慢了。",
     "Thỏ nghĩ: “Rùa chậm quá."),
    (434, "他可能明天早上才能到这里。",
     "Có lẽ sáng mai nó mới đến được đây."),
    (438, "天气这么好，我想在这里睡一会儿。",
     "Thời tiết đẹp thế này, mình muốn ngủ một lát ở đây."),
    (443, "我睡醒了，再跑也来得及。”",
     "Mình ngủ dậy rồi chạy tiếp vẫn kịp.”"),
    (443, "于是，兔子就在一棵大树下面，开始睡觉了。",
     "Thế là thỏ bắt đầu ngủ dưới một gốc cây lớn."),
    (452, "他睡得很香。",
     "Nó ngủ rất ngon."),
    (455, "这个时候，乌龟在哪里呢？",
     "Lúc này rùa đang ở đâu?"),
    (458, "乌龟还在路上。",
     "Rùa vẫn đang trên đường."),
    (461, "他很累，也很热。",
     "Nó rất mệt và cũng rất nóng."),
    (464, "但是他没有休息。",
     "Nhưng nó không nghỉ ngơi."),
    (466, "他心里想：“我一定要坚持。",
     "Nó thầm nghĩ: “Mình nhất định phải kiên trì."),
    (470, "我不能停。”",
     "Mình không thể dừng lại.”"),
    (470, "所以，乌龟一直走，一直走。",
     "Vì vậy rùa cứ đi mãi, đi mãi."),
    (476, "他走得很慢，但是他没有停。",
     "Nó đi rất chậm nhưng không dừng lại."),
    (480, "过了一会儿，乌龟走到了那棵大树下面。",
     "Một lúc sau, rùa đi đến dưới gốc cây lớn đó."),
    (486, "他看到了谁？",
     "Nó nhìn thấy ai?"),
    (487, "他看到了正在睡觉的兔子。",
     "Nó nhìn thấy thỏ đang ngủ."),
    (491, "对。兔子睡得正香呢。",
     "Đúng vậy. Thỏ đang ngủ rất say."),
    (495, "乌龟看了看兔子，他什么也没说，继续一步一步，慢慢地向前走。",
     "Rùa nhìn thỏ, không nói gì và tiếp tục từng bước đi về phía trước."),
    (504, "又过了很久很久，兔子醒了。",
     "Rất lâu sau, thỏ tỉnh dậy."),
    (508, "他睁开眼睛，伸了一个懒腰。",
     "Nó mở mắt và vươn vai."),
    (511, "他说：“啊，我睡得真好！",
     "Nó nói: “A, mình ngủ ngon quá!"),
    (514, "现在，乌龟到哪里了？”",
     "Bây giờ rùa đến đâu rồi nhỉ?”"),
    (514, "他向后看，没有乌龟。",
     "Nó nhìn ra phía sau nhưng không thấy rùa."),
    (521, "他又向前看……他看到了什么？",
     "Nó lại nhìn về phía trước... Nó đã nhìn thấy gì?"),
    (525, "他看到，乌龟已经快要到终点了！",
     "Nó thấy rùa đã sắp đến đích!"),
    (530, "兔子非常着急！",
     "Thỏ vô cùng sốt ruột!"),
    (532, "他马上开始跑。",
     "Nó lập tức bắt đầu chạy."),
    (534, "他跑得很快很快，比以前更快！",
     "Nó chạy rất nhanh, còn nhanh hơn trước!"),
    (538, "但是，太晚了。",
     "Nhưng đã quá muộn."),
    (542, "是的，太晚了。",
     "Đúng vậy, đã quá muộn."),
    (544, "就在兔子快要追上的时候，乌龟慢慢地走过了终点线。",
     "Ngay khi thỏ sắp đuổi kịp, rùa chậm rãi bước qua vạch đích."),
    (551, "所以，比赛结束了。",
     "Vậy là cuộc thi kết thúc."),
    (554, "谁是第一名？",
     "Ai là người về nhất?"),
    (556, "是那只走得很慢，但是一直没有放弃的乌龟。",
     "Chính là chú rùa đi rất chậm nhưng chưa từng bỏ cuộc."),
    (563, "这个故事讲完了。",
     "Câu chuyện đã kể xong."),
    (566, "虽然我们都知道这个故事，但是现在再说一遍，还是觉得很有意思。",
     "Dù chúng ta đều biết câu chuyện này, kể lại vẫn thấy rất thú vị."),
    (573, "是啊。一个简单的故事，但是有一个很重要的道理。",
     "Đúng vậy. Một câu chuyện đơn giản nhưng chứa đựng một bài học rất quan trọng."),
]


def main():
    if not INPUT.exists():
        raise FileNotFoundError(INPUT)

    if OUTPUT.exists():
        raise FileExistsError(
            f"File da ton tai, khong ghi de: {OUTPUT}"
        )

    with INPUT.open("r", encoding="utf-8-sig") as f:
        old_data = json.load(f)

    if not isinstance(old_data, list) or len(old_data) != 50:
        raise ValueError("File dau vao phai co 50 muc.")

    # Giữ nguyên 27 mục đã đối chiếu trước đó.
    result = old_data[:27]

    for i, (start, hanzi, vi) in enumerate(LINES):
        # Mốc kết thúc tạm là mốc phụ đề kế tiếp.
        # Các câu có cùng mốc bắt đầu sẽ được đánh dấu
        # để kiểm tra, không tự tạo timestamp giả.
        next_start = (
            LINES[i + 1][0]
            if i + 1 < len(LINES)
            else None
        )

        item = {
            "start": float(start),
            "end": (
                float(next_start)
                if next_start is not None and next_start > start
                else None
            ),
            "hanzi": hanzi,
            "pinyin": make_pinyin(hanzi),
            "vi": vi,
            "_review_status": "hanzi_da_doi_chieu_phu_de",
            "_timing_status": "chua_xac_minh_audio",
            "_subtitle_reference_seconds": start,
        }

        result.append(item)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("===== HSK2 VIDEO 1 - DOI CHIEU DEN 09:33 =====")
    print("Muc giu nguyen:", 27)
    print("Muc moi:", len(LINES))
    print("Tong muc:", len(result))
    print("File:", OUTPUT)

    unresolved = [
        i + 1 for i, item in enumerate(result)
        if item.get("end") is None
    ]

    print("Muc chua co end hop le:", unresolved)
    print("Timestamp moi chi la moc phu de tam.")
    print("Khong goi Supadata.")
    print("Chua thay doi SQL Server.")
    print("Khong thay doi HSK1.")
    print("Khong ghi de file cu.")


if __name__ == "__main__":
    main()
