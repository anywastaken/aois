_MANTISSA = 23
WIDTH = 32

class Arithmetics:
    global _MANTISSA

    def _add_arrays(self, a: list[int], b: list[int]) -> tuple[list[int], int]:
        result = [0] * len(a)
        carry = 0
        for i in range(len(a) - 1, -1, -1):
            bit_sum = a[i] + b[i] + carry
            result[i] = bit_sum % 2
            carry = bit_sum // 2
        return result, carry

    def _sub_arrays(self, a: list[int], b: list[int]) -> list[int]:
        result = [0] * len(a)
        borrow = 0
        for i in range(len(a) - 1, -1, -1):
            diff = a[i] - b[i] - borrow
            if diff < 0:
                diff += 2
                borrow = 1
            else:
                borrow = 0
            result[i] = diff
        return result

    def __add__(self, other):
        # Чтобы избежать циклического импорта, обращаемся к классу через type(self)
        CurrentClass = type(self) 

        if not any(self.bits[1:]): return other
        if not any(other.bits[1:]): return self

        sign1, exp1 = self.get_sign(), self.get_exponent_raw()
        sign2, exp2 = other.get_sign(), other.get_exponent_raw()

        m1 = [1] + self.bits[9:]
        m2 = [1] + other.bits[9:]

        exp_res = exp1
        if exp1 > exp2:
            shift = exp1 - exp2
            m2 = ([0] * shift + m2)[:_MANTISSA + 1]
            exp_res = exp1
        elif exp2 > exp1:
            shift = exp2 - exp1
            m1 = ([0] * shift + m1)[:_MANTISSA + 1]
            exp_res = exp2

        carry = 0
        if sign1 == sign2:
            m_res, carry = self._add_arrays(m1, m2)
            sign_res = sign1
        else:
            if m1 >= m2:
                m_res = self._sub_arrays(m1, m2)
                sign_res = sign1
            else:
                m_res = self._sub_arrays(m2, m1)
                sign_res = sign2

        if not any(m_res) and carry == 0:
            return CurrentClass([0] * WIDTH)

        if carry == 1:
            m_res = [1] + m_res[:-1]
            exp_res += 1
        else:
            shift = 0
            while shift < _MANTISSA + 1 and m_res[shift] == 0:
                shift += 1
            if shift > 0:
                m_res = m_res[shift:] + [0] * shift
                exp_res -= shift

        if exp_res >= 255:
            return CurrentClass([sign_res] + [1]*8 + [0]*_MANTISSA)
        if exp_res <= 0:
            return CurrentClass([sign_res] + [0]*8 + [0]*_MANTISSA)

        exp_bits = []
        temp_exp = exp_res
        for _ in range(8):
            exp_bits.append(temp_exp % 2)
            temp_exp //= 2
        exp_bits = exp_bits[::-1]

        mantissa_bits = m_res[1:]
        return CurrentClass([sign_res] + exp_bits + mantissa_bits)
    
    def _mul_arrays(self, a: list[int], b: list[int]) -> list[int]:
        """Умножает два _MANTISSA + 1-битных массива. Возвращает массив из 48 бит."""
        result = [0] * 48
        for i in range(_MANTISSA, -1, -1):
            if b[i] == 1:
                carry = 0
                for j in range(_MANTISSA, -1, -1):
                    pos = i + j + 1
                    bit_sum = result[pos] + a[j] + carry
                    result[pos] = bit_sum % 2
                    carry = bit_sum // 2
                result[i] += carry
        return result
    
    def __mul__(self, other):
        CurrentClass = type(self)
        
        # 1. Проверка на нули (любое число на 0 дает 0)
        # Если все биты кроме знакового равны 0, значит это ноль
        if not any(self.bits[1:]) or not any(other.bits[1:]): 
            # Вычисляем знак нуля по общим правилам
            sign_res = (self.get_sign() + other.get_sign()) % 2
            return CurrentClass([sign_res] + [0] * 31)

        sign1, exp1 = self.get_sign(), self.get_exponent_raw()
        sign2, exp2 = other.get_sign(), other.get_exponent_raw()

        # 2. Знак результата
        sign_res = (sign1 + sign2) % 2

        # 3. Сложение порядков со сбросом лишнего смещения (127)
        exp_res = exp1 + exp2 - 127

        # 4. Перемножение мантисс (добавляем неявную 1)
        m1 = [1] + self.bits[9:]
        m2 = [1] + other.bits[9:]
        m_res = self._mul_arrays(m1, m2)

        # 5. Нормализация мантиссы
        # В 48-битном результате целая часть находится в первых двух битах (индексы 0 и 1)
        if m_res[0] == 1:
            # Результат >= 2.0 (например, 1.5 * 1.5 = 2.25). Нужен сдвиг вправо.
            exp_res += 1
            mantissa_bits = m_res[1:_MANTISSA + 1]
        else:
            # Результат < 2.0 (например, 1.1 * 1.1 = 1.21). Нормализовано, берем со 2 бита.
            mantissa_bits = m_res[2:25]

        # 6. Проверка на переполнение / недобор экспоненты
        if exp_res >= 255: # Infinity
            return CurrentClass([sign_res] + [1] * 8 + [0] * _MANTISSA)
        if exp_res <= 0:   # Ноль (или денормализованное число, но мы округляем в ноль)
            return CurrentClass([sign_res] + [0] * 8 + [0] * _MANTISSA)

        # 7. Сборка результата
        # Переводим итоговую экспоненту в биты
        exp_bits = []
        temp_exp = exp_res
        for _ in range(8):
            exp_bits.append(temp_exp % 2)
            temp_exp //= 2
        exp_bits = exp_bits[::-1]

        return CurrentClass([sign_res] + exp_bits + mantissa_bits)
    
    def __sub__(self, other):
        CurrentClass = type(self)
        
        # Делаем копию массива бит второго операнда, чтобы не мутировать оригинальный объект
        other_bits_copy = other.bits[:]
        
        # Инвертируем знаковый бит: если был 0, станет 1; если был 1, станет 0
        other_bits_copy[0] = 1 - other_bits_copy[0]
        
        # Создаем временный объект с противоположным знаком
        negative_other = CurrentClass(other_bits_copy)
        
        # Делегируем всю работу нашей готовой перегрузке сложения
        return self.__add__(negative_other)
    
    def __truediv__(self, other):
        CurrentClass = type(self)
        
        # 1. Проверки на нули и особые случаи
        is_self_zero = not any(self.bits[1:])
        is_other_zero = not any(other.bits[1:])
        
        sign_res = (self.get_sign() + other.get_sign()) % 2
        
        if is_other_zero:
            if is_self_zero:
                # 0 / 0 = NaN (все 1 в экспоненте, первая 1 в мантиссе)
                return CurrentClass([0] + [1] * 8 + [1] + [0] * 22)
            else:
                # X / 0 = Infinity (все 1 в экспоненте, 0 в мантиссе)
                return CurrentClass([sign_res] + [1] * 8 + [0] * _MANTISSA)
                
        if is_self_zero:
            # 0 / X = 0
            return CurrentClass([sign_res] + [0] * 31)

        exp1 = self.get_exponent_raw()
        exp2 = other.get_exponent_raw()

        # 2. Вычисляем экспоненту результата
        exp_res = exp1 - exp2 + 127

        # 3. Подготовка мантисс (_MANTISSA + 1 бита: неявная 1 + _MANTISSA бита дроби)
        m1 = [1] + self.bits[9:]
        m2 = [1] + other.bits[9:]

        # 4. Бинарное деление в столбик
        quotient = []
        remainder = m1[:] # Начинаем с делимого
        
        # Нам нужно сгенерировать 25 бит частного: 
        # 1 бит целой части + _MANTISSA + 1 бита дроби (с запасом для сдвига)
        for _ in range(25):
            # Сравнение массивов (лексикографически работает как надо)
            if remainder >= m2:
                quotient.append(1)
                remainder = self._sub_arrays(remainder, m2)
            else:
                quotient.append(0)
            
            # Сдвиг остатка влево (эквивалент сноса следующего нуля)
            remainder = remainder[1:] + [0]

        # 5. Нормализация
        # Так как обе мантиссы лежат в диапазоне [1.0, 2.0), результат деления 
        # будет либо в диапазоне [1.0, 2.0) либо [0.5, 1.0)
        if quotient[0] == 1:
            # Результат >= 1. Нормализация не требуется. Берем со 2-го бита.
            mantissa_bits = quotient[1:_MANTISSA + 1]
        else:
            # Результат < 1 (начинается с 0). Нужен сдвиг влево.
            exp_res -= 1
            mantissa_bits = quotient[2:25]

        # добиваем нулями
        while len(mantissa_bits) < _MANTISSA:
            mantissa_bits.append(0)

        # 6. Проверка на переполнение / антипереполнение
        if exp_res >= 255:
            return CurrentClass([sign_res] + [1] * 8 + [0] * _MANTISSA)
        if exp_res <= 0:
            return CurrentClass([sign_res] + [0] * 8 + [0] * _MANTISSA)

        # 7. Сборка результата
        exp_bits = []
        temp_exp = exp_res
        for _ in range(8):
            exp_bits.append(temp_exp % 2)
            temp_exp //= 2
        exp_bits = exp_bits[::-1]

        return CurrentClass([sign_res] + exp_bits + mantissa_bits)