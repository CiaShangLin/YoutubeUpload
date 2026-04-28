"""
Token 狀態檢查對話框
顯示所有 Token 的過期狀態，並提供重新認證功能
"""

import json

from PyQt5 import QtCore, QtWidgets, QtGui
from token_manager import TokenManager, TokenStatus


class TokenStatusDialog(QtWidgets.QDialog):
    """Token 狀態檢查對話框"""
    
    def __init__(self, token_manager: TokenManager, parent=None):
        """
        初始化對話框
        
        Args:
            token_manager: Token 管理器實例
            parent: 父視窗
        """
        super().__init__(parent)
        self.token_manager = token_manager
        self.setupUi()
        self.check_tokens()
    
    def setupUi(self):
        """設置 UI"""
        self.setObjectName("TokenStatusDialog")
        self.setWindowTitle("Token 狀態檢查")
        self.resize(500, 400)
        
        # 主佈局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 標題
        title_label = QtWidgets.QLabel("OAuth Token 狀態檢查")
        title_font = QtGui.QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 分隔線
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line)
        
        # Token 狀態容器
        self.status_container = QtWidgets.QWidget()
        self.status_layout = QtWidgets.QVBoxLayout(self.status_container)
        self.status_layout.setSpacing(10)
        main_layout.addWidget(self.status_container)
        
        # 彈性空間
        main_layout.addStretch()
        
        # 底部按鈕
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        self.refresh_button = QtWidgets.QPushButton("🔄 重新檢查")
        self.refresh_button.clicked.connect(self.check_tokens)
        button_layout.addWidget(self.refresh_button)
        
        self.close_button = QtWidgets.QPushButton("關閉")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
    
    def check_tokens(self):
        """檢查所有 Token 狀態"""
        self.clear_status_widgets()

        loading_label = QtWidgets.QLabel("檢查中...")
        self.status_layout.addWidget(loading_label)
        QtWidgets.QApplication.processEvents()

        statuses = self.token_manager.check_all_tokens()
        is_bilibili_ok = self.token_manager.is_bilibili_logged_in()

        self.status_layout.removeWidget(loading_label)
        loading_label.deleteLater()

        for name, status in statuses.items():
            self.add_token_status_widget(name, status)

        self._add_bilibili_status_widget(is_bilibili_ok)
    
    def clear_status_widgets(self):
        """清除所有狀態顯示元件"""
        while self.status_layout.count():
            item = self.status_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def add_token_status_widget(self, name: str, status: TokenStatus):
        """
        新增 Token 狀態顯示元件
        
        Args:
            name: Token 名稱
            status: Token 狀態
        """
        # 容器
        container = QtWidgets.QGroupBox(name)
        container_layout = QtWidgets.QVBoxLayout(container)
        
        # 狀態文字
        status_label = QtWidgets.QLabel(status.status_text)
        status_font = QtGui.QFont()
        status_font.setPointSize(11)
        status_label.setFont(status_font)
        
        # 根據狀態設定顏色
        if status.is_valid:
            status_label.setStyleSheet("color: green;")
        else:
            status_label.setStyleSheet("color: red;")
        
        container_layout.addWidget(status_label)
        
        # 錯誤訊息
        if status.error_message:
            error_label = QtWidgets.QLabel(f"詳情: {status.error_message}")
            error_label.setStyleSheet("color: gray; font-size: 9pt;")
            error_label.setWordWrap(True)
            container_layout.addWidget(error_label)
        
        # 操作按鈕
        button_layout = QtWidgets.QHBoxLayout()
        
        # 如果可以刷新，顯示刷新按鈕
        if not status.is_valid and status.error_message and "可嘗試刷新" in status.error_message:
            refresh_btn = QtWidgets.QPushButton("🔄 刷新 Token")
            token_type = 'youtube' if name == 'YouTube' else 'google_drive'
            refresh_btn.clicked.connect(lambda: self.refresh_token(token_type))
            button_layout.addWidget(refresh_btn)
        
        # 重新認證按鈕
        if not status.is_valid:
            auth_btn = QtWidgets.QPushButton("🔐 重新認證")
            token_type = 'youtube' if name == 'YouTube' else 'google_drive'
            auth_btn.clicked.connect(lambda: self.authenticate_token(token_type))
            button_layout.addWidget(auth_btn)
        
        button_layout.addStretch()
        container_layout.addLayout(button_layout)
        
        self.status_layout.addWidget(container)

    def _add_bilibili_status_widget(self, is_logged_in: bool):
        """
        新增 B站 Cookie 狀態顯示元件

        Args:
            is_logged_in: Cookie 是否有效
        """
        container = QtWidgets.QGroupBox("B站 Cookie")
        container_layout = QtWidgets.QVBoxLayout(container)

        if is_logged_in:
            status_label = QtWidgets.QLabel("✅ 已設定")
            status_label.setStyleSheet("color: green; font-size: 11pt;")
        else:
            status_label = QtWidgets.QLabel("❌ 未設定")
            status_label.setStyleSheet("color: red; font-size: 11pt;")
        container_layout.addWidget(status_label)

        button_layout = QtWidgets.QHBoxLayout()
        btn_text = "🔄 重新設定" if is_logged_in else "🔐 設定 Cookie"
        cookie_btn = QtWidgets.QPushButton(btn_text)
        cookie_btn.clicked.connect(self._open_bilibili_cookie_dialog)
        button_layout.addWidget(cookie_btn)
        button_layout.addStretch()
        container_layout.addLayout(button_layout)

        self.status_layout.addWidget(container)

    def _open_bilibili_cookie_dialog(self):
        """開啟 B站 Cookie 輸入對話框"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("設定 B站 Cookie")
        dialog.resize(500, 320)
        layout = QtWidgets.QVBoxLayout(dialog)

        instruction = QtWidgets.QLabel(
            "請貼上 B站 Cookie JSON。\n"
            "必要欄位：SESSDATA, bili_jct, DedeUserID, DedeUserID__ckMd5, buvid3\n"
            "（請從瀏覽器 Application > Cookies > bilibili.com 複製）"
        )
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        text_edit = QtWidgets.QPlainTextEdit()
        text_edit.setPlaceholderText(
            '{\n'
            '  "SESSDATA": "your_sessdata",\n'
            '  "bili_jct": "your_bili_jct",\n'
            '  "DedeUserID": "your_uid",\n'
            '  "DedeUserID__ckMd5": "your_ckmd5",\n'
            '  "buvid3": "your_buvid3"\n'
            '}'
        )
        layout.addWidget(text_edit)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QtWidgets.QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        save_btn = QtWidgets.QPushButton("儲存")
        save_btn.clicked.connect(lambda: self._save_bilibili_cookie(text_edit.toPlainText(), dialog))
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        dialog.exec_()

    def _save_bilibili_cookie(self, json_text: str, dialog: QtWidgets.QDialog):
        """
        驗證並儲存 B站 Cookie

        Args:
            json_text: 使用者輸入的 JSON 文字
            dialog: 輸入對話框（成功後關閉）
        """
        try:
            cookies = json.loads(json_text.strip())
        except json.JSONDecodeError:
            QtWidgets.QMessageBox.warning(self, "格式錯誤", "請輸入有效的 JSON 格式。")
            return

        required = self.token_manager.BILIBILI_REQUIRED_FIELDS
        missing = [f for f in required if f not in cookies]
        if missing:
            QtWidgets.QMessageBox.warning(
                self, "欄位缺少",
                f"Cookie 缺少必要欄位：{', '.join(missing)}"
            )
            return

        if self.token_manager.save_bilibili_cookies(cookies):
            QtWidgets.QMessageBox.information(self, "成功", "B站 Cookie 已儲存！")
            dialog.accept()
            self.check_tokens()
        else:
            QtWidgets.QMessageBox.critical(self, "錯誤", "儲存失敗，請檢查檔案權限。")

    def refresh_token(self, token_type: str):
        """
        刷新指定的 Token
        
        Args:
            token_type: Token 類型
        """
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        try:
            success = self.token_manager.refresh_token(token_type)
            
            if success:
                QtWidgets.QMessageBox.information(
                    self,
                    "成功",
                    f"{token_type.upper()} Token 刷新成功！"
                )
                self.check_tokens()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "失敗",
                    f"{token_type.upper()} Token 刷新失敗，請嘗試重新認證。"
                )
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
    
    def authenticate_token(self, token_type: str):
        """
        執行 Token 認證
        
        Args:
            token_type: Token 類型
        """
        reply = QtWidgets.QMessageBox.question(
            self,
            "確認",
            f"即將開啟瀏覽器進行 {token_type.upper()} OAuth 認證，是否繼續？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            
            try:
                success = self.token_manager.authenticate(token_type)
                
                if success:
                    QtWidgets.QMessageBox.information(
                        self,
                        "成功",
                        f"{token_type.upper()} 認證成功！"
                    )
                    self.check_tokens()
                else:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "失敗",
                        f"{token_type.upper()} 認證失敗，請檢查網路連線和 token.json 設定。"
                    )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "錯誤",
                    f"認證過程發生錯誤：{str(e)}"
                )
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()


if __name__ == '__main__':
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    
    # 測試對話框
    manager = TokenManager()
    dialog = TokenStatusDialog(manager)
    dialog.exec_()
    
    sys.exit(app.exec_())
