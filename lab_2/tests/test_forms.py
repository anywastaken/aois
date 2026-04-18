import pytest
from SDNF_SKNF import SDNF_SKNF  

class MockForms(SDNF_SKNF):
    def __init__(self, variables):
        self.variables = variables

@pytest.fixture
def table_data():
    """
    Таблица истинности для функции XOR (a ^ b):
    a | b | F
    --|---|--
    0 | 0 | 0  (Индекс 0)
    0 | 1 | 1  (Индекс 1)
    1 | 0 | 1  (Индекс 2)
    1 | 1 | 0  (Индекс 3)
    """
    return [
        {'a': 0, 'b': 0, 'result': 0},
        {'a': 0, 'b': 1, 'result': 1},
        {'a': 1, 'b': 0, 'result': 1},
        {'a': 1, 'b': 1, 'result': 0}
    ]

@pytest.fixture
def forms_handler():
    return MockForms(['a', 'b'])


def test_get_sdnf(forms_handler, table_data):
    """Проверка текстового построения СДНФ."""
    
    result = forms_handler.get_sdnf(table_data)
    assert "(!ab)" in result
    assert "(a!b)" in result
    assert "&" in result

def test_get_sdnf_without_vars(forms_handler, table_data):
    """Проверка кортежной формы СДНФ (для минимизации)."""

    expected = [(0, 1), (1, 0)]
    result = forms_handler.get_sdnf_without_vars(table_data)
    assert result == expected

def test_get_numeric_sdnf(forms_handler, table_data):
    """Проверка числовой формы СДНФ."""
    
    result = forms_handler.get_numeric_sdnf(table_data)
    assert result == "|(1, 2)"


def test_get_sknf(forms_handler, table_data):
    """Проверка текстового построения СКНФ."""
    
    result = forms_handler.get_sknf(table_data)
    assert "(a|b)" in result
    assert "(!a|!b)" in result

def test_get_sknf_without_vars(forms_handler, table_data):
    """Проверка кортежной формы СКНФ."""
    expected = [(1, 1), (0, 0)]
    result = forms_handler.get_sknf_without_vars(table_data)
    assert result == expected

def test_get_numeric_sknf(forms_handler, table_data):
    """Проверка числовой формы СКНФ."""
    
    result = forms_handler.get_numeric_sknf(table_data)
    assert result == "&(0, 3)"


def test_empty_functions(forms_handler):
    """Проверка поведения при константах (все 0 или все 1)."""
    const_one = [{'a': 0, 'result': 1}, {'a': 1, 'result': 1}]
    
    assert "отсутствует" in forms_handler.get_numeric_sknf(const_one)
    
    const_zero = [{'a': 0, 'result': 0}, {'a': 1, 'result': 0}]
    assert "отсутствует" in forms_handler.get_numeric_sdnf(const_zero)