
# -*- coding: utf-8 -*-

"""
MOC HAN - HSK3 DE 10 (H31328)

SUA HTML XEM TRUOC 80 CAU.

- Cau 1-5: mot bang hinh A-F.
- Cau 6-10: mot bang hinh A-E.
- Hien thi cac o so cau ben duoi bang.
- Cau 11-80: hien thi anh cau hoi.
- Cau 41-60: hien bang lua chon chung.
- KHONG hien thi dap an.
- KHONG tao lai anh.
- KHONG sua JSON, MP3, SQL Server.
"""

from pathlib import Path
import shutil


# =====================================================
# 1. DUONG DAN
# =====================================================

ROOT = Path(r"D:\DATN1")

OUTPUT = (
    ROOT / "scripts"
    / "luyen_thi"
    / "hsk3"
    / "output"
    / "de_10"
)

HTML_FILE = OUTPUT / "kiem_tra_80_cau.html"

BACKUP_FILE = OUTPUT / "kiem_tra_80_cau.html.bak"


# =====================================================
# 2. CAU HINH BANG LUA CHON
# =====================================================

SHARED_GROUPS = {
    "nghe_01_05": (1, 5),
    "nghe_06_10": (6, 10),

    "doc_41_45": (41, 45),
    "doc_46_50": (46, 50),

    "doc_51_55": (51, 55),
    "doc_56_60": (56, 60),
}


# =====================================================
# 3. KIEM TRA ANH DA TACH
# =====================================================

def check_images():

    missing = []

    # 6 bang lua chon.
    for name in SHARED_GROUPS:

        path = (
            OUTPUT / "groups"
            / f"{name}.png"
        )

        if (
            not path.is_file()
            or path.stat().st_size == 0
        ):
            missing.append(str(path))

    # 70 anh cau hoi.
    for number in range(11, 81):

        path = (
            OUTPUT / "questions"
            / f"cau_{number:02d}.png"
        )

        if (
            not path.is_file()
            or path.stat().st_size == 0
        ):
            missing.append(str(path))

    if missing:

        raise RuntimeError(
            "Con thieu anh:\n"
            + "\n".join(missing)
        )

    print("Anh cau hoi: 70/70")
    print("Bang lua chon: 6/6")


# =====================================================
# 4. TAO BANG HINH CHUNG
# =====================================================

def shared_group(name):

    first, last = SHARED_GROUPS[name]

    buttons = ""

    for number in range(first, last + 1):

        buttons += (
            '<button type="button" '
            'class="number-btn" '
            f'onclick="chonCau(this,{number})">'
            f'Câu {number}'
            '</button>'
        )

    return f"""
<section class="group-card">

    <h3>Câu {first}–{last}</h3>

    <div class="group-image">
        <img
            src="groups/{name}.png"
            alt="Bảng hình câu {first}-{last}"
        >
    </div>

    <div class="number-buttons">
        {buttons}
    </div>

</section>
"""


# =====================================================
# 5. TAO KHUNG ANH CAU HOI
# =====================================================

def question_card(number):

    filename = f"cau_{number:02d}.png"

    return f"""
<section class="question-card" id="cau-{number}">

    <h3>Câu {number}</h3>

    <img
        src="questions/{filename}"
        alt="Nội dung câu {number}"
    >

</section>
"""


# =====================================================
# 6. TAO NOI DUNG 80 CAU
# =====================================================

def build_content():

    parts = []

    # ================================================
    # PHAN 1: NGHE
    # ================================================

    parts.append(
        '<h2>I. Nghe – Câu 1–40</h2>'
    )

    # Cau 1-5 dung chung mot bang.
    parts.append(
        shared_group("nghe_01_05")
    )

    # Cau 6-10 dung chung mot bang.
    parts.append(
        shared_group("nghe_06_10")
    )

    # Cau 11-40 co anh rieng.
    for number in range(11, 41):

        parts.append(
            question_card(number)
        )

    # ================================================
    # PHAN 2: DOC
    # ================================================

    parts.append(
        '<h2>II. Đọc – Câu 41–70</h2>'
    )

    # Cau 41-60 co bang lua chon chung.
    reading_groups = [
        "doc_41_45",
        "doc_46_50",
        "doc_51_55",
        "doc_56_60",
    ]

    for name in reading_groups:

        first, last = SHARED_GROUPS[name]

        parts.append(
            shared_group(name)
        )

        # Moi cau van giu anh rieng.
        for number in range(first, last + 1):

            parts.append(
                question_card(number)
            )

    # Cau 61-70.
    for number in range(61, 71):

        parts.append(
            question_card(number)
        )

    # ================================================
    # PHAN 3: VIET
    # ================================================

    parts.append(
        '<h2>III. Viết – Câu 71–80</h2>'
    )

    for number in range(71, 81):

        parts.append(
            question_card(number)
        )

    return "\n".join(parts)


# =====================================================
# 7. TAO HTML HOAN CHINH
# =====================================================

def build_html():

    content = build_content()

    template = """
<!DOCTYPE html>
<html lang="vi">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
HSK3 Đề 10 – Kiểm tra 80 câu
</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px;
    background: #f3f5fa;
    color: #172b4d;
    font-family: Arial, sans-serif;
}

.container {
    max-width: 1020px;
    margin: 0 auto;
}

h1 {
    font-size: 25px;
    margin-bottom: 12px;
}

h2 {
    font-size: 21px;
    margin: 30px 0 18px;
    padding-bottom: 12px;
    border-bottom: 2px solid #dbe3ef;
}

h3 {
    font-size: 20px;
    margin: 0 0 18px;
}

.note {
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 22px;
}

/* ============================================
   BANG HINH DUNG CHUNG
   ============================================ */

.group-card {
    background: #fff;
    border: 1px solid #dce4ef;
    border-radius: 14px;
    padding: 20px;
    margin: 18px 0;
}

.group-image {
    width: 100%;
    text-align: center;
}

.group-image img {
    display: block;
    width: 100%;
    max-width: 820px;
    height: auto;
    margin: 0 auto;
    object-fit: contain;
}

/* ============================================
   CAC O SO CAU
   ============================================ */

.number-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 22px;
}

.number-btn {
    padding: 13px 18px;
    min-width: 95px;

    background: #fff;
    color: #172b4d;

    border: 1px solid #c9d5e6;
    border-radius: 9px;

    font-family: inherit;
    font-size: 17px;
    font-weight: 500;

    cursor: pointer;

    transition: 0.15s;
}

.number-btn:hover {
    background: #eef5ff;
    border-color: #91b2e5;
}

.number-btn.active {
    background: #e8f1ff;
    border-color: #4387dc;
    color: #185da9;
}

/* ============================================
   ANH CAU 11-80
   ============================================ */

.question-card {
    background: #fff;

    border: 1px solid #dce4ef;
    border-radius: 12px;

    padding: 20px;
    margin: 16px 0;

    scroll-margin-top: 24px;
}

.question-card img {
    display: block;
    max-width: 100%;
    height: auto;
    object-fit: contain;
}

@media (max-width: 600px) {
    body {
        padding: 12px;
    }

    .group-card,
    .question-card {
        padding: 14px;
    }

    .number-btn {
        min-width: 75px;
        padding: 11px;
        font-size: 15px;
    }
}

</style>

</head>

<body>

<main class="container">

<h1>HSK3 – Đề 10 (H31328)</h1>

<p class="note">
Kiểm tra hình ảnh của 80 câu.
Các bảng hình dùng chung chỉ hiển thị một lần.
Không hiển thị đáp án.
</p>

__CONTENT__

</main>

<script>

function chonCau(button, number) {

    const container = button.closest(
        ".number-buttons"
    );

    container.querySelectorAll(
        ".number-btn"
    ).forEach(function(item) {
        item.classList.remove("active");
    });

    button.classList.add("active");

    // Cau 41-60 co anh cau hoi rieng.
    // Bam so cau se chuyen den anh tuong ung.
    const target = document.getElementById(
        "cau-" + number
    );

    if (target) {
        target.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}

</script>

</body>
</html>
"""

    return template.replace(
        "__CONTENT__",
        content
    )


# =====================================================
# 8. CHUONG TRINH CHINH
# =====================================================

def main():

    print("=" * 60)

    print("MOC HAN - SUA HTML HSK3 DE 10")

    print("=" * 60)

    # Kiem tra du anh truoc khi sua HTML.
    check_images()

    new_html = build_html()

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True
    )

    # Sao luu HTML cu mot lan.
    if (
        HTML_FILE.exists()
        and not BACKUP_FILE.exists()
    ):

        shutil.copy2(
            HTML_FILE,
            BACKUP_FILE
        )

        print("Da sao luu HTML cu.")

    # Chi thay noi dung file HTML xem truoc.
    HTML_FILE.write_text(
        new_html,
        encoding="utf-8"
    )

    print("\nHOAN THANH SUA HTML")

    print("Cau 1-5: 1 bang chung + 5 nut")
    print("Cau 6-10: 1 bang chung + 5 nut")

    print("Cau 11-80: 70 anh")
    print("Bang Doc: 4 bang chung")

    print("Khong co nut Xem dap an")
    print("Khong dua dap an vao HTML")

    print(f"\nHTML: {HTML_FILE}")

    print("\nKhong thay doi JSON.")
    print("Khong thay doi SQL Server.")


if __name__ == "__main__":
    main()
