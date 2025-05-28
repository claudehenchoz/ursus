from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFontDatabase, QFont, QTextCursor
from PySide6.QtCore import QTimer
import re
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
        
    def toggle_bold(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            
            # Get full text to check surrounding characters
            full_text = self.toPlainText()
            
            # Check if selection includes formatting or if surrounding text has formatting
            is_bold = False
            actual_start = start_pos
            actual_end = end_pos
            
            if selected_text.startswith('**') and selected_text.endswith('**') and len(selected_text) > 4:
                # Selection includes the ** characters
                is_bold = True
                actual_start = start_pos + 2
                actual_end = end_pos - 2
            elif (start_pos >= 2 and end_pos <= len(full_text) - 2 and 
                  full_text[start_pos-2:start_pos] == '**' and 
                  full_text[end_pos:end_pos+2] == '**'):
                # Selection is surrounded by ** characters
                is_bold = True
                actual_start = start_pos - 2
                actual_end = end_pos + 2
            
            if is_bold:
                # Remove bold formatting
                cursor.setPosition(actual_start)
                cursor.setPosition(actual_end, QTextCursor.KeepAnchor)
                new_text = cursor.selectedText()
                if new_text.startswith('**') and new_text.endswith('**'):
                    new_text = new_text[2:-2]
                cursor.insertText(new_text)
                # Restore selection on the unformatted text
                cursor.setPosition(actual_start)
                cursor.setPosition(actual_start + len(new_text), QTextCursor.KeepAnchor)
            else:
                # Add bold formatting
                new_text = f"**{selected_text}**"
                cursor.insertText(new_text)
                # Restore selection on the formatted text (excluding the **)
                cursor.setPosition(start_pos + 2)
                cursor.setPosition(start_pos + 2 + len(selected_text), QTextCursor.KeepAnchor)
            
            self.setTextCursor(cursor)
        else:
            # No selection - insert bold formatting at cursor position
            cursor.insertText("****")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 2)
            self.setTextCursor(cursor)
            
    def toggle_italic(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            
            # Get full text to check surrounding characters
            full_text = self.toPlainText()
            
            # Check if selection includes formatting or if surrounding text has formatting
            is_italic = False
            actual_start = start_pos
            actual_end = end_pos
            italic_char = '*'
            
            # Check if selection includes italic formatting
            if ((selected_text.startswith('*') and selected_text.endswith('*') and len(selected_text) > 2 and not selected_text.startswith('**')) or
                (selected_text.startswith('_') and selected_text.endswith('_') and len(selected_text) > 2)):
                is_italic = True
                actual_start = start_pos + 1
                actual_end = end_pos - 1
                italic_char = selected_text[0]
            # Check if selection is surrounded by * characters
            elif (start_pos >= 1 and end_pos <= len(full_text) - 1 and 
                  full_text[start_pos-1:start_pos] == '*' and 
                  full_text[end_pos:end_pos+1] == '*' and
                  (start_pos < 2 or full_text[start_pos-2:start_pos] != '**')):  # Not part of **bold**
                is_italic = True
                actual_start = start_pos - 1
                actual_end = end_pos + 1
                italic_char = '*'
            # Check if selection is surrounded by _ characters
            elif (start_pos >= 1 and end_pos <= len(full_text) - 1 and 
                  full_text[start_pos-1:start_pos] == '_' and 
                  full_text[end_pos:end_pos+1] == '_'):
                is_italic = True
                actual_start = start_pos - 1
                actual_end = end_pos + 1
                italic_char = '_'
            
            if is_italic:
                # Remove italic formatting
                cursor.setPosition(actual_start)
                cursor.setPosition(actual_end, QTextCursor.KeepAnchor)
                new_text = cursor.selectedText()
                if ((new_text.startswith('*') and new_text.endswith('*') and not new_text.startswith('**')) or
                    (new_text.startswith('_') and new_text.endswith('_'))):
                    new_text = new_text[1:-1]
                cursor.insertText(new_text)
                # Restore selection on the unformatted text
                cursor.setPosition(actual_start)
                cursor.setPosition(actual_start + len(new_text), QTextCursor.KeepAnchor)
            else:
                # Add italic formatting (using *)
                new_text = f"*{selected_text}*"
                cursor.insertText(new_text)
                # Restore selection on the formatted text (excluding the *)
                cursor.setPosition(start_pos + 1)
                cursor.setPosition(start_pos + 1 + len(selected_text), QTextCursor.KeepAnchor)
            
            self.setTextCursor(cursor)
        else:
            # No selection - insert italic formatting at cursor position
            cursor.insertText("**")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
            self.setTextCursor(cursor)
