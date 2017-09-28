import json

data = json.load(open('data.json', encoding='utf8'))
print(len(data))
ma = dict()
for i in data:
    y = i['发证日期'][:4]
    if int(y) > 4000 or int(y) < 2004 and int(y) != 0:
        print(i)
    if y not in ma:
        ma[y] = set()
    ma[y].add(i['企业名称'])
ys = sorted(ma.keys())
for i in ys:
    print(i, len(ma[i]))
a = dict()
for i in data:
    y = i['发证日期'][:4]
    name = i['所属省份']
    if y not in a:
        a[y] = dict()
    if name not in a[y]:
        a[y][name] = set()
    a[y][name].add(i['企业名称'])
ys = ['2012', '2013', '2014', '2015', '2016', '2017']
shengfen = set()
for i in ys:
    for j in a[i]:
        shengfen.add(j)
shengfen = sorted(list(shengfen))
ta = [['' for _ in range(len(ys) + 1)] for __ in range(len(shengfen) + 1)]
ta[0][0] = '省份\\年份'
for i in range(len(shengfen)):
    ta[i + 1][0] = shengfen[i]
for i in range(len(ys)):
    ta[0][i + 1] = ys[i]

for i in range(1, len(ys) + 1):
    for j in range(1, len(shengfen) + 1):
        if shengfen[j - 1] not in a[str(2011 + i)]:
            a[str(2011 + i)][shengfen[j - 1]] = set()
        ta[j][i] = len(a[str(2011 + i)][shengfen[j - 1]])
for i in ta:
    print(','.join(map(lambda x: str(x), i)))
