from backend.util import get_config

config = get_config()


class ExamHtmlDownloader:
    def __init__(self, session) -> None:
        self.session = session

    async def getHtml(self) -> str:
        url = config["jw_api_path"]["baseUrl"] + config["jw_api_path"]["examHTML"]

        payload = {"xnxqid": config["termId"]}

        async with self.session.post(url, data=payload) as response:
            html = await response.text()
            return html
