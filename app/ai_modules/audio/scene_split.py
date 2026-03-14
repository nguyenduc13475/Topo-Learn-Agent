from typing import List, Dict, Any
from scenedetect import detect, ContentDetector


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

            # TODO: Add OpenCV logic here to extract the middle frame (start_time + end_time)/2
            # and save it to data/uploads/frames/
            mock_frame_path = f"data/uploads/frames/scene_{i}.jpg"

            results.append(
                {
                    "scene_id": i,
                    "start_time": start_time,
                    "end_time": end_time,
                    "keyframe_path": mock_frame_path,
                }
            )

        return results
