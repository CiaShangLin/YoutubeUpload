"""
影片編輯對話框
用於新增或編輯單一影片的資訊
"""

import os
import re
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui
from video_item import VideoItem, MatchType


class VideoEditorDialog(QtWidgets.QDialog):
    """影片編輯對話框"""
    
    # 播放清單 ID 常數
    PLAYLIST_SC2_RANK_ID = "PL8TREsr2ZmqbIAM5TODn26C8my3cNiRev"
    PLAYLIST_PVP_ID = "PL8TREsr2ZmqbGXupnsOkyzoFTkr12cmVF"
    PLAYLIST_PVZ_ID = "PL8TREsr2ZmqaY8-tTDPvTLYRH38dtvY4I"
    PLAYLIST_PVT_ID = "PL8TREsr2ZmqYpi_IM1zSQSarofDQftjLj"
    
    def __init__(self, video: VideoItem = None, parent=None):
        """
        初始化對話框
        
        Args:
            video: 要編輯的影片（None 表示新增）
            parent: 父視窗
        """
        super().__init__(parent)
        self.video = video
        self.is_edit_mode = video is not None
        self.setupUi()
        
        if self.is_edit_mode:
            self.load_video_data()
    
    def setupUi(self):
        """設置 UI"""
        self.setObjectName("VideoEditorDialog")
        self.setWindowTitle("編輯影片" if self.is_edit_mode else "新增影片")
        self.resize(600, 550)
        
        # 主佈局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # === 檔案選擇區 ===
        file_group = QtWidgets.QGroupBox("檔案選擇")
        file_layout = QtWidgets.QVBoxLayout(file_group)
        
        # 影片檔案
        video_layout = QtWidgets.QHBoxLayout()
        self.btSelectVideo = QtWidgets.QPushButton("選擇影片")
        self.btSelectVideo.setFixedWidth(100)
        self.btSelectVideo.clicked.connect(self.select_video_file)
        self.tvVideoPath = QtWidgets.QLabel("未選擇")
        self.tvVideoPath.setStyleSheet("color: gray;")
        video_layout.addWidget(self.btSelectVideo)
        video_layout.addWidget(self.tvVideoPath, 1)
        file_layout.addLayout(video_layout)
        
        # 縮圖檔案
        thumbnail_layout = QtWidgets.QHBoxLayout()
        self.btSelectThumbnail = QtWidgets.QPushButton("選擇縮圖")
        self.btSelectThumbnail.setFixedWidth(100)
        self.btSelectThumbnail.clicked.connect(self.select_thumbnail_file)
        self.tvThumbnailPath = QtWidgets.QLabel("未選擇")
        self.tvThumbnailPath.setStyleSheet("color: gray;")
        thumbnail_layout.addWidget(self.btSelectThumbnail)
        thumbnail_layout.addWidget(self.tvThumbnailPath, 1)
        file_layout.addLayout(thumbnail_layout)
        
        # Replay 檔案
        replay_layout = QtWidgets.QHBoxLayout()
        self.btSelectReplay = QtWidgets.QPushButton("選擇 RP")
        self.btSelectReplay.setFixedWidth(100)
        self.btSelectReplay.clicked.connect(self.select_replay_file)
        self.tvReplayPath = QtWidgets.QLabel("未選擇")
        self.tvReplayPath.setStyleSheet("color: gray;")
        replay_layout.addWidget(self.btSelectReplay)
        replay_layout.addWidget(self.tvReplayPath, 1)
        file_layout.addLayout(replay_layout)
        
        main_layout.addWidget(file_group)
        
        # === 基本資訊區 ===
        info_group = QtWidgets.QGroupBox("基本資訊")
        info_layout = QtWidgets.QFormLayout(info_group)
        
        # 遊戲名稱
        self.gameInput = QtWidgets.QLineEdit()
        self.gameInput.setText("StarCraft II")
        info_layout.addRow("遊戲名稱:", self.gameInput)
        
        # 發布時間
        self.publishTime = QtWidgets.QDateTimeEdit()
        self.publishTime.setCalendarPopup(True)
        self.publishTime.setDateTime(QtCore.QDateTime(QtCore.QDate.currentDate(), QtCore.QTime(18, 0)))
        info_layout.addRow("發布時間:", self.publishTime)
        
        main_layout.addWidget(info_group)
        
        # === 播放清單區 ===
        playlist_group = QtWidgets.QGroupBox("播放清單")
        playlist_layout = QtWidgets.QHBoxLayout(playlist_group)
        
        self.ckbRank = QtWidgets.QCheckBox("SC2天梯")
        self.ckbRank.setChecked(True)
        self.ckbPVP = QtWidgets.QCheckBox("PVP")
        self.ckbPVZ = QtWidgets.QCheckBox("PVZ")
        self.ckbPVT = QtWidgets.QCheckBox("PVT")
        
        playlist_layout.addWidget(self.ckbRank)
        playlist_layout.addWidget(self.ckbPVP)
        playlist_layout.addWidget(self.ckbPVZ)
        playlist_layout.addWidget(self.ckbPVT)
        playlist_layout.addStretch()
        
        main_layout.addWidget(playlist_group)
        
        # === 字幕語言區 ===
        subtitle_group = QtWidgets.QGroupBox("字幕語言")
        subtitle_layout = QtWidgets.QHBoxLayout(subtitle_group)
        
        self.ckbEn = QtWidgets.QCheckBox("英文")
        self.ckbEn.setChecked(True)
        self.ckbTW = QtWidgets.QCheckBox("中文（台灣）")
        self.ckbTW.setChecked(True)
        
        subtitle_layout.addWidget(self.ckbEn)
        subtitle_layout.addWidget(self.ckbTW)
        subtitle_layout.addStretch()
        
        main_layout.addWidget(subtitle_group)
        
        # === 標題區 ===
        title_group = QtWidgets.QGroupBox("標題")
        title_layout = QtWidgets.QVBoxLayout(title_group)
        
        self.textEditTitle = QtWidgets.QTextEdit()
        self.textEditTitle.setMaximumHeight(60)
        title_layout.addWidget(self.textEditTitle)
        
        main_layout.addWidget(title_group)
        
        # === 按鈕區 ===
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.btCancel = QtWidgets.QPushButton("取消")
        self.btCancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btCancel)
        
        self.btConfirm = QtWidgets.QPushButton("確定")
        self.btConfirm.clicked.connect(self.confirm)
        button_layout.addWidget(self.btConfirm)
        
        main_layout.addLayout(button_layout)
    
    def select_video_file(self):
        """選擇影片檔案"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "選擇影片檔案",
            "",
            "影片檔案 (*.mp4 *.avi *.mkv *.mov);;所有檔案 (*)"
        )
        
        if file_path:
            self.tvVideoPath.setText(file_path)
            self.tvVideoPath.setStyleSheet("color: black;")
            
            # 自動解析標題和對戰類型
            title = self.parse_title(file_path)
            self.textEditTitle.setPlainText(title)
            
            match_type = self.parse_match_type(file_path)
            self.update_playlist_checkboxes(match_type)
    
    def select_thumbnail_file(self):
        """選擇縮圖檔案"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "選擇縮圖檔案",
            "",
            "圖片檔案 (*.jpg *.jpeg *.png);;所有檔案 (*)"
        )
        
        if file_path:
            self.tvThumbnailPath.setText(file_path)
            self.tvThumbnailPath.setStyleSheet("color: black;")
    
    def select_replay_file(self):
        """選擇 Replay 檔案"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "選擇 Replay 檔案",
            "",
            "Replay 檔案 (*.SC2Replay);;所有檔案 (*)"
        )
        
        if file_path:
            self.tvReplayPath.setText(file_path)
            self.tvReplayPath.setStyleSheet("color: black;")
    
    def parse_title(self, file_path: str) -> str:
        """
        從檔案路徑解析標題
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            str: 解析後的標題
        """
        basename = os.path.basename(file_path)
        filename = basename.rsplit(".", 1)[0].strip()
        
        # 尋找【StarCraft II】開頭的部分
        pattern = r"(【StarCraft II】.*?KR Server)"
        match = re.search(pattern, filename)
        
        if match:
            game_name = self.gameInput.text() if self.gameInput.text() else "StarCraft II"
            return match.group(1).replace("【StarCraft II】", f"【{game_name}】")
        
        return filename
    
    def parse_match_type(self, file_path: str) -> MatchType:
        """
        從檔案名稱解析對戰類型
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            MatchType: 對戰類型
        """
        basename = os.path.basename(file_path)
        pattern = r".*\((Protoss|Zerg|Terran)(?:\s*\d*)\)\s*vs\s*.*\((Protoss|Zerg|Terran)(?:\s*\d*)\)"
        match = re.search(pattern, basename, re.IGNORECASE)
        
        if match:
            left_race, right_race = match.groups()
            
            if left_race.lower() == "protoss" and right_race.lower() == "protoss":
                return MatchType.PVP
            elif left_race.lower() == "protoss" and right_race.lower() == "zerg":
                return MatchType.PVZ
            elif left_race.lower() == "protoss" and right_race.lower() == "terran":
                return MatchType.PVT
        
        return MatchType.UNKNOWN
    
    def update_playlist_checkboxes(self, match_type: MatchType):
        """
        根據對戰類型更新播放清單勾選狀態
        
        Args:
            match_type: 對戰類型
        """
        self.ckbPVP.setChecked(match_type == MatchType.PVP)
        self.ckbPVZ.setChecked(match_type == MatchType.PVZ)
        self.ckbPVT.setChecked(match_type == MatchType.PVT)
    
    def load_video_data(self):
        """載入影片資料到 UI"""
        if not self.video:
            return
        
        # 檔案路徑
        if self.video.video_path:
            self.tvVideoPath.setText(self.video.video_path)
            self.tvVideoPath.setStyleSheet("color: black;")
        
        if self.video.thumbnail_path:
            self.tvThumbnailPath.setText(self.video.thumbnail_path)
            self.tvThumbnailPath.setStyleSheet("color: black;")
        
        if self.video.replay_path:
            self.tvReplayPath.setText(self.video.replay_path)
            self.tvReplayPath.setStyleSheet("color: black;")
        
        # 基本資訊
        self.gameInput.setText(self.video.game_name)
        if self.video.publish_time:
            qt_datetime = QtCore.QDateTime.fromString(
                self.video.publish_time.strftime("%Y-%m-%d %H:%M"),
                "yyyy-MM-dd HH:mm"
            )
            self.publishTime.setDateTime(qt_datetime)
        
        # 播放清單
        self.ckbRank.setChecked(self.PLAYLIST_SC2_RANK_ID in self.video.playlist_ids)
        self.ckbPVP.setChecked(self.PLAYLIST_PVP_ID in self.video.playlist_ids)
        self.ckbPVZ.setChecked(self.PLAYLIST_PVZ_ID in self.video.playlist_ids)
        self.ckbPVT.setChecked(self.PLAYLIST_PVT_ID in self.video.playlist_ids)
        
        # 字幕語言
        self.ckbEn.setChecked("en" in self.video.subtitle_languages)
        self.ckbTW.setChecked("zh-TW" in self.video.subtitle_languages)
        
        # 標題
        self.textEditTitle.setPlainText(self.video.title)
    
    def confirm(self):
        """確認並返回影片資料"""
        # 驗證必填欄位
        video_path = self.tvVideoPath.text()
        if video_path == "未選擇" or not video_path:
            QtWidgets.QMessageBox.warning(self, "警告", "請選擇影片檔案！")
            return
        
        title = self.textEditTitle.toPlainText().strip()
        if not title:
            QtWidgets.QMessageBox.warning(self, "警告", "請輸入標題！")
            return
        
        # 收集播放清單 ID
        playlist_ids = []
        if self.ckbRank.isChecked():
            playlist_ids.append(self.PLAYLIST_SC2_RANK_ID)
        if self.ckbPVP.isChecked():
            playlist_ids.append(self.PLAYLIST_PVP_ID)
        if self.ckbPVZ.isChecked():
            playlist_ids.append(self.PLAYLIST_PVZ_ID)
        if self.ckbPVT.isChecked():
            playlist_ids.append(self.PLAYLIST_PVT_ID)
        
        # 收集字幕語言
        subtitle_languages = []
        if self.ckbEn.isChecked():
            subtitle_languages.append("en")
        if self.ckbTW.isChecked():
            subtitle_languages.append("zh-TW")
        
        # 解析對戰類型
        match_type = MatchType.UNKNOWN
        if self.ckbPVP.isChecked():
            match_type = MatchType.PVP
        elif self.ckbPVZ.isChecked():
            match_type = MatchType.PVZ
        elif self.ckbPVT.isChecked():
            match_type = MatchType.PVT
        
        # 轉換發布時間
        qt_datetime = self.publishTime.dateTime()
        publish_time = datetime(
            qt_datetime.date().year(),
            qt_datetime.date().month(),
            qt_datetime.date().day(),
            qt_datetime.time().hour(),
            qt_datetime.time().minute()
        )
        
        # 創建或更新 VideoItem
        thumbnail_path = self.tvThumbnailPath.text() if self.tvThumbnailPath.text() != "未選擇" else None
        replay_path = self.tvReplayPath.text() if self.tvReplayPath.text() != "未選擇" else None
        
        if self.is_edit_mode and self.video:
            # 編輯模式：更新現有影片
            self.video.video_path = video_path
            self.video.title = title
            self.video.thumbnail_path = thumbnail_path
            self.video.replay_path = replay_path
            self.video.game_name = self.gameInput.text()
            self.video.publish_time = publish_time
            self.video.playlist_ids = playlist_ids
            self.video.subtitle_languages = subtitle_languages
            self.video.match_type = match_type
        else:
            # 新增模式：創建新影片
            self.video = VideoItem(
                video_path=video_path,
                title=title,
                thumbnail_path=thumbnail_path,
                replay_path=replay_path,
                game_name=self.gameInput.text(),
                publish_time=publish_time,
                playlist_ids=playlist_ids,
                subtitle_languages=subtitle_languages,
                match_type=match_type
            )
        
        self.accept()
    
    def get_video(self) -> VideoItem:
        """
        取得影片資料
        
        Returns:
            VideoItem: 影片物件
        """
        return self.video


if __name__ == '__main__':
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    
    # 測試新增模式
    dialog = VideoEditorDialog()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        video = dialog.get_video()
        print("=== 新增的影片 ===")
        print(f"標題: {video.title}")
        print(f"影片路徑: {video.video_path}")
        print(f"對戰類型: {video.match_type_text}")
        print(f"發布時間: {video.publish_time_str}")
    
    sys.exit(0)
