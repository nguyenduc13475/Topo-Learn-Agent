import os
from typing import List, Dict, Any
from scenedetect import detect, ContentDetector
import cv2


class VideoSceneSplitter:
    def __init__(self, threshold: float = 27.0):
        self.threshold = threshold
        print(
            f"Initialized Scene Splitter with ContentDetector threshold: {self.threshold}"
        )

    def split_scenes(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Detect cuts/slide changes in a video using PySceneDetect.
        """
        print(f"Detecting scenes in video: {video_path}")

        # Run scene detection
        scene_list = detect(video_path, ContentDetector(threshold=self.threshold))

        results = []
        for i, scene in enumerate(scene_list):
            start_time = scene[0].get_seconds()
            end_time = scene[1].get_seconds()

            # Extract the middle frame (start_time + end_time)/2 and save it to data/uploads/frames/
            middle_time_sec = (start_time + end_time) / 2.0
            keyframe_path = f"data/uploads/frames/scene_{i}.jpg"
            os.makedirs("data/uploads/frames", exist_ok=True)

            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            target_frame = int(middle_time_sec * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            success, frame = cap.read()
            if success:
                cv2.imwrite(keyframe_path, frame)
                print(f"Saved keyframe for scene {i} at {keyframe_path}")
            else:
                print(f"Failed to extract frame for scene {i}")
            cap.release()

            results.append(
                {
                    "scene_id": i,
                    "start_time": start_time,
                    "end_time": end_time,
                    "keyframe_path": keyframe_path,
                }
            )

        return results
