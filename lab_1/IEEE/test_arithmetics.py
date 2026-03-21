from IEEE.Arithmetics import Arithmetics


class DummyFloat(Arithmetics):
    def __init__(self, bits):
        self.bits = bits

    def get_sign(self) -> int:
        return self.bits[0]

    def get_exponent_raw(self) -> int:
        val = 0
        for b in self.bits[1:9]:
            val = val * 2 + b
        return val


# --- Генераторы тестовых чисел (IEEE-754 представления) ---
ZERO = DummyFloat([0] * 32)
ONE = DummyFloat([0] + [0,1,1,1,1,1,1,1] + [0]*23)           # 1.0
TWO = DummyFloat([0] + [1,0,0,0,0,0,0,0] + [0]*23)           # 2.0
THREE = DummyFloat([0] + [1,0,0,0,0,0,0,0] + [1] + [0]*22)   # 3.0
MINUS_ONE = DummyFloat([1] + [0,1,1,1,1,1,1,1] + [0]*23)     # -1.0


def test_add_arrays():
    obj = DummyFloat([0]*32)
    a = [0, 1, 1]
    b = [0, 0, 1]
    res, carry = obj._add_arrays(a, b)
    assert res == [1, 0, 0] # 3 + 1 = 4 (в 3 битах это 100)
    assert carry == 0

def test_sub_arrays():
    obj = DummyFloat([0]*32)
    a = [1, 0, 0] # 4
    b = [0, 0, 1] # 1
    res = obj._sub_arrays(a, b)
    assert res == [0, 1, 1] # 3

def test_mul_arrays():
    obj = DummyFloat([0]*32)
    # Тест на коротких массивах для метода, который жестко зашит на 24 бита
    a = [0]*23 + [1] # 1
    b = [0]*22 + [1, 0] # 2
    res = obj._mul_arrays(a, b)
    assert res[-2:] == [1, 0] # 1 * 2 = 2

def test_addition_normal():
    # 1.0 + 2.0 = 3.0
    res = ONE + TWO
    assert res.bits == THREE.bits

def test_addition_zero():
    # 1.0 + 0.0 = 1.0
    res = ONE + ZERO
    assert res.bits == ONE.bits
    
    # 0.0 + 2.0 = 2.0
    res = ZERO + TWO
    assert res.bits == TWO.bits

def test_subtraction_normal():
    # 3.0 - 1.0 = 2.0
    res = THREE - ONE
    assert res.bits == TWO.bits
    
    # 2.0 - 3.0 = -1.0
    res = TWO - THREE
    assert res.bits == MINUS_ONE.bits

def test_subtraction_to_zero():
    # 2.0 - 2.0 = 0.0
    res = TWO - TWO
    assert res.bits == [0]*32

def test_multiplication_normal():
    # 1.0 * 2.0 = 2.0
    res = ONE * TWO
    assert res.bits == TWO.bits

def test_multiplication_zero():
    # 3.0 * 0.0 = 0.0
    res = THREE * ZERO
    assert res.bits == [0]*32

def test_multiplication_signs():
    # -1.0 * 2.0 = -2.0
    res = MINUS_ONE * TWO
    expected_bits = [1] + TWO.bits[1:]
    assert res.bits == expected_bits

def test_division_normal():
    # 3.0 / 1.0 = 3.0
    res = THREE / ONE
    assert res.bits == THREE.bits

def test_division_by_zero():
    # X / 0 = Infinity (Экспонента из единиц, мантисса нули)
    res = ONE / ZERO
    assert res.bits[1:9] == [1]*8
    assert res.bits[9:] == [0]*23

def test_zero_divided_by_zero():
    # 0 / 0 = NaN (Экспонента из единиц, мантисса не пустая)
    res = ZERO / ZERO
    assert res.bits[1:9] == [1]*8
    assert res.bits[9] == 1 # Первая 1 в мантиссе
    
def test_zero_divided_by_number():
    # 0 / X = 0
    res = ZERO / TWO
    assert res.bits[1:] == [0]*31

def test_overflow_add():
    # Искусственно создаем число близкое к переполнению
    huge = DummyFloat([0] + [1,1,1,1,1,1,1,0] + [1]*23) 
    res = huge + huge # Должно дать Infinity
    assert res.bits[1:9] == [1]*8
    assert res.bits[9:] == [0]*23

def test_underflow_mul():
    # Искусственно создаем очень маленькие числа
    tiny = DummyFloat([0] + [0,0,0,0,0,0,1,0] + [0]*23)
    res = tiny * tiny # Должно дать 0 (underflow)
    assert res.bits[1:] == [0]*31