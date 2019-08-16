from __future__ import annotations
from typing import Optional, Iterator, Union, Iterable
import fuelsdk_search.types as T
from fuelsdk_search.operators import Operator as Operator
import json
NULL = ''

class Operand:
    def __and__(self, other: Operand) -> Complex:
        if isinstance(other, dict):
            other = Simple(**other)
        return Complex(Operator.AND, self, other)

    def __or__(self, other: Operand) -> Complex:
        if isinstance(other, dict):
            other = Simple(**other)
        return Complex(Operator.OR, self, other)

    def copy(self) -> Simple:
        return self.__class__(**dict(self))

    def __repr__(self):
        return json.dumps(dict(self), indent='\t')


class Complex(Operand):
    def __init__(self, operator, *operands: Iterator[Operand]):
        self.operator = operator
        self.operands = tuple(self.flatten(operator, *operands))

    @classmethod
    def flatten(cls, operator, *operands):
        for operand in operands:
            if isinstance(operand, cls) and operand.operator is operator:
                yield from operand.operands
            else:
                yield operand

    def asdict(self):
        left, *operands = (dict(operand) for operand in self.operands if operand is not None)

        search_filter = {
            'LogicalOperator': '' + self.operator,
            'LeftOperand': left
        }

        if not operands:
            return left

        right, *operands = operands

        search_filter['RightOperand'] = right

        if operands:
            search_filter['AdditionalOperands'] = list(operands)

        return search_filter

    def __iter__(self):
        yield from json.loads(json.dumps(self.asdict())).items()

class Simple(Operand):
    def __init__(self, Property: T.Property, SimpleOperator: Optional[T.Operator]=None, Value: Union[T.Value, T.Values]=None) -> Simple:
        self.Property = Property
        self.SimpleOperator = SimpleOperator
        self.Value = Value

    def __invert__(self) -> Simple:
        if self.SimpleOperator is Operator.BETWEEN:
            lower, upper = self.Value
            return (self.copy() < lower) | (self.copy() > upper)

        if self.SimpleOperator is Operator.IN:
            return Complex('AND', *(self.copy() != value for value in self.Value))

        self.SimpleOperator = ~self.SimpleOperator
        return self

    def __pos__(self) -> Simple:
        self.SimpleOperator = Operator.IS_NOT_NULL
        self.Value = NULL
        return self

    def __neg__(self) -> Simple:
        return ~+self

    def __eq__(self, other: Union[T.Value, T.Values]) -> Simple:
        if other is None:
            return -self

        if not T.issubtype(other, T.Value):
            length = len(other)
            if length == 0:
                raise ValueError('Iterable length must be greater than or equal to 1')
            if length == 1:
                return self == other[0]

            self.SimpleOperator = Operator.IN
            self.Value = other
            return self

        self.SimpleOperator = Operator.EQ
        self.Value = other

        return self

    def __ne__(self, other: Union[T.Value, T.Values]) -> Simple:
        return ~(self == other)

    def __mod__(self, other: T.Value) -> Simple:
        self.SimpleOperator = Operator.LIKE
        self.Value = other
        return self

    def __lt__(self, other: T.Value, op=Operator.LT) -> Simple:
        if self.SimpleOperator is Operator.BETWEEN:
            lower, upper = self.Value
            self.SimpleOperator = ~op
            self.Value = lower
            return self.__lt__(other, op)
        elif other is None:
            pass
        elif self.SimpleOperator in {Operator.GT, Operator.GE}:
            self.SimpleOperator = Operator.BETWEEN
            self.Value = (self.Value, other)
        else:
            self.SimpleOperator = op
            self.Value = other
        return self

    def __gt__(self, other: T.Value, op=Operator.GT):
        if self.SimpleOperator is Operator.BETWEEN:
            lower, upper = self.Value
            self.SimpleOperator = ~op
            self.Value = upper
            return self.__gt__(other, op)
        elif other is None:
            pass
        elif self.SimpleOperator in {Operator.LT, Operator.LE}:
            self.SimpleOperator = Operator.BETWEEN
            self.Value = (other, self.Value)
        else:
            self.SimpleOperator = op
            self.Value = other
        return self

    def __le__(self, other: T.Value):
        return self.__lt__(other, op=Operator.LE)

    def __ge__(self, other: T.Value):
        return self.__gt__(other, op=Operator.GE)

    def asdict(self):
        return {
            'Property': self.Property,
            'SimpleOperator': self.SimpleOperator,
            'Value': self.Value #list(self.Value) if isinstance(self.Value, Iterable) and not isinstance(self.Value, str) else self.Value
        }

    def __iter__(self) -> Iterator[Simple]:
        yield from self.asdict().items()