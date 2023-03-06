import aiohttp
from backend.converter.timetable_to_ics import TimetableToICalendar
from backend.crawler.downloader.course_table_downloader import CourseTableDownloader
from backend.crawler.login.LoginHelper import LoginHelper
from backend.crawler.parser.course_html_parser import CourseHtmlParser
from backend.crawler.parser.exam_html_parser import ExamHtmlParser
from backend.crawler.downloader.exam_html_downloader import ExamHtmlDownloader


async def getCalendar(userName, password, md5):
    # Login to get HTML
    async with aiohttp.ClientSession() as session:
        loginHelper = LoginHelper(session)
        isSccessful = await loginHelper.login(userName, password)

        if not isSccessful:
            return False

        courseHtmlDownloader = CourseTableDownloader(session)
        courseHtml = await courseHtmlDownloader.getHtml()

        examHtmlDownloader = ExamHtmlDownloader(session)
        examHtml = await examHtmlDownloader.getHtml()

    # Parse courses HTML table
    courseHtmlParser = CourseHtmlParser(courseHtml)
    courseList = await courseHtmlParser.getCoursesList()

    # Parse exams HTML table
    examHtmlParser = ExamHtmlParser(examHtml)
    examList = await examHtmlParser.getExamList()

    # Save to ics file
    timetableToICalendar = TimetableToICalendar(courseList, examList)
    return timetableToICalendar.convertToIcsFile(md5)
