import network
import camera
import socket
import time
import os

# Initialize camera
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
    "frame_size": camera.FrameSize.R96X96,
    "pixel_format": camera.PixelFormat.GRAYSCALE
}

cam = camera.Camera(**CAMERA_PARAMETERS)
cam.init()
cam.set_bmp_out(True)

# Set up access point
ssid = "ESP32-Cam"
password = "12345678"
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

print(f"Access point started. Connect to '{ssid}' with password '{password}'")
print(f"AP IP address: {ap.ifconfig()[0]}")

# Create folder if it doesn't exist
folder_name = "paper"
try:
    os.mkdir(folder_name)
except OSError:
    pass

# Start web server
def start_server():
    addr = ('0.0.0.0', 5000)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(addr)
    s.listen(5)
    print("Web server listening on port 5000")

    count = 98
    while True:
        # Capture image every 4 seconds
        img = cam.capture()
        if img:
            # Save image in paper folder
            filename = f"{folder_name}/paper{count}.pgm"
            with open(filename, 'wb') as f:
                f.write(img)
            print(f"Saved image as {filename}")
            count += 1

        time.sleep(2)

        conn, addr = s.accept()
        request = conn.recv(1024)
        request = str(request)

        if "GET / " in request:
            # Generate HTTP response with image
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type: image/bmp\r\n"
            response += f"Content-Length: {len(img)}\r\n\r\n"
            conn.send(response.encode('utf-8') + img)
        else:
            # Serve basic HTML page
            html = """
            HTTP/1.1 200 OK
Content-Type: text/html


            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ESP32 Camera Preview</title>
            </head>
            <body>
                <h2>ESP32 Camera Preview</h2>
                <img src="/" style="width:100%; max-width:400px;" />
                <script>
                    setInterval(() => {
                        document.querySelector('img').src = '/' + Math.random();
                    }, 1000);
                </script>
            </body>
            </html>
            """
            conn.send(html.encode('utf-8'))
        conn.close()

start_server()
