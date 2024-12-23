# skipcq: PY-D0003
import pytest

from qlient.core.exceptions import NoTypesFound


# skipcq: PY-D0003
def test_parse_schema_types(raw_swapi_schema):
    from qlient.core.schema.parser import parse_types

    types = parse_types(raw_swapi_schema)
    assert isinstance(types, dict)


# skipcq: PY-D0003
def test_parse_schema_types_no_types():
    from qlient.core.schema.parser import parse_types

    with pytest.raises(NoTypesFound):
        parse_types({})


# skipcq: PY-D0003
def test_query_type_extraction(raw_swapi_schema):
    from qlient.core.schema.models import Type
    from qlient.core.schema.parser import extract_query_type, parse_types

    types = parse_types(raw_swapi_schema)
    query_type = extract_query_type(raw_swapi_schema, types)
    assert isinstance(query_type, Type)


# skipcq: PY-D0003
def test_mutation_type_extraction(raw_swapi_schema):
    from qlient.core.schema.parser import extract_mutation_type, parse_types

    types = parse_types(raw_swapi_schema)
    mutation_type = extract_mutation_type(raw_swapi_schema, types)
    assert mutation_type is None


# skipcq: PY-D0003
def test_subscription_type_extraction(raw_swapi_schema):
    from qlient.core.schema.parser import extract_subscription_type, parse_types

    types = parse_types(raw_swapi_schema)
    subscription_type = extract_subscription_type(raw_swapi_schema, types)
    assert subscription_type is None


# skipcq: PY-D0003
def test_parse_schema_directives(raw_swapi_schema):
    from qlient.core.schema.parser import parse_directives

    directives = parse_directives(raw_swapi_schema)
    assert isinstance(directives, dict)


# skipcq: PY-D0003
def test_empty_parse_result():
    from qlient.core.schema.parser import ParseResult

    empty_result = ParseResult()
    assert empty_result.query_type is None
    assert empty_result.mutation_type is None
    assert empty_result.subscription_type is None
    assert empty_result.types is None
    assert empty_result.directives is None


# skipcq: PY-D0003
def test_filled_parse_result():
    from qlient.core.schema.models import Type
    from qlient.core.schema.parser import ParseResult

    empty_result = ParseResult(
        query_type=Type(name="Query"),
        mutation_type=Type(name="Mutation"),
        subscription_type=Type(name="Subscription"),
        types={},
        directives={},
    )
    assert empty_result.query_type.name == "Query"
    assert empty_result.mutation_type.name == "Mutation"
    assert empty_result.subscription_type.name == "Subscription"
    assert empty_result.types == {}
    assert empty_result.directives == {}


# skipcq: PY-D0003
def test_parse_schema(raw_swapi_schema):
    from qlient.core.schema.parser import ParseResult, parse_schema

    parse_result: ParseResult = parse_schema(raw_swapi_schema)
    assert isinstance(parse_result, ParseResult)
    assert parse_result.query_type is not None
    assert parse_result.mutation_type is None
    assert parse_result.subscription_type is None
