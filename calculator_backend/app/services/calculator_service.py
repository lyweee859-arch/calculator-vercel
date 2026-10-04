from ..calculator.parser import calculate
from ..database.database import save_calculation


def calculate_and_save(expression):
    result = calculate(expression)
    save_calculation(expression, result)
    return result
