import fitz
import re
from pathlib import Path

pdf = Path(
    r"D:\DATN1\scripts\luyen_thi\source\De_HSK\HSK1\H11007.pdf"
)

with fitz.open(pdf) as doc:
    print("===== TOA DO CAU 26-35 =====")

    for page_no, page in enumerate(doc, 1):
        found = []

        for w in page.get_text("words"):
            x0, y0, x1, y1, word = w[:5]
            word = str(word).strip().replace("．", ".")

            m = re.fullmatch(
                r"(2[6-9]|30|3[1-5])\.?",
                word
            )

            if not m or x0 > 220:
                continue

            if y0 < 145:
                continue

            found.append(
                (int(m.group(1)), x0, y0, x1, y1)
            )

        if found:
            print(f"\nTRANG PDF {page_no}")
            print(f"Kich thuoc: {page.rect.width:.1f} x {page.rect.height:.1f}")

            for q, x0, y0, x1, y1 in sorted(
                found, key=lambda x: x[2]
            ):
                print(
                    f"Cau {q:02d}: "
                    f"x={x0:.1f}, "
                    f"y={y0:.1f}-{y1:.1f}"
                )

print("\n===== CAC FILE ANH HIEN CO =====")

out = Path(
    r"D:\DATN1\scripts\luyen_thi\hsk1\output\de_07"
)

for p in out.rglob("*.png"):
    if re.search(
        r"(?:^|[_-])0?(?:2[6-9]|30|3[1-5])(?:$|[_-])",
        p.stem.lower()
    ):
        print(p.relative_to(out))
