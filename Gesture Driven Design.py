import cv2
import mediapipe as mp
import math
import numpy as np
import serial
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize Mediapipe Hands module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize system volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# Initialize serial communication with Arduino
ser = serial.Serial('COM6', 9600)  # Adjust COM port as needed
time.sleep(2)  # Wait for Arduino to initialize

# Initialize webcam
wCam, hCam = 640, 480
cam = cv2.VideoCapture(0)
cam.set(3, wCam)
cam.set(4, hCam)

# Load images for menu selection
img_n1 = cv2.imread('n1.png')
img_n2 = cv2.imread('n2.png')
img_n3 = cv2.imread('n3.png')

# Resize images to 62x60 pixels
img_n1 = cv2.resize(img_n1, (62, 60))
img_n2 = cv2.resize(img_n2, (62, 60))
img_n3 = cv2.resize(img_n3, (62, 60))

# Variables to store menu state and color selection
menu = 1  # Start with LED Color Control Menu
last_color = 'None'

# Adjust positions for the resized images
n3_x, n3_y = wCam - 62 - 10, 10  # Position for n3
n2_x, n2_y = wCam - 62 - 10 - 72, 10  # Position for n2
n1_x, n1_y = wCam - 62 - 10 - 144, 10  # Position for n1

# Mediapipe Hands Model
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:

    menu_switched = False  # To prevent frequent menu switching

    while cam.isOpened():
        success, image = cam.read()
        if not success:
            break

        # Flip the image horizontally (1 means flipping around the y-axis)
        image_bgr = cv2.flip(image, 1)
        # Convert image to RGB and process with Mediapipe
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        # Overlay menu images on the camera feed
        image_bgr[n1_y:n1_y + 60, n1_x:n1_x + 62] = img_n1
        image_bgr[n2_y:n2_y + 60, n2_x:n2_x + 62] = img_n2
        image_bgr[n3_y:n3_y + 60, n3_x:n3_x + 62] = img_n3

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image_bgr,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

            lmList = []
            if results.multi_hand_landmarks:
                myHand = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = image_bgr.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

            # Detect index finger position to switch menus
            if len(lmList) != 0:
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]

                # Check if index finger is in the area of n1, n2, or n3
                if n1_x < x2 < n1_x + 62 and n1_y < y2 < n1_y + 60:
                    if not menu_switched:
                        menu = 1  # LED Color Control
                        menu_switched = True
                elif n2_x < x2 < n2_x + 62 and n2_y < y2 < n2_y + 60:
                    if not menu_switched:
                        menu = 2  # LED Dimming Control
                        menu_switched = True
                elif n3_x < x2 < n3_x + 62 and n3_y < y2 < n3_y + 60:
                    if not menu_switched:
                        menu = 3  # Volume Control
                        menu_switched = True
                else:
                    menu_switched = False  # Reset switching when finger leaves the area

                # Calculate distance between thumb and index finger
                length = math.hypot(x2 - x1, y2 - y1)

                if menu == 1:  # LED Color Control by Thumb Angle
                    thumb_to_index_angle = math.degrees(math.atan2(y2 - y1, x2 - x1))

                    if -180 < thumb_to_index_angle < -90:
                        color = 'Red'
                    elif -90 <= thumb_to_index_angle < 0:
                        color = 'Green'
                    elif 0 <= thumb_to_index_angle < 90:
                        color = 'Blue'
                    else:
                        color = 'Blue'  # Default to blue if the angle is outside the expected range

                    last_color = color  # Store the last selected color
                    cv2.putText(image_bgr, f'Color: {color}', (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)

                    # Send color command to Arduino
                    if color == 'Red':
                        ser.write(b'R\n')  # Send 'R' for Red with newline as delimiter
                    elif color == 'Green':
                        ser.write(b'G\n')  # Send 'G' for Green with newline as delimiter
                    elif color == 'Blue':
                        ser.write(b'B\n')  # Send 'B' for Blue with newline as delimiter

                elif menu == 2:  # LED Dimming Control
                    # Map the distance to a dimming level (0-255)
                    dimming_level = np.interp(length, [30, 200], [0, 255])
                    dimming_level = max(0, min(255, dimming_level))  # Ensure the level is within 0-255

                    # Send dimming command based on the last selected color
                    if last_color == 'Red':
                        ser.write(f'DR{int(dimming_level)}\n'.encode())  # Control dimming for Red
                    elif last_color == 'Green':
                        ser.write(f'DG{int(dimming_level)}\n'.encode())  # Control dimming for Green
                    elif last_color == 'Blue':
                        ser.write(f'DB{int(dimming_level)}\n'.encode())  # Control dimming for Blue

                    # Draw the dimming bar on the frame
                    dimBar = np.interp(dimming_level, [0, 255], [400, 150])
                    cv2.rectangle(image_bgr, (50, 150), (85, 400), (0, 0, 0), 3)
                    cv2.rectangle(image_bgr, (50, int(dimBar)), (85, 400), (0, 0, 0), cv2.FILLED)
                    cv2.putText(image_bgr, f'{int(dimming_level * 100 / 255)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

                elif menu == 3:  # Volume Control
                    # Map the distance to a percentage value (0-100)
                    volPer = np.interp(length, [30, 200], [0, 100])
                    volPer = max(0, min(100, volPer))  # Ensure the percentage is within 0-100

                    # Convert the percentage to a volume step
                    volume.SetMasterVolumeLevelScalar(volPer / 100, None)

                    # Draw the volume bar on the frame
                    volBar = np.interp(volPer, [0, 100], [400, 150])
                    cv2.rectangle(image_bgr, (50, 150), (85, 400), (0, 0, 0), 3)
                    cv2.rectangle(image_bgr, (50, int(volBar)), (85, 400), (0, 0, 0), cv2.FILLED)
                    cv2.putText(image_bgr, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        #Display the menu indicator
        #menu_text = ['LED Colors', 'LED Dimming', 'Volume Control']
        #cv2.putText(image_bgr, menu_text[menu - 1], (wCam // 2 - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        # Display the menu indicator
        menu_text = ['LED Colors', 'LED Dimming', 'Volume Control']

# Display the menu indicator
        menu_text = ['LED Colors', 'LED Dimming', 'Volume Control']

# Coordinates and size for the text background box (top-left corner)
        x, y, width, height = 10, 10, 400, 50  # x, y moved to top-left corner

# Copy the region where the text will go
        text_bg = image_bgr[y:y+height, x:x+width]

# Apply Gaussian blur to the copied region
        blurred_bg = cv2.GaussianBlur(text_bg, (15, 15), 0)

# Blend the blurred background with some transparency for a crystal effect
        alpha = 0.7
        image_bgr[y:y+height, x:x+width] = cv2.addWeighted(blurred_bg, alpha, text_bg, 1 - alpha, 0)

# Draw the text on top of the blurred background
        cv2.putText(image_bgr, menu_text[menu - 1], (x + 10, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Optionally, draw a semi-transparent box around the text
        overlay = image_bgr.copy()
        cv2.rectangle(overlay, (x, y), (x + width, y + height), (255, 255, 255), -1)
        cv2.addWeighted(overlay, 0.2, image_bgr, 0.8, 0, image_bgr)
        
        
        #Display the camera feed with overlay
        cv2.imshow('Camera', image_bgr)

        # Break loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cam.release()
cv2.destroyAllWindows()
