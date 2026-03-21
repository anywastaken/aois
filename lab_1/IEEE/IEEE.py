from BitArrayNumber import BitArrayNumber
from IEEE.Arithmetics import Arithmetics

_MANTISSA = 23

class IEEE(BitArrayNumber, Arithmetics):
    global _MANTISSA
    

    def get_sign(self) -> int:
        return self.bits[0]
    
    def get_exponent_raw(self) -> int:
        return self._bits_to_unsigned(self.bits[1:9])
    
    def get_exponent(self) -> int:
        return self.get_exponent_raw() - 127
    
    def get_mantissa(self) -> list[int]:
        return [1] + self.bits[9:]

    def to_decimal(self) -> float:
        sign_bit = self.get_sign()
        exp_raw = self.get_exponent_raw()
        fraction_bits = self.bits[9:]  # Дробная часть без ведущей 1

        # Проверка на NaN и Inf
        if exp_raw == 255:
            if any(fraction_bits):  # В дробной части есть хотя бы одна 1
                return float('nan')
            else:
                return float('-inf') if sign_bit else float('inf')
                
        # Проверка на ноль (0.0 и -0.0)
        if exp_raw == 0 and not any(fraction_bits):
            return -0.0 if sign_bit else 0.0

        # Стандартный код для нормализованных чисел
        sign = -1 if sign_bit else 1
        exponent = self.get_exponent()
        mantissa_bits = self.get_mantissa()

        mantissa = 0
        for i, b in enumerate(mantissa_bits):
            mantissa += b * (2 ** (-i))

        return sign * mantissa * (2 ** exponent)
    
    @classmethod
    def from_decimal(cls, value: float) -> "IEEE":
        # Обработка NaN (только NaN не равен самому себе)
        if value != value:
            # Знак 0, Экспонента все 1, Мантисса не 0 (ставим первую 1)
            return cls([0] + [1] * 8 + [1] + [0] * 22)

        # Обработка бесконечности (+Inf и -Inf)
        if value == float('inf'):
            return cls([0] + [1] * 8 + [0] * _MANTISSA)
        if value == float('-inf'):
            return cls([1] + [1] * 8 + [0] * _MANTISSA)

        # Обработка нуля (различаем 0.0 и -0.0 через строку)
        if value == 0.0:
            sign = 1 if str(value) == '-0.0' else 0
            return cls([sign] + [0] * 8 + [0] * _MANTISSA)

        # 1. знак
        sign = 0 if value >= 0 else 1
        value = abs(value)

        # 2. разделяем
        integer_part = int(value)
        fraction_part = value - integer_part

        # 3. целая часть
        def int_to_binary(n):
            if n == 0:
                return [0]
            bits = []
            while n > 0:
                bits.append(n % 2)
                n //= 2
            return bits[::-1]

        # 4. дробная часть
        def frac_to_binary(fraction, limit=30):
            bits = []
            f = fraction
            for _ in range(limit):
                f *= 2
                bit = int(f)
                bits.append(bit)
                f -= bit
            return bits

        int_bits = int_to_binary(integer_part)
        frac_bits = frac_to_binary(fraction_part)

        # 5. нормализация
        if integer_part != 0:
            shift = len(int_bits) - 1
            mantissa = int_bits[1:] + frac_bits
        else:
            shift = 0
            for i, bit in enumerate(frac_bits):
                if bit == 1:
                    shift = -(i + 1)
                    mantissa = frac_bits[i+1:]
                    break

        # 6. порядок
        exponent = shift + 127
        exp_bits = cls._unsigned_to_bits(exponent, 8)

        # 7. мантисса
        mantissa_bits = mantissa[:_MANTISSA]
        while len(mantissa_bits) < _MANTISSA:
            mantissa_bits.append(0)

        # 8. итог
        bits = [sign] + exp_bits + mantissa_bits
        return cls(bits)