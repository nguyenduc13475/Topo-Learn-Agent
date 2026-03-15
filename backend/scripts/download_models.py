import os
import urllib.request


def setup_directories():
    """Create necessary directories for data and weights."""
    print("Setting up directories...")
    directories = [
        "data/uploads",
        "data/uploads/temp",
        "data/uploads/frames",
        "data/weights",
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")


def download_yolo_placeholder():
    """
    Download a base YOLOv8 model to use as a placeholder for the fine-tuned DocLayNet model.
    This prevents the app from crashing during testing.
    """
    weight_path = "data/weights/yolov8_doclaynet.pt"

    if os.path.exists(weight_path):
        print(f"Model already exists at {weight_path}. Skipping download.")
        return

    print("Downloading YOLOv8n base model as a placeholder for DocLayNet...")
    url = "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt"

    try:
        urllib.request.urlretrieve(url, weight_path)
        print(f"Successfully downloaded placeholder model to {weight_path}")
        print(
            "NOTE: Replace this file with your actual fine-tuned DocLayNet model later!"
        )
    except Exception as e:
        print(f"Failed to download the model: {e}")


if __name__ == "__main__":
    print("--- Starting Environment Setup ---")
    setup_directories()
    download_yolo_placeholder()
    print("--- Setup Completed ---")
