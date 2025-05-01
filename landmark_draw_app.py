import cv2
import mediapipe as mp
import numpy as np
from enum import Enum

# Enum for gesture types
class GestureType(Enum):
    NONE = "none"
    DRAW = "draw"
    ERASE = "erase"
    SELECT = "select"
    CLEAR = "clear"
    SAVE = "save"    

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Canvas and drawing config
canvas = np.zeros((480, 640, 3), dtype=np.uint8)
drawing = False
prev_x, prev_y = None, None

# Colors & UI
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]  # red, green, blue, eraser
color_names = ["Red", "Green", "Blue", "Eraser"]
current_color = colors[0]

# Sidebar layout
bar_x, bar_y = 10, 50
bar_w, bar_h = 40, 40
spacing = 10

# State tracking
gesture_buffer = []
buffer_size = 7
gesture_cooldown = 0
gesture_delay = 10  # frames

# Count extended fingers
def get_finger_states(lm):
    states = []

    # Thumb: compare x not y (right hand)
    states.append(lm[4].x < lm[3].x)

    # Index, Middle, Ring, Pinky
    for tip_id in [8, 12, 16, 20]:
        is_up = lm[tip_id].y < lm[tip_id - 2].y
        states.append(is_up)

    return states  # [thumb, index, middle, ring, pinky]


# Classify gesture based on landmarks
def detect_gesture(lm):
    finger_states = get_finger_states(lm)
    thumb, index, middle, ring, pinky = finger_states

    # DRAW: pinch (index + thumb close)
    ix, iy = lm[8].x, lm[8].y
    tx, ty = lm[4].x, lm[4].y
    dist = np.hypot(ix - tx, iy - ty)
    #print("[DEBUG] Pinch distance:", dist)
    if dist < 0.07:
        return GestureType.DRAW

    # ERASE: all fingers up
    if all(finger_states[1:]):  # exclude thumb
        return GestureType.ERASE

    # SELECT: only index finger up
    if index and not (middle or ring or pinky):
        return GestureType.SELECT

    # SAVE: rock gesture = index + pinky
    if index and pinky and not middle and not ring:
        return GestureType.SAVE

    # CLEAR: fist = all fingers down
    if not any([index, middle, ring, pinky]):
        return GestureType.CLEAR

    return GestureType.NONE


# Webcam loop
cap = cv2.VideoCapture(0)
current_gesture = GestureType.NONE

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        lm = hand_landmarks.landmark

        # Detect gesture
        gesture = detect_gesture(lm)
        # DRAW is immediate (no debounce)
        if gesture == GestureType.DRAW:
            current_gesture = GestureType.DRAW

        # Other gestures still require buffering
        else:
            gesture_buffer.append(gesture)
            if len(gesture_buffer) > buffer_size:
                gesture_buffer.pop(0)

            if gesture_buffer.count(gesture_buffer[0]) == buffer_size:
                if gesture_cooldown == 0:
                    current_gesture = gesture_buffer[0]
                    gesture_cooldown = gesture_delay

        if gesture_cooldown > 0:
            gesture_cooldown -= 1

        # Get fingertip coords
        x = int(lm[8].x * w)
        y = int(lm[8].y * h)

        # ---- Action Logic ----
        if current_gesture == GestureType.DRAW:
            if prev_x is not None and prev_y is not None:
                distance = np.hypot(x - prev_x, y - prev_y)
                if distance > 5:
                    cv2.line(canvas, (prev_x, prev_y), (x, y), current_color, 5)
            prev_x, prev_y = x, y

        elif current_gesture == GestureType.SELECT:
            for i, color in enumerate(colors):
                top = bar_y + i * (bar_h + spacing)
                if bar_x < x < bar_x + bar_w and top < y < top + bar_h:
                    current_color = color
                    current_gesture = GestureType.NONE
                    break
            prev_x, prev_y = None, None

        elif current_gesture == GestureType.ERASE:
            canvas[:] = 0
            current_gesture = GestureType.NONE
            prev_x, prev_y = None, None

        elif current_gesture == GestureType.SAVE:
            filename = f"drawing_{int(cv2.getTickCount())}.png"
            cv2.imwrite(filename, canvas)
            print(f"[INFO] Drawing saved as {filename}")
            current_gesture = GestureType.NONE
            prev_x, prev_y = None, None

        elif current_gesture == GestureType.CLEAR:
            current_color = (0, 0, 0)
            current_gesture = GestureType.NONE
            prev_x, prev_y = None, None

        else:
            prev_x, prev_y = None, None

    else:
        prev_x, prev_y = None, None

    # Draw color sidebar
    for i, color in enumerate(colors):
        top = bar_y + i * (bar_h + spacing)
        cv2.rectangle(frame, (bar_x, top), (bar_x + bar_w, top + bar_h), color, -1)
        if color == current_color:
            cv2.rectangle(frame, (bar_x, top), (bar_x + bar_w, top + bar_h), (255, 255, 255), 2)

    # Show gesture status & result
    combined = cv2.addWeighted(frame, 1, canvas, 1, 0)
    cv2.putText(combined, f"Gesture: {current_gesture.value}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 255, 200), 2)
    cv2.imshow("Gesture Canvas", combined)

    # Quit on Q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
