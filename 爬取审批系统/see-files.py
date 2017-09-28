import pymysql

database = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'haha',
    'db': 'company',
    'charset': 'utf8'
}
conn = pymysql.connect(**database)
cur = conn.cursor()
rows = cur.execute("select url from files")
for i in range(rows):
    x = cur.fetchone()[0]
    if x.startswith('http://xkzsp.cnis.gov.cn/system/files/'):
        x = x[len('http://xkzsp.cnis.gov.cn/system/files/'):]
        if not x.startswith('lc'):
            if not x.startswith('yssm'):
                if not x.startswith('ir'):
                    if not x.startswith('sm'):
                        if not x.startswith('rf'):
                            if not x.startswith('qycn'):
                                if not x.startswith('pm'):
                                    if not x.startswith('mm'):
                                        if not x.startswith('mcn'):
                                            if not x.startswith('cyzccn'):
                                                if not x.startswith('af'):
                                                    print('system', x)
    elif x.startswith('http://xkzsp.cnis.gov.cn/sites/default/files/sm/'):
        pass
    else:
        print(x)
cur.close()
conn.close()
