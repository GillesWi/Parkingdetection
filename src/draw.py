import cv2


def draw_rectangle(img, coordinates, color, thickness, alpha=0.95):
    x1, y1, x2, y2 = coordinates  # Unpack the coordinates

    # Create a copy of the image to avoid modifying the original
    overlay = img.copy()

    # Draw the rectangle on the overlay
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, thickness)

    # Blend the overlay with the original image using addWeighted
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
