import ctypes
import sys
import pyautogui as pag
import time

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, QObject, pyqtSignal

import ExceptionDialog
import temp_path


class TMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.x_position = 0
        self.y_position = 0
        self.x_position_label = QLabel(self)
        self.y_position_label = QLabel(self)

        self.setWindowTitle("Cheater corsi FAD")
        self.setGeometry(300, 300, 800, 300)
        self.setFixedSize(700, 450)
        self.icon = QIcon(temp_path.resource_path(r'assets/logo.jpg'))
        self.setWindowIcon(self.icon)

        self.widget = QLabel()
        self.create_background()

        self.clicker_thread = QThread()
        self.clicker = Clicker()

        self.track_cursor()

        self.layout = QGridLayout()
        self.create_layout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def create_background(self):
        pixmap = QPixmap(temp_path.resource_path(r'assets/wallpaper_1.jpg'))

        new_pix = QPixmap(pixmap.size())
        overlay_color = QColor(245, 245, 255)
        new_pix.fill(overlay_color)

        painter = QPainter(new_pix)
        painter.setOpacity(0.45)
        painter.drawPixmap(QtCore.QPoint(), pixmap)
        painter.end()

        self.widget.setPixmap(new_pix)
        self.widget.setScaledContents(True)
        self.widget.setFont(QFont('Arial', 12))


    def create_layout(self):
        font1 = QFont("Roboto", 11, QFont.Bold)

        vertical_layout = QVBoxLayout()
        lower_grid_layout = QGridLayout()
        upper_grid_layout = QGridLayout()

        current_position_label = QLabel("Posizione corrente del cursore")
        current_position_label.setFont(font1)
        current_position_label.setAlignment(Qt.AlignCenter)
        current_position_label.setMaximumSize(1000, 100)
        next_position_label = QLabel("Imposta la posizione del cursore")
        next_position_label.setFont(font1)
        next_position_label.setAlignment(Qt.AlignCenter)
        next_position_label.setMaximumSize(1000, 100)

        self.x_position_label.setText(str(self.x_position))
        self.x_position_label.setAlignment(Qt.AlignCenter)
        self.x_position_label.setFont(font1)
        self.x_position_label.setMaximumSize(1000, 45)

        self.y_position_label.setText(str(self.y_position))
        self.y_position_label.setAlignment(Qt.AlignCenter)
        self.y_position_label.setFont(font1)
        self.y_position_label.setMaximumSize(1000, 45)

        x_label2 = QLabel("X:")
        x_label2.setMinimumSize(0, 50)
        y_label2 = QLabel("Y:")
        y_label2.setMinimumSize(0, 50)

        self.launch_button = QPushButton("Start")
        self.launch_button.clicked.connect(self.auto_click)
        self.launch_button.setMinimumSize(0, 35)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setMinimumSize(0, 35)
        self.stop_button.clicked.connect(self.stop_clicker)

        x_label1 = QLabel("Posizione X:")
        x_label1.setFont(font1)
        y_label1 = QLabel("Posizione Y:")
        y_label1.setFont(font1)

        self.x_input = QLineEdit()
        self.y_input = QLineEdit()

        upper_grid_layout.addWidget(current_position_label, 0, 0, 1, 4)
        upper_grid_layout.addWidget(x_label1, 1, 0)
        upper_grid_layout.addWidget(self.x_position_label, 1, 1)
        upper_grid_layout.addWidget(y_label1, 1, 2)
        upper_grid_layout.addWidget(self.y_position_label, 1, 3)
        lower_grid_layout.addWidget(next_position_label, 2, 0, 1, 4)
        lower_grid_layout.addWidget(x_label2, 3, 0)
        lower_grid_layout.addWidget(self.x_input, 3, 1)
        lower_grid_layout.addWidget(y_label2, 3, 2)
        lower_grid_layout.addWidget(self.y_input, 3, 3)
        lower_grid_layout.addWidget(self.launch_button, 4, 0, 1, 2)
        lower_grid_layout.addWidget(self.stop_button, 4, 2, 1, 2)

        vertical_layout.addLayout(upper_grid_layout)
        vertical_layout.addLayout(lower_grid_layout)

        self.layout.addLayout(vertical_layout, 0, 0)


    def update_position(self, position: tuple[int]):
        self.x_position = position[0]
        self.x_position_label.setText(str(self.x_position))
        self.y_position = position[1]
        self.y_position_label.setText(str(self.y_position))


    def track_cursor(self):

        self.tracker_thread = QThread()
        self.tracker = Tracker()
        self.tracker.moveToThread(self.tracker_thread)
        self.tracker_thread.started.connect(self.tracker.run)
        self.tracker.update.connect(self.update_position)
        self.tracker_thread.finished.connect(self.tracker_thread.deleteLater)

        self.tracker_thread.start()

        self.clicker.moveToThread(self.clicker_thread)
        self.clicker_thread.started.connect(self.clicker.run)

        self.clicker_thread.start()


    def auto_click(self):

        try:
            x = int(self.x_input.text())
            y = int(self.y_input.text())
            if x < 0 or y < 0:
                raise ValueError("Coordinates must be positive integers.")
            self.clicker.stop_flag = False
            self.clicker.position = (x, y)
        except Exception as e:
            error = ExceptionDialog.TExceptionDialog()
            error.exec()

    def stop_clicker(self):

        self.clicker.stop_flag = True

    def stop_thread(self):
        self.clicker.stop_flag = True
        self.clicker.super_stop_flag = True
        self.tracker.stop_flag = True

        self.tracker_thread.quit()
        self.tracker_thread.wait()

        self.clicker_thread.quit()
        self.clicker_thread.wait()

    def closeEvent(self, event):
        self.stop_thread()
        event.accept()


class Tracker(QObject):
    update = pyqtSignal(tuple)
    stop_flag = False

    def __init__(self):
        super().__init__()

    def run(self):
        while not self.stop_flag:
            position = pag.position()
            x = position.x
            y = position.y
            self.update.emit((x, y))
            time.sleep(0.2)


class Clicker(QObject):
    stop_flag = True
    super_stop_flag = False
    position = None

    def __init__(self):
        super().__init__()

    def run(self):
        start_time = time.time()

        while not self.super_stop_flag:
            while not self.stop_flag:
                current_time = time.time()
                if current_time - start_time > 12.0:
                    current_position = pag.position()
                    pag.moveTo(self.position[0], self.position[1])
                    pag.click()
                    pag.moveTo(current_position)
                    pag.click()
                    start_time = current_time
                    time.sleep(1)


appid = 'FAD_cheater.1.0.0'
if sys.platform == "cygwin" or sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

app = QApplication(sys.argv)
window = TMainWindow()
window.show()
app.exec()