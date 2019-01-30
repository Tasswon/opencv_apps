import cv2
import sys
import datetime
import numpy as np

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QWidget, QFileDialog
from PyQt5.uic import loadUi
from scipy.spatial import Delaunay


class Imgage_morph(QDialog):
    def __init__(self):
        super(Imgage_morph, self).__init__()
        loadUi('gui.ui', self)
        self.img1 = None
        self.img2 = None
        self.outFeed1 = None
        self.outFeed2 = None
        self.keypoint1 = []
        self.keypoint2 = []
        self.keypoint3 = []
        self.delaunay = None
        self.feed = None
        self.alpha = 0.5
        self.width = 200
        self.height = 200
        self.selectImg1.clicked.connect(self.select_image1)
        self.selectImg2.clicked.connect(self.select_image2)
        self.captureCam.clicked.connect(self.capture_cam)
        self.startCam.clicked.connect(self.start_camera)
        self.stopCam.clicked.connect(self.stop_camera)
        self.morphButton.clicked.connect(self.morph)
        self.delauney.clicked.connect(self.delauney_triangulation)
        self.image1.mousePressEvent = self.detect_keypoint1
        self.image2.mousePressEvent = self.detect_keypoint2

    # select keypoint 1 set
    def detect_keypoint1(self, e):
        if self.img1 is None:
            warning = QWidget()
            QMessageBox.warning(warning, "Message", "No image selected!")
        else:
            # get coordinates and apply rectangle to point
            x = e.pos().x()
            y = e.pos().y()
            z = [x, y]

            # add coordinates to keywords
            self.keypoint1.append(z)

            # apply tiny rectangle to coordinate (pen object)
            self.image1.setPixmap(QPixmap.fromImage(self.outFeed1))
            self.image1.setAlignment(Qt.AlignCenter)
            painterInstance = QPainter(self.outFeed1)
            penRectangle = QPen(Qt.red)
            painterInstance.setPen(penRectangle)
            painterInstance.drawRect(x, y, 2, 2)
            self.image1.setPixmap(QPixmap.fromImage(self.outFeed1))

    # select keypoint 2 set
    def detect_keypoint2(self, e):
        if self.img2 is None:
            warning = QWidget()
            QMessageBox.warning(warning, "Message", "No image selected!")
        else:
            # get coordinates and apply rectangle to point
            x = e.pos().x()
            y = e.pos().y()
            z = [x, y]

            # add coordinates to keywords
            self.keypoint2.append(z)

            # apply tiny rectangle to coordinate (pen object)
            self.image2.setPixmap(QPixmap.fromImage(self.outFeed2))
            self.image2.setAlignment(Qt.AlignCenter)
            painterInstance = QPainter(self.outFeed2)
            penRectangle = QPen(Qt.red)
            painterInstance.setPen(penRectangle)
            painterInstance.drawRect(x, y, 2, 2)
            self.image2.setPixmap(QPixmap.fromImage(self.outFeed2))

    # sets up the delauney triangulation before the morphing (based on formula)
    def delauney_triangulation(self):
        # result delaunay array and keypoints for intermediate (adjustment) image
        self.delaunay = []
        self.keypoints3 = []

        # ensure keypoints have been filled, and have the same number between images
        if len(self.keypoint1) != len(self.keypoint2) or len(self.keypoint1) <= 3:
            warning = QWidget()
            QMessageBox.warning(warning, "Message", "Must have same number of key points and at least four!")
        else:
            # generate average points between two, and the delaunay triangle for the result
            for i in range(len(self.keypoint1)):
                x = int((self.keypoint1[i][0] + self.keypoint2[i][0]) / 2)
                y = int((self.keypoint1[i][1] + self.keypoint2[i][1]) / 2)

                # add the resulting keypoints to the intermediate array
                self.keypoint3.append([x, y])

            # generate the delaunay triangles based on the new keypoints (library functions using generated keypoints)
            tri = Delaunay(self.keypoint3, False, False, qhull_options = "QJ")
            self.delaunay = tri.simplices

            # draw lines for the triangulation on image 1
            self.image1.setPixmap(QPixmap.fromImage(self.outFeed1))
            self.image1.setAlignment(Qt.AlignCenter)
            painterInstance = QPainter(self.outFeed1)
            penRectangle = QPen(Qt.red)
            painterInstance.setPen(penRectangle)
            for i in range(len(self.delaunay)):
                painterInstance.drawLine(self.keypoint1[self.delaunay[i][0]][0], self.keypoint1[self.delaunay[i][0]][1],
                                         self.keypoint1[self.delaunay[i][1]][0], self.keypoint1[self.delaunay[i][1]][1])
                painterInstance.drawLine(self.keypoint1[self.delaunay[i][1]][0], self.keypoint1[self.delaunay[i][1]][1],
                                         self.keypoint1[self.delaunay[i][2]][0], self.keypoint1[self.delaunay[i][2]][1])
                painterInstance.drawLine(self.keypoint1[self.delaunay[i][2]][0], self.keypoint1[self.delaunay[i][2]][1],
                                         self.keypoint1[self.delaunay[i][0]][0], self.keypoint1[self.delaunay[i][0]][1])
            # display the triangles in image 1
            self.image1.setPixmap(QPixmap.fromImage(self.outFeed1))

            # draw lines for the triangulation on image 2
            self.image2.setPixmap(QPixmap.fromImage(self.outFeed2))
            self.image2.setAlignment(Qt.AlignCenter)
            painterInstance = QPainter(self.outFeed2)
            penRectangle = QPen(Qt.red)
            painterInstance.setPen(penRectangle)
            for i in range(len(self.delaunay)):
                painterInstance.drawLine(self.keypoint2[self.delaunay[i][0]][0], self.keypoint2[self.delaunay[i][0]][1],
                                         self.keypoint2[self.delaunay[i][1]][0], self.keypoint2[self.delaunay[i][1]][1])
                painterInstance.drawLine(self.keypoint2[self.delaunay[i][1]][0], self.keypoint2[self.delaunay[i][1]][1],
                                         self.keypoint2[self.delaunay[i][2]][0], self.keypoint2[self.delaunay[i][2]][1])
                painterInstance.drawLine(self.keypoint2[self.delaunay[i][2]][0], self.keypoint2[self.delaunay[i][2]][1],
                                         self.keypoint2[self.delaunay[i][0]][0], self.keypoint2[self.delaunay[i][0]][1])
            # display the triangles in image 2
            self.image2.setPixmap(QPixmap.fromImage(self.outFeed2))

    def morph(self):
        # warning ensures that the delaunay triangles have been generated before performing the morph
        if self.delaunay is None:
            warning = QWidget()
            QMessageBox.warning(warning, "Message", "Please generate delaunay triangles first!")
        else:
            # return a numpy array filled with zeroes, which will hold the new image (errors when changing originals)
            img1 = np.zeros((self.height, self.width, 3))
            img2 = np.zeros((self.height, self.width, 3))

            # loop for the number of triangles that have been generated
            for i in range(len(self.delaunay)):
                temp1 = [self.keypoint1[self.delaunay[i][0]][0], self.keypoint1[self.delaunay[i][0]][1]]
                temp2 = [self.keypoint1[self.delaunay[i][1]][0], self.keypoint1[self.delaunay[i][1]][1]]
                temp3 = [self.keypoint1[self.delaunay[i][2]][0], self.keypoint1[self.delaunay[i][2]][1]]

                temp4 = [self.keypoint2[self.delaunay[i][0]][0], self.keypoint2[self.delaunay[i][0]][1]]
                temp5 = [self.keypoint2[self.delaunay[i][1]][0], self.keypoint2[self.delaunay[i][1]][1]]
                temp6 = [self.keypoint2[self.delaunay[i][2]][0], self.keypoint2[self.delaunay[i][2]][1]]

                temp7 = [self.keypoint3[self.delaunay[i][0]][0], self.keypoint3[self.delaunay[i][0]][1]]
                temp8 = [self.keypoint3[self.delaunay[i][1]][0], self.keypoint3[self.delaunay[i][1]][1]]
                temp9 = [self.keypoint3[self.delaunay[i][2]][0], self.keypoint3[self.delaunay[i][2]][1]]

                # create three arrays filled with the current looped triangles
                tri1 = ([temp1, temp2, temp3])
                tri2 = ([temp4, temp5, temp6])
                tri3 = ([temp7, temp8, temp9])

                # get affine transforms from cropped images (relative to intermediary)
                aff_tran_1 = cv2.getAffineTransform(np.float32(tri1), np.float32(tri3))
                aff_tran_2 = cv2.getAffineTransform(np.float32(tri2), np.float32(tri3))

                # apply affine transform that was calculated
                apply_aff_1 = cv2.warpAffine(self.img1, aff_tran_1, (200, 200))
                apply_aff_2 = cv2.warpAffine(self.img2, aff_tran_2, (200, 200))

                # store warped results
                for i in range(200):
                    for j in range(200):
                        img1[i][j] = apply_aff_1[i][j]
                        img2[i][j] = apply_aff_2[i][j]

            # image blending formula, where alpha is 0.5
            img = (1.0 - self.alpha) * img1 + self.alpha * img2

            # display the new image
            self.display_image(np.uint8(img), self.resultImage)

    # old code (algorithm above)
    # select the image 1
    def select_image1(self):
        # reset arrays
        self.outFeed1 = None
        self.keypoint1 = []
        self.delaunay = None

        # open file dialog and select
        temp = QFileDialog.getOpenFileName(self, 'Select an Image')
        fileName = temp[0]
        self.img1 = cv2.imread(fileName)
        self.fileBox1.setText(fileName)
        self.display_image(self.img1, self.image1)

    # select the image 2
    def select_image2(self):
        # reset keypoint array
        self.outFeed2 = None
        self.keypoint2 = []
        self.delaunay = None

        # open file dialog and select
        temp = QFileDialog.getOpenFileName(self, 'Select an Image')
        fileName = temp[0]
        self.img2 = cv2.imread(fileName)
        self.fileBox2.setText(fileName)
        self.display_image(self.img2, self.image2)

    # display the image on the screen
    def display_image(self, img, side):
        if img is None:
            warning = QWidget()
            QMessageBox.warning(warning, "Message", "No image selected!")
        else:
            # temp variable for changing size of original at the end
            temp = img

            # resize the image for the frame
            width = img.shape[1]
            height = img.shape[0]
            if height > width:
                height = 200
                width = int(img.shape[1] / int(img.shape[0]) * 200)
                dim = (width, height)
                img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                side.resize(width, height)
            else:
                height = int(img.shape[0] / int(img.shape[1]) * 200)
                width = 200
                dim = (width, height)
                img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                side.resize(width, height)

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

            # adjust original image size
            if temp is self.img1:
                self.img1 = img
                self.outFeed1 = outFeed
            elif temp is self.img2:
                self.img2 = img
                self.outFeed2 = outFeed

            # apply image and center it
            side.setPixmap(QPixmap.fromImage(outFeed))
            side.setAlignment(Qt.AlignCenter)

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
        dateVar = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = "snapshot_{}.png".format(dateVar)
        cv2.imwrite(filename, self.feed)


app = QApplication(sys.argv)
window = Imgage_morph()
window.setWindowTitle("Image Morph")
window.show()
sys.exit(app.exec_())


