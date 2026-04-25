import json
import os
import sys
from typing import List
from PyQt5 import QtCore, QtWidgets, QtGui

from token_manager import TokenManager
from video_item import VideoItem, UploadStatus
from dialogs.token_status_dialog import TokenStatusDialog
from dialogs.video_editor_dialog import VideoEditorDialog
from uploaders.youtube_uploader import YouTubeUploader
from uploaders.bilibili_uploader import BilibiliUploader


class BatchUploadWindow(QtWidgets.QMainWindow):
    """批次上傳主視窗"""
    
    def __init__(self):
        super().__init__()
        self.token_manager = TokenManager()
        self.youtube_uploader = YouTubeUploader(self.token_manager)
        self.video_list: List[VideoItem] = []
        self.setupUi()
    
    def setupUi(self):
        """設置 UI"""
        self.setObjectName("BatchUploadWindow")
        self.setWindowTitle("YouTube 批次上傳器")
        self.setWindowIcon(QtGui.QIcon('assets/icon.jpg'))
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
            self._execute_batch_upload(pending_videos)
    
    def _execute_batch_upload(self, videos: List[VideoItem]):
        """
        執行批次上傳
        
        Args:
            videos: 待上傳的影片列表
        """
        # 禁用上傳按鈕
        self.btStartUpload.setEnabled(False)
        self.btAddVideo.setEnabled(False)
        self.btRemoveVideo.setEnabled(False)
        self.btEditVideo.setEnabled(False)
        
        # 顯示進度條
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(videos))
        self.progress_bar.setValue(0)
        
        total = len(videos)
        success_count = 0
        fail_count = 0
        
        for index, video in enumerate(videos, 1):
            try:
                # 更新進度
                self.progress_label.setText(f"正在上傳 {index}/{total}: {video.title}")
                self.progress_bar.setValue(index - 1)
                QtWidgets.QApplication.processEvents()
                
                # 設定為上傳中
                video.set_status(UploadStatus.UPLOADING)
                self.refresh_video_table()
                QtWidgets.QApplication.processEvents()
                
                # 1. 上傳影片
                print(f"\n{'='*60}")
                print(f"開始上傳第 {index}/{total} 部影片")
                print(f"標題: {video.title}")
                print(f"{'='*60}")
                
                video_id = self.youtube_uploader.upload(video)
                video.set_video_id(video_id)
                
                # 2. 設定縮圖
                if video.has_thumbnail:
                    print(f"設定縮圖...")
                    self.youtube_uploader.set_thumbnail(video_id, video.thumbnail_path)
                
                # 3. 加入播放清單
                if video.playlist_ids:
                    print(f"加入播放清單...")
                    self.youtube_uploader.add_to_playlist(video_id, video.playlist_ids)
                
                # 4. 添加多國語言
                print(f"添加多國語言...")
                self.youtube_uploader.add_localizations(video_id, video.replay_url or "")
                
                # 5. 同步上傳 B站
                if video.upload_to_bilibili:
                    print(f"同步上傳 B站...")
                    try:
                        bilibili_uploader = BilibiliUploader(self.token_manager)
                        bvid = bilibili_uploader.upload(video)
                        video.bilibili_video_id = bvid
                        print(f"✅ B站上傳成功！BVID: {bvid}")
                    except Exception as bilibili_err:
                        print(f"⚠️ B站上傳失敗: {bilibili_err}")
                        QtWidgets.QMessageBox.warning(
                            self,
                            "B站上傳失敗",
                            f"YouTube 上傳成功，但 B站上傳失敗：\n{bilibili_err}"
                        )

                # 設定為完成
                video.set_status(UploadStatus.COMPLETED)
                success_count += 1
                
                print(f"✅ 第 {index}/{total} 部影片上傳成功！")
                
            except Exception as e:
                # 設定為失敗
                error_msg = str(e)
                video.set_status(UploadStatus.FAILED, error_msg)
                fail_count += 1
                
                print(f"❌ 第 {index}/{total} 部影片上傳失敗: {error_msg}")
                
                # 詢問是否繼續
                if index < total:
                    reply = QtWidgets.QMessageBox.question(
                        self,
                        "上傳失敗",
                        f"影片「{video.title}」上傳失敗：\n{error_msg}\n\n是否繼續上傳剩餘影片？",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                    )
                    
                    if reply == QtWidgets.QMessageBox.No:
                        break
            
            finally:
                # 刷新表格
                self.refresh_video_table()
                QtWidgets.QApplication.processEvents()
        
        # 完成
        self.progress_bar.setValue(total)
        self.progress_label.setText(f"上傳完成！成功: {success_count}, 失敗: {fail_count}")
        
        # 生成上傳報告 JSON
        if success_count > 0:
            self._generate_upload_report(videos)
        
        # 顯示結果
        QtWidgets.QMessageBox.information(
            self,
            "批次上傳完成",
            f"上傳完成！\n\n成功: {success_count} 部\n失敗: {fail_count} 部"
        )
        
        # 恢復按鈕
        self.btStartUpload.setEnabled(True)
        self.btAddVideo.setEnabled(True)
        self.btRemoveVideo.setEnabled(True)
        self.btEditVideo.setEnabled(True)
    
    def _generate_upload_report(self, videos: List[VideoItem]):
        """
        生成上傳結果 JSON 報告
        
        Args:
            videos: 上傳的影片列表
        """
        # 只包含上傳成功的影片
        completed_videos = [v for v in videos if v.status == UploadStatus.COMPLETED]
        
        if not completed_videos:
            return
        
        # 生成佇列資料
        queue_data = {
            "queue": [video.to_queue_dict() for video in completed_videos]
        }
        
        # 輸出到控制台
        print("\n" + "="*60)
        print("📋 上傳結果 JSON 報告")
        print("="*60)
        json_output = json.dumps(queue_data, indent=2, ensure_ascii=False)
        print(json_output)
        print("="*60 + "\n")
        
        # 詢問是否儲存到檔案
        reply = QtWidgets.QMessageBox.question(
            self,
            "儲存報告",
            "是否將上傳結果儲存為 JSON 檔案？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "儲存上傳報告",
                "upload_report.json",
                "JSON 檔案 (*.json)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(queue_data, f, indent=2, ensure_ascii=False)
                    QtWidgets.QMessageBox.information(
                        self,
                        "成功",
                        f"報告已儲存至：\n{file_path}"
                    )
                except Exception as e:
                    QtWidgets.QMessageBox.critical(
                        self,
                        "錯誤",
                        f"儲存失敗：{str(e)}"
                    )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BatchUploadWindow()
    window.show()
    sys.exit(app.exec_())