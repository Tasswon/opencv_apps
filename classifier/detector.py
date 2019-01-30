import cv2

# call the created classifier
cascade = cv2.CascadeClassifier("cascade.xml")

# use the webcam
video = cv2.VideoCapture(0)

# continually collect frames
while True:
    ret, frame = video.read()

    # detect objects of different sizes
    objects = cascade.detectMultiScale(
        frame,
        scaleFactor = 1.1,
        minNeighbors = 7,
        minSize = (30, 30),
    )

    # display a box around the object
    for (x, y, w, h) in objects:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 50), 2)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) and 0xFF == ord('q'):
        break

# release the webcam and the capture
video.release()
cv2.destroyAllWindows()