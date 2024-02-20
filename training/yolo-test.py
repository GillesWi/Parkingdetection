import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO('../model/yolov8m.pt')
results = model("../video/parking.mp4", show=True)

cv2.waitKey()
