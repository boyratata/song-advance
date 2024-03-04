from PySide2 import QtWidgets, QtGui, QtCore
import sys
import requests
import pygame
import os
from io import BytesIO
from zipfile import ZipFile

class SongPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Song Player")
        self.setGeometry(100, 100, 800, 500)
        self.current_song_playing = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #263238; color: #FFFFFF; font-size: 14px; border-radius: 10px;")

        pygame.init()
        pygame.mixer.init()

        self.song_dict = {}
        self.current_song = None
        self.song_name = None

        self.init_ui()
        self.fetch_songs()

    def set_icon_from_github(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            icon_data = response.content
            icon_pixmap = QtGui.QPixmap()
            icon_pixmap.loadFromData(icon_data)
            icon = QtGui.QIcon(icon_pixmap)
            self.setWindowIcon(icon)
        else:
            print("Failed to download icon from GitHub.")

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        self.menu_widget = QtWidgets.QWidget()
        layout.addWidget(self.menu_widget)

        self.song_list = QtWidgets.QListWidget()
        self.song_list.setStyleSheet(
            "color: #FFFFFF; background-color: #37474F; border-radius: 10px; padding: 10px; border: 2px solid #455A64;")
        self.song_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.song_list.itemClicked.connect(self.toggle_play_pause)
        layout.addWidget(self.song_list)

        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.change_volume)

        slider_stylesheet = """
            QSlider::groove:horizontal {
                background-color: #546E7A;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #FFFFFF;
                width: 10px; /* Width of the handle */
                margin: -5px 0; /* Centers the handle vertically */
                border-radius: 5px; /* Makes the handle circular */
           }
        """
        self.volume_slider.setStyleSheet(slider_stylesheet)
        layout.addWidget(self.volume_slider)

        self.setLayout(layout)

    def fetch_songs(self):
        urls = [
            "https://github.com/boyratata/song-list/raw/main/ayo.zip",
            "https://github.com/boyratata/song-list/raw/main/hey.zip",
            "https://github.com/boyratata/song-list/raw/main/nah.zip",
            "https://github.com/boyratata/song-list/raw/main/wow.zip",
            "https://github.com/boyratata/song-list/raw/main/ay.zip",
            "https://github.com/boyratata/song-list/raw/main/u.zip",
            "https://github.com/boyratata/song-list/raw/main/sup.zip",
            "https://github.com/boyratata/song-list/raw/main/yaa.zip",
            "https://github.com/boyratata/song-list/raw/main/upload.zip"
        ]
        song_count = 0
        for url in urls:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with ZipFile(BytesIO(response.content)) as z:
                        for filename in z.namelist():
                            if filename.endswith('.mp3'):
                                song_name = filename.split('.')[0]
                                song_data = z.read(filename)
                                self.song_dict[song_name] = song_data
                                song_count += 1
                                self.song_list.addItem(f"{song_count}. {song_name}")
            except Exception as e:
                print(f"Error fetching songs: {e}")

    def toggle_play_pause(self, item):
        full_song_name = item.text()
        song_name = full_song_name.split('. ', 1)[-1]
        song_data = self.song_dict.get(song_name)

        if song_data:
            if song_name == self.current_song:
                if self.current_song_playing:
                    self.current_song_playing = False
                    pygame.mixer.music.pause()
                else:
                    self.current_song_playing = True
                    pygame.mixer.music.unpause()
            else:
                if self.current_song_playing:
                    pygame.mixer.music.stop()
                self.current_song_playing = True
                song_data_io = BytesIO(song_data)
                pygame.mixer.music.load(song_data_io)
                pygame.mixer.music.set_volume(self.volume_slider.value() / 100)
                pygame.mixer.music.play(-1)
                self.current_song = song_name
                QtCore.QTimer.singleShot(100, self.check_song_finished)
        else:
            print(f"Failed to play song: {full_song_name}")

    def change_volume(self, value):
        volume = value / 200 
        pygame.mixer.music.set_volume(volume)
    
        if value == 200:
            print("Volume is at maximum.")

    def check_song_finished(self):
        if not pygame.mixer.music.get_busy():
            self.current_song = None


class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logs = ""
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        owner_image_url = "https://github.com/boyratata/profile/raw/main/yo.PNG"
        owner_image_data = requests.get(owner_image_url).content
        owner_pixmap = QtGui.QPixmap()
        owner_pixmap.loadFromData(owner_image_data)

        owner_label = QtWidgets.QLabel()
        owner_label.setPixmap(owner_pixmap.scaled(30, 30, aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                                                  transformMode=QtCore.Qt.SmoothTransformation))
        owner_label.setStyleSheet("background-color: #263238;")
        layout.addWidget(owner_label)

        self.title_label = QtWidgets.QLabel("Song Player")
        self.title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.minimize_button = QtWidgets.QPushButton("━")
        self.minimize_button.clicked.connect(self.minimize_window)
        self.minimize_button.setStyleSheet("color: white; font-weight: bold; background-color: #455A64;")
        self.minimize_button.setFixedSize(20, 20)
        layout.addWidget(self.minimize_button)

        self.maximize_button = QtWidgets.QPushButton("☐")
        self.maximize_button.clicked.connect(self.maximize_window)
        self.maximize_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                border: none;
                padding: 0;
                margin: 0;
                width: 20px;
                height: 20px;
                background-color: #455A64;
            }
        """)
        layout.addWidget(self.maximize_button)

        self.close_button = QtWidgets.QPushButton("X")
        self.close_button.clicked.connect(self.parent().close)
        self.close_button.setStyleSheet("color: white; font-weight: bold; background-color: #455A64;")
        self.close_button.setFixedSize(20, 20)
        layout.addWidget(self.close_button)

    def minimize_window(self):
        self.parent().showMinimized()

    def maximize_window(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setText("☐")
        else:
            self.parent().showMaximized()
            self.maximize_button.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = True
            self.mouse_pos = event.globalPos() - self.parent().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            self.parent().move(event.globalPos() - self.mouse_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = False
            event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    player = SongPlayer()
    player.set_icon_from_github("https://github.com/boyratata/profile/raw/main/yo.PNG")
    player.show()

    sys.exit(app.exec_())
