#!/usr/bin/python3
# -*- coding: utf-8 -*-
import urllib.request, json, sys, os
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea
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
        url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city='
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

class PyWeather(QWidget):
    # ウィンドウサイズが変更された時のイベントシグナル
    resized = QtCore.pyqtSignal()

    def __init__(self):
        super(QWidget, self).__init__()
        self.initUI()
        self.show()
        
    def initUI(self):
        self.setGeometry(400, 400, 500, 150)
        self.setWindowTitle('Pythonお天気 3代目')

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
            location_id = int(conf.readline())
        except:
            conf = open('location.conf', 'w')
            location_id = 120010
            conf.write(str(location_id))
        conf.close()
        
        # お天気情報オブジェクト
        self.WeatherInfoObj = WeatherInfo(location_id)
        self.day = 0
        self.fc = self.WeatherInfoObj.retForecasts(self.day)
        self.loc = self.WeatherInfoObj.retLocation()
        self.description = self.WeatherInfoObj.retDescription()
        
        # インターフェース：天気アイコンと日付ロータリーボタン
        iconPath = self.setIcon(self.fc['telop'])
        date_formatted = self.dateFormat(self.fc['date'].split('-')[1]) + "/" + self.dateFormat(self.fc['date'].split('-')[2])

        self.date_btn = QPushButton(date_formatted)
        self.date_btn.setIcon(QtGui.QIcon(iconPath))
        self.date_btn.setIconSize(QtCore.QSize(32,32))
        self.date_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.date_btn.clicked.connect(self.button_clicked)
        
        # インターフェース：お天気情報
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
        layout.addWidget(self.date_btn, 1)
        layout.addLayout(rbox, 3)
        self.setLayout(layout)
        
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

    def resizeEvent(self, event):
        ''' ウィンドウサイズが変更された時のスロット '''
        self.resized.emit()
        self.label_widget.resize(int(self.width()*2/3), self.height())
        return super(PyWeather, self).resizeEvent(event)

    def dateFormat(self, input):
        ''' 日付文字列の整形用関数（取得した月日が１桁の数値の場合、１桁目のゼロを消す） '''
        return input[1:] if input[0] == '0' else input
    
    def setIcon(self, weather):
        ''' 天気テロップの文字列情報から適切な天気アイコンのpathを返す '''
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

if __name__:
    app = QApplication(sys.argv)
    window = PyWeather()
    sys.exit(app.exec_())