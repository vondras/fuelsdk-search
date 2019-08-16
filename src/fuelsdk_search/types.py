from typing import AnyStr, Iterable, Union, TypeVar
from numbers import Number
from datetime import datetime


Value = TypeVar('Value', Number, AnyStr, datetime, None)
Values = Iterable[Value]
Property = AnyStr

def issubtype(instance, types):
    if not isinstance(types, Iterable):
        types = [types]
    for t in types:
        if isinstance(t, type):
            match = isinstance(instance, t)
        elif isinstance(t, TypeVar):
            match = issubtype(instance, t.__constraints__)
        elif hasattr(t, '__args__'):
            match = issubtype(instance, t.__args__)
        else:
            match = isinstance(instance, t)
        if match:
            return True
    return False

