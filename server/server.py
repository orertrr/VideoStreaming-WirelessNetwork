import socket
import click
import numpy
import math
import cv2
import os

BUFFER_SIZE = 2 ** 16
MAX_DGRAM_SIZW = BUFFER_SIZE - 64

def sendFrame(socket, client, frame):
    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    message = buffer.tobytes()
    messageSize = len(message)
    print(messageSize)
    numSegment = math.ceil(messageSize / BUFFER_SIZE)
    socket.sendto(str(numSegment).encode(), client)

    start = 0
    for _ in range(0, numSegment):
        end = min(messageSize, start + MAX_DGRAM_SIZW)
        socket.sendto(message[start:end], client)
        start = end

def getCapture(video):
    if video == "camera":
        return cv2.VideoCapture(0)
    else:
        if not os.path.exists(video):
            raise Exception(f"The video path {video} is not exists")
        return cv2.VideoCapture(video)

def streamVideo(socket, client, cap):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    fps = cap.get(cv2.CAP_PROP_FPS)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    delay = int((1 / fps) * 1000) - 5
    black = numpy.zeros((height, width, 3), numpy.uint8)
    
    streamInfo = numpy.array([fps, height, width], dtype=numpy.float64)
    socket.sendto(streamInfo.tobytes(), client)

    cv2.putText(black, "Press 'r' to replay", (int(width * 0.3), int(height * 0.45)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    cv2.putText(black, "Press 'q' to quit", (int(width * 0.3), int(height * 0.55)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    while True:
        ret, frame = cap.read()

        if ret:
            sendFrame(socket, client, frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            frame = black
            gray = black

        cv2.imshow("Server: Normal Video", frame)
        cv2.imshow("Server: Gray Video", gray)

        key = cv2.waitKey(delay)
        if key == ord('q'):
            socket.close()
            break
        elif key == ord('r'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            if key != -1:
                print(key)

@click.command()
@click.option("-p", "--port", default = 10000, help = "Server port")
@click.option("-v", "--video", default = "camera", help = "Video source: filename or camera")
def main(port, video):
    print(f"Server port: {port}")
    print(f"Video: {video}")

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    server.bind(("0.0.0.0", port))

    cap = getCapture(video)
    
    if not cap.isOpened():
        print("Cannot open Camera or File")
        return
    
    while True:
        # If server is closed
        if server.fileno() == -1:
            break

        # Wait for client
        _, client = server.recvfrom(BUFFER_SIZE)
        print("Connection from: ", client)

        streamVideo(server, client, cap)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()