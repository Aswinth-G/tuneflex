from ultralytics import YOLO
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "best.pt")

model = YOLO(MODEL_PATH)

def run_yolo_classification(image_path: str):
    """Run YOLO image classification and return result."""
    try:
        results = model(image_path)
        print(f"YOLO Results: {results}")  # Debug log

        classifications = []

        for r in results:
            # classification probabilities
            probs = r.probs  

            class_id = int(probs.top1)
            class_name = model.names[class_id]
            confidence = float(probs.top1conf)

            classifications.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": confidence
            })

        print(f"YOLO Classifications: {classifications}")  # Debug log
        return classifications

    except Exception as e:
        print(f"YOLO classification error: {e}")
        return []


if __name__ == "__main__":
    test_image = "test_image.jpg"

    results = run_yolo_classification(test_image)

    print(results)