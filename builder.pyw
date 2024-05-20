from PySide6 import QtWidgets, QtGui, QtCore
import sys
import requests
import pygame
import os
import shutil
from io import BytesIO
from zipfile import ZipFile

class SongPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Song-Advance")
        self.setGeometry(100, 100, 800, 500)
        self.current_song_playing = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #263238; color: #FFFFFF; font-size: 14px; border-radius: 10px;")

        pygame.init()
        pygame.mixer.init()

        self.song_dict = {}
        self.current_song = None

        self.init_ui()
        self.fetch_songs()

    def set_icon_from_github(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            icon_data = response.content
            icon_pixmap = QtGui.QPixmap()
            icon_pixmap.loadFromData(icon_data)
            self.setWindowIcon(QtGui.QIcon(icon_pixmap))
        except requests.RequestException as e:
            print(f"Failed to download icon from GitHub: {e}")

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        self.song_list = QtWidgets.QListWidget()
        self.song_list.setStyleSheet("color: #FFFFFF; background-color: #37474F; border-radius: 10px; padding: 10px; border: 2px solid #455A64;")
        self.song_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.song_list.itemClicked.connect(self.toggle_play_pause)
        layout.addWidget(self.song_list)

        self.volume_slider = self.create_volume_slider()
        layout.addWidget(self.volume_slider)

        self.setLayout(layout)

    def create_volume_slider(self):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(70)
        slider.setToolTip("Volume")
        slider.valueChanged.connect(self.change_volume)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #546E7A;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #B39CD0;
                width: 10px;
                margin: -5px 0;
                border-radius: 5px;
           }
        """)
        return slider

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
            "https://github.com/boyratata/song-list/raw/main/upload.zip",
            "https://github.com/boyratata/song-list/raw/main/b.zip"
        ]
        for url in urls:
            self.fetch_and_add_songs(url)

    def fetch_and_add_songs(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            with ZipFile(BytesIO(response.content)) as z:
                for filename in z.namelist():
                    if filename.endswith('.mp3'):
                        song_name = filename.split('.')[0]
                        song_data = z.read(filename)
                        self.song_dict[song_name] = song_data
                        self.song_list.addItem(f"{len(self.song_dict)}. {song_name}")
        except Exception as e:
            print(f"Error fetching songs from {url}: {e}")

    def toggle_play_pause(self, item):
        song_name = item.text().split('. ', 1)[-1]
        song_data = self.song_dict.get(song_name)

        if song_data:
            if song_name == self.current_song:
                self.toggle_pause()
            else:
                self.play_new_song(song_name, song_data)
        else:
            print(f"Failed to play song: {item.text()}")

    def toggle_pause(self):
        if self.current_song_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.current_song_playing = not self.current_song_playing

    def play_new_song(self, song_name, song_data):
        if self.current_song_playing:
            pygame.mixer.music.stop()
        self.current_song_playing = True
        song_data_io = BytesIO(song_data)
        pygame.mixer.music.load(song_data_io)
        pygame.mixer.music.set_volume(self.volume_slider.value() / 100)
        pygame.mixer.music.play(-1)
        self.current_song = song_name
        QtCore.QTimer.singleShot(100, self.check_song_finished)

    def change_volume(self, value):
        pygame.mixer.music.set_volume(value / 100)

    def check_song_finished(self):
        if not pygame.mixer.music.get_busy():
            self.current_song = None

class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #B39CD0;")
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        owner_image_url = "https://github.com/boyratata/profile/raw/main/yo.PNG"
        owner_label = QtWidgets.QLabel()
        owner_label.setPixmap(self.fetch_pixmap(owner_image_url).scaled(30, 30, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        owner_label.setStyleSheet("background-color: #FBEAFF;")
        layout.addWidget(owner_label)

        self.title_label = QtWidgets.QLabel("Song Player")
        self.title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.create_buttons(layout)

    def fetch_pixmap(self, url):
        response = requests.get(url)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(response.content)
        return pixmap

    def create_buttons(self, layout):
        buttons = [
            ("+", self.upload_mp3, 20, "color: white; font-weight: bold; background-color: #455A64;"),
            ("🔍", self.toggle_search_bar, 20, "color: white; font-weight: bold; background-color: #455A64;"),
            ("━", self.minimize_window, 20, "color: white; font-weight: bold; background-color: #455A64;"),
            ("☐", self.maximize_window, 20, "color: white; font-weight: bold; background-color: #455A64;"),
            ("X", self.parent().close, 20, "color: white; font-weight: bold; background-color: #455A64;"),
        ]

        for text, func, size, style in buttons:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(func)
            btn.setFixedSize(size, size)
            btn.setStyleSheet(style)
            layout.addWidget(btn)

    def minimize_window(self):
        self.parent().showMinimized()

    def maximize_window(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

    def upload_mp3(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("Music Files (*.mp3)")
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if file_dialog.exec_():
            for file_path in file_dialog.selectedFiles():
                self.handle_uploaded_file(file_path)

    def handle_uploaded_file(self, file_path):
        if file_path.endswith('.mp3'):
            upload_dir = 'uploaded_songs'
            os.makedirs(upload_dir, exist_ok=True)

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(upload_dir, file_name)
            try:
                shutil.copyfile(file_path, destination_path)
                song_name = file_name.split('.')[0]
                with open(destination_path, 'rb') as song_file:
                    song_data = song_file.read()

                    self.parent().song_dict[song_name] = song_data

                    self.parent().song_list.addItem(f"{len(self.parent().song_dict)}. {song_name}")
                print(f"Uploaded song '{song_name}' saved successfully.")
            except Exception as e:
                print(f"Error handling uploaded file: {e}")
        else:
            print("Unsupported file format. Only MP3 files are allowed.")

    def toggle_search_bar(self):
        if not hasattr(self, 'search_bar'):
            self.search_bar = QtWidgets.QLineEdit()
            self.search_bar.setPlaceholderText("Search Songs")
            self.search_bar.setStyleSheet("background: #263238; border-radius: 10px; color: white; padding: 5px; border: none;")
            self.search_bar.textChanged.connect(self.filter_songs)
            self.layout().addWidget(self.search_bar)
        else:
            self.search_bar.setHidden(not self.search_bar.isHidden())

    def filter_songs(self):
        search_query = self.search_bar.text().lower()
        song_list = self.parent().song_list
        for index in range(song_list.count()):
            item = song_list.item(index)
            item.setHidden(search_query not in item.text().lower())

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

    sys.exit(app.exec())
