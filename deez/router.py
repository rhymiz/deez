import re
from functools import lru_cache
from typing import Any, Dict, Match, Optional

from deez.exceptions import DuplicateRouteError, NoResponseError, NotFound404
from deez.request import Request


class Router:
    def __init__(self, app):
        self._app = app
        self._routes = {}
        self._route_names = {}
        self._route_patterns = []

    @lru_cache(maxsize=1000)
    def _get_re_match(self, path: str, method: str) -> Optional[Match]:
        matched_patterns = [
            re.search(pattern, path)
            for _, pattern in enumerate(self._route_patterns)
        ]

        if not matched_patterns:
            return None

        if len(matched_patterns) > 1:
            best_match = [
                match for _, match in enumerate(matched_patterns)
                if match and hasattr(self._routes[match.re.pattern], method)
            ]

            # method required to serve this request was not implemented
            if not best_match:
                return None

            best_pattern = None
            best_group_count = 0

            for _, best in enumerate(best_match):
                groups_len = len(best.groups())
                if groups_len > best_group_count:
                    best_pattern = best
                    best_group_count = groups_len
            return best_pattern
        else:
            return matched_patterns[0]

    def _execute(self, event=None, context=None) -> Any:
        path = event['path']
        method = event['httpMethod'].lower()
        headers = event['headers']
        url_params = event['queryStringParameters']
        request_body = event['body']

        re_match = self._get_re_match(path=path, method=method)
        if not re_match:
            raise NotFound404(f'{method.upper()} \'{path}\' not found!')

        view_class = self._routes[re_match.re.pattern]()

        request = Request(path, method, body=request_body, event=event,
                          headers=headers, context=context, url_params=url_params)

        # middleware that needs to run before calling the view
        middleware = self._app.middleware

        for _, m in enumerate(middleware):
            _request = m(view=view_class).before_request(request=request)
            if _request:
                request = _request

        kwargs = re_match.groupdict()
        response = view_class(method, request, **kwargs)
        if not response:
            raise NoResponseError(f'{view_class.get_class_name()} did not return anything')

        # middleware that needs to run before response
        for _, m in enumerate(reversed(middleware)):
            _response = m(view=view_class).before_response(response=response)
            if _response:
                response = _response

        if hasattr(response, 'render'):
            return response.render(self._app.template_loader)
        return response

    def _validate_path(self, path: str) -> None:
        if path in self._routes:
            raise DuplicateRouteError(f"\"{path}\" already defined")

    def register(self, path: str, view) -> None:
        self._validate_path(path)
        self._routes[path] = view
        self._route_patterns.append(re.compile(path))

    def route(self, event: Dict, context: object) -> Any:
        return self._execute(event=event, context=context)