from bsconfig import BookShelfConfig
import mkepub, shutil, zipfile, chardet, os, yaml, logging, re
from pathlib import Path
#import sqlite3, csv

EMPTY_LINE = "\n"
BREAK_LINE = "<br />|<br >|<br>"
TITLE_VOLUMN = "# "
TITLE_CHAPTER = "## "
class BookUtils:
    def __init__(self, book = None):
        if book != None:
            self.id = book['id']
            self.title = book['title']
            self.author = book['author']
            self.desc = book['desc']
            self.coverfile = book['cover']
            self.tags = ','.join(book['tags'])
            self.source = book['source']
            self.chapters = book['chapters']
            self.rootpath = BookShelfConfig().getTargetPath() + "%s-%s/" % (self.title, self.author)
            self.lines = None

    def dumpBookMeta(self):
        logging.debug('Dump Book Meta:')
        logging.debug('id is [%s]' % self.id)
        logging.debug('title: [%s]' % self.title)
        logging.debug('author: [%s]' % self.author)
        logging.debug('tags: [%s]' % self.tags)

    def loadFromPandocSource(self, source):
        pass

    def getChapterLines(self, chapter):
        if self.source == BookShelfConfig().getBookDB():
            filepath = chapter[2]
            self.encode2utf8(filepath)
            with open(filepath,'r', encoding="utf-8") as fp:
                content = fp.read()
                index = content.find(BookShelfConfig().getStartString())
                rindex = content.find(BookShelfConfig().getEndString())
                content = content[index + len(BookShelfConfig().getStartString()):rindex]
                return re.split(BREAK_LINE, content)

        if self.lines == None:
            with open(self.source, 'r', encoding="utf-8") as fp:
                content = fp.read()
                self.lines = content.rsplit("\n")

        return self.lines[chapter[3] : chapter[3] + chapter[4]]

    def generateEpub(self):
        book = mkepub.Book(title=self.title, author=self.author, description=self.desc, subjects=self.tags)
        with open(self.coverfile, 'rb') as file:
            book.set_cover(file.read())

        with open(BookShelfConfig().getCSSFile()) as file:
            book.set_stylesheet(file.read())

        chapters = self.orgnizeVolumns()
        withoutVolumn = (chapters[0][1] == 'delete')
        for chapter in chapters:
            if chapter[1] == 'delete':
                continue
            content = self.generateChapter(chapter)
            if withoutVolumn or chapter[1] == 'volumn':
                curVolumn = book.add_page(chapter[0], content)
            else:
                book.add_page(chapter[0], content, curVolumn)

        target = BookShelfConfig().getTargetFile() % book.title
        book.save(target)

    def packageBook(self):
        path = Path(self.rootpath)
        if path.exists() == False:
            path.mkdir(parents=True)
        target = self.rootpath + "%s-%s.md" % (self.title, self.author)
        chapters = self.orgnizeVolumns()
        withoutVolumn = (chapters[0][1] == 'delete')
        with open(target, 'w', encoding="utf-8") as ft:
            ft.write(self.composePandocHeader())
            description = [EMPTY_LINE + TITLE_VOLUMN + '简介']
            description = description + self.desc.rsplit(EMPTY_LINE)
            for line in description:
                ft.write(line + EMPTY_LINE + EMPTY_LINE)
            
            content = []
            for chapter in chapters:
                if chapter[1] == 'delete':
                    continue
                if withoutVolumn or chapter[1] == 'volumn':
                    content.append(TITLE_VOLUMN + chapter[0] + EMPTY_LINE + EMPTY_LINE)
                else:
                    content.append(TITLE_CHAPTER + chapter[0] + EMPTY_LINE + EMPTY_LINE)
                    
                if chapter[3] == -1:
                    content.append(chapter[0] + EMPTY_LINE + EMPTY_LINE)
                    continue

                lines = self.getChapterLines(chapter)
                for line in lines:
                    content.append(line.strip() + EMPTY_LINE + EMPTY_LINE)

            ft.writelines(content)

            ft.flush()

        self.generateZipFile()
        shutil.rmtree(self.rootpath)

    def orgnizeVolumns(self):
        refinedChapters = []
        volumnCount = 0
        volumnName = ''
        for chapter in self.chapters:
            if chapter[1] == 'delete':
                continue
            
            if chapter[1] == 'volumn':
                volumnName = chapter[0]
                volumnCount = volumnCount + 1
                refinedChapters.append(chapter)
                continue
            
            if chapter[1] != volumnName: # add new volumn
                volumn = [chapter[1], 'volumn', chapter[2], -1, -1, -1]
                volumnName = chapter[1]
                volumnCount = volumnCount + 1
                refinedChapters.append(volumn)
            
            refinedChapters.append(chapter)

        if volumnCount == 1:
            refinedChapters[0][1] = 'delete'

        return refinedChapters

    def composePandocHeader(self):
        coverfile = self.coverfile.rsplit('/')[-1]
        cssfile = BookShelfConfig().getCSSFile().rsplit('/')[-1]
        header = {
            'title': self.title,
            'author': self.author,
            'subject': self.tags,
            'publisher': 'nothingbut',
            'cover-image': coverfile,
            'css': cssfile,
            'description': self.desc
        }
        return BookShelfConfig().getPandocHeader().replace('$header$', yaml.dump(header, allow_unicode=True))

    def generateZipFile(self):
        shutil.copy(self.coverfile, self.rootpath)
        shutil.copy(BookShelfConfig().getCSSFile(), self.rootpath)

        zipfilename = BookShelfConfig().getTargetPath() + "%s.%s-%s.zip" % (self.id, self.title, self.author)
        with zipfile.ZipFile(zipfilename, "w", compression = zipfile.ZIP_DEFLATED) as zf:
            for file in Path(self.rootpath).iterdir():
                zf.write(file, file.name)

    def generateChapter(self, chapter):
        curcontent = [BookShelfConfig().getChapterHeaderTemplate() % chapter[0]]
        lines = self.getChapterLines(chapter)

        for line in lines:
            line = line.strip()
            curcontent.append(BookShelfConfig().getContentLineTemplate() % line)

        return ''.join(curcontent)

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
            with open(filepath, 'r', encoding=encode, errors="ignore") as fpr:
                filecontent = fpr.read()
            with open(filepath, 'w', encoding="utf-8", errors="ignore") as fpw:
                fpw.write(filecontent)

if __name__ == '__main__':
    LOG_FORMAT = "[%(filename)s:<%(lineno)d>] %(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    logging.basicConfig(filename='bsutil.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.debug(os.name)
'''
    csv.field_size_limit(500 * 1024 * 1024)

    conn = sqlite3.connect('/Users/shichang/sample.db')
    cursor = conn.cursor()
    with open('/Users/shichang/Public/Books/book_novel.csv', 'r') as fp:
        contents = csv.reader(fp, delimiter='^')
        for item in contents:
            query = 'insert into book_novel values (\'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', \'%s\')' % (item[0], item[1], item[2], item[4], item[16].strip(), item[15], item[17])
            try:
                cursor.execute(query)
            except:
                print(query)
                break

    with open('/Users/shichang/Public/Books/book_NovelContent.csv', 'r') as fp:
        contents = csv.reader(fp, delimiter='^')
        for item in contents:
            query = 'insert into book_contents values (%s, \'%s\', \'%s\', %s, \'%s\')' % (item[0], item[1].replace('\'', '"'), item[2], item[7], item[8].replace('\'','"'))
            try:
                cursor.execute(query)
            except:
                print(query)
                break

    cursor.close()
    conn.commit()
    conn.close()

    count = 0
    conn = sqlite3.connect('/Users/shichang/Downloads/temp/yousuu.db')
    queryNovel = 'select id, name, author from book_novel where LB like \'0B%\''
    shelfCursor = conn.cursor()
    shelfCursor.execute(queryNovel)
    queryCursor = conn.cursor()
    for row in shelfCursor:
        fullquery = 'select id, title, author, tags from book_info where title = \'%s\' and author =\'%s\'' % (row[1], row[2])
        queryCursor.execute(fullquery)
        done = False
        for item in queryCursor:
            done = True
            break
        if done: continue
        count += 1
        partialQuery = 'select id, title, author, tags from book_info where title = \'%s\'' % row[1]
        queryCursor.execute(partialQuery)
        for item in queryCursor:
            count -= 1
            break

    queryCursor.close()
    shelfCursor.close()
    conn.close()
    print(count)
'''