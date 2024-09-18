import regex as re, string, sqlite3, requests, os, sys, shutil, json, logging
from pathlib import PurePath
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QMenu, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
from bsconfig import BookShelfConfig
from enum import Enum
from bookutils import BookUtils
from pathlib import Path

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

    def __init__(self, book = None):
        super().__init__()

        self.initUI()

        if book is None:
            self.book = {}
        else:
            self.book = book
            self.fillBookFields()

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
        self.openFileBnt.clicked.connect(self.openFile)
        self.basicInfo.addWidget(self.openFileBnt, 2, 0)
        self.sourceInfo = QHBoxLayout()
        self.filepathEdit = QLineEdit()
        self.filepathEdit.setReadOnly(True)
        self.filepathEdit.textChanged.connect(self.updateFilePath)
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
        self.autoFill.clicked.connect(self.autofillInfo)
        self.cancel = QPushButton("取消")
        self.cancel.clicked.connect(self.close)
        self.importBook = QPushButton("确定")
        self.importBook.clicked.connect(self.importBookInfo)

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
        actionLoadCover.triggered.connect(self.openCoverFile)
        actionGenCover = self.coverMenu.addAction("生成默认封面")
        actionGenCover.triggered.connect(self.genDefaultCover)

        self.coverLabel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.coverLabel.customContextMenuRequested.connect(self.showCoverMenu)

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
            self.parentTag.addItem(parent['cat'])
        self.childTag.addItem('--')
        self.parentTag.activated.connect(self.updateChildTag)

    def initBookIdCombo(self):
        self.bookIdBox.addItem('000000')
        self.bookDict = {'000000': None}
        conn = sqlite3.connect(BookShelfConfig().getBookDB())
        queryNovel = 'select id, title, author, brief, cover from book_novel where LB like \'0B%\' order by id'
        cursor = conn.cursor()
        cursor.execute(queryNovel)
        count = 1
        for row in cursor:
            self.bookDict[row[0]] = {
                'title': row[1],
                'author': row[2],
                'cover': row[4],
                'brief': row[3]
            }
            self.bookIdBox.addItem(row[0])
            self.bookIdBox.model().item(count, 0).setToolTip('%s - %s' % (row[1], row[2]))
            count += 1

        self.bookIdBox.currentTextChanged.connect(self.refreshBook)

    def fillBookFields(self):
        id = self.book['id']
        self.filepathEdit.setText(self.book['source'])
        self.titleEdit.setText(self.book['title'])
        self.authorEdit.setText(self.book['author'])
        self.descEdit.setText(self.book['desc'])
        self.bookIdBox.setCurrentIndex(self.mapId(id))

        tagIdx = self.mapTags(self.book['tags'])
        self.parentTag.setCurrentIndex(tagIdx[0])
        self.updateChildTag(tagIdx[0])
        self.childTag.setCurrentIndex(tagIdx[1])

        self.sitesList.setCurrentIndex(self.mapSite(self.book['site']))
        self.statusList.setCurrentIndex(self.mapState(self.book['state']))

        if self.book['cover'] != None:
            logging.debug(self.coverLabel.size())
            image = QPixmap(self.book['cover']).scaled(self.coverLabel.size(), aspectMode=Qt.KeepAspectRatio)
            self.coverLabel.setPixmap(image)
        
    def refreshBook(self):
        bookId = self.bookIdBox.currentText()
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
        self.fillBookFields()

    def updateChildTag(self, index):
        self.childTag.clear()

        self.childTag.addItem('--')
        for child in self.allTags[index - 1]['sub']:
            self.childTag.addItem(child)

    def showCoverMenu(self, pos):
        self.coverMenu.exec(self.coverLabel.mapToGlobal(pos))

    def openCoverFile(self):
        imageFile, _ = QFileDialog.getOpenFileName(self, '选择封面图片', BookShelfConfig().getCoverPath(), 'Image files (*.jpg *.png)')
        image = QPixmap(imageFile).scaled(self.coverLabel.size(), aspectMode=Qt.KeepAspectRatio)
        self.coverfile = imageFile
        self.coverLabel.setPixmap(image)

    def genDefaultCover(self):
        pass

    def queryByName(self, name):
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

    def autofillInfo(self):
        bookEntity = self.queryByName(self.titleEdit.text())
        if bookEntity is None:
            self.book['id'] = '-1'
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
        self.fillBookFields()
 
    def mapTags(self, tags):
        index = -1
        for tag in tags:
            catIdx = 0
            for cat in self.allTags:
                try:
                    return (catIdx + 1, cat['sub'].index(tag) + 1)
                except:
                    pass
                if tag == cat['cat']:
                    index = catIdx
                    break
                catIdx += 1

        return (index + 1, 0)

    def mapSite(self, source):
        if source in self.sitemap.keys():
            site = self.sitemap[source]
        else:
            site = source

        index = self.sitesList.findText(site)
        if index == -1:
            index = 0
        return index

    def mapState(self, state):
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
        logging.debug('current id is %s' % id)
        index = self.bookIdBox.findText(id)
        if index == -1:
            index = 0
        return index

    def updateFilePath(self):
        self.book['filepath'] = self.filepathEdit.text()
        self.titleEdit.setText(PurePath(self.book['filepath']).name[0:-4])
        self.autofillInfo()

    def importBookInfo(self):
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
        self.book['cover'] = self.coverfile
        self.book['source'] = self.filepathEdit.text()
        if self.book['source'] == '':
            self.book['source'] = BookShelfConfig().getBookDB()
        self.book['cat'] = self.parentTag.currentText()
        self.book['sub'] = self.childTag.currentText()
        self.book['site'] = self.sitesList.currentText()
        self.book['state'] = self.statusList.currentText()
        self.book['tags'] = ['%s' % self.book['cat'], '%s' % self.book['sub'], '%s' % self.book['site'], '%s' % self.book['state']]

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
                logging.debug(row)
                self.book['chapters'].append([row[1], row[2], '%s%s%s%d.htm' % (BookShelfConfig().getSourcePath(), self.book['id'], pathsplitter, row[0]), 0, -1, index])
                index += 1
        else:
            # parse all chapters
            filepath = BookShelfConfig().getSourcePath() + os.path.basename(self.book['filepath'])
            shutil.copyfile(self.book['filepath'], filepath)
            BookUtils().encode2utf8(filepath)
            self.book['filepath'] = filepath
            self.book['source'] = filepath
            fp = open(filepath,'r', encoding="utf-8")
            content = fp.read()
            fp.close()

            lines = content.rsplit("\n")

            self.book['chapters'] = self.identifyChapters(filepath, lines)
            self.arrangeVolumns(lines)

        self.imported.emit(self.book)
        self.close()

    def identifyChapters(self, filepath, lines):
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

    def openFile(self):
        filePath = QFileDialog.getOpenFileName(self, '导入txt小说', BookShelfConfig().getSourcePath(), 'Text files (*.txt)')
        self.filepathEdit.setText(filePath[0])

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

if __name__ == '__main__':
    LOG_FORMAT = "[%(filename)s:<%(lineno)d>] %(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename='bsprop.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    filename = '%s/%s.json' % (BookShelfConfig().getBookShelf(), '000003')
    with open(filename, 'r') as f:
        book = json.load(f)

    app = QApplication(sys.argv)
    bookProperties = BookProperties(book)
    bookProperties.show()
    sys.exit(app.exec()) 