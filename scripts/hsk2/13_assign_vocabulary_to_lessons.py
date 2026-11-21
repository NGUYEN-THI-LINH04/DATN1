from pathlib import Path
import csv
import re
import pyodbc


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = DATA_DIR / "vocabulary_hsk2_by_lesson.csv"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=HocTiengTrungDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


# ============================================================
# 23 CHU DE BAI HOC
# ============================================================

LESSONS = {

    1: {
        "name": "Một ngày của tôi",
        "keywords": [
            "每天", "早晨", "上午", "中午", "下午", "晚上",
            "半夜", "起床", "睡觉", "洗澡", "休息", "生活",
            "时候", "时间", "平时", "经常", "常常"
        ]
    },

    2: {
        "name": "Cuộc sống học tập",
        "keywords": [
            "学习", "学校", "学生", "老师", "教室", "课堂",
            "课", "课本", "作业", "考试", "成绩", "复习",
            "词典", "字典", "笔记", "练习", "教育"
        ]
    },

    3: {
        "name": "Công việc",
        "keywords": [
            "工作", "公司", "办公室", "经理", "工人",
            "服务", "司机", "职业", "上班", "下班",
            "单位", "工资", "办"
        ]
    },

    4: {
        "name": "Gia đình và bạn bè",
        "keywords": [
            "家庭", "家人", "爸爸", "妈妈", "父母",
            "哥哥", "姐姐", "弟弟", "妹妹",
            "朋友", "爱情", "结婚", "关系"
        ]
    },

    5: {
        "name": "Ngoại hình và tính cách",
        "keywords": [
            "漂亮", "可爱", "年轻", "高", "矮", "胖", "瘦",
            "头发", "眼睛", "脸", "嘴", "性格",
            "热情", "安静", "聪明"
        ]
    },

    6: {
        "name": "Thời tiết và các mùa",
        "keywords": [
            "天气", "气温", "温度", "春", "夏", "秋", "冬",
            "下雨", "下雪", "雪", "阴天", "晴",
            "太阳", "冷", "热"
        ]
    },

    7: {
        "name": "Sức khỏe",
        "keywords": [
            "健康", "身体", "医院", "医生", "药",
            "疼", "病", "难受", "舒服", "休息",
            "检查", "腿", "眼睛"
        ]
    },

    8: {
        "name": "Ăn uống",
        "keywords": [
            "吃", "喝", "饭", "菜", "餐", "食品", "食物",
            "饺子", "筷子", "碗", "味道", "菜单",
            "早饭", "午饭", "晚饭", "快餐", "西餐", "中餐"
        ]
    },

    9: {
        "name": "Mua sắm",
        "keywords": [
            "买", "卖", "商店", "超市", "钱", "价格",
            "贵", "便宜", "衣服", "颜色", "红色",
            "白色", "黑色", "蓝色", "绿色", "黄色"
        ]
    },

    10: {
        "name": "Vị trí và khoảng cách",
        "keywords": [
            "地方", "位置", "附近", "旁边", "前面", "后面",
            "里面", "外面", "左", "右", "远", "近",
            "离", "中心"
        ]
    },

    11: {
        "name": "Hỏi đường và giao thông",
        "keywords": [
            "路", "公路", "车", "汽车", "公交车",
            "公共汽车", "地铁", "车站", "停车",
            "走", "往", "方向", "交通"
        ]
    },

    12: {
        "name": "Du lịch",
        "keywords": [
            "旅行", "旅游", "旅客", "游客",
            "护照", "飞机", "火车", "酒店",
            "宾馆", "出发", "到达"
        ]
    },

    13: {
        "name": "Thể thao",
        "keywords": [
            "运动", "体育", "篮球", "足球",
            "跑", "跑步", "比赛", "锻炼",
            "体育场", "体育馆"
        ]
    },

    14: {
        "name": "Sở thích và cuối tuần",
        "keywords": [
            "周末", "音乐", "电影", "唱歌",
            "跳舞", "玩", "兴趣", "喜欢",
            "节目", "活动", "快乐"
        ]
    },

    15: {
        "name": "Ngày lễ và sự kiện",
        "keywords": [
            "春节", "节日", "生日", "新年",
            "礼物", "祝", "年", "月", "日",
            "庆祝"
        ]
    },

    16: {
        "name": "Hành động đã hoàn thành",
        "keywords": [
            "已经", "完成", "完", "结果",
            "发现", "经历", "经过", "以前",
            "后来"
        ]
    },

    17: {
        "name": "Hành động đang diễn ra",
        "keywords": [
            "正在", "活动", "继续", "开始",
            "进行", "同时", "一边"
        ]
    },

    18: {
        "name": "So sánh",
        "keywords": [
            "比", "比较", "更", "最",
            "一样", "相同", "不同",
            "好处", "坏处"
        ]
    },

    19: {
        "name": "Thay đổi và mức độ",
        "keywords": [
            "越来越", "变化", "改变", "提高",
            "进步", "特别", "普通",
            "程度", "更加"
        ]
    },

    20: {
        "name": "Nguyên nhân và điều kiện",
        "keywords": [
            "因为", "所以", "如果", "虽然",
            "但是", "原因", "结果",
            "条件"
        ]
    },

    21: {
        "name": "Liên lạc và giao tiếp",
        "keywords": [
            "电话", "打电话", "联系", "告诉",
            "回答", "问", "说", "讨论",
            "消息", "新闻"
        ]
    },

    22: {
        "name": "Văn hóa và quan điểm",
        "keywords": [
            "中国", "文化", "历史", "语言",
            "汉语", "中文", "意见", "看法",
            "观点", "感兴趣", "认为"
        ]
    },

    23: {
        "name": "Ôn tập tổng hợp",
        "keywords": []
    }
}


# 772 / 23
# 13 bai x 34 + 10 bai x 33 = 772
CAPACITY = {
    lesson: 34 if lesson <= 13 else 33
    for lesson in range(1, 24)
}


def clean(value):
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value)
    ).strip()


def normalize_pinyin(value):
    return clean(value).lower()


def get_connection():
    return pyodbc.connect(
        CONNECTION_STRING,
        timeout=15,
        autocommit=False
    )


# ============================================================
# DOC 772 TU HSK2 + MAP SANG MaTuVung
# ============================================================

def load_vocabulary(cursor):

    mapping_file = (
        DATA_DIR
        / "vocabulary_hsk2_import_result.csv"
    )

    if not mapping_file.exists():
        raise FileNotFoundError(
            "Khong tim thay file mapping HSK2:\n"
            f"{mapping_file}"
        )

    # ========================================================
    # 1. DOC MAPPING DA TAO O BUOC IMPORT TU VUNG
    # ========================================================

    with mapping_file.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        mapping_rows = list(reader)

    if not mapping_rows:
        raise ValueError(
            "File mapping HSK2 dang rong."
        )

    headers = set(
        mapping_rows[0].keys()
    )

    print()
    print(
        "Cot trong file mapping:"
    )
    print(
        ", ".join(
            mapping_rows[0].keys()
        )
    )

    # ========================================================
    # 2. TIM TEN COT MaTuHSK VA MaTuVung
    # ========================================================

    possible_hsk_columns = [
        "MaTuHSK",
        "ma_tu_hsk",
        "MaTuHsk",
    ]

    possible_vocab_columns = [
        "MaTuVung",
        "ma_tu_vung",
        "MaTuVungSauImport",
        "MaTuVungKetQua",
    ]

    hsk_column = next(
        (
            col
            for col in possible_hsk_columns
            if col in headers
        ),
        None
    )

    vocab_column = next(
        (
            col
            for col in possible_vocab_columns
            if col in headers
        ),
        None
    )

    if hsk_column is None:
        raise ValueError(
            "Khong tim thay cot MaTuHSK "
            "trong file mapping."
        )

    if vocab_column is None:
        raise ValueError(
            "Khong tim thay cot MaTuVung "
            "trong file mapping.\n"
            "Cac cot hien co:\n"
            + ", ".join(
                mapping_rows[0].keys()
            )
        )

    # ========================================================
    # 3. TAO MAP MaTuHSK -> MaTuVung
    # ========================================================

    hsk_to_vocab = {}

    for row in mapping_rows:

        ma_hsk_text = clean(
            row.get(
                hsk_column
            )
        )

        ma_vocab_text = clean(
            row.get(
                vocab_column
            )
        )

        if (
            not ma_hsk_text
            or not ma_vocab_text
        ):
            continue

        ma_hsk = int(
            ma_hsk_text
        )

        ma_vocab = int(
            ma_vocab_text
        )

        if ma_hsk in hsk_to_vocab:
            raise ValueError(
                "MaTuHSK bi lap trong "
                "file mapping: "
                f"{ma_hsk}"
            )

        hsk_to_vocab[
            ma_hsk
        ] = ma_vocab

    # ========================================================
    # 4. DOC 772 DONG HSK2
    # ========================================================

    cursor.execute("""
        SELECT
            MaTuHSK,
            MaMucNoiBo,
            SoThuTuNguon,
            ChuHan,
            PhienAm,
            NghiaTiengVietThamChieu,
            TuLoai
        FROM dbo.TuVungHSKChuan
        WHERE MaCapDo = 2
        ORDER BY
            SoThuTuNguon,
            MaTuHSK;
    """)

    hsk_rows = cursor.fetchall()

    if len(hsk_rows) != 772:
        raise ValueError(
            "Du kien 772 dong HSK2, "
            f"nhung SQL co {len(hsk_rows)}."
        )

    # ========================================================
    # 5. DOC TuVung THEO MaTuVung
    # ========================================================

    cursor.execute("""
        SELECT
            MaTuVung,
            ChuHan,
            PhienAm,
            NghiaTiengViet,
            TuLoai,
            DaDuyet
        FROM dbo.TuVung;
    """)

    vocabulary_by_id = {}

    for row in cursor.fetchall():

        vocabulary_by_id[
            int(row.MaTuVung)
        ] = row

    # ========================================================
    # 6. NOI THEO MaTuHSK -> MaTuVung
    # KHONG CON DOI CHIEU ChuHan + PhienAm
    # ========================================================

    result = []

    missing_mapping = []
    missing_vocabulary = []

    for hsk in hsk_rows:

        ma_hsk = int(
            hsk.MaTuHSK
        )

        ma_vocab = (
            hsk_to_vocab.get(
                ma_hsk
            )
        )

        if ma_vocab is None:

            missing_mapping.append(
                ma_hsk
            )

            continue

        tv = vocabulary_by_id.get(
            ma_vocab
        )

        if tv is None:

            missing_vocabulary.append(
                (
                    ma_hsk,
                    ma_vocab
                )
            )

            continue

        result.append({

            "MaTuHSK":
                ma_hsk,

            "MaMucNoiBo":
                clean(
                    hsk.MaMucNoiBo
                ),

            "SoThuTuNguon":
                hsk.SoThuTuNguon,

            "MaTuVung":
                ma_vocab,

            "ChuHan":
                clean(
                    tv.ChuHan
                ),

            "PhienAm":
                clean(
                    tv.PhienAm
                ),

            "NghiaTiengViet":
                clean(
                    tv.NghiaTiengViet
                ),

            "TuLoai":
                clean(
                    hsk.TuLoai
                ),

            "DaDuyet":
                int(
                    tv.DaDuyet
                ),
        })

    # ========================================================
    # 7. KIEM TRA
    # ========================================================

    if missing_mapping:

        raise ValueError(
            "Cac MaTuHSK khong co trong "
            "file mapping:\n"
            + ", ".join(
                map(
                    str,
                    missing_mapping
                )
            )
        )

    if missing_vocabulary:

        raise ValueError(
            "Mapping tro toi MaTuVung "
            "khong ton tai:\n"
            + "\n".join(
                f"MaTuHSK={a}, "
                f"MaTuVung={b}"
                for a, b
                in missing_vocabulary
            )
        )

    if len(result) != 772:
        raise ValueError(
            "Sau khi noi mapping chi co "
            f"{len(result)}/772 dong."
        )

    print()
    print(
        f"Mapping HSK2 hop le: "
        f"{len(result)}/772"
    )

    return result


# ============================================================
# CHAM DIEM CHU DE
# ============================================================

def lesson_score(word, lesson_id):

    data = (
        word["ChuHan"]
        + " "
        + word["NghiaTiengViet"]
    ).lower()

    score = 0
    matched = []

    for keyword in (
        LESSONS[
            lesson_id
        ]["keywords"]
    ):

        keyword_lower = (
            keyword.lower()
        )

        if keyword_lower in data:

            # Khop truc tiep ChuHan uu tien hon
            if keyword in word["ChuHan"]:
                score += 5
            else:
                score += 2

            matched.append(
                keyword
            )

    return score, matched


def choose_lesson(
    word,
    lesson_counts
):

    candidates = []

    for lesson_id in range(
        1,
        23
    ):

        score, matched = (
            lesson_score(
                word,
                lesson_id
            )
        )

        if score > 0:
            candidates.append(
                (
                    score,
                    -lesson_counts[
                        lesson_id
                    ],
                    lesson_id,
                    matched
                )
            )

    candidates.sort(
        reverse=True
    )

    # --------------------------------------------
    # Co chu de ro rang
    # --------------------------------------------

    for (
        score,
        _,
        lesson_id,
        matched
    ) in candidates:

        if (
            lesson_counts[
                lesson_id
            ]
            < CAPACITY[
                lesson_id
            ]
        ):

            return (
                lesson_id,
                score,
                ", ".join(matched),
                "chu_de"
            )

    # --------------------------------------------
    # Khong co keyword ro rang
    # -> phan vao bai con cho trong it nhat
    # theo ty le lap day
    # --------------------------------------------

    available = [
        lesson_id
        for lesson_id in range(
            1,
            24
        )
        if lesson_counts[
            lesson_id
        ] < CAPACITY[
            lesson_id
        ]
    ]

    if not available:
        raise RuntimeError(
            "Khong con suc chua bai hoc."
        )

    selected = min(
        available,
        key=lambda lesson_id: (
            lesson_counts[
                lesson_id
            ]
            / CAPACITY[
                lesson_id
            ],
            lesson_id
        )
    )

    return (
        selected,
        0,
        "",
        "can_bang"
    )


# ============================================================
# MAIN
# ============================================================

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

    print("=" * 72)
    print("BUOC 13 - PHAN TU VUNG HSK2 VAO 23 BAI")
    print("KHONG GHI SQL")
    print("=" * 72)

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"File da ton tai:\n"
            f"{OUTPUT_FILE}\n"
            "Khong tu dong ghi de."
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        words = load_vocabulary(
            cursor
        )

        if len(words) != 772:
            raise ValueError(
                f"Du kien 772 tu HSK2, "
                f"nhung lay duoc "
                f"{len(words)}."
            )

        lesson_counts = {
            i: 0
            for i in range(
                1,
                24
            )
        }

        output_rows = []

        # --------------------------------------------
        # Uu tien cac tu co diem chu de cao truoc
        # --------------------------------------------

        scored_words = []

        for word in words:

            best_score = 0

            for lesson_id in range(
                1,
                23
            ):

                score, _ = (
                    lesson_score(
                        word,
                        lesson_id
                    )
                )

                best_score = max(
                    best_score,
                    score
                )

            scored_words.append(
                (
                    -best_score,
                    word[
                        "SoThuTuNguon"
                    ],
                    word
                )
            )

        scored_words.sort(
            key=lambda item: (
                item[0],
                item[1]
            )
        )

        assignments = []

        for _, _, word in scored_words:

            (
                lesson_id,
                score,
                matched,
                method
            ) = choose_lesson(
                word,
                lesson_counts
            )

            lesson_counts[
                lesson_id
            ] += 1

            assignments.append(
                (
                    word,
                    lesson_id,
                    score,
                    matched,
                    method
                )
            )

        # --------------------------------------------
        # Sap lai theo bai + thu tu nguon
        # --------------------------------------------

        assignments.sort(
            key=lambda item: (
                item[1],
                item[0][
                    "SoThuTuNguon"
                ]
            )
        )

        order_in_lesson = {
            i: 0
            for i in range(
                1,
                24
            )
        }

        theme_count = 0
        balance_count = 0

        for (
            word,
            lesson_id,
            score,
            matched,
            method
        ) in assignments:

            order_in_lesson[
                lesson_id
            ] += 1

            if method == "chu_de":
                theme_count += 1
            else:
                balance_count += 1

            output_rows.append({

                "MaTuHSK":
                    word["MaTuHSK"],

                "MaMucNoiBo":
                    word[
                        "MaMucNoiBo"
                    ],

                "SoThuTuNguon":
                    word[
                        "SoThuTuNguon"
                    ],

                "MaTuVung":
                    word[
                        "MaTuVung"
                    ],

                "ChuHan":
                    word[
                        "ChuHan"
                    ],

                "PhienAm":
                    word[
                        "PhienAm"
                    ],

                "NghiaTiengViet":
                    word[
                        "NghiaTiengViet"
                    ],

                "TuLoai":
                    word[
                        "TuLoai"
                    ],

                "DaDuyet":
                    word[
                        "DaDuyet"
                    ],

                "MaBaiHocTam":
                    f"L2-{lesson_id:02d}",

                "SoThuTuBai":
                    lesson_id,

                "TenBaiHoc":
                    LESSONS[
                        lesson_id
                    ]["name"],

                "ThuTuTrongBai":
                    order_in_lesson[
                        lesson_id
                    ],

                "CachPhan":
                    method,

                "DiemChuDe":
                    score,

                "TuKhoaKhop":
                    matched,
            })

        # --------------------------------------------
        # KIEM TRA
        # --------------------------------------------

        if len(output_rows) != 772:
            raise ValueError(
                "Tong so tu sau phan bai "
                "khong bang 772."
            )

        for lesson_id in range(
            1,
            24
        ):

            if (
                lesson_counts[
                    lesson_id
                ]
                != CAPACITY[
                    lesson_id
                ]
            ):
                raise ValueError(
                    f"Bai {lesson_id} "
                    f"co "
                    f"{lesson_counts[lesson_id]} "
                    f"tu, du kien "
                    f"{CAPACITY[lesson_id]}."
                )

        with OUTPUT_FILE.open(
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
                output_rows
            )

        connection.rollback()

        print()
        print(
            f"Tong tu HSK2: "
            f"{len(output_rows)}"
        )

        print(
            f"Phan theo chu de: "
            f"{theme_count}"
        )

        print(
            f"Phan de can bang: "
            f"{balance_count}"
        )

        print()
        print(
            "SO TU THEO BAI:"
        )

        for lesson_id in range(
            1,
            24
        ):

            print(
                f"  Bai "
                f"{lesson_id:02d}: "
                f"{lesson_counts[lesson_id]} tu"
            )

        print()
        print("Da tao:")
        print(OUTPUT_FILE)

        print()
        print(
            "DAY LA BAN PHAN BAI NHAP."
        )

        print(
            "CHUA GHI TuVungBaiHoc."
        )

        print(
            "CHUA INSERT/UPDATE/DELETE SQL."
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()