# descripcion: interfaz principal para comparar archivos python y mostrar coincidencias
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

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

from core.file_loader import DEFAULT_SOURCE_DIR, discoverSourceFiles
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
    # proposito: dibujar el margen de numeros de linea
    # parametros: editor -> editor al que pertenece esta area
    # retorno: ninguno
    def __init__(self, editor: CodeViewer) -> None:
        super().__init__(editor)
        self.editor = editor

    # proposito: dar el tamano sugerido del area lateral
    # parametros: ninguno
    # retorno: tamano sugerido del widget
    def sizeHint(self) -> QSize:
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    # proposito: pintar el area lateral
    # parametros: event -> evento de pintura
    # retorno: ninguno
    def paintEvent(self, event) -> None:  # noqa: N802
        self.editor.lineNumberAreaPaintEvent(event)


class CodeViewer(QPlainTextEdit):
    # proposito: crear un editor de solo lectura con numeros de linea y resaltado
    # parametros: parent -> widget padre opcional
    # retorno: ninguno
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setTabStopDistance(32)
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth(0)

    # proposito: calcular el ancho del margen de numeros de linea
    # parametros: ninguno
    # retorno: ancho del margen
    def lineNumberAreaWidth(self) -> int:
        digits = max(2, len(str(max(1, self.blockCount()))))
        return 14 + self.fontMetrics().horizontalAdvance("9") * digits

    # proposito: actualizar los margenes del editor
    # parametros: _ -> parametro requerido por la senal
    # retorno: ninguno
    def updateLineNumberAreaWidth(self, _: int) -> None:
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    # proposito: refrescar la zona donde van los numeros de linea
    # parametros: rect -> zona actualizada  dy -> desplazamiento vertical
    # retorno: ninguno
    def updateLineNumberArea(self, rect, dy: int) -> None:
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    # proposito: acomodar el margen lateral al redimensionar
    # parametros: event -> evento de cambio de tamano
    # retorno: ninguno
    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        contents = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(
                contents.left(),
                contents.top(),
                self.lineNumberAreaWidth(),
                contents.height(),
            )
        )

    # proposito: pintar los numeros de linea visibles
    # parametros: event -> evento de pintura
    # retorno: ninguno
    def lineNumberAreaPaintEvent(self, event) -> None:
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#f1ece3"))
        painter.setPen(QColor("#7a6958"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            blockVisible = block.isVisible() and bottom >= event.rect().top()
            if blockVisible:
                painter.drawText(
                    0,
                    top,
                    self.lineNumberArea.width() - 6,
                    self.fontMetrics().height(),
                    Qt.AlignRight | Qt.AlignVCenter,
                    str(blockNumber + 1),
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            blockNumber += 1

    # proposito: aplicar resaltado a una lista de rangos
    # parametros: spans -> rangos a pintar
    # retorno: ninguno
    def applyHighlights(self, spans: list[HighlightSpan]) -> None:
        selections: list[QTextEdit.ExtraSelection] = []

        for span in spans:
            validSpan = span.end > span.start
            if validSpan:
                selection = QTextEdit.ExtraSelection()
                cursor = self.textCursor()
                cursor.setPosition(span.start)
                cursor.setPosition(span.end, QTextCursor.KeepAnchor)
                selection.cursor = cursor

                color = QColor(HIGHLIGHT_COLORS[span.blockIndex % len(HIGHLIGHT_COLORS)])
                formatValue = QTextCharFormat()
                formatValue.setBackground(color)
                formatValue.setProperty(QTextCharFormat.FullWidthSelection, False)
                selection.format = formatValue
                selections.append(selection)

        self.setExtraSelections(selections)


class MainWindow(QMainWindow):
    # proposito: crear la ventana principal y cargar los archivos del proyecto
    # parametros: sourceDir -> carpeta de entrada opcional
    # retorno: ninguno
    def __init__(self, sourceDir: Path | None = None) -> None:
        super().__init__()
        self.sourceDir = sourceDir or DEFAULT_SOURCE_DIR
        self.engine = SimilarityEngine()
        self.sourceFiles: list[SourceFile] = []
        self.loadWarnings: list[str] = []
        self.currentResults: list[ComparisonResult] = []

        self.setWindowTitle("Analizador Lexico y Comparador de Similitud")
        self.resize(1480, 920)
        self.buildUi()
        self.loadFiles()

    # proposito: construir toda la interfaz
    # parametros: ninguno
    # retorno: ninguno
    def buildUi(self) -> None:
        container = QWidget()
        self.setCentralWidget(container)

        rootLayout = QVBoxLayout(container)
        rootLayout.setContentsMargins(12, 12, 12, 12)
        rootLayout.setSpacing(10)

        controlsGroup = QGroupBox("Configuracion")
        controlsLayout = QGridLayout(controlsGroup)

        self.techniqueCombo = QComboBox()
        self.techniqueCombo.addItem(TECHNIQUE_LABELS[TECHNIQUE_BAKER], TECHNIQUE_BAKER)
        self.techniqueCombo.addItem(TECHNIQUE_LABELS[TECHNIQUE_LCS_TEXT], TECHNIQUE_LCS_TEXT)
        self.techniqueCombo.addItem(TECHNIQUE_LABELS[TECHNIQUE_DIFF_TOKEN], TECHNIQUE_DIFF_TOKEN)
        self.techniqueCombo.addItem(TECHNIQUE_LABELS[TECHNIQUE_DIFF_TEXT], TECHNIQUE_DIFF_TEXT)

        self.baseFileCombo = QComboBox()
        self.baseFileCombo.currentIndexChanged.connect(self.onBaseFileChanged)

        self.analyzeButton = QPushButton("Analizar")
        self.analyzeButton.clicked.connect(self.analyze)

        self.datasetLabel = QLabel()
        self.datasetLabel.setWordWrap(True)
        self.datasetLabel.setObjectName("datasetInfo")

        controlsLayout.addWidget(QLabel("Tecnica"), 0, 0)
        controlsLayout.addWidget(self.techniqueCombo, 0, 1)
        controlsLayout.addWidget(QLabel("Archivo base"), 0, 2)
        controlsLayout.addWidget(self.baseFileCombo, 0, 3)
        controlsLayout.addWidget(self.analyzeButton, 0, 4)
        controlsLayout.addWidget(self.datasetLabel, 1, 0, 1, 5)
        controlsLayout.setColumnStretch(1, 2)
        controlsLayout.setColumnStretch(3, 2)

        rootLayout.addWidget(controlsGroup)

        contentSplitter = QSplitter(Qt.Horizontal)

        baseGroup = QGroupBox("Archivo base")
        baseLayout = QVBoxLayout(baseGroup)
        self.baseFileTitle = QLabel("Sin archivo cargado")
        self.baseFileTitle.setObjectName("panelTitle")
        self.baseEditor = CodeViewer()
        baseLayout.addWidget(self.baseFileTitle)
        baseLayout.addWidget(self.baseEditor)

        comparedGroup = QGroupBox("Archivo comparado")
        comparedLayout = QVBoxLayout(comparedGroup)
        self.comparedFileTitle = QLabel("Selecciona un resultado del ranking")
        self.comparedFileTitle.setObjectName("panelTitle")
        self.comparedEditor = CodeViewer()
        comparedLayout.addWidget(self.comparedFileTitle)
        comparedLayout.addWidget(self.comparedEditor)

        rankingGroup = QGroupBox("Ranking de similitud")
        rankingLayout = QVBoxLayout(rankingGroup)
        self.resultsTable = QTableWidget(0, 3)
        self.resultsTable.setHorizontalHeaderLabels(["Archivo", "Similitud (%)", "Bloques"])
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.resultsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultsTable.verticalHeader().setVisible(False)
        self.resultsTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.resultsTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.resultsTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.resultsTable.itemSelectionChanged.connect(self.onResultSelected)
        rankingLayout.addWidget(self.resultsTable)

        contentSplitter.addWidget(baseGroup)
        contentSplitter.addWidget(comparedGroup)
        contentSplitter.addWidget(rankingGroup)
        contentSplitter.setSizes([410, 410, 300])

        rootLayout.addWidget(contentSplitter, stretch=1)

        detailsGroup = QGroupBox("Detalles")
        detailsGroup.setMaximumHeight(220)
        detailsLayout = QVBoxLayout(detailsGroup)

        detailsScroll = QScrollArea()
        detailsScroll.setWidgetResizable(True)
        detailsScroll.setFrameShape(QFrame.NoFrame)
        detailsScroll.setObjectName("detailsScroll")

        detailsContent = QWidget()
        detailsContent.setObjectName("detailsContent")
        detailsContentLayout = QHBoxLayout(detailsContent)

        summaryFrame = QFrame()
        summaryFrame.setObjectName("detailsSummary")
        summaryLayout = QFormLayout(summaryFrame)
        self.techniqueValue = QLabel("-")
        self.matchCountValue = QLabel("0")
        self.commonLengthValue = QLabel("0")
        self.shorterLengthValue = QLabel("0")
        self.percentValue = QLabel("0.00%")
        summaryLayout.addRow("Tecnica", self.techniqueValue)
        summaryLayout.addRow("Coincidencias", self.matchCountValue)
        summaryLayout.addRow("Longitud comun", self.commonLengthValue)
        summaryLayout.addRow("Programa mas corto", self.shorterLengthValue)
        summaryLayout.addRow("Porcentaje final", self.percentValue)

        self.detailsBox = QTextEdit()
        self.detailsBox.setReadOnly(True)
        self.detailsBox.setPlaceholderText("Bloques coincidentes")
        self.detailsBox.setMinimumHeight(260)
        self.detailsBox.setObjectName("detailsBox")

        detailsContentLayout.addWidget(summaryFrame, stretch=0)
        detailsContentLayout.addWidget(self.detailsBox, stretch=1)
        detailsScroll.setWidget(detailsContent)
        detailsLayout.addWidget(detailsScroll)

        rootLayout.addWidget(detailsGroup)

        self.applyStyles()

    # proposito: aplicar estilos visuales a la interfaz
    # parametros: ninguno
    # retorno: ninguno
    def applyStyles(self) -> None:
        styleSheet = (
            "QWidget {"
            'font-family: "Segoe UI", "Noto Sans";'
            "font-size: 13px;"
            "color: #1f1f1f;"
            "}"
            "QMainWindow, QGroupBox {"
            "background: #f7f5ef;"
            "}"
            "QScrollArea {"
            "border: none;"
            "}"
            'QGroupBox[title="Detalles"] {'
            "background: #fffdfa;"
            "}"
            "QScrollArea#detailsScroll, QWidget#detailsContent, QFrame#detailsSummary, QTextEdit#detailsBox {"
            "background: #fffdfa;"
            "}"
            "QGroupBox {"
            "border: 1px solid #d8d1c2;"
            "border-radius: 8px;"
            "margin-top: 12px;"
            "font-weight: 600;"
            "}"
            "QGroupBox::title {"
            "subcontrol-origin: margin;"
            "left: 10px;"
            "padding: 0 4px;"
            "color: #5d4632;"
            "}"
            "QLabel, QTableWidget, QHeaderView::section, QComboBox, QPlainTextEdit {"
            "color: #1f1f1f;"
            "}"
            "QHeaderView::section {"
            "background: #fffdfa;"
            "border: 1px solid #d8d1c2;"
            "padding: 4px 6px;"
            "}"
            "QPlainTextEdit, QTableWidget, QComboBox {"
            "background: #fffdfa;"
            "border: 1px solid #d8d1c2;"
            "border-radius: 6px;"
            "selection-background-color: #d9c3a5;"
            "selection-color: #1f1f1f;"
            "}"
            "QTextEdit#detailsBox {"
            "border: 1px solid #d8d1c2;"
            "border-radius: 6px;"
            "selection-background-color: #d9c3a5;"
            "selection-color: #1f1f1f;"
            "}"
            "QTableWidget::item {"
            "color: #1f1f1f;"
            "}"
            "QComboBox QAbstractItemView {"
            "background: #fffdfa;"
            "color: #1f1f1f;"
            "selection-background-color: #d9c3a5;"
            "selection-color: #1f1f1f;"
            "}"
            "QPushButton {"
            "background: #9b6b43;"
            "color: white;"
            "border: none;"
            "border-radius: 6px;"
            "padding: 8px 16px;"
            "font-weight: 600;"
            "}"
            "QPushButton:hover {"
            "background: #825636;"
            "}"
            "QLabel#panelTitle {"
            "font-size: 14px;"
            "font-weight: 600;"
            "color: #513a27;"
            "}"
            "QLabel#datasetInfo {"
            "color: #6a5a4c;"
            "}"
        )
        self.setStyleSheet(styleSheet)

    # proposito: cargar archivos de la carpeta de entrada
    # parametros: ninguno
    # retorno: ninguno
    def loadFiles(self) -> None:
        self.sourceFiles, self.loadWarnings = discoverSourceFiles(self.sourceDir)
        self.baseFileCombo.clear()

        for sourceFile in self.sourceFiles:
            self.baseFileCombo.addItem(sourceFile.name, sourceFile)

        datasetText = f"Carpeta de entrada: {self.sourceDir.resolve()}"
        if self.loadWarnings:
            datasetText += " | " + " | ".join(self.loadWarnings)
        self.datasetLabel.setText(datasetText)

        if not self.sourceFiles:
            QMessageBox.warning(
                self,
                "Sin archivos",
                "No se encontraron archivos fuente en la carpeta configurada",
            )
            self.baseEditor.setPlainText("")
            self.comparedEditor.setPlainText("")
            self.baseFileTitle.setText("Sin archivo cargado")
        else:
            self.onBaseFileChanged(0)

    # proposito: actualizar la interfaz cuando cambia el archivo base
    # parametros: index -> posicion seleccionada en el combo
    # retorno: ninguno
    def onBaseFileChanged(self, index: int) -> None:
        sourceFile = self.baseFileCombo.itemData(index)
        validSourceFile = isinstance(sourceFile, SourceFile)

        if validSourceFile:
            self.baseFileTitle.setText(
                f"{sourceFile.name} | {sourceFile.lineCount} lineas | {sourceFile.extension or 'sin extension'}"
            )
            self.baseEditor.setPlainText(sourceFile.text)
            self.baseEditor.applyHighlights([])
            self.comparedEditor.setPlainText("")
            self.comparedEditor.applyHighlights([])
            self.comparedFileTitle.setText("Selecciona un resultado del ranking")
            self.resultsTable.setRowCount(0)
            self.currentResults = []
            self.updateDetails(None)
        else:
            self.baseEditor.setPlainText("")
            self.baseFileTitle.setText("Sin archivo base")

    # proposito: ejecutar la comparacion para el archivo base seleccionado
    # parametros: ninguno
    # retorno: ninguno
    def analyze(self) -> None:
        enoughFiles = len(self.sourceFiles) >= 2
        if not enoughFiles:
            QMessageBox.warning(
                self,
                "Archivos insuficientes",
                "Se necesitan al menos dos archivos fuente para comparar",
            )
        else:
            baseFile = self.baseFileCombo.currentData()
            validBaseFile = isinstance(baseFile, SourceFile)

            if validBaseFile:
                techniqueKey = self.techniqueCombo.currentData()
                self.currentResults = self.engine.compareAll(baseFile, self.sourceFiles, techniqueKey)
                self.populateResultsTable()
                self.baseEditor.setPlainText(baseFile.text)
                self.baseFileTitle.setText(
                    f"{baseFile.name} | {baseFile.lineCount} lineas | {baseFile.extension or 'sin extension'}"
                )

                if self.currentResults:
                    self.resultsTable.selectRow(0)
                    self.showResult(self.currentResults[0])
                else:
                    self.updateDetails(None)

    # proposito: llenar la tabla del ranking con los resultados actuales
    # parametros: ninguno
    # retorno: ninguno
    def populateResultsTable(self) -> None:
        self.resultsTable.setRowCount(len(self.currentResults))

        for row, result in enumerate(self.currentResults):
            fileItem = QTableWidgetItem(result.comparedFile.name)
            fileItem.setData(Qt.UserRole, result)
            percentItem = QTableWidgetItem(f"{result.similarityPercent:.2f}")
            blocksItem = QTableWidgetItem(str(result.blockCount))
            percentItem.setTextAlignment(Qt.AlignCenter)
            blocksItem.setTextAlignment(Qt.AlignCenter)
            self.resultsTable.setItem(row, 0, fileItem)
            self.resultsTable.setItem(row, 1, percentItem)
            self.resultsTable.setItem(row, 2, blocksItem)

        self.resultsTable.resizeRowsToContents()

    # proposito: mostrar el archivo seleccionado del ranking
    # parametros: ninguno
    # retorno: ninguno
    def onResultSelected(self) -> None:
        selectedItems = self.resultsTable.selectedItems()
        if selectedItems:
            result = selectedItems[0].data(Qt.UserRole)
            validResult = isinstance(result, ComparisonResult)
            if validResult:
                self.showResult(result)

    # proposito: cargar en pantalla un resultado de comparacion
    # parametros: result -> resultado seleccionado
    # retorno: ninguno
    def showResult(self, result: ComparisonResult) -> None:
        self.baseEditor.setPlainText(result.baseFile.text)
        self.comparedEditor.setPlainText(result.comparedFile.text)
        self.baseEditor.applyHighlights(result.baseHighlights)
        self.comparedEditor.applyHighlights(result.comparedHighlights)
        self.comparedFileTitle.setText(
            f"{result.comparedFile.name} | {result.comparedFile.lineCount} lineas | "
            f"{result.comparedFile.extension or 'sin extension'}"
        )
        self.updateDetails(result)

    # proposito: convertir un rango resaltado a lineas humanas
    # parametros: text -> texto completo  span -> rango resaltado
    # retorno: tupla con linea inicial y final
    @staticmethod
    def lineRangeFromSpan(text: str, span: HighlightSpan) -> tuple[int, int]:
        startLine = text.count("\n", 0, max(0, span.start)) + 1
        endIndex = max(span.start, span.end - 1)
        endLine = text.count("\n", 0, min(len(text), endIndex)) + 1
        return startLine, endLine

    # proposito: formatear un rango de lineas para mostrarlo en detalles
    # parametros: label startLine endLine -> datos del rango
    # retorno: texto listo para mostrar
    @staticmethod
    def formatLineRange(label: str, startLine: int, endLine: int) -> str:
        singleLine = startLine == endLine
        if singleLine:
            return f"{label} linea {startLine}"
        return f"{label} lineas {startLine}-{endLine}"

    # proposito: actualizar el panel inferior de detalles
    # parametros: result -> resultado a mostrar o none
    # retorno: ninguno
    def updateDetails(self, result: ComparisonResult | None) -> None:
        if result is None:
            self.techniqueValue.setText("-")
            self.matchCountValue.setText("0")
            self.commonLengthValue.setText("0")
            self.shorterLengthValue.setText("0")
            self.percentValue.setText("0.00%")
            detailsText = "\n".join(self.loadWarnings) if self.loadWarnings else ""
            self.detailsBox.setPlainText(detailsText)
        else:
            self.techniqueValue.setText(result.techniqueLabel)
            self.matchCountValue.setText(str(result.blockCount))
            self.commonLengthValue.setText(f"{result.totalCommonLength} {result.unitName}")
            self.shorterLengthValue.setText(f"{result.shorterLength} {result.unitName}")
            self.percentValue.setText(f"{result.similarityPercent:.2f}%")

            messageLines: list[str] = []
            if result.error:
                messageLines.append(f"Error: {result.error}")
            messageLines.extend(result.warnings)

            htmlParts: list[str] = []
            if messageLines:
                htmlParts.append(
                    "<div style='margin-bottom:8px;'>"
                    + "<br>".join(escape(line) for line in messageLines if line)
                    + "</div>"
                )

            if result.blocks:
                htmlParts.append("<div><b>Bloques detectados:</b></div>")
                baseSpansByBlock = {span.blockIndex: span for span in result.baseHighlights}
                comparedSpansByBlock = {span.blockIndex: span for span in result.comparedHighlights}

                for index, block in enumerate(result.blocks, start=1):
                    if index <= 20:
                        baseSpan = baseSpansByBlock.get(index - 1)
                        comparedSpan = comparedSpansByBlock.get(index - 1)
                        blockSummary = f"{index}. longitud={block.length} {result.unitName}"

                        if baseSpan and comparedSpan:
                            baseStartLine, baseEndLine = self.lineRangeFromSpan(result.baseFile.text, baseSpan)
                            comparedStartLine, comparedEndLine = self.lineRangeFromSpan(
                                result.comparedFile.text,
                                comparedSpan,
                            )
                            blockSummary += (
                                f" | {self.formatLineRange('Base', baseStartLine, baseEndLine)}"
                                f" | {self.formatLineRange('Comparado', comparedStartLine, comparedEndLine)}"
                            )
                        else:
                            blockSummary += (
                                f" | Base [{block.baseStart}, {block.baseEnd})"
                                f" | Comparado [{block.otherStart}, {block.otherEnd})"
                            )

                        color = HIGHLIGHT_COLORS[(index - 1) % len(HIGHLIGHT_COLORS)]
                        htmlParts.append(
                            "<div style='margin:4px 0;'>"
                            f"<span style='background:{color}; color:#1f1f1f; "
                            "padding:2px 6px; border-radius:4px; display:inline-block;'>"
                            f"{escape(blockSummary)}"
                            "</span>"
                            "</div>"
                        )

                if len(result.blocks) > 20:
                    htmlParts.append("<div>...</div>")

            if htmlParts:
                self.detailsBox.setHtml("".join(htmlParts))
            else:
                self.detailsBox.clear()


# proposito: lanzar la aplicacion de escritorio
# parametros: ninguno
# retorno: codigo de salida de qt
def launchApp() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()
