import itertools
import re

from SDNF_SKNF import SDNF_SKNF
from ZhegalkinPolynomial import ZhegalkinPolynomial
from Minimize import Minimize


class LogicExpression(SDNF_SKNF, ZhegalkinPolynomial, Minimize):
    def __init__(self, expression: str):
        self.raw_expression = expression.replace(" ", "")
        self.variables = sorted(list(set(re.findall(r'[a-e]', self.raw_expression))))
        
        self.operators = {
            '!': (4, 'R'),  
            '&': (3, 'L'),  
            '^': (3, 'L'),  
            '|': (2, 'L'),  
            '->': (1, 'L'), 
            '~': (1, 'L')   
        }
        
        if not self._is_valid(self.raw_expression):
            raise ValueError(f"Выражение '{expression}' содержит ошибки или недопустимые символы.")
            
        self.tokens = self._tokenize(self.raw_expression)
        self.rpn = self._to_rpn(self.tokens)

    def _tokenize(self, expr):

        """Разбивает строку на токены (переменные, операторы, скобки)."""

        return re.findall(r'[a-e]|->|[!&|~^()]', expr)

    def _to_rpn(self, tokens):

        """Преобразует инфиксную запись в обратную польскую нотацию."""

        output = []
        stack = []
        
        for token in tokens:
            if token in self.variables:
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            elif token in self.operators:
                p1, assoc1 = self.operators[token]
                while stack and stack[-1] in self.operators:
                    p2, _ = self.operators[stack[-1]]
                    if (assoc1 == 'L' and p1 <= p2) or (assoc1 == 'R' and p1 < p2):
                        output.append(stack.pop())
                    else:
                        break
                stack.append(token)
        while stack:
            output.append(stack.pop())
        return output

    def _evaluate(self, values):

        """Вычисляет значение выражения по ОПН для конкретного набора переменных."""

        stack = []
        for token in self.rpn:
            if token in self.variables:
                stack.append(values[token])
            elif token == '!':
                stack.append(int(not stack.pop()))
            else:
                b = stack.pop()
                a = stack.pop()
                if token == '&': stack.append(a & b)
                elif token == '|': stack.append(a | b)
                elif token == '^': stack.append(a ^ b)
                elif token == '~': stack.append(int(a == b))
                elif token == '->': stack.append(int(a <= b))
        return stack[0]

    def _is_valid(self, expr: bool) -> bool:

        """Проверка строки на корректность"""

        if not expr:
            return False
        
        temp_expr = expr.replace("->", ">")
        if not re.fullmatch(r'[a-e!&|~^()>\s]+', temp_expr):
            return False

        stack = []
        for char in expr:
            if char == '(': stack.append(char)
            elif char == ')':
                if not stack: return False
                stack.pop()
        if stack or "()" in expr:
            return False

        try:
            tokens = self._tokenize(expr)
            self._to_rpn(tokens)
        except Exception:
            return False
        return True

    def generate_truth_table(self):

        """Строит таблицу истинности"""
        
        table = []
        n = len(self.variables)
        combinations = list(itertools.product([0, 1], repeat=n))
        
        header = " | ".join(self.variables) + " | F"
        print(header)
        print("-" * len(header))

        for combo in combinations:
            values = dict(zip(self.variables, combo))
            try:
                result = self._evaluate(values)
                
                row = values.copy()
                row['result'] = result
                table.append(row)
                
                formatted_vals = " | ".join(map(str, combo))
                print(f"{formatted_vals} | {result}")
            except Exception as e:
                print(f"Ошибка вычисления на наборе {values}: {e}")
        
        return table

    def get_index_form(self, table_data):
        
        """Возвращает индексную форму функции (десятичное число)."""

        binary_index = "".join(str(row['result']) for row in table_data)
        
        decimal_index = int(binary_index, 2)
        
        return decimal_index
    
    def calculate_diff(self, current_values, variable):
        
        """Производная"""

        result = []
        
        var_index = self.variables.index(variable)
        step = 2 ** (len(self.variables) - 1 - var_index)
        
        for i in range(len(current_values)):
            
            pair_index = i ^ step
            
            res = current_values[i] ^ current_values[pair_index]
            result.append(res)
            
        return result