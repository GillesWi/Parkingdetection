import cv2
import time
from timetrack import get_elapsed_time, start_timer
from parkingspace import ParkingSpace, get_parking_spaces, check_parking_space
from logger import setup_logger
from errorcheck import check_video_capture, check_object
from detection import YoloDetection
from S3 import get_image
from api import data

# Settings
DETECTION_INTERVAL_SECONDS = 3
DEBUG = True

# Initialize the loggers
logger = setup_logger('Main', '../logs/main.log')
status_logger = setup_logger('ParkingStatus', '../logs/parking-space-status.log')

parking_spaces = [ParkingSpace(i, f"Position {i + 1}", start_timer, get_elapsed_time) for i in range(12)]

# Create YOLO detection object
yolo = YoloDetection()

# Open the video or image
cv2.namedWindow('Parking space detection', cv2.WINDOW_NORMAL)

last_activation_time = time.time()

while True:
    start_time = time.time()

    cap = cv2.VideoCapture("../image/parking.jpg")  # Load the Video
    check_video_capture(logger, cap)  # Check the object

    success, img = cap.read()
    check_object(logger, success)

    video_height, video_width, _ = img.shape

    # 1. Get all the cars, motorcycles, and trucks that YOLO detects
    car_positions, reference, park_positions = yolo.detect_objects(img, DEBUG)

    # 2. Check every parking space for a parked car
    current_parking_status = check_parking_space(reference, park_positions, parking_spaces, car_positions,
                                                 status_logger, img)

    # 4. Open preview window
    cv2.imshow('Parking space detection', img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:  # 27 is the ASCII code for the 'ESC' key
        break

    elapsed_time = time.time() - last_activation_time

    # Check if 15 seconds have elapsed
    if elapsed_time >= DETECTION_INTERVAL_SECONDS:
        # get_image()
        data(parking_spaces)
        

status_logger.info("Exiting...")
