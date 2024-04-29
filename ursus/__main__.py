import sys
from PySide6.QtWidgets import QApplication
from .config import Config
from .main_window import MainWindow

def main():
    app = QApplication(["Marky"])
    app.setApplicationName(Config.application_name)
    app.setOrganizationName(Config.organization_name)
    app.setOrganizationDomain(Config.domain)
    main_window = MainWindow(text_size=20)
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
