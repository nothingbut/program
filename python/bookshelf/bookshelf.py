import sys, mkepub
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QSplitter, QTreeView, QTableView, QFrame, QHeaderView, QStatusBar
from PySide6.QtGui import QAction, QCursor
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtWebEngineWidgets import QWebEngineView
from bookproperties import BookProperties
from bsconfig import BookShelfConfig

cssfile = '/Users/shichang/Workspace/program/data/epub.css'
targettemp = '/Users/shichang/Workspace/program/data/%s.epub'

class TOCModel(QAbstractTableModel):
    def __init__(self, parent, chaptersList, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.reload(chaptersList)
        
    def reload(self, chaptersList):
        self.header = ['章节','分卷','来源','开始于','行数','#']
        self.chaptersList = [item for item in chaptersList if item[1]!= 'delete' and item[1]!= 'volumn']

    def rowCount(self, parent = None):
        return len(self.chaptersList)
    
    def columnCount(self, parent = None):
        return len(self.chaptersList[0])
    
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.chaptersList[index.row()][index.column()]
    
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None
    
    def rawIndex(self, row):
        return self.chaptersList[row][5]

class BookshelfWnd(QMainWindow):
    def __init__(self,parent=None):
        super(BookshelfWnd, self).__init__(parent)
        self.initConfig()
        self.initModel()
        self.initUI(parent)

    def initConfig(self):
        self.config = BookShelfConfig()
    def initModel(self):
        self.chapterList = [('','','','','','')]
        self.tocModel = TOCModel(self, self.chapterList)

    def initUI(self, parent=None):
        self.setWindowTitle("Nothing but bookshelf")
        self.resize(1600, 1200)

        toolbar = self.addToolBar("Toolbar")
        self.btImport = QAction("导入txt小说", self)
        self.btImport.triggered.connect(self.onImportText)
        toolbar.addAction(self.btImport)
        self.btBuild = QAction("生成epub小说", self)
        self.btBuild.triggered.connect(self.onGenerateEpub)
        self.btBuild.setEnabled(False)
        toolbar.addAction(self.btBuild)

        statusbar = QStatusBar(self)
        self.setStatusBar(statusbar)

        self.mainSplitter = QSplitter(self)
        self.mainSplitter.setMinimumSize(200, 150)

        self.mainSplitter.setOrientation(Qt.Horizontal)
        
        self.shelfView = QTreeView(self.mainSplitter)
        self.mainSplitter.addWidget(self.shelfView)

        self.rightSplitter = QSplitter(self.mainSplitter)
        self.rightSplitter.setOrientation(Qt.Vertical)
        self.tocView = QTableView(self.rightSplitter)
        self.tocView.setModel(self.tocModel)
        self.tocView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tocView.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tocView.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tocView.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tocView.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.tocView.setEditTriggers(QTableView.NoEditTriggers)
        self.tocView.setSelectionBehavior(QTableView.SelectRows)
        self.tocView.setColumnHidden(5, True)
        
        self.tocView.horizontalHeader().setStretchLastSection(True)
        self.tocView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tocView.customContextMenuRequested.connect(self.showMergeMenu)
        self.tocView.clicked.connect(self.showChapterContent)
        
        self.rightSplitter.addWidget(self.tocView)
        
        self.bottomSplitter = QSplitter(self.rightSplitter)
        self.bottomSplitter.setOrientation(Qt.Horizontal)
        self.bookinfoTab = QTableView(self.bottomSplitter)
        self.bookinfoTab.setVisible(False)
        self.bottomSplitter.addWidget(self.bookinfoTab)
        self.chapterTab = QWebEngineView(self.bottomSplitter)
        self.chapterTab.setVisible(False)
        self.bottomSplitter.addWidget(self.chapterTab)

        self.rightSplitter.addWidget(self.bottomSplitter)
        self.rightSplitter.setSizes([1000, 1000])

        self.mainSplitter.addWidget(self.rightSplitter)
        self.mainSplitter.setSizes([1000, 5000])

        self.setCentralWidget(self.mainSplitter)
    
    def showMergeMenu(self):
        self.tocView.contextMenu = QMenu(self)
        self.mergeChapterAction = self.tocView.contextMenu.addAction('合并章节')
        self.tocView.contextMenu.popup(QCursor.pos()) 
        self.mergeChapterAction.triggered.connect(self.onMergeChapter)
        self.tocView.contextMenu.show()

    def onMergeChapter(self):
        selection = self.tocView.selectedIndexes()
        if len(selection) < 2:
            return
        start = self.tocModel.rawIndex(selection[0].row())
        end = self.tocModel.rawIndex(selection[-1].row())
        count = 0
        for i in range(end, start - 1, -1):
            count += self.chapterList[i][4]
            if i > start:
                self.chapterList[i][4] = 0
                self.chapterList[i][1] = 'delete'
        self.chapterList[start][4] = count
        self.tocModel = TOCModel(self, self.chapterList)
        self.tocView.setModel(self.tocModel)
        self.tocView.setColumnHidden(5, True)

    def onImportText(self, checked):
        # Code to import book text file
        self.bookProperties = BookProperties()
        self.bookProperties.show()
        self.bookProperties.imported.connect(self.refreshTocModel)
        self.btBuild.setEnabled(True)

    def refreshTocModel(self, bookData):
        self.chapterList.clear()
        for chapter in bookData['chapters']:
            self.chapterList.append(chapter)
        self.tocModel = TOCModel(self, self.chapterList)
        self.tocView.setModel(self.tocModel)
        self.book = bookData
        self.preloadContent()
    def generateChapter(self, chapter):
        curcontent = ['<h2 id=\"title\">%s</h2>' % chapter[0]]
        for idx in range(chapter[3], chapter[3] + chapter[4]):
            curcontent.append('<p>%s</p>' % self.lines[idx].strip())
        return ''.join(curcontent)

    def preloadContent(self):
        with open(self.book['source'],'r', encoding="utf-8") as fp:
            content = fp.read()
            self.lines = content.rsplit("\n")
    def onGenerateEpub(self):
        book = mkepub.Book(title=self.book['title'],author=self.book['author'],description=self.book['desc'],subjects=self.book['tags'])
        with open(self.book['cover'], 'rb') as file:
            book.set_cover(file.read())

        with open(self.config.getCSSFile()) as file:
            book.set_stylesheet(file.read())

        volpage = None
        for chapter in self.chapterList:
            if chapter[1] == 'delete':
                continue
            curcontent = self.generateChapter(chapter)

            if chapter[1] == 'volumn':
                volpage = book.add_page(chapter[0], curcontent)
                continue
            book.add_page(chapter[0], curcontent, volpage)

        targetfile = self.config.getTargetFile() % book.title
        book.save(targetfile)

    def showChapterContent(self):
        chapter = self.chapterList[self.tocModel.rawIndex(self.tocView.currentIndex().row())]
        self.chapterTab.setHtml(self.generateChapter(chapter))
        self.chapterTab.setVisible(True)
def main():
    app = QApplication(sys.argv)
    mainWnd = BookshelfWnd()
    mainWnd.show()
    sys.exit(app.exec()) 

if __name__ == '__main__':
    main()