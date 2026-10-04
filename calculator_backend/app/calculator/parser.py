import math
from decimal import Decimal, DivisionByZero, InvalidOperation, Overflow, localcontext

from .tokenizer import tokenize


class CalculationError(ValueError):
    pass


CONSTANTS = {"pi": Decimal(str(math.pi)), "e": Decimal(str(math.e))}
FUNCTIONS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "arcsin": math.asin, "arccos": math.acos, "arctan": math.atan,
    "sqrt": math.sqrt, "ln": math.log, "log": math.log10,
    "exp": math.exp,
}


def apply_function(name, value):
    if name == "abs":
        return abs(value)
    if name not in FUNCTIONS:
        raise CalculationError("表达式格式错误")
    if name in ("ln", "log") and value <= 0:
        raise CalculationError("函数输入超出定义域")
    if name == "sqrt" and value < 0:
        raise CalculationError("函数输入超出定义域")
    if name in ("arcsin", "arccos") and not -1 <= value <= 1:
        raise CalculationError("函数输入超出定义域")
    argument = float(value)
    if not math.isfinite(argument):
        raise CalculationError("结果超出范围")
    if name == "tan" and abs(math.cos(argument)) < 1e-15:
        raise CalculationError("函数输入超出定义域")
    try:
        result = FUNCTIONS[name](argument)
    except ValueError as error:
        raise CalculationError("函数输入超出定义域") from error
    except OverflowError as error:
        raise CalculationError("结果超出范围") from error
    if not math.isfinite(result):
        raise CalculationError("结果超出范围")
    if name in ("sin", "cos", "tan") and abs(result) < 1e-15:
        result = 0.0
    return Decimal(str(result))


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
        return self.power()

    def power(self):
        value = self.postfix()
        if self.accept("^"):
            exponent = self.unary()
            if (value < 0 and exponent != exponent.to_integral_value()) or (value == 0 and exponent < 0):
                raise CalculationError("乘方输入超出定义域")
            try:
                value = value ** exponent
            except (InvalidOperation, DivisionByZero, Overflow) as error:
                raise CalculationError("结果超出范围") from error
        return value

    def postfix(self):
        value = self.primary()
        while self.accept("!"):
            if value < 0 or value > 170 or value != value.to_integral_value():
                raise CalculationError("阶乘仅支持 0 到 170 的整数")
            value = Decimal(math.factorial(int(value)))
        return value

    def grouped(self):
        self.depth += 1
        if self.depth > 64:
            raise CalculationError("表达式格式错误")
        try:
            value = self.expression()
            if not self.accept(")"):
                raise CalculationError("表达式格式错误")
            return value
        finally:
            self.depth -= 1

    def primary(self):
        if self.current().kind == "number":
            value = self.current().value
            self.position += 1
            return value
        if self.current().kind == "identifier":
            name = self.current().value
            self.position += 1
            if name in CONSTANTS:
                return CONSTANTS[name]
            if not self.accept("("):
                raise CalculationError("表达式格式错误")
            return apply_function(name, self.grouped())
        if self.accept("("):
            return self.grouped()
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
    except (InvalidOperation, DivisionByZero, Overflow, OverflowError, RecursionError, ValueError) as error:
        if isinstance(error, CalculationError):
            raise
        raise CalculationError("表达式格式错误") from error
