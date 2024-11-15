import time
from ultralytics import YOLO
import cv2
import torch
from torchvision import transforms
import numpy as np

from utils.drawing import letterbox

def main():
    # Load a model
    model = YOLO("models/yolo11n-pose.pt")

    # Train the model
    # results = model.train(data="coco8-pose.yaml", epochs=100, imgsz=640)

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while (cap.isOpened):
        ret, frame = cap.read()

        results = model.track(source=frame)

        cv2.putText(frame, f"Total: {len(results[0].boxes)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow('Pose Estimation', results[0].plot())

        if cv2.waitKey(1) == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()