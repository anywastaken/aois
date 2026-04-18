

class ZhegalkinPolynomial:


    def _get_coefficients(self, table_data):
        
        """Получение коэффициентов полинома Жигалкина"""

        values = [row['result'] for row in table_data]
        
        coefficients = [values[0]] 
        current_column = values
        
        for i in range(1, len(values)):
            next_column = []
            for j in range(len(current_column) - 1):
                next_column.append(current_column[j] ^ current_column[j+1])
            
            coefficients.append(next_column[0])
            current_column = next_column
        return coefficients
    

    def get_zhegalkin_polynomial(self, table_data):
        
        """Построение полинома Жегалкина методом треугольника"""
        
        coefficients = self._get_coefficients(table_data)
        polynomial = f"{coefficients[0]}"

        for i in range(1, len(coefficients)):
            polynomial += f" ^ {coefficients[i]}"
            for var in self.variables:
                if table_data[i][var] == 1:
                    polynomial += var
        
        return polynomial


    def find_dummy_variables(self, table_data):

        """Поиск фиктивных переменных"""

        coefficients = self._get_coefficients(table_data)
        dummy_vars:list = self.variables.copy()

        for i in range(1, len(coefficients)):
            if coefficients[i] == 1:
                for var in self.variables:
                    if table_data[i][var] == 1 and var in dummy_vars: 
                        dummy_vars.remove(var)
        
        return dummy_vars
    

    def linearity(self, table_data):

        """Проверка на линейность"""

        coefficients = self._get_coefficients(table_data)

        for i in range(1, len(coefficients)):
            if coefficients[i] == 1:
                vars_in_term = 0
                for var in self.variables:
                    if table_data[i][var] == 1:
                        vars_in_term += 1
                if vars_in_term > 1:
                    return False
                    
        return True
    

    def preserving_zero(self, table_data):

        """Проверка на сохранение нуля"""

        return not bool(table_data[0]['result'])
    

    def preserving_one(self, table_data):

        """Проверка на сохранение еденицы"""

        return bool(table_data[-1]['result'])
    

    def self_duality(self, table_data):

        """Проверка на самодвойственность"""

        n = len(table_data)
        for i in range(n // 2):
            if table_data[i]['result'] == table_data[n - 1 - i]['result']:
                return False
        return True
    

    def monotonicity(self, table_data):

        """Проверка на монотонность"""

        n_rows = len(table_data)
        for i in range(n_rows):
            for j in range(n_rows):
                is_smaller_or_equal = True
                for var in self.variables:
                    if table_data[i][var] > table_data[j][var]:
                        is_smaller_or_equal = False
                        break

                if is_smaller_or_equal:
                    if table_data[i]['result'] > table_data[j]['result']:
                        return False 
        return True