from typing import Optional
from .lib import Handler, ODTMeta, runtime
from .config import ConfigurationMyOdt
from .odt_engine import MyOdfGenerator
import re
import datetime

# logger = ConfigurationMyOdt.logger


class ODTLoader:
    """The class loader data. Prepares data for further work with it"""
    def __init__(self, data_dict: dict):
        self.data = data_dict  # Получаем словарь содержащий входные данные

    def _get_template_block(self) -> Optional[list]:
        """Получаем список данных которые входят шаблонный блок"""
        pass  # TODO

    def _get_if_options(self) -> Optional[dict]:
        """Получаем условия"""
        # Если опция ехтенд сет существует
        if 'if_options' in self.data['content']:
            return self.data['content']['if_options']
        else:
            return None

    def _get_extend_set_text(self) -> Optional[list]:
        """Getting a list of data to replace in tables that use the extend_set option. If there is no such data,
         None is returned"""
        # Если опция ехтенд сет существует
        if 'extend_set' in self.data['content']:
            return self.data['content']['extend_set']

        else:
            return None

    def _get_diagram(self) -> Optional[list]:
        """Getting a list of data for working with charts. If there is no such data, None is returned"""
        if 'diagram' in self.data['content']:
            return self.data['content']['diagram']
        else:
            return None

    def _get_images(self) -> Optional[list]:
        """Getting a list of data for working with images. If there is no such data, None is returned."""
        if 'images' in self.data['content']:
            return self.data['content']['images']
        else:
            return None

    def _get_extend_set(self) -> Optional[dict]:
        """We get a list of options and their settings. If there is no such data, None is returned.
        [{'extend_set': {'count': 2, 'len1': 3, 'len2': 6}}]"""
        extend_set = {}
        if 'extend_set' in self.data['content']:
            count = int(len(self.data['content']['extend_set']))
            extend_set['count'] = count
            for i in range(count):
                len_str = len(self.data['content']['extend_set'][i]['content'])
                extend_set[self.data['content']['extend_set'][i]['key_']] = len_str
            return extend_set
        else:
            return None

    def _get_opt_diagram(self) -> Optional[dict]:
        if 'diagram' in self.data['content']:
        #  'diagram': {'diagram1': {'row': 3, 'cell': 4}, 'diagram2': {'row': 3, 'cell': 4}}
            temp_diagram_dict = {}
            for diagram in self.data['content']['diagram']:
                row = len(diagram['content'])
                cell = len(diagram['content'][0]['cells'])
                for i in diagram['content']:
                    if cell != len(i['cells']):
                        err = 'Длины строк должны быть равны: > ' + diagram['key_']
                        # logger.exception('app > ODTLoader > _get_opt_diagram > Except: ' + err)
                        raise Exception(err)
                temp_diagram_dict[diagram['key_']] = dict(row=row, cell=cell)
            return temp_diagram_dict
        else:
            return None

    def _get_options(self) -> Optional[list]:
        temp_list = []
        temp_dict = {'extend_set': '', 'diagram': ''}
        extend_send = self._get_extend_set()
        diagram = self._get_opt_diagram()
        if extend_send:
            temp_dict['extend_set'] = extend_send
        if diagram:
            temp_dict['diagram'] = diagram
        temp_list.append(temp_dict)
        if len(temp_list) > 0:
            return temp_list
        else:
            temp_list = None
            return temp_list

    def load(self) -> ODTMeta:
        """Base method of the class. Use it for work!"""
        try:
            name = self.data['document_name']
            document = self.data['document_template_binary']
            text_replace = self.data['content']['text_and_table_content']
            extend_set_text = self._get_extend_set_text()
            diagram = self._get_diagram()
            images = self._get_images()
            options = self._get_options()
            if_options = self._get_if_options()
            meta = ODTMeta(name=name, document=document, text_replace=text_replace, extend_set_text=extend_set_text,
                           diagram=diagram, images=images, options=options, if_options=if_options)
        except Exception:
            # logger.exception('app > ODTBuilder > load > Except:')
            raise
        return meta


class ODTBuilder:
    def __init__(self, meta: ODTMeta):
        self.meta_data = meta
        self.path = Handler.check_slash(ConfigurationMyOdt.path_template_folder)
        self.temp_path = self.path + 'temp/'
        self.out_path = self.path + 'out/'

    def _write_template(self) -> str:
        """Method for creating a template file from binary code"""
        Handler.check_and_make(self.path)
        new_name = self.meta_data.name
        with open(self.path + new_name + '.odt', 'wb') as file_out:
            file_out.write(self.meta_data.document)
        return new_name

    def _add_marker(self) -> None:
        """
        The method checks whether the {{REPORT_ID}} marker field is present in the template body, and
        adds it if it is not present. To later replace the marker with the request ID.
        """
        # Проверяем наличие маркера {{REPORT_ID}} в шаблоне
        search = '{{REPORT_ID}}'
        marker_var = 'xmlns:reportid="{{REPORT_ID}}"'
        content_path = self.temp_path + self.meta_data.name + '/content.xml'
        if Handler.is_exist(content_path):
            with open(content_path) as file_in:
                content = file_in.read()
            if search not in content:
                # logger.info('app > ODTBuilder > _add_marker > No marker')
                replace_text_select = re.findall(r'xmlns:.+', content)
                replace_text = marker_var + ' ' + replace_text_select[0]
                content = content.replace(replace_text_select[0], replace_text)
                with open(content_path, 'w') as file_out:
                    file_out.write(content)
        #     else:
        #         # logger.debug('app > ODTBuilder > _add_marker > Contains marker')
        # else:
        #     # logger.error(
        #     #     'app > ODTBuilder > _add_marker > {} - no such file or directory'.format(content_path))


    def build(self) -> str:
        new_name = Handler.check_filename(self._write_template())
        myodfcreate = MyOdfGenerator(new_name, self.path, self.out_path, self.meta_data)
        myodfcreate.move_and_unpack()
        self._add_marker()
        myodfcreate.settings_apply()
        myodfcreate.render_template()
        full_path_out = myodfcreate.move_and_pack_template()
        return full_path_out



class ODTemplater:
    def __init__(self, data: dict):
        self.data_dict = data
        self.full_path_out = None
        self.text_bytes = None

    def _read_template(self) -> None:
        """ Возвращает файл в виде байтовой последовательности """
        with open(self.full_path_out, 'rb') as file:
            self.text_bytes = file.read()

    @runtime
    def create(self) -> bytes:
        # logger.info('////////  ODTemplater > create > start--  ////////')
        welcome_string = '{} - ODTemplater started...'.format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print(welcome_string)
        loader = ODTLoader(self.data_dict)
        load_date = loader.load()
        build_date = ODTBuilder(load_date)
        self.full_path_out = build_date.build()
        self._read_template()
        Handler.removefile(self.full_path_out)
        farewell_string = '{} - ODTemplater done.'.format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print(farewell_string)
        # logger.info('////////  ODTemplater > create > end--  ////////')
        return self.text_bytes

