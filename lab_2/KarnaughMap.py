


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
        else:
            self.layers = 2
            self.rows, self.cols = 4, 4
            self.row_vars, self.col_vars, self.layer_vars = 2, 2, 1
            
        self.grid_indices = self._generate_grid_indices()

    def _generate_grid_indices(self):
    
        """Генерация индексов"""

        gray_map = {1: [0, 1], 2: [0, 1, 3, 2]}
        
        rows_g = gray_map[self.row_vars]
        cols_g = gray_map[self.col_vars]
        layers_g = gray_map[1] if self.num_vars == 5 else [0]
        
        grid_3d = []
        for l_val in layers_g:
            layer = []
            for r_val in rows_g:
                row = []
                for c_val in cols_g:
                    idx = (l_val << (self.row_vars + self.col_vars)) | (c_val << self.row_vars) | r_val
                    row.append(idx)
                layer.append(row)
            grid_3d.append(layer)
        return grid_3d

    def display(self, mode="DNF"):
        """Вывод таблицы Карно для 2, 3, 4 и 5 переменных."""
        target = 1 if mode == "DNF" else 0
        print(f"\n{'='*30}")
        print(f" КАРТА КАРНО ({mode})")
        print(f" Цель: группы по {target}")
        print(f"{'='*30}")
        
        col_vars_names = "".join(self.variables[:self.col_vars])
        if self.num_vars == 5:
            row_vars_names = "".join(self.variables[self.col_vars:self.col_vars+self.row_vars])
            layer_var_name = self.variables[-1]
        else:
            row_vars_names = "".join(self.variables[self.col_vars:])
            layer_var_name = ""

        gray_labels = {1: ["0", "1"], 2: ["00", "01", "11", "10"]}
        row_labels = gray_labels[self.row_vars]
        col_labels = gray_labels[self.col_vars]
        layer_labels = ["0", "1"] if self.num_vars == 5 else [""]

        for l_idx, l_val in enumerate(layer_labels):
            if self.num_vars == 5:
                print(f"\nСЛОЙ {layer_var_name} = {l_val}")
                print("-" * 20)

            header = f" {row_vars_names:^4} \\ {col_vars_names:^4} | "
            for label in col_labels:
                header += f" {label:^5} |"
            print(header)
            print("-" * len(header))

            for r in range(self.rows):
                row_str = f"    {row_labels[r]:^4}    |"
                for c in range(self.cols):
                    if self.num_vars == 5:
                        idx = self.grid_indices[l_idx][r][c]
                    else:
                        idx = self.grid_indices[0][r][c]
                    
                    val = self.results[idx]
                    
                    display_val = f"[{val}]" if val == target else f" {val} "
                    row_str += f"{display_val:^7}|"
                print(row_str)
            print("-" * len(header))
            
    def find_rectangles(self, target_value=1):

        """Поиск прямоугольников"""

        targets = []
        for l in range(len(self.grid_indices)):
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.results[self.grid_indices[l][r][c]] == target_value:
                        targets.append((l, r, c))
        
        if not targets: return []

        possible_l = [2, 1] if self.num_vars == 5 else [1]
        possible_h = [4, 2, 1]
        possible_w = [4, 2, 1]
        
        shapes = sorted([(l, h, w) for l in possible_l for h in possible_h for w in possible_w 
                         if h <= self.rows and w <= self.cols], 
                        key=lambda x: x[0]*x[1]*x[2], reverse=True)

        rectangles = []
        for dl, dh, dw in shapes:
            for l in range(len(self.grid_indices)):
                for r in range(self.rows):
                    for c in range(self.cols):
                        current_rect = []
                        valid = True
                        for il in range(dl):
                            for ir in range(dh):
                                for ic in range(dw):
                                    nl = (l + il) % len(self.grid_indices)
                                    nr = (r + ir) % self.rows
                                    nc = (c + ic) % self.cols
                                    if self.results[self.grid_indices[nl][nr][nc]] != target_value:
                                        valid = False; break
                                if not valid: break
                            if not valid: break
                        
                        if valid:
                            s_rect = tuple(sorted(current_rect))
                            if s_rect not in rectangles: rectangles.append(s_rect)
        
        return self.optimize_coverage(targets, rectangles)
        
    def optimize_coverage(self, targets, rectangles):

        """Алгоритм покрытия"""

        final_rects = []
        covered = set()
        targets_set = set(targets)
        
        remaining_targets = targets_set.copy()

        while remaining_targets:
            best_rect = None
            max_new_cover = 0
            
            for rect in rectangles:
                new_cover = len(set(rect) & remaining_targets)
                if new_cover > max_new_cover:
                    max_new_cover = new_cover
                    best_rect = rect
            
            if best_rect is None or max_new_cover == 0:
                for lone_target in remaining_targets:
                    final_rects.append((lone_target,))
                break
                
            final_rects.append(best_rect)
            remaining_targets -= set(best_rect)
            
        return final_rects
    
    def rect_to_term(self, rect, mode="DNF"):
        
        """Перевод найденного прямоугольника в логическое выражение."""

        gray_decode = {
            0: (0, 0), 1: (0, 1), 3: (1, 1), 2: (1, 0)
        }
        gray_decode_simple = {
            0: (0,), 1: (1,)
        }

        possible_vals = [set() for _ in range(self.num_vars)]
        
        row_gray_codes = [0, 1, 3, 2] if self.row_vars == 2 else [0, 1]
        col_gray_codes = [0, 1, 3, 2] if self.col_vars == 2 else [0, 1]
        layer_gray_codes = [0, 1] if (self.num_vars == 5) else [0]

        for l, r, c in rect:
            c_bits = (gray_decode if self.col_vars == 2 else gray_decode_simple)[col_gray_codes[c]]
            
            r_bits = (gray_decode if self.row_vars == 2 else gray_decode_simple)[row_gray_codes[r]]
            
            l_bits = (l,) if self.num_vars == 5 else ()
            
            full_code = c_bits + r_bits + l_bits
            
            for i in range(self.num_vars):
                possible_vals[i].add(full_code[i])

        term_elements = []
        for i in range(self.num_vars):
            if len(possible_vals[i]) == 1:
                val = list(possible_vals[i])[0]
                var_name = self.variables[i]
                
                if mode == "DNF":
                    term_elements.append(var_name if val == 1 else f"!{var_name}")
                else:
                    term_elements.append(var_name if val == 0 else f"!{var_name}")
        
        separator = " & " if mode == "DNF" else " | "
        
        if not term_elements:
            return "1" if mode == "DNF" else "0"
            
        return f"({separator.join(term_elements)})"