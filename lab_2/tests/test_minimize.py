import pytest
from Minimize import Minimize 

class MockLogic(Minimize):
    def __init__(self, variables):
        self.variables = variables

@pytest.fixture
def minimizer():
    return MockLogic(['a', 'b', 'c'])

def test_find_difference(minimizer):
    """Проверка подсчета различий между термами."""
    t1 = (1, 0, 1)
    t2 = (1, 1, 1)
    t3 = (0, 1, 0)
    assert minimizer.find_difference(t1, t2) == 1
    assert minimizer.find_difference(t1, t3) == 3

def test_merge(minimizer):
    """Проверка склеивания (операция поглощения переменной)."""
    t1 = (1, 0, 1)
    t2 = (1, 1, 1)
    assert minimizer.merge(t1, t2) == (1, None, 1)

def test_get_all_combinations(minimizer):
    """Проверка развертывания сокращенного терма в полные наборы."""
    term = (1, None, 0)
    expected = [(1, 0, 0), (1, 1, 0)]
    result = minimizer.get_all_combinations(term)
    assert set(result) == set(expected)

def test_matches(minimizer):
    """Проверка вхождения точки в область импликанты."""
    implicant = (1, None, 0)
    assert minimizer.matches((1, 0, 0), implicant) is True
    assert minimizer.matches((1, 1, 0), implicant) is True
    assert minimizer.matches((0, 0, 0), implicant) is False

def test_is_covered(minimizer):
    """Проверка избыточности терма."""
    term = (1, None, None) 
    others = [(1, 0, None), (1, 1, None)] 
    assert minimizer.is_covered(term, others) is True
    
    others_incomplete = [(1, 0, None)]
    assert minimizer.is_covered(term, others_incomplete) is False

def test_minimize_calculation_sdnf(minimizer, capsys):
    """Тест минимизации СДНФ расчетным методом."""
    terms = [(1,0,0), (1,0,1), (1,1,0), (1,1,1)]
    result = minimizer.minimize_calculation(terms, mode="SDNF")
    
    assert len(result) == 1
    assert result[0] == (1, None, None)
    
    captured = capsys.readouterr()
    assert "(a)" in captured.out

def test_minimize_calculation_table_method(minimizer, capsys):
    """Тест табличного метода минимизации."""
    terms = [
        (0,0,0), (0,0,1), (0,1,0), 
        (1,0,1), (1,1,0), (1,1,1)
    ]
    result = minimizer.minimize_calculation_table(terms, mode="SDNF")
    
    assert len(result) > 0
    captured = capsys.readouterr()
    assert "ИМПЛИКАНТНАЯ ТАБЛИЦА" in captured.out
    assert "X" in captured.out

def test_print_formats(minimizer):
    """Проверка строкового представления результатов."""
    sdnf = [(1, 0, None)] 
    sknf = [(0, 1, None)] 
    
    assert "a!b" in minimizer.print_minimized_sdnf(sdnf)
    assert "!a&b" in minimizer.print_minimized_sknf(sknf)