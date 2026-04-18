import pytest
from ZhegalkinPolynomial import ZhegalkinPolynomial

class MockZhegalkin(ZhegalkinPolynomial):
    def __init__(self, variables):
        self.variables = variables

@pytest.fixture
def table_xor():
    """Таблица для f = a ^ b (Линейная, самодвойственная, не сохраняет 1)"""
    return [
        {'a': 0, 'b': 0, 'result': 0},
        {'a': 0, 'b': 1, 'result': 1},
        {'a': 1, 'b': 0, 'result': 1},
        {'a': 1, 'b': 1, 'result': 0}
    ]

@pytest.fixture
def table_and():
    """Таблица для f = a & b (Монотонная, сохраняет 0 и 1, нелинейная)"""
    return [
        {'a': 0, 'b': 0, 'result': 0},
        {'a': 0, 'b': 1, 'result': 0},
        {'a': 1, 'b': 0, 'result': 0},
        {'a': 1, 'b': 1, 'result': 1}
    ]

@pytest.fixture
def poly_handler():
    return MockZhegalkin(['a', 'b'])

def test_get_coefficients(poly_handler, table_xor):
    """Проверка вычисления коэффициентов методом треугольника."""
    coeffs = poly_handler._get_coefficients(table_xor)
    assert coeffs == [0, 1, 1, 0]

def test_get_zhegalkin_polynomial(poly_handler, table_xor):
    """Проверка строкового представления полинома."""
    poly_str = poly_handler.get_zhegalkin_polynomial(table_xor)
    assert "1a" in poly_str
    assert "1b" in poly_str
    assert "0ab" in poly_str 


def test_linearity(poly_handler, table_xor, table_and):
    """Линейность: XOR - да, AND - нет."""
    assert poly_handler.linearity(table_xor) is True
    assert poly_handler.linearity(table_and) is False

def test_preserving_constants(poly_handler, table_and):
    """Сохранение констант 0 и 1."""
    assert poly_handler.preserving_zero(table_and) is True
    assert poly_handler.preserving_one(table_and) is True
    
    # f = !a
    not_table = [{'a': 0, 'result': 1}, {'a': 1, 'result': 0}]
    poly_handler_1 = MockZhegalkin(['a'])
    assert poly_handler_1.preserving_zero(not_table) is False
    assert poly_handler_1.preserving_one(not_table) is False

def test_self_duality(poly_handler, table_xor):
    """Самодвойственность: XOR(a,b) не самодвойственна, но NOT(a) - да."""
    assert poly_handler.self_duality(table_xor) is False
    
    not_table = [{'a': 0, 'result': 1}, {'a': 1, 'result': 0}]
    assert MockZhegalkin(['a']).self_duality(not_table) is True

def test_monotonicity(poly_handler, table_and, table_xor):
    """Монотонность: AND - да, XOR - нет."""
    assert poly_handler.monotonicity(table_and) is True
    assert poly_handler.monotonicity(table_xor) is False


def test_find_dummy_variables():
    """Поиск переменных, не влияющих на результат."""
    
    table = [
        {'a': 0, 'b': 0, 'result': 0},
        {'a': 0, 'b': 1, 'result': 0},
        {'a': 1, 'b': 0, 'result': 1},
        {'a': 1, 'b': 1, 'result': 1}
    ]
    handler = MockZhegalkin(['a', 'b'])
    dummies = handler.find_dummy_variables(table)
    assert 'b' in dummies
    assert 'a' not in dummies