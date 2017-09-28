import json
import re

sc = dict()  # string to code
cs = dict()  # code to string
words = ''


def load():
    global words
    ww = set()
    for i in open('行政区划.txt', encoding='utf8'):
        ks = i.strip().split()
        ks = [i.strip() for i in ks]
        k, v = ks[0], ks[1]
        cs[k] = v
        if v not in sc:
            sc[v] = [k]
        else:
            sc[v].append(k)
        ww.add(v)
        if v[-1] in '省市县区' and len(v) > 2:
            vv = v[:-1]
            ww.add(vv)
            if vv not in sc:
                sc[vv] = [k]
            else:
                sc[vv].append(k)
        if v.endswith("地区"):
            vv = v[:-2]
            ww.add(vv)
            if vv not in sc:
                sc[vv] = [k]
            else:
                sc[vv].append(k)
    words = '|'.join(ww)


def format_address(s, info=[]):
    info = [i.strip() for i in info if i.strip()]
    ans = re.findall(words, s)
    for i in info:
        if i[-1] in '省市县区' and len(i) > 2:
            i = i[:-1]
            if i in sc:
                ans.append(i)
    code = list(map(lambda x: sc[x], ans))  # 将文字转化为编码
    # 将编码一维化
    temp = []
    for i in code:
        temp.extend(i)
    code = temp
    # 统计各个编码出现的次数
    cnt = [0] * len(code)
    for i in range(len(code)):
        for k in range(len(code)):
            if code[i].strip('0').startswith(code[k].strip('0')):
                cnt[i] += 1
    # 找到出现次数最多的编码
    max_index = -1
    for i in range(len(cnt)):
        if max_index == -1 or cnt[i] > cnt[max_index] or (
                        cnt[i] == cnt[max_index] and (len(code[i].strip('0')) < len(code[max_index].strip('0')))):
            max_index = i
    if max_index == -1:
        print("unsure", s)
    c = code[max_index]
    if c.endswith('0000'):
        c = c[:2] + '0100'
        print('not very sure ', s, c)
    return c


def codeToStr(co):
    s = cs[co[:2] + "0000"] + cs[co[:4] + "00"] + cs[co]
    return s


def modify_qy():
    qys = json.load(open("qy.json", encoding='utf8'))
    for i in qys:
        address = i['通讯地址（复制生产地址）']
        pro = i['企业所在省（根据生产地址获取）']
        shi = i['企业所在市（根据生产地址获取）']
        f_address = format_address(address, [pro, shi])
        i['area_code'] = f_address
        print(address, pro, shi, f_address, codeToStr(f_address))
    json.dump(qys, open("qy2.json", 'w', encoding='utf8'), ensure_ascii=0, indent=2)


def modify_jg():
    jgs = json.load(open("jg.json", encoding='utf8'))
    for i in jgs:
        address = i['通讯地址']
        pro = i['所在省区']
        f_address = format_address(address, [pro])
        i['area_code'] = f_address
        print(address, codeToStr(f_address))
    json.dump(jgs, open("jg2.json", 'w', encoding='utf8'), ensure_ascii=0, indent=2)


if __name__ == '__main__':
    load()
    modify_jg()
