""" Support for Marshmallow.

::

    from mixer.backend.marshmallow import mixer


"""
from __future__ import absolute_import

import datetime as dt
import decimal

from marshmallow import fields, missing, validate

from .. import mix_types as t
from ..main import LOGGER, SKIP_VALUE
from ..main import GenFactory as BaseFactory
from ..main import Mixer as BaseMixer
from ..main import TypeMixer as BaseTypeMixer
from ..main import faker, partial
from mixer.mix_types import Field
from typing import Union
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Callable
from typing import Optional
from marshmallow.schema import Schema


def get_nested(_scheme: Schema, _typemixer: Union["NestedTypeMixer", "TypeMixer", None] = None, _many: bool = False, **kwargs: Any) -> Any:
    """Create nested objects."""
    obj = NestedMixer().blend(_scheme, **kwargs)
    if _many:
        return [obj]
    return obj


class GenFactory(BaseFactory):

    """Support for Marshmallow fields."""

    types = {
        (fields.Str, fields.String): str,
        fields.UUID: t.UUID,
        (fields.Number, fields.Integer, fields.Int): t.BigInteger,
        fields.Decimal: decimal.Decimal,
        (fields.Bool, fields.Boolean): bool,
        fields.Float: float,
        fields.DateTime: dt.datetime,
        fields.Time: dt.time,
        fields.Date: dt.date,
        (fields.URL, fields.Url): t.URL,
        fields.Email: t.EmailString,
        # fields.FormattedString
        # fields.TimeDelta
        # fields.Dict
        # fields.Method
        # fields.Function
        # fields.Constant
    }

    generators = {
        fields.DateTime: lambda: faker.date_time().isoformat(),
        fields.Nested: get_nested,
    }


class TypeMixer(BaseTypeMixer):

    """ TypeMixer for Marshmallow. """

    factory = GenFactory

    def __load_fields(self):
        for name, field in self.__scheme._declared_fields.items():
            yield name, t.Field(field, name)

    def is_required(self, field: Field) -> bool:
        """Return True is field's value should be defined.

        :return bool:

        """
        return field.scheme.required or (
            self.__mixer.params["required"] and not field.scheme.dump_only
        )

    @staticmethod
    def get_default(field: Field) -> Any:
        """Get default value from field.

        :return value:

        """
        return (
            field.scheme.default is missing and SKIP_VALUE or field.scheme.default
        )  # noqa

    def populate_target(self, values: Any) -> Any:
        """ Populate target. """
        data = self.__scheme().load(dict(values))
        return data

    def make_fabric(self, field: Any, field_name: str = None, fake: bool = False, kwargs: Optional[Any] = None) -> Callable:  # noqa
        kwargs = {} if kwargs is None else kwargs

        if isinstance(field, fields.Nested):
            kwargs.update(
                {"_typemixer": self, "_scheme": type(field.schema), "_many": field.many}
            )

        if isinstance(field, fields.List):
            fab = self.make_fabric(
                field.inner, field_name=field_name, fake=fake, kwargs=kwargs
            )
            return lambda: [fab() for _ in range(faker.small_positive_integer(4))]

        for validator in field.validators:
            if isinstance(validator, validate.OneOf):
                return partial(faker.random_element, validator.choices)

        return super(TypeMixer, self).make_fabric(
            type(field), field_name=field_name, fake=fake, kwargs=kwargs
        )


class NestedTypeMixer(TypeMixer):
    def populate_target(self, values: Any) -> Dict[str, Any]:
        """ Populate target. """
        return dict(values)


class Mixer(BaseMixer):

    """ Integration with Marshmallow. """

    type_mixer_cls = TypeMixer

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Mixer, self).__init__(*args, **kwargs)

        # All fields is required by default
        self.params.setdefault("required", True)


class NestedMixer(Mixer):

    type_mixer_cls = NestedTypeMixer


mixer = Mixer()
