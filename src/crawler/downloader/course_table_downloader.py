from util import get_config

import re


config = get_config()


class CourseTableDownloader:
    # rawHtml = None

    def __init__(self, session) -> None:
        self.session = session

    async def getHtml(self) -> str:
        url = (
            config["jw_api_path"]["baseUrl"] + config["jw_api_path"]["courseTableHTML"]
        )
        print(url)

        payload = {"xnxq01id": config["termId"]}  # 当前学期的 id

        async with self.session.post(url=url, data=payload) as response:

            rawHtml = await response.text()
            
            rawHtml = re.sub("<br>", "<br />", rawHtml)
            # 不然 _.children 会把一格中的第二、三、... 节课，用 <br></br> 包裹起来，成为一个子元素，不便于使用偏移量分析所有课程
            print("获取课表 HTML 表格成功")
            
            return rawHtml
