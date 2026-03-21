from BitArrayNumber import BitArrayNumber

WIDTH = 32

class BCDExcess3(BitArrayNumber):
    
    @classmethod
    def from_decimal(cls, value: int) -> "BCDExcess3":
        """Переводит десятичное число в 32-битный массив Excess-3."""
        if value < 0 or value > 99999999:
            raise ValueError("Поддерживаются только числа от 0 до 99 999 999")
            
        bits = []
        # Добиваем число нулями слева до 8 цифр
        value_str = ""
        temp_val = value
        for _ in range(8):
            value_str = chr(48 + (temp_val % 10)) + value_str # chr(48) это '0'
            temp_val //= 10
            
        for char in value_str:
            # Превращаем символ обратно в число и добавляем избыток 3
            digit = (ord(char) - 48) + 3 
            
            # Переводим в 4 бита
            nibble = []
            temp_digit = digit
            for _ in range(4):
                nibble.append(temp_digit % 2)
                temp_digit //= 2
            bits.extend(nibble[::-1])
            
        return cls(bits)

    def to_decimal(self) -> int:
        """Переводит 32-битный массив Excess-3 обратно в десятичное число."""
        total = 0
        multiplier = 10000000  # 10^7 для старшего разряда
        
        for i in range(8):
            start = i * 4
            end = start + 4
            nibble = self.bits[start:end]
            
            # Переводим 4 бита в число
            val = 0
            for bit in nibble:
                val = val * 2 + bit
                
            # Вычитаем избыток 3
            digit = val - 3
            total += digit * multiplier
            multiplier //= 10
            
        return total

    def _add_4bit(self, a: list[int], b: list[int], carry_in: int) -> tuple[list[int], int]:
        """Вспомогательный метод для сложения двух тетрад с переносом."""
        result = [0] * 4
        carry = carry_in
        for i in range(3, -1, -1):
            bit_sum = a[i] + b[i] + carry
            result[i] = bit_sum % 2
            carry = bit_sum // 2
        return result, carry

    def __add__(self, other: "BCDExcess3") -> "BCDExcess3":
        """Перегрузка сложения двух чисел в формате Excess-3."""
        result_bits = [0] * WIDTH
        main_carry = 0
        
        # Константы для коррекции
        ADD_3 = [0, 0, 1, 1]
        SUB_3 = [1, 1, 0, 1] # Трюк с дополнительным кодом (-3)

        # Идем с конца в начало блоками по 4 бита
        for i in range(7, -1, -1):
            start = i * 4
            end = start + 4
            
            nibble_a = self.bits[start:end]
            nibble_b = other.bits[start:end]
            
            # 1. Складываем тетрады + пришедший перенос
            sum_nibble, next_carry = self._add_4bit(nibble_a, nibble_b, main_carry)
            
            # 2. Коррекция
            if next_carry == 1:
                # Сумма > 9: прибавляем 3
                corrected_nibble, _ = self._add_4bit(sum_nibble, ADD_3, 0)
            else:
                # Сумма <= 9: вычитаем 3 (прибавляя 1101 и игнорируя перенос)
                corrected_nibble, _ = self._add_4bit(sum_nibble, SUB_3, 0)
                
            # 3. Записываем результат и сохраняем перенос для следующего шага
            result_bits[start:end] = corrected_nibble
            main_carry = next_carry

        return type(self)(result_bits)

    def get_binary_string(self) -> str:
        """Возвращает строку с двоичным представлением (с пробелами для удобства)."""
        chunks = []
        for i in range(8):
            start = i * 4
            chunk = "".join(str(b) for b in self.bits[start:start+4])
            chunks.append(chunk)
        return " ".join(chunks)