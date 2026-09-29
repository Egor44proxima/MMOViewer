from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from mmo_viewer.core.item_projection import (
    ItemViewColumn,
    item_column_value,
    split_item_view_columns,
)
from mmo_viewer.core.models import Severity, ValidationResult


ItemStatusProvider = Callable[[int], tuple[str, Severity | None, str]]


class ItemsWorkspace(QWidget):
    """Two-pane Items view with frozen operational columns and scrollable detail fields."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._syncing_selection = False
        self._detail_columns: tuple[ItemViewColumn, ...] = ()
        self._result: ValidationResult | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        self.operational_table = self._make_table()
        self.operational_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.operational_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.operational_table.setMinimumWidth(860)
        splitter.addWidget(self.operational_table)

        self.detail_table = self._make_table()
        self.detail_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.detail_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        splitter.addWidget(self.detail_table)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([900, 700])

        inspector = QFrame()
        inspector.setFrameShape(QFrame.Shape.StyledPanel)
        inspector_layout = QVBoxLayout(inspector)
        inspector_layout.setContentsMargins(10, 8, 10, 8)
        inspector_layout.setSpacing(5)

        self.inspector_title = QLabel("RAW Inspector")
        self.inspector_title.setProperty("class", "sectionTitle")
        inspector_layout.addWidget(self.inspector_title)

        self.inspector_meta = QLabel("Виберіть поле у правій таблиці")
        self.inspector_meta.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        inspector_layout.addWidget(self.inspector_meta)

        self.inspector_value = QPlainTextEdit()
        self.inspector_value.setReadOnly(True)
        self.inspector_value.setMaximumHeight(82)
        self.inspector_value.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        inspector_layout.addWidget(self.inspector_value)

        root.addWidget(inspector)

        self._wire_sync()

    def _make_table(self) -> QTableWidget:
        table = QTableWidget(0, 0)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        table.verticalHeader().setVisible(False)
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        return table

    def _wire_sync(self) -> None:
        left_bar = self.operational_table.verticalScrollBar()
        right_bar = self.detail_table.verticalScrollBar()
        left_bar.valueChanged.connect(right_bar.setValue)
        right_bar.valueChanged.connect(left_bar.setValue)

        self.operational_table.currentCellChanged.connect(self._sync_from_operational)
        self.detail_table.currentCellChanged.connect(self._sync_from_detail)
        self.detail_table.currentCellChanged.connect(self._update_inspector)

    def _sync_from_operational(self, row: int, _col: int, _prev_row: int, _prev_col: int) -> None:
        self._sync_row(row, self.detail_table)

    def _sync_from_detail(self, row: int, _col: int, _prev_row: int, _prev_col: int) -> None:
        self._sync_row(row, self.operational_table)

    def _sync_row(self, row: int, target: QTableWidget) -> None:
        if self._syncing_selection or row < 0 or row >= target.rowCount():
            return
        if target.columnCount() == 0:
            return
        self._syncing_selection = True
        try:
            current_col = target.currentColumn()
            target.setCurrentCell(row, current_col if current_col >= 0 else 0)
            target.selectRow(row)
        finally:
            self._syncing_selection = False

    def render(self, result: ValidationResult, status_provider: ItemStatusProvider) -> None:
        self._result = result
        operational, detail = split_item_view_columns(result.mmo)
        self._detail_columns = detail

        self._render_operational(result, operational, status_provider)
        self._render_detail(result, self._detail_columns)
        self._reset_inspector()

    def _render_operational(
        self,
        result: ValidationResult,
        columns: tuple[ItemViewColumn, ...],
        status_provider: ItemStatusProvider,
    ) -> None:
        headers = ["№", "Статус", *[column.label for column in columns]]
        table = self.operational_table
        table.clearContents()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(result.mmo.items))

        widths = [42, 76, 100, 92, 280, 58, 70, 84, 88]
        for index, width in enumerate(widths[: len(headers)]):
            table.setColumnWidth(index, width)

        for row, item in enumerate(result.mmo.items):
            status, severity, tooltip = status_provider(row + 1)
            values = [
                str(row + 1),
                status,
                *[item_column_value(item.fields, column) for column in columns],
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
                table.setItem(row, col, cell)

    def _render_detail(
        self,
        result: ValidationResult,
        columns: tuple[ItemViewColumn, ...],
    ) -> None:
        table = self.detail_table
        table.clearContents()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels([column.label for column in columns])
        table.setRowCount(len(result.mmo.items))

        for index in range(len(columns)):
            table.setColumnWidth(index, 155)

        for row, item in enumerate(result.mmo.items):
            for col, column in enumerate(columns):
                value = item_column_value(item.fields, column)
                cell = QTableWidgetItem(value)
                field_kind = "semantic" if column.semantic else "RAW"
                cell.setToolTip(
                    f"{column.label}\nПоле: {column.field_index or '—'}\nТип: {field_kind}"
                )
                table.setItem(row, col, cell)

    def _reset_inspector(self) -> None:
        self.inspector_title.setText("RAW Inspector")
        self.inspector_meta.setText("Виберіть поле у правій таблиці")
        self.inspector_value.clear()

    def _update_inspector(
        self,
        row: int,
        col: int,
        _prev_row: int,
        _prev_col: int,
    ) -> None:
        if (
            self._result is None
            or row < 0
            or col < 0
            or row >= len(self._result.mmo.items)
            or col >= len(self._detail_columns)
        ):
            self._reset_inspector()
            return

        column = self._detail_columns[col]
        item = self._result.mmo.items[row]
        value = item_column_value(item.fields, column)
        kind = "семантичне" if column.semantic else "RAW / непідтверджене"

        self.inspector_title.setText(column.label)
        self.inspector_meta.setText(
            f"Позиція {row + 1} · фізичне поле {column.field_index or '—'} · {kind}"
        )
        self.inspector_value.setPlainText(value)
