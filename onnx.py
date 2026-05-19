from pathlib import Path
import sys

from ultralytics import YOLO


MODEL_PATH = Path("best final.pt")
FALLBACK_MODEL_PATH = Path("models/bestfinal.pt")
OUTPUT_PATH = Path("best_final.onnx")


def main():
    script_dir = Path(__file__).resolve().parent
    sys.path = [
        path
        for path in sys.path
        if Path(path or ".").resolve() != script_dir
    ]

    model_path = MODEL_PATH if MODEL_PATH.exists() else FALLBACK_MODEL_PATH

    if not model_path.exists():
        raise FileNotFoundError(
            f"No se encontro el modelo: {MODEL_PATH} ni {FALLBACK_MODEL_PATH}"
        )

    model = YOLO(str(model_path))
    exported_path = Path(model.export(format="onnx"))

    if exported_path != OUTPUT_PATH:
        exported_path.replace(OUTPUT_PATH)

    print(f"Modelo exportado correctamente: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
