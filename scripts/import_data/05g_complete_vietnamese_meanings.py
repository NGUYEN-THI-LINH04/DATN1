from pathlib import Path
import csv


# =========================================================
# THƯ MỤC
# =========================================================
ROOT_DIR = Path(__file__).resolve().parents[2]

HSK_DIR = (
    ROOT_DIR
    / "data_sources"
    / "hsk"
)


# =========================================================
# FILE
# =========================================================
INPUT_FILE = (
    HSK_DIR
    / "hsk1_4_vietnamese_review.csv"
)

OUTPUT_FILE = (
    HSK_DIR
    / "hsk1_4_vietnamese_source_complete.csv"
)

MANUAL_FILLED_FILE = (
    HSK_DIR
    / "hsk1_4_manual_filled.csv"
)


# =========================================================
# 9 MỤC KHÔNG CÓ NGHĨA TRONG CVDICT
#
# Đây là nghĩa bổ sung thủ công ĐỀ XUẤT.
# Không gán nguồn CVDICT.
# Chưa coi là đã kiểm duyệt.
# =========================================================
MANUAL_MEANINGS = {

    "L1-0044": {
        "word": "车上",
        "meaning": "trên xe; ở trong xe",
    },

    "L2-0034": {
        "word": "不太",
        "meaning": "không lắm; không quá",
    },

    "L2-0044": {
        "word": "不一会儿",
        "meaning": "chẳng bao lâu; một lát sau",
    },

    "L2-0264": {
        "word": "见过",
        "meaning": "đã từng gặp; đã từng thấy",
    },

    "L2-0507": {
        "word": "送到",
        "meaning": "đưa đến; giao đến; chuyển đến",
    },

    "L3-0192": {
        "word": "放到",
        "meaning": "đặt vào; để vào một vị trí",
    },

    "L3-0508": {
        "word": "能不能",
        "meaning": "có thể hay không; có ... được không",
    },

    "L4-0853": {
        "word": "眼里",
        "meaning": (
            "trong mắt; theo cách nhìn "
            "hoặc quan niệm của ai đó"
        ),
    },

    "L4-0897": {
        "word": "有劲儿",
        "meaning": (
            "có sức; có năng lượng; "
            "thú vị, hấp dẫn"
        ),
    },
}


# =========================================================
# MỤC FALLBACK CVDICT
#
# 中医 đã có nghĩa Việt trong CVDICT.
# Chỉ xác nhận việc ghép mapping.
# Không thay nghĩa bằng dữ liệu tự tạo.
# =========================================================
CVDICT_FALLBACK_CONFIRM = {
    "L2-0739",
}


# =========================================================
# ĐỌC CSV
# =========================================================
def read_csv(path):

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(
            file
        )

        rows = list(reader)

        fields = list(
            reader.fieldnames
            or []
        )

    return rows, fields


# =========================================================
# MAIN
# =========================================================
def main():

    print("=" * 72)
    print(
        "HOAN THIEN NGHIA TIENG VIET "
        "CHO 3245 MUC HSK 1-4"
    )
    print("=" * 72)

    # -----------------------------------------------------
    # Kiểm tra file
    # -----------------------------------------------------
    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Khong tim thay file:\n"
            f"{INPUT_FILE}\n\n"
            "Hay chay 05f truoc."
        )

    # -----------------------------------------------------
    # Đọc dữ liệu
    # -----------------------------------------------------
    rows, fieldnames = read_csv(
        INPUT_FILE
    )

    print(
        f"So muc dau vao: "
        f"{len(rows)}"
    )

    if len(rows) != 3245:

        raise RuntimeError(
            "File dau vao khong co "
            "dung 3245 muc."
        )

    # -----------------------------------------------------
    # Cột bổ sung
    # -----------------------------------------------------
    extra_fields = [
        "LoaiNghiaTiengViet",
        "GhiChuNghiaTiengViet",
    ]

    for field in extra_fields:

        if field not in fieldnames:
            fieldnames.append(
                field
            )

    # -----------------------------------------------------
    # Thống kê
    # -----------------------------------------------------
    manual_filled = []
    cvdict_confirmed = []

    unknown_manual_ids = []

    processed_manual_ids = set()

    # -----------------------------------------------------
    # Xử lý
    # -----------------------------------------------------
    for row in rows:

        item_id = (
            row.get("ID")
            or ""
        ).strip()

        # =================================================
        # 1. 9 TỪ KHÔNG CÓ TRONG CVDICT
        # =================================================
        if item_id in MANUAL_MEANINGS:

            fix = MANUAL_MEANINGS[
                item_id
            ]

            # Kiểm tra tránh sửa nhầm dòng
            actual_word = (
                row.get(
                    "TuChinh",
                    "",
                )
                .strip()
            )

            expected_word = (
                fix["word"]
            )

            if (
                actual_word
                != expected_word
            ):

                raise RuntimeError(
                    "ID "
                    f"{item_id} "
                    "khong dung tu mong doi. "
                    f"File dang co '{actual_word}', "
                    f"mong doi '{expected_word}'."
                )

            # ---------------------------------------------
            # Gán nghĩa Việt đề xuất
            # ---------------------------------------------
            row[
                "NghiaTiengViet"
            ] = fix[
                "meaning"
            ]

            # ---------------------------------------------
            # Không được ghi CVDICT là nguồn
            # vì CVDICT không tìm thấy từ này.
            # ---------------------------------------------
            row[
                "MaNguonNghiaViet"
            ] = ""

            row[
                "NguonNghiaViet"
            ] = ""

            row[
                "TuCvdictKhop"
            ] = ""

            row[
                "PinyinCvdictKhop"
            ] = ""

            row[
                "TrangThaiNghiaViet"
            ] = (
                "bo_sung_thu_cong"
            )

            # Vẫn cần người quản trị kiểm tra
            row[
                "CanKiemTraNghia"
            ] = "1"

            row[
                "LoaiNghiaTiengViet"
            ] = (
                "de_xuat_thu_cong"
            )

            row[
                "GhiChuNghiaTiengViet"
            ] = (
                "Muc HSK khong co entry "
                "tuong ung trong CVDICT; "
                "nghia Viet duoc bo sung "
                "de xuat va chua duoc duyet."
            )

            # TUYỆT ĐỐI chưa duyệt
            row[
                "DaDuyet"
            ] = "0"

            manual_filled.append(
                row.copy()
            )

            processed_manual_ids.add(
                item_id
            )

            continue

        # =================================================
        # 2. 中医 - FALLBACK CVDICT
        # =================================================
        if (
            item_id
            in CVDICT_FALLBACK_CONFIRM
        ):

            meaning = (
                row.get(
                    "NghiaTiengViet",
                    "",
                )
                .strip()
            )

            if not meaning:

                raise RuntimeError(
                    "Muc Trung y khong co "
                    "nghia Viet CVDICT."
                )

            row[
                "TrangThaiNghiaViet"
            ] = (
                "cvdict_fallback_xac_nhan"
            )

            # Mapping đã được xác định,
            # nhưng nghĩa vẫn chưa phải dữ liệu
            # đã được Admin duyệt.
            row[
                "CanKiemTraNghia"
            ] = "0"

            row[
                "LoaiNghiaTiengViet"
            ] = (
                "nguon_cvdict"
            )

            row[
                "GhiChuNghiaTiengViet"
            ] = (
                "Nghia Viet co trong CVDICT; "
                "entry duoc tim bang fallback "
                "theo tu thay vi CEDICTKey."
            )

            row[
                "DaDuyet"
            ] = "0"

            cvdict_confirmed.append(
                row.copy()
            )

            processed_manual_ids.add(
                item_id
            )

            continue

        # =================================================
        # 3. CÁC MỤC CVDICT KHỚP CHÍNH XÁC
        # =================================================
        status = (
            row.get(
                "TrangThaiNghiaViet",
                "",
            )
            .strip()
        )

        if (
            status
            == "cvdict_khop_chinh_xac"
        ):

            row[
                "LoaiNghiaTiengViet"
            ] = (
                "nguon_cvdict"
            )

            row[
                "GhiChuNghiaTiengViet"
            ] = (
                "Nghia tu dien nguon CVDICT; "
                "chua duoc chuan hoa thanh "
                "nghia hoc tap."
            )

        else:

            # Không tự sửa những trạng thái
            # mà script chưa biết.
            row[
                "LoaiNghiaTiengViet"
            ] = (
                row.get(
                    "LoaiNghiaTiengViet",
                    "",
                )
            )

            row[
                "GhiChuNghiaTiengViet"
            ] = (
                row.get(
                    "GhiChuNghiaTiengViet",
                    "",
                )
            )

        # Mọi mục vẫn chưa duyệt
        row[
            "DaDuyet"
        ] = "0"

    # -----------------------------------------------------
    # Kiểm tra đủ 10 ID manual
    # -----------------------------------------------------
    expected_manual_ids = (
        set(
            MANUAL_MEANINGS.keys()
        )
        | CVDICT_FALLBACK_CONFIRM
    )

    missing_ids = (
        expected_manual_ids
        - processed_manual_ids
    )

    if missing_ids:

        raise RuntimeError(
            "Khong tim thay cac ID manual: "
            + ", ".join(
                sorted(missing_ids)
            )
        )

    # -----------------------------------------------------
    # Kiểm tra nghĩa trống
    # -----------------------------------------------------
    empty_meanings = []

    for row in rows:

        meaning = (
            row.get(
                "NghiaTiengViet",
                "",
            )
            .strip()
        )

        if not meaning:

            empty_meanings.append(
                (
                    row.get("ID", ""),
                    row.get(
                        "TuChinh",
                        "",
                    ),
                )
            )

    # -----------------------------------------------------
    # Kiểm tra DaDuyet
    # -----------------------------------------------------
    approved_count = sum(
        1
        for row in rows
        if (
            row.get(
                "DaDuyet",
                "",
            )
            .strip()
            == "1"
        )
    )

    # -----------------------------------------------------
    # GHI FILE ĐẦY ĐỦ
    # -----------------------------------------------------
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    # -----------------------------------------------------
    # GHI RIÊNG 10 MỤC
    # -----------------------------------------------------
    manual_output = (
        manual_filled
        + cvdict_confirmed
    )

    manual_output.sort(
        key=lambda x: (
            int(
                x.get(
                    "CapDoHSK",
                    "0",
                )
                or 0
            ),
            x.get(
                "ID",
                "",
            ),
        )
    )

    with open(
        MANUAL_FILLED_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        writer.writerows(
            manual_output
        )

    # -----------------------------------------------------
    # KẾT QUẢ
    # -----------------------------------------------------
    print()
    print("-" * 72)
    print("KET QUA")
    print("-" * 72)

    print(
        "Tong HSK 1-4: "
        f"{len(rows)}"
    )

    print(
        "Bo sung nghia thu cong: "
        f"{len(manual_filled)}"
    )

    print(
        "Fallback CVDICT da xac nhan: "
        f"{len(cvdict_confirmed)}"
    )

    print(
        "So muc con trong nghia Viet: "
        f"{len(empty_meanings)}"
    )

    print(
        "So muc DaDuyet = 1: "
        f"{approved_count}"
    )

    print()

    print(
        "File day du:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    print(
        "10 muc da xu ly:"
    )

    print(
        MANUAL_FILLED_FILE
    )

    # -----------------------------------------------------
    # Nếu còn nghĩa trống thì cảnh báo
    # -----------------------------------------------------
    if empty_meanings:

        print()
        print(
            "CANH BAO: "
            "Van con muc chua co nghia:"
        )

        for item_id, word in (
            empty_meanings[:20]
        ):

            print(
                f"- {item_id}: {word}"
            )

    else:

        print()
        print(
            "DA CO NGHIA TIENG VIET "
            "CHO DU 3245 MUC."
        )

    print()
    print(
        "LUU Y:"
    )

    print(
        "Day van la file NGHIA NGUON / "
        "DE XUAT."
    )

    print(
        "Chua phai nghia hoc tap "
        "cuoi cung de hien thi cho hoc vien."
    )

    print(
        "CHUA INSERT VAO TuVung."
    )

    print()
    print("=" * 72)
    print("HOAN TAT")
    print("=" * 72)


if __name__ == "__main__":
    main()