import xlrd
import json
import os
import re

xkz = set()

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


def filt_cols(data):
    ans = []
    for i in range(len(data)):
        it = dict()
        for j in data[i]:
            if j in col_map:
                it[col_map[j]] = data[i][j]
        ans.append(it)
    return ans


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


def parse_file(file):
    data = read_xls(file)
    data = filt_cols(data)
    data = filt_xkz(data)
    return data


def filt_xkz(data):
    for i in data:
        s = i['证书编号'].upper()
        s = s.replace('（', '(').replace('）', ')')
        i['证书编号'] = re.sub('\s', '', s)
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
    print(sum_cnt)
    return all_data


data = parse_folder(r"C:\Users\weidiao\Desktop\注销")
print(len(data))
for i in data:
    print(i['企业名称'], i['证书编号'])
