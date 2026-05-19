import argparse
import os
from pathlib import Path

import cv2
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault("YOLO_CONFIG_DIR", str((BASE_DIR / "Ultralytics").resolve()))


LABELS = {
    "damage": "Dano",
    "no_damage": "Sin dano",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Clasificacion en tiempo real con webcam.")
    parser.add_argument("--model", default="models/bestfinal.pt", help="Ruta al modelo .pt")
    parser.add_argument("--camera", type=int, default=0, help="Indice de webcam")
    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.is_absolute():
        model_path = BASE_DIR / model_path

    if not model_path.exists():
        raise FileNotFoundError(f"No existe el modelo: {model_path}")

    model = YOLO(str(model_path))
    cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        raise RuntimeError("No pude abrir la webcam. Prueba con --camera 1.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        result = model.predict(frame, verbose=False)[0]
        top_id = int(result.probs.top1)
        class_name = result.names[top_id]
        confidence = float(result.probs.top1conf.item())

        label = LABELS.get(class_name, class_name)
        text = f"{label} - {confidence * 100:.1f}%"
        color = (0, 0, 255) if class_name == "damage" else (0, 180, 0)

        cv2.rectangle(frame, (12, 12), (430, 68), (0, 0, 0), -1)
        cv2.putText(
            frame,
            text,
            (24, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            color,
            2,
            cv2.LINE_AA,
        )

        cv2.imshow("Rescue Vision - Webcam", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
