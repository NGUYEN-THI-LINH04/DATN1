
/* ==========================================================
   MỘC HÁN - GÓP Ý DÀNH CHO NGƯỜI HỌC

   File: static/js/feedback.js

   HTML:
       templates/student/feedback.html

   Python:
       routes/student/feedback.py

   API:
       GET  /student/feedback/api/list
       POST /student/feedback/api/send

   Chức năng:
       1. Gửi góp ý vào SQL Server.
       2. Hiển thị lịch sử góp ý.
       3. Lọc theo trạng thái.
       4. Hiển thị phản hồi của Admin.
       5. Đếm số ký tự nội dung.
       6. Chống gửi trùng do nhấn nhiều lần.

   Không dùng thư viện JavaScript bên ngoài.
========================================================== */

(function () {
    "use strict";

    // ======================================================
    // 1. KHỞI TẠO
    // ======================================================

    function initializeFeedback() {
        const page = document.getElementById("feedbackPage");

        if (!page) {
            return;
        }

        const API_LIST_URL = page.dataset.listUrl;
        const API_SEND_URL = page.dataset.sendUrl;

        const form = document.getElementById("feedbackForm");
        const contentInput = document.getElementById("feedbackContent");

        const csrfInput = document.getElementById(
            "feedbackCsrfToken"
        );

        const submitButton = document.getElementById(
            "feedbackSubmitButton"
        );

        const submitText = document.getElementById(
            "feedbackSubmitText"
        );

        const characterCount = document.getElementById(
            "feedbackCharacterCount"
        );

        const notice = document.getElementById(
            "feedbackNotice"
        );

        const refreshButton = document.getElementById(
            "feedbackRefreshButton"
        );

        const historyList = document.getElementById(
            "feedbackHistoryList"
        );

        const historyLoading = document.getElementById(
            "feedbackHistoryLoading"
        );

        const historyError = document.getElementById(
            "feedbackHistoryError"
        );

        const historyEmpty = document.getElementById(
            "feedbackHistoryEmpty"
        );

        const itemTemplate = document.getElementById(
            "feedbackItemTemplate"
        );

        const filterButtons = Array.from(
            page.querySelectorAll(
                ".feedback-filter-button"
            )
        );

        if (
            !API_LIST_URL ||
            !API_SEND_URL ||
            !form ||
            !contentInput ||
            !csrfInput ||
            !submitButton ||
            !submitText ||
            !historyList ||
            !itemTemplate
        ) {
            console.error(
                "[Mộc Hán] Thiếu thành phần giao diện Góp ý."
            );
            return;
        }

        // ==================================================
        // 2. BIẾN TRẠNG THÁI
        // ==================================================

        const MIN_LENGTH = 10;
        const MAX_LENGTH = 4000;

        const STATUS_LABELS = {
            moi: "Chờ xử lý",
            dang_xu_ly: "Đang xử lý",
            da_xu_ly: "Đã xử lý"
        };

        let feedbackItems = [];
        let activeFilter = "all";

        let isSending = false;
        let isLoading = false;

        // Tránh kết quả yêu cầu cũ ghi đè yêu cầu mới.
        let latestLoadId = 0;


        // ==================================================
        // 3. HÀM HIỂN THỊ THÔNG BÁO
        // ==================================================

        function showNotice(message, type = "success") {
            if (!notice) {
                return;
            }

            notice.textContent = message;

            notice.classList.remove(
                "success",
                "error",
                "is-success",
                "is-error"
            );

            if (type === "error") {
                notice.classList.add("is-error");
                notice.setAttribute("role", "alert");
            } else {
                notice.classList.add("is-success");
                notice.setAttribute("role", "status");
            }

            notice.hidden = false;
        }


        function hideNotice() {
            if (!notice) {
                return;
            }

            notice.hidden = true;
            notice.textContent = "";
        }


        function showHistoryError(message) {
            if (!historyError) {
                return;
            }

            historyError.textContent = message;
            historyError.hidden = false;
        }


        function hideHistoryError() {
            if (!historyError) {
                return;
            }

            historyError.hidden = true;
            historyError.textContent = "";
        }


        // ==================================================
        // 4. ĐẾM KÝ TỰ
        // ==================================================

        function updateCharacterCount() {
            const length = contentInput.value.length;

            if (!characterCount) {
                return;
            }

            characterCount.textContent =
                `${length} / ${MAX_LENGTH}`;

            characterCount.classList.toggle(
                "is-limit",
                length >= MAX_LENGTH
            );
        }


        // ==================================================
        // 5. ĐỊNH DẠNG NGÀY
        //
        // Backend trả về thời gian UTC dạng ISO.
        // Chuyển sang giờ Việt Nam khi hiển thị.
        // ==================================================

        function formatDate(value) {
            if (!value) {
                return "";
            }

            const date = new Date(value);

            if (Number.isNaN(date.getTime())) {
                return "";
            }

            try {
                return new Intl.DateTimeFormat(
                    "vi-VN",
                    {
                        timeZone: "Asia/Ho_Chi_Minh",
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: false
                    }
                ).format(date);
            } catch (error) {
                console.error(
                    "[Mộc Hán] Lỗi định dạng ngày:",
                    error
                );

                return date.toLocaleString("vi-VN");
            }
        }


        // ==================================================
        // 6. HÀM GỌI API
        // ==================================================

        async function fetchJSON(url, options = {}) {
            const response = await fetch(
                url,
                {
                    credentials: "same-origin",
                    ...options
                }
            );

            const contentType = (
                response.headers.get("content-type") || ""
            ).toLowerCase();

            if (!contentType.includes("application/json")) {
                if (response.status === 401) {
                    throw new Error(
                        "Phiên đăng nhập đã hết hạn. " +
                        "Bạn hãy đăng nhập lại."
                    );
                }

                if (response.status === 403) {
                    throw new Error(
                        "Bạn không có quyền thực hiện thao tác này."
                    );
                }

                throw new Error(
                    "Máy chủ không trả về dữ liệu hợp lệ."
                );
            }

            const data = await response.json();

            if (!response.ok || data.success !== true) {
                throw new Error(
                    data.message ||
                    "Yêu cầu không thành công. Vui lòng thử lại."
                );
            }

            return data;
        }


        // ==================================================
        // 7. TẠO THẺ GÓP Ý TỪ TEMPLATE
        //
        // Sử dụng textContent để tránh chèn HTML
        // không an toàn từ nội dung người dùng.
        // ==================================================

        function createFeedbackCard(item) {
            const fragment = itemTemplate.content.cloneNode(
                true
            );

            const card = fragment.querySelector(
                ".feedback-item"
            );

            const numberElement = fragment.querySelector(
                ".feedback-item-number"
            );

            const dateElement = fragment.querySelector(
                ".feedback-item-date"
            );

            const statusElement = fragment.querySelector(
                ".feedback-status"
            );

            const contentElement = fragment.querySelector(
                ".feedback-item-content"
            );

            const replySection = fragment.querySelector(
                ".feedback-admin-reply"
            );

            const replyContent = fragment.querySelector(
                ".feedback-admin-reply-content"
            );

            const resolvedDate = fragment.querySelector(
                ".feedback-resolved-date"
            );

            const pendingReply = fragment.querySelector(
                ".feedback-pending-reply"
            );

            const itemId = Number(item.id) || 0;

            const status = Object.prototype.hasOwnProperty.call(
                STATUS_LABELS,
                item.status
            )
                ? item.status
                : "moi";

            const adminReply = String(
                item.admin_reply || ""
            ).trim();

            if (card) {
                card.dataset.feedbackId = String(itemId);
                card.dataset.status = status;
            }

            if (numberElement) {
                numberElement.textContent =
                    `Góp ý #${itemId}`;
            }

            if (dateElement) {
                const dateLabel = formatDate(
                    item.created_at
                );

                dateElement.textContent = dateLabel
                    ? `Đã gửi: ${dateLabel}`
                    : "Ngày gửi chưa xác định";

                if (item.created_at) {
                    dateElement.dateTime = item.created_at;
                }
            }

            if (statusElement) {
                statusElement.textContent =
                    STATUS_LABELS[status];

                statusElement.dataset.status = status;
            }

            if (contentElement) {
                contentElement.textContent = String(
                    item.content || ""
                );
            }

            // ----------------------------------------------
            // ĐÃ CÓ PHẢN HỒI ADMIN
            // ----------------------------------------------

            if (adminReply) {
                if (replySection) {
                    replySection.hidden = false;
                }

                if (replyContent) {
                    replyContent.textContent = adminReply;
                }

                if (resolvedDate) {
                    const dateLabel = formatDate(
                        item.resolved_at
                    );

                    resolvedDate.textContent = dateLabel
                        ? `Ngày hoàn tất: ${dateLabel}`
                        : "";

                    if (item.resolved_at) {
                        resolvedDate.dateTime =
                            item.resolved_at;
                    }

                    resolvedDate.hidden = !dateLabel;
                }

                if (pendingReply) {
                    pendingReply.hidden = true;
                }

            } else {

                // ------------------------------------------
                // CHƯA CÓ PHẢN HỒI
                // ------------------------------------------

                if (replySection) {
                    replySection.hidden = true;
                }

                if (pendingReply) {
                    pendingReply.hidden = false;
                }
            }

            return fragment;
        }


        // ==================================================
        // 8. LỌC GÓP Ý
        // ==================================================

        function getFilteredItems() {
            if (activeFilter === "all") {
                return feedbackItems;
            }

            return feedbackItems.filter(
                function (item) {
                    return item.status === activeFilter;
                }
            );
        }


        function updateFilterButtons() {
            filterButtons.forEach(function (button) {
                const isActive =
                    button.dataset.status === activeFilter;

                button.classList.toggle(
                    "active",
                    isActive
                );

                button.setAttribute(
                    "aria-pressed",
                    isActive ? "true" : "false"
                );
            });
        }


        // ==================================================
        // 9. HIỂN THỊ LỊCH SỬ
        // ==================================================

        function renderHistory() {
            const filteredItems = getFilteredItems();

            historyList.replaceChildren();

            if (historyEmpty) {
                historyEmpty.hidden =
                    filteredItems.length > 0;

                const title = historyEmpty.querySelector("h3");
                const description = historyEmpty.querySelector("p");

                if (filteredItems.length === 0) {
                    if (feedbackItems.length === 0) {
                        if (title) {
                            title.textContent =
                                "Chưa có góp ý nào";
                        }

                        if (description) {
                            description.textContent =
                                "Những góp ý bạn gửi sẽ xuất hiện " +
                                "ở đây để bạn dễ dàng theo dõi.";
                        }

                    } else {
                        if (title) {
                            title.textContent =
                                "Không có góp ý phù hợp";
                        }

                        if (description) {
                            description.textContent =
                                "Chưa có góp ý nào ở trạng thái " +
                                "bạn đang chọn.";
                        }
                    }
                }
            }

            if (filteredItems.length === 0) {
                return;
            }

            const fragment = document.createDocumentFragment();

            filteredItems.forEach(function (item) {
                fragment.appendChild(
                    createFeedbackCard(item)
                );
            });

            historyList.appendChild(fragment);
        }


        // ==================================================
        // 10. TẢI LỊCH SỬ TỪ SQL SERVER
        // ==================================================

        async function loadHistory() {
            if (isLoading) {
                return;
            }

            isLoading = true;
            const currentLoadId = ++latestLoadId;

            if (refreshButton) {
                refreshButton.disabled = true;
            }

            if (historyLoading) {
                historyLoading.hidden = false;
            }

            if (historyEmpty) {
                historyEmpty.hidden = true;
            }

            hideHistoryError();

            try {
                const data = await fetchJSON(
                    API_LIST_URL,
                    {
                        method: "GET",
                        headers: {
                            "Accept": "application/json"
                        },
                        cache: "no-store"
                    }
                );

                if (currentLoadId !== latestLoadId) {
                    return;
                }

                feedbackItems = Array.isArray(data.items)
                    ? data.items
                    : [];

                renderHistory();

            } catch (error) {

                console.error(
                    "[Mộc Hán] Không tải được lịch sử góp ý:",
                    error
                );

                showHistoryError(
                    error.message ||
                    "Không thể tải lịch sử góp ý."
                );

                // Không hiển thị thông báo "chưa có"
                // nếu thực tế lỗi kết nối SQL Server.
                if (historyEmpty) {
                    historyEmpty.hidden = true;
                }

            } finally {

                isLoading = false;

                if (historyLoading) {
                    historyLoading.hidden = true;
                }

                if (refreshButton) {
                    refreshButton.disabled = false;
                }
            }
        }


        // ==================================================
        // 11. GỬI GÓP Ý
        // ==================================================

        async function sendFeedback(event) {
            event.preventDefault();

            if (isSending) {
                return;
            }

            const content = contentInput.value.trim();

            // ----------------------------------------------
            // KIỂM TRA NỘI DUNG
            // ----------------------------------------------

            if (content.length < MIN_LENGTH) {
                showNotice(
                    "Nội dung góp ý cần có ít nhất 10 ký tự.",
                    "error"
                );

                contentInput.focus();
                return;
            }

            if (content.length > MAX_LENGTH) {
                showNotice(
                    "Nội dung góp ý không được vượt quá " +
                    "4000 ký tự.",
                    "error"
                );

                contentInput.focus();
                return;
            }

            const csrfToken = csrfInput.value;

            if (!csrfToken) {
                showNotice(
                    "Không tìm thấy mã bảo vệ biểu mẫu. " +
                    "Vui lòng tải lại trang.",
                    "error"
                );

                return;
            }

            // ----------------------------------------------
            // KHÓA NÚT TRONG KHI GỬI
            // ----------------------------------------------

            isSending = true;

            submitButton.disabled = true;
            submitText.textContent = "Đang gửi...";

            hideNotice();

            try {
                const data = await fetchJSON(
                    API_SEND_URL,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "X-CSRFToken": csrfToken
                        },
                        body: JSON.stringify({
                            content: content
                        })
                    }
                );

                // ------------------------------------------
                // GỬI THÀNH CÔNG
                // ------------------------------------------

                contentInput.value = "";
                updateCharacterCount();

                showNotice(
                    data.message ||
                    "Gửi góp ý thành công!",
                    "success"
                );

                // Chuyển về bộ lọc "Tất cả" để nhìn thấy
                // góp ý vừa gửi, có trạng thái "moi".
                activeFilter = "all";

                updateFilterButtons();

                await loadHistory();

            } catch (error) {

                console.error(
                    "[Mộc Hán] Lỗi khi gửi góp ý:",
                    error
                );

                showNotice(
                    error.message ||
                    "Không thể gửi góp ý. Vui lòng thử lại.",
                    "error"
                );

            } finally {

                isSending = false;

                submitButton.disabled = false;
                submitText.textContent = "Gửi góp ý";
            }
        }


        // ==================================================
        // 12. SỰ KIỆN FORM
        // ==================================================

        form.addEventListener(
            "submit",
            sendFeedback
        );


        // ==================================================
        // 13. SỰ KIỆN NHẬP NỘI DUNG
        // ==================================================

        contentInput.addEventListener(
            "input",
            updateCharacterCount
        );


        // ==================================================
        // 14. SỰ KIỆN LỌC TRẠNG THÁI
        // ==================================================

        filterButtons.forEach(function (button) {
            button.addEventListener(
                "click",
                function () {
                    const selectedStatus =
                        button.dataset.status;

                    if (
                        selectedStatus !== "all" &&
                        !Object.prototype.hasOwnProperty.call(
                            STATUS_LABELS,
                            selectedStatus
                        )
                    ) {
                        return;
                    }

                    activeFilter = selectedStatus;

                    updateFilterButtons();

                    if (!isLoading) {
                        renderHistory();
                    }
                }
            );
        });


        // ==================================================
        // 15. NÚT LÀM MỚI
        // ==================================================

        if (refreshButton) {
            refreshButton.addEventListener(
                "click",
                function () {
                    loadHistory();
                }
            );
        }


        // ==================================================
        // 16. KHỞI TẠO GIAO DIỆN
        // ==================================================

        updateCharacterCount();
        updateFilterButtons();
        loadHistory();
    }


    // ======================================================
    // 17. CHẠY SAU KHI HTML TẢI XONG
    // ======================================================

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initializeFeedback
        );
    } else {
        initializeFeedback();
    }

})();
