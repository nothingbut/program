import sys
from PySide6.QtWidgets import QApplication
from ux.bookshelf import BookshelfWnd

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BookshelfWnd()
    window.show()
    sys.exit(app.exec())