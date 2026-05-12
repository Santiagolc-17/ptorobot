import argparse
import os
import time
from collections import deque
from pathlib import Path

import cv2


BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault("YOLO_CONFIG_DIR", str((BASE_DIR / "Ultralytics").resolve()))


LABELS = {
    "damage": "DAMAGE",
    "no_damage": "NO DAMAGE",
}


def majority_label(history: deque[tuple[str, float]]) -> tuple[str, float]:
    totals: dict[str, list[float]] = {}
    for name, conf in history:
        totals.setdefault(name, []).append(conf)
    best_name = max(totals, key=lambda name: (len(totals[name]), sum(totals[name]) / len(totals[name])))
    return best_name, sum(totals[best_name]) / len(totals[best_name])


def main() -> None:
    parser = argparse.ArgumentParser(description="Visor webcam damage/no_damage.")
    parser.add_argument("--model", default="models/best.pt", type=Path)
    parser.add_argument("--camera", default=0, type=int)
    parser.add_argument("--width", default=1920, type=int)
    parser.add_argument("--height", default=1080, type=int)
    parser.add_argument("--imgsz", default=224, type=int)
    parser.add_argument("--infer-every", default=3, type=int, help="Corre inferencia cada N frames.")
    parser.add_argument("--smooth", default=7, type=int, help="Ventana de suavizado.")
    args = parser.parse_args()

    model_path = args.model if args.model.is_absolute() else BASE_DIR / args.model
    if not model_path.exists():
        raise FileNotFoundError(f"No existe el modelo: {model_path}")

    from ultralytics import YOLO

    model = YOLO(str(model_path))
    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    if not cap.isOpened():
        raise RuntimeError(f"No pude abrir la camara {args.camera}")

    history: deque[tuple[str, float]] = deque(maxlen=args.smooth)
    shown_label = "INICIANDO"
    shown_conf = 0.0
    frame_index = 0
    fps_start = time.perf_counter()
    fps_frames = 0
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_index % max(args.infer_every, 1) == 0:
            result = model.predict(frame, imgsz=args.imgsz, verbose=False)[0]
            top_id = int(result.probs.top1)
            class_name = result.names[top_id]
            confidence = float(result.probs.top1conf.item())
            history.append((class_name, confidence))
            shown_label, shown_conf = majority_label(history)

        color = (40, 40, 230) if shown_label == "damage" else (40, 180, 70)
        label_text = LABELS.get(shown_label, shown_label)
        cv2.rectangle(frame, (24, 24), (520, 126), (0, 0, 0), -1)
        cv2.rectangle(frame, (24, 24), (520, 126), color, 3)
        cv2.putText(frame, label_text, (44, 72), cv2.FONT_HERSHEY_SIMPLEX, 1.25, color, 3, cv2.LINE_AA)
        cv2.putText(
            frame,
            f"{shown_conf * 100:.1f}%  {fps:.1f} FPS",
            (44, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (245, 245, 245),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow("Rescue Vision Webcam", frame)
        if cv2.waitKey(1) & 0xFF in (27, ord("q")):
            break

        frame_index += 1
        fps_frames += 1
        elapsed = time.perf_counter() - fps_start
        if elapsed >= 1.0:
            fps = fps_frames / elapsed
            fps_start = time.perf_counter()
            fps_frames = 0

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
