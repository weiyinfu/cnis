import os

root_dir = r"C:\Users\weidiao\Desktop\SogouC.reduced.20061127\SogouC.reduced\Reduced"


def dataset_info():
    a = os.listdir(root_dir)
    xsize = 0
    for i in a:
        p = os.path.join(root_dir, i)
        xs = os.listdir(p)
        xsize += len(xs)
        print(i, len(xs))
    print('total sample size', xsize)


def data():
    a = os.listdir(root_dir)
    ans = []
    for i in a:
        p = os.path.join(root_dir, i)
        for j in os.listdir(p):
            f = open(os.path.join(p, j),encoding='gbk',errors='ignore')
            x = f.read()
            ans.append((x, i))
    return ans


for i in data():
    print(i)
    input()
