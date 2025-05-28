from PySide6.QtWidgets import QMainWindow, QFileDialog, QColorDialog, QErrorMessage, QApplication
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QColor
from PySide6.QtCore import Qt, QSettings
import sys
import ctypes
import platform

from .config import Config
from .main_widget import MainWidget

class MainWindow(QMainWindow):
    def __init__(self, text_size=12):
        super().__init__()
        self.setup_ui(text_size)

    def setup_ui(self, text_size):
        self.setObjectName("MainWindow")
        self.setWindowTitle(Config.application_name)
        self.settings = QSettings(Config.organization_name, Config.application_name)
        self.main_widget = MainWidget(text_size)
        self.setCentralWidget(self.main_widget)

        my_icon = QIcon()
        my_icon.addFile('resources/marky.png')
        self.setWindowIcon(my_icon)

        if platform.system() == 'Windows':
            myappid = u'henchoz.marky.0-1'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        desktop = QApplication.primaryScreen()
        screen_rect = desktop.availableGeometry()
        window_width = int(screen_rect.width() * 0.5)
        window_height = int(screen_rect.height() * 0.5)
        self.setGeometry(
            int((screen_rect.width() - window_width) / 2),
            int((screen_rect.height() - window_height) / 2),
            window_width,
            window_height
        )

        self.create_shortcuts()

    def create_shortcuts(self):
        self.shortcuts = {
            'open': (QKeySequence("Ctrl+O"), self.open_file),
            'save': (QKeySequence("Ctrl+S"), self.save_file),
            'save_as': (QKeySequence("Ctrl+Shift+S"), self.save_file_as),
            'copy_html': (QKeySequence("Ctrl+Shift+C"), self.copy_as_html),
            'new': (QKeySequence("Ctrl+N"), self.new_file),
            'change_color': (QKeySequence("Ctrl+K"), self.select_colors),
            'toggle_bold': (QKeySequence("Ctrl+B"), self.main_widget.toggle_bold),
            'toggle_italic': (QKeySequence("Ctrl+I"), self.main_widget.toggle_italic),
            'exit': (QKeySequence(Qt.Key_Escape), sys.exit)
        }
        for key, (seq, func) in self.shortcuts.items():
            shortcut = QShortcut(seq, self)
            shortcut.activated.connect(func)

    def select_colors(self):
        fg = QColorDialog.getColor(QColor('green'), self, "Select Text Color")
        bg = QColorDialog.getColor(QColor('black'), self, "Select Background Color")
        if fg.isValid() and bg.isValid():
            self.main_widget.change_colors(bg.name(), fg.name())

    def new_file(self):
        self.main_widget.setPlainText("")
        self.current_file_path = None

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*.*)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.main_widget.setPlainText(file.read())
            self.current_file_path = file_path

    def _save_file(self, file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.main_widget.toPlainText())
        self.current_file_path = file_path

    def copy_as_html(self):
        import mistune
        import klembord
        markdown_text = self.main_widget.toPlainText()
        html_text = mistune.markdown(markdown_text)
        klembord.init()
        klembord.set_with_rich_text(markdown_text, html_text)

    def save_file(self):
        try:
            self._save_file(self.current_file_path)
        except AttributeError:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save As...", "", "Text Files (*.txt);;All Files (*.*)")
        if file_path:
            self._save_file(file_path)

    def show_error_message(self, message):
        error_dialog = QErrorMessage(self)
        error_dialog.showMessage(message)
