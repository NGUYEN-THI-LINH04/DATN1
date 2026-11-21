
# -*- coding: utf-8 -*-
"""
MỘC HÁN - HSK1 ĐỀ 4 (H11003)
CÔNG CỤ SỬA VÙNG CẮT TRỰC QUAN

- Hiển thị trang PDF thật.
- Chọn câu hỏi bên trái.
- Kéo chuột khoanh vùng cần giữ.
- Lưu tọa độ vào JSON riêng.
- Xuất lại ảnh và HTML kiểm tra.
- Giữ nguyên ảnh câu 1-5 và 21-25.
- Không sửa SQL hoặc các đề khác.

Cài đặt:
    pip install pymupdf pillow
"""

import json
import tkinter as tk

from html import escape
from pathlib import Path
from tkinter import messagebox, ttk

import fitz
from PIL import Image, ImageTk


# ==================================================
# 1. CẤU HÌNH
# ==================================================

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

PDF_PATH = (
    ROOT / "source" / "De_HSK"
    / "HSK1" / "H11003.pdf"
)

DATA = HERE / "data" / "de_04"
OUTPUT = HERE / "output" / "de_04"

QUESTIONS = OUTPUT / "questions"
GROUPS = OUTPUT / "groups"

ANSWER_PATH = DATA / "de_04_dap_an.json"
FIRST_PATH = DATA / "hinh_cau_hoi_kiem_tra.json"

CROP_CONFIG = DATA / "toa_do_cat_de_04.json"

RESULT_PATH = DATA / "hinh_40_cau_ung_vien.json"

HTML_PATH = OUTPUT / "kiem_tra_40_cau_ung_vien.html"

SCALE_EXPORT = 3.0


# ==================================================
# 2. DANH SÁCH CẦN CẮT
#
# Trang PDF đã đối chiếu từ H11003.pdf.
# Chưa đặt sẵn tọa độ cắt.
# ==================================================

ITEMS = []

for number in range(6, 9):
    ITEMS.append((f"cau_{number:02d}", 3))

for number in range(9, 11):
    ITEMS.append((f"cau_{number:02d}", 4))

ITEMS.append(("nghe_3", 5))

for number in range(16, 21):
    ITEMS.append((f"cau_{number:02d}", 6))

ITEMS.append(("doc_2", 8))

for number in range(26, 31):
    ITEMS.append((f"cau_{number:02d}", 8))

ITEMS.append(("doc_3", 9))

for number in range(31, 36):
    ITEMS.append((f"cau_{number:02d}", 9))

ITEMS.append(("doc_4", 10))

for number in range(36, 41):
    ITEMS.append((f"cau_{number:02d}", 10))


GROUP_KEYS = {
    "nghe_3": range(11, 16),
    "doc_2": range(26, 31),
    "doc_3": range(31, 36),
    "doc_4": range(36, 41),
}


# ==================================================
# 3. HÀM DỮ LIỆU
# ==================================================

def read_json(path):

    if not path.is_file():
        raise FileNotFoundError(str(path))

    return json.loads(
        path.read_text(encoding="utf-8-sig")
    )


def write_json(path, value):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def normalize_answer(value):

    value = str(value).strip().upper()

    return {
        "X": "×",
        "✓": "√",
        "✔": "√",
    }.get(value, value)


def section(number):

    if number <= 20:
        return "nghe", (number - 1) // 5 + 1

    return "doc", (number - 21) // 5 + 1


def question_type(number):

    if number <= 5 or 21 <= number <= 25:
        return "dung_sai"

    if 11 <= number <= 15:
        return "ghep_hinh_theo_audio"

    if 26 <= number <= 30:
        return "ghep_hinh_theo_noi_dung"

    if number >= 31:
        return "ghep_cap"

    return "chon_mot"


def group_for(number):

    for key, numbers in GROUP_KEYS.items():
        if number in numbers:
            return key

    return None


def label_for(key):

    if key in GROUP_KEYS:
        return {
            "nghe_3": "Bảng A-F: Nghe phần 3",
            "doc_2": "Bảng A-F: Đọc phần 2",
            "doc_3": "Bảng A-F: Đọc phần 3",
            "doc_4": "Bảng A-F: Đọc phần 4",
        }[key]

    return f"Câu {int(key.split('_')[1]):02d}"


# ==================================================
# 4. GIAO DIỆN CẮT ẢNH
# ==================================================

class CropEditor:

    def __init__(self, root):

        self.root = root

        root.title(
            "Mộc Hán - Sửa ảnh HSK1 Đề 4"
        )

        root.geometry("1250x850")

        self.document = fitz.open(PDF_PATH)

        if len(self.document) != 10:
            raise ValueError(
                "PDF H11003 phải có 10 trang."
            )

        self.saved = {}

        if CROP_CONFIG.is_file():

            old = read_json(CROP_CONFIG)

            if old.get("ma_de_goc") == "H11003":
                self.saved = old.get("regions", {})

        self.current_index = 0

        self.photo = None

        self.start_point = None

        self.canvas_image_width = 0
        self.canvas_image_height = 0

        self.offset_x = 0
        self.offset_y = 0

        self.build_ui()

        self.root.after(100, self.show_current)


    def build_ui(self):

        wrapper = ttk.Frame(self.root, padding=10)
        wrapper.pack(
            fill="both",
            expand=True
        )

        left = ttk.Frame(wrapper, width=260)
        left.pack(
            side="left",
            fill="y",
            padx=(0, 12)
        )

        ttk.Label(
            left,
            text="HSK1 - Đề 4 (H11003)",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=8)

        ttk.Label(
            left,
            text="Chọn phần cần cắt:",
        ).pack(anchor="w")

        self.listbox = tk.Listbox(
            left,
            width=34,
            height=29,
            font=("Arial", 10)
        )

        self.listbox.pack(
            fill="both",
            expand=True,
            pady=8
        )

        for key, page in ITEMS:

            self.listbox.insert(
                "end",
                f"{label_for(key)} - trang {page}"
            )

        self.listbox.bind(
            "<<ListboxSelect>>",
            self.on_select
        )

        ttk.Button(
            left,
            text="Lưu vùng đang chọn",
            command=self.save_current
        ).pack(fill="x", pady=4)

        ttk.Button(
            left,
            text="Câu / phần tiếp theo",
            command=self.next_item
        ).pack(fill="x", pady=4)

        ttk.Button(
            left,
            text="Xuất toàn bộ ảnh + HTML",
            command=self.export_all
        ).pack(fill="x", pady=12)

        self.status = ttk.Label(
            left,
            text="",
            wraplength=250,
            justify="left"
        )

        self.status.pack(
            anchor="w",
            pady=10
        )

        right = ttk.Frame(wrapper)
        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        ttk.Label(
            right,
            text=(
                "Kéo chuột trên trang PDF để "
                "khoanh đúng nội dung cần giữ."
            ),
            font=("Arial", 11)
        ).pack(anchor="w", pady=6)

        self.canvas = tk.Canvas(
            right,
            bg="#e5e7eb",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self.canvas.bind(
            "<ButtonPress-1>",
            self.mouse_down
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.mouse_move
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self.mouse_up
        )

        self.canvas.bind(
            "<Configure>",
            self.on_resize
        )

        self.listbox.selection_set(0)


    def on_resize(self, event):

        if (
            self.canvas.winfo_width() > 200
            and self.canvas.winfo_height() > 200
        ):
            self.show_current()


    def on_select(self, event):

        selection = self.listbox.curselection()

        if not selection:
            return

        self.current_index = selection[0]

        self.show_current()


    def current_item(self):

        return ITEMS[self.current_index]


    def show_current(self):

        key, page_number = self.current_item()

        page = self.document[page_number - 1]

        available_width = max(
            300,
            self.canvas.winfo_width() - 24
        )

        available_height = max(
            400,
            self.canvas.winfo_height() - 24
        )

        factor = min(
            available_width / page.rect.width,
            available_height / page.rect.height
        )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(
                factor,
                factor
            ),
            colorspace=fitz.csRGB,
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            (pix.width, pix.height),
            pix.samples
        )

        self.photo = ImageTk.PhotoImage(image)

        self.canvas.delete("all")

        self.canvas_image_width = pix.width
        self.canvas_image_height = pix.height

        self.offset_x = (
            self.canvas.winfo_width()
            - pix.width
        ) / 2

        self.offset_y = (
            self.canvas.winfo_height()
            - pix.height
        ) / 2

        self.canvas.create_image(
            self.offset_x,
            self.offset_y,
            anchor="nw",
            image=self.photo
        )

        if key in self.saved:

            region = self.saved[key]["box"]

            self.draw_rectangle(
                self.normalized_to_canvas(region),
                color="#16a34a"
            )

        self.update_status()


    def normalized_to_canvas(self, box):

        x0, y0, x1, y1 = box

        return (
            self.offset_x
            + x0 * self.canvas_image_width,

            self.offset_y
            + y0 * self.canvas_image_height,

            self.offset_x
            + x1 * self.canvas_image_width,

            self.offset_y
            + y1 * self.canvas_image_height
        )


    def canvas_to_normalized(self, box):

        x0, y0, x1, y1 = box

        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))

        width = self.canvas_image_width
        height = self.canvas_image_height

        if width <= 0 or height <= 0:
            raise ValueError(
                "Ảnh PDF chưa được hiển thị."
            )

        values = [
            (x0 - self.offset_x) / width,
            (y0 - self.offset_y) / height,
            (x1 - self.offset_x) / width,
            (y1 - self.offset_y) / height,
        ]

        values = [
            max(0.0, min(1.0, value))
            for value in values
        ]

        if (
            values[2] - values[0] < 0.015
            or values[3] - values[1] < 0.01
        ):
            raise ValueError(
                "Vùng cắt quá nhỏ."
            )

        return [
            round(value, 6)
            for value in values
        ]


    def draw_rectangle(
        self,
        box,
        color="#dc2626"
    ):

        self.canvas.delete("crop_box")

        self.canvas.create_rectangle(
            *box,
            outline=color,
            width=3,
            tags="crop_box"
        )


    def mouse_down(self, event):

        self.start_point = (
            event.x,
            event.y
        )


    def mouse_move(self, event):

        if self.start_point is None:
            return

        self.draw_rectangle(
            (
                self.start_point[0],
                self.start_point[1],
                event.x,
                event.y
            )
        )


    def mouse_up(self, event):

        if self.start_point is None:
            return

        box = (
            self.start_point[0],
            self.start_point[1],
            event.x,
            event.y
        )

        self.start_point = None

        try:

            normalized = (
                self.canvas_to_normalized(box)
            )

        except ValueError as error:

            messagebox.showwarning(
                "Vùng cắt",
                str(error)
            )

            return

        key, page_number = self.current_item()

        self.saved[key] = {
            "page": page_number,
            "box": normalized
        }

        self.draw_rectangle(
            self.normalized_to_canvas(
                normalized
            ),
            color="#16a34a"
        )

        self.persist()

        self.update_status()


    def persist(self):

        write_json(
            CROP_CONFIG,
            {
                "ma_de_goc": "H11003",
                "ten_de": "Đề 4",
                "regions": self.saved
            }
        )


    def save_current(self):

        key, _ = self.current_item()

        if key not in self.saved:

            messagebox.showwarning(
                "Chưa cắt",
                "Hãy kéo chuột khoanh vùng trước."
            )

            return

        self.persist()

        messagebox.showinfo(
            "Đã lưu",
            f"Đã lưu vùng cắt: {label_for(key)}"
        )


    def next_item(self):

        if self.current_index + 1 >= len(ITEMS):
            return

        self.current_index += 1

        self.listbox.selection_clear(
            0,
            "end"
        )

        self.listbox.selection_set(
            self.current_index
        )

        self.listbox.see(
            self.current_index
        )

        self.show_current()


    def update_status(self):

        key, page = self.current_item()

        done = sum(
            item_key in self.saved
            for item_key, _ in ITEMS
        )

        self.status.configure(
            text=(
                f"Đang chọn: {label_for(key)}\n"
                f"Trang PDF: {page}\n"
                f"Đã khoanh: {done}/{len(ITEMS)}\n\n"
                "Khung xanh = đã lưu.\n"
                "Muốn sửa: kéo lại khung mới.\n\n"
                "Mỗi lần kéo sẽ tự lưu tọa độ."
            )
        )


    # ==============================================
    # 5. XUẤT ẢNH
    # ==============================================

    def export_crop(
        self,
        key,
        destination
    ):

        region = self.saved[key]

        page_number = region["page"]

        page = self.document[
            page_number - 1
        ]

        x0, y0, x1, y1 = region["box"]

        rect = fitz.Rect(
            x0 * page.rect.width,
            y0 * page.rect.height,
            x1 * page.rect.width,
            y1 * page.rect.height
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(
                SCALE_EXPORT,
                SCALE_EXPORT
            ),
            clip=rect,
            colorspace=fitz.csRGB,
            alpha=False
        )

        pix.save(str(destination))

        return [
            round(float(v), 2)
            for v in rect
        ]


    def export_all(self):

        missing = [
            label_for(key)
            for key, _ in ITEMS
            if key not in self.saved
        ]

        if missing:

            messagebox.showwarning(
                "Chưa đủ vùng cắt",
                "Cần khoanh đủ các vùng:\n\n"
                + "\n".join(missing[:12])
                + (
                    "\n..."
                    if len(missing) > 12
                    else ""
                )
            )

            return

        try:

            self.persist()

            self.generate_output()

        except Exception as error:

            messagebox.showerror(
                "Lỗi xuất ảnh",
                str(error)
            )

            return

        messagebox.showinfo(
            "Hoàn thành",
            "Đã xuất ảnh và HTML kiểm tra.\n\n"
            f"{HTML_PATH}"
        )


    def generate_output(self):

        answer_data = read_json(
            ANSWER_PATH
        )

        if answer_data.get("ma_de_goc") != "H11003":
            raise ValueError(
                "Sai mã đề trong JSON đáp án."
            )

        answers = {
            int(k): normalize_answer(v)
            for k, v in
            answer_data["dap_an"].items()
        }

        if set(answers) != set(range(1, 41)):
            raise ValueError(
                "Chưa đủ 40 đáp án."
            )

        first_data = read_json(
            FIRST_PATH
        )

        if first_data.get("ma_de_goc") != "H11003":
            raise ValueError(
                "Sai mã đề trong 10 câu đầu."
            )

        first_items = first_data["cau_hoi"]

        first_numbers = [
            int(item["so_cau"])
            for item in first_items
        ]

        if (
            len(first_items) != 10
            or set(first_numbers) != (
                set(range(1, 6))
                | set(range(21, 26))
            )
        ):
            raise ValueError(
                "10 câu đầu không hợp lệ."
            )

        QUESTIONS.mkdir(
            parents=True,
            exist_ok=True
        )

        GROUPS.mkdir(
            parents=True,
            exist_ok=True
        )

        rows = []

        # Giữ nguyên 10 câu đã đúng.
        for item in first_items:

            number = int(item["so_cau"])

            skill, part = section(number)

            relative = (
                f"questions/cau_{number:02d}.png"
            )

            if not (OUTPUT / relative).is_file():
                raise FileNotFoundError(
                    f"Thiếu ảnh câu {number}"
                )

            if normalize_answer(
                item["dap_an_goc"]
            ) != answers[number]:
                raise ValueError(
                    f"Đáp án câu {number} không khớp."
                )

            rows.append({
                "so_cau": number,
                "ky_nang": skill,
                "phan": part,
                "loai_cau_hoi": question_type(number),
                "trang_pdf": item["trang_pdf"],
                "anh_cau_hoi": relative,
                "anh_nhom_lua_chon": None,
                "dap_an_goc": answers[number],
                "vung_cat_pdf": item.get(
                    "vung_cat_pdf"
                ),
                "da_kiem_tra_hinh": False,
            })

        # Xuất bảng chung.
        for key in GROUP_KEYS:

            self.export_crop(
                key,
                GROUPS / f"{key}.png"
            )

        # Xuất 25 ảnh riêng còn lại.
        numbers_to_export = (
            list(range(6, 11))
            + list(range(16, 21))
            + list(range(26, 41))
        )

        for number in numbers_to_export:

            key = f"cau_{number:02d}"

            crop_rect = self.export_crop(
                key,
                QUESTIONS / f"{key}.png"
            )

            skill, part = section(number)

            group = group_for(number)

            rows.append({
                "so_cau": number,
                "ky_nang": skill,
                "phan": part,
                "loai_cau_hoi": question_type(number),
                "trang_pdf": self.saved[key]["page"],
                "anh_cau_hoi": (
                    f"questions/{key}.png"
                ),
                "anh_nhom_lua_chon": (
                    f"groups/{group}.png"
                    if group else None
                ),
                "dap_an_goc": answers[number],
                "vung_cat_pdf": crop_rect,
                "da_kiem_tra_hinh": False,
            })

        # Câu 11-15 chỉ có bảng chung.
        for number in range(11, 16):

            skill, part = section(number)

            rows.append({
                "so_cau": number,
                "ky_nang": skill,
                "phan": part,
                "loai_cau_hoi": question_type(number),
                "trang_pdf": 5,
                "anh_cau_hoi": None,
                "anh_nhom_lua_chon": (
                    "groups/nghe_3.png"
                ),
                "dap_an_goc": answers[number],
                "vung_cat_pdf": None,
                "da_kiem_tra_hinh": False,
            })

        rows.sort(
            key=lambda item: item["so_cau"]
        )

        if (
            len(rows) != 40
            or [
                item["so_cau"]
                for item in rows
            ] != list(range(1, 41))
        ):
            raise ValueError(
                "Kết quả không đủ 40 câu liên tục."
            )

        write_json(
            RESULT_PATH,
            {
                "ma_de_goc": "H11003",
                "cap_hsk": 1,
                "ten_hien_thi": "Đề 4",
                "so_cau": 40,
                "trang_thai": "cho_kiem_tra_hinh",
                "cau_hoi": rows
            }
        )

        create_html(rows)


# ==================================================
# 6. TẠO HTML KIỂM TRA
# ==================================================

def create_html(rows):

    sections = [
        ("nghe", 1, "Nghe hiểu - Phần 1"),
        ("nghe", 2, "Nghe hiểu - Phần 2"),
        ("nghe", 3, "Nghe hiểu - Phần 3"),
        ("nghe", 4, "Nghe hiểu - Phần 4"),
        ("doc", 1, "Đọc hiểu - Phần 1"),
        ("doc", 2, "Đọc hiểu - Phần 2"),
        ("doc", 3, "Đọc hiểu - Phần 3"),
        ("doc", 4, "Đọc hiểu - Phần 4"),
    ]

    html = [
        "<!DOCTYPE html>",
        '<html lang="vi">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" '
        'content="width=device-width,initial-scale=1">',
        "<title>HSK1 Đề 4 - Kiểm tra ảnh</title>",
        "<style>",
        "*{box-sizing:border-box}",
        "body{font-family:Arial,sans-serif;"
        "background:#f3f5f9;margin:0;padding:14px}",
        "main{max-width:1050px;margin:auto}",
        "section{background:white;padding:15px;"
        "border-radius:10px;margin-bottom:15px}",
        "h2{font-size:17px}",
        ".grid{display:grid;"
        "grid-template-columns:repeat(2,minmax(0,1fr));"
        "gap:10px}",
        ".card,.group{border:1px solid #d6dce6;"
        "border-radius:7px;padding:10px;min-width:0}",
        ".card strong{font-size:12px;color:#1653a5}",
        "img{display:block;max-width:100%;height:auto;"
        "max-height:450px;object-fit:contain;margin-top:7px}",
        ".group{margin-bottom:10px}",
        ".group img{max-height:650px}",
        ".hint{font-size:12px;color:#666}",
        "@media(max-width:700px){"
        ".grid{grid-template-columns:1fr}}",
        "</style>",
        "</head><body><main>",
        "<h1>HSK1 - Đề 4 (H11003)</h1>",
        "<p>Ảnh được cắt theo các vùng đã chọn "
        "trên PDF gốc. Chưa nhập SQL.</p>",
    ]

    for skill, part, title in sections:

        items = [
            item for item in rows
            if item["ky_nang"] == skill
            and item["phan"] == part
        ]

        html.append(
            f"<section><h2>{escape(title)}</h2>"
        )

        group = items[0].get(
            "anh_nhom_lua_chon"
        )

        if group:

            html.append(
                '<div class="group">'
                "<strong>Bảng lựa chọn chung</strong>"
                f'<img src="{escape(group, quote=True)}">'
                "</div>"
            )

        html.append('<div class="grid">')

        for item in items:

            number = item["so_cau"]

            html.append(
                '<div class="card">'
                f"<strong>Câu {number:02d}</strong>"
            )

            relative = item.get(
                "anh_cau_hoi"
            )

            if relative:

                html.append(
                    f'<img src="{escape(relative, quote=True)}" '
                    f'alt="Câu {number}">'
                )

            else:

                html.append(
                    '<p class="hint">'
                    "Dùng bảng lựa chọn chung phía trên."
                    "</p>"
                )

            html.append("</div>")

        html.append("</div></section>")

    html.append("</main></body></html>")

    HTML_PATH.write_text(
        "\n".join(html),
        encoding="utf-8"
    )


# ==================================================
# 7. CHẠY
# ==================================================

def main():

    if not PDF_PATH.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy PDF:\n{PDF_PATH}"
        )

    DATA.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.mkdir(
        parents=True,
        exist_ok=True
    )

    root = tk.Tk()

    editor = CropEditor(root)

    root.mainloop()

    editor.document.close()


if __name__ == "__main__":
    main()
