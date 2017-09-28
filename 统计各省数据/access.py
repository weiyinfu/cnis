import pypyodbc

import json


def read_access():
    url = 'Driver={Microsoft Access Driver (*.mdb)};DBQ=' + r"C:\Users\weidiao\Desktop\ZhijianZ\ZhijianZ.mdb"
    conn = pypyodbc.win_connect_mdb(url)
    cur = conn.cursor()
    cur.execute("SELECT * FROM qiye")
    ans = []
    for row in cur.fetchall():
        it = dict()
        for i in range(len(row)):
            it[cur.description[i][0]] = row[i]
        ans.append(it)
    cur.close()
    conn.close()
    return ans


category_map = dict({
    '钢筋混凝土用热轧钢 筋': '建筑用钢筋',
    '港口装 卸机械': '港口装卸机械',
    '港 口装 卸机 械': '港口装卸机械',
})


def load_category():
    line = 0
    for i in open("产品类别.txt", encoding='utf8'):
        k, v = i.strip().split()
        line += 1
        category_map[k] = v


col_map = {
    '企业名称': '企业名称',
    '住所': '住所',
    '生产地址': '生产地址',
    '产品类别': '产品类别',
    '产品名称': '产品名称',
    '申证单元': '申证单元',
    '产品单元': '申证单元',
    '证书编号': '证书编号',
    '许可证编号': '证书编号',
    '有效期': '有效期',
    '发证日期': '发证日期',
    '所属省份': '所属省份',
    '省份': '所属省份',
    '省别': '所属省份',
    'QYMC': '企业名称',
    'qymc': '企业名称',
    'CPLB': '产品类别',
    'cplb': '产品类别',
    'CPMC': '产品名称',
    'cpmc': '产品名称',
    'SZDY': '申证单元',
    'szdy': '申证单元',
    'XKZBH': '证书编号',
    'xkzbh': '证书编号',
    'YXQ': '有效期',
    'yxq': '有效期',
    'FZRQ': '发证日期',
    'fzrq': '发证日期',
    'SHENGB': '所属省份',
    'shengb': '所属省份',
    'SCDZ': '生产地址',
    'scdz': '生产地址',
    'ZHUSUO': '住所',
    'zhusuo': '住所',
}


def filt_cols(data):
    ans = []
    for i in range(len(data)):
        it = dict()
        for j in data[i]:
            if j in col_map:
                it[col_map[j]] = data[i][j]
        ans.append(it)
    return ans


special_category_list = {}


def get_category(product):
    product = product.strip().replace('\n', '').strip('产品')
    if not product:
        return '竟然没有产品'
    elif product in special_category_list:
        return '竟然没有产品'
    elif product in category_map:
        return category_map[product]
    elif product.startswith('危险化学'):
        return '危险化学品'
    else:
        print(product, 'not have')
        print(product, product in category_map)
        exit(1)


def filt_product(data):
    for i in data:
        cate = get_category(i['产品名称'])
        if '产品类别' in i and i['产品类别']:
            if cate != i['产品类别']:
                print('产品类别不一样', '产品名称', i['产品名称'], '产品类别', i['产品类别'], 'mycategory', cate, i['产品类别'] == cate)
                i['产品类别_add'] = cate
            else:
                i['产品类别_add'] = cate
        else:
            i['产品类别_add'] = get_category(i['产品名称'])


load_category()
data = read_access()
data = filt_cols(data)
filt_product(data)
json.dump(data, open('data2.json', encoding='utf8', mode='w'), ensure_ascii=0, indent=2)