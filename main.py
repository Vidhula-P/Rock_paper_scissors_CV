import network
import socket
import time
from machine import Pin, ADC

# Network credentials - replace with your details
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
PORT = 80

def connect_wifi():
    # Initialize WiFi in station mode
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(SSID, PASSWORD)
        
        # Wait for connection with timeout
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)
    
    if wlan.isconnected():
        print('WiFi connected')
        print('Network config:', wlan.ifconfig())
    else:
        print('WiFi connection failed')
        return False
    return True

def setup_webserver():
    # Create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', PORT))
    s.listen(5)
    print('Listening on port', PORT)
    return s

def create_html_response():
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>ESP32-S3 Stream</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <h1>ESP32-S3 Data Stream</h1>
            <div id="data">Waiting for data...</div>
            <script>
                var eventSource = new EventSource('/stream');
                eventSource.onmessage = function(event) {
                    document.getElementById('data').innerHTML = event.data;
                };
            </script>
        </body>
    </html>
    """
    return html

def main():
    # Connect to WiFi
    if not connect_wifi():
        return
    
    # Setup web server
    s = setup_webserver()
    
    # Example sensor setup (ADC on pin A0)
    adc = ADC(Pin(1))  # Use appropriate pin number for your setup
    
    while True:
        try:
            # Accept client connection
            conn, addr = s.accept()
            print('Client connected from', addr)
            request = conn.recv(1024).decode()
            
            if 'GET /stream' in request:
                # Handle SSE stream
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/event-stream\r\n')
                conn.send('Cache-Control: no-cache\r\n')
                conn.send('Connection: keep-alive\r\n\r\n')
                
                while True:
                    # Read sensor data
                    sensor_value = adc.read_u16()
                    
                    # Send data in SSE format
                    data = f'data: {{"value": {sensor_value}}}\n\n'
                    conn.send(data)
                    time.sleep(1)
                    
            else:
                # Serve main page
                response = create_html_response()
                conn.send('HTTP/1.1 200 OK\r\n')
                conn.send('Content-Type: text/html\r\n')
                conn.send('Connection: close\r\n\n')
                conn.send(response)
                conn.close()
                
        except Exception as e:
            print('Error:', e)
            conn.close()

if __name__ == '__main__':
    main()