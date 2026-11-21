
/* =========================================================
   MỘC HÁN - STUDENT LUYỆN THI HSK

   Cả đề / Nghe / Đọc / Viết

   - Đồng hồ do Flask + SQL Server quyết định.
   - Tải lại trang không đặt lại thời gian.
   - Lưu tạm đáp án vào SQL Server.
   - Hết giờ tự động nộp bài.
   - MP3 nguyên bài, không chia theo câu.
   - Nhóm hình A-F dùng chung chỉ hiện một lần.
   - HSK1/2 không có phần Viết.

   Dùng với:
   routes/student/luyen_thi_lam_bai.py
   templates/student/luyen_thi_lam_bai.html
========================================================= */

(() => {
    "use strict";

    // =====================================================
    // 1. CẤU HÌNH VÀ TRẠNG THÁI
    // =====================================================

    const root = document.body;

    const el = id => document.getElementById(id);

    const examId = Number(root.dataset.examId);
    const skill = root.dataset.skill;
    const startUrl = root.dataset.startUrl;
    const detailUrl = root.dataset.detailUrl;

    const csrf = document.querySelector(
        'meta[name="csrf-token"]'
    )?.content || "";

    const skillNames = {
        tat_ca: "Cả đề",
        nghe: "Nghe hiểu",
        doc: "Đọc hiểu",
        viet: "Viết"
    };

    const audio = el("lt-audio");

    let attemptId = null;
    let exam = null;
    let groups = [];
    let groupIndex = 0;
    let answers = {};
    let storageKey = "";

    // Đồng hồ từ SQL Server
    let serverRemaining = 0;
    let syncedAt = 0;
    let clockId = null;
    let timerTriggered = false;

    let submitting = false;
    let closed = false;
    let audioReady = false;

    // Hàng đợi lưu tạm, tránh ghi đè đáp án mới.
    let dirty = new Map();
    let saveTimer = null;
    let flushPromise = null;
    let saveFailed = false;


    // =====================================================
    // 2. CÁC HÀM HỖ TRỢ
    // =====================================================

    const safe = value =>
        String(value ?? "").replace(
            /[&<>"']/g,
            c => ({
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#39;"
            })[c]
        );

    function media(value) {

        if (
            typeof value !== "string" ||
            !/^\/static\/media\/luyen_thi\/[A-Za-z0-9_./-]+$/.test(value) ||
            value.split("/").includes("..")
        ) {
            return null;
        }

        return value;
    }

    function fmt(seconds) {

        const n = Math.max(
            0,
            Math.ceil(Number(seconds) || 0)
        );

        return (
            Math.floor(n / 60) +
            ":" +
            String(n % 60).padStart(2, "0")
        );
    }


    // =====================================================
    // 3. GỌI API FLASK
    // =====================================================

    async function api(
        url,
        method = "GET",
        data
    ) {

        const config = {
            method,
            credentials: "same-origin",
            headers: {
                Accept: "application/json"
            }
        };

        if (data !== undefined) {

            config.headers["Content-Type"] =
                "application/json";

            if (csrf) {
                config.headers["X-CSRFToken"] = csrf;
            }

            config.body = JSON.stringify(data);
        }

        const response = await fetch(url, config);

        const result = await response.json()
            .catch(() => ({}));

        if (!response.ok) {

            const error = new Error(
                result.loi ||
                `Máy chủ trả về HTTP ${response.status}`
            );

            error.resultUrl = result.ket_qua;

            throw error;
        }

        return result;
    }


    // =====================================================
    // 4. CHUYỂN SANG TRANG KẾT QUẢ
    // =====================================================

    function goResult(url) {

        closed = true;

        if (clockId !== null) {
            clearInterval(clockId);
        }

        if (audio) {
            audio.pause();
        }

        window.location.assign(url);
    }

    function onApiError(error) {

        if (error.resultUrl) {

            goResult(error.resultUrl);

            return true;
        }

        return false;
    }


    // =====================================================
    // 5. QUẢN LÝ CÂU TRẢ LỜI
    // =====================================================

    const keyOf = question =>
        String(question.MaCauHoiThi);

    const allQuestions = () =>
        groups.flatMap(group => group.questions);

    function hasAnswer(question) {

        if (!question) {
            return false;
        }

        const answer = answers[keyOf(question)];

        if (Array.isArray(answer)) {
            return answer.length > 0;
        }

        return (
            answer !== undefined &&
            answer !== null &&
            String(answer).trim() !== ""
        );
    }

    function localSave() {

        try {

            sessionStorage.setItem(
                storageKey,
                JSON.stringify(answers)
            );

        } catch (_) {
            // Một số chế độ trình duyệt hạn chế lưu phiên.
        }
    }

    function saveText(message) {

        const note = document.querySelector(
            ".lt-sidebar-note"
        );

        if (note) {
            note.textContent = message;
        }
    }


    // =====================================================
    // 6. ĐÁNH DẤU CÂU CẦN LƯU TẠM
    // =====================================================

    function markDirty(question) {

        const key = keyOf(question);

        dirty.set(
            key,
            answers[key] ?? null
        );

        localSave();

        saveText("Đang lưu câu trả lời…");

        if (saveTimer) {
            clearTimeout(saveTimer);
        }

        saveTimer = setTimeout(() => {

            void flushSaves().catch(() => {});

        }, 350);

        updateProgress();
    }


    // =====================================================
    // 7. LƯU ĐÁP ÁN TẠM VÀO SQL SERVER
    // =====================================================

    async function flushSaves() {

        if (saveTimer) {
            clearTimeout(saveTimer);
            saveTimer = null;
        }

        // Nếu đang lưu, dùng chung tiến trình đó.
        if (flushPromise) {
            return flushPromise;
        }

        if (
            closed ||
            !attemptId ||
            dirty.size === 0
        ) {
            return;
        }

        // Gửi từng câu tuần tự để câu cũ không
        // ghi đè câu vừa được người học thay đổi.
        flushPromise = (async () => {

            while (
                dirty.size > 0 &&
                !closed
            ) {

                const [key, value] =
                    dirty.entries().next().value;

                dirty.delete(key);

                try {

                    await api(
                        `/student/luyen-thi/api/lam-bai/${attemptId}/luu-tam`,
                        "POST",
                        {
                            ma_cau_hoi: Number(key),
                            cau_tra_loi: value
                        }
                    );

                    saveFailed = false;

                } catch (error) {

                    // Flask đã chốt bài vì hết giờ.
                    if (onApiError(error)) {
                        return;
                    }

                    // Không ghi đè nếu trong lúc lỗi
                    // người học đã thay đáp án mới hơn.
                    if (!dirty.has(key)) {
                        dirty.set(key, value);
                    }

                    saveFailed = true;

                    saveText(
                        "Chưa lưu được lên hệ thống. " +
                        "Đáp án vẫn còn trong tab này."
                    );

                    throw error;
                }
            }

            if (!closed) {

                saveText(
                    "Đáp án đã được lưu tạm trên hệ thống."
                );
            }

        })().finally(() => {

            flushPromise = null;

        });

        return flushPromise;
    }


    // =====================================================
    // 8. KHÔI PHỤC ĐÁP ÁN KHI TẢI LẠI TRANG
    // =====================================================

    function restoreAnswers(
        questions,
        serverDrafts
    ) {

        const ids = new Set(
            questions.map(keyOf)
        );

        answers = {};

        // Ưu tiên đọc những đáp án đã lưu trong SQL.
        if (
            serverDrafts &&
            typeof serverDrafts === "object" &&
            !Array.isArray(serverDrafts)
        ) {

            for (
                const [id, value]
                of Object.entries(serverDrafts)
            ) {

                if (ids.has(id)) {
                    answers[id] = value;
                }
            }
        }

        // Khôi phục cả những đáp án vừa gõ,
        // chưa kịp đồng bộ lên SQL trước khi tải lại.
        let local = {};

        try {

            local = JSON.parse(
                sessionStorage.getItem(storageKey) || "{}"
            );

        } catch (_) {

            local = {};
        }

        if (
            local &&
            typeof local === "object" &&
            !Array.isArray(local)
        ) {

            for (
                const [id, value]
                of Object.entries(local)
            ) {

                if (!ids.has(id)) {
                    continue;
                }

                if (
                    typeof value !== "string" &&
                    !Array.isArray(value) &&
                    value !== null
                ) {
                    continue;
                }

                if (
                    JSON.stringify(value) !==
                    JSON.stringify(answers[id])
                ) {

                    dirty.set(id, value);
                }

                answers[id] = value;
            }
        }

        localSave();
    }


    // =====================================================
    // 9. NHÓM CÂU THEO KỸ NĂNG VÀ PHẦN
    // =====================================================

    function partLabel(part) {

        const p = String(part ?? "").trim();

        if (!p) {
            return "Phần 1";
        }

        if (/^\d+$/.test(p)) {
            return `Phần ${p}`;
        }

        return p;
    }

    function makeGroups(questions) {

        const grouped = new Map();

        for (const question of questions) {

            const groupKey =
                `${question.KyNang}|${question.Phan ?? ""}`;

            if (!grouped.has(groupKey)) {

                grouped.set(groupKey, {
                    skill: question.KyNang,
                    part: question.Phan,
                    questions: []
                });
            }

            grouped.get(groupKey)
                .questions.push(question);
        }

        groups = [...grouped.values()];

        groups.forEach(group => {

            group.questions.sort(
                (a, b) =>
                    Number(a.SoCau) -
                    Number(b.SoCau)
            );
        });

        groups.sort(
            (a, b) =>
                Number(a.questions[0].SoCau) -
                Number(b.questions[0].SoCau)
        );
    }


    // =====================================================
    // 10. CẬP NHẬT TIẾN ĐỘ CÂU HỎI
    // =====================================================

    function updateProgress() {

        const questions = allQuestions();

        const count = questions.filter(
            hasAnswer
        ).length;

        el("lt-top-progress").textContent =
            `${count}/${questions.length} câu`;

        el("lt-side-count").textContent =
            `${count}/${questions.length} CÂU`;

        document.querySelectorAll(
            "[data-group-index]"
        ).forEach(button => {

            const n = Number(
                button.dataset.groupIndex
            );

            const group = groups[n];

            if (!group) {
                return;
            }

            const number = group.questions.filter(
                hasAnswer
            ).length;

            const first =
                group.questions[0].SoCau;

            const last =
                group.questions.at(-1).SoCau;

            button.querySelector("small").textContent =
                `Câu ${first}–${last} · ` +
                `${number}/${group.questions.length}`;

            button.classList.toggle(
                "is-current",
                n === groupIndex
            );
        });

        const ids = new Set(
            groups[groupIndex].questions.map(keyOf)
        );

        const questionMap = new Map(
            questions.map(
                q => [keyOf(q), q]
            )
        );

        document.querySelectorAll(
            "[data-question-id]"
        ).forEach(button => {

            const key = button.dataset.questionId;

            button.classList.toggle(
                "is-current",
                ids.has(key)
            );

            button.classList.toggle(
                "is-done",
                hasAnswer(questionMap.get(key))
            );
        });
    }


    // =====================================================
    // 11. SIDEBAR PHẦN THI VÀ SỐ CÂU
    // =====================================================

    function buildSidebar() {

        const parts = el("lt-groups");
        const indices = el("lt-question-index");

        parts.replaceChildren();
        indices.replaceChildren();

        groups.forEach((group, index) => {

            const button = document.createElement(
                "button"
            );

            button.type = "button";

            button.dataset.groupIndex = String(index);

            button.innerHTML = `
                <strong>
                    ${safe(
                        skillNames[group.skill] ||
                        group.skill
                    )}
                    · ${safe(partLabel(group.part))}
                </strong>
                <small></small>
            `;

            button.addEventListener(
                "click",
                () => showGroup(index)
            );

            parts.append(button);
        });

        allQuestions().forEach(question => {

            const button = document.createElement(
                "button"
            );

            button.type = "button";

            button.dataset.questionId = keyOf(question);

            button.textContent =
                String(question.SoCau);

            button.addEventListener(
                "click",
                () => {

                    const index = groups.findIndex(
                        group =>
                            group.questions.includes(question)
                    );

                    showGroup(index, false);

                    el(
                        `lt-q-${question.MaCauHoiThi}`
                    )?.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });
                }
            );

            indices.append(button);
        });
    }


    // =====================================================
    // 12. HIỂN THỊ HÌNH ẢNH GỐC
    // =====================================================

    function picture(path, alt) {

        const src = media(path);

        return src
            ? `
                <img
                    class="lt-question-img"
                    src="${safe(src)}"
                    alt="${safe(alt)}"
                    loading="lazy"
                >
            `
            : "";
    }

    function optionsOf(question) {

        return Array.isArray(question.lua_chon)
            ? question.lua_chon
            : [];
    }


    // =====================================================
    // 13. HIỂN THỊ CÁC DẠNG CÂU TRẢ LỜI
    // =====================================================

    function answerMarkup(question) {

        const key = keyOf(question);

        const selected = answers[key];

        const type = String(
            question.LoaiCauHoi || ""
        );

        const options = optionsOf(question);


        // ---------------------------------------------
        // DẠNG SẮP XẾP TỪ - HSK3/4
        // ---------------------------------------------

        if (
            ["sap_xep", "sap_xep_abc"].includes(type) &&
            options.length > 0
        ) {

            const chosen = Array.isArray(selected)
                ? selected
                : [];

            const selectedHtml = chosen.length

                ? chosen.map(
                    (word, i) => `
                        <button
                            type="button"
                            data-undo="${i}"
                        >
                            ${safe(word)} ×
                        </button>
                    `
                ).join("")

                : `
                    <span>
                        Bấm từ theo đúng thứ tự
                        để tạo câu
                    </span>
                `;

            const tokens = options.map(
                (option, i) => {

                    const token = String(
                        option.nhan ??
                        option.ma ??
                        ""
                    );

                    // Xử lý trường hợp có từ giống nhau.
                    const preceding = options
                        .slice(0, i + 1)
                        .filter(
                            x =>
                                String(
                                    x.nhan ??
                                    x.ma ??
                                    ""
                                ) === token
                        ).length;

                    const used = chosen.filter(
                        x => x === token
                    ).length;

                    return `
                        <button
                            type="button"
                            data-token="${i}"
                            ${used >= preceding ? "disabled" : ""}
                        >
                            ${safe(token)}
                        </button>
                    `;
                }
            ).join("");

            return `
                <div class="lt-order-answer">
                    ${selectedHtml}
                </div>

                <div class="lt-order-tokens">
                    ${tokens}
                </div>
            `;
        }


        // ---------------------------------------------
        // DẠNG VIẾT NGẮN HOẶC ĐIỀN TỪ
        // ---------------------------------------------

        if (
            ["viet_ngan", "dien_tu"].includes(type) ||
            options.length === 0
        ) {

            const value = typeof selected === "string"
                ? selected
                : "";

            return `
                <textarea
                    class="lt-answer-input"
                    data-free-text="1"
                    rows="2"
                    maxlength="3000"
                    placeholder="Nhập câu trả lời…"
                >${safe(value)}</textarea>
            `;
        }


        // ---------------------------------------------
        // TRẮC NGHIỆM / ĐÚNG SAI / GHÉP HÌNH
        // ---------------------------------------------

        const multiple = type === "chon_nhieu";

        const values = Array.isArray(selected)
            ? selected
            : [selected];

        const buttons = options.map(option => {

            const code = String(
                option.ma ?? ""
            );

            const label = (
                type === "dung_sai" &&
                ["√", "×"].includes(code)
            )
                ? code
                : String(option.nhan ?? code);

            const active = values.includes(code);

            return `
                <button
                    type="button"
                    data-option="${safe(code)}"
                    title="${safe(option.nhan ?? label)}"
                    class="${active ? "is-selected" : ""}"
                    aria-pressed="${active}"
                >
                    ${safe(label)}
                </button>
            `;
        }).join("");

        return `
            <div class="lt-answer-options">
                ${buttons}
            </div>

            ${multiple
                ? "<small>Được chọn nhiều đáp án.</small>"
                : ""}
        `;
    }


    // =====================================================
    // 14. HIỂN THỊ THẺ CÂU HỎI
    // =====================================================

    function questionMarkup(
        question,
        sharedPicture
    ) {

        const content = question.NoiDung
            ? `
                <div class="lt-question-text">
                    ${safe(question.NoiDung)}
                </div>
            `
            : "";

        const questionImage = picture(
            question.AnhCauHoi,
            `Hình câu ${question.SoCau}`
        );

        const groupImage = sharedPicture
            ? ""
            : picture(
                question.AnhNhomLuaChon,
                `Nhóm lựa chọn câu ${question.SoCau}`
            );

        return `
            <article
                class="lt-question-card"
                id="lt-q-${question.MaCauHoiThi}"
                data-qid="${question.MaCauHoiThi}"
            >
                <span class="lt-question-number">
                    ${safe(question.SoCau)}
                </span>

                <div class="lt-question-content">
                    ${content}
                    ${questionImage}
                    ${groupImage}
                    ${answerMarkup(question)}
                </div>
            </article>
        `;
    }


    // =====================================================
    // 15. SỰ KIỆN TRẢ LỜI CÂU HỎI
    // =====================================================

    function bindAnswers() {

        el("lt-question-area")
            .querySelectorAll("[data-qid]")
            .forEach(card => {

                const question = groups[groupIndex]
                    .questions.find(
                        q =>
                            keyOf(q) === card.dataset.qid
                    );

                if (!question) {
                    return;
                }

                const key = keyOf(question);


                // -------------------------------------
                // CHỌN ĐÁP ÁN
                // -------------------------------------

                card.querySelectorAll(
                    "[data-option]"
                ).forEach(button => {

                    button.addEventListener(
                        "click",
                        () => {

                            const value =
                                button.dataset.option;

                            if (
                                question.LoaiCauHoi ===
                                "chon_nhieu"
                            ) {

                                const chosen =
                                    Array.isArray(answers[key])
                                    ? [...answers[key]]
                                    : [];

                                answers[key] =
                                    chosen.includes(value)
                                    ? chosen.filter(
                                        x => x !== value
                                    )
                                    : [...chosen, value];

                            } else {

                                answers[key] = value;
                            }

                            card.querySelectorAll(
                                "[data-option]"
                            ).forEach(item => {

                                const on =
                                    Array.isArray(answers[key])
                                    ? answers[key].includes(
                                        item.dataset.option
                                    )
                                    : answers[key] ===
                                        item.dataset.option;

                                item.classList.toggle(
                                    "is-selected",
                                    on
                                );

                                item.setAttribute(
                                    "aria-pressed",
                                    String(on)
                                );
                            });

                            markDirty(question);
                        }
                    );
                });


                // -------------------------------------
                // GÕ CÂU TRẢ LỜI
                // -------------------------------------

                const input = card.querySelector(
                    "[data-free-text]"
                );

                if (input) {

                    input.addEventListener(
                        "input",
                        () => {

                            answers[key] = input.value;

                            markDirty(question);
                        }
                    );
                }


                // -------------------------------------
                // CHỌN TỪ ĐỂ SẮP XẾP
                // -------------------------------------

                card.querySelectorAll(
                    "[data-token]"
                ).forEach(button => {

                    button.addEventListener(
                        "click",
                        () => {

                            const option = optionsOf(
                                question
                            )[
                                Number(button.dataset.token)
                            ];

                            if (!option) {
                                return;
                            }

                            const chosen =
                                Array.isArray(answers[key])
                                ? [...answers[key]]
                                : [];

                            chosen.push(
                                String(
                                    option.nhan ??
                                    option.ma ??
                                    ""
                                )
                            );

                            answers[key] = chosen;

                            markDirty(question);

                            showGroup(groupIndex, false);
                        }
                    );
                });


                // -------------------------------------
                // BỎ MỘT TỪ ĐÃ CHỌN
                // -------------------------------------

                card.querySelectorAll(
                    "[data-undo]"
                ).forEach(button => {

                    button.addEventListener(
                        "click",
                        () => {

                            const chosen =
                                Array.isArray(answers[key])
                                ? [...answers[key]]
                                : [];

                            chosen.splice(
                                Number(button.dataset.undo),
                                1
                            );

                            answers[key] = chosen;

                            markDirty(question);

                            showGroup(groupIndex, false);
                        }
                    );
                });
            });
    }


    // =====================================================
    // 16. HIỂN THỊ NHÓM CÂU THEO PHẦN THI
    // =====================================================

    function showGroup(
        index,
        scroll = true
    ) {

        if (
            index < 0 ||
            index >= groups.length ||
            closed
        ) {
            return;
        }

        groupIndex = index;

        const group = groups[index];

        const first = group.questions[0];

        const last = group.questions.at(-1);

        el("lt-skill-title").textContent =
            (
                group.skill === "nghe"
                ? "🎧 "
                : group.skill === "doc"
                    ? "▤ "
                    : "✎ "
            ) +
            (
                skillNames[group.skill] ||
                group.skill
            );

        el("lt-part-title").textContent =
            `${partLabel(group.part)} · ` +
            `Câu ${first.SoCau}–${last.SoCau}`;

        el("lt-group-meta").textContent =
            `${group.questions.length} câu`;

        el("lt-instruction").textContent =
            group.skill === "nghe"
                ? "Nghe MP3 gốc và chọn đáp án cho mỗi câu."
                : group.skill === "doc"
                    ? "Quan sát hình hoặc đọc nội dung và chọn đáp án."
                    : "Chọn từ theo thứ tự hoặc nhập câu trả lời.";


        // Một nhóm câu dùng chung hình A-F.
        const sharedPath = first.AnhNhomLuaChon;

        const shared = (
            sharedPath &&
            group.questions.every(
                q =>
                    q.AnhNhomLuaChon === sharedPath
            )
        )
            ? sharedPath
            : null;

        el("lt-group-picture").hidden =
            !shared;

        el("lt-group-picture").innerHTML =
            shared
            ? `
                <div class="lt-group-picture-label">
                    NHÓM HÌNH LỰA CHỌN
                </div>
                ${picture(
                    shared,
                    "Nhóm hình A–F dùng chung"
                )}
            `
            : "";

        // Moi bang chung chi hien thi mot lan.
        const seenSharedPaths = new Set();

        el("lt-question-area").innerHTML =
            group.questions.map(q => {

                const path = q.AnhNhomLuaChon;

                const skipGroupImage = Boolean(shared) ||
                    Boolean(
                        path &&
                        seenSharedPaths.has(path)
                    );

                if (path) {
                    seenSharedPaths.add(path);
                }

                return questionMarkup(
                    q,
                    skipGroupImage
                );

            }).join("");

        bindAnswers();


        // ---------------------------------------------
        // MP3 GIỮ NGUYÊN KHI CHUYỂN NHÓM
        // ---------------------------------------------

        const audioVisible =
            group.skill === "nghe" &&
            audioReady;

        el("lt-audio-panel").hidden =
            !audioVisible;

        if (
            !audioVisible &&
            audio &&
            !audio.paused
        ) {
            audio.pause();
        }


        // ---------------------------------------------
        // NÚT CHUYỂN PHẦN
        // ---------------------------------------------

        el("lt-prev").disabled =
            index === 0;

        el("lt-next").textContent =
            index === groups.length - 1
            ? "Nộp bài →"
            : "Phần tiếp ›";

        el("lt-pager").textContent =
            `Phần ${index + 1}/${groups.length}`;

        updateProgress();

        if (scroll) {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        }
    }


    // =====================================================
    // 17. MP3 TOÀN BÀI
    // =====================================================

    function setupAudio() {

        if (
            !audio ||
            !groups.some(
                group =>
                    group.skill === "nghe"
            )
        ) {
            return;
        }

        const src = media(exam.AudioUrl);

        if (!src) {
            return;
        }

        audio.src = src;

        audio.playbackRate = 1;

        audioReady = true;

        const sync = () => {

            el("lt-audio-now").textContent =
                fmt(audio.currentTime);

            el("lt-audio-total").textContent =
                Number.isFinite(audio.duration)
                ? fmt(audio.duration)
                : "0:00";

            el("lt-audio-seek").value =
                Number.isFinite(audio.duration) &&
                audio.duration > 0
                ? String(
                    Math.round(
                        audio.currentTime /
                        audio.duration * 100
                    )
                )
                : "0";
        };

        for (
            const ev of [
                "loadedmetadata",
                "durationchange",
                "timeupdate"
            ]
        ) {

            audio.addEventListener(ev, sync);
        }

        audio.addEventListener(
            "play",
            () => {

                el("lt-play").textContent =
                    "❚❚";
            }
        );

        audio.addEventListener(
            "pause",
            () => {

                el("lt-play").textContent =
                    "▶";
            }
        );

        audio.addEventListener(
            "ended",
            () => {

                el("lt-play").textContent =
                    "▶";
            }
        );

        audio.addEventListener(
            "error",
            () => {

                audioReady = false;

                el("lt-play").disabled = true;

                el("lt-audio-total").textContent =
                    "Lỗi MP3";
            }
        );


        // PHÁT / TẠM DỪNG
        el("lt-play").addEventListener(
            "click",
            () => {

                if (audio.paused) {

                    audio.play().catch(
                        () => alert(
                            "Không phát được MP3."
                        )
                    );

                } else {

                    audio.pause();
                }
            }
        );


        // LÙI 5 GIÂY
        el("lt-rewind").addEventListener(
            "click",
            () => {

                audio.currentTime = Math.max(
                    0,
                    audio.currentTime - 5
                );
            }
        );


        // TUA ÂM THANH
        el("lt-audio-seek").addEventListener(
            "input",
            event => {

                if (
                    Number.isFinite(audio.duration) &&
                    audio.duration > 0
                ) {

                    audio.currentTime =
                        audio.duration *
                        Number(event.target.value) / 100;
                }
            }
        );


        // TỐC ĐỘ PHÁT
        document.querySelectorAll(
            "[data-speed]"
        ).forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    audio.playbackRate = Number(
                        button.dataset.speed
                    );

                    document.querySelectorAll(
                        "[data-speed]"
                    ).forEach(item => {

                        item.classList.toggle(
                            "is-active",
                            item === button
                        );
                    });
                }
            );
        });
    }


    // =====================================================
    // 18. ĐỒNG BỘ THỜI GIAN TỪ SQL SERVER
    // =====================================================

    function syncTime(data) {

        if (
            !Number.isFinite(
                Number(data.con_lai_giay)
            )
        ) {
            return;
        }

        serverRemaining = Math.max(
            0,
            Number(data.con_lai_giay)
        );

        // Mốc thời gian của trình duyệt để
        // tính số giây chạy tiếp sau lần đồng bộ.
        syncedAt = performance.now();

        renderClock();
    }

    function secondsLeft() {

        return Math.max(
            0,
            serverRemaining -
            (
                performance.now() -
                syncedAt
            ) / 1000
        );
    }

    function renderClock() {

        if (closed) {
            return;
        }

        const remaining = secondsLeft();

        el("lt-clock").textContent =
            "⌛ " + fmt(remaining);

        if (
            remaining <= 0 &&
            !timerTriggered &&
            !submitting
        ) {

            timerTriggered = true;

            void submitExam(true);
        }
    }

    function startClock() {

        if (clockId !== null) {
            clearInterval(clockId);
        }

        renderClock();

        clockId = setInterval(
            renderClock,
            250
        );
    }


    // =====================================================
    // 19. ĐỒNG BỘ LẠI KHI QUAY VỀ TAB
    // =====================================================

    async function syncOnReturn() {

        if (
            !attemptId ||
            closed ||
            submitting
        ) {
            return;
        }

        try {

            const data = await api(
                `/student/luyen-thi/api/lam-bai/${attemptId}/du-lieu`
            );

            syncTime(data);

        } catch (error) {

            onApiError(error);
        }
    }


    // =====================================================
    // 20. NỘP BÀI / TỰ NỘP KHI HẾT GIỜ
    // =====================================================

    async function submitExam(
        automatic = false
    ) {

        if (
            submitting ||
            closed ||
            !attemptId
        ) {
            return;
        }

        const questions = allQuestions();

        const done = questions.filter(
            hasAnswer
        ).length;

        if (
            !automatic &&
            !confirm(
                `Bạn đã trả lời ${done}/${questions.length} câu. ` +
                "Nộp bài ngay?"
            )
        ) {
            return;
        }

        submitting = true;

        el("lt-submit").disabled = true;

        el("lt-submit").textContent =
            automatic
            ? "Hết giờ · đang nộp…"
            : "Đang nộp…";

        if (
            audio &&
            !audio.paused
        ) {
            audio.pause();
        }

        if (saveTimer) {

            clearTimeout(saveTimer);
            saveTimer = null;
        }

        try {

            // Cố gắng lưu các đáp án cuối cùng
            // trước khi chấm điểm.
            try {

                await flushSaves();

            } catch (_) {

                // Lần nộp chính thức vẫn gửi
                // toàn bộ đáp án trong một request.
            }

            if (closed) {
                return;
            }

            const result = await api(
                `/student/luyen-thi/api/lam-bai/${attemptId}/nop-bai`,
                "POST",
                {
                    cau_tra_loi: answers
                }
            );

            try {

                sessionStorage.removeItem(
                    storageKey
                );

            } catch (_) {}

            goResult(result.ket_qua);

        } catch (error) {

            if (onApiError(error)) {
                return;
            }

            submitting = false;

            el("lt-submit").disabled = false;

            el("lt-submit").textContent =
                "⚑ Thử nộp lại";

            saveText(
                "Chưa nộp được bài. " +
                "Kiểm tra kết nối và nhấn Thử nộp lại."
            );

            alert(
                "Chưa nộp được bài: " +
                error.message
            );
        }
    }


    // =====================================================
    // 21. KHỞI TẠO TRANG LÀM BÀI
    // =====================================================

    async function init() {

        try {

            if (
                !Number.isSafeInteger(examId) ||
                examId <= 0 ||
                !skillNames[skill] ||
                !startUrl
            ) {

                throw new Error(
                    "Mã đề hoặc kỹ năng không hợp lệ."
                );
            }


            // ---------------------------------------------
            // BẮT ĐẦU HOẶC TIẾP TỤC LẦN THI
            // ---------------------------------------------

            const started = await api(
                startUrl,
                "POST",
                {
                    ma_de: examId,
                    ky_nang: skill
                }
            );

            // Lần thi trước đã hết giờ, Flask đã chấm.
            if (
                started.het_gio &&
                started.ket_qua
            ) {

                goResult(started.ket_qua);

                return;
            }

            attemptId = Number(
                started.ma_lan_thi
            );

            if (
                !Number.isSafeInteger(attemptId) ||
                attemptId <= 0
            ) {

                throw new Error(
                    "Không nhận được mã lần thi."
                );
            }

            storageKey =
                "moc-han-hsk-attempt-" +
                attemptId;


            // ---------------------------------------------
            // LẤY CÂU HỎI VÀ THỜI GIAN TỪ SQL
            // ---------------------------------------------

            const data = await api(
                `/student/luyen-thi/api/lam-bai/${attemptId}/du-lieu`
            );

            exam = data.de_thi;

            if (
                !Array.isArray(data.cau_hoi) ||
                data.cau_hoi.length === 0
            ) {

                throw new Error(
                    "Đề thi chưa có câu hỏi."
                );
            }


            // ---------------------------------------------
            // KHÔI PHỤC ĐÁP ÁN
            // ---------------------------------------------

            restoreAnswers(
                data.cau_hoi,
                data.dap_an_da_luu
            );

            makeGroups(data.cau_hoi);

            el("lt-mode-name").textContent =
                skillNames[skill];

            buildSidebar();

            setupAudio();


            // ---------------------------------------------
            // HIỂN THỊ GIAO DIỆN
            // ---------------------------------------------

            el("lt-loading").hidden = true;

            el("lt-exam-body").hidden = false;

            el("lt-submit").disabled = false;


            // ---------------------------------------------
            // CÁC NÚT CHUYỂN PHẦN
            // ---------------------------------------------

            el("lt-prev").addEventListener(
                "click",
                () => showGroup(groupIndex - 1)
            );

            el("lt-next").addEventListener(
                "click",
                () => {

                    if (
                        groupIndex === groups.length - 1
                    ) {

                        void submitExam();

                    } else {

                        showGroup(groupIndex + 1);
                    }
                }
            );


            // ---------------------------------------------
            // NÚT NỘP BÀI
            // ---------------------------------------------

            el("lt-submit").addEventListener(
                "click",
                () => {

                    void submitExam();
                }
            );


            // ---------------------------------------------
            // NÚT THOÁT
            // ---------------------------------------------

            el("lt-exit").addEventListener(
                "click",
                async event => {

                    if (
                        !confirm(
                            "Thoát bài thi? Thời gian vẫn " +
                            "tiếp tục chạy khi bạn rời trang."
                        )
                    ) {

                        event.preventDefault();

                        return;
                    }

                    event.preventDefault();

                    try {

                        await flushSaves();

                    } catch (_) {}

                    if (!closed) {

                        window.location.assign(
                            detailUrl
                        );
                    }
                }
            );


            // ---------------------------------------------
            // KHI TRỞ LẠI TAB, ĐỒNG BỘ GIỜ VỚI SQL
            // ---------------------------------------------

            document.addEventListener(
                "visibilitychange",
                () => {

                    if (!document.hidden) {

                        void syncOnReturn();
                    }
                }
            );


            // ---------------------------------------------
            // HIỂN THỊ NHÓM ĐẦU TIÊN VÀ BẬT ĐỒNG HỒ
            // ---------------------------------------------

            showGroup(0, false);

            syncTime(data);

            startClock();


            // Đồng bộ nốt đáp án khôi phục từ
            // sessionStorage nhưng chưa có trong SQL.
            if (dirty.size) {

                void flushSaves().catch(() => {});
            }

            if (!saveFailed) {

                saveText(
                    "Đáp án được lưu tạm vào SQL Server " +
                    "khi bạn trả lời."
                );
            }

        } catch (error) {

            if (onApiError(error)) {
                return;
            }

            el("lt-loading").hidden = false;

            el("lt-loading").textContent =
                "Không mở được đề thi: " +
                error.message;
        }
    }

    void init();

})();
