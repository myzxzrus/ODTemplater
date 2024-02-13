from typing import NamedTuple, Optional
from ..config import ConfigurationMyOdt
from . import SettingExtendSet
from . import SettingAddImages
from . import SettingExtendDiagram
from . import SettingIfBlock
from ..lib import ODTMeta

# logger = ConfigurationMyOdt.logger


class ODTApplySettings:
    """A class that aggregates all document settings. Applies the necessary parameters and settings."""
    def __init__(self, file_name: str, temp_path: str, date: ODTMeta):
        self._file_name = file_name
        self._temp_path = temp_path
        self._date = date

    def loop_settings(self) -> None:
        """Function for applying settings to a template"""
        # Применяем настройки к шаблону
        try:
            if self._date.if_options:
                content_path = self._temp_path + self._file_name + '/content.xml'
                with open(content_path) as file_in:
                    text = file_in.read()
                if_settings = SettingIfBlock(text, self._date)
                text = if_settings.apply_setting()
                with open(content_path, 'w') as file_out:
                    file_out.write(text)
            if self._date.extend_set_text:
                for select_option in self._date.options:
                    if 'extend_set' in select_option:  # определяем есть ли опция extend_set в полученных данных
                        content_path = self._temp_path + self._file_name + '/content.xml'
                        with open(content_path) as file_in:
                            text = file_in.read()
                        setting_extend_set = SettingExtendSet(text, self._date)
                        text = setting_extend_set.apply_setting()
                        with open(content_path, 'w') as file_out:
                            file_out.write(text)
            if self._date.diagram:  # определяем есть ли опция diagram в полученных данных
                path = self._temp_path + self._file_name
                diagram = SettingExtendDiagram(path, self._date)
                diagram.apply_setting()
            if self._date.images:
                content_path = self._temp_path + self._file_name + '/content.xml'
                path_to_folder = self._temp_path + self._file_name
                with open(content_path) as file_in:
                    text = file_in.read()
                setting_add_images = SettingAddImages(text, self._date, path_to_folder)
                setting_add_images.apply_setting()
        except Exception:
            # logger.exception(u'odtapplysettings > odt_apply_settings > OdtApplySettings > loop_settings > Error')
            raise
