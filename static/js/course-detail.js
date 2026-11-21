document.addEventListener(
    "DOMContentLoaded",
    function () {

        /* =====================================================
           ELEMENT
        ====================================================== */

        const openButton =
            document.getElementById(
                "openCourseReviewButton"
            );


        const modal =
            document.getElementById(
                "courseReviewModal"
            );


        const dialog =
            modal
                ? modal.querySelector(
                    ".course-review-dialog"
                )
                : null;


        const overlay =
            document.getElementById(
                "courseReviewOverlay"
            );


        const closeButton =
            document.getElementById(
                "closeCourseReviewButton"
            );


        const cancelButton =
            document.getElementById(
                "cancelCourseReviewButton"
            );


        const selectAllButton =
            document.getElementById(
                "courseReviewSelectAllButton"
            );


        const startButton =
            document.getElementById(
                "startCourseReviewButton"
            );


        const selectedText =
            document.getElementById(
                "courseReviewSelectedText"
            );


        const checkboxes =
            Array.from(
                document.querySelectorAll(
                    ".course-review-lesson-checkbox"
                )
            );


        if (
            !openButton
            ||
            !modal
            ||
            !dialog
        ) {

            return;

        }


        /* =====================================================
           MỞ POPUP
        ====================================================== */

        function openModal() {

            modal.classList.add(
                "show"
            );


            modal.setAttribute(
                "aria-hidden",
                "false"
            );


            document.body.classList.add(
                "review-modal-open"
            );


            updateSelection();

        }


        /* =====================================================
           ĐÓNG POPUP
        ====================================================== */

        function closeModal() {

            modal.classList.remove(
                "show"
            );


            modal.setAttribute(
                "aria-hidden",
                "true"
            );


            document.body.classList.remove(
                "review-modal-open"
            );

        }


        /* =====================================================
           CẬP NHẬT DANH SÁCH ĐÃ CHỌN
        ====================================================== */

        function updateSelection() {

            let selectedCount =
                0;


            let vocabularyCount =
                0;


            checkboxes.forEach(
                function (
                    checkbox
                ) {

                    const item =
                        checkbox.closest(
                            ".course-review-lesson-item"
                        );


                    if (
                        checkbox.checked
                    ) {

                        selectedCount++;


                        vocabularyCount +=
                            Number(
                                checkbox.dataset
                                    .vocabularyCount
                                || 0
                            );

                    }


                    if (
                        item
                    ) {

                        item.classList.toggle(
                            "selected",
                            checkbox.checked
                        );

                    }

                }
            );


            /* ---------------------------------------------
               Dòng: Đã chọn 1 / 23 bài
            --------------------------------------------- */

            if (
                selectedText
            ) {

                selectedText.textContent =
                    "Đã chọn "
                    + selectedCount
                    + " / "
                    + checkboxes.length
                    + " bài";

            }


            /* ---------------------------------------------
               Nút bắt đầu
            --------------------------------------------- */

            if (
                startButton
            ) {

                startButton.disabled =
                    selectedCount === 0;


                if (
                    selectedCount === 0
                ) {

                    startButton.textContent =
                        "▷ Chọn ít nhất 1 bài";

                }
                else {

                    startButton.textContent =
                        "▷ Bắt đầu ôn "
                        + selectedCount
                        + " bài · "
                        + vocabularyCount
                        + " từ";

                }

            }


            /* ---------------------------------------------
               Chọn tất cả / Bỏ chọn tất cả
            --------------------------------------------- */

            if (
                selectAllButton
            ) {

                if (
                    selectedCount
                    === checkboxes.length
                ) {

                    selectAllButton.textContent =
                        "Bỏ chọn tất cả";

                }
                else {

                    selectAllButton.textContent =
                        "Chọn tất cả";

                }

            }

        }


        /* =====================================================
           CLICK NÚT TỔNG ÔN
        ====================================================== */

        openButton.addEventListener(
            "click",
            openModal
        );


        /* =====================================================
           ĐÓNG
        ====================================================== */

        if (
            closeButton
        ) {

            closeButton.addEventListener(
                "click",
                closeModal
            );

        }


        if (
            cancelButton
        ) {

            cancelButton.addEventListener(
                "click",
                closeModal
            );

        }


        if (
            overlay
        ) {

            overlay.addEventListener(
                "click",
                closeModal
            );

        }


        /* =====================================================
           ESC ĐỂ ĐÓNG
        ====================================================== */

        document.addEventListener(
            "keydown",
            function (
                event
            ) {

                if (
                    event.key
                    === "Escape"

                    &&

                    modal.classList.contains(
                        "show"
                    )
                ) {

                    closeModal();

                }

            }
        );


        /* =====================================================
           CHECKBOX
        ====================================================== */

        checkboxes.forEach(
            function (
                checkbox
            ) {

                checkbox.addEventListener(
                    "change",
                    updateSelection
                );

            }
        );


        /* =====================================================
           CHỌN TẤT CẢ / BỎ TẤT CẢ
        ====================================================== */

        if (
            selectAllButton
        ) {

            selectAllButton.addEventListener(
                "click",
                function () {

                    const selectedCount =
                        checkboxes.filter(
                            function (
                                checkbox
                            ) {

                                return (
                                    checkbox.checked
                                );

                            }
                        ).length;


                    const shouldSelect =
                        selectedCount
                        !== checkboxes.length;


                    checkboxes.forEach(
                        function (
                            checkbox
                        ) {

                            checkbox.checked =
                                shouldSelect;

                        }
                    );


                    updateSelection();

                }
            );

        }


        /* =====================================================
           BẮT ĐẦU ÔN
        ====================================================== */

        if (
            startButton
        ) {

            startButton.addEventListener(
                "click",
                function () {

                    const selectedIds =
                        checkboxes

                            .filter(
                                function (
                                    checkbox
                                ) {

                                    return (
                                        checkbox.checked
                                    );

                                }
                            )

                            .map(
                                function (
                                    checkbox
                                ) {

                                    return (
                                        checkbox.value
                                    );

                                }
                            );


                    if (
                        selectedIds.length
                        === 0
                    ) {

                        return;

                    }


                    const courseId =
                        dialog.dataset.courseId;


                    const reviewUrl =
                        dialog.dataset.reviewUrl;


                    const params =
                        new URLSearchParams();


                    params.set(
                        "course_id",
                        courseId
                    );


                    params.set(
                        "lesson_ids",
                        selectedIds.join(
                            ","
                        )
                    );


                    window.location.href =
                        reviewUrl
                        + "?"
                        + params.toString();

                }
            );

        }


        /* =====================================================
           KHỞI TẠO
        ====================================================== */

        updateSelection();

    }
);