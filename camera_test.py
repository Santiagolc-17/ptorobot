import cv2

cap = cv2.VideoCapture(0)

ret, frame = cap.read()

print("RET:", ret)

if ret:
    print("Frame shape:", frame.shape)
    cv2.imwrite("test.jpg", frame)
    print("Imagen guardada")
else:
    print("No se pudo leer frame")

cap.release()

