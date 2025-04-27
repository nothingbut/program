import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QTableWidget, QPushButton, QSlider, QLabel, QFileDialog,
    QSplitter, QHeaderView, QAbstractItemView, QTableWidgetItem
)
from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import mutagen

class MusicPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MusicLib 音乐播放器")
        self.setGeometry(100, 100, 1000, 600)

        self.music_folders = []
        self.playlist_data = [] # List of dictionaries {path, title, artist, album, track, duration}
        self.current_playing_index = -1
        self.is_shuffle = False

        # Media Player Setup
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # --- Main Layout --- 
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Splitter (Left: Folders, Right: Playlist) --- 
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # --- Left Panel (Folders) --- 
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.folder_list_widget = QListWidget()
        self.folder_list_widget.currentItemChanged.connect(self.load_songs_from_folder)
        left_layout.addWidget(self.folder_list_widget)

        add_folder_button = QPushButton("+")
        add_folder_button.clicked.connect(self.add_music_folder)
        left_layout.addWidget(add_folder_button)

        self.splitter.addWidget(left_panel)

        # --- Right Panel (Playlist) --- 
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.playlist_table_widget = QTableWidget()
        self.playlist_table_widget.setColumnCount(5) # Title, Artist, Album, Track, Duration
        self.playlist_table_widget.setHorizontalHeaderLabels(["歌名", "歌手", "专辑", "音轨", "时长"])
        self.playlist_table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers) # Read-only
        self.playlist_table_widget.setSelectionBehavior(QAbstractItemView.SelectRows) # Select whole row
        self.playlist_table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.playlist_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        self.playlist_table_widget.verticalHeader().setVisible(False) # Hide row numbers
        self.playlist_table_widget.doubleClicked.connect(self.play_selected_song)
        right_layout.addWidget(self.playlist_table_widget)

        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([200, 800]) # Initial sizes

        # --- Bottom Panel (Controls) --- 
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        main_layout.addWidget(bottom_panel)

        self.cover_label = QLabel("封面") # Placeholder for cover art
        self.cover_label.setFixedSize(50, 50)
        self.cover_label.setStyleSheet("border: 1px solid black;") # Basic styling
        bottom_layout.addWidget(self.cover_label)

        self.song_info_label = QLabel("无歌曲播放")
        bottom_layout.addWidget(self.song_info_label)

        prev_button = QPushButton("<")
        prev_button.clicked.connect(self.play_previous)
        bottom_layout.addWidget(prev_button)

        self.play_pause_button = QPushButton("播放")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        bottom_layout.addWidget(self.play_pause_button)

        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        bottom_layout.addWidget(self.progress_slider)

        self.time_label = QLabel("00:00 / 00:00")
        bottom_layout.addWidget(self.time_label)

        next_button = QPushButton(">")
        next_button.clicked.connect(self.play_next)
        bottom_layout.addWidget(next_button)

        self.shuffle_button = QPushButton("顺序")
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        bottom_layout.addWidget(self.shuffle_button)

        # --- Connect Signals --- 
        self.player.positionChanged.connect(self.update_progress)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.handle_media_status)
        self.player.errorOccurred.connect(self.handle_player_error)

    @Slot()
    def add_music_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择音乐文件夹")
        if folder_path and folder_path not in self.music_folders:
            self.music_folders.append(folder_path)
            self.folder_list_widget.addItem(os.path.basename(folder_path))
            # Select the newly added folder to trigger loading songs
            self.folder_list_widget.setCurrentRow(self.folder_list_widget.count() - 1)

    @Slot()
    def load_songs_from_folder(self):
        current_item = self.folder_list_widget.currentItem()
        if not current_item:
            return

        selected_folder_index = self.folder_list_widget.row(current_item)
        if selected_folder_index < 0 or selected_folder_index >= len(self.music_folders):
             return
        
        folder_path = self.music_folders[selected_folder_index]
        self.playlist_data = []
        self.playlist_table_widget.setRowCount(0) # Clear table

        for filename in os.listdir(folder_path):
            if filename.lower().endswith(".mp3"):
                file_path = os.path.join(folder_path, filename)
                try:
                    audio = mutagen.File(file_path, easy=True)
                    if audio:
                        title = audio.get('title', [os.path.splitext(filename)[0]])[0]
                        artist = audio.get('artist', ['未知艺术家'])[0]
                        album = audio.get('album', ['未知专辑'])[0]
                        track = audio.get('tracknumber', ['?'])[0]
                        duration_sec = audio.info.length
                        duration_str = f"{int(duration_sec // 60):02d}:{int(duration_sec % 60):02d}"
                        
                        self.playlist_data.append({
                            'path': file_path,
                            'title': title,
                            'artist': artist,
                            'album': album,
                            'track': track,
                            'duration': duration_str
                        })
                except Exception as e:
                    print(f"无法读取MP3标签 {file_path}: {e}")

        # Populate table
        self.playlist_table_widget.setRowCount(len(self.playlist_data))
        for row, song_data in enumerate(self.playlist_data):
            self.playlist_table_widget.setItem(row, 0, QTableWidgetItem(song_data['title']))
            self.playlist_table_widget.setItem(row, 1, QTableWidgetItem(song_data['artist']))
            self.playlist_table_widget.setItem(row, 2, QTableWidgetItem(song_data['album']))
            self.playlist_table_widget.setItem(row, 3, QTableWidgetItem(str(song_data['track'])))
            self.playlist_table_widget.setItem(row, 4, QTableWidgetItem(song_data['duration']))

    @Slot()
    def play_selected_song(self):
        selected_row = self.playlist_table_widget.currentRow()
        if 0 <= selected_row < len(self.playlist_data):
            self.current_playing_index = selected_row
            self.play_song_at_index(self.current_playing_index)

    def play_song_at_index(self, index):
        if 0 <= index < len(self.playlist_data):
            song_data = self.playlist_data[index]
            file_path = song_data['path']
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()
            
            # Update bottom panel info (basic)
            info_text = f"{song_data['album']}({song_data['track']}): {song_data['title']} - {song_data['artist']}"
            self.song_info_label.setText(info_text)
            self.play_pause_button.setText("暂停")
            # Load and display cover art
            self.load_and_display_cover(file_path)
            # Update duration/progress properly (already handled by signals)
        else:
            print("无效的播放索引")

    def load_and_display_cover(self, file_path):
        try:
            audio = mutagen.File(file_path)
            if audio is None:
                self.cover_label.setPixmap(QPixmap()) # Clear pixmap
                self.cover_label.setText("无封面")
                return

            # Try to get embedded cover art (APIC frame)
            if 'APIC:' in audio.tags:
                artwork = audio.tags['APIC:'].data
                pixmap = QPixmap()
                pixmap.loadFromData(artwork)
                if not pixmap.isNull():
                    self.cover_label.setPixmap(pixmap.scaled(self.cover_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    self.cover_label.setText("") # Clear text
                    return
            # Handle other potential cover art tags if necessary (e.g., 'covr' for older formats)
            # elif 'covr' in audio.tags: ...

            # If no embedded cover found
            self.cover_label.setPixmap(QPixmap()) # Clear pixmap
            self.cover_label.setText("无封面")

        except Exception as e:
            print(f"无法加载封面 {file_path}: {e}")
            self.cover_label.setPixmap(QPixmap())
            self.cover_label.setText("封面错误")

    # --- Playback Control Slots ---
    @Slot()
    def toggle_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_pause_button.setText("播放")
        else:
            if self.current_playing_index != -1:
                self.player.play()
                self.play_pause_button.setText("暂停")
            elif len(self.playlist_data) > 0:
                 # If nothing is selected, play the first song
                 self.play_song_at_index(0)

    @Slot()
    def play_next(self):
        if not self.playlist_data:
            return
        
        if self.is_shuffle:
            import random
            next_index = random.randint(0, len(self.playlist_data) - 1)
        else:
            next_index = (self.current_playing_index + 1) % len(self.playlist_data)
        
        self.play_song_at_index(next_index)

    @Slot()
    def play_previous(self):
        if not self.playlist_data:
            return

        if self.is_shuffle:
            import random
            prev_index = random.randint(0, len(self.playlist_data) - 1)
        else:
            prev_index = (self.current_playing_index - 1 + len(self.playlist_data)) % len(self.playlist_data)
        
        self.play_song_at_index(prev_index)

    @Slot(int)
    def seek_position(self, position):
        self.player.setPosition(position)

    @Slot(int)
    def update_progress(self, position):
        if self.player.duration() > 0:
            self.progress_slider.setValue(position)
            duration = self.player.duration()
            self.time_label.setText(f"{self.format_time(position)} / {self.format_time(duration)}")

    @Slot(int)
    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)
        self.time_label.setText(f"{self.format_time(self.player.position())} / {self.format_time(duration)}")

    @Slot()
    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        self.shuffle_button.setText("随机" if self.is_shuffle else "顺序")

    @Slot(QMediaPlayer.MediaStatus)
    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            # Play next song when current one finishes
            self.play_next()
        elif status == QMediaPlayer.InvalidMedia:
            print("错误: 无效的媒体文件")
            self.song_info_label.setText("错误: 无法播放文件")
            # Optionally play next
            # self.play_next()

    @Slot(QMediaPlayer.Error, str)
    def handle_player_error(self, error, error_string):
        print(f"播放器错误: {error} - {error_string}")
        self.song_info_label.setText(f"播放错误: {error_string}")
        # Optionally try to play the next song
        # self.play_next()

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02d}:{seconds:02d}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayerApp()
    window.show()
    sys.exit(app.exec())