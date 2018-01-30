#!/usr/bin/python3
# -*- coding: utf-8 -*-
import urllib.request, json, sys
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QScrollArea
from PyQt5 import QtCore

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
        self.description = info['description']['text']
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
        self.init_ui()
        self.show()
        
    def init_ui(self):
        self.setGeometry(400, 400, 500, 150)
        self.setWindowTitle('Pythonお天気 3代目')
        
        # APIに投げる地域別のID番号を.confから取得
        try:
            conf = open('location.conf', 'r')
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
        self.description = self.WeatherInfoObj.retDescription().replace('。', '。</p><p>')
        
        # インターフェース：日付ロータリーボタン
        date_formatted = self.fc['date'].split('-')[1] + '/' + self.fc['date'].split('-')[2]
        date_formatted = date_formatted[1:] if date_formatted[0] == "0" else date_formatted
        self.date_btn = QPushButton(date_formatted, self)
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
        date_formatted = self.fc['date'].split('-')[1] + '/' + self.fc['date'].split('-')[2]
        date_formatted = date_formatted[1:] if date_formatted[0] == "0" else date_formatted
        self.date_btn.setText(date_formatted)

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

if __name__:
    app = QApplication(sys.argv)
    window = PyWeather()
    sys.exit(app.exec_())