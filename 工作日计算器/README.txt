holiday文件夹中表示各个年份的法定节假日数据。
1.1-1.3 表示1月1日、1月2日、1月3日这三天为假期。
1.1-1.1 表示1月1日为假期
如果没有“-”，单独一行1.4表示1月4日是工作日。
也就是说，如果包含“-”，表示一个时间段，表示放假时间，这是一个前闭后闭区间。
如果不包含“-”，表示一个时间点，表示工作时间，这是一个时间点。

举个例子：1.1-1.5（周一到周五）放了五天假，1.6和1.7（周六周日）需要补课，那么就写成：
1.1-1.5
1.6
1.7


首先，一个int数组a[N]，表示有N天。
a[0]表示2005年1月1日。
如果a[0]==1，表示第0天是工作日；
如果a[0]==0，表示第0天是假期。
一开始，整个数组a[N]全为1，表示全部都是工作日。
然后，把全部的周六、周日置为0，表示休息。
最后，读取法定节假日数据，把该置为0的时间段置为0，该置为1的时间点置为1。