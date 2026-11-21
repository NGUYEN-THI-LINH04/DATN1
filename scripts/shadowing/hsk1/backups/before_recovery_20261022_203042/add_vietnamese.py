
import json
from pathlib import Path

# ============================================================
# 1. DUONG DAN VA CAU HINH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PREVIEW_DIR = BASE_DIR / "previews"

INPUT_FILE = (
    PREVIEW_DIR / "jian_dan_sheng_huo_normalized.json"
)

OUTPUT_FILE = (
    PREVIEW_DIR / "jian_dan_sheng_huo_final_preview.json"
)

VIDEO_ID = "6YGJswSorYw"
EXPECTED_COUNT = 57


# ============================================================
# 2. BAN DICH TIENG VIET - 57 CAU
# ============================================================

TRANSLATIONS = [

    # ---------------- CAU 1 - 10 ----------------

    "Chào các bạn! Hôm nay mình muốn kể cho các bạn nghe về một ngày trong cuộc sống của mình.",

    "Mình là một nhân viên văn phòng làm việc tại Việt Nam, năm nay 30 tuổi.",

    "Cuộc sống của mình rất bình thường như bao người, nhưng mỗi ngày đều có những chuyện vui và buồn.",

    "Sáng sớm lúc sáu giờ, chuông báo thức vang lên và mình thức dậy.",

    "Bên ngoài trời nắng rất đẹp, thời tiết không quá lạnh cũng không quá nóng.",

    "Mình ăn một bữa sáng đơn giản với bánh mì và sữa.",

    "Ăn xong, mình thay quần áo rồi lái xe máy đi làm.",

    "Trên đường có rất nhiều xe và người qua lại, giao thông khá đông đúc.",

    "Khi lái xe phải cẩn thận, chú ý đèn giao thông và người đi đường.",

    "Mình thích nhìn mọi người trên phố, ai cũng làm việc rất chăm chỉ.",


    # ---------------- CAU 11 - 20 ----------------

    "Khi đến công ty, nhiều đồng nghiệp đã bắt đầu làm việc.",

    "Trong văn phòng có máy tính và hồ sơ, giấy tờ.",

    "Hôm nay mình có một cuộc họp quan trọng, phải trình bày kế hoạch công việc với mọi người.",

    "Mình hơi lo lắng, nhưng các đồng nghiệp động viên, giúp mình cảm thấy tự tin hơn.",

    "Sau khi nghe báo cáo, sếp nói: 'Em làm rất tốt!'",

    "Nghe vậy, mình rất vui.",

    "Trong công việc cũng có những vấn đề phát sinh.",

    "Buổi chiều, máy tính bị hỏng khiến mình không mở được tài liệu.",

    "Mình rất sốt ruột nên đã tìm nhân viên kỹ thuật nhờ giúp đỡ.",

    "Cuối cùng mình đã sửa được máy tính và hoàn thành công việc.",


    # ---------------- CAU 21 - 30 ----------------

    "Dù mệt nhưng mình rất vui vì đã tự giải quyết được vấn đề.",

    "Buổi trưa, mình cùng đồng nghiệp đi ăn.",

    "Chúng mình đã ăn phở bò Việt Nam và nem rán.",

    "Mọi người trò chuyện, mình kể rằng mình và bạn gái mới bắt đầu hẹn hò.",

    "Cô ấy rất dịu dàng, chúng mình thích cùng nhau uống cà phê và trò chuyện.",

    "Các đồng nghiệp mỉm cười nói: 'Chúc hai bạn hạnh phúc!'",

    "Mình cũng cười theo.",

    "Buổi chiều gần tan làm, bạn gái nhắn tin: 'Hôm nay em muốn gặp anh.'",

    "Mình rất muốn gặp cô ấy, nhưng công việc vẫn chưa xong.",

    "Mình đành nhắn lại: 'Đợi anh tan làm nhé, anh sẽ đến gặp em.'",


    # ---------------- CAU 31 - 40 ----------------

    "Cô ấy gửi lại một biểu tượng mặt cười, khiến lòng mình cảm thấy rất ấm áp.",

    "Sau khi tan làm, mình lái xe đến gặp cô ấy.",

    "Cô ấy đang đợi mình ở dưới nhà.",

    "Chúng mình cùng nhau đi ăn tối, có rất nhiều món ăn Việt Nam ngon.",

    "Cô ấy hỏi: 'Hôm nay anh có mệt không?'",

    "Mình trả lời: 'Hơi mệt một chút, nhưng gặp được em thì anh thấy vui.'",

    "Cô ấy mỉm cười nói: 'Chúng ta cùng nhau cố gắng nhé?'",

    "Mình gật đầu.",

    "Buổi tối về nhà, mình chuẩn bị công việc cho ngày mai.",

    "Dù mệt nhưng mình vẫn rất vui.",


    # ---------------- CAU 41 - 50 ----------------

    "Cuộc sống có những niềm vui nhưng cũng có những khó khăn.",

    "Có người mình yêu thương và bạn bè ủng hộ, mình cảm thấy rất hạnh phúc.",

    "Mình hy vọng sau này có thể cùng bạn gái xây dựng cuộc sống tốt đẹp hơn.",

    "Mình cũng hy vọng công việc ngày càng thuận lợi.",

    "Đôi khi mình nhớ lại cuộc sống thời thơ ấu.",

    "Khi ấy gia đình mình không được khá giả.",

    "Bố mẹ ngày nào cũng làm việc chăm chỉ để cho mình được học hành tốt.",

    "Mình rất biết ơn bố mẹ.",

    "Vì vậy, hiện tại mình cũng cố gắng làm việc chăm chỉ, không muốn khiến bố mẹ thất vọng.",

    "Mặc dù công việc có áp lực, nhưng mình biết tất cả đều vì một tương lai tốt đẹp hơn.",


    # ---------------- CAU 51 - 57 ----------------

    "Vào cuối tuần, mình thích cùng bạn gái đi dạo trong công viên hoặc xem phim.",

    "Chúng mình cũng cùng nhau nấu ăn.",

    "Mặc dù mình nấu ăn không giỏi lắm, nhưng cô ấy luôn động viên mình.",

    "Những điều nhỏ bé ấy khiến mình cảm thấy cuộc sống thật tươi đẹp.",

    "Chúng cũng tiếp thêm sức mạnh để mình đối mặt với những thử thách mỗi ngày.",

    "Cảm ơn mọi người đã lắng nghe câu chuyện của mình.",

    "Hy vọng các bạn ngày nào cũng vui vẻ và cuộc sống ngày càng tốt đẹp hơn.",
]


# ============================================================
# 3. CAC CAU HANZI CAN DOI CHIEU
# ============================================================

EXPECTED_HANZI = {
    1: "大家好，今天我想和大家说说我一天的生活。",

    20: "最后我修好了电脑，完成了工作。",

    23: "我们吃了越南的牛肉粉和春卷。",

    33: "在楼下等我。",

    57: "希望你们每天都开心，生活越来越好。",
}


# ============================================================
# 4. SUA LOI DA XAC NHAN TU VIDEO
# ============================================================

def apply_verified_fixes(sentences):

    # CAU 33
    # Video hien thi:
    # 她在楼下等我。
    #
    # Transcript Supadata cu:
    # 在楼下等我。
    #
    # Bo sung chu 她 va pinyin tuong ung.

    sentence_33 = sentences[32]

    old_hanzi = sentence_33["hanzi"]

    if old_hanzi == "在楼下等我。":

        sentence_33["hanzi"] = "她在楼下等我。"

        sentence_33["pinyin"] = (
            "tā zài lóu xià děng wǒ 。"
        )

        print("[FIX] Cau 33: Da bo sung chu 她")

    elif old_hanzi == "她在楼下等我。":

        sentence_33["pinyin"] = (
            "tā zài lóu xià děng wǒ 。"
        )

        print("[OK] Cau 33: Da dung")

    else:

        raise ValueError(
            f"Cau 33 co Hanzi bat thuong: {old_hanzi}"
        )


# ============================================================
# 5. KIEM TRA DU LIEU
# ============================================================

def validate_data(data):

    if data.get("module") != "shadowing":
        raise ValueError("Module khong phai shadowing")

    if data.get("youtube_id") != VIDEO_ID:
        raise ValueError("YouTube ID khong khop")

    sentences = data.get("sentences", [])

    if len(sentences) != EXPECTED_COUNT:
        raise ValueError(
            f"Can {EXPECTED_COUNT} cau, "
            f"nhung file co {len(sentences)} cau"
        )

    if len(TRANSLATIONS) != EXPECTED_COUNT:
        raise ValueError(
            "Danh sach ban dich khong du 57 cau"
        )

    # Kiem tra cac cau moc.
    for number, expected in EXPECTED_HANZI.items():

        actual = sentences[number - 1].get("hanzi")

        # Cau 33 chap nhan ca ban da sua.
        if number == 33 and actual == "她在楼下等我。":
            continue

        if actual != expected:
            raise ValueError(
                f"Cau {number} khong khop:\n"
                f"Thuc te: {actual}\n"
                f"Du kien: {expected}"
            )

    # Kiem tra tung cau.
    for index, sentence in enumerate(sentences):

        number = index + 1

        required_fields = [
            "start",
            "end",
            "hanzi",
            "pinyin",
        ]

        for field in required_fields:

            if field not in sentence:
                raise ValueError(
                    f"Cau {number} thieu {field}"
                )

        start = sentence["start"]
        end = sentence["end"]

        if not isinstance(start, (int, float)):
            raise ValueError(
                f"Cau {number}: start khong hop le"
            )

        if not isinstance(end, (int, float)):
            raise ValueError(
                f"Cau {number}: end khong hop le"
            )

        if start < 0 or end <= start:
            raise ValueError(
                f"Cau {number}: timestamp sai"
            )

        if index > 0:

            previous_end = sentences[index - 1]["end"]

            if start < previous_end - 0.02:
                raise ValueError(
                    f"Cau {number}: timestamp chong lap"
                )

        if not sentence["hanzi"].strip():
            raise ValueError(
                f"Cau {number}: thieu Hanzi"
            )

        if not sentence["pinyin"].strip():
            raise ValueError(
                f"Cau {number}: thieu Pinyin"
            )


# ============================================================
# 6. MAIN
# ============================================================

def main():

    print("===== CAP NHAT SHADOWING HSK1 =====")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay file:\n{INPUT_FILE}"
        )

    # DOC JSON CHUAN HOA
    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig"
    ) as f:

        data = json.load(f)

    # KIEM TRA DU LIEU GOC
    validate_data(data)

    sentences = data["sentences"]

    # SUA LOI DA XAC NHAN
    apply_verified_fixes(sentences)

    # GAN BAN DICH TIENG VIET
    for index, sentence in enumerate(sentences):

        translation = TRANSLATIONS[index].strip()

        if not translation:
            raise ValueError(
                f"Cau {index + 1} chua co ban dich"
            )

        sentence["vi"] = translation

    # KIEM TRA LAN CUOI
    if len(sentences) != 57:
        raise ValueError("So cau khong hop le")

    if not all(
        sentence["vi"].strip()
        for sentence in sentences
    ):
        raise ValueError("Con cau chua duoc dich")

    # LUU FILE JSON MOI
    # KHONG SUA FILE NORMALIZED GOC
    PREVIEW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    # DOC LAI DE XAC MINH
    with OUTPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as f:

        saved = json.load(f)

    if len(saved["sentences"]) != 57:
        raise ValueError(
            "Loi xac minh file sau khi luu"
        )

    # THONG BAO KET QUA
    print("\n===== HOAN THANH =====")
    print("Video:", saved["youtube_id"])
    print("Tong so cau:", len(saved["sentences"]))
    print("So cau da dich:", len(TRANSLATIONS))
    print("File:", OUTPUT_FILE)

    # HIEN THI 3 CAU DAU
    print("\n===== 3 CAU DAU =====")

    for index, item in enumerate(
        saved["sentences"][:3],
        start=1
    ):

        print(f"\nCau {index}")

        print(
            "Time:",
            item["start"],
            "-",
            item["end"]
        )

        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Tieng Viet:", item["vi"])

    # KIEM TRA 2 CAU DA SUA
    print("\n===== CAC CAU DA CAP NHAT =====")

    for number in [23, 33]:

        item = saved["sentences"][number - 1]

        print(f"\nCau {number}")
        print("Hanzi:", item["hanzi"])
        print("Pinyin:", item["pinyin"])
        print("Tieng Viet:", item["vi"])

    print("\n===== TRANG THAI =====")
    print("Da tao file JSON hoan chinh.")
    print("Chua thay doi SQL Server.")
    print("Khong goi Supadata.")
    print("Can kiem tra dong bo voi video.")
    print("Cau 20 van can doi chieu Hanzi voi am thanh.")


if __name__ == "__main__":
    main()
