
/* ===========================================================
   MỘC HÁN - LUYỆN THI HSK

   JavaScript cho:
   - Chọn cấp HSK
   - Hiển thị danh sách đề
   - Tìm kiếm
   - Sắp xếp

   Không xử lý audio hoặc chấm điểm ở bước này.
   Không thay đổi student.js.
=========================================================== */

(() => {
    "use strict";

    const page = document.querySelector(
        ".luyenthi-page"
    );

    if (!page) {
        return;
    }


    // =====================================================
    // 1. ĐÁNH DẤU CẤP HSK ĐANG CHỌN
    // =====================================================

    const selectedLevel = page.querySelector(
        ".luyenthi-level-card.is-active"
    );

    if (selectedLevel) {
        selectedLevel.setAttribute(
            "aria-current",
            "page"
        );
    }


    // =====================================================
    // 2. CUỘN ĐẾN DANH SÁCH ĐỀ KHI CHỌN HSK
    // =====================================================

    const params = new URLSearchParams(
        window.location.search
    );

    const examSection = page.querySelector(
        "#danh-sach-de"
    );

    const chosenHSK = Number(
        params.get("hsk")
    );

    if (
        examSection &&
        [1, 2, 3, 4].includes(chosenHSK)
    ) {
        window.requestAnimationFrame(() => {

            const reducedMotion = window.matchMedia(
                "(prefers-reduced-motion: reduce)"
            ).matches;

            examSection.scrollIntoView({
                behavior: reducedMotion
                    ? "auto"
                    : "smooth",

                block: "start",
            });
        });
    }


    // =====================================================
    // 3. KIỂM TRA DANH SÁCH ĐỀ
    // =====================================================

    if (!examSection) {
        return;
    }

    const examGrid = examSection.querySelector(
        ".luyenthi-exam-grid"
    );

    // Khi SQL chưa có đề được xuất bản,
    // HTML sẽ hiển thị thông báo riêng.
    if (!examGrid) {
        return;
    }


    // =====================================================
    // 4. ĐỌC DANH SÁCH ĐỀ TỪ HTML
    // =====================================================

    const cards = Array.from(
        examGrid.querySelectorAll(
            ".luyenthi-exam-card"
        )
    ).map((element, index) => {

        const title = element.querySelector("h3")
            ?.textContent
            ?.trim() || "";

        const numberText = element.querySelector(
            ".luyenthi-exam-number"
        )?.textContent || "";

        const number = Number(
            numberText.replace(/[^0-9]/g, "")
        ) || index + 1;

        return {
            element,
            index,
            title,
            number,
        };
    });

    if (cards.length === 0) {
        return;
    }


    // =====================================================
    // 5. HÀM TẠO PHẦN TỬ HTML
    // =====================================================

    function createElement(tag, className, text) {

        const element = document.createElement(tag);

        if (className) {
            element.className = className;
        }

        if (text !== undefined) {
            element.textContent = text;
        }

        return element;
    }


    // =====================================================
    // 6. TẠO THANH TÌM KIẾM VÀ SẮP XẾP
    // =====================================================

    const toolbar = createElement(
        "div",
        "luyenthi-toolbar"
    );

    const toolbarMain = createElement(
        "div",
        "luyenthi-toolbar-main"
    );


    // -----------------------------------------------------
    // 6.1. Ô TÌM KIẾM
    // -----------------------------------------------------

    const searchLabel = createElement(
        "label",
        "luyenthi-field",
        "Tìm đề thi"
    );

    const searchInput = createElement("input");

    searchInput.type = "search";
    searchInput.autocomplete = "off";

    searchInput.placeholder =
        "Ví dụ: Đề 1, Đề 2...";

    searchInput.setAttribute(
        "aria-label",
        "Tìm đề thi theo tên"
    );

    searchLabel.appendChild(
        searchInput
    );


    // -----------------------------------------------------
    // 6.2. BỘ SẮP XẾP
    // -----------------------------------------------------

    const sortLabel = createElement(
        "label",
        "luyenthi-field luyenthi-field--sort",
        "Sắp xếp"
    );

    const sortSelect = createElement(
        "select"
    );

    sortSelect.setAttribute(
        "aria-label",
        "Sắp xếp danh sách đề thi"
    );

    const sortOptions = [
        ["default", "Theo thứ tự"],
        ["newest", "Đề số lớn trước"],
        ["name", "Tên A–Z"],
    ];

    sortOptions.forEach(([value, name]) => {

        const option = createElement(
            "option",
            "",
            name
        );

        option.value = value;

        sortSelect.appendChild(
            option
        );
    });

    sortLabel.appendChild(
        sortSelect
    );


    // -----------------------------------------------------
    // 6.3. SỐ LƯỢNG ĐỀ ĐANG HIỂN THỊ
    // -----------------------------------------------------

    const countText = createElement(
        "p",
        "luyenthi-count"
    );

    countText.setAttribute(
        "aria-live",
        "polite"
    );


    // -----------------------------------------------------
    // 6.4. ĐƯA THANH CÔNG CỤ VÀO TRANG
    // -----------------------------------------------------

    toolbarMain.append(
        searchLabel,
        sortLabel
    );

    toolbar.append(
        toolbarMain,
        countText
    );

    examGrid.before(
        toolbar
    );


    // =====================================================
    // 7. THÔNG BÁO KHÔNG TÌM THẤY ĐỀ
    // =====================================================

    const emptySearch = createElement(
        "div",
        "luyenthi-search-empty",
        "Không tìm thấy đề thi phù hợp. Hãy thử từ khóa khác."
    );

    emptySearch.hidden = true;

    emptySearch.setAttribute(
        "role",
        "status"
    );

    examGrid.after(
        emptySearch
    );


    // =====================================================
    // 8. CHUẨN HÓA TỪ KHÓA TÌM KIẾM
    // =====================================================

    function normalizeText(value) {

        return String(value)
            .normalize("NFD")
            .replace(
                /[\u0300-\u036f]/g,
                ""
            )
            .replace(/đ/g, "d")
            .toLowerCase()
            .trim();
    }


    // =====================================================
    // 9. CẬP NHẬT DANH SÁCH ĐỀ
    // =====================================================

    function updateExamList() {

        const query = normalizeText(
            searchInput.value
        );

        const sortMode = sortSelect.value;


        // -----------------------------------------------
        // 9.1. TÌM ĐỀ PHÙ HỢP
        // -----------------------------------------------

        const matchingCards = cards.filter(
            (card) => {

                const searchable = normalizeText(
                    `${card.title} ${card.number} Đề ${card.number}`
                );

                return searchable.includes(query);
            }
        );


        // -----------------------------------------------
        // 9.2. SẮP XẾP
        // -----------------------------------------------

        matchingCards.sort((a, b) => {

            if (sortMode === "newest") {

                return (
                    b.number - a.number ||
                    a.index - b.index
                );
            }

            if (sortMode === "name") {

                return (
                    a.title.localeCompare(
                        b.title,
                        "vi"
                    ) ||
                    a.index - b.index
                );
            }

            return a.index - b.index;
        });


        // -----------------------------------------------
        // 9.3. ẨN / HIỆN CÁC THẺ
        // -----------------------------------------------

        cards.forEach(({ element }) => {
            element.hidden = true;
        });

        matchingCards.forEach(({ element }) => {

            element.hidden = false;

            examGrid.appendChild(
                element
            );
        });


        // -----------------------------------------------
        // 9.4. CẬP NHẬT SỐ LƯỢNG
        // -----------------------------------------------

        countText.textContent =
            `Hiển thị ${matchingCards.length}/${cards.length} đề`;


        // -----------------------------------------------
        // 9.5. THÔNG BÁO NẾU KHÔNG CÓ KẾT QUẢ
        // -----------------------------------------------

        emptySearch.hidden =
            matchingCards.length > 0;
    }


    // =====================================================
    // 10. ĐĂNG KÝ SỰ KIỆN
    // =====================================================

    searchInput.addEventListener(
        "input",
        updateExamList
    );

    sortSelect.addEventListener(
        "change",
        updateExamList
    );

    // Nhấn Escape để xóa nhanh từ khóa tìm kiếm.
    searchInput.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape" &&
                searchInput.value
            ) {

                searchInput.value = "";

                updateExamList();
            }
        }
    );


    // =====================================================
    // 11. HIỂN THỊ DANH SÁCH LẦN ĐẦU
    // =====================================================

    updateExamList();

})();
