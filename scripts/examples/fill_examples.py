import os
import re
import json
import time
import argparse
from pathlib import Path

import pyodbc
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================================
# 1. CẤU HÌNH
# ==========================================================

ROOT = Path(r"D:\DATN1")

DATA_DIR = ROOT / "scripts" / "examples" / "data"

PREVIEW_FILE = (
    DATA_DIR / "examples_preview_gemini.json"
)

MODEL_DEFAULT = "gemini-3.8-flash"

load_dotenv(ROOT / ".env")


# ==========================================================
# 2. HÀM HỖ TRỢ
# ==========================================================

def clean(value):
    return str(value or "").strip()


def get_target_word(chu_han):
    """
    Một số từ trong DB có dạng:

    面1 -> 面
    称1 -> 称
    家（科学家） -> 科学家
    """

    word = clean(chu_han)

    match = re.search(
        r"（([^（）]+)）",
        word
    )

    if match:
        return match.group(1).strip()

    return re.sub(
        r"\d+$",
        "",
        word
    ).strip()


def normalize_chinese(sentence):
    """
    Đảm bảo câu Trung có dấu kết thúc.
    """

    sentence = clean(sentence)

    if (
        sentence
        and sentence[-1]
        not in "。！？!?"
    ):
        sentence += "。"

    return sentence


def normalize_vietnamese(sentence):
    """
    Gemini đôi khi dùng dấu 。 cho tiếng Việt.
    Ta tự đổi về dấu .
    """

    sentence = clean(sentence)

    if not sentence:
        return ""

    sentence = sentence.replace(
        "。",
        "."
    )

    if sentence[-1] not in ".?!":
        sentence += "."

    return sentence


# ==========================================================
# 3. KẾT NỐI SQL SERVER
# ==========================================================

def connect_db():

    server = clean(
        os.getenv("DB_SERVER")
    )

    database = clean(
        os.getenv(
            "DB_NAME",
            "HocTiengTrungDB"
        )
    )

    username = clean(
        os.getenv("DB_USER")
    )

    password = os.getenv(
        "DB_PASSWORD",
        ""
    )

    if not server:
        raise RuntimeError(
            "Chưa có DB_SERVER trong .env"
        )

    drivers = pyodbc.drivers()

    driver = next(
        (
            d
            for d in reversed(drivers)
            if "ODBC Driver" in d
            and "SQL Server" in d
        ),
        None
    )

    if not driver:
        raise RuntimeError(
            "Không tìm thấy ODBC Driver for SQL Server."
        )

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        "TrustServerCertificate=yes",
        "Connection Timeout=30",
    ]

    if username and password:

        parts += [
            f"UID={username}",
            f"PWD={password}",
        ]

    else:

        parts.append(
            "Trusted_Connection=yes"
        )

    return pyodbc.connect(
        ";".join(parts),
        autocommit=False
    )


# ==========================================================
# 4. LẤY TỪ ĐANG THIẾU VÍ DỤ
# ==========================================================

def get_missing_words(
    conn,
    level=None
):

    sql = """
    SELECT
        tv.MaTuVung,
        MIN(kh.MaCapDo) AS HSK,
        tv.ChuHan,
        tv.PhienAm,
        tv.NghiaTiengViet,
        tv.TuLoai,
        tv.ViDuTiengTrung,
        tv.ViDuTiengViet

    FROM dbo.TuVung AS tv

    INNER JOIN dbo.TuVungBaiHoc AS tvbh
        ON tvbh.MaTuVung = tv.MaTuVung

    INNER JOIN dbo.BaiHoc AS bh
        ON bh.MaBaiHoc = tvbh.MaBaiHoc

    INNER JOIN dbo.KhoaHoc AS kh
        ON kh.MaKhoaHoc = bh.MaKhoaHoc

    WHERE
        kh.MaCapDo BETWEEN 2 AND 4

        AND
        (
            NULLIF(
                LTRIM(
                    RTRIM(
                        tv.ViDuTiengTrung
                    )
                ),
                N''
            ) IS NULL

            OR

            NULLIF(
                LTRIM(
                    RTRIM(
                        tv.ViDuTiengViet
                    )
                ),
                N''
            ) IS NULL
        )

    GROUP BY
        tv.MaTuVung,
        tv.ChuHan,
        tv.PhienAm,
        tv.NghiaTiengViet,
        tv.TuLoai,
        tv.ViDuTiengTrung,
        tv.ViDuTiengViet

    HAVING
        (
            ? IS NULL
            OR MIN(kh.MaCapDo) = ?
        )

    ORDER BY
        HSK,
        tv.MaTuVung;
    """

    cursor = conn.cursor()

    cursor.execute(
        sql,
        level,
        level
    )

    columns = [
        column[0]
        for column
        in cursor.description
    ]

    return [
        dict(
            zip(
                columns,
                row
            )
        )
        for row
        in cursor.fetchall()
    ]


# ==========================================================
# 5. FILE PREVIEW
# ==========================================================

def load_preview():

    if not PREVIEW_FILE.exists():
        return {}

    data = json.loads(
        PREVIEW_FILE.read_text(
            encoding="utf-8"
        )
    )

    return {
        int(item["MaTuVung"]): item
        for item
        in data.get(
            "items",
            []
        )
    }


def save_preview(items):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    values = sorted(
        items.values(),
        key=lambda x: (
            int(x["HSK"]),
            int(x["MaTuVung"])
        )
    )

    PREVIEW_FILE.write_text(
        json.dumps(
            {
                "items": values
            },
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


# ==========================================================
# 6. KIỂM TRA CÂU
# ==========================================================

def validate_item(
    item,
    source
):

    chinese = normalize_chinese(
        item.get(
            "ViDuTiengTrung"
        )
    )

    vietnamese = normalize_vietnamese(
        item.get(
            "ViDuTiengViet"
        )
    )

    target = get_target_word(
        source["ChuHan"]
    )

    if not chinese:
        return False, "Thiếu câu Trung"

    if not vietnamese:
        return False, "Thiếu câu Việt"

    if (
        target
        and target not in chinese
    ):
        return (
            False,
            f"Câu không chứa từ {target}"
        )

    chinese_chars = re.findall(
        r"[\u4e00-\u9fff]",
        chinese
    )

    if len(chinese_chars) < 5:
        return (
            False,
            "Câu Trung quá ngắn"
        )

    if (
        len(chinese) > 1000
        or len(vietnamese) > 1000
    ):
        return (
            False,
            "Câu quá dài"
        )

    return True, "OK"


# ==========================================================
# 7. GEMINI
# ==========================================================

def create_client():

    key = clean(
        os.getenv(
            "GEMINI_API_KEY"
        )
    )

    if not key:
        raise RuntimeError(
            "Chưa có GEMINI_API_KEY trong .env"
        )

    return genai.Client(
        api_key=key
    )


def create_prompt(batch):

    words = []

    for row in batch:

        words.append(
            {
                "MaTuVung":
                    int(
                        row["MaTuVung"]
                    ),

                "HSK":
                    int(
                        row["HSK"]
                    ),

                "ChuHan":
                    clean(
                        row["ChuHan"]
                    ),

                "TuBatBuocTrongCau":
                    get_target_word(
                        row["ChuHan"]
                    ),

                "PhienAm":
                    clean(
                        row["PhienAm"]
                    ),

                "NghiaTiengViet":
                    clean(
                        row[
                            "NghiaTiengViet"
                        ]
                    ),

                "TuLoai":
                    clean(
                        row["TuLoai"]
                    ),

                "ViDuTiengTrungHienCo":
                    clean(
                        row[
                            "ViDuTiengTrung"
                        ]
                    ),

                "ViDuTiengVietHienCo":
                    clean(
                        row[
                            "ViDuTiengViet"
                        ]
                    ),
            }
        )

    return f"""
Bạn là giáo viên tiếng Trung
cho người Việt Nam.

Hãy tạo 1 câu ví dụ tiếng Trung
và 1 bản dịch tiếng Việt
cho MỖI từ bên dưới.

YÊU CẦU:

1. Dùng đúng nghĩa trong NghiaTiengViet.

2. Câu tiếng Trung phải chứa
   TuBatBuocTrongCau.

3. Câu phải tự nhiên,
   đúng ngữ pháp.

4. Câu phù hợp với cấp HSK được ghi.

5. Có thể sử dụng các từ quen thuộc
   ở những cấp HSK gần nhau.
   Không cần ép câu chỉ chứa từ
   của đúng một cấp HSK.

6. Không làm câu quá phức tạp.

7. Câu cần đủ nội dung để dùng cho:
   - Đọc hiểu
   - Nghe ghép câu

8. Bản dịch tiếng Việt phải tự nhiên
   và đúng nghĩa câu Trung.

9. Không viết pinyin trong câu ví dụ.

10. Nếu ví dụ hiện tại đã có,
    giữ nguyên phần đã có.

11. Mỗi MaTuVung chỉ xuất hiện 1 lần.

12. Không bỏ sót từ.

13. Chỉ trả JSON.
    Không giải thích.
    Không markdown.

Cấu trúc JSON:

{{
  "items": [
    {{
      "MaTuVung": 123,
      "ViDuTiengTrung":
        "我每天晚上十点睡觉。",
      "ViDuTiengViet":
        "Mỗi tối tôi đi ngủ lúc mười giờ."
    }}
  ]
}}

DỮ LIỆU:

{json.dumps(
    words,
    ensure_ascii=False
)}
""".strip()


def call_gemini(client, model, batch):

    for attempt in range(1, 4):

        try:
            response = client.models.generate_content(
                model=model,
                contents=create_prompt(batch),
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )

            if not response.text:
                raise RuntimeError("Gemini không trả dữ liệu")

            result = json.loads(response.text)

            items = result.get("items")

            if not isinstance(items, list):
                raise ValueError("JSON thiếu items")

            return items

        except Exception as error:

            message = str(error).lower()

            if "429" in message or "503" in message:

                if attempt == 5:
                    raise

                # Đợi lâu hơn sau mỗi lần lỗi
                wait_time = attempt * 15

                print(
                    f"Gemini đang bận hoặc giới hạn lượt. "
                    f"Đợi {wait_time} giây rồi thử lại..."
                )

                time.sleep(wait_time)

            else:
                raise


# ==========================================================
# 8. TẠO CÂU
# ==========================================================

def generate(
    model,
    level,
    limit,
    batch_size
):

    client = create_client()

    conn = connect_db()

    try:

        rows = get_missing_words(
            conn,
            level
        )

        preview = load_preview()

        pending = [
            row
            for row in rows
            if int(
                row["MaTuVung"]
            )
            not in preview
        ]

        if limit > 0:

            pending = pending[
                :limit
            ]

        print("=" * 50)

        print(
            "Số từ còn thiếu:",
            len(rows)
        )

        print(
            "Số từ tạo lần này:",
            len(pending)
        )

        print(
            "HSK:",
            level or "2-4"
        )

        print(
            "Model:",
            model
        )

        print("=" * 50)

        for start in range(
            0,
            len(pending),
            batch_size
        ):

            batch = pending[
                start:
                start + batch_size
            ]

            batch_no = (
                start // batch_size
            ) + 1

            source_map = {
                int(
                    row["MaTuVung"]
                ): row
                for row
                in batch
            }

            try:

                results = call_gemini(
                    client,
                    model,
                    batch
                )

            except Exception as exc:

                print(
                    f"Batch {batch_no} lỗi:"
                )

                print(exc)

                error_text = str(
                    exc
                ).lower()

                if (
                    "429" in error_text
                    or "quota" in error_text
                    or
                    "resource_exhausted"
                    in error_text
                ):

                    print(
                        "Đã chạm giới hạn "
                        "Free Tier."
                    )

                    print(
                        "Dữ liệu đã tạo trước "
                        "đó vẫn được giữ."
                    )

                    return

                continue

            accepted = 0

            for item in results:

                try:

                    mid = int(
                        item[
                            "MaTuVung"
                        ]
                    )

                except Exception:

                    continue

                source = source_map.get(
                    mid
                )

                if source is None:
                    continue

                # Không ghi đè dữ liệu cũ

                old_cn = clean(
                    source[
                        "ViDuTiengTrung"
                    ]
                )

                old_vi = clean(
                    source[
                        "ViDuTiengViet"
                    ]
                )

                if old_cn:

                    item[
                        "ViDuTiengTrung"
                    ] = old_cn

                if old_vi:

                    item[
                        "ViDuTiengViet"
                    ] = old_vi

                # Chuẩn hóa dấu câu

                item[
                    "ViDuTiengTrung"
                ] = normalize_chinese(
                    item.get(
                        "ViDuTiengTrung"
                    )
                )

                item[
                    "ViDuTiengViet"
                ] = normalize_vietnamese(
                    item.get(
                        "ViDuTiengViet"
                    )
                )

                valid, reason = (
                    validate_item(
                        item,
                        source
                    )
                )

                if not valid:

                    print(
                        f"SKIP {mid}: "
                        f"{reason}"
                    )

                    continue

                preview[mid] = {

                    "MaTuVung":
                        mid,

                    "HSK":
                        int(
                            source["HSK"]
                        ),

                    "ChuHan":
                        clean(
                            source["ChuHan"]
                        ),

                    "PhienAm":
                        clean(
                            source["PhienAm"]
                        ),

                    "NghiaTiengViet":
                        clean(
                            source[
                                "NghiaTiengViet"
                            ]
                        ),

                    "TuLoai":
                        clean(
                            source["TuLoai"]
                        ),

                    "ViDuTiengTrung":
                        item[
                            "ViDuTiengTrung"
                        ],

                    "ViDuTiengViet":
                        item[
                            "ViDuTiengViet"
                        ],
                }

                accepted += 1

            save_preview(
                preview
            )

            print(
                f"Batch {batch_no}: "
                f"{accepted}/"
                f"{len(batch)} PASS"
            )

            print(
                "Tổng preview:",
                len(preview)
            )

            time.sleep(15)

        print()

        print(
            "ĐÃ LƯU PREVIEW:"
        )

        print(
            PREVIEW_FILE
        )

        print(
            "CHƯA GHI VÀO SQL."
        )

    finally:

        conn.rollback()

        conn.close()


# ==========================================================
# 9. KIỂM TRA PREVIEW
# ==========================================================

def validate_preview(
    level=None
):

    conn = connect_db()

    try:

        rows = get_missing_words(
            conn,
            level
        )

        source_map = {
            int(
                row["MaTuVung"]
            ): row
            for row in rows
        }

        preview = load_preview()

        passed = 0
        failed = 0

        for mid, item in (
            preview.items()
        ):

            source = source_map.get(
                mid
            )

            if source is None:
                continue

            valid, reason = (
                validate_item(
                    item,
                    source
                )
            )

            if valid:

                passed += 1

            else:

                failed += 1

                print(
                    f"FAIL {mid}: "
                    f"{reason}"
                )

        print(
            "PASS:",
            passed
        )

        print(
            "FAIL:",
            failed
        )

    finally:

        conn.rollback()

        conn.close()


# ==========================================================
# 10. IMPORT VÀO SQL
# ==========================================================

def import_preview(
    level=None,
    commit=False
):

    preview = load_preview()

    if not preview:

        raise RuntimeError(
            "Chưa có preview."
        )

    conn = connect_db()

    try:

        rows = get_missing_words(
            conn,
            level
        )

        source_map = {
            int(
                row["MaTuVung"]
            ): row
            for row in rows
        }

        cursor = conn.cursor()

        affected = 0

        for mid, item in (
            preview.items()
        ):

            source = source_map.get(
                mid
            )

            if source is None:
                continue

            chinese = normalize_chinese(
                item[
                    "ViDuTiengTrung"
                ]
            )

            vietnamese = (
                normalize_vietnamese(
                    item[
                        "ViDuTiengViet"
                    ]
                )
            )

            item[
                "ViDuTiengTrung"
            ] = chinese

            item[
                "ViDuTiengViet"
            ] = vietnamese

            valid, reason = (
                validate_item(
                    item,
                    source
                )
            )

            if not valid:

                raise RuntimeError(
                    f"{mid}: {reason}"
                )

            cursor.execute(
                """
                UPDATE dbo.TuVung

                SET
                    ViDuTiengTrung =
                    CASE

                        WHEN NULLIF(
                            LTRIM(
                                RTRIM(
                                    ViDuTiengTrung
                                )
                            ),
                            N''
                        ) IS NULL

                        THEN ?

                        ELSE ViDuTiengTrung

                    END,

                    ViDuTiengViet =
                    CASE

                        WHEN NULLIF(
                            LTRIM(
                                RTRIM(
                                    ViDuTiengViet
                                )
                            ),
                            N''
                        ) IS NULL

                        THEN ?

                        ELSE ViDuTiengViet

                    END

                WHERE
                    MaTuVung = ?

                    AND
                    (
                        NULLIF(
                            LTRIM(
                                RTRIM(
                                    ViDuTiengTrung
                                )
                            ),
                            N''
                        ) IS NULL

                        OR

                        NULLIF(
                            LTRIM(
                                RTRIM(
                                    ViDuTiengViet
                                )
                            ),
                            N''
                        ) IS NULL
                    );
                """,

                chinese,
                vietnamese,
                mid
            )

            affected += (
                cursor.rowcount
            )

        print(
            "Số từ cập nhật:",
            affected
        )

        if commit:

            conn.commit()

            print(
                "COMMIT PASS"
            )

            print(
                "ĐÃ LƯU VÀO SQL."
            )

        else:

            conn.rollback()

            print(
                "DRY RUN PASS"
            )

            print(
                "DATABASE CHƯA THAY ĐỔI."
            )

    except Exception:

        conn.rollback()

        raise

    finally:

        conn.close()


# ==========================================================
# 11. BÁO CÁO
# ==========================================================

def report():

    conn = connect_db()

    try:

        rows = get_missing_words(
            conn
        )

        counts = {
            2: 0,
            3: 0,
            4: 0
        }

        for row in rows:

            counts[
                int(
                    row["HSK"]
                )
            ] += 1

        print("=" * 40)

        for level in (
            2,
            3,
            4
        ):

            print(
                f"HSK{level}: "
                f"{counts[level]} "
                f"từ thiếu ví dụ"
            )

        print("-" * 40)

        print(
            "Tổng từ duy nhất:",
            len(rows)
        )

        print("=" * 40)

    finally:

        conn.rollback()

        conn.close()


# ==========================================================
# 12. MAIN
# ==========================================================

def main():

    parser = (
        argparse.ArgumentParser()
    )

    modes = (
        parser
        .add_mutually_exclusive_group(
            required=True
        )
    )

    modes.add_argument(
        "--generate",
        action="store_true"
    )

    modes.add_argument(
        "--validate",
        action="store_true"
    )

    modes.add_argument(
        "--import-preview",
        action="store_true"
    )

    modes.add_argument(
        "--report",
        action="store_true"
    )

    parser.add_argument(
        "--commit",
        action="store_true"
    )

    parser.add_argument(
        "--level",
        type=int,
        choices=[
            2,
            3,
            4
        ],
        default=None
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=5
    )

    parser.add_argument(
        "--model",
        default=MODEL_DEFAULT
    )

    args = parser.parse_args()

    if (
        args.commit
        and not args.import_preview
    ):

        parser.error(
            "--commit phải dùng cùng "
            "--import-preview"
        )

    if args.generate:

        generate(
            args.model,
            args.level,
            args.limit,
            args.batch_size
        )

    elif args.validate:

        validate_preview(
            args.level
        )

    elif args.import_preview:

        import_preview(
            args.level,
            args.commit
        )

    elif args.report:

        report()


if __name__ == "__main__":
    main()