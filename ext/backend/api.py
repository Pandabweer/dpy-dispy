import aiohttp_cors

from aiohttp.web import TCPSite, Application, AppRunner, json_response
from aiohttp.web_request import Request

from log import log


class DispyApi:
    def __init__(self) -> None:
        self.client = None
        self.app = Application()
        self.cors = aiohttp_cors.setup(self.app)
        self.setup_routes()

    async def start(self, client) -> None:
        runner = AppRunner(self.app)
        await runner.setup()

        client.api = TCPSite(runner, "0.0.0.0", 6969)

        await client.wait_until_ready()
        await client.api.start()
        self.client = client
        log.info("Started the bot API")

    async def get_status(self, request: Request) -> dict:
        return json_response({"Guilds": len(self.client.guilds)})

    def setup_routes(self) -> None:
        resource = self.cors.add(self.app.router.add_resource("/status"))
        self.cors.add(
            resource.add_route("GET", self.get_status), {
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                )
            })
