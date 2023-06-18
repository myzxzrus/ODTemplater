import re


class MyOdtCheckerAnchor:
    """The class checks for inclusions in anchors in the document {{ANCHOR}} and {%options%}. Errors may occur during
    document generation, such as splitting the anchor into styles {%extend_set</text:span>(<text:span
    text:style-name= "T5">number=1, </text:span>extend_add=1)%}. In this case, the anchor will not be processed. The
    class removes anchor inclusions in the xml text. """

    @staticmethod
    def _check_anchor_list(anchor_list: list, text_xml: str) -> str:
        text_new = text_xml
        for i in range(len(anchor_list)):  # Перебираем список якорей
            # Делаем выборку включенных в якоря тегов XML {{PLACE_OF_<text:span text:style-name="T7">BIRTH</text:span>}}
            search_bag = re.findall(r'<.+?>', anchor_list[i])
            if len(search_bag) > 0:  # Если включения есть
                if search_bag[0][1:2] == '/':  # Проверяем первое включение, и если оно является закрывающим тегом XML
                    # Создаем переменную которая содержит регулярное выражения для поиска всего начиная с начала документа
                    # и до нашего якоря включительно.
                    search_var = '<.+?>' + anchor_list[i]
                    # Получаем кусок текста с начала документа и до нашего якоря
                    search_temp = re.findall(search_var, text_new)[0].replace(anchor_list[i], '')
                    # Получем список тегов с начала текста и до нашего якоря берем последний.
                    search_temp = re.findall(r'<.+?>', search_temp)[-1]
                    # В списке якорей в тексте добавляем открывающий XML тег который идет перед нашим якорем.
                    anchor_list[i] = search_temp + anchor_list[i]
                if search_bag[-1][
                   1:2] != '/':  # Проверяем последнее включение, и если оно является открывающим тегом XML
                    # Создаем переменную которая содержит регулярное выражения для поиска всего начиная с начала
                    # нашего якоря включительно и следующего за ним тега.
                    search_var = anchor_list[i] + '.+?>'
                    search_temp = re.findall(search_var, text_new)[0]  # Получаем кусок текста с описанного выше
                    # В списке якорей в тексте добавляем закрывающий XML тег который идет следом нашим якорем.
                    anchor_list[i] = search_temp
        for i in range(len(anchor_list)):  # Перебираем лист якорей
            search_bag = re.findall(r'<.+?>', anchor_list[i])  # Получаем лист багов
            if len(search_bag) > 0:  # Если лист багов существует
                for bag in search_bag:  # Бежим по нему
                    # Делаем временный лист якорей и убираем в нем баг
                    temp_token = anchor_list[i].replace(bag, '')
                    # Замещаем в тексте якорь с багами из листа на временный якорь с убранным багом
                    text_new = text_new.replace(anchor_list[i], temp_token)
                    # Убираем
                    anchor_list[i] = temp_token
        return text_new

    @staticmethod
    def check_anchor_bag(text_xml: str) -> str:
        new_text = text_xml
        search_anchor_list = re.findall(r'\{\{.+?\}\}', new_text)  # Получаем список якорей в тексте
        new_text = MyOdtCheckerAnchor._check_anchor_list(search_anchor_list, new_text)
        search_option_list = re.findall(r'\{\%.+?\%\}', new_text)  # Все описанное выше только для якоря с опцией
        new_text = MyOdtCheckerAnchor._check_anchor_list(search_option_list, new_text)
        return new_text

