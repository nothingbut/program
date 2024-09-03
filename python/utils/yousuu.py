import requests, time, json
import sqlite3

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
ids = 400000
max = 0
conn = sqlite3.connect('/Users/shichang/Downloads/temp/yousuu.db')
querycur = conn.cursor()
querystr = 'select id from main.book_info where updated = False'
querycur.execute(querystr)
updatecur = conn.cursor()

requests.packages.urllib3.disable_warnings()

count = 0
try:
    for row in querycur:
        max = int(row[0])
        result = requests.get('https://api.yousuu.com/api/book/' + str(max), headers=headers, verify=False).json()
        with open('/Users/shichang/Workspace/program/data/cache/%d.json' % max, 'w') as f:
            json.dump(result, f, ensure_ascii=False) 
        time.sleep(1)
        updatestr = 'update main.book_info set updated = True where id = %d' % max
        updatecur.execute(updatestr)
        count = count + 1
        if count == 100:
            print('updated on %d' % max)
            conn.commit()
            count = 0

finally:
    print('close legacy update on %d' % max)
    conn.commit()
    querycur.close()
    updatecur.close()

print('existing is %d' % max)
count = 0
error = 0
insertcur = conn.cursor()
for id in range(ids):  
    if id < max:
        continue

    if error > 100:
        print('ending ...')
        break

    result = requests.get('https://api.yousuu.com/api/book/' + str(id + 1), headers=headers).json()
    with open('/Users/shichang/Workspace/program/data/cache/%d.json' % (id + 1), 'w') as f:
        json.dump(result, f, ensure_ascii=False) 
    time.sleep(1)

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
    sqlstring = 'insert into main.book_info values (%d, \'%s\', \'%s\', \'%s\', \'%s\', \'%s\', NULL, True)' % (int (book.get('_id')), 
                                                                                            book.get('title').replace('\'', '\\\t'), 
                                                                                            book.get('author').replace('\'', '\\\t'), 
                                                                                            book.get('cover'), 
                                                                                            book.get('introduction').replace('\'', '’'), 
                                                                                            tags)
    try:
        insertcur.execute(sqlstring)
    except:
        print('failed to execute [%s]' % sqlstring)
        break

    count = count + 1
    if count == 100:
        print('commit by %d' % (id - 1))
        conn.commit()
        count = 0

    conn.commit()
    insertcur.close()
    conn.close()

