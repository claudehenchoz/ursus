from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import QTimer
from .highlighter import MarkdownHighlighter

class MainWidget(QTextEdit):
    def __init__(self, text_size=12):
        super().__init__()
        self.text_size = text_size
        self.load_fonts()
        self.set_default_style()
        self.highlighter = MarkdownHighlighter(self)
        self.setup_cursor()
        self.setup_cursor_tracking()

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
        
    def setup_cursor_tracking(self):
        # Connect cursor position changes to highlighter
        self.cursorPositionChanged.connect(self.on_cursor_position_changed)
        
        # Use a timer for debouncing to avoid excessive rehighlighting
        self.cursor_timer = QTimer()
        self.cursor_timer.setSingleShot(True)
        self.cursor_timer.timeout.connect(self.update_highlighting)
        
    def on_cursor_position_changed(self):
        # Debounce cursor position changes to avoid excessive rehighlighting
        self.cursor_timer.stop()
        self.cursor_timer.start(50)  # 50ms delay
        
    def update_highlighting(self):
        cursor_position = self.textCursor().position()
        self.highlighter.set_cursor_position(cursor_position)
