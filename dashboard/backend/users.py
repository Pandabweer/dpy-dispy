from sanic.views import HTTPMethodView
from sanic.exceptions import InvalidUsage
from sanic.response import json

from hikari import RESTApp
from hikari.users import OwnUser

rest_api = RESTApp()


class UsersView(HTTPMethodView):
    user: OwnUser

    @staticmethod
    async def get(request) -> json:
        token = request.args.get("token")

        if not token:
            raise InvalidUsage("Invalid request")

        async with rest_api.acquire(token) as client:
            user = await client.fetch_my_user()

        return json({
            "id": str(user.id),
            "username": str(user.username),
            "discriminator": str(user.discriminator),
            "avatar_url": str(user.avatar_url)
        })
