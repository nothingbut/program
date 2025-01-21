import chardet
import mkepub
from pathlib import Path, PurePath
import regex as re
import requests

template = '/Users/shichang/Workspace/programing/data/template.html'
cssfile = '/Users/shichang/Workspace/programing/data/epub.css'
coverfile = '/Users/shichang/Workspace/programing/data/cover.jpg'
genpath = '/Users/shichang/Workspace/programing/data/'

def downloadCover(url):
    cover_url = 'https:' + url + '600' #将链接转换为600*800尺寸图片的链接
    response = requests.get(cover_url, stream=True)
    with open(coverfile, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def getMetadataFromQD(title):
    url = 'https://m.qidian.com/soushu/' + title + '.html'  # 指定目标url
    response = requests.get(url, stream=True)

    with open('url.html', 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
      	    if chunk:
                f.write(chunk)

    ob = response
    urlname = 'url.html'
    with open("url.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    Path.unlink('url.html')
# 使用正则表达式提取第一个匹配的属性值
    match = re.search(r'bName":"([^"]+)"', html_content)
    if match:
        name = match.group(1)
        if name != title:
            print("No novel found")
            return False   
    else:
        print("No novel found")
        return False
   
    match = re.search(r'bAuth":"([^"]+)"', html_content)
    if match:
        author = match.group(1)
    else:
        print("No author found")

    match = re.search(r'desc":"([^"]+)"', html_content)
    if match:
        desc = match.group(1)
    else:
        print("No description found")

    subjects = ["网络小说"]
    match = re.search(r'category":"([^"]+)"', html_content)
    if match:
        subjects.append(match.group(1))
    match = re.search(r'subCateName":"([^"]+)"', html_content)
    if match:
        subjects.append(match.group(1))

    match = re.search(r'imgUrl":"([^"]+)"', html_content)
    if match:
        coverUrl = match.group(1)[:-3]
    else:
        print("No cover found")

    return {
        'author': author,
        'desc': desc,
        'subjects': subjects,
        'coverUrl': coverUrl
    }

def parseFileContent(filepath):
    encode2utf8(filepath)
    contents = []
    print("生成电子书内容")

    fp = open(filepath,'r', encoding="utf-8")
    content = fp.read()
    fp.close

    lines = content.rsplit("\n")
    
    curcontent = ''
    curvol = ('empty', 'empty', [])
    chapttitle = ''

    for line in lines:
        line = line.strip()
        linetype = checkline(line)

        if linetype == 'ending':
            break

        if linetype == 'normal':
            curcontent += ('<p>$line$</p>'.replace('$line$', line))
            continue

        if chapttitle != '':
            curvol[2].append((chapttitle, curcontent))
            chapttitle = ''
            curcontent = ''

        if (linetype == 'chapter'):
            chapttitle = line
            curcontent = '<h2 id=\"title\">$title$</h2>'.replace('$title$', line)
            continue

        if (linetype == 'volume'):
            if len(curvol[2]) > 0:
                contents.append(curvol)
            curvol = (line, '<h2 id=\"title\">$title$</h2>'.replace('$title$', line), [])
                    
    if chapttitle != '':
        curvol[2].append((chapttitle, curcontent))
    if len(curvol[2]) > 0:
        contents.append(curvol)
 
    return contents

def checkline(line):
    if line == '（全书完）' or line == '《全本完》':
        return 'ending'
    if re.match(r'^\s*(楔子|序章|序言|序|引子).*',line):
        return 'chapter'
    if re.match(r'^\s*[第][0123456789ⅠI一二三四五六七八九十零序〇百千两]*[章].*',line):
        return 'chapter'
    if re.match(r'^\s*[第][0123456789ⅠI一二三四五六七八九十零序〇百千两]*[卷].*',line):
        return 'volume'
    if re.match(r'^\s*[卷][0123456789ⅠI一二三四五六七八九十零序〇百千两]*[ ].*',line):
        return 'volume'
    return 'normal'

def detectsubject(line):
    if line == '（全书完）' or line == '《全本完》':
        return 'ending'
    if re.match(r'^\s*(楔子|序章|序言|序|引子) .*',line):
        return 'subject'
    if re.match(r'^\s*[第卷][0123456789一二三四五六七八九十零〇百千两]*[章回部节集卷] .*',line):
        return 'subject'
    return 'content'

def encode2utf8(filepath):
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

def txt2epub(bookfile):
    bookname = PurePath(bookfile).name[0:-4]
    bookmeta = getMetadataFromQD(bookname)
    if bookmeta == False:
        print("《%s》不是起点小说" % bookname)
        bookmeta = {
        'author': 'author',
        'desc': 'desc',
        'subjects': '[subjects]',
        'coverUrl': 'coverUrl'
    }
###        exit()
    
    book = mkepub.Book(title=bookname, author=bookmeta.get('author'), 
                       description = bookmeta.get('desc'), 
                       subjects = bookmeta.get('subjects'))

    ### parse novel text file into content
    contents = parseFileContent(bookfile)

    downloadCover(bookmeta.get('coverUrl'))
    with open(coverfile, 'rb') as file:
        book.set_cover(file.read())
    with open(cssfile) as file:
        book.set_stylesheet(file.read())

    for vol in contents:
        if vol[0] == 'empty':
            for chapt in vol[2]:
                book.add_page(chapt[0], chapt[1])
        else:
            volpage = book.add_page(vol[0], vol[1])
            for chapt in vol[2]:
                book.add_page(chapt[0], chapt[1], parent=volpage)

    target = genpath + '%s(作者：%s).epub' % (bookname, bookmeta.get('author'))
    if Path(target).exists():
        Path(target).unlink()

    book.save(target)

if __name__ == '__main__':
    print("My Python Playground on epub generating")
    bookfile = '/Users/shichang/Downloads/temp/zxcs/雾都侦探.txt'
    txt2epub(bookfile)