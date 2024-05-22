import requests, time
import sqlite3
import html


conn = sqlite3.connect('/Users/shichang/Workspace/programing/data/yousuu.db')
cur = conn.cursor()
querystr = 'select max(id) from main.book_info'
cur.execute(querystr)
total = 0
for row in cur:
    if row[0] == None:
        break
    total = int(row[0])
start = 0
for id in range(total):
    if id < start:
        continue
    querystr = 'select id, desc, cover from main.book_info where id = %d' % id
    cur.execute(querystr)
    if (cur.rowcount > 0):
        try:
            response = requests.get(row[2], stream=True)
            with open('/users/shichang/Workspace/programing/temp/cover/%s.jpg' % row[0], 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except requests.exceptions.RequestException as err:
            print(err)

        desc = html.unescape(row[1]).strip()
        updatestr = 'update main.book_info set desc = \'%s\' where id = %s' % (desc, row[0])
        print(updatestr)
        cur.execute(updatestr)
        conn.commit()

cur.close()
conn.close()
