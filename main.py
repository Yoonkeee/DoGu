import re
import sys
import json
import requests
import pyautogui
import collections
from heapq import *
from PIL import Image
import urllib.request
from PyQt5 import uic
import datetime as dt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication, QWidget

form_class = uic.loadUiType("Dogu_PyQt.ui")[0]
api_key = 'RGAPI-5a937c8a-f537-435d-ac3a-1c6ad7765f9e'
#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        # self.setStyleSheet('background-color: #f5ffee')
        self.summoner_search.setStyleSheet(
            '''
            QPushButton{image : url(images/bee.png); border:0px;}
            QPushButton:hover{image : url(images/bee_sad.png); border:0px;}
            ''')
        self.summoner_search.clicked.connect(self.summoner_search_Func)
        self.summoner_name_input.returnPressed.connect(self.summoner_search_Func)
        self.player_team = ''
        self.enemy_team = ''
        self.ionia_bool = [False] * 5
        self.cosmic_bool = [False] * 5
        self.spell_bool = [True] * 10
        self.spell_cooldown = [0] * 10
        self.current_cooldown = [0] * 10  # 현재 스펠 쿨타임(초)
        self.spells = []
        self.kor_champs = []
        self.kor_spells = []
        self.log = []
        self.log_str = ''
        self.current_level = [1] * 5
        self.teleport_bool = [False] * 5
        self.spellbars = [self.spellbar1, self.spellbar2, self.spellbar3, self.spellbar4, self.spellbar5,
                          self.spellbar6, self.spellbar7, self.spellbar8, self.spellbar9, self.spellbar10]
        self.timers = [self.spelltimer1, self.spelltimer2, self.spelltimer3, self.spelltimer4,
                       self.spelltimer5, self.spelltimer6, self.spelltimer7, self.spelltimer8,
                       self.spelltimer9, self.spelltimer10]

        self.levels = [self.level1, self.level2, self.level3, self.level4, self.level5]
        shoes = [self.ionia1, self.ionia2, self.ionia3, self.ionia4, self.ionia5]
        for t in self.levels:
            t.resize(0,0)
        self.ionia1.setStyleSheet('image : url(images/buttons/ionia.png);')
        for i in range(5):
            shoes[i].setStyleSheet('image : url(images/buttons/no_ionia.png);')
        self.ionia_buttons = [self.ionia1, self.ionia2, self.ionia3, self.ionia4, self.ionia5]
        self.spell_buttons = [self.enemy1_spell1, self.enemy1_spell2, self.enemy2_spell1,
                              self.enemy2_spell2, self.enemy3_spell1,self.enemy3_spell2,
                              self.enemy4_spell1, self.enemy4_spell2,
                              self.enemy5_spell1, self.enemy5_spell2]
        self.spell_labels = [self.spell_label1, self.spell_label2, self.spell_label3,
                           self.spell_label4, self.spell_label5, self.spell_label6,
                           self.spell_label7, self.spell_label8, self.spell_label9,
                           self.spell_label10]
        self.ionia1.clicked.connect(self.ionia1_clicked)
        self.ionia2.clicked.connect(self.ionia2_clicked)
        self.ionia3.clicked.connect(self.ionia3_clicked)
        self.ionia4.clicked.connect(self.ionia4_clicked)
        self.ionia5.clicked.connect(self.ionia5_clicked)
        self.enemy1_spell1.clicked.connect(self.spell1_clicked)
        self.enemy1_spell2.clicked.connect(self.spell2_clicked)
        self.enemy2_spell1.clicked.connect(self.spell3_clicked)
        self.enemy2_spell2.clicked.connect(self.spell4_clicked)
        self.enemy3_spell1.clicked.connect(self.spell5_clicked)
        self.enemy3_spell2.clicked.connect(self.spell6_clicked)
        self.enemy4_spell1.clicked.connect(self.spell7_clicked)
        self.enemy4_spell2.clicked.connect(self.spell8_clicked)
        self.enemy5_spell1.clicked.connect(self.spell9_clicked)
        self.enemy5_spell2.clicked.connect(self.spell10_clicked)
        self.level1.valueChanged.connect(self.level1_changed)
        self.level2.valueChanged.connect(self.level2_changed)
        self.level3.valueChanged.connect(self.level3_changed)
        self.level4.valueChanged.connect(self.level4_changed)
        self.level5.valueChanged.connect(self.level5_changed)
        self.spelltimer1.valueChanged.connect(self.timer1_changed)
        self.spelltimer2.valueChanged.connect(self.timer2_changed)
        self.spelltimer3.valueChanged.connect(self.timer3_changed)
        self.spelltimer4.valueChanged.connect(self.timer4_changed)
        self.spelltimer5.valueChanged.connect(self.timer5_changed)
        self.spelltimer6.valueChanged.connect(self.timer6_changed)
        self.spelltimer7.valueChanged.connect(self.timer7_changed)
        self.spelltimer8.valueChanged.connect(self.timer8_changed)
        self.spelltimer9.valueChanged.connect(self.timer9_changed)
        self.spelltimer10.valueChanged.connect(self.timer10_changed)
        self.gametime_sec.timeChanged.connect(self.sec_changed)
        self.gametime_min.timeChanged.connect(self.min_changed)

        self.current_time = 0
        self.timerVar = QTimer()
        self.timerVar.setInterval(1000)
        self.timerVar.timeout.connect(self.bar_timer)

    def sec_changed(self):
        self.current_time = self.gametime_min.time().minute() * 60 + \
                            self.gametime_sec.time().second()
    def min_changed(self):
        self.current_time = self.gametime_min.time().minute() * 60 + \
                            self.gametime_sec.time().second()

    def bar_timer(self):  # 매초 실행되는 함수
        self.current_cooldown = [self.current_cooldown[i] - 1 for i in range(10)]
        log = []
        for i in range(10):
            self.spellbars[i].setValue(self.current_cooldown[i])
            self.timers[i].setValue(self.current_cooldown[i])
            if self.current_cooldown[i] > 0 and self.spells[i] in ['Flash', 'Teleport']:
                kor_champ = self.kor_champs[i // 2]
                if self.spells[i] == 'Teleport':
                    kor_champ = kor_champ + ' 텔'
                log.append([self.current_cooldown[i], kor_champ])
            if self.current_cooldown[i] <= 0:
                self.spell_bool[i] = True
                self.spell_cooldown[i] = 0
                self.spell_buttons[i].setStyleSheet('image : url(images/spells/' + self.spells[i] + '.png);')
                self.spell_labels[i].clear()
        if False not in self.spell_bool:
            log, self.log_str = [], ''
        self.log = sorted(log[:])
        m, s = str(self.current_time // 60), str(self.current_time % 60)
        if len(m) < 2:
            m = '0'+m
        if len(s) < 2:
            s = '0'+s
        self.gametime_min.setTime(QTime.fromString(m, 'mm'))
        self.gametime_sec.setTime(QTime.fromString(s, 'ss'))
        self.current_time += 1
        self.log_label.setText(self.log_str)

    def ionia1_clicked(self): self.change_ionia_img(0)
    def ionia2_clicked(self): self.change_ionia_img(1)
    def ionia3_clicked(self): self.change_ionia_img(2)
    def ionia4_clicked(self): self.change_ionia_img(3)
    def ionia5_clicked(self): self.change_ionia_img(4)

    def spell1_clicked(self): self.change_spell_img(0)
    def spell2_clicked(self): self.change_spell_img(1)
    def spell3_clicked(self): self.change_spell_img(2)
    def spell4_clicked(self): self.change_spell_img(3)
    def spell5_clicked(self): self.change_spell_img(4)
    def spell6_clicked(self): self.change_spell_img(5)
    def spell7_clicked(self): self.change_spell_img(6)
    def spell8_clicked(self): self.change_spell_img(7)
    def spell9_clicked(self): self.change_spell_img(8)
    def spell10_clicked(self): self.change_spell_img(9)

    def level1_changed(self): self.set_level(0)
    def level2_changed(self): self.set_level(1)
    def level3_changed(self): self.set_level(2)
    def level4_changed(self): self.set_level(3)
    def level5_changed(self): self.set_level(4)
    def timer1_changed(self): self.set_timer(0)
    def timer2_changed(self): self.set_timer(1)
    def timer3_changed(self): self.set_timer(2)
    def timer4_changed(self): self.set_timer(3)
    def timer5_changed(self): self.set_timer(4)
    def timer6_changed(self): self.set_timer(5)
    def timer7_changed(self): self.set_timer(6)
    def timer8_changed(self): self.set_timer(7)
    def timer9_changed(self): self.set_timer(8)
    def timer10_changed(self): self.set_timer(9)

    def set_timer(self, i):
        if not self.spells:
            return
        self.current_cooldown[i] = self.timers[i].value()
        s = self.current_time - (self.spell_cooldown[i] - self.current_cooldown[i])
        m = str(s // 60)
        s = str(s % 60)
        if len(m) < 2:
            m = '0'+m
        if len(s) < 2:
            s = '0'+s
        self.spell_labels[i].setText(str(self.kor_spells[i] + ' ' + m + ':' + s))
        # 01:00  06:00  03:00  2분지남 3분남음 현재시간 - 지난시간 지난시간=스펠쿨-현재쿨
        # 현재시간 - (스펠쿨 - 현재쿨)
        # 현재시간 + 현재쿨(t)
        log = ''
        for i in range(len(self.log)):
            t, champ = self.log[i]  # 초, 챔피언 이름
            t += self.current_time
            m = str(t // 60)
            s = str((t-1) % 60)
            if len(m) < 2: m = '0' + m
            if len(s) < 2: s = '0' + s
            log = (log + m+':'+s+' '+champ+' ')
        self.log_str = log

    def set_level(self, i):
        self.current_level[i] = self.levels[i].value()

    def change_spell_img(self, i):
        if not self.spells:
            return
        if self.spell_bool[i]:
            self.spell_bool[i] = False
            self.spell_buttons[i].setStyleSheet('image : url(images/spells/no_' + self.spells[i] + '.png);')
            spell_str = ''
            if self.cosmic_bool[i // 2]: spell_str = spell_str + 'c'
            if self.ionia_bool[i // 2]: spell_str = spell_str + 's'
            spell_str = spell_str + self.spells[i]
            if self.spells[i] == 'Teleport':
                self.spell_cooldown[i] = spells_cooldown_json[spell_str][0][self.current_level[i//2]-1]
            else:
                self.spell_cooldown[i] = spells_cooldown_json[spell_str][0]

            self.current_cooldown[i] = self.spell_cooldown[i]
            self.timers[i].setValue(self.spell_cooldown[i])
            self.spellbars[i].reset()
            self.spellbars[i].setRange(0, self.spell_cooldown[i])
            self.spellbars[i].setValue(self.spell_cooldown[i])
            m, s = str(self.gametime_min.time().minute()), \
                   str(self.gametime_sec.time().second())
            if len(m) < 2: m='0'+m
            if len(s) < 2: s='0'+s
            self.spell_labels[i].setText(str(self.kor_spells[i]+' '+m+':'+s))

        else:
            self.spell_bool[i] = True
            self.spell_cooldown[i] = 0
            self.timers[i].setValue(0)
            self.spellbars[i].reset()
            self.spell_buttons[i].setStyleSheet('image : url(images/spells/' + self.spells[i] + '.png);')
            self.spell_labels[i].clear()


    def change_ionia_img(self, i):
        if self.ionia_bool[i] == False:
            self.ionia_bool[i] = True
            self.ionia_buttons[i].setStyleSheet('image : url(images/buttons/ionia.png);')
        else:
            self.ionia_bool[i] = False
            self.ionia_buttons[i].setStyleSheet('image : url(images/buttons/no_ionia.png);')

    def summoner_search_Func(self):
        png = '.png'
        self.ionia_bool = [False] * 5
        self.cosmic_bool = [False] * 5
        self.spell_bool = [True] * 10
        self.spell_cooldown = [0] * 10
        self.spells = []
        self.current_level = [1] * 5
        self.teleport_bool = [False] * 5
        for t in self.levels:
            t.resize(0,0)
        summoner_name = self.summoner_name_input.text()
        match_info = get_match_info(summoner_name)
        if match_info == None:
            return
        self.enemy_team = 'RED Team' if self.player_team == 'BLUE Team' else 'BLUE Team'
        enemy_info = match_info['players'][self.enemy_team]
        enemy_champ_list = list(enemy_info.keys())
        cosmic_list = []
        spells = []
        spell_cooldown = [0] * 10
        kor_champs = []
        kor_spells = []

        for s in match_info['players'][self.enemy_team].values():
            spells.append(s[0][8:])
            spells.append(s[1][8:])
            cosmic_list.append(s[2])
            kor_champs.append(s[3])
            kor_spells.append(s[4])
            kor_spells.append(s[5])

        self.spells = spells[:]
        self.spell_cooldown = spell_cooldown[:]
        self.kor_champs = kor_champs[:]
        self.kor_spells = kor_spells[:]
        # Reset Default ----------------------------
        self.log_str = ''
        self.spell_bool = [True] * 10
        self.ionia_bool = [False] * 5
        self.spell_cooldown = [0] * 10
        self.current_cooldown = [0] * 10
        self.teleport_bool = [False] * 5
        for i in range(10):
            self.spellbars[i].reset()
        for i in range(5):
            # print(self.levels[i])
            self.current_level[i] = 1
            self.levels[i].setValue(1)
        # End Reset Default -------------------------
        spell_set = set(spells)
        spells_image = {}
        champs_image = {}
        qPixmapVar = QPixmap()

        enemy_champs = [
            self.enemy1, self.enemy2, self.enemy3, self.enemy4, self.enemy5
        ]
        for i, champ in enumerate(enemy_champ_list):
            enemy_champs[i].setStyleSheet('image : url(images/champions/'+ champ +'.png);')

        enemy_spells = [
            self.enemy1_spell1, self.enemy1_spell2,
            self.enemy2_spell1, self.enemy2_spell2,
            self.enemy3_spell1, self.enemy3_spell2,
            self.enemy4_spell1, self.enemy4_spell2,
            self.enemy5_spell1, self.enemy5_spell2
        ]
        for i in range(10):
            enemy_spells[i].setStyleSheet('image : url(images/spells/'+spells[i]+'.png);')
            if spells[i] == 'Teleport':
                self.teleport_bool[i // 2] = True
                self.levels[i // 2].resize(84, 84)

        cosmic = [self.cosmic1, self.cosmic2, self.cosmic3, self.cosmic4, self.cosmic5]
        for i in range(5):
            if cosmic_list[i]:
                self.cosmic_bool[i] = True
                cosmic[i].setStyleSheet('image : url(images/buttons/cosmic.png);')
            else:
                self.cosmic_bool[i] = False
                cosmic[i].setStyleSheet('image : url(images/buttons/no_cosmic.png);')

        shoes = [self.ionia1, self.ionia2, self.ionia3, self.ionia4, self.ionia5]
        for i in range(5):
            shoes[i].setStyleSheet('image : url(images/buttons/no_ionia.png);')

        self.timerVar.start()
        # minute, second = elapsed_time(match_info)
        # if len(minute) < 2: minute = '0'+minute
        # if len(second) < 2: second = '0'+second
        #
        # self.current_time = int(minute) * 60 + int(second)
        # self.gametime_min.setTime(QTime.fromString(minute, 'mm'))
        # self.gametime_sec.setTime(QTime.fromString(second, 'ss'))

        self.gametime_min.setTime(QTime.fromString('00', 'mm'))
        self.gametime_sec.setTime(QTime.fromString('00', 'ss'))


#-----------------------------------------------------------------------
entered_api_key = ''
api_key = '?api_key=' + entered_api_key
version = '11.1.1'
urls = {
    'get_id' : 'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/',
    'get_match_info' : 'https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/',
    'challanger' : 'https://kr.api.riotgames.com/lol/spectator/v4/featured-games',
    # 'champions' : 'https://ddragon.leagueoflegends.com/cdn/' + version + '/data/ko_KR/champion.json',
    'spells' : 'https://ddragon.leagueoflegends.com/cdn/' + version + '/data/ko_KR/summoner.json',
    'runes' : 'https://ddragon.leagueoflegends.com/cdn/' + version + '/data/ko_KR/runesReforged.json',
    'items' : 'http://ddragon.leagueoflegends.com/cdn/' + version + '/data/ko_KR/item.json',
    'champions' : 'src/champions.json',
    'buttons' : 'images/buttons/',
    'champion_image' : 'images/champions/',
    'spell_image' : 'images/spells/'
    # 'images/' : 'https://raw.githubusercontent.com/Yoonkeee/DoGu/master/images/',
    # 'champion_image' : 'https://raw.githubusercontent.com/Yoonkeee/DoGu/master/images/champions/',
    # 'spell_image' : 'https://raw.githubusercontent.com/Yoonkeee/DoGu/master/images/spells/'
}
def request_json(url, summoner_name=None):
    request = requests.get(url)
    if request.status_code != 200:
        if request.status_code == 404:
            s = str('현재 게임중이 아닙니다.')
            pyautogui.alert(s)
            return None
        elif request.status_code == 403:
            new_api = pyautogui.prompt('API Key Expired! Enter New API')
            global api_key
            api_key = '?api_key=' + new_api
            url = url.split('?api_key=')[0] + api_key
            return request_json(url, summoner_name)
        else:
            s = str(str(request.status_code) + ' Error')
            pyautogui.alert(s)
            return None
    js = json.loads(request.text)
    return js

def elapsed_time(match):
  t = datetime.now() - datetime.fromtimestamp(match['start_time'] / 1000)
  (_, minutes, seconds) = str(dt.timedelta(seconds=t.seconds)).split(':')
  return [minutes, seconds]

def get_match_info(summoner_name):
  encrypted_id = request_json(urls['get_id'] + summoner_name + api_key, summoner_name)
  if encrypted_id == None:
      return None
  else:
      encrypted_id = encrypted_id['id']
  match_info = request_json(urls['get_match_info'] + encrypted_id + api_key)
  if match_info == None:
      return None
  users_info = match_info['participants']
  start_time = match_info['gameStartTime']
  team_color = {
    100: 'RED Team',
    200: 'BLUE Team'
  }

  match = {'players': {'RED Team': {}, 'BLUE Team': {}},
           'start_time': start_time}
  # cosmic_insite : 8347
  for user in users_info:
    color = team_color[user['teamId']]
    if user['summonerName'] == summoner_name:
        myWindow.player_team = color
    spell_1 = spells_id[user['spell1Id']]['name']
    spell_2 = spells_id[user['spell2Id']]['name']
    kor_spell1 = spells_id[user['spell1Id']]['kr_name']
    kor_spell2 = spells_id[user['spell2Id']]['kr_name']
    try:
        champ, kor_champ = champions_id[str(user['championId'])]
    except:
        champ, kor_champ = 'null', 'null'
    cosmic_insight = 8347 in user['perks']['perkIds']
    match['players'][color][champ] = [spell_1, spell_2, cosmic_insight, kor_champ,
                                      kor_spell1, kor_spell2]
  return match

runes = request_json(urls['runes'])
cosmic_insight_cooldown = int(re.findall('\d+', runes[1]['slots'][3]
                                         ['runes'][0]['shortDesc'].split('아이템 가속')[0])[0])
items = request_json(urls['items'])
ionia_boots_cooldown = int(re.findall('\d+', str(items['data'])
                                      .split('소환사 주문 가속이 ')[1].split(' ')[0])[0])
spells_id = {}
spells = request_json(urls['spells'])['data']
for spell in spells.keys():
    key, name, cooldown, kor = (int(spells[spell]['key']), spell, spells[spell]['cooldown'][0],
                                spells[spell]['name'])
    if spell == 'SummonerTeleport':
        cooldown = 420
    spells_id[key] = {'name' : spell, 'cooldown' : cooldown, 'kr_name' : kor}

with open('src/champions.json', 'r') as f:
    champions_id = json.load(f)
with open('src/spells.json', 'r') as f:
    spells_cooldown_json = json.load(f)


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)
    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()
    #프로그램 화면을 보여주는 코드
    # global entered_api_key
    # global api_key
    myWindow.show()
    pyautogui.alert('아이디 검색 후 게임 시간을 현재 시간과 동일하게 맞춘 후 사용! 텔레포트는 레벨 맞추고 누르기!',
                    '사용법!')
    entered_api_key = pyautogui.prompt('Enter API Key')
    api_key = '?api_key=' + entered_api_key
    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()