import requests
from bs4 import BeautifulSoup
import os
import re
import collections

import markdownify
import frontmatter
from html5lib_to_markdown import transform

# 设置请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# 创建输出目录
output_dir = 'runoob'
os.makedirs(output_dir, exist_ok=True)
base_url = 'https://www.runoob.com/'

def genMarkdown4Course(name, base, fname):
    response = requests.get(base, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    left_col = soup.find_all(name='div',id='leftcolumn',attrs={"class":"design"})
    html_list = left_col[0].find_all(name='a')
    html_dict = collections.OrderedDict()
    for html in html_list:
        if not html['href'].startswith('http'):
            val = "/".join(base.split("/")[0:-1]) + "/" + html['href']
            html_dict[html.string.strip()] = val
        else:
            html_dict[html.string.strip()] = html['href']
    
    if os.path.exists(fname):
        return
    
    with open(fname, 'w', encoding='utf-8') as f:
        for chapt in html_dict:
            print(chapt)
            appendChapter(f, chapt, html_dict[chapt])

    print("completed on %s" % fname)
def appendChapter(file, title, url):
    file.write("# " + title)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    content = soup.find('div', {'class': 'article-body'})

    if content:
        md_content = transform(str(content))
        with open("cache/%s.md" % title, 'w', encoding='utf-8') as fp:
            fp.write(md_content)
        '''
        # 处理段落、标题、列表等
        for element in content.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'ol', 'pre', 'img', 'table']):
            if element.name.startswith('h'):
                # 处理标题级别
                header_level = int(element.name[1])
                file.write(f"{'#' * header_level} {element.get_text().strip()}\n\n")
            elif element.name == 'p':
                file.write(f"{element.get_text().strip()}\n\n")
            elif element.name in ['ul', 'ol']:
                # 处理列表
                for li in element.find_all('li'):
                    file.write(f"- {li.get_text().strip()}\n")
                file.write("\n")
            elif element.name == 'pre':
                # 处理代码块
                code = element.find('code')
                if code:
                    file.write(f"```{code.get('class', [''])[0]}\n{code.get_text().strip()}\n```\n\n")
            elif element.name == 'img':
                # 处理图片
                img_src = element.get('src')
                if img_src and not img_src.startswith('http'):
                    img_src = os.path.join(base_url, img_src)
                file.write(f"![{element.get('alt', '')}]({img_src})\n\n")
            elif element.name == 'table':
                # 处理表格
                file.write(element.get_text().strip() + "\n\n")'
        converter = markdownify.MarkdownConverter(
            bullets="•",  # 保持列表符号一致性
            heading_style="ATX",  # 使用#标题格式
            wrap=80,  # 适当换行
            newline_style='BACKSLASH'  # 保持严格换行
        )
        md_content = converter.convert(str(content))

        # 后处理优化
        md_content = re.sub(r'\n{3,}', '\n\n', md_content)  # 移除多余空行
        md_content = re.sub(r'(?<!\n)\n(?!\n)', ' ', md_content)  # 合并段落内换行
        file.write(md_content)
        '''

def main():
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    pageClassPattern = re.compile("codelist codelist-desktop cate\d")
    middle_col = soup.find_all(name='div',attrs={"class":pageClassPattern})

    for cat in middle_col:
        catalog = str(cat.h2).split("</i>")[-1].split("</h2>")[0].strip().replace("/", "_").replace("$", "_").replace(" ", "_").replace("(", "_").replace(")", "_")
        FILE_PATH = "./runoob/%s"%(catalog)
        if os.path.exists(FILE_PATH) == False: 
            os.makedirs(FILE_PATH)

        html_list = cat.find_all(name='a')
        for course in html_list:
            title = course.h4.string.strip()
            link = "http:" + course['href']
            filename = "%s/%s.md"%(FILE_PATH, title)
            genMarkdown4Course(title, link, filename)
            break
        break

if __name__ == '__main__':
    main()