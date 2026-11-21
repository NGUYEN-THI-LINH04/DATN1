
/* ==========================================================
   MỘC HÁN - TRA TỪ ĐIỂN STUDENT

   File: static/js/dictionary.js

   Kết nối:
   - routes/student/dictionary.py
   - templates/student/dictionary.html
   - static/css/dictionary.css

   API tra từ:
   GET /student/dictionary/api/search?q=...

   API lưu để ôn tập hiện có:
   GET  /vocabulary-review/api/saved-ids
   POST /vocabulary-review/api/save-word

   Không sử dụng localStorage để lưu từ.
   Không thay đổi SQL Server.
========================================================== */

(function () {
    "use strict";

    const SAVED_IDS_URL =
        "/vocabulary-review/api/saved-ids";

    const SAVE_WORD_URL =
        "/vocabulary-review/api/save-word";

    let searchController = null;
    let savedWordIds = new Set();


    // ======================================================
    // 1. KHỞI TẠO
    // ======================================================

    function initDictionary() {
        const page = document.getElementById(
            "dictionaryPage"
        );

        if (!page) {
            return;
        }

        const searchUrl = page.dataset.searchUrl;

        const form = document.getElementById(
            "dictionarySearchForm"
        );

        const input = document.getElementById(
            "dictionarySearchInput"
        );

        const clearButton = document.getElementById(
            "dictionaryClearButton"
        );

        const searchButton = document.getElementById(
            "dictionarySearchButton"
        );

        const status = document.getElementById(
            "dictionaryStatus"
        );

        const loading = document.getElementById(
            "dictionaryLoading"
        );

        const errorBox = document.getElementById(
            "dictionaryError"
        );

        const results = document.getElementById(
            "dictionaryResults"
        );

        const empty = document.getElementById(
            "dictionaryEmpty"
        );

        const cardTemplate = document.getElementById(
            "dictionaryCardTemplate"
        );

        const exampleTemplate = document.getElementById(
            "dictionaryExampleTemplate"
        );

        if (
            !searchUrl ||
            !form ||
            !input ||
            !clearButton ||
            !searchButton ||
            !status ||
            !loading ||
            !errorBox ||
            !results ||
            !empty ||
            !cardTemplate ||
            !exampleTemplate
        ) {
            console.error(
                "Tra từ điển: thiếu thành phần HTML."
            );
            return;
        }


        // ==================================================
        // 2. HÀM HIỂN THỊ
        // ==================================================

        function showError(message) {
            errorBox.textContent = message;
            errorBox.hidden = false;
        }

        function hideError() {
            errorBox.textContent = "";
            errorBox.hidden = true;
        }

        function setLoading(value) {
            loading.hidden = !value;
            searchButton.disabled = value;
        }

        function setStatus(message) {
            status.textContent = message;
        }

        function showDefaultState() {
            results.replaceChildren();
            hideError();
            setLoading(false);

            empty.hidden = false;

            setStatus(
                "Nhập từ khóa để bắt đầu tra từ."
            );
        }

        function showNoResults(query) {
            results.replaceChildren();

            empty.hidden = false;

            const title = empty.querySelector("h2");
            const description = empty.querySelector("p");

            if (title) {
                title.textContent =
                    "Không tìm thấy từ phù hợp";
            }

            if (description) {
                description.textContent =
                    `Chưa tìm thấy kết quả cho "${query}". ` +
                    "Bạn thử nhập chữ Hán, Pinyin hoặc " +
                    "một từ khóa khác nhé.";
            }

            setStatus(
                `Không có kết quả cho "${query}".`
            );
        }

        function updateSearchUrl(query) {
            const url = new URL(
                window.location.href
            );

            if (query) {
                url.searchParams.set("q", query);
            } else {
                url.searchParams.delete("q");
            }

            window.history.replaceState(
                null,
                "",
                url.pathname +
                url.search +
                url.hash
            );
        }


        // ==================================================
        // 3. HIỂN THỊ CÂU VÍ DỤ
        // ==================================================

        function createExample(example) {
            const fragment =
                exampleTemplate.content.cloneNode(true);

            const item = fragment.querySelector(
                ".dictionary-example"
            );

            const pinyin = item.querySelector(
                ".dictionary-example-pinyin"
            );

            const chinese = item.querySelector(
                ".dictionary-example-chinese"
            );

            const vietnamese = item.querySelector(
                ".dictionary-example-vietnamese"
            );

            const audioButton = item.querySelector(
                ".dictionary-example-audio"
            );

            pinyin.textContent =
                example.pinyin || "";

            chinese.textContent =
                example.tieng_trung || "";

            vietnamese.textContent =
                example.tieng_viet || "";

            audioButton.addEventListener(
                "click",
                function () {
                    speakChinese(
                        example.tieng_trung || ""
                    );
                }
            );

            return fragment;
        }


        // ==================================================
        // 4. HIỂN THỊ THẺ TỪ VỰNG
        // ==================================================

        function createWordCard(word) {
            const fragment =
                cardTemplate.content.cloneNode(true);

            const card = fragment.querySelector(
                ".dictionary-word-card"
            );

            const hanzi = card.querySelector(
                ".dictionary-word-hanzi"
            );

            const traditional = card.querySelector(
                ".dictionary-word-traditional"
            );

            const pinyin = card.querySelector(
                ".dictionary-word-pinyin"
            );

            const meaning = card.querySelector(
                ".dictionary-word-meaning"
            );

            const hsk = card.querySelector(
                ".dictionary-hsk-tag"
            );

            const type = card.querySelector(
                ".dictionary-type-tag"
            );

            const audioButton = card.querySelector(
                ".dictionary-audio-button"
            );

            const saveButton = card.querySelector(
                ".dictionary-save-button"
            );

            const exampleList = card.querySelector(
                ".dictionary-examples-list"
            );

            const exampleSection = card.querySelector(
                ".dictionary-examples-section"
            );

            const wordId = Number(
                word.ma_tu_vung
            );

            card.dataset.wordId = String(wordId);

            hanzi.textContent =
                word.chu_han || "";

            pinyin.textContent =
                word.phien_am || "";

            meaning.textContent =
                word.nghia_tieng_viet || "Chưa có nghĩa.";

            if (
                word.chu_phon_the &&
                word.chu_phon_the !== word.chu_han
            ) {
                traditional.textContent =
                    `(${word.chu_phon_the})`;
            } else {
                traditional.textContent = "";
            }

            hsk.textContent = word.hsk
                ? `HSK ${word.hsk}`
                : "";

            type.textContent =
                word.tu_loai || "";

            // Nghe phát âm từ vựng.
            audioButton.addEventListener(
                "click",
                function () {
                    speakChinese(
                        word.chu_han || ""
                    );
                }
            );

            // Lưu vào danh sách ôn tập từ vựng.
            // Không gọi đây là sổ tay nhiều cuốn.
            saveButton.dataset.wordId =
                String(wordId);

            updateSaveButton(
                saveButton,
                wordId
            );

            saveButton.addEventListener(
                "click",
                function () {
                    saveWordForReview(
                        wordId,
                        saveButton
                    );
                }
            );

            // Hiển thị tối đa ba ví dụ từ Python.
            const examples = Array.isArray(
                word.vi_du
            )
                ? word.vi_du
                : [];

            exampleList.replaceChildren();

            examples.forEach(function (example) {
                exampleList.appendChild(
                    createExample(example)
                );
            });

            if (exampleSection) {
                const heading =
                    exampleSection.querySelector("h3");

                if (heading) {
                    heading.textContent = "Ví dụ";
                }
            }

            return fragment;
        }


        // ==================================================
        // 5. HIỂN THỊ DANH SÁCH KẾT QUẢ
        // ==================================================

        function renderResults(words, query) {
            results.replaceChildren();

            if (!Array.isArray(words) || !words.length) {
                showNoResults(query);
                return;
            }

            empty.hidden = true;

            const fragment =
                document.createDocumentFragment();

            words.forEach(function (word) {
                fragment.appendChild(
                    createWordCard(word)
                );
            });

            results.appendChild(fragment);

            setStatus(
                `Tìm thấy ${words.length} kết quả ` +
                `cho "${query}".`
            );
        }


        // ==================================================
        // 6. GỌI API TRA TỪ ĐIỂN
        // ==================================================

        async function searchDictionary(query) {
            const keyword = String(
                query || ""
            ).trim();

            if (searchController) {
                searchController.abort();
            }

            if (!keyword) {
                showDefaultState();
                updateSearchUrl("");
                return;
            }

            if (keyword.length > 80) {
                showError(
                    "Từ khóa không được vượt quá 80 ký tự."
                );
                return;
            }

            searchController =
                new AbortController();

            const controller = searchController;

            hideError();
            setLoading(true);

            empty.hidden = true;
            results.replaceChildren();

            setStatus(
                `Đang tra từ "${keyword}"...`
            );

            const params = new URLSearchParams({
                q: keyword
            });

            try {
                const response = await fetch(
                    `${searchUrl}?${params.toString()}`,
                    {
                        method: "GET",
                        credentials: "same-origin",
                        headers: {
                            "Accept": "application/json"
                        },
                        signal: controller.signal
                    }
                );

                const contentType =
                    response.headers.get(
                        "content-type"
                    ) || "";

                if (
                    !contentType.includes(
                        "application/json"
                    )
                ) {
                    throw new Error(
                        "Máy chủ không trả về dữ liệu JSON."
                    );
                }

                const data = await response.json();

                if (!response.ok || data.ok === false) {
                    throw new Error(
                        data.error ||
                        `Không thể tra từ (HTTP ${response.status}).`
                    );
                }

                renderResults(
                    data.results || [],
                    keyword
                );

                updateSearchUrl(keyword);

            } catch (error) {
                if (error.name === "AbortError") {
                    return;
                }

                results.replaceChildren();
                empty.hidden = true;

                setStatus(
                    "Không thể hoàn thành tìm kiếm."
                );

                showError(
                    error.message ||
                    "Có lỗi khi tra từ. Vui lòng thử lại."
                );

                console.error(
                    "Dictionary search error:",
                    error
                );

            } finally {
                if (
                    searchController === controller
                ) {
                    setLoading(false);
                    searchController = null;
                }
            }
        }


        // ==================================================
        // 7. NGHE PHÁT ÂM TIẾNG TRUNG
        //
        // Dùng SpeechSynthesis của trình duyệt.
        // Chưa đọc file audio từ TepDaPhuongTien.
        // ==================================================

        function speakChinese(text) {
            const content = String(
                text || ""
            ).trim();

            if (!content) {
                return;
            }

            if (
                !("speechSynthesis" in window) ||
                !("SpeechSynthesisUtterance" in window)
            ) {
                showError(
                    "Trình duyệt chưa hỗ trợ phát âm."
                );
                return;
            }

            try {
                window.speechSynthesis.cancel();

                const utterance =
                    new SpeechSynthesisUtterance(
                        content
                    );

                utterance.lang = "zh-CN";
                utterance.rate = 0.85;
                utterance.pitch = 1;
                utterance.volume = 1;

                const voices =
                    window.speechSynthesis.getVoices();

                const chineseVoice = voices.find(
                    function (voice) {
                        return /^zh[-_]CN/i.test(
                            voice.lang
                        );
                    }
                ) || voices.find(
                    function (voice) {
                        return /^zh/i.test(
                            voice.lang
                        );
                    }
                );

                if (chineseVoice) {
                    utterance.voice = chineseVoice;
                }

                utterance.onerror = function (event) {
                    if (
                        event.error === "canceled" ||
                        event.error === "interrupted"
                    ) {
                        return;
                    }

                    showError(
                        "Không thể phát âm. " +
                        "Bạn kiểm tra giọng tiếng Trung " +
                        "trên trình duyệt hoặc hệ điều hành."
                    );
                };

                window.speechSynthesis.speak(
                    utterance
                );

            } catch (error) {
                showError(
                    "Không thể phát âm từ này."
                );

                console.error(
                    "Dictionary audio error:",
                    error
                );
            }
        }


        // ==================================================
        // 8. ĐỒNG BỘ DANH SÁCH TỪ ĐÃ LƯU ĐỂ ÔN
        // ==================================================

        function updateSaveButton(button, wordId) {
            const saved = savedWordIds.has(
                Number(wordId)
            );

            button.classList.toggle(
                "is-saved",
                saved
            );

            button.textContent = saved
                ? "✓ Đã lưu để ôn tập"
                : "+ Lưu để ôn tập";

            button.disabled = saved;
        }

        function refreshSaveButtons() {
            results.querySelectorAll(
                ".dictionary-save-button"
            ).forEach(function (button) {
                const id = Number(
                    button.dataset.wordId
                );

                updateSaveButton(
                    button,
                    id
                );
            });
        }

        async function loadSavedWordIds() {
            try {
                const response = await fetch(
                    SAVED_IDS_URL,
                    {
                        credentials: "same-origin",
                        headers: {
                            "Accept": "application/json"
                        }
                    }
                );

                if (!response.ok) {
                    return;
                }

                const data = await response.json();

                if (
                    data.success &&
                    Array.isArray(data.word_ids)
                ) {
                    savedWordIds = new Set(
                        data.word_ids.map(Number)
                    );

                    refreshSaveButtons();
                }

            } catch (error) {
                console.warn(
                    "Chưa đồng bộ được từ đã lưu:",
                    error
                );
            }
        }


        // ==================================================
        // 9. LƯU TỪ VÀO ÔN TẬP
        //
        // Sử dụng API ĐÃ CÓ của vocabulary_review.py
        // Không tạo bảng SQL mới.
        // ==================================================

        async function saveWordForReview(
            wordId,
            button
        ) {
            if (savedWordIds.has(wordId)) {
                updateSaveButton(
                    button,
                    wordId
                );
                return;
            }

            const csrfInput = document.querySelector(
                "#dictionaryCsrfToken"
            ) || document.querySelector(
                'input[name="csrf_token"]'
            );

            const csrfToken = csrfInput
                ? csrfInput.value
                : "";

            if (!csrfToken) {
                showError(
                    "Thiếu mã bảo mật CSRF. " +
                    "Hãy kiểm tra dictionary.html."
                );
                return;
            }

            button.disabled = true;
            button.textContent = "Đang lưu...";

            hideError();

            try {
                const response = await fetch(
                    SAVE_WORD_URL,
                    {
                        method: "POST",
                        credentials: "same-origin",
                        headers: {
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken
                        },
                        body: JSON.stringify({
                            word_id: wordId
                        })
                    }
                );

                const contentType =
                    response.headers.get(
                        "content-type"
                    ) || "";

                if (
                    !contentType.includes(
                        "application/json"
                    )
                ) {
                    throw new Error(
                        "Máy chủ không trả về JSON. " +
                        "Bạn kiểm tra đăng nhập và CSRF."
                    );
                }

                const data = await response.json();

                if (
                    !response.ok ||
                    data.success !== true
                ) {
                    throw new Error(
                        data.message ||
                        data.error ||
                        "Không thể lưu từ vựng."
                    );
                }

                savedWordIds.add(wordId);

                refreshSaveButtons();

                setStatus(
                    "Đã lưu từ vào danh sách ôn tập."
                );

            } catch (error) {
                showError(
                    error.message ||
                    "Không thể lưu từ vựng."
                );

                updateSaveButton(
                    button,
                    wordId
                );

            }
        }


        // ==================================================
        // 10. SỰ KIỆN TÌM KIẾM
        // ==================================================

        form.addEventListener(
            "submit",
            function (event) {
                event.preventDefault();

                searchDictionary(
                    input.value
                );
            }
        );

        clearButton.addEventListener(
            "click",
            function () {
                input.value = "";

                if (searchController) {
                    searchController.abort();
                    searchController = null;
                }

                window.speechSynthesis?.cancel();

                showDefaultState();
                updateSearchUrl("");

                input.focus();
            }
        );


        // ==================================================
        // 11. KHỞI TẠO DỮ LIỆU
        // ==================================================

        loadSavedWordIds();

        const params = new URLSearchParams(
            window.location.search
        );

        const initialQuery = (
            params.get("q") ||
            input.value ||
            ""
        ).trim();

        if (initialQuery) {
            input.value = initialQuery;

            searchDictionary(
                initialQuery
            );
        } else {
            showDefaultState();
        }

    }


    // ======================================================
    // 12. CHẠY KHI HTML SẴN SÀNG
    // ======================================================

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initDictionary
        );
    } else {
        initDictionary();
    }

})();
