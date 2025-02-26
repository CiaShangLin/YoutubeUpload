import os
import random
import re
import time
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
import googleapiclient.discovery
import googleapiclient.errors
import httplib2
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
LOGIN_TOKEN_FILE = "login_token.json"
UPLOAD_TOKEN_FILE = "upload_token.json"
CHANNEL_ID = 'UC9RrMSH_OaUP2kIFqzPrBpw'

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
category_id = "20"
keyword = "StarCraft II, Starcraft 2, SC2, 星海爭霸2, Ladder, 天梯, Ranked Match, Protoss, 神族, Zerg, 蟲族, Terran, 人族, Nzx, Gameplay, SC2 Strategy, PvP, PvZ, PvT, IEM, ESL, KR Server"
playList_PVT_id = "PL8TREsr2ZmqYpi_IM1zSQSarofDQftjLj"
playList_PVZ_id = "PL8TREsr2ZmqaY8-tTDPvTLYRH38dtvY4I"
playList_PVP_id = "PL8TREsr2ZmqbGXupnsOkyzoFTkr12cmVF"
playList_PVR_id = "PL8TREsr2ZmqY80QnGjRpFpxcq2ES_YGKf"
playList_Sc2Rank_id = "PL8TREsr2ZmqbIAM5TODn26C8my3cNiRev"

eng_to_tw = {"Protoss": "神族", "Zerg": "蟲族", "Terran": "人族", "Random": "隨機"}
eng_to_ja = {"Protoss": "プロトス", "Zerg": "ザーグ", "Terran": "テラン", "Random": "ランダム"}
eng_to_kr = {"Protoss": "프로トス", "Zerg": "저그", "Terran": "テラン", "Random": "랜덤"}
eng_to_ch = {"Protoss": "神族", "Zerg": "虫族", "Terran": "人类", "Random": "随机"}


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(740, 700)

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

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(20, 140, 651, 80))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.ckbRank = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.ckbRank.setObjectName("ckbRank")
        self.ckbRank.setChecked(True)
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

        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(20, 240, 301, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.ckbEn = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.ckbEn.setChecked(True)
        self.ckbEn.setObjectName("ckbEn")
        self.horizontalLayout_2.addWidget(self.ckbEn)
        self.ckbTW = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.ckbTW.setChecked(True)
        self.ckbTW.setObjectName("ckbTW")
        self.horizontalLayout_2.addWidget(self.ckbTW)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.textEditDescribe = QtWidgets.QTextEdit(Dialog)
        self.textEditDescribe.setGeometry(QtCore.QRect(20, 600, 651, 81))
        self.textEditDescribe.setObjectName("textEdit")

        self.labelGame = QtWidgets.QLabel(Dialog)
        self.labelGame.setGeometry(QtCore.QRect(20, 470, 80, 30))
        self.labelGame.setObjectName("labelGame")
        self.gameInput = QtWidgets.QLineEdit(Dialog)
        self.gameInput.setGeometry(QtCore.QRect(120, 470, 200, 30))
        self.gameInput.setText("StarCraft II")

        self.labelPublishTime = QtWidgets.QLabel(Dialog)
        self.labelPublishTime.setGeometry(QtCore.QRect(20, 510, 80, 30))
        self.labelPublishTime.setObjectName("labelPublishTime")
        self.publishTime = QtWidgets.QDateTimeEdit(Dialog)
        self.publishTime.setGeometry(QtCore.QRect(120, 510, 200, 30))
        self.publishTime.setCalendarPopup(True)
        self.publishTime.setDateTime(QtCore.QDateTime(QtCore.QDate.currentDate(), QtCore.QTime(18, 0)))

        self.textEditTitle = QtWidgets.QTextEdit(Dialog)
        self.textEditTitle.setGeometry(QtCore.QRect(20, 550, 651, 40))
        self.textEditTitle.setObjectName("textEditTitle")

        self.btUpload = QtWidgets.QPushButton(Dialog)
        self.btUpload.setGeometry(QtCore.QRect(560, 650, 113, 32))
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
        self.label_3.setText(_translate("Dialog", "字幕語言"))
        self.ckbEn.setText(_translate("Dialog", "英文(預設)"))
        self.ckbTW.setText(_translate("Dialog", "中文(台灣)"))
        self.label_2.setText(_translate("Dialog", "播放清單"))
        self.ckbRank.setText(_translate("Dialog", "SC2天梯"))
        self.ckbPVP.setText(_translate("Dialog", "PVP"))
        self.ckbPVZ.setText(_translate("Dialog", "PVZ"))
        self.ckbPVT.setText(_translate("Dialog", "PVT"))
        self.labelGame.setText(_translate("Dialog", "遊戲名稱"))
        self.labelPublishTime.setText(_translate("Dialog", "發布時間"))
        self.btUpload.setText(_translate("Dialog", "上傳"))

    def open_video_file(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName()
        if filePath:
            self.tvFilePath.setText(filePath)
            title = self.get_title(filePath)
            self.textEditTitle.setPlainText(title)
            replay_url = ""
            description = self.get_description(title, replay_url)
            self.textEditDescribe.setPlainText(description)

            # 根據檔案名稱自動勾選對戰類型
            basename = os.path.basename(filePath)
            print(f"檔案名稱: {basename}")
            pattern = r".*\((Protoss|Zerg|Terran)(?:\s*\d*)\)\s*vs\s*.*\((Protoss|Zerg|Terran)(?:\s*\d*)\)"
            match = re.search(pattern, basename, re.IGNORECASE)
            if match:
                left_race, right_race = match.groups()
                print(f"左種族: {left_race}, 右種族: {right_race}")
                self.ckbPVP.setChecked(False)
                self.ckbPVZ.setChecked(False)
                self.ckbPVT.setChecked(False)
                if left_race.lower() == "protoss" and right_race.lower() == "protoss":
                    self.ckbPVP.setChecked(True)
                    print("勾選 PVP")
                elif left_race.lower() == "protoss" and right_race.lower() == "zerg":
                    self.ckbPVZ.setChecked(True)
                    print("勾選 PVZ")
                elif left_race.lower() == "protoss" and right_race.lower() == "terran":
                    self.ckbPVT.setChecked(True)
                    print("勾選 PVT")
            else:
                print("未匹配到對戰種族")

    def open_image_file(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName()
        if filePath:
            self.tvImagePath.setText(filePath)

    def open_replay_file(self):
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName()
        if filePath:
            self.tvReplayPath.setText(filePath)

    def get_title(self, file_path):
        basename = os.path.basename(file_path)
        new_filename = basename.rsplit(".", 1)[0].strip()
        pattern = r"(【StarCraft II】.*?KR Server)"
        match = re.search(pattern, new_filename)
        if match:
            game_name = self.gameInput.text() if self.gameInput.text() else "StarCraft II"
            return match.group(1).replace("【StarCraft II】", f"【{game_name}】")
        return new_filename

    def get_description(self, title, replay_url):
        tags = '#starcraft2 #星海爭霸2 #gaming'
        rp = f'RP : {replay_url}' if replay_url else ""
        return f'{tags}\n{title}\n{rp}'

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

    def get_multi_language(self, replay_url):
        en_title = self.textEditTitle.toPlainText()
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

    def get_authenticated_service_ssl(self):
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
        return googleapiclient.discovery.build('youtube', 'v3', http=http)

    def initialize_upload(self, youtube, options):
        tags = options.keywords.split(",") if options.keywords else []
        game_name = self.gameInput.text()
        if game_name and game_name not in tags:
            tags.append(game_name)

        publish_at = None
        if self.publishTime.dateTime() > QtCore.QDateTime.currentDateTime():
            publish_at = self.publishTime.dateTime().toString("yyyy-MM-ddThh:mm:ss+08:00")

        body = {
            "snippet": {
                "title": options.title,
                "description": options.description,
                "tags": tags,
                "categoryId": options.category_id,
            },
            "status": {
                "privacyStatus": "private" if publish_at else options.privacy_status,
                "publishAt": publish_at
            }
        }
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
        )
        return self.resumable_upload(insert_request)

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
                        print("Video id '%s' was successfully uploaded." % response['id'])
                        return response['id']
                    else:
                        exit("The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
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

    def set_thumbnail(self, youtube, video_id, thumbnail_path):
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print("設置縮圖完成 Thumbnail set for video id '%s'." % video_id)

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

    def add_video_localizations(self, youtube, video_id, localizations):
        video_response = youtube.videos().list(
            part="snippet,localizations",
            id=video_id
        ).execute()

        video = video_response['items'][0]
        snippet = video['snippet']
        existing_localizations = video.get('localizations', {})
        snippet['defaultLanguage'] = "en"
        existing_localizations.update(localizations)

        youtube.videos().update(
            part="snippet,localizations",
            body=dict(
                id=video_id,
                snippet=snippet,
                localizations=existing_localizations
            )
        ).execute()
        print(f"添加多國字幕 Updated video '{video_id}' with localizations: {localizations}")

    def upload(self):
        try:
            replay_file_path = self.tvReplayPath.text()
            replay_url = UploadGoogleDrive.upload_replay(replay_file_path) if replay_file_path else ""

            title = self.textEditTitle.toPlainText()
            description = self.textEditDescribe.toPlainText()
            if replay_url:
                description += f"\nRP : {replay_url}"

            args = UploadArgs(
                file=self.tvFilePath.text(),
                title=title,
                thumbnail=self.tvImagePath.text(),
                description=description,
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
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


if __name__ == "__main__":


    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
