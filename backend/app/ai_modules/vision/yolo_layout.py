from typing import List, Dict, Any
from ultralytics import YOLO


class YoloLayoutAnalyzer:
    def __init__(self, model_path: str = "data/weights/yolov8_doclaynet.pt"):
        """
        Initialize the fine-tuned YOLOv8 model.
        """
        print(f"Loading YOLOv8 model from {model_path}...")
        self.model = YOLO(model_path)

    def analyze_pdf_page(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Run inference on a single PDF page (converted to image).
        Returns a list of bounding boxes with labels (Text, Table, Figure, Title)
        sorted by Y-coordinate (top to bottom).
        """
        print(f"Analyzing layout for image: {image_path}")
        results = self.model(image_path)
        extracted_elements = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                label = self.model.names[cls]

                extracted_elements.append(
                    {
                        "label": label,
                        "bbox": [x1, y1, x2, y2],
                        "confidence": conf,
                        "y_min": y1,  # Used for sorting
                    }
                )

        # Sort elements top-to-bottom
        extracted_elements.sort(key=lambda x: x["y_min"])
        return extracted_elements
