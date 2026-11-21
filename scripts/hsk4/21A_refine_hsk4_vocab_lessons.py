
# -*- coding: utf-8 -*-

"""
BUOC 21A - PHAN LAI 1000 TU HSK4 THEO CHU DE

INPUT:
  vocabulary_hsk4_by_lesson_draft_21.csv

OUTPUT:
  vocabulary_hsk4_by_lesson_draft_21A.csv
  vocabulary_hsk4_by_lesson_review_21A.csv
  hsk4_lessons_vocab_summary_21A.json

Nguyen tac:
- Doc dung snapshot 1000 tu Step21.
- Uu tien chu de theo Hanzi va nghia tieng Viet.
- Khong ep cac tu co chu de ro sang bai khac.
- Can doi chi nhung tu khong du tin cay.
- Khong sua file goc.
- Khong ghi SQL.
- Khong tao audio.
"""

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(r"D:\DATN1\scripts\hsk4\data\processed")

SOURCE = BASE / "vocabulary_hsk4_by_lesson_draft_21.csv"
OUTPUT = BASE / "vocabulary_hsk4_by_lesson_draft_21A.csv"
REVIEW = BASE / "vocabulary_hsk4_by_lesson_review_21A.csv"
SUMMARY = BASE / "hsk4_lessons_vocab_summary_21A.json"

EXPECTED_HASH = (
    "5988aeacd5846846ab000aa5edcae3dbea92a58cdd52140870384a003dda5436"
)

# Khoang muc tieu cho ban nhap, KHONG phai rang buoc bat buoc.
MIN_TARGET = 35
MAX_TARGET = 65

# Tu khoa Hanzi theo 20 chu de.
# Chi tinh diem khi cum Hanzi xuat hien trong tu.
HANZI = {
    1: "朋友 同事 同学 邻居 亲戚 交往 关系 友谊 伙伴 人际 联系 相处",
    2: "阿姨 宝宝 父母 母亲 父亲 家庭 婚姻 结婚 丈夫 妻子 亲人 婴儿 儿童",
    3: "学习 学校 学生 老师 教师 教育 考试 成绩 毕业 本科 博士 教授 课堂 知识 教材 复习",
    4: "工作 职业 公司 员工 经理 工资 招聘 面试 加班 办公 职位 事业 就业 失业",
    5: "商业 经济 银行 投资 利润 资金 财产 财务 贸易 企业 市场 合同 收入 经营",
    6: "交流 表达 讨论 解释 意见 观点 建议 说明 回答 询问 说服 争论 讲话",
    7: "心情 感情 情绪 紧张 担心 失望 害怕 愤怒 伤心 性格 勇敢 骄傲 耐心 表扬 称赞",
    8: "健康 身体 医院 医生 医疗 病人 生病 治疗 药物 打针 疼痛 护士 生命 症状",
    9: "冰箱 家具 房间 房屋 房子 洗衣 打扫 修理 钥匙 住宿 住宅 电梯 电灯 家务",
    10: "百货 茶叶 食品 食物 蔬菜 水果 饮料 饭店 餐厅 商店 超市 购物 衣服 味道 菜单",
    11: "巴士 大巴 交通 飞机 机场 火车 汽车 地铁 车站 司机 旅行 旅游 航班 行李 乘客 长途",
    12: "城市 地区 地址 地点 方向 距离 附近 位置 街道 农村 地面 地下 出口 入口",
    13: "时间 计划 安排 按时 提前 推迟 继续 变化 改变 过程 未来 过去 最近 日期 期限",
    14: "天气 气候 环境 自然 空气 冰雪 打雷 潮湿 森林 河流 海洋 地球 温度 风景",
    15: "科学 技术 电脑 计算机 手机 网络 互联网 网站 软件 设备 机器 电子 登录 电源 操作",
    16: "文化 传统 艺术 电影 音乐 电视 新闻 报纸 杂志 节目 演员 记者 小说 故事 作品",
    17: "运动 体育 比赛 足球 篮球 游泳 跑步 训练 冠军 运动员 操场 娱乐 游戏",
    18: "社会 法律 政府 警察 安全 危险 事故 犯罪 国家 公民 制度 规则 责任 爱国",
    19: "数量 数字 百分比 比例 增加 减少 重量 长度 高度 尺寸 程度 质量 倍数",
    20: "虽然 但是 而且 不过 因此 所以 既然 否则 即使 尽管 由于 关于 根据 按照 除了 甚至",
}

# Tu khoa tieng Viet duoc doi chieu theo ranh gioi tu.
# Dung cum tu de han che match sai nhu "con" trong "cong".
VIET = {
    1: "bạn bè|đồng nghiệp|hàng xóm|mối quan hệ|giao tiếp xã hội|người quen",
    2: "gia đình|bố mẹ|cha mẹ|mẹ kế|bảo mẫu|em bé|trẻ sơ sinh|hôn nhân|vợ chồng|họ hàng",
    3: "học tập|giáo dục|trường học|đại học|thi cử|tốt nghiệp|bài tập|giảng dạy|học sinh|sinh viên",
    4: "nghề nghiệp|công việc|tuyển dụng|phỏng vấn xin việc|nhân viên|tiền lương|tăng ca|thất nghiệp",
    5: "tài sản|ngân hàng|kinh doanh|đầu tư|tài chính|lợi nhuận|thu nhập|thị trường|hợp đồng|thương mại",
    6: "ý kiến|quan điểm|giải thích|thảo luận|diễn đạt|đề nghị|phát biểu|thuyết phục|tranh luận",
    7: "cảm xúc|tâm trạng|tính cách|lo lắng|buồn bã|thất vọng|tức giận|khen ngợi|thành thật",
    8: "bệnh viện|bác sĩ|y tá|tiêm|chữa bệnh|điều trị|thuốc men|sức khỏe|đau đớn|triệu chứng",
    9: "tủ lạnh|thang máy|đèn điện|đồ gia dụng|dọn dẹp|sửa chữa|chìa khóa|căn phòng|nhà ở",
    10: "hàng hóa|trà|thức ăn|đồ uống|món ăn|rau quả|siêu thị|cửa hàng|mua sắm|thực phẩm",
    11: "xe buýt|máy bay|sân bay|tàu hỏa|tàu điện|giao thông|du lịch|hành lý|chuyến bay|đường dài",
    12: "địa chỉ|địa điểm|thành phố|vị trí|phương hướng|khoảng cách|lối ra|lối vào|mặt đất",
    13: "thời gian|kế hoạch|lịch trình|đúng giờ|thời hạn|trì hoãn|thay đổi|trước đây|tương lai",
    14: "thời tiết|thiên nhiên|môi trường|khí hậu|ẩm ướt|sấm|tuyết|động vật|thực vật|ô nhiễm",
    15: "công nghệ|máy tính|internet|đăng nhập|phần mềm|nguồn điện|thiết bị|máy móc|vận hành",
    16: "văn hóa|truyền thống|nghệ thuật|âm nhạc|điện ảnh|truyền hình|báo chí|tác phẩm|tiểu thuyết",
    17: "thể thao|thi đấu|bóng đá|bóng rổ|bơi lội|chạy bộ|sân thể thao|trò chơi|giải trí",
    18: "pháp luật|chính phủ|cảnh sát|tai nạn|an toàn|tội phạm|yêu nước|quốc gia|xã hội",
    19: "số lượng|kích thước|chiều dài|chiều cao|trọng lượng|tỷ lệ|phần trăm|gấp đôi|đơn vị đo",
    20: "liên từ|phó từ|giới từ|trợ từ|mặc dù|tuy nhiên|do đó|thậm chí|căn cứ vào",
}

# Truong hop de nham do nghia tu dien co nhieu nghia.
# Gan diem cao cho chu de co ngữ canh Hanzi ro.
EXACT_OVERRIDES = {
    "冰箱": 9,
    "财产": 5,
    "打针": 8,
    "打雷": 14,
    "登录": 15,
    "百货": 10,
    "茶叶": 10,
    "长途": 11,
    "爱国": 18,
    "宝宝": 2,
    "传统": 16,
    "操场": 17,
    "电梯": 9,
    "电源": 15,
    "地址": 12,
    "包裹": 11,
}

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def norm(text):
    text = str(text or "").lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )

def keyword_found(text, keyword):
    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(norm(keyword))
        + r"(?![a-z0-9])"
    )
    return bool(re.search(pattern, norm(text)))

def load_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)

def score_row(row, lesson_no):
    hanzi = row["ChuHan"].strip()
    meaning = row["NghiaTiengViet"].split("/ LT:")[0]

    # Hanzi exact: diem cao nhat.
    if hanzi in EXACT_OVERRIDES:
        if EXACT_OVERRIDES[hanzi] == lesson_no:
            return 100, "EXACT_OVERRIDE"

    score = 0
    evidence = []

    for keyword in HANZI[lesson_no].split():
        if keyword == hanzi:
            score += 14
            evidence.append("HANZI_EXACT:" + keyword)
        elif len(keyword) >= 2 and keyword in hanzi:
            score += 9
            evidence.append("HANZI_PART:" + keyword)

    for keyword in VIET[lesson_no].split("|"):
        if keyword_found(meaning, keyword):
            score += 5
            evidence.append("NGHIA:" + keyword)

    # Chi dung tu loai khi khong co bang chung noi dung.
    if score == 0:
        pos = row["TuLoai"]
        if lesson_no == 19 and ("量" in pos or "数" in pos):
            score = 2
            evidence.append("TU_LOAI_SO_LUONG")
        elif lesson_no == 20 and any(
            c in pos for c in ("副", "连", "介", "助")
        ):
            score = 2
            evidence.append("TU_LOAI_CHUC_NANG")

    return score, " | ".join(evidence)

def write_csv(path, fields, rows):
    if path.exists():
        raise FileExistsError(
            f"File da ton tai, khong ghi de: {path}"
        )
    with path.open("x", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=fields, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)

def main():
    print("=" * 78)
    print("BUOC 21A - CAI THIEN PHAN 1000 TU HSK4")
    print("KHONG GHI SQL - KHONG TAO AUDIO")
    print("=" * 78)

    print("\n[1] KIEM TRA SNAPSHOT")
    actual_hash = sha(SOURCE)
    print("SHA256:", actual_hash)

    if actual_hash != EXPECTED_HASH:
        raise RuntimeError("FAIL: file Step21 khong dung snapshot")

    fields, rows = load_csv(SOURCE)

    if len(rows) != 1000:
        raise RuntimeError("FAIL: khong du 1000 tu")

    ids = [r["MaMucNoiBo"] for r in rows]
    if len(set(ids)) != 1000:
        raise RuntimeError("FAIL: trung MaMucNoiBo")

    print("PASS: 1000 tu, 1000 ID duy nhat")

    # ========================================================
    # 2. TINH DIEM CHU DE CHO TOAN BO 1000 TU
    # ========================================================

    print("\n[2] TINH DIEM CHU DE")

    records = []

    for row in rows:
        scores = {}
        evidence = {}

        for lesson_no in range(1, 21):
            score, reason = score_row(row, lesson_no)
            scores[lesson_no] = score
            evidence[lesson_no] = reason

        ranking = sorted(
            scores,
            key=lambda n: (-scores[n], n)
        )

        best = ranking[0]
        best_score = scores[best]
        second_score = scores[ranking[1]]

        tied = [
            n for n in ranking
            if scores[n] == best_score
        ]

        # Chon bai cu khi bang diem, neu no nam trong nhom.
        old_lesson = int(row["SoThuTuBai"])

        if old_lesson in tied:
            best = old_lesson

        if best_score >= 9 and len(tied) == 1:
            confidence = "CAO"
        elif best_score >= 5 and len(tied) == 1:
            confidence = "TRUNG_BINH"
        else:
            confidence = "THAP"

        records.append({
            "row": dict(row),
            "scores": scores,
            "evidence": evidence,
            "lesson": best,
            "confidence": confidence,
            "best_score": best_score,
            "second_score": second_score,
            "reason": "CHU_DE" if best_score > 0 else "KHONG_CO_TIN_HIEU",
        })

    # ========================================================
    # 3. CAN DOI CHI CAC TU CO DO TIN CAY THAP
    # ========================================================

    print("\n[3] CAN DOI TU CHUA CHAC CHAN")

    counts = Counter(r["lesson"] for r in records)
    moved = 0

    # Di chuyen tu bai qua dong sang bai thieu tu.
    # KHONG di chuyen cac tu confidence CAO/TRUNG_BINH.
    for _ in range(1000):
        under = [
            n for n in range(1, 21)
            if counts[n] < MIN_TARGET
        ]
        over = [
            n for n in range(1, 21)
            if counts[n] > MAX_TARGET
        ]

        if not under or not over:
            break

        target = min(under, key=lambda n: (counts[n], n))

        candidates = []

        for record in records:
            old = record["lesson"]

            if old not in over:
                continue

            if record["confidence"] != "THAP":
                continue

            # Uu tien bai dich co diem chu de tot hon.
            target_score = record["scores"][target]
            loss = record["scores"][old] - target_score

            candidates.append(
                (loss, -target_score, old, record)
            )

        if not candidates:
            break

        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        chosen = candidates[0][3]
        old = chosen["lesson"]

        chosen["lesson"] = target
        chosen["reason"] = "CAN_DOI_CAN_REVIEW"

        counts[old] -= 1
        counts[target] += 1
        moved += 1

    print("So tu can doi:", moved)

    # ========================================================
    # 4. CAP NHAT MA BAI TAM VA THU TU
    # ========================================================

    print("\n[4] TAO KET QUA")

    title_by_lesson = {}

    for row in rows:
        n = int(row["SoThuTuBai"])
        title_by_lesson[n] = row["TieuDeBaiHoc"]

    grouped = defaultdict(list)

    for record in records:
        grouped[record["lesson"]].append(record)

    result = []
    review = []

    for lesson_no in range(1, 21):
        group = grouped[lesson_no]

        group.sort(
            key=lambda item: (
                int(item["row"]["SoThuTuNguon"] or 999999),
                item["row"]["MaMucNoiBo"],
            )
        )

        for index, record in enumerate(group, start=1):
            row = record["row"]
            old_lesson = int(row["SoThuTuBai"])

            row["SoThuTuBaiCu"] = old_lesson
            row["SoThuTuBai"] = lesson_no
            row["MaBaiHocTam"] = f"H4-L{lesson_no:02d}"
            row["TieuDeBaiHoc"] = title_by_lesson[lesson_no]
            row["ThuTuTrongBai"] = index

            row["DiemChuDe21A"] = record["scores"][lesson_no]
            row["DoTinCay21A"] = record["confidence"]
            row["LyDo21A"] = record["reason"]
            row["BangChung21A"] = record["evidence"][lesson_no]

            # Chua duoc review chuyen gia, khong danh dau
            # tat ca cac truong hop la da duyet.
            row["CanReview21A"] = (
                "CO" if (
                    record["confidence"] != "CAO"
                    or record["reason"] == "CAN_DOI_CAN_REVIEW"
                ) else "KHONG"
            )

            result.append(row)

            if row["CanReview21A"] == "CO":
                review.append(row)

    # ========================================================
    # 5. KIEM TRA BAT BUOC
    # ========================================================

    print("\n[5] VALIDATE")

    if len(result) != 1000:
        raise RuntimeError("FAIL: khong du 1000 tu")

    if len(set(r["MaMucNoiBo"] for r in result)) != 1000:
        raise RuntimeError("FAIL: trung ID")

    if set(r["MaMucNoiBo"] for r in result) != set(ids):
        raise RuntimeError("FAIL: mat hoac them tu")

    if set(int(r["SoThuTuBai"]) for r in result) != set(range(1, 21)):
        raise RuntimeError("FAIL: chua du 20 bai")

    print("PASS: 1000/1000 tu, khong trung, khong mat")
    print("PASS: 20/20 bai co tu vung")

    counts = Counter(int(r["SoThuTuBai"]) for r in result)

    for n in range(1, 21):
        review_count = sum(
            int(r["SoThuTuBai"]) == n
            for r in review
        )
        print(
            f"Bai {n:02d}: {counts[n]:3d} tu | "
            f"review={review_count:3d}"
        )

    print("Tong can review:", len(review))

    # ========================================================
    # 6. XUAT FILE
    # ========================================================

    print("\n[6] XUAT CSV VA SUMMARY")

    extra_fields = [
        "SoThuTuBaiCu",
        "DiemChuDe21A",
        "DoTinCay21A",
        "LyDo21A",
        "BangChung21A",
        "CanReview21A",
    ]

    output_fields = fields + [
        c for c in extra_fields if c not in fields
    ]

    # Kiem tra tat ca file truoc khi ghi.
    outputs = [OUTPUT, REVIEW, SUMMARY]

    existing = [str(p) for p in outputs if p.exists()]

    if existing:
        raise FileExistsError(
            "FAIL: output da ton tai, khong ghi de:\n"
            + "\n".join(existing)
        )

    write_csv(OUTPUT, output_fields, result)
    write_csv(REVIEW, output_fields, review)

    summary = {
        "buoc": "21A",
        "source_sha256": EXPECTED_HASH,
        "tong_tu": len(result),
        "so_bai": 20,
        "tu_can_review": len(review),
        "tu_da_can_doi": moved,
        "phan_bo": {
            str(n): counts[n] for n in range(1, 21)
        },
        "vocabulary_output": str(OUTPUT),
        "vocabulary_sha256": sha(OUTPUT),
        "review_output": str(REVIEW),
        "review_sha256": sha(REVIEW),
        "ghi_sql": False,
        "tao_audio": False,
        "trang_thai": "BAN_NHAP_CAN_REVIEW",
    }

    with SUMMARY.open("x", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 78)
    print("PASS: BUOC 21A HOAN THANH")
    print("=" * 78)
    print("Tong tu:", len(result))
    print("So bai:", 20)
    print("Tu can review:", len(review))
    print("FILE:", OUTPUT)
    print("SHA256:", sha(OUTPUT))
    print("REVIEW:", REVIEW)
    print("SUMMARY:", SUMMARY)
    print("KHONG GHI SQL - KHONG TAO AUDIO")
    print("=" * 78)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nFAIL:", exc)
        raise SystemExit(1)
