from flask import Flask, render_template, Response
import cv2
import numpy as np
import HandDetectModule as hdm
import dalgona_result as dr
import random
from threading import Thread
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

#######################
brushThickness = 10
display_size_width = 400
display_size_height = 400
startlist = [[200, 116], [200, 97], [200, 88], [200, 95], [200, 95]]  # 1. 삼각형, 2.원, 3.별, 4. 트리, 5. 우산
imglist = ["img/tri.jpg", "img/circle.jpg", "img/star.jpg", "img/tree.jpg", "img/um.jpg"]
########################

global start_condition
start_condition = False
global starttimer
starttimer = False
global hand_co
global img
global result
result = "0"
global shape_num
global remain_time
remain_time = 15

cap = cv2.VideoCapture(0)
color = (0, 0, 0)  # 컬러지정
cap.set(3, display_size_width)  # 가로 크기 수정
cap.set(4, display_size_height)  # 세로 크기 수정

detector = hdm.MPHands(detectionCon=0.75, maxHands=1)
xp, yp = 0, 0

success, img1 = cap.read()
img2 = cv2.flip(img1, 1)
img2 = detector.DetectHand(img2)
hand_co = detector.DetectCoordi(img2, draw=False)


def timer(startlist, shape_num):
    global start_condition
    global starttimer
    global img
    time_limit = time.time() + 3
    while time.time() < time_limit:
        cv2.putText(img, str(round(time_limit - time.time())), (550, 100), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 2)
        if start_condition == False and startlist[shape_num][0] - 10 < x1 < startlist[shape_num][0] + 10 and \
                startlist[shape_num][1] - 10 < y1 < startlist[shape_num][1] + 10:
            pass

        else:
            starttimer = False
            return

    start_condition = True
    thread = Thread(target=timer1, args=())
    thread.start()


def timer1():
    global remain_time
    global start_condition
    time_limit = time.time() + 15
    while time.time() < time_limit:
        remain_time = round(time_limit - time.time())
        cv2.putText(img, str(remain_time), (500, 100), cv2.FONT_HERSHEY_DUPLEX, 3, (255, 0, 0), 2)
        if start_condition == False:
            return


def gen_frames():
    global start_condition
    global starttimer
    global hand_co
    global img
    global result
    global shape_num
    global remain_time

    # 달고나 모양 좌표 추출
    imgCanvas = cv2.imread(imglist[shape_num])
    imgray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    ret, thr = cv2.threshold(imgray, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # 비교를 위한 결과값
    imgCanvas1 = np.ones((400, 400, 3), np.uint8) * 255
    log = []
    while True:
        success, img1 = cap.read()
        if not success:
            break
        else:
            img2 = cv2.flip(img1, 1)

            # 손인식, 손가락 좌표 검출
            img = detector.DetectHand(img2)
            hand_co = detector.DetectCoordi(img, draw=False)

            if len(hand_co) != 0:

                # 8, 12번 x,y값
                global x1, y1
                x1, y1 = hand_co[8][1:]

                # 손가락업 판별
                fingers = detector.Up()

                # 손가락 2개 업일 때
                if fingers[1] and fingers[2] and start_condition == False:
                    xp, yp = 0, 0
                    cv2.putText(img, "Go to start point", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)
                    # 처음 시작 타이머
                    if starttimer == False and startlist[shape_num][0] - 10 < x1 < startlist[shape_num][0] + 10 and \
                            startlist[shape_num][1] - 10 < y1 < startlist[shape_num][1] + 10:
                        starttimer = True
                        thread = Thread(target=timer, args=(startlist, shape_num))
                        thread.start()

                if fingers[1] and fingers[2] == False and starttimer == False:
                    cv2.putText(img, "Two Fingers UP!", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)

                # 손가락 1개 업일 때
                if fingers[1] and fingers[2] == False and start_condition == True:
                    cv2.circle(img, (x1, y1), 15, color, cv2.FILLED)

                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1

                    cv2.line(imgCanvas1, (xp, yp), (x1, y1), color, brushThickness)
                    xp, yp = x1, y1

                    # 좌표 비교(채점)
                    correct = False
                    broken = True
                    for i in range(len(contours[1])):
                        if contours[1][i][0][0] - 20 < x1 < contours[1][i][0][0] + 20 and \
                                contours[1][i][0][1] - 20 < y1 < contours[1][i][0][1] + 20 and broken == True:
                            broken = False

                        if (contours[1][i][0][0] - 8 < x1 < contours[1][i][0][0] + 8) and \
                                (contours[1][i][0][1] - 8 < y1 < contours[1][i][0][1] + 8):
                            correct = True
                            print("ALIVE")
                            log.append(1)
                            break
                    if broken == True:
                        print("Dalgona Broken")
                        result = "2"
                        return "Dalgona Broken"
                    if correct == False:
                        print("*********************die***********************")
                        log.append(0)
                    print(len(log))
                    if correct == True and startlist[shape_num][0] - 5 < x1 < startlist[shape_num][0] + 5 and \
                            startlist[shape_num][1] - 5 < y1 < startlist[shape_num][1] + 5 and 150 < len(log):
                        print("game complete----------------")
                        # result = "2"
                        break
            if remain_time == 0:
                result = "3"
                return

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    if dr.score(contours[1], imgCanvas1, shape_num) == "success":
        score = log.count(1) / len(log) * 100
        result = str(score)
        return "점수 : " + str(log.count(1) / len(log) * 100)
    elif dr.score(contours[1], imgCanvas1, shape_num) == "fail":
        print("실패")
        result = "1"
        return "실패"


def gen_frames1():
    global start_condition
    global hand_co
    global result
    global shape_num

    time.sleep(0.2)
    while result == "0":
        if start_condition == False:
            imgCanvas = cv2.imread(imglist[shape_num])

        if len(hand_co) != 0:

            # 8, 12번 x,y값
            x1, y1 = hand_co[8][1:]

            # 손가락업 판별
            fingers = detector.Up()

            # 손가락 2개 업일 때
            if fingers[1] and fingers[2] and start_condition == False:
                xp, yp = 0, 0
                cv2.circle(imgCanvas, (x1, y1), 8, color, cv2.FILLED)

            # 손가락 1개 업일 때
            if fingers[1] and fingers[2] == False and start_condition == True:

                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                cv2.line(imgCanvas, (xp, yp), (x1, y1), color, brushThickness)
                xp, yp = x1, y1

        ret, buffer = cv2.imencode('.jpg', imgCanvas)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    if result == "2":
        cv2.line(imgCanvas, (xp, yp), (200, 200), (200, 200, 200), 6)
        if xp <= 200:
            if yp <= 200:
                cv2.line(imgCanvas, (320, 320), (200, 200), (200, 200, 200), 6)
            else:
                cv2.line(imgCanvas, (320, 80), (200, 200), (200, 200, 200), 6)
        else:
            if yp <= 200:
                cv2.line(imgCanvas, (80, 320), (200, 200), (200, 200, 200), 6)
            else:
                cv2.line(imgCanvas, (80, 80), (200, 200), (200, 200, 200), 6)

        xp, yp = x1, y1
        ret2, buffer2 = cv2.imencode('.jpg', imgCanvas)
        frame2 = buffer2.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame2 + b'\r\n')

    return


@app.route("/", methods=['GET', 'POST'])
def index():
    global start_condition
    start_condition = False
    global starttimer
    starttimer = False
    global result
    global shape_num
    result = "0"
    global remain_time
    remain_time = 15


@app.route('/video_feed')
def video_feed():
    global start_condition
    start_condition = False
    global starttimer
    starttimer = False
    global result
    global shape_num
    result = "0"
    global remain_time
    remain_time = 15

    # 달고나 모양 랜덤 선택
    shape_num = random.randrange(0, 5)
    # shape_num = 0
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed1')
def video_feed1():
    return Response(gen_frames1(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/rr')
def rr():
    global result
    return result


if __name__ == '__main__':
    app.run(debug=False, host="127.0.0.1", port=5000, threaded=True, use_reloader=False)