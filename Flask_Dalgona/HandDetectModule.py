import cv2
import mediapipe as mp
 
class MPHands():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
 
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipends = [4, 8, 12, 16, 20]
 
    # 손 인식
    def DetectHand(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        # 손모양 표시
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, hand_landmarks,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
 
    # 0 ~ 20번 포인트까지 x, y값 검출
    def DetectCoordi(self, img, handNo=0, draw=True): #handNo = 손 갯수
 
        self.coordinates = []
        if self.results.multi_hand_landmarks:
            for index, co in enumerate(self.results.multi_hand_landmarks[handNo].landmark):
                h, w, c = img.shape
                cx, cy = int(co.x * w), int(co.y * h)
                self.coordinates.append([index, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
 
        return self.coordinates

    def Up(self):
        fingers_state = []
        # 엄지손가락
        if self.coordinates[self.tipends[0]][1] < self.coordinates[self.tipends[0] - 1][1]: #엄지손가락 3번, 4번 x값비교
            fingers_state.append(1)
        else:
            fingers_state.append(0)
    
        # 나머지 손가락
        for id in range(1, 5):
            if self.coordinates[self.tipends[id]][2] < self.coordinates[self.tipends[id] - 2][2]: #나머지손가락 8,6 / 12,10 / 16,14 / 20,18 y값 비교
                fingers_state.append(1)
            else:
                fingers_state.append(0)

        return fingers_state