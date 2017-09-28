import json
import os
import re
import time

import pymysql
import uuid
import requests
from pyquery import PyQuery as pq

import config

config.login()


def downloadJson():
    data = []
    for i in range(19):
        resp = config.sess.get("http://xkzsp.cnis.gov.cn/works/report/list?page=" + str(i))
        time.sleep(1)
        resp.encoding = 'utf8'
        tbody = re.search('<tbody>.*?</tbody>', resp.text, re.DOTALL).group()
        trs = pq(tbody)('tr')
        for i in range(trs.length):
            tr = trs.eq(i)
            tds = tr("td")
            it = dict()
            it['name'] = tds.eq(0).text()
            nodeid = tds.eq(0).find('a').attr('href')
            nodeid = re.search('\d+', nodeid).group()
            it['nodeId'] = nodeid
            it['piHao'] = tds.eq(1).text()
            it['filename'] = tds.eq(2).text()
            it['type'] = tds.eq(3).text()
            it['date'] = tds.eq(4).text()
            it['state'] = tds.eq(5).text()
            it['url'] = tds.eq(2).find("a").attr('href')
            it['real_file'] = requests.utils.unquote(it['url'][it['url'].rindex('/') + 1:])
            data.append(it)
            print(it)
    json.dump(data, open('大签报.json', encoding='utf8', mode='w'), ensure_ascii=0, indent=2)


def downloadFile():
    data = json.load(open("大签报.json", encoding='utf8'))
    print(len(data))
    for i in data:
        path = os.path.join('大签报doc', i['real_file'])
        print(i['url'], i['real_file'])
        if not os.path.exists(path):
            with open(path, mode='wb') as f:
                resp = config.sess.get(i['url'])
                resp.encoding = 'utf8'
                f.write(resp.content)
                time.sleep(1)


def insertData():
    conn = pymysql.connect(**config.database)
    cur = conn.cursor()
    data = json.load(open("大签报.json", encoding='utf8'))
    for i in data:
        i['id'] = uuid.uuid4()
        config.insert("qianbao", i, cur, conn)
        print(i)
    conn.commit()
    cur.close()
    conn.close()


insertData()
# downloadFile()
# downloadJson()
