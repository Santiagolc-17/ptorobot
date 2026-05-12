import random
import shutil
from pathlib import Path

SOURCE_CLASSES = {
    "damage": Path("Damage/images"),
    "no_damage": Path("NoDamage/images"),
}

OUTPUT_DIR = Path("dataset")
TRAIN_RATIO = 0.8
SEED = 42
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images(folder: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def copy_split(class_name: str, images: list[Path]) -> tuple[int, int]:
    random.Random(SEED).shuffle(images)
    train_count = int(len(images) * TRAIN_RATIO)
    splits = {
        "train": images[:train_count],
        "val": images[train_count:],
    }

    for split, split_images in splits.items():
        target_dir = OUTPUT_DIR / split / class_name
        target_dir.mkdir(parents=True, exist_ok=True)

        for image_path in split_images:
            shutil.copy2(image_path, target_dir / image_path.name)

    return len(splits["train"]), len(splits["val"])


def main() -> None:
    for class_name, source_dir in SOURCE_CLASSES.items():
        if not source_dir.exists():
            raise FileNotFoundError(f"No existe la carpeta: {source_dir}")

        images = list_images(source_dir)
        if not images:
            raise ValueError(f"No encontre imagenes en: {source_dir}")

        train_count, val_count = copy_split(class_name, images)
        print(f"{class_name}: {train_count} train, {val_count} val")

    print(f"\nOK: dataset de clasificacion creado en '{OUTPUT_DIR}'")


if __name__ == "__main__":
    main()
