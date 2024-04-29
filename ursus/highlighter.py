from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont
from PySide6.QtCore import QRegularExpression

class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for markdown."""
    def __init__(self, parent):
        super().__init__(parent)
        self.rules = []

        self.bold_format = self.create_text_format(parent.text_size, QFont.Bold)
        self.italic_format = self.create_text_format(parent.text_size, QFont.StyleItalic)
        self.heading_format = self.create_text_format(parent.text_size + 4, QFont.Bold)

        self.rules.append((QRegularExpression(r"\*\*([^*]+)\*\*"), self.bold_format))
        self.rules.append((QRegularExpression(r"(?<!\*)\*([^*]+)\*(?!\*)"), self.italic_format))
        self.rules.append((QRegularExpression(r"^# .+"), self.heading_format))

    def create_text_format(self, size, style):
        font = QFont("Montserrat", size)
        if isinstance(style, QFont.Weight):
            font.setWeight(style)
        else:
            font.setStyle(style)
        fmt = QTextCharFormat()
        fmt.setFont(font)
        return fmt

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
