import re
from ..config import ConfigurationMyOdt
from ..lib import Handler, ImageResize
from ..lib import ODTMeta


# logger = ConfigurationMyOdt.logger


class SettingAddImages:
    """Class for replacing template images in the processed template."""
    def __init__(self, text_xml: str, date: ODTMeta, path_to_folder_template: str):
        self.text = text_xml
        self.date = date
        self.path = Handler.check_slash(path_to_folder_template)

    def replace_img(self, name_pictures: str, bin_pictures: bytes) -> None:
        """This function overwrites the image in the document files"""
        name_master = name_pictures
        name_submissive = name_pictures.split('/')
        name_submissive[-1] = '@#$' + name_submissive[-1]
        name_submissive = '/'.join(name_submissive)
        with open(self.path + name_submissive, 'wb') as file_out:
            file_out.write(bin_pictures)
        img = ImageResize(self.path + name_master, self.path + name_submissive, self.path + name_master)
        img.apply_resize()
        Handler.removefile(self.path + name_submissive)

    def loop_search_images(self) -> None:
        """The function finds images in the document body and matches them to the template. And passes the name of
        the image in the template files for replacement. """
        img_tags = re.findall(r'<draw:frame.+?</draw:frame>', self.text)  # Ищем все изображения в тексте
        # Перебираем теги изображения
        for img_tag in img_tags:
            # Перебираем название маркеров из входных параметров.
            for images in self.date.images:
                var_anchor = '{{' + images['key_'] + '}}'
                # Если есть совпадения входных данных с текстом в документе
                if var_anchor in img_tag:
                    # Выделяем опцию содержащию имя изображения
                    name = re.findall(r'xlink:href=".+?"', img_tag)
                    # Очищаем весь мусор
                    name = name[0].replace('xlink:href="', '').replace('"', '')
                    # Вызываем функцию перезаписи изображения
                    self.replace_img(name, images['source_binary'])

    def apply_setting(self) -> None:
        try:
            self.loop_search_images()
        except Exception:
            # logger.exception(u'odtapplysettings > setting_add_images > SettingAddImages > apply_setting > Error')
            raise
