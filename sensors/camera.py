import cv2

def record_camera(output="output.avi", width=1024, height=576, fps=15):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(output, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out.write(frame)
        cv2.imshow("Recording", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    record_camera()