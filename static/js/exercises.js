
/* ============================================================
   MỘC HÁN - BÀI TẬP DÀNH CHO STUDENT
   File: static/js/exercises.js

   Chức năng:
   - Chọn và lọc bài tập
   - Bắt đầu bài tập từ API Flask
   - Trắc nghiệm một đáp án
   - Trắc nghiệm nhiều đáp án
   - Đúng / Sai
   - Điền từ
   - Sắp xếp câu
   - Chuyển câu, lưu đáp án trong phiên làm
   - Đếm thời gian
   - Nộp bài và chuyển đến trang kết quả
   - Xem lịch sử làm bài

   Backend:
   routes/student/exercises.py
============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const app = document.getElementById("mhExerciseApp");

    if (!app) return;

    // ========================================================
    // 1. CẤU HÌNH
    // ========================================================

    const $ = (id) => document.getElementById(id);

    const $$ = (selector, root = document) =>
        Array.from(root.querySelectorAll(selector));

    const API_BASE =
        app.dataset.exerciseApiBase ||
        "/student/exercises/api/exercises";

    const HISTORY_URL =
        app.dataset.historyUrl ||
        "/student/exercises/api/history";

    const CSRF_TOKEN =
        $("mhExCsrfToken")?.value ||
        document.querySelector(
            'meta[name="csrf-token"]'
        )?.content ||
        "";

    const state = {
        exercise: null,
        exerciseId: null,
        attemptToken: null,
        questions: [],
        answers: {},
        currentIndex: 0,
        startedAt: null,
        deadline: null,
        remainingSeconds: null,
        timerId: null,
        submitting: false,
        loading: false,
        expired: false,
        historyLoaded: false
    };

    const LABELS = {
    chon_mot: "Chọn một đáp án",
    chon_nhieu: "Chọn nhiều đáp án",
    dung_sai: "Đúng / Sai",
    dien_tu: "Điền từ",
    sap_xep: "Sắp xếp câu",
    ghep_cap: "Ghép cặp",
    viet_ngan: "Viết ngắn"
};

    // ========================================================
    // 2. HÀM HIỂN THỊ
    // ========================================================

    function show(id) {
        const element = $(id);
        if (element) element.hidden = false;
    }

    function hide(id) {
        const element = $(id);
        if (element) element.hidden = true;
    }

    function setText(id, value) {
        const element = $(id);

        if (element) {
            element.textContent = value ?? "";
        }
    }

    function setDisabled(id, disabled) {
        const element = $(id);

        if (element) {
            element.disabled = Boolean(disabled);
        }
    }

    function clearElement(element) {
        if (element) element.replaceChildren();
    }

    function createElement(tag, className, text) {
        const element = document.createElement(tag);

        if (className) {
            element.className = className;
        }

        if (text !== undefined && text !== null) {
            element.textContent = String(text);
        }

        return element;
    }

    function notice(message, type = "info") {
        const element = $("mhExNotice");

        if (!element) return;

        element.textContent = message;
        element.className = "mh-ex-notice";

        if (type === "error") {
            element.classList.add("error");
        }

        if (type === "success") {
            element.classList.add("success");
        }

        element.hidden = false;

        element.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });
    }

    function clearNotice() {
        const element = $("mhExNotice");

        if (element) {
            element.hidden = true;
            element.textContent = "";
        }
    }

    function showLoading(title, message) {
        setText(
            "mhExLoadingTitle",
            title || "Đang xử lý..."
        );

        setText(
            "mhExLoadingMessage",
            message || "Vui lòng chờ trong giây lát."
        );

        show("mhExLoadingScreen");
        hide("mhExOverview");
        hide("mhExQuizScreen");
    }

    function hideLoading() {
        hide("mhExLoadingScreen");
    }

    function scrollTop() {
        app.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }

    function formatNumber(value) {
        const n = Number(value);

        return Number.isFinite(n)
            ? n.toLocaleString("vi-VN")
            : "0";
    }

    // ========================================================
    // 3. GỌI API
    // ========================================================

    async function requestJson(url, options = {}) {
        const response = await fetch(url, {
            credentials: "same-origin",
            ...options,
            headers: {
                Accept: "application/json",
                ...(options.headers || {})
            }
        });

        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            if (response.status === 401) {
                throw new Error(
                    "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại."
                );
            }

            throw new Error(
                `Máy chủ không trả về JSON (HTTP ${response.status}).`
            );
        }

        const result = await response.json();

        if (!response.ok || result.success === false) {
            throw new Error(
                result.message ||
                `Yêu cầu thất bại (HTTP ${response.status}).`
            );
        }

        return result;
    }

    async function postJson(url, data) {
        if (!CSRF_TOKEN) {
            throw new Error(
                "Không tìm thấy CSRF token trong trang."
            );
        }

        return requestJson(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRF_TOKEN
            },
            body: JSON.stringify(data)
        });
    }

    // ========================================================
    // 4. THỐNG KÊ DANH SÁCH BÀI
    // ========================================================

    function updateOverviewStats() {
        const cards = $$(
            ".mh-ex-exercise-card",
            $("mhExExerciseGrid")
        );

        const totalQuestions = cards.reduce(
            (sum, card) => {
                const text = card.querySelector(
                    ".mh-ex-card-meta"
                )?.textContent || "";

                const match = text.match(/(\d+)\s*câu hỏi/);

                return sum + (
                    match ? Number(match[1]) : 0
                );
            },
            0
        );

        const completed = cards.filter(card =>
            card.querySelector(
                ".mh-ex-status-badge.done"
            )
        ).length;

        setText("mhExTotalCount", cards.length);
        setText("mhExCompletedCount", completed);
        setText("mhExQuestionCount", totalQuestions);
    }

    // ========================================================
    // 5. BỘ LỌC BÀI HỌC
    // ========================================================

    function populateLessonFilter() {
        const select = $("mhExLessonFilter");

        if (!select) return;

        const cards = $$(
            ".mh-ex-exercise-card",
            $("mhExExerciseGrid")
        );

        const lessons = new Map();

        cards.forEach(card => {
            const id = card.dataset.lessonId;
            const order = Number(
                card.dataset.lessonOrder || 0
            );

            const title =
                card.dataset.lessonTitle || "";

            if (!id || lessons.has(id)) return;

            lessons.set(id, {
                id,
                order,
                title
            });
        });

        const sorted = Array.from(
            lessons.values()
        ).sort((a, b) =>
            a.order - b.order
        );

        select.replaceChildren();

        const allOption = document.createElement("option");

        allOption.value = "";
        allOption.textContent = "Tất cả bài học";

        select.appendChild(allOption);

        sorted.forEach(lesson => {
            const option = document.createElement("option");

            option.value = lesson.id;
            option.textContent =
                `Bài ${lesson.order} · ${lesson.title}`;

            select.appendChild(option);
        });
    }

    function normalizeSearch(value) {
        return String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();
    }

    
    // ========================================================
    // 5. PHÂN TRANG DANH SÁCH BÀI TẬP
    // Mỗi trang hiển thị 4 bài tập.
    // Hỗ trợ lọc bài học và tìm kiếm.
    // ========================================================

    const PAGE_SIZE = 4;
    let currentPage = 1;

    // --------------------------------------------------------
    // TẠO THANH PHÂN TRANG
    // --------------------------------------------------------

    function renderPagination(totalPages) {
        const container = $("mhExPagination");

        if (!container) return;

        clearElement(container);

        // Có 0 hoặc 1 trang thì không cần phân trang.
        if (totalPages <= 1) {
            hide("mhExPagination");
            return;
        }

        show("mhExPagination");

        // Nút Trang trước
        const previousButton = createElement(
            "button",
            "mh-ex-page-btn",
            "← Trang trước"
        );

        previousButton.type = "button";
        previousButton.disabled = currentPage <= 1;

        previousButton.addEventListener("click", () => {
            if (currentPage <= 1) return;

            currentPage--;

            filterExercises(false, true);
        });

        // Thông tin trang hiện tại
        const pageInfo = createElement(
            "span",
            "mh-ex-pagination-info",
            `Trang ${currentPage} / ${totalPages}`
        );

        pageInfo.setAttribute(
            "aria-live",
            "polite"
        );

        // Nút Trang sau
        const nextButton = createElement(
            "button",
            "mh-ex-page-btn",
            "Trang sau →"
        );

        nextButton.type = "button";
        nextButton.disabled = currentPage >= totalPages;

        nextButton.addEventListener("click", () => {
            if (currentPage >= totalPages) return;

            currentPage++;

            filterExercises(false, true);
        });

        // Ghép ba thành phần
        container.append(
            previousButton,
            pageInfo,
            nextButton
        );
    }

    // --------------------------------------------------------
    // LỌC BÀI TẬP VÀ CHIA TRANG
    // --------------------------------------------------------

    function filterExercises(
        resetPage = false,
        scrollToList = false
    ) {
        const selectedLesson =
            $("mhExLessonFilter")?.value || "";

        const keyword = normalizeSearch(
            $("mhExSearchInput")?.value
        );

        const cards = $$(
            ".mh-ex-exercise-card",
            $("mhExExerciseGrid")
        );

        // Khi đổi bộ lọc hoặc tìm kiếm,
        // luôn quay về trang đầu tiên.
        if (resetPage) {
            currentPage = 1;
        }

        // Lấy toàn bộ bài tập phù hợp.
        const matchedCards = cards.filter(card => {
            const lessonId =
                card.dataset.lessonId || "";

            const title = normalizeSearch(
                card.dataset.exerciseTitle
            );

            const lessonTitle = normalizeSearch(
                card.dataset.lessonTitle
            );

            const matchesLesson =
                !selectedLesson ||
                lessonId === selectedLesson;

            const matchesKeyword =
                !keyword ||
                title.includes(keyword) ||
                lessonTitle.includes(keyword);

            return matchesLesson && matchesKeyword;
        });

        const total = matchedCards.length;

        // Tính số trang dựa trên số bài sau khi lọc.
        const totalPages = Math.ceil(
            total / PAGE_SIZE
        );

        // Không để trang hiện tại vượt quá số trang.
        if (totalPages === 0) {
            currentPage = 1;
        } else {
            currentPage = Math.min(
                Math.max(currentPage, 1),
                totalPages
            );
        }

        // Xác định 4 bài được hiển thị.
        const startIndex =
            (currentPage - 1) * PAGE_SIZE;

        const endIndex =
            startIndex + PAGE_SIZE;

        const pageCards = matchedCards.slice(
            startIndex,
            endIndex
        );

        const visibleCards = new Set(pageCards);

        // Ẩn tất cả bài không thuộc trang hiện tại.
        cards.forEach(card => {
            card.hidden = !visibleCards.has(card);
        });

        // Hiển thị tổng số bài tìm thấy.
        setText(
            "mhExVisibleCount",
            total
        );

        // Trạng thái không có bài tập.
        if (total === 0) {
            show("mhExEmptyState");
        } else {
            hide("mhExEmptyState");
        }

        // Cập nhật thanh phân trang.
        renderPagination(totalPages);

        // Khi chuyển trang, cuộn lên đầu danh sách.
        if (scrollToList) {
            const target = $("mhExExerciseGrid");

            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }
    }

    // --------------------------------------------------------
    // LỌC THEO BÀI HỌC
    // --------------------------------------------------------

    $("mhExLessonFilter")?.addEventListener(
        "change",
        () => {
            filterExercises(true);
        }
    );

    // --------------------------------------------------------
    // TÌM KIẾM BÀI TẬP
    // --------------------------------------------------------

    $("mhExSearchInput")?.addEventListener(
        "input",
        () => {
            filterExercises(true);
        }
    );


    // ========================================================
    // 6. BẮT ĐẦU BÀI TẬP
    // ========================================================

    async function startExercise(exerciseId) {
        if (state.loading || state.submitting) {
            return;
        }

        const id = Number(exerciseId);

        if (!Number.isInteger(id) || id <= 0) {
            notice("Mã bài tập không hợp lệ.", "error");
            return;
        }

        state.loading = true;

        clearNotice();

        showLoading(
            "Đang mở bài tập...",
            "Hệ thống đang lấy câu hỏi từ SQL Server."
        );

        try {
            const result = await postJson(
                `${API_BASE}/${id}/start`,
                {}
            );

            if (
                !Array.isArray(result.questions) ||
                result.questions.length === 0
            ) {
                throw new Error(
                    "Bài tập chưa có câu hỏi."
                );
            }

            stopTimer();

            state.exercise = result.exercise || {};
            state.exerciseId = id;
            state.attemptToken = result.attempt_token;
            state.questions = result.questions;
            state.answers = {};
            state.currentIndex = 0;
            state.startedAt = Date.now();
            state.expired = false;

            if (!state.attemptToken) {
                throw new Error(
                    "Máy chủ chưa cấp phiên làm bài."
                );
            }

            setupExerciseHeader();
            startTimer();

            hideLoading();
            hide("mhExOverview");
            show("mhExQuizScreen");

            renderQuestion();
            updateProgress();
            scrollTop();

        } catch (error) {
            console.error(
                "Lỗi mở bài tập:",
                error
            );

            hideLoading();
            show("mhExOverview");

            notice(error.message, "error");
        } finally {
            state.loading = false;
        }
    }

    $("mhExExerciseGrid")?.addEventListener(
        "click",
        event => {
            const button = event.target.closest(
                "[data-mh-start-exercise]"
            );

            if (!button || button.disabled) return;

            startExercise(
                button.dataset.mhStartExercise
            );
        }
    );

    // ========================================================
    // 7. HEADER BÀI TẬP
    // ========================================================

    function setupExerciseHeader() {
        const exercise = state.exercise || {};

        setText(
            "mhExQuizKicker",
            `HSK ${exercise.hsk ?? ""} · ${exercise.lesson ?? ""}`
        );

        setText(
            "mhExQuizTitle",
            exercise.title || "Bài tập HSK"
        );

        setText(
            "mhExQuizInstruction",
            exercise.instruction ||
            "Đọc kỹ câu hỏi và chọn đáp án phù hợp."
        );

        setText(
            "mhExTotalQuestions",
            state.questions.length
        );

        setText(
            "mhExSideTotal",
            state.questions.length
        );
    }

    // ========================================================
    // 8. TIẾN ĐỘ
    // ========================================================

    function currentQuestion() {
        return state.questions[
            state.currentIndex
        ] || null;
    }

    
    function hasAnswer(question) {
        if (!question) return false;

        const value = state.answers[String(question.id)];

        if (value === undefined || value === null) {
        return false;
        }

        // Ghép cặp: chỉ tính đã làm khi ghép đủ số cặp.
        if (question.type === "ghep_cap") {
            const leftItems = Array.isArray(question.left_items)
                ? question.left_items
                : [];

            return (
                leftItems.length > 0 &&
                Array.isArray(value) &&
                value.length === leftItems.length &&
                value.every(pair =>
                    pair &&
                    typeof pair.left === "string" &&
                    typeof pair.right === "string" &&
                    pair.left.trim() &&
                    pair.right.trim()
                )
            );
        
        }

        if (typeof value === "string") {
            return value.trim().length > 0;
        }

        if (Array.isArray(value)) {
            return value.length > 0;
     }

        return true;
    }


    function answeredCount() {
        return state.questions.filter(
            hasAnswer
        ).length;
    }

    function updateProgress() {
        const total = state.questions.length;
        const answered = answeredCount();
        const remaining = total - answered;

        const percentage = total
            ? Math.round(answered / total * 100)
            : 0;

        setText(
            "mhExCurrentQuestionNumber",
            total ? state.currentIndex + 1 : 0
        );

        setText(
            "mhExTotalQuestions",
            total
        );

        setText(
            "mhExAnsweredCount",
            answered
        );

        setText(
            "mhExSideAnswered",
            answered
        );

        setText(
            "mhExSideRemaining",
            remaining
        );

        const progress = $("mhExProgressFill");

        if (progress) {
            progress.style.width = `${percentage}%`;
        }

        const track = $("mhExProgressTrack");

        if (track) {
            track.setAttribute(
                "aria-valuenow",
                String(percentage)
            );
        }

        setDisabled(
            "mhExPreviousButton",
            state.currentIndex <= 0
        );

        const nextButton = $("mhExNextButton");

        if (nextButton) {
            nextButton.disabled =
                state.currentIndex >= total - 1;
        }

        renderQuestionNumbers();
    }

    // ========================================================
    // 9. DANH SÁCH SỐ CÂU
    // ========================================================

    function renderQuestionNumbers() {
        const container = $("mhExQuestionNumbers");

        if (!container) return;

        clearElement(container);

        state.questions.forEach((question, index) => {
            const button = createElement(
                "button",
                "mh-ex-question-number",
                index + 1
            );

            button.type = "button";

            if (index === state.currentIndex) {
                button.classList.add("current");
            } else if (hasAnswer(question)) {
                button.classList.add("answered");
            } else {
                button.classList.add("unanswered");
            }

            button.setAttribute(
                "aria-label",
                `Chuyển đến câu ${index + 1}`
            );

            button.addEventListener("click", () => {
                goToQuestion(index);
            });

            container.appendChild(button);
        });
    }

    // ========================================================
    // 10. HIỂN THỊ CÂU HỎI
    // ========================================================

    
    function hideAnswerAreas() {
        [
            "mhExChoiceArea",
            "mhExTrueFalseArea",
            "mhExFillArea",
            "mhExSortArea",
            "mhExMatchingArea",
            "mhExShortWritingArea",
            "mhExQuestionPassage",
            "mhExQuestionMedia"
        ].forEach(hide);
    }


    function renderQuestion() {
        const question = currentQuestion();

        if (!question) return;

        ensureExtraAnswerAreas();
        hideAnswerAreas();

        setText(
            "mhExQuestionType",
            LABELS[question.type] ||
            question.type_label ||
            "Câu hỏi"
        );

        setText(
            "mhExQuestionScore",
            `${formatNumber(question.max_score)} điểm`
        );

        setText(
            "mhExQuestionContent",
            question.content || ""
        );

        if (question.passage) {
            setText(
                "mhExQuestionPassage",
                question.passage
            );

            show("mhExQuestionPassage");
        }

        // API hiện mới cung cấp media_id.
        // Chưa có URL phát media nên không tự tạo
        // đường dẫn để tránh phát sai file.
        hide("mhExQuestionMedia");

        switch (question.type) {
            case "chon_mot":
                renderChoices(question, false);
                break;

            case "chon_nhieu":
                renderChoices(question, true);
                break;

            case "dung_sai":
                renderTrueFalse(question);
                break;

            case "dien_tu":
                renderFill(question);
                break;

            
            case "sap_xep":
                renderSorting(question);
                break;

            case "ghep_cap":
                renderMatching(question);
                break;

            case "viet_ngan":
                renderShortWriting(question);
                break;

            default:
                notice(
                    "Dạng câu hỏi này chưa được hỗ trợ.",
                    "error"
                );
        }

        updateProgress();
    }

    // ========================================================
    // 11. CHỌN MỘT / CHỌN NHIỀU
    // ========================================================

    function renderChoices(question, multiple) {
        show("mhExChoiceArea");

        setText(
            "mhExChoiceHint",
            multiple
                ? "Có thể chọn nhiều đáp án đúng."
                : "Chọn một đáp án đúng."
        );

        const container = $("mhExOptionList");

        if (!container) return;

        clearElement(container);

        const key = String(question.id);
        const stored = state.answers[key];

        const selected = multiple
            ? Array.isArray(stored) ? stored : []
            : stored;

        (question.choices || []).forEach(
            (choice, index) => {
                const label = createElement(
                    "label",
                    "mh-ex-option"
                );

                const input = document.createElement(
                    "input"
                );

                input.type = multiple
                    ? "checkbox"
                    : "radio";

                input.name = `mh-ex-choice-${question.id}`;
                input.value = String(choice.id);

                input.checked = multiple
                    ? selected.includes(Number(choice.id))
                    : Number(selected) === Number(choice.id);

                const letter = createElement(
                    "span",
                    "mh-ex-option-letter",
                    String.fromCharCode(65 + index)
                );

                const text = createElement(
                    "span",
                    "mh-ex-option-text",
                    choice.text || ""
                );

                label.append(
                    input,
                    letter,
                    text
                );

                if (input.checked) {
                    label.classList.add("selected");
                }

                input.addEventListener("change", () => {
                    if (multiple) {
                        const values = $$(
                            `input[name="mh-ex-choice-${question.id}"]:checked`,
                            container
                        ).map(item => Number(item.value));

                        state.answers[key] = values;
                    } else {
                        state.answers[key] = Number(
                            input.value
                        );
                    }

                    $$(
                        ".mh-ex-option",
                        container
                    ).forEach(option => {
                        const control =
                            option.querySelector("input");

                        option.classList.toggle(
                            "selected",
                            Boolean(control?.checked)
                        );
                    });

                    updateProgress();
                });

                container.appendChild(label);
            }
        );
    }

    // ========================================================
    // 12. ĐÚNG / SAI
    // ========================================================

    function renderTrueFalse(question) {
        show("mhExTrueFalseArea");

        const key = String(question.id);
        const stored = state.answers[key];

        const inputs = $$(
            'input[name="mhExTrueFalse"]',
            $("mhExTrueFalseArea")
        );

        inputs.forEach(input => {
            input.checked = input.value === stored;

            input.onchange = () => {
                state.answers[key] = input.value;

                updateTrueFalseStyles();
                updateProgress();
            };
        });

        updateTrueFalseStyles();
    }

    function updateTrueFalseStyles() {
        $$(
            ".mh-ex-true-false-option",
            $("mhExTrueFalseArea")
        ).forEach(label => {
            const input = label.querySelector("input");

            label.classList.toggle(
                "selected",
                Boolean(input?.checked)
            );
        });
    }

    // ========================================================
    // 13. ĐIỀN TỪ
    // ========================================================

    function renderFill(question) {
        show("mhExFillArea");

        const input = $("mhExFillInput");

        if (!input) return;

        const key = String(question.id);

        input.value =
            typeof state.answers[key] === "string"
                ? state.answers[key]
                : "";

        input.oninput = () => {
            state.answers[key] = input.value;

            updateProgress();
        };
    }

    // ========================================================
    // 14. SẮP XẾP CÂU
    //
    // Backend yêu cầu:
    // answer = [0, 1, 2, ...]
    //
    // Mỗi số là vị trí gốc của thành phần.
    // ========================================================

    function renderSorting(question) {
        show("mhExSortArea");

        const answerContainer = $("mhExSortAnswer");
        const itemsContainer = $("mhExSortItems");

        if (!answerContainer || !itemsContainer) {
            return;
        }

        const key = String(question.id);

        const items = Array.isArray(question.items)
            ? question.items
            : [];

        let selected = Array.isArray(state.answers[key])
            ? [...state.answers[key]]
            : [];

        selected = selected.filter(
            (value, index) =>
                Number.isInteger(value) &&
                value >= 0 &&
                value < items.length &&
                selected.indexOf(value) === index
        );

        function syncSorting() {
            state.answers[key] = [...selected];

            clearElement(answerContainer);
            clearElement(itemsContainer);

            if (selected.length === 0) {
                const placeholder = createElement(
                    "span",
                    "mh-ex-sort-placeholder",
                    "Chọn các từ bên dưới để ghép câu..."
                );

                answerContainer.appendChild(
                    placeholder
                );
            }

            selected.forEach((itemIndex, position) => {
                const button = createElement(
                    "button",
                    "mh-ex-sort-chip selected",
                    items[itemIndex]
                );

                button.type = "button";

                button.title = "Nhấn để bỏ từ này";

                button.addEventListener("click", () => {
                    selected.splice(position, 1);
                    syncSorting();
                });

                answerContainer.appendChild(button);
            });

            items.forEach((item, index) => {
                if (selected.includes(index)) return;

                const button = createElement(
                    "button",
                    "mh-ex-sort-chip",
                    item
                );

                button.type = "button";

                button.addEventListener("click", () => {
                    selected.push(index);
                    syncSorting();
                });

                itemsContainer.appendChild(button);
            });

            updateProgress();
        }

        const reset = $("mhExSortReset");

        if (reset) {
            reset.onclick = () => {
                selected = [];
                syncSorting();
            };
        }

        syncSorting();
    }
    
    // ========================================================
    // GIAO DIỆN CHO GHÉP CẶP VÀ VIẾT NGẮN
    // ========================================================

    function ensureExtraAnswerAreas() {
        const anchor = $("mhExSortArea") || $("mhExFillArea");

        if (!anchor || !anchor.parentElement) return;

        // Tạo khu vực Ghép cặp nếu chưa tồn tại.
        if (!$("mhExMatchingArea")) {
            const area = createElement(
                "div",
                "mh-ex-matching-area"
            );

            area.id = "mhExMatchingArea";
            area.hidden = true;

            anchor.insertAdjacentElement("afterend", area);
        }

        // Tạo khu vực Viết ngắn nếu chưa tồn tại.
        if (!$("mhExShortWritingArea")) {
            const area = createElement(
                "div",
                "mh-ex-writing-area"
            );

            area.id = "mhExShortWritingArea";
            area.hidden = true;

            $("mhExMatchingArea").insertAdjacentElement(
                "afterend",
                area
            );
        }
    }

    // ========================================================
    // GHÉP CẶP
    //
    // Backend gửi:
    // left_items: ["你好", "谢谢", ...]
    // right_items: ["Cảm ơn", "Xin chào", ...]
    //
    // Backend nhận:
    // [
    //     { left: "你好", right: "Xin chào" },
    //     { left: "谢谢", right: "Cảm ơn" }
    // ]
    // ========================================================

    function renderMatching(question) {
        const area = $("mhExMatchingArea");

        if (!area) {
            notice(
                "Không tìm thấy khu vực ghép cặp trên trang.",
                "error"
            );
            return;
        }

        clearElement(area);
        show("mhExMatchingArea");

        const leftItems = Array.isArray(question.left_items)
            ? question.left_items
            : [];

        const rightItems = Array.isArray(question.right_items)
            ? question.right_items
            : [];

        if (
            !leftItems.length ||
            !rightItems.length ||
            leftItems.length !== rightItems.length
        ) {
            area.appendChild(
                createElement(
                    "p",
                    "mh-ex-match-hint",
                    "Dữ liệu ghép cặp chưa đầy đủ."
                )
            );
            return;
        }

        const hint = createElement(
            "p",
            "mh-ex-match-hint",
            "Chọn nghĩa hoặc cách đọc tương ứng cho từng từ bên trái."
        );

        area.appendChild(hint);

        const key = String(question.id);

        // Khôi phục đáp án khi người học quay lại câu.
        const previous = Array.isArray(state.answers[key])
            ? state.answers[key]
            : [];

        const chosen = new Map(
            previous
                .filter(pair =>
                    pair &&
                    typeof pair.left === "string" &&
                    typeof pair.right === "string"
                )
                .map(pair => [
                    pair.left,
                    pair.right
                ])
        );

        const list = createElement(
            "div",
            "mh-ex-matching-list"
        );

        const selects = [];

        leftItems.forEach(left => {
            const row = createElement(
                "div",
                "mh-ex-matching-row"
            );

            const word = createElement(
                "span",
                "mh-ex-matching-word",
                left
            );

            const arrow = createElement(
                "span",
                "mh-ex-matching-arrow",
                "→"
            );

            arrow.setAttribute(
                "aria-hidden",
                "true"
            );

            const select = createElement(
                "select",
                "mh-ex-matching-select"
            );

            select.setAttribute(
                "aria-label",
                `Ghép đáp án cho ${left}`
            );

            const placeholder = createElement(
                "option",
                "",
                "— Chọn đáp án —"
            );

            placeholder.value = "";
            select.appendChild(placeholder);

            // Các đáp án phía bên phải đã được
            // Python trộn trước khi gửi về.
            rightItems.forEach(right => {
                const option = createElement(
                    "option",
                    "",
                    right
                );

                option.value = right;

                select.appendChild(option);
            });

            // Giữ lại lựa chọn cũ khi chuyển câu.
            select.value = chosen.get(left) || "";

            selects.push({
                left,
                select
            });

            select.addEventListener("change", () => {
                const answer = selects
                    .filter(item =>
                        item.select.value !== ""
                    )
                    .map(item => ({
                        left: item.left,
                        right: item.select.value
                    }));

                state.answers[key] = answer;

                updateProgress();
            });

            row.append(
                word,
                arrow,
                select
            );

            list.appendChild(row);
        });

        area.appendChild(list);
    }

    // ========================================================
    // VIẾT NGẮN
    //
    // Backend nhận một chuỗi văn bản.
    // Việc chấm điểm được thực hiện trong Python.
    // ========================================================

    function renderShortWriting(question) {
        const area = $("mhExShortWritingArea");

        if (!area) {
            notice(
                "Không tìm thấy khu vực viết ngắn trên trang.",
                "error"
            );
            return;
        }

        clearElement(area);
        show("mhExShortWritingArea");

        const hint = createElement(
            "p",
            "mh-ex-writing-hint",
            "Nhập câu trả lời. Hệ thống chấm tự động theo đáp án mẫu và các đáp án được chấp nhận."
        );

        const input = createElement(
            "textarea",
            "mh-ex-writing-input"
        );

        input.rows = 4;
        input.maxLength = 1500;

        input.placeholder =
            "Nhập câu trả lời của bạn ở đây...";

        input.setAttribute(
            "aria-label",
            "Câu trả lời viết ngắn"
        );

        const key = String(question.id);

        // Khôi phục nội dung khi quay lại câu.
        input.value =
            typeof state.answers[key] === "string"
                ? state.answers[key]
                : "";

        input.addEventListener("input", () => {
            state.answers[key] = input.value;

            updateProgress();
        });

        area.append(
            hint,
            input
        );
    }


    // ========================================================
    // 15. CHUYỂN CÂU
    // ========================================================

    function goToQuestion(index) {
        if (
            state.submitting ||
            state.expired ||
            index < 0 ||
            index >= state.questions.length
        ) {
            return;
        }

        state.currentIndex = index;

        renderQuestion();

        $("mhExQuestionContent")?.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });
    }

    $("mhExPreviousButton")?.addEventListener(
        "click",
        () => {
            goToQuestion(state.currentIndex - 1);
        }
    );

    $("mhExNextButton")?.addEventListener(
        "click",
        () => {
            goToQuestion(state.currentIndex + 1);
        }
    );

    // ========================================================
    // 16. ĐỒNG HỒ
    // ========================================================

    function stopTimer() {
        if (state.timerId !== null) {
            clearInterval(state.timerId);
            state.timerId = null;
        }
    }

    function formatTime(seconds) {
        const safe = Math.max(
            0,
            Math.floor(seconds)
        );

        const hours = Math.floor(safe / 3600);
        const minutes = Math.floor(
            (safe % 3600) / 60
        );
        const secs = safe % 60;

        const pad = value =>
            String(value).padStart(2, "0");

        if (hours > 0) {
            return (
                `${pad(hours)}:` +
                `${pad(minutes)}:` +
                `${pad(secs)}`
            );
        }

        return `${pad(minutes)}:${pad(secs)}`;
    }

    function startTimer() {
        stopTimer();

        const seconds = Number(
            state.exercise?.time_limit_seconds
        );

        if (
            !Number.isFinite(seconds) ||
            seconds <= 0
        ) {
            state.deadline = null;
            state.remainingSeconds = null;
            hide("mhExTimer");
            return;
        }

        state.deadline = Date.now() + seconds * 1000;
        state.remainingSeconds = seconds;

        show("mhExTimer");

        const tick = () => {
            if (state.submitting) return;

            const remaining = Math.max(
                0,
                Math.ceil(
                    (state.deadline - Date.now()) / 1000
                )
            );

            state.remainingSeconds = remaining;

            setText(
                "mhExTimerValue",
                formatTime(remaining)
            );

            $("mhExTimer")?.classList.toggle(
                "warning",
                remaining <= 60
            );

            if (remaining <= 0) {
                stopTimer();
                state.expired = true;

                // Không tự nộp khi hết giờ:
                // Backend hiện từ chối lượt quá hạn.
                // Giữ câu trả lời trong trang để
                // người học biết trạng thái.
                notice(
                    "Đã hết thời gian làm bài. " +
                    "Bạn cần quay lại và bắt đầu lượt mới.",
                    "error"
                );

                setDisabled(
                    "mhExSubmitButton",
                    true
                );

                show("mhExExitModal");
            }
        };

        tick();

        state.timerId = setInterval(
            tick,
            1000
        );
    }

    // ========================================================
    // 17. HỘP XÁC NHẬN NỘP BÀI
    // ========================================================

    function openSubmitModal() {
        if (
            state.submitting ||
            state.expired ||
            !state.attemptToken
        ) {
            return;
        }

        const total = state.questions.length;
        const answered = answeredCount();
        const remaining = total - answered;

        setText(
            "mhExSubmitModalMessage",
            remaining > 0
                ? `Bạn còn ${remaining} câu chưa trả lời. ` +
                  "Bạn vẫn muốn nộp bài?"
                : "Bạn đã trả lời tất cả câu hỏi. " +
                  "Xác nhận nộp bài?"
        );

        show("mhExSubmitModal");
    }

    function closeSubmitModal() {
        hide("mhExSubmitModal");
    }

    $("mhExSubmitButton")?.addEventListener(
        "click",
        openSubmitModal
    );

    $("mhExCancelSubmit")?.addEventListener(
        "click",
        closeSubmitModal
    );

    $("mhExConfirmSubmit")?.addEventListener(
        "click",
        submitExercise
    );

    // ========================================================
    // 18. NỘP BÀI
    // ========================================================

    async function submitExercise() {
        if (
            state.submitting ||
            state.expired ||
            !state.exerciseId ||
            !state.attemptToken
        ) {
            return;
        }

        closeSubmitModal();

        state.submitting = true;

        setDisabled("mhExSubmitButton", true);
        setDisabled("mhExConfirmSubmit", true);

        stopTimer();

        const answers = state.questions.map(
            question => ({
                question_id: Number(question.id),
                answer:
                    state.answers[String(question.id)] ??
                    null
            })
        );

        showLoading(
            "Đang chấm bài...",
            "Hệ thống đang kiểm tra đáp án và lưu kết quả."
        );

        try {
            const result = await postJson(
                `${API_BASE}/${state.exerciseId}/submit`,
                {
                    attempt_token: state.attemptToken,
                    answers
                }
            );

            if (!result.result_url) {
                throw new Error(
                    "Máy chủ chưa trả về đường dẫn kết quả."
                );
            }

            // Thành công: mở trang kết quả.
            window.location.assign(
                result.result_url
            );

        } catch (error) {
            console.error(
                "Lỗi nộp bài:",
                error
            );

            hideLoading();
            show("mhExQuizScreen");

            notice(
                "Không thể nộp bài: " + error.message,
                "error"
            );

            // Nếu server lỗi, cho phép thử lại.
            // Đồng hồ vẫn dựa trên deadline ban đầu.
            if (
                !state.expired &&
                state.deadline !== null &&
                Date.now() < state.deadline
            ) {
                state.timerId = setInterval(() => {
                    const remaining = Math.max(
                        0,
                        Math.ceil(
                            (state.deadline - Date.now()) /
                            1000
                        )
                    );

                    state.remainingSeconds = remaining;

                    setText(
                        "mhExTimerValue",
                        formatTime(remaining)
                    );

                    if (remaining <= 0) {
                        stopTimer();
                        state.expired = true;
                        setDisabled(
                            "mhExSubmitButton",
                            true
                        );
                    }
                }, 1000);
            }

        } finally {
            state.submitting = false;

            setDisabled(
                "mhExSubmitButton",
                state.expired
            );

            setDisabled(
                "mhExConfirmSubmit",
                false
            );
        }
    }

    // ========================================================
    // 19. THOÁT BÀI
    // ========================================================

    function openExitModal() {
        if (state.submitting) return;

        show("mhExExitModal");
    }

    function closeExitModal() {
        hide("mhExExitModal");
    }

    function exitExercise() {
        stopTimer();

        state.exercise = null;
        state.exerciseId = null;
        state.attemptToken = null;
        state.questions = [];
        state.answers = {};
        state.currentIndex = 0;
        state.startedAt = null;
        state.deadline = null;
        state.remainingSeconds = null;
        state.expired = false;

        hide("mhExExitModal");
        hide("mhExSubmitModal");
        hide("mhExQuizScreen");
        hideLoading();

        show("mhExOverview");

        setDisabled("mhExSubmitButton", false);

        clearNotice();
        scrollTop();
    }

    $("mhExBackButton")?.addEventListener(
        "click",
        openExitModal
    );

    $("mhExCancelExit")?.addEventListener(
        "click",
        closeExitModal
    );

    $("mhExConfirmExit")?.addEventListener(
        "click",
        exitExercise
    );

    // ========================================================
    // 20. LỊCH SỬ LÀM BÀI
    // ========================================================

    function formatDate(value) {
        if (!value) return "—";

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return String(value);
        }

        return date.toLocaleString("vi-VN", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
    }

    function renderHistory(history) {
        const container = $("mhExHistoryList");

        if (!container) return;

        clearElement(container);

        if (!Array.isArray(history) || history.length === 0) {
            show("mhExHistoryEmpty");
            return;
        }

        hide("mhExHistoryEmpty");

        history.forEach(item => {
            const card = createElement(
                "article",
                "mh-ex-history-item"
            );

            const info = createElement(
                "div",
                "mh-ex-history-info"
            );

            const title = createElement(
                "strong",
                "",
                item.TieuDe || "Bài tập"
            );

            const date = createElement(
                "span",
                "",
                formatDate(item.NgayNop)
            );

            info.append(title, date);

            const score = createElement(
                "strong",
                "mh-ex-history-score",
                `${formatNumber(item.Diem)} / ` +
                `${formatNumber(item.DiemToiDaLucLam)}`
            );

            const link = createElement(
                "a",
                "mh-ex-history-link",
                "Xem kết quả"
            );

            link.href =
                `/student/exercises/result/` +
                encodeURIComponent(item.MaLanLamBai);

            card.append(info, score, link);

            container.appendChild(card);
        });
    }

    async function loadHistory() {
        const container = $("mhExHistoryList");

        if (container) {
            container.textContent =
                "Đang tải lịch sử làm bài...";
        }

        show("mhExHistory");

        try {
            const result = await requestJson(
                HISTORY_URL
            );

            renderHistory(
                result.history || []
            );

            state.historyLoaded = true;

            $("mhExHistory")?.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            console.error(
                "Lỗi tải lịch sử:",
                error
            );

            if (container) {
                container.textContent =
                    "Không thể tải lịch sử: " +
                    error.message;
            }
        }
    }

    $("mhExHistoryButton")?.addEventListener(
        "click",
        loadHistory
    );

    $("mhExCloseHistory")?.addEventListener(
        "click",
        () => {
            hide("mhExHistory");
        }
    );

    // ========================================================
    // 21. PHÍM TẮT
    // ========================================================

    document.addEventListener("keydown", event => {
        const quiz = $("mhExQuizScreen");

        if (!quiz || quiz.hidden) return;

        if (
            event.target instanceof HTMLElement &&
            event.target.closest(
                "input, textarea, select, [contenteditable]"
            )
        ) {
            return;
        }

        if (event.key === "ArrowLeft") {
            event.preventDefault();

            goToQuestion(
                state.currentIndex - 1
            );
        }

        if (event.key === "ArrowRight") {
            event.preventDefault();

            goToQuestion(
                state.currentIndex + 1
            );
        }
    });

    // ========================================================
    // 22. KHỞI TẠO
    // ========================================================

    hide("mhExQuizScreen");
    hide("mhExLoadingScreen");
    hide("mhExSubmitModal");
    hide("mhExExitModal");
    hide("mhExHistory");

    show("mhExOverview");

   populateLessonFilter();
filterExercises();
updateOverviewStats();

// Tự động mở bài tập khi nhấn "Làm lại"
const params = new URLSearchParams(window.location.search);
const restartId = Number(params.get("start"));

if (Number.isInteger(restartId) && restartId > 0) {
    const matchingButton = Array.from(
        document.querySelectorAll("[data-mh-start-exercise]")
    ).find(button =>
        Number(button.dataset.mhStartExercise) === restartId &&
        !button.disabled
    );

    if (matchingButton) {
        params.delete("start");

        const query = params.toString();
        const cleanUrl =
            window.location.pathname +
            (query ? "?" + query : "") +
            window.location.hash;

        window.history.replaceState(null, "", cleanUrl);

        startExercise(restartId);
    } else {
        notice(
            "Bài tập không còn khả dụng để làm lại.",
            "error"
        );
    }
}

    console.log(
        "[Mộc Hán] Student Exercises JS đã khởi tạo."
    );
});
