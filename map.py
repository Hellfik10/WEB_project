import requests
import json
import pygame

import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class Map(QMainWindow):
    def __init__(self):
        self.ll = ['50', '50']
        self.z = '5'
        self.mode = 'map'
        self.size = ['650', '450']
        super().__init__()
        uic.loadUi('map.ui', self)
        self.ui()

    def ui(self):
        self.index_state.clicked.connect(self.index_states)
        self.reset_address.clicked.connect(self.reset)
        self.search.clicked.connect(self.search_address)
        self.layout.clicked.connect(self.mode_layout)
        self.satellite.clicked.connect(self.mode_satellite)
        self.hybrid.clicked.connect(self.mode_hybrid)

    def mousePressEvent(self, event):
        focused_widget = QApplication.focusWidget()
        if focused_widget:
            focused_widget.clearFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if float(self.ll[1]) + 1 <= 90:
                self.ll[1] = str(float(self.ll[1]) + 1)
                self.move_search()
        elif event.key() == Qt.Key_Down:
            if float(self.ll[1]) - 1 >= -90:
                self.ll[1] = str(float(self.ll[1]) - 1)
                self.move_search()
        elif event.key() == Qt.Key_Left:
            if float(self.ll[0]) - 1 >= -180:
                self.ll[0] = str(float(self.ll[0]) - 1)
                self.move_search()
        elif event.key() == Qt.Key_Right:
            if float(self.ll[0]) + 1 <= 180:
                self.ll[0] = str(float(self.ll[0]) + 1)
                self.move_search()
        elif event.key() == Qt.Key_PageUp:
            if int(self.z) + 1 <= 17:
                self.z = str(int(self.z) + 1)
                self.move_search()
        elif event.key() == Qt.Key_PageDown:
            if int(self.z) - 1 >= 0:
                self.z = str(int(self.z) - 1)
                self.move_search()

    def reset(self):
        self.address_input.setText('')
        self.address_output.setText('')
        self.point = ''
        self.move_search()

    def move_search(self):
        map_api_server = f"http://static-maps.yandex.ru/1.x/"
        if self.point:
            map_params = {
                # позиционируем карту центром на наш исходный адрес
                "ll": ','.join(self.ll),
                "z": self.z,
                "l": self.mode,
                "size": ','.join(self.size),
                # добавим точку, чтобы указать найденную аптеку
                "pt": "{0},pm2dgl".format(','.join(self.point))
            }
        else:
            map_params = {
                # позиционируем карту центром на наш исходный адрес
                "ll": ','.join(self.ll),
                "z": self.z,
                "l": self.mode,
                "size": ','.join(self.size)
            }
        response = requests.get(map_api_server, params=map_params)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.screen.setPixmap(self.pixmap)

    def search_address(self):

        map_api_server = f"http://static-maps.yandex.ru/1.x/"

        if self.address_input.text():
            toponym_to_find = self.address_input.text()

            geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

            geocoder_params = {
                "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                "geocode": toponym_to_find,
                "format": "json"}

            response = requests.get(geocoder_api_server, params=geocoder_params)

            if not response:
                # обработка ошибочной ситуации
                pass

            # Преобразуем ответ в json-объект
            json_response = response.json()
            # Получаем первый топоним из ответа геокодера.
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            self.toponym = toponym
            toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"].split(', ')
            # Координаты центра топонима:
            toponym_coodrinates = toponym["Point"]["pos"]
            # Долгота и широта:

            self.ll = toponym_coodrinates.split(" ")
            self.address = ', '.join(toponym_address)

            state = self.index_state.checkState()
            if state:
                try:
                    self.address_output.setText(f'{self.address} \
                        {toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]}')
                except:
                    self.address_output.setText(self.address)
            else:
                self.address_output.setText(self.address)
            self.point = self.ll.copy()

            map_params = {
                # позиционируем карту центром на наш исходный адрес
                "ll": ','.join(self.ll),
                "z": self.z,
                "l": self.mode,
                "size": ','.join(self.size),
                # добавим точку, чтобы указать найденную аптеку
                "pt": "{0},pm2dgl".format(','.join(self.point))
            }
        else:
            self.point = ''

            map_params = {
                # позиционируем карту центром на наш исходный адрес
                "ll": ','.join(self.ll),
                "z": self.z,
                "l": self.mode,
                "size": ','.join(self.size)
            }

        response = requests.get(map_api_server, params=map_params)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.screen.setPixmap(self.pixmap)

    def mode_layout(self):
        self.mode = 'map'
        self.move_search()

    def mode_satellite(self):
        self.mode = 'sat'
        self.move_search()

    def mode_hybrid(self):
        self.mode = 'sat,skl'
        self.move_search()

    def index_states(self):
        state = self.index_state.checkState()
        if state:
            try:
                self.address_output.setText(f'{self.address} \
                    {self.toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]}')
            except:
                self.address_output.setText(self.address)
        else:
            self.address_output.setText(self.address)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())
