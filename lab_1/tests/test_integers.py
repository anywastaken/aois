import pytest
from Integers import SignMagnitude, SignMagnitudeWithFraction, OnesComplement, TwosComplement

# ==========================================
# 1. Тесты для SignMagnitude (Прямой код)
# ==========================================

def test_sign_magnitude_conversion():
    """Проверка перевода числа в прямой код и обратно."""
    sm_pos = SignMagnitude.from_int(42)
    assert sm_pos.to_int() == 42
    assert sm_pos.bits[0] == 0  # Знак +

    sm_neg = SignMagnitude.from_int(-42)
    assert sm_neg.to_int() == -42
    assert sm_neg.bits[0] == 1  # Знак -

    sm_zero = SignMagnitude.from_int(0)
    assert sm_zero.to_int() == 0

def test_sign_magnitude_multiplication():
    """Проверка умножения в прямом коде."""
    a = SignMagnitude.from_int(5)
    b = SignMagnitude.from_int(3)
    c = SignMagnitude.from_int(-4)

    assert (a * b).to_int() == 15
    assert (a * c).to_int() == -20
    assert (c * a).to_int() == -20
    assert (c * SignMagnitude.from_int(-2)).to_int() == 8
    assert (a * SignMagnitude.from_int(0)).to_int() == 0

    with pytest.raises(TypeError, match="Can only multiply SignMagnitude objects"):
        a * 5

def test_sign_magnitude_division():
    """Проверка деления в прямом коде с дробной частью."""
    a = SignMagnitude.from_int(5)
    b = SignMagnitude.from_int(2)
    c = SignMagnitude.from_int(-2)

    # 5 / 2 = 2.5
    res_pos = a / b
    assert res_pos.to_decimal() == 2.5
    assert res_pos.to_binary_str() == "10.10000"

    # 5 / -2 = -2.5
    res_neg = a / c
    assert res_neg.to_decimal() == -2.5
    assert res_neg.to_binary_str() == "-10.10000"

    # 1 / 3 (проверка точности 5 бит: 0.01010 в двоичной)
    res_frac = SignMagnitude.from_int(1) / SignMagnitude.from_int(3)
    assert res_frac.integer == 0
    assert res_frac.fraction == [0, 1, 0, 1, 0]

    with pytest.raises(ZeroDivisionError, match="Деление на ноль!"):
        a / SignMagnitude.from_int(0)

    with pytest.raises(TypeError, match="Can only divide SignMagnitude objects"):
        a / 2

# ==========================================
# 2. Тесты для SignMagnitudeWithFraction
# ==========================================

def test_sign_magnitude_with_fraction():
    """Проверка вспомогательного класса для результатов деления."""
    # Число 0.0
    zero = SignMagnitudeWithFraction(sign=0, integer=0, fraction=[0, 0, 0, 0, 0])
    assert zero.to_decimal() == 0.0
    assert zero.to_binary_str() == "0.00000"

    # Число -3.125 (3 + 1/8) -> 3.00100
    frac_num = SignMagnitudeWithFraction(sign=1, integer=3, fraction=[0, 0, 1, 0, 0])
    assert frac_num.to_decimal() == -3.125
    assert frac_num.to_binary_str() == "-11.00100"

# ==========================================
# 3. Тесты для OnesComplement (Обратный код)
# ==========================================

def test_ones_complement_conversion():
    """Проверка перевода числа в обратный код и обратно."""
    oc_pos = OnesComplement.from_int(10)
    assert oc_pos.to_int() == 10
    assert oc_pos.bits[0] == 0

    oc_neg = OnesComplement.from_int(-10)
    assert oc_neg.to_int() == -10
    assert oc_neg.bits[0] == 1

def test_ones_complement_negative_zero():
    """Проверка 'отрицательного нуля' (все биты = 1), характерного для обратного кода."""
    neg_zero_bits = [1] * 32
    oc_neg_zero = OnesComplement(neg_zero_bits)
    assert oc_neg_zero.to_int() == 0

# ==========================================
# 4. Тесты для TwosComplement (Дополнительный код)
# ==========================================

def test_twos_complement_conversion():
    """Проверка перевода числа в дополнительный код и обратно."""
    tc_pos = TwosComplement.from_int(15)
    assert tc_pos.to_int() == 15
    assert tc_pos.bits[0] == 0

    tc_neg = TwosComplement.from_int(-15)
    assert tc_neg.to_int() == -15
    assert tc_neg.bits[0] == 1

    tc_zero = TwosComplement.from_int(0)
    assert tc_zero.to_int() == 0

def test_twos_complement_addition():
    """Проверка сложения в дополнительном коде."""
    a = TwosComplement.from_int(20)
    b = TwosComplement.from_int(-5)
    c = TwosComplement.from_int(-25)

    assert (a + b).to_int() == 15
    assert (b + c).to_int() == -30
    assert (a + c).to_int() == -5
    
    # Сложение с нулем
    assert (a + TwosComplement.from_int(0)).to_int() == 20

    with pytest.raises(TypeError, match="Can only add TwosComplement objects"):
        a + 10

def test_twos_complement_subtraction_and_negation():
    """Проверка вычитания и отрицания (унарный минус) в дополнительном коде."""
    a = TwosComplement.from_int(10)
    b = TwosComplement.from_int(4)
    
    # Проверка унарного минуса (__neg__)
    neg_a = -a
    assert neg_a.to_int() == -10
    
    # Проверка вычитания (__sub__)
    assert (a - b).to_int() == 6
    assert (b - a).to_int() == -6
    assert (a - a).to_int() == 0