import argparse
import os
import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault("YOLO_CONFIG_DIR", str((BASE_DIR / "Ultralytics").resolve()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Reentrena clasificador damage/no_damage.")
    parser.add_argument("--data", default="dataset", type=Path)
    parser.add_argument("--model", default="models/best.pt", type=Path, help="Modelo inicial para fine-tuning.")
    parser.add_argument("--epochs", default=60, type=int)
    parser.add_argument("--imgsz", default=224, type=int, help="224 es ligero para Jetson Nano.")
    parser.add_argument("--batch", default=8, type=int)
    parser.add_argument("--device", default="cpu", help="Usa 0 si tienes CUDA disponible.")
    parser.add_argument("--project", default="runs/classify", type=Path)
    parser.add_argument("--name", default="damage_retrain")
    parser.add_argument("--copy-to", default="models/best.pt", type=Path)
    args = parser.parse_args()

    data = args.data if args.data.is_absolute() else BASE_DIR / args.data
    model_path = args.model if args.model.is_absolute() else BASE_DIR / args.model
    project = args.project if args.project.is_absolute() else BASE_DIR / args.project
    copy_to = args.copy_to if args.copy_to.is_absolute() else BASE_DIR / args.copy_to

    if not data.exists():
        raise FileNotFoundError(f"No existe el dataset: {data}")
    if not model_path.exists():
        raise FileNotFoundError(f"No existe el modelo inicial: {model_path}")

    from ultralytics import YOLO

    model = YOLO(str(model_path))
    results = model.train(
        data=str(data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=str(project),
        name=args.name,
        patience=12,
        workers=0,
    )

    best_path = Path(results.save_dir) / "weights" / "best.pt"
    if not best_path.exists():
        raise FileNotFoundError(f"No se genero best.pt en: {best_path}")

    copy_to.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best_path, copy_to)
    print(f"OK: mejor modelo copiado a {copy_to}")
    print(f"Run completo: {results.save_dir}")


if __name__ == "__main__":
    main()
