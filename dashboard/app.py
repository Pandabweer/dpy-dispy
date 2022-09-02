from sanic import Sanic
from sanic.log import logger
from sanic.response import json, text
from sanic.views import HTTPMethodView
from sanic_cors import CORS

from backend.callback import CallbackView
from backend.users import UsersView


class MainView(HTTPMethodView):
    @staticmethod
    async def get(request):
        logger.info('Here is your log')
        return text('Hello World!')


app = Sanic("Discord_dashboard")
CORS(app)
app.add_route(MainView.as_view(), "/")
app.add_route(CallbackView.as_view(), "/oauth/callback")
app.add_route(UsersView.as_view(), "/users/me")


if __name__ == "__main__":
    app.run(debug=True, access_log=True)
