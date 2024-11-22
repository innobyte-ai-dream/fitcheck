from ultralytics import YOLO, solutions
import cv2
import numpy as np

# Define a function to classify the exercise type
# def classify_exercise(keypoints):
#     # Placeholder logic for exercise classification
#     # Replace with actual logic based on keypoint analysis
#     if some_condition_based_on_keypoints:
#         return "pushup"
#     elif some_other_condition_based_on_keypoints:
#         return "pullup"
#     else:
#         return "unknown"


def main():
    # Define keypoint labels for your pose model (order should match the model's output)
    labels = ["nose", "left_eye", "right_eye", "left_ear", "right_ear", "left_shoulder",
              "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist",
              "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"]

    # Pre-trained weights
    # Load a pretrained model (on the COCO dataset)
    # model = YOLO("models/yolo11x-pose.pt")

    # Train the model
    # results = model.train(data="coco8-pose.yaml", epochs=100, imgsz=640)

    # Open the default camera
    cap = cv2.VideoCapture(0)
    assert cap.isOpened(), "Error reading video file"

    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    gym = solutions.AIGym(
        model="models/yolo11x-pose.pt",
        line_width=2,
        show=True,
        kpts=[6, 8, 10]
    )

    # gym_objects = {
    #     "pushup": solutions.AIGym(line_width=2, model="models/yolo11x-pose.pt", show=True, kpts=[6, 8, 10]),
    #     "pullup": solutions.AIGym(line_width=2, model="models/yolo11x-pose.pt", show=True, kpts=[6, 8, 10]),
    #     "squat": solutions.AIGym(line_width=2, model="models/yolo11x-pose.pt", show=True, kpts=[6, 8, 10])
    # }

    # current_exercise = "unknown"

    # Loop through the video frames
    while cap.isOpened:
        
        # Read a frame from the video
        success, frame = cap.read()

        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break

        # frame_counter += 1

        # results = model.track(frame, verbose=False)

        # Classify the exercise based on keypoints
        # keypoints = results[0].keypoints
        # exercise_type = "pushup"

        # if exercise_type in gym_objects:
        #     gym = gym_objects[exercise_type]
        #     frame = gym.monitor(frame)

        # cv2.imshow("Pose Estimation", frame)

        # Mirror live webcam
        frame = cv2.flip(frame, 1)
        frame = gym.monitor(frame)

        # Track with the model
        # Run YOLO11 tracking on the frame, persisting tracks between frames if set the  persist=True
        # results = model.track(source=frame)

        # Extract keypoint
        # result_keypoint = results.keypoints.xyn.cpu().numpy()[0]

        # Visualize the results on the frame
        # annotated_frame = results[0].plot()

        # cv2.putText(frame, f"Total: {len(results[0].boxes)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        # cv2.imshow('Pose Estimation', annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()