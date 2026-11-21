
/* ============================================================
   MỘC HÁN - ÔN TẬP TỪ VỰNG CÁ NHÂN

   File: static/js/vocabulary-review.js

   Chức năng:
   1. Tải từ vựng đã lưu từ SQL Server
   2. Hiển thị tổng quan ôn tập
   3. Ôn những từ đến hạn hoặc ôn tất cả
   4. Flashcard
   5. Gõ Pinyin
   6. Gõ chữ Hán
   7. Đánh giá 4 mức độ nhớ
   8. Lưu lịch sử ôn tập vào SQL Server
   9. Cập nhật tiến độ sau mỗi lần ôn

   API:
   GET  /vocabulary-review/api/words
   GET  /vocabulary-review/api/stats
   POST /vocabulary-review/api/review
============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // ========================================================
    // 1. CẤU HÌNH
    // ========================================================

    const API = {
        words: "/vocabulary-review/api/words",
        stats: "/vocabulary-review/api/stats",
        review: "/vocabulary-review/api/review"
    };

    const $ = (id) => document.getElementById(id);

    const $$ = (selector) =>
        Array.from(document.querySelectorAll(selector));

    const page = $("vocabularyReviewPage");

    if (!page) {
        return;
    }

    // ========================================================
    // 2. BIẾN TRẠNG THÁI
    // ========================================================

    let allWords = [];

    let sessionWords = [];
    let currentIndex = 0;

    let currentMode = "flashcard";

    let cardFlipped = false;
    let answerRevealed = false;
    let answerChecked = false;

    let isLoading = false;
    let isSaving = false;

    let sessionFinished = new Set();
    let sessionGrades = new Map();

    let currentAudio = null;

    let lastSessionType = "due";

    // ========================================================
    // 3. HÀM HỖ TRỢ
    // ========================================================

    function setText(id, text) {
        const element = $(id);

        if (element) {
            element.textContent = text ?? "";
        }
    }

    function show(id) {
        const element = $(id);

        if (element) {
            element.hidden = false;
        }
    }

    function hide(id) {
        const element = $(id);

        if (element) {
            element.hidden = true;
        }
    }

    function disable(id, value) {
        const element = $(id);

        if (element) {
            element.disabled = Boolean(value);
        }
    }

    function number(value) {
        return Number(value) || 0;
    }

    function validWordId(word) {
        const id = Number(word?.id);

        return Number.isInteger(id) && id > 0;
    }

    function currentWord() {
        return sessionWords[currentIndex] || null;
    }

    function currentWordKey() {
        const word = currentWord();

        return word ? String(word.id) : "";
    }

    function scrollToElement(id) {
        const element = $(id);

        if (!element) {
            return;
        }

        element.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    function getCsrfToken() {
        const input = document.querySelector(
            'input[name="csrf_token"]'
        );

        const meta = document.querySelector(
            'meta[name="csrf-token"]'
        );

        return (
            input?.value ||
            meta?.getAttribute("content") ||
            ""
        );
    }

    // ========================================================
    // 4. THÔNG BÁO
    // ========================================================

    function notify(message, type = "info") {
        const notice = $("vrNotice");

        if (!notice) {
            return;
        }

        notice.textContent = message;

        notice.className = "vr-notice";

        if (type === "error") {
            notice.classList.add("error");
        }

        if (type === "success") {
            notice.classList.add("success");
        }

        notice.hidden = false;
    }

    function clearNotice() {
        const notice = $("vrNotice");

        if (!notice) {
            return;
        }

        notice.textContent = "";
        notice.hidden = true;
    }

    // ========================================================
    // 5. CHUẨN HÓA NGÀY GIỜ
    //
    // Python trả datetime từ SQL Server dưới dạng ISO.
    // Dữ liệu hiện tại lưu theo UTC.
    // ========================================================

    function parseSqlDate(value) {
        if (!value) {
            return null;
        }

        if (value instanceof Date) {
            return Number.isNaN(value.getTime())
                ? null
                : value;
        }

        let text = String(value).trim();

        if (!text) {
            return null;
        }

        text = text.replace(" ", "T");

        // Nếu chưa có múi giờ, hiểu là UTC.
        if (
            !/[zZ]$/.test(text) &&
            !/[+-]\d{2}:\d{2}$/.test(text)
        ) {
            text += "Z";
        }

        const date = new Date(text);

        return Number.isNaN(date.getTime())
            ? null
            : date;
    }

    function isDue(word) {
        const nextDate = parseSqlDate(
            word.nextReviewAt
        );

        if (!nextDate) {
            return true;
        }

        return nextDate.getTime() <= Date.now();
    }

    function isNew(word) {
        return number(word.reviewCount) === 0;
    }

    function nextReviewText(words) {
        const upcoming = words
            .map(word => parseSqlDate(
                word.nextReviewAt
            ))
            .filter(date => (
                date &&
                date.getTime() > Date.now()
            ))
            .sort((a, b) => (
                a.getTime() - b.getTime()
            ));

        if (upcoming.length === 0) {
            return words.length
                ? "Chưa có lịch sắp tới"
                : "Chưa có dữ liệu";
        }

        const diff = upcoming[0].getTime() - Date.now();

        const minutes = Math.ceil(
            diff / (60 * 1000)
        );

        if (minutes < 60) {
            return minutes + " phút";
        }

        const hours = Math.ceil(
            diff / (60 * 60 * 1000)
        );

        if (hours < 24) {
            return hours + " giờ";
        }

        const days = Math.ceil(
            diff / (24 * 60 * 60 * 1000)
        );

        return days + " ngày";
    }

    // ========================================================
    // 6. GỌI API FLASK
    // ========================================================

    async function getApi(url) {
        const response = await fetch(url, {
            method: "GET",
            credentials: "same-origin",
            headers: {
                "Accept": "application/json"
            }
        });

        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            if (response.status === 401) {
                throw new Error(
                    "Bạn cần đăng nhập để sử dụng chức năng này."
                );
            }

            throw new Error(
                "Không nhận được dữ liệu JSON từ máy chủ. " +
                "HTTP " + response.status
            );
        }

        const result = await response.json();

        if (!response.ok || result.success === false) {
            throw new Error(
                result.message ||
                "Không thể tải dữ liệu."
            );
        }

        return result;
    }

    async function postApi(url, data) {
        const csrfToken = getCsrfToken();

        if (!csrfToken) {
            throw new Error(
                "Không tìm thấy CSRF token."
            );
        }

        const response = await fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(data)
        });

        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            if (response.status === 400) {
                throw new Error(
                    "Yêu cầu không hợp lệ hoặc CSRF token đã hết hạn."
                );
            }

            if (response.status === 401) {
                throw new Error(
                    "Phiên đăng nhập đã hết hạn."
                );
            }

            throw new Error(
                "Máy chủ trả về lỗi HTTP " +
                response.status
            );
        }

        const result = await response.json();

        if (!response.ok || result.success === false) {
            throw new Error(
                result.message ||
                "Không thể lưu kết quả ôn tập."
            );
        }

        return result;
    }

    // ========================================================
    // 7. TẢI DỮ LIỆU TỪ SQL SERVER
    // ========================================================

    async function loadDashboard() {
        if (isLoading) {
            return;
        }

        isLoading = true;

        disable("vrStartButton", true);
        disable("vrStudyAllButton", true);

        try {
            const wordsResult = await getApi(
                API.words
            );

            allWords = Array.isArray(wordsResult.words)
                ? wordsResult.words.filter(validWordId)
                : [];

            renderOverview();

            // Thống kê tổng lượt ôn từ SQL Server.
            try {
                const statsResult = await getApi(
                    API.stats
                );

                setText(
                    "vrTotalReviews",
                    number(statsResult.total_reviews)
                );

                setText(
                    "vrReviewedCount",
                    number(statsResult.reviewed_count)
                );
            } catch (statsError) {
                console.warn(
                    "Chưa lấy được thống kê chi tiết:",
                    statsError
                );

                // Các số đếm vẫn có thể tính từ words.
                setText(
                    "vrReviewedCount",
                    allWords.filter(word =>
                        !isNew(word)
                    ).length
                );

                setText("vrTotalReviews", "—");
            }

            clearNotice();
        } catch (error) {
            console.error(
                "Lỗi tải dữ liệu ôn tập:",
                error
            );

            notify(
                "Không thể tải từ vựng: " +
                error.message,
                "error"
            );
        } finally {
            isLoading = false;

            updateStartButtons();
        }
    }

    // ========================================================
    // 8. TỔNG QUAN
    // ========================================================

    function renderOverview() {
        const totalSaved = allWords.length;

        const dueWords = allWords.filter(isDue);

        const newWords = allWords.filter(isNew);

        const reviewedWords = allWords.filter(
            word => !isNew(word)
        );

        const notDueWords = allWords.filter(
            word => !isDue(word)
        );

        setText("vrTabCount", totalSaved);

        setText(
            "vrSavedCount",
            totalSaved
        );

        setText(
            "vrDueCount",
            dueWords.length
        );

        setText(
            "vrTodayCount",
            dueWords.length
        );

        setText(
            "vrNewCount",
            newWords.length
        );

        setText(
            "vrReviewedCount",
            reviewedWords.length
        );

        setText(
            "vrNotDueCount",
            notDueWords.length
        );

        setText(
            "vrNextReview",
            nextReviewText(allWords)
        );

        if (totalSaved === 0) {
            show("vrEmpty");
        } else {
            hide("vrEmpty");
        }

        updateStartButtons();
    }

    function updateStartButtons() {
        const dueCount = allWords.filter(isDue).length;

        disable(
            "vrStartButton",
            isLoading || dueCount === 0
        );

        disable(
            "vrStudyAllButton",
            isLoading || allWords.length === 0
        );
    }

    // ========================================================
    // 9. CHỌN CHẾ ĐỘ HỌC
    // ========================================================

    const MODE_TITLES = {
        flashcard: "Flashcard",
        pinyin: "Gõ Pinyin",
        hanzi: "Gõ chữ Hán"
    };

    function updateModeButtons() {
        $$("[data-vr-mode]").forEach(button => {
            const active =
                button.dataset.vrMode === currentMode;

            button.classList.toggle(
                "active",
                active
            );

            button.setAttribute(
                "aria-pressed",
                String(active)
            );
        });

        $$("[data-vr-study-mode]").forEach(button => {
            const active =
                button.dataset.vrStudyMode === currentMode;

            button.classList.toggle(
                "active",
                active
            );

            button.setAttribute(
                "aria-pressed",
                String(active)
            );
        });

        setText(
            "vrStudyModeTitle",
            MODE_TITLES[currentMode]
        );
    }

    function changeMode(mode) {
        if (isSaving) {
            return;
        }

        if (!Object.hasOwn(MODE_TITLES, mode)) {
            return;
        }

        currentMode = mode;

        updateModeButtons();

        // Nếu đang trong buổi học thì cập nhật thẻ.
        if (!$("vrStudy")?.hidden) {
            renderCurrentWord();
        }
    }

    $$("[data-vr-mode]").forEach(button => {
        button.addEventListener("click", function () {
            changeMode(
                this.dataset.vrMode
            );
        });
    });

    $$("[data-vr-study-mode]").forEach(button => {
        button.addEventListener("click", function () {
            changeMode(
                this.dataset.vrStudyMode
            );
        });
    });

    // ========================================================
    // 10. BẮT ĐẦU BUỔI ÔN
    // ========================================================

    function startSession(type = "due") {
        if (isSaving || isLoading) {
            return;
        }

        let words = [];

        if (type === "all") {
            words = [...allWords];
        } else {
            words = allWords.filter(isDue);
        }

        if (words.length === 0) {
            notify(
                type === "due"
                    ? "Hiện tại bạn không có từ đến hạn ôn."
                    : "Bạn chưa lưu từ vựng nào.",
                "info"
            );

            return;
        }

        clearNotice();

        lastSessionType = type;

        sessionWords = words;

        currentIndex = 0;

        sessionFinished = new Set();
        sessionGrades = new Map();

        cardFlipped = false;
        answerRevealed = false;
        answerChecked = false;

        hide("vrOverview");
        hide("vrResult");
        show("vrStudy");

        updateModeButtons();

        renderCurrentWord();

        scrollToElement("vrStudy");
    }

    $("vrStartButton")?.addEventListener(
        "click",
        function () {
            startSession("due");
        }
    );

    $("vrStudyAllButton")?.addEventListener(
        "click",
        function () {
            startSession("all");
        }
    );

    // ========================================================
    // 11. THANH TIẾN TRÌNH
    // ========================================================

    function updateProgress() {
        const total = sessionWords.length;

        setText(
            "vrCurrentNumber",
            total ? currentIndex + 1 : 0
        );

        setText(
            "vrTotalNumber",
            total
        );

        const percent = total
            ? Math.round(
                sessionFinished.size / total * 100
            )
            : 0;

        const bar = $("vrProgressFill");

        if (bar) {
            bar.style.width = percent + "%";
        }

        disable(
            "vrPreviousButton",
            currentIndex <= 0 || isSaving
        );

        disable(
            "vrNextButton",
            isSaving
        );
    }

    // ========================================================
    // 12. HIỂN THỊ TỪ HIỆN TẠI
    // ========================================================

    function renderCurrentWord() {
        const word = currentWord();

        if (!word) {
            finishSession();
            return;
        }

        stopAudio();

        cardFlipped = false;
        answerChecked = false;
        answerRevealed = false;

        hide("vrRating");

        setText("vrSaveStatus", "");

        updateProgress();

        if (currentMode === "flashcard") {
            show("vrFlashcardArea");
            hide("vrTypingArea");

            renderFlashcard(word);
        } else {
            hide("vrFlashcardArea");
            show("vrTypingArea");

            renderTyping(word);
        }

        // Không cho đánh giá lại từ đã hoàn thành
        // trong chính buổi ôn hiện tại.
        if (sessionFinished.has(currentWordKey())) {
            hide("vrRating");

            disable(
                "vrCheckButton",
                true
            );

            disable(
                "vrAnswerInput",
                true
            );

            disable(
                "vrRevealButton",
                true
            );
        }
    }

    // ========================================================
    // 13. FLASHCARD
    // ========================================================

    function renderFlashcard(word) {
        const card = $("vrFlashcard");

        card?.classList.remove(
            "flipped"
        );

        card?.setAttribute(
            "aria-pressed",
            "false"
        );

        setText(
            "vrCardHanzi",
            word.hanzi
        );

        setText(
            "vrCardPinyin",
            word.pinyin
        );

        setText(
            "vrCardBackHanzi",
            word.hanzi
        );

        setText(
            "vrCardBackPinyin",
            word.pinyin
        );

        setText(
            "vrCardMeaning",
            word.meaning
        );

        let exampleText =
            word.exampleChinese || "";

        if (word.exampleVietnamese) {
            exampleText += exampleText
                ? " — " + word.exampleVietnamese
                : word.exampleVietnamese;
        }

        setText(
            "vrCardExample",
            exampleText
        );

        const audioButton = $("vrAudioButton");

        if (audioButton) {
            audioButton.hidden = !word.audioUrl;
        }
    }

    function flipCard() {
        if (
            currentMode !== "flashcard" ||
            isSaving
        ) {
            return;
        }

        const word = currentWord();

        if (!word) {
            return;
        }

        cardFlipped = !cardFlipped;

        $("vrFlashcard")?.classList.toggle(
            "flipped",
            cardFlipped
        );

        $("vrFlashcard")?.setAttribute(
            "aria-pressed",
            String(cardFlipped)
        );

        if (sessionFinished.has(currentWordKey())) {
            hide("vrRating");
            return;
        }

        if (cardFlipped) {
            answerRevealed = true;
            show("vrRating");
        } else {
            hide("vrRating");
        }
    }

    $("vrFlashcard")?.addEventListener(
        "click",
        flipCard
    );

    // ========================================================
    // 14. PHÁT ÂM
    // ========================================================

    function stopAudio() {
        if (!currentAudio) {
            return;
        }

        currentAudio.pause();
        currentAudio.currentTime = 0;

        currentAudio = null;
    }

    $("vrAudioButton")?.addEventListener(
        "click",
        async function () {
            const word = currentWord();

            if (!word || !word.audioUrl) {
                return;
            }

            stopAudio();

            const audio = new Audio(
                word.audioUrl
            );

            currentAudio = audio;

            try {
                await audio.play();
            } catch (error) {
                console.error(
                    "Lỗi phát âm thanh:",
                    error
                );

                notify(
                    "Không phát được âm thanh của từ này.",
                    "error"
                );
            }
        }
    );

    // ========================================================
    // 15. CHUẨN HÓA CHỮ HÁN VÀ PINYIN
    // ========================================================

    function normalizeHanzi(value) {
        return String(value || "")
            .trim()
            .replace(/\s+/g, "")
            .replace(/[，。！？、,.!?]/g, "");
    }

    /*
       Pinyin:
       - Chấp nhận có hoặc không có dấu thanh
       - Chấp nhận khoảng trắng khác nhau
       - Chấp nhận ü hoặc v
       - Ví dụ:
           nǐ hǎo
           ni hao
           nihao
         đều được xem là cùng cách viết âm tiết.

       Lưu ý:
       Việc bỏ dấu thanh giúp dễ nhập hơn,
       nhưng không kiểm tra được lỗi thanh điệu.
    */

    function normalizePinyin(value) {
        return String(value || "")
            .toLowerCase()
            .trim()
            .replace(/u:/g, "v")
            .replace(/ü/g, "v")
            .replace(/[ǖǘǚǜ]/g, "v")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[1-5]/g, "")
            .replace(/[^a-zv]/g, "");
    }

    // ========================================================
    // 16. GÕ PINYIN / GÕ CHỮ HÁN
    // ========================================================

    function renderTyping(word) {
        const input = $("vrAnswerInput");
        const feedback = $("vrFeedback");

        if (input) {
            input.value = "";
            input.disabled = false;
        }

        disable("vrCheckButton", false);
        disable("vrRevealButton", false);

        if (feedback) {
            feedback.textContent = "";
            feedback.className = "vr-feedback";
        }

        show("vrRevealButton");

        if (currentMode === "pinyin") {
            setText(
                "vrQuestionLabel",
                "HÃY NHẬP PINYIN"
            );

            setText(
                "vrQuestionMain",
                word.hanzi
            );

            setText(
                "vrQuestionHint",
                word.meaning
            );

            if (input) {
                input.placeholder =
                    "Nhập Pinyin của từ...";
            }
        } else {
            setText(
                "vrQuestionLabel",
                "HÃY NHẬP CHỮ HÁN"
            );

            setText(
                "vrQuestionMain",
                word.meaning
            );

            setText(
                "vrQuestionHint",
                word.pinyin || ""
            );

            if (input) {
                input.placeholder =
                    "Nhập chữ Hán...";
            }
        }

        input?.focus();
    }

    function setFeedback(text, type = "info") {
        const element = $("vrFeedback");

        if (!element) {
            return;
        }

        element.textContent = text;

        element.className =
            "vr-feedback " + type;
    }

    function showTypingResult(correct, expected) {
        answerChecked = true;
        answerRevealed = true;

        if (correct) {
            setFeedback(
                "✓ Chính xác!",
                "correct"
            );
        } else {
            setFeedback(
                "✕ Chưa đúng. Đáp án: " + expected,
                "wrong"
            );
        }

        disable("vrAnswerInput", true);
        disable("vrCheckButton", true);
        disable("vrRevealButton", true);

        hide("vrRevealButton");

        if (!sessionFinished.has(currentWordKey())) {
            show("vrRating");
        }
    }

    function checkTypingAnswer() {
        if (
            answerChecked ||
            isSaving ||
            sessionFinished.has(currentWordKey())
        ) {
            return;
        }

        const word = currentWord();
        const input = $("vrAnswerInput");

        if (!word || !input) {
            return;
        }

        const answer = input.value.trim();

        if (!answer) {
            setFeedback(
                "Bạn chưa nhập đáp án.",
                "wrong"
            );

            input.focus();
            return;
        }

        const expected =
            currentMode === "pinyin"
                ? word.pinyin
                : word.hanzi;

        if (!expected) {
            setFeedback(
                "Từ này chưa có đáp án trong dữ liệu.",
                "wrong"
            );
            return;
        }

        const normalizedAnswer =
            currentMode === "pinyin"
                ? normalizePinyin(answer)
                : normalizeHanzi(answer);

        const normalizedExpected =
            currentMode === "pinyin"
                ? normalizePinyin(expected)
                : normalizeHanzi(expected);

        const correct =
            normalizedAnswer.length > 0 &&
            normalizedAnswer === normalizedExpected;

        showTypingResult(
            correct,
            expected
        );
    }

    function revealTypingAnswer() {
        if (
            isSaving ||
            sessionFinished.has(currentWordKey())
        ) {
            return;
        }

        const word = currentWord();

        if (!word) {
            return;
        }

        const expected =
            currentMode === "pinyin"
                ? word.pinyin
                : word.hanzi;

        answerChecked = true;
        answerRevealed = true;

        setFeedback(
            "Đáp án: " + (expected || "Chưa có dữ liệu"),
            "info"
        );

        disable("vrAnswerInput", true);
        disable("vrCheckButton", true);
        disable("vrRevealButton", true);

        hide("vrRevealButton");

        show("vrRating");
    }

    $("vrCheckButton")?.addEventListener(
        "click",
        checkTypingAnswer
    );

    $("vrRevealButton")?.addEventListener(
        "click",
        revealTypingAnswer
    );

    $("vrAnswerInput")?.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key !== "Enter" ||
                event.isComposing ||
                event.keyCode === 229
            ) {
                return;
            }

            event.preventDefault();

            checkTypingAnswer();
        }
    );

    // ========================================================
    // 17. ĐÁNH GIÁ MỨC ĐỘ NHỚ
    //
    // 1 - Quên rồi
    // 2 - Khó
    // 3 - Tốt
    // 4 - Dễ
    //
    // Chỉ ghi lịch sử khi người học chọn mức độ.
    // ========================================================

    function setGradeButtonsDisabled(disabled) {
        $$("[data-vr-grade]").forEach(button => {
            button.disabled = disabled;
        });
    }

    async function saveGrade(grade) {
        const word = currentWord();

        if (!word || isSaving) {
            return;
        }

        if (![1, 2, 3, 4].includes(grade)) {
            return;
        }

        if (!answerRevealed) {
            notify(
                "Hãy xem đáp án trước khi đánh giá.",
                "info"
            );
            return;
        }

        const wordKey = currentWordKey();

        if (sessionFinished.has(wordKey)) {
            notify(
                "Bạn đã ôn từ này trong buổi hiện tại.",
                "info"
            );
            return;
        }

        isSaving = true;

        setGradeButtonsDisabled(true);

        disable("vrNextButton", true);
        disable("vrPreviousButton", true);

        setText(
            "vrSaveStatus",
            "Đang lưu kết quả..."
        );

        try {
            // Gửi kết quả tới SQL Server.
            await postApi(
                API.review,
                {
                    word_id: Number(word.id),
                    grade: grade
                }
            );

            // Chỉ đánh dấu hoàn thành
            // sau khi server xác nhận thành công.
            sessionFinished.add(wordKey);

            sessionGrades.set(
                wordKey,
                grade
            );

            setText(
                "vrSaveStatus",
                "✓ Đã lưu kết quả."
            );

            updateProgress();

            if (
                sessionFinished.size ===
                sessionWords.length
            ) {
                finishSession();
                return;
            }

            // Chuyển sang từ chưa ôn tiếp theo.
            const nextIndex = findNextUnfinishedIndex();

            if (nextIndex !== -1) {
                currentIndex = nextIndex;
                renderCurrentWord();
            }

            // Làm mới thống kê từ SQL.
            await loadDashboard();

        } catch (error) {
            console.error(
                "Lỗi lưu kết quả ôn tập:",
                error
            );

            setText(
                "vrSaveStatus",
                "✕ " + error.message
            );

            notify(
                "Không lưu được kết quả: " +
                error.message,
                "error"
            );
        } finally {
            isSaving = false;

            setGradeButtonsDisabled(false);

            updateProgress();
        }
    }

    function findNextUnfinishedIndex() {
        if (sessionWords.length === 0) {
            return -1;
        }

        for (
            let offset = 1;
            offset <= sessionWords.length;
            offset++
        ) {
            const index =
                (currentIndex + offset) %
                sessionWords.length;

            const word = sessionWords[index];

            if (
                !sessionFinished.has(String(word.id))
            ) {
                return index;
            }
        }

        return -1;
    }

    $$("[data-vr-grade]").forEach(button => {
        button.addEventListener(
            "click",
            function () {
                const grade = Number(
                    this.dataset.vrGrade
                );

                saveGrade(grade);
            }
        );
    });

    // ========================================================
    // 18. CHUYỂN TỪ TRƯỚC / SAU
    // ========================================================

    function previousWord() {
        if (isSaving || currentIndex <= 0) {
            return;
        }

        currentIndex--;

        renderCurrentWord();
    }

    function nextWord() {
        if (isSaving) {
            return;
        }

        if (
            currentIndex <
            sessionWords.length - 1
        ) {
            currentIndex++;

            renderCurrentWord();
            return;
        }

        // Đang ở từ cuối, tìm từ chưa hoàn thành.
        const nextIndex = findNextUnfinishedIndex();

        if (nextIndex !== -1) {
            currentIndex = nextIndex;
            renderCurrentWord();
        } else {
            finishSession();
        }
    }

    $("vrPreviousButton")?.addEventListener(
        "click",
        previousWord
    );

    $("vrNextButton")?.addEventListener(
        "click",
        nextWord
    );

    // ========================================================
    // 19. KẾT THÚC BUỔI ÔN
    // ========================================================

    function finishSession() {
        stopAudio();

        hide("vrStudy");
        hide("vrOverview");

        show("vrResult");

        setText(
            "vrCompletedCount",
            sessionFinished.size
        );

        setText(
            "vrSessionTotal",
            sessionWords.length
        );

        scrollToElement("vrResult");

        // Cập nhật thống kê từ SQL Server.
        void loadDashboard();
    }

    // ========================================================
    // 20. QUAY LẠI TỔNG QUAN
    // ========================================================

    async function returnToOverview() {
        if (isSaving) {
            return;
        }

        stopAudio();

        hide("vrStudy");
        hide("vrResult");

        show("vrOverview");

        await loadDashboard();

        scrollToElement("vrOverview");
    }

    $("vrBackButton")?.addEventListener(
        "click",
        returnToOverview
    );

    $("vrReturnButton")?.addEventListener(
        "click",
        returnToOverview
    );

    $("vrRestartButton")?.addEventListener(
        "click",
        function () {
            startSession(lastSessionType);
        }
    );

    // ========================================================
    // 21. KHỞI TẠO
    // ========================================================

    hide("vrStudy");
    hide("vrResult");

    show("vrOverview");

    updateModeButtons();

    void loadDashboard();

    console.log(
        "[Mộc Hán] Ôn tập từ vựng cá nhân đã khởi tạo."
    );
});
