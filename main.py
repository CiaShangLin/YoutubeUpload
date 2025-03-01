import sys
from PyQt5 import QtWidgets
from src.views.main_view import MainView
from src.controllers.upload_controller import UploadController
from src.models.video_data import VideoData
from src.utils.logger import logger

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        
        # 創建MVC組件
        model = VideoData()
        view = MainView()
        controller = UploadController(model, view)
        
        # 設置控制器
        view.set_controller(controller)
        
        # 顯示視圖
        view.show()
        
        # 執行應用
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"應用啟動時出錯: {str(e)}")
        raise

if __name__ == "__main__":
    main()