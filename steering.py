import cv2
import mediapipe as mp
import pydirectinput
import directinput
import time

framecapture = cv2.VideoCapture(0) # Fetching video camera.
# Setting video capture resolution for the webcam to 680x620 (px)
framecapture.set(3, 680)
framecapture.set(4, 620)

mp_drawing = mp.solutions.drawing_utils

# Fetching hand models.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

def write_text(img, text, x, y):
    """ Writing (overlaying) text on the OpenCV camera view.

    Parameters
    __________
    img:
        Frame of the current image.
    text: str
        Text being written to the camera view.
    x: int
        X coordinate for plotting the text.
    y: int
        Y coordinate for plotting the text.
    """
    font = cv2.FONT_HERSHEY_SIMPLEX
    pos = (x, y)
    fontScale = 1
    fontColor = (255, 255, 255) # White.
    lineType = 2
    cv2.putText(img,
                text,
                pos,
                font,
                fontScale,
                fontColor,
                lineType)

# Used for FPS calculations.
def steering_wheel():
    """ Uses the slope of the distance between middle fingers to create a virtual steering wheel for gaming.
    """
    prev_frame_time = 0
    new_frame_time = 0
    while framecapture.isOpened():
        success, img = framecapture.read()
        cv2.waitKey(1) # Continuously refreshes the webcam frame every 1ms.
        img = cv2.flip(img, 1) #Horizontally flipping the image
        img.flags.writeable = False # Making the images not writeable on disk for optimization.
        results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) # Processing video.
        # Note: Converting to RGB results in a significant increase in hand recognition accuracy.

        # Checking if a hand exists in the frame.
        landmarks = results.multi_hand_landmarks # Fetches all the landmarks (points) on the hand.
        if landmarks:
            # When a hand exists in the frame.

            # FPS Calculations
            new_frame_time = time.time()
            fps = str(int(1/(new_frame_time - prev_frame_time)))
            write_text(img, fps, 150, 500)
            prev_frame_time = new_frame_time

            if(len(landmarks) == 2): # If 2 hands are in view.
                left_hand_landmarks = landmarks[1].landmark
                right_hand_landmarks = landmarks[0].landmark
                # To inverse the steering put 0 in left hand landmarks and 1 in right hand landmarks
                # Fetching the height and width of the camera view.
                shape = img.shape
                width = shape[1]
                height = shape[0]

                # Isolating the tip of middle fingers from both hands, and normalizing their coordinates based on height/width
                # of the camera view.
                left_mFingerX, left_mFingerY = (left_hand_landmarks[11].x * width), (left_hand_landmarks[11].y * height)
                right_mFingerX, right_mFingerY = (right_hand_landmarks[11].x * width), (right_hand_landmarks[11].y * height)

                left_thumbX, left_thumbY= (left_hand_landmarks[4].x * width), (left_hand_landmarks[4].y * height)
                right_thumbX, right_thumbY = (right_hand_landmarks[4].x * width), (right_hand_landmarks[4].y * height)

                # Calculating slope between middle fingers of both hands (we use this to determine whether we're turning
                # left or right.
                slope = ((right_mFingerY - left_mFingerY)/(right_mFingerX-left_mFingerX))
                slopethumbs = ((right_thumbY - right_mFingerY)/(left_thumbX-left_mFingerX))


                #print(slopethumbs)
                # Outputs for testing.
                #print(f"Left hand: ({left_mFingerX}, {left_mFingerY})")
                #print(f"Right hand: ({right_mFingerX}, {right_mFingerY})")
                #print(f"Slope: {slope}")

                sensitivity = 0.2 # Adjusts sentivity for turing; the higher this is, the more you have to turn your hands.


                if abs(slope) > sensitivity:
                    if slope < 0:
                        # When the slope is negative, we turn left.
                        print("Turn left.")
                        write_text(img, "Left.", 360, 360)
                        directinput.release_key('Space')
                        directinput.release_key('w')
                        directinput.release_key('a')
                        directinput.release_key('d')
                        directinput.press_key('a')
                        if (abs(slopethumbs) >= 5.0):
                            print("jump")
                            write_text(img, "Jump.", 360, 360)
                            #directinput.release_key('w')
                            # directinput.release_key('Space')
                            directinput.press_key('Space')
                            #directinput.release_key('Space')
                    if slope > 0:
                        # When the slope is positive, we turn right.
                        print("Turn right.")
                        write_text(img, "Right.", 360, 360)
                        directinput.release_key('Space')
                        directinput.release_key('w')
                        directinput.release_key('a')
                        directinput.release_key('d')
                        directinput.press_key('d')
                        if (abs(slopethumbs) >= 5.0):
                            print("jump")
                            write_text(img, "Jump.", 360, 360)
                            directinput.release_key('w')
                            # directinput.release_key('Space')
                            directinput.press_key('Space')
                            #directinput.release_key('Space')
                if abs(slope) < sensitivity:
                    # When our hands are straight, we stay still (and also throttle).
                    print("Keeping straight.")
                    write_text(img, "Straight.", 360, 360)
                    directinput.release_key('Space')
                    directinput.release_key('a')
                    directinput.release_key('d')
                    directinput.press_key('w') # Remove this if you have pedals to control the speed.
                    if (abs(slopethumbs) >= 5.0):
                        print("jump")
                        write_text(img, "Jump.", 360, 360)
                        directinput.release_key('w')
                        # directinput.release_key('Space')
                        directinput.press_key('Space')
                        #directinput.release_key('Space')
            else:  # when the hands are not in frame, release the controls
                directinput.release_key('Space')
                directinput.release_key('w')
                directinput.release_key('a')
                directinput.release_key('d')

             # Iterating through landmarks (i.e., co-ordinates for finger joints) and drawing the connections.
            for hand_landmarks in landmarks:
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.imshow("Hand Recognition", img)
    framecapture.release()
steering_wheel()
