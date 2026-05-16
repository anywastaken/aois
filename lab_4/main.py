class HashEntry:

    def __init__(self):

        self.key = ""
        self.data = ""

        self.C = 0
        self.U = 0
        self.T = 0
        self.L = 0
        self.D = 0


class HashTable:

    def __init__(self, size=23):

        self.SIZE = size
        self.table = [HashEntry() for _ in range(size)]

    # ==========================================
    # Вычисление V
    # ==========================================
    def get_value(self, key):

        alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

        key = key.lower()

        if len(key) < 2:
            return -1

        first = alphabet.index(key[0])
        second = alphabet.index(key[1])

        value = first * 33 + second

        return value

    # ==========================================
    # Хеш-функция
    # ==========================================
    def hash_function(self, value):

        return value % self.SIZE

    # ==========================================
    # Добавление
    # ==========================================
    def insert(self, key, data):

        V = self.get_value(key)
        h = self.hash_function(V)

        print(f"\nV = {V}")
        print(f"h = {h}")

        collision = False

        for i in range(self.SIZE):

            index = (h + i * i) % self.SIZE

            cell = self.table[index]

            # Проверка дубликатов
            if cell.U == 1 and cell.D == 0 and cell.key == key:

                print("Такой ключ уже существует!")
                return

            # Свободная ячейка
            if cell.U == 0 or cell.D == 1:

                cell.key = key
                cell.data = data

                cell.U = 1
                cell.D = 0
                cell.T = 1

                if collision:
                    cell.C = 1

                print(f"Запись добавлена в ячейку {index}")

                return

            collision = True

        print("Таблица переполнена!")

    # ==========================================
    # Поиск
    # ==========================================
    def search(self, key):

        V = self.get_value(key)
        h = self.hash_function(V)

        for i in range(self.SIZE):

            index = (h + i * i) % self.SIZE

            cell = self.table[index]

            if cell.U == 0 and cell.D == 0:
                break

            if cell.key == key and cell.D == 0:

                print("\nЭлемент найден")
                print(f"Ячейка: {index}")
                print(f"Ключ: {cell.key}")
                print(f"Данные: {cell.data}")

                return

        print("Элемент не найден!")

    # ==========================================
    # Удаление
    # ==========================================
    def delete(self, key):

        V = self.get_value(key)
        h = self.hash_function(V)

        for i in range(self.SIZE):

            index = (h + i * i) % self.SIZE

            cell = self.table[index]

            if cell.U == 0 and cell.D == 0:
                break

            if cell.key == key and cell.D == 0:

                cell.D = 1
                cell.U = 0

                print("Запись удалена")

                return

        print("Элемент не найден!")

    # ==========================================
    # Коэффициент заполнения
    # ==========================================
    def load_factor(self):

        count = 0

        for cell in self.table:

            if cell.U == 1 and cell.D == 0:
                count += 1

        return count / self.SIZE

    # ==========================================
    # Вывод таблицы
    # ==========================================
    def print_table(self):

        print("\n================ HASH TABLE ================\n")

        print(
            f"{'№':<4}"
            f"{'KEY':<15}"
            f"{'DATA':<20}"
            f"{'C':<4}"
            f"{'U':<4}"
            f"{'T':<4}"
            f"{'L':<4}"
            f"{'D':<4}"
        )

        print("-" * 70)

        for i, cell in enumerate(self.table):

            if cell.U == 1 and cell.D == 0:

                print(
                    f"{i:<4}"
                    f"{cell.key:<15}"
                    f"{cell.data:<20}"
                    f"{cell.C:<4}"
                    f"{cell.U:<4}"
                    f"{cell.T:<4}"
                    f"{cell.L:<4}"
                    f"{cell.D:<4}"
                )

            elif cell.D == 1:

                print(
                    f"{i:<4}"
                    f"{'DELETED':<15}"
                    f"{'-':<20}"
                    f"{cell.C:<4}"
                    f"{cell.U:<4}"
                    f"{cell.T:<4}"
                    f"{cell.L:<4}"
                    f"{cell.D:<4}"
                )

            else:

                print(
                    f"{i:<4}"
                    f"{'-':<15}"
                    f"{'-':<20}"
                    f"0   0   0   0   0"
                )

        print("\nКоэффициент заполнения:",
              round(self.load_factor(), 2))


# =====================================================
# МЕНЮ
# =====================================================
def run_menu():
    ht = HashTable()

    while True:

        print("\n========== МЕНЮ ==========")
        print("1. Добавить запись")
        print("2. Найти запись")
        print("3. Удалить запись")
        print("4. Показать таблицу")
        print("5. Коэффициент заполнения")
        print("0. Выход")

        choice = input("\nВыберите пункт: ")

        # -------------------------------------

        if choice == "1":

            key = input("Введите ключ: ")
            data = input("Введите данные: ")

            ht.insert(key, data)

        # -------------------------------------

        elif choice == "2":

            key = input("Введите ключ для поиска: ")

            ht.search(key)

        # -------------------------------------

        elif choice == "3":

            key = input("Введите ключ для удаления: ")

            ht.delete(key)

        # -------------------------------------

        elif choice == "4":

            ht.print_table()

        # -------------------------------------

        elif choice == "5":

            print("\nКоэффициент заполнения:",
                round(ht.load_factor(), 2))

        # -------------------------------------

        elif choice == "0":

            print("Выход из программы")
            break

        # -------------------------------------

        else:

            print("Неверный пункт меню!")

if __name__=="__main__":
    run_menu()
