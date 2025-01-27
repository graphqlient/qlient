"""This file contains all qlient specific exceptions."""


class QlientException(Exception):
    """Base class for qlient exceptions."""


class SchemaException(QlientException):
    """Indicates that something is wrong regarding the graphql schema."""

    def __init__(self, schema: dict, *args):
        self.schema: dict = schema
        super().__init__(*args)


class SchemaParseException(SchemaException):
    """Indicates an exception in the schema parsing process.

    This exception gets thrown when the parser was unable to parse the graphql schema
    """


class NoTypesFound(SchemaParseException):
    """Indicates that the schema does not have any types defined."""


class OutOfAsyncContext(QlientException):
    """Indicates that you are running out of an async context."""
