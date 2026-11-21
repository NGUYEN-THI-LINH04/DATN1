
from pathlib import Path
from html import escape
import json
import webbrowser

BASE = Path(r"D:\DATN1\scripts\shadowing\hsk2")
DATA = BASE / "data" / "processed"

SOURCE = DATA / "video_chabuduo_review_v3.json"
OUTPUT = DATA / "video_chabuduo_review.html"

data = json.loads(
    SOURCE.read_text(encoding="utf-8")
)

sentences = data["sentences"]
video_id = data["youtube_id"]

rows = []

for i, s in enumerate(sentences, 1):
    start = float(s["start"])
    end = float(s["end"])

    youtube_url = (
        f"https://www.youtube.com/watch?v={video_id}"
        f"&t={int(start)}s"
    )

    rows.append(f"""
    <tr>
        <td>{i}</td>
        <td>{start:.2f} - {end:.2f}s</td>
        <td>
            <div class="hanzi">{escape(s["hanzi"])}</div>
            <div class="pinyin">{escape(s["pinyin"])}</div>
            <div class="vi">{escape(s["vi"])}</div>
        </td>
        <td>
            <a href="{escape(youtube_url)}"
               target="_blank">
               ▶ Nghe
            </a>
        </td>
    </tr>
    """)

html_content = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Kiểm tra Shadowing - 差不多</title>
<style>
body {
    font-family: Arial, sans-serif;
    margin: 30px;
    background: #f7f8fa;
    color: #222;
}
h1 { color: #245b4b; }
table {
    border-collapse: collapse;
    width: 100%;
    background: white;
}
th, td {
    border: 1px solid #ddd;
    padding: 14px;
    text-align: left;
    vertical-align: top;
}
th { background: #e3eee9; }
.hanzi {
    font-size: 23px;
    margin-bottom: 6px;
}
.pinyin {
    color: #b15d27;
    margin-bottom: 5px;
}
.vi { color: #555; }
a {
    color: #146c43;
    font-weight: bold;
    text-decoration: none;
}
tr:hover { background: #f0f7f3; }
</style>
</head>
<body>
<h1>Kiểm tra Shadowing: 差不多</h1>
<p>36 câu dự thảo - cần đối chiếu với âm thanh gốc.</p>
<table>
<thead>
<tr>
<th>STT</th>
<th>Thời gian</th>
<th>Nội dung</th>
<th>Video</th>
</tr>
</thead>
<tbody>
""" + "\n".join(rows) + """
</tbody>
</table>
</body>
</html>
"""

OUTPUT.write_text(
    html_content,
    encoding="utf-8"
)

print("Da tao trang kiem tra:")
print(OUTPUT)
print("Tong so cau:", len(sentences))
print("Chua cap nhat SQL Server.")

webbrowser.open(OUTPUT.as_uri())
