from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
from PySide6.QtCore import QRegularExpression
import re

class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for markdown."""
    
    # Pre-compiled regex patterns for better performance
    _compiled_patterns = {
        'bold': re.compile(r'\*\*([^*]+)\*\*'),
        'italic_star': re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)'),
        'italic_underscore': re.compile(r'(?<!\_)\_([^_]+)\_(?!\_)'),
        'heading5': re.compile(r'^(#####) (.+)'),
        'heading4': re.compile(r'^(####) (.+)'),
        'heading3': re.compile(r'^(###) (.+)'),
        'heading2': re.compile(r'^(##) (.+)'),
        'heading1': re.compile(r'^(#) (.+)')
    }
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_widget = parent
        self.rules = []
        self.formatting_ranges = []
        self.cursor_position = 0
        self.cursor_block_number = 0

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

        # Heading patterns are now handled separately in highlightBlock

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
        # Calculate which block (line) the cursor is on
        cursor = self.parent_widget.textCursor()
        cursor.setPosition(position)
        self.cursor_block_number = cursor.blockNumber()
        self.rehighlight()

    def highlightBlock(self, text):
        block_start = self.currentBlock().position()
        current_block_number = self.currentBlock().blockNumber()
        
        # Clear previous formatting ranges for this block
        self.formatting_ranges = [r for r in self.formatting_ranges if r['block_start'] != block_start]
        
        # Handle headings with cursor-based visibility using pre-compiled patterns
        heading_patterns = [
            ('heading5', self.heading5_format),
            ('heading4', self.heading4_format),
            ('heading3', self.heading3_format),
            ('heading2', self.heading2_format),
            ('heading1', self.heading1_format)
        ]
        
        for pattern_name, heading_format in heading_patterns:
            match = self._compiled_patterns[pattern_name].match(text)
            if match:
                # Get the hash characters and content
                hash_chars = match.group(1)  # The # characters
                content = match.group(2)     # The text after space
                hash_length = len(hash_chars)
                content_start = hash_length + 1  # +1 for the space
                
                # Apply formatting to the content (after the # and space)
                self.setFormat(content_start, len(content), heading_format)
                
                # Handle # character visibility based on cursor position
                cursor_on_this_line = (current_block_number == self.cursor_block_number)
                
                if not cursor_on_this_line:
                    # Hide the # characters and the space
                    self.setFormat(0, content_start, self.hidden_format)
                
                break  # Only one heading pattern can match per line
        
        # Handle bold formatting (**text**) using pre-compiled pattern
        for match in self._compiled_patterns['bold'].finditer(text):
            start = match.start()
            length = match.end() - match.start()
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
        
        # Handle italic formatting (*text* and _text_) using pre-compiled patterns
        for pattern_name in ['italic_star', 'italic_underscore']:
            for match in self._compiled_patterns[pattern_name].finditer(text):
                start = match.start()
                length = match.end() - match.start()
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
