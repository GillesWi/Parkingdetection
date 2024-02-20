from roboflow import Roboflow

rf = Roboflow(api_key="XbBReuZ6NaN8q1LNBOGI")
project = rf.workspace("car-detection-gnsmo").project("car-detection-eszol")
dataset = project.version(1).download("yolov8")

# In terminal
# yolo train model=../model/YOLOv8m.pt data=Parkingdetection/data.yaml epochs=20 imgsz=640
