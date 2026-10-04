import math

import pytest

from calculator_backend.app.calculator.parser import CalculationError, calculate


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1+2", 3), ("10-3", 7), ("4*5", 20), ("20/4", 5),
        ("1+2*3", 7), ("(1+2)*3", 9), ("-5+8", 3),
        ("3*-2", -6), ("-(2+3)", -5), ("3.14*2", 6.28),
        ("10/(2+3)", 2), ("  +2 * (-3 + 5) ", 4),
        ("0.1+0.2", 0.3), ("2*(-3+5)", 4),
    ],
)
def test_valid_expressions(expression, expected):
    assert calculate(expression) == expected


@pytest.mark.parametrize(
    "expression",
    ["1++*", "((1+2)", "abc", "", "  ", "1+", "2**3", "1..2", ")1(", "2(3)", "1e9"],
)
def test_invalid_expressions(expression):
    with pytest.raises(CalculationError, match="表达式格式错误|请输入表达式"):
        calculate(expression)


def test_division_by_zero():
    with pytest.raises(CalculationError, match="除数不能为 0"):
        calculate("1/0")


def test_expression_length_limit():
    with pytest.raises(CalculationError):
        calculate("1" * 257)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("sin(π/2)", 1), ("cos(0)", 1), ("tan(π/4)", 1),
        ("arcsin(1)", math.pi / 2), ("arccos(1)", 0),
        ("arctan(1)", math.pi / 4), ("sqrt(81)", 9),
        ("2^3^2", 512), ("-2^2", -4), ("2^-2", 0.25),
        ("5!", 120), ("(3+2)!", 120), ("abs(-4.5)", 4.5),
        ("π", math.pi), ("e", math.e), ("ln(e)", 1),
        ("log(100)", 2), ("exp(1)", math.e),
    ],
)
def test_scientific_expressions(expression, expected):
    assert calculate(expression) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression",
    ["sqrt(-1)", "ln(0)", "log(-10)", "arcsin(2)", "arccos(-2)",
     "(-2)^0.5", "2.5!", "(-1)!", "171!", "exp(1000)"],
)
def test_scientific_domain_errors(expression):
    with pytest.raises(CalculationError, match="定义域|阶乘|范围"):
        calculate(expression)
