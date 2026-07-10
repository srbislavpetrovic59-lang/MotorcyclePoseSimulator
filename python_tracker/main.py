import cv2

from camera import Camera


def main():

    camera = Camera()

    while True:

        frame = camera.read()

        if frame is None:
            break

        cv2.imshow("Motorcycle Pose Simulator", frame)

        key = cv2.waitKey(1)

        if key == 27:
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()