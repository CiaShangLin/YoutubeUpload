from PyQt5 import QtCore, QtWidgets, QtGui

class MainView(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.controller = None
        self.setupUi()
        
    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(740, 700)
        self.setWindowTitle("YouTube上傳工具")
        
        # 視頻文件選擇
        self.btOpenVideo = QtWidgets.QPushButton(self)
        self.btOpenVideo.setGeometry(QtCore.QRect(20, 30, 80, 30))
        self.btOpenVideo.setText("選擇檔案")
        
        self.tvFilePath = QtWidgets.QLabel(self)
        self.tvFilePath.setGeometry(QtCore.QRect(120, 30, 601, 30))
        self.tvFilePath.setText("File Path")
        
        # 縮略圖選擇
        self.btOpenImage = QtWidgets.QPushButton(self)
        self.btOpenImage.setGeometry(QtCore.QRect(20, 70, 80, 30))
        self.btOpenImage.setText("選擇縮圖")
        
        self.tvImagePath = QtWidgets.QLabel(self)
        self.tvImagePath.setGeometry(QtCore.QRect(120, 70, 601, 30))
        self.tvImagePath.setText("Image Path")
        
        # 重播文件選擇
        self.btOpenReplay = QtWidgets.QPushButton(self)
        self.btOpenReplay.setGeometry(QtCore.QRect(20, 110, 80, 30))
        self.btOpenReplay.setText("選擇RP")
        
        self.tvReplayPath = QtWidgets.QLabel(self)
        self.tvReplayPath.setGeometry(QtCore.QRect(120, 110, 601, 30))
        self.tvReplayPath.setText("Replay Path")
        
        # 播放列表選擇
        self.playlistGroup = QtWidgets.QGroupBox(self)
        self.playlistGroup.setGeometry(QtCore.QRect(20, 150, 700, 80))
        self.playlistGroup.setTitle("播放清單")
        
        self.playlistLayout = QtWidgets.QHBoxLayout(self.playlistGroup)
        
        self.ckbRank = QtWidgets.QCheckBox(self.playlistGroup)
        self.ckbRank.setText("SC2天梯")
        self.ckbRank.setChecked(True)
        self.playlistLayout.addWidget(self.ckbRank)
        
        self.ckbPVP = QtWidgets.QCheckBox(self.playlistGroup)
        self.ckbPVP.setText("PVP")
        self.playlistLayout.addWidget(self.ckbPVP)
        
        self.ckbPVZ = QtWidgets.QCheckBox(self.playlistGroup)
        self.ckbPVZ.setText("PVZ")
        self.playlistLayout.addWidget(self.ckbPVZ)
        
        self.ckbPVT = QtWidgets.QCheckBox(self.playlistGroup)
        self.ckbPVT.setText("PVT")
        self.playlistLayout.addWidget(self.ckbPVT)
        
        # 語言選擇
        self.languageGroup = QtWidgets.QGroupBox(self)
        self.languageGroup.setGeometry(QtCore.QRect(20, 240, 700, 80))
        self.languageGroup.setTitle("字幕語言")
        
        self.languageLayout = QtWidgets.QHBoxLayout(self.languageGroup)
        
        self.ckbEn = QtWidgets.QCheckBox(self.languageGroup)
        self.ckbEn.setText("英文(預設)")
        self.ckbEn.setChecked(True)
        self.languageLayout.addWidget(self.ckbEn)
        
        self.ckbTW = QtWidgets.QCheckBox(self.languageGroup)
        self.ckbTW.setText("中文(台灣)")
        self.ckbTW.setChecked(True)
        self.languageLayout.addWidget(self.ckbTW)
        
        # 遊戲名稱
        self.labelGame = QtWidgets.QLabel(self)
        self.labelGame.setGeometry(QtCore.QRect(20, 330, 80, 30))
        self.labelGame.setText("遊戲名稱")
        
        self.gameInput = QtWidgets.QLineEdit(self)
        self.gameInput.setGeometry(QtCore.QRect(120, 330, 200, 30))
        self.gameInput.setText("StarCraft II")
        
        # 發布時間
        self.labelPublishTime = QtWidgets.QLabel(self)
        self.labelPublishTime.setGeometry(QtCore.QRect(20, 370, 80, 30))
        self.labelPublishTime.setText("發布時間")
        
        self.publishTime = QtWidgets.QDateTimeEdit(self)
        self.publishTime.setGeometry(QtCore.QRect(120, 370, 200, 30))
        self.publishTime.setCalendarPopup(True)
        self.publishTime.setDateTime(QtCore.QDateTime(QtCore.QDate.currentDate(), QtCore.QTime(18, 0)))
        
        # 標題
        self.labelTitle = QtWidgets.QLabel(self)
        self.labelTitle.setGeometry(QtCore.QRect(20, 410, 80, 30))
        self.labelTitle.setText("標題")
        
        self.textEditTitle = QtWidgets.QTextEdit(self)
        self.textEditTitle.setGeometry(QtCore.QRect(20, 440, 700, 60))
        
        # 描述
        self.labelDescription = QtWidgets.QLabel(self)
        self.labelDescription.setGeometry(QtCore.QRect(20, 510, 80, 30))
        self.labelDescription.setText("描述")
        
        self.textEditDescribe = QtWidgets.QTextEdit(self)
        self.textEditDescribe.setGeometry(QtCore.QRect(20, 540, 700, 100))
        self.textEditDescribe.setHtml("#starcraft2 #星海爭霸2 #gaming")
        
        # 上傳按鈕
        self.btUpload = QtWidgets.QPushButton(self)
        self.btUpload.setGeometry(QtCore.QRect(600, 650, 113, 32))
        self.btUpload.setText("上傳")
        
        # 連接信號和槽
        self.btOpenVideo.clicked.connect(lambda: self.handle_file_selection("video"))
        self.btOpenImage.clicked.connect(lambda: self.handle_file_selection("thumbnail"))
        self.btOpenReplay.clicked.connect(lambda: self.handle_file_selection("replay"))
        self.btUpload.clicked.connect(self.handle_upload)
        
    def set_controller(self, controller):
        self.controller = controller
        
    def handle_file_selection(self, file_type):
        if self.controller:
            self.controller.handle_file_selection(file_type)
            
    def handle_upload(self):
        if self.controller:
            self.controller.handle_upload()
        
    def open_file_dialog(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName()
        return filePath
        
    def set_video_path(self, path):
        self.tvFilePath.setText(path)
        
    def set_thumbnail_path(self, path):
        self.tvImagePath.setText(path)
        
    def set_replay_path(self, path):
        self.tvReplayPath.setText(path)
        
    def set_title(self, title):
        self.textEditTitle.setPlainText(title)
        
    def is_pvp_checked(self):
        return self.ckbPVP.isChecked()
        
    def is_pvz_checked(self):
        return self.ckbPVZ.isChecked()
        
    def is_pvt_checked(self):
        return self.ckbPVT.isChecked()
        
    def is_rank_checked(self):
        return self.ckbRank.isChecked()
        
    def is_chinese_enabled(self):
        return self.ckbTW.isChecked()
        
    def set_pvp_checked(self, checked):
        self.ckbPVP.setChecked(checked)
        
    def set_pvz_checked(self, checked):
        self.ckbPVZ.setChecked(checked)
        
    def set_pvt_checked(self, checked):
        self.ckbPVT.setChecked(checked)
        
    def show_success_message(self, message):
        QtWidgets.QMessageBox.information(self, "成功", message)
        
    def show_error_message(self, message):
        QtWidgets.QMessageBox.critical(self, "錯誤", message) 