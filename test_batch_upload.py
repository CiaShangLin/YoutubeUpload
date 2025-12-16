"""
測試 Phase 2 批次影片列表功能
"""

import sys
from PyQt5 import QtWidgets
from main import BatchUploadWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    
    # 創建主視窗
    window = BatchUploadWindow()
    window.show()
    
    sys.exit(app.exec_())
