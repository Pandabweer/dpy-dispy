from sanic.views import HTTPMethodView
from sanic.exceptions import InvalidUsage
from sanic.response import json

from aiohttp import ClientSession

CLIENT_ID = 822427264574160928
CLIENT_SECRET = "iHYzryh9KyzJLnPLY8LxgbQVcc0lIywm"

REDIRECT_URI = "http://127.0.0.1:8000/oauth/callback"
OATH_URI = "https://discord.com/api/oauth2/authorize?client_id=822427264574160928&redirect_uri=http%3A%2F%2F127.0.0.1%3A8000%2Foauth%2Fcallback&response_type=code&scope=identify%20guilds"


class CallbackView(HTTPMethodView):
    @staticmethod
    async def get(request):
        code = request.args.get("code")
        print(code)

        if not code:
            raise InvalidUsage("Invalid request")

        async with ClientSession() as session:
            response = await session.post("https://discord.com/api/oauth2/token", data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI
                }, headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )

        return json(await response.json())
