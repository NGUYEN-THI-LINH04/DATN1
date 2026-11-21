
"""
MỘC HÁN - TRA CỨU KIẾN THỨC CHATBOT

File: routes/chatbot_knowledge.py

Chức năng:
01. Nhận diện loại câu hỏi
02. Tách từ / cụm chữ Hán
03. Tra từ vựng đã duyệt
04. Tra ngữ pháp đã xuất bản
05. Tra chữ Hán và bộ thủ
06. Tra ví dụ đã xuất bản
07. Chuẩn bị ngữ cảnh SQL cho Qwen3

Dùng chung cho Admin và Student.

Không tạo bảng SQL mới.
Không tự tạo pinyin hoặc nghĩa tiếng Việt.
"""

import re
from contextlib import closing

from database import get_connection


# ==========================================================
# 01. NHẬN DIỆN LOẠI CÂU HỎI
#
# Các loại:
# - tu_vung
# - ngu_phap
# - chu_han
# - hoi_dap
#
# Không coi mọi câu tiếng Trung đều là câu tra từ.
# ==========================================================

GRAMMAR_WORDS = (
    "ngữ pháp",
    "cấu trúc",
    "mẫu câu",
    "cách dùng",
    "语法",
    "句型",
)

HANZI_WORDS = (
    "chữ hán",
    "hán tự",
    "bộ thủ",
    "số nét",
    "cách viết chữ",
    "cách viết",
    "ký tự",
    "chữ này",
    "chữ ",
    "汉字",
    "偏旁",
    "部首",
)

VOCAB_WORDS = (
    "từ vựng",
    "giải thích từ",
    "nghĩa của từ",
    "từ này",
    "pinyin",
    "phiên âm",
    "cách đọc",
    "phát âm",
    "nghĩa là gì",
    "tiếng trung của",
    "dịch từ",
    "dịch sang tiếng trung",
    "词语",
    "什么意思",
)

CHINESE_RE = re.compile(
    r"[\u3400-\u9fff]+"
)


def detect_intent(question):
    """
    Nhận diện sơ bộ ý định câu hỏi.

    Chế độ hội thoại nhập vai được xử lý
    tại routes/student/chatbot.py.
    """

    text = str(question or "").strip().lower()

    if any(
        marker in text
        for marker in GRAMMAR_WORDS
        if marker != "cách dùng"
    ):
        return "ngu_phap"

    if "cách dùng" in text:
        if "từ " in text or "từ vựng" in text:
            return "tu_vung"

        return "ngu_phap"

    if any(
        marker in text
        for marker in HANZI_WORDS
    ):
        return "chu_han"

    if any(
        marker in text
        for marker in VOCAB_WORDS
    ):
        return "tu_vung"

    if "ví dụ" in text or "例句" in text:
        return "tu_vung"

    if CHINESE_RE.search(text):
        if "giải thích" in text:
            return "tu_vung"

        if "+" in text:
            return "ngu_phap"

    # Một từ Hán đứng riêng có thể là
    # yêu cầu tra từ vựng.
    #
    # Câu có dấu hỏi hoặc dấu câu khác
    # không được tự động coi là tra từ.
    if re.fullmatch(
        r"[\u3400-\u9fff]{1,10}",
        text,
    ):
        return "tu_vung"

    return "hoi_dap"


# ==========================================================
# 02. TRÍCH XUẤT CỤM CHỮ HÁN
#
# Ví dụ:
# "Giải thích từ 学习"
#
# Kết quả có:
# - 学习
# - 学
# - 习
#
# Khi trả kết quả sẽ ưu tiên từ dài hơn.
# ==========================================================

def extract_hanzi_terms(question, max_terms=45):

    unique = set()
    result = []

    groups = CHINESE_RE.findall(
        str(question or "")
    )

    for group in groups:

        candidates = []

        if len(group) <= 12:
            candidates.append(group)

        for size in range(
            min(len(group), 8),
            1,
            -1,
        ):

            for start in range(
                len(group) - size + 1
            ):

                candidates.append(
                    group[start:start + size]
                )

        if len(group) <= 12:
            candidates.extend(group)

        for term in candidates:

            if term in unique:
                continue

            unique.add(term)
            result.append(term)

            if len(result) >= max_terms:
                return result

    return result


# ==========================================================
# 03. XÁC ĐỊNH CHỮ HÁN CẦN TRA
#
# Ví dụ:
# "Giải thích chữ 学 trong 学习"
#
# Ưu tiên chữ 学 thay vì tra cả 学 và 习.
# ==========================================================

def _hanzi_focus(question):

    match = re.search(
        (
            r"(?:chữ hán|chữ|ký tự|hán tự|汉字)"
            r"\s*[:：]?\s*([\u3400-\u9fff])"
        ),
        question,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return None


# ==========================================================
# 04. TÁCH CHỦ ĐỀ NGỮ PHÁP TIẾNG VIỆT
#
# Ví dụ:
# "Giải thích ngữ pháp so sánh hơn"
#
# Có thể tìm trong:
# - TenCauTruc
# - MoTa
# - CachDung
# ==========================================================

def _vietnamese_grammar_topics(question):

    text = str(question or "").lower()

    for prefix in (
        "ngữ pháp",
        "cấu trúc",
        "mẫu câu",
        "cách dùng",
    ):

        if prefix in text:
            text = text.split(prefix, 1)[1]
            break

    text = re.sub(
        r"[^\w\sÀ-ỹ]",
        " ",
        text,
    )

    text = re.sub(
        (
            r"\b(?:là|gì|về|cho|mình|tôi|bạn|hãy|"
            r"giải|thích|ví|dụ|trong|tiếng|trung|"
            r"nhé|như|thế|nào|được|không|có|của)\b"
        ),
        " ",
        text,
    )

    words = [
        word
        for word in text.split()
        if len(word) >= 2
    ]

    phrases = []

    if len(words) >= 2:

        phrases.append(
            " ".join(words[:3])
        )

        phrases.append(
            " ".join(words[:2])
        )

    phrases.extend(
        word
        for word in words[:3]
        if len(word) >= 4
    )

    return [
        phrase
        for phrase in dict.fromkeys(phrases)
        if len(phrase) >= 4
    ][:4]


# ==========================================================
# 05. TÁCH NGHĨA TIẾNG VIỆT CẦN TRA
#
# Ví dụ:
# "Tiếng Trung của 'học tập' là gì?"
#
# Chỉ dùng khi người học chỉ rõ cụm cần tra.
# ==========================================================

def _vietnamese_vocabulary_topics(question):

    question = str(question or "").strip()

    matches = re.findall(
        r'[“"‘\']([^”"’\']{2,60})[”"’\']',
        question,
    )

    if matches:

        return [
            term.strip()
            for term in matches
            if not CHINESE_RE.search(term)
        ][:2]

    match = re.search(
        (
            r"(?:tiếng trung của(?: từ)?|dịch từ)"
            r"\s*[:：]?\s*([^?.!,，。]{2,50})"
        ),
        question,
        flags=re.IGNORECASE,
    )

    if match:

        value = match.group(1)

        value = re.sub(
            r"\s+(?:là gì|như thế nào)\s*$",
            "",
            value,
            flags=re.IGNORECASE,
        )

        if not CHINESE_RE.search(value):
            return [value.strip()]

    return []


# ==========================================================
# 06. HÀM TRUY VẤN SQL DÙNG CHUNG
#
# Giá trị người dùng được truyền bằng tham số.
# Không nối trực tiếp từ khóa người dùng
# vào câu lệnh SQL.
# ==========================================================

def _rows(cursor, sql, params=()):

    cursor.execute(sql, *params)

    columns = [
        column[0]
        for column in cursor.description
    ]

    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def _placeholders(values):

    return ",".join(
        "?"
        for _ in values
    )


# ==========================================================
# 07. SẮP XẾP TỪ VỰNG
#
# Ví dụ:
# 学习 được ưu tiên hơn 学.
#
# Khi đã tìm được từ nhiều chữ,
# không lấy thêm các từ đơn một chữ
# không cần thiết.
# ==========================================================

def _rank_vocabulary(
    rows,
    question,
    limit=3,
):

    if not rows:
        return []

    max_length = max(
        len(str(row.get("ChuHan") or ""))
        for row in rows
    )

    if max_length > 1:

        rows = [
            row
            for row in rows
            if len(
                str(row.get("ChuHan") or "")
            ) > 1
        ]

    rows = sorted(
        rows,
        key=lambda row: (
            -len(str(row.get("ChuHan") or "")),

            question.find(
                str(row.get("ChuHan") or "")
            ),

            row.get("MaTuVung") or 0,
        ),
    )

    return rows[:limit]


# ==========================================================
# 08. TRA TỪ VỰNG ĐÃ DUYỆT
#
# Bảng:
# dbo.TuVung
#
# Điều kiện:
# DaDuyet = 1
#
# Lấy:
# - Chữ Hán
# - Chữ phồn thể
# - Pinyin
# - Nghĩa
# - Từ loại
# - Ví dụ chính
# ==========================================================

def _search_vocabulary(
    cursor,
    question,
    terms,
    intent,
):

    params = list(terms)

    if params:

        sql = f"""
            SELECT
                MaTuVung,
                ChuHan,
                ChuPhonThe,
                PhienAm,
                NghiaTiengViet,
                TuLoai,
                ViDuTiengTrung,
                ViDuTiengViet

            FROM dbo.TuVung

            WHERE
                DaDuyet = 1
                AND ChuHan IN (
                    {_placeholders(params)}
                )
        """

        rows = _rows(
            cursor,
            sql,
            params,
        )

        if rows:
            return _rank_vocabulary(
                rows,
                question,
            )

    # Tra bằng nghĩa tiếng Việt.
    if intent != "tu_vung" or terms:
        return []

    topics = _vietnamese_vocabulary_topics(
        question
    )

    if not topics:
        return []

    conditions = " OR ".join(
        "CHARINDEX(?, NghiaTiengViet) > 0"
        for _ in topics
    )

    sql = f"""
        SELECT TOP (30)
            MaTuVung,
            ChuHan,
            ChuPhonThe,
            PhienAm,
            NghiaTiengViet,
            TuLoai,
            ViDuTiengTrung,
            ViDuTiengViet

        FROM dbo.TuVung

        WHERE
            DaDuyet = 1
            AND ({conditions})

        ORDER BY
            LEN(NghiaTiengViet),
            MaTuVung
    """

    rows = _rows(
        cursor,
        sql,
        topics,
    )

    return rows[:3]


# ==========================================================
# 09. TRA NGỮ PHÁP ĐÃ XUẤT BẢN
#
# Bảng:
# - dbo.NguPhap
# - dbo.BaiHoc
# - dbo.KhoaHoc
#
# Điều kiện:
# NguPhap.TrangThai = da_xuat_ban
#
# Tìm trong:
# - TenCauTruc
# - MoTa
# - CachDung
#
# Có hỗ trợ ngữ pháp một chữ:
# 把, 被, 了...
# ==========================================================

def _search_grammar(
    cursor,
    question,
    terms,
):

    hanzi_terms = [
        term
        for term in terms
        if len(term) >= 2
    ][:12]

    if not hanzi_terms:

        hanzi_terms = [
            term
            for term in terms
            if len(term) == 1
        ][:4]

    else:

        hanzi_terms += [
            term
            for term in terms
            if len(term) == 1
        ][:3]

    topics = (
        _vietnamese_grammar_topics(question)
        if not terms
        else []
    )

    keys = list(
        dict.fromkeys(
            hanzi_terms + topics
        )
    )[:16]

    if not keys:
        return []

    conditions = []
    params = []

    for keyword in keys:

        conditions.append(
            """
            (
                CHARINDEX(?, g.TenCauTruc) > 0
                OR CHARINDEX(?, g.MoTa) > 0
                OR CHARINDEX(?, g.CachDung) > 0
            )
            """
        )

        params.extend([
            keyword,
            keyword,
            keyword,
        ])

    sql = f"""
        SELECT TOP (100)
            g.MaNguPhap,
            g.MaBaiHoc,
            g.TenCauTruc,
            g.MoTa,
            g.CachDung,
            g.ViDuTiengTrung,
            g.ViDuPinyin,
            g.ViDuTiengViet,
            kh.MaCapDo AS CapDoHSK

        FROM dbo.NguPhap AS g

        LEFT JOIN dbo.BaiHoc AS b
            ON b.MaBaiHoc = g.MaBaiHoc
            AND b.TrangThai = 'da_xuat_ban'

        LEFT JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc = b.MaKhoaHoc
            AND kh.TrangThai = 'da_xuat_ban'

        WHERE
            g.TrangThai = 'da_xuat_ban'
            AND (
                {' OR '.join(conditions)}
            )

        ORDER BY g.MaNguPhap
    """

    rows = _rows(
        cursor,
        sql,
        params,
    )

    lowered_question = question.lower()

    rows.sort(
        key=lambda item: (
            0
            if str(
                item.get("TenCauTruc") or ""
            ).lower() in lowered_question
            else 1,

            -sum(
                len(keyword)
                for keyword in keys
                if keyword.lower() in str(
                    item.get("TenCauTruc") or ""
                ).lower()
            ),

            len(
                str(item.get("TenCauTruc") or "")
            ),

            item.get("MaNguPhap") or 0,
        )
    )

    return rows[:3]


# ==========================================================
# 10. TRA CHỮ HÁN VÀ BỘ THỦ
#
# Bảng:
# - dbo.ChuHan
# - dbo.BoThu
# - dbo.BaiHoc
# - dbo.KhoaHoc
#
# Chỉ lấy chữ Hán đã xuất bản.
#
# Nếu có bộ thủ liên quan đã xuất bản,
# lấy thêm tên, ký hiệu và ý nghĩa bộ thủ.
# ==========================================================

def _search_hanzi(
    cursor,
    question,
    terms,
):

    focused = _hanzi_focus(
        question
    )

    if focused:

        chars = [focused]

    else:

        chars = [
            term
            for term in terms
            if len(term) == 1
        ][:8]

    if not chars:
        return []

    sql = f"""
        SELECT TOP (24)
            h.MaChuHan,
            h.MaBaiHoc,
            h.KyTu,
            h.Pinyin,
            h.NghiaTiengViet,
            h.SoNet,
            h.CachGhiNho,
            h.ViDuTiengTrung,
            h.ViDuPinyin,
            h.ViDuTiengViet,

            bt.KyHieu AS KyHieuBoThu,
            bt.TenBoThu,
            bt.YNghia AS YNghiaBoThu,

            kh.MaCapDo AS CapDoHSK

        FROM dbo.ChuHan AS h

        LEFT JOIN dbo.BoThu AS bt
            ON bt.MaBoThu = h.MaBoThu
            AND bt.TrangThai = 'da_xuat_ban'

        LEFT JOIN dbo.BaiHoc AS b
            ON b.MaBaiHoc = h.MaBaiHoc
            AND b.TrangThai = 'da_xuat_ban'

        LEFT JOIN dbo.KhoaHoc AS kh
            ON kh.MaKhoaHoc = b.MaKhoaHoc
            AND kh.TrangThai = 'da_xuat_ban'

        WHERE
            h.TrangThai = 'da_xuat_ban'
            AND h.KyTu IN (
                {_placeholders(chars)}
            )

        ORDER BY h.MaChuHan
    """

    rows = _rows(
        cursor,
        sql,
        chars,
    )

    rows.sort(
        key=lambda item: (
            0
            if focused and item.get("KyTu") == focused
            else 1,

            question.find(
                str(item.get("KyTu") or "")
            ),

            item.get("MaChuHan") or 0,
        )
    )

    return rows[:3]


# ==========================================================
# 11. TRA VÍ DỤ TỪ VỰNG
#
# Bảng:
# dbo.ViDuTuVung
#
# Liên kết:
# ViDuTuVung.MaTuVung -> TuVung.MaTuVung
#
# Chỉ lấy:
# TrangThai = da_xuat_ban
#
# Nếu ví dụ riêng chưa xuất bản,
# từ vựng vẫn có ViDuTiengTrung và
# ViDuTiengViet ở bảng TuVung.
# ==========================================================

def _search_examples(
    cursor,
    vocabulary,
):

    ids = list(
        dict.fromkeys(
            int(item["MaTuVung"])
            for item in vocabulary
        )
    )

    if not ids:
        return []

    sql = f"""
        SELECT TOP (30)
            e.MaViDu,
            e.MaTuVung,
            e.CauTiengTrung,
            e.Pinyin,
            e.NghiaTiengViet,
            e.LaViDuChinh,
            e.ThuTu

        FROM dbo.ViDuTuVung AS e

        INNER JOIN dbo.TuVung AS v
            ON v.MaTuVung = e.MaTuVung
            AND v.DaDuyet = 1

        WHERE
            e.TrangThai = 'da_xuat_ban'
            AND e.MaTuVung IN (
                {_placeholders(ids)}
            )

        ORDER BY
            e.LaViDuChinh DESC,
            e.ThuTu,
            e.MaViDu
    """

    examples = _rows(
        cursor,
        sql,
        ids,
    )

    selected = []
    counted = {}

    # Tối đa hai ví dụ riêng cho mỗi từ,
    # tránh ngữ cảnh gửi cho Qwen3 quá dài.
    for example in examples:

        word_id = int(
            example["MaTuVung"]
        )

        if counted.get(word_id, 0) >= 2:
            continue

        selected.append(example)

        counted[word_id] = (
            counted.get(word_id, 0) + 1
        )

    return selected


# ==========================================================
# 12. CHUẨN BỊ NGỮ CẢNH TỪ SQL CHO AI
#
# Các trường pinyin, nghĩa và ví dụ
# được lấy nguyên từ dữ liệu SQL Server.
#
# Qwen3 chỉ sử dụng làm thông tin tham khảo.
# ==========================================================

def format_approved_context(result):

    sections = []

    examples_by_word = {}

    for example in result.get("examples", []):

        word_id = example["MaTuVung"]

        examples_by_word.setdefault(
            word_id,
            [],
        ).append(example)

    # ------------------------------------------------------
    # A. NGỮ CẢNH TỪ VỰNG
    # ------------------------------------------------------

    def add_vocabulary():

        for item in result.get("vocabulary", []):

            lines = [
                "[TỪ VỰNG ĐÃ DUYỆT - SQL Server]",

                f"Mã: {item['MaTuVung']}",

                f"Chữ Hán: {item['ChuHan']}",

                f"Pinyin: {item['PhienAm']}",

                f"Nghĩa: {item['NghiaTiengViet']}",
            ]

            if item.get("ChuPhonThe"):

                lines.append(
                    f"Phồn thể: {item['ChuPhonThe']}"
                )

            if item.get("TuLoai"):

                lines.append(
                    f"Từ loại: {item['TuLoai']}"
                )

            if item.get("ViDuTiengTrung"):

                lines.append(
                    f"Ví dụ chính: {item['ViDuTiengTrung']}"
                )

                lines.append(
                    "Dịch ví dụ: "
                    + str(
                        item.get("ViDuTiengViet") or ""
                    )
                )

            # Ví dụ bổ sung đã xuất bản.
            for example in examples_by_word.get(
                item["MaTuVung"],
                [],
            ):

                lines.extend([
                    "Ví dụ bổ sung: "
                    + str(example["CauTiengTrung"]),

                    "Pinyin ví dụ: "
                    + str(example.get("Pinyin") or ""),

                    "Dịch ví dụ: "
                    + str(example["NghiaTiengViet"]),
                ])

            sections.append(
                "\n".join(lines)
            )

    # ------------------------------------------------------
    # B. NGỮ CẢNH NGỮ PHÁP
    # ------------------------------------------------------

    def add_grammar():

        for item in result.get("grammar", []):

            lines = [
                "[NGỮ PHÁP ĐÃ XUẤT BẢN - SQL Server]",

                f"Mã: {item['MaNguPhap']}",

                f"Cấu trúc: {item['TenCauTruc']}",

                f"Mô tả: {item.get('MoTa') or ''}",

                f"Cách dùng: {item.get('CachDung') or ''}",

                f"Ví dụ: {item.get('ViDuTiengTrung') or ''}",

                f"Pinyin: {item.get('ViDuPinyin') or ''}",

                f"Dịch: {item.get('ViDuTiengViet') or ''}",
            ]

            if item.get("CapDoHSK"):

                lines.append(
                    f"HSK: {item['CapDoHSK']}"
                )

            sections.append(
                "\n".join(lines)
            )

    # ------------------------------------------------------
    # C. NGỮ CẢNH CHỮ HÁN
    # ------------------------------------------------------

    def add_hanzi():

        for item in result.get("hanzi", []):

            lines = [
                "[CHỮ HÁN ĐÃ XUẤT BẢN - SQL Server]",

                f"Mã: {item['MaChuHan']}",

                f"Chữ: {item['KyTu']}",

                f"Pinyin: {item.get('Pinyin') or ''}",

                f"Nghĩa: {item.get('NghiaTiengViet') or ''}",

                f"Số nét: {item.get('SoNet') if item.get('SoNet') is not None else ''}",

                f"Ghi nhớ: {item.get('CachGhiNho') or ''}",

                f"Ví dụ: {item.get('ViDuTiengTrung') or ''}",

                f"Pinyin ví dụ: {item.get('ViDuPinyin') or ''}",

                f"Dịch ví dụ: {item.get('ViDuTiengViet') or ''}",
            ]

            if item.get("TenBoThu"):

                lines.append(
                    "Bộ thủ: "
                    + str(
                        item.get("KyHieuBoThu") or ""
                    )
                    + " - "
                    + str(item["TenBoThu"])
                )

                lines.append(
                    "Nghĩa bộ thủ: "
                    + str(
                        item.get("YNghiaBoThu") or ""
                    )
                )

            if item.get("CapDoHSK"):

                lines.append(
                    f"HSK: {item['CapDoHSK']}"
                )

            sections.append(
                "\n".join(lines)
            )

    # ------------------------------------------------------
    # D. ƯU TIÊN LOẠI DỮ LIỆU ĐƯỢC HỎI
    # ------------------------------------------------------

    intent = result.get("intent")

    if intent == "ngu_phap":

        add_grammar()
        add_vocabulary()
        add_hanzi()

    elif intent == "chu_han":

        add_hanzi()
        add_vocabulary()
        add_grammar()

    else:

        add_vocabulary()
        add_grammar()
        add_hanzi()

    # Giới hạn độ dài để phù hợp Qwen3 nhỏ.
    return "\n\n".join(
        sections
    )[:5000]


# ==========================================================
# 12A. TRA CỨU KHO KIẾN THỨC BỔ SUNG CHATBOT
#
# Bảng: dbo.KhoKienThuc
#
# Chỉ sử dụng kiến thức:
# - Đã duyệt: DaDuyet = 1
# - Đang hoạt động: DangHoatDong = 1
#
# Chỉ hỗ trợ câu hỏi mở (hoi_dap).
# Không thay thế học liệu từ vựng, ngữ pháp, chữ Hán.
# Không can thiệp hội thoại nhập vai.
# ==========================================================

_SUPPLEMENTAL_SKIP = frozenset({
    "cách", "các", "của", "trong", "bằng",
    "tiếng", "trung", "cho", "mình", "tôi",
    "bạn", "hãy", "giải", "thích", "giúp",
    "về", "như", "thế", "nào", "không",
    "được", "với", "một", "là", "và",
    "khi", "để", "có", "thể", "xin",
    "biết", "nội", "dung", "gì", "nhé",
})


def _supplemental_terms(text):
    """
    Tách các từ khóa quan trọng trong
    câu hỏi hoặc tiêu đề kiến thức.

    Bỏ những từ chung để hạn chế
    tìm nhầm kiến thức không liên quan.
    """

    words = re.findall(
        r"[^\W_]+",
        str(text or "").lower(),
    )

    return {
        word
        for word in words
        if len(word) >= 2
        and word not in _SUPPLEMENTAL_SKIP
    }


def _search_supplemental_knowledge(
    cursor,
    question,
):
    """
    Tìm kiến thức bổ sung có tiêu đề
    phù hợp với câu hỏi của người học.

    Sử dụng cursor SQL đang có.
    Không mở thêm kết nối bên trong hàm.
    """

    lowered = question.lower()

    # ------------------------------------------------------
    # 01. KHÔNG CAN THIỆP LUYỆN HỘI THOẠI
    # ------------------------------------------------------

    dialogue_phrases = (
        "đóng vai",
        "nhập vai",
        "luyện hội thoại",
        "tạo hội thoại",
        "đoạn hội thoại",
        "hội thoại",
        "trò chuyện",
        "hãy nói chuyện",
        "đối thoại",
        "扮演",
        "角色扮演",
        "对话",
    )

    if any(
        phrase in lowered
        for phrase in dialogue_phrases
    ):
        return None

    # ------------------------------------------------------
    # 02. TÁCH TỪ KHÓA CÂU HỎI
    # ------------------------------------------------------

    question_terms = _supplemental_terms(
        question
    )

    if len(question_terms) < 2:
        return None

    search_terms = sorted(
        question_terms,
        key=lambda value: (
            -len(value),
            value,
        ),
    )[:12]

    # ------------------------------------------------------
    # 03. TÌM TRONG TIÊU ĐỀ KIẾN THỨC
    #
    # Không tìm lan man trong toàn bộ nội dung.
    # Sử dụng tham số SQL để an toàn.
    # ------------------------------------------------------

    conditions = " OR ".join(
        "CHARINDEX(?, LOWER(TieuDe)) > 0"
        for _ in search_terms
    )

    sql = f"""
        SELECT TOP (100)
            MaKienThuc,
            TieuDe,
            NoiDung,
            MaCapDo

        FROM dbo.KhoKienThuc

        WHERE DaDuyet = 1
          AND DangHoatDong = 1
          AND ({conditions})

        ORDER BY
            NgayCapNhat DESC,
            MaKienThuc DESC
    """

    candidates = _rows(
        cursor,
        sql,
        search_terms,
    )

    # ------------------------------------------------------
    # 04. CHỌN KIẾN THỨC PHÙ HỢP NHẤT
    #
    # Cần ít nhất 2 từ khóa trùng nhau
    # và độ phủ tiêu đề từ 60% trở lên.
    # ------------------------------------------------------

    best = None
    best_score = None

    for item in candidates:

        title_terms = _supplemental_terms(
            item.get("TieuDe")
        )

        if len(title_terms) < 2:
            continue

        common = len(
            title_terms & question_terms
        )

        coverage = (
            common / len(title_terms)
        )

        if (
            common < 2
            or coverage < 0.6
        ):
            continue

        score = (
            coverage,
            common,
        )

        if (
            best_score is None
            or score > best_score
        ):
            best = item
            best_score = score

    return best

# ==========================================================
# 13. HÀM CHÍNH: TRA KIẾN THỨC ĐÃ DUYỆT
#
# Đây là hàm được Admin và Student gọi.
#
# Giữ các trường tương thích code cũ:
# - intent
# - vocabulary
# - grammar
# - hanzi
# - found
# - context
#
# Bổ sung:
# - examples
#
# Không lưu hoặc thay đổi dữ liệu SQL.
# ==========================================================

def search_approved_knowledge(question):

    question = str(
        question or ""
    ).strip()

    if not 1 <= len(question) <= 2000:

        raise ValueError(
            "Câu hỏi phải có từ 1 đến 2000 ký tự."
        )

    intent = detect_intent(
        question
    )

    result = {
        "intent": intent,

        "vocabulary": [],

        "grammar": [],

        "hanzi": [],

        "examples": [],

        "found": False,

        "context": "",
    }

    
    # ------------------------------------------------------
    # TRA CỨU KIẾN THỨC BỔ SUNG CHO CÂU HỎI MỞ
    #
    # Chỉ xử lý khi intent = hoi_dap.
    #
    # Không thay đổi:
    # - Tra từ vựng
    # - Tra ngữ pháp
    # - Tra chữ Hán
    # - Hội thoại nhập vai
    # ------------------------------------------------------

    if intent == "hoi_dap":

        with closing(get_connection()) as conn:

            with closing(conn.cursor()) as cursor:

                extra = _search_supplemental_knowledge(
                    cursor,
                    question,
                )

        # --------------------------------------------------
        # CÓ KIẾN THỨC BỔ SUNG ĐÃ DUYỆT
        # --------------------------------------------------

        if extra:

            result["found"] = True

            result["supplemental"] = [
                extra
            ]

            # Giữ cấu trúc context mà
            # chatbot Student và Admin đã dùng.
            #
            # Qwen3 được cung cấp nội dung
            # đã duyệt để tham khảo khi trả lời.

            result["context"] = (
                "[KIẾN THỨC BỔ SUNG ĐÃ DUYỆT "
                "- SQL Server]\n"
                f"Mã: {extra['MaKienThuc']}\n"
                f"Tiêu đề: {extra['TieuDe']}\n"
                f"Nội dung: "
                f"{str(extra['NoiDung'])[:2000]}"
            )

        # --------------------------------------------------
        # KHÔNG CÓ KIẾN THỨC PHÙ HỢP
        #
        # Giữ kết quả mặc định như code cũ.
        # --------------------------------------------------

        return result


    terms = extract_hanzi_terms(
        question
    )

    if not terms and intent == "chu_han":
        return result

    # ------------------------------------------------------
    # A. TRUY VẤN SQL SERVER
    # ------------------------------------------------------

    with closing(get_connection()) as conn:

        with closing(conn.cursor()) as cursor:

            # TRA TỪ VỰNG
            result["vocabulary"] = _search_vocabulary(
                cursor,
                question,
                terms,
                intent,
            )

            # TRA NGỮ PHÁP
            if intent == "ngu_phap":

                result["grammar"] = _search_grammar(
                    cursor,
                    question,
                    terms,
                )

            # TRA CHỮ HÁN
            if intent == "chu_han":

                result["hanzi"] = _search_hanzi(
                    cursor,
                    question,
                    terms,
                )

            # TRA VÍ DỤ TỪ VỰNG ĐÃ XUẤT BẢN
            if result["vocabulary"]:

                result["examples"] = _search_examples(
                    cursor,
                    result["vocabulary"],
                )

    # ------------------------------------------------------
    # B. KIỂM TRA CÓ KIẾN THỨC THẬT HAY KHÔNG
    # ------------------------------------------------------

    result["found"] = bool(
        result["vocabulary"]
        or result["grammar"]
        or result["hanzi"]
    )

    # ------------------------------------------------------
    # C. TẠO NGỮ CẢNH TỪ SQL CHO QWEN3
    # ------------------------------------------------------

    result["context"] = format_approved_context(
        result
    )

    return result
