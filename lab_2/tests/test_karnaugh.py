import pytest
from KarnaughMap import KarnaughMap  

@pytest.fixture
def kmap_2var():
    return KarnaughMap([0, 0, 0, 1], ['a', 'b'])

@pytest.fixture
def kmap_3var_corners():
    results = [1, 0, 1, 0, 1, 0, 1, 0]
    return KarnaughMap(results, ['a', 'b', 'c'])

def test_init_dimensions():
    """Проверка правильности определения размеров сетки."""
    km2 = KarnaughMap([0]*4, ['a', 'b'])
    assert km2.rows == 2 and km2.cols == 2
    
    km3 = KarnaughMap([0]*8, ['a', 'b', 'c'])
    assert km3.rows == 2 and km3.cols == 4
    
    km4 = KarnaughMap([0]*16, ['a', 'b', 'c', 'd'])
    assert km4.rows == 4 and km4.cols == 4

def test_grid_indices_gray_logic():
    """Проверка, что индексы в сетке соответствуют коду Грея."""
    km = KarnaughMap([i for i in range(16)], ['a', 'b', 'c', 'd'])
    assert km.grid_indices[0][0] == 0
    assert km.grid_indices[0][2] == 12
    assert km.grid_indices[2][2] == 15 

def test_find_rectangles_simple(kmap_2var):
    """Тест поиска одной группы для функции И (a & b)."""
    rects = kmap_2var.find_rectangles(target_value=1)
    assert len(rects) == 1
    assert len(rects[0]) == 1

def test_find_rectangles_large_group(kmap_3var_corners):
    """Тест поиска большой группы (4 клетки)."""
    rects = kmap_3var_corners.find_rectangles(target_value=1)
    assert len(rects) == 1
    assert len(rects[0]) == 4

def test_rect_to_term_dnf(kmap_2var):
    """Проверка перевода прямоугольника в терм ДНФ."""
    rects = kmap_2var.find_rectangles(target_value=1)
    term = kmap_2var.rect_to_term(rects[0], mode="DNF")
    assert "a" in term
    assert "b" in term
    assert "!" not in term

def test_rect_to_term_knf():
    """Проверка перевода в терм КНФ."""
    km = KarnaughMap([0, 1, 1, 1], ['a', 'b']) 

    rects = km.find_rectangles(target_value=0)
    term = km.rect_to_term(rects[0], mode="KNF")
    assert term == "(a | b)"

def test_optimize_coverage():
    """Тест алгоритма минимального покрытия."""
    km = KarnaughMap([0]*4, ['a', 'b'])
    targets = [(0, 0), (0, 1), (1, 0)]
    rectangles = [
        ((0, 0), (0, 1)), 
        ((0, 0), (1, 0)), 
        ((0, 0),),        
        ((0, 1),),
        ((1, 0),)
    ]
    optimized = km.optimize_coverage(targets, rectangles)
    assert len(optimized) == 2

def test_display_smoke(kmap_2var, capsys):
    """Smoke-тест метода отображения (что не падает и выводит таблицу)."""
    kmap_2var.display(mode="DNF")
    captured = capsys.readouterr()
    assert "КАРТА КАРНО" in captured.out
    assert "[1]" in captured.out 

def test_cyclic_edge_case():
    """Проверка склейки через края (цикличность)."""
    results = [0] * 16
    for i in [0, 8, 2, 10]: results[i] = 1
    km = KarnaughMap(results, ['a', 'b', 'c', 'd'])
    
    rects = km.find_rectangles(target_value=1)
    assert len(rects) == 1
    assert len(rects[0]) == 4
    term = km.rect_to_term(rects[0], mode="DNF")
    assert term == "(!b & !d)"