#!/usr/bin/python3
# -*- coding: utf-8 -*-
import urllib.request, json, sys, os
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea, QAction, qApp
from PyQt5 import QtCore, QtGui

class WeatherInfo(object):
    def __init__(self, location_id):
        self.location = []
        self.title = None
        self.link = None
        self.publicTime = None
        self.description = None
        self.forecasts = []
        self.copyright = []
        self.getInfo(location_id)

    def getInfo(self, location_id):
        url = 'https://weather.tsukumijima.net/api/forecast?city='
        response = urllib.request.urlopen(url + str(location_id))
        info = json.loads(response.read().decode('utf-8'))

        self.location = info['location']
        self.title = info['title']
        self.link = info['link']
        self.publicTime = info['publicTime']
        self.description = info['description']['text'].replace(' ', '').replace('\r\n', '').replace('\n', '')
        self.forecasts = info['forecasts']
        self.copyright = info['copyright']

    def retForecasts(self, date):
        return self.forecasts[date]

    def retLocation(self):
        return self.location

    def retDescription(self):
        return self.description

class PyWeather(QMainWindow):
    # ウィンドウサイズが変更された時のイベントシグナル
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(400, 400, 500, 150)
        self.setWindowTitle('Pythonお天気 3代目')

        # メニューバーの設定
        self.setMenuBar()

        # スタイルシートの読み込み
        try:
            styleFile = os.path.join(
                os.path.dirname(__file__), 'style.css'
            )
            with open(styleFile, 'r') as f:
                style = f.read()
        except:
            print('スタイルシートが設定されていません（標準デザインで表示します）。')
            style = ''
        self.setStyleSheet(style)

        # APIに投げる地域別のID番号を.confから取得
        try:
            confFile = os.path.join(
                os.path.dirname(__file__), 'location.conf'
            )
            conf = open(confFile, 'r')
            location_id = conf.readline()

            # location_id が空欄の場合は Exception を発生させる
            if location_id == '':
                raise Exception

        except:
            conf = open(confFile, 'w')
            location_id = '120010'
            conf.write(location_id)
        conf.close()

        self.setWeatherInfoObj(location_id)

    def setMenuBar(self):
        ''' メニューバーを定義する '''
        # メニューバーアクションの定義
        exitAction = QAction('終了', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        changeStyle = QAction('スタイルを変更', self)
        changeStyle.setShortcut('Ctrl+C')
        changeStyle.triggered.connect(self.setStyle)

        # 天気表示地点の変更
        change2SPR = QAction('札幌', self)
        change2SND = QAction('仙台', self)
        change2CHB = QAction('千葉', self)
        change2TKO = QAction('東京', self)
        change2NGY = QAction('名古屋', self)
        change2KNZ = QAction('金沢', self)
        change2OSK = QAction('大阪', self)
        change2TAK = QAction('高松', self)
        change2FUK = QAction('福岡', self)
        change2SAG = QAction('佐賀', self)
        change2KAG = QAction('鹿児島', self)
        change2OKI = QAction('沖縄', self)
        # http://drilldripper.hatenablog.com/entry/2016/08/06/175641
        # 引数付きの関数を connect に渡すために lambda を使用
        change2SPR.triggered.connect(lambda: self.setPlace('016010'))
        change2SND.triggered.connect(lambda: self.setPlace('040010'))
        change2CHB.triggered.connect(lambda: self.setPlace('120010'))
        change2TKO.triggered.connect(lambda: self.setPlace('130010'))
        change2NGY.triggered.connect(lambda: self.setPlace('230010'))
        change2KNZ.triggered.connect(lambda: self.setPlace('170010'))
        change2OSK.triggered.connect(lambda: self.setPlace('270000'))
        change2TAK.triggered.connect(lambda: self.setPlace('370000'))
        change2FUK.triggered.connect(lambda: self.setPlace('400010'))
        change2SAG.triggered.connect(lambda: self.setPlace('410010'))
        change2KAG.triggered.connect(lambda: self.setPlace('460010'))
        change2OKI.triggered.connect(lambda: self.setPlace('471010'))

        # メニューバーの定義とアクションの追加
        menubar = self.menuBar()

        # Mac OSのシステムメニューバー上にメニューを表示させない
        menubar.setNativeMenuBar(False)

        fileMenu = menubar.addMenu('メニュー')
        fileMenu.addAction(changeStyle)
        fileMenu.addAction(exitAction)

        fileMenu = menubar.addMenu('地点を変更')
        fileMenu.addAction(change2SPR)
        fileMenu.addAction(change2SND)
        fileMenu.addAction(change2CHB)
        fileMenu.addAction(change2TKO)
        fileMenu.addAction(change2NGY)
        fileMenu.addAction(change2KNZ)
        fileMenu.addAction(change2OSK)
        fileMenu.addAction(change2TAK)
        fileMenu.addAction(change2FUK)
        fileMenu.addAction(change2SAG)
        fileMenu.addAction(change2KAG)
        fileMenu.addAction(change2OKI)

    def setStyle(self):
        ''' ライト/ダークモードの表示スタイルを変更するメソッド（作成中） '''
        print('style changed.')

    def setPlace(self, location_id):
        ''' 天気表示地点を変更し、location.conf に保存するメソッド '''
        confFile = os.path.join(
            os.path.dirname(__file__), 'location.conf'
        )
        conf = open(confFile, 'w')
        conf.write(location_id)
        conf.close()

        self.setWeatherInfoObj(location_id)

    def resizeEvent(self, event):
        ''' ウィンドウサイズが変更された時のスロット '''
        self.resized.emit()
        self.label_widget.resize(int(self.width()*2/3), self.height())
        return super(PyWeather, self).resizeEvent(event)

    def button_clicked(self):
        ''' 日付ボタンが押されたときの動作 '''
        # 0, 1, 2と値をロータリーする
        self.day += 1 if self.day < 2 else -2

        # 深夜の更新前など翌々日の天気情報が無い場合の例外
        try:
            self.fc = self.WeatherInfoObj.retForecasts(self.day)
        except:
            self.day = 0
            self.fc = self.WeatherInfoObj.retForecasts(self.day)

        # 日付ボタンの更新
        iconPath = self.setIcon(self.fc['telop'])
        date_formatted = self.dateFormat(self.fc['date'].split('-')[1]) + '/' + self.dateFormat(self.fc['date'].split('-')[2])
        self.date_btn.setText(date_formatted)
        self.date_btn.setIcon(QtGui.QIcon(iconPath))

        # お天気情報の更新
        self.weather_str = (
            '<h1>' + self.fc['telop'] + '＠' + self.loc['city'] + '</h1>' +
            '<p>' + self.description + '</p>'
        )
        self.label_widget.setText(self.weather_str)

    def dateFormat(self, input):
        ''' 日付文字列の整形用関数（取得した月日が１桁の数値の場合、１桁目のゼロを消す） '''
        return input[1:] if input[0] == '0' else input

    def setIcon(self, weather):
        ''' 天気テロップの文字列情報から適当な天気アイコンのpathを返す '''
        weatherCode = 0
        for char in weather:
            weatherCode += 1 if char == '晴' else 0
            weatherCode += 2 if char == '曇' else 0
            weatherCode += 4 if char == '雨' else 0
            weatherCode += 8 if char == '雷' else 0
            weatherCode += 16 if char == '雪' else 0

        if weatherCode == 1:
            iconPath = '00_sunny.png'
        if weatherCode == 2:
            iconPath = '01_cloudy.png'
        if weatherCode == 3:
            iconPath = '02_partlyCloudy.png'
        if weatherCode >= 4 and weatherCode < 8:
            iconPath = '03_rainy.png'
        if weatherCode >= 8 and weatherCode < 16:
            iconPath = '04_thunder.png'
        if weatherCode >= 16 and weatherCode < 32:
            iconPath = '05_snow.png'
        if weatherCode < 1 or weatherCode >= 32:
            iconPath = '99_noMatch.png'

        return os.path.join(os.path.dirname(__file__), 'icon/', iconPath)

    def setWeatherInfoObj(self, location_id):
        ''' お天気情報オブジェクトを取得・設定するメソッド '''
        # location_id が正しくない場合など、お天気情報が正しく取得できない場合の例外処理
        try:
            self.WeatherInfoObj = WeatherInfo(location_id)
        except:
            print('location.conf が破損しているか、インターネットに接続されていません。')
            print('location.conf を削除して再度実行してください。また、インターネットへの接続を確認してください。')
            exit()

        self.day = 0
        self.fc = self.WeatherInfoObj.retForecasts(self.day)
        self.loc = self.WeatherInfoObj.retLocation()
        self.description = self.WeatherInfoObj.retDescription()

        # 天気アイコンと日付ロータリーボタン
        iconPath = self.setIcon(self.fc['telop'])
        date_formatted = self.dateFormat(self.fc['date'].split('-')[1]) + "/" + self.dateFormat(self.fc['date'].split('-')[2])

        self.date_btn = QPushButton(date_formatted)
        self.date_btn.setIcon(QtGui.QIcon(iconPath))
        self.date_btn.setIconSize(QtCore.QSize(32,32))
        self.date_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.date_btn.clicked.connect(self.button_clicked)

        # お天気情報
        self.weather_str = (
            '<h1>' + self.fc['telop'] + '＠' + self.loc['city'] + '</h1>' +
            '<p>' + self.description + '</p>'
        )

        # QLabelにお天気情報の文字列をはっつける
        self.label_widget = QLabel(self.weather_str, self)
        self.label_widget.resize(335, self.height())
        self.label_widget.setWordWrap(True)

        # QLabelをQScrollAreaにはっつける
        self.label = QScrollArea(self)
        self.label.setWidget(self.label_widget)

        # インターフェース：右画面お天気情報
        rbox = QVBoxLayout()
        rbox.addWidget(self.label)

        # インターフェース：全体
        layout = QHBoxLayout()
        centralWidget = QWidget()

        layout.addWidget(self.date_btn, 1)
        layout.addLayout(rbox, 3)
        centralWidget.setLayout(layout)

        self.setCentralWidget(centralWidget)

if __name__:
    app = QApplication(sys.argv)
    window = PyWeather()
    window.show()
    sys.exit(app.exec_())