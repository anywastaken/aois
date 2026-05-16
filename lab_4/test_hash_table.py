import pytest

from main import HashTable


# =====================================================
# Создание таблицы
# =====================================================

@pytest.fixture
def table():
    return HashTable(23)


# =====================================================
# Тест вычисления V
# =====================================================

def test_get_value(table):

    # Ю = 31
    # Р = 16

    expected = 31 * 33 + 17

    assert table.get_value("Юрий") == expected


# =====================================================
# Тест hash_function
# =====================================================

def test_hash_function(table):

    value = 1039

    assert table.hash_function(value) == value % 23


# =====================================================
# Тест вставки
# =====================================================

def test_insert(table):

    table.insert("Юрий", "Студент")

    found = False

    for cell in table.table:

        if cell.key == "Юрий":
            found = True
            assert cell.data == "Студент"
            assert cell.U == 1
            assert cell.D == 0

    assert found


# =====================================================
# Тест поиска существующего элемента
# =====================================================

def test_search_existing(table, capsys):

    table.insert("Юрий", "Студент")

    table.search("Юрий")

    captured = capsys.readouterr()

    assert "Элемент найден" in captured.out
    assert "Юрий" in captured.out


# =====================================================
# Тест поиска отсутствующего элемента
# =====================================================

def test_search_not_existing(table, capsys):

    table.search("Андрей")

    captured = capsys.readouterr()

    assert "Элемент не найден" in captured.out


# =====================================================
# Тест удаления
# =====================================================

def test_delete(table):

    table.insert("Юрий", "Студент")

    table.delete("Юрий")

    deleted = False

    for cell in table.table:

        if cell.key == "Юрий":

            deleted = True

            assert cell.D == 1
            assert cell.U == 0

    assert deleted


# =====================================================
# Тест удаления отсутствующего элемента
# =====================================================

def test_delete_not_existing(table, capsys):

    table.delete("НеСуществует")

    captured = capsys.readouterr()

    assert "Элемент не найден" in captured.out


# =====================================================
# Тест коэффициента заполнения
# =====================================================

def test_load_factor(table):

    table.insert("Юрий", "1")
    table.insert("Анна", "2")

    expected = 2 / 23

    assert table.load_factor() == expected


# =====================================================
# Тест коллизии
# =====================================================

def test_collision():

    table = HashTable(5)

    table.insert("АБ", "1")
    table.insert("ЕЁ", "2")

    collision_found = False

    for cell in table.table:

        if cell.key == "ЕЁ":

            collision_found = True

            assert cell.C == 1

    assert collision_found

# =====================================================
# Тест дубликатов
# =====================================================

def test_duplicate_key(table, capsys):

    table.insert("Юрий", "1")
    table.insert("Юрий", "2")

    captured = capsys.readouterr()

    assert "уже существует" in captured.out


# =====================================================
# Тест короткого ключа
# =====================================================

def test_short_key(table):

    assert table.get_value("А") == -1


# =====================================================
# Тест print_table
# =====================================================

def test_print_table(table, capsys):

    table.insert("Юрий", "Студент")

    table.print_table()

    captured = capsys.readouterr()

    assert "HASH TABLE" in captured.out
    assert "Юрий" in captured.out


# =====================================================
# Тест переполнения
# =====================================================

def test_table_overflow(table, capsys):

    keys = [
        "АА", "АБ", "АВ", "АГ", "АД",
        "АЕ", "АЁ", "АЖ", "АЗ", "АИ",
        "АЙ", "АК", "АЛ", "АМ", "АН",
        "АО", "АП", "АР", "АС", "АТ",
        "АУ", "АФ", "АХ"
    ]

    for i in range(23):
        table.insert(keys[i], str(i))

    table.insert("Переполнение", "XXX")

    captured = capsys.readouterr()

    assert "переполнена" in captured.out.lower()

from main import run_menu


def test_menu_exit(monkeypatch, capsys):

    inputs = iter(["0"])

    monkeypatch.setattr("builtins.input",
                        lambda _: next(inputs))

    run_menu()

    captured = capsys.readouterr()

    assert "Выход из программы" in captured.out