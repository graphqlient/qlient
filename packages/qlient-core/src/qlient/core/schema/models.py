"""This file contains the graphql schema."""

import enum
import logging
from typing import Any, Optional, Union

logger = logging.getLogger("qlient")


class Kind(enum.Enum):
    """Enum for the Schema Type Kind."""

    OBJECT = "OBJECT"
    SCALAR = "SCALAR"
    NON_NULL = "NON_NULL"
    LIST = "LIST"
    INTERFACE = "INTERFACE"
    ENUM = "ENUM"
    INPUT_OBJECT = "INPUT_OBJECT"
    UNION = "UNION"


class TypeRef:
    """Represents a basic graphql Type Reference."""

    kind: Kind | None
    name: str | None
    of_type_ref: Optional["TypeRef"]
    type: Optional["Type"]  # skipcq: PYL-W0622

    @classmethod
    def parse(cls, type_ref: Union["TypeRef", dict]) -> "TypeRef":
        """Parse a single type reference.

        Args:
            type_ref: holds the type reference to parse

        Returns:
            the parsed type ref
        """
        if isinstance(type_ref, dict):
            type_ref = cls(**type_ref)
        if not isinstance(type_ref, cls):
            raise TypeError(f"Expected dict, {cls.__name__} got {type(type_ref)}")
        return type_ref

    @classmethod
    def parse_list(cls, type_refs: list[Union["TypeRef", dict]] | None) -> list["TypeRef"]:
        """Parse a list of type_refs.

        Args:
            type_refs: holds the type_ref list to parse

        Returns:
            a list of type_refs
        """
        return [cls.parse(type_ref) for type_ref in type_refs if type_ref] if type_refs else []

    def __init__(
        self,
        kind: str | Kind | None = None,
        name: str | None = None,
        ofType: Optional["TypeRef"] = None,  # noqa
    ):
        self.kind = Kind(kind) if kind else None
        self.name = name
        self.of_type_ref = self.parse(ofType) if ofType else None
        self.type: Optional["Type"] = None  # skipcq: PYL-W0622

    def __str__(self) -> str:
        """Return a simple string representation of the type ref instance."""
        return repr(self)

    def __repr__(self) -> str:
        """Return a more detailed string representation of the type ref instance."""
        class_name = self.__class__.__name__
        return f"<{class_name}(" f"kind=`{self.kind.name}`, " f"name=`{self.name}`, " f"ofType={self.of_type_ref}" ")>"

    def __gql__(self) -> str:
        representation = self.of_type_ref.graphql_representation if self.of_type_ref is not None else self.name
        if self.kind == Kind.NON_NULL:
            representation = f"{representation}!"
        if self.kind == Kind.LIST:
            representation = f"[{representation}]"
        return representation

    def infer_type_refs(self, types_dict: dict[str, "Type"]):
        """Method to recursively infer types down to the deepest type level.

        Args:
            types_dict: holds the mapping of type name to type
        """
        self.type = types_dict.get(self.name)
        if self.of_type_ref is not None:
            self.of_type_ref.infer_type_refs(types_dict)

    @property
    def graphql_representation(self) -> str:
        """Property for the graphql type representation.

        See docstring of :ref:`__gql__` for more information

        Returns:
            the graphql type representation for this.
        """
        return self.__gql__()

    @property
    def leaf_type_name(self) -> str | None:
        """Property to return the name of the very last (leaf) `of_type`

        As long as the `of_type` property is not None,
        it will call the `leaf_type_name` property of the `of_type`.

        Returns:
            The name of the very last (leaf) `of_type` Type Ref.
        """
        return self.name if self.of_type_ref is None else self.of_type_ref.leaf_type_name

    @property
    def leaf_type(self) -> Optional["Type"]:
        """Property to return the very last (leaf) `of_type` type.

        Returns:
            The type of the very last (leaf) `of_type`
        """
        return self.type if self.of_type_ref is None else self.of_type_ref.leaf_type


class Input:
    """Represents a basic graphql Input."""

    name: str | None
    description: str | None
    type: TypeRef | None  # skipcq: PYL-W0622
    default_value: Any | None

    @classmethod
    def parse(cls, input_value: Union["Input", dict]) -> "Input":
        """Parse a single input value.

        Args:
            input_value: holds the input value to parse

        Returns:
            the parsed input
        """
        if isinstance(input_value, dict):
            input_value = cls(**input_value)
        if not isinstance(input_value, cls):
            raise TypeError(f"Expected dict, {cls.__name__} got {type(input_value)}")
        return input_value

    @classmethod
    def parse_list(cls, inputs: list[Union["Input", dict]] | None) -> list["Input"]:
        """Parse a list of inputs.

        Args:
            inputs: holds the input list to parse

        Returns:
            a list of inputs
        """
        return [cls.parse(input_value) for input_value in inputs if input_value] if inputs else []

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        # skipcq: PYL-W0622
        type: TypeRef | None = None,  # noqa
        defaultValue: Any | None = None,  # noqa
    ):
        self.name = name
        self.description = description
        self.type = TypeRef.parse(type) if type else None
        self.default_value = defaultValue

    def __str__(self) -> str:
        """Return a simple string representation of the input instance."""
        return repr(self)

    def __repr__(self) -> str:
        """Return a more detailed string representation of the input instance."""
        class_name = self.__class__.__name__
        return f"<{class_name}(name=`{self.name}`, type={self.type})>"


class Directive:
    """Represents a basic graphql Directive."""

    name: str | None
    description: str | None
    locations: list[str] | None
    args: list[Input] | None

    @classmethod
    def parse(cls, directive: Union["Directive", dict]) -> "Directive":
        """Parse a single directive.

        Args:
            directive: holds the directive to parse

        Returns:
            the parsed directive
        """
        if isinstance(directive, dict):
            directive = cls(**directive)
        if not isinstance(directive, cls):
            raise TypeError(f"Expected dict, {cls.__name__} got {type(directive)}")
        return directive

    @classmethod
    def parse_list(cls, directives: list[Union["Directive", dict]] | None) -> list["Directive"]:
        """Parse a list of directives.

        Args:
            directives: holds the directive list to parse

        Returns:
            a list of directives
        """
        return [cls.parse(directive) for directive in directives if directive] if directives else []

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        locations: list[str] | None = None,
        args: list[Input] | None = None,
    ):
        self.name: str | None = name
        self.description: str | None = description
        self.locations: list[str] | None = locations
        self.args: list[Input] = Input.parse_list(args)

    @property
    def arg_name_to_arg(self) -> dict[str, Input]:
        """Property for mapping the argument name to the argument for faster lookups.

        Returns:
            A dictionary where the argument name is mapped to the argument itself
        """
        return {arg.name: arg for arg in self.args}

    def __str__(self) -> str:
        """Return a simple string representation of the directive instance."""
        return repr(self)

    def __repr__(self) -> str:
        """Return a more detailed string representation of the directive instance."""
        class_name = self.__class__.__name__
        return f"<{class_name}(name=`{self.name}`, locations={self.locations})>"


class Field:
    """Represents a basic graphql Field."""

    name: str | None
    description: str | None
    args: list[Input] | None
    type: TypeRef | None  # skipcq: PYL-W0622
    is_deprecated: bool | None
    deprecation_reason: str | None

    @classmethod
    def parse(cls, field: Union["Field", dict]) -> "Field":
        """Parse a single field.

        Args:
            field: holds the field to parse

        Returns:
            the parsed field
        """
        if isinstance(field, dict):
            field = cls(**field)
        if not isinstance(field, cls):
            raise TypeError(f"Expected dict, {cls.__name__} got {type(field)}")
        return field

    @classmethod
    def parse_list(cls, fields: list[Union["Field", dict]] | None) -> list["Field"]:
        """Parse a list of fields.

        Args:
            fields: holds the field list to parse

        Returns:
            a list of fields
        """
        return [cls.parse(field) for field in fields if field] if fields else []

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        args: list[Input] | None = None,
        # skipcq: PYL-W0622
        type: TypeRef | None = None,  # noqa
        isDeprecated: bool | None = None,  # noqa
        deprecationReason: str | None = None,  # noqa
    ):
        self.name: str | None = name
        self.description: str | None = description
        self.args: list[Input] = Input.parse_list(args)
        self.type: TypeRef | None = TypeRef.parse(type) if type else None  # skipcq: PYL-W0622
        self.is_deprecated: bool | None = isDeprecated
        self.deprecation_reason: str | None = deprecationReason

    def __str__(self) -> str:
        """Return a simple string representation of the field instance."""
        return repr(self)

    def __repr__(self) -> str:
        """Return a more detailed string representation of the field instance."""
        class_name = self.__class__.__name__
        return f"<{class_name}(name=`{self.name}`, type={self.type})>"

    @property
    def arg_name_to_arg(self) -> dict[str, Input]:
        """Property for mapping the argument name to the argument for faster lookups.

        Returns:
            A dictionary where the argument name is mapped to the argument itself
        """
        return {arg.name: arg for arg in self.args}

    @property
    def output_type(self) -> Optional["Type"]:
        if self.type is None:
            return None
        return self.type.leaf_type

    @property
    def output_type_name(self) -> str | None:
        """Property to return the output type name (which is the leaf type name)

        The output type name can only be looked up
        if the `self.type` property is not None

        Returns:
            Either None (if `self.type` is None) or the leaf type name
        """
        leaf_type = self.output_type
        if leaf_type is None:
            return None
        return leaf_type.name

    @property
    def is_object_kind(self) -> bool:
        """True if the field type is of kind OBJECT."""
        return self.output_type and self.output_type.kind == Kind.OBJECT

    @property
    def is_scalar_kind(self) -> bool:
        """True if the field type is of kind SCALAR."""
        return self.output_type and self.output_type.kind == Kind.SCALAR


class EnumValue:
    """Represents a basic graphql enum value."""

    @classmethod
    def parse(cls, enum_value: Union["EnumValue", dict]) -> "EnumValue":
        """Parse a single field.

        Args:
            enum_value: holds the field to parse

        Returns:
            the parsed field
        """
        if isinstance(enum_value, dict):
            enum_value = cls(**enum_value)
        if not isinstance(enum_value, cls):
            raise TypeError(f"Expected dict, {cls.__name__} got {type(enum_value)}")
        return enum_value

    @classmethod
    def parse_list(cls, enum_values: list[Union["EnumValue", dict]] | None) -> list["EnumValue"]:
        """Parse a list of enum values.

        Args:
            enum_values: holds the list of enum values to parse

        Returns:
            a list of enum values
        """
        return [cls.parse(enum_value) for enum_value in enum_values if enum_value] if enum_values else []

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        isDeprecated: bool | None = None,  # noqa
        deprecationReason: str | None = None,  # noqa
    ):
        self.name: str | None = name
        self.description: str | None = description
        self.is_deprecated: bool | None = isDeprecated
        self.deprecation_reason: str | None = deprecationReason

    def __str__(self) -> str:
        """Return a simple string representation of the enum value instance."""
        return repr(self)

    def __repr__(self) -> str:
        """Return a more detailed string representation of the enum value instance."""
        class_name = self.__class__.__name__
        return f"<{class_name}(name=`{self.name}`)>"


class Type:
    """Represents a basic graphql Type."""

    kind: Kind | None
    name: str | None
    description: str | None
    fields: list[Field] | None
    input_fields: list[Input] | None
    interfaces: list[TypeRef] | None
    enum_values: list[EnumValue] | None
    possible_types: list[TypeRef] | None

    @classmethod
    def parse(cls, type_value: Union["Type", dict]) -> "Type":
        """Parse a single field.

        Args:
            type_value: holds the field to parse

        Returns:
            the parsed field
        """
        if isinstance(type_value, dict):
            type_value = cls(**type_value)
        if not isinstance(type_value, cls):
            raise TypeError(f"Expected dict, {cls.__name__} got {type(type_value)}")
        return type_value

    def __init__(
        self,
        kind: str | Kind | None = None,
        name: str | None = None,
        description: str | None = None,
        fields: list[Field | dict] | None = None,
        inputFields: list[Input | dict] | None = None,  # noqa
        interfaces: list[TypeRef | dict] | None = None,
        enumValues: list[EnumValue | dict] | None = None,  # noqa
        possibleTypes: list[TypeRef | dict] | None = None,  # noqa
    ):
        self.kind: Kind | None = Kind(kind) if kind else None
        self.name: str | None = name
        self.description: str | None = description
        self.fields: list[Field] = Field.parse_list(fields)
        self.input_fields: list[Input] = Input.parse_list(inputFields)
        self.interfaces: list[TypeRef] = TypeRef.parse_list(interfaces)
        self.enum_values: list[EnumValue] = EnumValue.parse_list(enumValues)
        self.possible_types: list[TypeRef] = TypeRef.parse_list(possibleTypes)

    def infer_types(self, types_dict: dict[str, "Type"]):
        """Method to infer the types for all graphql schema types.

        This method iterates over each and all fields,
        input fields, interfaces and possible types to infer
        the `types` of the instance.

        Args:
            types_dict: Holds a dictionary with the name of the typed
                        mapped to the actual graphql schema type.
        """
        if self.fields is not None:
            for type_field in self.fields:
                type_field.type.infer_type_refs(types_dict)

        if self.input_fields is not None:
            for input_field in self.input_fields:
                input_field.type.infer_type_refs(types_dict)

        if self.interfaces is not None:
            for interface in self.interfaces:
                interface.infer_type_refs(types_dict)

        if self.possible_types is not None:
            for possible_type in self.possible_types:
                possible_type.infer_type_refs(types_dict)

    @property
    def field_name_to_field(self) -> dict[str, Field]:
        """Property for mapping the field name to the field for faster lookups.

        Returns:
            A dictionary where the field name is mapped to the field itself
        """
        return {
            field.name: field
            for field in self.fields or []  # because self.fields might be None
        }

    def __str__(self) -> str:
        """Return a simple string representation of the type instance."""
        return repr(self)

    def __repr__(self) -> str:
        """Return a more detailed string representation of the type instance."""
        class_name = self.__class__.__name__
        return f"<{class_name}(name=`{self.name}`)>"
