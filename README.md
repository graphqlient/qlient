# Qlient: Python GraphQL Client Library

_This project is young so there might be bugs but I am very reactive so feel free to open issues._

This is a blazingly fast and modern graphql client that was designed with simplicity in mind.

## Installation

```shell
pip install qlient
```

## Quick Start

````python
from qlient.http import HTTPClient, GraphQLResponse

client = HTTPClient("https://swapi-graphql.netlify.app/.netlify/functions/index")

res: GraphQLResponse = client.query.film(
    # swapi graphql input fields
    id="ZmlsbXM6MQ==",

    # qlient specific
    _fields=["id", "title", "episodeID"]
)

print(res.request.query)  # query film($id: ID) { film(id: $id) { id title episodeID } }
print(res.request.variables)  # {'id': 'ZmlsbXM6MQ=='}
print(res.data)  # {'film': {'id': 'ZmlsbXM6MQ==', 'title': 'A New Hope', 'episodeID': 4}}
````
