"""This module contains the qlient models."""

from typing import Any, Optional

from qlient.core._types import (
    GraphQLAnyReturnType,
    GraphQLContextType,
    GraphQLData,
    GraphQLErrors,
    GraphQLExtensions,
    GraphQLOperationNameType,
    GraphQLQueryType,
    GraphQLRootType,
    GraphQLVariablesType,
)
from qlient.core.schema.models import Directive as SchemaDirective
from qlient.core.schema.models import Field as SchemaField
from qlient.core.schema.models import Type as SchemaType
from qlient.core.schema.schema import Schema


class Directive:
    """Class to create a directive on a Field."""

    def __init__(self, _name: str):
        self.name: str = _name

    def prepare(self, schema: Schema) -> "PreparedDirective":
        """Prepare this directive and return a ref:`PreparedDirective`

        Args:
            schema: holds the schema that is currently being used.

        Returns:
            a PreparedDirective
        """
        p = PreparedDirective()
        p.prepare(
            schema=schema,
            name=self.name,
        )
        return p

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can not compare other classes than {self.__class__.__name__}")
        return hash(self) == hash(other)


class PreparedDirective:
    """Class that represents a prepared directive.

    There should be no more changes made on this directive.
    """

    def __init__(self):
        # the graphql schema directive type
        self.schema_directive: SchemaDirective | None = None
        # the name of the directive
        self.name: str | None = None

    def prepare(
        self,
        schema: Schema,
        name: str | None = None,
    ):
        """Method to prepare this directive after it has been initialized.

        Args:
            schema: holds the client's schema that is currently being used.
            name: holds the name of this directive
        """
        self.prepare_name(name)
        self.prepare_type_checking(schema)

    def prepare_type_checking(self, schema: Schema):
        """Method to prepare for type checking.

        This is important to make sure that the directive is known.

        Make sure that you have called `prepare_name` before calling this method.

        Args:
            schema: holds the client's schema that is currently being used
        """
        if not self.name:
            raise ValueError(f"Name required before calling `{self.prepare_type_checking.__name__}`")
        schema_directive = schema.directives_registry.get(self.name)
        if schema_directive is None:
            raise ValueError(f"No directive found named `{self.name}` in schema.")
        self.schema_directive = schema_directive

    def prepare_name(self, name: str | None):
        """Method to prepare the name of this directive.

        Args:
            name: holds the name of this directive
        """
        if not name:
            raise ValueError("Directive name must have a value.")
        self.name = name

    def __str__(self) -> str:
        return self.__gql__()

    def __gql__(self) -> str:
        """Method to create a graphql representation of this directive.

        Returns:
            a string with the graphql representation of this directive
        """
        builder = f"@{self.name}"
        return builder

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can not compare other classes than {self.__class__.__name__}")
        return hash(self) == hash(other)


class Field:
    """Class to create a field in the selection.

    Use this class for more customization. If you only make a simple selection, I highly recommend only using the Fields
    class.
    """

    def __init__(
        self,
        _name: str,
        _alias: str | None = None,
        _directive: Directive | None = None,
        _sub_fields: Any | None = None,
    ):
        self.name: str = _name
        self.alias: str | None = _alias
        self.directive: Directive | None = _directive
        self.sub_fields: Optional["Fields"] = Fields(_sub_fields) if _sub_fields is not None else None

    def __and__(self, other) -> "Fields":
        return self.__add__(other)

    def __add__(self, other) -> "Fields":
        if isinstance(other, (str, self.__class__)):
            other = Fields(other)
        if isinstance(other, (list, tuple, set)):
            other = Fields(*other)
        if isinstance(other, dict):
            other = Fields(**other)
        if isinstance(other, Fields):
            return Fields(self) + other
        raise TypeError(f"Can not handle type `{type(other)}`")

    def prepare(
        self,
        parent_type: SchemaType,
        schema: Schema,
    ) -> "PreparedField":
        """Method to convert this field into a PreparedField.

        Args:
            parent_type: holds the parent type of this Field
            schema: holds the schema that should be used for validation

        Returns:
            a PreparedField
        """
        p = PreparedField()
        p.prepare(
            parent_type=parent_type,
            schema=schema,
            name=self.name,
            alias=self.alias,
            directive=self.directive,
            sub_fields=self.sub_fields,
        )
        return p

    def __hash__(self) -> int:
        return hash((self.alias, self.name, self.directive, self.sub_fields))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can not compare other classes than {self.__class__.__name__}")
        return hash(self) == hash(other)


class PreparedField:
    """Class that represents a PreparedField.

    This means that there should be no more changes made to this field.
    """

    def __init__(self):
        # the field parent type
        self.parent_type: SchemaType | None = None
        # the graphql schema field type
        self.field_type: SchemaField | None = None
        # the name of the field
        self.name: str | None = None
        # the alias of the field
        self.alias: str | None = None
        # the directive of the field
        self.directive: PreparedDirective | None = None
        # a sub selection of fields of this type
        self.sub_fields: PreparedFields | None = None

    def prepare(
        self,
        parent_type: SchemaType,
        schema: Schema,
        name: str | None = None,
        alias: str | None = None,
        directive: Directive | None = None,
        sub_fields: Any | None = None,
    ):
        """Method to prepare this instance.

        Args:
            parent_type: holds the parent schema type of this field
            schema: holds the schema that should be used for validation
            name: holds the name of this explicit field
            alias: holds an alias that should be used for this field
            directive: holds a directive that should be used on this field
            sub_fields: holds a selection of sub_fields for this field
        """
        self.prepare_name(name, alias)
        self.prepare_type_checking(parent_type)
        self.prepare_directive(schema, directive)
        self.prepare_sub_fields(schema, sub_fields)

    def prepare_name(self, name: str | None, alias: str | None):
        """Method to prepare the name including alias of this field.

        Args:
            name: holds the name of this field
            alias: holds an alias of this field
        """
        if not name:
            raise ValueError("Directive name must have a value.")
        self.name = name
        self.alias = alias

    def prepare_type_checking(self, parent_type: SchemaType):
        """Method to prepare this field for type checking.

        Args:
            parent_type: holds the schema type of the parent field
        """
        if not self.name:
            raise ValueError(f"Name must be set before " f"calling `{self.prepare_type_checking.__name__}`")
        self.parent_type = parent_type
        schema_field_type = parent_type.field_name_to_field.get(self.name)
        if schema_field_type is None:
            raise ValueError(f"No Field found with name `{self.name}` in schema.")
        self.field_type = schema_field_type

    def prepare_directive(self, schema: Schema, directive: Directive | None):
        """Method to prepare the directive of this field.

        Args:
            schema: holds the schema to used (needed to prepare the directive)
            directive: holds the actual directive to be prepared
        """
        if directive is None:
            return
        self.directive = directive.prepare(schema)

    def prepare_sub_fields(
        self,
        schema: Schema,
        sub_fields: Optional["Fields"],
    ):
        """Method to prepare the subfields selection.

        Args:
            schema: holds the schema that is being used by the client
            sub_fields: holds the selected subfields
        """
        if sub_fields is None:
            return
        new_parent_type = self.field_type.type.leaf_type
        self.sub_fields = sub_fields.prepare(new_parent_type, schema)

    def __gql__(self) -> str:
        """Method to create a graphql representation of this field.

        Returns:
            a string with the graphql representation of this field
        """
        builder = f"{f'{self.alias}: ' if self.alias else ''}{self.name}"
        if self.directive is not None:
            builder += f" {self.directive.__gql__()}"
        if self.sub_fields is not None:
            builder += f" {{ {self.sub_fields.__gql__()} }}"
        return builder

    def __hash__(self) -> int:
        return hash((self.alias, self.name, self.directive, self.sub_fields))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can not compare other classes than {self.__class__.__name__}")
        return hash(self) == hash(other)


class Fields:
    """Class to create a selection of multiple fields.

    Use this class to create a selection of multiple fields or combine multiple instances.
    """

    @classmethod
    def parse_args(
        cls,
        args: tuple[Any],
        fields: dict[int, Field] = None,
    ) -> dict[int, Field]:
        """Class method to parse given *args.

        Args:
            args: holds the given *args
            fields: optional, holds a dictionary of fields parsed so far,
                    empty dict if None

        Returns:
            a dictionary mapped with the hash of the field to the Field itself.
        """
        fields = fields or {}
        for arg in args:
            if isinstance(arg, str):
                arg = arg.strip()
                if not arg:
                    continue
                arg = Field(arg)
            if isinstance(arg, Field):
                fields[hash(arg)] = arg
                continue
            if isinstance(arg, (list, tuple, set)):
                arg = cls(*arg)
            if isinstance(arg, dict):
                arg = cls(**arg)
            if isinstance(arg, cls):
                for field in arg.selected_fields:
                    fields[hash(field)] = field
                continue
            raise TypeError(f"Can't handle type `{type(arg).__name__}`")

        return fields

    @classmethod
    def parse_kwargs(
        cls,
        kwargs: dict[Any, Any],
        fields: dict[int, Field] = None,
    ) -> dict[int, Field]:
        """Class method to parse given **kwargs.

        Args:
            kwargs: holds the given **kwargs
            fields: optional, holds a dictionary of fields parsed so far,
                    empty dict if None

        Returns:
            a dictionary mapped with the hash of the field to the Field itself.
        """
        fields = fields or {}
        for key, value in kwargs.items():
            field = Field(key, _sub_fields=cls(value))
            fields[hash(field)] = field
        return fields

    def __init__(self, *args, **kwargs):
        _fields: dict[int, Field] = {}

        _fields = self.parse_args(args, _fields)
        _fields = self.parse_kwargs(kwargs, _fields)

        self.selected_fields: list[Field] = list(_fields.values())

    def __contains__(self, item) -> bool:
        if isinstance(item, str):
            item = Field(item)
        return item in self.selected_fields

    def __and__(self, other) -> "Fields":
        """Synthetic sugar method which essentially just does the __add__

        Args:
            other: holds the other instance to add to this instance

        Returns:
            a new Fields instance with the added properties
        """
        return self.__add__(other)

    def __add__(self, other) -> "Fields":
        """Add another object to this fields.

        Args:
            other: the object to add

        Returns:
            a new instance of this class with the added fields
        """
        cls = self.__class__
        if other is None:
            return cls(*self.selected_fields)
        if isinstance(other, (str, Field)):
            other = cls(other)
        if isinstance(other, (list, tuple, set)):
            other = cls(*other)
        if isinstance(other, dict):
            other = cls(**other)
        if isinstance(other, cls):
            args = [*self.selected_fields, *other.selected_fields]
            return cls(*args)
        raise TypeError(f"Can not add {other} to {self}")

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can not compare other classes than {self.__class__.__name__}")
        return hash(self) == hash(other)

    def __bool__(self) -> bool:
        return bool(self.selected_fields)

    def __hash__(self) -> int:
        return hash(tuple(self.selected_fields))

    def prepare(
        self,
        parent_type: SchemaType,
        schema: Schema,
    ) -> "PreparedFields":
        """Method to convert this fields instance into a PreparedFields instance.

        Args:
            parent_type: holds the parent type of this Field
            schema: holds the schema that should be used for validation

        Returns:
            a PreparedFields instance
        """
        p = PreparedFields()
        p.prepare(
            parent_type=parent_type,
            schema=schema,
            fields=self.selected_fields,
        )
        return p


class PreparedFields:
    """Class that represents a prepared version of the Fields class.

    A prepared class should not be changed after preparation.
    """

    def __init__(self):
        # the prepared fields
        self.fields: list[PreparedField] | None = None

    def prepare(
        self,
        parent_type: SchemaType,
        schema: Schema,
        fields: list[Field] | None = None,
    ):
        """Method to prepare this instance after initialization.

        Args:
            parent_type: holds the parent's field schema type
            schema: holds the schema to use for validation and type lookups.
            fields: holds the list of fields that were selected
        """
        self.prepare_fields(parent_type, schema, fields)

    def prepare_fields(
        self,
        parent_type: SchemaType,
        schema: Schema,
        fields: list[Fields] | None,
    ):
        """Method to turn all selected fields into prepared fields.

        Args:
            parent_type: holds this fields instance parents field schema type.
            schema: holds the schema to use for validation and type lookups.
            fields: holds a list of fields that should be prepared
        """
        fields: list[Field] = fields if fields is not None else []
        self.fields = [
            field.prepare(
                parent_type,
                schema,
            )
            for field in fields
        ]

    def __gql__(self) -> str:
        """Method to create a graphql representation of this fields instance.

        Returns:
            a string with the graphql representation of this fields instance
        """
        return " ".join(field.__gql__() for field in self.fields)

    def __hash__(self) -> int:
        return hash(tuple(self.fields))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(f"Can not compare other classes than {self.__class__.__name__}")
        return hash(self) == hash(other)


class GraphQLRequest:
    """Represents the graphql request."""

    def __init__(
        self,
        query: GraphQLQueryType = None,
        variables: GraphQLVariablesType = None,
        operation_name: GraphQLOperationNameType = None,
        context: GraphQLContextType = None,
        root: GraphQLRootType = None,
    ):
        if variables is None:
            variables = {}
        self.query: GraphQLQueryType = query
        self.variables: GraphQLVariablesType = variables
        self.operation_name: GraphQLOperationNameType = operation_name
        self.context: GraphQLContextType = context
        self.root: GraphQLRootType = root


class GraphQLSubscriptionRequest(GraphQLRequest):
    """Represents a graphql subscription request."""

    subscription_id: str
    options: dict[str, Any]

    def __init__(self, subscription_id: str = None, options: dict[str, Any] = None, **kwargs):
        super().__init__(**kwargs)
        if options is None:
            options = {}
        self.subscription_id = subscription_id
        self.options = options


class GraphQLResponse:
    """Represents the graphql response type."""

    def __init__(
        self,
        request: GraphQLRequest,
        response: GraphQLAnyReturnType,
    ):
        self.request: GraphQLRequest = request
        self.raw: GraphQLAnyReturnType = response

        self.data = None
        self.errors = None
        self.extensions = None

        if isinstance(self.raw, dict):
            # response parsing
            self.data: GraphQLData = self.raw.get("data")
            self.errors: GraphQLErrors = self.raw.get("errors")
            self.extensions: GraphQLExtensions = self.raw.get("extensions")

    def __iter__(self):
        # for a synchronous subscription
        return iter(self.raw)

    def __aiter__(self):
        # for an asynchronous subscription
        return self.raw.__aiter__()


auto = object()
