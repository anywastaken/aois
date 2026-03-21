from BitArrayNumber import BitArrayNumber


#прямой код
class SignMagnitude(BitArrayNumber):
    @classmethod
    def from_int(cls, value: int) -> "SignMagnitude":
        sign = 1 if value < 0 else 0
        magnitude = -value if value < 0 else value
        mag_bits = cls._unsigned_to_bits(magnitude, cls.WIDTH - 1)
        return cls([sign] + mag_bits)

    def to_int(self) -> int:
        sign = self.bits[0]
        magnitude = self._bits_to_unsigned(self.bits[1:])
        return -magnitude if sign == 1 else magnitude
    
    def __mul__(self, other: "SignMagnitude") -> "SignMagnitude":
        """Умножение двух чисел в прямом коде"""
        if not isinstance(other, SignMagnitude):
            raise TypeError("Can only multiply SignMagnitude objects")
        
        # 1. Определяем знак результата (XOR знаков)
        result_sign = self.bits[0] ^ other.bits[0]
        
        # 2. Извлекаем модули (без знакового бита)
        a_magnitude = self.bits[1:]  # 31 бит
        b_magnitude = other.bits[1:]  # 31 бит
        
        # 3. Умножаем модули (алгоритм сдвига и сложения)
        product_bits = self._multiply_unsigned(a_magnitude, b_magnitude)
        
        # 4. Добавляем знаковый бит и возвращаем результат
        return SignMagnitude([result_sign] + product_bits)
    
    
    def __truediv__(self, other: "SignMagnitude") -> "SignMagnitudeWithFraction":
        """Деление двух чисел в прямом коде с точностью до 5 бит"""
        if not isinstance(other, SignMagnitude):
            raise TypeError("Can only divide SignMagnitude objects")
        
        # Проверка на деление на 0 (проверяем массив делителя на наличие единиц)
        if not any(other.bits[1:]):
            raise ZeroDivisionError("Деление на ноль!")
        
        # 1. Определяем знак результата (XOR знаков)
        result_sign = self.bits[0] ^ other.bits[0]
        
        # 2. Извлекаем модули как МАССИВЫ (без перевода в int!)
        a_magnitude = self.bits[1:]
        b_magnitude = other.bits[1:]
        
        # 3. Делим модули массивами
        integer_part, fractional_bits = self._divide_with_fraction(
            a_magnitude, b_magnitude, fraction_bits=5
        )
        
        # 4. Возвращаем результат со знаком и дробной частью
        return SignMagnitudeWithFraction(result_sign, integer_part, fractional_bits)

    
    def _add_31bit(self, a: list[int], b: list[int]) -> list[int]:
        """Сложение 31-битных массивов (модулей)"""
        res = [0] * 31
        carry = 0
        for i in range(30, -1, -1):
            s = a[i] + b[i] + carry
            res[i] = s % 2
            carry = s // 2
        return res

    def _sub_31bit(self, a: list[int], b: list[int]) -> list[int]:
        """Вычитание 31-битных массивов (a должно быть >= b)"""
        res = [0] * 31
        borrow = 0
        for i in range(30, -1, -1):
            diff = a[i] - b[i] - borrow
            if diff < 0:
                diff += 2
                borrow = 1
            else:
                borrow = 0
            res[i] = diff
        return res

    def _multiply_unsigned(self, a: list[int], b: list[int]) -> list[int]:
        """Умножение двух 31-битных массивов 'в столбик'"""
        result = [0] * 31
        for i in range(30, -1, -1):
            if b[i] == 1:
                # Сдвигаем массив 'a' влево на нужное количество позиций
                shift = 30 - i
                shifted_a = a[shift:] + [0] * shift
                # Складываем с промежуточным результатом
                result = self._add_31bit(result, shifted_a)
        return result

    def _divide_with_fraction(self, dividend: list[int], divisor: list[int], fraction_bits: int) -> tuple[int, list[int]]:
        """Деление массивов уголком с получением целой и дробной части"""
        quotient = []
        remainder = [0] * 31
        
        # 1. Вычисляем целую часть (проходим по 31 биту делимого)
        for bit in dividend:
            # Сдвигаем остаток влево и добавляем следующий бит делимого
            remainder = remainder[1:] + [bit]
            # Лексикографическое сравнение массивов работает как арифметическое
            if remainder >= divisor:
                quotient.append(1)
                remainder = self._sub_31bit(remainder, divisor)
            else:
                quotient.append(0)
                
        # Переводим массив целой части в int, так как этого требует твой класс SignMagnitudeWithFraction
        integer_part = self._bits_to_unsigned(quotient)
        
        # 2. Вычисляем дробную часть (добавляем нули на каждом шаге)
        fractional_bits = []
        for _ in range(fraction_bits):
            remainder = remainder[1:] + [0]
            if remainder >= divisor:
                fractional_bits.append(1)
                remainder = self._sub_31bit(remainder, divisor)
            else:
                fractional_bits.append(0)
                
        return integer_part, fractional_bits
    
class SignMagnitudeWithFraction:
    def __init__(self, sign: int, integer: int, fraction: list[int]):
        self.sign = sign
        self.integer = integer
        self.fraction = fraction  # 5 бит
    
    def to_decimal(self) -> float:
        """Конвертация в десятичное число"""
        value = self.integer
        for i, bit in enumerate(self.fraction):
            value += bit * (2 ** -(i + 1))
        return -value if self.sign == 1 else value
    
    def to_binary_str(self) -> str:
        """Конвертация в двоичную строку"""
        int_bits = []
        if self.integer == 0:
            int_bits = [0]
        else:
            v = self.integer
            while v > 0:
                int_bits.append(v % 2)
                v //= 2
            int_bits.reverse()
        
        int_str = "".join(str(b) for b in int_bits)
        frac_str = "".join(str(b) for b in self.fraction)
        
        sign_str = "-" if self.sign == 1 else ""
        return f"{sign_str}{int_str}.{frac_str}"
    

#обратный код
class OnesComplement(BitArrayNumber):
    @classmethod
    def from_int(cls, value: int) -> "OnesComplement":
        if value >= 0:
            mag_bits = cls._unsigned_to_bits(value, cls.WIDTH - 1)
            return cls([0] + mag_bits)

        magnitude = -value
        pos_bits = [0] + cls._unsigned_to_bits(magnitude, cls.WIDTH - 1)
        inv_bits = [0 if b else 1 for b in pos_bits]
        return cls(inv_bits)

    def to_int(self) -> int:
        if self.bits.count(1) == self.WIDTH:
            return 0  # negative zero
        sign = self.bits[0]
        if sign == 0:
            return self._bits_to_unsigned(self.bits[1:])
        inv_bits = [0 if b else 1 for b in self.bits]
        magnitude = self._bits_to_unsigned(inv_bits[1:])
        return -magnitude


#дополнительный код
class TwosComplement(BitArrayNumber):
    @classmethod
    def from_int(cls, value: int) -> "TwosComplement":
        if value >= 0:
            mag_bits = cls._unsigned_to_bits(value, cls.WIDTH - 1)
            return cls([0] + mag_bits)

        magnitude = -value
        pos_bits = [0] + cls._unsigned_to_bits(magnitude, cls.WIDTH - 1)
        inv_bits = [0 if b else 1 for b in pos_bits]
        # add 1
        carry = 1
        for i in range(cls.WIDTH - 1, -1, -1):
            s = inv_bits[i] + carry
            inv_bits[i] = 1 if s % 2 == 1 else 0
            carry = 1 if s >= 2 else 0
        return cls(inv_bits)

    def to_int(self) -> int:
        sign = self.bits[0]
        if sign == 0:
            return self._bits_to_unsigned(self.bits[1:])
        # two's complement: invert +1, then negative
        inv_bits = [0 if b else 1 for b in self.bits]
        carry = 1
        for i in range(self.WIDTH - 1, -1, -1):
            s = inv_bits[i] + carry
            inv_bits[i] = 1 if s % 2 == 1 else 0
            carry = 1 if s >= 2 else 0
        magnitude = self._bits_to_unsigned(inv_bits[1:])
        return -magnitude
    
    def __add__(self, other: "TwosComplement") -> "TwosComplement":
        """Сложение двух чисел в дополнительном коде"""
        if not isinstance(other, TwosComplement):
            raise TypeError("Can only add TwosComplement objects")
        
        result_bits = [0] * self.WIDTH
        carry = 0
        
        # Поразрядное сложение справа налево
        for i in range(self.WIDTH - 1, -1, -1):
            total = self.bits[i] + other.bits[i] + carry
            result_bits[i] = total % 2
            carry = total // 2
        
        # Перенос за 32-й бит отбрасывается (переполнение)
        return TwosComplement(result_bits)
    
    def __neg__(self) -> "TwosComplement":
        """Отрицание числа (нужно для вычитания)"""
        # Инвертируем все биты
        inv_bits = [0 if b else 1 for b in self.bits]
        
        # Прибавляем 1
        carry = 1
        for i in range(self.WIDTH - 1, -1, -1):
            total = inv_bits[i] + carry
            inv_bits[i] = total % 2
            carry = total // 2
        
        return TwosComplement(inv_bits)

    def __sub__(self, other: "TwosComplement") -> "TwosComplement":
        """Вычитание через сложение: A - B = A + (-B)"""
        return self + (-other)