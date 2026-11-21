
/* ============================================================
   MỘC HÁN - QUẢN LÝ GÓP Ý BÊN ADMIN

   File:
       static/js/admin-feedback.js

   HTML:
       templates/admin/feedback.html

   CSS:
       static/css/admin-feedback.css

   Python:
       routes/admin/feedback.py

   API:
       GET  /admin/gop-y/api/list
       POST /admin/gop-y/api/update/<feedback_id>

   Chức năng:
       1. Tải góp ý từ SQL Server.
       2. Hiển thị thống kê.
       3. Tìm kiếm góp ý.
       4. Lọc theo trạng thái.
       5. Phân trang.
       6. Cập nhật trạng thái.
       7. Gửi phản hồi cho người học.
       8. Hiển thị giờ Việt Nam.
       9. Bảo vệ CSRF khi gửi dữ liệu.

   Không sử dụng dữ liệu giả.
   Không sử dụng localStorage.
   Không can thiệp các chức năng Admin khác.
============================================================ */

(function () {
    "use strict";

    // ========================================================
    // 1. KHỞI TẠO
    // ========================================================

    function initializeAdminFeedback() {

        const page = document.getElementById(
            "adminFeedbackPage"
        );

        if (!page) {
            return;
        }

        // ----------------------------------------------------
        // API
        // ----------------------------------------------------

        const API_LIST_URL = page.dataset.listUrl;

        const API_UPDATE_TEMPLATE =
            page.dataset.updateUrlTemplate;

        // ----------------------------------------------------
        // CÁC THÀNH PHẦN GIAO DIỆN
        // ----------------------------------------------------

        const csrfInput = document.getElementById(
            "adminFeedbackCsrfToken"
        );

        const notice = document.getElementById(
            "adminFeedbackNotice"
        );

        const refreshButton = document.getElementById(
            "adminFeedbackRefreshButton"
        );

        const searchForm = document.getElementById(
            "adminFeedbackSearchForm"
        );

        const searchInput = document.getElementById(
            "adminFeedbackSearchInput"
        );

        const searchButton = document.getElementById(
            "adminFeedbackSearchButton"
        );

        const filters = Array.from(
            page.querySelectorAll(
                ".admin-feedback-filter"
            )
        );

        const listElement = document.getElementById(
            "adminFeedbackList"
        );

        const loadingElement = document.getElementById(
            "adminFeedbackLoading"
        );

        const errorElement = document.getElementById(
            "adminFeedbackError"
        );

        const emptyElement = document.getElementById(
            "adminFeedbackEmpty"
        );

        const emptyTitle = document.getElementById(
            "adminFeedbackEmptyTitle"
        );

        const emptyDescription = document.getElementById(
            "adminFeedbackEmptyDescription"
        );

        const resultCount = document.getElementById(
            "adminFeedbackResultCount"
        );

        const itemTemplate = document.getElementById(
            "adminFeedbackItemTemplate"
        );

        // ----------------------------------------------------
        // THỐNG KÊ
        // ----------------------------------------------------

        const totalCount = document.getElementById(
            "adminFeedbackTotalCount"
        );

        const newCount = document.getElementById(
            "adminFeedbackNewCount"
        );

        const processingCount = document.getElementById(
            "adminFeedbackProcessingCount"
        );

        const doneCount = document.getElementById(
            "adminFeedbackDoneCount"
        );

        // ----------------------------------------------------
        // PHÂN TRANG
        // ----------------------------------------------------

        const pagination = document.getElementById(
            "adminFeedbackPagination"
        );

        const prevButton = document.getElementById(
            "adminFeedbackPrevButton"
        );

        const nextButton = document.getElementById(
            "adminFeedbackNextButton"
        );

        const pageInfo = document.getElementById(
            "adminFeedbackPageInfo"
        );

        // ----------------------------------------------------
        // KIỂM TRA THÀNH PHẦN BẮT BUỘC
        // ----------------------------------------------------

        if (
            !API_LIST_URL ||
            !API_UPDATE_TEMPLATE ||
            !csrfInput ||
            !searchForm ||
            !searchInput ||
            !listElement ||
            !itemTemplate
        ) {

            console.error(
                "[Mộc Hán] Thiếu thành phần giao diện Admin Góp ý."
            );

            return;
        }

        // ====================================================
        // 2. CẤU HÌNH
        // ====================================================

        const MAX_REPLY_LENGTH = 4000;

        const STATUS_LABELS = {
            moi: "Chờ xử lý",
            dang_xu_ly: "Đang xử lý",
            da_xu_ly: "Đã xử lý"
        };

        let currentStatus = "all";
        let currentKeyword = "";
        let currentPage = 1;
        let totalPages = 1;

        let loadingRequestId = 0;
        let activeController = null;

        // ====================================================
        // 3. THÔNG BÁO CHUNG
        // ====================================================

        function showNotice(message, type = "success") {

            if (!notice) {
                return;
            }

            notice.textContent = message;

            notice.classList.remove(
                "is-success",
                "is-error"
            );

            notice.classList.add(
                type === "error"
                    ? "is-error"
                    : "is-success"
            );

            notice.setAttribute(
                "role",
                type === "error" ? "alert" : "status"
            );

            notice.hidden = false;
        }

        function hideNotice() {

            if (!notice) {
                return;
            }

            notice.hidden = true;
            notice.textContent = "";
        }

        // ====================================================
        // 4. THÔNG BÁO LỖI DANH SÁCH
        // ====================================================

        function showError(message) {

            if (!errorElement) {
                return;
            }

            errorElement.textContent = message;
            errorElement.hidden = false;
        }

        function hideError() {

            if (!errorElement) {
                return;
            }

            errorElement.hidden = true;
            errorElement.textContent = "";
        }

        // ====================================================
        // 5. ĐỊNH DẠNG SỐ
        // ====================================================

        function formatNumber(value) {

            return Number(
                value || 0
            ).toLocaleString("vi-VN");
        }

        // ====================================================
        // 6. ĐỊNH DẠNG NGÀY GIỜ VIỆT NAM
        //
        // Python trả về UTC ISO, ví dụ:
        //     2026-11-02T15:13:39Z
        //
        // Hiển thị:
        //     02/11/2026 22:13
        // ====================================================

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

        // ====================================================
        // 7. GỌI API JSON
        // ====================================================

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

            if (
                !contentType.includes(
                    "application/json"
                )
            ) {

                if (response.status === 401) {
                    throw new Error(
                        "Phiên đăng nhập đã hết hạn. " +
                        "Vui lòng đăng nhập lại."
                    );
                }

                if (response.status === 403) {
                    throw new Error(
                        "Bạn không có quyền thực hiện thao tác này " +
                        "hoặc mã CSRF đã hết hạn. " +
                        "Hãy tải lại trang và thử lại."
                    );
                }

                throw new Error(
                    "Máy chủ không trả về dữ liệu JSON hợp lệ."
                );
            }

            const data = await response.json();

            if (
                !response.ok ||
                data.success !== true
            ) {

                throw new Error(
                    data.message ||
                    "Yêu cầu không thành công."
                );
            }

            return data;
        }

        // ====================================================
        // 8. CẬP NHẬT 4 Ô THỐNG KÊ
        // ====================================================

        function renderSummary(summary) {

            if (!summary) {
                return;
            }

            if (totalCount) {
                totalCount.textContent = formatNumber(
                    summary.total
                );
            }

            if (newCount) {
                newCount.textContent = formatNumber(
                    summary.moi
                );
            }

            if (processingCount) {
                processingCount.textContent = formatNumber(
                    summary.dang_xu_ly
                );
            }

            if (doneCount) {
                doneCount.textContent = formatNumber(
                    summary.da_xu_ly
                );
            }
        }

        // ====================================================
        // 9. CẬP NHẬT NÚT LỌC
        // ====================================================

        function renderFilters() {

            filters.forEach(function (button) {

                const isActive =
                    button.dataset.status === currentStatus;

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

        // ====================================================
        // 10. HIỂN THỊ THÔNG BÁO TRONG TỪNG THẺ
        // ====================================================

        function showItemNotice(
            element,
            message,
            type = "success"
        ) {

            if (!element) {
                return;
            }

            element.textContent = message;

            element.classList.remove(
                "is-success",
                "is-error"
            );

            element.classList.add(
                type === "error"
                    ? "is-error"
                    : "is-success"
            );

            element.setAttribute(
                "role",
                type === "error" ? "alert" : "status"
            );

            element.hidden = false;
        }

        // ====================================================
        // 11. TẠO URL CẬP NHẬT
        //
        // HTML cung cấp:
        //     /admin/gop-y/api/update/0
        //
        // Thay ID 0 bằng mã góp ý thực tế.
        // ====================================================

        function getUpdateURL(feedbackId) {

            const id = Number(feedbackId);

            if (
                !Number.isSafeInteger(id) ||
                id <= 0
            ) {
                throw new Error(
                    "Mã góp ý không hợp lệ."
                );
            }

            const url = API_UPDATE_TEMPLATE.replace(
                /\/0\/?$/,
                "/" + String(id)
            );

            if (url === API_UPDATE_TEMPLATE) {
                throw new Error(
                    "Không thể tạo đường dẫn cập nhật góp ý."
                );
            }

            return url;
        }

        // ====================================================
        // 12. TẠO THẺ GÓP Ý
        //
        // Sử dụng textContent để hiển thị dữ liệu.
        // Không chèn trực tiếp HTML của người học.
        // ====================================================

        function createFeedbackCard(item) {

            const fragment = itemTemplate.content.cloneNode(
                true
            );

            const card = fragment.querySelector(
                ".admin-feedback-item"
            );

            const numberElement = fragment.querySelector(
                ".admin-feedback-item-number"
            );

            const dateElement = fragment.querySelector(
                ".admin-feedback-item-date"
            );

            const statusElement = fragment.querySelector(
                ".admin-feedback-status"
            );

            const avatarElement = fragment.querySelector(
                ".admin-feedback-avatar"
            );

            const studentName = fragment.querySelector(
                ".admin-feedback-student-name"
            );

            const studentUsername = fragment.querySelector(
                ".admin-feedback-student-username"
            );

            const studentEmail = fragment.querySelector(
                ".admin-feedback-student-email"
            );

            const contentElement = fragment.querySelector(
                ".admin-feedback-content"
            );

            const form = fragment.querySelector(
                ".admin-feedback-reply-form"
            );

            const statusSelect = fragment.querySelector(
                ".admin-feedback-status-select"
            );

            const replyInput = fragment.querySelector(
                ".admin-feedback-reply-input"
            );

            const replyCount = fragment.querySelector(
                ".admin-feedback-reply-count"
            );

            const itemNotice = fragment.querySelector(
                ".admin-feedback-item-notice"
            );

            const processedDate = fragment.querySelector(
                ".admin-feedback-processed-date"
            );

            const saveButton = fragment.querySelector(
                ".admin-feedback-save-button"
            );

            const saveText = fragment.querySelector(
                ".admin-feedback-save-text"
            );

            const feedbackId = Number(item.id);

            const status = Object.prototype.hasOwnProperty.call(
                STATUS_LABELS,
                item.status
            )
                ? item.status
                : "moi";

            const name = String(
                item.student_name || "Người học"
            ).trim();

            const username = String(
                item.username || ""
            ).trim();

            const email = String(
                item.email || ""
            ).trim();

            // ------------------------------------------------
            // MÃ GÓP Ý
            // ------------------------------------------------

            if (card) {
                card.dataset.feedbackId = String(
                    feedbackId
                );
            }

            if (numberElement) {
                numberElement.textContent =
                    `Góp ý #${feedbackId}`;
            }

            // ------------------------------------------------
            // NGÀY GỬI
            // ------------------------------------------------

            if (dateElement) {

                const dateLabel = formatDate(
                    item.created_at
                );

                dateElement.textContent = dateLabel
                    ? `Đã gửi: ${dateLabel}`
                    : "Chưa xác định ngày gửi";
            }

            // ------------------------------------------------
            // NHÃN TRẠNG THÁI
            // ------------------------------------------------

            if (statusElement) {

                statusElement.textContent =
                    STATUS_LABELS[status];

                statusElement.dataset.status = status;
            }

            // ------------------------------------------------
            // NGƯỜI GỬI
            // ------------------------------------------------

            if (avatarElement) {

                avatarElement.textContent =
                    name.charAt(0).toUpperCase() || "N";
            }

            if (studentName) {
                studentName.textContent = name;
            }

            if (studentUsername) {

                studentUsername.textContent = username
                    ? `@${username}`
                    : "";
            }

            if (studentEmail) {
                studentEmail.textContent = email;
            }

            // ------------------------------------------------
            // NỘI DUNG NGƯỜI HỌC
            // ------------------------------------------------

            if (contentElement) {

                contentElement.textContent = String(
                    item.content || ""
                );
            }

            // ------------------------------------------------
            // TRẠNG THÁI HIỆN TẠI
            // ------------------------------------------------

            if (statusSelect) {
                statusSelect.value = status;
            }

            // ------------------------------------------------
            // PHẢN HỒI HIỆN TẠI
            // ------------------------------------------------

            if (replyInput) {

                replyInput.value = String(
                    item.admin_reply || ""
                );
            }

            // ------------------------------------------------
            // NGÀY XỬ LÝ
            // ------------------------------------------------

            if (processedDate) {

                const resolved = formatDate(
                    item.resolved_at
                );

                processedDate.textContent = resolved
                    ? `Hoàn tất: ${resolved}`
                    : "";
            }

            // ------------------------------------------------
            // ĐẾM KÝ TỰ PHẢN HỒI
            // ------------------------------------------------

            function updateReplyCount() {

                if (
                    !replyInput ||
                    !replyCount
                ) {
                    return;
                }

                const length = replyInput.value.length;

                replyCount.textContent =
                    `${length} / ${MAX_REPLY_LENGTH}`;

                replyCount.classList.toggle(
                    "is-limit",
                    length >= MAX_REPLY_LENGTH
                );
            }

            if (replyInput) {

                replyInput.addEventListener(
                    "input",
                    updateReplyCount
                );

                updateReplyCount();
            }

            // ------------------------------------------------
            // XỬ LÝ NÚT LƯU
            // ------------------------------------------------

            if (form) {

                form.addEventListener(
                    "submit",
                    async function (event) {

                        event.preventDefault();

                        if (
                            !statusSelect ||
                            !replyInput ||
                            !saveButton
                        ) {
                            return;
                        }

                        if (saveButton.disabled) {
                            return;
                        }

                        const newStatus =
                            statusSelect.value;

                        const reply =
                            replyInput.value.trim();

                        // ------------------------------------
                        // KIỂM TRA TRẠNG THÁI
                        // ------------------------------------

                        if (
                            !Object.prototype.hasOwnProperty.call(
                                STATUS_LABELS,
                                newStatus
                            )
                        ) {

                            showItemNotice(
                                itemNotice,
                                "Trạng thái không hợp lệ.",
                                "error"
                            );

                            return;
                        }

                        // ------------------------------------
                        // KIỂM TRA PHẢN HỒI
                        // ------------------------------------

                        if (reply.length > MAX_REPLY_LENGTH) {

                            showItemNotice(
                                itemNotice,
                                "Phản hồi không được vượt quá 4000 ký tự.",
                                "error"
                            );

                            replyInput.focus();

                            return;
                        }

                        // ------------------------------------
                        // ĐÃ XỬ LÝ PHẢI CÓ PHẢN HỒI
                        // ------------------------------------

                        if (
                            newStatus === "da_xu_ly" &&
                            !reply
                        ) {

                            showItemNotice(
                                itemNotice,
                                "Bạn cần nhập phản hồi trước khi " +
                                "đánh dấu đã xử lý.",
                                "error"
                            );

                            replyInput.focus();

                            return;
                        }

                        // ------------------------------------
                        // CSRF
                        // ------------------------------------

                        const csrfToken = csrfInput.value;

                        if (!csrfToken) {

                            showItemNotice(
                                itemNotice,
                                "Không tìm thấy mã CSRF. " +
                                "Vui lòng tải lại trang.",
                                "error"
                            );

                            return;
                        }

                        // ------------------------------------
                        // KHÓA NÚT LƯU
                        // ------------------------------------

                        saveButton.disabled = true;

                        if (saveText) {
                            saveText.textContent =
                                "Đang lưu...";
                        }

                        if (itemNotice) {
                            itemNotice.hidden = true;
                        }

                        try {

                            const updateURL = getUpdateURL(
                                feedbackId
                            );

                            // --------------------------------
                            // GỬI API
                            // --------------------------------

                            const result = await fetchJSON(
                                updateURL,
                                {
                                    method: "POST",

                                    headers: {
                                        "Content-Type":
                                            "application/json",

                                        "Accept":
                                            "application/json",

                                        "X-CSRFToken":
                                            csrfToken
                                    },

                                    body: JSON.stringify({
                                        status: newStatus,
                                        reply: reply
                                    })
                                }
                            );

                            // --------------------------------
                            // CẬP NHẬT NHÃN NGAY SAU KHI LƯU
                            // --------------------------------

                            if (statusElement) {

                                statusElement.textContent =
                                    STATUS_LABELS[newStatus];

                                statusElement.dataset.status =
                                    newStatus;
                            }

                            if (processedDate) {

                                // Ngày hoàn tất thực tế sẽ
                                // được lấy lại từ SQL.
                                processedDate.textContent =
                                    newStatus === "da_xu_ly"
                                        ? "Đã hoàn tất xử lý"
                                        : "";
                            }

                            showItemNotice(
                                itemNotice,
                                result.message ||
                                "Đã lưu xử lý thành công.",
                                "success"
                            );

                            // --------------------------------
                            // THÔNG BÁO CHUNG
                            // --------------------------------

                            showNotice(
                                `Đã cập nhật góp ý #${feedbackId}.`,
                                "success"
                            );

                            // --------------------------------
                            // TẢI LẠI DỮ LIỆU SQL
                            //
                            // Đồng bộ:
                            //     - Thống kê
                            //     - Danh sách
                            //     - Trạng thái
                            //     - Ngày hoàn tất
                            // --------------------------------

                            await loadFeedback();

                        } catch (error) {

                            console.error(
                                "[Mộc Hán] Lỗi cập nhật góp ý:",
                                error
                            );

                            showItemNotice(
                                itemNotice,
                                error.message ||
                                "Không thể cập nhật góp ý.",
                                "error"
                            );

                        } finally {

                            saveButton.disabled = false;

                            if (saveText) {
                                saveText.textContent =
                                    "Lưu xử lý";
                            }
                        }
                    }
                );
            }

            return fragment;
        }

        // ====================================================
        // 13. HIỂN THỊ DANH SÁCH
        // ====================================================

        function renderItems(items) {

            listElement.replaceChildren();

            if (!Array.isArray(items)) {
                items = [];
            }

            // ------------------------------------------------
            // KHÔNG CÓ GÓP Ý
            // ------------------------------------------------

            if (items.length === 0) {

                if (emptyElement) {
                    emptyElement.hidden = false;
                }

                if (emptyTitle) {

                    emptyTitle.textContent =
                        currentKeyword ||
                        currentStatus !== "all"
                            ? "Không tìm thấy góp ý phù hợp"
                            : "Chưa có góp ý nào";
                }

                if (emptyDescription) {

                    emptyDescription.textContent =
                        currentKeyword ||
                        currentStatus !== "all"
                            ? "Bạn có thể thay đổi từ khóa " +
                              "hoặc chọn trạng thái khác."
                            : "Khi người học gửi góp ý, " +
                              "nội dung sẽ xuất hiện tại đây.";
                }

                return;
            }

            if (emptyElement) {
                emptyElement.hidden = true;
            }

            // ------------------------------------------------
            // TẠO THẺ
            // ------------------------------------------------

            const fragment =
                document.createDocumentFragment();

            items.forEach(function (item) {

                fragment.appendChild(
                    createFeedbackCard(item)
                );
            });

            listElement.appendChild(fragment);
        }

        // ====================================================
        // 14. PHÂN TRANG
        // ====================================================

        function renderPagination(data) {

            currentPage = Number(
                data.page || 1
            );

            totalPages = Math.max(
                1,
                Number(data.total_pages || 1)
            );

            if (pageInfo) {

                pageInfo.textContent =
                    `Trang ${currentPage} / ${totalPages}`;
            }

            if (prevButton) {

                prevButton.disabled =
                    currentPage <= 1;
            }

            if (nextButton) {

                nextButton.disabled =
                    currentPage >= totalPages;
            }

            if (pagination) {

                pagination.hidden =
                    totalPages <= 1;
            }
        }

        // ====================================================
        // 15. TẠO URL DANH SÁCH
        // ====================================================

        function buildListURL() {

            const url = new URL(
                API_LIST_URL,
                window.location.origin
            );

            url.searchParams.set(
                "status",
                currentStatus
            );

            url.searchParams.set(
                "q",
                currentKeyword
            );

            url.searchParams.set(
                "page",
                String(currentPage)
            );

            return url.toString();
        }

        // ====================================================
        // 16. TẢI GÓP Ý TỪ SQL SERVER
        // ====================================================

        async function loadFeedback() {

            const requestId = ++loadingRequestId;

            // Hủy yêu cầu cũ nếu người dùng đổi bộ lọc
            // khi dữ liệu vẫn đang tải.
            if (activeController) {
                activeController.abort();
            }

            const controller = new AbortController();
            activeController = controller;

            if (loadingElement) {
                loadingElement.hidden = false;
            }

            if (emptyElement) {
                emptyElement.hidden = true;
            }

            if (refreshButton) {
                refreshButton.disabled = true;
            }

            if (searchButton) {
                searchButton.disabled = true;
            }

            hideError();

            try {

                const data = await fetchJSON(
                    buildListURL(),
                    {
                        method: "GET",

                        headers: {
                            "Accept": "application/json"
                        },

                        cache: "no-store",

                        signal: controller.signal
                    }
                );

                // Bỏ qua kết quả của request cũ.
                if (requestId !== loadingRequestId) {
                    return;
                }

                // --------------------------------------------
                // THỐNG KÊ
                // --------------------------------------------

                renderSummary(data.summary);

                // --------------------------------------------
                // SỐ KẾT QUẢ
                // --------------------------------------------

                if (resultCount) {

                    resultCount.textContent =
                        `${formatNumber(data.total)} kết quả`;
                }

                // --------------------------------------------
                // DANH SÁCH
                // --------------------------------------------

                renderItems(data.items);

                // --------------------------------------------
                // PHÂN TRANG
                // --------------------------------------------

                renderPagination(data);

            } catch (error) {

                if (
                    error.name === "AbortError" ||
                    requestId !== loadingRequestId
                ) {
                    return;
                }

                console.error(
                    "[Mộc Hán] Không tải được góp ý:",
                    error
                );

                showError(
                    error.message ||
                    "Không thể tải danh sách góp ý."
                );

            } finally {

                if (requestId === loadingRequestId) {

                    if (loadingElement) {
                        loadingElement.hidden = true;
                    }

                    if (refreshButton) {
                        refreshButton.disabled = false;
                    }

                    if (searchButton) {
                        searchButton.disabled = false;
                    }

                    activeController = null;
                }
            }
        }

        // ====================================================
        // 17. TÌM KIẾM
        // ====================================================

        searchForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();

                currentKeyword = searchInput.value.trim();

                currentPage = 1;

                hideNotice();

                loadFeedback();
            }
        );

        // ====================================================
        // 18. LỌC TRẠNG THÁI
        // ====================================================

        filters.forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    const selected =
                        button.dataset.status;

                    if (
                        selected !== "all" &&
                        !Object.prototype.hasOwnProperty.call(
                            STATUS_LABELS,
                            selected
                        )
                    ) {
                        return;
                    }

                    currentStatus = selected;
                    currentPage = 1;

                    hideNotice();

                    renderFilters();
                    loadFeedback();
                }
            );
        });

        // ====================================================
        // 19. NÚT LÀM MỚI
        // ====================================================

        if (refreshButton) {

            refreshButton.addEventListener(
                "click",
                function () {

                    hideNotice();
                    loadFeedback();
                }
            );
        }

        // ====================================================
        // 20. TRANG TRƯỚC
        // ====================================================

        if (prevButton) {

            prevButton.addEventListener(
                "click",
                function () {

                    if (currentPage <= 1) {
                        return;
                    }

                    currentPage -= 1;

                    loadFeedback();
                }
            );
        }

        // ====================================================
        // 21. TRANG SAU
        // ====================================================

        if (nextButton) {

            nextButton.addEventListener(
                "click",
                function () {

                    if (currentPage >= totalPages) {
                        return;
                    }

                    currentPage += 1;

                    loadFeedback();
                }
            );
        }

        // ====================================================
        // 22. KHỞI TẠO TRANG
        // ====================================================

        renderFilters();
        loadFeedback();

    }

    // ========================================================
    // 23. CHẠY KHI HTML ĐÃ SẴN SÀNG
    // ========================================================

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            initializeAdminFeedback
        );

    } else {

        initializeAdminFeedback();
    }

})();
