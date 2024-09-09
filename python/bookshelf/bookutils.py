from bsconfig import BookShelfConfig
import pypandoc, shutil, zipfile, sqlite3, chardet, csv, os
from pathlib import Path

EMPTY_LINE = "\n"
BREAK_LINE = "<br />"
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

    def loadFromDBSource(self, id):
        pass

    def loadFromPandocSource(self, source):
        pass

    def genEpubByMkepub(self):
        pass

    def genEpubByPandoc(self):
        target = self.rootpath + "%s-%s.epub" % (self.title, self.author)
        pypandoc.convert_file(self.preparePandocSource(), 'epub3', outputfile=target, extra_args='--split-level=2')

    def preparePandocSource(self):
        if self.source != BookShelfConfig().getBookDB():
            type = 'file'
        else:
            type = 'db'
        path = Path(self.rootpath)
        if path.exists() == False:
            path.mkdir(parents=True)
        target = self.rootpath + "%s-%s.txt" % (self.title, self.author)
        chapters = self.orgnizeVolumns()
        withoutVolumn = (chapters[0][1] == 'delete')
        with open(target, 'w', encoding="utf-8") as ft:
            ft.write(self.composePandocHeader())
            description = [EMPTY_LINE + TITLE_VOLUMN + '简介']
            description = description + self.desc.rsplit(EMPTY_LINE)
            for line in description:
                ft.write(line + EMPTY_LINE + EMPTY_LINE)

            content = []
            
            if type == 'file':
                with open(self.source, 'r', encoding="utf-8") as fs:
                  filecontent = fs.read()
                  lines = filecontent.rsplit(EMPTY_LINE)

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
                if type == 'file':
                    for idx in range(chapter[3], chapter[3] + chapter[4]):
                        content.append(lines[idx].strip() + EMPTY_LINE + EMPTY_LINE)
                else:
                    lines = self.readChapterLines(chapter[2])
                    for line in lines:
                        content.append(line.strip() + EMPTY_LINE + EMPTY_LINE)

            ft.writelines(content)

            ft.flush()

            self.generateZipFile()

            return target

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
        header = BookShelfConfig().getPandocHeader()
        coverfile = self.coverfile.rsplit('/')[-1]
        cssfile = BookShelfConfig().getCSSFile().rsplit('/')[-1]
        return header.replace('$title$', self.title).replace('$author$', self.author).replace('$coverfile$', coverfile).replace('$tags$', self.tags).replace('$cssfile$', cssfile)

    def generateZipFile(self):
        shutil.copy(self.coverfile, self.rootpath)
        shutil.copy(BookShelfConfig().getCSSFile(), self.rootpath)

        zipfilename = BookShelfConfig().getTargetPath() + "%s.zip" % (self.id)
        with zipfile.ZipFile(zipfilename, "w", compression = zipfile.ZIP_DEFLATED) as zf:
            for file in Path(self.rootpath).iterdir():
                zf.write(file, file.name)

        shutil.rmtree(self.rootpath)

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
            with open(filepath, 'r', encoding=encode, errors="ignore") as fpr:
                filecontent = fpr.read()
            with open(filepath, 'w', encoding="utf-8", errors="ignore") as fpw:
                fpw.write(filecontent)

    def readChapterLines(self, filepath):
        self.encode2utf8(filepath)
        with open(filepath,'r', encoding="utf-8") as fp:
            content = fp.read()
            index = content.find(BookShelfConfig().getStartString())
            rindex = content.find(BookShelfConfig().getEndString())
            content = content[index + len(BookShelfConfig().getStartString()):rindex]
            lines = content.rsplit(BREAK_LINE)

        return lines

if __name__ == '__main__':
    print(os.name)
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