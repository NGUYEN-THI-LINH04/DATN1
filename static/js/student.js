
document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       1. SIDEBAR SUBMENU
       NEN TANG + CA NHAN HOA
    ====================================================== */

    const toggleButtons = document.querySelectorAll(
        "[data-sidebar-toggle]"
    );


    function setSubmenuState(name, open) {

        const button = document.querySelector(
            '[data-sidebar-toggle="' + name + '"]'
        );

        const submenu = document.getElementById(
            "sidebar-" + name
        );

        if (!button || !submenu) {
            return;
        }

        // Cap nhat trang thai nut
        button.classList.toggle("open", open);

        button.setAttribute(
            "aria-expanded",
            String(open)
        );

        // Hien / an submenu theo CSS cu
        submenu.classList.toggle("show", open);

        // =================================================
        // RIENG MENU CA NHAN HOA
        // =================================================

        if (name === "personal") {

            submenu.hidden = !open;

            if (open) {

                // Lay vi tri cua nut Ca nhan hoa
                const buttonRect =
                    button.getBoundingClientRect();

                // Menu phai hien thi truoc
                // moi do duoc chieu cao thuc te
                const menuHeight =
                    submenu.getBoundingClientRect().height;

                // Can ngang voi nut Ca nhan hoa
                let top = buttonRect.top;

                // Giu menu khong tran khoi man hinh
                const maxTop = Math.max(
                    10,
                    window.innerHeight - menuHeight - 10
                );

                top = Math.max(
                    10,
                    Math.min(top, maxTop)
                );

                // Ghi de top co dinh trong student.css
                submenu.style.top = top + "px";

            } else {

                // Xoa vi tri khi dong menu
                submenu.style.removeProperty("top");

            }

        }

    }


    /* =====================================================
       DONG TAT CA SUBMENU
    ====================================================== */

    function closeAllSubmenus(exceptName = null) {

        toggleButtons.forEach(function (button) {

            const name =
                button.dataset.sidebarToggle;

            if (name !== exceptName) {

                setSubmenuState(name, false);

            }

        });

    }


    /* =====================================================
       KHOI TAO MENU
    ====================================================== */

    toggleButtons.forEach(function (button) {

        const name =
            button.dataset.sidebarToggle;

        const submenu = document.getElementById(
            "sidebar-" + name
        );

        if (!submenu) {
            return;
        }

        // Tu dong mo Ca nhan hoa neu dang o trang
        // On tap tu vung hoac Tien do hoc
        const initiallyOpen =
            button.getAttribute("aria-expanded") === "true";

        setSubmenuState(name, initiallyOpen);


        // Click de mo / dong menu
        button.addEventListener("click", function (event) {

            event.stopPropagation();

            const willOpen =
                !submenu.classList.contains("show");

            // Mo nhom nay thi dong nhom khac
            closeAllSubmenus();

            setSubmenuState(name, willOpen);

        });

    });


    /* =====================================================
       CLICK RA NGOAI SIDEBAR
    ====================================================== */

    document.addEventListener("click", function (event) {

        const clickedInsideSidebar =
            event.target.closest(".student-sidebar");

        if (!clickedInsideSidebar) {

            closeAllSubmenus();

        }

    });


    /* =====================================================
       CAP NHAT VI TRI CA NHAN HOA KHI CUON
       HOAC THAY DOI KICH THUOC MAN HINH
    ====================================================== */

    function updatePersonalPosition() {

        const button = document.querySelector(
            '[data-sidebar-toggle="personal"]'
        );

        const submenu = document.getElementById(
            "sidebar-personal"
        );

        if (!button || !submenu) {
            return;
        }

        if (!submenu.classList.contains("show")) {
            return;
        }

        const buttonRect =
            button.getBoundingClientRect();

        const menuHeight =
            submenu.getBoundingClientRect().height;

        let top = buttonRect.top;

        const maxTop = Math.max(
            10,
            window.innerHeight - menuHeight - 10
        );

        top = Math.max(
            10,
            Math.min(top, maxTop)
        );

        submenu.style.top = top + "px";

    }


    window.addEventListener(
        "resize",
        updatePersonalPosition
    );


    document.addEventListener(
        "scroll",
        updatePersonalPosition,
        true
    );


    /* =====================================================
       2. MOBILE SIDEBAR
       GIU NGUYEN CHUC NANG CU
    ====================================================== */

    const sidebar = document.getElementById(
        "studentSidebar"
    );

    const mobileButton = document.getElementById(
        "mobileSidebarButton"
    );

    const overlay = document.getElementById(
        "sidebarOverlay"
    );


    function openMobileSidebar() {

        if (!sidebar || !overlay) {
            return;
        }

        sidebar.classList.add("mobile-open");

        overlay.classList.add("show");

        document.body.style.overflow = "hidden";

    }


    function closeMobileSidebar() {

        if (!sidebar || !overlay) {
            return;
        }

        sidebar.classList.remove("mobile-open");

        overlay.classList.remove("show");

        document.body.style.overflow = "";

    }


    if (mobileButton) {

        mobileButton.addEventListener("click", function () {

            if (
                sidebar &&
                sidebar.classList.contains("mobile-open")
            ) {

                closeMobileSidebar();

            } else {

                openMobileSidebar();

            }

        });

    }


    if (overlay) {

        overlay.addEventListener("click", function () {

            closeMobileSidebar();

            closeAllSubmenus();

        });

    }


    window.addEventListener("resize", function () {

        if (window.innerWidth > 760) {

            closeMobileSidebar();

        }

    });


    /* =====================================================
       3. FLASH MESSAGE AUTO CLOSE
       GIU NGUYEN CHUC NANG CU
    ====================================================== */

    const flashMessages = document.querySelectorAll(
        ".flash-message"
    );


    flashMessages.forEach(function (message) {

        setTimeout(function () {

            if (document.body.contains(message)) {

                message.style.opacity = "0";

                message.style.transform =
                    "translateY(-5px)";

                message.style.transition =
                    "0.2s ease";


                setTimeout(function () {

                    message.remove();

                }, 220);

            }

        }, 4500);

    });


    /* =====================================================
       4. COURSE TABS
       GIU NGUYEN CHUC NANG CU
    ====================================================== */

    const skillTabs = document.querySelectorAll(
        ".course-skill-tab"
    );


    skillTabs.forEach(function (tab) {

        tab.addEventListener("click", function () {

            skillTabs.forEach(function (item) {

                item.classList.remove("active");

            });

            tab.classList.add("active");

        });

    });


    /* =====================================================
       5. THANH TIEN DO KHOA HOC
       GIU NGUYEN CHUC NANG CU
    ====================================================== */

    const courseProgressBox = document.querySelector(
        ".course-progress-box"
    );


    if (courseProgressBox) {

        const progressValue =
            courseProgressBox.querySelector(
                ".course-progress-value"
            );

        let progressPercent = Number(
            courseProgressBox.dataset.progress || 0
        );

        if (Number.isNaN(progressPercent)) {

            progressPercent = 0;

        }

        progressPercent = Math.max(
            0,
            Math.min(100, progressPercent)
        );

        if (progressValue) {

            progressValue.style.width =
                progressPercent + "%";

        }

    }


    /* =====================================================
       6. FLOATING CHAT
       GIU NGUYEN CHUC NANG CU
    ====================================================== */

    const chatButton = document.getElementById(
        "floatingChatButton"
    );


    if (chatButton) {

        chatButton.addEventListener("click", function () {

            console.log(
                "Chatbot UI sẽ được nối ở bước sau."
            );

        });

    }

});
