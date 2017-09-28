import os
import time

import pymysql
import requests

import config

sess = config.sess


def grab(url, filename):
    print(url, filename)
    path = os.path.join(config.res, filename)
    if os.path.exists(path):
        print(path, 'already had')
        return
    with open(path, 'wb') as f:
        resp = sess.get(url)
        f.write(resp.content)
    time.sleep(0.2)


def scrawl():
    conn = pymysql.connect(**config.database)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    rows = cur.execute("select * from files")
    for i in range(rows):
        it = cur.fetchone()
        grab(it['url'], it['path'])
    cur.close()
    conn.close()


scrawl()
