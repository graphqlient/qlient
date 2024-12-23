from qlient.core.models import GraphQLRequest, GraphQLResponse


class Plugin:
    """Base plugin."""

    # skipcq: PYL-R0201
    def pre(self, request: GraphQLRequest) -> GraphQLRequest:
        """Override to make changes to the request before giving it to the backend.

        Args:
            request: holds the request

        Returns:
            the request
        """
        return request

    # skipcq: PYL-R0201
    def post(self, response: GraphQLResponse) -> GraphQLResponse:
        """Override to update the response when the result is in.

        Args:
            response: holds the response

        Returns:
            the response
        """
        return response


def apply_pre(plugins: list[Plugin], request: GraphQLRequest) -> GraphQLRequest:
    """Helper function to apply all pre plugins.

    Args:
        plugins: the list of plugins to apply
        request: the graphql request instance

    Returns:
        the graphql request instance
    """
    for plugin in plugins:
        request = plugin.pre(request)
    return request


def apply_post(plugins: list[Plugin], response: GraphQLResponse) -> GraphQLResponse:
    """Helper function to apply all post plugins.

    Args:
        plugins: the list of plugins to apply
        response: the graphql response instance

    Returns:
        the graphql response instance
    """
    for plugin in plugins:
        response = plugin.post(response)
    return response
