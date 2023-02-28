import asyncio
from crawler.login.LoginHelper import main
from crawler.parser.exam_html_parser import ExamHtmlParser


def main():
    with open("src/1.txt", "r") as file:
        html = file.read()
    examHtmlParser = ExamHtmlParser(html)
    examHtmlParser.getExamList()


if __name__ == "__main__":
    # asyncio.run(main())
    main()
