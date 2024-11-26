import os
import random
import re
import time

import googleapiclient.discovery
import googleapiclient.errors
import httplib2
from PyQt5 import QtCore, QtWidgets, QtGui
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client import client, tools, file
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow

import UploadGoogleDrive
from UploadArgs import UploadArgs

httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = "token.json"

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secret.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secret.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
LOGIN_TOKEN_FILE = "login_token.json"
UPLOAD_TOKEN_FILE = "upload_token.json"
CHANNEL_ID = 'UC9RrMSH_OaUP2kIFqzPrBpw'

category_id = "20"
keyword = "StarCraft II,Protoss,Zerg,Nzx,Mzx,Mzs,906906,906,九妹,藍兔,Hui,mrbeast,館長,IEM,ESL,SC2,StarCraft,Onion Man"
playList_PVT_id = "PL8TREsr2ZmqYpi_IM1zSQSarofDQftjLj"
playList_PVZ_id = "PL8TREsr2ZmqaY8-tTDPvTLYRH38dtvY4I"
playList_PVP_id = "PL8TREsr2ZmqbGXupnsOkyzoFTkr12cmVF"
playList_PVR_id = "PL8TREsr2ZmqY80QnGjRpFpxcq2ES_YGKf"
playList_Sc2Rank_id = "PL8TREsr2ZmqbIAM5TODn26C8my3cNiRev"

eng_to_tw = {
    "Protoss": "神族",
    "Zerg": "蟲族",
    "Terran": "人族",
    "Random": "隨機"
}

eng_to_ja = {
    "Protoss": "プロトス",
    "Zerg": "ザーグ",
    "Terran": "テラン",
    "Random": "ランダム"
}

eng_to_kr = {
    "Protoss": "프로토스",
    "Zerg": "저그",
    "Terran": "테란",
    "Random": "랜덤"
}

eng_to_ch = {
    "Protoss": "神族",
    "Zerg": "虫族",
    "Terran": "人类",
    "Random": "随机"
}


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(740, 620)
        self.tvFilePath = QtWidgets.QLabel(Dialog)
        self.tvFilePath.setGeometry(QtCore.QRect(120, 30, 601, 30))
        self.tvFilePath.setObjectName("tvFilePath")

        self.btOpenVideo = QtWidgets.QPushButton(Dialog)
        self.btOpenVideo.setGeometry(QtCore.QRect(20, 30, 80, 30))
        self.btOpenVideo.setObjectName("btOpenVideo")

        self.btOpenImage = QtWidgets.QPushButton(Dialog)
        self.btOpenImage.setGeometry(QtCore.QRect(20, 70, 80, 30))
        self.btOpenImage.setObjectName("btOpenImage")

        self.tvImagePath = QtWidgets.QLabel(Dialog)
        self.tvImagePath.setGeometry(QtCore.QRect(120, 70, 601, 30))
        self.tvImagePath.setObjectName("tvImagePath")

        self.btOpenReplay = QtWidgets.QPushButton(Dialog)
        self.btOpenReplay.setGeometry(QtCore.QRect(20, 110, 80, 30))
        self.btOpenReplay.setObjectName("btOpenReplay")

        self.tvReplayPath = QtWidgets.QLabel(Dialog)
        self.tvReplayPath.setGeometry(QtCore.QRect(120, 110, 601, 30))
        self.tvReplayPath.setObjectName("tvReplayPath")

        self.textEditDescribe = QtWidgets.QTextEdit(Dialog)
        self.textEditDescribe.setGeometry(QtCore.QRect(20, 340, 651, 81))
        self.textEditDescribe.setObjectName("textEdit")

        self.textEditEp = QtWidgets.QTextEdit(Dialog)
        self.textEditEp.setGeometry(QtCore.QRect(20, 430, 65, 30))
        self.textEditEp.setObjectName("textEdit_2")

        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 240, 301, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.ckbEn = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.ckbEn.setChecked(True)
        self.ckbEn.setObjectName("ckbEn")
        self.horizontalLayout_2.addWidget(self.ckbEn)

        self.ckbTW = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.ckbTW.setChecked(True)
        self.ckbTW.setObjectName("ckbTW")
        self.horizontalLayout_2.addWidget(self.ckbTW)

        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(20, 140, 651, 80))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ckbRank = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.ckbRank.setObjectName("ckbRank")
        self.horizontalLayout.addWidget(self.ckbRank)

        self.ckbPVP = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.ckbPVP.setObjectName("ckbPVP")
        self.horizontalLayout.addWidget(self.ckbPVP)

        self.ckbPVZ = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.ckbPVZ.setObjectName("ckbPVZ")
        self.horizontalLayout.addWidget(self.ckbPVZ)

        self.ckbPVT = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.ckbPVT.setObjectName("ckbPVT")
        self.horizontalLayout.addWidget(self.ckbPVT)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.btUpload = QtWidgets.QPushButton(Dialog)
        self.btUpload.setGeometry(QtCore.QRect(560, 480, 113, 32))
        self.btUpload.setObjectName("btUpload")

        self.retranslateUi(Dialog)

        self.btOpenVideo.clicked.connect(self.open_video_file)
        self.btOpenImage.clicked.connect(self.open_image_file)
        self.btOpenReplay.clicked.connect(self.open_replay_file)
        self.btUpload.clicked.connect(self.upload)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "YoutubeUpload"))
        Dialog.setWindowIcon(QtGui.QIcon('icon.jpg'))
        self.tvFilePath.setText(_translate("Dialog", "File Path"))
        self.btOpenVideo.setText(_translate("Dialog", "選擇檔案"))
        self.btOpenImage.setText(_translate("Dialog", "選擇縮圖"))
        self.tvImagePath.setText(_translate("Dialog", "Image Path"))
        self.btOpenReplay.setText(_translate("Dialog", "選擇RP"))
        self.tvReplayPath.setText(_translate("Dialog", "Replay Path"))

        self.textEditDescribe.setHtml(_translate("Dialog",
                                                 "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                                 "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                                 "p, li { white-space: pre-wrap; }\n"
                                                 "</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
                                                 "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'PMingLiU\'; font-size:9pt;\">#startcraft2 #星海爭霸2 #gaming</span></p>\n"
                                                 "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'PMingLiU\'; font-size:9pt;\"><br /></p></body></html>"))
        self.textEditEp.setHtml(_translate("Dialog",
                                           "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'.AppleSystemUIFont\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
                                           "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'PMingLiU\'; font-size:9pt;\">EP-</span></p></body></html>"))
        self.label_3.setText(_translate("Dialog", "字幕語言"))
        self.ckbEn.setText(_translate("Dialog", "英文(預設)"))
        self.ckbTW.setText(_translate("Dialog", "中文(台灣)"))
        self.label_2.setText(_translate("Dialog", "播放清單"))
        self.ckbRank.setText(_translate("Dialog", "SC2天梯"))
        self.ckbPVP.setText(_translate("Dialog", "PVP"))
        self.ckbPVZ.setText(_translate("Dialog", "PVZ"))
        self.ckbPVT.setText(_translate("Dialog", "PVT"))
        self.btUpload.setText(_translate("Dialog", "上傳"))

    # 選擇影片路徑
    def open_video_file(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName()  # 選擇檔案對話視窗
        if filePath:
            self.tvFilePath.setText(filePath)

    # 選擇縮圖路徑
    def open_image_file(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName()  # 選擇檔案對話視窗
        if filePath:
            self.tvImagePath.setText(filePath)

    # 選擇RP路徑
    def open_replay_file(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName()  # 選擇檔案對話視窗
        if filePath:
            self.tvReplayPath.setText(filePath)

    def get_authenticated_service_ssl(self):
        # 檢查 token.json 檔案，若不存在則進行 OAuth 流程
        credential_path = os.path.join("./", LOGIN_TOKEN_FILE)
        store = file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, YOUTUBE_SSL_SCOPE)
            credentials = tools.run_flow(flow, store)
        return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    def get_authenticated_service(self):
        credential_path = os.path.join("./", UPLOAD_TOKEN_FILE)
        store = file.Storage(credential_path)
        credentials = store.get()
        if credentials is None or credentials.invalid:
            flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
            http = httplib2.Http()
            credentials = run_flow(flow, store, http=http)
        http = credentials.authorize(httplib2.Http())
        service = googleapiclient.discovery.build('youtube', 'v3', http=http)
        return service

    def initialize_upload(self, youtube, options):
        tags = None
        if options.keywords:
            tags = options.keywords.split(",")

        body = dict(
            snippet=dict(
                title=options.title,
                description=options.description,
                tags=tags,
                categoryId=options.category_id,
                thumbnail=options.thumbnail
            ),
            status=dict(
                privacyStatus=options.privacy_status
            )
        )
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
        )

        video_id = self.resumable_upload(insert_request)
        return video_id

    # Youtube Api 上傳影片
    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print("Video id '%s' was successfully uploaded." %
                              response['id'])
                        return response['id']
                    else:
                        exit("The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                         e.content)
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print("Sleeping %f seconds and then retrying..." % sleep_seconds)
                time.sleep(sleep_seconds)

    # Youtube Api 設定縮圖
    def set_thumbnail(self, youtube, video_id, thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print("設置縮圖完成 Thumbnail set for video id '%s'." % video_id)

    # Youtube Api 添加至播放列表
    def add_video_to_playlist(self, youtube, video_id, playlist_ids):
        for playlist_id in playlist_ids:
            add_video_request = youtube.playlistItems().insert(
                part="snippet",
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()
            print(f"添加至播放列表 Video id '{video_id}' has been added to playlist id '{playlist_id}'.")

    # Youtube Api 添加多國字幕
    def add_video_localizations(self, youtube, video_id, localizations):
        # 獲取現有影片資料
        video_response = youtube.videos().list(
            part="snippet,localizations",
            id=video_id
        ).execute()

        video = video_response['items'][0]
        snippet = video['snippet']
        existing_localizations = video.get('localizations', {})
        snippet['defaultLanguage'] = "en"

        # 更新本地化標題和描述
        existing_localizations.update(localizations)

        # 更新影片資料
        youtube.videos().update(
            part="snippet,localizations",
            body=dict(
                id=video_id,
                snippet=snippet,
                localizations=existing_localizations
            )
        ).execute()

        print(f"添加多國字幕 Updated video '{video_id}' with localizations: {localizations}")

    # Youtube Api 取得自己頻道的播放清單,上傳的時候不會用到
    def list_playlists(self, youtube, channel_id):
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=25
        )
        response = request.execute()
        return response.get("items", [])

    # 取得標題,預設剔除副檔名和時間戳
    def get_title(self):
        # 提取檔名
        basename = os.path.basename(self.tvFilePath.text())
        # 移除附檔名
        new_filename = basename.rsplit(".", 1)[0].strip()
        pattern = r"(【StarCraft II】.*?KR Server)"
        match = re.search(pattern, new_filename)
        result = match.group(1)
        return result + " " + self.textEditEp.toPlainText()

    # 取得預設描述
    def get_description(self, title, replay_url):
        tags = '#startcraft2 #星海爭霸2 #gaming'
        rp = f'RP : {replay_url}'
        description = f'{tags}\n{title}\n{rp}'
        return description

    # 取得有添加的播放列表
    def get_add_playlist(self):
        playList = []
        if self.ckbPVZ.isChecked():
            playList.append(playList_PVZ_id)

        if self.ckbPVP.isChecked():
            playList.append(playList_PVP_id)

        if self.ckbPVT.isChecked():
            playList.append(playList_PVT_id)

        if self.ckbRank.isChecked():
            playList.append(playList_Sc2Rank_id)

        return playList

    # 標題英文轉中文
    def english_to_chinese(self, title):
        for eng, tw in eng_to_tw.items():
            title = title.replace(eng, tw)
        return title

    def english_to_japan(self, title):
        for eng, ja in eng_to_ja.items():
            title = title.replace(eng, ja)
        return title

    def english_to_kr(self, title):
        for eng, kr in eng_to_kr.items():
            title = title.replace(eng, kr)
        return title

    # 標題,描述:多種語言設定
    def get_multi_language(self, replay_url):
        en_title = self.get_title()
        en_description = self.get_description(en_title, replay_url)

        zhTW_title = self.english_to_chinese(en_title)
        zhTW_description = self.get_description(zhTW_title, replay_url)

        ja_title = self.english_to_japan(en_title)
        ja_description = self.get_description(ja_title, replay_url)

        kr_title = self.english_to_kr(en_title)
        kr_description = self.get_description(kr_title, replay_url)

        return {
            'en': {'title': en_title, 'description': en_description},
            'zh-TW': {'title': zhTW_title, 'description': zhTW_description},
            'ja': {'title': ja_title, 'description': ja_description},
            'ko': {'title': kr_title, 'description': kr_description}
        }

    def print_upload_args(self, replay_url):
        print(self.tvFilePath.text())
        print(self.get_title())
        print(self.tvImagePath.text())
        print(self.tvReplayPath.text())
        print(self.get_description(self.get_title(), replay_url))
        print(category_id)
        print(keyword)
        print(VALID_PRIVACY_STATUSES[1])

    def upload(self):
        try:
            replay_file_path = self.tvReplayPath.text()
            replay_url = ''
            if replay_file_path != '':
                replay_url = UploadGoogleDrive.upload_replay(replay_file_path)

            args = UploadArgs(
                file=self.tvFilePath.text(),
                title=self.get_title(),
                thumbnail=self.tvImagePath.text(),
                description=self.get_description(self.get_title(), replay_url),
                category_id=category_id,
                keywords=keyword,
                privacy_status=VALID_PRIVACY_STATUSES[1]
            )

            youtube = self.get_authenticated_service()
            video_id = self.initialize_upload(youtube, args)
            print(f"Uploaded video with ID: {video_id}")

            if args.thumbnail:
                self.set_thumbnail(youtube, video_id, args.thumbnail)

            ssl = self.get_authenticated_service_ssl()
            self.add_video_to_playlist(ssl, video_id, self.get_add_playlist())
            self.add_video_localizations(ssl, video_id, self.get_multi_language(replay_url))
            print("上傳完成")
        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        except Exception as e:
            print("An error occurred: %s" % str(e))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
