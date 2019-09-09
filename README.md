# Deez (Under Development)
A little library I building to simplify building small web services (mostly APIs) on top of AWS Lambda.

> ##### DOCUMENTATION TBD

### Installation
`pip install deez`

### Example of how to use
Note: The Deez router uses regex for path matching.

`app.py`
```python
from deez import Deez
from deez.views import View
from deez.response import JsonResponse


class HelloWorldView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(data={'message': 'hello world'})


app = Deez()
app.register_route('^hello/world$', HelloWorldView)
```

`middleware.py`
```python
from deez.middleware import Middleware

class User:
    # fake user object
    pass

class AuthMiddleware(Middleware):
    def before_request(self, request):
        # do auth things
        request.user = User() 
        return request
```

`settings.py`
```python
# middleware runs before views are called and before the response is returned
# so you can manipulate the response and requests objects.
MIDDLEWARE = ['middleware.AuthMiddleware']
```

`handler.py`
```python

from app import app

def handle_event(event, context):
    return app.process_request(event, context)
```