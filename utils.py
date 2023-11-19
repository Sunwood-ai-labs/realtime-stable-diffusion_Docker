from PIL import Image
import numpy as np

def replace_background(image: Image.Image, new_background_color=(0, 255, 255)):
    image_np = np.array(image)

    white_threshold = 255 * 3 
    white_pixels = np.sum(image_np, axis=-1) == white_threshold

    image_np[white_pixels] = new_background_color

    result = Image.fromarray(image_np)

    return result
