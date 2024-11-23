from collections.abc import AsyncGenerator, AsyncIterator, Generator, Iterator
from typing import (
    Any,
    Optional,
    Union,
)

JSON = Union[str, int, float, bool, None, dict[str, "JSON"], list["JSON"]]

RawSchema = dict[str, JSON]

GraphQLQueryType = str
GraphQLVariablesType = Optional[dict[str, JSON]]
GraphQLOperationNameType = Optional[str]
GraphQLReturnType = dict[str, JSON]
GraphQLReturnTypeIterator = Union[Iterator[GraphQLReturnType], Generator[GraphQLReturnType, None, None]]
AsyncGraphQLReturnTypeIterator = Union[AsyncIterator[GraphQLReturnType], AsyncGenerator[GraphQLReturnType, None]]
GraphQLAnyReturnType = Union[GraphQLReturnType, GraphQLReturnTypeIterator, AsyncGraphQLReturnTypeIterator]
GraphQLContextType = Any
GraphQLRootType = Any

GraphQLData = Optional[dict[str, JSON]]
GraphQLErrors = Optional[list[dict[str, JSON]]]
GraphQLExtensions = Optional[list[dict[str, JSON]]]
