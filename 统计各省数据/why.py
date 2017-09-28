import json
import pprint

data = json.load(open('data2.json', encoding='utf8'))
cnt = 0
print(len(data))
s = set()
for i in data:
    if i['所属省份'] == '湖北':
        s.add(i['企业名称'])
print(len(s))
