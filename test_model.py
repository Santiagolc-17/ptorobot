import os

os.environ["YOLO_OFFLINE"] = "True"

from ultralytics import YOLO

model = YOLO("best.pt")

print("Modelo cargado correctamente")