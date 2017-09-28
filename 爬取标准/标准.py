import math
import re
import threading
import uuid

import pymysql
import requests
from pyquery import PyQuery as pq
import time
from pprint import pprint

database = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'haha',
    'db': 'standard',
    'charset': 'utf8'
}
base_url = "http://www.gb688.cn/bzgk/gb/std_list?page={}&p.p90=circulation_date&p.p91=desc"
table_name = 'standard'


def get_total_count():
    # 获取总页数
    resp = get(base_url.format(1))
    resp.encoding = 'utf8'
    table = pq(resp.text).find('table').eq(3).find('td').eq(0).text()
    res = re.findall('\d+', table)
    return int(res[3])


def escape(diction, conn):
    # 对字典中的str类型对象进行转义
    for i in diction:
        if type(diction[i]) == str:
            diction[i] = conn.escape_string(diction[i])


def parse_tds(tds):
    # 解析多个td项，转换为一个standard对象
    standard = dict()
    standard['standard_number'] = tds.eq(1).text()
    standard['is_caibiao'] = '1' if tds.eq(2).text() else '0'
    standard['standard_name'] = tds.eq(3).text()
    standard['is_force'] = '1' if tds.eq(4).text() == '强标' else '0'
    standard['state'] = tds.eq(5).text().replace("'", "")
    post_time = tds.eq(6).text()
    use_time = tds.eq(7).text()
    standard['post_time'] = post_time if post_time else use_time
    standard['use_time'] = use_time if use_time else post_time
    id = tds.eq(1).find('a').attr('onclick')
    id = re.search('[ABCDEF\d]+', id).group()
    resp = get('http://www.gb688.cn/bzgk/gb/newGbInfo?hcno=' + id)
    resp.encoding = 'utf8'
    contents = pq(resp.text).find('.content')
    standard['ccs'] = contents.eq(0).text()
    standard['ics'] = contents.eq(1).text()
    standard['manager_department'] = contents.eq(4).text()
    standard['owner_department'] = contents.eq(5).text()
    standard['post_department'] = contents.eq(6).text()
    standard['remark'] = contents.eq(7).text()
    standard['english_name'] = pq(resp.text).find('table').eq(1).find('tr').eq(1).text()[7:]
    return standard


def get(url):
    for i in range(10):
        try:
            resp = requests.get(url, timeout=4)
            return resp
        except Exception as e:
            print(e)
            print(url)
            time.sleep((i + 1) * 3)


def scrawl(page_from, page_end):
    # 爬取base_url，从page_from页到page_end页，将爬取到的standard插入到table_name表中
    print(scrawl.__name__, page_from, page_end)
    conn = pymysql.connect(**database)
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    for i in range(page_from, page_end):
        print('page', i + 1)
        resp = get(base_url.format(i + 1))  # 页码从1开始
        resp.encoding = 'utf8'
        table = pq(resp.text).find('.result_list')
        trs = table.find('tbody').eq(1).find('tr')
        for j in range(len(trs)):
            standard = parse_tds(trs.eq(j).find('td'))
            escape(standard, conn)
            sql = "select * from {} where standard_number='{}'".format(table_name,
                                                                       standard['standard_number'])
            kv = ','.join(map(lambda x: "%s='%s'" % (x[0], x[1]), standard.items()))
            rows = cur.execute(sql)
            if rows == 0:  # 如果不存在该条标准
                sql = "insert into %s set id='%s',%s" % (table_name, uuid.uuid1(), kv)
                cur.execute(sql)
                conn.commit()
                update_one_application(standard['standard_number'])
            else:
                sql = "update %s set %s where standard_number='%s'" % (
                    table_name, kv, standard['standard_number'])
                cur.execute(sql)
                conn.commit()
    cur.close()
    conn.close()


def scrawl_all_standard(thread_cnt=10):
    # 多线程爬虫爬取标准
    page_size = get_total_count()
    page_per_thread = math.ceil(page_size / thread_cnt)
    for i in range(thread_cnt):
        th = threading.Thread(
            target=scrawl,
            args=(page_per_thread * i, min(page_size, page_per_thread * (i + 1))))
        th.start()


def get_application(standard_number):
    # 根据标准号，返回标准适用范围
    try:
        print(get_application.__name__, standard_number)
        standard_number = re.sub('/', '%252F', standard_number)
        standard_number = re.sub(' ', '%2520', standard_number)
        resp = get('http://www.spc.org.cn/gb168/online/{}/'.format(standard_number))
        resp.encoding = 'utf8'
        html = re.sub('|\r', '', resp.text)
        html = re.sub('<br/>', '\n', html)
        s = re.search('<div class="detailedinfo-text">((.|\n|\s)*?)<\/div>', html)
        if s:
            s = s.group(1)
            return s
    except:
        return None


def update_one_application(standard_number):
    # 更新一条标准的适用范围
    conn = pymysql.connect(**database)
    app = conn.escape_string(get_application(standard_number))
    cur = conn.cursor()
    cur.execute("update %s set application='%s' where standard_number='%s'" % (table_name, app, standard_number))
    cur.close()
    conn.commit()
    conn.close()


def update_all_application(begIndex, sz):
    # 更新标准的应用范围
    print(update_all_application.__name__, begIndex, sz)
    conn = pymysql.connect(**database)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    update_cursor = conn.cursor()
    res = cursor.execute('select * from {} limit {},{}'.format(table_name, begIndex, sz))
    for i in range(res):
        try:
            it = cursor.fetchone()
            if it['application']:  # 如果已经有了就不更新了
                print('had', it['standard_number'])
                continue
            app = None
            for retry in range(3):  # 尝试三次
                time.sleep((retry + 1) * 2)
                app = get_application(it['standard_number'])
                if app: break
            if app:
                sql = "update %s set application='%s' where standard_number='%s'" % (
                    table_name, app, it['standard_number'])
                update_cursor.execute(sql)
                print(update_all_application.__name__, 'thread', begIndex, 'finished', i, 'total', sz)
                conn.commit()
        except Exception as e:
            print(e)
            pass
    cursor.close()
    update_cursor.close()
    conn.commit()
    conn.close()


def application(thread_cnt=5):
    conn = pymysql.connect(**database)
    cur = conn.cursor()
    cur.execute('select count(1) from %s' % table_name)
    total = cur.fetchone()[0]
    count_per_thread = math.ceil(total / thread_cnt)
    for i in range(thread_cnt):
        th = threading.Thread(target=update_all_application,
                              args=(i * count_per_thread, count_per_thread))
        th.start()


scrawl_all_standard(10)
