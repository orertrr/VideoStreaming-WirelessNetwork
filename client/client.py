import socket
import click
import numpy
import cv2
import os

def recvFrame(client):
    received, _ = client.recvfrom(BUFFER_SIZE)
    numSegment = int(received.decode())
    result = bytes()
    
    for _ in range(0, numSegment):
        received, _ = client.recvfrom(BUFFER_SIZE)
        result = result + received
    
    return result
        

BUFFER_SIZE = 2 ** 16

@click.command()
@click.option("-h", "--host", default = "127.0.0.1", help = "Server IP")
@click.option("-p", "--port", default = 10000, help = "Server port")
def main(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)

    client.sendto(b"hello", (host, port))
    received, _ = client.recvfrom(BUFFER_SIZE)
    streamInfo = numpy.frombuffer(received, numpy.float64)

    fps, height, width = streamInfo
    delay = int((1 / fps) * 1000) - 5

    while True:
        # received, _ = client.recvfrom(BUFFER_SIZE)
        received = recvFrame(client)
        npdata = numpy.frombuffer(received, dtype=numpy.uint8)
        frame = cv2.imdecode(npdata, cv2.IMREAD_COLOR)
        hpf = frame - cv2.GaussianBlur(frame, (21, 21), 3) + 127

        cv2.imshow("Client", hpf)
        key = cv2.waitKey(delay)
        if key == ord('q'):
            client.close()
            break
        elif key == ord('s'):
            filePath_filter = os.path.dirname(__file__).join("screenshot_filter.jpg")
            filePath_normal = os.path.dirname(__file__).join("screenshot_normal.jpg")
            cv2.imwrite("screenshot_filter.jpg", hpf)
            cv2.imwrite("screenshot_normal.jpg", frame)

if __name__ == "__main__":
    main()