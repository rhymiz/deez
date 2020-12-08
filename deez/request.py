import json
from json import JSONDecodeError
from typing import Any, Dict, Optional

from deez.logger import get_logger


class Header:
    def __init__(self, data: Dict[str, str]) -> None:
        self.data = data

    def get(self, key: str) -> Optional[str]:
        return self.data.get(key)


class Post:
    def __init__(self, body: str) -> None:
        self.data = {}
        self.content = body
        self._loads(body)

    def _loads(self, body: Any):
        if isinstance(body, dict):
            self.data = body

        # If we can't decode the payload automatically
        # it is up to the developer to handle dealing with
        # the content of the request.
        if isinstance(body, (str, bytes)):
            try:
                self.data = json.loads(body)
            except JSONDecodeError:
                get_logger().warning(
                    "unable to decode `POST#data`. "
                    "decoding must be handled manually and is "
                    "available in POST#content.")
                pass

    def get(self, key: str) -> Optional[Any]:
        return self.data.get(key)


class Get:
    def __init__(self, params: Dict[str, Any]) -> None:
        self.data = params

    def get(self, key: str) -> Optional[Any]:
        return self.data.get(key) if self.data else None


class Request:
    def __init__(self, event, context):
        self.raw_event = event
        self.lambda_context = context
        self.GET = Get(event.get('queryStringParameters', {}))
        self.POST = Post(event.get('body', {}))
        self.HEADERS = Header(event.get('headers', {}))
        self.kwargs = {}

    @property
    def path(self) -> str:
        return self.raw_event['path']

    @property
    def method(self) -> str:
        return self.raw_event['httpMethod']

    def __str__(self):
        return '%s %s' % (self.method, self.path)

    def __getattr__(self, item):
        return self.__dict__.get(item)
