
"use strict";

// ============================================================
// 1. DU LIEU SHADOWING TU FLASK / SQL SERVER
// ============================================================

const shadowingConfig = document.getElementById("shadowing-config");

window.SHADOWING_VIDEO_ID =
    shadowingConfig?.dataset.videoId || "";

try {
    const raw = shadowingConfig?.dataset.sentences || "[]";
    const data = JSON.parse(raw);

    window.SHADOWING_SENTENCES = Array.isArray(data)
        ? data
        : [];

} catch (error) {
    console.error("Loi doc du lieu Shadowing:", error);
    window.SHADOWING_SENTENCES = [];
}

const sentences = window.SHADOWING_SENTENCES;


// ============================================================
// 2. TRANG THAI CHUNG
// ============================================================

let player = null;
let playerReady = false;

let currentIndex = 0;
let activeStudyMode = "shadowing";

let showPinyin = true;
let showVi = true;
let showVideo = true;

let autoPause = false;
let pausedAtSentenceEnd = false;

let transcriptSyncTimer = null;
let lastVideoTime = null;
let ignoreSyncUntil = 0;
let isDraggingSeek = false;

// Chep chinh ta
const dictationAttempts = new Map();
const dictationDrafts = new Map();

// Ghep cau
const assembleStates = new Map();
const assembleAttempts = new Map();

// So lan nghe lai
const replayCounts = new Map();


// ============================================================
// 3. CAC HAM HO TRO
// ============================================================

function getElement(id) {
    return document.getElementById(id);
}

function getSentence(index) {
    return sentences[index] || null;
}

function clampIndex(index) {
    if (!sentences.length) return 0;

    return Math.max(
        0,
        Math.min(Number(index) || 0, sentences.length - 1)
    );
}

function hasPlayer() {
    return Boolean(
        playerReady &&
        player &&
        typeof player.getCurrentTime === "function"
    );
}

function getPlayerState() {
    if (!hasPlayer()) return -1;

    try {
        return player.getPlayerState();
    } catch (error) {
        return -1;
    }
}

function isPlaying() {
    return (
        typeof YT !== "undefined" &&
        getPlayerState() === YT.PlayerState.PLAYING
    );
}

function formatTime(seconds) {
    const value = Math.max(
        0,
        Math.floor(Number(seconds) || 0)
    );

    const minutes = Math.floor(value / 60);
    const remaining = value % 60;

    return minutes + ":" + String(remaining).padStart(2, "0");
}

function findSentenceIndexByTime(time) {
    const currentTime = Number(time);

    if (!Number.isFinite(currentTime)) return -1;

    for (let i = 0; i < sentences.length; i++) {
        const start = Number(sentences[i].start);
        const end = Number(sentences[i].end);

        if (
            Number.isFinite(start) &&
            Number.isFinite(end) &&
            currentTime >= start &&
            currentTime < end
        ) {
            return i;
        }
    }

    return -1;
}


// ============================================================
// 4. CHUAN HOA VA SO SANH DAP AN
// ============================================================

// Bo dau cau va khoang trang.
// Khong tu dong chuyen gian the / phon the.
function normalizeHanzi(text) {
    return String(text || "")
        .normalize("NFKC")
        .replace(/[\s\p{P}\p{S}]/gu, "");
}

// Levenshtein: dem so ky tu them, xoa, thay the.
function countCharacterErrors(expected, actual) {
    const a = Array.from(expected);
    const b = Array.from(actual);

    let previous = Array.from(
        { length: b.length + 1 },
        (_, index) => index
    );

    for (let i = 1; i <= a.length; i++) {
        const current = [i];

        for (let j = 1; j <= b.length; j++) {
            const cost = a[i - 1] === b[j - 1] ? 0 : 1;

            current[j] = Math.min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + cost
            );
        }

        previous = current;
    }

    return previous[b.length];
}

function calculateScore(expected, submitted) {
    const correctText = normalizeHanzi(expected);
    const submittedText = normalizeHanzi(submitted);

    const errors = countCharacterErrors(
        correctText,
        submittedText
    );

    const totalCharacters = Array.from(correctText).length;

    const score = totalCharacters
        ? Math.max(
            0,
            Math.round(
                (1 - errors / totalCharacters) * 100
            )
        )
        : 0;

    return {
        errors,
        score,
        correct: totalCharacters > 0 && errors === 0,
        totalCharacters
    };
}


// ============================================================
// 5. CHE DO HOC VA HIEN THI DAP AN
// ============================================================

function isPracticeMode() {
    return (
        activeStudyMode === "dictation" ||
        activeStudyMode === "assemble"
    );
}

function isAnswerRevealed(index = currentIndex) {
    if (activeStudyMode === "dictation") {
        return dictationAttempts.has(index);
    }

    if (activeStudyMode === "assemble") {
        return assembleAttempts.has(index);
    }

    return true;
}

function shouldHideAnswer(index = currentIndex) {
    return isPracticeMode() && !isAnswerRevealed(index);
}

function renderFocus(sentence) {
    const hanzi = getElement("focusHanzi");
    const pinyin = getElement("focusPinyin");
    const vi = getElement("focusVi");

    if (!hanzi || !pinyin || !vi) return;

    if (!sentence) {
        hanzi.textContent = "Đang chờ lời thoại...";
        pinyin.textContent = "";
        vi.textContent = "";
        return;
    }

    if (shouldHideAnswer()) {
        hanzi.textContent = activeStudyMode === "dictation"
            ? "🎧 Hãy nghe và chép lại câu tiếng Trung"
            : "🧩 Hãy nghe và ghép lại câu tiếng Trung";

        pinyin.textContent = "";
        vi.textContent = "";

        pinyin.hidden = true;
        vi.hidden = true;

        return;
    }

    hanzi.textContent = sentence.hanzi || "";
    pinyin.textContent = sentence.pinyin || "";
    vi.textContent = sentence.vi || "";

    pinyin.hidden = !showPinyin;
    vi.hidden = !showVi;
}

function updateTranscriptVisibility() {
    const root = document.querySelector(".shadowing-study");

    if (!root) return;

    root.classList.toggle(
        "is-practice-mode",
        isPracticeMode()
    );

    root.classList.toggle(
        "is-dictation-mode",
        activeStudyMode === "dictation"
    );

    root.classList.toggle(
        "is-assemble-mode",
        activeStudyMode === "assemble"
    );

    document.querySelectorAll(
        ".shadowing-transcript-item"
    ).forEach(item => {
        const index = Number(item.dataset.index);

        const hidden = isPracticeMode() &&
            !(
                index === currentIndex &&
                isAnswerRevealed(index)
            );

        const hanzi = item.querySelector(
            ".shadowing-transcript-hanzi"
        );

        const pinyin = item.querySelector(
            ".shadowing-transcript-pinyin"
        );

        const vi = item.querySelector(
            ".shadowing-transcript-vi"
        );

        if (hanzi) {
            if (!hanzi.dataset.originalText) {
                hanzi.dataset.originalText =
                    hanzi.textContent;
            }

            hanzi.textContent = hidden
                ? "🔒 Hoàn thành câu để xem đáp án"
                : hanzi.dataset.originalText;
        }

        if (pinyin) {
            pinyin.hidden = hidden || !showPinyin;
        }

        if (vi) {
            vi.hidden = hidden || !showVi;
        }
    });
}


// ============================================================
// 6. DONG BO CAU DANG HOC
// ============================================================

function highlightTranscript(index, scroll = true) {
    const items = document.querySelectorAll(
        ".shadowing-transcript-item"
    );

    items.forEach(item => {
        item.classList.toggle(
            "active",
            Number(item.dataset.index) === index
        );
    });

    if (!scroll || index < 0) return;

    const activeItem = Array.from(items).find(
        item => Number(item.dataset.index) === index
    );

    if (activeItem) {
        activeItem.scrollIntoView({
            behavior: "auto",
            block: "nearest"
        });
    }
}

function saveCurrentDictationDraft() {
    if (activeStudyMode !== "dictation") return;

    const input = getElement("dictationAnswer");

    if (input) {
        dictationDrafts.set(currentIndex, input.value);
    }
}

function refreshCurrentPractice() {
    refreshDictationSentence();
    renderAssemble();

    renderFocus(getSentence(currentIndex));
    updateTranscriptVisibility();
}

function setActiveSentence(
    index,
    shouldSeek = true,
    shouldPlay = true
) {
    if (!sentences.length) {
        renderFocus(null);
        return;
    }

    saveCurrentDictationDraft();

    currentIndex = clampIndex(index);
    pausedAtSentenceEnd = false;

    const sentence = getSentence(currentIndex);

    highlightTranscript(currentIndex);
    refreshCurrentPractice();

    if (shouldSeek && hasPlayer()) {
        ignoreSyncUntil = Date.now() + 700;
        lastVideoTime = null;

        player.seekTo(Number(sentence.start) || 0, true);

        if (shouldPlay) {
            player.playVideo();
        } else {
            player.pauseVideo();
        }
    }
}

function updateSentenceFromTime(time) {
    const index = findSentenceIndexByTime(time);

    if (index === -1) {
        highlightTranscript(-1, false);
        renderFocus(null);
        return;
    }

    if (index !== currentIndex) {
        saveCurrentDictationDraft();

        currentIndex = index;
        pausedAtSentenceEnd = false;

        highlightTranscript(index);
        refreshCurrentPractice();

    } else {
        const active = document.querySelector(
            ".shadowing-transcript-item.active"
        );

        if (!active) {
            renderFocus(getSentence(index));
            highlightTranscript(index);
        }
    }
}


// ============================================================
// 7. TU NGAT CAU
// ============================================================

function setAutoPause(enabled) {
    autoPause = Boolean(enabled);

    pausedAtSentenceEnd = false;
    lastVideoTime = null;

    const button = getElement("btnAutoPause");

    if (button) {
        button.textContent = autoPause
            ? "✂ Tự ngắt câu: Bật"
            : "✂ Tự ngắt câu: Tắt";

        button.classList.toggle(
            "is-active",
            autoPause
        );

        button.setAttribute(
            "aria-pressed",
            String(autoPause)
        );
    }

    if (autoPause && hasPlayer()) {
        updateSentenceFromTime(
            player.getCurrentTime()
        );
    }
}


// ============================================================
// 8. PHAT / TAM DUNG / NGHE LAI
// ============================================================

function updatePlayButtons() {
    const button = getElement("btnPlayPause");

    if (button) {
        const playing = isPlaying();

        button.textContent = playing ? "⏸" : "▶";
        button.title = playing ? "Tạm dừng" : "Phát";
    }
}

function togglePlayPause() {
    if (!hasPlayer()) return;

    if (isPlaying()) {
        player.pauseVideo();
        updatePlayButtons();
        return;
    }

    if (autoPause && pausedAtSentenceEnd) {
        const nextIndex = currentIndex < sentences.length - 1
            ? currentIndex + 1
            : currentIndex;

        setActiveSentence(nextIndex, true, true);
        return;
    }

    player.playVideo();
    updatePlayButtons();
}

function replayCurrentSentence() {
    const count = replayCounts.get(currentIndex) || 0;

    replayCounts.set(currentIndex, count + 1);

    setActiveSentence(currentIndex, true, true);
    renderDictationResult();
}


// ============================================================
// 9. AN / HIEN VIDEO
// ============================================================

function setVideoVisibility(visible) {
    showVideo = Boolean(visible);

    const root = document.querySelector(
        ".shadowing-study"
    );

    const button = getElement("btnToggleVideo");
    const audioBar = getElement("shadowingAudioBar");

    root?.classList.toggle(
        "is-video-hidden",
        !showVideo
    );

    if (audioBar) {
        audioBar.hidden = showVideo;
    }

    if (button) {
        button.textContent = showVideo
            ? "◉ Ẩn video"
            : "◉ Hiện video";

        button.setAttribute(
            "aria-pressed",
            String(!showVideo)
        );

        button.classList.toggle(
            "is-active",
            !showVideo
        );
    }
}


// ============================================================
// 10. PINYIN VA BAN DICH
// ============================================================

function updateTextVisibility() {
    const root = document.querySelector(
        ".shadowing-study"
    );

    const pinyinButton = getElement(
        "btnTogglePinyin"
    );

    const viButton = getElement(
        "btnToggleVi"
    );

    const pinyinCheckbox = getElement(
        "transcriptShowPinyin"
    );

    const viCheckbox = getElement(
        "transcriptShowVi"
    );

    root?.classList.toggle(
        "hide-transcript-pinyin",
        !showPinyin
    );

    root?.classList.toggle(
        "hide-transcript-vi",
        !showVi
    );

    pinyinButton?.classList.toggle(
        "active",
        showPinyin
    );

    viButton?.classList.toggle(
        "active",
        showVi
    );

    if (pinyinCheckbox) {
        pinyinCheckbox.checked = showPinyin;
    }

    if (viCheckbox) {
        viCheckbox.checked = showVi;
    }

    renderFocus(getSentence(currentIndex));
    updateTranscriptVisibility();
}


// ============================================================
// 11. THANH TUA VIDEO
// ============================================================

function updateAudioBar() {
    if (!hasPlayer()) return;

    const seek = getElement("shadowingAudioSeek");
    const label = getElement("shadowingAudioTime");

    const now = Number(
        player.getCurrentTime() || 0
    );

    const duration = Number(
        player.getDuration() || 0
    );

    if (seek && duration > 0 && !isDraggingSeek) {
        seek.value = String(
            (now / duration) * 100
        );
    }

    if (label) {
        label.textContent =
            formatTime(now) + " / " +
            formatTime(duration);
    }
}

function seekToPercent(percent) {
    if (!hasPlayer()) return;

    const duration = Number(
        player.getDuration() || 0
    );

    if (duration <= 0) return;

    const value = Math.max(
        0,
        Math.min(Number(percent) || 0, 100)
    );

    const time = duration * value / 100;

    pausedAtSentenceEnd = false;
    ignoreSyncUntil = Date.now() + 700;
    lastVideoTime = null;

    player.seekTo(time, true);

    updateSentenceFromTime(time);
    updateAudioBar();
}


// ============================================================
// 12. DONG BO VIDEO VA TU NGAT CAU
// ============================================================

function syncTranscriptWithVideo() {
    if (!hasPlayer()) return;

    const time = Number(
        player.getCurrentTime() || 0
    );

    const state = getPlayerState();

    updateAudioBar();
    updatePlayButtons();

    if (!sentences.length) return;

    if (Date.now() < ignoreSyncUntil) {
        return;
    }

    if (
        typeof YT === "undefined" ||
        state !== YT.PlayerState.PLAYING
    ) {
        lastVideoTime = time;
        return;
    }

    const wasJump =
        lastVideoTime !== null &&
        Math.abs(time - lastVideoTime) > 1.5;

    lastVideoTime = time;

    if (wasJump) {
        pausedAtSentenceEnd = false;
        updateSentenceFromTime(time);
        return;
    }

    if (!autoPause) {
        updateSentenceFromTime(time);
        return;
    }

    const current = getSentence(currentIndex);

    if (!current) return;

    const start = Number(current.start);
    const end = Number(current.end);

    if (
        !Number.isFinite(start) ||
        !Number.isFinite(end)
    ) {
        return;
    }

    if (
        time < start - 0.7 ||
        time > end + 1.2
    ) {
        pausedAtSentenceEnd = false;
        updateSentenceFromTime(time);
        return;
    }

    if (time >= end - 0.06) {
        if (!pausedAtSentenceEnd) {
            pausedAtSentenceEnd = true;

            player.pauseVideo();

            renderFocus(current);
            highlightTranscript(
                currentIndex,
                false
            );

            updatePlayButtons();
        }

        return;
    }

    if (time >= start && time < end) {
        const active = document.querySelector(
            ".shadowing-transcript-item.active"
        );

        if (
            !active ||
            Number(active.dataset.index) !== currentIndex
        ) {
            renderFocus(current);
            highlightTranscript(currentIndex);
        }
    }
}


// ============================================================
// 13. HAM HIEN THI KET QUA CHUNG
// ============================================================

function makeResultLine(label, value) {
    const paragraph = document.createElement("p");

    const strong = document.createElement("strong");
    strong.textContent = label;

    paragraph.append(
        strong,
        document.createTextNode(
            String(value ?? "")
        )
    );

    return paragraph;
}

function setResultStatus(element, status) {
    if (!element) return;

    element.classList.remove(
        "is-correct",
        "is-wrong"
    );

    if (status === true) {
        element.classList.add("is-correct");
    }

    if (status === false) {
        element.classList.add("is-wrong");
    }
}


// ============================================================
// 14. CHEP CHINH TA - HIEN THI KET QUA
// ============================================================

function renderDictationResult() {
    const result = getElement("dictationResult");
    const sentence = getSentence(currentIndex);

    if (!result) return;

    result.replaceChildren();
    setResultStatus(result, null);

    if (!sentence) {
        result.textContent =
            "Không có câu thoại để kiểm tra.";
        return;
    }

    const attempt = dictationAttempts.get(
        currentIndex
    );

    if (!attempt) {
        result.textContent =
            "Chưa kiểm tra đáp án.";
        return;
    }

    const heading = document.createElement("h3");

    heading.textContent = attempt.correct
        ? "✅ Chính xác!"
        : "❌ Câu trả lời chưa chính xác";

    result.append(
        heading,
        makeResultLine(
            "Điểm: ",
            `${attempt.score}/100`
        ),
        makeResultLine(
            "Số lỗi: ",
            attempt.errors
        ),
        makeResultLine(
            "Số lần nghe lại: ",
            replayCounts.get(currentIndex) || 0
        ),
        makeResultLine(
            "Bạn đã viết: ",
            attempt.answer
        ),
        makeResultLine(
            "Đáp án đúng: ",
            sentence.hanzi || ""
        ),
        makeResultLine(
            "Pinyin: ",
            sentence.pinyin || ""
        ),
        makeResultLine(
            "Nghĩa tiếng Việt: ",
            sentence.vi || ""
        )
    );

    setResultStatus(result, attempt.correct);
}

function checkDictation() {
    const input = getElement("dictationAnswer");
    const result = getElement("dictationResult");
    const sentence = getSentence(currentIndex);

    if (!input || !result || !sentence) return;

    const answer = input.value.trim();

    if (!normalizeHanzi(answer)) {
        result.textContent =
            "Bạn chưa nhập câu trả lời bằng chữ Hán.";

        input.focus();
        return;
    }

    const evaluation = calculateScore(
        sentence.hanzi || "",
        answer
    );

    dictationDrafts.set(currentIndex, answer);

    dictationAttempts.set(currentIndex, {
        answer,
        ...evaluation
    });

    renderDictationResult();
    renderFocus(sentence);
    updateTranscriptVisibility();
}

function refreshDictationSentence() {
    const input = getElement("dictationAnswer");
    const counter = getElement("dictationCounter");

    if (input) {
        input.value =
            dictationDrafts.get(currentIndex) || "";
    }

    if (counter) {
        counter.textContent =
            `Câu ${currentIndex + 1} / ${sentences.length}`;
    }

    renderDictationResult();
}

function clearDictation() {
    const input = getElement("dictationAnswer");

    dictationDrafts.delete(currentIndex);
    dictationAttempts.delete(currentIndex);

    if (input) {
        input.value = "";
        input.focus();
    }

    refreshDictationSentence();

    renderFocus(getSentence(currentIndex));
    updateTranscriptVisibility();
}

function handleDictationInput() {
    const input = getElement("dictationAnswer");

    if (!input) return;

    dictationDrafts.set(
        currentIndex,
        input.value
    );

    if (dictationAttempts.has(currentIndex)) {
        dictationAttempts.delete(currentIndex);

        renderFocus(getSentence(currentIndex));
        updateTranscriptVisibility();
    }

    renderDictationResult();
}


// ============================================================
// 15. GHEP CAU - TACH CAC MANH TU CAU GOC
// ============================================================

// Tach cau thanh cac tu/cum tu.
// Intl.Segmenter duoc su dung khi trinh duyet ho tro.
// Khong can cai thu vien ngoai.
function splitSentenceIntoPieces(hanzi) {
    const text = normalizeHanzi(hanzi);

    if (!text) return [];

    const characters = Array.from(text);

    if (characters.length === 1) {
        return [text];
    }

    let words = [];

    if (
        typeof Intl !== "undefined" &&
        typeof Intl.Segmenter === "function"
    ) {
        try {
            const segmenter = new Intl.Segmenter(
                "zh",
                { granularity: "word" }
            );

            words = Array.from(
                segmenter.segment(text),
                item => item.segment
            ).filter(Boolean);

        } catch (error) {
            words = [];
        }
    }

    if (!words.length) {
        // Phuong an du phong neu khong co Segmenter.
        words = characters;
    }

    const pieces = [];
    let buffer = "";

    function pushBuffer() {
        if (buffer) {
            pieces.push(buffer);
            buffer = "";
        }
    }

    // Gom cac tu thanh cum 2-4 ky tu, tranh qua nhieu
    // nut nho doi voi cau dai.
    for (const word of words) {
        const nextLength = Array.from(
            buffer + word
        ).length;

        if (
            buffer &&
            Array.from(buffer).length >= 2 &&
            nextLength > 4
        ) {
            pushBuffer();
        }

        buffer += word;

        if (Array.from(buffer).length >= 4) {
            pushBuffer();
        }
    }

    pushBuffer();

    // Neu manh cuoi chi 1 ky tu thi ghep vao manh truoc.
    if (
        pieces.length > 1 &&
        Array.from(pieces[pieces.length - 1]).length === 1
    ) {
        const last = pieces.pop();
        pieces[pieces.length - 1] += last;
    }

    // Cau ngan co the chi ra mot manh.
    // Chia thanh hai manh de van co bai tap.
    if (pieces.length < 2 && characters.length >= 2) {
        const middle = Math.ceil(
            characters.length / 2
        );

        return [
            characters.slice(0, middle).join(""),
            characters.slice(middle).join("")
        ];
    }

    return pieces;
}


// ============================================================
// 16. GHEP CAU - XAO TRON CAC MANH
// ============================================================

function shufflePieces(pieces) {
    const shuffled = pieces.map((text, id) => ({
        id,
        text
    }));

    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(
            Math.random() * (i + 1)
        );

        [shuffled[i], shuffled[j]] = [
            shuffled[j],
            shuffled[i]
        ];
    }

    // Dam bao khong hien ra dung thu tu goc.
    if (
        shuffled.length > 1 &&
        shuffled.every(
            (piece, index) => piece.id === index
        )
    ) {
        [shuffled[0], shuffled[1]] = [
            shuffled[1],
            shuffled[0]
        ];
    }

    return shuffled;
}

function getAssembleState(index = currentIndex) {
    if (assembleStates.has(index)) {
        return assembleStates.get(index);
    }

    const sentence = getSentence(index);

    if (!sentence) return null;

    const pieces = splitSentenceIntoPieces(
        sentence.hanzi || ""
    );

    const state = {
        pieces,
        shuffled: shufflePieces(pieces),
        selected: []
    };

    assembleStates.set(index, state);

    return state;
}


// ============================================================
// 17. GHEP CAU - TAO NUT MANH GHEP
// ============================================================

function createAssembleButton(piece, onClick) {
    const button = document.createElement("button");

    button.type = "button";
    button.className = "assemble-piece";
    button.textContent = piece.text;

    button.addEventListener(
        "click",
        onClick
    );

    return button;
}

function invalidateAssembleAttempt() {
    assembleAttempts.delete(currentIndex);

    renderFocus(getSentence(currentIndex));
    updateTranscriptVisibility();
}

function renderAssemble() {
    const availableBox = getElement(
        "assembleAvailable"
    );

    const selectedBox = getElement(
        "assembleSelected"
    );

    const counter = getElement(
        "assembleCounter"
    );

    const result = getElement(
        "assembleResult"
    );

    if (
        !availableBox ||
        !selectedBox ||
        !result
    ) {
        return;
    }

    availableBox.replaceChildren();
    selectedBox.replaceChildren();

    if (counter) {
        counter.textContent =
            `Câu ${currentIndex + 1} / ${sentences.length}`;
    }

    const state = getAssembleState();

    if (!state || !state.pieces.length) {
        result.textContent =
            "Câu này chưa có dữ liệu ghép câu.";
        return;
    }

    // Cac manh da ghep.
    for (const id of state.selected) {
        const piece = {
            id,
            text: state.pieces[id]
        };

        const button = createAssembleButton(
            piece,
            () => {
                const position =
                    state.selected.indexOf(id);

                if (position !== -1) {
                    state.selected.splice(
                        position,
                        1
                    );
                }

                invalidateAssembleAttempt();
                renderAssemble();
            }
        );

        selectedBox.appendChild(button);
    }

    if (state.selected.length === 0) {
        const hint = document.createElement("span");

        hint.className = "assemble-hint";

        hint.textContent =
            "Chọn các mảnh phía dưới để ghép thành câu...";

        selectedBox.appendChild(hint);
    }

    // Cac manh chua duoc chon.
    for (const piece of state.shuffled) {
        if (
            state.selected.includes(piece.id)
        ) {
            continue;
        }

        const button = createAssembleButton(
            piece,
            () => {
                state.selected.push(piece.id);

                invalidateAssembleAttempt();
                renderAssemble();
            }
        );

        availableBox.appendChild(button);
    }

    renderAssembleResult();
}


// ============================================================
// 18. GHEP CAU - KIEM TRA DAP AN
// ============================================================

function checkAssemble() {
    const state = getAssembleState();
    const result = getElement("assembleResult");
    const sentence = getSentence(currentIndex);

    if (!state || !result || !sentence) {
        return;
    }

    if (state.pieces.length < 2) {
        result.textContent =
            "Câu này quá ngắn để tạo bài tập ghép câu.";
        return;
    }

    if (
        state.selected.length !==
        state.pieces.length
    ) {
        result.textContent =
            "Bạn cần chọn đủ các mảnh trước khi kiểm tra.";

        return;
    }

    const answer = state.selected
        .map(id => state.pieces[id])
        .join("");

    // Cham theo cau goc, khong cham theo ID don thuan
    // de xu ly dung cac manh trung noi dung.
    const evaluation = calculateScore(
        sentence.hanzi,
        answer
    );

    assembleAttempts.set(currentIndex, {
        answer,
        ...evaluation
    });

    renderAssembleResult();

    renderFocus(sentence);
    updateTranscriptVisibility();
}

function renderAssembleResult() {
    const result = getElement("assembleResult");

    if (!result) return;

    result.replaceChildren();
    setResultStatus(result, null);

    const sentence = getSentence(currentIndex);

    if (!sentence) {
        result.textContent =
            "Không có câu thoại để ghép.";
        return;
    }

    const attempt = assembleAttempts.get(
        currentIndex
    );

    if (!attempt) {
        result.textContent =
            "Chưa kiểm tra đáp án.";
        return;
    }

    const heading = document.createElement("h3");

    heading.textContent = attempt.correct
        ? "✅ Ghép câu chính xác!"
        : "❌ Thứ tự ghép chưa chính xác";

    result.append(
        heading,
        makeResultLine(
            "Điểm: ",
            `${attempt.score}/100`
        ),
        makeResultLine(
            "Số ký tự sai thứ tự: ",
            attempt.errors
        ),
        makeResultLine(
            "Câu bạn ghép: ",
            attempt.answer
        ),
        makeResultLine(
            "Đáp án đúng: ",
            sentence.hanzi || ""
        ),
        makeResultLine(
            "Pinyin: ",
            sentence.pinyin || ""
        ),
        makeResultLine(
            "Nghĩa tiếng Việt: ",
            sentence.vi || ""
        )
    );

    setResultStatus(
        result,
        attempt.correct
    );
}


// ============================================================
// 19. GHEP CAU - LAM LAI
// ============================================================

function resetAssemble() {
    assembleStates.delete(currentIndex);
    assembleAttempts.delete(currentIndex);

    renderAssemble();

    renderFocus(
        getSentence(currentIndex)
    );

    updateTranscriptVisibility();
}

function setupAssembleControls() {
    getElement("btnCheckAssemble")?.addEventListener(
        "click",
        checkAssemble
    );

    getElement("btnResetAssemble")?.addEventListener(
        "click",
        resetAssemble
    );
}


// ============================================================
// 20. CHUYEN CHE DO HOC
// ============================================================

function activateStudyMode(mode) {
    const allowed = [
        "shadowing",
        "dictation",
        "assemble"
    ];

    if (!allowed.includes(mode)) {
        return;
    }

    saveCurrentDictationDraft();

    activeStudyMode = mode;

    document.querySelectorAll(
        "[data-study-tab]"
    ).forEach(button => {
        const active =
            button.dataset.studyTab === mode;

        button.classList.toggle(
            "active",
            active
        );

        button.setAttribute(
            "aria-selected",
            String(active)
        );
    });

    document.querySelectorAll(
        "[data-study-panel]"
    ).forEach(panel => {
        panel.hidden =
            panel.dataset.studyPanel !== mode;
    });

    if (isPracticeMode()) {
        setAutoPause(true);

        if (hasPlayer()) {
            player.pauseVideo();
        }
    }

    refreshCurrentPractice();
}

function setupTabs() {
    document.querySelectorAll(
        "[data-study-tab]"
    ).forEach(button => {
        button.addEventListener(
            "click",
            () => {
                activateStudyMode(
                    button.dataset.studyTab
                );
            }
        );
    });
}


// ============================================================
// 21. CLICK CAU TRONG BAN CHEP
// ============================================================

function setupTranscriptClicks() {
    document.querySelectorAll(
        ".shadowing-transcript-item"
    ).forEach(item => {
        item.addEventListener("click", () => {
            const index = Number(
                item.dataset.index
            );

            if (!Number.isInteger(index)) {
                return;
            }

            setActiveSentence(
                index,
                true,
                true
            );
        });
    });
}


// ============================================================
// 22. GAN CAC SU KIEN DIEU KHIEN
// ============================================================

function setupControls() {
    const prevBtn = getElement("btnPrev");
    const replayBtn = getElement("btnReplay");
    const playPauseBtn = getElement("btnPlayPause");
    const nextBtn = getElement("btnNext");

    const pinyinBtn = getElement("btnTogglePinyin");
    const viBtn = getElement("btnToggleVi");

    const videoBtn = getElement("btnToggleVideo");
    const autoPauseBtn = getElement("btnAutoPause");

    const pinyinCheckbox = getElement(
        "transcriptShowPinyin"
    );

    const viCheckbox = getElement(
        "transcriptShowVi"
    );

    const audioSeek = getElement(
        "shadowingAudioSeek"
    );

    // Cau truoc.
    prevBtn?.addEventListener("click", () => {
        setActiveSentence(
            currentIndex - 1,
            true,
            true
        );
    });

    // Nghe lai.
    replayBtn?.addEventListener(
        "click",
        replayCurrentSentence
    );

    // Phat / dung.
    playPauseBtn?.addEventListener(
        "click",
        togglePlayPause
    );

    // Cau tiep theo.
    nextBtn?.addEventListener("click", () => {
        setActiveSentence(
            currentIndex + 1,
            true,
            true
        );
    });

    autoPauseBtn?.addEventListener("click", () => {
        setAutoPause(!autoPause);
    });

    videoBtn?.addEventListener("click", () => {
        setVideoVisibility(!showVideo);
    });

    pinyinBtn?.addEventListener("click", () => {
        showPinyin = !showPinyin;
        updateTextVisibility();
    });

    viBtn?.addEventListener("click", () => {
        showVi = !showVi;
        updateTextVisibility();
    });

    pinyinCheckbox?.addEventListener(
        "change",
        event => {
            showPinyin = event.target.checked;
            updateTextVisibility();
        }
    );

    viCheckbox?.addEventListener(
        "change",
        event => {
            showVi = event.target.checked;
            updateTextVisibility();
        }
    );

    // Thanh tua khi an video.
    if (audioSeek) {
        audioSeek.addEventListener("input", () => {
            isDraggingSeek = true;

            if (!hasPlayer()) return;

            const duration =
                player.getDuration() || 0;

            const time =
                duration *
                Number(audioSeek.value) / 100;

            const label = getElement(
                "shadowingAudioTime"
            );

            if (label) {
                label.textContent =
                    formatTime(time) +
                    " / " +
                    formatTime(duration);
            }
        });

        audioSeek.addEventListener("change", () => {
            seekToPercent(audioSeek.value);
            isDraggingSeek = false;
        });

        audioSeek.addEventListener("pointerup", () => {
            isDraggingSeek = false;
        });
    }

    // Chep chinh ta.
    getElement("btnCheckDictation")?.addEventListener(
        "click",
        checkDictation
    );

    getElement("btnClearDictation")?.addEventListener(
        "click",
        clearDictation
    );

    getElement("dictationAnswer")?.addEventListener(
        "input",
        handleDictationInput
    );

    // Ghep cau.
    setupAssembleControls();
}


// ============================================================
// 23. KHOI TAO TRANG
// ============================================================

function initializeShadowing() {
    setupTabs();
    setupTranscriptClicks();
    setupControls();

    const activeTab = document.querySelector(
        "[data-study-tab].active"
    );

    const initialMode =
        activeTab?.dataset.studyTab || "shadowing";

    if (sentences.length) {
        setActiveSentence(
            0,
            false,
            false
        );
    } else {
        renderFocus(null);
    }

    setAutoPause(false);
    setVideoVisibility(true);

    activateStudyMode(initialMode);
    updateTextVisibility();
}

if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initializeShadowing
    );
} else {
    initializeShadowing();
}


// ============================================================
// 24. YOUTUBE IFRAME API
// ============================================================

function onYouTubeIframeAPIReady() {
    if (player) return;

    const videoId =
        window.SHADOWING_VIDEO_ID;

    if (!videoId) {
        console.error(
            "Không tìm thấy YouTube ID."
        );
        return;
    }

    if (!getElement("youtube-player")) {
        console.error(
            "Không tìm thấy khung YouTube."
        );
        return;
    }

    player = new YT.Player(
        "youtube-player",
        {
            videoId,

            playerVars: {
                playsinline: 1,
                rel: 0,
                cc_load_policy: 1
            },

            events: {
                onReady: function () {
                    playerReady = true;

                    if (
                        transcriptSyncTimer !== null
                    ) {
                        clearInterval(
                            transcriptSyncTimer
                        );
                    }

                    transcriptSyncTimer = setInterval(
                        syncTranscriptWithVideo,
                        100
                    );

                    updateAudioBar();
                    updatePlayButtons();

                    if (isPracticeMode()) {
                        setAutoPause(true);
                    }
                },

                onStateChange: function () {
                    updatePlayButtons();
                    updateAudioBar();
                },

                onError: function (event) {
                    console.error(
                        "Lỗi YouTube Player:",
                        event.data
                    );
                }
            }
        }
    );
}

window.onYouTubeIframeAPIReady =
    onYouTubeIframeAPIReady;

// Truong hop API YouTube da san sang truoc file JS.
if (
    window.YT &&
    typeof window.YT.Player === "function"
) {
    onYouTubeIframeAPIReady();
}
