import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any

import aiohttp

from qlient.aiohttp.consts import (
    GRAPHQL_WS_PROTOCOL,
    GRAPHQL_TRANSPORT_WS_PROTOCOL,
    CONNECTION_INIT,
    CONNECTION_ACKNOWLEDGED,
    START,
)
from qlient.aiohttp.exceptions import ConnectionRejected
from qlient.aiohttp.models import GraphQLSubscriptionResponse
from qlient.aiohttp.settings import AIOHTTPSettings
from qlient.core import (
    AsyncBackend,
    GraphQLRequest,
    GraphQLResponse,
    GraphQLSubscriptionRequest,
)

logger = logging.getLogger("qlient")

SUBSCRIPTION_ID_TO_RESPONSE: dict[str, GraphQLSubscriptionResponse] = {}


async def close_all():
    for subscription_id, response in SUBSCRIPTION_ID_TO_RESPONSE.items():
        logger.info(f"Ending subscription {subscription_id}")
        await response.close()


class AIOHTTPBackend(AsyncBackend):
    """The AIOHTTP Backend.

    Examples:
        >>> backend = AIOHTTPBackend("https://swapi-graphql.netlify.app/.netlify/functions/index")
        >>> result = await backend.execute_query(...)
    """

    @classmethod
    def generate_subscription_id(cls) -> str:
        """Class method to generate unique subscription ids.

        Returns:
            A unique subscription id
        """
        return f"qlient:{cls.__name__}:{uuid.uuid4()}".replace("-", "")

    @staticmethod
    def make_payload(request: GraphQLRequest) -> dict[str, Any]:
        """Static method for generating the request payload.

        Args:
            request: holds the graphql request

        Returns:
            the payload to send as dictionary
        """
        return {
            "query": request.query,
            "operationName": request.operation_name,
            "variables": request.variables,
        }

    def __init__(
            self,
            endpoint: str,
            ws_endpoint: str | None = None,
            session: aiohttp.ClientSession | None = None,
            subscription_protocols: list[str] | None = None,
            settings: AIOHTTPSettings | None = None,
    ):
        if settings is None:
            settings = AIOHTTPSettings()

        if not subscription_protocols:
            subscription_protocols = [
                GRAPHQL_WS_PROTOCOL,
                GRAPHQL_TRANSPORT_WS_PROTOCOL,
            ]

        self.settings: AIOHTTPSettings = settings
        self.endpoint: str = endpoint
        self.ws_endpoint: str = ws_endpoint or self.endpoint
        self.subscription_protocols = subscription_protocols
        self._session: aiohttp.ClientSession | None = session

    @property
    @asynccontextmanager
    async def session(self) -> aiohttp.ClientSession:
        """Property to get the session to use for requests.

        If the session is pre-defined, use that session,
        otherwise create a new aiohttp.ClientSession.

        Returns:
            the ClientSession to use
        """
        if self._session is not None:
            yield self._session
            return

        async with aiohttp.ClientSession() as session:
            yield session

    async def execute_query(self, request: GraphQLRequest) -> GraphQLResponse:
        """Method to execute a query on the http server.

        First the request is transformed to a payload.
        >>> {
        >>>     "query": "query X { X { ... } }",
        >>>     "variables": {},
        >>>     "operationName": ""
        >>> }

        Args:
            request: holds the request to execute on the http endpoint

        Returns:
            the query GraphQLResponse
        """
        payload_dict = self.make_payload(request)
        payload_str = self.settings.json_dumps(payload_dict)
        logger.debug(f"Sending request: {payload_str}")
        async with self.session as session:
            async with session.post(
                    self.endpoint,
                    data=payload_str,
                    headers={
                        "Content-Type": "application/json; charset=utf-8",
                        "Accept": "application/json; charset=utf-8",
                    }
            ) as response:
                response_str = await response.text()
                response_body = self.settings.json_loads(response_str)
                return GraphQLResponse(request, response_body)

    async def execute_mutation(self, request: GraphQLRequest) -> GraphQLResponse:
        """Method to execute a mutation on the http server.

        Because a mutation handles the same as a query over http,
        it just calls the execute_query function without any further changes.

        Args:
            request: holds the request to execute on the http endpoint

        Returns:
            the query GraphQLResponse
        """
        return await self.execute_query(request)

    async def execute_subscription(self, request: GraphQLSubscriptionRequest) -> GraphQLResponse:
        """Initiate a subscription and start listening to messages.

        This opens a websocket connection and starts the initiation sequence.

        First send the "connection_init" request with the request.options.
        Second await the "connection_ack" message from the server.
        Third "start" the subscription and wait for incoming messages.

        Args:
            request: holds the request to execute

        Returns:
        """
        payload = self.make_payload(request)
        async with self.session as session:
            request.subscription_id = request.subscription_id or self.generate_subscription_id()

            ws = await session.ws_connect(self.endpoint, protocols=self.subscription_protocols, autoclose=False)

            # initiate connection
            await ws.send_str(self.settings.json_dumps({"type": CONNECTION_INIT, "payload": request.options}))

            initial_response = self.settings.json_loads(await ws.receive_str())
            if initial_response["type"] != CONNECTION_ACKNOWLEDGED:
                logger.critical("The server did not acknowledged the connection.")
                raise ConnectionRejected("The server did not acknowledge the connection.")

            # connection acknowledged, start subscription
            await ws.send_str(
                self.settings.json_dumps({"type": START, "id": request.subscription_id, "payload": payload})
            )

            response = GraphQLSubscriptionResponse(request, ws, settings=self.settings)

            SUBSCRIPTION_ID_TO_RESPONSE[request.subscription_id] = response

            return response
