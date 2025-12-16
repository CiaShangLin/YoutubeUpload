import os
import sys
from typing import List
from PyQt5 import QtCore, QtWidgets, QtGui

from token_manager import TokenManager
from video_item import VideoItem, UploadStatus
from dialogs.token_status_dialog import TokenStatusDialog
from dialogs.video_editor_dialog import VideoEditorDialog


class BatchUploadWindow(QtWidgets.QMainWindow):
    """批次上傳主視窗"""
    
    def __init__(self):
        super().__init__()
        self.token_manager = TokenManager()
        self.video_list: List[VideoItem] = []
        self.setupUi()
    
    def setupUi(self):
        """設置 UI"""
        self.setObjectName("BatchUploadWindow")
        self.setWindowTitle("YouTube 批次上傳器")
        self.setWindowIcon(QtGui.QIcon('icon.jpg'))
        self.resize(900, 600)
        
        # 中央 Widget
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        
        # 主佈局
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # === 頂部工具列 ===
        toolbar_layout = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("影片上傳列表")
        title_font = QtGui.QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        toolbar_layout.addWidget(title_label)
        
        toolbar_layout.addStretch()
        
        self.btCheckToken = QtWidgets.QPushButton("🔐 檢查 Token")
        self.btCheckToken.clicked.connect(self.check_token_status)
        toolbar_layout.addWidget(self.btCheckToken)
        
        main_layout.addLayout(toolbar_layout)
        
        # === 影片列表表格 ===
        self.video_table = QtWidgets.QTableWidget()
        self.video_table.setColumnCount(6)
        self.video_table.setHorizontalHeaderLabels([
            "#", "標題", "對戰類型", "發布時間", "狀態", "操作"
        ])
        
        # 設定欄位寬度
        header = self.video_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # #
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)  # 標題
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)  # 對戰類型
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)  # 發布時間
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)  # 狀態
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)  # 操作
        
        # 設定選擇模式
        self.video_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.video_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        main_layout.addWidget(self.video_table)
        
        # === 按鈕列 ===
        button_layout = QtWidgets.QHBoxLayout()
        
        self.btAddVideo = QtWidgets.QPushButton("➕ 新增影片")
        self.btAddVideo.clicked.connect(self.add_video)
        button_layout.addWidget(self.btAddVideo)
        
        self.btRemoveVideo = QtWidgets.QPushButton("➖ 移除影片")
        self.btRemoveVideo.clicked.connect(self.remove_video)
        button_layout.addWidget(self.btRemoveVideo)
        
        self.btEditVideo = QtWidgets.QPushButton("✏️ 編輯影片")
        self.btEditVideo.clicked.connect(self.edit_video)
        button_layout.addWidget(self.btEditVideo)
        
        button_layout.addStretch()
        
        self.btStartUpload = QtWidgets.QPushButton("🚀 開始批次上傳")
        self.btStartUpload.clicked.connect(self.start_batch_upload)
        self.btStartUpload.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        button_layout.addWidget(self.btStartUpload)
        
        main_layout.addLayout(button_layout)
        
        # === 進度顯示 ===
        progress_layout = QtWidgets.QHBoxLayout()
        
        self.progress_label = QtWidgets.QLabel("就緒")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar, 1)
        
        main_layout.addLayout(progress_layout)
    
    def check_token_status(self):
        """開啟 Token 狀態檢查對話框"""
        dialog = TokenStatusDialog(self.token_manager, self)
        dialog.exec_()
    
    def add_video(self):
        """新增影片"""
        dialog = VideoEditorDialog(parent=self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            video = dialog.get_video()
            self.video_list.append(video)
            self.refresh_video_table()
    
    def remove_video(self):
        """移除選中的影片"""
        current_row = self.video_table.currentRow()
        if current_row < 0:
            QtWidgets.QMessageBox.warning(self, "警告", "請先選擇要移除的影片！")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "確認",
            "確定要移除這部影片嗎？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            del self.video_list[current_row]
            self.refresh_video_table()
    
    def edit_video(self):
        """編輯選中的影片"""
        current_row = self.video_table.currentRow()
        if current_row < 0:
            QtWidgets.QMessageBox.warning(self, "警告", "請先選擇要編輯的影片！")
            return
        
        video = self.video_list[current_row]
        dialog = VideoEditorDialog(video=video, parent=self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.refresh_video_table()
    
    def refresh_video_table(self):
        """刷新影片列表表格"""
        self.video_table.setRowCount(len(self.video_list))
        
        for row, video in enumerate(self.video_list):
            # 序號
            num_item = QtWidgets.QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.video_table.setItem(row, 0, num_item)
            
            # 標題
            title_item = QtWidgets.QTableWidgetItem(video.title)
            self.video_table.setItem(row, 1, title_item)
            
            # 對戰類型
            match_type_item = QtWidgets.QTableWidgetItem(video.match_type_text)
            match_type_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.video_table.setItem(row, 2, match_type_item)
            
            # 發布時間
            time_item = QtWidgets.QTableWidgetItem(video.publish_time_str)
            time_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.video_table.setItem(row, 3, time_item)
            
            # 狀態
            status_item = QtWidgets.QTableWidgetItem(video.status_text)
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            
            # 根據狀態設定顏色
            if video.status == UploadStatus.COMPLETED:
                status_item.setForeground(QtGui.QColor("green"))
            elif video.status == UploadStatus.FAILED:
                status_item.setForeground(QtGui.QColor("red"))
            elif video.status == UploadStatus.UPLOADING:
                status_item.setForeground(QtGui.QColor("blue"))
            
            self.video_table.setItem(row, 4, status_item)
            
            # 操作按鈕（預留）
            action_widget = QtWidgets.QWidget()
            action_layout = QtWidgets.QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(4)
            
            # 可以在這裡加入單獨的操作按鈕
            # 例如：查看詳情、重新上傳等
            
            self.video_table.setCellWidget(row, 5, action_widget)
    
    def start_batch_upload(self):
        """開始批次上傳"""
        if not self.video_list:
            QtWidgets.QMessageBox.warning(self, "警告", "影片列表為空，請先新增影片！")
            return
        
        # 檢查是否有待上傳的影片
        pending_videos = [v for v in self.video_list if v.status == UploadStatus.PENDING]
        if not pending_videos:
            QtWidgets.QMessageBox.information(self, "提示", "沒有待上傳的影片！")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "確認",
            f"即將上傳 {len(pending_videos)} 部影片，是否繼續？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # TODO: 實作批次上傳邏輯（Phase 3）
            QtWidgets.QMessageBox.information(
                self,
                "開發中",
                "批次上傳功能將在 Phase 3 實作！\n目前僅完成 UI 和資料模型。"
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BatchUploadWindow()
    window.show()
    sys.exit(app.exec_())