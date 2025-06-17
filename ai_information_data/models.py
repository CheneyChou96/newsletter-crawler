import json


class AiInformationDataReq:
    def __init__(self):
        self.id = None
        self.title = None
        self.continent = None
        self.country = None
        self.publishColumns = None
        self.lang = None
        self.sourceUrl = None
        self.markdown = None
        self.metadata = None
        self.status = None
        self.deep = None
        self.pid = None
        self.path = None
        self.source = None
        self.failed = None
        self.publishTime = None

    def to_json_str(self):
        data = {
            "id": self.id,
            "title": self.title,
            "continent": self.continent,
            "country": self.country,
            "publishColumns": self.publishColumns,
            "lang": self.lang,
            "sourceUrl": self.sourceUrl,
            "markdown": self.markdown,
            "metadata": self.metadata,
            "status": self.status,
            "deep": self.deep,
            "pid": self.pid,
            "path": self.path,
            "source": self.source,
            "failed": self.failed,
            "publishTime": self.publishTime
        }
        return json.dumps(data, ensure_ascii=False)
