from bs4 import BeautifulSoup as bs4
import requests
import json
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
from uuid import uuid1
import pytz
import re


def list2ics(classList):
    # Calendar 对象
    calendar = Calendar()
    calendar['version'] = '2.0'
    calendar['prodid'] = '-//CDUT//TimeTable//CN'

    firstDay = datetime(2022, 2, 21, tzinfo=pytz.timezone(
        "Asia/Shanghai")) - timedelta(days=1)  # 开学第一周星期一的时间，需要修改以便学期更替

    beginTime = {
        1: timedelta(hours=8, minutes=10),
        2: timedelta(hours=9, minutes=00),
        3: timedelta(hours=10, minutes=15),
        4: timedelta(hours=11, minutes=5),
        5: timedelta(hours=14, minutes=30),
        6: timedelta(hours=15, minutes=20),
        7: timedelta(hours=16, minutes=25),
        8: timedelta(hours=17, minutes=15),
        9: timedelta(hours=19, minutes=10),
        10: timedelta(hours=20, minutes=00),
        11: timedelta(hours=20, minutes=50),
    }
    endTime = {
        1: timedelta(hours=8, minutes=55),
        2: timedelta(hours=9, minutes=45),
        3: timedelta(hours=11, minutes=00),
        4: timedelta(hours=11, minutes=50),
        5: timedelta(hours=15, minutes=15),
        6: timedelta(hours=16, minutes=5),
        7: timedelta(hours=17, minutes=10),
        8: timedelta(hours=18, minutes=0),
        9: timedelta(hours=19, minutes=55),
        10: timedelta(hours=20, minutes=45),
        11: timedelta(hours=21, minutes=35),
    }

    for item in classList:
        event = Event()
        event['uid'] = str(uuid1())

        event.add('summary', item['name'])
        # description = "教师：{}  学时：{}  学分：{}".format(
        #     item['teacher'], \
        #     item['学时'], \
        #     item['学分'] \
        # )
        description = "教师：{}".format(
            item['teacher'],
        )
        event.add('description', description)
        event.add('location', item['location'])

        # 时间
        event.add('tzid', 'Asia/Shanghai')
        startDateTime = firstDay + \
            timedelta(days=item['累计开学天数']) + \
            beginTime[item['begin']]
        endDateTime = firstDay + \
            timedelta(days=item['累计开学天数']) + \
            endTime[item['end']]

        event.add('dtstart', startDateTime)
        event.add('dtend', endDateTime)

        # 在 上课前 40 分钟前发出通知
        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', '上课前 40 分钟通知')
        alarm.add('trigger', timedelta(minutes=-40))
        event.add_component(alarm)

        # 将此 Event 添加到 Calendar
        calendar.add_component(event)

    with open(file="TimeTable.ics", mode="wb+") as icsFile:
        # 因 Windows 换行是 \r\n，而 macOS/Linux/Unix 是 \n，所以需要转换为 bytes，
        # 阻止 ics 文件的换行符变成 \r\n，导致空行问题
        icsFile.write(prettify(calendar))
    print("生成 ics 文件成功")


# 更改 ics 部分格式，使其排版更合理
def prettify(calendar):
    # 使用 bytes() 将 str 转换为 bytes
    # 修复 Windows 下运行，ics 文件中每一行都存在两个换行符，导致无法导入部分日历的问题。
    return bytes(calendar.to_ical().decode("utf-8").replace('\,', ',').strip(), encoding="utf-8")


# ! 需在登录之前先获取 Cookie 与 一些数据，以供登录时使用
def getPreCodeAndCookies():
    baseURL = "https://jw.cdut.edu.cn"
    response = requests.post(
        baseURL+"/Logon.do?method=logon&flag=sess")
    scode, sxh = response.text.split("#")
    cookies = response.cookies

    return (scode, sxh, cookies)


def getCookies(userName: str = None, password: str = None) -> dict:
    # with open("cookies.json", "w+") as f:
    #     if f.read() not in ["", None]:
    #         print("读取 cookies 成功")
    #         cookies = json.load(f)
    #         return cookies
    if userName is None or password is None:
        print("请输入用户名和密码")
        exit(0)

    baseURL = "https://jw.cdut.edu.cn"
    scode, sxh, cookies = getPreCodeAndCookies()

    # 以下只是把新教务处官网登录的 JavaScript 源代码翻译过来。
    code = userName+"%%%"+password
    encoded = ""

    i = 0
    while i < len(code):
        if i < 20:
            encoded = encoded + code[i:i + 1] + scode[0:int(sxh[i:i + 1])]
            scode = scode[int(sxh[i:i + 1]): len(scode)]
        else:
            encoded = encoded + code[i: len(code)]
            i = len(code)
        i = i + 1

    # print(encoded)
    url = baseURL+"/Logon.do?method=logon"

    data = {
        "userAccount": userName,
        "userPassword": "",
        "encoded": encoded
    }
    session = requests.Session()
    response = session.post(url=url, data=data, cookies=cookies)

    # 登录成功后 URL 会发生跳转，可依据此判断是否登录成功
    if response.url == "https://jw.cdut.edu.cn/jsxsd/framework/xsMainV.htmlx":

        newCookie = {**cookies, **session.cookies}  # 合并两个 Cookie
        # with open("cookies.json", "w") as f:
        #     json.dump(newCookie, f)

        # print(newCookie)
        print("获取 Cookie 成功")
        return newCookie
    else:
        print("获取 Cookie 失败")
        return None


def getHTML(userName=None, password=None) -> str:
    url = "https://jw.cdut.edu.cn/jsxsd/xskb/xskb_list.do"

    cookies = getCookies(userName, password)
    response = requests.get(url=url, cookies=cookies)
    html = response.text
    html = re.sub("<br>", "<br />", response.text)
    # 不然 _.children 会把一格中的第二、三、... 节课，用 <br></br> 包裹起来，成为一个子元素，不便于使用偏移量分析所有课程
    print("获取课表 HTML 表格成功")
    return html


def parseHTML(html):

    soup = bs4(html, "html.parser")
    table = soup.find('table', attrs={'id': 'timetable'})
    rows = table.find_all('tr')
    classList = []

    for row in rows:
        day = 1
        cols = row.find_all('td')    # 周一 -> 周五的每节课程

        for col in cols:
            course = col.find(
                'div', attrs={'class': 'kbcontent'})  # find course
            # 根据 .kbcontent 查询来的标签，有的是无效信息（完全没有子元素）
            if course is None:
                continue
            # 而有的格子是一学期都没有安排课的
            elif course.text == '\xa0' or course.text == " ":
                day += 1
                continue

            # print(course)
            teacher = [item.text for item in course.findAll(
                "font", title="教师")]
            location = [item.text for item in course.findAll(
                "font", title="教室")]
            relativeTime = [item.text for item in course.findAll(
                "font", title="周次(节次)")]
            detail = [item.text for item in course.findAll(
                "font", attrs={"name": "xsks"})]
            # print(detail)

            name = []
            listOfChildren = list(course.children)
            for (i, e) in enumerate(listOfChildren):
                if i == 0:
                    name.append(e)
                elif e == "---------------------":
                    name.append(listOfChildren[i+2])
                else:
                    continue
            # print(name)

            for i in range(len(name)):
                classInfo = {
                    "name": name[i],
                    "teacher": teacher[i],
                    "relativeTime": relativeTime[i],
                    "location": location[i],
                    "detail": detail[i],
                    "day": day,
                }
                classList.append(classInfo)

            day += 1

    classList = removeDuplicateClass(classList)
    # print(classList)
    print("解析 HTML 表格成功")
    return classList


def removeDuplicateClass(classList):
    tupleOfNameAndTime = []
    newClassList = []
    for e in classList:
        if (e['name'], e['relativeTime'], e['day']) not in tupleOfNameAndTime:
            newClassList.append(e)
            tupleOfNameAndTime.append((e['name'], e['relativeTime'], e['day']))
        else:
            continue
    return newClassList


def parseTime(relativeTime):
    """ 测试数据：
    relativeTime = "1,2,3-5,8-10,14-17,20(周)[01-02-03-04节]"
    """

    week = relativeTime.split('(周)')[0]
    indexInADay = relativeTime.split('(周)')[1]

    # ! 处理周
    setOfWeek = set()
    regex_1 = re.compile(r'\b\d+-\d+\b')
    regex_2 = re.compile(r'\d+')

    # 处理 "1-5" 这类情况
    group1 = regex_1.findall(week)

    # 处理 "2" 这类情况
    group2 = regex_2.findall(week)

    for e in group1:
        start = int(e.split('-')[0])
        end = int(e.split('-')[1])
        for i in range(start, end+1):
            setOfWeek.add(i)
    for e in group2:
        setOfWeek.add(int(e))

    # ! 处理节数
    regex_3 = re.compile(r'\d+')
    group3 = regex_3.findall(indexInADay)
    setOfTime = {int(e) for e in group3}

    return(setOfWeek, setOfTime)


def getDetailedClassList(classList):
    detailedClassList = []
    for e in classList:
        setOfWeek, setOfTime = parseTime(e['relativeTime'])
        # print(setOfWeek, setOfTime)

        for week in setOfWeek:

            copyOfSetOfTime = setOfTime.copy()  # 需要浅拷贝，因为后面会改变值
            while len(copyOfSetOfTime) > 0:

                begin, end = 1, 2
                if copyOfSetOfTime & {1, 2, 3, 4} == {1, 2, 3, 4}:
                    begin = 1
                    end = 4
                    copyOfSetOfTime -= {1, 2, 3, 4}
                elif copyOfSetOfTime & {5, 6, 7, 8} == {5, 6, 7, 8}:
                    begin = 5
                    end = 8
                    copyOfSetOfTime -= {5, 6, 7, 8}
                elif copyOfSetOfTime & {9, 10, 11} == {9, 10, 11}:
                    begin = 9
                    end = 11
                    copyOfSetOfTime -= {9, 10, 11}
                elif copyOfSetOfTime & {9, 10} == {9, 10}:
                    begin = 9
                    end = 10
                    copyOfSetOfTime -= {9, 10}
                elif copyOfSetOfTime & {1, 2} == {1, 2}:
                    begin = 1
                    end = 2
                    copyOfSetOfTime -= {1, 2}
                elif copyOfSetOfTime & {3, 4} == {3, 4}:
                    begin = 3
                    end = 4
                    copyOfSetOfTime -= {3, 4}
                elif copyOfSetOfTime & {5, 6} == {5, 6}:
                    begin = 5
                    end = 6
                    copyOfSetOfTime -= {5, 6}
                elif copyOfSetOfTime & {7, 8} == {7, 8}:
                    begin = 7
                    end = 8
                    copyOfSetOfTime -= {7, 8}
                elif copyOfSetOfTime & {1} == {1}:
                    begin = 1
                    end = 1
                    copyOfSetOfTime -= {1}
                elif copyOfSetOfTime & {2} == {2}:
                    begin = 2
                    end = 2
                    copyOfSetOfTime -= {2}
                elif copyOfSetOfTime & {3} == {3}:
                    begin = 3
                    end = 3
                    copyOfSetOfTime -= {3}
                elif copyOfSetOfTime & {4} == {4}:
                    begin = 4
                    end = 4
                    copyOfSetOfTime -= {4}
                elif copyOfSetOfTime & {5} == {5}:
                    begin = 5
                    end = 5
                    copyOfSetOfTime -= {5}
                elif copyOfSetOfTime & {6} == {6}:
                    begin = 6
                    end = 6
                    copyOfSetOfTime -= {6}
                elif copyOfSetOfTime & {7} == {7}:
                    begin = 7
                    end = 7
                    copyOfSetOfTime -= {7}
                elif copyOfSetOfTime & {8} == {8}:
                    begin = 8
                    end = 8
                    copyOfSetOfTime -= {8}
                elif copyOfSetOfTime & {9} == {9}:
                    begin = 9
                    end = 9
                    copyOfSetOfTime -= {9}
                elif copyOfSetOfTime & {10} == {10}:
                    begin = 10
                    end = 10
                    copyOfSetOfTime -= {10}
                elif copyOfSetOfTime & {11} == {11}:
                    begin = 11
                    end = 11
                    copyOfSetOfTime -= {11}

                # 很不明白为什么会有 12 节，但是有的课表确实存在。
                elif copyOfSetOfTime & {12} == {12}:
                    copyOfSetOfTime -= {12}

                # print(begin, end)
                detailedClassList.append({
                    "name": e['name'],
                    # "type": e['type'],
                    "teacher": e['teacher'],
                    "location": e['location'],
                    # "detail": e['detail'],
                    "累计开学天数": (week-1)*7+e['day'],
                    "begin": begin,
                    "end": end
                })

            # print(listOfTime)
    # print(detailedClassList)
    print("处理课程数据成功")
    return detailedClassList


def main():
    with open("account.json", "r+", encoding="utf-8") as f:
        accountInfo = json.load(f)
    userName, password = accountInfo['userName'], accountInfo['password']
    try:
        assert userName != "" and password != ""
    except:
        print("请先在 account.json 中设置阁下在新版教务系统的用户名和密码")
        return

    html = getHTML(userName, password)
    classList = parseHTML(html)
    detailedClassList = getDetailedClassList(classList)

    list2ics(detailedClassList)


if __name__ == '__main__':
    main()
