from PySide6.QtGui import QPainter, QPainterPath, QBrush, QColor, QRegion 
from PySide6.QtWidgets import QApplication, QWidget, QPushButton
from PySide6.QtGui import QPainter, QPainterPath, QBrush, QColor
from concurrent.futures import ThreadPoolExecutor
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor
from pypresence import Presence
from PySide6.QtCore import Qt
from zipfile import ZipFile
from io import BytesIO
import webbrowser
import requests
import pygame
import shutil
import json
import time
import sys
import os

class Vance(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vance")
        self.setGeometry(100, 100, 800, 500)
        self.playing = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("""
            background-color: #1C1C1C;
            color: #FFFFFF;
            font-size: 14px;
            border-radius: 10px;
        """)

        pygame.init()
        pygame.mixer.init()

        self.song_dict = {}
        self.current_song = None

        self.ui()
        self.song()
        self.setup_discord_presence()

    def ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        self.song_list = QtWidgets.QListWidget()
        self.song_list.setStyleSheet("""
            color: #FFFFFF;
            background-color: #2E2E2E;
            border-radius: 10px;
            border: 2px solid #3E3E3E;
        """)
        self.song_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.song_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.song_list.itemClicked.connect(self.play)
        layout.addWidget(self.song_list)

        self.volume_slider = self.slider()
        layout.addWidget(self.volume_slider)
        
        self.update_mask(10)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        rect = self.rect()
        painter.fillRect(rect, self.palette().color(QtGui.QPalette.Window))

    def resizeEvent(self, event):
        radius = 10
        self.update_mask(radius)

    def update_mask(self, radius):
        mask_region = self.rounded_mask(self.size(), radius)
        self.setMask(mask_region)

    def rounded_mask(self, size, radius):
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(0, 0, size.width(), size.height()), radius, radius)
        return QtGui.QRegion(path.toFillPolygon().toPolygon())
        
    def slider(self):
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(70)
        slider.setToolTip("Volume")
        slider.valueChanged.connect(self.volume)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background-color: #4E4E4E;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #171716;
                width: 10px;
                margin: -5px 0;
                border-radius: 5px;
           }
        """)
        return slider

    def song(self):
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

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.get_song, url) for url in urls]
            for future in futures:
                future.result()

    def get_song(self, url):
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
            
    def setup_discord_presence(self):
        self.client_id = "1260552765160034405"  # Replace with your own client ID
        self.discord_presence = Presence(client_id=self.client_id)
        try:
            self.discord_presence.connect()
            self.update_presence()
        except Exception as e:
            print(f"Error connecting to Discord RPC: {e}")

    def update_presence(self):
        presence_data = {
            "state": "Listening to music",
            "details": f"Now playing: {self.current_song}" if self.current_song else "Browsing songs",
            "large_image": "red"  # Replace with the key of your large image
        }
        self.discord_presence.update(**presence_data)

    def closeEvent(self, event):
        try:
            self.discord_presence.close()
        except Exception as e:
            print(f"Error closing Discord RPC connection: {e}")

    def play(self, item):
        song_name = item.text().split('. ', 1)[-1]
        song_data = self.song_dict.get(song_name)

        if song_data:
            if song_name == self.current_song:
                self.pause()
            else:
                self.new(song_name, song_data)
        else:
            print(f"Failed to play song: {item.text()}")

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.playing = not self.playing

    def new(self, song_name, song_data):
        if self.playing:
            pygame.mixer.music.stop()
        self.playing = True
        song_data_io = BytesIO(song_data)
        pygame.mixer.music.load(song_data_io)
        
        # Ensure self.volume_slider is not None before accessing its value
        if self.volume_slider:
            pygame.mixer.music.set_volume(self.volume_slider.value() / 100)
        else:
            print("Volume slider is not initialized correctly.")

        pygame.mixer.music.play(-1)
        self.current_song = song_name
        QtCore.QTimer.singleShot(100, self.check)

    def volume(self, value):
        pygame.mixer.music.set_volume(value / 100)

    def check(self):
        if not pygame.mixer.music.get_busy():
            self.current_song = None

class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #333333;")
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.title_label = QtWidgets.QLabel("Vance")
        self.title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.maximized = False  # Add this line to track the window state
        self.search_bar = None
        self.maximize_button = None  # Initialize maximize_button attribute

        self.buttons(layout)  # Ensure this method initializes maximize_button

    def buttons(self, layout):
        base_url = "https://raw.githubusercontent.com/boyratata/gui/main/"
        icon_dir = "icons/"
        os.makedirs(icon_dir, exist_ok=True)

        other_buttons = [
            ("volume.png", "Volume", 25, self.svolume),
            ("github.png", "GitHub", 25, self.github),
            ("save.png", "Save", 25, self.upload),
            ("search.png", "Search", 25, self.search),
            ("minus.png", "Minimize", 25, self.minimize),
            ("maximize.png", "Maximize", 25, self.maximize, "maximize_button"),
            ("close.png", "Close", 25, self.close_app),
        ]

        for img_name, tooltip, size, action, *args in other_buttons:
            img_url = f"{base_url}{img_name}"
            save_path = os.path.join(icon_dir, img_name)
            
            if not os.path.exists(save_path):
                self.download_icon(img_url, save_path)

            btn = QtWidgets.QPushButton()
            btn.setIcon(QtGui.QIcon(save_path))
            btn.setIconSize(QtCore.QSize(size, size))
            btn.setFixedSize(size, size)
            btn.clicked.connect(action)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("border: none; background-color: #555555;")
            if args:
                btn.setObjectName(args[0])
                if args[0] == "maximize_button":
                    self.maximize_button = btn  # Assign maximize_button attribute
            layout.addWidget(btn)

    def download_icon(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded {url} successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")
        except Exception as e:
            print(f"An error occurred while downloading {url}: {e}")
            
    def github(self):
        url = "https://github.com/boyratata"
        webbrowser.open(url)
        
    def minimize(self):
        self.parent().showMinimized()

    def maximize(self):
        if self.maximized:
            self.parent().showNormal()  # Restore normal size
            self.maximize_button.setIcon(QtGui.QIcon("icons/maximize.png"))  # Change button icon
        else:
            self.parent().showMaximized()  # Maximize the window
            self.maximize_button.setIcon(QtGui.QIcon("icons/minimize.png"))  # Change button icon
        self.maximized = not self.maximized 
      
    def close_app(self):
        self.parent().close()

    def upload(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("Music Files (*.mp3)")
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if file_dialog.exec():
            for file_path in file_dialog.selectedFiles():
                self.file(file_path)

    def file(self, file_path):
        if file_path.endswith('.mp3'):
            upload_dir = 'songs'
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

    def search(self):
        if self.search_bar is None:
            self.search_bar = QtWidgets.QLineEdit()
            self.search_bar.setPlaceholderText("Search for a song...")
            self.search_bar.setStyleSheet("""
                background-color: #2E2E2E;
                color: #FFFFFF;
                padding: 5px;
                border: 2px solid #3E3E3E;
                border-radius: 10px;
            """)
            self.search_bar.textChanged.connect(self.filters)
            self.layout().insertWidget(2, self.search_bar)

        self.search_bar.setVisible(not self.search_bar.isVisible())

    def filters(self):
        if self.search_bar:
            search_query = self.search_bar.text().lower()
            song_list = self.parent().song_list
            for index in range(song_list.count()):
                item = song_list.item(index)
                item.setHidden(search_query not in item.text().lower())
                
    def svolume(self):
        parent = self.parent()
        if hasattr(parent, 'volume_slider'):
            volume_slider = parent.volume_slider
            if volume_slider.isHidden():
                volume_slider.show()
            else:
                volume_slider.hide()
        else:
            print("Volume slider not found in parent widget.")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = True
            self.mouse_pos = event.globalPosition().toPoint() - self.parent().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            self.parent().move(event.globalPosition().toPoint() - self.mouse_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = False
            event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = Vance()
    player.show()
    sys.exit(app.exec())