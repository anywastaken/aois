import pytest
from BCDExcess3 import BCDExcess3


def test_from_and_to_decimal():
    """Проверка перевода числа в формат Excess-3 и обратно."""
    # Проверка нуля
    bcd_zero = BCDExcess3.from_decimal(0)
    assert bcd_zero.to_decimal() == 0
    
    # Проверка максимального числа
    bcd_max = BCDExcess3.from_decimal(99999999)
    assert bcd_max.to_decimal() == 99999999
    
    # Обычное число
    bcd_normal = BCDExcess3.from_decimal(12345)
    assert bcd_normal.to_decimal() == 12345

def test_from_decimal_exceptions():
    """Проверка срабатывания исключений при недопустимых значениях."""
    # Отрицательное число
    with pytest.raises(ValueError, match="Поддерживаются только числа от 0 до 99 999 999"):
        BCDExcess3.from_decimal(-1)
        
    # Число больше 8 знаков
    with pytest.raises(ValueError, match="Поддерживаются только числа от 0 до 99 999 999"):
        BCDExcess3.from_decimal(100000000)


def test_add_4bit():
    """Проверка сложения двух 4-битных массивов с учетом переноса."""
    # Создаем любой объект, чтобы иметь доступ к методу _add_4bit
    obj = BCDExcess3.from_decimal(0)
    
    # 3 (0011) + 4 (0100) = 7 (0111), перенос 0
    res, carry = obj._add_4bit([0, 0, 1, 1], [0, 1, 0, 0], 0)
    assert res == [0, 1, 1, 1]
    assert carry == 0

    # 9 (1001) + 7 (0111) = 16 -> 0 (0000), перенос 1
    res, carry = obj._add_4bit([1, 0, 0, 1], [0, 1, 1, 1], 0)
    assert res == [0, 0, 0, 0]
    assert carry == 1

    # Проверка входящего переноса: 9 + 7 + 1 = 17 -> 1 (0001), перенос 1
    res, carry = obj._add_4bit([1, 0, 0, 1], [0, 1, 1, 1], 1)
    assert res == [0, 0, 0, 1]
    assert carry == 1


def test_bcd_addition_no_carry():
    """Сложение без перехода через десяток (коррекция SUB_3)."""
    # 2 + 3 = 5 (сумма тетрад <= 9, должен сработать вычет 3)
    a = BCDExcess3.from_decimal(2)
    b = BCDExcess3.from_decimal(3)
    assert (a + b).to_decimal() == 5

def test_bcd_addition_with_carry():
    """Сложение с переходом через десяток (коррекция ADD_3)."""
    # 7 + 5 = 12 (сумма тетрад > 9, должно сработать прибавление 3 и перенос)
    a = BCDExcess3.from_decimal(7)
    b = BCDExcess3.from_decimal(5)
    assert (a + b).to_decimal() == 12

def test_bcd_addition_cascade_carry():
    """Сложение с каскадным переносом по всем разрядам."""
    # 9999 + 1 = 10000
    a = BCDExcess3.from_decimal(9999)
    b = BCDExcess3.from_decimal(1)
    assert (a + b).to_decimal() == 10000

def test_bcd_addition_overflow():
    """Проверка поведения при переполнении 32 бит (8 цифр)."""
    a = BCDExcess3.from_decimal(99999999)
    b = BCDExcess3.from_decimal(1)
    assert (a + b).to_decimal() == 0


def test_get_binary_string():
    """Проверка генерации двоичной строки с пробелами."""
    # Для 0 (в Excess-3 каждая цифра 0 кодируется как 0011)
    num_zero = BCDExcess3.from_decimal(0)
    expected_zero = " ".join(["0011"] * 8)
    assert num_zero.get_binary_string() == expected_zero
    
    num_1234 = BCDExcess3.from_decimal(1234)
    expected_1234 = "0011 0011 0011 0011 0100 0101 0110 0111"
    assert num_1234.get_binary_string() == expected_1234