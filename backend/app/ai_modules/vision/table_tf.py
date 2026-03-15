from transformers import TableTransformerForObjectDetection, AutoImageProcessor
from PIL import Image
import torch
import pytesseract


class TableTransformerModule:
    def __init__(
        self, model_name: str = "microsoft/table-transformer-structure-recognition"
    ):
        """
        Initialize Microsoft's Table Transformer via HuggingFace.
        """
        print(f"Initializing Table Transformer model: {model_name}...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.image_processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = TableTransformerForObjectDetection.from_pretrained(model_name).to(
            self.device
        )
        print(f"Table Transformer successfully loaded on {self.device}.")

    def extract_table_to_markdown(self, cropped_image_path: str) -> str:
        """
        Convert a cropped table image into Markdown by detecting rows and using OCR.
        """
        print(f"Extracting real table content from {cropped_image_path}...")
        try:
            image = Image.open(cropped_image_path).convert("RGB")

            # Prepare image for the model
            inputs = self.image_processor(images=image, return_tensors="pt").to(
                self.device
            )

            # Forward pass
            outputs = self.model(**inputs)

            # Post-process to get bounding boxes
            target_sizes = torch.tensor([image.size[::-1]])
            results = self.image_processor.post_process_object_detection(
                outputs, threshold=0.7, target_sizes=target_sizes
            )[0]

            labels = results["labels"].tolist()
            boxes = results["boxes"].tolist()

            # Filter out only the "table row" bounding boxes (label 2 is table row)
            rows = []
            for label, box in zip(labels, boxes):
                if label == 2:
                    rows.append(box)

            # Sort rows from top to bottom based on y_min coordinate
            rows.sort(key=lambda x: x[1])

            markdown_lines = []
            print(f"Detected {len(rows)} rows. Running OCR on each row...")

            for i, row_box in enumerate(rows):
                # Crop the specific row
                row_img = image.crop((row_box[0], row_box[1], row_box[2], row_box[3]))

                # Run OCR on the row image (PSM 6 assumes a single uniform block of text)
                row_text = pytesseract.image_to_string(
                    row_img, config="--psm 6"
                ).strip()

                # Replace newlines with spaces, and treat multiple spaces as column separators
                cleaned_text = " | ".join(
                    [col for col in row_text.split("  ") if col.strip()]
                )

                markdown_lines.append(f"| {cleaned_text} |")

                # Add markdown separator after the first row (header)
                if i == 0:
                    markdown_lines.append("|---|---|")

            # Fallback if the model failed to detect specific rows
            if not markdown_lines:
                print(
                    "No rows detected by Transformer. Falling back to full image OCR."
                )
                full_text = pytesseract.image_to_string(image).strip()
                return f"[Extracted Table Text]:\n{full_text}"

            return "\n".join(markdown_lines)

        except Exception as e:
            print(f"Error extracting table from {cropped_image_path}: {e}")
            return "[Table extraction failed]"
