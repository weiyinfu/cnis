import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class WorkdayUtil {
static int[] days;
static long begDay;
static Path folder = Paths.get("holiday");

static {
    load();
}

public static void load() {
    try {
        Stream<Path> files = Files.list(folder);
        List<Integer> years = files.map(x -> Integer.parseInt(x.getFileName().toString().substring(0, 4))).sorted().collect(Collectors.toList());
        int maxYear = years.get(years.size() - 1);
        int minYear = years.get(0);
        boolean flag = true;
        for (int i = 0; i < years.size(); i++) {
            if (years.get(i) != i + minYear) {
                flag = false;
                break;
            }
        }
        if (flag == false) {
            throw new RuntimeException("文件夹中年份不连续");
        }
        int totalDays = years.stream().mapToInt(i -> LocalDate.ofYearDay(i, 1).isLeapYear() ? 366 : 365).sum();
        begDay = LocalDate.ofYearDay(minYear, 1).toEpochDay();
        days = new int[totalDays];
        //每一天都是工作日
        for (int i = 0; i < days.length; i++) {
            days[i] = 1;
        }
        //去掉周末
        int first = LocalDate.ofYearDay(minYear, 1).getDayOfWeek().getValue();
        for (int i = (6 - first + 7) % 7; i < days.length; i += 7) {
            days[i] = 0;
        }
        for (int i = (7 - first + 7) % 7; i < days.length; i += 7) {
            days[i] = 0;
        }
        //加载法定节假日
        Pattern form1 = Pattern.compile("(\\d+)\\.(\\d+)-(\\d+)\\.(\\d+)");
        for (int i = minYear; i <= maxYear; i++) {
            Stream<String> lines = Files.lines(folder.resolve(i + ".txt"), Charset.forName("utf8"));
            final int nowYear = i;
            lines.forEach(x -> {
                x = x.trim();
                if (x.length() == 0) return;
                if (x.contains("-")) {
                    Matcher res = form1.matcher(x);
                    res.find();
                    int fm = Integer.parseInt(res.group(1));
                    int fd = Integer.parseInt(res.group(2));
                    int tm = Integer.parseInt(res.group(3));
                    int td = Integer.parseInt(res.group(4));
                    for (int j = (int) (LocalDate.of(nowYear, fm, fd).toEpochDay() - begDay); j <= LocalDate.of(nowYear, tm, td).toEpochDay() - begDay; j++) {
                        days[j] = 0;
                    }
                } else {
                    int dotPos = x.indexOf(".");
                    int dayId = (int) (LocalDate.of(nowYear, Integer.parseInt(x.substring(0, dotPos)), Integer.parseInt(x.substring(dotPos + 1))).toEpochDay() - begDay);
                    days[dayId] = 1;
                }
            });
        }
        for (int i = 1; i < days.length; i++) {
            days[i] += days[i - 1];
        }
    } catch (IOException e) {
        e.printStackTrace();
    }
}

public static int workdays(int fYear, int fMonth, int fDay, int tYear, int tMonth, int tDay) {
    return workdays(LocalDate.of(fYear, fMonth, fDay), LocalDate.of(tYear, tMonth, tDay));
}

private static int workdays(LocalDate from, LocalDate to) {
    int f = (int) (from.toEpochDay() - begDay);
    int t = (int) (to.toEpochDay() - begDay);
    if (f == 0) return days[t];
    return days[t] - days[f - 1];
}

public static void main(String[] args) throws FileNotFoundException {
    System.out.println(WorkdayUtil.workdays(2017, 9, 26, 2017, 10, 26));
}
}
