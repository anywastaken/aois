

class Minimize:

    def find_difference(self, first_tuple, second_tuple):

        """Считает количество несовпадающих разрядов между двумя термами"""

        n = len(first_tuple)
        count = 0
        for i in range(0, n):
            if first_tuple[i] != second_tuple[i]:
                count += 1

        return count
    
    def merge(self, first_tuple, second_tuple):

        """Выполняет операцию склеивания двух термов."""

        n = len(first_tuple)
        result = []
        for i in range(0, n):
            if first_tuple[i] == second_tuple[i]:
                result.append(first_tuple[i])
            else:
                result.append(None)
        
        return tuple(result)
    
    def get_all_combinations(self, term):
        
        """Превращает терм вида (1, None, 0) в список наборов: [(1, 0, 0), (1, 1, 0)]"""
        
        combinations = [term]

        for i in range(len(term)):
            new_combinations = []
            for combo in combinations:
                if combo[i] is None:
                    combo_0 = list(combo)
                    combo_0[i] = 0
                    new_combinations.append(tuple(combo_0))
                    
                    combo_1 = list(combo)
                    combo_1[i] = 1
                    new_combinations.append(tuple(combo_1))
                else:
                    new_combinations.append(combo)
            combinations = new_combinations

        return combinations
    
    def matches(self, combo, other_term):
        
        """Проверяет, входит ли конкретная точка в область, которую покрывает импликанта."""
        
        for i in range(len(combo)):
            if other_term[i] is not None:
                if other_term[i] != combo[i]:
                    return False 
                    
        return True
    
    def is_covered(self, term, others):

        """Определяет, является ли проверяемый терм избыточным."""

        term_combinations = self.get_all_combinations(term)
        
        for combo in term_combinations:
            covered_by_other = False
            for other_term in others:
                if self.matches(combo, other_term):
                    covered_by_other = True
                    break
            
            if not covered_by_other:
                return False
                
        return True
                
    def minimize_calculation(self, terms, mode):
        
        """Минимизация СДНФ рассчетным методом"""
        
        current_level = terms
        all_simple_implicants = set()
        
        while True:
            next_level = set()
            used = set()
            
            for i in range(len(current_level)):
                for j in range(i + 1, len(current_level)):
                    diff_count = self.find_difference(current_level[i], current_level[j])
                    if diff_count == 1: 
                        next_level.add(self.merge(current_level[i], current_level[j]))
                        used.add(current_level[i])
                        used.add(current_level[j])
            
            for t in current_level:
                if t not in used:
                    all_simple_implicants.add(t)
            
            if not next_level: break
            current_level = list(next_level)

        final_form = list(all_simple_implicants)
        if mode == "SKNF":
            print(self.print_minimized_sknf(final_form))
        elif mode == "SDNF":
            print(self.print_minimized_sdnf(final_form))

        for term in final_form[:]:
            others = [t for t in final_form if t != term]
            if self.is_covered(term, others):
                final_form.remove(term)
                
        return final_form
    
    def print_minimized_sdnf(self, sdnf):

        """Преобразование в читаемую строку"""

        sdnf_parts = []
        for i in range(len(sdnf)):
            konjunkt = "("
            for j in range(len(self.variables)):
                if sdnf[i][j] == 1:
                    konjunkt += f"{self.variables[j]}"
                elif sdnf[i][j] == 0:
                    konjunkt += f"!{self.variables[j]}"
            konjunkt+=")"
            sdnf_parts.append(konjunkt)
        return "|".join(sdnf_parts)
    
    def print_minimized_sknf(self, sknf):

        """Преобразование в читаемую строку"""

        sknf_parts = []
        for i in range(len(sknf)):
            disjunkt = []
            for j in range(len(self.variables)):
                if sknf[i][j] == 1:
                    disjunkt.append(f"{self.variables[j]}")
                elif sknf[i][j] == 0:
                    disjunkt.append(f"!{self.variables[j]}")
            disjunkt = "&".join(disjunkt)
            sknf_parts.append(f"({disjunkt})")
        return "".join(sknf_parts)
    
    def minimize_calculation_table(self, terms, mode):
        
        """Минимизация расчетно-табличным методом """

        current_level = terms
        all_simple_implicants = set()
        
        while True:
            next_level = set()
            used = set()
            
            for i in range(len(current_level)):
                for j in range(i + 1, len(current_level)):
                    if self.find_difference(current_level[i], current_level[j]) == 1: 
                        next_level.add(self.merge(current_level[i], current_level[j]))
                        used.add(current_level[i])
                        used.add(current_level[j])
            
            for t in current_level:
                if t not in used:
                    all_simple_implicants.add(t)
            
            if not next_level: 
                break
            current_level = list(next_level)

        simple_implicants = list(all_simple_implicants)
        
        table = []
        for imp in simple_implicants:
            row = [self.matches(term, imp) for term in terms]
            table.append(row)

        self.display_implicant_table(simple_implicants, terms, table)

        final_form = set()
        covered_terms = [False] * len(terms)

        for col in range(len(terms)):
            count = 0
            last_imp_idx = -1
            for row in range(len(simple_implicants)):
                if table[row][col]:
                    count += 1
                    last_imp_idx = row
            
            if count == 1:
                final_form.add(simple_implicants[last_imp_idx])
                for c in range(len(terms)):
                    if table[last_imp_idx][c]:
                        covered_terms[c] = True

        while not all(covered_terms):
            best_imp = None
            max_new_cover = 0
            
            for i, imp in enumerate(simple_implicants):
                if imp in final_form: continue
                
                current_cover = sum(1 for col in range(len(terms)) if table[i][col] and not covered_terms[col])
                
                if current_cover > max_new_cover:
                    max_new_cover = current_cover
                    best_imp = imp
            
            if best_imp:
                final_form.add(best_imp)
                idx = simple_implicants.index(best_imp)
                for c in range(len(terms)):
                    if table[idx][c]:
                        covered_terms[c] = True
            else:
                break

        result_list = list(final_form)
        
        if mode == "SKNF":
            print("Минимизированная МКНФ:", self.print_minimized_sknf(result_list))
        else:
            print("Минимизированная МДНФ:", self.print_minimized_sdnf(result_list))
                
        return result_list
    
    def display_implicant_table(self, implicants, terms, table):

        """Вспомошательный метод для вывода таблицы"""

        print("\n" + "="*30)
        print("   ИМПЛИКАНТНАЯ ТАБЛИЦА")
        print("="*30)

        imp_col_width = max(len(str(imp)) for imp in implicants) if implicants else 10
        imp_col_width = max(imp_col_width, 10)

        term_headers = [f"T{i}" for i in range(len(terms))]
        col_width = 5 

        header = f"{'Implicant':<{imp_col_width}} |"
        for h in term_headers:
            header += f"{h:^{col_width}}|"
        
        print(header)
        print("-" * len(header))

        for i, imp in enumerate(implicants):
            row_str = f"{str(imp):<{imp_col_width}} |"
            for val in table[i]:
                mark = "  X  " if val else "     "
                row_str += f"{mark:^{col_width}}|"
            print(row_str)
        
        print("-" * len(header))