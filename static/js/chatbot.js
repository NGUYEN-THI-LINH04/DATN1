
/**
 * =========================================================
 * MỘC HÁN - CHATBOT NGƯỜI HỌC
 *
 * File: static/js/chatbot.js
 *
 * Chức năng:
 * 01. Khởi tạo giao diện chatbot
 * 02. Đọc CSRF token
 * 03. Gửi câu hỏi đến Flask
 * 04. Hiển thị câu trả lời từ SQL / Qwen3
 * 05. Hiển thị trạng thái đang trả lời
 * 06. Tạo cuộc trò chuyện mới
 * 07. Tải danh sách lịch sử từ SQL
 * 08. Mở lại cuộc trò chuyện cũ
 * 09. Giữ mã hội thoại khi gửi câu tiếp theo
 * 10. Xử lý lỗi mạng và lỗi backend
 * 11. Hỗ trợ Enter và Shift + Enter
 * 12. Không hiển thị nội dung <think>
 * 13. Ẩn / hiện lịch sử để mở rộng khung trò chuyện
 *
 * Backend:
 * routes/student/chatbot.py
 *
 * API:
 * POST /chatbot/api/chat
 * GET  /chatbot/api/conversations
 * GET  /chatbot/api/conversations/<id>
 *
 * Dữ liệu được lưu ở SQL Server bởi Flask.
 * Không lưu lịch sử vào localStorage.
 * =========================================================
 */

document.addEventListener("DOMContentLoaded", function () {
    "use strict";


    // =====================================================
    // 01. LẤY CÁC PHẦN TỬ HTML
    // =====================================================

    const chatForm = document.getElementById(
        "chatbot-form"
    );

    const chatInput = document.getElementById(
        "chatbot-input"
    );

    const sendButton = document.getElementById(
        "chatbot-send"
    );

    const messagesBox = document.getElementById(
        "chatbot-messages"
    );

    const conversationList = document.getElementById(
        "chatbot-conversations"
    );

    const newChatButton = document.getElementById(
        "chatbot-new"
    );

    const statusBox = document.getElementById(
        "chatbot-status"
    );

    // Các phần tử phục vụ chức năng ẩn / hiện lịch sử.
    const chatbotLayout = document.getElementById(
        "chatbot-layout"
    );

    const historyPanel = document.getElementById(
        "chatbot-history-panel"
    );

    const historyToggle = document.getElementById(
        "chatbot-history-toggle"
    );

    const historyToggleText = document.getElementById(
        "chatbot-history-toggle-text"
    );

    // Chỉ chạy ở trang chatbot Student.
    if (
        !chatForm ||
        !chatInput ||
        !sendButton ||
        !messagesBox ||
        !conversationList
    ) {
        return;
    }


    // =====================================================
    // 02. KHAI BÁO API BACKEND
    //
    // Những route này đã được đăng ký trong app.py.
    // =====================================================

    const API = {
        send: "/chatbot/api/chat",

        conversations: "/chatbot/api/conversations",

        detail: function (id) {
            return (
                "/chatbot/api/conversations/" +
                encodeURIComponent(id)
            );
        }
    };


    // =====================================================
    // 03. TRẠNG THÁI CHATBOT
    //
    // conversationId:
    //     null = cuộc trò chuyện mới
    //     số ID = hội thoại đã lưu trong SQL
    //
    // isSending:
    //     Ngăn gửi hai câu đồng thời.
    //
    // isLoading:
    //     Ngăn chuyển hội thoại khi đang tải.
    // =====================================================

    let conversationId = null;

    let isSending = false;

    let isLoading = false;

    let historyVersion = 0;


    // =====================================================
    // 03A. ẨN / HIỆN LỊCH SỬ TRÒ CHUYỆN
    //
    // - Chỉ thay đổi bố cục hiển thị ở phía trình duyệt.
    // - Không xóa cuộc trò chuyện đang mở.
    // - Không ghi hoặc xóa dữ liệu SQL Server.
    // - Không dùng localStorage để lưu lịch sử.
    // - CSS dùng class is-history-collapsed trên layout.
    // =====================================================

    function setHistoryCollapsed(collapsed) {
        if (!chatbotLayout || !historyPanel || !historyToggle) {
            return;
        }

        const isCollapsed = Boolean(collapsed);
        const label = isCollapsed
            ? "Hiện lịch sử trò chuyện"
            : "Ẩn lịch sử trò chuyện";

        chatbotLayout.classList.toggle(
            "is-history-collapsed",
            isCollapsed
        );

        historyToggle.setAttribute(
            "aria-expanded",
            String(!isCollapsed)
        );

        historyToggle.setAttribute("aria-label", label);
        historyToggle.title = label;
        historyPanel.setAttribute(
            "aria-hidden",
            String(isCollapsed)
        );

        if (historyToggleText) {
            historyToggleText.textContent = isCollapsed
                ? "Hiện lịch sử"
                : "Ẩn lịch sử";
        }
    }

    if (chatbotLayout && historyPanel && historyToggle) {
        setHistoryCollapsed(false);

        historyToggle.addEventListener("click", function () {
            const isCollapsed = chatbotLayout.classList.contains(
                "is-history-collapsed"
            );

            setHistoryCollapsed(!isCollapsed);
        });
    }


    // =====================================================
    // 04. ĐỌC CSRF TOKEN TỪ FLASK
    //
    // HTML Student đã có:
    // <input name="csrf_token" ...>
    // =====================================================

    function getCSRFToken() {
        const tokenInput = chatForm.querySelector(
            'input[name="csrf_token"]'
        );

        if (tokenInput && tokenInput.value) {
            return tokenInput.value;
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
    // 05. ĐỌC PHẢN HỒI JSON TỪ FLASK
    //
    // Kiểm tra:
    // - HTTP status
    // - Content-Type
    // - Thông báo lỗi từ backend
    // =====================================================

    async function readJSON(response) {
        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {
            throw new Error(
                "Máy chủ không trả về dữ liệu hợp lệ. " +
                "Bạn kiểm tra trạng thái đăng nhập nhé."
            );
        }

        let data;

        try {
            data = await response.json();
        } catch (error) {
            throw new Error(
                "Không đọc được dữ liệu phản hồi từ máy chủ."
            );
        }

        if (!response.ok) {
            throw new Error(
                data.error ||
                data.message ||
                "Không thể thực hiện yêu cầu."
            );
        }

        return data;
    }


    // =====================================================
    // 06. GỌI API DÙNG CHUNG
    //
    // Mặc định gửi cookie đăng nhập Flask.
    // =====================================================

    async function apiRequest(url, options = {}) {
        const headers = {
            Accept: "application/json",
            ...(options.headers || {})
        };

        const response = await fetch(url, {
            credentials: "same-origin",
            cache: "no-store",
            ...options,
            headers: headers
        });

        return readJSON(response);
    }


    // =====================================================
    // 07. XỬ LÝ NỘI DUNG THINK CỦA QWEN3
    //
    // Backend đã gửi think: false.
    // Đây chỉ là bước bảo vệ hiển thị dự phòng.
    // =====================================================

    function cleanAIContent(content) {
        let text = String(content || "");

        // Khối suy luận hoàn chỉnh.
        text = text.replace(
            /<think>[\s\S]*?<\/think>/gi,
            ""
        );

        // Khối suy luận chưa đóng.
        text = text.replace(
            /<think>[\s\S]*$/gi,
            ""
        );

        // Thẻ lẻ còn sót.
        text = text.replace(
            /<\/?think>/gi,
            ""
        );

        return text.trim();
    }


    // =====================================================
    // 08. HIỂN THỊ THÔNG BÁO TRẠNG THÁI
    //
    // Ví dụ:
    // - Đang tải lịch sử
    // - Không kết nối được Ollama
    // - Không lưu được tin nhắn
    // =====================================================

    function setStatus(message, isError = false) {
        if (!statusBox) {
            return;
        }

        statusBox.textContent = message || "";

        statusBox.style.color = isError
            ? "#ae5046"
            : "#8b765e";
    }


    // =====================================================
    // 09. CUỘN ĐẾN TIN NHẮN CUỐI
    // =====================================================

    function scrollToBottom() {
        messagesBox.scrollTop =
            messagesBox.scrollHeight;
    }


    // =====================================================
    // 10. TẠO MỘT BONG BÓNG TIN NHẮN
    //
    // Vai trò:
    // user      = người học
    // assistant = trợ lý AI
    //
    // Dùng textContent để không thực thi HTML
    // do người dùng hoặc AI gửi về.
    // =====================================================

    function createMessage(role, content) {
        const normalizedRole = (
            role === "user" ||
            role === "nguoi_dung"
        )
            ? "user"
            : "assistant";

        const message = document.createElement("div");

        message.className =
            "chatbot-message chatbot-message-" +
            normalizedRole;

        const bubble = document.createElement("div");

        bubble.className = "chatbot-message-bubble";

        bubble.textContent = (
            normalizedRole === "assistant"
                ? cleanAIContent(content)
                : String(content || "")
        );

        message.appendChild(bubble);

        messagesBox.appendChild(message);

        scrollToBottom();

        return message;
    }


    // =====================================================
    // 11. LỜI CHÀO BAN ĐẦU
    //
    // Đây chỉ là lời chào của giao diện.
    // Không tự ghi một tin nhắn mẫu vào SQL.
    // =====================================================

    function showWelcome() {
        messagesBox.replaceChildren();

        createMessage(
            "assistant",
            "Xin chào! Mình là trợ lý Mộc Hán.\n\n" +
            "Bạn có thể hỏi mình về từ vựng, " +
            "ngữ pháp, chữ Hán hoặc luyện " +
            "hội thoại tiếng Trung nhé!\n\n" +
            "Hôm nay bạn muốn học gì?"
        );
    }


    // =====================================================
    // 12. HIỆU ỨNG TRỢ LÝ ĐANG TRẢ LỜI
    //
    // Chỉ hiển thị trạng thái chờ.
    // Không hiển thị quá trình suy luận của AI.
    // =====================================================

    function showTyping() {
        const element = createMessage(
            "assistant",
            "Mộc Hán đang trả lời..."
        );

        element.classList.add(
            "chatbot-message-typing"
        );

        return element;
    }


    // =====================================================
    // 13. KHÓA / MỞ CÁC NÚT KHI GỬI
    // =====================================================

    function setSending(value) {
        isSending = Boolean(value);

        chatInput.disabled = isSending;

        sendButton.disabled = isSending;

        if (newChatButton) {
            newChatButton.disabled = isSending;
        }

        sendButton.textContent = isSending
            ? "Đang trả lời..."
            : "Gửi ➤";
    }


    // =====================================================
    // 14. HIỂN THỊ DANH SÁCH HỘI THOẠI
    //
    // API:
    // GET /chatbot/api/conversations
    //
    // Dữ liệu:
    // {
    //     conversations: [
    //         {id, title, created_at}
    //     ]
    // }
    // =====================================================

    function renderConversations(items) {
        conversationList.replaceChildren();

        if (!Array.isArray(items) || items.length === 0) {
            const empty = document.createElement("div");

            empty.className =
                "chatbot-conversations-empty";

            empty.textContent =
                "Chưa có cuộc trò chuyện nào.";

            conversationList.appendChild(empty);

            return;
        }

        items.forEach(function (item) {
            if (
                item.id === undefined ||
                item.id === null
            ) {
                return;
            }

            const button = document.createElement("button");

            button.type = "button";

            button.className =
                "chatbot-conversation-item";

            button.textContent =
                item.title || "Cuộc trò chuyện";

            button.title =
                item.title || "Cuộc trò chuyện";

            button.dataset.conversationId =
                String(item.id);

            const isCurrent = (
                conversationId !== null &&
                String(conversationId) === String(item.id)
            );

            if (isCurrent) {
                button.classList.add("active");
                button.setAttribute(
                    "aria-current",
                    "true"
                );
            }

            button.addEventListener(
                "click",
                function () {
                    openConversation(item.id);
                }
            );

            conversationList.appendChild(button);
        });
    }


    // =====================================================
    // 15. CẬP NHẬT HỘI THOẠI ĐANG ĐƯỢC CHỌN
    // =====================================================

    function highlightCurrentConversation() {
        const buttons =
            conversationList.querySelectorAll(
                ".chatbot-conversation-item"
            );

        buttons.forEach(function (button) {
            const selected = (
                conversationId !== null &&
                button.dataset.conversationId ===
                    String(conversationId)
            );

            button.classList.toggle(
                "active",
                selected
            );

            if (selected) {
                button.setAttribute(
                    "aria-current",
                    "true"
                );
            } else {
                button.removeAttribute(
                    "aria-current"
                );
            }
        });
    }


    // =====================================================
    // 16. TẢI LỊCH SỬ TỪ SQL SERVER
    //
    // API:
    // GET /chatbot/api/conversations
    //
    // Chỉ hiển thị hội thoại của người học
    // đang đăng nhập.
    // =====================================================

    async function loadConversations() {
        try {
            const data = await apiRequest(
                API.conversations
            );

            renderConversations(
                data.conversations || []
            );

            return true;

        } catch (error) {
            setStatus(
                "Không tải được lịch sử: " +
                error.message,
                true
            );

            return false;
        }
    }


    // =====================================================
    // 17. MỞ LẠI CUỘC TRÒ CHUYỆN CŨ
    //
    // API:
    // GET /chatbot/api/conversations/<id>
    //
    // Backend kiểm tra quyền sở hữu của
    // người học trước khi trả dữ liệu.
    // =====================================================

    async function openConversation(id) {
        if (isSending || isLoading) {
            return;
        }

        isLoading = true;

        const version = ++historyVersion;

        setStatus("Đang tải cuộc trò chuyện...");

        try {
            const data = await apiRequest(
                API.detail(id)
            );

            if (version !== historyVersion) {
                return;
            }

            conversationId = data.conversation_id ?? id;

            messagesBox.replaceChildren();

            const messages = Array.isArray(data.messages)
                ? data.messages
                : [];

            if (messages.length === 0) {
                showWelcome();
            } else {
                messages.forEach(function (message) {
                    createMessage(
                        message.role,
                        message.content
                    );
                });
            }

            highlightCurrentConversation();

            setStatus("");

            chatInput.focus();

        } catch (error) {
            setStatus(
                "Không mở được cuộc trò chuyện: " +
                error.message,
                true
            );

        } finally {
            isLoading = false;
        }
    }


    // =====================================================
    // 18. TẠO CUỘC TRÒ CHUYỆN MỚI
    //
    // Chưa cần INSERT SQL ngay.
    // Backend sẽ tạo CuocHoiThoai khi người học
    // gửi câu hỏi đầu tiên.
    // =====================================================

    function createNewConversation() {
        if (isSending || isLoading) {
            return;
        }

        historyVersion++;

        conversationId = null;

        chatInput.value = "";

        showWelcome();

        highlightCurrentConversation();

        setStatus("");

        chatInput.focus();
    }


    // =====================================================
    // 19. GẮN SỰ KIỆN TẠO HỘI THOẠI MỚI
    // =====================================================

    if (newChatButton) {
        newChatButton.addEventListener(
            "click",
            createNewConversation
        );
    }


    // =====================================================
    // 20. GỬI TIN NHẮN ĐẾN FLASK
    //
    // API:
    // POST /chatbot/api/chat
    //
    // JSON gửi lên:
    // {
    //     message: "...",
    //     conversation_id: null hoặc ID
    // }
    //
    // Backend sẽ:
    // - Tra học liệu SQL
    // - Gọi Qwen3 khi cần
    // - Lưu TinNhan
    // - Trả answer và conversation_id
    // =====================================================

    async function sendMessage() {
        if (isSending || isLoading) {
            return;
        }

        const question = chatInput.value.trim();

        if (!question) {
            chatInput.focus();
            return;
        }

        if (question.length > 2000) {
            setStatus(
                "Câu hỏi không được vượt quá 2000 ký tự.",
                true
            );

            return;
        }

        const originalConversationId = conversationId;

        const version = historyVersion;

        // Hiển thị câu hỏi trên giao diện.
        const userElement = createMessage(
            "user",
            question
        );

        chatInput.value = "";

        setStatus("");

        setSending(true);

        // Trạng thái đang xử lý.
        const typingElement = showTyping();

        try {
            const response = await apiRequest(
                API.send,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },

                    body: JSON.stringify({
                        message: question,

                        conversation_id:
                            originalConversationId
                    })
                }
            );

            if (version !== historyVersion) {
                return;
            }

            // Xóa trạng thái đang trả lời.
            typingElement.remove();

            const answer = cleanAIContent(
                response.answer || ""
            );

            if (!answer) {
                throw new Error(
                    "Chatbot chưa trả về câu trả lời."
                );
            }

            createMessage(
                "assistant",
                answer
            );

            // Quan trọng:
            // Dùng ID mới trả về từ SQL,
            // để câu hỏi tiếp theo nằm trong
            // cùng một cuộc trò chuyện.
            if (
                response.conversation_id !== undefined &&
                response.conversation_id !== null
            ) {
                conversationId =
                    response.conversation_id;
            }

            setStatus("");

            // Tải lại lịch sử để xuất hiện cuộc trò
            // chuyện vừa tạo hoặc vừa cập nhật.
            await loadConversations();

            highlightCurrentConversation();

        } catch (error) {
            typingElement.remove();

            setStatus(
                "Không gửi được tin nhắn: " +
                error.message,
                true
            );

            // Không tự gửi lại để tránh tạo
            // tin nhắn trùng trong SQL.
            //
            // Giữ câu hỏi trong ô nhập để
            // người học có thể kiểm tra rồi
            // quyết định gửi lại.
            if (!chatInput.value.trim()) {
                chatInput.value = question;
            }

            // Tin đã gửi thử sẽ được giữ lại
            // trên màn hình để người học biết
            // câu nào gặp lỗi.
            userElement.classList.add(
                "chatbot-message-failed"
            );

        } finally {
            setSending(false);

            chatInput.focus();
        }
    }


    // =====================================================
    // 21. GỬI TIN BẰNG FORM
    //
    // Chặn tải lại trang.
    // =====================================================

    chatForm.addEventListener(
        "submit",
        function (event) {
            event.preventDefault();

            sendMessage();
        }
    );


    // =====================================================
    // 22. PHÍM ENTER VÀ SHIFT + ENTER
    //
    // Enter:
    //     Gửi câu hỏi.
    //
    // Shift + Enter:
    //     Xuống dòng.
    //
    // Không gửi khi đang nhập bộ gõ IME.
    // =====================================================

    chatInput.addEventListener(
        "keydown",
        function (event) {
            if (
                event.key === "Enter" &&
                !event.shiftKey &&
                !event.isComposing &&
                event.keyCode !== 229
            ) {
                event.preventDefault();

                sendMessage();
            }
        }
    );


    // =====================================================
    // 23. KHỞI TẠO TRANG CHATBOT
    //
    // - Hiển thị lời chào
    // - Tải lịch sử từ SQL
    // - Chưa tạo cuộc trò chuyện mới trong SQL
    //   cho đến khi người học gửi câu đầu tiên.
    // =====================================================

    async function initializeChatbot() {
        showWelcome();

        setStatus("");

        await loadConversations();
    }

    initializeChatbot();
});
