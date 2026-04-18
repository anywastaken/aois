


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
        else: 
            self.rows, self.cols = 4, 4
            self.row_vars, self.col_vars = 2, 2
            
        self.grid_indices = self._generate_grid_indices()

    def _generate_grid_indices(self):
    
        """Генерация индексов"""

        gray_map = {1: [0, 1], 2: [0, 1, 3, 2]}
        
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
        print(f"\n{'='*20}")
        print(f" КАРТА КАРНО ({mode})")
        print(f" Цель: группы по {target}")
        print(f"{'='*20}")
        
        col_vars_names = "".join(self.variables[:self.col_vars])
        row_vars_names = "".join(self.variables[self.col_vars:])
        
        gray_labels = {1: ["0", "1"], 2: ["00", "01", "11", "10"]}
        row_labels = gray_labels[self.row_vars]
        col_labels = gray_labels[self.col_vars]

        header = f" {row_vars_names:^4} \\ {col_vars_names:^4} | "
        for label in col_labels:
            header += f" {label:^3} |"
        print(header)
        print("-" * len(header))

        for r in range(self.rows):
            row_str = f"    {row_labels[r]:^4}    |"
            for c in range(self.cols):
                val = self.results[self.grid_indices[r][c]]
                
                display_val = f"[{val}]" if val == target else f" {val} "
                
                row_str += f"{display_val:^5}|"
            print(row_str)
        print("-" * len(header))

    def find_rectangles(self, target_value=1):

        """Поиск прямоугольников"""

        targets = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.results[self.grid_indices[r][c]] == target_value:
                    targets.append((r, c))
        
        if not targets: return []
        possible_h = [h for h in [4, 2, 1] if h <= self.rows]
        possible_w = [w for w in [4, 2, 1] if w <= self.cols]
        
        possible_shapes = sorted([(h, w) for h in possible_h for w in possible_w], 
                                 key=lambda x: x[0]*x[1], reverse=True)
        
        rectangles = []
        for h, w in possible_shapes:
            for r in range(self.rows):
                for c in range(self.cols):
                    current_rect = []
                    valid = True
                    for dr in range(h):
                        for dc in range(w):
                            nr, nc = (r + dr) % self.rows, (c + dc) % self.cols
                            if self.results[self.grid_indices[nr][nc]] != target_value:
                                valid = False
                                break
                            current_rect.append((nr, nc))
                        if not valid: break
                    
                    if valid:
                        s_rect = tuple(sorted(current_rect))
                        if s_rect not in rectangles:
                            rectangles.append(s_rect)
        
        return self.optimize_coverage(targets, rectangles)
    
    def optimize_coverage(self, targets, rectangles):

        """Алгоритм покрытия"""

        final_rects = []
        covered = set()
        targets_set = set(targets)

        while covered != targets_set:
            best_rect = max(rectangles, key=lambda res: len(set(res) - covered))
            final_rects.append(best_rect)
            covered.update(best_rect)
        return final_rects
    
    def rect_to_term(self, rect, mode="DNF"):

        """Перевод в читаемый вид"""

        gray_decode = {0: (0,0), 1: (0,1), 3: (1,1), 2: (1,0)}
        gray_decode_simple = {0: (0,), 1: (1,)}

        possible_vals = [set() for _ in range(self.num_vars)]
        
        rows_g = [0, 1, 3, 2] if self.row_vars == 2 else [0, 1]
        cols_g = [0, 1, 3, 2] if self.col_vars == 2 else [0, 1]

        for r, c in rect:
            r_bits = (gray_decode if self.row_vars == 2 else gray_decode_simple)[rows_g[r]]
            c_bits = (gray_decode if self.col_vars == 2 else gray_decode_simple)[cols_g[c]]
            
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