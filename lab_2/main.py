import itertools
from LogicExpression import LogicExpression
from KarnaughMap import KarnaughMap

def main():
    # Ввод логической функции
    expression_str = input("Введите логическую функцию: ")
    
    try:
        expr = LogicExpression(expression_str)
    except Exception as e:
        print(f"Ошибка при обработке выражения: {e}")
        return

    # 1. Таблица истинности
    print("\n1. Таблица истинности:")
    table_data = expr.generate_truth_table()

    # 2. СДНФ и СКНФ
    print("\n2. СДНФ и СКНФ:")
    print("СДНФ:", expr.get_sdnf(table_data))
    print("СКНФ:", expr.get_sknf(table_data))

    # 3. Числовая форма для СДНФ и СКНФ
    print("\n3. Числовая форма:")
    print("СДНФ (числовая):", expr.get_numeric_sdnf(table_data))
    print("СКНФ (числовая):", expr.get_numeric_sknf(table_data))

    # 4. Индексная форма функции
    print("\n4. Индексная форма функции:")
    print("Индекс (десятичный):", expr.get_index_form(table_data))

    # 5. Принадлежность к классам Поста
    print("\n5. Принадлежность к классам Поста:")
    print("Сохраняет 0 (T0):", expr.preserving_zero(table_data))
    print("Сохраняет 1 (T1):", expr.preserving_one(table_data))
    print("Самодвойственная (S):", expr.self_duality(table_data))
    print("Монотонная (M):", expr.monotonicity(table_data))
    print("Линейная (L):", expr.linearity(table_data))

    # 6. Полином Жегалкина
    print("\n6. Полином Жегалкина:")
    print("Полином:", expr.get_zhegalkin_polynomial(table_data))

    # 7. Поиск фиктивных переменных
    print("\n7. Поиск фиктивных переменных:")
    dummy_vars = expr.find_dummy_variables(table_data)
    print("Фиктивные переменные:", dummy_vars if dummy_vars else "Отсутствуют")

    # 8. Булева дифференциация (частные и смешанные производные)
    print("\n8. Булева дифференциация (до 4 переменных):")

    if(len(expr.variables)>4):
        print("\nБольше 4 переменных.")
    else:
        base_values = [row['result'] for row in table_data]
        vars_for_print = ""
        for var in expr.variables:
            vars_for_print += var
            base_values = expr.calculate_diff(base_values, var)
            print(f"\ndf/d{vars_for_print}: {base_values}")


    # Подготовка данных для минимизации
    terms_sdnf = expr.get_sdnf_without_vars(table_data)
    terms_sknf = expr.get_sknf_without_vars(table_data)

    # 9. Минимизация расчетным методом
    print("\n9. Минимизация функции расчетным методом:")
    print("--- Для ДНФ ---")
    if terms_sdnf:
        print(expr.print_minimized_sdnf(expr.minimize_calculation(terms_sdnf, "SDNF")))
    else:
        print("Функция тождественно равна 0, минимизация невозможна.")
        
    print("\n--- Для КНФ ---")
    if terms_sknf:
        print(expr.print_minimized_sknf(expr.minimize_calculation(terms_sknf, "SKNF")))
    else:
        print("Функция тождественно равна 1, минимизация невозможна.")

    # 10. Минимизация расчетно-табличным методом
    print("\n10. Минимизация расчетно-табличным методом:")
    print("--- Для ДНФ ---")
    if terms_sdnf:
        expr.minimize_calculation_table(terms_sdnf, "SDNF")
    else:
        print("Функция тождественно равна 0.")

    print("\n--- Для КНФ ---")
    if terms_sknf:
        expr.minimize_calculation_table(terms_sknf, "SKNF")
    else:
        print("Функция тождественно равна 1.")

    # 11. Минимизация табличным методом (Карта Карно)
    print("\n11. Минимизация табличным методом (Карта Карно):")
    results = [row['result'] for row in table_data]
    
    if len(expr.variables) in [2, 3, 4, 5]:
        kmap = KarnaughMap(results, expr.variables)
        
        # Для ДНФ
        kmap.display(mode="DNF")
        rects_dnf = kmap.find_rectangles(target_value=1)
        if rects_dnf:
            terms_dnf = [kmap.rect_to_term(r, mode="DNF") for r in rects_dnf]
            print("Минимизированная МДНФ (по Карте Карно):", " | ".join(terms_dnf))
        else:
            print("Минимизированная МДНФ: 0")

        # Для КНФ
        kmap.display(mode="KNF")
        rects_knf = kmap.find_rectangles(target_value=0)
        if rects_knf:
            terms_knf = [kmap.rect_to_term(r, mode="KNF") for r in rects_knf]
            print("Минимизированная МКНФ (по Карте Карно):", " & ".join(terms_knf))
        else:
            print("Минимизированная МКНФ: 1")
    else:
        print(f"Карта Карно не поддерживается для {len(expr.variables)} переменных (допустимо только 2, 3 или 4).")

if __name__ == "__main__":
    main()