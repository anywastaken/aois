import pytest
from BitArrayNumber import BitArrayNumber

# ==========================================
# Тесты инициализации (__init__)
# ==========================================

def test_init_valid():
    """Проверка создания объекта с правильными данными."""
    bits = [0] * 31 + [1]
    num = BitArrayNumber(bits)
    assert num.bits == bits

def test_init_invalid_length():
    """Проверка ошибки при неверной длине массива (не 32 бита)."""
    with pytest.raises(ValueError, match="bits length must be 32"):
        BitArrayNumber([0] * 31)  # 31 бит
        
    with pytest.raises(ValueError, match="bits length must be 32"):
        BitArrayNumber([0] * 33)  # 33 бита

def test_init_invalid_values():
    """Проверка ошибки, если в массиве есть числа кроме 0 и 1."""
    bits = [0] * 31 + [2]
    with pytest.raises(ValueError, match="bits must be 0 or 1"):
        BitArrayNumber(bits)
        
    bits_str = [0] * 31 + ["1"] # Передали строку вместо числа
    with pytest.raises(ValueError, match="bits must be 0 or 1"):
        BitArrayNumber(bits_str)

# ==========================================
# Тесты методов экземпляра
# ==========================================

def test_to_bits():
    """Проверка возврата копии массива бит."""
    original_bits = [1, 0] * 16
    num = BitArrayNumber(original_bits)
    
    returned_bits = num.to_bits()
    assert returned_bits == original_bits
    
    # Проверяем, что вернулась именно копия, а не ссылка на оригинальный массив
    returned_bits[0] = 0
    assert num.bits[0] == 1 # Оригинал не должен измениться

def test_to_bin_str():
    """Проверка перевода в строковый формат."""
    bits = [1, 1, 0, 0] + [0] * 28
    num = BitArrayNumber(bits)
    expected_str = "1100" + "0" * 28
    assert num.to_bin_str() == expected_str

# ==========================================
# Тесты статических методов конвертации
# ==========================================

def test_unsigned_to_bits_valid():
    """Проверка корректного перевода числа в биты."""
    # 5 в двоичной это 101, ширина 4 -> 0101
    assert BitArrayNumber._unsigned_to_bits(5, 4) == [0, 1, 0, 1]
    
    # 0 всегда нули
    assert BitArrayNumber._unsigned_to_bits(0, 8) == [0] * 8

def test_unsigned_to_bits_negative():
    """Проверка ошибки при передаче отрицательного числа."""
    with pytest.raises(ValueError, match="value must be non-negative"):
        BitArrayNumber._unsigned_to_bits(-5, 4)

def test_unsigned_to_bits_overflow():
    """Проверка ошибки переполнения (число не влезает в заданную ширину)."""
    # 16 в двоичной это 10000 (5 бит), в ширину 4 не влезет
    with pytest.raises(OverflowError, match="value does not fit in width"):
        BitArrayNumber._unsigned_to_bits(16, 4)

def test_bits_to_unsigned():
    """Проверка перевода массива бит обратно в число."""
    assert BitArrayNumber._bits_to_unsigned([0, 1, 0, 1]) == 5
    assert BitArrayNumber._bits_to_unsigned([1, 1, 1, 1]) == 15
    assert BitArrayNumber._bits_to_unsigned([0, 0, 0, 0]) == 0