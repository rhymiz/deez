# Stubs for deez.resource (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from deez import Request

class Resource:
    def dispatch(self, method: str=..., request: Request=..., *args: Any, **kwargs: Any) -> Any: ...
    def get_class_name(self): ...
