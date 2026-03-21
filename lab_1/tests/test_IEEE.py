import pytest
import math
from IEEE.IEEE import IEEE


def test_getters():
    bits = [0] + [0, 1, 1, 1, 1, 1, 1, 1] + [1] + [0] * 22
    num = IEEE(bits)
    
    assert num.get_sign() == 0
    assert num.get_exponent_raw() == 127
    assert num.get_exponent() == 0  # 127 - 127 = 0
    
    # Метод get_mantissa добавляет неявную единицу в начало
    expected_mantissa = [1, 1] + [0] * 22
    assert num.get_mantissa() == expected_mantissa



def test_from_decimal_normal():
    # Обычное положительное число (целая часть > 0)
    num1 = IEEE.from_decimal(1.5)
    assert num1.bits[0] == 0
    
    # Обычное отрицательное число
    num2 = IEEE.from_decimal(-2.25)
    assert num2.bits[0] == 1

def test_from_decimal_fraction_only():
    num = IEEE.from_decimal(0.25)
    assert num.get_exponent() == -2
    assert num.to_decimal() == 0.25

def test_from_decimal_special_cases():
    # Ноль и отрицательный ноль
    zero = IEEE.from_decimal(0.0)
    assert zero.bits[0] == 0
    assert zero.get_exponent_raw() == 0
    
    neg_zero = IEEE.from_decimal(-0.0)
    assert neg_zero.bits[0] == 1
    assert neg_zero.get_exponent_raw() == 0

    # Бесконечности
    inf = IEEE.from_decimal(float('inf'))
    assert inf.bits[0] == 0
    assert inf.get_exponent_raw() == 255
    assert not any(inf.bits[9:]) # Мантисса должна состоять из нулей
    
    neg_inf = IEEE.from_decimal(float('-inf'))
    assert neg_inf.bits[0] == 1
    assert neg_inf.get_exponent_raw() == 255
    
    # NaN
    nan_val = IEEE.from_decimal(float('nan'))
    assert nan_val.get_exponent_raw() == 255
    assert any(nan_val.bits[9:]) # В мантиссе должна быть хотя бы одна 1


def test_to_decimal_normal():
    # Взаимная проверка: собираем через from_decimal и проверяем to_decimal
    values = [1.5, -3.14, 100.0, -0.125, 0.333]
    for val in values:
        num = IEEE.from_decimal(val)
        # Для float используем pytest.approx из-за погрешности вычислений
        assert num.to_decimal() == pytest.approx(val, rel=1e-5)

def test_to_decimal_special_cases():
    # Проверка нуля
    assert IEEE([0] + [0]*8 + [0]*23).to_decimal() == 0.0
    
    # Проверка отрицательного нуля
    res_neg_zero = IEEE([1] + [0]*8 + [0]*23).to_decimal()
    # В Python 0.0 == -0.0, но можно проверить через строку, как в вашем коде
    assert str(res_neg_zero) == "-0.0"

    # Проверка бесконечностей
    assert IEEE([0] + [1]*8 + [0]*23).to_decimal() == float('inf')
    assert IEEE([1] + [1]*8 + [0]*23).to_decimal() == float('-inf')

    nan_num = IEEE([0] + [1]*8 + [1] + [0]*22)
    assert math.isnan(nan_num.to_decimal())