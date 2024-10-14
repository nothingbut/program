import sys, logging, json, csv
from PySide6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QSplitter, QTreeWidget, QTableView, QHeaderView, QStatusBar, QTreeWidgetItem, QInputDialog
from PySide6.QtGui import QAction, QCursor, QIcon
from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtWebEngineWidgets import QWebEngineView
from bookproperties import BookProperties, BookStatus
from bsconfig import BookShelfConfig
from bookutils import BookUtils

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
        return len(self.header)

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
        self.initModel()
        self.initUI(parent)
        self.cat = None
        self.sub = None

    def initModel(self):
        self.chapterList = list()
        self.tocModel = TOCModel(self, self.chapterList)

    def initUI(self, parent=None):
        self.setWindowTitle("Nothing but bookshelf")
        self.resize(1600, 1200)

        toolbar = self.addToolBar("Toolbar")
        self.btImport = QAction("导入小说", self)
        self.btImport.triggered.connect(self.onImportBook)
        toolbar.addAction(self.btImport)
        self.btSave = QAction("保存书架", self)
        self.btSave.triggered.connect(self.onSaveShelf)        
        toolbar.addAction(self.btSave)

        statusbar = QStatusBar(self)
        self.setStatusBar(statusbar)

        self.mainSplitter = QSplitter(self)
        self.mainSplitter.setMinimumSize(200, 150)

        self.mainSplitter.setOrientation(Qt.Horizontal)
        
        self.shelfView = QTreeWidget(self.mainSplitter)
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
        self.tocView.customContextMenuRequested.connect(self.showContextMenu)
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

        self.initTagTree()
        self.shelfView.itemClicked.connect(self.onSelectBook)
        self.shelfView.itemExpanded.connect(self.onExpandCurrent)
        self.setCentralWidget(self.mainSplitter)

        self.loadShelf()
    
    def initTagTree(self):
        self.shelfView.setColumnCount(1)
        self.shelfView.setHeaderLabels(['书架'])
        allTags = BookShelfConfig().getTagsJson()
        for top in allTags:
            topItem = QTreeWidgetItem(self.shelfView)
            topItem.setText(0, top['cat'])
            for tag in top['sub']:
                tagItem = QTreeWidgetItem()
                tagItem.setText(0, tag)
                topItem.addChild(tagItem)
            self.shelfView.addTopLevelItem(topItem)
        
        otherItem = QTreeWidgetItem(self.shelfView)
        otherItem.setText(0, '其他')
        self.shelfView.addTopLevelItem(otherItem)
        
        self.shelfView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.shelfView.customContextMenuRequested.connect(self.showTreeItemMenu)

    def showTreeItemMenu(self, pos):
        item = self.shelfView.currentItem()
        if item is None:
            return
        if item.whatsThis(0) is None or item.whatsThis(0) == '':
            return
        popMenu = QMenu(self)

        self.modifyMetaAction = popMenu.addAction('修改')
        self.modifyMetaAction.triggered.connect(self.onModifyMeta)
        self.deleteBookAction = popMenu.addAction('删除')
        self.deleteBookAction.triggered.connect(self.onDeleteBook)
        self.packageBookAction = popMenu.addAction('打包')
        self.packageBookAction.triggered.connect(self.onPackageBook)
        self.generateBookAction = popMenu.addAction('生成')
        self.generateBookAction.triggered.connect(self.onGenerateEpub)
        
        popMenu.exec(QCursor.pos())
 
    def loadShelf(self):
        self.bookList = {'-1': None}
        self.curBook = '-1'
        with open('%s/shelf.csv' % BookShelfConfig().getBookShelf(), 'r') as f:
            reader = csv.reader(f)
            isHeader = True
            for item in reader:
                if isHeader:
                    isHeader = False
                    continue

                book = {'id': item[0], 'title': item[1], 'cat': item[2], 'sub': item[3], 'site': item[4], 'state': item[5], 'source': item[6], 'tags': [item[2], item[3], item[4], item[5]], 'status': BookStatus.none}
                try:
                    self.addBook2Shelf(book)
                except:
                    print(book)

    def loadBook(self, id):
        filename = '%s/%s.json' % (BookShelfConfig().getBookShelf(), id)
        with open(filename, 'r') as f:
            book = json.load(f)
            book['status'] = BookStatus.load
            self.bookList[id] = book

    def onModifyMeta(self):
        item = self.shelfView.currentItem()
        id = item.whatsThis(0)
        book = self.bookList[id]
        self.bookProperties = BookProperties(book=book)
        self.bookProperties.show()
        self.bookProperties.imported.connect(self.importBook)

    def onDeleteBook(self):
        item = self.shelfView.currentItem()
        self.deleteBook(item)

        if id == self.curBook:
            self.curBook = '-1'
            self.clearTocModel()

    def deleteBook(self, item):
        id = item.whatsThis(0)
        self.bookList[id]['status'] = BookStatus.delete
        item.parent().removeChild(item)
        
    def showContextMenu(self):
        self.tocView.contextMenu = QMenu(self)
        self.mergeChapterAction = self.tocView.contextMenu.addAction('合并章节')
        self.modifyVolumnAction = self.tocView.contextMenu.addAction('更改卷名')
        self.tocView.contextMenu.popup(QCursor.pos()) 
        self.mergeChapterAction.triggered.connect(self.onMergeChapter)
        self.modifyVolumnAction.triggered.connect(self.onModifyVolumn)
        self.tocView.contextMenu.show()

    def onMergeChapter(self):
        selections = self.tocView.selectedIndexes()
        if len(selections) < 2:
            return
        start = self.tocModel.rawIndex(selections[0].row())
        end = self.tocModel.rawIndex(selections[-1].row())
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

    def onModifyVolumn(self):
        volumn = volumn, ok = QInputDialog.getText(self, '更新卷名', '新的卷名')
        selections = self.tocView.selectedIndexes()
        start = self.tocModel.rawIndex(selections[0].row())
        end = self.tocModel.rawIndex(selections[-1].row())
        original = self.chapterList[start][1]
        for i in range(end, start - 1, -1):
            self.chapterList[i][1] = volumn
        if start > 0:
            previous = self.chapterList[start - 1]
            if previous[1] == 'volumn' and previous[0] == original:
                previous[0] = volumn
        self.tocModel = TOCModel(self, self.chapterList)
        self.tocView.setModel(self.tocModel)
        self.tocView.setColumnHidden(5, True)        

    def onImportBook(self, checked):
        self.bookProperties = BookProperties(blacklist=self.bookList.keys())
        self.bookProperties.show()
        self.bookProperties.imported.connect(self.importBook)

    def refreshTocModel(self, book):
        self.chapterList.clear()
        
        for chapter in book['chapters']:
            self.chapterList.append(chapter)

        self.tocModel = TOCModel(self, self.chapterList)

        self.tocView.setModel(self.tocModel)
        self.book = book

    def clearTocModel(self):
        self.chapterList.clear()
        self.tocModel = TOCModel(self, self.chapterList)
        self.tocView.setModel(self.tocModel)
        self.book = None

    def onPackageBook(self):
        BookUtils(self.book).packageBook()
        
    def onGenerateEpub(self):
        BookUtils(self.book).generateEpub()

    def showChapterContent(self):
        chapter = self.chapterList[self.tocModel.rawIndex(self.tocView.currentIndex().row())]
        self.chapterTab.setHtml(BookUtils(self.book).generateChapter(chapter))
        self.chapterTab.setVisible(True)

    def addBook2Shelf(self, book):
        topAmount = self.shelfView.topLevelItemCount()
        for top in range(0, topAmount):
            cat = self.shelfView.topLevelItem(top)
            if book['cat'] != cat.text(0):
                continue
            childAmount = cat.childCount()
            for idx in range(0, childAmount):
                if book['sub'] == cat.child(idx).text(0):
                    bookItem = QTreeWidgetItem()
                    bookItem.setText(0, book['title'])
                    bookItem.setWhatsThis(0, book['id'])
                    cat.child(idx).addChild(bookItem)

                    bookItem.childCount()

        self.bookList[book['id']] = book
        return bookItem

    def importBook(self, book):
        logging.debug('Invoking importBook ...')
        
        if book['status'] == BookStatus.modified:
            org = self.shelfView.currentItem()
            org.parent().removeChild(org)

        item = self.addBook2Shelf(book)
        last = self.updateCurentShelf(item.parent())
        if last is not None:
            logging.debug('item %s need to be collapsed' % last.text(0))
            self.collapseItem(last)
        self.refreshTocModel(book)
        self.shelfView.setCurrentItem(item)

    def onSelectBook(self, item, column):
        if item.whatsThis(0) == '':
            return
        self.curBook = item.whatsThis(0)
        book = self.bookList[self.curBook]
        if book['status'] == BookStatus.none:
            self.loadBook(self.curBook)
        self.refreshTocModel(self.bookList[self.curBook])

    def onExpandCurrent(self, item):
        last = self.updateCurentShelf(item)
        if last is not None:
            self.collapseItem(last)

        item.setExpanded(True)

    def collapseItem(self, item):
        for idx in range(item.childCount()):
            child = item.child(idx)
            if child.isExpanded():
                logging.debug('collapse %s ...' % child.text(0))
                self.shelfView.collapseItem(child)

        self.shelfView.collapseItem(item)

    def updateCurentShelf(self, item):
        logging.debug('update to %s' % item.text(0))
        if item.parent() is None:
            cat = item
            sub = None
        else:
            sub = item
            cat = item.parent()

        if cat == self.cat and sub is None:
            return None
        if sub == self.sub and sub is not None:
            return None
        returnItem = self.sub
        self.sub = sub
        if cat == self.cat:
            if self.sub is None:
                return None
            if returnItem is not None:
                logging.debug('from [%s] to [%s]' % (returnItem.text(0), self.sub.text(0)))

            return returnItem
        
        returnItem = self.cat
        self.cat = cat
        if returnItem is not None:
            logging.debug('from [%s] to [%s]' % (returnItem.text(0), self.cat.text(0)))

        return returnItem

    def onSaveShelf(self):
        self.saveBookList()

    def saveBookList(self):
        allBookIds = self.bookList.keys()
        bookSummaryList = list()
        for id in allBookIds:
            book = self.bookList[id]
            if book is None:
                continue
            if book['status'] == BookStatus.delete:
                continue
            bookSummaryList.append([book['id'], book['title'], book['cat'], book['sub'], book['site'], book['state'], book['source']])
            if book['status'] == BookStatus.modified or book['status'] == BookStatus.new:
                self.saveBook(book)

        with open('%s/shelf.csv' % BookShelfConfig().getBookShelf(), 'w') as f:
            writer = csv.writer(f)
            writer.writerows([['id', 'title', 'cat','sub','site','state','source']])
            writer.writerows(bookSummaryList)

    def saveBook(self, book):
        filename = '%s/%s.json' % (BookShelfConfig().getBookShelf(), book['id'])
        with open(filename, 'w') as f:
            book['status'] = None
            json.dump(book, f, ensure_ascii=False)
            book['status'] = BookStatus.load

def main():
    LOG_FORMAT = "[%(filename)s:<%(lineno)d>] %(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename='bsapp.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    logging.info("Start application .....")
    app = QApplication(sys.argv)
    mainWnd = BookshelfWnd()
    icon = QIcon("/Users/shichang/workspace/program/data/bookshelf.png")
    mainWnd.setWindowIcon(icon)
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)
    mainWnd.show()
    sys.exit(app.exec()) 

if __name__ == '__main__':
    main()