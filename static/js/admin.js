"use strict";

document.querySelectorAll("[data-admin-table]").forEach(function (section) {
    const tableBody = section.querySelector("tbody");
    const search = section.querySelector("[data-table-search]");
    const status = section.querySelector("[data-table-status]");
    const dialog = section.querySelector("[data-editor]");
    const form = section.querySelector("[data-editor-form]");
    const fields = section.querySelector("[data-editor-fields]");

    const columns = Array.from(
        section.querySelectorAll("[data-column]")
    ).map(function (cell) {
        return cell.textContent.trim();
    });

    let editingRow = null;

    function normalize(text) {
        return text.toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/đ/g, "d");
    }

    function filterRows() {
        const query = normalize(search.value.trim());
        let count = 0;

        tableBody.querySelectorAll("tr").forEach(function (row) {
            const text = Array.from(
                row.querySelectorAll("[data-value]")
            ).map(cell => cell.textContent).join(" ");

            const visible = normalize(text).includes(query);
            row.hidden = !visible;

            if (visible) count++;
        });

        status.textContent = "Hiển thị " + count + " bản ghi mẫu.";
    }

    function actionButton(text, attribute) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "small-button";
        button.textContent = text;
        button.setAttribute(attribute, "");
        return button;
    }

    function createRow(values) {
        const row = document.createElement("tr");

        values.forEach(function (value) {
            const cell = document.createElement("td");
            cell.setAttribute("data-value", "");
            cell.textContent = value;
            row.append(cell);
        });

        const actions = document.createElement("td");
        actions.append(
            actionButton("Sửa", "data-edit"),
            actionButton("Xóa", "data-delete")
        );

        row.append(actions);
        return row;
    }

    function openEditor(row) {
        editingRow = row;
        fields.replaceChildren();

        const values = row
            ? Array.from(row.querySelectorAll("[data-value]"))
                .map(cell => cell.textContent)
            : [];

        section.querySelector("[data-editor-title]").textContent =
            row ? "Sửa bản ghi mẫu" : "Thêm bản ghi mẫu";

        columns.forEach(function (column, index) {
            const label = document.createElement("label");
            label.className = "field";
            label.textContent = column;

            const input = document.createElement("input");
            input.name = "field_" + index;
            input.value = values[index] || "";
            input.required = index === 0;
            input.maxLength = 2000;

            label.append(input);
            fields.append(label);
        });

        dialog.showModal();
    }

    section.querySelector("[data-table-add]").onclick = function () {
        openEditor(null);
    };

    section.querySelector("[data-editor-close]").onclick = function () {
        dialog.close();
    };

    tableBody.addEventListener("click", function (event) {
        const editButton = event.target.closest("[data-edit]");
        const deleteButton = event.target.closest("[data-delete]");

        if (editButton) {
            openEditor(editButton.closest("tr"));
        }

        if (deleteButton) {
            if (window.confirm("Xóa bản ghi mẫu này khỏi giao diện?")) {
                deleteButton.closest("tr").remove();
                filterRows();
            }
        }
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const data = new FormData(form);

        const values = columns.map(function (_, index) {
            return String(data.get("field_" + index) || "").trim();
        });

        const row = createRow(values);

        if (editingRow) {
            editingRow.replaceWith(row);
        } else {
            tableBody.append(row);
        }

        dialog.close();
        filterRows();
    });

    search.addEventListener("input", filterRows);
    filterRows();
});