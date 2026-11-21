
document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    /* =====================================================
       MỘC HÁN - TỔNG ÔN TỪ VỰNG
       Flashcard, Trắc nghiệm, Gõ từ, Đọc hiểu,
       Nghe ghép câu, Đấu trí

       BỔ SUNG:
       - Lưu kết quả ôn vào SQL Server qua Flask API
       - Không tính trùng câu trả lời
       - Hỗ trợ CSRF
       - Không tính việc chỉ xem/lật thẻ là đã ôn
    ===================================================== */

    const $ = (id) => document.getElementById(id);
    const $$ = (selector) =>
        Array.from(document.querySelectorAll(selector));

    const dataElement = $("reviewVocabularyData");
    let allVocabulary = [];

    try {
        allVocabulary = dataElement
            ? JSON.parse(dataElement.textContent || "[]")
            : [];
        if (!Array.isArray(allVocabulary)) allVocabulary = [];
    } catch (error) {
        console.error("Lỗi dữ liệu Tổng ôn:", error);
        allVocabulary = [];
    }

    const lessonCheckboxes = $$(".review-lesson-checkbox");
    const modeCards = $$(".review-mode-card");
    const speedButtons = $$("[data-review-speed]");
    const typingModeInputs = $$('input[name="reviewTypingMode"]');

    const areas = {
        flashcard: $("reviewFlashcardShell"),
        quiz: $("reviewQuizArea"),
        typing: $("reviewTypingArea"),
        reading: $("reviewReadingArea"),
        listening: $("reviewListeningArea"),
        battle: $("reviewBattleArea"),
        result: $("reviewResultArea")
    };

    let reviewWords = [...allVocabulary];
    let currentMode = "flashcard";
    let currentIndex = 0;
    let cardFlipped = false;
    let cardView = "word";
    let direction = "zh-vi";

    let autoTimer = null;
    let currentAudio = null;

    const learnedIds = new Set();
    const notLearnedIds = new Set();

    let quizQuestions = [];
    let quizIndex = 0;
    let quizCorrect = 0;
    let quizAnswered = false;

    let typingQuestions = [];
    let typingIndex = 0;
    let typingCorrect = 0;
    let typingAnswered = false;

    let readingQuestions = [];
    let readingIndex = 0;
    let readingCorrect = 0;
    let readingAnswered = false;

    let listeningQuestions = [];
    let listeningIndex = 0;
    let listeningCorrect = 0;
    let listeningSpeed = 1;
    let listeningTokens = [];
    let listeningSelected = [];
    let listeningSolved = false;
    let listeningHadWrongAttempt = false;

    let battleQuestions = [];
    let battleIndex = 0;
    let battleCorrect = 0;
    let battlePoints = 0;
    let battleTimeLeft = 15;
    let battleTimer = null;
    let battleAnswered = false;

    /* =====================================================
       1. HÀM HỖ TRỢ
    ===================================================== */

    function setText(id, value) {
        const element = $(id);
        if (element) element.textContent = value ?? "";
    }

    function setHidden(id, hidden) {
        const element = $(id);
        if (element) element.hidden = hidden;
    }

    function shuffle(items) {
        const result = [...items];

        for (let i = result.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [result[i], result[j]] = [result[j], result[i]];
        }

        return result;
    }

    function normalizeText(value) {
        return String(value || "")
            .trim()
            .toLowerCase()
            .replace(/\s+/g, "")
            .replace(
                /[，。！？、；：,.!?;:“”"'（）()《》\-—]/g,
                ""
            );
    }

    function normalizePinyin(value) {
        const toneMap = {
            "ā": "a", "á": "a", "ǎ": "a", "à": "a",
            "ē": "e", "é": "e", "ě": "e", "è": "e",
            "ī": "i", "í": "i", "ǐ": "i", "ì": "i",
            "ō": "o", "ó": "o", "ǒ": "o", "ò": "o",
            "ū": "u", "ú": "u", "ǔ": "u", "ù": "u",
            "ǖ": "v", "ǘ": "v", "ǚ": "v", "ǜ": "v",
            "ü": "v",
            "ń": "n", "ň": "n", "ǹ": "n", "ḿ": "m"
        };

        return Array.from(String(value || "").toLowerCase())
            .map((character) => toneMap[character] || character)
            .join("")
            .replace(/u:/g, "v")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[1-5]/g, "")
            .replace(/[^a-z]/g, "");
    }

    function calculatePercent(correct, total) {
        return total ? Math.round(correct * 100 / total) : 0;
    }

    function uniqueValues(values) {
        return [...new Set(
            values.map((value) => String(value || "").trim())
                .filter(Boolean)
        )];
    }

    function setFeedback(id, message, type = "") {
        const element = $(id);
        if (!element) return;

        element.textContent = message;
        element.className =
            "review-feedback" + (type ? " " + type : "");
    }

    function createOption(text, callback) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = text;

        button.addEventListener("click", function () {
            callback(button);
        });

        return button;
    }

    function markOptions(container, correctAnswer) {
        if (!container) return;

        container.querySelectorAll("button").forEach((button) => {
            button.disabled = true;

            if (button.textContent === correctAnswer) {
                button.classList.add("correct");
            }
        });
    }

    function buildOptions(correct, otherValues) {
        const distractors = uniqueValues(otherValues)
            .filter((item) => item !== correct);

        return shuffle([
            correct,
            ...shuffle(distractors).slice(0, 3)
        ]);
    }

    /* =====================================================
       2. LƯU LỊCH SỬ ÔN TẬP VÀO SQL SERVER
    ===================================================== */

    const REVIEW_SAVE_URL = "/review/api/vocabulary-result";

    function getCsrfToken() {
        const meta = document.querySelector(
            'meta[name="csrf-token"]'
        );

        const hiddenInput = document.querySelector(
            'input[name="csrf_token"]'
        );

        return (
            window.reviewCsrfToken ||
            meta?.content ||
            hiddenInput?.value ||
            ""
        );
    }

    /*
       Mỗi kết quả chỉ được gửi khi có hành động học:
       - Flashcard: Đã thuộc / Chưa thuộc
       - Trắc nghiệm: Chọn đáp án
       - Gõ từ: Bấm Kiểm tra
       - Đọc hiểu: Chọn đáp án
       - Nghe ghép câu: Hoàn thành câu
       - Đấu trí: Trả lời hoặc hết giờ

       grade:
       1 = Quên rồi
       2 = Khó
       3 = Tốt
       4 = Dễ
    */

    let savedReviewCount = null;
    let saveFailureCount = 0;

    async function saveReviewResult(wordId, grade) {
        const id = Number(wordId);
        const level = Number(grade);

        if (
            !Number.isInteger(id) ||
            id <= 0 ||
            ![1, 2, 3, 4].includes(level)
        ) {
            console.error(
                "Dữ liệu lưu ôn tập không hợp lệ:",
                wordId,
                grade
            );
            return false;
        }

        const csrfToken = getCsrfToken();

        const headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        };

        if (csrfToken) {
            headers["X-CSRFToken"] = csrfToken;
        }

        try {
            const response = await fetch(REVIEW_SAVE_URL, {
                method: "POST",
                credentials: "same-origin",
                headers,
                body: JSON.stringify({
                    word_id: id,
                    grade: level
                })
            });

            const contentType =
                response.headers.get("content-type") || "";

            let result = null;

            if (contentType.includes("application/json")) {
                result = await response.json();
            }

            if (!response.ok || !result?.success) {
                saveFailureCount++;

                console.error(
                    "Không lưu được lịch sử ôn tập:",
                    response.status,
                    result?.message ||
                    "Máy chủ không trả về kết quả hợp lệ."
                );

                return false;
            }

            savedReviewCount = Number(
                result.reviewed_count || 0
            );

            console.log(
                "[Mộc Hán] Đã lưu lượt ôn:",
                {
                    wordId: id,
                    grade: level,
                    totalReviewed: savedReviewCount
                }
            );

            return true;

        } catch (error) {
            saveFailureCount++;

            console.error(
                "Lỗi kết nối khi lưu lịch sử ôn tập:",
                error
            );

            return false;
        }
    }

    /*
       Dùng cho các thao tác không cần chờ lưu
       mới chuyển câu. Vẫn ghi lỗi vào Console.
    */
    function recordReview(word, grade) {
        if (!word || !word.id) return;

        void saveReviewResult(word.id, grade);
    }

    /* =====================================================
       3. AUDIO VÀ TIMER
    ===================================================== */

    function stopAudio() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
        }

        $("reviewAudioButton")?.classList.remove("is-playing");
    }

    function stopAutoPlay() {
        if (autoTimer !== null) {
            clearInterval(autoTimer);
            autoTimer = null;
        }

        const button = $("reviewAutoButton");

        if (button) {
            button.classList.remove("active");
            button.textContent = "▷ Tự động";
        }
    }

    function stopSpeech() {
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
        }
    }

    function stopBattleTimer() {
        if (battleTimer !== null) {
            clearInterval(battleTimer);
            battleTimer = null;
        }
    }

    function stopAllMedia() {
        stopAudio();
        stopAutoPlay();
        stopSpeech();
        stopBattleTimer();
    }

    /* =====================================================
       4. CHỌN PHẠM VI BÀI HỌC
    ===================================================== */

    function selectedLessonIds() {
        return new Set(
            lessonCheckboxes
                .filter((checkbox) => checkbox.checked)
                .map((checkbox) => Number(checkbox.value))
        );
    }

    function updateLessonVisuals() {
        lessonCheckboxes.forEach((checkbox) => {
            checkbox.closest(".review-lesson-option")
                ?.classList.toggle(
                    "selected",
                    checkbox.checked
                );
        });
    }

    function updateSelectedCounts() {
        let lessons = 0;
        let vocabulary = 0;
        let grammar = 0;
        let hanzi = 0;

        lessonCheckboxes.forEach((checkbox) => {
            if (!checkbox.checked) return;

            lessons++;

            vocabulary += Number(
                checkbox.dataset.vocabularyCount || 0
            );

            grammar += Number(
                checkbox.dataset.grammarCount || 0
            );

            hanzi += Number(
                checkbox.dataset.hanziCount || 0
            );
        });

        setText("reviewSelectedLessons", lessons);
        setText("reviewSelectedVocabulary", vocabulary);
        setText("reviewSelectedGrammar", grammar);
        setText("reviewSelectedHanzi", hanzi);
    }

    function getReadingPool() {
        const seen = new Set();

        return reviewWords.filter((word) => {
            const chinese = String(
                word.exampleChinese || ""
            ).trim();

            const vietnamese = String(
                word.exampleVietnamese || ""
            ).trim();

            if (
                !chinese ||
                !vietnamese ||
                seen.has(chinese)
            ) {
                return false;
            }

            seen.add(chinese);
            return true;
        });
    }

    function getListeningPool() {
        return getReadingPool();
    }

    function refreshReviewWords() {
        const ids = selectedLessonIds();

        reviewWords = allVocabulary.filter((word) => {
            return ids.has(Number(word.lessonId));
        });

        currentIndex = 0;
        cardFlipped = false;

        stopAllMedia();
        updateLessonVisuals();
        updateSelectedCounts();
        updateModeAvailability();

        setText("reviewTotalNumber", reviewWords.length);

        const currentCard = modeCards.find(
            (card) => card.dataset.reviewMode === currentMode
        );

        if (currentCard?.disabled) {
            showMode("flashcard", false);
        } else {
            showMode(currentMode, false);
        }
    }

    lessonCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener(
            "change",
            refreshReviewWords
        );
    });

    $("reviewSelectAllButton")?.addEventListener(
        "click",
        function () {
            lessonCheckboxes.forEach((checkbox) => {
                checkbox.checked = true;
            });

            refreshReviewWords();
        }
    );

    $("reviewClearAllButton")?.addEventListener(
        "click",
        function () {
            lessonCheckboxes.forEach((checkbox) => {
                checkbox.checked = false;
            });

            refreshReviewWords();
        }
    );

    /* =====================================================
       5. CHUYỂN CHẾ ĐỘ HỌC
    ===================================================== */

    function updateModeAvailability() {
        const readingCount = getReadingPool().length;
        const listeningCount = getListeningPool().length;

        modeCards.forEach((card) => {
            const mode = card.dataset.reviewMode;
            let enabled = reviewWords.length > 0;

            if (mode === "quiz" || mode === "battle") {
                enabled = reviewWords.length >= 2;
            }

            if (mode === "reading") {
                enabled = readingCount >= 2;
            }

            if (mode === "listening") {
                enabled = listeningCount >= 1;
            }

            if (mode === "typing") {
                enabled = getTypingPool().length > 0;
            }

            card.disabled = !enabled;
        });
    }

    function setActiveMode(mode) {
        modeCards.forEach((card) => {
            const active = card.dataset.reviewMode === mode;

            card.classList.toggle("active", active);

            const status = card.querySelector(
                ".review-mode-status"
            );

            if (status) {
                status.textContent = active
                    ? "Đang học"
                    : "Chưa học";
            }
        });
    }

    function hideAllAreas() {
        Object.values(areas).forEach((area) => {
            if (area) area.hidden = true;
        });
    }

    function showResult(title, correct, total, special = null) {
        stopAllMedia();
        hideAllAreas();

        setHidden("reviewResultArea", false);

        setText("reviewResultTitle", title);
        setText("reviewResultScore", `${correct} / ${total}`);

        setText(
            "reviewResultPercent",
            special || calculatePercent(correct, total) + "%"
        );
    }

    function showMode(mode, scroll = true) {
        stopAllMedia();
        hideAllAreas();

        currentMode = mode;
        setActiveMode(mode);

        if (mode === "flashcard") {
            setHidden("reviewFlashcardShell", false);
            renderCard();
        } else if (mode === "quiz") {
            startQuiz();
        } else if (mode === "typing") {
            startTyping();
        } else if (mode === "reading") {
            startReading();
        } else if (mode === "listening") {
            startListening();
        } else if (mode === "battle") {
            startBattle();
        }

        if (scroll && areas[mode]) {
            setTimeout(() => {
                areas[mode].scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }, 30);
        }
    }

    modeCards.forEach((card) => {
        card.addEventListener("click", function () {
            if (card.disabled) return;
            showMode(card.dataset.reviewMode);
        });
    });

    /* =====================================================
       6. FLASHCARD
    ===================================================== */

    function currentWord() {
        if (!reviewWords.length) return null;

        if (currentIndex >= reviewWords.length) {
            currentIndex = 0;
        }

        if (currentIndex < 0) {
            currentIndex = reviewWords.length - 1;
        }

        return reviewWords[currentIndex] || null;
    }

    function renderCard() {
        stopAudio();

        const word = currentWord();
        const card = $("reviewFlashcard");
        const audioButton = $("reviewAudioButton");

        if (!word) {
            setText("reviewCurrentNumber", 0);
            setText("reviewFrontPinyin", "");
            setText(
                "reviewFrontText",
                "Hãy chọn ít nhất một bài"
            );
            setText(
                "reviewFrontSecondary",
                "để bắt đầu Tổng ôn"
            );

            [
                "reviewBackHanzi",
                "reviewBackPinyin",
                "reviewBackMeaning",
                "reviewBackType",
                "reviewBackExample",
                "reviewBackExampleMeaning"
            ].forEach((id) => setText(id, ""));

            if (audioButton) {
                audioButton.hidden = true;
                audioButton.dataset.audioUrl = "";
            }

            card?.classList.remove("flipped");
            return;
        }

        setText("reviewCurrentNumber", currentIndex + 1);
        card?.classList.toggle("flipped", cardFlipped);

        if (cardView === "example") {
            const chinese =
                word.exampleChinese || "Chưa có câu ví dụ";

            const vietnamese =
                word.exampleVietnamese || "Chưa có bản dịch";

            setText("reviewFrontPinyin", "");
            setText("reviewFrontSecondary", "");

            setText(
                "reviewFrontText",
                direction === "zh-vi" ? chinese : vietnamese
            );

            setText("reviewBackHanzi", chinese);
            setText("reviewBackPinyin", "");
            setText("reviewBackMeaning", vietnamese);

            setText(
                "reviewBackType",
                word.hanzi ? "Từ chính: " + word.hanzi : ""
            );

            setText("reviewBackExample", "");
            setText("reviewBackExampleMeaning", "");

            if (audioButton) {
                audioButton.hidden = true;
                audioButton.dataset.audioUrl = "";
            }
        } else {
            if (direction === "zh-vi") {
                setText("reviewFrontPinyin", word.pinyin);
                setText("reviewFrontText", word.hanzi);
            } else {
                setText("reviewFrontPinyin", "");
                setText("reviewFrontText", word.meaning);
            }

            setText("reviewFrontSecondary", word.type);
            setText("reviewBackHanzi", word.hanzi);
            setText("reviewBackPinyin", word.pinyin);
            setText("reviewBackMeaning", word.meaning);
            setText("reviewBackType", word.type);

            setText(
                "reviewBackExample",
                word.exampleChinese
            );

            setText(
                "reviewBackExampleMeaning",
                word.exampleVietnamese
            );

            if (audioButton) {
                const url = String(
                    word.audioUrl || ""
                ).trim();

                audioButton.hidden = !url;
                audioButton.dataset.audioUrl = url;
            }
        }

        const id = String(word.id);

        $("reviewLearnedButton")?.classList.toggle(
            "active",
            learnedIds.has(id)
        );

        $("reviewNotLearnedButton")?.classList.toggle(
            "active",
            notLearnedIds.has(id)
        );
    }

    function flipCard() {
        if (!reviewWords.length) return;

        cardFlipped = !cardFlipped;

        $("reviewFlashcard")?.classList.toggle(
            "flipped",
            cardFlipped
        );
    }

    $("reviewFlashcard")?.addEventListener(
        "click",
        function (event) {
            if (event.target.closest("#reviewAudioButton")) {
                return;
            }

            flipCard();
        }
    );

    $("reviewFlashcard")?.addEventListener(
        "keydown",
        function (event) {
            if (
                event.target !== event.currentTarget ||
                !["Enter", " "].includes(event.key)
            ) {
                return;
            }

            event.preventDefault();
            flipCard();
        }
    );

    function nextCard() {
        if (!reviewWords.length) return;

        currentIndex =
            (currentIndex + 1) % reviewWords.length;

        cardFlipped = false;
        renderCard();
    }

    function previousCard() {
        if (!reviewWords.length) return;

        currentIndex =
            (currentIndex - 1 + reviewWords.length) %
            reviewWords.length;

        cardFlipped = false;
        renderCard();
    }

    $("reviewNextButton")?.addEventListener(
        "click",
        nextCard
    );

    $("reviewPreviousButton")?.addEventListener(
        "click",
        previousCard
    );

    /* =====================================================
       7. FLASHCARD - ĐÃ THUỘC / CHƯA THUỘC
    ===================================================== */

    $("reviewLearnedButton")?.addEventListener(
        "click",
        function () {
            const word = currentWord();
            if (!word) return;

            const id = String(word.id);

            learnedIds.add(id);
            notLearnedIds.delete(id);

            // Đã thuộc tương ứng mức nhớ 3 - Tốt.
            recordReview(word, 3);

            nextCard();
        }
    );

    $("reviewNotLearnedButton")?.addEventListener(
        "click",
        function () {
            const word = currentWord();
            if (!word) return;

            const id = String(word.id);

            notLearnedIds.add(id);
            learnedIds.delete(id);

            // Chưa thuộc tương ứng mức nhớ 1.
            recordReview(word, 1);

            nextCard();
        }
    );

    /* =====================================================
       8. CÀI ĐẶT FLASHCARD
    ===================================================== */

    $("reviewWordModeButton")?.addEventListener(
        "click",
        function () {
            cardView = "word";
            cardFlipped = false;

            this.classList.add("active");

            $("reviewExampleModeButton")
                ?.classList.remove("active");

            renderCard();
        }
    );

    $("reviewExampleModeButton")?.addEventListener(
        "click",
        function () {
            cardView = "example";
            cardFlipped = false;

            this.classList.add("active");

            $("reviewWordModeButton")
                ?.classList.remove("active");

            renderCard();
        }
    );

    $("reviewDirectionButton")?.addEventListener(
        "click",
        function () {
            direction =
                direction === "zh-vi" ? "vi-zh" : "zh-vi";

            this.textContent = direction === "zh-vi"
                ? "⇄ ZH → VI"
                : "⇄ VI → ZH";

            cardFlipped = false;
            renderCard();
        }
    );

    $("reviewShuffleButton")?.addEventListener(
        "click",
        function () {
            reviewWords = shuffle(reviewWords);
            currentIndex = 0;
            cardFlipped = false;
            renderCard();
        }
    );

    $("reviewAutoButton")?.addEventListener(
        "click",
        function () {
            if (autoTimer !== null) {
                stopAutoPlay();
                return;
            }

            if (!reviewWords.length) return;

            this.classList.add("active");
            this.textContent = "Ⅱ Dừng";

            autoTimer = setInterval(function () {
                if (!cardFlipped) {
                    cardFlipped = true;

                    $("reviewFlashcard")
                        ?.classList.add("flipped");
                } else {
                    nextCard();
                }
            }, 2500);
        }
    );

    /* =====================================================
       9. AUDIO FLASHCARD
    ===================================================== */

    $("reviewAudioButton")?.addEventListener(
        "click",
        function (event) {
            event.stopPropagation();

            const url = String(
                this.dataset.audioUrl || ""
            ).trim();

            if (!url) return;

            stopAudio();

            const audio = new Audio(url);
            currentAudio = audio;

            const button = this;
            button.classList.add("is-playing");

            function clearAudio() {
                button.classList.remove("is-playing");

                if (currentAudio === audio) {
                    currentAudio = null;
                }
            }

            audio.addEventListener("ended", clearAudio);
            audio.addEventListener("error", clearAudio);

            audio.play().catch((error) => {
                console.error(
                    "Không phát được audio:",
                    error
                );
                clearAudio();
            });
        }
    );

    /* =====================================================
       10. TRẮC NGHIỆM
    ===================================================== */

    function startQuiz() {
        hideAllAreas();
        setHidden("reviewQuizArea", false);

        quizQuestions = shuffle(reviewWords).slice(0, 20);
        quizIndex = 0;
        quizCorrect = 0;

        renderQuizQuestion();
    }

    function renderQuizQuestion() {
        const word = quizQuestions[quizIndex];

        if (!word) {
            showResult(
                "Kết quả Trắc nghiệm",
                quizCorrect,
                quizQuestions.length
            );
            return;
        }

        quizAnswered = false;

        setText(
            "reviewQuizProgress",
            `Câu ${quizIndex + 1} / ${quizQuestions.length}`
        );

        setText("reviewQuizQuestion", word.hanzi);
        setText("reviewQuizPinyin", word.pinyin);

        setHidden("reviewQuizNextButton", true);
        setFeedback("reviewQuizFeedback", "");

        const container = $("reviewQuizOptions");
        if (!container) return;

        container.innerHTML = "";

        const options = buildOptions(
            String(word.meaning || ""),
            reviewWords
                .filter((item) => item.id !== word.id)
                .map((item) => item.meaning)
        );

        options.forEach((answer) => {
            const button = createOption(
                answer,
                function (selectedButton) {
                    if (quizAnswered) return;

                    quizAnswered = true;

                    markOptions(container, word.meaning);

                    const correct = answer === word.meaning;

                    if (correct) {
                        quizCorrect++;
                        selectedButton.classList.add("correct");

                        setFeedback(
                            "reviewQuizFeedback",
                            "✓ Chính xác!",
                            "correct"
                        );
                    } else {
                        selectedButton.classList.add("wrong");

                        setFeedback(
                            "reviewQuizFeedback",
                            "✕ Chưa đúng. Đáp án: " +
                                word.meaning,
                            "wrong"
                        );
                    }

                    // Đúng: 3, sai: 1.
                    recordReview(word, correct ? 3 : 1);

                    setHidden(
                        "reviewQuizNextButton",
                        false
                    );
                }
            );

            container.appendChild(button);
        });
    }

    $("reviewQuizNextButton")?.addEventListener(
        "click",
        function () {
            quizIndex++;
            renderQuizQuestion();
        }
    );

    /* =====================================================
       11. GÕ CHỮ HÁN / GÕ PINYIN
    ===================================================== */

    function getTypingMode() {
        const selected = typingModeInputs.find(
            (input) => input.checked
        );

        return selected?.value === "pinyin"
            ? "pinyin"
            : "hanzi";
    }

    function getTypingPool() {
        const mode = getTypingMode();

        return reviewWords.filter((word) => {
            const expected = mode === "pinyin"
                ? word.pinyin
                : word.hanzi;

            return (
                String(word.meaning || "").trim() &&
                String(expected || "").trim()
            );
        });
    }

    function startTyping() {
        hideAllAreas();
        setHidden("reviewTypingArea", false);

        typingQuestions = shuffle(
            getTypingPool()
        ).slice(0, 20);

        typingIndex = 0;
        typingCorrect = 0;

        renderTypingQuestion();
    }

    function renderTypingQuestion() {
        const word = typingQuestions[typingIndex];
        const mode = getTypingMode();

        if (!word) {
            showResult(
                mode === "pinyin"
                    ? "Kết quả Gõ Pinyin"
                    : "Kết quả Gõ chữ Hán",
                typingCorrect,
                typingQuestions.length
            );
            return;
        }

        typingAnswered = false;

        setText(
            "reviewTypingProgress",
            `Câu ${typingIndex + 1} / ${typingQuestions.length}`
        );

        if (mode === "pinyin") {
            setText(
                "reviewTypingQuestion",
                word.hanzi || ""
            );

            setText(
                "reviewTypingHint",
                word.meaning
                    ? "Nghĩa: " + word.meaning
                    : "Hãy nhập Pinyin của từ này."
            );
        } else {
            setText(
                "reviewTypingQuestion",
                word.meaning || ""
            );

            setText(
                "reviewTypingHint",
                word.pinyin
                    ? "Gợi ý phát âm: " + word.pinyin
                    : "Nhập chữ Hán tương ứng."
            );
        }

        const input = $("reviewTypingInput");
        const checkButton = $("reviewTypingCheckButton");

        if (input) {
            input.value = "";
            input.disabled = false;

            input.placeholder = mode === "pinyin"
                ? "Ví dụ: xuexi hoặc xuéxí"
                : "Nhập chữ Hán...";

            setTimeout(function () {
                if (
                    currentMode === "typing" &&
                    !input.disabled
                ) {
                    input.focus();
                }
            }, 30);
        }

        if (checkButton) {
            checkButton.disabled = false;
        }

        setHidden("reviewTypingNextButton", true);
        setFeedback("reviewTypingFeedback", "");
    }

    function checkTypingAnswer() {
        if (typingAnswered) return;

        const word = typingQuestions[typingIndex];
        const input = $("reviewTypingInput");

        if (!word || !input) return;

        const mode = getTypingMode();
        const rawAnswer = input.value.trim();

        if (!rawAnswer) {
            setFeedback(
                "reviewTypingFeedback",
                "Bạn chưa nhập đáp án.",
                "wrong"
            );
            return;
        }

        const expected = mode === "pinyin"
            ? String(word.pinyin || "")
            : String(word.hanzi || "");

        const answer = mode === "pinyin"
            ? normalizePinyin(rawAnswer)
            : normalizeText(rawAnswer);

        const correctAnswer = mode === "pinyin"
            ? normalizePinyin(expected)
            : normalizeText(expected);

        if (!answer) {
            setFeedback(
                "reviewTypingFeedback",
                "Đáp án không hợp lệ.",
                "wrong"
            );
            return;
        }

        typingAnswered = true;
        input.disabled = true;

        const checkButton = $("reviewTypingCheckButton");

        if (checkButton) {
            checkButton.disabled = true;
        }

        const correct = answer === correctAnswer;

        if (correct) {
            typingCorrect++;

            setFeedback(
                "reviewTypingFeedback",
                "✓ Chính xác! " +
                    word.hanzi + " · " +
                    word.pinyin + " · " +
                    word.meaning,
                "correct"
            );
        } else {
            setFeedback(
                "reviewTypingFeedback",
                "✕ Chưa đúng. Đáp án: " +
                    expected +
                    (mode === "pinyin"
                        ? " (" + word.hanzi + ")"
                        : " — " + word.meaning),
                "wrong"
            );
        }

        // Ghi nhận đúng một lần cho mỗi câu.
        recordReview(word, correct ? 3 : 1);

        setHidden("reviewTypingNextButton", false);
    }

    typingModeInputs.forEach((input) => {
        input.addEventListener("change", function () {
            if (!this.checked) return;

            if (currentMode === "typing") {
                startTyping();
            }
        });
    });

    $("reviewTypingCheckButton")?.addEventListener(
        "click",
        checkTypingAnswer
    );

    $("reviewTypingInput")?.addEventListener(
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

            if (typingAnswered) {
                typingIndex++;
                renderTypingQuestion();
            } else {
                checkTypingAnswer();
            }
        }
    );

    $("reviewTypingNextButton")?.addEventListener(
        "click",
        function () {
            typingIndex++;
            renderTypingQuestion();
        }
    );

    /* =====================================================
       12. ĐỌC HIỂU
    ===================================================== */

    function startReading() {
        hideAllAreas();
        setHidden("reviewReadingArea", false);

        readingQuestions = shuffle(
            getReadingPool()
        ).slice(0, 15);

        readingIndex = 0;
        readingCorrect = 0;

        renderReadingQuestion();
    }

    function renderReadingQuestion() {
        const word = readingQuestions[readingIndex];

        if (!word) {
            showResult(
                "Kết quả Đọc hiểu",
                readingCorrect,
                readingQuestions.length
            );
            return;
        }

        readingAnswered = false;

        setText(
            "reviewReadingProgress",
            `Câu ${readingIndex + 1} / ${readingQuestions.length}`
        );

        setText(
            "reviewReadingChinese",
            word.exampleChinese
        );

        setHidden("reviewReadingNextButton", true);
        setFeedback("reviewReadingFeedback", "");

        const container = $("reviewReadingOptions");
        if (!container) return;

        container.innerHTML = "";

        const options = buildOptions(
            String(word.exampleVietnamese || ""),
            getReadingPool()
                .filter((item) => {
                    return (
                        item.exampleChinese !==
                        word.exampleChinese
                    );
                })
                .map((item) => item.exampleVietnamese)
        );

        options.forEach((answer) => {
            const button = createOption(
                answer,
                function (selectedButton) {
                    if (readingAnswered) return;

                    readingAnswered = true;

                    markOptions(
                        container,
                        word.exampleVietnamese
                    );

                    const correct =
                        answer === word.exampleVietnamese;

                    if (correct) {
                        readingCorrect++;
                        selectedButton.classList.add("correct");

                        setFeedback(
                            "reviewReadingFeedback",
                            "✓ Chính xác!",
                            "correct"
                        );
                    } else {
                        selectedButton.classList.add("wrong");

                        setFeedback(
                            "reviewReadingFeedback",
                            "✕ Đáp án: " +
                                word.exampleVietnamese,
                            "wrong"
                        );
                    }

                    recordReview(word, correct ? 3 : 1);

                    setHidden(
                        "reviewReadingNextButton",
                        false
                    );
                }
            );

            container.appendChild(button);
        });
    }

    $("reviewReadingNextButton")?.addEventListener(
        "click",
        function () {
            readingIndex++;
            renderReadingQuestion();
        }
    );

    /* =====================================================
       13. NGHE GHÉP CÂU
    ===================================================== */

    function tokenizeChineseSentence(sentence) {
        const text = String(sentence || "")
            .replace(/\s+/g, "")
            .replace(
                /[，。！？、；：,.!?;:“”"'（）()《》]/g,
                ""
            );

        const knownWords = uniqueValues(
            reviewWords.map((word) => word.hanzi)
        ).sort((a, b) => b.length - a.length);

        const tokens = [];
        let index = 0;

        while (index < text.length) {
            let matched = "";

            for (const candidate of knownWords) {
                if (
                    candidate.length > 1 &&
                    text.startsWith(candidate, index)
                ) {
                    matched = candidate;
                    break;
                }
            }

            if (matched) {
                tokens.push(matched);
                index += matched.length;
            } else {
                const character = Array.from(
                    text.slice(index)
                )[0];

                if (!character) break;

                tokens.push(character);
                index += character.length;
            }
        }

        return tokens;
    }

    function speakListeningSentence() {
        const item = listeningQuestions[listeningIndex];

        if (
            !item ||
            !("speechSynthesis" in window)
        ) {
            return;
        }

        stopSpeech();

        const utterance = new SpeechSynthesisUtterance(
            item.exampleChinese
        );

        utterance.lang = "zh-CN";
        utterance.rate = listeningSpeed;

        window.speechSynthesis.speak(utterance);
    }

    function startListening() {
        hideAllAreas();
        setHidden("reviewListeningArea", false);

        listeningQuestions = shuffle(
            getListeningPool()
        ).slice(0, 15);

        listeningIndex = 0;
        listeningCorrect = 0;

        renderListeningQuestion();
    }

    function renderListeningQuestion() {
        const item = listeningQuestions[listeningIndex];

        if (!item) {
            showResult(
                "Kết quả Nghe ghép câu",
                listeningCorrect,
                listeningQuestions.length
            );
            return;
        }

        listeningSolved = false;
        listeningHadWrongAttempt = false;
        listeningSelected = [];

        const rawTokens = tokenizeChineseSentence(
            item.exampleChinese
        );

        listeningTokens = shuffle(
            rawTokens.map((text, index) => ({
                id: `${listeningIndex}-${index}`,
                text
            }))
        );

        setText(
            "reviewListeningProgress",
            `Câu ${listeningIndex + 1} / ${listeningQuestions.length}`
        );

        setHidden("reviewListeningNextButton", true);
        setFeedback("reviewListeningFeedback", "");

        renderListeningTokens();
    }

    function renderListeningTokens() {
        const slots = $("reviewListeningSlots");
        const bank = $("reviewListeningTokenBank");

        if (!slots || !bank) return;

        slots.innerHTML = "";
        bank.innerHTML = "";

        listeningSelected.forEach((item) => {
            const button = createOption(
                item.text,
                function () {
                    if (listeningSolved) return;

                    listeningSelected = listeningSelected.filter(
                        (selected) => selected.id !== item.id
                    );

                    setFeedback(
                        "reviewListeningFeedback",
                        ""
                    );

                    renderListeningTokens();
                }
            );

            slots.appendChild(button);
        });

        listeningTokens
            .filter((item) => {
                return !listeningSelected.some(
                    (selected) => selected.id === item.id
                );
            })
            .forEach((item) => {
                const button = createOption(
                    item.text,
                    function () {
                        if (listeningSolved) return;

                        listeningSelected.push(item);
                        renderListeningTokens();
                        checkListeningAnswer();
                    }
                );

                bank.appendChild(button);
            });
    }

    function checkListeningAnswer() {
        const item = listeningQuestions[listeningIndex];
        if (!item || listeningSolved) return;

        const expectedTokens = tokenizeChineseSentence(
            item.exampleChinese
        );

        if (
            listeningSelected.length !==
            expectedTokens.length
        ) {
            return;
        }

        const answer = normalizeText(
            listeningSelected
                .map((token) => token.text)
                .join("")
        );

        const expected = normalizeText(
            item.exampleChinese
        );

        if (answer === expected) {
            listeningSolved = true;

            if (!listeningHadWrongAttempt) {
                listeningCorrect++;
            }

            setFeedback(
                "reviewListeningFeedback",
                "✓ Chính xác! " + item.exampleVietnamese,
                "correct"
            );

            // Nếu từng ghép sai, mức nhớ thấp hơn.
            recordReview(
                item,
                listeningHadWrongAttempt ? 2 : 3
            );

            setHidden(
                "reviewListeningNextButton",
                false
            );
        } else {
            listeningHadWrongAttempt = true;

            setFeedback(
                "reviewListeningFeedback",
                "✕ Thứ tự chưa đúng. " +
                    "Bấm các thẻ đã ghép để sửa lại.",
                "wrong"
            );
        }
    }

    $("reviewListeningPlayButton")?.addEventListener(
        "click",
        speakListeningSentence
    );

    speedButtons.forEach((button) => {
        button.addEventListener("click", function () {
            listeningSpeed = Number(
                this.dataset.reviewSpeed || 1
            );

            speedButtons.forEach((item) => {
                item.classList.remove("active");
            });

            this.classList.add("active");
            speakListeningSentence();
        });
    });

    $("reviewListeningNextButton")?.addEventListener(
        "click",
        function () {
            listeningIndex++;
            stopSpeech();
            renderListeningQuestion();
        }
    );

    /* =====================================================
       14. ĐẤU TRÍ
    ===================================================== */

    function buildBattleQuestion(word, index) {
        const chineseToVietnamese = index % 2 === 0;

        if (chineseToVietnamese) {
            return {
                word,
                label: "CHỌN NGHĨA ĐÚNG",
                main: word.hanzi,
                secondary: word.pinyin || "",
                correct: word.meaning,
                options: buildOptions(
                    word.meaning,
                    reviewWords
                        .filter((item) => item.id !== word.id)
                        .map((item) => item.meaning)
                )
            };
        }

        return {
            word,
            label: "CHỌN CHỮ HÁN ĐÚNG",
            main: word.meaning,
            secondary: "",
            correct: word.hanzi,
            options: buildOptions(
                word.hanzi,
                reviewWords
                    .filter((item) => item.id !== word.id)
                    .map((item) => item.hanzi)
            )
        };
    }

    function startBattle() {
        hideAllAreas();
        setHidden("reviewBattleArea", false);

        battleQuestions = shuffle(reviewWords)
            .slice(0, 10)
            .map((word, index) => {
                return buildBattleQuestion(word, index);
            });

        battleIndex = 0;
        battleCorrect = 0;
        battlePoints = 0;

        renderBattleQuestion();
    }

    function updateBattleStats() {
        setText(
            "reviewBattlePoints",
            battlePoints + " điểm"
        );

        setText(
            "reviewBattleTimer",
            battleTimeLeft + "s"
        );
    }

    function beginBattleTimer() {
        stopBattleTimer();

        battleTimeLeft = 15;
        updateBattleStats();

        battleTimer = setInterval(function () {
            battleTimeLeft--;
            updateBattleStats();

            if (battleTimeLeft <= 0) {
                stopBattleTimer();
                answerBattle(null, null, true);
            }
        }, 1000);
    }

    function renderBattleQuestion() {
        const item = battleQuestions[battleIndex];

        if (!item) {
            showResult(
                "Kết quả Đấu trí",
                battleCorrect,
                battleQuestions.length,
                battlePoints + " điểm"
            );
            return;
        }

        battleAnswered = false;

        setText(
            "reviewBattleProgress",
            `Câu ${battleIndex + 1} / ${battleQuestions.length}`
        );

        setText(
            "reviewBattleQuestionLabel",
            item.label
        );

        setText("reviewBattleQuestion", item.main);
        setText(
            "reviewBattleSecondary",
            item.secondary
        );

        setHidden("reviewBattleNextButton", true);
        setFeedback("reviewBattleFeedback", "");

        const container = $("reviewBattleOptions");
        if (!container) return;

        container.innerHTML = "";

        item.options.forEach((answer) => {
            const button = createOption(
                answer,
                function (selectedButton) {
                    answerBattle(
                        selectedButton,
                        answer,
                        false
                    );
                }
            );

            container.appendChild(button);
        });

        beginBattleTimer();
    }

    function answerBattle(selectedButton, answer, timedOut) {
        if (battleAnswered) return;

        const item = battleQuestions[battleIndex];
        if (!item) return;

        battleAnswered = true;
        stopBattleTimer();

        markOptions(
            $("reviewBattleOptions"),
            item.correct
        );

        const correct =
            !timedOut && answer === item.correct;

        if (timedOut) {
            setFeedback(
                "reviewBattleFeedback",
                "⌛ Hết giờ. Đáp án: " + item.correct,
                "wrong"
            );
        } else if (correct) {
            battleCorrect++;

            const gained = 100 + battleTimeLeft * 5;
            battlePoints += gained;

            selectedButton?.classList.add("correct");

            setFeedback(
                "reviewBattleFeedback",
                "✓ Chính xác! +" + gained + " điểm",
                "correct"
            );
        } else {
            selectedButton?.classList.add("wrong");

            setFeedback(
                "reviewBattleFeedback",
                "✕ Chưa đúng. Đáp án: " + item.correct,
                "wrong"
            );
        }

        // Hết giờ hoặc trả lời sai đều ghi mức 1.
        recordReview(item.word, correct ? 3 : 1);

        updateBattleStats();
        setHidden("reviewBattleNextButton", false);
    }

    $("reviewBattleNextButton")?.addEventListener(
        "click",
        function () {
            battleIndex++;
            renderBattleQuestion();
        }
    );

    /* =====================================================
       15. KẾT QUẢ VÀ LÀM LẠI
    ===================================================== */

    $("reviewRestartButton")?.addEventListener(
        "click",
        function () {
            showMode(currentMode);
        }
    );

    $("reviewBackFlashcardButton")?.addEventListener(
        "click",
        function () {
            showMode("flashcard");
        }
    );

    /* =====================================================
       16. KHỞI TẠO
    ===================================================== */

    updateLessonVisuals();
    updateSelectedCounts();
    updateModeAvailability();

    setText(
        "reviewTotalNumber",
        reviewWords.length
    );

    setActiveMode("flashcard");
    setHidden("reviewFlashcardShell", false);

    renderCard();

    /* =====================================================
       17. RỜI TRANG
    ===================================================== */

    window.addEventListener("beforeunload", function () {
        stopAllMedia();
    });

    console.log(
        "Mộc Hán - Tổng ôn đã tải:",
        reviewWords.length,
        "từ vựng"
    );

    console.log(
        "API lưu lịch sử:",
        REVIEW_SAVE_URL
    );

    if (!getCsrfToken()) {
        console.warn(
            "Chưa tìm thấy CSRF token trên trang Tổng ôn. " +
            "Nếu Flask bật CSRFProtect, yêu cầu POST " +
            "có thể bị từ chối."
        );
    }
});
