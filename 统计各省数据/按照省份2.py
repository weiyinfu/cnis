import json
s = """
建筑用钢筋
轴承钢材
水泥
人民币鉴别仪
防伪技术产品
集成电路卡及集成电路卡读写机
卫星电视广播地面接收设备
无线广播电视发射设备
广播通信铁塔及桅杆
防爆电气
燃气器具
空气压缩机
港口装卸机械
摩擦材料及密封制品
公路桥梁支座
预应力混凝土铁路桥简支梁
水工金属结构
制冷设备
内燃机
砂轮
饲料粉碎机械
建筑卷扬机
钢丝绳
轻小型起重运输设备
预应力混凝土用钢材
预应力混凝土枕
救生设备
"""
ca=set(s.split())
data = json.load(open('data2.json', encoding='utf8'))
temp = []
for i in data:
    if i['有效期'] >= '20170829' and i['产品类别_add'] in ca:
        temp.append(i)
    else:
        continue
data = temp
print(len(data))
ma = dict()
for i in data:
    if i['所属省份'] not in ma:
        ma[i['所属省份']] = []
    ma[i['所属省份']].append(i)
ans = []


def uniq(li):
    if len(li) == 1: return li
    li = sorted(li, key=lambda x: x['企业名称'])
    l = []
    for i in range(len(li)):
        if li[i]['企业名称'] == li[i - 1]['企业名称']:
            continue
        else:
            l.append(li[i])
    return l


print("省份,证书数,企业数")
for i in ma:
    it = dict()
    it['省份'] = i
    it['证书数'] = len(ma[i])
    it['企业数'] = len(uniq(ma[i]))
    print("%s,%d,%d" % (it['省份'], it['证书数'], it['企业数']))
