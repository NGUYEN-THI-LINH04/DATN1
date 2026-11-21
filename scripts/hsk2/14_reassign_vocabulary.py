from pathlib import Path
import csv
import re


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "vocabulary_hsk2_by_lesson.csv"

OUTPUT_ASSIGNED = (
    DATA_DIR / "vocabulary_hsk2_reassigned.csv"
)

OUTPUT_REVIEW = (
    DATA_DIR / "vocabulary_hsk2_need_lesson_review.csv"
)


# ============================================================
# 23 BAI HOC HSK2
# ============================================================

LESSONS = {

    1: {
        "name": "Một ngày của tôi",

        "zh": [
            "每天", "每日", "早晨", "早上", "上午",
            "中午", "下午", "晚上", "夜里", "半夜",
            "起床", "睡觉", "洗澡", "休息",
            "平时", "经常", "常常", "时候",
            "生活", "日常", "时间"
        ],

        "vi": [
            "hằng ngày", "hàng ngày", "mỗi ngày",
            "buổi sáng", "buổi trưa", "buổi chiều",
            "buổi tối", "nửa đêm", "thường xuyên",
            "thường ngày", "sinh hoạt", "cuộc sống",
            "ngủ", "thức dậy", "tắm"
        ]
    },

    2: {
        "name": "Cuộc sống học tập",

        "zh": [
            "学习", "学校", "学生", "老师", "教师",
            "教室", "教学", "课堂", "课本", "上课",
            "下课", "作业", "考试", "考生",
            "成绩", "分数", "复习", "练习",
            "笔记", "词典", "字典", "教育",
            "开学", "留学生", "题", "句子"
        ],

        "vi": [
            "học", "học tập", "trường", "giáo viên",
            "học sinh", "sinh viên", "lớp học",
            "bài tập", "bài thi", "thi cử",
            "điểm số", "thành tích học tập",
            "ôn tập", "luyện tập", "từ điển",
            "giảng dạy", "giáo dục"
        ]
    },

    3: {
        "name": "Công việc",

        "zh": [
            "工作", "上班", "下班", "公司",
            "办公室", "单位", "经理", "老板",
            "工人", "工资", "收入", "服务",
            "职业", "司机", "打工", "请假",
            "休假", "业务"
        ],

        "vi": [
            "công việc", "làm việc", "đi làm",
            "công ty", "văn phòng", "nơi làm việc",
            "giám đốc", "quản lý", "công nhân",
            "lương", "thu nhập", "nghề nghiệp",
            "dịch vụ", "xin nghỉ"
        ]
    },

    4: {
        "name": "Gia đình và bạn bè",

        "zh": [
            "家庭", "家人", "父母", "爸爸", "妈妈",
            "哥哥", "姐姐", "弟弟", "妹妹",
            "丈夫", "妻子", "爱人", "孩子",
            "朋友", "老朋友", "交朋友",
            "结婚", "爱情"
        ],

        "vi": [
            "gia đình", "bố", "mẹ", "cha mẹ",
            "anh trai", "chị gái", "em trai",
            "em gái", "vợ", "chồng", "con cái",
            "bạn bè", "bạn cũ", "kết bạn",
            "kết hôn", "tình yêu"
        ]
    },

    5: {
        "name": "Ngoại hình và tính cách",

        "zh": [
            "漂亮", "可爱", "年轻", "老",
            "高", "矮", "胖", "瘦",
            "头发", "眼睛", "脸", "嘴",
            "热情", "安静", "聪明",
            "性格", "长得"
        ],

        "vi": [
            "xinh đẹp", "đẹp", "đáng yêu",
            "trẻ", "già", "cao", "thấp",
            "béo", "gầy", "tóc", "mắt",
            "khuôn mặt", "miệng",
            "tính cách", "thông minh",
            "nhiệt tình", "yên tĩnh"
        ]
    },

    6: {
        "name": "Thời tiết và các mùa",

        "zh": [
            "天气", "气温", "温度", "春天",
            "夏天", "秋天", "冬天",
            "春", "夏", "秋", "冬",
            "下雨", "下雪", "雪",
            "阴天", "晴天", "太阳",
            "冷", "热", "风"
        ],

        "vi": [
            "thời tiết", "nhiệt độ", "mùa xuân",
            "mùa hè", "mùa thu", "mùa đông",
            "mưa", "tuyết", "trời âm u",
            "nắng", "mặt trời", "lạnh", "nóng",
            "gió"
        ]
    },

    7: {
        "name": "Sức khỏe",

        "zh": [
            "身体", "健康", "医院", "医生",
            "药", "药店", "药片", "药水",
            "病", "疼", "难受", "舒服",
            "检查", "住院", "腿", "脚",
            "感冒", "休息"
        ],

        "vi": [
            "sức khỏe", "cơ thể", "bệnh viện",
            "bác sĩ", "thuốc", "bệnh",
            "đau", "khó chịu", "khỏe",
            "kiểm tra sức khỏe", "nhập viện",
            "chân", "bàn chân", "cảm cúm"
        ]
    },

    8: {
        "name": "Ăn uống",

        "zh": [
            "吃", "喝", "饭", "菜", "菜单",
            "食物", "食品", "早饭", "午饭",
            "晚饭", "早餐", "午餐", "晚餐",
            "快餐", "西餐", "中餐",
            "饺子", "筷子", "碗",
            "米", "面", "鸡", "鱼",
            "味道", "饿", "饱"
        ],

        "vi": [
            "ăn", "uống", "cơm", "món ăn",
            "thức ăn", "thực phẩm", "thực đơn",
            "bữa sáng", "bữa trưa", "bữa tối",
            "đồ ăn nhanh", "sủi cảo", "đũa",
            "bát", "gạo", "mì", "gà", "cá",
            "hương vị", "đói", "no"
        ]
    },

    9: {
        "name": "Mua sắm",

        "zh": [
            "买", "卖", "商店", "超市",
            "钱", "价格", "贵", "便宜",
            "衣服", "大衣", "颜色",
            "红", "黑", "白", "蓝",
            "绿", "黄", "大小"
        ],

        "vi": [
            "mua", "bán", "cửa hàng",
            "siêu thị", "tiền", "giá",
            "đắt", "rẻ", "quần áo",
            "áo khoác", "màu sắc",
            "màu đỏ", "màu đen", "màu trắng",
            "màu xanh", "kích cỡ"
        ]
    },

    10: {
        "name": "Vị trí và khoảng cách",

        "zh": [
            "位置", "地方", "附近",
            "旁边", "前面", "后面",
            "里面", "外面", "里头",
            "左边", "右边", "东", "西",
            "南", "北", "远", "近",
            "离", "中心", "入口"
        ],

        "vi": [
            "vị trí", "địa điểm", "gần đây",
            "bên cạnh", "phía trước", "phía sau",
            "bên trong", "bên ngoài",
            "bên trái", "bên phải",
            "phía đông", "phía tây",
            "phía nam", "phía bắc",
            "xa", "gần", "khoảng cách",
            "lối vào"
        ]
    },

    11: {
        "name": "Hỏi đường và giao thông",

        "zh": [
            "问路", "路", "公路",
            "交通", "汽车", "公共汽车",
            "公交车", "地铁", "地铁站",
            "车站", "停车", "停车场",
            "骑", "自行车", "往",
            "方向", "公里", "走"
        ],

        "vi": [
            "hỏi đường", "đường", "giao thông",
            "xe", "ô tô", "xe buýt",
            "tàu điện ngầm", "ga", "trạm",
            "đỗ xe", "xe đạp", "phương hướng",
            "kilômét"
        ]
    },

    12: {
        "name": "Du lịch",

        "zh": [
            "旅行", "旅游", "旅客", "游客",
            "护照", "飞机", "火车", "机场",
            "酒店", "宾馆", "出发",
            "到达", "回国", "起飞",
            "行李", "照片", "照相", "相机"
        ],

        "vi": [
            "du lịch", "du khách", "khách du lịch",
            "hộ chiếu", "máy bay", "tàu hỏa",
            "sân bay", "khách sạn",
            "khởi hành", "đến nơi",
            "về nước", "cất cánh",
            "hành lý", "ảnh", "chụp ảnh",
            "máy ảnh"
        ]
    },

    13: {
        "name": "Thể thao",

        "zh": [
            "运动", "体育", "篮球", "足球",
            "网球", "比赛", "跑步",
            "跑", "游泳", "锻炼",
            "体育场", "体育馆",
            "队", "队长"
        ],

        "vi": [
            "thể thao", "vận động",
            "bóng rổ", "bóng đá",
            "quần vợt", "thi đấu",
            "chạy", "chạy bộ", "bơi",
            "luyện tập", "đội", "đội trưởng"
        ]
    },

    14: {
        "name": "Sở thích và cuối tuần",

        "zh": [
            "周末", "兴趣", "喜欢",
            "音乐", "电影", "唱歌",
            "跳舞", "玩", "节目",
            "活动", "开心", "快乐",
            "有意思"
        ],

        "vi": [
            "cuối tuần", "sở thích",
            "thích", "âm nhạc", "phim",
            "hát", "nhảy", "chơi",
            "chương trình", "hoạt động",
            "vui", "thú vị"
        ]
    },

    15: {
        "name": "Ngày lễ và sự kiện",

        "zh": [
            "春节", "节日", "生日",
            "新年", "礼物", "晚会",
            "举行", "庆祝", "祝",
            "年", "月", "日"
        ],

        "vi": [
            "tết", "lễ hội", "ngày lễ",
            "sinh nhật", "năm mới",
            "quà", "buổi tiệc",
            "tổ chức", "chúc mừng"
        ]
    },

    16: {
        "name": "Hành động đã hoàn thành",

        "zh": [
            "已经", "完成", "完",
            "做完", "看完", "写完",
            "结果", "发现", "经过",
            "以前", "后来", "收到"
        ],

        "vi": [
            "đã", "hoàn thành", "làm xong",
            "kết quả", "phát hiện",
            "trải qua", "trước đây",
            "sau đó", "nhận được"
        ]
    },

    17: {
        "name": "Hành động đang diễn ra",

        "zh": [
            "正在", "正", "进行",
            "继续", "开始", "一边",
            "同时", "行动", "活动"
        ],

        "vi": [
            "đang", "đang diễn ra",
            "tiến hành", "tiếp tục",
            "bắt đầu", "đồng thời",
            "vừa", "hành động"
        ]
    },

    18: {
        "name": "So sánh",

        "zh": [
            "比较", "比", "更", "最",
            "一样", "相同", "不同",
            "不如", "好处", "坏处",
            "高", "低", "大小"
        ],

        "vi": [
            "so sánh", "hơn", "nhất",
            "giống nhau", "khác nhau",
            "không bằng", "ưu điểm",
            "nhược điểm", "cao", "thấp"
        ]
    },

    19: {
        "name": "Thay đổi và mức độ",

        "zh": [
            "变化", "改变", "变",
            "变成", "成为", "提高",
            "进步", "越来越",
            "更加", "特别", "普通",
            "一点点", "有点"
        ],

        "vi": [
            "thay đổi", "biến thành",
            "trở thành", "nâng cao",
            "tiến bộ", "ngày càng",
            "càng", "đặc biệt",
            "bình thường", "một chút"
        ]
    },

    20: {
        "name": "Nguyên nhân và điều kiện",

        "zh": [
            "因为", "所以", "如果",
            "虽然", "但是", "不过",
            "原因", "结果", "条件",
            "否则"
        ],

        "vi": [
            "bởi vì", "vì vậy",
            "nếu", "mặc dù", "nhưng",
            "nguyên nhân", "kết quả",
            "điều kiện"
        ]
    },

    21: {
        "name": "Liên lạc và giao tiếp",

        "zh": [
            "电话", "打电话", "联系",
            "短信", "消息", "新闻",
            "说", "说明", "告诉",
            "回答", "问", "问题",
            "听说", "讨论", "对话",
            "商量", "交给"
        ],

        "vi": [
            "điện thoại", "gọi điện",
            "liên lạc", "tin nhắn",
            "tin tức", "nói", "giải thích",
            "nói cho", "trả lời",
            "hỏi", "câu hỏi",
            "thảo luận", "đối thoại",
            "trao đổi"
        ]
    },

    22: {
        "name": "Văn hóa và quan điểm",

        "zh": [
            "中国", "文化", "历史",
            "语言", "汉语", "中文",
            "观点", "看法", "意见",
            "认为", "想法", "理想",
            "态度", "公平"
        ],

        "vi": [
            "trung quốc", "văn hóa",
            "lịch sử", "ngôn ngữ",
            "tiếng trung", "quan điểm",
            "ý kiến", "cho rằng",
            "cách nghĩ", "lý tưởng",
            "thái độ", "công bằng"
        ]
    },

    23: {
        "name": "Ôn tập và từ dùng chung",

        "zh": [],

        "vi": []
    },
}


# ============================================================
# MOT SO TU PHAN LOAI CHAC CHAN
# DUNG DE SUA CAC TRUONG HOP MA KEYWORD DE NHAM
# ============================================================

FORCED = {

    # Bai 1
    "半夜": 1,
    "经常": 1,
    "平时": 1,
    "生活": 1,
    "早晨": 1,
    "小时候": 1,
    "那时候": 1,
    "这时候": 1,

    # Bai 2
    "笔记": 2,
    "笔记本": 2,
    "成绩": 2,
    "分数": 2,
    "复习": 2,
    "教室": 2,
    "教育": 2,
    "课堂": 2,
    "练习": 2,
    "留学生": 2,
    "字典": 2,
    "词典": 2,
    "作业": 2,
    "教师": 2,
    "教学": 2,
    "开学": 2,

    # Bai 3
    "办公室": 3,
    "单位": 3,
    "服务": 3,
    "公司": 3,
    "经理": 3,
    "司机": 3,
    "收入": 3,
    "打工": 3,
    "休假": 3,

    # Bai 4
    "爱情": 4,
    "爱人": 4,
    "家庭": 4,
    "交朋友": 4,
    "老朋友": 4,

    # Bai 6
    "大自然": 6,

    # Bai 7
    "脚": 7,
    "住院": 7,

    # Bai 8
    "饱": 8,
    "鸡": 8,
    "米": 8,
    "鱼": 8,

    # Bai 12
    "相机": 12,
    "回国": 12,
    "起飞": 12,
    "照片": 12,
    "照相": 12,

    # Bai 13
    "队": 13,
    "队长": 13,
    "网球": 13,
    "爬山": 13,

    # Bai 19
    "变": 19,
    "变成": 19,
    "成为": 19,

    # Bai 20
    "因为": 20,
    "所以": 20,
    "如果": 20,
    "虽然": 20,
    "原因": 20,
    "条件": 20,

    # Bai 21
    "短信": 21,
    "新闻": 21,
    "讨论": 21,
    "听说": 21,
    "问题": 21,
    "问路": 11,

    # Bai 22
    "观点": 22,
    "看法": 22,
    "意见": 22,
    "认为": 22,
    "语言": 22,
}


def clean(value):
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value)
    ).strip()


def normalize(value):
    return clean(
        value
    ).lower()


def contains_keyword(
    hanzi,
    meaning,
    keyword
):
    keyword = normalize(
        keyword
    )

    return (
        keyword
        and (
            keyword in normalize(hanzi)
            or keyword in normalize(meaning)
        )
    )


def calculate_score(
    hanzi,
    meaning,
    lesson
):

    score = 0
    matches = []

    # Chu Han uu tien cao hon
    for keyword in lesson["zh"]:

        if keyword in hanzi:

            # Khop nguyen tu
            if hanzi == keyword:
                score += 20
            else:
                score += 8

            matches.append(
                f"ZH:{keyword}"
            )

    # Nghia Viet
    meaning_norm = normalize(
        meaning
    )

    for keyword in lesson["vi"]:

        key = normalize(
            keyword
        )

        if (
            key
            and key in meaning_norm
        ):
            score += 4

            matches.append(
                f"VI:{keyword}"
            )

    return score, matches


FIELDS = [
    "MaTuHSK",
    "MaMucNoiBo",
    "SoThuTuNguon",
    "MaTuVung",
    "ChuHan",
    "PhienAm",
    "NghiaTiengViet",
    "TuLoai",
    "DaDuyet",
    "MaBaiHocTam",
    "SoThuTuBai",
    "TenBaiHoc",
    "ThuTuTrongBai",
    "CachPhan",
    "DiemChuDe",
    "TuKhoaKhop",
]


def main():

    print("=" * 74)
    print("BUOC 14 - PHAN LAI TU VUNG HSK2 THEO NOI DUNG")
    print("KHONG EP SO TU MOI BAI")
    print("KHONG GHI SQL")
    print("=" * 74)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Khong tim thay:\n"
            f"{INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        rows = list(
            csv.DictReader(file)
        )

    if len(rows) != 772:
        raise ValueError(
            f"Du kien 772 tu, "
            f"nhung file co "
            f"{len(rows)}."
        )

    assigned = []
    review = []

    count_forced = 0
    count_topic = 0

    for row in rows:

        hanzi = clean(
            row["ChuHan"]
        )

        meaning = clean(
            row["NghiaTiengViet"]
        )

        # ========================================
        # 1. CAC TRUONG HOP DA QUY DINH RO
        # ========================================

        if hanzi in FORCED:

            lesson_id = FORCED[
                hanzi
            ]

            row[
                "SoThuTuBai"
            ] = lesson_id

            row[
                "MaBaiHocTam"
            ] = (
                f"L2-{lesson_id:02d}"
            )

            row[
                "TenBaiHoc"
            ] = LESSONS[
                lesson_id
            ]["name"]

            row[
                "CachPhan"
            ] = "xac_dinh"

            row[
                "DiemChuDe"
            ] = 100

            row[
                "TuKhoaKhop"
            ] = "FORCED"

            assigned.append(
                row
            )

            count_forced += 1

            continue

        # ========================================
        # 2. CHAM DIEM 22 CHU DE
        # ========================================

        scores = []

        for lesson_id in range(
            1,
            23
        ):

            score, matches = (
                calculate_score(
                    hanzi,
                    meaning,
                    LESSONS[
                        lesson_id
                    ]
                )
            )

            if score > 0:

                scores.append(
                    (
                        score,
                        lesson_id,
                        matches
                    )
                )

        scores.sort(
            key=lambda item: (
                -item[0],
                item[1]
            )
        )

        # ========================================
        # 3. CHI NHAN KHI DIEM DU TIN CAY
        # ========================================

        if scores:

            best_score = (
                scores[0][0]
            )

            best_lesson = (
                scores[0][1]
            )

            best_matches = (
                scores[0][2]
            )

            second_score = (
                scores[1][0]
                if len(scores) > 1
                else 0
            )

            # Chap nhan neu:
            # - diem >= 8
            # hoac
            # - diem >= 4 va khong bi hoa/gan hoa
            reliable = (
                best_score >= 8
                or (
                    best_score >= 4
                    and (
                        best_score
                        - second_score
                    ) >= 4
                )
            )

            if reliable:

                row[
                    "SoThuTuBai"
                ] = best_lesson

                row[
                    "MaBaiHocTam"
                ] = (
                    f"L2-{best_lesson:02d}"
                )

                row[
                    "TenBaiHoc"
                ] = LESSONS[
                    best_lesson
                ]["name"]

                row[
                    "CachPhan"
                ] = "chu_de"

                row[
                    "DiemChuDe"
                ] = best_score

                row[
                    "TuKhoaKhop"
                ] = ", ".join(
                    best_matches
                )

                assigned.append(
                    row
                )

                count_topic += 1

                continue

        # ========================================
        # 4. KHONG EP VAO BAI
        # ========================================

        row[
            "MaBaiHocTam"
        ] = ""

        row[
            "SoThuTuBai"
        ] = ""

        row[
            "TenBaiHoc"
        ] = ""

        row[
            "ThuTuTrongBai"
        ] = ""

        row[
            "CachPhan"
        ] = "can_xem"

        row[
            "DiemChuDe"
        ] = (
            scores[0][0]
            if scores
            else 0
        )

        row[
            "TuKhoaKhop"
        ] = (
            ", ".join(
                scores[0][2]
            )
            if scores
            else ""
        )

        review.append(
            row
        )

    # ============================================
    # SAP THU TU TRONG BAI
    # ============================================

    assigned.sort(
        key=lambda r: (
            int(
                r["SoThuTuBai"]
            ),
            int(
                r["SoThuTuNguon"]
            )
        )
    )

    counters = {
        i: 0
        for i in range(
            1,
            24
        )
    }

    for row in assigned:

        lesson_id = int(
            row["SoThuTuBai"]
        )

        counters[
            lesson_id
        ] += 1

        row[
            "ThuTuTrongBai"
        ] = counters[
            lesson_id
        ]

    # ============================================
    # GHI FILE
    # ============================================

    with OUTPUT_ASSIGNED.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writeheader()
        writer.writerows(
            assigned
        )

    with OUTPUT_REVIEW.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writeheader()
        writer.writerows(
            review
        )

    # ============================================
    # THONG KE
    # ============================================

    print()
    print(
        f"Tong tu HSK2: "
        f"{len(rows)}"
    )

    print(
        f"Gan chac chan: "
        f"{count_forced}"
    )

    print(
        f"Gan theo chu de: "
        f"{count_topic}"
    )

    print(
        f"Can xem lai: "
        f"{len(review)}"
    )

    print()
    print("SO TU TAM THOI THEO BAI:")

    for lesson_id in range(
        1,
        23
    ):

        print(
            f"  Bai "
            f"{lesson_id:02d}: "
            f"{counters[lesson_id]} tu"
        )

    print()
    print(
        "Bai 23 chua tu dong dua tu vao."
    )

    print(
        "Cac tu khong xac dinh duoc "
        "duoc dua vao file review, "
        "KHONG nhat vao bai 23."
    )

    print()
    print("File da gan bai:")
    print(OUTPUT_ASSIGNED)

    print()
    print("File can xem lai:")
    print(OUTPUT_REVIEW)

    print()
    print(
        "Tong kiem tra: "
        f"{len(assigned)} + "
        f"{len(review)} = "
        f"{len(assigned) + len(review)}"
    )

    print()
    print(
        "KHONG INSERT/UPDATE/DELETE SQL."
    )


if __name__ == "__main__":
    main()