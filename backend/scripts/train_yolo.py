import os
import yaml
import pandas as pd
import matplotlib.pyplot as plt
from datasets import load_dataset
from ultralytics import YOLO

# ==========================================
# CONFIGURATION
# ==========================================
DATASET_DIR = os.path.abspath("data/doclaynet_yolo")
IMG_DIR_TRAIN = os.path.join(DATASET_DIR, "images", "train")
LBL_DIR_TRAIN = os.path.join(DATASET_DIR, "labels", "train")
IMG_DIR_VAL = os.path.join(DATASET_DIR, "images", "val")
LBL_DIR_VAL = os.path.join(DATASET_DIR, "labels", "val")

# Mapping DocLayNet 11 classes to our 4 core classes
CLASS_MAPPING = {
    1: 2,  # Caption -> Figure
    7: 2,  # Picture -> Figure
    8: 3,  # Section-header -> Title
    11: 3,  # Title -> Title
    9: 1,  # Table -> Table
    10: 0,  # Text -> Text
    4: 0,  # List-item -> Text
}
YOLO_CLASSES = ["Text", "Table", "Figure", "Title"]


def setup_directories():
    """Create directories for YOLO dataset structure."""
    print("Setting up YOLO dataset directories...")
    os.makedirs(IMG_DIR_TRAIN, exist_ok=True)
    os.makedirs(LBL_DIR_TRAIN, exist_ok=True)
    os.makedirs(IMG_DIR_VAL, exist_ok=True)
    os.makedirs(LBL_DIR_VAL, exist_ok=True)


def convert_bbox_to_yolo(bbox, img_width, img_height):
    """Convert bounding box to YOLO normalized format."""
    x_min, y_min, w, h = bbox
    x_center = (x_min + (w / 2.0)) / img_width
    y_center = (y_min + (h / 2.0)) / img_height
    w /= img_width
    h /= img_height
    return [x_center, y_center, w, h]


def process_and_save_dataset(hf_dataset, split_name):
    """Download and process Full HF dataset into YOLO format."""
    print(f"Processing FULL '{split_name}' split for production training...")

    img_dir = IMG_DIR_TRAIN if split_name == "train" else IMG_DIR_VAL
    lbl_dir = LBL_DIR_TRAIN if split_name == "train" else LBL_DIR_VAL

    count = 0
    for item in hf_dataset:
        image = item["image"]
        img_width, img_height = image.size

        img_filename = f"{split_name}_{count}.jpg"
        img_path = os.path.join(img_dir, img_filename)
        image.save(img_path, "JPEG")

        lbl_filename = f"{split_name}_{count}.txt"
        lbl_path = os.path.join(lbl_dir, lbl_filename)

        bboxes = item["bboxes"]
        categories = item["categories"]

        with open(lbl_path, "w") as f:
            for bbox, category_id in zip(bboxes, categories):
                yolo_class_id = CLASS_MAPPING.get(category_id, -1)
                if yolo_class_id != -1:
                    yolo_bbox = convert_bbox_to_yolo(bbox, img_width, img_height)
                    f.write(
                        f"{yolo_class_id} {yolo_bbox[0]:.6f} {yolo_bbox[1]:.6f} {yolo_bbox[2]:.6f} {yolo_bbox[3]:.6f}\n"
                    )

        count += 1
        if count % 1000 == 0:
            print(f"Processed {count} images...")


def create_yaml():
    """Create dataset.yaml for YOLO training."""
    yaml_path = os.path.join(DATASET_DIR, "doclaynet.yaml")
    data = {
        "train": IMG_DIR_TRAIN,
        "val": IMG_DIR_VAL,
        "nc": len(YOLO_CLASSES),
        "names": YOLO_CLASSES,
    }
    with open(yaml_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"Created YAML config at: {yaml_path}")
    return yaml_path


def plot_training_results(run_dir):
    """Plot Loss and mAP from YOLO results.csv"""
    print("Plotting training curves...")
    csv_path = os.path.join(run_dir, "results.csv")

    if not os.path.exists(csv_path):
        print(f"Cannot find {csv_path}. Plotting skipped.")
        return

    # Read CSV, stripping whitespace from column names
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    epochs = df["epoch"]

    plt.figure(figsize=(15, 5))

    # Plot Losses
    plt.subplot(1, 2, 1)
    plt.plot(epochs, df["train/box_loss"], label="Train Box Loss")
    plt.plot(epochs, df["val/box_loss"], label="Val Box Loss")
    plt.plot(epochs, df["train/cls_loss"], label="Train Class Loss")
    plt.plot(epochs, df["val/cls_loss"], label="Val Class Loss")
    plt.title("Training and Validation Loss")
    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True)

    # Plot Metrics (mAP)
    plt.subplot(1, 2, 2)
    plt.plot(epochs, df["metrics/mAP50(B)"], label="mAP@0.5", color="green")
    plt.plot(epochs, df["metrics/mAP50-95(B)"], label="mAP@0.5:0.95", color="blue")
    plt.title("Validation Accuracy (mAP)")
    plt.xlabel("Epochs")
    plt.ylabel("mAP")
    plt.legend()
    plt.grid(True)

    plot_path = os.path.join(run_dir, "custom_learning_curves.png")
    plt.savefig(plot_path)
    print(f"Saved custom plots to {plot_path}")

    # Close the plot explicitly to free memory in production environments
    plt.close()


if __name__ == "__main__":
    print("--- Starting YOLOv8 DocLayNet PRODUCTION Fine-Tuning ---")
    setup_directories()

    print("Downloading full dataset from HuggingFace...")
    # NOTE: This will take a while as it downloads the full dataset
    ds_train = load_dataset("pierreguillou/DocLayNet-small", split="train")
    ds_val = load_dataset("pierreguillou/DocLayNet-small", split="validation")

    # No max_samples limits anymore
    process_and_save_dataset(ds_train, "train")
    process_and_save_dataset(ds_val, "val")

    yaml_config_path = create_yaml()

    print("Initializing YOLOv8 Medium model for production...")
    model = YOLO("yolov8m.pt")

    print("Starting production training phase (50 epochs)...")
    results = model.train(
        data=yaml_config_path,
        epochs=50,
        imgsz=800,  # Increased resolution for document readability
        batch=16,
        project="data/weights",
        name="yolov8_doclaynet_prod",
        device="0",  # Force GPU
    )

    print("Production training finished successfully!")

    best_weight_path = "data/weights/yolov8_doclaynet_prod/weights/best.pt"
    target_path = "data/weights/yolov8_doclaynet.pt"
    if os.path.exists(best_weight_path):
        import shutil

        shutil.copy(best_weight_path, target_path)
        print(f"Deployed best production weights to {target_path}")

    # Plot the results for CV portfolio
    plot_training_results("data/weights/yolov8_doclaynet_prod")
