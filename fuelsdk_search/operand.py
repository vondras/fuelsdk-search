from __future__ import annotations

import dataclasses as dc
from collections.abc import Collection, Mapping
from typing import Optional, Union, Any

from fuelsdk_search.operator import Operator

NULL = ''


def is_non_string_collection(value: Any) -> bool:
    return isinstance(value, str) and isinstance(value, Collection)


class AttributeMap(Mapping):
    def __getitem__(self, k):
        return self.__dict__.__getitem__(k)

    def __iter__(self):
        return self.__dict__.__iter__()

    def __len__(self):
        return self.__dict__.__len__()


@dc.dataclass(frozen=True, eq=False)
class Operand(AttributeMap):
    @property
    def _fields(self):
        return tuple(f.name for f in dc.fields(self))

    def _replace(self, **kwargs):
        return dc.replace(self, **kwargs)

    def __and__(self, other: Operand) -> Complex:
        if isinstance(other, Operand):
            pass
        elif isinstance(other, Mapping):
            other = Simple(**other)
        else:
            raise TypeError('Unsupported Operand')
        return Complex(Operator.AND, (self, other))

    def __or__(self, other: Operand) -> Complex:
        if isinstance(other, Operand):
            pass
        elif isinstance(other, Mapping):
            other = Simple(**other)
        else:
            raise TypeError('Unsupported Operand')
        return Complex(Operator.OR, (self, other))


@dc.dataclass(frozen=True, eq=False)
class Complex(Operand):
    operator: Operator
    operands: Collection[Operand]

    @classmethod
    def flatten(cls, operator, operands):
        for operand in operands:
            if isinstance(operand, cls) and operand.operator is operator:
                yield from Complex.flatten(operand.operator, operand.operands)
            else:
                yield operand

    @property
    def __dict__(self) -> dict:
        left, *operands = (dict(operand) for operand in Complex.flatten(self.operator, self.operands) if
                           operand is not None)

        operands = list(operands)
        n = len(operands)

        if n == 0:
            return left

        search_filter = {
            'LeftOperand': left,
            'LogicalOperator': self.operator,
        }

        if n > 1:
            search_filter['AdditionalOperands'] = operands[1:]

        search_filter['RightOperand'] = operands[0]

        return search_filter


@dc.dataclass(frozen=True, eq=False)
class Simple(Operand):
    Property: Any
    SimpleOperator: Optional[Operator] = None
    Value: Any = None

    def __invert__(self) -> Union[Simple, Complex]:
        operator = self.SimpleOperator

        if operator is None:
            raise ValueError('Cannot invert, SimpleOperator is None')

        if operator is Operator.BETWEEN:
            lower, upper = self.Value
            return (self < lower) | (self > upper)

        if operator is Operator.IN:
            return Complex(Operator.AND, list(self != value for value in self.Value))

        operator = ~operator
        return self._replace(SimpleOperator=operator)

    def __pos__(self) -> Simple:
        return self._replace(SimpleOperator=Operator.IS_NOT_NULL, Value=NULL)

    def __neg__(self) -> Simple:
        return ~+self

    def __eq__(self, other: Any) -> Simple:
        if other is None:
            return -self

        operator, value = Operator.EQ, other

        if is_non_string_collection(other):
            n = len(other)
            if n == 0:
                raise ValueError('Collection length must be greater than or equal to 1')
            if n == 1:
                return self == other.__iter__().__next__()
            operator, value = Operator.IN, list(value)

        return self._replace(SimpleOperator=operator, Value=value)

    def __ne__(self, other: Any) -> Simple:
        return ~(self == other)

    def __mod__(self, other: Any) -> Simple:
        return self._replace(SimpleOperator=Operator.LIKE, Value=other)

    def __lt__(self, other: Any, op: Operator = Operator.LT) -> Simple:
        operator, value = self.SimpleOperator, self.Value

        if operator is Operator.BETWEEN:
            lower, upper = value
            return self._replace(SimpleOperator=~op, Value=lower).__lt__(other, op)
        elif other is None:
            pass
        elif operator in {Operator.GT, Operator.GE}:
            operator, value = Operator.BETWEEN, [value, other]
        else:
            operator, value = op, other
        return self._replace(SimpleOperator=operator, Value=value)

    def __gt__(self, other: Any, op: Operator = Operator.GT) -> Simple:
        operator, value = self.SimpleOperator, self.Value

        if operator is Operator.BETWEEN:
            lower, upper = value
            return self._replace(SimpleOperator=~op, Value=upper).__gt__(other, op)
        elif other is None:
            # On the second loop through for the BETWEEN Operator, this allows us to delete a bound
            pass
        elif operator in {Operator.LT, Operator.LE}:
            operator, value = Operator.BETWEEN, [other, value]
        else:
            operator, value = op, other
        return self._replace(SimpleOperator=operator, Value=value)

    def __le__(self, other: Any) -> Simple:
        return self.__lt__(other, op=Operator.LE)

    def __ge__(self, other: Any) -> Simple:
        return self.__gt__(other, op=Operator.GE)
