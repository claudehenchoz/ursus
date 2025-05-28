from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PySide6.QtCore import QRegularExpression

class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for markdown."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_widget = parent
        self.rules = []
        self.formatting_ranges = []
        self.cursor_position = 0

        self.bold_format = self.create_text_format(parent.text_size, QFont.Bold)
        self.italic_format = self.create_text_format(parent.text_size, QFont.StyleItalic)
        self.heading1_format = self.create_text_format(parent.text_size + 8, QFont.Bold)
        self.heading2_format = self.create_text_format(parent.text_size + 6, QFont.Bold)
        self.heading3_format = self.create_text_format(parent.text_size + 4, QFont.Bold)
        self.heading4_format = self.create_text_format(parent.text_size + 2, QFont.Bold)
        self.heading5_format = self.create_text_format(parent.text_size + 1, QFont.Bold)
        
        # Create format for hiding formatting characters without gaps
        self.hidden_format = QTextCharFormat()
        # Use a very small font and make it transparent
        hidden_font = QFont("Montserrat", 1)
        hidden_font.setLetterSpacing(QFont.PercentageSpacing, 0)
        self.hidden_format.setFont(hidden_font)
        self.hidden_format.setForeground(QColor(0, 0, 0, 0))
        # Also set font size percentage to make it as small as possible
        self.hidden_format.setFontPointSize(0.1)

        self.rules.append((QRegularExpression(r"^##### .+"), self.heading5_format))
        self.rules.append((QRegularExpression(r"^#### .+"), self.heading4_format))
        self.rules.append((QRegularExpression(r"^### .+"), self.heading3_format))
        self.rules.append((QRegularExpression(r"^## .+"), self.heading2_format))
        self.rules.append((QRegularExpression(r"^# .+"), self.heading1_format))

    def create_text_format(self, size, style):
        font = QFont("Montserrat", size)
        if isinstance(style, QFont.Weight):
            font.setWeight(style)
        else:
            font.setStyle(style)
        fmt = QTextCharFormat()
        fmt.setFont(font)
        return fmt

    def set_cursor_position(self, position):
        self.cursor_position = position
        self.rehighlight()

    def highlightBlock(self, text):
        block_start = self.currentBlock().position()
        
        # Clear previous formatting ranges for this block
        self.formatting_ranges = [r for r in self.formatting_ranges if r['block_start'] != block_start]
        
        # Handle headings first
        for pattern, fmt in self.rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
        
        # Handle bold formatting (**text**)
        bold_pattern = QRegularExpression(r"\*\*([^*]+)\*\*")
        match_iterator = bold_pattern.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            start = match.capturedStart()
            length = match.capturedLength()
            content_start = start + 2
            content_length = length - 4
            absolute_start = block_start + start
            absolute_end = absolute_start + length
            
            # Store formatting range info
            range_info = {
                'block_start': block_start,
                'start': start,
                'end': start + length,
                'content_start': content_start,
                'content_end': content_start + content_length,
                'absolute_start': absolute_start,
                'absolute_end': absolute_end,
                'type': 'bold'
            }
            self.formatting_ranges.append(range_info)
            
            # Check if cursor is within this formatting range
            cursor_in_range = (absolute_start <= self.cursor_position <= absolute_end)
            
            # Apply formatting to content
            self.setFormat(content_start, content_length, self.bold_format)
            
            # Hide or show formatting characters based on cursor position
            if not cursor_in_range:
                self.setFormat(start, 2, self.hidden_format)  # Hide opening **
                self.setFormat(start + length - 2, 2, self.hidden_format)  # Hide closing **
        
        # Handle italic formatting (*text* and _text_)
        italic_patterns = [
            QRegularExpression(r"(?<!\*)\*([^*]+)\*(?!\*)"),
            QRegularExpression(r"(?<!\_)\_([^_]+)\_(?!\_)")
        ]
        
        for pattern in italic_patterns:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                content_start = start + 1
                content_length = length - 2
                absolute_start = block_start + start
                absolute_end = absolute_start + length
                
                # Store formatting range info
                range_info = {
                    'block_start': block_start,
                    'start': start,
                    'end': start + length,
                    'content_start': content_start,
                    'content_end': content_start + content_length,
                    'absolute_start': absolute_start,
                    'absolute_end': absolute_end,
                    'type': 'italic'
                }
                self.formatting_ranges.append(range_info)
                
                # Check if cursor is within this formatting range
                cursor_in_range = (absolute_start <= self.cursor_position <= absolute_end)
                
                # Apply formatting to content
                self.setFormat(content_start, content_length, self.italic_format)
                
                # Hide or show formatting characters based on cursor position
                if not cursor_in_range:
                    self.setFormat(start, 1, self.hidden_format)  # Hide opening char
                    self.setFormat(start + length - 1, 1, self.hidden_format)  # Hide closing char
