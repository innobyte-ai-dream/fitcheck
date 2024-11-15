from ultralytics import YOLO

def main():
    # Load a model
    model = YOLO("models/yolo11n-pose.pt")

    # Train the model
    results = model.train(data="coco8-pose.yaml", epochs=100, imgsz=640)

if __name__ == "__main__":
    main()