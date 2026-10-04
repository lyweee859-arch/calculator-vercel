import math
from decimal import Decimal, DivisionByZero, InvalidOperation, localcontext

from .tokenizer import tokenize


class CalculationError(ValueError):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.depth = 0

    def current(self):
        return self.tokens[self.position]

    def accept(self, kind):
        if self.current().kind == kind:
            self.position += 1
            return True
        return False

    def expression(self):
        value = self.term()
        while self.current().kind in ("+", "-"):
            operator = self.current().kind
            self.position += 1
            right = self.term()
            value = value + right if operator == "+" else value - right
        return value

    def term(self):
        value = self.unary()
        while self.current().kind in ("*", "/"):
            operator = self.current().kind
            self.position += 1
            right = self.unary()
            if operator == "/" and right == 0:
                raise CalculationError("除数不能为 0")
            value = value * right if operator == "*" else value / right
        return value

    def unary(self):
        if self.accept("+"):
            return self.unary()
        if self.accept("-"):
            return -self.unary()
        return self.primary()

    def primary(self):
        if self.current().kind == "number":
            value = self.current().value
            self.position += 1
            return value
        if self.accept("("):
            self.depth += 1
            if self.depth > 64:
                raise CalculationError("表达式格式错误")
            value = self.expression()
            self.depth -= 1
            if not self.accept(")"):
                raise CalculationError("表达式格式错误")
            return value
        raise CalculationError("表达式格式错误")


def calculate(expression):
    if not isinstance(expression, str) or not expression.strip():
        raise CalculationError("请输入表达式")
    if len(expression) > 256:
        raise CalculationError("表达式格式错误")
    try:
        parser = Parser(tokenize(expression))
        with localcontext() as context:
            context.prec = 16
            value = parser.expression()
        if parser.current().kind != "end":
            raise CalculationError("表达式格式错误")
        result = float(value)
        if not math.isfinite(result):
            raise CalculationError("表达式格式错误")
        return result
    except (InvalidOperation, DivisionByZero, OverflowError, RecursionError, ValueError) as error:
        if isinstance(error, CalculationError):
            raise
        raise CalculationError("表达式格式错误") from error
