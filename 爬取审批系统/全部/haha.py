import config
import pymysql
import os

conn = pymysql.connect(**config.database)
cur = conn.cursor()
rows = cur.execute("select path from files")
cnt = 0
for i in range(rows):
    one = cur.fetchone()
    if not os.path.exists(os.path.join(r"D:\88大合并\res", one[0])):
        print(one)
        cnt += 1
print(cnt)
