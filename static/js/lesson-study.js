document.addEventListener("DOMContentLoaded", function () {

    /* =========================================================
       AUDIO TỪ VỰNG / CHỮ HÁN
    ========================================================= */

    let currentLessonAudio = null;
    let currentLessonAudioButton = null;


    const flashcardAudioButton =
        document.getElementById(
            "vocabFlashcardAudioButton"
        );


    function resetCurrentAudioButton() {

        if (
            currentLessonAudioButton
        ) {

            currentLessonAudioButton.classList.remove(
                "is-playing"
            );

        }

        currentLessonAudioButton = null;

    }


    function stopCurrentLessonAudio() {

        if (
            currentLessonAudio
        ) {

            currentLessonAudio.pause();

            currentLessonAudio.currentTime = 0;

            currentLessonAudio = null;

        }

        resetCurrentAudioButton();

    }


    function playLessonAudio(
        audioUrl,
        button
    ) {

        if (
            !audioUrl
        ) {

            return;

        }


        /*
         * Nếu đang phát đúng audio này
         * mà bấm lại thì dừng.
         */
        if (
            currentLessonAudio
            &&
            currentLessonAudioButton === button
            &&
            !currentLessonAudio.paused
        ) {

            stopCurrentLessonAudio();

            return;

        }


        /*
         * Dừng audio trước đó
         * để không bị phát chồng.
         */
        stopCurrentLessonAudio();


        const audio =
            new Audio(
                audioUrl
            );


        audio.preload =
            "auto";


        currentLessonAudio =
            audio;


        currentLessonAudioButton =
            button;


        if (
            button
        ) {

            button.classList.add(
                "is-playing"
            );

        }


        audio.addEventListener(
            "ended",
            function () {

                if (
                    currentLessonAudio
                    === audio
                ) {

                    currentLessonAudio =
                        null;

                }


                resetCurrentAudioButton();

            }
        );


        audio.addEventListener(
            "error",
            function () {

                console.error(
                    "Không phát được audio:",
                    audioUrl
                );


                if (
                    currentLessonAudio
                    === audio
                ) {

                    currentLessonAudio =
                        null;

                }


                resetCurrentAudioButton();

            }
        );


        audio.play().catch(
            function (error) {

                console.error(
                    "Trình duyệt không phát được audio:",
                    error
                );


                if (
                    currentLessonAudio
                    === audio
                ) {

                    currentLessonAudio =
                        null;

                }


                resetCurrentAudioButton();

            }
        );

    }


    /*
     * Xử lý nút loa:
     *
     * - Flashcard
     * - Danh sách từ vựng
     * - Chữ Hán
     */
    document.addEventListener(
        "click",
        function (event) {

            const audioButton =
                event.target.closest(
                    ".lesson-audio-button"
                );


            if (
                !audioButton
            ) {

                return;

            }


            event.preventDefault();

            event.stopPropagation();


            const audioUrl =
                audioButton.dataset.audioUrl
                || "";


            playLessonAudio(
                audioUrl,
                audioButton
            );

        }
    );



    /* =========================================================
       1. TAB TỪ VỰNG / NGỮ PHÁP / CHỮ HÁN
    ========================================================= */

    const lessonTabs =
        document.querySelectorAll(
            ".lesson-learning-tab"
        );


    const lessonPanels =
        document.querySelectorAll(
            ".lesson-tab-panel"
        );


    lessonTabs.forEach(
        function (tab) {

            tab.addEventListener(
                "click",
                function () {

                    const target =
                        tab.dataset.lessonTab;


                    /*
                     * Khi đổi tab thì dừng audio.
                     */
                    stopCurrentLessonAudio();


                    lessonTabs.forEach(
                        function (item) {

                            item.classList.remove(
                                "active"
                            );

                        }
                    );


                    lessonPanels.forEach(
                        function (panel) {

                            panel.classList.remove(
                                "active"
                            );

                        }
                    );


                    tab.classList.add(
                        "active"
                    );


                    const targetPanel =
                        document.getElementById(
                            "lesson-panel-"
                            + target
                        );


                    if (
                        targetPanel
                    ) {

                        targetPanel.classList.add(
                            "active"
                        );

                    }

                }
            );

        }
    );



    /* =========================================================
       2. ĐỌC DỮ LIỆU TỪ VỰNG
    ========================================================= */

    const dataElement =
        document.getElementById(
            "lessonVocabularyData"
        );


    let vocabularies = [];


    if (
        dataElement
    ) {

        try {

            vocabularies =
                JSON.parse(
                    dataElement.textContent
                );

        }
        catch (
            error
        ) {

            console.error(
                "Không đọc được dữ liệu từ vựng:",
                error
            );

            return;

        }

    }


    if (
        vocabularies.length === 0
    ) {

        return;

    }



    /* =========================================================
       3. ELEMENT CHUNG
    ========================================================= */

    const studyPage =
        document.getElementById(
            "lessonStudyPage"
        );


    const lessonId =
        studyPage
            ? studyPage.dataset.lessonId
            : "unknown";


    /* FLASHCARD */

    const flashcardToolbar =
        document.querySelector(
            ".vocab-study-toolbar"
        );


    const flashcardShell =
        document.querySelector(
            ".vocab-flashcard-shell"
        );


    const flashcard =
        document.getElementById(
            "vocabFlashcard"
        );


    const frontText =
        document.getElementById(
            "vocabFrontText"
        );


    const frontType =
        document.getElementById(
            "vocabFrontType"
        );


    const backHanzi =
        document.getElementById(
            "vocabBackHanzi"
        );


    const backPinyin =
        document.getElementById(
            "vocabBackPinyin"
        );


    const backMeaning =
        document.getElementById(
            "vocabBackMeaning"
        );


    const backExample =
        document.getElementById(
            "vocabBackExample"
        );


    const currentNumber =
        document.getElementById(
            "vocabCurrentNumber"
        );


    const previousButton =
        document.getElementById(
            "vocabPreviousButton"
        );


    const nextButton =
        document.getElementById(
            "vocabNextButton"
        );


    const learnedButton =
        document.getElementById(
            "vocabLearnedButton"
        );


    const notLearnedButton =
        document.getElementById(
            "vocabNotLearnedButton"
        );


    const shuffleButton =
        document.getElementById(
            "vocabShuffleButton"
        );


    const directionButton =
        document.getElementById(
            "vocabDirectionButton"
        );


    const wordModeButton =
        document.getElementById(
            "vocabModeWord"
        );


    const exampleModeButton =
        document.getElementById(
            "vocabModeExample"
        );


    /* DANH SÁCH TỪ */

    const detailCards =
        document.querySelectorAll(
            ".vocab-detail-card"
        );


    const reviewButtons =
        document.querySelectorAll(
            ".vocab-review-one"
        );


    const addAllReviewButton =
        document.getElementById(
            "addAllReviewButton"
        );


    const printButton =
        document.getElementById(
            "printLessonButton"
        );



    /* =========================================================
       4. LOCAL STORAGE
    ========================================================= */

    const statusStorageKey =
        "moc_han_lesson_"
        + lessonId
        + "_vocab_status";


    const reviewStorageKey =
        "moc_han_lesson_"
        + lessonId
        + "_vocab_review";


    let statuses = {};

    let reviewWords = [];


    try {

        statuses =
            JSON.parse(
                localStorage.getItem(
                    statusStorageKey
                )
            ) || {};

    }
    catch (
        error
    ) {

        statuses = {};

    }


    try {

        reviewWords =
            JSON.parse(
                localStorage.getItem(
                    reviewStorageKey
                )
            ) || [];

    }
    catch (
        error
    ) {

        reviewWords = [];

    }


    function saveStatuses() {

        localStorage.setItem(
            statusStorageKey,
            JSON.stringify(
                statuses
            )
        );

    }


    function saveReviewWords() {

        localStorage.setItem(
            reviewStorageKey,
            JSON.stringify(
                reviewWords
            )
        );

    }



    /* =========================================================
       5. HÀM DÙNG CHUNG
    ========================================================= */

    function shuffledArray(
        array
    ) {

        const copy =
            [
                ...array
            ];


        for (
            let i = copy.length - 1;
            i > 0;
            i--
        ) {

            const j =
                Math.floor(
                    Math.random()
                    * (i + 1)
                );


            [
                copy[i],
                copy[j]
            ] =
            [
                copy[j],
                copy[i]
            ];

        }


        return copy;

    }


    function escapeHtml(
        value
    ) {

        const div =
            document.createElement(
                "div"
            );


        div.textContent =
            value || "";


        return div.innerHTML;

    }



    /* =========================================================
       6. FLASHCARD - STATE
    ========================================================= */

    let order =
        vocabularies.map(
            function (
                _,
                index
            ) {

                return index;

            }
        );


    let currentPosition = 0;

    let direction =
        "zh-vi";


    let cardMode =
        "word";


    let flipped =
        false;


    function getCurrentOriginalIndex() {

        return order[
            currentPosition
        ];

    }


    function getCurrentWord() {

        return vocabularies[
            getCurrentOriginalIndex()
        ];

    }



    /* =========================================================
       7. UPDATE CARD DANH SÁCH
    ========================================================= */

    function updateDetailCards() {

        const currentOriginalIndex =
            getCurrentOriginalIndex();


        detailCards.forEach(
            function (
                card
            ) {

                const index =
                    Number(
                        card.dataset.vocabIndex
                    );


                card.classList.remove(
                    "active",
                    "learned",
                    "not-learned"
                );


                if (
                    index
                    === currentOriginalIndex
                ) {

                    card.classList.add(
                        "active"
                    );

                }


                const word =
                    vocabularies[
                        index
                    ];


                if (
                    !word
                ) {

                    return;

                }


                const status =
                    statuses[
                        String(
                            word.id
                        )
                    ];


                if (
                    status
                    === "learned"
                ) {

                    card.classList.add(
                        "learned"
                    );

                }


                if (
                    status
                    === "not-learned"
                ) {

                    card.classList.add(
                        "not-learned"
                    );

                }


                const starButton =
                    card.querySelector(
                        ".vocab-review-one"
                    );


                if (
                    starButton
                ) {

                    const saved =
                        reviewWords.includes(
                            String(
                                word.id
                            )
                        );


                    starButton.textContent =
                        saved
                            ? "★"
                            : "☆";


                    starButton.classList.toggle(
                        "saved",
                        saved
                    );

                }

            }
        );

    }



    /* =========================================================
       8. RENDER FLASHCARD
    ========================================================= */

    function renderCard() {

        const word =
            getCurrentWord();


        if (
            !word
        ) {

            return;

        }


        /*
         * Đổi từ thì dừng audio cũ.
         */
        stopCurrentLessonAudio();


        /*
         * Gắn audio của từ hiện tại
         * vào nút nghe trên Flashcard.
         */
        if (
            flashcardAudioButton
        ) {

            const audioUrl =
                word.audioUrl
                || "";


            flashcardAudioButton.dataset.audioUrl =
                audioUrl;


            flashcardAudioButton.hidden =
                !audioUrl;

        }


        if (
            currentNumber
        ) {

            currentNumber.textContent =
                currentPosition + 1;

        }


        flipped =
            false;


        if (
            flashcard
        ) {

            flashcard.classList.remove(
                "flipped"
            );

        }


        /* ==============================
           MẶT TRƯỚC
        ============================== */

        if (
            direction
            === "zh-vi"
        ) {

            if (
                cardMode
                === "example"
                &&
                word.exampleChinese
            ) {

                frontText.textContent =
                    word.exampleChinese;


                frontType.textContent =
                    "Ví dụ";

            }
            else {

                frontText.textContent =
                    word.hanzi;


                frontType.textContent =
                    word.type
                    || "Từ vựng";

            }

        }
        else {

            if (
                cardMode
                === "example"
                &&
                word.exampleVietnamese
            ) {

                frontText.textContent =
                    word.exampleVietnamese;


                frontType.textContent =
                    "Ví dụ";

            }
            else {

                frontText.textContent =
                    word.meaning;


                frontType.textContent =
                    word.type
                    || "Từ vựng";

            }

        }


        /* ==============================
           MẶT SAU
        ============================== */

        backHanzi.textContent =
            word.hanzi
            || "";


        backPinyin.textContent =
            word.pinyin
            || "";


        backMeaning.textContent =
            word.meaning
            || "";


        let exampleText =
            "";


        if (
            word.exampleChinese
        ) {

            exampleText +=
                word.exampleChinese;

        }


        if (
            word.exampleChinese
            &&
            word.exampleVietnamese
        ) {

            exampleText +=
                " — ";

        }


        if (
            word.exampleVietnamese
        ) {

            exampleText +=
                word.exampleVietnamese;

        }


        if (
            exampleText
        ) {

            backExample.textContent =
                exampleText;


            backExample.style.display =
                "block";

        }
        else {

            backExample.textContent =
                "";


            backExample.style.display =
                "none";

        }


        updateDetailCards();

    }



    /* =========================================================
       9. FLASHCARD EVENTS
    ========================================================= */

    if (
        flashcard
    ) {

        flashcard.addEventListener(
            "click",
            function () {

                flipped =
                    !flipped;


                flashcard.classList.toggle(
                    "flipped",
                    flipped
                );

            }
        );

    }


    if (
        previousButton
    ) {

        previousButton.addEventListener(
            "click",
            function () {

                currentPosition--;


                if (
                    currentPosition
                    < 0
                ) {

                    currentPosition =
                        order.length
                        - 1;

                }


                renderCard();

            }
        );

    }


    if (
        nextButton
    ) {

        nextButton.addEventListener(
            "click",
            function () {

                currentPosition++;


                if (
                    currentPosition
                    >= order.length
                ) {

                    currentPosition =
                        0;

                }


                renderCard();

            }
        );

    }


    if (
        learnedButton
    ) {

        learnedButton.addEventListener(
            "click",
            function () {

                const word =
                    getCurrentWord();


                statuses[
                    String(
                        word.id
                    )
                ] =
                    "learned";


                saveStatuses();

                updateDetailCards();


                if (
                    nextButton
                ) {

                    nextButton.click();

                }

            }
        );

    }


    if (
        notLearnedButton
    ) {

        notLearnedButton.addEventListener(
            "click",
            function () {

                const word =
                    getCurrentWord();


                statuses[
                    String(
                        word.id
                    )
                ] =
                    "not-learned";


                saveStatuses();

                updateDetailCards();


                if (
                    nextButton
                ) {

                    nextButton.click();

                }

            }
        );

    }


    if (
        shuffleButton
    ) {

        shuffleButton.addEventListener(
            "click",
            function () {

                order =
                    shuffledArray(
                        order
                    );


                currentPosition =
                    0;


                renderCard();

            }
        );

    }


    if (
        directionButton
    ) {

        directionButton.addEventListener(
            "click",
            function () {

                if (
                    direction
                    === "zh-vi"
                ) {

                    direction =
                        "vi-zh";


                    directionButton.textContent =
                        "⇄ VI → ZH";

                }
                else {

                    direction =
                        "zh-vi";


                    directionButton.textContent =
                        "⇄ ZH → VI";

                }


                renderCard();

            }
        );

    }


    if (
        wordModeButton
    ) {

        wordModeButton.addEventListener(
            "click",
            function () {

                cardMode =
                    "word";


                wordModeButton.classList.add(
                    "active"
                );


                if (
                    exampleModeButton
                ) {

                    exampleModeButton.classList.remove(
                        "active"
                    );

                }


                renderCard();

            }
        );

    }


    if (
        exampleModeButton
    ) {

        exampleModeButton.addEventListener(
            "click",
            function () {

                cardMode =
                    "example";


                exampleModeButton.classList.add(
                    "active"
                );


                if (
                    wordModeButton
                ) {

                    wordModeButton.classList.remove(
                        "active"
                    );

                }


                renderCard();

            }
        );

    }



    /* =========================================================
       10. CLICK CARD TỪ VỰNG
    ========================================================= */

    detailCards.forEach(
        function (
            card
        ) {

            card.addEventListener(
                "click",
                function (
                    event
                ) {

                    /*
                     * Bấm nút loa hoặc sao thì
                     * không đổi Flashcard.
                     */
                    if (
                        event.target.closest(
                            ".vocab-detail-icon-button"
                        )
                    ) {

                        return;

                    }


                    const originalIndex =
                        Number(
                            card.dataset.vocabIndex
                        );


                    let position =
                        order.indexOf(
                            originalIndex
                        );


                    if (
                        position
                        === -1
                    ) {

                        order =
                            vocabularies.map(
                                function (
                                    _,
                                    index
                                ) {

                                    return index;

                                }
                            );


                        position =
                            originalIndex;

                    }


                    currentPosition =
                        position;


                    showFlashcardMode();

                    renderCard();


                    if (
                        flashcard
                    ) {

                        flashcard.scrollIntoView(
                            {
                                behavior:
                                    "smooth",

                                block:
                                    "center"
                            }
                        );

                    }

                }
            );

        }
    );



    /* =========================================================
       11. ÔN TẬP
    ========================================================= */

    reviewButtons.forEach(
        function (
            button
        ) {

            button.addEventListener(
                "click",
                function (
                    event
                ) {

                    event.stopPropagation();


                    const id =
                        String(
                            button.dataset.vocabId
                        );


                    const index =
                        reviewWords.indexOf(
                            id
                        );


                    if (
                        index
                        === -1
                    ) {

                        reviewWords.push(
                            id
                        );

                    }
                    else {

                        reviewWords.splice(
                            index,
                            1
                        );

                    }


                    saveReviewWords();

                    updateDetailCards();

                }
            );

        }
    );


    if (
        addAllReviewButton
    ) {

        addAllReviewButton.addEventListener(
            "click",
            function () {

                vocabularies.forEach(
                    function (
                        word
                    ) {

                        const id =
                            String(
                                word.id
                            );


                        if (
                            !reviewWords.includes(
                                id
                            )
                        ) {

                            reviewWords.push(
                                id
                            );

                        }

                    }
                );


                saveReviewWords();

                updateDetailCards();


                addAllReviewButton.textContent =
                    "★ Đã thêm cả bài vào ôn tập";

            }
        );

    }



    /* =========================================================
       12. IN BÀI
    ========================================================= */

    if (
        printButton
    ) {

        printButton.addEventListener(
            "click",
            function () {

                window.print();

            }
        );

    }



    /* =========================================================
       13. TRẮC NGHIỆM - ELEMENT
    ========================================================= */

    const quizArea =
        document.getElementById(
            "vocabQuizArea"
        );


    const quizProgress =
        document.getElementById(
            "quizProgress"
        );


    const quizHanzi =
        document.getElementById(
            "quizHanzi"
        );


    const quizPinyin =
        document.getElementById(
            "quizPinyin"
        );


    const quizOptions =
        document.getElementById(
            "quizOptions"
        );


    const quizFeedback =
        document.getElementById(
            "quizFeedback"
        );


    const quizNextButton =
        document.getElementById(
            "quizNextButton"
        );


    const quizResult =
        document.getElementById(
            "quizResult"
        );


    const quizScore =
        document.getElementById(
            "quizScore"
        );


    const quizPercent =
        document.getElementById(
            "quizPercent"
        );


    const quizRestartButton =
        document.getElementById(
            "quizRestartButton"
        );


    const quizBackButton =
        document.getElementById(
            "quizBackButton"
        );


    let quizOrder = [];

    let quizPosition =
        0;


    let quizCorrect =
        0;


    let quizAnswered =
        false;



    /* =========================================================
       14. TRẮC NGHIỆM - TẠO ĐÁP ÁN
    ========================================================= */

    function createQuizOptions(
        correctWord
    ) {

        const otherMeanings =
            vocabularies
                .filter(
                    function (
                        word
                    ) {

                        return (
                            word.id
                            !== correctWord.id
                            &&
                            word.meaning
                            !== correctWord.meaning
                        );

                    }
                )
                .map(
                    function (
                        word
                    ) {

                        return word.meaning;

                    }
                );


        const uniqueOthers =
            [
                ...new Set(
                    otherMeanings
                )
            ];


        const wrongAnswers =
            shuffledArray(
                uniqueOthers
            ).slice(
                0,
                3
            );


        return shuffledArray(
            [
                correctWord.meaning,
                ...wrongAnswers
            ]
        );

    }



    /* =========================================================
       15. TRẮC NGHIỆM - BẮT ĐẦU
    ========================================================= */

    function startQuiz() {

        quizOrder =
            shuffledArray(
                vocabularies.map(
                    function (
                        _,
                        index
                    ) {

                        return index;

                    }
                )
            );


        quizPosition =
            0;


        quizCorrect =
            0;


        quizAnswered =
            false;


        if (
            quizResult
        ) {

            quizResult.hidden =
                true;

        }


        if (
            quizArea
        ) {

            quizArea.hidden =
                false;

        }


        renderQuizQuestion();

    }



    /* =========================================================
       16. TRẮC NGHIỆM - RENDER CÂU
    ========================================================= */

    function renderQuizQuestion() {

        if (
            !quizArea
        ) {

            return;

        }


        quizAnswered =
            false;


        const word =
            vocabularies[
                quizOrder[
                    quizPosition
                ]
            ];


        quizProgress.textContent =
            "Câu "
            + (quizPosition + 1)
            + " / "
            + quizOrder.length;


        quizHanzi.textContent =
            word.hanzi;


        quizPinyin.textContent =
            word.pinyin
            || "";


        quizFeedback.textContent =
            "";


        quizFeedback.className =
            "quiz-feedback";


        quizNextButton.hidden =
            true;


        quizOptions.innerHTML =
            "";


        const answers =
            createQuizOptions(
                word
            );


        answers.forEach(
            function (
                answer,
                index
            ) {

                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.className =
                    "quiz-option";


                const letter =
                    String.fromCharCode(
                        65 + index
                    );


                button.innerHTML =
                    "<span>"
                    + letter
                    + "</span>"
                    + "<strong>"
                    + escapeHtml(
                        answer
                    )
                    + "</strong>";


                button.addEventListener(
                    "click",
                    function () {

                        answerQuiz(
                            button,
                            answer,
                            word
                        );

                    }
                );


                quizOptions.appendChild(
                    button
                );

            }
        );

    }



    /* =========================================================
       17. TRẮC NGHIỆM - CHẤM
    ========================================================= */

    function answerQuiz(
        selectedButton,
        answer,
        word
    ) {

        if (
            quizAnswered
        ) {

            return;

        }


        quizAnswered =
            true;


        const optionButtons =
            quizOptions.querySelectorAll(
                ".quiz-option"
            );


        optionButtons.forEach(
            function (
                button
            ) {

                button.disabled =
                    true;


                const text =
                    button
                        .querySelector(
                            "strong"
                        )
                        .textContent;


                if (
                    text
                    === word.meaning
                ) {

                    button.classList.add(
                        "correct"
                    );

                }

            }
        );


        if (
            answer
            === word.meaning
        ) {

            quizCorrect++;


            selectedButton.classList.add(
                "correct"
            );


            quizFeedback.textContent =
                "✓ Chính xác!";


            quizFeedback.classList.add(
                "correct"
            );

        }
        else {

            selectedButton.classList.add(
                "wrong"
            );


            quizFeedback.textContent =
                "✕ Chưa đúng. Đáp án đúng: "
                + word.meaning;


            quizFeedback.classList.add(
                "wrong"
            );

        }


        quizNextButton.hidden =
            false;

    }



    /* =========================================================
       18. TRẮC NGHIỆM - CÂU TIẾP
    ========================================================= */

    function nextQuizQuestion() {

        quizPosition++;


        if (
            quizPosition
            >= quizOrder.length
        ) {

            finishQuiz();

            return;

        }


        renderQuizQuestion();

    }



    /* =========================================================
       19. TRẮC NGHIỆM - KẾT QUẢ
    ========================================================= */

    function finishQuiz() {

        quizArea.hidden =
            true;


        quizResult.hidden =
            false;


        const percent =
            Math.round(
                (
                    quizCorrect
                    / quizOrder.length
                )
                * 1000
            )
            / 10;


        quizScore.textContent =
            quizCorrect
            + " / "
            + quizOrder.length;


        quizPercent.textContent =
            percent
            + "%";

    }


    if (
        quizNextButton
    ) {

        quizNextButton.addEventListener(
            "click",
            nextQuizQuestion
        );

    }


    if (
        quizRestartButton
    ) {

        quizRestartButton.addEventListener(
            "click",
            startQuiz
        );

    }


    if (
        quizBackButton
    ) {

        quizBackButton.addEventListener(
            "click",
            showFlashcardMode
        );

    }



    /* =========================================================
       20. GÕ TỪ - ELEMENT
    ========================================================= */

    const typingArea =
        document.getElementById(
            "vocabTypingArea"
        );


    const typingResult =
        document.getElementById(
            "typingResult"
        );


    const typingProgress =
        document.getElementById(
            "typingProgress"
        );


    const typingQuestionMain =
        document.getElementById(
            "typingQuestionMain"
        );


    const typingQuestionSecondary =
        document.getElementById(
            "typingQuestionSecondary"
        );


    const typingAnswerInput =
        document.getElementById(
            "typingAnswerInput"
        );


    const typingCheckButton =
        document.getElementById(
            "typingCheckButton"
        );


    const typingFeedback =
        document.getElementById(
            "typingFeedback"
        );


    const typingNextButton =
        document.getElementById(
            "typingNextButton"
        );


    const typingDirectionButton =
        document.getElementById(
            "typingDirectionButton"
        );


    const typingScore =
        document.getElementById(
            "typingScore"
        );


    const typingPercent =
        document.getElementById(
            "typingPercent"
        );


    const typingRestartButton =
        document.getElementById(
            "typingRestartButton"
        );


    const typingBackButton =
        document.getElementById(
            "typingBackButton"
        );


    let typingOrder = [];

    let typingPosition =
        0;


    let typingCorrect =
        0;


    let typingAnswered =
        false;


    let typingDirection =
        "vi-zh";



    /* =========================================================
       21. GÕ TỪ - CHUẨN HÓA
    ========================================================= */

    function normalizeTypingAnswer(
        value
    ) {

        return String(
            value || ""
        )
            .toLowerCase()
            .trim()
            .normalize(
                "NFD"
            )
            .replace(
                /[\u0300-\u036f]/g,
                ""
            )
            .replace(
                /\s+/g,
                " "
            );

    }



    /* =========================================================
       22. GÕ TỪ - KIỂM TRA NGHĨA VIỆT
    ========================================================= */

    function checkVietnameseMeaning(
        answer,
        correctMeaning
    ) {

        const normalizedAnswer =
            normalizeTypingAnswer(
                answer
            );


        const fullMeaning =
            normalizeTypingAnswer(
                correctMeaning
            );


        if (
            normalizedAnswer
            === fullMeaning
        ) {

            return true;

        }


        const parts =
            String(
                correctMeaning
                || ""
            )
                .split(
                    /[;,/|]+/
                )
                .map(
                    function (
                        item
                    ) {

                        return normalizeTypingAnswer(
                            item
                        );

                    }
                )
                .filter(
                    Boolean
                );


        return parts.includes(
            normalizedAnswer
        );

    }



    /* =========================================================
       23. GÕ TỪ - BẮT ĐẦU
    ========================================================= */

    function startTyping() {

        if (
            !typingArea
        ) {

            return;

        }


        typingOrder =
            shuffledArray(
                vocabularies.map(
                    function (
                        _,
                        index
                    ) {

                        return index;

                    }
                )
            );


        typingPosition =
            0;


        typingCorrect =
            0;


        typingAnswered =
            false;


        if (
            typingResult
        ) {

            typingResult.hidden =
                true;

        }


        typingArea.hidden =
            false;


        renderTypingQuestion();

    }



    /* =========================================================
       24. GÕ TỪ - RENDER CÂU
    ========================================================= */

    function renderTypingQuestion() {

        typingAnswered =
            false;


        const word =
            vocabularies[
                typingOrder[
                    typingPosition
                ]
            ];


        typingProgress.textContent =
            "Câu "
            + (typingPosition + 1)
            + " / "
            + typingOrder.length;


        typingAnswerInput.value =
            "";


        typingAnswerInput.disabled =
            false;


        typingCheckButton.disabled =
            false;


        typingFeedback.textContent =
            "";


        typingFeedback.className =
            "typing-feedback";


        typingNextButton.hidden =
            true;


        if (
            typingDirection
            === "vi-zh"
        ) {

            typingQuestionMain.textContent =
                word.meaning;


            typingQuestionSecondary.textContent =
                "Hãy gõ chữ Hán tương ứng";


            typingAnswerInput.placeholder =
                "Nhập chữ Hán...";

        }
        else {

            typingQuestionMain.textContent =
                word.hanzi;


            typingQuestionSecondary.textContent =
                word.pinyin
                || "Hãy nhập nghĩa tiếng Việt";


            typingAnswerInput.placeholder =
                "Nhập nghĩa tiếng Việt...";

        }


        setTimeout(
            function () {

                typingAnswerInput.focus();

            },
            50
        );

    }



    /* =========================================================
       25. GÕ TỪ - CHẤM
    ========================================================= */

    function checkTypingAnswer() {

        if (
            typingAnswered
        ) {

            return;

        }


        const word =
            vocabularies[
                typingOrder[
                    typingPosition
                ]
            ];


        const answer =
            typingAnswerInput
                .value
                .trim();


        if (
            !answer
        ) {

            typingFeedback.textContent =
                "Bạn chưa nhập đáp án.";


            typingFeedback.className =
                "typing-feedback wrong";


            typingAnswerInput.focus();

            return;

        }


        let isCorrect =
            false;


        if (
            typingDirection
            === "vi-zh"
        ) {

            isCorrect =
                answer.replace(
                    /\s+/g,
                    ""
                )
                ===
                String(
                    word.hanzi
                    || ""
                ).replace(
                    /\s+/g,
                    ""
                );

        }
        else {

            isCorrect =
                checkVietnameseMeaning(
                    answer,
                    word.meaning
                );

        }


        typingAnswered =
            true;


        typingAnswerInput.disabled =
            true;


        typingCheckButton.disabled =
            true;


        if (
            isCorrect
        ) {

            typingCorrect++;


            typingFeedback.textContent =
                "✓ Chính xác!";


            typingFeedback.className =
                "typing-feedback correct";

        }
        else {

            const correctAnswer =
                typingDirection
                === "vi-zh"
                    ? word.hanzi
                    : word.meaning;


            typingFeedback.innerHTML =
                "✕ Chưa đúng. Đáp án đúng: "
                + "<strong>"
                + escapeHtml(
                    correctAnswer
                )
                + "</strong>";


            typingFeedback.className =
                "typing-feedback wrong";

        }


        typingNextButton.hidden =
            false;

    }



    /* =========================================================
       26. GÕ TỪ - CÂU TIẾP
    ========================================================= */

    function nextTypingQuestion() {

        typingPosition++;


        if (
            typingPosition
            >= typingOrder.length
        ) {

            finishTyping();

            return;

        }


        renderTypingQuestion();

    }



    /* =========================================================
       27. GÕ TỪ - KẾT QUẢ
    ========================================================= */

    function finishTyping() {

        typingArea.hidden =
            true;


        typingResult.hidden =
            false;


        const percent =
            Math.round(
                (
                    typingCorrect
                    / typingOrder.length
                )
                * 1000
            )
            / 10;


        typingScore.textContent =
            typingCorrect
            + " / "
            + typingOrder.length;


        typingPercent.textContent =
            percent
            + "%";

    }



    /* =========================================================
       28. GÕ TỪ - EVENTS
    ========================================================= */

    if (
        typingDirectionButton
    ) {

        typingDirectionButton.addEventListener(
            "click",
            function () {

                if (
                    typingDirection
                    === "vi-zh"
                ) {

                    typingDirection =
                        "zh-vi";


                    typingDirectionButton.textContent =
                        "⇄ ZH → VI";

                }
                else {

                    typingDirection =
                        "vi-zh";


                    typingDirectionButton.textContent =
                        "⇄ VI → ZH";

                }


                startTyping();

            }
        );

    }


    if (
        typingCheckButton
    ) {

        typingCheckButton.addEventListener(
            "click",
            checkTypingAnswer
        );

    }


    if (
        typingAnswerInput
    ) {

        typingAnswerInput.addEventListener(
            "keydown",
            function (
                event
            ) {

                if (
                    event.key
                    !== "Enter"
                ) {

                    return;

                }


                if (
                    typingAnswered
                ) {

                    nextTypingQuestion();

                }
                else {

                    checkTypingAnswer();

                }

            }
        );

    }


    if (
        typingNextButton
    ) {

        typingNextButton.addEventListener(
            "click",
            nextTypingQuestion
        );

    }


    if (
        typingRestartButton
    ) {

        typingRestartButton.addEventListener(
            "click",
            startTyping
        );

    }


    if (
        typingBackButton
    ) {

        typingBackButton.addEventListener(
            "click",
            showFlashcardMode
        );

    }



    /* =========================================================
       ĐỌC HIỂU - ELEMENT
    ========================================================= */

    const readingArea =
        document.getElementById(
            "vocabReadingArea"
        );


    const readingUnavailable =
        document.getElementById(
            "readingUnavailable"
        );


    const readingResult =
        document.getElementById(
            "readingResult"
        );


    const readingProgress =
        document.getElementById(
            "readingProgress"
        );


    const readingChinese =
        document.getElementById(
            "readingChinese"
        );


    const readingOptions =
        document.getElementById(
            "readingOptions"
        );


    const readingFeedback =
        document.getElementById(
            "readingFeedback"
        );


    const readingNextButton =
        document.getElementById(
            "readingNextButton"
        );


    const readingScore =
        document.getElementById(
            "readingScore"
        );


    const readingPercent =
        document.getElementById(
            "readingPercent"
        );


    const readingRestartButton =
        document.getElementById(
            "readingRestartButton"
        );


    const readingBackButton =
        document.getElementById(
            "readingBackButton"
        );



    /* =========================================================
       CHỈ LẤY CÂU CÓ ĐỦ TRUNG + VIỆT
    ========================================================= */

    const readingWords =
        vocabularies.filter(
            function (
                word
            ) {

                return (
                    word.exampleChinese
                    &&
                    word.exampleChinese.trim()
                    &&
                    word.exampleVietnamese
                    &&
                    word.exampleVietnamese.trim()
                );

            }
        );


    let readingOrder = [];

    let readingPosition =
        0;


    let readingCorrect =
        0;


    let readingAnswered =
        false;



    /* =========================================================
       TẠO ĐÁP ÁN ĐỌC HIỂU
    ========================================================= */

    function createReadingOptions(
        correctWord
    ) {

        const otherTranslations =
            readingWords
                .filter(
                    function (
                        word
                    ) {

                        return (
                            word.id
                            !== correctWord.id
                            &&
                            word.exampleVietnamese
                            !== correctWord.exampleVietnamese
                        );

                    }
                )
                .map(
                    function (
                        word
                    ) {

                        return word.exampleVietnamese;

                    }
                );


        const uniqueOthers =
            [
                ...new Set(
                    otherTranslations
                )
            ];


        const wrongAnswers =
            shuffledArray(
                uniqueOthers
            ).slice(
                0,
                3
            );


        return shuffledArray(
            [
                correctWord.exampleVietnamese,
                ...wrongAnswers
            ]
        );

    }



    /* =========================================================
       BẮT ĐẦU ĐỌC HIỂU
    ========================================================= */

    function startReading() {

        if (
            readingWords.length
            < 2
        ) {

            if (
                readingArea
            ) {

                readingArea.hidden =
                    true;

            }


            if (
                readingResult
            ) {

                readingResult.hidden =
                    true;

            }


            if (
                readingUnavailable
            ) {

                readingUnavailable.hidden =
                    false;

            }


            return;

        }


        if (
            readingUnavailable
        ) {

            readingUnavailable.hidden =
                true;

        }


        readingOrder =
            shuffledArray(
                readingWords.map(
                    function (
                        _,
                        index
                    ) {

                        return index;

                    }
                )
            );


        readingPosition =
            0;


        readingCorrect =
            0;


        readingAnswered =
            false;


        if (
            readingResult
        ) {

            readingResult.hidden =
                true;

        }


        if (
            readingArea
        ) {

            readingArea.hidden =
                false;

        }


        renderReadingQuestion();

    }



    /* =========================================================
       HIỂN THỊ CÂU ĐỌC
    ========================================================= */

    function renderReadingQuestion() {

        readingAnswered =
            false;


        const word =
            readingWords[
                readingOrder[
                    readingPosition
                ]
            ];


        readingProgress.textContent =
            "Câu "
            + (readingPosition + 1)
            + " / "
            + readingOrder.length;


        readingChinese.textContent =
            word.exampleChinese;


        readingFeedback.textContent =
            "";


        readingFeedback.className =
            "reading-feedback";


        readingNextButton.hidden =
            true;


        readingOptions.innerHTML =
            "";


        const answers =
            createReadingOptions(
                word
            );


        answers.forEach(
            function (
                answer,
                index
            ) {

                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.className =
                    "reading-option";


                const letter =
                    String.fromCharCode(
                        65 + index
                    );


                button.innerHTML =
                    "<span>"
                    + letter
                    + "</span>"
                    + "<strong>"
                    + escapeHtml(
                        answer
                    )
                    + "</strong>";


                button.addEventListener(
                    "click",
                    function () {

                        answerReading(
                            button,
                            answer,
                            word
                        );

                    }
                );


                readingOptions.appendChild(
                    button
                );

            }
        );

    }



    /* =========================================================
       CHẤM ĐỌC HIỂU
    ========================================================= */

    function answerReading(
        selectedButton,
        answer,
        word
    ) {

        if (
            readingAnswered
        ) {

            return;

        }


        readingAnswered =
            true;


        const buttons =
            readingOptions.querySelectorAll(
                ".reading-option"
            );


        buttons.forEach(
            function (
                button
            ) {

                button.disabled =
                    true;


                const text =
                    button
                        .querySelector(
                            "strong"
                        )
                        .textContent;


                if (
                    text
                    === word.exampleVietnamese
                ) {

                    button.classList.add(
                        "correct"
                    );

                }

            }
        );


        if (
            answer
            === word.exampleVietnamese
        ) {

            readingCorrect++;


            selectedButton.classList.add(
                "correct"
            );


            readingFeedback.textContent =
                "✓ Chính xác!";


            readingFeedback.classList.add(
                "correct"
            );

        }
        else {

            selectedButton.classList.add(
                "wrong"
            );


            readingFeedback.textContent =
                "✕ Chưa đúng. Đáp án đúng: "
                + word.exampleVietnamese;


            readingFeedback.classList.add(
                "wrong"
            );

        }


        readingNextButton.hidden =
            false;

    }



    /* =========================================================
       CÂU ĐỌC TIẾP
    ========================================================= */

    function nextReadingQuestion() {

        readingPosition++;


        if (
            readingPosition
            >= readingOrder.length
        ) {

            finishReading();

            return;

        }


        renderReadingQuestion();

    }



    /* =========================================================
       KẾT QUẢ ĐỌC HIỂU
    ========================================================= */

    function finishReading() {

        readingArea.hidden =
            true;


        readingResult.hidden =
            false;


        const percent =
            Math.round(
                (
                    readingCorrect
                    / readingOrder.length
                )
                * 1000
            )
            / 10;


        readingScore.textContent =
            readingCorrect
            + " / "
            + readingOrder.length;


        readingPercent.textContent =
            percent
            + "%";

    }



    /* =========================================================
       EVENT ĐỌC HIỂU
    ========================================================= */

    if (
        readingNextButton
    ) {

        readingNextButton.addEventListener(
            "click",
            nextReadingQuestion
        );

    }


    if (
        readingRestartButton
    ) {

        readingRestartButton.addEventListener(
            "click",
            startReading
        );

    }


    if (
        readingBackButton
    ) {

        readingBackButton.addEventListener(
            "click",
            showFlashcardMode
        );

    }



       /* =========================================================
       29. CHẾ ĐỘ HỌC + DỮ LIỆU CHỮ HÁN
    ========================================================= */

    const modeCards =
        document.querySelectorAll(
            ".vocab-study-mode-card"
        );


    const modeNotice =
        document.getElementById(
            "vocabModeNotice"
        );


    const hanziDataElement =
        document.getElementById(
            "lessonHanziData"
        );


    let hanzis = [];


    if (
        hanziDataElement
    ) {

        try {

            hanzis =
                JSON.parse(
                    hanziDataElement.textContent
                );

        }
        catch (
            error
        ) {

            console.error(
                "Không đọc được dữ liệu chữ Hán:",
                error
            );


            hanzis = [];

        }

    }



    /* =========================================================
       ĐỔI TRẠNG THÁI THẺ CHẾ ĐỘ HỌC
    ========================================================= */

    function setActiveMode(
        modeName,
        selectedStatus
    ) {

        modeCards.forEach(
            function (
                card
            ) {

                const active =
                    card.dataset.studyMode
                    === modeName;


                card.classList.toggle(
                    "active",
                    active
                );


                const status =
                    card.querySelector(
                        ".mode-status"
                    );


                if (
                    !status
                ) {

                    return;

                }


                if (
                    active
                ) {

                    status.textContent =
                        selectedStatus
                        || "Đang học";


                    status.classList.add(
                        "mode-status-active"
                    );

                }
                else {

                    status.textContent =
                        "Chưa học";


                    status.classList.remove(
                        "mode-status-active"
                    );

                }

            }
        );

    }



    /* =========================================================
       CUỘN ĐẾN KHUNG ĐANG HỌC
    ========================================================= */

    function scrollToStudyArea(
        area
    ) {

        if (
            !area
        ) {

            return;

        }


        setTimeout(
            function () {

                area.scrollIntoView(
                    {
                        behavior:
                            "smooth",

                        block:
                            "start"
                    }
                );

            },
            30
        );

    }



    /* =========================================================
       THÔNG BÁO
    ========================================================= */

    function showModeMessage(
        message
    ) {

        if (
            !modeNotice
        ) {

            return;

        }


        modeNotice.hidden =
            false;


        modeNotice.textContent =
            message;

    }



    /* =========================================================
       30. NGHE GHÉP CÂU
    ========================================================= */

    const listeningArea =
        document.getElementById(
            "vocabListeningArea"
        );


    const listeningResult =
        document.getElementById(
            "listeningResult"
        );


    const listeningProgress =
        document.getElementById(
            "listeningProgress"
        );


    const listeningCounter =
        document.getElementById(
            "listeningCounter"
        );


    const listeningPlayButton =
        document.getElementById(
            "listeningPlayButton"
        );


    const listeningTaskButtons =
        document.querySelectorAll(
            "#listeningTaskSwitch button"
        );


    const listeningAssemblePanel =
        document.getElementById(
            "listeningAssemblePanel"
        );


    const listeningTypingPanel =
        document.getElementById(
            "listeningTypingPanel"
        );


    const listeningTypingInput =
        document.getElementById(
            "listeningTypingInput"
        );


    const listeningTypingCheckButton =
        document.getElementById(
            "listeningTypingCheckButton"
        );


    const listeningAnswerSlots =
        document.getElementById(
            "listeningAnswerSlots"
        );


    const listeningTokenBank =
        document.getElementById(
            "listeningTokenBank"
        );


    const listeningFeedback =
        document.getElementById(
            "listeningFeedback"
        );


    const listeningNextButton =
        document.getElementById(
            "listeningNextButton"
        );


    const listeningScore =
        document.getElementById(
            "listeningScore"
        );


    const listeningPercent =
        document.getElementById(
            "listeningPercent"
        );


    const listeningRestartButton =
        document.getElementById(
            "listeningRestartButton"
        );


    const listeningSpeedButtons =
        document.querySelectorAll(
            "#listeningSpeedGroup button"
        );


    let listeningQuestions =
        [];


    let listeningOrder =
        [];


    let listeningPosition =
        0;


    let listeningCorrect =
        0;


    let listeningSpeed =
        1;


    let listeningTaskMode =
        "assemble";


    let listeningTokens =
        [];


    let listeningSelected =
        [];


    let listeningSolved =
        false;



    /* =========================================================
       DỪNG GIỌNG ĐỌC
    ========================================================= */

    function stopListeningSpeech() {

        if (
            "speechSynthesis"
            in window
        ) {

            window
                .speechSynthesis
                .cancel();

        }

    }



    /* =========================================================
       CHUẨN HÓA CÂU
    ========================================================= */

    function normalizeSentence(
        value
    ) {

        return String(
            value
            || ""
        )
            .replace(
                /\s+/g,
                ""
            )
            .replace(
                /[，。！？、；：,.!?;:“”"'（）()《》]/g,
                ""
            )
            .trim();

    }



    /* =========================================================
       TÁCH CÂU THÀNH CÁC THẺ
    ========================================================= */

    function tokenizeChineseSentence(
        sentence
    ) {

        const text =
            normalizeSentence(
                sentence
            );


        if (
            !text
        ) {

            return [];

        }


        /*
         * Ưu tiên nhận ra các từ
         * đang có trong bài trước.
         */
        const knownWords =
            vocabularies
                .map(
                    function (
                        word
                    ) {

                        return String(
                            word.hanzi
                            || ""
                        ).trim();

                    }
                )
                .filter(
                    Boolean
                )
                .sort(
                    function (
                        a,
                        b
                    ) {

                        return (
                            b.length
                            - a.length
                        );

                    }
                );


        const result =
            [];


        let index =
            0;


        while (
            index
            < text.length
        ) {

            let match =
                "";


            for (
                let i = 0;
                i < knownWords.length;
                i++
            ) {

                const candidate =
                    knownWords[
                        i
                    ];


                if (
                    candidate
                    &&
                    text.startsWith(
                        candidate,
                        index
                    )
                ) {

                    match =
                        candidate;


                    break;

                }

            }


            if (
                match
            ) {

                result.push(
                    match
                );


                index +=
                    match.length;

            }
            else {

                const rest =
                    Array.from(
                        text.slice(
                            index
                        )
                    );


                const currentCharacter =
                    rest[0];


                if (
                    !currentCharacter
                ) {

                    break;

                }


                result.push(
                    currentCharacter
                );


                index +=
                    currentCharacter.length;

            }

        }


        return result;

    }



    /* =========================================================
       TẠO DANH SÁCH CÂU NGHE
    ========================================================= */

    function buildListeningQuestions() {

        const seen =
            new Set();


        const questions =
            [];


        vocabularies.forEach(
            function (
                word
            ) {

                const sentence =
                    String(
                        word.exampleChinese
                        || ""
                    ).trim();


                if (
                    !sentence
                ) {

                    return;

                }


                const normalized =
                    normalizeSentence(
                        sentence
                    );


                if (
                    !normalized
                    ||
                    seen.has(
                        normalized
                    )
                ) {

                    return;

                }


                const tokens =
                    tokenizeChineseSentence(
                        sentence
                    );


                if (
                    tokens.length
                    < 2
                ) {

                    return;

                }


                seen.add(
                    normalized
                );


                questions.push(
                    {
                        sentence:
                            sentence,

                        translation:
                            word.exampleVietnamese
                            || "",

                        tokens:
                            tokens
                    }
                );

            }
        );


        /*
         * Tối đa 15 câu / lượt.
         */
        return questions.slice(
            0,
            15
        );

    }



    /* =========================================================
       ĐỌC CÂU TIẾNG TRUNG
    ========================================================= */

    function speakListeningSentence() {

        const question =
            listeningQuestions[
                listeningOrder[
                    listeningPosition
                ]
            ];


        if (
            !question
        ) {

            return;

        }


        if (
            !(
                "speechSynthesis"
                in window
            )
        ) {

            listeningFeedback.textContent =
                "Trình duyệt này không hỗ trợ đọc câu tiếng Trung.";


            listeningFeedback.className =
                "listening-feedback wrong";


            return;

        }


        stopListeningSpeech();


        const utterance =
            new SpeechSynthesisUtterance(
                question.sentence
            );


        utterance.lang =
            "zh-CN";


        utterance.rate =
            listeningSpeed;


        utterance.pitch =
            1;


        /*
         * Tìm giọng tiếng Trung
         * nếu máy có.
         */
        const voices =
            window
                .speechSynthesis
                .getVoices();


        const chineseVoice =
            voices.find(
                function (
                    voice
                ) {

                    return String(
                        voice.lang
                        || ""
                    )
                        .toLowerCase()
                        .startsWith(
                            "zh"
                        );

                }
            );


        if (
            chineseVoice
        ) {

            utterance.voice =
                chineseVoice;

        }


        window
            .speechSynthesis
            .speak(
                utterance
            );

    }



    /* =========================================================
       CHUYỂN GHÉP CÂU / GÕ LẠI
    ========================================================= */

    function renderListeningTaskPanels() {

        if (
            listeningAssemblePanel
        ) {

            listeningAssemblePanel.hidden =
                listeningTaskMode
                !== "assemble";

        }


        if (
            listeningTypingPanel
        ) {

            listeningTypingPanel.hidden =
                listeningTaskMode
                !== "typing";

        }


        listeningTaskButtons.forEach(
            function (
                button
            ) {

                button.classList.toggle(
                    "active",

                    button.dataset
                        .listeningTask
                    === listeningTaskMode
                );

            }
        );


        if (
            listeningTaskMode
            === "typing"
            &&
            listeningTypingInput
            &&
            !listeningSolved
        ) {

            setTimeout(
                function () {

                    listeningTypingInput
                        .focus();

                },
                30
            );

        }

    }



    /* =========================================================
       CHẤM PHẦN GÕ LẠI
    ========================================================= */

    function checkListeningTypingAnswer() {

        if (
            listeningSolved
            ||
            !listeningTypingInput
        ) {

            return;

        }


        const question =
            listeningQuestions[
                listeningOrder[
                    listeningPosition
                ]
            ];


        if (
            !question
        ) {

            return;

        }


        const answer =
            normalizeSentence(
                listeningTypingInput
                    .value
            );


        if (
            !answer
        ) {

            listeningFeedback.textContent =
                "Bạn chưa nhập câu trả lời.";


            listeningFeedback.className =
                "listening-feedback wrong";


            listeningTypingInput.focus();


            return;

        }


        const correct =
            normalizeSentence(
                question.sentence
            );


        if (
            answer
            === correct
        ) {

            listeningSolved =
                true;


            listeningCorrect++;


            listeningTypingInput.disabled =
                true;


            listeningTypingCheckButton.disabled =
                true;


            listeningFeedback.textContent =
                question.translation
                    ? (
                        "✓ Chính xác! "
                        + question.translation
                    )
                    : "✓ Chính xác!";


            listeningFeedback.className =
                "listening-feedback correct";


            listeningNextButton.hidden =
                false;

        }
        else {

            listeningFeedback.textContent =
                "✕ Chưa đúng. Hãy nghe lại và thử tiếp.";


            listeningFeedback.className =
                "listening-feedback wrong";


            listeningTypingInput.focus();

        }

    }



    /* =========================================================
       HIỂN THỊ CÁC THẺ GHÉP CÂU
    ========================================================= */

    function renderListeningTokens() {

        listeningAnswerSlots.innerHTML =
            "";


        listeningTokenBank.innerHTML =
            "";


        /*
         * Các thẻ đã chọn.
         */
        listeningSelected.forEach(
            function (
                item
            ) {

                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.className =
                    "listening-selected-token";


                button.textContent =
                    item.text;


                button.addEventListener(
                    "click",
                    function () {

                        if (
                            listeningSolved
                        ) {

                            return;

                        }


                        listeningSelected =
                            listeningSelected.filter(
                                function (
                                    selected
                                ) {

                                    return (
                                        selected.id
                                        !== item.id
                                    );

                                }
                            );


                        listeningFeedback.textContent =
                            "";


                        listeningFeedback.className =
                            "listening-feedback";


                        renderListeningTokens();

                    }
                );


                listeningAnswerSlots
                    .appendChild(
                        button
                    );

            }
        );


        /*
         * Những thẻ chưa chọn.
         */
        listeningTokens
            .filter(
                function (
                    item
                ) {

                    return !listeningSelected
                        .some(
                            function (
                                selected
                            ) {

                                return (
                                    selected.id
                                    === item.id
                                );

                            }
                        );

                }
            )
            .forEach(
                function (
                    item
                ) {

                    const button =
                        document.createElement(
                            "button"
                        );


                    button.type =
                        "button";


                    button.className =
                        "listening-token";


                    button.textContent =
                        item.text;


                    button.addEventListener(
                        "click",
                        function () {

                            if (
                                listeningSolved
                            ) {

                                return;

                            }


                            listeningSelected.push(
                                item
                            );


                            renderListeningTokens();


                            checkListeningAnswer();

                        }
                    );


                    listeningTokenBank
                        .appendChild(
                            button
                        );

                }
            );


        /*
         * Chưa chọn từ nào.
         */
        if (
            listeningSelected.length
            === 0
        ) {

            const placeholder =
                document.createElement(
                    "span"
                );


            placeholder.className =
                "listening-answer-placeholder";


            placeholder.textContent =
                "Bấm các thẻ bên dưới để ghép câu";


            listeningAnswerSlots
                .appendChild(
                    placeholder
                );

        }

    }



    /* =========================================================
       KIỂM TRA GHÉP CÂU
    ========================================================= */

    function checkListeningAnswer() {

        const question =
            listeningQuestions[
                listeningOrder[
                    listeningPosition
                ]
            ];


        if (
            !question
            ||
            listeningSelected.length
            !== question.tokens.length
        ) {

            return;

        }


        const answer =
            listeningSelected
                .map(
                    function (
                        item
                    ) {

                        return item.text;

                    }
                )
                .join(
                    ""
                );


        const correct =
            question.tokens.join(
                ""
            );


        if (
            answer
            === correct
        ) {

            listeningSolved =
                true;


            listeningCorrect++;


            listeningFeedback.textContent =
                question.translation
                    ? (
                        "✓ Chính xác! "
                        + question.translation
                    )
                    : "✓ Chính xác!";


            listeningFeedback.className =
                "listening-feedback correct";


            listeningNextButton.hidden =
                false;


            if (
                listeningTypingInput
            ) {

                listeningTypingInput.disabled =
                    true;

            }


            if (
                listeningTypingCheckButton
            ) {

                listeningTypingCheckButton.disabled =
                    true;

            }


            renderListeningTokens();

        }
        else {

            listeningFeedback.textContent =
                "✕ Thứ tự chưa đúng. Bấm vào từ đã ghép để đưa từ đó xuống lại.";


            listeningFeedback.className =
                "listening-feedback wrong";

        }

    }



    /* =========================================================
       HIỂN THỊ 1 CÂU NGHE
    ========================================================= */

    function renderListeningQuestion() {

        const question =
            listeningQuestions[
                listeningOrder[
                    listeningPosition
                ]
            ];


        if (
            !question
        ) {

            return;

        }


        stopListeningSpeech();


        listeningSolved =
            false;


        listeningSelected =
            [];


        /*
         * Tạo ID riêng cho từng thẻ.
         * Cần thiết khi trong câu
         * có 2 từ giống nhau.
         */
        listeningTokens =
            shuffledArray(
                question.tokens.map(
                    function (
                        text,
                        index
                    ) {

                        return {
                            id:
                                listeningPosition
                                + "_"
                                + index
                                + "_"
                                + Math.random(),

                            text:
                                text
                        };

                    }
                )
            );


        listeningProgress.textContent =
            "Câu "
            + (listeningPosition + 1)
            + " / "
            + listeningOrder.length;


        listeningCounter.textContent =
            (listeningPosition + 1)
            + " / "
            + listeningOrder.length;


        listeningFeedback.textContent =
            "";


        listeningFeedback.className =
            "listening-feedback";


        listeningNextButton.hidden =
            true;


        if (
            listeningTypingInput
        ) {

            listeningTypingInput.value =
                "";


            listeningTypingInput.disabled =
                false;

        }


        if (
            listeningTypingCheckButton
        ) {

            listeningTypingCheckButton.disabled =
                false;

        }


        renderListeningTokens();


        renderListeningTaskPanels();

    }



    /* =========================================================
       BẮT ĐẦU NGHE GHÉP CÂU
    ========================================================= */

    function startListening() {

        listeningQuestions =
            buildListeningQuestions();


        if (
            listeningQuestions.length
            === 0
        ) {

            if (
                listeningArea
            ) {

                listeningArea.hidden =
                    true;

            }


            showModeMessage(
                "Bài này chưa có đủ câu ví dụ tiếng Trung để tạo bài Nghe ghép câu."
            );


            return;

        }


        listeningOrder =
            shuffledArray(
                listeningQuestions.map(
                    function (
                        _,
                        index
                    ) {

                        return index;

                    }
                )
            );


        listeningPosition =
            0;


        listeningCorrect =
            0;


        listeningTaskMode =
            "assemble";


        if (
            listeningResult
        ) {

            listeningResult.hidden =
                true;

        }


        if (
            listeningArea
        ) {

            listeningArea.hidden =
                false;

        }


        renderListeningQuestion();

    }



    /* =========================================================
       CÂU NGHE TIẾP THEO
    ========================================================= */

    function nextListeningQuestion() {

        listeningPosition++;


        if (
            listeningPosition
            >= listeningOrder.length
        ) {

            finishListening();


            return;

        }


        renderListeningQuestion();

    }



    /* =========================================================
       KẾT QUẢ NGHE GHÉP CÂU
    ========================================================= */

    function finishListening() {

        stopListeningSpeech();


        if (
            listeningArea
        ) {

            listeningArea.hidden =
                true;

        }


        if (
            listeningResult
        ) {

            listeningResult.hidden =
                false;

        }


        const total =
            listeningOrder.length;


        const percent =
            total
                ? (
                    Math.round(
                        listeningCorrect
                        / total
                        * 1000
                    )
                    / 10
                )
                : 0;


        listeningScore.textContent =
            listeningCorrect
            + " / "
            + total;


        listeningPercent.textContent =
            percent
            + "%";

    }



    /* =========================================================
       EVENT NGHE GHÉP CÂU
    ========================================================= */

    if (
        listeningPlayButton
    ) {

        listeningPlayButton.addEventListener(
            "click",
            speakListeningSentence
        );

    }


    listeningTaskButtons.forEach(
        function (
            button
        ) {

            button.addEventListener(
                "click",
                function () {

                    listeningTaskMode =
                        button.dataset
                            .listeningTask
                        || "assemble";


                    listeningFeedback.textContent =
                        "";


                    listeningFeedback.className =
                        "listening-feedback";


                    renderListeningTaskPanels();

                }
            );

        }
    );


    if (
        listeningTypingCheckButton
    ) {

        listeningTypingCheckButton.addEventListener(
            "click",
            checkListeningTypingAnswer
        );

    }


    if (
        listeningTypingInput
    ) {

        listeningTypingInput.addEventListener(
            "keydown",
            function (
                event
            ) {

                if (
                    event.key
                    === "Enter"
                ) {

                    checkListeningTypingAnswer();

                }

            }
        );

    }


    if (
        listeningNextButton
    ) {

        listeningNextButton.addEventListener(
            "click",
            nextListeningQuestion
        );

    }


    if (
        listeningRestartButton
    ) {

        listeningRestartButton.addEventListener(
            "click",
            startListening
        );

    }


    listeningSpeedButtons.forEach(
        function (
            button
        ) {

            button.addEventListener(
                "click",
                function () {

                    listeningSpeed =
                        Number(
                            button.dataset.speed
                        )
                        || 1;


                    listeningSpeedButtons.forEach(
                        function (
                            item
                        ) {

                            item.classList.remove(
                                "active"
                            );

                        }
                    );


                    button.classList.add(
                        "active"
                    );


                    stopListeningSpeech();

                }
            );

        }
    );



    /* =========================================================
       31. HANZI DANCE
    ========================================================= */

    const hanziDanceArea =
        document.getElementById(
            "hanziDanceArea"
        );


    const hanziDanceResult =
        document.getElementById(
            "hanziDanceResult"
        );


    const hanziDanceProgress =
        document.getElementById(
            "hanziDanceProgress"
        );


    const hanziDanceLiveScore =
        document.getElementById(
            "hanziDanceLiveScore"
        );


    const hanziDanceCharacter =
        document.getElementById(
            "hanziDanceCharacter"
        );


    const hanziDancePinyin =
        document.getElementById(
            "hanziDancePinyin"
        );


    const hanziDanceOptions =
        document.getElementById(
            "hanziDanceOptions"
        );


    const hanziDanceFeedback =
        document.getElementById(
            "hanziDanceFeedback"
        );


    const hanziDanceNextButton =
        document.getElementById(
            "hanziDanceNextButton"
        );


    const hanziDanceScore =
        document.getElementById(
            "hanziDanceScore"
        );


    const hanziDancePercent =
        document.getElementById(
            "hanziDancePercent"
        );


    const hanziDanceRestartButton =
        document.getElementById(
            "hanziDanceRestartButton"
        );


    let hanziDanceOrder =
        [];


    let hanziDancePosition =
        0;


    let hanziDanceCorrect =
        0;


    let hanziDanceAnswered =
        false;



    /* =========================================================
       TẠO ĐÁP ÁN HANZI DANCE
    ========================================================= */

    function createHanziDanceOptions(
        correctHanzi
    ) {

        const otherMeanings =
            hanzis
                .filter(
                    function (
                        item
                    ) {

                        return (
                            item.id
                            !== correctHanzi.id
                            &&
                            item.meaning
                            &&
                            item.meaning
                            !== correctHanzi.meaning
                        );

                    }
                )
                .map(
                    function (
                        item
                    ) {

                        return item.meaning;

                    }
                );


        const uniqueOthers =
            [
                ...new Set(
                    otherMeanings
                )
            ];


        const wrongAnswers =
            shuffledArray(
                uniqueOthers
            ).slice(
                0,
                3
            );


        return shuffledArray(
            [
                correctHanzi.meaning,
                ...wrongAnswers
            ]
        );

    }



    /* =========================================================
       HIỂN THỊ CÂU HANZI DANCE
    ========================================================= */

    function renderHanziDanceQuestion() {

        const item =
            hanzis[
                hanziDanceOrder[
                    hanziDancePosition
                ]
            ];


        if (
            !item
        ) {

            return;

        }


        hanziDanceAnswered =
            false;


        hanziDanceProgress.textContent =
            "Câu "
            + (hanziDancePosition + 1)
            + " / "
            + hanziDanceOrder.length;


        hanziDanceLiveScore.textContent =
            hanziDanceCorrect
            + " điểm";


        hanziDanceCharacter.textContent =
            item.character
            || "";


        hanziDancePinyin.textContent =
            item.pinyin
            || "";


        hanziDanceFeedback.textContent =
            "";


        hanziDanceFeedback.className =
            "hanzi-dance-feedback";


        hanziDanceNextButton.hidden =
            true;


        hanziDanceOptions.innerHTML =
            "";


        const answers =
            createHanziDanceOptions(
                item
            );


        answers.forEach(
            function (
                answer
            ) {

                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.className =
                    "hanzi-dance-option";


                button.textContent =
                    answer;


                button.addEventListener(
                    "click",
                    function () {

                        if (
                            hanziDanceAnswered
                        ) {

                            return;

                        }


                        hanziDanceAnswered =
                            true;


                        const buttons =
                            hanziDanceOptions
                                .querySelectorAll(
                                    ".hanzi-dance-option"
                                );


                        buttons.forEach(
                            function (
                                option
                            ) {

                                option.disabled =
                                    true;


                                if (
                                    option.textContent
                                    === item.meaning
                                ) {

                                    option.classList.add(
                                        "correct"
                                    );

                                }

                            }
                        );


                        if (
                            answer
                            === item.meaning
                        ) {

                            hanziDanceCorrect++;


                            button.classList.add(
                                "correct"
                            );


                            hanziDanceFeedback.textContent =
                                "✓ Chính xác!";


                            hanziDanceFeedback.className =
                                "hanzi-dance-feedback correct";


                            hanziDanceCharacter.classList.add(
                                "dance-correct"
                            );


                            /*
                             * Phát luôn âm chữ Hán
                             * nếu có audio.
                             */
                            if (
                                item.audioUrl
                            ) {

                                playLessonAudio(
                                    item.audioUrl,
                                    null
                                );

                            }


                            setTimeout(
                                function () {

                                    hanziDanceCharacter
                                        .classList
                                        .remove(
                                            "dance-correct"
                                        );

                                },
                                600
                            );

                        }
                        else {

                            button.classList.add(
                                "wrong"
                            );


                            hanziDanceFeedback.textContent =
                                "✕ Chưa đúng. Đáp án: "
                                + item.meaning;


                            hanziDanceFeedback.className =
                                "hanzi-dance-feedback wrong";

                        }


                        hanziDanceLiveScore.textContent =
                            hanziDanceCorrect
                            + " điểm";


                        hanziDanceNextButton.hidden =
                            false;

                    }
                );


                hanziDanceOptions
                    .appendChild(
                        button
                    );

            }
        );

    }



    /* =========================================================
       BẮT ĐẦU HANZI DANCE
    ========================================================= */

    function startHanziDance() {

        const validIndexes =
            hanzis
                .map(
                    function (
                        item,
                        index
                    ) {

                        if (
                            item.character
                            &&
                            item.meaning
                        ) {

                            return index;

                        }


                        return -1;

                    }
                )
                .filter(
                    function (
                        index
                    ) {

                        return (
                            index
                            >= 0
                        );

                    }
                );


        if (
            validIndexes.length
            < 2
        ) {

            if (
                hanziDanceArea
            ) {

                hanziDanceArea.hidden =
                    true;

            }


            showModeMessage(
                "Bài này chưa đủ dữ liệu chữ Hán để chơi Hanzi Dance."
            );


            return;

        }


        hanziDanceOrder =
            shuffledArray(
                validIndexes
            );


        hanziDancePosition =
            0;


        hanziDanceCorrect =
            0;


        if (
            hanziDanceResult
        ) {

            hanziDanceResult.hidden =
                true;

        }


        if (
            hanziDanceArea
        ) {

            hanziDanceArea.hidden =
                false;

        }


        renderHanziDanceQuestion();

    }



    /* =========================================================
       HANZI TIẾP THEO
    ========================================================= */

    function nextHanziDanceQuestion() {

        hanziDancePosition++;


        if (
            hanziDancePosition
            >= hanziDanceOrder.length
        ) {

            finishHanziDance();


            return;

        }


        renderHanziDanceQuestion();

    }



    /* =========================================================
       KẾT QUẢ HANZI DANCE
    ========================================================= */

    function finishHanziDance() {

        if (
            hanziDanceArea
        ) {

            hanziDanceArea.hidden =
                true;

        }


        if (
            hanziDanceResult
        ) {

            hanziDanceResult.hidden =
                false;

        }


        const total =
            hanziDanceOrder.length;


        const percent =
            total
                ? (
                    Math.round(
                        hanziDanceCorrect
                        / total
                        * 1000
                    )
                    / 10
                )
                : 0;


        hanziDanceScore.textContent =
            hanziDanceCorrect
            + " / "
            + total;


        hanziDancePercent.textContent =
            percent
            + "%";

    }



    /* =========================================================
       EVENT HANZI DANCE
    ========================================================= */

    if (
        hanziDanceNextButton
    ) {

        hanziDanceNextButton.addEventListener(
            "click",
            nextHanziDanceQuestion
        );

    }


    if (
        hanziDanceRestartButton
    ) {

        hanziDanceRestartButton.addEventListener(
            "click",
            startHanziDance
        );

    }



    /* =========================================================
       32. ĐẤU TRÍ
    ========================================================= */

    const battleArea =
        document.getElementById(
            "battleArea"
        );


    const battleResult =
        document.getElementById(
            "battleResult"
        );


    const battleProgress =
        document.getElementById(
            "battleProgress"
        );


    const battlePoints =
        document.getElementById(
            "battlePoints"
        );


    const battleTimer =
        document.getElementById(
            "battleTimer"
        );


    const battleQuestionLabel =
        document.getElementById(
            "battleQuestionLabel"
        );


    const battleQuestionMain =
        document.getElementById(
            "battleQuestionMain"
        );


    const battleQuestionSecondary =
        document.getElementById(
            "battleQuestionSecondary"
        );


    const battleOptions =
        document.getElementById(
            "battleOptions"
        );


    const battleFeedback =
        document.getElementById(
            "battleFeedback"
        );


    const battleNextButton =
        document.getElementById(
            "battleNextButton"
        );


    const battleFinalPoints =
        document.getElementById(
            "battleFinalPoints"
        );


    const battleScore =
        document.getElementById(
            "battleScore"
        );


    const battleRestartButton =
        document.getElementById(
            "battleRestartButton"
        );


    let battleOrder =
        [];


    let battlePosition =
        0;


    let battleCorrect =
        0;


    let battlePointValue =
        0;


    let battleAnswered =
        false;


    let battleSeconds =
        15;


    let battleInterval =
        null;


    let battleDirection =
        "zh-vi";



    /* =========================================================
       DỪNG ĐỒNG HỒ
    ========================================================= */

    function clearBattleTimer() {

        if (
            battleInterval
        ) {

            clearInterval(
                battleInterval
            );


            battleInterval =
                null;

        }

    }



    /* =========================================================
       TẠO ĐÁP ÁN ĐẤU TRÍ
    ========================================================= */

    function createBattleOptions(
        correctWord,
        directionName
    ) {

        const correct =
            directionName
            === "zh-vi"
                ? correctWord.meaning
                : correctWord.hanzi;


        const others =
            vocabularies
                .filter(
                    function (
                        word
                    ) {

                        if (
                            word.id
                            === correctWord.id
                        ) {

                            return false;

                        }


                        const value =
                            directionName
                            === "zh-vi"
                                ? word.meaning
                                : word.hanzi;


                        return (
                            value
                            &&
                            value
                            !== correct
                        );

                    }
                )
                .map(
                    function (
                        word
                    ) {

                        return (
                            directionName
                            === "zh-vi"
                                ? word.meaning
                                : word.hanzi
                        );

                    }
                );


        const uniqueOthers =
            [
                ...new Set(
                    others
                )
            ];


        const wrongAnswers =
            shuffledArray(
                uniqueOthers
            ).slice(
                0,
                3
            );


        return shuffledArray(
            [
                correct,
                ...wrongAnswers
            ]
        );

    }



    /* =========================================================
       ĐỒNG HỒ 15 GIÂY
    ========================================================= */

    function startBattleTimer(
        word,
        correctAnswer
    ) {

        clearBattleTimer();


        battleSeconds =
            15;


        battleTimer.textContent =
            battleSeconds
            + "s";


        battleInterval =
            setInterval(
                function () {

                    battleSeconds--;


                    battleTimer.textContent =
                        Math.max(
                            battleSeconds,
                            0
                        )
                        + "s";


                    if (
                        battleSeconds
                        <= 0
                    ) {

                        clearBattleTimer();


                        if (
                            !battleAnswered
                        ) {

                            answerBattle(
                                null,
                                null,
                                word,
                                correctAnswer
                            );

                        }

                    }

                },
                1000
            );

    }



    /* =========================================================
       HIỂN THỊ CÂU ĐẤU TRÍ
    ========================================================= */

    function renderBattleQuestion() {

        const word =
            vocabularies[
                battleOrder[
                    battlePosition
                ]
            ];


        if (
            !word
        ) {

            return;

        }


        battleAnswered =
            false;


        /*
         * Câu hỏi ngẫu nhiên:
         *
         * Trung -> Việt
         * hoặc
         * Việt -> Trung
         */
        battleDirection =
            Math.random()
            < 0.5
                ? "zh-vi"
                : "vi-zh";


        const correctAnswer =
            battleDirection
            === "zh-vi"
                ? word.meaning
                : word.hanzi;


        battleProgress.textContent =
            "Câu "
            + (battlePosition + 1)
            + " / "
            + battleOrder.length;


        battlePoints.textContent =
            battlePointValue
            + " điểm";


        if (
            battleDirection
            === "zh-vi"
        ) {

            battleQuestionLabel.textContent =
                "CHỌN NGHĨA ĐÚNG";


            battleQuestionMain.textContent =
                word.hanzi;


            battleQuestionSecondary.textContent =
                word.pinyin
                || "";

        }
        else {

            battleQuestionLabel.textContent =
                "CHỌN CHỮ HÁN ĐÚNG";


            battleQuestionMain.textContent =
                word.meaning;


            battleQuestionSecondary.textContent =
                "Bạn có 15 giây";

        }


        battleFeedback.textContent =
            "";


        battleFeedback.className =
            "battle-feedback";


        battleNextButton.hidden =
            true;


        battleOptions.innerHTML =
            "";


        const answers =
            createBattleOptions(
                word,
                battleDirection
            );


        answers.forEach(
            function (
                answer,
                index
            ) {

                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.className =
                    "battle-option";


                const letter =
                    String.fromCharCode(
                        65 + index
                    );


                button.innerHTML =
                    "<span>"
                    + letter
                    + "</span>"
                    + "<strong>"
                    + escapeHtml(
                        answer
                    )
                    + "</strong>";


                button.addEventListener(
                    "click",
                    function () {

                        answerBattle(
                            button,
                            answer,
                            word,
                            correctAnswer
                        );

                    }
                );


                battleOptions.appendChild(
                    button
                );

            }
        );


        startBattleTimer(
            word,
            correctAnswer
        );

    }



    /* =========================================================
       CHẤM ĐẤU TRÍ
    ========================================================= */

    function answerBattle(
        selectedButton,
        answer,
        word,
        correctAnswer
    ) {

        if (
            battleAnswered
        ) {

            return;

        }


        battleAnswered =
            true;


        clearBattleTimer();


        const buttons =
            battleOptions.querySelectorAll(
                ".battle-option"
            );


        buttons.forEach(
            function (
                button
            ) {

                button.disabled =
                    true;


                const strong =
                    button.querySelector(
                        "strong"
                    );


                if (
                    !strong
                ) {

                    return;

                }


                if (
                    strong.textContent
                    === correctAnswer
                ) {

                    button.classList.add(
                        "correct"
                    );

                }

            }
        );


        if (
            answer
            === correctAnswer
        ) {

            battleCorrect++;


            /*
             * Điểm:
             *
             * đúng = 100
             * +
             * thời gian còn lại x 5
             */
            const bonus =
                100
                + Math.max(
                    battleSeconds,
                    0
                )
                * 5;


            battlePointValue +=
                bonus;


            if (
                selectedButton
            ) {

                selectedButton.classList.add(
                    "correct"
                );

            }


            battleFeedback.textContent =
                "✓ Chính xác! +"
                + bonus
                + " điểm";


            battleFeedback.className =
                "battle-feedback correct";

        }
        else {

            if (
                selectedButton
            ) {

                selectedButton.classList.add(
                    "wrong"
                );

            }


            if (
                answer
                === null
            ) {

                battleFeedback.textContent =
                    "⌛ Hết giờ! Đáp án đúng: "
                    + correctAnswer;

            }
            else {

                battleFeedback.textContent =
                    "✕ Chưa đúng. Đáp án đúng: "
                    + correctAnswer;

            }


            battleFeedback.className =
                "battle-feedback wrong";

        }


        battlePoints.textContent =
            battlePointValue
            + " điểm";


        battleNextButton.hidden =
            false;

    }



    /* =========================================================
       BẮT ĐẦU ĐẤU TRÍ
    ========================================================= */

    function startBattle() {

        if (
            vocabularies.length
            < 2
        ) {

            if (
                battleArea
            ) {

                battleArea.hidden =
                    true;

            }


            showModeMessage(
                "Bài này chưa đủ từ vựng để chơi Đấu trí."
            );


            return;

        }


        /*
         * Mỗi lượt tối đa 10 câu.
         */
        battleOrder =
            shuffledArray(
                vocabularies.map(
                    function (
                        _,
                        index
                    ) {

                        return index;

                    }
                )
            ).slice(
                0,
                Math.min(
                    10,
                    vocabularies.length
                )
            );


        battlePosition =
            0;


        battleCorrect =
            0;


        battlePointValue =
            0;


        if (
            battleResult
        ) {

            battleResult.hidden =
                true;

        }


        if (
            battleArea
        ) {

            battleArea.hidden =
                false;

        }


        renderBattleQuestion();

    }



    /* =========================================================
       CÂU ĐẤU TRÍ TIẾP THEO
    ========================================================= */

    function nextBattleQuestion() {

        battlePosition++;


        if (
            battlePosition
            >= battleOrder.length
        ) {

            finishBattle();


            return;

        }


        renderBattleQuestion();

    }



    /* =========================================================
       KẾT QUẢ ĐẤU TRÍ
    ========================================================= */

    function finishBattle() {

        clearBattleTimer();


        if (
            battleArea
        ) {

            battleArea.hidden =
                true;

        }


        if (
            battleResult
        ) {

            battleResult.hidden =
                false;

        }


        battleFinalPoints.textContent =
            battlePointValue;


        battleScore.textContent =
            battleCorrect
            + " / "
            + battleOrder.length;

    }



    /* =========================================================
       EVENT ĐẤU TRÍ
    ========================================================= */

    if (
        battleNextButton
    ) {

        battleNextButton.addEventListener(
            "click",
            nextBattleQuestion
        );

    }


    if (
        battleRestartButton
    ) {

        battleRestartButton.addEventListener(
            "click",
            startBattle
        );

    }



    /* =========================================================
       33. ẨN TẤT CẢ KHUNG HỌC
    ========================================================= */

    function hideAllStudyAreas() {

        /*
         * Dừng audio từ vựng /
         * chữ Hán.
         */
        stopCurrentLessonAudio();


        /*
         * Dừng câu đang đọc.
         */
        stopListeningSpeech();


        /*
         * Dừng đồng hồ Đấu trí.
         */
        clearBattleTimer();


        const areas =
            [
                flashcardToolbar,
                flashcardShell,

                quizArea,
                quizResult,

                typingArea,
                typingResult,

                readingArea,
                readingResult,
                readingUnavailable,

                listeningArea,
                listeningResult,

                hanziDanceArea,
                hanziDanceResult,

                battleArea,
                battleResult,

                modeNotice
            ];


        areas.forEach(
            function (
                area
            ) {

                if (
                    area
                ) {

                    area.hidden =
                        true;

                }

            }
        );

    }



    /* =========================================================
       34. HIỂN THỊ FLASHCARD
    ========================================================= */

    function showFlashcardMode(
        shouldScroll = true
    ) {

        hideAllStudyAreas();


        setActiveMode(
            "flashcard",
            "Đang học"
        );


        if (
            flashcardToolbar
        ) {

            flashcardToolbar.hidden =
                false;

        }


        if (
            flashcardShell
        ) {

            flashcardShell.hidden =
                false;

        }


        if (
            shouldScroll
        ) {

            scrollToStudyArea(
                flashcardToolbar
                || flashcardShell
            );

        }

    }



    /* =========================================================
       HIỂN THỊ TRẮC NGHIỆM
    ========================================================= */

    function showQuizMode() {

        hideAllStudyAreas();


        setActiveMode(
            "quiz",
            "Đang học"
        );


        startQuiz();


        scrollToStudyArea(
            quizArea
        );

    }



    /* =========================================================
       HIỂN THỊ GÕ TỪ
    ========================================================= */

    function showTypingMode() {

        hideAllStudyAreas();


        setActiveMode(
            "typing",
            "Đang học"
        );


        startTyping();


        scrollToStudyArea(
            typingArea
        );

    }



    /* =========================================================
       HIỂN THỊ ĐỌC HIỂU
    ========================================================= */

    function showReadingMode() {

        hideAllStudyAreas();


        setActiveMode(
            "reading",
            "Đang học"
        );


        startReading();


        scrollToStudyArea(
            readingArea
            &&
            !readingArea.hidden
                ? readingArea
                : readingUnavailable
        );

    }



    /* =========================================================
       HIỂN THỊ NGHE GHÉP CÂU
    ========================================================= */

    function showListeningMode() {

        hideAllStudyAreas();


        setActiveMode(
            "listening",
            "Đang học"
        );


        startListening();


        scrollToStudyArea(
            listeningArea
            &&
            !listeningArea.hidden
                ? listeningArea
                : modeNotice
        );

    }



    /* =========================================================
       HIỂN THỊ HANZI DANCE
    ========================================================= */

    function showHanziDanceMode() {

        hideAllStudyAreas();


        setActiveMode(
            "hanzi-dance",
            "Đang chơi"
        );


        startHanziDance();


        scrollToStudyArea(
            hanziDanceArea
            &&
            !hanziDanceArea.hidden
                ? hanziDanceArea
                : modeNotice
        );

    }



    /* =========================================================
       HIỂN THỊ ĐẤU TRÍ
    ========================================================= */

    function showBattleMode() {

        hideAllStudyAreas();


        setActiveMode(
            "battle",
            "Đang chơi"
        );


        startBattle();


        scrollToStudyArea(
            battleArea
            &&
            !battleArea.hidden
                ? battleArea
                : modeNotice
        );

    }



    /* =========================================================
       35. CLICK CHẾ ĐỘ HỌC
    ========================================================= */

    modeCards.forEach(
        function (
            card
        ) {

            card.addEventListener(
                "click",
                function () {

                    const mode =
                        card.dataset
                            .studyMode;


                    if (
                        mode
                        === "flashcard"
                    ) {

                        showFlashcardMode();


                        return;

                    }


                    if (
                        mode
                        === "quiz"
                    ) {

                        showQuizMode();


                        return;

                    }


                    if (
                        mode
                        === "typing"
                    ) {

                        showTypingMode();


                        return;

                    }


                    if (
                        mode
                        === "reading"
                    ) {

                        showReadingMode();


                        return;

                    }


                    if (
                        mode
                        === "listening"
                    ) {

                        showListeningMode();


                        return;

                    }


                    if (
                        mode
                        === "hanzi-dance"
                    ) {

                        showHanziDanceMode();


                        return;

                    }


                    if (
                        mode
                        === "battle"
                    ) {

                        showBattleMode();

                    }

                }
            );

        }
    );



        /* =========================================================
       36. NGỮ PHÁP - ĐỌC DỮ LIỆU
    ========================================================= */

    const grammarDataElement =
        document.getElementById(
            "lessonGrammarData"
        );


    let grammars =
        [];


    if (
        grammarDataElement
    ) {

        try {

            grammars =
                JSON.parse(
                    grammarDataElement.textContent
                );

        }
        catch (
            error
        ) {

            console.error(
                "Không đọc được dữ liệu ngữ pháp:",
                error
            );


            grammars =
                [];

        }

    }



    /* =========================================================
       37. NGỮ PHÁP - ELEMENT
    ========================================================= */

    const grammarModeCards =
        document.querySelectorAll(
            ".grammar-study-mode-card"
        );


    const grammarModeNotice =
        document.getElementById(
            "grammarModeNotice"
        );



    /* HỌC CẤU TRÚC */

    const grammarStudyArea =
        document.getElementById(
            "grammarStudyArea"
        );


    const grammarStudyProgress =
        document.getElementById(
            "grammarStudyProgress"
        );


    const grammarStudyTitle =
        document.getElementById(
            "grammarStudyTitle"
        );


    const grammarStudyDescription =
        document.getElementById(
            "grammarStudyDescription"
        );


    const grammarStudyUsage =
        document.getElementById(
            "grammarStudyUsage"
        );


    const grammarStudyExampleChinese =
        document.getElementById(
            "grammarStudyExampleChinese"
        );


    const grammarStudyExamplePinyin =
        document.getElementById(
            "grammarStudyExamplePinyin"
        );


    const grammarStudyExampleVietnamese =
        document.getElementById(
            "grammarStudyExampleVietnamese"
        );


    const grammarPreviousButton =
        document.getElementById(
            "grammarPreviousButton"
        );


    const grammarNextButton =
        document.getElementById(
            "grammarNextButton"
        );


    const grammarShuffleButton =
        document.getElementById(
            "grammarShuffleButton"
        );


    const grammarDetailCards =
        document.querySelectorAll(
            ".grammar-detail-card"
        );



    /* CHỌN ĐÁP ÁN */

    const grammarQuizArea =
        document.getElementById(
            "grammarQuizArea"
        );


    const grammarQuizProgress =
        document.getElementById(
            "grammarQuizProgress"
        );


    const grammarQuizExample =
        document.getElementById(
            "grammarQuizExample"
        );


    const grammarQuizPinyin =
        document.getElementById(
            "grammarQuizPinyin"
        );


    const grammarQuizOptions =
        document.getElementById(
            "grammarQuizOptions"
        );


    const grammarQuizFeedback =
        document.getElementById(
            "grammarQuizFeedback"
        );


    const grammarQuizNextButton =
        document.getElementById(
            "grammarQuizNextButton"
        );


    const grammarQuizResult =
        document.getElementById(
            "grammarQuizResult"
        );


    const grammarQuizScore =
        document.getElementById(
            "grammarQuizScore"
        );


    const grammarQuizPercent =
        document.getElementById(
            "grammarQuizPercent"
        );


    const grammarQuizRestartButton =
        document.getElementById(
            "grammarQuizRestartButton"
        );


    const grammarQuizBackButton =
        document.getElementById(
            "grammarQuizBackButton"
        );



    /* ĐIỀN TỪ */

    const grammarFillArea =
        document.getElementById(
            "grammarFillArea"
        );


    const grammarFillProgress =
        document.getElementById(
            "grammarFillProgress"
        );


    const grammarFillSentence =
        document.getElementById(
            "grammarFillSentence"
        );


    const grammarFillPinyin =
        document.getElementById(
            "grammarFillPinyin"
        );


    const grammarFillVietnamese =
        document.getElementById(
            "grammarFillVietnamese"
        );


    const grammarFillInput =
        document.getElementById(
            "grammarFillInput"
        );


    const grammarFillCheckButton =
        document.getElementById(
            "grammarFillCheckButton"
        );


    const grammarFillFeedback =
        document.getElementById(
            "grammarFillFeedback"
        );


    const grammarFillNextButton =
        document.getElementById(
            "grammarFillNextButton"
        );


    const grammarFillResult =
        document.getElementById(
            "grammarFillResult"
        );


    const grammarFillScore =
        document.getElementById(
            "grammarFillScore"
        );


    const grammarFillPercent =
        document.getElementById(
            "grammarFillPercent"
        );


    const grammarFillRestartButton =
        document.getElementById(
            "grammarFillRestartButton"
        );


    const grammarFillBackButton =
        document.getElementById(
            "grammarFillBackButton"
        );



    /* SẮP XẾP CÂU */

    const grammarArrangeArea =
        document.getElementById(
            "grammarArrangeArea"
        );


    const grammarArrangeProgress =
        document.getElementById(
            "grammarArrangeProgress"
        );


    const grammarArrangeVietnamese =
        document.getElementById(
            "grammarArrangeVietnamese"
        );


    const grammarArrangePinyin =
        document.getElementById(
            "grammarArrangePinyin"
        );


    const grammarArrangeSlots =
        document.getElementById(
            "grammarArrangeSlots"
        );


    const grammarTokenBank =
        document.getElementById(
            "grammarTokenBank"
        );


    const grammarArrangeFeedback =
        document.getElementById(
            "grammarArrangeFeedback"
        );


    const grammarArrangeNextButton =
        document.getElementById(
            "grammarArrangeNextButton"
        );


    const grammarArrangeResult =
        document.getElementById(
            "grammarArrangeResult"
        );


    const grammarArrangeScore =
        document.getElementById(
            "grammarArrangeScore"
        );


    const grammarArrangePercent =
        document.getElementById(
            "grammarArrangePercent"
        );


    const grammarArrangeRestartButton =
        document.getElementById(
            "grammarArrangeRestartButton"
        );


    const grammarArrangeBackButton =
        document.getElementById(
            "grammarArrangeBackButton"
        );



    /* =========================================================
       38. NGỮ PHÁP - HÀM CHUNG
    ========================================================= */

    function setActiveGrammarMode(
        modeName
    ) {

        grammarModeCards.forEach(
            function (
                card
            ) {

                const active =
                    card.dataset.grammarMode
                    === modeName;


                card.classList.toggle(
                    "active",
                    active
                );


                const status =
                    card.querySelector(
                        ".grammar-mode-status"
                    );


                if (
                    !status
                ) {

                    return;

                }


                if (
                    active
                ) {

                    status.textContent =
                        "Đang học";


                    status.classList.add(
                        "grammar-mode-status-active"
                    );

                }
                else {

                    status.textContent =
                        "Chưa học";


                    status.classList.remove(
                        "grammar-mode-status-active"
                    );

                }

            }
        );

    }



    function hideAllGrammarAreas() {

        const areas =
            [
                grammarStudyArea,

                grammarQuizArea,
                grammarQuizResult,

                grammarFillArea,
                grammarFillResult,

                grammarArrangeArea,
                grammarArrangeResult,

                grammarModeNotice
            ];


        areas.forEach(
            function (
                area
            ) {

                if (
                    area
                ) {

                    area.hidden =
                        true;

                }

            }
        );

    }



    function scrollToGrammarArea(
        area
    ) {

        if (
            !area
        ) {

            return;

        }


        setTimeout(
            function () {

                area.scrollIntoView(
                    {
                        behavior:
                            "smooth",

                        block:
                            "start"
                    }
                );

            },
            30
        );

    }



    function showGrammarNotice(
        message
    ) {

        if (
            !grammarModeNotice
        ) {

            return;

        }


        grammarModeNotice.hidden =
            false;


        grammarModeNotice.textContent =
            message;

    }



    function grammarPercent(
        correct,
        total
    ) {

        if (
            !total
        ) {

            return 0;

        }


        return (
            Math.round(
                (
                    correct
                    / total
                )
                * 1000
            )
            / 10
        );

    }



    function normalizeGrammarText(
        value
    ) {

        return String(
            value
            || ""
        )
            .replace(
                /\s+/g,
                ""
            )
            .replace(
                /[，。！？、；：,.!?;:“”"'（）()《》]/g,
                ""
            )
            .trim();

    }



    /* =========================================================
       39. HỌC CẤU TRÚC
    ========================================================= */

    let grammarStudyOrder =
        grammars.map(
            function (
                _,
                index
            ) {

                return index;

            }
        );


    let grammarStudyPosition =
        0;



    function getCurrentGrammar() {

        if (
            grammarStudyOrder.length
            === 0
        ) {

            return null;

        }


        const index =
            grammarStudyOrder[
                grammarStudyPosition
            ];


        return grammars[
            index
        ]
        || null;

    }



    function updateGrammarDetailCards() {

        if (
            grammarStudyOrder.length
            === 0
        ) {

            return;

        }


        const currentIndex =
            grammarStudyOrder[
                grammarStudyPosition
            ];


        grammarDetailCards.forEach(
            function (
                card
            ) {

                const cardIndex =
                    Number(
                        card.dataset.grammarIndex
                    );


                card.classList.toggle(
                    "active",
                    cardIndex
                    === currentIndex
                );

            }
        );

    }



    function renderGrammarStudy() {

        const grammar =
            getCurrentGrammar();


        if (
            !grammar
        ) {

            return;

        }


        if (
            grammarStudyProgress
        ) {

            grammarStudyProgress.textContent =
                "Cấu trúc "
                + (
                    grammarStudyPosition
                    + 1
                )
                + " / "
                + grammarStudyOrder.length;

        }


        if (
            grammarStudyTitle
        ) {

            grammarStudyTitle.textContent =
                grammar.title
                || "";

        }


        if (
            grammarStudyDescription
        ) {

            grammarStudyDescription.textContent =
                grammar.description
                || "";

        }


        if (
            grammarStudyUsage
        ) {

            grammarStudyUsage.textContent =
                grammar.usage
                || "";

        }


        if (
            grammarStudyExampleChinese
        ) {

            grammarStudyExampleChinese.textContent =
                grammar.exampleChinese
                || "";

        }


        if (
            grammarStudyExamplePinyin
        ) {

            grammarStudyExamplePinyin.textContent =
                grammar.examplePinyin
                || "";

        }


        if (
            grammarStudyExampleVietnamese
        ) {

            grammarStudyExampleVietnamese.textContent =
                grammar.exampleVietnamese
                || "";

        }


        updateGrammarDetailCards();

    }



    function showGrammarStudyMode(
        shouldScroll = true
    ) {

        hideAllGrammarAreas();


        setActiveGrammarMode(
            "study"
        );


        if (
            grammarStudyArea
        ) {

            grammarStudyArea.hidden =
                false;

        }


        renderGrammarStudy();


        if (
            shouldScroll
        ) {

            scrollToGrammarArea(
                grammarStudyArea
            );

        }

    }



    if (
        grammarPreviousButton
    ) {

        grammarPreviousButton.addEventListener(
            "click",
            function () {

                if (
                    grammarStudyOrder.length
                    === 0
                ) {

                    return;

                }


                grammarStudyPosition--;


                if (
                    grammarStudyPosition
                    < 0
                ) {

                    grammarStudyPosition =
                        grammarStudyOrder.length
                        - 1;

                }


                renderGrammarStudy();

            }
        );

    }



    if (
        grammarNextButton
    ) {

        grammarNextButton.addEventListener(
            "click",
            function () {

                if (
                    grammarStudyOrder.length
                    === 0
                ) {

                    return;

                }


                grammarStudyPosition++;


                if (
                    grammarStudyPosition
                    >= grammarStudyOrder.length
                ) {

                    grammarStudyPosition =
                        0;

                }


                renderGrammarStudy();

            }
        );

    }



    if (
        grammarShuffleButton
    ) {

        grammarShuffleButton.addEventListener(
            "click",
            function () {

                grammarStudyOrder =
                    shuffledArray(
                        grammarStudyOrder
                    );


                grammarStudyPosition =
                    0;


                renderGrammarStudy();

            }
        );

    }



    grammarDetailCards.forEach(
        function (
            card
        ) {

            card.addEventListener(
                "click",
                function () {

                    const originalIndex =
                        Number(
                            card.dataset.grammarIndex
                        );


                    let position =
                        grammarStudyOrder.indexOf(
                            originalIndex
                        );


                    if (
                        position
                        === -1
                    ) {

                        grammarStudyOrder =
                            grammars.map(
                                function (
                                    _,
                                    index
                                ) {

                                    return index;

                                }
                            );


                        position =
                            originalIndex;

                    }


                    grammarStudyPosition =
                        position;


                    showGrammarStudyMode();

                }
            );

        }
    );



    /* =========================================================
       40. CHỌN ĐÁP ÁN
    ========================================================= */

    let grammarQuizOrder =
        [];


    let grammarQuizPosition =
        0;


    let grammarQuizCorrect =
        0;


    let grammarQuizAnswered =
        false;



    function createGrammarQuizOptions(
        correctGrammar
    ) {

        const otherTitles =
            grammars
                .filter(
                    function (
                        grammar
                    ) {

                        return (
                            grammar.id
                            !== correctGrammar.id

                            &&

                            grammar.title
                            !== correctGrammar.title
                        );

                    }
                )
                .map(
                    function (
                        grammar
                    ) {

                        return grammar.title;

                    }
                );


        const uniqueOthers =
            [
                ...new Set(
                    otherTitles
                )
            ];


        const wrongAnswers =
            shuffledArray(
                uniqueOthers
            ).slice(
                0,
                3
            );


        return shuffledArray(
            [
                correctGrammar.title,
                ...wrongAnswers
            ]
        );

    }



    function startGrammarQuiz() {

        if (
            grammars.length
            < 2
        ) {

            showGrammarNotice(
                "Bài này chưa đủ dữ liệu để tạo bài Chọn đáp án."
            );


            return;

        }


        grammarQuizOrder =
            shuffledArray(
                grammars.map(
                    function (
                        _,
                        index
                    ) {

                        return index;

                    }
                )
            );


        grammarQuizPosition =
            0;


        grammarQuizCorrect =
            0;


        grammarQuizAnswered =
            false;


        if (
            grammarQuizResult
        ) {

            grammarQuizResult.hidden =
                true;

        }


        if (
            grammarQuizArea
        ) {

            grammarQuizArea.hidden =
                false;

        }


        renderGrammarQuizQuestion();

    }



    function renderGrammarQuizQuestion() {

        if (
            !grammarQuizArea
            ||
            grammarQuizOrder.length
            === 0
        ) {

            return;

        }


        grammarQuizAnswered =
            false;


        const grammar =
            grammars[
                grammarQuizOrder[
                    grammarQuizPosition
                ]
            ];


        grammarQuizProgress.textContent =
            "Câu "
            + (
                grammarQuizPosition
                + 1
            )
            + " / "
            + grammarQuizOrder.length;


        grammarQuizExample.textContent =
            grammar.exampleChinese
            || "";


        grammarQuizPinyin.textContent =
            grammar.examplePinyin
            || "";


        grammarQuizFeedback.textContent =
            "";


        grammarQuizFeedback.className =
            "grammar-feedback";


        grammarQuizNextButton.hidden =
            true;


        grammarQuizOptions.innerHTML =
            "";


        const answers =
            createGrammarQuizOptions(
                grammar
            );


        answers.forEach(
            function (
                answer,
                index
            ) {

                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.className =
                    "grammar-answer-option";


                const letter =
                    String.fromCharCode(
                        65 + index
                    );


                button.innerHTML =
                    "<span>"
                    + letter
                    + "</span>"
                    + "<strong>"
                    + escapeHtml(
                        answer
                    )
                    + "</strong>";


                button.addEventListener(
                    "click",
                    function () {

                        answerGrammarQuiz(
                            button,
                            answer,
                            grammar
                        );

                    }
                );


                grammarQuizOptions.appendChild(
                    button
                );

            }
        );

    }



    function answerGrammarQuiz(
        selectedButton,
        answer,
        grammar
    ) {

        if (
            grammarQuizAnswered
        ) {

            return;

        }


        grammarQuizAnswered =
            true;


        const buttons =
            grammarQuizOptions
                .querySelectorAll(
                    ".grammar-answer-option"
                );


        buttons.forEach(
            function (
                button
            ) {

                button.disabled =
                    true;


                const strong =
                    button.querySelector(
                        "strong"
                    );


                if (
                    strong
                    &&
                    strong.textContent
                    === grammar.title
                ) {

                    button.classList.add(
                        "correct"
                    );

                }

            }
        );


        if (
            answer
            === grammar.title
        ) {

            grammarQuizCorrect++;


            selectedButton.classList.add(
                "correct"
            );


            grammarQuizFeedback.textContent =
                "✓ Chính xác! "
                + (
                    grammar.exampleVietnamese
                    || ""
                );


            grammarQuizFeedback.className =
                "grammar-feedback correct";

        }
        else {

            selectedButton.classList.add(
                "wrong"
            );


            grammarQuizFeedback.innerHTML =
                "✕ Chưa đúng. Cấu trúc đúng: "
                + "<strong>"
                + escapeHtml(
                    grammar.title
                )
                + "</strong>";


            grammarQuizFeedback.className =
                "grammar-feedback wrong";

        }


        grammarQuizNextButton.hidden =
            false;

    }



    function nextGrammarQuizQuestion() {

        grammarQuizPosition++;


        if (
            grammarQuizPosition
            >= grammarQuizOrder.length
        ) {

            finishGrammarQuiz();


            return;

        }


        renderGrammarQuizQuestion();

    }



    function finishGrammarQuiz() {

        grammarQuizArea.hidden =
            true;


        grammarQuizResult.hidden =
            false;


        grammarQuizScore.textContent =
            grammarQuizCorrect
            + " / "
            + grammarQuizOrder.length;


        grammarQuizPercent.textContent =
            grammarPercent(
                grammarQuizCorrect,
                grammarQuizOrder.length
            )
            + "%";

    }



    if (
        grammarQuizNextButton
    ) {

        grammarQuizNextButton.addEventListener(
            "click",
            nextGrammarQuizQuestion
        );

    }



    if (
        grammarQuizRestartButton
    ) {

        grammarQuizRestartButton.addEventListener(
            "click",
            function () {

                hideAllGrammarAreas();


                setActiveGrammarMode(
                    "quiz"
                );


                startGrammarQuiz();

            }
        );

    }



    if (
        grammarQuizBackButton
    ) {

        grammarQuizBackButton.addEventListener(
            "click",
            function () {

                showGrammarStudyMode();

            }
        );

    }



    /* =========================================================
       41. ĐIỀN TỪ
    ========================================================= */

    let grammarFillQuestions =
        [];


    let grammarFillOrder =
        [];


    let grammarFillPosition =
        0;


    let grammarFillCorrect =
        0;


    let grammarFillAnswered =
        false;



    function findGrammarFillAnswer(
        grammar
    ) {

        const title =
            String(
                grammar.title
                || ""
            );


        const sentence =
            String(
                grammar.exampleChinese
                || ""
            );


        const matches =
            title.match(
                /[\u3400-\u9fff]+/g
            )
            || [];


        const candidates =
            [
                ...new Set(
                    matches
                )
            ].sort(
                function (
                    a,
                    b
                ) {

                    return (
                        b.length
                        - a.length
                    );

                }
            );


        for (
            let i = 0;
            i < candidates.length;
            i++
        ) {

            if (
                sentence.includes(
                    candidates[i]
                )
            ) {

                return candidates[i];

            }

        }


        return "";

    }



    function buildGrammarFillQuestions() {

        return grammars
            .map(
                function (
                    grammar
                ) {

                    const answer =
                        findGrammarFillAnswer(
                            grammar
                        );


                    if (
                        !answer
                    ) {

                        return null;

                    }


                    return {

                        grammar:
                            grammar,


                        answer:
                            answer,


                        blankSentence:
                            String(
                                grammar.exampleChinese
                                || ""
                            ).replace(
                                answer,
                                "＿＿＿"
                            )

                    };

                }
            )
            .filter(
                Boolean
            );

    }



    function startGrammarFill() {

        grammarFillQuestions =
            buildGrammarFillQuestions();


        if (
            grammarFillQuestions.length
            === 0
        ) {

            showGrammarNotice(
                "Bài này chưa có cấu trúc phù hợp để tạo bài Điền từ."
            );


            return;

        }


        grammarFillOrder =
            shuffledArray(
                grammarFillQuestions.map(
                    function (
                        _,
                        index
                    ) {

                        return index;

                    }
                )
            );


        grammarFillPosition =
            0;


        grammarFillCorrect =
            0;


        grammarFillAnswered =
            false;


        grammarFillResult.hidden =
            true;


        grammarFillArea.hidden =
            false;


        renderGrammarFillQuestion();

    }



    function getCurrentGrammarFillQuestion() {

        return grammarFillQuestions[
            grammarFillOrder[
                grammarFillPosition
            ]
        ];

    }



    function renderGrammarFillQuestion() {

        const question =
            getCurrentGrammarFillQuestion();


        if (
            !question
        ) {

            return;

        }


        grammarFillAnswered =
            false;


        grammarFillProgress.textContent =
            "Câu "
            + (
                grammarFillPosition
                + 1
            )
            + " / "
            + grammarFillOrder.length;


        grammarFillSentence.textContent =
            question.blankSentence;


        grammarFillPinyin.textContent =
            question.grammar.examplePinyin
            || "";


        grammarFillVietnamese.textContent =
            question.grammar.exampleVietnamese
            || "";


        grammarFillInput.value =
            "";


        grammarFillInput.disabled =
            false;


        grammarFillCheckButton.disabled =
            false;


        grammarFillFeedback.textContent =
            "";


        grammarFillFeedback.className =
            "grammar-feedback";


        grammarFillNextButton.hidden =
            true;


        setTimeout(
            function () {

                grammarFillInput.focus();

            },
            30
        );

    }



    function checkGrammarFillAnswer() {

        if (
            grammarFillAnswered
        ) {

            return;

        }


        const question =
            getCurrentGrammarFillQuestion();


        if (
            !question
        ) {

            return;

        }


        const answer =
            normalizeGrammarText(
                grammarFillInput.value
            );


        if (
            !answer
        ) {

            grammarFillFeedback.textContent =
                "Bạn chưa nhập đáp án.";


            grammarFillFeedback.className =
                "grammar-feedback wrong";


            grammarFillInput.focus();


            return;

        }


        grammarFillAnswered =
            true;


        grammarFillInput.disabled =
            true;


        grammarFillCheckButton.disabled =
            true;


        if (
            answer
            === normalizeGrammarText(
                question.answer
            )
        ) {

            grammarFillCorrect++;


            grammarFillFeedback.textContent =
                "✓ Chính xác! Cấu trúc: "
                + question.grammar.title;


            grammarFillFeedback.className =
                "grammar-feedback correct";

        }
        else {

            grammarFillFeedback.innerHTML =
                "✕ Chưa đúng. Đáp án: "
                + "<strong>"
                + escapeHtml(
                    question.answer
                )
                + "</strong>"
                + "<br>"
                + escapeHtml(
                    question.grammar.exampleChinese
                );


            grammarFillFeedback.className =
                "grammar-feedback wrong";

        }


        grammarFillNextButton.hidden =
            false;

    }



    function nextGrammarFillQuestion() {

        grammarFillPosition++;


        if (
            grammarFillPosition
            >= grammarFillOrder.length
        ) {

            finishGrammarFill();


            return;

        }


        renderGrammarFillQuestion();

    }



    function finishGrammarFill() {

        grammarFillArea.hidden =
            true;


        grammarFillResult.hidden =
            false;


        grammarFillScore.textContent =
            grammarFillCorrect
            + " / "
            + grammarFillOrder.length;


        grammarFillPercent.textContent =
            grammarPercent(
                grammarFillCorrect,
                grammarFillOrder.length
            )
            + "%";

    }



    if (
        grammarFillCheckButton
    ) {

        grammarFillCheckButton.addEventListener(
            "click",
            checkGrammarFillAnswer
        );

    }



    if (
        grammarFillInput
    ) {

        grammarFillInput.addEventListener(
            "keydown",
            function (
                event
            ) {

                if (
                    event.key
                    !== "Enter"
                ) {

                    return;

                }


                if (
                    grammarFillAnswered
                ) {

                    nextGrammarFillQuestion();

                }
                else {

                    checkGrammarFillAnswer();

                }

            }
        );

    }



    if (
        grammarFillNextButton
    ) {

        grammarFillNextButton.addEventListener(
            "click",
            nextGrammarFillQuestion
        );

    }



    if (
        grammarFillRestartButton
    ) {

        grammarFillRestartButton.addEventListener(
            "click",
            function () {

                hideAllGrammarAreas();


                setActiveGrammarMode(
                    "fill"
                );


                startGrammarFill();

            }
        );

    }



    if (
        grammarFillBackButton
    ) {

        grammarFillBackButton.addEventListener(
            "click",
            function () {

                showGrammarStudyMode();

            }
        );

    }



    /* =========================================================
       42. SẮP XẾP CÂU
    ========================================================= */

    let grammarArrangeQuestions =
        [];


    let grammarArrangeOrder =
        [];


    let grammarArrangePosition =
        0;


    let grammarArrangeCorrect =
        0;


    let grammarArrangeSolved =
        false;


    let grammarArrangeTokens =
        [];


    let grammarArrangeSelected =
        [];



    function buildGrammarArrangeTokens(
        sentence
    ) {

        let tokens =
            [];


        if (
            typeof tokenizeChineseSentence
            === "function"
        ) {

            tokens =
                tokenizeChineseSentence(
                    sentence
                );

        }


        if (
            tokens.length
            < 2
        ) {

            tokens =
                Array.from(
                    normalizeGrammarText(
                        sentence
                    )
                );

        }


        return tokens;

    }



    function buildGrammarArrangeQuestions() {

        return grammars
            .map(
                function (
                    grammar
                ) {

                    const sentence =
                        String(
                            grammar.exampleChinese
                            || ""
                        ).trim();


                    if (
                        !sentence
                    ) {

                        return null;

                    }


                    const tokens =
                        buildGrammarArrangeTokens(
                            sentence
                        );


                    if (
                        tokens.length
                        < 2
                    ) {

                        return null;

                    }


                    return {

                        grammar:
                            grammar,


                        sentence:
                            sentence,


                        tokens:
                            tokens

                    };

                }
            )
            .filter(
                Boolean
            );

    }



    function startGrammarArrange() {

        grammarArrangeQuestions =
            buildGrammarArrangeQuestions();


        if (
            grammarArrangeQuestions.length
            === 0
        ) {

            showGrammarNotice(
                "Bài này chưa đủ dữ liệu để tạo bài Sắp xếp câu."
            );


            return;

        }


        grammarArrangeOrder =
            shuffledArray(
                grammarArrangeQuestions.map(
                    function (
                        _,
                        index
                    ) {

                        return index;

                    }
                )
            );


        grammarArrangePosition =
            0;


        grammarArrangeCorrect =
            0;


        grammarArrangeResult.hidden =
            true;


        grammarArrangeArea.hidden =
            false;


        renderGrammarArrangeQuestion();

    }



    function getCurrentGrammarArrangeQuestion() {

        return grammarArrangeQuestions[
            grammarArrangeOrder[
                grammarArrangePosition
            ]
        ];

    }



    function renderGrammarArrangeQuestion() {

        const question =
            getCurrentGrammarArrangeQuestion();


        if (
            !question
        ) {

            return;

        }


        grammarArrangeSolved =
            false;


        grammarArrangeSelected =
            [];


        grammarArrangeTokens =
            shuffledArray(
                question.tokens.map(
                    function (
                        text,
                        index
                    ) {

                        return {

                            id:
                                grammarArrangePosition
                                + "_"
                                + index
                                + "_"
                                + Math.random(),


                            text:
                                text

                        };

                    }
                )
            );


        grammarArrangeProgress.textContent =
            "Câu "
            + (
                grammarArrangePosition
                + 1
            )
            + " / "
            + grammarArrangeOrder.length;


        grammarArrangeVietnamese.textContent =
            question.grammar.exampleVietnamese
            || "";


        grammarArrangePinyin.textContent =
            question.grammar.examplePinyin
            || "";


        grammarArrangeFeedback.textContent =
            "";


        grammarArrangeFeedback.className =
            "grammar-feedback";


        grammarArrangeNextButton.hidden =
            true;


        renderGrammarArrangeTokens();

    }



    function renderGrammarArrangeTokens() {

        grammarArrangeSlots.innerHTML =
            "";


        grammarTokenBank.innerHTML =
            "";


        grammarArrangeSelected.forEach(
            function (
                item
            ) {

                const button =
                    document.createElement(
                        "button"
                    );


                button.type =
                    "button";


                button.className =
                    "grammar-selected-token";


                button.textContent =
                    item.text;


                button.addEventListener(
                    "click",
                    function () {

                        if (
                            grammarArrangeSolved
                        ) {

                            return;

                        }


                        grammarArrangeSelected =
                            grammarArrangeSelected.filter(
                                function (
                                    selected
                                ) {

                                    return (
                                        selected.id
                                        !== item.id
                                    );

                                }
                            );


                        grammarArrangeFeedback.textContent =
                            "";


                        grammarArrangeFeedback.className =
                            "grammar-feedback";


                        renderGrammarArrangeTokens();

                    }
                );


                grammarArrangeSlots.appendChild(
                    button
                );

            }
        );



        grammarArrangeTokens
            .filter(
                function (
                    item
                ) {

                    return !grammarArrangeSelected.some(
                        function (
                            selected
                        ) {

                            return (
                                selected.id
                                === item.id
                            );

                        }
                    );

                }
            )
            .forEach(
                function (
                    item
                ) {

                    const button =
                        document.createElement(
                            "button"
                        );


                    button.type =
                        "button";


                    button.className =
                        "grammar-token";


                    button.textContent =
                        item.text;


                    button.addEventListener(
                        "click",
                        function () {

                            if (
                                grammarArrangeSolved
                            ) {

                                return;

                            }


                            grammarArrangeSelected.push(
                                item
                            );


                            renderGrammarArrangeTokens();


                            checkGrammarArrangeAnswer();

                        }
                    );


                    grammarTokenBank.appendChild(
                        button
                    );

                }
            );



        if (
            grammarArrangeSelected.length
            === 0
        ) {

            const placeholder =
                document.createElement(
                    "span"
                );


            placeholder.className =
                "grammar-arrange-placeholder";


            placeholder.textContent =
                "Bấm các thẻ bên dưới để ghép câu";


            grammarArrangeSlots.appendChild(
                placeholder
            );

        }

    }



    function checkGrammarArrangeAnswer() {

        const question =
            getCurrentGrammarArrangeQuestion();


        if (
            !question
            ||
            grammarArrangeSelected.length
            !== question.tokens.length
        ) {

            return;

        }


        const answer =
            normalizeGrammarText(
                grammarArrangeSelected
                    .map(
                        function (
                            item
                        ) {

                            return item.text;

                        }
                    )
                    .join(
                        ""
                    )
            );


        const correctAnswer =
            normalizeGrammarText(
                question.sentence
            );


        if (
            answer
            === correctAnswer
        ) {

            grammarArrangeSolved =
                true;


            grammarArrangeCorrect++;


            grammarArrangeFeedback.textContent =
                "✓ Chính xác! "
                + (
                    question.grammar.exampleVietnamese
                    || ""
                );


            grammarArrangeFeedback.className =
                "grammar-feedback correct";


            grammarArrangeNextButton.hidden =
                false;

        }
        else {

            grammarArrangeFeedback.textContent =
                "✕ Thứ tự chưa đúng. "
                + "Bấm vào thẻ đã ghép để đưa thẻ xuống lại.";


            grammarArrangeFeedback.className =
                "grammar-feedback wrong";

        }

    }



    function nextGrammarArrangeQuestion() {

        grammarArrangePosition++;


        if (
            grammarArrangePosition
            >= grammarArrangeOrder.length
        ) {

            finishGrammarArrange();


            return;

        }


        renderGrammarArrangeQuestion();

    }



    function finishGrammarArrange() {

        grammarArrangeArea.hidden =
            true;


        grammarArrangeResult.hidden =
            false;


        grammarArrangeScore.textContent =
            grammarArrangeCorrect
            + " / "
            + grammarArrangeOrder.length;


        grammarArrangePercent.textContent =
            grammarPercent(
                grammarArrangeCorrect,
                grammarArrangeOrder.length
            )
            + "%";

    }



    if (
        grammarArrangeNextButton
    ) {

        grammarArrangeNextButton.addEventListener(
            "click",
            nextGrammarArrangeQuestion
        );

    }



    if (
        grammarArrangeRestartButton
    ) {

        grammarArrangeRestartButton.addEventListener(
            "click",
            function () {

                hideAllGrammarAreas();


                setActiveGrammarMode(
                    "arrange"
                );


                startGrammarArrange();

            }
        );

    }



    if (
        grammarArrangeBackButton
    ) {

        grammarArrangeBackButton.addEventListener(
            "click",
            function () {

                showGrammarStudyMode();

            }
        );

    }



    /* =========================================================
       43. CHUYỂN CHẾ ĐỘ NGỮ PHÁP
    ========================================================= */

    function showGrammarQuizMode() {

        hideAllGrammarAreas();


        setActiveGrammarMode(
            "quiz"
        );


        startGrammarQuiz();


        scrollToGrammarArea(
            grammarQuizArea
            &&
            !grammarQuizArea.hidden

                ? grammarQuizArea
                : grammarModeNotice
        );

    }



    function showGrammarFillMode() {

        hideAllGrammarAreas();


        setActiveGrammarMode(
            "fill"
        );


        startGrammarFill();


        scrollToGrammarArea(
            grammarFillArea
            &&
            !grammarFillArea.hidden

                ? grammarFillArea
                : grammarModeNotice
        );

    }



    function showGrammarArrangeMode() {

        hideAllGrammarAreas();


        setActiveGrammarMode(
            "arrange"
        );


        startGrammarArrange();


        scrollToGrammarArea(
            grammarArrangeArea
            &&
            !grammarArrangeArea.hidden

                ? grammarArrangeArea
                : grammarModeNotice
        );

    }



    grammarModeCards.forEach(
        function (
            card
        ) {

            card.addEventListener(
                "click",
                function () {

                    const mode =
                        card.dataset.grammarMode;


                    if (
                        mode
                        === "study"
                    ) {

                        showGrammarStudyMode();


                        return;

                    }


                    if (
                        mode
                        === "quiz"
                    ) {

                        showGrammarQuizMode();


                        return;

                    }


                    if (
                        mode
                        === "fill"
                    ) {

                        showGrammarFillMode();


                        return;

                    }


                    if (
                        mode
                        === "arrange"
                    ) {

                        showGrammarArrangeMode();

                    }

                }
            );

        }
    );



    /* =========================================================
       44. KHỞI TẠO NGỮ PHÁP
    ========================================================= */

    if (
        grammars.length
        > 0
    ) {

        grammarStudyOrder =
            grammars.map(
                function (
                    _,
                    index
                ) {

                    return index;

                }
            );


        grammarStudyPosition =
            0;


        showGrammarStudyMode(
            false
        );


        renderGrammarStudy();

    }
    else {

        console.warn(
            "Không có dữ liệu Ngữ pháp để hiển thị."
        );

    }



    /* =========================================================
       45. KHỞI TẠO TỪ VỰNG
    ========================================================= */

    showFlashcardMode(
        false
    );


    renderCard();

});