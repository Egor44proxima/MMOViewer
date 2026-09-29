from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mmo_viewer.core.models import Diagnostic, Severity, ValidationResult
from mmo_viewer.core.profiles import ProfileStatus, detect_profile
from mmo_viewer.core.spec import DOCUMENT_FIELDS, HEADER_FIELDS
from mmo_viewer.core.validator import open_and_validate


class SummaryCard(QFrame):
    def __init__(self, title: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.setProperty("class", "summaryCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(2)
        self.value_label = QLabel(value)
        self.value_label.setProperty("class", "summaryValue")
        title_label = QLabel(title)
        title_label.setProperty("class", "summaryTitle")
        layout.addWidget(self.value_label)
        layout.addWidget(title_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MMO Viewer")
        self.resize(1280, 800)
        self.setAcceptDrops(True)
        self.result: ValidationResult | None = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)

        top = QHBoxLayout()
        title_box = QVBoxLayout()
        app_title = QLabel("MMO Viewer")
        app_title.setProperty("class", "appTitle")
        self.file_label = QLabel("Файл не відкрито")
        self.file_label.setProperty("class", "muted")
        title_box.addWidget(app_title)
        title_box.addWidget(self.file_label)
        top.addLayout(title_box)
        top.addStretch(1)
        open_btn = QPushButton("Відкрити MMO")
        open_btn.setProperty("variant", "primary")
        open_btn.clicked.connect(self.open_dialog)
        top.addWidget(open_btn)
        root.addLayout(top)

        cards = QHBoxLayout()
        self.card_status = SummaryCard("Статус")
        self.card_items = SummaryCard("Позицій")
        self.card_sum = SummaryCard("Сума з ПДВ")
        self.card_errors = SummaryCard("Помилок")
        self.card_warnings = SummaryCard("Попереджень")
        for card in (self.card_status, self.card_items, self.card_sum, self.card_errors, self.card_warnings):
            cards.addWidget(card)
        root.addLayout(cards)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        self.invoice_tab = self._build_invoice_tab()
        self.items_table = self._build_items_table()
        self.diag_table = self._build_diagnostics_table()
        self.raw_view = QPlainTextEdit()
        self.raw_view.setReadOnly(True)
        self.raw_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.raw_view.setProperty("class", "rawView")

        self.tabs.addTab(self.invoice_tab, "Накладна")
        self.tabs.addTab(self.items_table, "Товари")
        self.tabs.addTab(self.diag_table, "Діагностика")
        self.tabs.addTab(self.raw_view, "RAW")

        self._show_empty_state()

    def _build_invoice_tab(self) -> QWidget:
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 10, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.invoice_form = QFormLayout(content)
        self.invoice_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.invoice_form.setHorizontalSpacing(18)
        self.invoice_form.setVerticalSpacing(8)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        return container

    def _build_items_table(self) -> QTableWidget:
        table = QTableWidget(0, 9)
        table.setHorizontalHeaderLabels(["№", "Статус", "Morion ID", "УКТ ЗЕД", "Товар", "Од.", "К-сть", "Ціна", "Сума"])
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        for i in range(3, 4):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(5, 9):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        return table

    def _build_diagnostics_table(self) -> QTableWidget:
        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels(["Рівень", "Код", "Рядок", "Позиція", "Поле", "Значення", "Опис"])
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        return table

    def _show_empty_state(self) -> None:
        self.card_status.set_value("—")
        self.card_items.set_value("0")
        self.card_sum.set_value("—")
        self.card_errors.set_value("0")
        self.card_warnings.set_value("0")
        self._clear_form()
        label = QLabel("Перетягніть файл .MMO у вікно або натисніть «Відкрити MMO»")
        label.setProperty("class", "emptyState")
        self.invoice_form.addRow(label)

    def _clear_form(self) -> None:
        while self.invoice_form.rowCount():
            self.invoice_form.removeRow(0)

    def open_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Відкрити MMO", "", "MMO files (*.mmo);;All files (*.*)")
        if path:
            self.load_file(Path(path))

    def dragEnterEvent(self, event) -> None:
        urls = event.mimeData().urls()
        if urls and urls[0].toLocalFile().lower().endswith(".mmo"):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        urls = event.mimeData().urls()
        if urls:
            self.load_file(Path(urls[0].toLocalFile()))
            event.acceptProposedAction()

    def load_file(self, path: Path) -> None:
        try:
            self.result = open_and_validate(path)
        except Exception as exc:
            QMessageBox.critical(self, "Не вдалося відкрити MMO", str(exc))
            return
        self.file_label.setText(str(path))
        self._render_result(self.result)

    def _render_result(self, result: ValidationResult) -> None:
        mmo = result.mmo
        self.card_status.set_value(result.status)
        self.card_items.set_value(str(mmo.item_count))
        self.card_errors.set_value(str(len(result.errors)))
        self.card_warnings.set_value(str(len(result.warnings)))

        total = "—"
        if mmo.document and len(mmo.document.fields) >= 13:
            total = mmo.document.fields[12] or "—"
        self.card_sum.set_value(total)

        self._render_invoice(result)
        self._render_items(result)
        self._render_diagnostics(result)
        self._render_raw(result)

    def _field_diagnostics(self, section: str, field_index: int, item_index: int | None = None) -> list[Diagnostic]:
        if not self.result:
            return []
        return [d for d in self.result.diagnostics
                if d.section == section and d.field_index == field_index and d.item_index == item_index]

    def _value_label(self, value: str, diagnostics: list[Diagnostic]) -> QLabel:
        label = QLabel(value if value else "—")
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        if diagnostics:
            severity = max(d.severity for d in diagnostics)
            label.setProperty("severity", "error" if severity == Severity.ERROR else "warning")
            label.setToolTip("\n".join(d.message for d in diagnostics))
        return label

    def _render_invoice(self, result: ValidationResult) -> None:
        self._clear_form()
        mmo = result.mmo

        section = QLabel("Заголовок")
        section.setProperty("class", "sectionTitle")
        self.invoice_form.addRow(section)
        if mmo.header:
            for idx, spec in enumerate(HEADER_FIELDS, start=1):
                value = mmo.header.fields[idx - 1] if idx <= len(mmo.header.fields) else ""
                self.invoice_form.addRow(spec.name + ":", self._value_label(value, self._field_diagnostics("HEADER", idx)))

        section = QLabel("Реквізити документа")
        section.setProperty("class", "sectionTitle")
        self.invoice_form.addRow(section)
        if mmo.document:
            for idx, spec in enumerate(DOCUMENT_FIELDS, start=1):
                value = mmo.document.fields[idx - 1] if idx <= len(mmo.document.fields) else ""
                self.invoice_form.addRow(spec.name + ":", self._value_label(value, self._field_diagnostics("DOCUMENT", idx)))

        section = QLabel("Коментар")
        section.setProperty("class", "sectionTitle")
        self.invoice_form.addRow(section)
        comment = mmo.comment.fields[0] if mmo.comment and mmo.comment.fields else ""
        self.invoice_form.addRow("Коментар:", self._value_label(comment, self._field_diagnostics("COMMENT", 1)))

    def _item_status(self, item_index: int) -> tuple[str, Severity | None, str]:
        assert self.result is not None
        ds = [d for d in self.result.diagnostics if d.item_index == item_index]
        if not ds:
            return "OK", None, ""
        sev = max(d.severity for d in ds)
        if sev == Severity.ERROR:
            return "ERROR", sev, "\n".join(d.message for d in ds if d.severity == Severity.ERROR)
        return "WARNING", sev, "\n".join(d.message for d in ds)

    def _render_items(self, result: ValidationResult) -> None:
        self.items_table.setRowCount(len(result.mmo.items))
        profile_match = detect_profile(result.mmo)
        semantic_layout_supported = profile_match.status != ProfileStatus.UNSUPPORTED
        uktzed_index = (
            profile_match.profile.uktzed_field_index
            if profile_match.profile is not None
            else None
        )
        for row, item in enumerate(result.mmo.items):
            f = item.fields
            status, severity, tooltip = self._item_status(row + 1)

            morion = f[4] if semantic_layout_supported and len(f) > 4 else "—"
            uktzed = (
                f[uktzed_index - 1]
                if uktzed_index and len(f) >= uktzed_index
                else "—"
            )

            values = [
                str(row + 1),
                status,
                morion,
                uktzed,
                f[1] if len(f) > 1 else "",
                f[14] if len(f) > 14 else "",
                f[15] if len(f) > 15 else "",
                f[19] if len(f) > 19 else "",
                f[20] if len(f) > 20 else "",
            ]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if tooltip:
                    cell.setToolTip(tooltip)
                if col == 1:
                    if severity == Severity.ERROR:
                        cell.setForeground(QColor("#b42318"))
                    elif severity == Severity.WARNING:
                        cell.setForeground(QColor("#b54708"))
                    else:
                        cell.setForeground(QColor("#067647"))
                self.items_table.setItem(row, col, cell)

    def _render_diagnostics(self, result: ValidationResult) -> None:
        self.diag_table.setRowCount(len(result.diagnostics))
        for row, d in enumerate(result.diagnostics):
            values = [
                d.severity.label,
                d.code,
                str(d.line or ""),
                str(d.item_index or ""),
                f"{d.field_index or ''} {d.field_name}".strip(),
                d.value,
                d.message,
            ]
            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                if col == 0:
                    if d.severity == Severity.ERROR:
                        cell.setForeground(QColor("#b42318"))
                    elif d.severity == Severity.WARNING:
                        cell.setForeground(QColor("#b54708"))
                    else:
                        cell.setForeground(QColor("#175cd3"))
                self.diag_table.setItem(row, col, cell)

    def _render_raw(self, result: ValidationResult) -> None:
        lines: list[str] = []
        mmo = result.mmo
        lines.append(f"FILE: {mmo.path}")
        lines.append(f"ENCODING: {mmo.encoding}    EOL: {mmo.eol}    BOM: {mmo.bom}")
        lines.append("")

        physical = mmo.text.splitlines()
        for line_no, raw in enumerate(physical, start=1):
            lines.append(f"L{line_no:04d}  {raw}")
            if line_no != 3:  # comment is intentionally a single field
                for field_no, value in enumerate(raw.split("\t"), start=1):
                    lines.append(f"        [{field_no:02d}] {value!r}")
        self.raw_view.setPlainText("\n".join(lines))
