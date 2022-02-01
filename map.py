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
        self.ll = ['138.190176', '-29.054505']
        self.spn = ['20', '20']
        self.mode = 'map'
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
        elif event.key() == Qt.Key_Down:
            if float(self.ll[1]) - 1 >= -90:
                self.ll[1] = str(float(self.ll[1]) - 1)
        elif event.key() == Qt.Key_Left:
            if float(self.ll[0]) - 1 >= -180:
                self.ll[0] = str(float(self.ll[0]) - 1)
        elif event.key() == Qt.Key_Right:
            if float(self.ll[0]) + 1 <= 180:
                self.ll[0] = str(float(self.ll[0]) + 1)
        elif event.key() == Qt.Key_PageUp:
            if float(self.spn[0]) + 10 <= 90:
                self.spn[0] = str(float(self.spn[0]) + 2)
                self.spn[1] = str(float(self.spn[1]) + 2)
        elif event.key() == Qt.Key_PageDown:
            if float(self.spn[0]) - 10 >= 0:
                self.spn[1] = str(float(self.spn[1]) - 2)
                self.spn[0] = str(float(self.spn[0]) - 2)

        self.search_address()

    def reset(self):
        self.address_input.setText('')
        self.address_output.setText('')

    def search_address(self):
        self.address_output.setText('')
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(self.ll)}&spn={','.join(self.spn)}&l={self.mode}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.pixmap = self.pixmap.scaled(700, 500)
        self.screen.setPixmap(self.pixmap)

    def mode_layout(self):
        self.mode = 'map'
        self.search_address()

    def mode_satellite(self):
        self.mode = 'sat'
        self.search_address()

    def mode_hybrid(self):
        self.mode = 'sat,skl'
        self.search_address()

    def index_states(self):
        state = self.index_state.checkState()
        if state:
            pass
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Map()
    ex.show()
    sys.exit(app.exec())
