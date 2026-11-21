
import json
import math
import re
from pathlib import Path

from pypinyin import lazy_pinyin, Style


# ==================================================
# 1. CAU HINH HSK3 - VIDEO 5
# ==================================================

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk3")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video5_zh_preview.json"
OUTPUT = DATA / "video5_translated_full.json"
REPORT = DATA / "video5_review_report.txt"

VIDEO_ID = "2EythZkR8w8"
EXPECTED_COUNT = 146


# ==================================================
# 2. BAN DICH TIENG VIET - 146 DOAN
#
# Moi dong: STT|Ban dich
# STT phai trung voi transcript Supadata.
# ==================================================

TRANSLATION_TEXT = """
001|À, Lý Minh, bạn xem này, bây giờ đã năm giờ chiều rồi. Hôm nay là thứ Sáu! Bạn có vui không?
002|Haha, Vương Vũ, tôi thấy bạn rất vui. Đúng vậy, tôi cũng rất vui.
003|Cả tuần công việc bận rộn, tôi cảm thấy hơi mệt.
004|Đúng, tôi cũng vậy. Thứ Hai, thứ Ba, thứ Tư, thứ Năm... ngày nào cũng cảm thấy thời gian trôi rất chậm.
005|Nhưng hôm nay tôi lại thấy thời gian trôi rất nhanh!
006|Tôi hoàn toàn hiểu. Cảm giác vào chiều thứ Sáu là tuyệt nhất.
007|Vậy cuối tuần này bạn có kế hoạch gì không? Đã nghĩ xem sẽ làm gì chưa?
008|Kế hoạch à? Tôi có rất, rất nhiều kế hoạch! Cuối tuần của tôi sẽ vô cùng thú vị.
009|Còn bạn? Bạn nói trước đi, kế hoạch cuối tuần của bạn là gì?
010|Tôi à? Kế hoạch của tôi rất đơn giản. Nhưng tôi vẫn muốn nghe kế hoạch thú vị của bạn trước.
011|Kế hoạch của bạn chắc chắn thú vị hơn của tôi.
012|Haha, được thôi! Vậy tôi nói trước nhé.
013|Được, mời bạn nói. Tôi đang nghe đây.
014|Ừm... để tôi nghĩ xem. Ngày mai là thứ Bảy. Sáng thứ Bảy, tôi và bạn thân sẽ đi mua sắm.
015|Đi mua sắm à? Hai bạn định mua gì?
016|Chúng tôi muốn mua quần áo mới.
017|Tuần sau là sinh nhật Tiểu Lệ, tôi muốn mua tặng cô ấy một bộ quần áo đẹp.
018|Tôi cũng muốn mua cho mình một ít đồ.
019|Kế hoạch này hay đấy.
020|Vậy buổi chiều thì sao? Mua sắm xong, các bạn làm gì?
021|Buổi chiều chúng tôi muốn đi xem một bộ phim mới.
022|Tôi nghe nói bộ phim này rất hay, nhiều người đều nói muốn xem.
023|Bạn có thích xem phim không?
024|Tôi rất thích. Nhưng tôi thích xem ở nhà hơn.
025|Rạp chiếu phim đông người quá.
026|Thế à? Tôi lại thấy xem phim ở rạp có cảm giác tuyệt hơn!
027|Màn hình rất lớn, âm thanh cũng rất to.
028|Mọi người cùng cười, cùng khóc, rất thú vị.
029|Ừm, điều đó cũng đúng.
030|Vậy xem phim xong, buổi tối các bạn ăn gì?
031|Chúng tôi định đến một nhà hàng mới.
032|Bạn tôi nói món Trung Quốc ở đó được nấu đặc biệt ngon.
033|Tôi rất muốn đến ăn thử.
034|Vậy thứ Bảy sẽ là: mua sắm, xem phim và ăn món ngon!
035|Thế nào? Kế hoạch của tôi có tuyệt không?
036|Nghe thật sự rất hay.
037|Bạn của bạn chắc chắn sẽ rất vui. Một ngày thứ Bảy vô cùng vui vẻ.
038|Vậy còn Chủ nhật thì sao?
039|Chủ nhật à... Chủ nhật tôi vẫn chưa nghĩ xong.
040|Có lẽ buổi sáng ngủ ở nhà, buổi chiều cùng gia đình đi dạo công viên nếu thời tiết đẹp.
041|Nghe có vẻ rất thư giãn.
042|Vậy cuối tuần của bạn là một ngày rất bận rộn, một ngày rất thư giãn.
043|Đúng! Chính là như vậy!
044|Được rồi, tôi nói xong rồi. Bây giờ đến lượt bạn.
045|Lý Minh, mau kể cho chúng tôi nghe kế hoạch cuối tuần "đơn giản" của bạn là gì?
046|Haha, kế hoạch của tôi rất khác bạn.
047|Nghe xong có lẽ bạn sẽ thấy hơi nhàm chán.
048|Không sao, bạn cứ kể đi. Tôi rất tò mò.
049|Được. Ngày mai, thứ Bảy, buổi sáng tôi muốn ở nhà đọc sách.
050|Ở nhà đọc sách à?
051|Đúng. Trên bàn tôi có rất nhiều sách mới, tuần này công việc quá bận, tôi chưa đọc được trang nào.
052|Vì vậy cuối tuần tôi muốn yên tĩnh đọc sách một chút.
053|Được thôi. Vậy buổi chiều thì sao? Cũng đọc sách à?
054|Buổi chiều có lẽ tôi sẽ nghe nhạc và uống trà.
055|Nếu thời tiết đẹp, tôi sẽ mở cửa sổ, ngắm nhìn bầu trời xanh bên ngoài.
056|Tôi thấy như vậy đặc biệt dễ chịu.
057|Trời ơi! Lý Minh! Bạn giống một ông cụ quá! Đọc sách, uống trà!
058|Haha, bạn không thích sao?
059|Tôi thấy như thế mới thật sự là nghỉ ngơi.
060|Còn buổi tối, có lẽ tôi sẽ tự nấu vài món ngon, rồi ở nhà xem một bộ phim cũ.
061|Được rồi, nghe có vẻ... rất yên tĩnh.
062|Vậy Chủ nhật bạn làm gì?
063|Không lẽ cũng ở nhà sao?
064|Đúng vậy, Chủ nhật tôi cũng ở nhà.
065|Tôi định dọn dẹp nhà cửa, làm cho căn phòng thật sạch sẽ.
066|Sau đó buổi chiều, có lẽ tôi sẽ đến siêu thị lớn gần nhà mua một ít trái cây và rau.
067|Vậy cả hai ngày cuối tuần, về cơ bản bạn đều ở nhà hoặc quanh khu vực gần nhà?
068|Có thể nói như vậy. Tôi thích ở nhà. Nhà khiến tôi cảm thấy an toàn và thư giãn.
069|Tôi hiểu rồi. Hai chúng ta thật sự rất khác nhau.
070|Tôi thích ra ngoài, thích ở cùng bạn bè và thích không khí náo nhiệt.
071|Bạn thích ở nhà, thích ở một mình và thích sự yên tĩnh.
072|Đúng vậy. Tôi nghĩ không có đúng sai, chỉ là lựa chọn của mỗi người khác nhau.
073|Khi ở cùng bạn bè, có phải bạn thấy rất vui và quên đi sự mệt mỏi trong công việc không?
074|Đúng! Bạn nói chính xác quá!
075|Cùng bạn bè trò chuyện vui vẻ, ăn những món ngon, xem những bộ phim hay,
076|tôi cảm thấy mọi mệt mỏi cả tuần đều biến mất. Tôi thấy đó mới là cuộc sống.
077|Ừm. Nhưng với tôi, nếu cuối tuần cũng đến nơi đông người và trò chuyện với nhiều người, tôi sẽ thấy mệt hơn.
078|Vì công việc của tôi ngày nào cũng phải nói chuyện và gặp gỡ rất nhiều người.
079|À, tôi hiểu rồi.
080|Vậy đến cuối tuần, bạn không muốn nói chuyện, cũng không muốn gặp ai nữa.
081|Đúng vậy. Tôi cần một khoảng thời gian và không gian hoàn toàn yên tĩnh để ở một mình.
082|Đối với tôi, đó là cách nghỉ ngơi tốt nhất.
083|Giống như bạn nói, sự mệt mỏi cả tuần sẽ biến mất nhờ đọc sách và nghe nhạc.
084|Thú vị thật, rất thú vị.
085|Cách nghỉ ngơi của chúng ta khác nhau nhưng mục đích đều giống nhau, đó là để thứ Hai có trạng thái tốt hơn khi làm việc.
086|Bạn nói rất đúng. Nhưng chúng ta cũng có điểm giống nhau.
087|Ồ? Là gì vậy?
088|Chúng ta đều thích đồ ăn ngon và thích xem phim.
089|Bạn thích đến nhà hàng mới để ăn, còn tôi thích tự nấu ở nhà.
090|Bạn thích xem ở rạp chiếu phim, còn tôi thích xem trên máy tính.
091|Chúng ta thích những thứ giống nhau, chỉ khác cách tận hưởng chúng.
092|Haha, đúng vậy! Ví dụ ở nhà bạn thích nấu món gì?
093|Tôi thích làm những món ăn gia đình đơn giản, như trứng xào cà chua hoặc gói bánh chẻo.
094|Gói bánh chẻo à? Bạn biết gói bánh chẻo sao? Giỏi quá!
095|Tôi biết một chút. Cuối tuần ở nhà cùng gia đình gói bánh chẻo là một việc rất hạnh phúc.
096|Bánh chẻo rất ngon, hơn nữa mọi người có thể vừa gói vừa trò chuyện.
097|Ừm, nghe tuyệt thật. Đó là niềm vui khi được ở bên gia đình.
098|Tôi hiểu rồi, niềm vui của bạn là niềm vui yên tĩnh, ở trong nhà.
099|Còn niềm vui của tôi là niềm vui náo nhiệt, ở bên ngoài.
100|Nhưng nói thật, Lý Minh, đôi khi tôi cũng cảm thấy ra ngoài chơi rất mệt.
101|Ồ? Thật vậy sao?
102|Đúng vậy. Có những cuối tuần tôi chơi quá vui và còn đi ngủ muộn.
103|Đến sáng thứ Hai, tôi thấy mình còn mệt hơn cả thứ Sáu! Tôi không biết tại sao.
104|Tôi hoàn toàn hiểu cảm giác của bạn. Rất nhiều người cũng gặp vấn đề này.
105|Tôi nghĩ đối với chúng ta, nghỉ ngơi giống như sạc pin cho điện thoại.
106|Sạc pin điện thoại à? Cách nói này thú vị đấy. Ý bạn là sao?
107|Bạn xem, cơ thể chúng ta giống như điện thoại, làm việc một ngày thì pin lại giảm đi một chút.
108|Làm việc cả tuần thì pin gần như cạn rồi.
109|Cuối tuần chính là thời gian sạc pin của chúng ta.
110|Ừm, đúng vậy.
111|Có những người như bạn, cách sạc pin là "sạc nhanh".
112|Bạn cần ra ngoài, gặp bạn bè và làm nhiều việc thú vị,
113|sau đó pin của bạn nhanh chóng đầy lại, tràn đầy năng lượng.
114|Haha, "sạc nhanh"! Tôi thích từ này!
115|Còn có những người như tôi, cách sạc pin là "sạc chậm".
116|Tôi cần tắt điện thoại, yên tĩnh đặt nó sang một bên, không sử dụng.
117|Nghĩa là tôi cần ở nhà một mình, đọc sách, nghe nhạc, rồi từ từ pin của tôi cũng đầy lại.
118|Ồ, phép so sánh của bạn hay quá!
119|"Sạc nhanh" và "sạc chậm". Tôi hiểu rồi!
120|Vậy có khi thứ Hai tôi cảm thấy mệt là vì cuối tuần tôi "sạc pin" quá nhanh, đến mức điện thoại nóng lên!
121|Haha, có lẽ là vậy.
122|Vì vậy không có phương pháp sạc pin nào là tốt nhất cho tất cả mọi người.
123|Điều quan trọng nhất là tìm ra cách "sạc pin" phù hợp nhất với chính mình.
124|Đôi khi bạn có thể "sạc nhanh", đôi khi cũng có thể thử "sạc chậm".
125|Bạn nói đúng. Có lẽ cuối tuần sau tôi sẽ thử cách của bạn.
126|Thứ Bảy ở nhà cả ngày, đọc sách và nghe nhạc. Có thể cảm giác sẽ rất khác.
127|Tất nhiên rồi. Bạn cũng có thể thử nấu ăn ở nhà. Đồ ăn tự mình nấu cảm giác đặc biệt thơm ngon.
128|Được! Tôi quyết định rồi! Cuối tuần sau tôi sẽ ở nhà làm món trứng xào cà chua cho bạn!
129|Haha, được thôi, tôi đợi đấy.
130|Được rồi, hôm nay chúng ta trò chuyện rất vui. Cũng gần hết thời gian rồi.
131|Hôm nay chúng ta đã nói nhiều từ liên quan đến "cuối tuần", hy vọng giúp ích cho những bạn đang học tiếng Trung.
132|Đúng vậy, chúng ta cùng tổng kết ngắn gọn nhé?
133|Được. Chúng ta đã nói về "cuối tuần" và "kế hoạch".
134|Kế hoạch của Vương Vũ là "ra ngoài chơi", như "đi mua sắm", "xem phim" và "ăn món ngon".
135|Đúng, kế hoạch của Lý Minh là "ở nhà", như "đọc sách", "nghe nhạc" và "nấu ăn".
136|Từ quan trọng nhất là "nghỉ ngơi".
137|Đúng vậy. Chúng ta còn nói rằng nghỉ ngơi giống như "sạc pin" cho điện thoại.
138|Bạn có thể chọn "sạc nhanh", cũng có thể chọn "sạc chậm".
139|Bạn tổng kết hay quá. Vậy các bạn đang nghe chương trình, kế hoạch cuối tuần của các bạn là gì?
140|Các bạn thích ở nhà nghỉ ngơi như Lý Minh, hay thích ra ngoài chơi như Vương Vũ?
141|Cách "sạc lại năng lượng" của các bạn là gì?
142|Nếu muốn, các bạn có thể dùng tiếng Trung đơn giản để chia sẻ với chúng tôi.
143|Chúng tôi rất mong được nghe câu trả lời của các bạn.
144|Được rồi, chương trình hôm nay đến đây thôi. Cảm ơn mọi người đã lắng nghe.
145|Hẹn gặp lại mọi người lần sau!
146|Hẹn gặp lại!
""".strip()


# ==================================================
# 3. KIEM TRA DAY DU BAN DICH
# ==================================================

def load_translations():

    translations = {}

    for line_no, line in enumerate(
        TRANSLATION_TEXT.splitlines(), 1
    ):

        line = line.strip()

        if not line:
            continue

        number_text, separator, vi = line.partition("|")

        if not separator or not number_text.isdigit():
            raise ValueError(
                f"Ban dich sai dinh dang tai dong {line_no}"
            )

        number = int(number_text)

        if number in translations:
            raise ValueError(
                f"Trung so thu tu {number}"
            )

        if not vi.strip():
            raise ValueError(
                f"Doan {number} chua co ban dich"
            )

        translations[number] = vi.strip()

    expected = set(range(1, EXPECTED_COUNT + 1))

    missing = sorted(expected - set(translations))
    extra = sorted(set(translations) - expected)

    if missing or extra:
        raise ValueError(
            f"Ban dich thieu {missing}, thua {extra}"
        )

    return translations


# ==================================================
# 4. TAO PINYIN CO DAU THANH
# ==================================================

def make_pinyin(hanzi):

    tokens = re.findall(
        r"[\u3400-\u9fff]+|[A-Za-z0-9]+",
        hanzi
    )

    result = []

    for token in tokens:

        if re.fullmatch(
            r"[\u3400-\u9fff]+",
            token
        ):
            result.extend(
                lazy_pinyin(
                    token,
                    style=Style.TONE
                )
            )

        else:
            result.append(token)

    return " ".join(result).strip()


# ==================================================
# 5. DOC PHU DE VA GHEP BAN DICH
# ==================================================

def main():

    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file: {SOURCE}"
        )

    data = json.loads(
        SOURCE.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError("JSON nguon khong hop le.")

    if data.get("module") != "shadowing":
        raise ValueError("Sai module Shadowing.")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError(
            "YouTube ID khong khop HSK3 video 5."
        )

    original = data.get("sentences")

    if not isinstance(original, list):
        raise ValueError(
            "sentences phai la danh sach."
        )

    if len(original) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} doan, "
            f"hien co {len(original)}."
        )

    translations = load_translations()

    sentences = []
    short_segments = []
    long_segments = []

    previous_end = 0.0

    for i, item in enumerate(original, 1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Doan {i} khong hop le."
            )

        start = float(item["start"])
        end = float(item["end"])

        if not (
            math.isfinite(start)
            and math.isfinite(end)
        ):
            raise ValueError(
                f"Timestamp khong hop le o doan {i}."
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Timestamp sai o doan {i}."
            )

        if i > 1 and start < previous_end - 0.001:
            raise ValueError(
                f"Timestamp chong nhau o doan {i}."
            )

        # Giu nguyen chu Han goc cua Supadata.
        hanzi = str(item["hanzi"]).strip()

        pinyin = make_pinyin(hanzi)
        vi = translations[i]

        if not hanzi or not pinyin or not vi:
            raise ValueError(
                f"Thieu noi dung o doan {i}."
            )

        duration = round(end - start, 3)

        if duration < 0.8:
            short_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        if duration > 10:
            long_segments.append({
                "number": i,
                "duration": duration,
                "hanzi": hanzi
            })

        sentences.append({
            "start": start,
            "end": end,
            "hanzi": hanzi,
            "pinyin": pinyin,
            "vi": vi
        })

        previous_end = end

    # ==================================================
    # 6. LUU JSON HOAN CHINH
    # ==================================================

    document = {
        "module": "shadowing",
        "youtube_id": VIDEO_ID,
        "sentences": sentences
    }

    OUTPUT.write_text(
        json.dumps(
            document,
            ensure_ascii=False,
            indent=2,
            allow_nan=False
        ),
        encoding="utf-8"
    )

    # ==================================================
    # 7. TAO BAO CAO KIEM TRA
    # ==================================================

    lines = [
        "SHADOWING HSK3 - VIDEO 5",
        f"YouTube: {VIDEO_ID}",
        f"So doan: {len(sentences)}",
        f"So ban dich: {len(translations)}",
        f"Doan ngan < 0.8s: {len(short_segments)}",
        f"Doan dai > 10s: {len(long_segments)}",
        "Timestamp chong nhau: 0",
        "",
        "===== DOAN QUA NGAN ====="
    ]

    for item in short_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.append("")
    lines.append("===== DOAN QUA DAI =====")

    for item in long_segments:
        lines.append(
            f"{item['number']:03d} | "
            f"{item['duration']:.3f}s | "
            f"{item['hanzi']}"
        )

    lines.extend([
        "",
        "===== NOI DUNG CAN RA SOAT =====",
        "014: Doan dai hon 10 giay.",
        "093-096: Cach noi ve mon banh cheo.",
        "105-124: Phep so sanh sac pin.",
        "Pinyin tu dong can kiem tra tu da am.",
        "Ban dich can doi chieu voi am thanh goc.",
        "",
        "CHUA CAP NHAT SQL SERVER."
    ])

    REPORT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    # ==================================================
    # 8. DOC LAI VA KIEM TRA JSON
    # ==================================================

    saved = json.loads(
        OUTPUT.read_text(encoding="utf-8")
    )

    if saved["youtube_id"] != VIDEO_ID:
        raise RuntimeError(
            "YouTube ID sau luu khong khop."
        )

    if len(saved["sentences"]) != EXPECTED_COUNT:
        raise RuntimeError(
            "So doan sau luu khong bang 146."
        )

    for i, (old, new) in enumerate(
        zip(original, saved["sentences"]), 1
    ):

        for key in ("start", "end"):
            if float(old[key]) != new[key]:
                raise RuntimeError(
                    f"Doan {i} bi thay doi {key}."
                )

        if old["hanzi"].strip() != new["hanzi"]:
            raise RuntimeError(
                f"Doan {i} bi thay doi hanzi."
            )

        if not new["pinyin"] or not new["vi"]:
            raise RuntimeError(
                f"Doan {i} thieu pinyin hoac vi."
            )

    # ==================================================
    # 9. HIEN THI KET QUA
    # ==================================================

    print("===== HSK3 VIDEO 5 - PINYIN VA DICH =====")
    print("YouTube:", VIDEO_ID)
    print("So doan:", len(sentences))
    print("Da dich:", len(translations))
    print("Doan ngan < 0.8s:", len(short_segments))
    print("Doan dai > 10s:", len(long_segments))

    print("\n===== 5 DOAN DAU =====")

    for i, item in enumerate(sentences[:5], 1):

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
