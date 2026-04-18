

class SDNF_SKNF:

    def get_sknf(self, table_data):
        
        """Строит СКНФ в обычном текстовом виде на основе таблицы истинности."""
        
        sknf_parts = []
        
        for row in table_data:
            if row['result'] == 0:
                disjunct = []
                for variable in self.variables:
                    value = row[variable]
                    if value == 0:
                        disjunct.append(variable)
                    else:
                        disjunct.append(f"!{variable}")
                
                sknf_parts.append(f"({'|'.join(disjunct)})")
        
        return "".join(sknf_parts)
    
    def get_sknf_without_vars(self, table_data):
        
        """Строит СКНФ в виде списка картежей на основе таблицы истинности."""
        
        sknf_parts = []
        
        for row in table_data:
            if row['result'] == 0:
                konjunct = ()
                for variable in self.variables:
                    value = row[variable]
                    if value == 0:
                        konjunct+=(1,)
                    else:
                        konjunct+=(0,)
                sknf_parts.append(konjunct)
        
        return sknf_parts
    
    def get_sdnf(self, table_data):

        """Строит СDНФ в обычном текстовом виде на основе таблицы истинности."""
        
        sdnf_parts = []
        
        for row in table_data:
            if row['result'] == 1:
                disjunct = ''
                for variable in self.variables:
                    value = row[variable]
                    if value == 1:
                        disjunct += variable
                    else:
                        disjunct += f"!{variable}"
                
                sdnf_parts.append(f"({disjunct})")
        
        return "&".join(sdnf_parts)
    
    def get_sdnf_without_vars(self, table_data):
        
        """Строит СDНФ в виде списка картежей на основе таблицы истинности."""
        
        sdnf_parts = []
        
        for row in table_data:
            if row['result'] == 1:
                disjunct = ()
                for variable in self.variables:
                    value = row[variable]
                    if value == 1:
                        disjunct+=(1,)
                    else:
                        disjunct += (0,)
                
                sdnf_parts.append(disjunct)
        
        return sdnf_parts


    def get_numeric_sknf(self, table_data):
        
        """Возвращает числовую форму СКНФ"""

        indices = []
        
        for index, row in enumerate(table_data):
            if row['result'] == 0:
                indices.append(index)
        
        if not indices:
            return "СКНФ отсутствует (функция — константа 1)"
            
        return f"&({', '.join(map(str, indices))})"
    
    def get_numeric_sdnf(self, table_data):
        
        """Возвращает числовую форму СДНФ."""

        indices = []
        
        for index, row in enumerate(table_data):
            if row['result'] == 1:
                indices.append(index)
        
        if not indices:
            return "СКНФ отсутствует (функция — константа 1)"
            
        return f"|({', '.join(map(str, indices))})"