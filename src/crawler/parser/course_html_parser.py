from bs4 import BeautifulSoup as bs


import crawler.util
import re


class CourseHtmlParser:
    rawHtml = None
    dilutedCoursesList: list = []
    detailedClassList: list = []

    def __init__(self, rawHtml):
        self.rawHtml = rawHtml

    async def getCoursesList(self):
        await self.parseHTML()
        self.removeDuplicateClass()
        self.getDetailedClassList()
        print(self.detailedClassList)
        return self.detailedClassList

    async def parseHTML(self):

        soup = bs(self.rawHtml, "html.parser")
        table = soup.find("table", attrs={"id": "timetable"})
        rows = table.find_all("tr")
        coursesList = []

        for row in rows:
            day = 1
            cols = row.find_all("td")  # 周一 -> 周五的每节课程

            for col in cols:
                course = col.find("div", attrs={"class": "kbcontent"})  # find course
                # 根据 .kbcontent 查询来的标签，有的是无效信息（完全没有子元素）
                if course is None:
                    continue
                # 而有的格子是一学期都没有安排课的
                elif course.text == "\xa0" or course.text == " ":
                    day += 1
                    continue

                # print(course)
                teacher = [item.text for item in course.findAll("font", title="教师")]
                location = [item.text for item in course.findAll("font", title="教室")]
                relativeTime = [
                    item.text for item in course.findAll("font", title="周次(节次)")
                ]
                detail = [
                    item.text for item in course.findAll("font", attrs={"name": "xsks"})
                ]
                # print(detail)

                coursesInATableElement = []
                listOfChildren = list(course.children)
                for (i, e) in enumerate(listOfChildren):
                    if i == 1:
                        coursesInATableElement.append(e.text)
                    elif e == "---------------------":
                        coursesInATableElement.append(listOfChildren[i + 3].text)
                    else:
                        continue

                for i in range(len(coursesInATableElement)):
                    course = {
                        "name": coursesInATableElement[i],
                        "teacher": teacher[i],
                        "relativeTime": relativeTime[i],
                        "location": location[i],
                        "detail": detail[i],
                        "day": day,
                    }
                    coursesList.append(course)

                day += 1

        self.dilutedCoursesList = coursesList
        # print(self.dilutedCoursesList)
        print("解析 HTML 表格成功")

        return True

    def removeDuplicateClass(self):
        tupleOfNameAndTime = []
        newClassList = []
        for e in self.dilutedCoursesList:
            if (e["name"], e["relativeTime"], e["day"]) not in tupleOfNameAndTime:
                newClassList.append(e)
                tupleOfNameAndTime.append((e["name"], e["relativeTime"], e["day"]))
            else:
                continue
        self.dilutedCoursesList = newClassList
        return True

    def getDetailedClassList(self):
        try:
            for e in self.dilutedCoursesList:
                setOfWeek, setOfTime = self.parseTime(e["relativeTime"])
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
                        self.detailedClassList.append(
                            {
                                "name": e["name"],
                                # "type": e['type'],
                                "teacher": e["teacher"],
                                "location": e["location"],
                                "detail": e["detail"],
                                "累计开学天数": (week - 1) * 7 + e["day"],
                                "begin": begin,
                                "end": end,
                            }
                        )

                    # print(listOfTime)
            # print(self.detailedClassList)
            print("处理课程数据成功")
            return True
        except Exception as e:
            print(e)
            return False

    def parseTime(self, relativeTime):
        """测试数据：
        relativeTime = "1,2,3-5,8-10,14-17,20(周)[01-02-03-04节]"
        """

        week = relativeTime.split("(周)")[0]
        indexInADay = relativeTime.split("(周)")[1]

        # ! 处理周
        setOfWeek = set()
        regex_1 = re.compile(r"\b\d+-\d+\b")
        regex_2 = re.compile(r"\d+")

        # 处理 "1-5" 这类情况
        group1 = regex_1.findall(week)

        # 处理 "2" 这类情况
        group2 = regex_2.findall(week)

        for e in group1:
            start = int(e.split("-")[0])
            end = int(e.split("-")[1])
            for i in range(start, end + 1):
                setOfWeek.add(i)
        for e in group2:
            setOfWeek.add(int(e))

        # ! 处理节数
        regex_3 = re.compile(r"\d+")
        group3 = regex_3.findall(indexInADay)
        setOfTime = {int(e) for e in group3}

        return (setOfWeek, setOfTime)

    def sortDetailedClassList(self) -> list:
        # 按照累计开学天数、开始的时间序号排序
        self.detailedClassList.sort(key=lambda x: (x["累计开学天数"], x["begin"]))

    def concatenateAdjacentCourses(self):
        for i in range(self.detailedClassList):
            if (
                self.detailedClassList[i]["name"]
                == self.detailedClassList[i + 1]["name"]
            ):
                if (
                    self.detailedClassList["累计开学天数"]
                    == self.detailedClassList[i + 1]["累计开学天数"]
                ):
                    if (
                        self.detailedClassList["end"]
                        == self.detailedClassList[i + 1]["begin"] - 1
                    ):
                        self.detailedClassList[i]["end"] = self.detailedClassList[
                            i + 1
                        ]["end"]
                        self.detailedClassList.pop(i + 1)
