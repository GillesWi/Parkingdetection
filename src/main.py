import cv2
import time
from timetrack import get_elapsed_time, start_timer
from parkingspace import ParkingSpace, check_parking_space
from logger import setup_logger
from errorcheck import check_object
from detection import YoloDetection
from S3 import get_image
from api import data

# Settings
DETECTION_INTERVAL_SECONDS = 15  # Delay before getting new image
OPEN_WINDOW = True  # Show what Yolo sees

# Initialize the loggers
logger = setup_logger('Main', '../logs/main.log')
status_logger = setup_logger('ParkingStatus', '../logs/parking-space-status.log')

# Create objects
parking_spaces = [ParkingSpace(i, f"Position {i + 1}", start_timer, get_elapsed_time) for i in range(12)]
yolo = YoloDetection()

# Create a window
if OPEN_WINDOW:
    cv2.namedWindow('Parking space detection', cv2.WINDOW_NORMAL)

while True:
    # 0. Load the image
    get_image()
    img = cv2.imread("../image/parking.jpg")
    check_object(logger, img)  # Check the object
    video_height, video_width, _ = img.shape

    # 1. Get all the cars, motorcycles, and trucks that YOLO detects
    car_positions, reference, park_positions = yolo.detect_objects(img)

    # 2. Check every parking space for a parked car
    current_parking_status = check_parking_space(park_positions, parking_spaces, car_positions,
                                                 status_logger, img)

    # 4. Open preview window
    if OPEN_WINDOW:
        cv2.imshow('Parking space detection', img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 27 is the ASCII code for the 'ESC' key
            break

    # 5. Call API
    data(parking_spaces)

    # 6. Wait 15 seconds
    print("Waiting 15 seconds")
    time.sleep(DETECTION_INTERVAL_SECONDS)

# Release the window and cleanup
cv2.destroyAllWindows()
