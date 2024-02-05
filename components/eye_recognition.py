import cv2

class Eye(object):
    
    def __init__(self, landmarks, frame):
        # Initialize the Eye object with landmarks and a frame
        self.landmarks = landmarks
        self.frame = frame
        self.frame_h, self.frame_w, _ = frame.shape
    
    def _eye_coord_x(self, index):
        # Calculate the x coordinate of a specific landmark index based on the frame width
        return int(self.landmarks[index].x * self.frame_w)
    
    def _eye_coord_y(self, index):
        # Calculate the y coordinate of a specific landmark index based on the frame height
        return int(self.landmarks[index].y * self.frame_h)
    
    def eye_recognition(self):
        # Extract specific landmarks for left and right eyes
        # Calculate coordinates for different eye regions and centers of the eyes
        self.left_left_x, self.left_left_y = self._eye_coord_x(33), self._eye_coord_y(33)
        self.left_right_x, self.left_right_y  = self._eye_coord_x(173), self._eye_coord_y(173)
        self.left_bottom_x, self.left_bottom_y = self._eye_coord_x(145), self._eye_coord_y(145)
        self.left_top_x, self.left_top_y = self._eye_coord_x(159), self._eye_coord_y(159)

        self.right_left_x, self.right_left_y = self._eye_coord_x(362), self._eye_coord_y(362)
        self.right_right_x, self.right_right_y  = self._eye_coord_x(466), self._eye_coord_y(466)
        self.right_bottom_x, self.right_bottom_y = self._eye_coord_x(374), self._eye_coord_y(374)
        self.right_top_x, self.right_top_y = self._eye_coord_x(386), self._eye_coord_y(386)

        self.lpupil_x, self.lpupil_y = self._eye_coord_x(468), self._eye_coord_y(468)
        self.rpupil_x, self.rpupil_y = self._eye_coord_x(473), self._eye_coord_y(473)
        
        self.lcenter_x, self.lcenter_y = int((self.left_left_x + self.left_right_x) / 2), int((self.left_bottom_y + self.left_top_y) / 2)
        self.rcenter_x, self.rcenter_y = int((self.right_left_x + self.right_right_x) / 2), int((self.right_bottom_y + self.right_top_y) / 2)
    
    def eye_coordinates(self):
        # Return a list of tuples containing the coordinates of the left and right pupils
        eye_coordinate = [(self.lpupil_x, self.lpupil_y), (self.rpupil_x, self.rpupil_y)]
        return eye_coordinate
    
    def is_left_blink(self):
        # Check if the left eye is blinking by comparing the difference between bottom and top landmarks
        if (self.left_bottom_y - self.left_top_y) <= 5:
            return 1
        else:
            return 0
    
    def is_right_blink(self):
        # Check if the right eye is blinking by comparing the difference between bottom and top landmarks
        if (self.right_bottom_y - self.right_top_y) <= 5:
            return 1
        else:
            return 0
            
    def draw_base(self): 
        # Draw circles on the frame to represent left and right pupils, as well as centers of the left and right eyes
        cv2.circle(self.frame, (self.lpupil_x, self.lpupil_y), 3, (0, 0, 255), 2)
        cv2.circle(self.frame, (self.rpupil_x, self.rpupil_y), 3, (0, 0, 255), 2)
        cv2.circle(self.frame, (self.lcenter_x, self.lcenter_y), 1, (0, 255, 0), 2)
        cv2.circle(self.frame, (self.rcenter_x, self.rcenter_y), 1, (0, 255, 0), 2)