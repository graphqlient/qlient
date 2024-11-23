from collections.abc import AsyncGenerator

import aiohttp

from qlient.aiohttp.consts import CONNECTION_TERMINATE, CONNECTION_ERROR, COMPLETE, CONNECTION_KEEP_ALIVE, STOP
from qlient.aiohttp.settings import AIOHTTPSettings
from qlient.core import GraphQLResponse, GraphQLSubscriptionRequest


class GraphQLSubscriptionResponse(GraphQLResponse):
    request: GraphQLSubscriptionRequest

    def __init__(
        self,
        request: GraphQLSubscriptionRequest,
        socket: aiohttp.ClientWebSocketResponse,
        settings: AIOHTTPSettings | None = None,
    ):
        if settings is None:
            settings = AIOHTTPSettings()

        self.__active: bool = False
        self.ws: aiohttp.ClientWebSocketResponse = socket
        self.settings: AIOHTTPSettings = settings

        super().__init__(request, self.message_generator())

    async def message_generator(self) -> AsyncGenerator:
        msg: aiohttp.WSMessage
        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.ERROR:
                # break the iterator
                await self.ws.close()
                break

            if msg.type != aiohttp.WSMsgType.TEXT:
                raise TypeError(f"Expected {aiohttp.WSMsgType.TEXT}; Got {msg.type}")

            data = msg.json(loads=self.settings.json_loads)
            data_type = data["type"]

            if data_type in (CONNECTION_TERMINATE, CONNECTION_ERROR, COMPLETE):
                # break the iterator
                await self.close()
                break

            if data_type == CONNECTION_KEEP_ALIVE:
                continue

            yield GraphQLResponse(self.request, data["payload"])

    async def end(self):
        await self.ws.send_str(self.settings.json_dumps({"type": STOP, "id": self.request.subscription_id}))

    async def close(self):
        await self.end()
        await self.ws.close()
