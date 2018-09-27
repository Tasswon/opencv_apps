import uuid

import cv2
import sys

from math import floor
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QWidget, QFileDialog
from PyQt5.uic import loadUi


class AssignmentOne(QDialog):
    def __init__(self):
        super(AssignmentOne, self).__init__()
        loadUi('gui.ui', self)
        self.img = None
        self.feed = None
        self.selectImg.clicked.connect(self.select_image)
        self.histogramEq.clicked.connect(self.histogram_equalization)
        self.captureCam.clicked.connect(self.capture_cam)
        self.startCam.clicked.connect(self.start_camera)
        self.stopCam.clicked.connect(self.stop_camera)

    # select the image
    def select_image(self):
        temp = QFileDialog.getOpenFileName(self, 'Select an Image')
        fileName = temp[0]
        self.img = cv2.imread(fileName)
        self.fileBox.setText(fileName)
        self.displayImage(self.img, self.beforeImage)

    # display the image on the screen
    def displayImage(self, img, side):
        if self.img is None:
            warning = QWidget()
            QMessageBox.warning(warning, "Message", "No image selected!")
        else:
            # resize the image for the frame
            width = img.shape[1]
            height = img.shape[0]
            if height > width:
                height = 195
                width = int(img.shape[1] / int(img.shape[0]) * 195)
                dim = (width, height)
                img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            else:
                height = int(img.shape[0] / int(img.shape[1]) * 195)
                width = 195
                dim = (width, height)
                img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

            qformat = QImage.Format_Indexed8
            if len(img.shape) == 3:
                if img.shape[2] == 4:
                    qformat = QImage.Format_RGBA8888
                else:
                    qformat = QImage.Format_RGB888

                    # creates it for the output box
                    outFeed = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)

            # swap colour channels as opencv uses BGR for some reason
            outFeed = outFeed.rgbSwapped()

            # apply image and center it
            side.setPixmap(QPixmap.fromImage(outFeed))
            side.setAlignment(Qt.AlignCenter)

    # performs a histogram equalization (receives image from class variable)
    def histogram_equalization(self):
        # warning if image is empty or invalid
        if self.img is None:
            warning = QWidget()
            QMessageBox.warning(warning, "Message", "No image selected!")
        else:
            # get sizing properties of the image
            row = self.img.shape[0]
            col = self.img.shape[1]
            pic_size = self.img.size / self.img.shape[2]

            # arrays for counting instances for each rgb value
            b = [0] * 256
            g = [0] * 256
            r = [0] * 256

            # count the the instances of each intensity value
            for i in range(0, row):
                for j in range(0, col):
                    intensity = self.img[i][j]

                    blue = intensity[0]
                    green = intensity[1]
                    red = intensity[2]

                    b[blue] += 1
                    g[green] += 1
                    r[red] += 1

            # divide the resulting intensity sums by the total image size
            for i in range(0, 256):
                b[i] /= pic_size
                g[i] /= pic_size
                r[i] /= pic_size

            # sum the products into each preceding divided value
            for i in range(1, 256):
                b[i] += b[i - 1]
                g[i] += g[i - 1]
                r[i] += r[i - 1]

            # get the new intensity values by multiplying the result by the rbg range and floor rounding
            for i in range(0, 256):
                b[i] = floor(b[i] * 255)
                g[i] = floor(g[i] * 255)
                r[i] = floor(r[i] * 255)

            # insert the new intensity values into the image
            for i in range(0, row):
                for j in range(0, col):
                    intensity = self.img[i][j]

                    blue = intensity[0]
                    green = intensity[1]
                    red = intensity[2]

                    self.img[i][j][0] = b[blue]
                    self.img[i][j][1] = g[green]
                    self.img[i][j][2] = r[red]

            # display the image
            self.displayImage(self.img, self.afterImage)

    # creates the video capture
    def start_camera(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        # creates the timer and updates the frame (call update frame every minute)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

    # flips the feed and displays it in the window (read the image feed)
    # ret = obtain return value from image frame
    def update_frame(self):
        ret, self.feed = self.capture.read()
        self.feed = cv2.flip(self.feed, 1)
        self.display_feed(self.feed, 1)

    # decides what format to use the feed as (monochromatic, RGB, RGBA)
    def display_feed(self, img, window = 1):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        # creates it for the output box
        self.outFeed = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)

        # swap colour channels as opencv uses BGR for some reason
        self.outFeed = self.outFeed.rgbSwapped()

        # apply camera and scale it
        if window == 1:
            self.camera.setPixmap(QPixmap.fromImage(self.outFeed))
            self.camera.setScaledContents(True)

    # stops the web camera
    def stop_camera(self):
        self.timer.stop()
        self.camera.clear()

    # captures an image from the camera
    def capture_cam(self):
        filename = "snapshot_{}.png".format(str(uuid.uuid4()))
        cv2.imwrite(filename, self.feed)


app = QApplication(sys.argv)
window = AssignmentOne()
window.setWindowTitle("Assignment One")
window.show()
sys.exit(app.exec_())


