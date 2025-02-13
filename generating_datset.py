from machine import Pin, I2C
from time import sleep
import camera
import os

"""Initialize the camera module"""
CAMERA_PARAMETERS = {
    "data_pins": [15, 17, 18, 16, 14, 12, 11, 48],
    "vsync_pin": 38,
    "href_pin": 47,
    "sda_pin": 40,
    "scl_pin": 39,
    "pclk_pin": 13,
    "xclk_pin": 10,
    "xclk_freq": 20000000,
    "powerdown_pin": -1,
    "reset_pin": -1,
    "frame_size": camera.FrameSize.R96X96,  # Use camera.FrameSize
    "pixel_format": camera.PixelFormat.GRAYSCALE  # Use camera.PixelFormat
}
try:
    cam = camera.Camera(**CAMERA_PARAMETERS)
    cam.init()
    cam.set_bmp_out(True)# this will produced uncompressed images which we need for preprocessing
    print("Camera initialized successfully")
except Exception as e:
    print("Error initializing camera:", e)

def create_directories():
    """Create directories for each class if they don't exist"""
    classes = ['rock', 'paper', 'scissors']
    for class_name in classes:
        try:
            os.mkdir('/' + class_name)
        except:
            pass  # Directory already exists

def capture_single_image(class_name):
    """Capture a single image for the specified class"""
    try:
        # Get the number of existing files in the class directory
        existing_files = os.listdir('/' + class_name)
        image_count = len([f for f in existing_files if f.endswith('.jpg')])
        
        # Capture image
        print("Capturing in 5 seconds...")
        sleep(5)  # Give time to prepare gesture
        
        buf = cam.capture()
        if buf:
            # Save image with incrementing filename
            filename = f"/{class_name}/{class_name}_{image_count:03d}.jpg"
            with open(filename, 'wb') as f:
                f.write(buf)
            print(f"Saved {filename}")
            return True
        else:
            print("Failed to capture image")
            return False
    except Exception as e:
        print("Error capturing image:", e)
        return False

def main():
    """Main function to capture a single image"""
    print("Rock-Paper-Scissors Image Capture")
    
    create_directories()
    
    # Ask for the class
    print("\nSelect gesture class:")
    print("1: Rock")
    print("2: Paper")
    print("3: Scissors")
    
    try:
        choice = input("Enter choice (1-3): ")
        class_map = {'1': 'rock', '2': 'paper', '3': 'scissors'}
        if choice in class_map:
            class_name = class_map[choice]
            capture_single_image(class_name)
        else:
            print("Invalid choice!")
    except Exception as e:
        print("Error:", e)
    
    cam.deinit()

if __name__ == "__main__":
    main()


