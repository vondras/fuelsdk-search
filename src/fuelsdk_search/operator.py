# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import Enum


class Operator(str, Enum):
    EQ = "equals"
    NE = "notEquals"
    GT = "greaterThan"
    GE = "greaterThanOrEqual"
    LT = "lessThan"
    LE = "lessThanOrEqual"
    IN = "IN"
    LIKE = "like"
    BETWEEN = "between"
    IS_NULL = "isNull"
    IS_NOT_NULL = "isNotNull"
    AND = "AND"
    OR = "OR"
    
    def __str__(self):
        return self.value

    def __invert__(self):
        return self.__class__.invert(self)

    @classmethod
    def invert(cls, op):
        inversions = {
            cls.IS_NULL: cls.IS_NOT_NULL,
            cls.IS_NOT_NULL: cls.IS_NULL,
            cls.EQ: cls.NE,
            cls.NE: cls.EQ,
            cls.LT: cls.GE,
            cls.LE: cls.GT,
            cls.GT: cls.LE,
            cls.GE: cls.LT,
        }

        try:
            return inversions[op]
        except KeyError:
            raise KeyError(f"The '{op}' SimpleOperator cannot be inverted")
