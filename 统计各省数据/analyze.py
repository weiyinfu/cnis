import json
import re

data = json.load(open('data.json', 'r', encoding='utf8'))


def uniq():
    global data
    cnt = 0
    data = sorted(data, key=lambda x: (x['企业名称'], x['证书编号'], x['发证日期'], x['产品类别_add']))
    for i in range(1, len(data)):
        if data[i]['企业名称'] == data[i - 1]['企业名称'] \
                and data[i]['证书编号'] == data[i - 1]['证书编号'] \
                and data[i]['发证日期'] == data[i - 1]['发证日期'] and \
                        data[i]['产品类别_add'] == data[i]['产品类别_add']:
            print(data[i - 1])
            print(data[i])
            print("=" * 10)
            input()
        else:
            cnt += 1
    print(len(data), cnt)


def illegal_date():
    for i in data:
        if re.match('\d\d\d\d.\d\d.\d\d', i['有效期']):  # and re.match('\d\d\d\d.\d\d.\d\d', i['发证日期']):
            pass
        else:
            print("illegal", i)


