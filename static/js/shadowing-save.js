
"use strict";

// ======================================================
// MOC HAN - LUU KET QUA SHADOWING
//
// Khong thay doi logic cua shadowing-study.js.
// Su dung ket qua da duoc kiem tra tai giao dien.
// Flask se tu cham lai truoc khi luu SQL Server.
// ======================================================

(function () {

    function initShadowingSave() {

        const config = document.getElementById(
            "shadowing-config"
        );

        if (!config) return;

        const contentId = Number(
            config.dataset.contentId
        );

        const saveUrl = config.dataset.saveUrl;
        const summaryUrl = config.dataset.summaryUrl;
        const csrfToken = config.dataset.csrfToken;

        if (
            !Number.isInteger(contentId) ||
            contentId <= 0 ||
            !saveUrl ||
            !summaryUrl
        ) {
            console.error(
                "Shadowing: thiếu cấu hình lưu kết quả."
            );
            return;
        }

        // ==================================================
        // 1. HIEN THI THONG BAO LUU
        // ==================================================

        function getStatusElement(mode) {

            const id = mode === "dictation"
                ? "dictationSaveStatus"
                : "assembleSaveStatus";

            let element = document.getElementById(id);

            if (element) return element;

            const resultId = mode === "dictation"
                ? "dictationResult"
                : "assembleResult";

            const result = document.getElementById(
                resultId
            );

            if (!result) return null;

            element = document.createElement("div");

            element.id = id;

            element.setAttribute("role", "status");

            element.style.cssText = [
                "margin-top:10px",
                "padding:9px 12px",
                "border-radius:8px",
                "font-size:13px",
                "line-height:1.6",
                "background:#f1f5ee",
                "color:#435744"
            ].join(";");

            element.hidden = true;

            result.insertAdjacentElement(
                "afterend",
                element
            );

            return element;
        }

        function showStatus(mode, message, isError) {

            const element = getStatusElement(mode);

            if (!element) return;

            element.hidden = false;
            element.textContent = message;

            element.style.background = isError
                ? "#fff0ee"
                : "#f1f5ee";

            element.style.color = isError
                ? "#a43e34"
                : "#435744";
        }

        // ==================================================
        // 2. DINH DANG TIEN DO
        // ==================================================

        function formatProgress(summary) {

            if (!summary || !summary.modes) {
                return "";
            }

            const total = summary.total_sentences || 0;

            const dictation = summary.modes.dictation;
            const assemble = summary.modes.assemble;

            if (!dictation || !assemble) {
                return "";
            }

            return (
                "Chép chính tả: " +
                dictation.done + "/" + total +
                " câu, điểm TB " +
                dictation.average + "/100. " +

                "Ghép câu: " +
                assemble.done + "/" + total +
                " câu, điểm TB " +
                assemble.average + "/100."
            );
        }

        // ==================================================
        // 3. GUI KET QUA DEN FLASK
        // ==================================================

        async function saveResult(
            mode,
            sentenceIndex,
            answer,
            replayCount
        ) {

            showStatus(
                mode,
                "Đang lưu kết quả...",
                false
            );

            try {

                const headers = {
                    "Content-Type": "application/json"
                };

                if (csrfToken) {
                    headers["X-CSRFToken"] = csrfToken;
                }

                const response = await fetch(
                    saveUrl,
                    {
                        method: "POST",
                        credentials: "same-origin",
                        headers: headers,

                        body: JSON.stringify({
                            content_id: contentId,
                            sentence_index: sentenceIndex,
                            mode: mode,
                            answer: answer,
                            replay_count: replayCount
                        })
                    }
                );

                const contentType = (
                    response.headers.get("content-type") || ""
                ).toLowerCase();

                if (!contentType.includes("application/json")) {
                    throw new Error(
                        "Máy chủ không trả về JSON. " +
                        "Hãy kiểm tra đăng nhập và CSRF."
                    );
                }

                const data = await response.json();

                if (!response.ok || !data.saved) {

                    throw new Error(
                        data.error ||
                        "Không lưu được kết quả."
                    );
                }

                showStatus(
                    mode,
                    "Đã lưu vào SQL Server. " +
                    "Điểm: " + data.score + "/100. " +
                    formatProgress(data.summary),
                    false
                );

                console.log(
                    "[Shadowing] Đã lưu kết quả:",
                    data
                );

            } catch (error) {

                console.error(
                    "[Shadowing] Lỗi lưu kết quả:",
                    error
                );

                showStatus(
                    mode,
                    "Chưa lưu được kết quả: " +
                    error.message,
                    true
                );
            }
        }

        // ==================================================
        // 4. LAY KET QUA VUA KIEM TRA
        //
        // Hai Map va currentIndex duoc khai bao trong
        // shadowing-study.js, tai truoc file nay.
        // ==================================================

        function saveCheckedAnswer(mode) {

            try {

                const index = currentIndex;

                const attempts = mode === "dictation"
                    ? dictationAttempts
                    : assembleAttempts;

                const attempt = attempts.get(index);

                if (
                    !attempt ||
                    typeof attempt.answer !== "string" ||
                    !attempt.answer.trim()
                ) {
                    return;
                }

                const answer = attempt.answer;

                if (mode === "dictation") {

                    const input = document.getElementById(
                        "dictationAnswer"
                    );

                    // Khong gui dap an cu khi nguoi hoc
                    // vua thay doi noi dung o nhap.
                    if (
                        !input ||
                        input.value.trim() !== answer
                    ) {
                        return;
                    }

                } else {

                    const state = assembleStates.get(index);

                    if (
                        !state ||
                        !Array.isArray(state.pieces) ||
                        !Array.isArray(state.selected) ||
                        state.pieces.length < 2 ||
                        state.selected.length !==
                            state.pieces.length
                    ) {
                        return;
                    }

                    const selectedAnswer = state.selected
                        .map(id => state.pieces[id])
                        .join("");

                    if (selectedAnswer !== answer) {
                        return;
                    }
                }

                const replayCount =
                    replayCounts.get(index) || 0;

                saveResult(
                    mode,
                    index,
                    answer,
                    replayCount
                );

            } catch (error) {

                console.error(
                    "[Shadowing] Không đọc được đáp án:",
                    error
                );

                showStatus(
                    mode,
                    "Không đọc được kết quả vừa kiểm tra.",
                    true
                );
            }
        }

        // ==================================================
        // 5. GAN SU KIEN SAU JS GOC
        //
        // shadowing-study.js duoc nap truoc file nay.
        // Handler cu cham diem truoc, handler moi luu sau.
        // ==================================================

        const dictationButton = document.getElementById(
            "btnCheckDictation"
        );

        const assembleButton = document.getElementById(
            "btnCheckAssemble"
        );

        if (dictationButton) {

            dictationButton.addEventListener(
                "click",
                function () {
                    saveCheckedAnswer("dictation");
                }
            );
        }

        if (assembleButton) {

            assembleButton.addEventListener(
                "click",
                function () {
                    saveCheckedAnswer("assemble");
                }
            );
        }

        // ==================================================
        // 6. DOC TIEN DO CU KHI MO VIDEO
        // ==================================================

        async function loadPreviousProgress() {

            try {

                const response = await fetch(
                    summaryUrl,
                    {
                        credentials: "same-origin"
                    }
                );

                if (!response.ok) {
                    return;
                }

                const summary = await response.json();

                if (!summary || !summary.modes) {
                    return;
                }

                const dictation = summary.modes.dictation;
                const assemble = summary.modes.assemble;

                if (
                    dictation.done === 0 &&
                    assemble.done === 0
                ) {
                    return;
                }

                const message =
                    "Tiến độ lần học trước: " +
                    formatProgress(summary);

                showStatus(
                    "dictation",
                    message,
                    false
                );

                showStatus(
                    "assemble",
                    message,
                    false
                );

            } catch (error) {

                console.warn(
                    "[Shadowing] Không tải được tiến độ:",
                    error
                );
            }
        }

        loadPreviousProgress();

        console.log(
            "[Shadowing] Đã khởi tạo chức năng lưu điểm."
        );
    }

    // ======================================================
    // 7. KHOI TAO
    // ======================================================

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            initShadowingSave
        );

    } else {

        initShadowingSave();
    }

})();
