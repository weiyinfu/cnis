import json
import datetime
import re

import xlrd
import os

category_map = {
    "铝合金窗   塑料窗": '建筑外窗',
    "铝合金窗 塑料窗": '建筑外窗',
    '特种劳动 防护用': '特种劳动防护用品',
    '复肥    复混肥料': '化肥',
    '特种劳动防护用品 防静电服、阻燃服': '特种劳动防护用品',
    '架空绞线 架空绝缘电缆': '架空绞线',
    '1.非复合膜袋    2. 食品用工具': '食品相关产品',
    '编织袋  非复合膜袋': '食品相关产品',
    '硫 酸': '危险化学品',
    '碳化钙（电石）（优等品）': '危险化学品',
}


def number_to_day(s):
    beg = datetime.date(1900, 1, 1)
    now = beg + datetime.timedelta(days=int(s))
    now = str(now).replace('-', '.')
    return now


def load_category():
    for i in open("产品类别.txt", encoding='utf8'):
        k, v = i.strip().split()
        category_map[k] = v


def format_date(s):
    a = re.findall('\d+', s)
    for i in range(len(a)):
        if len(a[i]) == 1:
            a[i] = '0' + a[i]
    if len(a) == 0:
        return '0000.00.00'
    if len(a) == 1 and len(a[0]) == 4 and 2025 > int(a[0]) > 2000:
        return a[0] + '.01.01'
    if len(a[0]) == 8:
        return '.'.join([a[0][:4], a[0][4:6], a[0][6:]])
    if len(a) == 2:
        if a[1] == '00':
            return number_to_day(a[0])
        if len(a[0]) == 5 and len(a[1]) == 0:
            return number_to_day(a[0])
        else:
            return '.'.join(a) + ".01"
    if len(a) == 6:
        if len(a[3]) == 4:
            return '.'.join(a[3:])
        else:
            return '.'.join(a[:3])
    if len(a) != 3:
        print(s, len(a), a, 'date is longer than 3')
        exit(-1)
    if len(a) == 3 and int(a[0]) > 2030:
        return number_to_day(a[0])
    return '.'.join(a)


def read_xls(filename):
    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(0)
    beg_row = 1 if sheet.cell(0, 1).ctype == 0 else 0
    ks = []
    for i in range(sheet.ncols):
        k = sheet.cell_value(beg_row, i).strip()
        k = k.replace('\n', '')
        ks.append(k)
    ans = []
    for i in range(beg_row + 1, sheet.nrows):
        if not sheet.cell_value(i, 1).strip(): continue
        it = dict()
        for j in range(sheet.ncols):
            it[ks[j]] = str(sheet.cell_value(i, j)).strip()
        ans.append(it)
    return ans


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
    '证书批准时间': '发证日期',
    'SHENGB': '所属省份',
    'shengb': '所属省份',
    'SCDZ': '生产地址',
    'scdz': '生产地址',
    'ZHUSUO': '住所',
    'zhusuo': '住所',
}

special_category_list = {'内蒙古巴彦淖尔市乌拉特后旗青山工业园区'}
special_date_list = {'正定县凯明装饰板厂', '宁波联润流体机械制造有限公司', '宁波东海岸包装有限公司'}


def filt_cols(data):
    ans = []
    for i in range(len(data)):
        it = dict()
        for j in data[i]:
            if j in col_map:
                it[col_map[j]] = data[i][j]
        ans.append(it)
    return ans


def filt_date(data):
    for i in data:
        if i['企业名称'] in special_date_list:
            continue
        i['有效期'] = format_date(i['有效期'])
        i['发证日期'] = format_date(i['发证日期'])


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
        print(product, product in special_category_list)
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


def filt_xkz(data):
    for i in data:
        s = i['证书编号'].upper()
        s = s.replace('（', '(').replace('）', ')')
        i['证书编号'] = re.sub('\s', '', s)


def parse_file(file, simple=False):
    data = read_xls(file)
    data = filt_cols(data)
    filt_date(data)
    filt_product(data)
    filt_xkz(data)
    if simple:
        for j in data:
            print(j)
    return data


def parse_folder(folder):
    sum_cnt = dict()
    all_data = []
    cnt = 0
    for i in os.listdir(folder):
        print(cnt)
        cnt += 1
        p = os.path.join(folder, i)
        print(p)
        data = parse_file(p)
        for j in data:
            j['src'] = i
        sum_cnt[i] = len(data)
        all_data.extend(data)
    json.dump(all_data, open('data.json', 'w', encoding='utf8'), ensure_ascii=0, indent=2)
    print(sum_cnt)


load_category()
# parse_folder(r"C:\Users\weidiao\desktop\现行有效库")
parse_folder(r"C:\Users\weidiao\desktop\历史数据库")
# parse_file(r"C:\Users\weidiao\Desktop\历史数据库\河南历史.xlsx", simple=True)
# parse_file(r"C:\Users\weidiao\Desktop\历史数据库\甘肃历史.xlsx", simple=True)
# print(format_date("20161114"))
# print(get_category('特种劳动防护用品'))
