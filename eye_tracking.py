# Import necessary libraries
import cv2
import ast
import time
import mediapipe as mp
import pyautogui as py
import components.eye_recognition as eye

# Open the camera (index 1 == phone camera) for video capture
cam = cv2.VideoCapture(0)

# Initialize the face mesh model from MediaPipe with landmark refinement
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# Get the screen size using PyAutoGUI
screen_w, screen_h = py.size()

# Initialize variables for eye state and calibration
right_blink = False
left_blink = False
calib_coord = []
index = 0
blink = 0

# Create and initialize coordinates.txt with default values
with open("components/coordinates.txt", "w") as file:
    file.write(str([(0, 0), (0, 0), -1]))
file.close()

# Main loop for capturing and processing video frames
while True:
    # Read a frame from the camera and flip it horizontally
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    
    # Convert the frame to RGB for face mesh processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame with the face mesh model
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape
    
    try:
        # Check if landmarks are detected
        if landmark_points:
            landmarks = landmark_points[0].landmark
            
            # Initialize and process eye recognition using custom Eye class
            eyes = eye.Eye(landmarks, frame)
            eyes.eye_recognition()
            eyes.draw_base()
            right_blink = eyes.is_right_blink()
            left_blink = eyes.is_left_blink()
            if (right_blink == 1 and left_blink == 1):
                blink = 1
            else:
                blink = 0
            # Write right blink state and eye coordinates to blink.txt
            with open("components/blink.txt", "w") as file1:
                file1.write(str(right_blink) + "\n")
                file1.write(str(eyes.eye_coordinates()) + "\n")
                file1.write(str(blink))
            file1.close()
            
            # Read the calibration coordinates from coordinates.txt
            with open("components/coordinates.txt", "r") as file2:
                line = file2.readline()
            file2.close()
            coord = ast.literal_eval(line)
            
            # Perform calibration using four consecutive frames
            if coord[2] == index:
                calib_coord.append(coord)
                index += 1
            
            # Once calibration is done, calculate screen coordinates and move the cursor
            if coord[2] == 4:
                leftBorder = calib_coord[0][0][0]
                rightBorder = calib_coord[1][0][0]
                topBorder = calib_coord[2][0][1]
                bottomBorder = calib_coord[3][0][1]
                
                diff_x =  rightBorder - leftBorder
                diff_y = bottomBorder - topBorder
                
                screen_x = int((screen_w / diff_x) * (eyes.lpupil_x - calib_coord[0][0][0]))
                screen_y = int((screen_h / diff_y) * (eyes.lpupil_y - calib_coord[2][0][1]))
                
                if (eyes.lpupil_x < leftBorder or eyes.lpupil_x > rightBorder
                    or eyes.lpupil_y < topBorder or eyes.lpupil_y > bottomBorder):
                    layout_message = ""
                else:
                    layout_message = ""
                
                with open("components/blink.txt", "w") as file3:
                    file3.write(layout_message)
                file3.close()
            
                # Move the cursor to the calculated screen coordinates
                py.moveTo(screen_x, screen_y)
                
                # Imitating left click property of the mouse with right eye blink
                if right_blink:
                    py.click()
    
    except Exception as e:
        # Print any errors that occur during execution
        print(f"Error: {e}")
    
    # Display the video frame with the eye-controlled cursor
    cv2.imshow('Eye Controlled Cursor', frame)
    cv2.waitKey(1)