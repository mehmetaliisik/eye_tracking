import sys
from PyQt5.QtGui import QImage, QPixmap, QPainter, QCursor, QTransform
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QDesktopWidget, QMainWindow, QApplication, QAction, QHBoxLayout, QPushButton
import cv2
import numpy as np
import urllib.request
from io import BytesIO

class CameraWidget(QWidget):
    def __init__(self, camera_index=0): #camera_indexe DİKAKT ET !!!
        super().__init__()

        self.camera = cv2.VideoCapture(camera_index)

        self.camera_label = QLabel(self)
        self.camera_label.setAlignment(Qt.AlignCenter)

        """self.arrow_path = "a1.png"
        self.arrow = cv2.imread(self.arrow_path, cv2.IMREAD_UNCHANGED)"""
        
        self.do_pixmap = QPixmap("tut_birak.png")
        self.arrow_pixmap = QPixmap("a1.png")
        
        self.arrow_width=int(948/10)
        self.arrow_height=int(1297/10)
        self.do_width = 150
        self.do_height = 50

        self.scaled_do_pixmap = self.do_pixmap.scaled(self.do_width, self.do_height)
        self.scaled_arrow_pixmap = self.arrow_pixmap.scaled(self.arrow_width, self.arrow_height)
        self.scaled_arrow_pixmap90 = self.scaled_arrow_pixmap.transformed(QTransform().rotate(90))
        self.scaled_arrow_pixmap180 = self.scaled_arrow_pixmap.transformed(QTransform().rotate(180))
        self.scaled_arrow_pixmap270 = self.scaled_arrow_pixmap.transformed(QTransform().rotate(270))

        layout = QVBoxLayout(self)
        layout.addWidget(self.camera_label)
        
        # kamera frame güncelleme aralığı
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(3)  # milisaniye

    def updateFrame(self):
        
        ret, frame = self.camera.read()
        """y_offset, x_offset = 120, 530
        logo_resized = cv2.resize(self.logo, (100, 200))
        for c in range(0, 3):
            frame[y_offset:y_offset + logo_resized.shape[0], x_offset:x_offset + logo_resized.shape[1], c] = \
            (1.0 - logo_resized[:, :, 3] / 255.0) * frame[y_offset:y_offset + logo_resized.shape[0], x_offset:x_offset + logo_resized.shape[1], c] + \
            (logo_resized[:, :, c] / 255.0) * logo_resized[:, :, c]"""

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.camera_height, self.camera_width, channel = frame.shape
            #print(camera_width,type(camera_width),camera_height,type(camera_height))
            bytes_per_line = 3 * self.camera_width
            q_image = QImage(frame.data, self.camera_width, self.camera_height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            #arrow konum hesapları
            arrow_h_center=int((self.camera_height/2)-(self.arrow_height/2))
            arrow_w_center=int((self.camera_width/2)-(self.arrow_height/2))
            arrow_r_max=int(self.camera_width-self.arrow_width)
            arrow_b_max=int(self.camera_height-(self.arrow_width))

            #arrow seçimi ve konum belirleme
            painter = QPainter(pixmap)
            painter.drawPixmap(arrow_w_center , 0              , self.scaled_arrow_pixmap270)
            painter.drawPixmap(arrow_r_max    , arrow_h_center , self.scaled_arrow_pixmap)
            painter.drawPixmap(arrow_w_center , arrow_b_max    , self.scaled_arrow_pixmap90)
            painter.drawPixmap(0              , arrow_h_center , self.scaled_arrow_pixmap180)
            painter.drawPixmap(int(self.camera_width/2) - int(self.do_width/2) , int(self.camera_height*(3/5)) , self.scaled_do_pixmap)
            painter.end()

            self.camera_label.setPixmap(pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio))
            

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Pencere ayarları
        self.setWindowTitle("Göz Takip Destekli Robot Kol Kontrolü")
        self.showFullScreen()

        #menübar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Dosya')
        exit_action = QAction('Çıkış', self)
        exit_action.setShortcut('Esc')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        arac_menu = menubar.addMenu('Araçlar')
        base_eye = QAction('Baskın Gözü Seçin', self)
        base_eye.setShortcut('Ctrl+L')
        arac_menu.addAction(base_eye)

        central_widget = MyWidget(self)
        self.setCentralWidget(central_widget)

class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QDesktopWidget()
        screen = desktop.screen(0) #hangi ekranı alacağımız
        screen_geometry = screen.geometry()
        self.desk_width = screen_geometry.width()
        self.desk_height = screen_geometry.height()

        v_box = QVBoxLayout(self)
        v_box1= QVBoxLayout(self)
        h_box = QHBoxLayout(self)

        self.text_widget = QLabel(self)
        self.text_widget.resize(200,15)
        self.text_widget.move(5,0)
        self.text_widget2 = QLabel(self)
        self.text_widget2.resize(200,15)
        self.text_widget2.move(215,0)

        self.okay = QPushButton("oki")

        self.camera_widget = CameraWidget()  # arayüz kamera widget oluşturma

        #v_box.addSpacing(-900)
        #v_box.addWidget(self.text_widget)
        #v_box.addStretch()
        #v_box.addSpacing(-500)
        #v_box.addWidget(self.text_widget2)
        #v_box.addStretch()
        #v_box.addSpacing(-100)
        v_box.addWidget(self.camera_widget)
        self.setLayout(v_box)

        

        # fare pozisyonu güncelleme aralığı
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCursorPosition)
        self.timer.start(100)  # milisaniye


    def updateCursorPosition(self):
        
        cursor = QCursor() # fare pozisyonunu alma
        pos = cursor.pos()

        self.text_widget.setText(f"Fare pozisyonu(x)(y): ({pos.x()}, {pos.y()})")
        if (    pos.x() >= 0
            and pos.x() <= (self.desk_width*(1/3))
            and pos.y() >= (self.desk_height*(1/3))
            and pos.y() <= (self.desk_height*(2/3))):
            self.text_widget2.setText("SOL")
        elif(    pos.x() > self.desk_width*(1/3)
            and pos.x() <= (self.desk_width*(2/3))
            and pos.y() >= 0
            and pos.y() <= (self.desk_height*(1/3))):
            self.text_widget2.setText("YUKARI")
        elif(    pos.x() > self.desk_width*(1/3)
            and pos.x() <= (self.desk_width*(2/3))
            and pos.y() > (self.desk_height*(1/3))
            and pos.y() <= (self.desk_height*(2/3))):
            self.text_widget2.setText("ORTA")
        elif(    pos.x() > self.desk_width*(1/3)
            and pos.x() <= (self.desk_width*(2/3))
            and pos.y() > (self.desk_height*(2/3))
            and pos.y() <= (self.desk_height*(3/3))):
            self.text_widget2.setText("AŞAĞI")
        elif(    pos.x() > self.desk_width*(2/3)
            and pos.x() <= (self.desk_width*(3/3))
            and pos.y() > (self.desk_height*(1/3))
            and pos.y() <= (self.desk_height*(2/3))):
            self.text_widget2.setText("SAĞ")
        else:
            self.text_widget2.setText("")


    """def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MyMainWindow()
    main_win.show()
    sys.exit(app.exec_())