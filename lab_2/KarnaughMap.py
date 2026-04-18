from itertools import product

class KarnaughMap:
    def __init__(self, results, variables):
        self.results = results
        self.variables = variables
        self.num_vars = len(variables)
        
        if self.num_vars == 2:
            self.rows, self.cols = 2, 2
            self.row_vars, self.col_vars = 1, 1 
        elif self.num_vars == 3:
            self.rows, self.cols = 2, 4
            self.row_vars, self.col_vars = 1, 2
        elif self.num_vars == 4: 
            self.rows, self.cols = 4, 4
            self.row_vars, self.col_vars = 2, 2
        elif self.num_vars == 5:
            self.rows, self.cols = 4, 8
            self.row_vars, self.col_vars = 2, 3
        else:
            raise ValueError("Поддерживается от 2 до 5 переменных.")
            
        self.grid_indices = self._generate_grid_indices()

    def _generate_grid_indices(self):
        """Генерация индексов с поддержкой 3-битного кода Грея"""
        gray_map = {
            1: [0, 1], 
            2: [0, 1, 3, 2],
            3: [0, 1, 3, 2, 6, 7, 5, 4] 
        }
        
        rows_g = gray_map[self.row_vars]
        cols_g = gray_map[self.col_vars]
        
        grid = []
        for r_val in rows_g:
            row = []
            for c_val in cols_g:
                idx = (c_val << self.row_vars) | r_val
                row.append(idx)
            grid.append(row)
        return grid

    def display(self, mode="DNF"):
        """Вывод таблицы"""
        target = 1 if mode == "DNF" else 0
        print(f"\n{'='*25}")
        print(f" КАРТА КАРНО ({mode})")
        print(f" Цель: группы по {target}")
        print(f"{'='*25}")
        
        col_vars_names = "".join(self.variables[:self.col_vars])
        row_vars_names = "".join(self.variables[self.col_vars:])
        
        gray_labels = {
            1: ["0", "1"], 
            2: ["00", "01", "11", "10"],
            3: ["000", "001", "011", "010", "110", "111", "101", "100"]
        }
        row_labels = gray_labels[self.row_vars]
        col_labels = gray_labels[self.col_vars]

        header = f" {row_vars_names:^4} \\ {col_vars_names:^5} | "
        for label in col_labels:
            header += f" {label:^3} |"
        print(header)
        print("-" * len(header))

        for r in range(self.rows):
            row_str = f"    {row_labels[r]:^4}     |"
            for c in range(self.cols):
                val = self.results[self.grid_indices[r][c]]
                display_val = f"[{val}]" if val == target else f" {val} "
                row_str += f"{display_val:^5}|"
            print(row_str)
        print("-" * len(header))

    def find_rectangles(self, target_value=1):
        """Поиск логических субкубов (заменяет геометрический поиск для поддержки 5 переменных)"""
        targets = []
        idx_to_rc = {}
        for r in range(self.rows):
            for c in range(self.cols):
                idx = self.grid_indices[r][c]
                idx_to_rc[idx] = (r, c)
                if self.results[idx] == target_value:
                    targets.append((r, c))
        
        if not targets: return []
        
        rectangles = []
        
        for mask in product(['0', '1', '-'], repeat=self.num_vars):
            minterms = []
            valid = True
            def get_minterms(m_idx, current_val):
                if m_idx == self.num_vars:
                    minterms.append(current_val)
                    return
                if mask[m_idx] == '-':
                    get_minterms(m_idx + 1, current_val)
                    get_minterms(m_idx + 1, current_val | (1 << (self.num_vars - 1 - m_idx)))
                else:
                    if mask[m_idx] == '1':
                        current_val |= (1 << (self.num_vars - 1 - m_idx))
                    get_minterms(m_idx + 1, current_val)
                    
            get_minterms(0, 0)
            
            current_rect = []
            for m in minterms:
                if self.results[m] != target_value:
                    valid = False
                    break
                current_rect.append(idx_to_rc[m])
                
            if valid and current_rect:
                rectangles.append(tuple(sorted(current_rect)))
        
        rectangles = list(set(rectangles))
        rectangles.sort(key=len, reverse=True)
        
        return self.optimize_coverage(targets, rectangles)
    
    def optimize_coverage(self, targets, rectangles):
        """Алгоритм покрытия (оставлен без изменений)"""
        final_rects = []
        covered = set()
        targets_set = set(targets)

        while covered != targets_set:
            best_rect = max(rectangles, key=lambda res: len(set(res) - covered))
            final_rects.append(best_rect)
            covered.update(best_rect)
        return final_rects
    
    def rect_to_term(self, rect, mode="DNF"):
        """Перевод в читаемый вид с динамическим определением порядка"""
        gray_decode = {
            1: {0: (0,), 1: (1,)},
            2: {0: (0,0), 1: (0,1), 3: (1,1), 2: (1,0)},
            3: {0: (0,0,0), 1: (0,0,1), 3: (0,1,1), 2: (0,1,0), 
                6: (1,1,0), 7: (1,1,1), 5: (1,0,1), 4: (1,0,0)}
        }
        
        gray_seq = {
            1: [0, 1],
            2: [0, 1, 3, 2],
            3: [0, 1, 3, 2, 6, 7, 5, 4]
        }

        possible_vals = [set() for _ in range(self.num_vars)]
        
        rows_g = gray_seq[self.row_vars]
        cols_g = gray_seq[self.col_vars]

        for r, c in rect:
            r_bits = gray_decode[self.row_vars][rows_g[r]]
            c_bits = gray_decode[self.col_vars][cols_g[c]]
            
            full_code = c_bits + r_bits 
            
            for i in range(self.num_vars):
                possible_vals[i].add(full_code[i])

        term = []
        for i in range(self.num_vars):
            if len(possible_vals[i]) == 1:
                val = list(possible_vals[i])[0]
                var = self.variables[i]
                if mode == "DNF":
                    term.append(var if val == 1 else f"!{var}")
                else:
                    term.append(var if val == 0 else f"!{var}")
        
        sep = " & " if mode == "DNF" else " | "
        return f"({sep.join(term)})"