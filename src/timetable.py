from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
from uuid import uuid1
from zoneinfo import ZoneInfo


import json
from crawler.downloader.course_table_downloader import CourseTableDownloader
from crawler.login.LoginHelper import LoginHelper
from crawler.parser.course_html_parser import CourseHtmlParser
from util import get_config


config = get_config()

# 开学第一周星期一的时间（需要与课表上的匹配），学期更替时应更改
firstDayInOneTerm = datetime(
    year=config["firstDayInOneTerm"]["year"],
    month=config["firstDayInOneTerm"]["month"],
    day=config["firstDayInOneTerm"]["day"],
    tzinfo=ZoneInfo("Asia/Shanghai"),
)


def list2ics(fileName: str, classList: list):
    # Calendar 对象
    calendar = Calendar()
    calendar["version"] = "2.0"
    calendar["prodid"] = "-//CDUT//TimeTable//CN"

    firstDay = firstDayInOneTerm - timedelta(days=1)

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

        event["uid"] = str(uuid1())  # 每个日程都会有一个唯一的 uuid

        event.add("summary", item["name"])

        # description = f"教师：{item['teacher']}  学时：{item['学时']}  学分：{item['学分']}"

        description = "教师：{item['teacher']}"
        event.add("description", description)
        event.add("location", item["location"])

        # 时间
        event.add("tzid", "Asia/Shanghai")
        startDateTime = (
            firstDay + timedelta(days=item["累计开学天数"]) + beginTime[item["begin"]]
        )

        endDateTime = firstDay + timedelta(days=item["累计开学天数"]) + endTime[item["end"]]

        event.add("dtstart", startDateTime)
        event.add("dtend", endDateTime)

        # 在 上课前 30 分钟前发出通知
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", "上课前 30 分钟通知")
        alarm.add("trigger", timedelta(minutes=-30))
        event.add_component(alarm)

        # 将此 Event 添加到 Calendar
        calendar.add_component(event)

    with open(file=f"timetable/{fileName}.ics", mode="wb+") as icsFile:
        icsFile.write(prettify(calendar))

    print("生成 ics 文件成功")


# 更改 ics 部分格式，使其排版更合理
def prettify(calendar):
    # 使用 bytes() 将 str 转换为 bytes
    # 因 Windows 换行是 \r\n，而 macOS/Linux/Unix 是 \n，所以需要转换为 bytes，
    # 阻止问题：ics 文件的换行符变成 \r\n，导致空行 => 无法被部分日历软件正确解析。
    return bytes(
        calendar.to_ical().decode("utf-8").replace("\,", ",").strip(), encoding="utf-8"
    )


#  TODO - choose sign method from here
#


def timetable2ics(timetable: list, fileName: str):
    # Calendar 对象
    calendar = Calendar()
    calendar["version"] = "2.0"
    calendar["prodid"] = "-//CDUT//TimeTable//CN"

    for item in timetable:
        event = Event()

        event["uid"] = str(uuid1())  # 每个日程都会有一个唯一的 uuid
        event.add("tzid", "Asia/Shanghai")
        event.add("summary", item["name"])
        event.add("description", item["description"])
        event.add("location", item["location"])

        # 时间
        event.add("dtstart", item["startDateTime"])
        event.add("dtend", item["endDateTime"])

        # 在 上课前 30 分钟前发出通知
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", "上课前 30 分钟通知")
        alarm.add("trigger", timedelta(minutes=-30))
        event.add_component(alarm)

        # 将此 Event 添加到 Calendar
        calendar.add_component(event)

    with open(file=f"timetable/{fileName}.ics", mode="wb+") as icsFile:
        icsFile.write(prettify(calendar))

    print("生成 ics 文件成功")


def getUser():
    with open("config.json", "r+", encoding="UTF-8") as f:
        user = json.load(f)

    md5 = "课程表"
    return (user["userName"], user["password"], md5)


async def getCalendar(userName, password, md5):
    async with aiohttp.ClientSession() as session:
        loginHelper = LoginHelper(session)
        isSccessful = await loginHelper.login(userName, password)

        if not isSccessful:
            return False

        courseHtmlDownloader = CourseTableDownloader(session)
        html = await courseHtmlDownloader.getHtml()

    courseHtmlParser = CourseHtmlParser(html)
    courseList = await courseHtmlParser.getCoursesList()

    list2ics(md5, courseList, isRunByServer=True)
    return True


# if __name__ == "__main__":
#     main()
