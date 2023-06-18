import re
import copy
from ..config import ConfigurationMyOdt
from ..lib import ODTMeta
from ..lib import Handler

# logger = ConfigurationMyOdt.logger


class SettingExtendDiagram:
    def __init__(self, path: str, date: ODTMeta):
        self.path = Handler.check_slash(path)
        self.date = date

    @staticmethod
    def _parse_table(text_xml: str) -> list:
        """Функция разбора таблиц на составные части вида:
        table = [start_table,
                    ['<table:table-rows>', [
                        ['<table:table-row>', [<cell></cell>, <cell></cell>, <cell></cell>...], '</table:table-row>'],
                        ['<table:table-row>', [...], '</table:table-row>'],
                        ['<table:table-row>', [...], '</table:table-row>'],
                                           ],
                    '</table:table-rows>'],
                end_table]
        Где мы получем в table[1] список строк, где первая и последние строки являются тегами, а дальнейшие строки
        представляют из себя список ячеек <cell> каждой строки."""
        # Получаем из XML таблицу
        table = re.findall(r'<table.+?<\/table:table>', text_xml)[0]
        # Получаем начало таблицы
        table_start = re.findall(r'<table:table table:name.+?<\/table:table-header-rows>', table)[0]
        # Получаем строки, с данными для выделения конца таблицы.
        rows = re.findall(r'<table:table-rows>.+?<\/table:table-rows>', table)[0]
        # Получаем конец таблицы
        table_end = re.findall(r'<table:table-rows>.+?</table:table>', table)[0].replace(rows, '')
        # Получаем строки, с данными для заполнения списка
        row = re.findall(r'(<table:table-rows>.+?<\/table:table-rows>)', table)
        row = re.findall(r'(<table:table-row>.+?<\/table:table-row>)', row[0])
        table_new = [table_start, ['<table:table-rows>', [], '</table:table-rows>'], table_end]
        # Перебираем строки и выделяем ячейки.
        for i in range(len(row)):
            cell = re.findall(r'(<table:table-cell.+?<\/table:table-cell>)', row[i])
            temp = ['<table:table-row>', '</table:table-row>']
            temp.insert(1, cell)
            table_new[1][1].append(temp)
        return table_new

    @staticmethod
    def _check_data(table_option: dict, table: list) -> bool:
        """Функция проверяет колличество столбцов и строк во входных и выходных данных на соответсвие."""
        check = True
        if table_option['row'] == len(table[1][1]):
            for i in table[1][1]:
                if table_option['cell'] != len(i[1])-1:
                    check = False
        else:
            check = False
        return check

    @staticmethod
    def _add_row_and_cell(data_diagram: dict, table: list) -> list:
        """Метод добавляет строки в шаблон если занчений в параметрах больше чем в шаблоне"""
        if len(data_diagram['content']) > len(table[1][1]):
            multiplier = len(data_diagram['content']) - len(table[1][1])
            temp_row = table[1][1][-1]
            for i in range(multiplier):
                # Необходимо делать глубокое копирование строки, что бы различались id
                temp_row = copy.deepcopy(temp_row)
                table[1][1].append(temp_row)
        return table

    @staticmethod
    def _insert_data(data_in: str, cell_out: str) -> str:
        """
        Метод заменяет значения в переданной ячейке на новые
        data_in = 5555
        cell_out = <table:table-cell office:value-type="float" office:value="22222"><text:p>22222</text:p></table:table-cell>

        data_out = <table:table-cell office:value-type="float" office:value="555"><text:p>5555</text:p></table:table-cell>
        """
        value = re.findall(r'office:value="(.+?)"', cell_out)[0]
        data_out = cell_out.replace(value, data_in)
        return data_out

    @staticmethod
    def _insert_row_name(data_in: str, cell_in: str) -> str:
        """
        Метод заменяет значения в переданной ячейке на новые
        data_in = 5555
        cell_out = <table:table-cell office:value-type="float" office:value="22222"><text:p>22222</text:p></table:table-cell>

        data_out = <table:table-cell office:value-type="float" office:value="555"><text:p>5555</text:p></table:table-cell>
        """
        value = re.findall(r'<text:p>(.+?)</text:p>', cell_in)[0]
        data_out = cell_in.replace(value, data_in)
        return data_out

    @staticmethod
    def _check_first_cell(row: list) -> bool:
        """Метод проверяет на валидность первый элемент в списке."""
        list_index_str = []
        for cell_index in range(len(row)):
            value = re.findall(r'office:value-type="(.+?)"', row[cell_index])[0]
            if value == 'string':
                list_index_str.append(cell_index)
        if (len(list_index_str) == 1) and (list_index_str[0] == 0):
            return True
        else:
            return False

    @staticmethod
    def _loop_render(table: list, diagram: dict) -> list:
        """Метод перебирает строки, и ячейки в них, и вызывает фукнцию для замены значений на новые."""
        result_table = table
        for row in range(len(diagram['content'])):
            # Получаем строку  с входными данными [{'cell': '1', 'value': '1'}]
            row_in_data = diagram['content'][row]
            """
            Получаем строку с XML 
            ['<table:table-row>', 
            ['<table:table-cell office:value-type="string"><text:p>Строка 1</text:p></table:table-cell>', 
            '<table:table-cell office:value-type="float" office:value="9.1"><text:p>9.1</text:p></table:table-cell>'],
            '</table:table-row>']
            """
            # Меняем название строки.
            if row_in_data['row']:
                row_xml_table = result_table[1][1][row]
                result_table[1][1][row][1][0] = SettingExtendDiagram._insert_row_name(row_in_data['row'],
                                                                                      result_table[1][1][row][1][0])
            if SettingExtendDiagram._check_first_cell(row_xml_table[1]):
                for cell in range(len(row_xml_table[1])-1):
                    cell_in_data = row_in_data['cells'][cell]
                    cell_xml_data = row_xml_table[1][cell+1]
                    result_table[1][1][row][1][cell+1] = SettingExtendDiagram._insert_data(cell_in_data['value'],
                                                                                          cell_xml_data)
            else:
                # logger.error('odtapplysettings > setting_extend_diagram > _loop_render > Ошибка в типе первой ячейке '
                #              'входных данных. Или длинне строки. ' + row_xml_table)
                raise Exception('Ошибка в типе первой ячейке входных данных. Или длинне строки. ' + row_xml_table)
        return result_table

    @staticmethod
    def _chek_list_in_join(in_data: list) -> str:
        """Рекурсивный метод, объединяет структуру таблицы из листов в строку."""
        for i in range(len(in_data)):
            if type(in_data[i]) == list:
                temp = SettingExtendDiagram._chek_list_in_join(in_data[i])
                in_data[i] = temp
        out_data = ''.join(in_data)
        return out_data

    @staticmethod
    def _text_build(text_xml: str, table: str) -> str:
        """Метод для сборки текста. Заменяет текст таблицы в общем тексте документа"""
        # Получаем из XML таблицу
        table_search = re.findall(r'<table.+?<\/table:table>', text_xml)[0]
        text_xml = text_xml.replace(table_search, table)
        return text_xml

    def apply_setting(self) -> None:
        """Основной метод применения настроек"""
        # Перебираем диаграммы из входных данных
        for diagram in self.date.diagram:
            # Получаем имя диаграммы
            name = diagram['key_']
            # Берем порядковый номер ктороый присваивается в имени.
            name = name.split('_')[-1]
            # Создаем строку содержащую участок пути, например Object 1/content.xml
            name = 'Object ' + name + '/content.xml'
            # Проверяем есть ли файл по указанному пути
            if Handler.is_exist(self.path + name):
                # Если есть открываем
                with open(self.path + name, 'r') as file:
                    text = file.read()
            else:
                # Если нет то возвращаем ошибку
                # logger.error('odtapplysettings > setting_extend_diagram > _loop_render > The chart file in the ' +
                #              self.path + name + 'path does not exist! There may be an error in the chart name. ' +
                #              diagram['key_'])
                raise Exception('The chart file in the ' + self.path + name + 'path does not exist!'
                                ' There may be an error in the chart name. ' + diagram['key_'])
            # Вызываем функцию разбора таблицы на составные части в виде вложенных списков
            table = SettingExtendDiagram._parse_table(text)
            # Проверяем есть ли необходимость расширять строки, или же входные данные соответсвуют шаблону
            if not SettingExtendDiagram._check_data(self.date.options[0]['diagram'][diagram['key_']], table):
                table = SettingExtendDiagram._add_row_and_cell(diagram, table)
            table = SettingExtendDiagram._loop_render(table, diagram)
            table = SettingExtendDiagram._chek_list_in_join(table)
            text = SettingExtendDiagram._text_build(text, table)
            with open(self.path + name, 'w') as file:
                file.write(text)
