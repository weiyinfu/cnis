from datetime import date, timedelta
import os
import re
import requests

work_day = []
from_year, end_year = -1, -1


def is_leap_year(x):
    if x % 100 == 0:
        return int(x / 100) % 4 == 0
    else:
        return x % 4 == 0


def accumulate():
    for i in range(1, len(work_day)):
        work_day[i] += work_day[i - 1]


def set_weekday():
    weekday = date(from_year, 1, 1).isoweekday()
    for i in range((6 - weekday + 7) % 7, len(work_day), 7):
        work_day[i] = 0
    for i in range((7 - weekday + 7) % 7, len(work_day), 7):
        work_day[i] = 0


def get_month_days(month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month == 2:
        return 28
    else:
        return 30


def index_of(year, month, day):
    total_days = -1  # 下标从0开始
    for i in range(from_year, year):
        total_days += 365
        if is_leap_year(i):
            total_days += 1
    for i in range(1, month):
        total_days += get_month_days(i)
    total_days += day
    if month > 2 and is_leap_year(year):
        total_days += 1
    return total_days


def load_holiday():
    for i in range(from_year, end_year + 1):
        f = open("holiday/{}.txt".format(i))
        s = f.readlines()
        for j in s:
            if not i: continue
            if '-' in j:
                res = re.search('(\d+)\.(\d+)-(\d+)\.(\d+)', j)
                fm, fd, tm, td = [int(res.group(i + 1)) for i in range(4)]
                for k in range(index_of(i, fm, fd), index_of(i, tm, td) + 1):
                    work_day[k] = 0
            else:
                m, d = j.split('.')
                work_day[index_of(i, int(m), int(d))] = 1
        f.close()


def init():
    global work_day, from_year, end_year
    x = sorted(os.listdir('holiday'))
    from_year = int(x[0][:-4])
    end_year = int(x[-1][:-4])
    total_days = 0
    for i in range(from_year, end_year + 1):
        total_days += 365
        if is_leap_year(i):
            total_days += 1
    work_day = [1] * total_days


def get_workday(fy, fm, fd, ty, tm, td):
    f, t = index_of(fy, fm, fd), index_of(ty, tm, td)
    return work_day[t] if f == 0 else work_day[t] - work_day[f - 1]


def get_totalday(fy, fm, fd, ty, tm, td):
    f, t = index_of(fy, fm, fd), index_of(ty, tm, td)
    return t - f + 1


def web_ans(fy, fm, fd, ty, tm, td):
    resp = requests.post('http://www.fynas.com/workday/count', {
        'start_date': '%d-%02d-%02d' % (fy, fm, fd),
        'end_date': '%d-%02d-%02d' % (ty, tm, td)
    })
    return resp.json()['data']['workday']


def test_right():
    for i in range(0, len(work_day)):
        x = date(2005, 1, 1) + timedelta(days=i)
        his = web_ans(x.year, x.month, x.day, x.year, x.month, x.day)
        mine = get_workday(x.year, x.month, x.day, x.year, x.month, x.day)
        if his != mine:
            print(x, his, mine)


init()
set_weekday()
load_holiday()
accumulate()
if __name__ == '__main__':
    #test_right()
    for i in range(len(work_day)):
    	print(i,work_day[i])
