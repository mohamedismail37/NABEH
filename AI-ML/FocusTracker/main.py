import cv2
import mediapipe as mp
import time
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

cap = cv2.VideoCapture(0)

not_focused_start = None
WARNING_THRESHOLD = 5  # seconds

def get_head_direction(landmarks):
    nose = landmarks[1]
    left_face = landmarks[234]
    right_face = landmarks[454]

    face_width = abs(left_face.x - right_face.x)
    nose_offset = nose.x - (left_face.x + face_width / 2)

    # normalize
    ratio = nose_offset / face_width

    return ratio  

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    focused = True

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            landmarks = face_landmarks.landmark
            direction = get_head_direction(landmarks)

            if abs(direction) > 0.3:
                focused = False
    else:
        focused = False

    #track time when not focused
    if not focused:
        if not_focused_start is None:
            not_focused_start = time.time()
        else:
            elapsed = time.time() - not_focused_start
            if elapsed > WARNING_THRESHOLD:
                cv2.putText(frame, "WARNING: Not Focused!",
                            (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2)
    else:
        not_focused_start = None

    status = "Focused" if focused else "Not Focused"
    cv2.putText(frame, status,
                (50, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0) if focused else (0, 0, 255), 2)

    cv2.imshow("Focus Tracker", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()