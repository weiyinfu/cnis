import re
import uuid

import pymysql
from pyquery import PyQuery as pq
import config

sess = config.sess


def pages():
    base_url = 'http://xkzsp.cnis.gov.cn/follow?page='
    conn = pymysql.connect(**config.database)
    cur = conn.cursor()
    for i in range(3135,3981):
        # time.sleep(1
        print('page', i)
        url = base_url + str(i)
        resp = sess.get(url)
        resp.encoding = 'utf8'
        tbody = re.search('<tbody>.*?</tbody>', resp.text, re.DOTALL).group()
        trs = pq(tbody)('tr')
        for j in range(trs.length):
            tr = trs.eq(j)
            it = dict()
            it['id'] = uuid.uuid1()
            href = tr('td').eq(0).find('a').attr('href')
            if not href: continue
            it['node_id'] = re.search('\d+', href).group()
            rows = cur.execute("select * from company_ids where node_id='%s'" % it['node_id'])
            if rows == 0:
                config.insert('company_ids', it, cur, conn)
                conn.commit()
            print(it['node_id'])
    cur.close()
    conn.close()


config.login()
pages()
###3140
###944
