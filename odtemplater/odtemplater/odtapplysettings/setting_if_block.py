import re
from ..config import ConfigurationMyOdt
from . import MyOdtCheckerAnchor
from ..lib import ODTMeta


# logger = ConfigurationMyOdt.logger


class SettingIfBlock:
    """The class uses the option to multiply rows in document tables."""

    def __init__(self, text_xml: str, date: ODTMeta):
        self.text = text_xml
        self.date = date
        self.if_block = []  # Объявляем пустую переменную типа list

    def _build_if_block_in_text(self):
        for key, value in self.date.if_options.items():
            if not value:
                regex_pattern = r"({%\s*if\s+" + re.escape(key) + r"\s*%}(.*?){%\s*endif\s*%})"
                regex = re.compile(regex_pattern, re.DOTALL | re.MULTILINE)
                matches = regex.findall(self.text)
                if len(matches) > 0:
                    if len(matches[0]) > 0:
                        self.text = self.text.replace(matches[0][0], '')
            else:
                regex_pattern = r"({%\s*if\s+" + re.escape(key) + r"\s*%}(.*?){%\s*endif\s*%})"
                regex = re.compile(regex_pattern, re.DOTALL | re.MULTILINE)
                matches = regex.findall(self.text)
                if len(matches) > 0:
                    if len(matches[0]) > 1:
                        self.text = self.text.replace(matches[0][0], matches[0][1])

    def apply_setting(self) -> str:
        """
        "ENG" The function applies all the methods of the class, and returns the result.

        "RUS" Функция применяет все  методы класса, и возвращает результат.
        """
        try:
            self._build_if_block_in_text()
            return self.text
        except Exception:
            # logger.exception(u'odt_engine > SettingExtendSet > apply_setting > Error')
            raise
