import argparse
import random
import shutil
from pathlib import Path

SOURCE_CLASSES = {
    "damage": [Path("Damage/images"), Path("New_Data_damage/images")],
    "no_damage": [Path("NoDamage/images"), Path("New_Data_no_damage/images")],
}

OUTPUT_DIR = Path("dataset")
TRAIN_RATIO = 0.8
SEED = 42
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images(folder: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def copy_split(
    class_name: str,
    images: list[Path],
    output_dir: Path,
    train_ratio: float,
    seed: int,
) -> tuple[int, int]:
    random.Random(seed).shuffle(images)
    train_count = int(len(images) * train_ratio)
    splits = {
        "train": images[:train_count],
        "val": images[train_count:],
    }

    for split, split_images in splits.items():
        target_dir = output_dir / split / class_name
        target_dir.mkdir(parents=True, exist_ok=True)

        for image_path in split_images:
            source_tag = image_path.parts[-3] if len(image_path.parts) >= 3 else image_path.parent.name
            target_name = f"{source_tag}_{image_path.name}"
            shutil.copy2(image_path, target_dir / target_name)

    return len(splits["train"]), len(splits["val"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara dataset YOLO classification damage/no_damage.")
    parser.add_argument("--output", default=OUTPUT_DIR, type=Path, help="Carpeta de salida.")
    parser.add_argument("--train-ratio", default=TRAIN_RATIO, type=float, help="Proporcion para train.")
    parser.add_argument("--seed", default=SEED, type=int, help="Semilla para split reproducible.")
    args = parser.parse_args()

    output_dir = args.output
    if output_dir.exists():
        shutil.rmtree(output_dir)

    for class_name, source_dirs in SOURCE_CLASSES.items():
        images: list[Path] = []
        for source_dir in source_dirs:
            if not source_dir.exists():
                print(f"AVISO: no existe la carpeta: {source_dir}")
                continue
            found = list_images(source_dir)
            images.extend(found)
            print(f"{class_name}: {len(found)} imagenes desde {source_dir}")

        if not images:
            raise ValueError(f"No encontre imagenes para la clase: {class_name}")

        train_count, val_count = copy_split(class_name, images, output_dir, args.train_ratio, args.seed)
        print(f"{class_name}: {len(images)} total, {train_count} train, {val_count} val")

    print(f"\nOK: dataset de clasificacion creado en '{output_dir}'")


if __name__ == "__main__":
    main()
