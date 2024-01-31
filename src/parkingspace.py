from logger import setup_logger
from draw import draw_rectangle

# Constants
EMPTY = "empty"
OCCUPIED = "occupied"
TRANSITION = "transition"

# Configurable parameters
TRANSITION_DELAY_INSIDE = 4  # Time to wait before transitioning after a car is found inside (in seconds)
TRANSITION_DELAY_OUTSIDE = 5  # Time to wait before transitioning after a car leaves (in seconds)
OCCUPIED_THRESHOLD = 4  # Time threshold to consider a space occupied (in seconds)
EMPTY_DELAY = 4  # Time to wait before transitioning to EMPTY after the car leaves (in seconds)


def get_parking_spaces(parkingspace_file):
    # Load YOLO text annotations into a list of tuples
    with open(parkingspace_file, 'r') as f:
        parkingspace_positions = [tuple(map(float, line.split()[1:])) for line in f.readlines()]
    return parkingspace_positions


class ParkingSpace:
    def __init__(self, number, coordinates, start_timer, get_elapsed_time):
        # Initialization
        self.number = number
        self.coordinates = coordinates

        self.park_coordinates = []
        self.width = 0
        self.height = 0  # Initialize height
        self.adapted_coordinates = [0, 0, 0, 0]  # Initialize coordinates
        self.smoothed_coordinates = [0, 0, 0, 0]  # Initialize smoothed coordinates
        self.smoothing_factor = 0.5  # Adjust this factor for smoothing (0.0 for no smoothing, 1.0 for immediate 
        # adjustment)

        self.last_status = EMPTY
        self.status = EMPTY
        self.last_car_found_inside = False
        self.last_car_left_time = None
        self.last_change_time = None
        self.start_timer = start_timer
        self.get_elapsed_time = get_elapsed_time
        self.elapsed_time = 0  # Initialize elapsed_time

        # Configurable parameters
        self.transition_delay_inside = TRANSITION_DELAY_INSIDE
        self.transition_delay_outside = TRANSITION_DELAY_OUTSIDE
        self.occupied_threshold = OCCUPIED_THRESHOLD
        self.empty_delay = EMPTY_DELAY

        # Logger setup
        self.logger = setup_logger('ParkingActivity', '../logs/parking-space-activity.log')

    def update_status(self, car_found_inside):
        # Update elapsed time
        self.elapsed_time = self.get_elapsed_time(self.last_change_time)

        # Check if a car is found inside
        if car_found_inside and not self.last_car_found_inside:
            self.handle_car_found_inside()

        # Check if a car has left
        elif not car_found_inside and self.last_car_found_inside:
            self.handle_car_left()

        # Check if a car is still inside (OCCUPIED state)
        elif car_found_inside and self.elapsed_time < self.occupied_threshold:
            self.status = OCCUPIED

        # Check if the parking space is empty for a certain duration
        elif not car_found_inside and self.elapsed_time > self.empty_delay:
            self.handle_empty()

        # Check for state transition
        self.check_transition()

    def handle_car_found_inside(self):
        self.status = TRANSITION
        self.last_change_time = self.start_timer()
        self.last_car_found_inside = True

    def handle_car_left(self):
        self.elapsed_time = self.get_elapsed_time(self.last_change_time)

        # Start the timer when the car leaves
        self.last_car_left_time = self.start_timer()

        if self.elapsed_time > TRANSITION_DELAY_OUTSIDE:
            self.status = TRANSITION
            self.last_change_time = self.start_timer()
            self.last_car_found_inside = False

    def handle_empty(self):
        # Only transition to EMPTY after a specific time of the car leaving
        if self.get_elapsed_time(self.last_car_left_time) > EMPTY_DELAY:
            self.status = EMPTY

    def check_transition(self):
        # Check for state transition and log if needed
        current_time = self.start_timer()
        elapsed_since_last_log = self.get_elapsed_time(self.last_change_time)

        if (self.last_status != self.status) and (self.status != TRANSITION) and (
                elapsed_since_last_log > 1):
            # Log the status transition
            self.logger.info(f"Parking space {self.number} changed from {self.last_status} to {self.status}")

            # Update the last status and last change time
            self.last_status = self.status
            self.last_change_time = current_time

    def get_draw_color(self):
        # Define colors based on the status
        if self.status == TRANSITION:
            return 0, 165, 255  # Orange color
        elif self.status == OCCUPIED:
            return 0, 0, 200  # Adjust the color for OCCUPIED state
        else:
            return 0, 200, 0

    def get_position(self, parkingspace, parkingspaces):

        if parkingspace.park_coordinates:
            self.adapted_coordinates = [int(parkingspace.park_coordinates[0]), int(parkingspace.park_coordinates[1]),
                                        int(parkingspace.park_coordinates[2]), int(parkingspace.park_coordinates[3])]
        else:
            # Get previous parking space height
            previous_height = parkingspaces[self.number - 1].adapted_coordinates[3] - \
                              parkingspaces[self.number - 1].adapted_coordinates[1]

            # Gradually adjust the height towards the new value
            self.height = previous_height + (self.height - previous_height) * self.smoothing_factor

            # Calculate the adapted coordinates
            x_min = parkingspaces[self.number - 1].adapted_coordinates[0] + 2

            y_min = int((parkingspaces[self.number - 1].adapted_coordinates[1] - self.height) + 6.6)

            x_max = parkingspaces[self.number - 1].adapted_coordinates[2] - 2
            y_max = int((parkingspaces[self.number - 1].adapted_coordinates[3]) - self.height)

            self.adapted_coordinates = [x_min, y_min, x_max, y_max]

        # Apply smoothing using simple moving average
        self.smoothed_coordinates = [
            int((self.adapted_coordinates[0] + self.smoothed_coordinates[0]) / 2),
            int((self.adapted_coordinates[1] + self.smoothed_coordinates[1]) / 2),
            int((self.adapted_coordinates[2] + self.smoothed_coordinates[2]) / 2),
            int((self.adapted_coordinates[3] + self.smoothed_coordinates[3]) / 2),
        ]
        return self.smoothed_coordinates

    def get_number(self):
        return self.number


def check_parking_space(reference, park_position, parking_spaces, car_positions, status_logger, img):
    parking_spaces_current_status = {}

    # Check every parking space for a parked car
    for parkingspace in parking_spaces:
        parkingspace_number = parkingspace.get_number()

        if parkingspace_number < len(park_position):
            parkingspace.park_coordinates = park_position[parkingspace_number]
        park_coordinates = parkingspace.get_position(parkingspace, parking_spaces)

        # Check if the middle point of any car is inside the parking space
        # Assuming park_coordinates is a list of the form [[x1, y1, x2, y2]]
        car_in_parking_space = any(
            park_coordinates[0] < (car[0] + car[2]) // 2 < park_coordinates[2] and
            park_coordinates[1] < (car[1] + car[3]) // 2 < park_coordinates[3]
            for car in car_positions
        )

        # Update parking space status and draw color
        parkingspace.update_status(car_in_parking_space)
        draw_color = parkingspace.get_draw_color()
        draw_rectangle(img, park_coordinates, draw_color, 2)

        # Log
        status_logger.info(f"Parking space {parkingspace_number} is {parkingspace.status}")

        # Update the dictionary with parking space status
        parking_spaces_current_status[parkingspace_number] = parkingspace.status

    return parking_spaces_current_status
