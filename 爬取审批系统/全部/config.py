import requests

res = r'D:\88大合并\res'
html = r'D:\88大合并\html'

database = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'haha',
    'db': 'company',
    'charset': 'utf8'
}

sess = requests.Session()


def login():
    # 登录系统
    resp = sess.post('http://xkzsp.cnis.gov.cn/user/login?destination=/', data={
        'name': 'admin',
        'pass': 'xkz315admin',
        'form_id': 'user_login',
        'op': '登录'
    })
    if resp.status_code == 200:
        print('login success')
    else:
        print('login faied')
        exit(0)
def insert(table_name, kvs, cur, conn):
    # 向数据库中插入键值对
    assign = ','.join(["%s='%s'" % (k, conn.escape_string(str(v))) for k, v in kvs.items()])
    cur.execute("insert into {} set {}".format(table_name, assign))
