from PIL import Image
from typing import NamedTuple, Optional
from ..config import ConfigurationMyOdt
import os
import zipfile
import shutil
import logging
import datetime
import time


# logger = ConfigurationMyOdt.logger

class ODTMeta(NamedTuple):
    """Tuple-type container class for storing and quickly handling information """
    name: str  # Имя документа.
    document: bytes  # Документ в виде массива байтов.
    text_replace: list  # Список словарей ключь-значения для замены.
    extend_set_text: Optional[list]  # Список словарей ключь-значения для замены в опциях {%extend_set()%}.
    diagram: Optional[list]  # Список содержащий данные для работы с диаграмой.
    images: Optional[list]  # Список содержащий словари словари с опциями для вставки изображений
    options: Optional[list]  # Список опций сгенерированных из входных данных
    if_options: Optional[dict]


class Handler:
    """This class contains auxiliary methods"""

    @staticmethod
    def check_slash(path: str) -> str:
        """
        This method checks for a closing slash at the end of the path. Example: a = '/home/user/folder'
        a = Handler.chek_slash(a) a -> /home/user/folder/
        """
        if not path[-1] == '/':
            path = path + '/'
        return path

    @staticmethod
    def check_filename(file_name: str) -> str:
        """
        This method checks the file name for an extension and returns the name without an extension. Example:
        a = 'Filename.odt'
        a = Handler.check_filename(a)
        a -> 'Filename'
        """
        file_name = file_name.split('.')[0]
        return file_name

    @staticmethod
    def check_format(format_file: str) -> str:
        """
        This method checks the parameter containing the file extension. Example: a = 'ODT'
        a = Handler.check_format(a)
        a -> '.odt'
        """
        format_file = format_file.lower()
        if not format_file[0] == '.':
            format_file = '.' + format_file
        return format_file

    @staticmethod
    def is_exist(path: str) -> bool:
        """This method checks the existence of a path and returns True or False"""
        if os.path.exists(path):
            return True
        else:
            return False

    @staticmethod
    def make_folder(path: str) -> None:
        """Use this method to create a file or folder."""
        try:
            os.makedirs(path)
        except Exception:
            # logger.exception('lib > Handler > make_folder > The {} directory could not be created'.format(path))
            raise

    @staticmethod
    def check_and_make(path: str) -> None:
        """This method checks for the specified file or directory and creates it if it is not present."""
        if Handler.is_exist(path):
            logging.debug('lib > Handler > check_and_make > Directory {} already exists'.format(path))
        else:
            logging.debug('lib > Handler > check_and_make > Directory {} does not exist'.format(path))
            Handler.make_folder(path)

    @staticmethod
    def copyfile(copy_file: str, out_folder: str, out_name: str, out_format: str) -> None:
        """
        The method checks if there is a file and copies it to the specified folder
        with the specified name and extension.
        """
        if Handler.is_exist(copy_file):
            try:
                Handler.check_and_make(out_folder)
                shutil.copyfile(copy_file, Handler.check_slash(out_folder) + Handler.check_filename(
                    out_name) + Handler.check_format(out_format))
            except Exception:
                # logger.exception('lib > Handler > copyfile > File {} copying crash'.format(copy_file))
                raise
        # else:
        #     logging.error('lib > Handler > copyfile > {} - no such file or directory'.format(copy_file))

    @staticmethod
    def movefile(copy_file: str, out_folder: str, out_name: str, out_format: str) -> None:
        """
        The method checks if there is a file and movies it to the specified folder
        with the specified name and extension.
        """
        if Handler.is_exist(copy_file):
            try:
                Handler.check_and_make(out_folder)
                shutil.copyfile(copy_file,
                                Handler.check_slash(out_folder) + Handler.check_filename(
                                    out_name) + Handler.check_format(out_format))
                os.remove(copy_file)
            except Exception:
                # logger.exception('lib > Handler > movefile > File {} movings crash'.format(copy_file))
                raise
        else:
            pass
            # logging.error('lib > Handler > movefile > {} - no such file or directory'.format(copy_file))

    @staticmethod
    def removefile(file: str) -> None:
        """This method deletes the specified file or directory."""
        if Handler.is_exist(file):
            try:
                if '.' in file.split('/')[-1]:
                    os.remove(file)
                else:
                    shutil.rmtree(file)
            except Exception:
                # logger.exception('lib > Handler > removefile > File {} remove crash'.format(file))
                raise
        # else:
            # logging.error('lib > Handler > removefile > {} - no such file or directory'.format(file))

    @staticmethod
    def renamefile(file_old: str, file_new: str) -> None:
        """This method renames the specified file or directory."""
        if Handler.is_exist(file_old):
            try:
                os.rename(file_old, file_new)
            except Exception:
                # logger.exception('lib > Handler > renamefile > File {} rename to {} crash'.format(file_old, file_new))
                raise
        # else:
        #     logging.error('lib > Handler > renamefile > {} - no such file or directory'.format(file_old))


class Archiver:
    """Class for Archive and Unarchive *.odt templates"""

    @staticmethod
    def extract_template(file_path: str, file_name: str, out_path: str) -> None:
        """
        Unpacks the zip archive
        Example: /home/user/Archive1.zip -> /home/out/{ARCHIVE NAME}
        file_path: Path to the folder containing the file. # /home/user/
        file_name: File name without file extension. # Archive1
        out_path: Path to the folder to unpack to, in a subdirectory equal to the archive name. # /home/out/
        """
        file_path = Handler.check_slash(file_path)
        file_name = Handler.check_filename(file_name)
        out_path = Handler.check_slash(out_path)
        full_path = file_path + file_name
        full_out_path = out_path + file_name
        try:
            fantasy_zip = zipfile.ZipFile(full_path + '.zip')
            fantasy_zip.extractall(full_out_path)
            fantasy_zip.close()
        except Exception:
            # logger.exception('lib > Archiver > execute_template > File: {} not extracting'.format(full_path))
            raise

    @staticmethod
    def pack_template(path_to_pack_folder: str, out_path: str, out_name: str) -> None:
        """
        To pack the files in a directory to the archive.
        path_to_pack_folder: The path to the directory with the backup files.
        out_path: The path where the archive will be saved.
        out_name: Archive name without extension.
        """
        path_to_pack_folder = Handler.check_slash(path_to_pack_folder)
        out_path = Handler.check_slash(out_path)
        out_name = Handler.check_filename(out_name)
        try:
            Handler.check_and_make(out_path)
            z = zipfile.ZipFile(out_path + out_name + '.zip', 'w')  # Создание нового архива
            for root, dirs, files in os.walk(path_to_pack_folder):  # Список всех файлов и папок в директории folder
                without_root = root.replace(path_to_pack_folder, "", 1)
                for file in files:
                    # Создание относительных путей и запись файлов в архив
                    z.write(os.path.join(root, file), arcname=os.path.join(without_root, file))
            z.close()
        except Exception:
            # logger.exception('lib > Archiver > pack_template > File {} zip not complete'.format(out_name))
            raise


class ImageResize:
    def __init__(self, path_image_master: str, path_image_submissive: str, path_image_out: str,
                 border_color: tuple = (255, 255, 255)):
        """Класс приводит размеры изоброжение ведомого под размеры изображения мастера с сохранением пропорций.
        В path_image_master = /you`r_path/image_name.jpg передается полный или относительный путь с указанием имени,
        и расширения изображения. Аналогично и для переменных path_image_submissive, path_image_out.
        """
        self.img_master = path_image_master
        self.img_submissive = path_image_submissive
        self.border_color = border_color
        self.out_image = path_image_out
        self.master_size = None
        self.submissive_size = None
        self.master_im = None
        self.submissive_im = None

    def _image_size(self) -> None:
        """Функция открывает изображение и является сетером атриботов класса содержащих размеры изображения"""
        if (Handler.is_exist(self.img_master)) and (Handler.is_exist(self.img_submissive)):
            self.master_im = Image.open(self.img_master)
            self.master_size = dict(width=float(self.master_im.size[0]), height=float(self.master_im.size[1]))
            self.submissive_im = Image.open(self.img_submissive)
            self.submissive_size = dict(width=float(self.submissive_im.size[0]), height=float(self.submissive_im.size[1]))
        else:
            # logger.error('lib > ImageResize > _image_size > Error')
            raise Exception('Один или несколько файлов не найдены. {} {}'.format(self.img_master, self.img_submissive))

    def _check_size(self) -> None:
        """
        Математическая логика приведения размера сторон ведомого изображения, к сторонам ведущего.
        В процентном соотношении, с сохранением пропорций. Без привышения какой либо из сторон ведомого изображения,
        длинны стороны ведущего.
        """
        a1 = self.master_size['width']
        b1 = self.master_size['height']
        a2 = self.submissive_size['width']
        b2 = self.submissive_size['height']
        if ((a1 < a2) and (b1 == b2)) or ((a1 > a2) and (b1 == b2)):
            k = a1 / a2
            self.submissive_size['width'] = a2 * k
            self.submissive_size['height'] = b2 * k
        elif ((a1 == a2) and (b1 < b2)) or ((a1 == a2) and (b1 > b2)):
            k = b1 / b2
            self.submissive_size['width'] = a2 * k
            self.submissive_size['height'] = b2 * k
        elif ((a1 < a2) and (b1 < b2)) or ((a1 > a2) and (b1 > b2)):
            k1 = a1 / a2
            k2 = b1 / b2
            if k1 < k2:
                self.submissive_size['width'] = a2 * k1
                self.submissive_size['height'] = b2 * k1
            elif k2 < k1:
                self.submissive_size['width'] = a2 * k2
                self.submissive_size['height'] = b2 * k2
            elif k1 == k2:
                self.submissive_size['width'] = a2 * k1
                self.submissive_size['height'] = b2 * k1

    def apply_resize(self) -> None:
        """
        Основной, публичный метод, выполняющий расчеты и сохранение приведенного,
        к необходиммым параметрам, изображения.
        """
        try:
            self._image_size()
            self._check_size()
            master_size = (int(self.master_size['width']), int(self.master_size['height']))
            submissive_size = (int(self.submissive_size['width']), int(self.submissive_size['height']))
            new_im = Image.new('RGB', master_size, self.border_color)  # luckily, this is already black!
            self.submissive_im = self.submissive_im.resize((int(self.submissive_size['width']),
                                                            int(self.submissive_size['height'])))
            new_im.paste(self.submissive_im, (int((master_size[0]-submissive_size[0])/2),
                                              int((master_size[1]-submissive_size[1])/2)))
            # new_im.show()
            new_im.save(self.out_image)
        except Exception:
            # logger.error('lib > ImageResize > apply_resize > Error')
            raise


def runtime_hour(func):
    """A decorator that displays the execution time in the format hours, minutes, seconds, and microseconds."""
    def start_runtime_hour(*args, **kwargs):
        now = datetime.datetime.now()
        hour_start = now.hour
        min_start = now.minute
        sec_start = now.second
        msec_start = now.microsecond
        temp = func(*args, **kwargs)
        now = datetime.datetime.now()
        hour_stop = now.hour
        min_stop = now.minute
        sec_stop = now.second
        msec_stop = now.microsecond
        hour = hour_stop - hour_start
        min = min_stop - min_start
        sec = sec_stop - sec_start
        msec = msec_stop - msec_start
        print('Время выполнения составило: "ЧЧ:ММ:СС:МС" {}:{}:{}:{}'.format(hour, min, sec, msec))
        return temp
    return start_runtime_hour()


def runtime(func):
    """A decorator that displays the execution time in seconds with fractions."""
    def start_runtime(*args, **kwargs) -> str:
        now = time.time()
        temp = func(*args, **kwargs)
        print('Время выполнения составило: {}'.format(time.time()-now))
        return temp
    return start_runtime
