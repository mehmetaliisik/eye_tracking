import sys
import cv2
import time
import numpy as np
import urllib.request
import paho.mqtt.client as mqtt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QCursor, QTransform
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QDesktopWidget, QMainWindow, QApplication, QAction, QHBoxLayout, QPushButton



class CameraWidget(QWidget):
    
    def __init__(self, camera_url="http://192.168.4.1"): #camera_indexe DİKAKT ET !!!
        super().__init__()
        
        self.camera_url = camera_url
        self.camera_stream = urllib.request.urlopen(camera_url)
        self.camera_bytes = b''

        self.camera_label = QLabel(self)
        self.camera_label.setAlignment(Qt.AlignCenter)
        """self.arrow_path = "a1.png"
        self.arrow = cv2.imread(self.arrow_path, cv2.IMREAD_UNCHANGED)"""
        
        self.sq_pixmap = QPixmap("components/tut_birak.png")
        self.arrow_pixmap = QPixmap("components/a1.png")
        
        self.arrow_width=int(948/10)
        self.arrow_height=int(1297/10)
        self.sq_width = 150
        self.sq_height = 50

        self.scaled_sq_pixmap = self.sq_pixmap.scaled(self.sq_width, self.sq_height)
        self.scaled_sq_pixmap180 = self.scaled_sq_pixmap.transformed(QTransform().rotate(180)) #DEĞİŞTİR
        
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
        
        self.camera_bytes += self.camera_stream.read(1024)
        a = self.camera_bytes.find(b'\xff\xd8')
        b = self.camera_bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            try:
                jpg = self.camera_bytes[a:b + 2]
                self.camera_bytes = self.camera_bytes[b + 2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.camera_height, self.camera_width, channel = frame.shape
                    bytes_per_line = 3 * self.camera_width
                    q_image = QImage(frame.data, self.camera_width, self.camera_height, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(q_image)

                    # arrow konum hesapları
                    arrow_h_center = int((self.camera_height / 2) - (self.arrow_height / 2))
                    arrow_w_center = int((self.camera_width / 2) - (self.arrow_height / 2))
                    arrow_r_max = int(self.camera_width - self.arrow_width)
                    arrow_b_max = int(self.camera_height - self.arrow_width)

                    # arrow seçimi ve konum belirleme
                    painter = QPainter(pixmap)
                    painter.drawPixmap(arrow_w_center, 0, self.scaled_arrow_pixmap270)
                    painter.drawPixmap(arrow_r_max, arrow_h_center, self.scaled_arrow_pixmap)
                    painter.drawPixmap(arrow_w_center, arrow_b_max, self.scaled_arrow_pixmap90)
                    painter.drawPixmap(0, arrow_h_center, self.scaled_arrow_pixmap180)
                    painter.end()

                    self.camera_label.setPixmap(pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio))

                    self.camera_label.setPixmap(self.camera_label.pixmap().transformed(QTransform().rotate(180)))
                
            except Exception as e:
                # Print any errors that occur during execution
                print(f"Error: {e}")
            

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
        base_eye = arac_menu.addMenu('Baskın Gözü Seçin')
        base_eye_left = QAction('Sol Göz', self)
        base_eye_right = QAction('Sağ Göz', self)
        base_eye_left.setShortcut('Ctrl+L')
        base_eye_right.setShortcut('Ctrl+R')
        base_eye.addAction(base_eye_left)
        base_eye.addAction(base_eye_right)

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

        
        self.blink_counter = 0
        
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
        message = ""
        border = ""
        
        with open("components/screen.txt", "r") as file1:
            border = file1.readline()
        file1.close()
        
        self.text_widget.setText(f"Fare pozisyonu(x)(y): ({pos.x()}, {pos.y()})")
        if border != "Out":
            if (    pos.x() >= 0
                and pos.x() <= (self.desk_width*(1/3))
                and pos.y() >= (self.desk_height*(1/3))
                and pos.y() <= (self.desk_height*(2/3))):
                self.text_widget2.setText("SOL")
                message = "left"
            elif(    pos.x() > self.desk_width*(1/3)
                and pos.x() <= (self.desk_width*(2/3))
                and pos.y() >= 0
                and pos.y() <= (self.desk_height*(1/3))):
                self.text_widget2.setText("YUKARI")
                message = "forward"
            elif(    pos.x() > self.desk_width*(1/3)
                and pos.x() <= (self.desk_width*(2/3))
                and pos.y() > (self.desk_height*(1/3))
                and pos.y() <= (self.desk_height*(2/3))):
                self.text_widget2.setText("ORTA")
                # Read blink information from the file
                try:
                    with open("components/blink.txt", "r") as file2:
                        lines = file2.readlines()
                        is_right_blink = int(lines[0])
                        is_both_blink = int(lines[2])
                    file2.close()
                    if (is_right_blink == 1 and is_both_blink != 1):
                        if (self.blink_counter == 0):
                            message = "startsq"
                            self.blink_counter += 1
                        elif (self.blink_counter == 1):
                            message = "stopsq"
                            self.blink_counter += 1
                        else:
                            message = "release"
                            self.blink_counter = 0
                except Exception as e:
                    # Print any errors that occur during execution
                    print(f"Error: {e}")
                        
            elif(    pos.x() > self.desk_width*(1/3)
                and pos.x() <= (self.desk_width*(2/3))
                and pos.y() > (self.desk_height*(2/3))
                and pos.y() <= (self.desk_height*(3/3))):
                self.text_widget2.setText("AŞAĞI")
                message = "backward"
            elif(    pos.x() > self.desk_width*(2/3)
                and pos.x() <= (self.desk_width*(3/3))
                and pos.y() > (self.desk_height*(1/3))
                and pos.y() <= (self.desk_height*(2/3))):
                self.text_widget2.setText("SAĞ")
                message = "right"
            else:
                self.text_widget2.setText("")
        
        client.publish("command/move", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MyMainWindow()
    main_win.show()
    
    client = mqtt.Client()
    # Connect to the MQTT broker
    client.connect("192.168.4.3", 1883, 60)
    
    sys.exit(app.exec_())