import pytest
from LogicExpression import LogicExpression 


def test_initialization_valid():
    """Тест корректной инициализации и определения переменных."""
    expr = "a & b -> c"
    le = LogicExpression(expr)
    assert le.variables == ['a', 'b', 'c']
    assert '->' in le.tokens
    assert le.raw_expression == "a&b->c"

@pytest.mark.parametrize("expression, expected_tokens", [
    ("a&b", ['a', '&', 'b']),
    ("!(a|b)", ['!', '(', 'a', '|', 'b', ')']),
    ("a->b~c", ['a', '->', 'b', '~', 'c']),
    ("a^b", ['a', '^', 'b'])
])
def test_tokenize(expression, expected_tokens):
    le = LogicExpression(expression)
    assert le._tokenize(le.raw_expression) == expected_tokens

@pytest.mark.parametrize("expression, expected_rpn", [
    ("a&b", ['a', 'b', '&']),
    ("!a", ['a', '!']),
    ("a|b&c", ['a', 'b', 'c', '&', '|']), 
    ("(a|b)&c", ['a', 'b', '|', 'c', '&'])
])
def test_to_rpn(expression, expected_rpn):
    le = LogicExpression(expression)
    assert le.rpn == expected_rpn

@pytest.mark.parametrize("expression, values, expected_result", [
    ("a & b", {'a': 1, 'b': 1}, 1),
    ("a & b", {'a': 1, 'b': 0}, 0),
    ("a | b", {'a': 0, 'b': 1}, 1),
    ("!a", {'a': 1}, 0),
    ("!a", {'a': 0}, 1),
    ("a -> b", {'a': 1, 'b': 0}, 0),
    ("a -> b", {'a': 0, 'b': 1}, 1),
    ("a ~ b", {'a': 1, 'b': 1}, 1),
    ("a ~ b", {'a': 1, 'b': 0}, 0),
    ("a ^ b", {'a': 1, 'b': 1}, 0),
    ("a ^ b", {'a': 1, 'b': 0}, 1),
])
def test_evaluate(expression, values, expected_result):
    le = LogicExpression(expression)
    assert le._evaluate(values) == expected_result

def test_generate_truth_table(capsys):
    """Проверяет генерацию таблицы и вывод в консоль."""
    le = LogicExpression("a & b")
    table = le.generate_truth_table()
    
    assert len(table) == 4 # 2^2 комбинации
    assert table[0] == {'a': 0, 'b': 0, 'result': 0}
    assert table[3] == {'a': 1, 'b': 1, 'result': 1}
    
    captured = capsys.readouterr()
    assert "a | b | F" in captured.out

def test_get_index_form():
    """Тест получения десятичного индекса функции."""
    le = LogicExpression("a & b")
    table = [
        {'result': 0}, 
        {'result': 0}, 
        {'result': 0}, 
        {'result': 1}  
    ]
    assert le.get_index_form(table) == 1

def test_calculate_diff():
    """Тест производной булевой функции."""
    le = LogicExpression("a")
    values = [0, 1] 
    diff = le.calculate_diff(values, 'a')
    assert diff == [1, 1]

def test_is_valid_edge_cases():
    le = LogicExpression("a")
    assert le._is_valid("") is False
    assert le._is_valid("a & (b") is False 
    assert le._is_valid("()") is False 