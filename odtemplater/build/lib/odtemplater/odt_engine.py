# -*- coding: utf-8 -*-
import re
from .config import ConfigurationMyOdt
from .lib import Archiver, Handler, ODTMeta
from .odtapplysettings import ODTApplySettings


# logger = ConfigurationMyOdt.logger


class MyOdfGenerator:
    """
    "ENG"
    Handler for *.ODT format templates. Allows you to create templates and replace anchors of the "{{STR}}
    "type with the passed values in "data_list". The "data_list" sheet must match the pattern: data_list = [{{'key_':
    'STR', 'render_text': 'You're text ...] where" key_ "contains the anchor name from the template, and "render_text"
    the value to replace.

    "RUS"
    Обработчик шаблонов формата *.ODT. Позваляет создавать
    шаблоны, и заменять в них якоря типа "{{STR}}" на переданные значения в "data_list". Лист "data_list" должен
    соответствовать образцу: data_list = [{{'key_': 'STR', 'render_text': 'You're text ...] где "key_" содержит имя
    якоря из шаблона, а  "render_text" значение для замены.tg'
    """
    def __init__(self, file_name_without_file_extension: str, path_to_file: str, out_path: str, meta: ODTMeta):
        self._file_name = Handler.check_filename(file_name_without_file_extension)
        self._path_to_file = Handler.check_slash(path_to_file)
        self._temp_path = self._path_to_file + 'temp/'
        self._out_path = Handler.check_slash(out_path)
        self._data = meta

    def move_and_unpack(self) -> None:
        """The method moves the template file to a temporary directory and unpacks it."""
        file_move = self._path_to_file + self._file_name + '.odt'
        Handler.movefile(file_move, self._temp_path, self._file_name, '.zip')
        Archiver.extract_template(self._temp_path, self._file_name, self._temp_path)
        Handler.removefile(self._temp_path + self._file_name + '.zip')

    def settings_apply(self) -> None:
        try:
            setting = ODTApplySettings(self._file_name, self._temp_path, self._data)
            setting.loop_settings()
        except Exception:
            # logger.exception('odt_engine > MyOdfGenerator > settings_apply > File not render')
            raise

    def _clear_template(self, text: str) -> str:
        """Method for processing the template and replacing key markers with the passed values."""
        # Ищем переменные и заменяем их значения
        try:
            list_clear = re.findall(r'\{\{.+?\}\}', text)
            if len(list_clear) > 0:
                for i in list_clear:
                    text = text.replace(i, '')
            return text
        except Exception:
            # logger.exception('odt_engine > MyOdfGenerator > _clear_template > File not clear')
            raise

    def render_template(self) -> None:
        """Method for processing the template and replacing key markers with the passed values."""
        # Ищем переменные и заменяем их значения
        content_path = self._temp_path + self._file_name + '/content.xml'
        try:
            with open(content_path) as file_in:
                text = file_in.read()
            # Меняем ключь значение по тексту.
            for i in self._data.text_replace:
                if 'key_' and 'render_text' in i:
                    text = text.replace('{{' + i['key_'] + '}}', i['render_text'])
            # Бежим по опции extend_set, перебираем все строки.
            if self._data.extend_set_text:
                for content_extend_set in self._data.extend_set_text:
                    for row_content in content_extend_set['content']:
                        for i in row_content:
                            if 'key_' and 'render_text' in i:
                                text = text.replace('{{' + i['key_'] + '}}', i['render_text'])
            text = self._clear_template(text)
            with open(content_path, 'w') as file_out:
                file_out.write(text)
        except Exception:
            # logger.exception('odt_engine > MyOdfGenerator > _render_template > File not render')
            raise

    def move_and_pack_template(self) -> str:
        """The method packages the template files and moves them to the output folder."""
        # Запаковывем результат в архив .zip
        try:
            path_to_pack = self._temp_path + self._file_name
            Archiver.pack_template(path_to_pack, self._out_path, self._file_name)
            Handler.removefile(path_to_pack)
            old_name = self._out_path + self._file_name + '.zip'
            new_name = self._out_path + self._file_name + '.odt'
            Handler.renamefile(old_name, new_name)
            return new_name
        except Exception:
            # logger.exception(u'odt_engine > MyOdfGenerator > _move_and_pack_template > File zip not complete')
            raise







