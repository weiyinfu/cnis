import json

s = """ 
泵
抽油设备
电力金具
电力调度通讯设备
电力整流器
电热毯
电线电缆
防爆电气
防喷器及防喷器控制装置
防伪技术产品
钢丝绳
港口装卸机械
工厂制造型眼镜
公路桥梁支座
广播通信铁塔及桅杆
化肥
混凝土输水管
机动脱粒机
集成电路卡及集成电路卡读写机
建筑防水卷材
建筑钢管脚手架扣件
建筑卷扬机
建筑用钢筋
救生设备
空气压缩机
铝、钛合金加工产品
棉花加工机械
摩擦材料及密封制品
摩托车头盔
耐火材料
内燃机
农药
汽车制动液
轻小型起重运输设备
燃气器具
人民币鉴别仪
人造板
砂轮
输电线路铁塔
水工金属结构
水泥
水文仪器
税控收款机
饲料粉碎机械
特种劳动防护产品
铁路桥预应力混凝土简支梁
铜及铜合金管材
危险化学品
危险化学品包装物、容器
卫星电视广播地面接收设备
无线广播电视发射设备
橡胶制品
蓄电池
岩土工程仪器
预应力混凝土轨枕
预应力混凝土用钢材
制冷设备
轴承钢材
助力车
钻井悬吊工具
"""
import 注销 as zx

ca = set(s.split())
data = json.load(open('data.json', encoding='utf8'))
temp = []
lose_cnt = 0
for i in data:
    if i['证书编号'] in zx.lose:
        lose_cnt += 1
        continue
    if i['有效期'] > '20170905' and i['产品类别_add'] in ca and i['有效期'] > i['发证日期']:
        temp.append(i)
data = temp
print(lose_cnt, 'lose count', len(data))
ma = dict()
for i in data:
    if i['所属省份'] not in ma:
        ma[i['所属省份']] = []
    ma[i['所属省份']].append(i)
ans = []
print(len(ma['湖北']))
print(list(map(lambda x: x['企业名称'], sorted(ma['湖北'], key=lambda x: x['企业名称']))))


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


all_count = 0
print("省份,证书数,企业数")
for i in ma:
    it = dict()
    it['省份'] = i
    it['证书数'] = len(ma[i])
    it['企业数'] = len(uniq(ma[i]))
    all_count += it['企业数']
    print("%s,%d,%d" % (it['省份'], it['证书数'], it['企业数']))
print(all_count)
