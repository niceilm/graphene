from collections import OrderedDict

import six

from .base import BaseOptions, BaseType
from .unmountedtype import UnmountedType
from graphene.pyutils.init_subclass import InitSubclassMeta

try:
    from enum import Enum as PyEnum
except ImportError:
    from ..pyutils.enum import Enum as PyEnum


def eq_enum(self, other):
    if isinstance(other, self.__class__):
        return self is other
    return self.value is other


EnumType = type(PyEnum)


class EnumOptions(BaseOptions):
    enum = None  # type: Enum


class EnumMeta(InitSubclassMeta):
    def get(cls, value):
        return cls._meta.enum(value)

    def __getitem__(cls, value):
        return cls._meta.enum[value]

    def __prepare__(name, bases, **kwargs):  # noqa: N805
        return OrderedDict()

    def __call__(cls, *args, **kwargs):  # noqa: N805
        if cls is Enum:
            description = kwargs.pop('description', None)
            return cls.from_enum(PyEnum(*args, **kwargs), description=description)
        return super(EnumMeta, cls).__call__(*args, **kwargs)
        # return cls._meta.enum(*args, **kwargs)

    def from_enum(cls, enum, description=None):  # noqa: N805
        meta_class = type('Meta', (object,), {'enum': enum, 'description': description})
        return type(meta_class.enum.__name__, (Enum,), {'Meta': meta_class})


class Enum(six.with_metaclass(EnumMeta, UnmountedType, BaseType)):
    @classmethod
    def __init_subclass_with_meta__(cls, enum=None, **options):
        _meta = EnumOptions(cls)
        _meta.enum = enum or PyEnum(cls.__name__, dict(cls.__dict__, __eq__=eq_enum))
        for key, value in _meta.enum.__members__.items():
            setattr(cls, key, value)
        super(Enum, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def get_type(cls):
        '''
        This function is called when the unmounted type (Enum instance)
        is mounted (as a Field, InputField or Argument)
        '''
        return cls
