from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class Token:
    kind: str
    value: object


def tokenize(expression):
    tokens = []
    index = 0
    while index < len(expression):
        char = expression[index]
        if char.isspace():
            index += 1
            continue
        if char in "+-*/()":
            tokens.append(Token(char, char))
            index += 1
            continue
        if char in "0123456789.":
            start = index
            while index < len(expression) and expression[index] in "0123456789":
                index += 1
            if index < len(expression) and expression[index] == ".":
                index += 1
                while index < len(expression) and expression[index] in "0123456789":
                    index += 1
            literal = expression[start:index]
            try:
                if literal == ".":
                    raise InvalidOperation
                tokens.append(Token("number", Decimal(literal)))
            except InvalidOperation as error:
                raise ValueError("表达式格式错误") from error
            continue
        raise ValueError("表达式格式错误")
    tokens.append(Token("end", None))
    return tokens
