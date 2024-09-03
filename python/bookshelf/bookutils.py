from bsconfig import BookShelfConfig
import pypandoc, shutil, zipfile, sys, csv, sqlite3
from pathlib import Path

EMPTY_LINE = "\n"
TITLE_VOLUMN = "# "
TITLE_CHAPTER = "## "
class BookUtils:
    def __init__(self, book = None):
        if book != None:
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

            with open(self.source, 'r', encoding="utf-8") as fs:
                content = fs.read()
                lines = content.rsplit(EMPTY_LINE)
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
                    for idx in range(chapter[3], chapter[3] + chapter[4]):
                        content.append(lines[idx].strip() + EMPTY_LINE + EMPTY_LINE)

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

        zipfilename = BookShelfConfig().getTargetPath() + "%s-%s.zip" % (self.title, self.author)
        with zipfile.ZipFile(zipfilename, "w", compression = zipfile.ZIP_DEFLATED) as zf:
            for file in Path(self.rootpath).iterdir():
                zf.write(file, file.name)

        shutil.rmtree(self.rootpath)

if __name__ == '__main__':
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