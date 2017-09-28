f = open("注销.txt", encoding='utf8')
lose = dict()
for i in f:
    k, v = i.strip().split()
    lose[v] = k