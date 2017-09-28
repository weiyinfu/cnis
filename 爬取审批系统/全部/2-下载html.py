import os
import time

import pymysql

import config

sess = config.sess


def grab(company):
    p = os.path.join(config.html, company['node_id'])
    if os.path.exists(p):
        print('exists', company)
        return
    resp = sess.get('http://xkzsp.cnis.gov.cn/node/' + company['node_id'])
    resp.encoding = 'utf8'
    f = open(p, encoding='utf8', mode='w')
    f.write(resp.text)
    f.close()
    # time.sleep(0.2)


config.login()
time.sleep(1)
conn = pymysql.connect(**config.database)
cur = conn.cursor(pymysql.cursors.DictCursor)
rows = cur.execute('select * from company_ids')
for i in range(rows):
    it = cur.fetchone()
    print(i, it)
    grab(it)
cur.close()
conn.close()
