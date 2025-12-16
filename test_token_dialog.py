"""
測試 Token 狀態對話框
"""

import sys
from PyQt5 import QtWidgets
from token_manager import TokenManager
from dialogs.token_status_dialog import TokenStatusDialog

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # 創建 Token 管理器
    manager = TokenManager()
    
    # 顯示對話框
    dialog = TokenStatusDialog(manager)
    dialog.exec_()
    
    sys.exit(0)
