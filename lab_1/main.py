from Integers import SignMagnitude, OnesComplement, TwosComplement
from IEEE.IEEE import IEEE
from BCDExcess3 import BCDExcess3

def print_result(title: str, dec_val, bin_val: str):
    """Вспомогательная функция для красивого вывода"""
    print(f"\n--- {title} ---")
    print(f"10-й формат: {dec_val}")
    print(f" 2-й формат: {bin_val}")
    print("-" * 30)

def format_ieee(bits: list[int]) -> str:
    """Форматирует 32 бита IEEE-754 с пробелами (знак | порядок | мантисса)"""
    b_str = "".join(str(b) for b in bits)
    return f"{b_str[0]} {b_str[1:9]} {b_str[9:]}"

def get_int_input(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число!")

def get_float_input(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите число!")

def main():
    while True:
        print("\n" + "="*50)
        print("ЛАБОРАТОРНАЯ РАБОТА №1. Представление чисел в памяти")
        print("="*50)
        print("1. Перевод числа (Прямой, Обратный, Дополнительный)")
        print("2. Сложение в дополнительном коде")
        print("3. Вычитание в дополнительном коде")
        print("4. Умножение в прямом коде")
        print("5. Деление в прямом коде")
        print("6. Операции с плавающей точкой (IEEE-754)")
        print("7. Сложение в двоично-десятичном коде (Excess-3)")
        print("0. Выход")
        print("="*50)
        
        choice = input("Выберите пункт меню: ")

        if choice == '0':
            print("Выход из программы...")
            break
            
        elif choice == '1':
            num = get_int_input("Введите целое число: ")
            
            sm = SignMagnitude.from_int(num)
            oc = OnesComplement.from_int(num)
            tc = TwosComplement.from_int(num)
            
            print_result("Прямой код", sm.to_int(), sm.to_bin_str())
            print_result("Обратный код", oc.to_int(), oc.to_bin_str())
            print_result("Дополнительный код", tc.to_int(), tc.to_bin_str())

        elif choice == '2':
            num1 = get_int_input("Введите первое число: ")
            num2 = get_int_input("Введите второе число: ")
            
            tc1 = TwosComplement.from_int(num1)
            tc2 = TwosComplement.from_int(num2)
            res = tc1 + tc2
            
            print_result("Первое число", tc1.to_int(), tc1.to_bin_str())
            print_result("Второе число", tc2.to_int(), tc2.to_bin_str())
            print_result("Сумма", res.to_int(), res.to_bin_str())

        elif choice == '3':
            num1 = get_int_input("Уменьшаемое: ")
            num2 = get_int_input("Вычитаемое: ")
            
            tc1 = TwosComplement.from_int(num1)
            tc2 = TwosComplement.from_int(num2)
            res = tc1 - tc2
            
            print_result("Уменьшаемое", tc1.to_int(), tc1.to_bin_str())
            print_result("Вычитаемое", tc2.to_int(), tc2.to_bin_str())
            print_result("Разность", res.to_int(), res.to_bin_str())

        elif choice == '4':
            num1 = get_int_input("Введите первое число: ")
            num2 = get_int_input("Введите второе число: ")
            
            sm1 = SignMagnitude.from_int(num1)
            sm2 = SignMagnitude.from_int(num2)
            res = sm1 * sm2
            print_result("Произведение", res.to_int(), res.to_bin_str())
            

        elif choice == '5':
            num1 = get_int_input("Делимое: ")
            num2 = get_int_input("Делитель: ")
            
            sm1 = SignMagnitude.from_int(num1)
            sm2 = SignMagnitude.from_int(num2)
            try:
                res = sm1 / sm2
                print_result("Частное", res.to_decimal(), res.to_binary_str())
            except AttributeError as e:
                print(f"Ошибка: {e}. Метод еще не дописан!")
            except ZeroDivisionError as e:
                print(e)

        elif choice == '6':
            num1 = get_float_input("Введите первое число: ")
            num2 = get_float_input("Введите второе число: ")
            op = input("Выберите операцию (+, -, *, /): ")

            f1 = IEEE.from_decimal(num1)
            f2 = IEEE.from_decimal(num2)
            
            print_result("Число 1", f1.to_decimal(), format_ieee(f1.bits))
            print_result("Число 2", f2.to_decimal(), format_ieee(f2.bits))
            
            res = None
            if op == '+': res = f1 + f2
            elif op == '-': res = f1 - f2
            elif op == '*': res = f1 * f2
            elif op == '/': res = f1 / f2
            else: print("Неизвестная операция")
            
            if res:
                print_result(f"Результат ({op})", res.to_decimal(), format_ieee(res.bits))

        elif choice == '7':
            try:
                num1 = get_int_input("Введите первое число (0-99999999): ")
                num2 = get_int_input("Введите второе число (0-99999999): ")
                
                bcd1 = BCDExcess3.from_decimal(num1)
                bcd2 = BCDExcess3.from_decimal(num2)
                res = bcd1 + bcd2
                
                print_result("Число 1", bcd1.to_decimal(), bcd1.get_binary_string())
                print_result("Число 2", bcd2.to_decimal(), bcd2.get_binary_string())
                print_result("Сумма", res.to_decimal(), res.get_binary_string())
            except ValueError as e:
                print(e)
                
        else:
            print("Неверный пункт меню. Попробуйте снова.")

if __name__ == "__main__":
    main()