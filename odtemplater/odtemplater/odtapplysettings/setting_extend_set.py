import re
from ..config import ConfigurationMyOdt
from . import MyOdtCheckerAnchor
from ..lib import ODTMeta


# logger = ConfigurationMyOdt.logger


class SettingExtendSet:
    """The class uses the option to multiply rows in document tables."""
    def __init__(self, text_xml: str, date: ODTMeta):
        self.text = text_xml
        self.date = date
        self.table = []  # Объявляем пустую переменную типа list

    @staticmethod
    def _chek_index_str_sequence(list_index: list) -> bool:
        """
        "ENG" Function for checking the sequence of numbers in a sheet.
        If each subsequent number is greater than one, it returns True, but if not, it returns False.

        "RUS":" Функция для проверки последовательности чисел в листе.
        Если каждое последующее число больше на единицу, то возвращается True, если же нет то False.
        """
        # Предыдущий индекс не сущетсвует.
        prev_index = None
        # Перебираем индексы.
        for i in list_index:
            # Если предыдущий индекс не существует
            if prev_index is None:
                # Приравниваем предыдущий индекс индексу из листа.
                prev_index = i
            # Если существует
            else:
                # Выполняем проверку на числовую последовательность.
                if (i - prev_index) == 1:
                    # Если число больше предыдущего на единицу, переписываем переменную предыдущего индекса на нынешний
                    prev_index = i
                # Если же число не последовательно возвращаем False
                else:
                    return False
        # Если все числа прошли проверку возвращаем True
        return True

    def _parsing_table(self) -> list:
        """
        "ENG" The function gets a list of tables and brings it to the form: [table 1, table 2, table 3...] where
        table[i] = [start, [row 1, row 2, row 3...], end].

        "RUS" Функция получает список таблиц и приводит его к виду: [table1, table2, table3...] где
        table[i] = [start, [row1, row2, row3...], end] Начало таблицы, список строк, конец таблицы.
        """
        try:
            # Перебираем список таблиц
            for table_select in range(len(self.table)):
                """
                Находим все от начала первой до конца последней строки в таблицах. Берем индекс [0], так как
                получаем список, с одним элементом.
                """
                table_row = re.findall(r'(<table:table-row.*</table:table-row>)', self.table[table_select])[0]
                # Добавляем разделитель между строками
                table_row = table_row.replace('</table:table-row>', '</table:table-row>↑')
                #  Разбиваем стринговую переменную содержащую строки по добавленному разделителю.
                table_row = table_row.split('↑')
                #  Так как разделитель добавляется и к окончанию всех строк, то убираем последний пустой элемент списка.
                table_row = table_row[:-1]
                #  Получаем начало таблицы до <table:table-row
                table_start = re.findall(r'<table:table table:name.+?<table:table-row', self.table[table_select])[
                    0].replace('<table:table-row', '')
                #  Получаем конец таблицы от последнего закрытого тега </table:table-row>
                table_end = self.table[table_select].replace(
                    re.findall(r'.*</table:table-row>', self.table[table_select])[0], '')
                #  Делаем лист содержащий в себе начало конец таблицы и список строк такблицы.
                #  temp_list = [var1, [var1, var2, ...], var3]
                temp_list = [table_start, table_row, table_end]
                #  Заменяем в списке таблиц выбранную таблицу на таблицу со списком строк.
                self.table[table_select] = temp_list
            return self.table
        except Exception:
            # logger.exception(u'setting_extend_set > SettingExtendSet > _parsing_table > Error')
            raise

    @staticmethod
    def _apply_numeric_anchor(row_table: str, group_name: str, number_replace: str) -> str:
        """
        "ENG" The function removes service information in the anchor in the form of the group name and the ~separator.
        And changes the saliva marker # for the sequence number passed to the function. As a result, it returns a
        string with numbered and cleared anchors.

        "RUS" Функция убирает в якоре служебную информацию в виде имени группы и разделителя ~. И меняет служебюный
        маркер # на порядковый номер переданный функции. Как результат возвращает строку с пронумерованными и
        очищенными якорями."""
        # Создаем список исходных якорей
        list_anchors = re.findall(r'\{\{' + group_name + '~.+?\}\}', row_table)
        # Создаем пустой список для новых якорей
        list_new_anchors = []
        # Проверяем наличие якорей в строке.
        if len(list_anchors) > 0:
            # Перебираем якоря
            for i in list_anchors:
                # Меняем в якоре служебную информацию на необходимые значения
                # {{GR1~TEXT#}} -> {{TEXT1}}
                anchors = i.replace(group_name + '~', '').replace('#', number_replace)
                # Добавляем измененный якорь в список
                list_new_anchors.append(anchors)
            # Убеждаемся что списки равны по колличеству элементов, если True
            if len(list_anchors) == len(list_new_anchors):
                # Перебираем индексы списка один (индексы элементов равны)
                for i in range(len(list_anchors)):
                    # Меняем исходный элемент в строке на измененный.
                    row_table = row_table.replace(list_anchors[i], list_new_anchors[i])
                # Возврощаем строку
                return row_table
            # Если длины списков не равны, то возвращаем ошибку.
            else:
                raise Exception('Lists are not equal!')

    @staticmethod
    def _search_group_apply_multiplying_strings(table_string: list, group_name: str, int_multiplier: int) -> list:
        """
        "ENG" The function searches for groups of anchors and strings. Calls the anchor numbering function,
        multiplies rows, and returns new, enlarged list of strings

        "RUS" Функция ищет групы якорей и строк. Вызывает функцию нумерации якоря, размножает строки, и возвращает
        новый, увеличенный список строк
        """
        temp_string_table = []
        index_str = []
        # Перебираем полученный список строк в таблицах
        for index_row_table in range(len(table_string)):
            # Если в строке есть якорь с именем группы то добавляем ее индекс в список.
            if re.search(r'\{\{' + group_name + '~.+?\}\}', table_string[index_row_table]):
                index_str.append(index_row_table)
        # Проверим список строк на размножение на возможную ошибку в виде не последовательно стоящих строк.
        check = SettingExtendSet._chek_index_str_sequence(index_str)
        if not check:
            raise Exception('The multiplication strings are inconsistent!')
        # Перебираем индексы входного листа строк и добавляем строки во временный список.
        check_multiplier = False
        for i in range(len(table_string)):
            # Если выбранный индекс отсутсвует в списке индексов строк для размножения
            if i not in index_str:
                # Добавляем строку по индексу во временный список.
                temp_string_table.append(table_string[i])
            # Если же строка есть в списке для размножения
            else:
                # Берем последовательно каждую строчку и прибавляем ее нужное колличество раз.
                if not check_multiplier:
                    for count_multiplier in range(int_multiplier):
                        for index_row in index_str:
                            temp_str = SettingExtendSet._apply_numeric_anchor(table_string[index_row], group_name,
                                                                              str(count_multiplier + 1))
                            temp_string_table.append(temp_str)
                            check_multiplier = True
        return temp_string_table

    def _apply_setting_table(self) -> list:
        """
        "ENG" The function applies options to table rows. .

        "RUS" Функция применяет опции к строкам таблиц.
        """
        try:
            # counter_options = 0
            for i in range(len(self.table)):  # table[0] = [var1, [var1, var2, ...], var3]
                table_get = self.table[i][1]  # Берем список строк из таблиц
                for extend_gr_name in self.date.extend_set_text:
                    gr_name = extend_gr_name['key_']
                    int_multiplier = int(self.date.options[0]['extend_set'][gr_name])
                    self.table[i][1] = self._search_group_apply_multiplying_strings(table_get, gr_name, int_multiplier)
            return self.table
        except Exception:
            # logger.exception(u'odt_engine > SettingExtendSet > apply_setting > Error')
            raise

    def _build_out_xml(self) -> str:
        """
        "ENG"The function collects table sheets back into XML text

        "RUS"Функция собирает листы таблиц, обратно в текст XML
        """
        for sp_i in range(len(self.table)):
            self.table[sp_i][1] = ''.join(self.table[sp_i][1])  # объединяем строки в таблицах
            self.table[sp_i] = ''.join(self.table[sp_i])  # объединяем началок строки и конец в таблице.
        # Замещаем сатрый текст на новый в XML
        for text_iter_table in range(len(re.findall(r'(<table:table table:name.+?</table:table>)', self.text))):
            self.text = self.text.replace(
                re.findall(r'(<table:table table:name.+?</table:table>)', self.text)[text_iter_table],
                self.table[text_iter_table])
        return self.text

    def apply_setting(self) -> str:
        """
        "ENG" The function applies all the methods of the class, and returns the result.

        "RUS" Функция применяет все  методы класса, и возвращает результат.
        """
        try:
            self.text = MyOdtCheckerAnchor.check_anchor_bag(self.text)  # Исключаем ошибки форматирования якорей
            #  Находим таблицы в тексте, получаем их список.
            self.table = re.findall(r'(<table:table table:name.+?</table:table>)', self.text)
            #  Парсим таблицу
            self.table = self._parsing_table()
            #  Применяем опции
            self.table = self._apply_setting_table()
            #  Упаковываем строки обратно в текст
            self.text = self._build_out_xml()
            return self.text
        except Exception:
            # logger.exception(u'odt_engine > SettingExtendSet > apply_setting > Error')
            raise
