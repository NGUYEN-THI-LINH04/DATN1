
# -*- coding: utf-8 -*-
"""
BUOC 44 - CHUAN BI NGU PHAP HSK3
DU AN MOC HAN

- Tao danh sach ngu phap HSK3 ban dau.
- Co giai thich tieng Viet.
- Co cau vi du tieng Trung, Pinyin, ban dich.
- Chua gan MaBaiHoc.
- Khong ghi SQL.

Danh sach duoi day la bo noi dung bien soan
cho Moc Han, can kiem duyet truoc khi xuat ban.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OUT = (
    ROOT / "scripts" / "hsk3"
    / "data" / "processed"
    / "grammar_hsk3_draft.csv"
)

GRAMMAR_DATA = [
    (
        "把 + tân ngữ + động từ",
        "Câu chữ 把 nhấn mạnh đối tượng chịu tác động của hành động.",
        "Chủ ngữ + 把 + tân ngữ + động từ + thành phần kết quả hoặc vị trí.",
        "请把门关上。",
        "Qǐng bǎ mén guān shàng.",
        "Xin hãy đóng cửa lại.",
    ),
    (
        "被 + tác nhân + động từ",
        "Câu chữ 被 diễn đạt ý bị động, nhấn mạnh đối tượng chịu tác động.",
        "Đối tượng + 被 + tác nhân + động từ + thành phần bổ sung.",
        "我的手机被弟弟拿走了。",
        "Wǒ de shǒujī bèi dìdi ná zǒu le.",
        "Điện thoại của tôi bị em trai lấy đi rồi.",
    ),
    (
        "不但……而且……",
        "Liên kết hai ý, ý thứ hai bổ sung và nhấn mạnh ý thứ nhất.",
        "不但 + ý 1 + 而且 + ý 2.",
        "他不但会说汉语，而且会说英语。",
        "Tā búdàn huì shuō Hànyǔ, érqiě huì shuō Yīngyǔ.",
        "Anh ấy không những biết nói tiếng Trung mà còn biết nói tiếng Anh.",
    ),
    (
        "只有……才……",
        "Biểu thị điều kiện cần thiết để đạt được kết quả.",
        "只有 + điều kiện + 才 + kết quả.",
        "只有努力学习，才能取得好成绩。",
        "Zhǐyǒu nǔlì xuéxí, cái néng qǔdé hǎo chéngjì.",
        "Chỉ khi học tập chăm chỉ mới có thể đạt kết quả tốt.",
    ),
    (
        "只要……就……",
        "Biểu thị điều kiện đủ để dẫn đến một kết quả.",
        "只要 + điều kiện + 就 + kết quả.",
        "只要你愿意，我就帮你。",
        "Zhǐyào nǐ yuànyì, wǒ jiù bāng nǐ.",
        "Chỉ cần bạn đồng ý, tôi sẽ giúp bạn.",
    ),
    (
        "即使……也……",
        "Biểu thị sự nhượng bộ: dù điều kiện xảy ra, kết quả vẫn không thay đổi.",
        "即使 + tình huống giả định + 也 + kết quả.",
        "即使下雨，我们也要去。",
        "Jíshǐ xià yǔ, wǒmen yě yào qù.",
        "Dù trời mưa, chúng tôi vẫn sẽ đi.",
    ),
    (
        "既然……就……",
        "Dựa trên một sự việc đã rõ để đưa ra kết luận hoặc quyết định.",
        "既然 + sự việc đã biết + 就 + quyết định.",
        "既然你累了，就休息一下吧。",
        "Jìrán nǐ lèi le, jiù xiūxi yíxià ba.",
        "Nếu bạn đã mệt thì nghỉ một lát đi.",
    ),
    (
        "无论……都……",
        "Biểu thị kết quả không thay đổi dù điều kiện khác nhau.",
        "无论 + điều kiện nào + 都 + kết quả.",
        "无论遇到什么困难，我都不会放弃。",
        "Wúlùn yùdào shénme kùnnan, wǒ dōu bú huì fàngqì.",
        "Dù gặp khó khăn gì, tôi cũng sẽ không bỏ cuộc.",
    ),
    (
        "连……都 / 也……",
        "Nhấn mạnh một trường hợp bất ngờ hoặc cực đoan.",
        "连 + đối tượng được nhấn mạnh + 都/也 + vị ngữ.",
        "这个问题连老师都不知道。",
        "Zhège wèntí lián lǎoshī dōu bù zhīdào.",
        "Câu hỏi này ngay cả giáo viên cũng không biết.",
    ),
    (
        "宁可……也不……",
        "Thể hiện sự lựa chọn một phương án dù phải chấp nhận bất lợi.",
        "宁可 + lựa chọn 1 + 也不 + lựa chọn 2.",
        "我宁可走路，也不坐出租车。",
        "Wǒ nìngkě zǒulù, yě bù zuò chūzūchē.",
        "Tôi thà đi bộ còn hơn đi taxi.",
    ),
    (
        "把 + tân ngữ + 放在 + nơi chốn",
        "Câu chữ 把 dùng để diễn đạt việc di chuyển đối tượng tới một vị trí.",
        "Chủ ngữ + 把 + đồ vật + 放在 + vị trí.",
        "请把书放在桌子上。",
        "Qǐng bǎ shū fàng zài zhuōzi shàng.",
        "Xin hãy đặt sách lên bàn.",
    ),
    (
        "动词 + 起来",
        "Bổ ngữ 起来 có thể biểu thị sự bắt đầu của một hành động hoặc trạng thái.",
        "Động từ + 起来. Nghĩa cụ thể tùy động từ và ngữ cảnh.",
        "孩子们笑起来了。",
        "Háizimen xiào qǐlái le.",
        "Bọn trẻ bắt đầu cười.",
    ),
    (
        "动词 + 下去",
        "Bổ ngữ 下去 có thể biểu thị sự tiếp tục của hành động.",
        "Động từ + 下去.",
        "请继续说下去。",
        "Qǐng jìxù shuō xiàqù.",
        "Xin hãy tiếp tục nói.",
    ),
    (
        "看起来 + tính từ",
        "Diễn đạt nhận xét dựa trên những gì quan sát được.",
        "Chủ ngữ + 看起来 + tính từ hoặc cụm miêu tả.",
        "这个办法看起来不错。",
        "Zhège bànfǎ kàn qǐlái búcuò.",
        "Cách này có vẻ khá tốt.",
    ),
    (
        "来得及 / 来不及",
        "Diễn đạt việc còn kịp hoặc không còn kịp làm gì.",
        "来得及 + động từ; 来不及 + động từ.",
        "现在出发还来得及。",
        "Xiànzài chūfā hái láidejí.",
        "Xuất phát bây giờ vẫn còn kịp.",
    ),
    (
        "差点儿 + động từ",
        "Biểu thị một việc suýt xảy ra nhưng thực tế không xảy ra.",
        "Chủ ngữ + 差点儿 + động từ.",
        "我差点儿忘了今天的会议。",
        "Wǒ chàdiǎnr wàng le jīntiān de huìyì.",
        "Tôi suýt quên cuộc họp hôm nay.",
    ),
    (
        "大概 / 可能 + mệnh đề",
        "Biểu thị sự phỏng đoán hoặc khả năng xảy ra sự việc.",
        "Chủ ngữ + 大概/可能 + vị ngữ.",
        "他大概明天回来。",
        "Tā dàgài míngtiān huílái.",
        "Có lẽ ngày mai anh ấy về.",
    ),
    (
        "恐怕 + mệnh đề",
        "Biểu thị dự đoán mang sắc thái lo ngại hoặc kết quả không mong muốn.",
        "恐怕 + mệnh đề.",
        "恐怕今天不能完成这个任务。",
        "Kǒngpà jīntiān bù néng wánchéng zhège rènwu.",
        "E rằng hôm nay không thể hoàn thành nhiệm vụ này.",
    ),
    (
        "由于……因此……",
        "Nêu nguyên nhân và kết quả theo lối diễn đạt trang trọng.",
        "由于 + nguyên nhân + 因此 + kết quả.",
        "由于天气不好，因此比赛取消了。",
        "Yóuyú tiānqì bù hǎo, yīncǐ bǐsài qǔxiāo le.",
        "Do thời tiết xấu nên cuộc thi đã bị hủy.",
    ),
    (
        "随着……",
        "Diễn đạt sự thay đổi diễn ra cùng với một sự phát triển khác.",
        "随着 + sự thay đổi + mệnh đề kết quả.",
        "随着时间的变化，他越来越成熟。",
        "Suízhe shíjiān de biànhuà, tā yuèláiyuè chéngshú.",
        "Theo thời gian, anh ấy ngày càng trưởng thành.",
    ),
]

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
    print("=" * 65)
    print("BUOC 44 - CHUAN BI NGU PHAP HSK3")
    print("=" * 65)

    if OUT.exists():
        raise FileExistsError(
            f"File da ton tai: {OUT}\n"
            "Khong ghi de du lieu cu."
        )

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    records = []

    for index, data in enumerate(
        GRAMMAR_DATA,
        start=1,
    ):
        if len(data) != 6 or any(
            not str(value).strip()
            for value in data
        ):
            raise ValueError(
                f"Du lieu ngu phap so {index} khong day du."
            )

        title, description, usage, zh, py, vi = data

        records.append({
            "MaNguPhapTam": f"G3-{index:03d}",
            "MaBaiHoc": "",
            "TenCauTruc": title,
            "MoTa": description,
            "CachDung": usage,
            "ViDuTiengTrung": zh,
            "ViDuPinyin": py,
            "ViDuTiengViet": vi,
            "MaTep": "",
            "MaNguon": "",
            "ThuTuTam": index,
            "TrangThai": "ban_nhap",
        })

    with OUT.open(
        "x",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS,
        )
        writer.writeheader()
        writer.writerows(records)

    print("So cau truc ngu phap ban dau:", len(records))
    print("Da tao file:", OUT)
    print("Trang thai: ban_nhap")
    print("Chua gan MaBaiHoc")
    print("CHUA GHI SQL")


if __name__ == "__main__":
    main()
