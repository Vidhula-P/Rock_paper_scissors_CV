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


# Serve video stream
def serve_stream():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print("Web server running...")

    while True:
        conn, addr = s.accept()
        print("Client connected from", addr)
        conn.send(
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n"
        )

        try:
            while True:
                frame = cam.capture()
                if frame:
                    conn.send(
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n" +
                        frame + b"\r\n"
                    )
                time.sleep(0.05)  # Adjust delay to balance performance
        except Exception as e:
            print("Client disconnected:", e)
        finally:
            conn.close()

serve_stream()

