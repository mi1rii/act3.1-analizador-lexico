"""Ventana principal de la aplicacion de similitud."""

from __future__ import annotations

from html import escape
from pathlib import Path

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.file_loader import DEFAULT_SOURCE_DIR, discover_source_files
from core.similarity import (
    SimilarityEngine,
    TECHNIQUE_BAKER,
    TECHNIQUE_DIFF_TEXT,
    TECHNIQUE_DIFF_TOKEN,
    TECHNIQUE_LABELS,
    TECHNIQUE_LCS_TEXT,
)
from models.match_models import ComparisonResult, HighlightSpan, SourceFile


HIGHLIGHT_COLORS = [
    "#ffe082",
    "#ffcc80",
    "#fff59d",
    "#c5e1a5",
    "#b3e5fc",
    "#d1c4e9",
    "#f8bbd0",
    "#ffab91",
]


class LineNumberArea(QWidget):
    """Area lateral con numeros de linea."""

    def __init__(self, editor: "CodeViewer") -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802
        self.editor.line_number_area_paint_event(event)


class CodeViewer(QPlainTextEdit):
    """Editor de solo lectura con resaltado y numeros de linea."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopDistance(32)
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

    def line_number_area_width(self) -> int:
        digits = max(2, len(str(max(1, self.blockCount()))))
        return 14 + self.fontMetrics().horizontalAdvance("9") * digits

    def update_line_number_area_width(self, _: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy: int) -> None:
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        contents = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(
                contents.left(),
                contents.top(),
                self.line_number_area_width(),
                contents.height(),
            )
        )

    def line_number_area_paint_event(self, event) -> None:
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#f1ece3"))
        painter.setPen(QColor("#7a6958"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignRight | Qt.AlignVCenter,
                    str(block_number + 1),
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def apply_highlights(self, spans: list[HighlightSpan]) -> None:
        selections: list[QTextEdit.ExtraSelection] = []
        for span in spans:
            if span.end <= span.start:
                continue
            selection = QTextEdit.ExtraSelection()
            cursor = self.textCursor()
            cursor.setPosition(span.start)
            cursor.setPosition(span.end, QTextCursor.KeepAnchor)
            selection.cursor = cursor
            color = QColor(HIGHLIGHT_COLORS[span.block_index % len(HIGHLIGHT_COLORS)])
            format_ = QTextCharFormat()
            format_.setBackground(color)
            format_.setProperty(QTextCharFormat.FullWidthSelection, False)
            selection.format = format_
            selections.append(selection)
        self.setExtraSelections(selections)


class MainWindow(QMainWindow):
    """UI principal que coordina carga, comparacion y visualizacion."""

    def __init__(self, source_dir: Path | None = None) -> None:
        super().__init__()
        self.source_dir = source_dir or DEFAULT_SOURCE_DIR
        self.engine = SimilarityEngine()
        self.source_files: list[SourceFile] = []
        self.load_warnings: list[str] = []
        self.current_results: list[ComparisonResult] = []

        self.setWindowTitle("Analizador Lexico y Comparador de Similitud")
        self.resize(1480, 920)
        self._build_ui()
        self._load_files()

    def _build_ui(self) -> None:
        container = QWidget()
        self.setCentralWidget(container)

        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        controls_group = QGroupBox("Configuracion")
        controls_layout = QGridLayout(controls_group)

        self.technique_combo = QComboBox()
        self.technique_combo.addItem(TECHNIQUE_LABELS[TECHNIQUE_BAKER], TECHNIQUE_BAKER)
        self.technique_combo.addItem(TECHNIQUE_LABELS[TECHNIQUE_LCS_TEXT], TECHNIQUE_LCS_TEXT)
        self.technique_combo.addItem(TECHNIQUE_LABELS[TECHNIQUE_DIFF_TOKEN], TECHNIQUE_DIFF_TOKEN)
        self.technique_combo.addItem(TECHNIQUE_LABELS[TECHNIQUE_DIFF_TEXT], TECHNIQUE_DIFF_TEXT)

        self.base_file_combo = QComboBox()
        self.base_file_combo.currentIndexChanged.connect(self._on_base_file_changed)

        self.analyze_button = QPushButton("Analizar")
        self.analyze_button.clicked.connect(self._analyze)

        self.dataset_label = QLabel()
        self.dataset_label.setWordWrap(True)
        self.dataset_label.setObjectName("datasetInfo")

        controls_layout.addWidget(QLabel("Tecnica"), 0, 0)
        controls_layout.addWidget(self.technique_combo, 0, 1)
        controls_layout.addWidget(QLabel("Archivo base"), 0, 2)
        controls_layout.addWidget(self.base_file_combo, 0, 3)
        controls_layout.addWidget(self.analyze_button, 0, 4)
        controls_layout.addWidget(self.dataset_label, 1, 0, 1, 5)
        controls_layout.setColumnStretch(1, 2)
        controls_layout.setColumnStretch(3, 2)

        root_layout.addWidget(controls_group)

        content_splitter = QSplitter(Qt.Horizontal)

        base_group = QGroupBox("Archivo base")
        base_layout = QVBoxLayout(base_group)
        self.base_file_title = QLabel("Sin archivo cargado")
        self.base_file_title.setObjectName("panelTitle")
        self.base_editor = CodeViewer()
        base_layout.addWidget(self.base_file_title)
        base_layout.addWidget(self.base_editor)

        compared_group = QGroupBox("Archivo comparado")
        compared_layout = QVBoxLayout(compared_group)
        self.compared_file_title = QLabel("Selecciona un resultado del ranking")
        self.compared_file_title.setObjectName("panelTitle")
        self.compared_editor = CodeViewer()
        compared_layout.addWidget(self.compared_file_title)
        compared_layout.addWidget(self.compared_editor)

        ranking_group = QGroupBox("Ranking de similitud")
        ranking_layout = QVBoxLayout(ranking_group)
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["Archivo", "Similitud (%)", "Bloques"])
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.itemSelectionChanged.connect(self._on_result_selected)
        ranking_layout.addWidget(self.results_table)

        content_splitter.addWidget(base_group)
        content_splitter.addWidget(compared_group)
        content_splitter.addWidget(ranking_group)
        content_splitter.setSizes([410, 410, 300])

        root_layout.addWidget(content_splitter, stretch=1)

        details_group = QGroupBox("Detalles")
        details_group.setMaximumHeight(220)
        details_layout = QVBoxLayout(details_group)

        details_scroll = QScrollArea()
        details_scroll.setWidgetResizable(True)
        details_scroll.setFrameShape(QFrame.NoFrame)
        details_scroll.setObjectName("detailsScroll")

        details_content = QWidget()
        details_content.setObjectName("detailsContent")
        details_content_layout = QHBoxLayout(details_content)

        summary_frame = QFrame()
        summary_frame.setObjectName("detailsSummary")
        summary_layout = QFormLayout(summary_frame)
        self.technique_value = QLabel("-")
        self.match_count_value = QLabel("0")
        self.common_length_value = QLabel("0")
        self.shorter_length_value = QLabel("0")
        self.percent_value = QLabel("0.00%")
        summary_layout.addRow("Tecnica", self.technique_value)
        summary_layout.addRow("Coincidencias", self.match_count_value)
        summary_layout.addRow("Longitud comun", self.common_length_value)
        summary_layout.addRow("Programa mas corto", self.shorter_length_value)
        summary_layout.addRow("Porcentaje final", self.percent_value)

        self.warnings_box = QTextEdit()
        self.warnings_box.setReadOnly(True)
        self.warnings_box.setPlaceholderText("Bloques coincidentes")
        self.warnings_box.setMinimumHeight(260)
        self.warnings_box.setObjectName("detailsBox")

        details_content_layout.addWidget(summary_frame, stretch=0)
        details_content_layout.addWidget(self.warnings_box, stretch=1)
        details_scroll.setWidget(details_content)
        details_layout.addWidget(details_scroll)

        root_layout.addWidget(details_group)

        self._apply_styles()

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                font-family: "Segoe UI", "Noto Sans";
                font-size: 13px;
                color: #1f1f1f;
            }
            QMainWindow, QGroupBox {
                background: #f7f5ef;
            }
            QScrollArea {
                border: none;
            }
            QGroupBox[title="Detalles"] {
                background: #fffdfa;
            }
            QScrollArea#detailsScroll, QWidget#detailsContent, QFrame#detailsSummary, QTextEdit#detailsBox {
                background: #fffdfa;
            }
            QGroupBox {
                border: 1px solid #d8d1c2;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #5d4632;
            }
            QLabel, QTableWidget, QHeaderView::section, QComboBox, QPlainTextEdit {
                color: #1f1f1f;
            }
            QHeaderView::section {
                background: #fffdfa;
                border: 1px solid #d8d1c2;
                padding: 4px 6px;
            }
            QPlainTextEdit, QTableWidget, QComboBox {
                background: #fffdfa;
                border: 1px solid #d8d1c2;
                border-radius: 6px;
                selection-background-color: #d9c3a5;
                selection-color: #1f1f1f;
            }
            QTextEdit#detailsBox {
                border: 1px solid #d8d1c2;
                border-radius: 6px;
                selection-background-color: #d9c3a5;
                selection-color: #1f1f1f;
            }
            QTableWidget::item {
                color: #1f1f1f;
            }
            QComboBox QAbstractItemView {
                background: #fffdfa;
                color: #1f1f1f;
                selection-background-color: #d9c3a5;
                selection-color: #1f1f1f;
            }
            QPushButton {
                background: #9b6b43;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #825636;
            }
            QLabel#panelTitle {
                font-size: 14px;
                font-weight: 600;
                color: #513a27;
            }
            QLabel#datasetInfo {
                color: #6a5a4c;
            }
            """
        )

    def _load_files(self) -> None:
        self.source_files, self.load_warnings = discover_source_files(self.source_dir)
        self.base_file_combo.clear()
        for source_file in self.source_files:
            self.base_file_combo.addItem(source_file.name, source_file)

        dataset_text = f"Carpeta de entrada: {self.source_dir.resolve()}"
        if self.load_warnings:
            dataset_text += " | " + " | ".join(self.load_warnings)
        self.dataset_label.setText(dataset_text)

        if not self.source_files:
            QMessageBox.warning(
                self,
                "Sin archivos",
                "No se encontraron archivos fuente en la carpeta configurada.",
            )
            self.base_editor.setPlainText("")
            self.compared_editor.setPlainText("")
            self.base_file_title.setText("Sin archivo cargado")
            return

        self._on_base_file_changed(0)

    def _on_base_file_changed(self, index: int) -> None:
        source_file = self.base_file_combo.itemData(index)
        if not isinstance(source_file, SourceFile):
            self.base_editor.setPlainText("")
            self.base_file_title.setText("Sin archivo base")
            return

        self.base_file_title.setText(
            f"{source_file.name} | {source_file.line_count} lineas | {source_file.extension or 'sin extension'}"
        )
        self.base_editor.setPlainText(source_file.text)
        self.base_editor.apply_highlights([])
        self.compared_editor.setPlainText("")
        self.compared_editor.apply_highlights([])
        self.compared_file_title.setText("Selecciona un resultado del ranking")
        self.results_table.setRowCount(0)
        self.current_results = []
        self._update_details(None)

    def _analyze(self) -> None:
        if len(self.source_files) < 2:
            QMessageBox.warning(
                self,
                "Archivos insuficientes",
                "Se necesitan al menos dos archivos fuente para comparar.",
            )
            return

        base_file = self.base_file_combo.currentData()
        if not isinstance(base_file, SourceFile):
            return

        technique_key = self.technique_combo.currentData()
        self.current_results = self.engine.compare_all(base_file, self.source_files, technique_key)
        self._populate_results_table()
        self.base_editor.setPlainText(base_file.text)
        self.base_file_title.setText(
            f"{base_file.name} | {base_file.line_count} lineas | {base_file.extension or 'sin extension'}"
        )

        if self.current_results:
            self.results_table.selectRow(0)
            self._show_result(self.current_results[0])
        else:
            self._update_details(None)

    def _populate_results_table(self) -> None:
        self.results_table.setRowCount(len(self.current_results))
        for row, result in enumerate(self.current_results):
            file_item = QTableWidgetItem(result.compared_file.name)
            file_item.setData(Qt.UserRole, result)
            percent_item = QTableWidgetItem(f"{result.similarity_percent:.2f}")
            blocks_item = QTableWidgetItem(str(result.block_count))
            percent_item.setTextAlignment(Qt.AlignCenter)
            blocks_item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setItem(row, 0, file_item)
            self.results_table.setItem(row, 1, percent_item)
            self.results_table.setItem(row, 2, blocks_item)
        self.results_table.resizeRowsToContents()

    def _on_result_selected(self) -> None:
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            return
        result = selected_items[0].data(Qt.UserRole)
        if isinstance(result, ComparisonResult):
            self._show_result(result)

    def _show_result(self, result: ComparisonResult) -> None:
        self.base_editor.setPlainText(result.base_file.text)
        self.compared_editor.setPlainText(result.compared_file.text)
        self.base_editor.apply_highlights(result.base_highlights)
        self.compared_editor.apply_highlights(result.compared_highlights)
        self.compared_file_title.setText(
            f"{result.compared_file.name} | {result.compared_file.line_count} lineas | "
            f"{result.compared_file.extension or 'sin extension'}"
        )
        self._update_details(result)

    @staticmethod
    def _line_range_from_span(text: str, span: HighlightSpan) -> tuple[int, int]:
        start_line = text.count("\n", 0, max(0, span.start)) + 1
        end_index = max(span.start, span.end - 1)
        end_line = text.count("\n", 0, min(len(text), end_index)) + 1
        return start_line, end_line

    @staticmethod
    def _format_line_range(label: str, start_line: int, end_line: int) -> str:
        if start_line == end_line:
            return f"{label} linea {start_line}"
        return f"{label} lineas {start_line}-{end_line}"

    def _update_details(self, result: ComparisonResult | None) -> None:
        if result is None:
            self.technique_value.setText("-")
            self.match_count_value.setText("0")
            self.common_length_value.setText("0")
            self.shorter_length_value.setText("0")
            self.percent_value.setText("0.00%")
            text = "\n".join(self.load_warnings) if self.load_warnings else ""
            self.warnings_box.setPlainText(text)
            return

        self.technique_value.setText(result.technique_label)
        self.match_count_value.setText(str(result.block_count))
        self.common_length_value.setText(f"{result.total_common_length} {result.unit_name}")
        self.shorter_length_value.setText(f"{result.shorter_length} {result.unit_name}")
        self.percent_value.setText(f"{result.similarity_percent:.2f}%")

        message_lines: list[str] = []
        if result.error:
            message_lines.append(f"Error: {result.error}")
        message_lines.extend(result.warnings)

        html_parts: list[str] = []
        if message_lines:
            html_parts.append(
                "<div style='margin-bottom:8px;'>" +
                "<br>".join(escape(line) for line in message_lines if line) +
                "</div>"
            )

        if result.blocks:
            html_parts.append("<div><b>Bloques detectados:</b></div>")
            base_spans_by_block = {span.block_index: span for span in result.base_highlights}
            compared_spans_by_block = {span.block_index: span for span in result.compared_highlights}
            for index, block in enumerate(result.blocks[:20], start=1):
                base_span = base_spans_by_block.get(index - 1)
                compared_span = compared_spans_by_block.get(index - 1)
                block_summary = (
                    f"{index}. longitud={block.length} {result.unit_name}"
                )
                if base_span and compared_span:
                    base_start_line, base_end_line = self._line_range_from_span(
                        result.base_file.text,
                        base_span,
                    )
                    compared_start_line, compared_end_line = self._line_range_from_span(
                        result.compared_file.text,
                        compared_span,
                    )
                    block_summary += (
                        f" | {self._format_line_range('Base', base_start_line, base_end_line)}"
                        f" | {self._format_line_range('Comparado', compared_start_line, compared_end_line)}"
                    )
                else:
                    block_summary += (
                        f" | Base [{block.base_start}, {block.base_end})"
                        f" | Comparado [{block.other_start}, {block.other_end})"
                    )
                color = HIGHLIGHT_COLORS[(index - 1) % len(HIGHLIGHT_COLORS)]
                html_parts.append(
                    "<div style='margin:4px 0;'>"
                    f"<span style='background:{color}; color:#1f1f1f; "
                    "padding:2px 6px; border-radius:4px; display:inline-block;'>"
                    f"{escape(block_summary)}"
                    "</span>"
                    "</div>"
                )
            if len(result.blocks) > 20:
                html_parts.append("<div>...</div>")

        if not html_parts:
            self.warnings_box.clear()
            return

        self.warnings_box.setHtml("".join(html_parts))


def launch_app() -> int:
    """Punto de entrada de escritorio."""

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()
