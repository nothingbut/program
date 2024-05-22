import requests, time
import sqlite3

def cleanup():
    conn.commit()
    cur.close()
    conn.close()

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
conn = sqlite3.connect('/Users/shichang/Workspace/programing/data/yousuu.db')
cur = conn.cursor()
ids = 400000
querystr = 'select max(id) from main.book_info'
cur.execute(querystr)
total = 0
for row in cur:
    if row[0] == None:
        break
    total = int(row[0])
print('total is %d' % total)
count = 0
error = 0
for id in range(ids):  
    if id < total:
        continue

    if error > 100:
        print('ending ...')
        break

    result = requests.get('https://api.yousuu.com/api/book/' + str(id + 1), headers=headers).json()
    time.sleep(2)

    if result.get('success') != True:
        error += 1
        continue

    error = 0
    book = result['data']['bookInfo']
    tags = '[网络小说'
    for tag in book.get('tags'):
        tags = tags + ', %s' % tag
    tags = tags + ']'
    if book.get('introduction') == None:
        book['introduction'] = ''
    sqlstring = 'insert into main.book_info values (%d, \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', NULL)' % (int (book.get('_id')), 
                                                                                            book.get('title').replace('\'', '\\\t'), 
                                                                                            book.get('author').replace('\'', '\\\t'), 
                                                                                            book.get('cover'), 
                                                                                            book.get('introduction').replace('\'', '’'), 
                                                                                            tags)
    try:
        cur.execute(sqlstring)
    except:
        print('failed to execute [%s]' % sqlstring)
        break

    count = count + 1
    if count == 100:
        print('commit by %d' % (id - 1))
        conn.commit()
        count = 0
cleanup()
