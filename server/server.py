import click
import cv2
import os

def getCapture(video):
    if video == "camera":
        return cv2.VideoCapture(0)
    else:
        if not os.path.exists(video):
            raise Exception(f"The video path {video} is not exists")
        return cv2.VideoCapture(video)

def video_file(cap):
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int((1 / fps) * 1000) - 5

    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Server: Normal Video", frame)
        cv2.imshow("Server: Gray Video", gray)
        key = cv2.waitKey(delay)

        if key == ord('q'):
            break
        elif key == ord('r'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            if key != -1:
                print(key)

def video_camera(cap):
    pass

@click.command()
@click.option("-p", "--port", default = 10000, help = "Server port")
@click.option("-v", "--video", default = "camera", help = "Video source: filename or camera")
def main(port, video):
    print(f"Server port: {port}")
    print(f"Video: {video}")

    cap = getCapture(video)
    
    if not cap.isOpened():
        print("Cannot open Camera or File")
        return
    
    if video != "camera":
        video_file(cap)
    else:
        video_camera(cap)
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()