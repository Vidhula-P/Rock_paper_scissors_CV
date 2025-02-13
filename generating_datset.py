import camera
import network
import time
import socket
import os
from machine import Pin
import uos

# Network credentials - replace with your details
SSID = "Vidhula- Hotspot"
PASSWORD = "blueberry"
PORT = 80

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

cam = camera.Camera(**CAMERA_PARAMETERS)
cam.init()
cam.set_bmp_out(True)  # This will produce uncompressed images which we need for preprocessing

# Wi-Fi connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)

print("Connected! IP Address:", wlan.ifconfig()[0])

# Create folders for storing labeled images
def create_directories():
    """Create directories for each class if they don't exist"""
    classes = ['rock', 'paper', 'scissors']
    for class_name in classes:
        try:
            os.mkdir('/' + class_name)
        except:
            pass  # Directory already exists
        
create_directories()

def save_image(label):
    # Capture the frame
    frame = cam.capture()
    if frame:
        # Generate filename based on label and timestamp
        filename = "/{}/img_{}.bmp".format(label, time.ticks_ms())
        
        # Save the image to the appropriate folder
        with open(filename, "wb") as f:
            f.write(frame)
        print(f"Image saved as {filename}")
    else:
        print("Failed to capture image.")

def serve_stream():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print("Web server running...")

    while True:
        conn, addr = s.accept()
        print("Client connected from", addr)

        # Serve HTML page with buttons to select labels
        html = """
        <html>
        <body>
        <h1>Select Label</h1>
        <form method="POST" action="/capture">
        <button name="label" value="rock">Rock</button>
        <button name="label" value="paper">Paper</button>
        <button name="label" value="scissors">Scissors</button>
        </form>
        </body>
        </html>
        """
        conn.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        conn.send(html.encode())

        # Check if there's a form submission (button click)
        data = conn.recv(1024).decode()
        if "label=" in data:
            label = data.split("label=")[1].split(" ")[0]
            if label in ["rock", "paper", "scissors"]:
                save_image(label)  # Save the image to the corresponding folder

        conn.close()

serve_stream()

