import sys
from ctypes import Union
from typing import List, Dict, Any

from PySide6 import QtWidgets
from PySide6.QtCore import QModelIndex, QAbstractItemModel, QObject, QAbstractTableModel
from PySide6.QtGui import Qt, QStandardItem
from PySide6.QtWidgets import QTreeView
from MainWindow import Ui_MainWindow
from qt_material import apply_stylesheet
import requests
from enum import IntEnum, Enum
import json

my_dict = {
    '5': 'first',
    '2': 'two',
    '7': 'seven',
    '1': {
        '23': 'twenty three',
        '41': 'forty-one'
    },
    '3': 'three',
    '4': 'four'
}


class WordItem:
    def __init__(self, parent: 'WordItem' = None):
        self._parent = parent
        self._pos = ''
        self._word = ''
        self._ts = ''
        self._translate = ''
        self._fr = 0
        self._example = ''
        self._gen = ''
        self._mean = []
        self._syn = []
        self._children = []


class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # return self._data[index.row()][index.column()]
            if index.column() == 0:
                return self._data[index.row()][0]
            if index.column() == 1:
                return self._data[index.row()][1]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return 2


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
        _list = self.load()
        self._model = TableModel(_list)
        self.tableLeft.setModel(self._model)

    def read_json_file(self):
        with open('response.json', "r", encoding='utf-8') as file:
            data = json.load(file)
            return data['def']

    def load(self):
        _list = self.read_json_file()
        list_data = []
        _pos = ''
        _tr = None

        for index, value in enumerate(_list):
            for key, _value in value.items():
                if key == 'pos':
                    _pos = _value
                elif key == 'tr':
                    _tr = _value
                    for d in _tr:
                        _data_tuple = _pos, d['text'], _value
                        list_data.append(_data_tuple)
        return list_data


class TreeItem:
    def __init__(self, parent: 'TreeItem' = None):
        self._parent = parent
        self._key = ''
        self._value = ''
        self._value_type = None
        self._children = []

    @property
    def value_type(self):
        return self._value_type

    @value_type.setter
    def value_type(self, value):
        self._value_type = value

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, key: str):
        self._key = key

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value

    def appendChild(self, item: 'TreeItem'):
        self._children.append(item)

    def child(self, row: 'int') -> 'TreeItem':
        return self._children[row]

    def parent(self) -> 'TreeItem':
        return self._parent

    def childCount(self) -> 'int':
        return len(self._children)

    def row(self) -> 'int':
        return self._parent._children.index(self) if self._parent else 0

    @classmethod
    def load(cls, value, parent: 'TreeItem' = None) -> 'TreeItem':
        rootItem = TreeItem(parent)
        rootItem.key = 'root'
        if isinstance(value, Dict):
            for key, value in value.items():
                child = cls.load(value, rootItem)
                child.key = key
                child.value_type = type(value)
                rootItem.appendChild(child)
        elif isinstance(value, List):
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                child.key = index
                child.value_type = type(value)
                rootItem.appendChild(child)
        else:
            rootItem.value = value
            rootItem._value_type = type(value)

        return rootItem


class JsonModel(QAbstractItemModel):
    """ An editable model of Json data """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self._rootItem = TreeItem()
        self._headers = ("key", "value")

    def clear(self):
        """ Clear data from the model """
        self.load({})

    def load(self, document: dict):
        """Load model from a nested dictionary returned by json.loads()

        Arguments:
            document (dict): JSON-compatible dictionary
        """

        assert isinstance(
            document, (dict, list, tuple)
        ), "`document` must be of dict, list or tuple, " f"not {type(document)}"

        self.beginResetModel()

        self._rootItem = TreeItem.load(document)
        self._rootItem.value_type = type(document)

        self.endResetModel()

        return True

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """Override from QAbstractItemModel

        Return data from a json item according index and role

        """
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            # if index.column() == 0:
            return item.value

            # if index.column() == 1:
            #     return item.value

        elif role == Qt.EditRole:
            if index.column() == 1:
                return item.value

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole):
        """Override from QAbstractItemModel

        Set json item according index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)

        """
        if role == Qt.EditRole:
            if index.column() == 1:
                item = index.internalPointer()
                item.value = str(value)

                # if __binding__ in ("PySide", "PyQt4"):
                #     self.dataChanged.emit(index, index)
                # else:
                self.dataChanged.emit(index, index, [Qt.EditRole])

                return True

        return False

    def headerData(
            self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override from QAbstractItemModel

        For the JsonModel, it returns only data for columns (orientation = Horizontal)

        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        """Override from QAbstractItemModel

        Return index according row, column and parent

        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Override from QAbstractItemModel

        Return parent index of index

        """

        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return 2

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super(JsonModel, self).flags(index)

        if index.column() == 1:
            return Qt.ItemIsEditable | flags
        else:
            return flags

    def to_json(self, item=None):

        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        if item.value_type is dict:
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.key] = self.to_json(ch)
            return document

        elif item.value_type == list:
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_json(ch))
            return document

        else:
            return item.value


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


# def read_json_file(file_name):
#     with open(file_name, "r", encoding='utf-8') as file:
#         data = json.load(file)
#         return data['def']
#
#
# def load():
#     _list = read_json_file(path_name)
#     list_data = []
#     _pos = ''
#     _tr = None
#
#     for index, value in enumerate(_list):
#         for key, _value in value.items():
#             if key == 'pos':
#                 _pos = _value
#             elif key == 'tr':
#                 _tr = _value
#                 for d in _tr:
#                     _data_tuple = _pos, d['text'], _value
#                     list_data.append(_data_tuple)
#     print(list_data)


def main():
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
