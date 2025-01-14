"""This file contains the graphql schema parser functions."""

from qlient.core._types import RawSchema
from qlient.core.exceptions import NoTypesFound
from qlient.core.schema.models import Directive, Type


class ParseResult:
    """Represents a parsed graphql schema."""

    def __init__(
        self,
        query_type: Type | None = None,
        mutation_type: Type | None = None,
        subscription_type: Type | None = None,
        types: dict[str, Type] | None = None,
        directives: dict[str, Directive] | None = None,
    ):
        self.query_type: Type | None = query_type
        self.mutation_type: Type | None = mutation_type
        self.subscription_type: Type | None = subscription_type
        self.types: dict[str, Type] = types
        self.directives: dict[str, Directive] | None = directives


def extract_type(type_name: str | None, types: dict[str, Type]) -> Type | None:
    """Extract a type from all types."""
    if not type_name:
        return None
    return types.get(type_name)


def extract_query_type(schema: dict, types: dict[str, Type] | None) -> Type | None:
    """Extract the name of the query type from the schema."""
    query_type: dict | None = schema.get("queryType")
    query_type_name: str | None = query_type.get("name")
    return extract_type(query_type_name, types)


def extract_mutation_type(schema: dict, types: dict[str, Type] | None) -> Type | None:
    """Extract the name of the mutation type from the schema."""
    mutation_type: dict | None = schema.get("mutationType")
    if not mutation_type:
        return None
    mutation_type_name: str | None = mutation_type.get("name")
    return extract_type(mutation_type_name, types)


def extract_subscription_type(schema: dict, types: dict[str, Type] | None) -> Type | None:
    """Extract the name of the subscription type from the schema."""
    subscription_type: dict | None = schema.get("subscriptionType")
    if not subscription_type:
        return None
    subscription_type_name: str | None = subscription_type.get("name")
    return extract_type(subscription_type_name, types)


def parse_types(schema: dict) -> dict[str, Type]:
    """Parse/Extract all types from the schema.

    The types are required.
    Everything in GraphQL is a type.
    A string for example is a scalar and a scalar is a type.

    This function returns a dictionary where each Type is associated with its name.
    This is possible due to the fact that a type name must be unique.

    Args:
        schema: holds the schema to parse

    Returns:
        holds a dictionary where each type name is mapped to it's parsed type
    """
    types_list: list[dict] = schema.get("types", [])
    if not types_list:
        raise NoTypesFound(schema)

    types_list: list[Type] = [Type.parse(type_dict) for type_dict in types_list if type_dict]

    types_dict: dict[str, Type] = {_type.name: _type for _type in types_list if _type}

    for _type in types_dict.values():
        _type.infer_types(types_dict)

    return types_dict


def parse_directives(schema: dict) -> dict[str, Directive] | None:
    """Parse the directives of the schema.

    A directive is an identifier preceded by a @ character,
    optionally followed by a list of named arguments,
    which can appear after almost any form of syntax
    in the GraphQL query or schema languages.

    Args:
        schema: holds the schema to parse

    Returns:
        either None or a dictionary of directive names matching the directive
    """
    directives_list: list[dict] = schema.get("directives", [])
    if not directives_list:
        return None

    directives_dict: dict[str, Directive] = {
        _directive.name: _directive for _directive in Directive.parse_list(directives_list) if _directive
    }

    return directives_dict


def parse_schema(schema: RawSchema) -> ParseResult:
    """Parse the given graphql schema and return the parsed result.

    Args:
        schema: holds the raw schema as a dictionary

    Returns:
        parse result with all types, directives and stuff
    """
    types = parse_types(schema)
    return ParseResult(
        query_type=extract_query_type(schema, types),
        mutation_type=extract_mutation_type(schema, types),
        subscription_type=extract_subscription_type(schema, types),
        types=types,
        directives=parse_directives(schema),
    )
