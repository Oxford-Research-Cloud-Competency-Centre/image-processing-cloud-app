import cv2

def process_image(file_path):
    # Load the image
    image = cv2.imread(file_path)

    # Convert the image to grayscale and then resize
    processed_image = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (300,300))

    return processed_image

