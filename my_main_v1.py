import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QUrl, QThread
from PyQt5 import QtCore
from PyQt5 import uic
from lib.MyViewerLayout import Ui_MainWindow
from lib.MyAuthDialog import AuthDialog
from lib.MyIntroWorker import MyIntroWorker
import pytube
import re
import datetime
from PyQt5.QtMultimedia import QSound
# import os
# os.path 절대경로 불러와서 join 해서 파일불러와야함 --> 상대경로 하는법도 연습ㅋ

# form_class = uic.loadUiType("D:/inflearn/crawling/section6/ui/my_viewer_v1.0.ui")[0]

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # 초기화
        self.setupUi(self)
        # 초기  잠구는 메소드
        self.initAuthLock()
        self.initSignal()  # 프로그램이 실행될때 시그널 초기화
        # 로그인 관련 변수 선언
        self.user_id = None
        self.user_pw = None
        # 재생 여부
        self.is_play = False
        # youtube 관련 작업
        self.youtb = None
        self.youtb_fsize = 0
        # 배경음악 Thread 작업 선언
        self.initIntroThread()
        # QThread 사용안할 경우
        # 레퍼런스 보면 여러옵션이 있음(replay 등등)
        # QSound.play("D:/inflearn/crawling/section6/resource/intro.wav")

    # 기본 UI 비활성화
    def initAuthLock(self):  # 인증받기전에 모든 버튼 비활성화 (종료버튼만 내비둠)
        self.previewButton.setEnabled(False)  # 확인버튼 비활성화
        self.fileNavButton.setEnabled(False)  # ... 버튼 비활성화
        self.streamCombobox.setEnabled(False)
        self.startButton.setEnabled(False)
        self.calendarWidget.setEnabled(False)
        self.urlTextEdit.setEnabled(False)
        self.pathTextEdit.setEnabled(False)
        self.showStatusMsg('인증 안됨')

    # 기본 UI 활성화
    def initAuthActive(self):
        self.previewButton.setEnabled(True)
        self.fileNavButton.setEnabled(True)
        self.streamCombobox.setEnabled(True)
        # self.startButton.setEnabled(True)  # 스타트버튼은 제외 (동영상이 있어야 활성화되도록)
        self.calendarWidget.setEnabled(True)
        self.urlTextEdit.setEnabled(True)
        self.pathTextEdit.setEnabled(True)
        self.showStatusMsg('인증 완료')

    def showStatusMsg(self, msg):
        self.statusbar.showMessage(msg)

    # 시그널 초기화
    def initSignal(self):
        self.loginButton.clicked.connect(self.authCheck)
        self.previewButton.clicked.connect(self.load_url)
        # 자기자신을 가져오는 인스턴스 호출 (실행되는 자기자신의 주소값, 인스턴스)
        self.exitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.webEngineView.loadProgress.connect(self.showProgressBrowserLoading)
        self.fileNavButton.clicked.connect(self.selectDownPath)
        self.calendarWidget.clicked.connect(self.append_date)
        self.startButton.clicked.connect(self.downloadYoutb)

    # 인트로 쓰레드 초기화 및 활성화
    def initIntroThread(self):
        # worker 선언
        self.introObj = MyIntroWorker()  # 클래스를 인스턴스화
        # QThread 선언
        self.introThread = QThread()  # Pyqt에서 제공하는 Qthread 인스턴스화
        # worker to thread 전환
        self.introObj.moveToThread(self.introThread)  # QObject에서 제공하는 메쏘드
        # 시그널 연결
        self.introObj.startMsg.connect(self.showIntroInfo)
        # Thread 시작 메소드 연결
        self.introThread.started.connect(self.introObj.playBgm)  # 쓰레드가 시작되면..
        # Thread 스타트버튼은
        self.introThread.start()

    # 인트로 쓰레드 시그널 실행
    def showIntroInfo(self, userName, fileName):
        self.plainTextEdit.appendPlainText("Program started by : " + userName)
        self.plainTextEdit.appendPlainText("Playing intro Information is :")
        self.plainTextEdit.appendPlainText(fileName)

    @pyqtSlot()
    def authCheck(self):
        dlg = AuthDialog()   # 매번 로그인하기 귀찮으니까 잠시 주석처리 아래 네줄
        dlg.exec_()
        self.user_id = dlg.user_id  # MyAuthDialog 에서 가져와야되므로
        self.user_pw = dlg.user_pw

        # 이 부분에서 필요한 경우 실제 로컬 DB 또는 서버로 연홍 후
        # 유저 정보 및 사용 유효기간을 체크하는 코드를 넣어주세요
        # code
        # code
        # print("id: %s password: %s" %(self.user_id, self.user_pw))

        if True:
            self.initAuthActive()  # 버튼들 활성화
            self.loginButton.setText("인증완료")  # 인증버튼 표시에 인증완료로
            self.loginButton.setEnabled(False)  # 인증버튼은 비활성화
            self.urlTextEdit.setFocus(True)
            self.append_log_msg("Login Success")

        else:
            QMessageBox.about(self, "인증오류", "아이디 또는 비밀번호 인증 오류")

    def load_url(self):
        url = self.urlTextEdit.text().strip()
        v = re.compile('^https://www.youtube.com/?')
        if self.is_play:  # True일경우
            self.append_log_msg("Stop Click")
            self.webEngineView.load(QUrl('about:blank'))  # 그냥 빈페이지 띄우기
            self.previewButton.setText("재생")
            self.is_play = False
            self.urlTextEdit.clear()
            self.urlTextEdit.setFocus(True)
            self.startButton.setEnabled(False)
            self.streamCombobox.clear()  # 동영상이 중지되면 스트림 선택 바가 리셋되어야하니까
            self.progressBar_2.setValue(0)  # 다운로드바 0%로 초기화
            self.showStatusMsg("인증완료")  # 맨아래 상태바 표시 바꾸기
        else:
            if v.match(url) is not None:  # 정확하게 매치가 되었다믄
                self.append_log_msg('Play Click')
                self.webEngineView.load(QUrl(url))  # 웹뷰 위치에 보드함수를 쓰고 Qurl로 로딩
                self.showStatusMsg(url + "재생 중")
                self.previewButton.setText("중지")
                self.is_play = True
                self.startButton.setEnabled(True)
                self.initialYouWork(url)
            else:
                QMessageBox.about(self, "URL 형식 오류", "YouTube 주소 형식이 아닙니다.")
                self.urlTextEdit.clear()   # 텍스트 비우고 포커싱 주기
                self.urlTextEdit.setFocus(True)

    def initialYouWork(self, url):
        video_list = pytube.YouTube(url)
        #로딩바 계산
        video_list.register_on_progress_callback(self.showProgressDownLoading)
        self.youtb = video_list.streams.all()
        self.streamCombobox.clear()
        for q in self.youtb:
            print('step1', q.itag, q.mime_type, q.abr)
            tmp_list, str_list = [], []
            tmp_list.append(str(q.mime_type or ''))
            tmp_list.append(str(q.res or ''))
            tmp_list.append(str(q.fps or ''))
            tmp_list.append(str(q.abr or ''))

            # print('step2', tmp_list)
            str_list = [x for x in tmp_list if x != '']
            # print('step3', str_list)
            # print('join', ','.join(str_list))
            self.streamCombobox.addItem(','.join(str_list))

    def append_log_msg(self, act):
        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
        app_msg = self.user_id + " : " + act + " - (" + nowDatetime + ")"
        print(app_msg)
        self.plainTextEdit.appendPlainText(app_msg)  # insertPlainText 줄바꿈 차이

        # 활동 로그 저장 (또는 DB를 사용 추천)
        with open('d:/inflearn/crawling/section6/log/log.txt', 'a') as f:
            f.write(app_msg+'\n')

    @pyqtSlot(int)  # 이 슬롯에는 int가 넘어온다 라고 명시적으로 알려줌
    def showProgressBrowserLoading(self, v):  # v는 딱히 의미없고 그냥 인트..?
        self.progressBar.setValue(v)

    @pyqtSlot()
    def selectDownPath(self):
        # 파일 선택
        # fname = QFileDialog.getOpenFileName(self)
        # self.pathTextEdit.setText(fname[0])  # fname[0]은 파일이름
        # 경로 선택 (폴더선택)
        fpath = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.pathTextEdit.setText(fpath)

    @pyqtSlot()
    def append_date(self):
        cur_date = self.calendarWidget.selectedDate()
        # print('click date', self.calendarWidget.selectedDate().toString())  # 요일 출력
        # print("cur_date", cur_date)
        # print(str(cur_date.year())+'-'+str(cur_date.month())+'-'+str(cur_date.day()))
        self.append_log_msg('Calendar Click')

    @pyqtSlot()
    def downloadYoutb(self):
        down_dir = self.pathTextEdit.text().strip()
        if down_dir is None or down_dir == "" or not down_dir:
            QMessageBox(self, "경로 선택", "다운로드 받을 경로를 선택하세요")
            return None
        # print('fsize', self.youtb_fsize)
        # print('test_size', self.youtb[3].filesize)  filesize 확인 안됨
        self.youtb_fsize = self.youtb[self.streamCombobox.currentIndex()].filesize
        print('fsize', self.youtb_fsize)
        self.youtb[self.streamCombobox.currentIndex()].download(down_dir)
        self.append_log_msg('Download Click')

    # pytube의 레퍼런스 문서를 확인해야만 알수 있는 내용임
    def showProgressDownLoading(self, stream, chunk, file_handle, bytes_remaining):
        # print(int(self.youtb_fsize - bytes_remaining))
        # print('bytes_remaining', bytes_remaining)
        self.progressBar_2.setValue(int(((self.youtb_fsize - bytes_remaining) / self.youtb_fsize) * 100))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_viewer_main = Main()
    my_viewer_main.show()
    app.exec_()

# 디자인이 픽스되었을때 ui 파일을 py파일로 변경하는 명령어(콘솔창에서) -x ui파일명 -o 생성 py 파일명
# pyuic5 -x my_viewer_v1.0.ui -o my_viewer_layout.py
