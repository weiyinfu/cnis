import json
import re

data = json.load(open('data.json', encoding='utf8'))


def all_province():
    pro = set()
    for i in data:
        if '所属省份' not in i:
            print('没有所属省份')
            print(i)
            exit(-1)
        pro.add(i['所属省份'])
    print(pro)


def find_province(p):
    for i in data:
        if i['所属省份'] == p:
            print(p,i['src'])


def youxiaoqi():
    cnt = 0
    for i in data:
        if i['发证日期'] > i['有效期'] != '0000.00.00':
            cnt += 1
            print(i['src'], i['企业名称'])
    print(cnt)


def xkz():
    for i in data:
        if not re.match("(\(?[\u4e00-\u9fa5]\)?)?XK\d\d-\d\d\d-\d\d\d\d\d", i['证书编号']):
            print(i['证书编号'], i['src'])


all_province()
find_province('')
find_province('运城')
find_province('临汾')
find_province('黑龙江省')
find_province("湖北省")
# youxiaoqi()
# xkz()
