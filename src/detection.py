from draw import draw_rectangle
from ultralytics import YOLO
import cv2


class YoloDetection:
    def __init__(self):
        self.model = YOLO('../model/parking.pt')  # Load YOLO model
        self.classnames = get_labels()
        self.positions = []  # Reset all the positions of the car
        self.reference = []
        self.park_positions = []

    def detect_objects(self, img):
        self.positions = []  # Reset positions list for each frame
        results = self.model(img, stream=True)

        classnames = get_labels()

        for r in results:

            boxes = r.boxes
            if boxes:
                for box in boxes:
                    # Confidence
                    conf = round(box.conf[0].item(), 2)

                    # Check if confidence is above a certain threshold 
                    if conf > 0.6:
                        # Bounding box in YOLO format
                        car_position = tuple(map(int, box.xyxy[0]))

                        cls = int(box.cls[0])

                        # Get the reference point
                        if classnames[cls] == 'cabinet':
                            self.reference = [car_position[0], car_position[1], car_position[2], car_position[3]]

                        if classnames[cls] == 'parking':
                            self.park_positions.append(car_position)

                        if classnames[cls] == 'supercharger':
                            draw_rectangle(img, car_position, (255, 255, 255), 1)

                        # Save the position of car
                        if classnames[cls] == 'car' or classnames[cls] == 'truck' or classnames[cls] == 'motorbike':
                            self.positions.append(car_position)
                            draw_rectangle(img, car_position, (175, 175, 175), 1)

                        # Show position and class name
                        label = f'{classnames[cls]}: {conf}'
                        cv2.putText(img, label, (max(0, car_position[0]), max(0, car_position[1])),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (255, 255, 255), 1)
            else:
                print("Nothing detected")
            return self.positions, self.reference, self.park_positions


def get_labels():
    # Read class names from file
    classnamesfile = '../model/parkingdetection.names'
    with open(classnamesfile, 'rt') as f:
        classnames = f.read().rstrip('\n').split('\n')
    return classnames
