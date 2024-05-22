import regex as re, chardet, string, sqlite3, json, requests, os, sys
from pathlib import Path, PurePath
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QMenu, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

class BookProperties(QWidget):
    imported = Signal(dict)

    def __init__(self, book = None):
        super().__init__()

        self.resize(400, 300)
        if book is None:
            self.book = {}
        else:
            self.book = book

        layout = QVBoxLayout()

        self.basicInfo = QGridLayout()
        self.titleLabel = QLabel("书名")
        self.basicInfo.addWidget(self.titleLabel, 0, 0)
        self.authorLabel = QLabel("作者")
        self.basicInfo.addWidget(self.authorLabel, 1, 0)
        self.titleEdit = QLineEdit(self.book.get('title'))
        self.basicInfo.addWidget(self.titleEdit, 0, 1)
        self.authorEdit = QLineEdit(self.book.get('author'))
        self.basicInfo.addWidget(self.authorEdit, 1, 1)
        self.openFileBnt = QPushButton("...")
        self.openFileBnt.clicked.connect(self.openFile)
        self.basicInfo.addWidget(self.openFileBnt, 2, 0)
        self.filepathEdit = QLineEdit(self.book.get('filepath'))
        self.filepathEdit.setReadOnly(True)
        self.filepathEdit.textChanged.connect(self.updateFilePath)
        self.basicInfo.addWidget(self.filepathEdit, 2, 1)

        self.infoPanel = QHBoxLayout()
        self.infoPanel.addLayout(self.basicInfo)
        self.coverLabel = QLabel()
        self.coverLabel.setMinimumSize(80, 60)
        self.coverLabel.setText("无封面")
        self.coverLabel.setAlignment(Qt.AlignCenter)
        self.coverLabel.setScaledContents(True)
        self.infoPanel.addWidget(self.coverLabel)

        self.tagPanel = QHBoxLayout()
        self.descLabel = QLabel("简介")
        self.parentTag = QComboBox()
        self.childTag = QComboBox()
        self.tagPanel.addWidget(self.descLabel)
        self.tagPanel.addWidget(self.parentTag)
        self.tagPanel.addWidget(self.childTag)
        self.initTagComboBox()
        self.descEdit = QTextEdit(self.book.get('desc'))

        self.actionPanel = QHBoxLayout()
        self.autoFill = QPushButton("O")
        self.autoFill.clicked.connect(self.autofillInfo)
        self.cancel = QPushButton("取消")
        self.cancel.clicked.connect(self.close)
        self.importBook = QPushButton("导入")
        self.importBook.clicked.connect(self.importBookInfo)

        self.actionPanel.addWidget(self.autoFill)
        self.actionPanel.addWidget(self.cancel)
        self.actionPanel.addWidget(self.importBook)

        layout.addLayout(self.infoPanel)
        layout.addLayout(self.tagPanel)
        layout.addWidget(self.descEdit)
        layout.addLayout(self.actionPanel)

        self.setLayout(layout)

        self.coverMenu = QMenu(self)
        actionLoadCover = self.coverMenu.addAction("打开本地文件")
        actionLoadCover.triggered.connect(self.openCoverFile)
        actionGenCover = self.coverMenu.addAction("生成默认封面")
        actionGenCover.triggered.connect(self.genDefaultCover)

        self.coverLabel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.coverLabel.customContextMenuRequested.connect(self.showCoverMenu)

    def initTagComboBox(self):
        self.allTags = []
        with open('/Users/shichang/Workspace/programing/data/tags.json','r') as fp:
            self.allTags = json.load(fp)

        self.parentTag.addItem('--')
        for parent in self.allTags:
            self.parentTag.addItem(parent['cat'])
        self.childTag.addItem('--')
        self.parentTag.activated.connect(self.updateChildTag)

    def updateChildTag(self, index):
        self.childTag.clear()

        self.childTag.addItem('--')
        for child in self.allTags[index - 1]['sub']:
            self.childTag.addItem(child)

    def showCoverMenu(self, pos):
        self.coverMenu.exec(self.coverLabel.mapToGlobal(pos))

    def openCoverFile(self):
        imageFile, _ = QFileDialog.getOpenFileName(self, '选择封面图片', '/Users/shichang/Workspace/programing/data/cover', 'Image files (*.jpg *.png)')
        image = QPixmap(imageFile).scaled(self.coverLabel.size(), aspectMode=Qt.KeepAspectRatio)
        self.coverfile = imageFile
        self.coverLabel.setPixmap(image)

    def genDefaultCover(self):
        pass

    def autofillInfo(self):
        conn = sqlite3.connect('/Users/shichang/Workspace/programing/data/yousuu.db')
        cur = conn.cursor()
        querystr = 'select id, title, author, desc, cover, tags from main.book_info where title = \'%s\'' % self.titleEdit.text()
        cur.execute(querystr)
        for row in cur:
            self.authorEdit.setText(row[2])
            self.descEdit.setText(row[3])
            self.coverfile = '/Users/shichang/Workspace/programing/data/cover/%s.jpg' % row[0]
            if os.path.exists(self.coverfile) == False:
                response = requests.get(row[4], stream=True)
                with open(self.coverfile, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            image = QPixmap(self.coverfile).scaled(self.coverLabel.size(), aspectMode=Qt.KeepAspectRatio)
            self.coverLabel.setPixmap(image)

            tagIdx = self.mapTags(row[5])
            self.parentTag.setCurrentIndex(tagIdx[0])
            self.updateChildTag(tagIdx[0])
            self.childTag.setCurrentIndex(tagIdx[1])

            break
        cur.close()
        conn.close()

    def mapTags(self, input):
        tags = input.replace('[', '').replace(']','').split(', ')
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
    def updateFilePath(self):
        self.book['filepath'] = self.filepathEdit.text()
        self.titleEdit.setText(PurePath(self.book['filepath']).name[0:-4])
        self.autofillInfo()

    def encode2utf8(self, filepath):
        with open(filepath, 'rb') as file:
            data = file.read(20000)
            dicts = chardet.detect(data)
        encode = dicts["encoding"]
        if encode != 'utf-8' and encode != 'UTF-8-SIG':
            if 'GB' or 'gb' in encode:
                encode = 'gbk'
            else:
                pass
            print("文件编码不是utf-8,开始转换.....")
            fpr = open(filepath, 'r', encoding=encode, errors="ignore")
            filecontent = fpr.read()
            fpr.close()
            fpw = open(filepath, 'w', encoding="utf-8", errors="ignore")
            fpw.write(filecontent)
            fpw.close()

    def importBookInfo(self):
        # check book metadata
        if self.titleEdit.text() == '' or self.authorEdit.text() == '':
            QMessageBox.warning(self, "错误", "请填写完整的书籍信息")
            return
        # fill book metadata
        self.book['title'] = self.titleEdit.text()
        self.book['author'] = self.authorEdit.text()
        self.book['desc'] = self.descEdit.toPlainText()
        self.book['cover'] = self.coverfile
        self.book['source'] = self.filepathEdit.text()
        self.book['tags'] = ['%s' % self.parentTag.currentText(), '%s' % self.childTag.currentText()]

        # parse all chapters
        filepath = self.book['filepath']
        self.encode2utf8(filepath)
        fp = open(filepath,'r', encoding="utf-8")
        content = fp.read()
        fp.close

        self.book['chapters'] = []
        lines = content.rsplit("\n")
        start = 0
        empty = 0
        index = 0
        for line in lines:
            start += 1
            subject = BookProperties.detectsubject(line)

            if subject == 'ending':
                break
            if subject == 'empty':
                empty += 1
            if subject == 'subject':
                chapters = self.book['chapters']
                if chapters.__len__() > 0:
                    chapters[chapters.__len__() - 1][4] = start - 1 - empty
                chapter = {}
                chapter[0] = line
                chapter[1] = ''
                chapter[2] = filepath
                chapter[3] = start
                chapter[4] = 0
                chapter[5] = index
                chapters.append(chapter)
                empty = 0
                index += 1

        chapters = self.book['chapters']
        if chapters.__len__() > 0:
            chapters[chapters.__len__() - 1][4] = start - 1 - empty

        print("导入书籍信息完成!")
        self.arrangeVolumns()
        self.imported.emit(self.book)
        self.close()

    def arrangeVolumns(self):
        curvol = '正文'
        for chapter in self.book['chapters']:
            length = chapter[4] - chapter[3]
            if  length <= 3:
                chapter[1] = 'volumn'
                curvol = chapter[0]
            else:
                chapter[1] = curvol
            chapter[4] = length

    def openFile(self):
        filePath = QFileDialog.getOpenFileName(self, '导入txt小说', '/Users/shichang/Downloads/temp/zxcs/', 'Text files (*.txt)')
        self.filepathEdit.setText(filePath[0])

    def detectsubject(line):
        if line in string.whitespace:
            return 'empty'
        if line == '（全书完）' or line == '《全本完》':
            return 'ending'
        if re.match(r'^\s*(楔子|序章|序言|序 |引子|终幕|后记).*',line):
            return 'subject'
        if re.match(r'^\s*[第卷][0123456789一二三四五六七八九十零〇百千两]*[章回部节集卷][:： ].*',line):
            return 'subject'
        return 'content'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    bookProperties = BookProperties()
    bookProperties.show()
    sys.exit(app.exec()) 