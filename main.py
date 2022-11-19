import sys
from PySide6 import QtWidgets
from MainWindow import Ui_MainWindow
from qt_material import apply_stylesheet
import requests
from enum import IntEnum, Enum
import json


class EnumError(Enum):
    ERR_OK = 200
    ERR_KEY_INVALID = 401
    ERR_KEY_BLOCKED = 402
    ERR_DAILY_REQ_LIMIT_EXCEEDED = 403
    ERR_TEXT_TOO_LONG = 413
    ERR_LANG_NOT_SUPPORTED = 501


path_name = "response.json"
dict_key_errors = {
    200: 'Операция выполнена успешно.',
    401: 'Ключ API невалиден.',
    402: 'Ключ API заблокирован.',
    403: 'Превышено суточное ограничение на количество запросов.',
    413: 'Превышен максимальный размер текста.',
    501: 'Заданное направление перевода не поддерживается.'
}


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.label_3.setText('Simple text')


def request():
    _def = None
    param = {
        "key": 'dict.1.1.20221117T140505Z.c922e22b66033b98.85efa77b962fdd9f7de016d41321213dcbd4af7d',
        "lang": 'en-ru',
        'text': 'addition',
        'ui': 'ru',
        'flags': 0x0002 | 0x0008
    }
    response = requests.get('https://dictionary.yandex.net/api/v1/dicservice.json/lookup', params=param)
    _code = response.status_code
    if _code == EnumError.ERR_OK:
        _json = response.json()
        _def = _json['def']  # список словарей
    else:
        if _code in dict_key_errors:
            print(dict_key_errors[_code])
            return
        else:
            print(_code)
            return

    s = json.dumps(response.json(), indent=4, sort_keys=True, ensure_ascii=False)
    with open("response.json", "w", encoding='utf-8') as file:
        file.write(s)


def read_json_file(file_name):
    with open(file_name, "r", encoding='utf-8') as file:
        data = json.load(file)
        print(data)
        for _l in data['def']:
            pos = _l['pos']
            text = _l['text']
            tr = _l['tr']
            ts = _l['ts']
            print(pos, text, ts)


def main():
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    # setup stylesheet
    apply_stylesheet(app, theme='dark_teal.xml')
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
