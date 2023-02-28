from util import get_config
from bs4 import BeautifulSoup as bs
from datetime import datetime
from zoneinfo import ZoneInfo

config = get_config()


class ExamHtmlParser:
    rawHtml: str = None
    examList: list = []

    def __init__(self, rawHtml) -> None:
        self.rawHtml = rawHtml

    def parseHtml(self):
        soup = bs(self.rawHtml, "html.parser")
        table = soup.find("table", attrs={"id": "dataList"})
        rows = table.find_all("tr")
        for i, e in enumerate(rows):
            # 表格标题
            if i == 0:
                continue

            listOfChildren = list(e.children)

            # 若不存在考试
            if len(listOfChildren) <= 1:
                continue

            # 正常逻辑
            # for i, e in enumerate(listOfChildren):
            #     print(f"{i}: {e.text}")

            self.examList.append(
                {
                    "name": listOfChildren[11].text,
                    "teacher": listOfChildren[13].text,
                    "datetime": listOfChildren[15].text,
                    "location": listOfChildren[17].text,
                    "seat": listOfChildren[19].text,
                }
            )

    def parseTime(self):
        for i in range(len(self.examList)):
            (
                self.examList[i]["startTime"],
                self.examList[i]["endTime"],
            ) = self.timeParser(self.examList[i]["datetime"])

    def getExamList(self):
        self.parseHtml()
        self.parseTime()
        print(self.examList)
        return self.examList

    def timeParser(self, timeToParse):
        date, time = timeToParse.split(" ")

        year, month, day = [int(e) for e in date.split("-")]
        startTime, endTime = time.split("~")

        startHour, startMinute = [int(e) for e in startTime.split(":")]
        endHour, endMinute = [int(e) for e in endTime.split(":")]

        startDateTime = datetime(
            year=year,
            month=month,
            day=day,
            hour=startHour,
            minute=startMinute,
            tzinfo=ZoneInfo("Asia/Shanghai"),
        )
        endDateTime = datetime(
            year=year,
            month=month,
            day=day,
            hour=endHour,
            minute=endMinute,
            tzinfo=ZoneInfo("Asia/Shanghai"),
        )

        return startDateTime, endDateTime
