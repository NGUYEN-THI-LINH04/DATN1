
# -*- coding: utf-8 -*-
"""
BUOC 55 - BO SUNG NGU PHAP CHO 12 BAI HSK3 CON TRONG

- Giu nguyen 20 ngu phap da co.
- Them 12 mau ngu phap de xuat.
- Co giai thich, cach dung, vi du, Pinyin, ban dich.
- Kiem tra MaBaiHoc va tinh trang trong SQL.
- PREVIEW mac dinh, --commit moi INSERT.
- Khong UPDATE/DELETE HSK1, HSK2, HSK3.
- Tat ca ngu phap moi la ban_nhap.

Luu y: chua xac minh chuan cap do HSK3.
"""

import argparse
import hashlib
import json
import sys
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from database import get_connection

DATA = ROOT / "scripts" / "hsk3" / "data" / "processed"
PREVIEW_FILE = DATA / "hsk3_missing_grammar_preview.json"

COURSE_ID = 3

# So bai -> cau truc, mo ta, cach dung, vi du ZH/PY/VI
GRAMMAR = {
    2: (
        "为了……",
        "Diễn đạt mục đích của hành động.",
        "为了 + mục đích, chủ ngữ + hành động.",
        "为了学好汉语，她每天练习听力。",
        "Wèile xuéhǎo Hànyǔ, tā měitiān liànxí tīnglì.",
        "Để học tốt tiếng Trung, cô ấy luyện nghe mỗi ngày.",
    ),
    3: (
        "通过……",
        "Nêu phương thức hoặc quá trình giúp đạt được kết quả.",
        "通过 + hoạt động / phương thức, + kết quả.",
        "通过这次实习，我学到了很多东西。",
        "Tōngguò zhè cì shíxí, wǒ xuédào le hěn duō dōngxi.",
        "Thông qua kỳ thực tập này, tôi đã học được rất nhiều điều.",
    ),
    5: (
        "互相 + động từ",
        "Diễn đạt hành động qua lại giữa hai hoặc nhiều người.",
        "Chủ ngữ số nhiều + 互相 + động từ.",
        "我们应该互相帮助。",
        "Wǒmen yīnggāi hùxiāng bāngzhù.",
        "Chúng ta nên giúp đỡ lẫn nhau.",
    ),
    7: (
        "最好 + động từ",
        "Dùng để đưa ra lời khuyên hoặc phương án tốt nhất.",
        "Chủ ngữ + 最好 + động từ / cụm động từ.",
        "你最好早点儿休息。",
        "Nǐ zuìhǎo zǎodiǎnr xiūxi.",
        "Tốt nhất bạn nên nghỉ ngơi sớm một chút.",
    ),
    8: (
        "A + 不如 + B + tính từ",
        "So sánh, diễn đạt A không bằng B về một phương diện.",
        "A + 不如 + B + tính từ.",
        "我跑步不如他快。",
        "Wǒ pǎobù bùrú tā kuài.",
        "Tôi chạy không nhanh bằng anh ấy.",
    ),
    9: (
        "尽量 + động từ",
        "Diễn đạt việc cố gắng thực hiện một hành động trong khả năng.",
        "Chủ ngữ + 尽量 + động từ / cụm động từ.",
        "我们尽量少吃甜食。",
        "Wǒmen jǐnliàng shǎo chī tiánshí.",
        "Chúng ta cố gắng ăn ít đồ ngọt.",
    ),
    11: (
        "要么……要么……",
        "Đưa ra hai lựa chọn thay thế nhau.",
        "要么 + lựa chọn 1, 要么 + lựa chọn 2.",
        "我们要么坐地铁，要么坐公交车。",
        "Wǒmen yàome zuò dìtiě, yàome zuò gōngjiāochē.",
        "Chúng ta hoặc đi tàu điện ngầm, hoặc đi xe buýt.",
    ),
    12: (
        "提前 + động từ",
        "Diễn đạt việc thực hiện hành động trước thời điểm dự kiến.",
        "提前 + động từ / cụm động từ.",
        "出发前，我们最好提前订票。",
        "Chūfā qián, wǒmen zuìhǎo tíqián dìngpiào.",
        "Trước khi xuất phát, tốt nhất chúng ta nên đặt vé trước.",
    ),
    13: (
        "根据……",
        "Nêu căn cứ để đưa ra nhận định hoặc quyết định.",
        "根据 + căn cứ, + nhận định / kết luận.",
        "根据天气预报，明天可能下雨。",
        "Gēnjù tiānqì yùbào, míngtiān kěnéng xià yǔ.",
        "Theo dự báo thời tiết, ngày mai có thể sẽ mưa.",
    ),
    16: (
        "与其……不如……",
        "Đưa ra hai phương án và ưu tiên phương án thứ hai.",
        "与其 + phương án 1, 不如 + phương án 2.",
        "与其在家看电视，不如出去走走。",
        "Yǔqí zài jiā kàn diànshì, bùrú chūqù zǒuzou.",
        "Thay vì ở nhà xem tivi, chi bằng ra ngoài đi dạo.",
    ),
    17: (
        "以……为例",
        "Dùng một đối tượng hoặc sự việc làm ví dụ minh họa.",
        "以 + đối tượng + 为例, + nội dung giải thích.",
        "以春节为例，很多家庭会一起吃饭。",
        "Yǐ Chūnjié wéi lì, hěn duō jiātíng huì yìqǐ chīfàn.",
        "Lấy Tết Nguyên đán làm ví dụ, nhiều gia đình sẽ ăn cơm cùng nhau.",
    ),
    18: (
        "用……来……",
        "Diễn đạt việc sử dụng công cụ hoặc phương pháp nhằm đạt mục đích.",
        "用 + công cụ / phương pháp + 来 + động từ.",
        "我用手机来学习汉语。",
        "Wǒ yòng shǒujī lái xuéxí Hànyǔ.",
        "Tôi dùng điện thoại để học tiếng Trung.",
    ),
}


def make_signature(data):
    raw = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def check_database(cursor):
    cursor.execute("""
        SELECT
            bh.MaBaiHoc,
            bh.SoThuTuBai,
            bh.TrangThai,
            COUNT(np.MaNguPhap) AS SoNguPhap
        FROM dbo.BaiHoc AS bh
        LEFT JOIN dbo.NguPhap AS np
            ON np.MaBaiHoc = bh.MaBaiHoc
        WHERE bh.MaKhoaHoc = ?
        GROUP BY
            bh.MaBaiHoc,
            bh.SoThuTuBai,
            bh.TrangThai
        ORDER BY bh.SoThuTuBai;
    """, COURSE_ID)

    rows = cursor.fetchall()

    if len(rows) != 20:
        raise RuntimeError(
            f"HSK3 phai co 20 bai. Tim thay {len(rows)}."
        )

    lessons = {}
    total_existing = 0

    for lesson_id, number, status, count in rows:
        number = int(number)
        count = int(count)

        if number in lessons:
            raise RuntimeError(
                f"Trung SoThuTuBai={number}."
            )

        lessons[number] = {
            "id": int(lesson_id),
            "status": str(status),
            "grammar_count": count,
        }

        total_existing += count

    if set(lessons) != set(range(1, 21)):
        raise RuntimeError(
            "HSK3 khong du so thu tu 1-20."
        )

    if total_existing != 20:
        raise RuntimeError(
            "So ngu phap HSK3 da thay doi. "
            f"Du kien 20, thuc te {total_existing}."
        )

    empty_lessons = {
        number
        for number, value in lessons.items()
        if value["grammar_count"] == 0
    }

    if empty_lessons != set(GRAMMAR):
        raise RuntimeError(
            "Danh sach bai trong khong khop.\n"
            f"Thuc te: {sorted(empty_lessons)}\n"
            f"Du kien: {sorted(GRAMMAR)}"
        )

    if any(
        lessons[number]["status"] != "ban_nhap"
        for number in lessons
    ):
        raise RuntimeError(
            "Co bai HSK3 khong con la ban_nhap."
        )

    return lessons


def validate_contents():
    if len(GRAMMAR) != 12:
        raise RuntimeError("Can dung 12 mau bo sung.")

    for number, fields in GRAMMAR.items():
        if len(fields) != 6:
            raise RuntimeError(
                f"Bai {number}: du lieu khong day du."
            )

        if any(not str(field).strip() for field in fields):
            raise RuntimeError(
                f"Bai {number}: co truong rong."
            )

        title, description, usage, zh, py, vi = fields

        if len(title) > 300:
            raise RuntimeError(
                f"Bai {number}: ten cau truc qua dai."
            )

        if any(len(text) > 1000 for text in (zh, py, vi)):
            raise RuntimeError(
                f"Bai {number}: vi du qua dai."
            )


def make_plan(lessons):
    plan = []

    for number in sorted(GRAMMAR):
        title, description, usage, zh, py, vi = GRAMMAR[number]

        plan.append({
            "SoThuTuBai": number,
            "MaBaiHoc": lessons[number]["id"],
            "TenCauTruc": title,
            "MoTa": description,
            "CachDung": usage,
            "ViDuTiengTrung": zh,
            "ViDuPinyin": py,
            "ViDuTiengViet": vi,
            "ThuTu": 1,
            "TrangThai": "ban_nhap",
        })

    return plan


def insert_one(cursor, item):
    cursor.execute("""
        INSERT INTO dbo.NguPhap
        (
            MaBaiHoc,
            TenCauTruc,
            MoTa,
            CachDung,
            ViDuTiengTrung,
            ViDuPinyin,
            ViDuTiengViet,
            MaTep,
            MaNguon,
            ThuTu,
            TrangThai,
            MaQuanTriVienCapNhat,
            NgayCapNhat
        )
        OUTPUT INSERTED.MaNguPhap
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?,
            NULL, NULL, ?,
            'ban_nhap', NULL, NULL
        );
    """,
        item["MaBaiHoc"],
        item["TenCauTruc"],
        item["MoTa"],
        item["CachDung"],
        item["ViDuTiengTrung"],
        item["ViDuPinyin"],
        item["ViDuTiengViet"],
        item["ThuTu"],
    )

    result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            "Khong nhan duoc MaNguPhap."
        )

    return int(result[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    print("=" * 68)
    print("BUOC 55 - BO SUNG NGU PHAP HSK3")
    print("=" * 68)
    print("CHE DO:", "COMMIT" if args.commit else "PREVIEW")

    validate_contents()

    with closing(get_connection()) as connection:
        if getattr(connection, "autocommit", False):
            raise RuntimeError(
                "Ket noi SQL dang autocommit=True."
            )

        with closing(connection.cursor()) as cursor:
            try:
                lessons = check_database(cursor)
                plan = make_plan(lessons)
                signature = make_signature(plan)

                print("\nCAC BAI SE DUOC BO SUNG:")

                for row in plan:
                    print(
                        f"Bai {row['SoThuTuBai']:02d}"
                        f" | MaBaiHoc={row['MaBaiHoc']}"
                        f" | {row['TenCauTruc']}"
                    )

                print("\nTong mau de xuat:", len(plan))
                print("Ngu phap HSK3 hien co:", 20)
                print("Tong du kien sau import:", 32)

                if not args.commit:
                    DATA.mkdir(parents=True, exist_ok=True)

                    PREVIEW_FILE.write_text(
                        json.dumps(
                            {
                                "signature": signature,
                                "count": len(plan),
                            },
                            indent=2,
                        ),
                        encoding="utf-8",
                    )

                    connection.rollback()

                    print("\nPREVIEW THANH CONG")
                    print("CHUA GHI SQL")
                    return

                if not PREVIEW_FILE.exists():
                    raise RuntimeError(
                        "Chua co PREVIEW. "
                        "Hay chay khong co --commit truoc."
                    )

                saved = json.loads(
                    PREVIEW_FILE.read_text(encoding="utf-8")
                )

                if (
                    saved.get("signature") != signature
                    or saved.get("count") != len(plan)
                ):
                    raise RuntimeError(
                        "Ke hoach khac PREVIEW. "
                        "Hay chay PREVIEW lai."
                    )

                print("\nDANG INSERT:")

                for row in plan:
                    new_id = insert_one(cursor, row)

                    print(
                        f"  OK Bai {row['SoThuTuBai']:02d}"
                        f" -> MaNguPhap={new_id}"
                    )

                cursor.execute("""
                    SELECT
                        COUNT(*) AS TongNguPhap,
                        COUNT(DISTINCT np.MaBaiHoc) AS SoBaiCoNguPhap
                    FROM dbo.NguPhap AS np
                    INNER JOIN dbo.BaiHoc AS bh
                        ON bh.MaBaiHoc = np.MaBaiHoc
                    WHERE bh.MaKhoaHoc = ?;
                """, COURSE_ID)

                total, lesson_count = cursor.fetchone()

                if int(total) != 32 or int(lesson_count) != 20:
                    raise RuntimeError(
                        "Kiem tra sau INSERT khong khop: "
                        f"{total} ngu phap, {lesson_count} bai."
                    )

                connection.commit()

                print("\n" + "=" * 68)
                print("COMMIT THANH CONG!")
                print("=" * 68)
                print("Da bo sung:", len(plan))
                print("Tong ngu phap HSK3:", total)
                print("So bai co ngu phap:", lesson_count)
                print("Trang thai: ban_nhap")
                print("CHUA XUAT BAN")

            except Exception:
                connection.rollback()
                raise


if __name__ == "__main__":
    main()

