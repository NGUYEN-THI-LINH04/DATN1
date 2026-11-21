
/*
=========================================================
MỘC HÁN - LƯU TỪ VỰNG VÀO ÔN TẬP CÁ NHÂN

File: static/js/lesson-vocabulary-save.js

Chức năng:
- Đồng bộ dấu sao từ SQL Server
- Thêm một từ vào ôn tập
- Bỏ một từ khỏi ôn tập
- Thêm toàn bộ từ vựng của bài học
- Không ảnh hưởng các chế độ học của lesson-study.js

Backend: routes/student/vocabulary_review.py
=========================================================
*/

document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // =====================================================
    // 1. CẤU HÌNH API - KHỚP VỚI PYTHON
    // =====================================================

    const API = {
        savedIds: "/vocabulary-review/api/saved-ids",
        saveWord: "/vocabulary-review/api/save-word",
        removeWord: "/vocabulary-review/api/remove-word",
        saveLesson: "/vocabulary-review/api/save-lesson"
    };

    const studyPage = document.getElementById(
        "lessonStudyPage"
    );

    const vocabularyData = document.getElementById(
        "lessonVocabularyData"
    );

    const addAllButton = document.getElementById(
        "addAllReviewButton"
    );

    const starButtons = Array.from(
        document.querySelectorAll(".vocab-review-one")
    );

    if (!studyPage || !vocabularyData) {
        return;
    }

    let vocabularies = [];

    try {
        const data = JSON.parse(
            vocabularyData.textContent
        );

        vocabularies = Array.isArray(data) ? data : [];
    } catch (error) {
        console.error(
            "[Mộc Hán] Không đọc được dữ liệu từ vựng:",
            error
        );
        return;
    }

    if (vocabularies.length === 0) {
        return;
    }

    const lessonId = Number(
        studyPage.dataset.lessonId
    );

    const wordIds = [
        ...new Set(
            vocabularies
                .map(word => Number(word.id))
                .filter(
                    id => Number.isInteger(id) && id > 0
                )
        )
    ];

    const wordIdSet = new Set(wordIds);

    // Danh sách từ đã lưu trên SQL Server.
    let savedIds = new Set();

    let initialized = false;
    let busy = false;

    // =====================================================
    // 2. LẤY CSRF TOKEN
    // =====================================================

    function getCsrfToken() {
        const meta = document.querySelector(
            'meta[name="csrf-token"]'
        );

        const input = document.querySelector(
            'input[name="csrf_token"]'
        );

        return (
            window.lessonReviewCsrfToken ||
            meta?.getAttribute("content") ||
            input?.value ||
            ""
        );
    }

    // =====================================================
    // 3. GỌI API FLASK
    // =====================================================

    async function callApi(url, method = "GET", data = null) {
        const headers = {
            "Accept": "application/json"
        };

        const options = {
            method,
            credentials: "same-origin",
            headers
        };

        if (method !== "GET") {
            const csrfToken = getCsrfToken();

            if (!csrfToken) {
                throw new Error(
                    "Không tìm thấy CSRF token trên trang bài học."
                );
            }

            headers["Content-Type"] = "application/json";
            headers["X-CSRFToken"] = csrfToken;

            options.body = JSON.stringify(data || {});
        }

        const response = await fetch(url, options);

        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            if (response.status === 400) {
                throw new Error(
                    "Yêu cầu không hợp lệ. Hãy kiểm tra CSRF token."
                );
            }

            if (response.status === 401) {
                throw new Error(
                    "Bạn cần đăng nhập bằng tài khoản người học."
                );
            }

            throw new Error(
                "API không trả về JSON (HTTP " +
                response.status +
                ")."
            );
        }

        const result = await response.json();

        if (!response.ok || result.success === false) {
            throw new Error(
                result.message ||
                "Không thể xử lý yêu cầu."
            );
        }

        return result;
    }

    // =====================================================
    // 4. THÔNG BÁO
    // =====================================================

    let noticeTimeout = null;

    function showNotice(message, isError = false) {
        let notice = document.getElementById(
            "lessonVocabularySaveNotice"
        );

        if (!notice) {
            notice = document.createElement("div");

            notice.id = "lessonVocabularySaveNotice";

            notice.setAttribute("role", "status");

            Object.assign(notice.style, {
                position: "fixed",
                right: "20px",
                bottom: "24px",
                zIndex: "99999",
                maxWidth: "360px",
                padding: "12px 16px",
                borderRadius: "10px",
                fontSize: "13px",
                fontWeight: "500",
                lineHeight: "1.6",
                color: "#ffffff",
                boxShadow:
                    "0 5px 20px rgba(0,0,0,0.14)"
            });

            document.body.appendChild(notice);
        }

        notice.textContent = message;

        notice.style.background = isError
            ? "#b45147"
            : "#405d4c";

        notice.hidden = false;

        clearTimeout(noticeTimeout);

        noticeTimeout = setTimeout(function () {
            notice.hidden = true;
        }, 3000);
    }

    // =====================================================
    // 5. CẬP NHẬT DẤU SAO
    // =====================================================

    function updateStars() {
        starButtons.forEach(function (button) {
            const wordId = Number(
                button.dataset.vocabId
            );

            const saved = savedIds.has(wordId);

            const text = saved ? "★" : "☆";

            // Chỉ cập nhật khi thực sự khác,
            // tránh kích hoạt MutationObserver liên tục.
            if (button.textContent !== text) {
                button.textContent = text;
            }

            button.classList.toggle(
                "saved",
                saved
            );

            button.setAttribute(
                "aria-pressed",
                String(saved)
            );

            button.title = saved
                ? "Đã lưu - Bấm để bỏ khỏi ôn tập"
                : "Thêm từ vào ôn tập";

            button.disabled = busy || !initialized;
        });

        if (addAllButton) {
            const allSaved =
                wordIds.length > 0 &&
                wordIds.every(
                    id => savedIds.has(id)
                );

            addAllButton.textContent = allSaved
                ? "★ Đã thêm cả bài vào ôn tập"
                : "☆ Thêm cả bài vào ôn tập";

            addAllButton.disabled =
                busy ||
                !initialized ||
                allSaved;
        }
    }

    // =====================================================
    // 6. LẤY TỪ ĐÃ LƯU TỪ SQL SERVER
    // =====================================================

    async function loadSavedWords() {
        initialized = false;

        updateStars();

        const result = await callApi(
            API.savedIds,
            "GET"
        );

        if (!Array.isArray(result.word_ids)) {
            throw new Error(
                "API không trả về danh sách word_ids."
            );
        }

        savedIds = new Set(
            result.word_ids
                .map(Number)
                .filter(
                    id => Number.isInteger(id) && id > 0
                )
        );

        initialized = true;

        updateStars();

        console.log(
            "[Mộc Hán] Đã đồng bộ",
            savedIds.size,
            "từ đã lưu từ SQL Server."
        );
    }

    // =====================================================
    // 7. THÊM HOẶC BỎ MỘT TỪ
    // =====================================================

    async function toggleWord(wordId) {
        if (!initialized || busy) {
            return;
        }

        if (!wordIdSet.has(wordId)) {
            showNotice(
                "Mã từ vựng không hợp lệ.",
                true
            );
            return;
        }

        const alreadySaved = savedIds.has(wordId);

        busy = true;

        updateStars();

        try {
            if (alreadySaved) {
                // Bỏ từ khỏi danh sách.
                await callApi(
                    API.removeWord,
                    "POST",
                    {
                        word_id: wordId
                    }
                );

                savedIds.delete(wordId);

                showNotice(
                    "Đã bỏ từ khỏi danh sách ôn tập."
                );
            } else {
                // Thêm từ vào danh sách.
                await callApi(
                    API.saveWord,
                    "POST",
                    {
                        word_id: wordId
                    }
                );

                savedIds.add(wordId);

                showNotice(
                    "Đã thêm từ vào ôn tập cá nhân."
                );
            }
        } catch (error) {
            console.error(
                "[Mộc Hán] Lỗi thêm/bỏ từ:",
                error
            );

            showNotice(
                error.message ||
                "Không thể lưu từ vựng.",
                true
            );
        } finally {
            busy = false;
            updateStars();
        }
    }

    // =====================================================
    // 8. THÊM TOÀN BỘ TỪ CỦA BÀI HỌC
    // =====================================================

    async function addAllWords() {
        if (!initialized || busy) {
            return;
        }

        if (
            !Number.isInteger(lessonId) ||
            lessonId <= 0
        ) {
            showNotice(
                "Không xác định được mã bài học.",
                true
            );
            return;
        }

        const missingWords = wordIds.filter(
            id => !savedIds.has(id)
        );

        if (missingWords.length === 0) {
            showNotice(
                "Tất cả từ của bài đã được thêm vào ôn tập."
            );
            return;
        }

        busy = true;

        updateStars();

        try {
            const result = await callApi(
                API.saveLesson,
                "POST",
                {
                    lesson_id: lessonId
                }
            );

            // Chỉ đánh dấu những ID được server
            // xác nhận, không tự đoán lưu thành công.
            if (!Array.isArray(result.word_ids)) {
                throw new Error(
                    "API chưa trả về word_ids của bài học."
                );
            }

            result.word_ids.forEach(function (value) {
                const id = Number(value);

                if (wordIdSet.has(id)) {
                    savedIds.add(id);
                }
            });

            showNotice(
                "Đã thêm từ vựng của bài vào ôn tập."
            );
        } catch (error) {
            console.error(
                "[Mộc Hán] Lỗi thêm cả bài:",
                error
            );

            showNotice(
                error.message ||
                "Không thể thêm từ của bài.",
                true
            );
        } finally {
            busy = false;
            updateStars();
        }
    }

    // =====================================================
    // 9. CHẶN CLICK CŨ TRONG lesson-study.js
    //
    // lesson-study.js hiện xử lý nút sao bằng
    // localStorage.
    //
    // Chúng ta bắt sự kiện ở capture phase
    // để nút sao chỉ gọi SQL Server.
    //
    // Các nút học khác vẫn hoạt động bình thường.
    // =====================================================

    document.addEventListener(
        "click",
        function (event) {
            const target = event.target;

            if (!(target instanceof Element)) {
                return;
            }

            const starButton = target.closest(
                ".vocab-review-one"
            );

            if (starButton) {
                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();

                toggleWord(
                    Number(starButton.dataset.vocabId)
                );

                return;
            }

            const bulkButton = target.closest(
                "#addAllReviewButton"
            );

            if (bulkButton) {
                event.preventDefault();
                event.stopPropagation();
                event.stopImmediatePropagation();

                addAllWords();
            }
        },
        true
    );

    // =====================================================
    // 10. ĐỒNG BỘ SAO SAU KHI ĐỔI FLASHCARD
    //
    // File lesson-study.js vẫn cập nhật lại
    // giao diện khi chuyển từ.
    //
    // Observer sẽ sửa lại dấu sao theo SQL Server,
    // tránh hiển thị trạng thái localStorage cũ.
    // =====================================================

    if (starButtons.length > 0) {
        const observer = new MutationObserver(
            function () {
                if (initialized) {
                    updateStars();
                }
            }
        );

        starButtons.forEach(function (button) {
            observer.observe(button, {
                childList: true,
                characterData: true,
                subtree: true
            });
        });
    }

    // =====================================================
    // 11. KHỞI TẠO
    // =====================================================

    updateStars();

    loadSavedWords().catch(function (error) {
        console.error(
            "[Mộc Hán] Không tải được từ đã lưu:",
            error
        );

        showNotice(
            "Không thể đồng bộ từ ôn tập: " +
            error.message,
            true
        );

        initialized = false;

        updateStars();
    });
});
