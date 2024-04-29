from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFontDatabase, QFont
from .highlighter import MarkdownHighlighter

class MainWidget(QTextEdit):
    def __init__(self, text_size=12):
        super().__init__()
        self.text_size = text_size
        self.load_fonts()
        self.set_default_style()
        self.highlighter = MarkdownHighlighter(self)
        self.setup_cursor()

    def load_fonts(self):
        QFontDatabase.addApplicationFont("resources/Montserrat-Regular.ttf")
        QFontDatabase.addApplicationFont("resources/Montserrat-Italic.ttf")
        QFontDatabase.addApplicationFont("resources/Montserrat-Bold.ttf")

    def set_default_style(self):
        self.change_colors("white", "black")
        self.set_text_size(self.text_size)

    def change_colors(self, bg="black", fg="green"):
        padding = str(int(self.width() * 0.1))
        self.setStyleSheet(f"background-color: {bg}; color: {fg}; padding: {padding}px;")

    def set_text_size(self, size):
        font_regular = QFont("Montserrat", size)
        self.setFont(font_regular)

    def setup_cursor(self):
        self.setCursorWidth(3)
