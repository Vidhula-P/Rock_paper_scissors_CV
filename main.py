import camera
import network
import time
import socket

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
cam.set_bmp_out(True)# this will produced uncompressed images which we need for preprocessing
    
frame = cam.capture()

if frame:
    print("Captured frame successfully! Length:", len(frame))
else:
    print("Failed to capture frame.")

ssid = "Vidhula- Hotspot"
password = "blueberry"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)

print("Connected! IP Address:", wlan.ifconfig()[0])


def serve_frame():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print("Web server running...")

    while True:
        conn, addr = s.accept()
        print("Client connected from", addr)
        frame = cam.capture()

        if frame:
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: image/bmp\r\n"
                "Content-Length: {}\r\n"
                "\r\n".format(len(frame))
            )
            conn.send(response.encode() + frame)
        else:
            conn.send(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
        
        conn.close()

serve_frame()
