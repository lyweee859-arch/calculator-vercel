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
