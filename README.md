# Youtube Python 上傳器

### 開發需求
自己有開了一個Youtube頻道,主要上傳自己玩星海爭霸2的天梯錄影,每天都會上傳一部,每次都需要重複興趣設置標題,描述這些欄位真的是偏煩,原本是想說用Flutter來寫但是我看Youtube Data Api v3沒有提供Dart版本的,所以使用python開發配合PyQt5來繪製GUI。

### 功能
- 設定標題
- 設定描述
- 設定縮圖
- 設定指定播放清單
- 設定分類
- 設定多國語言標題和描述

### 設定教學
https://developers.google.com/youtube/v3/quickstart/python?hl=zh-tw#step_1_set_up_your_project_and_credentials
1. 創立新專案
2. 選擇API和服務
3. 點選程式庫
4. 搜尋YouTube Data API v3點擊開啟
5. Youtube Data API相關的都勾選上
6. 點擊憑證
7. 建立憑證->OAuth2->選擇電腦版
8. 下載json檔案,或是自己手動創立一下也可以

### 上傳影片
https://developers.google.com/youtube/v3/guides/uploading_a_video?hl=zh-tw
建議下載別人寫的python3版本的,官方提供程式碼是python2
https://github.com/davidrazmadzeExtra/YouTube_Python3_Upload_Video
除了安裝套件之外還要設定client_secrets.json
這個client_secrets.json就是設定第8點的json檔案,要複製自己填上client_id,client_secret也可以

### 特別說明
官方的程式碼上傳影片的時候只能填入必填的欄位,像是縮圖,播放清單,多國語言只能等上傳完後再去修改
要注意的是上傳跟修改的權限SCOPE是不同的,有一個權限的文檔但忘記在哪了
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"

### 結論
太久沒寫python了好不習慣,官方文檔都是基於API的,通時是取得Youtube的資料的比較多,
像這種上傳用到API的情況比較少所以也比較難找得到對應的文檔,python套件本身的文檔
也不適很好找,點進去本身的程式碼也幾乎沒有註解可看,不會像是Android這樣。
程式碼本身幾乎都是用ChatGPT找的,連裁切標題有的沒的都是用AI產出,AI寫成是在一個小範圍的情況下
基本上已經超越junior了。

### 指令紀錄
Qt Designer build to python

pyuic5 -x main.ui -o main.py

Pyinstall

pyinstaller --onefile main.py

### Youtube頻道
無聊可以訂閱一下 感謝~~
[Youtube Sc2Nzs906](https://www.youtube.com/@Sc2Nzs906 "Youtube Sc2Nzs906")

### demo截圖
[![DemoGUI](https://github.com/CiaShangLin/YoutubeUpload/blob/master/demo_gui.PNG "DemoGUI")](https://github.com/CiaShangLin/YoutubeUpload/blob/master/demo_gui.PNG "DemoGUI")

