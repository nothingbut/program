import regex as re, string, sqlite3, requests, os, sys, shutil, json, logging, zipfile, rarfile
from pathlib import PurePath
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QMenu, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
from pathlib import Path
from enum import Enum
from bsconfig import BookShelfConfig
from utils.bookutils import BookUtils

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Origin': 'https://www.yousuu.com',
    'Referer': 'https://www.yousuu.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

class BookStatus(Enum):
    none = -1
    load = 0
    new = 1
    modified = 2
    delete = 3
    
class BookProperties(QWidget):
    imported = Signal(dict)

    def __init__(self, *, book=None, blacklist = None, debug = False):
        super().__init__()

        self.isDebug = debug

        if blacklist is None:
            self.blacklist = []
        else:
            self.blacklist = blacklist

        self.initUI()

        self.isNew = False
        if book is None:
            self.isNew = True
            self.book = {}
        else:
            self.book = book
            BookUtils(book).dumpBookMeta()
            self.fillFormFields()
            self.disableChangeSource()

    def initUI(self):
        self.resize(400, 300)

        layout = QVBoxLayout()

        self.basicInfo = QGridLayout()
        self.titleLabel = QLabel("书名")
        self.basicInfo.addWidget(self.titleLabel, 0, 0)
        self.authorLabel = QLabel("作者")
        self.basicInfo.addWidget(self.authorLabel, 1, 0)
        self.titleEdit = QLineEdit()
        self.basicInfo.addWidget(self.titleEdit, 0, 1)
        self.authorEdit = QLineEdit()
        self.basicInfo.addWidget(self.authorEdit, 1, 1)
        self.openFileBnt = QPushButton("...")
        self.openFileBnt.clicked.connect(self.onFileOpen)
        self.basicInfo.addWidget(self.openFileBnt, 2, 0)
        self.sourceInfo = QHBoxLayout()
        self.filepathEdit = QLineEdit()
        self.filepathEdit.setReadOnly(True)
        self.filepathEdit.textChanged.connect(self.onFilepathUpdate)
        self.sourceInfo.addWidget(self.filepathEdit)
        self.bookIdBox = QComboBox(self)
        self.sourceInfo.addWidget(self.bookIdBox)
        self.initBookIdCombo()
        self.basicInfo.addLayout(self.sourceInfo, 2, 1)

        self.infoPanel = QHBoxLayout()
        self.infoPanel.addLayout(self.basicInfo)
        self.coverLabel = QLabel()
        self.coverLabel.setFixedSize(84, 112)
        self.coverLabel.setText("无封面")
        self.coverLabel.setAlignment(Qt.AlignCenter)
        self.coverLabel.setScaledContents(True)
        self.infoPanel.addWidget(self.coverLabel)

        self.tagPanel = QHBoxLayout()
        self.descLabel = QLabel("简介")
        self.statusList = QComboBox()
        self.sitesList = QComboBox()
        self.parentTag = QComboBox()
        self.childTag = QComboBox()
        self.tagPanel.addWidget(self.descLabel)
        self.tagPanel.addWidget(self.statusList)
        self.tagPanel.addWidget(self.sitesList)
        self.tagPanel.addWidget(self.parentTag)
        self.tagPanel.addWidget(self.childTag)
        self.statusList.addItems(['连载', '完本', '太监'])
        self.initSourceComobo()
        self.initTagCombo()
        self.descEdit = QTextEdit()
        self.extraEdit = QTextEdit('volumn:')

        self.actionPanel = QHBoxLayout()
        self.autoFill = QPushButton("O")
        self.autoFill.clicked.connect(self.onRefreshFromDB)
        self.cancel = QPushButton("取消")
        self.cancel.clicked.connect(self.close)
        self.importBook = QPushButton("确定")
        self.importBook.clicked.connect(self.onBookImport)

        self.actionPanel.addWidget(self.autoFill)
        self.actionPanel.addWidget(self.cancel)
        self.actionPanel.addWidget(self.importBook)

        layout.addLayout(self.infoPanel)
        layout.addLayout(self.tagPanel)
        layout.addWidget(self.descEdit)
        layout.addWidget(self.extraEdit)
        layout.addLayout(self.actionPanel)

        self.setLayout(layout)

        self.coverMenu = QMenu(self)
        actionLoadCover = self.coverMenu.addAction("打开本地文件")
        actionLoadCover.triggered.connect(self.onCoverFileOpen)
        actionGenCover = self.coverMenu.addAction("生成默认封面")
        actionGenCover.triggered.connect(self.onDefaultCoverGen)

        self.coverLabel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.coverLabel.customContextMenuRequested.connect(self.showCoverMenu)

    def disableChangeSource(self):
        self.openFileBnt.setDisabled(True)
        self.filepathEdit.setDisabled(True)
        if not self.isDebug:
            self.bookIdBox.setDisabled(True)

    def initSourceComobo(self):
        for source in BookShelfConfig().getSourceList():
            self.sitesList.addItem(source)
        conn = sqlite3.connect(BookShelfConfig().getBookDB())
        querySite = 'select source, site from book_sitemap'
        cursor = conn.cursor()
        cursor.execute(querySite)
        self.sitemap = {}
        for row in cursor:
            self.sitemap[row[0]] = row[1]

    def initTagCombo(self):
        self.allTags = BookShelfConfig().getTagsJson()

        self.parentTag.addItem('--')
        for parent in self.allTags:
            self.parentTag.addItem(parent['category'])
        self.childTag.addItem('--')
        self.parentTag.activated.connect(self.onChildTagUpdate)

    def initBookIdCombo(self):
        self.bookIdBox.addItem('000000')
        self.bookDict = {'000000': None}
        conn = sqlite3.connect(BookShelfConfig().getBookDB())
        queryNovel = 'select id, title, author, brief, cover from book_novel where LB like \'0B%\' order by id'
        cursor = conn.cursor()
        cursor.execute(queryNovel)
        count = 1
        for row in cursor:
            if row[0] in self.blacklist:
                continue

            self.bookDict[row[0]] = {
                'title': row[1],
                'author': row[2],
                'cover': row[4],
                'brief': row[3]
            }
            self.bookIdBox.addItem(row[0])
            self.bookIdBox.model().item(count, 0).setToolTip('%s - %s' % (row[1], row[2]))
            count += 1

        self.bookIdBox.currentTextChanged.connect(self.onBookRefresh)

    def fillFormFields(self):
        logging.debug('Invoking fillFormFields ...')

        id = self.book['id']
        self.filepathEdit.setText(self.book['source'])
        self.titleEdit.setText(self.book['title'])
        self.authorEdit.setText(self.book['author'])
        self.descEdit.setText(self.book['desc'])
        self.bookIdBox.setCurrentIndex(self.mapId(id))

        if 'tags' in self.book.keys():
            tagIdx = self.mapTags(self.book['tags'])
            self.parentTag.setCurrentIndex(tagIdx[0])
            self.onChildTagUpdate(tagIdx[0])
            self.childTag.setCurrentIndex(tagIdx[1])

        if 'site' in self.book.keys():
            self.sitesList.setCurrentIndex(self.mapSite(self.book['site']))
        if 'state' in self.book.keys():
            self.statusList.setCurrentIndex(self.mapState(self.book['state']))

        if ('cover' in self.book.keys()) and (self.book['cover'] != None):
            self.coverfile = self.book['cover']
            try :
                image = QPixmap(self.book['cover']).scaled(self.coverLabel.size(), aspectMode=Qt.KeepAspectRatio)
                self.coverLabel.setPixmap(image)
            except:
                logging.error('load image error for %s' % self.book['cover'])
        else:
            self.coverfile = None
        
    def onBookRefresh(self):
        logging.debug('Invoking onBookRefresh ...')

        bookId = self.bookIdBox.currentText()
        if 'id' in self.book.keys() and bookId == self.book['id']:
            return
        
        self.book['id'] = bookId
        self.book['title'] = self.bookDict[bookId]['title']
        self.book['author'] = self.bookDict[bookId]['author']
        self.book['desc'] = self.bookDict[bookId]['brief']
        self.book['source'] = BookShelfConfig().getBookDB()
        self.coverfile = BookShelfConfig().getCoverPath() + '%s.jpg' % bookId
        if not os.path.exists(self.coverfile):
            sourcefile = '%s%s/%s' % (BookShelfConfig().getSourcePath() , bookId, self.bookDict[bookId]['cover'])
            try:
                shutil.copyfile(sourcefile, self.coverfile)
            except:
                logging.warning("cover copy failed.\nsource:  %s\ntarget: %s" % (sourcefile, self.coverfile))
                self.coverfile = None
        self.book['cover'] = self.coverfile

        bookEntity = self.queryByName(self.book['title'])
        if bookEntity != None:
            self.book['tags'] = bookEntity['tags'].replace('[', '').replace(']','').split(', ')
            self.book['site'] = bookEntity['site']
            self.book['state'] = bookEntity['state']

        self.fillFormFields()

    def onChildTagUpdate(self, index):
        logging.debug('Invoking onChildTagUpdate ...')

        self.childTag.clear()
        self.childTag.addItem('--')
        for child in self.allTags[index - 1]['subcategories']:
            self.childTag.addItem(child)

    def showCoverMenu(self, pos):
        self.coverMenu.exec(self.coverLabel.mapToGlobal(pos))

    def onCoverFileOpen(self):
        imageFile, _ = QFileDialog.getOpenFileName(self, '选择封面图片', BookShelfConfig().getCoverPath(), 'Image files (*.jpg *.png)')
        image = QPixmap(imageFile).scaled(self.coverLabel.size(), aspectMode=Qt.KeepAspectRatio)
        self.coverfile = imageFile
        self.coverLabel.setPixmap(image)

    def onDefaultCoverGen(self):
        pass

    def queryByName(self, name):
        logging.debug('Invoking queryByName with [%s] ...' % name)

        with sqlite3.connect(BookShelfConfig().getBookDB()) as conn:
            cur = conn.cursor()
            querystr = BookShelfConfig().getBookDetailQuery() % name
            try:
                cur.execute(querystr)
                for row in cur:
                    logging.debug(row)
                    return {
                        'id': row[0],
                        'title': row[1],
                        'author': row[2],
                        'desc': row[3],
                        'cover': row[4],
                        'tags': row[5],
                        'site': row[6],
                        'state': row[7]
                    }
            except:
                logging.warning("fail on %s" % querystr)
                return None

    def onRefreshFromDB(self):
        logging.debug('Invoking onRefreshFromDB ...')
        self.autofillInfo()
        
    def autofillInfo(self):
        logging.debug('Invoking autofillInfo ...')

        bookEntity = self.queryByName(self.titleEdit.text())
        if bookEntity is None:
            if 'id' not in self.book.keys():
                self.book['id'] = self.generateBookId()
            print(self.book['id'])
            return

        self.book['id'] = '%s' % bookEntity['id']
        self.book['title'] = self.titleEdit.text()
        self.book['author'] = bookEntity['author']
        self.book['desc'] = bookEntity['desc']
        self.book['source'] = self.filepathEdit.text()
        self.coverfile = BookShelfConfig().getCoverPath() + '%s.jpg' % bookEntity['id']
        if not os.path.exists(self.coverfile):
            with requests.get(bookEntity['cover'], stream=True) as response:
                with open(self.coverfile, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)

        self.book['cover'] = self.coverfile
        self.book['tags'] = bookEntity['tags'].replace('[', '').replace(']','').split(', ')
        self.book['site'] = bookEntity['site']
        self.book['state'] = bookEntity['state']

        self.fillFormFields()
 
    def mapTags(self, tags):
        logging.debug('Invoking mapTags from [%s] ...' % tags)

        index = -1
        for tag in tags:
            catIdx = 0
            for category in self.allTags:
                try:
                    return (catIdx + 1, category['subcategories'].index(tag) + 1)
                except:
                    pass
                if tag == category['category']:
                    index = catIdx
                    break
                catIdx += 1

        return (index + 1, 0)

    def mapSite(self, source):
        logging.debug('Invoking mapSite from [%s] ...' % source)

        if source in self.sitemap.keys():
            site = self.sitemap[source]
        else:
            site = source

        index = self.sitesList.findText(site)
        if index == -1:
            index = 0
        return index

    def mapState(self, state):
        logging.debug('Invoking mapState from [%s] ...' % state)

        if type(state) == int:
            return state
        match state: 
            case '连载':
                return 0
            case '完本':
                return 1
            case '太监':
                return 2
            case _:
                return -1
    
    def mapId(self, id):
        logging.debug('Invoking mapId from [%s] ...' % id)

        index = self.bookIdBox.findText(id)
        if index == -1:
            index = 0
        return index

    def onFilepathUpdate(self):
        logging.debug('Invoking onFilepathUpdate ...')

        self.book['filepath'] = self.filepathEdit.text()
        self.titleEdit.setText(PurePath(self.book['filepath']).name[0:-4])

    def onBookImport(self):
        logging.debug('Invoking onBookImport ...')

        # check book metadata
        if self.titleEdit.text() == '' or self.authorEdit.text() == '':
            QMessageBox.warning(self, "错误", "请填写完整的书籍信息")
            return
        # fill book metadata
        if self.bookIdBox.currentText() != '000000':
            self.book['id'] = self.bookIdBox.currentText()
        self.book['title'] = self.titleEdit.text()
        self.book['author'] = self.authorEdit.text()
        self.book['desc'] = self.descEdit.toPlainText()
        if self.coverfile is not None:
            self.book['cover'] = self.coverfile
        self.book['source'] = self.filepathEdit.text()
        if self.book['source'] == '':
            self.book['source'] = BookShelfConfig().getBookDB()
        self.book['category'] = self.parentTag.currentText()
        self.book['subcategory'] = self.childTag.currentText()
        self.book['site'] = self.sitesList.currentText()
        self.book['state'] = self.statusList.currentText()
        self.book['tags'] = ['%s' % self.book['category'], '%s' % self.book['subcategory'], '%s' % self.book['site'], '%s' % self.book['state']]

        if self.isNew is False:
            logging.debug('Modify metadata for [%s]' % self.book['title'])
            self.book['status'] = BookStatus.modified
            self.imported.emit(self.book)
            self.close()
            return

        self.book['status'] = BookStatus.new
        logging.debug("source is %s" % self.book['source'])
        if self.book['source'] == BookShelfConfig().getBookDB():
            self.book['chapters'] = []
            index = 0
            conn = sqlite3.connect(BookShelfConfig().getBookDB())
            queryNovel = 'select id, title, volumn from book_contents where novelid = \'%s\' order by displayorder' % self.book['id']
            logging.debug(queryNovel)
            cursor = conn.cursor()
            cursor.execute(queryNovel)
            pathsplitter = '/' if os.name == 'posix' else '\\'
            for row in cursor:
                self.book['chapters'].append([row[1], row[2], '%s%s%s%d.htm' % (BookShelfConfig().getSourcePath(), self.book['id'], pathsplitter, row[0]), 0, -1, index])
                index += 1
        else:
            # parse all chapters
            filepath = BookShelfConfig().getSourcePath()
            fileext = os.path.splitext(self.book['filepath'])[1]
            if fileext == ".txt":
                filepath = filepath + os.path.basename(self.book['filepath'])
                if self.book['filepath'] != filepath:
                    shutil.copyfile(self.book['filepath'], filepath)
            elif fileext == ".zip":
                source = zipfile.ZipFile(self.book['filepath'])
                ziplist = source.namelist()
                for item in ziplist:
                    source.extract(item, filepath)
                    filepath = filepath + item
                    logging.debug("file path as %s" % filepath)
                    break
            elif fileext == ".rar":
                source = rarfile.RarFile(self.book['filepath'])
                rarlist = source.namelist()
                for item in rarlist:
                    source.extract(item, filepath)
                    filepath = filepath + item
                    logging.debug("file path as %s" % filepath)
                    break
            else:
                logging.error("incorrect import file: %s" % fileext)
                return

            BookUtils().encode2utf8(filepath)
            self.book['filepath'] = filepath
            self.book['source'] = filepath

            with open(filepath, "r", encoding="utf-8") as fp:
                content = fp.read()
                lines = content.rsplit("\n")
                self.book['chapters'] = self.identifyChapters(filepath, lines)
                self.arrangeVolumns(lines)

        logging.debug('Adding new book [%s]' % self.book['title'])
        self.imported.emit(self.book)
        self.close()

    def identifyChapters(self, filepath, lines):
        logging.debug('Invoking identifyChapters ...')

        chapters = []
        start = 0
        empty = 0
        index = 0

        extraText = self.extraEdit.toPlainText()
        prefixes = extraText.rsplit("\n")
        prefixes.append('')
        for line in lines:
            start += 1
            type = self.detectsubject(line, prefixes)

            if type == 'ending':
                break
            if type == 'empty':
                empty += 1
            if type.startswith('subject:'):
                if chapters.__len__() > 0:
                    chapters[chapters.__len__() - 1][4] = start - 1 - empty
                chapter = [line,type.replace('subject:',''),filepath,start,0,index]
                chapters.append(chapter)
                empty = 0
                index += 1

        if chapters.__len__() > 0:
            chapters[chapters.__len__() - 1][4] = start - 1 - empty
        return chapters

    def arrangeVolumns(self, lines):
        logging.debug('Invoking arrangeVolumns ...')

        curvol = '正文'
        for chapter in self.book['chapters']:
            chapter[4] = chapter[4] - chapter[3]
            backfill = False
            if chapter[4] > 3:
                backfill = True
            else:
                for idx in range(chapter[3], chapter[3] + chapter[4]):
                    if len(lines[idx]) > 100:
                        backfill = True
                        chapter[1] = curvol
                        break

            if chapter[1] == '':
                if backfill:
                    chapter[1] = curvol
                else:
                    chapter[1] = 'volumn'
                    curvol = chapter[0]

    def onFileOpen(self):
        filePath = QFileDialog.getOpenFileName(self, '导入文字（可压缩）小说', BookShelfConfig().getSourcePath(), '小说文件 (*.txt *.zip *.rar)')
        if filePath[0] != '':
            self.filepathEdit.setText(filePath[0])
            self.autofillInfo()

    def detectsubject(self, line, prefixes):
        if line in string.whitespace:
            return 'empty'
        endTags = BookShelfConfig().getTextEndingList()
        for tag in endTags:
            if tag == line:
                return 'ending'
        subjectTags = BookShelfConfig().getTextSubjectList()
        for tag in subjectTags:
            for prefix in prefixes:
                if re.match(tag % prefix, line):
                    return 'subject:%s' % prefix
        return 'content'

    def generateBookId(self):
        conn = sqlite3.connect(BookShelfConfig().getBookDB())
        queryMaxId = 'select max(id) from book_id'
        cursor = conn.cursor()
        cursor.execute(queryMaxId)
        newId = 0
        for row in cursor:
            if row is not None and row[0] is not None:
                newId = int(row[0])
        queryAddId = 'insert into book_id values(%d)' % (newId + 1)
        cursor.execute(queryAddId)
        cursor.close()
        conn.commit()
        conn.close()

        return '09%04d' % (newId + 1)

if __name__ == '__main__':
    LOG_FORMAT = "[%(filename)s:<%(lineno)d>] %(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename='bsprop.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    filename = '%s/%s.json' % (BookShelfConfig().getBookShelf(), '000132')
    with open(filename, 'r') as f:
        book = json.load(f)

    app = QApplication(sys.argv)
#   bookProperties = BookProperties(book=book, blacklist = ['000001','000002'], debug = True)
    bookProperties = BookProperties(debug=True)
    bookProperties.show()
    sys.exit(app.exec()) 