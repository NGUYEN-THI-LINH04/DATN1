
/**
 * MỘC HÁN - ADMIN CHATBOT
 *
 * Chức năng:
 * - Kiểm tra kết nối Ollama
 * - Gửi câu hỏi thử đến Qwen3
 * - Hiển thị câu trả lời
 * - Không hiển thị nội dung suy luận
 * - Hỗ trợ CSRF Flask
 *
 * API:
 * GET  /admin/chatbot/trang-thai
 * POST /admin/chatbot/thu-ai
 */

document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // =====================================================
    // LẤY CÁC THÀNH PHẦN GIAO DIỆN
    // =====================================================

    const settingsForm = document.getElementById(
        "chatbot-settings-form"
    );

    const checkConnectionButton = document.getElementById(
        "chatbot-check-connection"
    );

    const ollamaStatus = document.getElementById(
        "chatbot-ollama-status"
    );

    const ollamaDescription = document.getElementById(
        "chatbot-ollama-description"
    );

    const testButton = document.getElementById(
        "chatbot-test-button"
    );

    const questionInput = document.getElementById(
        "chatbot-test-question"
    );

    const resultBox = document.getElementById(
        "chatbot-test-result"
    );

    if (!settingsForm) {
        return;
    }

    // =====================================================
    // LẤY CSRF TOKEN
    // =====================================================

    function getCSRFToken() {
        const input = document.querySelector(
            'input[name="csrf_token"]'
        );

        if (input && input.value) {
            return input.value;
        }

        const meta = document.querySelector(
            'meta[name="csrf-token"]'
        );

        if (meta) {
            return meta.getAttribute("content") || "";
        }

        return "";
    }

    // =====================================================
    // HÀM ĐỌC PHẢN HỒI API
    // =====================================================

    async function parseResponse(response) {
        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            throw new Error(
                "Máy chủ trả về dữ liệu không hợp lệ. " +
                "Bạn kiểm tra đăng nhập Admin nhé."
            );
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error ||
                data.message ||
                "Có lỗi xảy ra khi xử lý yêu cầu."
            );
        }

        return data;
    }

    // =====================================================
    // HIỂN THỊ TRẠNG THÁI OLLAMA
    // =====================================================

    function updateOllamaStatus(online, models = []) {
        if (ollamaStatus) {
            ollamaStatus.textContent = online
                ? "● Đã kết nối"
                : "● Chưa kết nối";

            ollamaStatus.classList.remove(
                "chatbot-online",
                "chatbot-offline"
            );

            ollamaStatus.classList.add(
                online
                    ? "chatbot-online"
                    : "chatbot-offline"
            );
        }

        if (ollamaDescription) {
            if (online) {
                const count = Array.isArray(models)
                    ? models.length
                    : 0;

                ollamaDescription.textContent =
                    `Ollama đang hoạt động. Có ${count} mô hình AI.`;
            } else {
                ollamaDescription.textContent =
                    "Không thể kết nối tới Ollama.";
            }
        }
    }

    // =====================================================
    // KIỂM TRA KẾT NỐI OLLAMA
    // =====================================================

    async function checkConnection() {
        if (!checkConnectionButton) {
            return;
        }

        const originalText =
            checkConnectionButton.textContent;

        checkConnectionButton.disabled = true;
        checkConnectionButton.textContent =
            "Đang kiểm tra...";

        try {
            const response = await fetch(
                "/admin/chatbot/trang-thai",
                {
                    method: "GET",
                    credentials: "same-origin",
                    cache: "no-store",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            const data = await parseResponse(response);

            updateOllamaStatus(
                Boolean(data.online),
                data.models || []
            );

        } catch (error) {
            updateOllamaStatus(false);

            if (ollamaDescription) {
                ollamaDescription.textContent =
                    error.message ||
                    "Không kiểm tra được kết nối.";
            }
        } finally {
            checkConnectionButton.disabled = false;

            checkConnectionButton.textContent =
                originalText;
        }
    }

    if (checkConnectionButton) {
        checkConnectionButton.addEventListener(
            "click",
            checkConnection
        );
    }

    // =====================================================
    // XỬ LÝ NỘI DUNG AI
    // =====================================================

    function cleanAnswer(content) {
        let text = String(content || "");

        // Xóa thẻ suy luận của Qwen3 nếu có.
        text = text.replace(
            /<think>[\s\S]*?<\/think>/gi,
            ""
        );

        // Xóa trường hợp khối think chưa đóng.
        text = text.replace(
            /<think>[\s\S]*$/gi,
            ""
        );

        // Không hiển thị dấu kết thúc suy luận.
        text = text.replace(
            /^\s*\.\.\.done thinking\.\s*/i,
            ""
        );

        return text.trim();
    }

    // =====================================================
    // HIỂN THỊ KẾT QUẢ
    // =====================================================

    function showResult(text, isError = false) {
        if (!resultBox) {
            return;
        }

        // Dùng textContent để tránh chèn HTML nguy hiểm.
        resultBox.textContent = text;

        resultBox.style.color = isError
            ? "#a63830"
            : "";

        resultBox.scrollTop =
            resultBox.scrollHeight;
    }

    // =====================================================
    // GỬI CÂU HỎI THỬ ĐẾN OLLAMA
    // =====================================================

    async function testChatbot() {
        if (!testButton || !questionInput || !resultBox) {
            return;
        }

        const question = questionInput.value.trim();

        if (!question) {
            showResult(
                "Bạn hãy nhập câu hỏi trước nhé.",
                true
            );

            questionInput.focus();
            return;
        }

        if (question.length > 500) {
            showResult(
                "Câu hỏi không được vượt quá 500 ký tự.",
                true
            );

            return;
        }

        const originalText = testButton.textContent;

        testButton.disabled = true;
        questionInput.disabled = true;

        testButton.textContent = "AI đang trả lời...";

        showResult(
            "Đang gửi câu hỏi đến trợ lý Mộc Hán..."
        );

        try {
            const response = await fetch(
                "/admin/chatbot/thu-ai",
                {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify({
                        question: question
                    })
                }
            );

            const data = await parseResponse(response);

            const answer = cleanAnswer(
                data.answer || ""
            );

            if (!answer) {
                showResult(
                    "AI chưa trả về câu trả lời.",
                    true
                );

                return;
            }

            showResult(answer);

        } catch (error) {
            showResult(
                error.message ||
                "Không thể kết nối tới chatbot.",
                true
            );
        } finally {
            testButton.disabled = false;
            questionInput.disabled = false;

            testButton.textContent = originalText;
        }
    }

    if (testButton) {
        testButton.addEventListener(
            "click",
            testChatbot
        );
    }

    // =====================================================
    // PHÍM TẮT CTRL + ENTER
    // =====================================================

    if (questionInput) {
        questionInput.addEventListener(
            "keydown",
            function (event) {
                if (
                    event.key === "Enter" &&
                    (event.ctrlKey || event.metaKey)
                ) {
                    event.preventDefault();

                    if (!testButton.disabled) {
                        testChatbot();
                    }
                }
            }
        );
    }

    // =====================================================
    // XÁC NHẬN TRƯỚC KHI LƯU
    // =====================================================

    settingsForm.addEventListener(
        "submit",
        function () {
            const submitButton = settingsForm.querySelector(
                'button[type="submit"]'
            );

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent =
                    "Đang lưu cấu hình...";
            }
        }
    );
});
