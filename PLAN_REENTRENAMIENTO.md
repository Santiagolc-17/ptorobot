# Plan chill para reentrenar Rescue Vision

Esta guia es para reentrenar el modelo con un banco de imagenes mas grande, sin hacerlo dramatico.

La idea es avanzar por sprints pequenos. Cada sprint tiene:

- objetivo
- que hacer
- como saber que ya quedo
- prompt pequeno para pedirme ayuda

## Primero: que estamos haciendo

Tu modelo actual clasifica imagenes en dos clases:

```text
damage
no_damage
```

No esta detectando cajas ni ubicando el dano dentro de la imagen. Esta respondiendo algo tipo:

```text
esta imagen parece damage
esta imagen parece no_damage
```

Eso esta perfecto para una primera version.

## Cuando usar Colab/GPU

Si vas a entrenar con pocas imagenes, puedes probar local.

Si vas a entrenar con muchas imagenes, usa Colab con GPU. Ayer hiciste bien cambiando runtime a GPU.

Regla simple:

| Caso | Que usar |
| --- | --- |
| Probar que el dataset esta bien armado | Local |
| Entrenar rapido con 100-300 imagenes | Local o Colab |
| Entrenar con banco grande | Colab con GPU |
| Entrenar varias veces comparando resultados | Colab con GPU |

Mi recomendacion para hoy:

```text
Si ya tienes muchas imagenes nuevas, usa Colab con GPU otra vez.
```

No porque sea obligatorio, sino porque te ahorra tiempo y frustracion.

## Camino feliz

```text
1. Juntar imagenes
2. Separar en damage / no_damage
3. Limpiar imagenes malas o repetidas
4. Preparar dataset train/val
5. Subir a Colab
6. Entrenar con GPU
7. Descargar best.pt
8. Reemplazar models/best.pt
9. Probar en la UI
10. Anotar resultados
```

## Sprint 1: Ordenar el banco de imagenes

Objetivo: dejar las imagenes listas para que el modelo aprenda bien.

Estructura recomendada:

```text
data_raw/
|-- damage/
`-- no_damage/
```

Que hacer:

1. Mete todas las imagenes con dano en `data_raw/damage`.
2. Mete todas las imagenes sin dano en `data_raw/no_damage`.
3. Evita mezclar clases.
4. Borra imagenes borrosas, negras, duplicadas o que no se entiendan.
5. Si dudas con una imagen, dejala fuera por ahora.

Como saber que ya quedo:

```text
Tengo dos carpetas limpias:
data_raw/damage
data_raw/no_damage
```

Prompt pequeno:

```text
Ayudame a revisar mi estructura de imagenes y dime si esta lista para entrenar.
```

## Sprint 2: Balancear un poco las clases

Objetivo: que el modelo no aprenda solo la clase mas abundante.

Idealmente quieres algo cercano a:

```text
damage:     500 imagenes
no_damage:  500 imagenes
```

No tiene que ser perfecto. Pero si tienes:

```text
damage:     2000
no_damage:  100
```

el modelo puede sesgarse.

Que hacer:

1. Cuenta cuantas imagenes tienes por clase.
2. Si una clase tiene poquitas, consigue mas.
3. Si una clase tiene demasiadas, no pasa nada, pero conviene revisar resultados con cuidado.

Como saber que ya quedo:

```text
Ya se cuantas imagenes tengo por clase y no esta absurdamente desbalanceado.
```

Prompt pequeno:

```text
Cuenta mis imagenes por clase y dime si mi dataset esta balanceado.
```

## Sprint 3: Generar el dataset de entrenamiento

Objetivo: crear esta estructura:

```text
dataset/
|-- train/
|   |-- damage/
|   `-- no_damage/
`-- val/
    |-- damage/
    `-- no_damage/
```

Que hacer:

1. Ajustar `prepare_cls_dataset.py` para leer desde `data_raw/`.
2. Hacer split 80/20:
   - 80% para entrenar
   - 20% para validar
3. Regenerar `dataset/`.

Comando:

```powershell
python .\prepare_cls_dataset.py
```

Como saber que ya quedo:

```text
dataset/train/damage tiene imagenes
dataset/train/no_damage tiene imagenes
dataset/val/damage tiene imagenes
dataset/val/no_damage tiene imagenes
```

Prompt pequeno:

```text
Actualiza mi script para generar dataset desde data_raw y limpiarlo antes de copiar.
```

## Sprint 4: Hacer una prueba local mini

Objetivo: comprobar que el dataset no esta roto antes de subirlo a Colab.

Que hacer:

Entrena poquito, solo para probar:

```powershell
yolo classify train data=dataset model=yolo11n-cls.pt imgsz=224 epochs=1 name=smoke_test
```

Si eso corre, el dataset probablemente esta bien.

Como saber que ya quedo:

```text
El entrenamiento de 1 epoch no truena.
```

Prompt pequeno:

```text
Haz una prueba rapida de entrenamiento local para validar que el dataset sirve.
```

## Sprint 5: Subir a Colab y usar GPU

Objetivo: entrenar mas rapido con GPU.

Que hacer en Colab:

1. Abre Colab.
2. Ve a `Runtime`.
3. Selecciona `Change runtime type`.
4. En hardware accelerator elige `T4 GPU` o cualquier GPU disponible.
5. Sube el dataset comprimido o montalo desde Drive.
6. Instala Ultralytics:

```python
!pip install ultralytics
```

7. Verifica GPU:

```python
!nvidia-smi
```

Si ves una GPU, vas bien.

Como saber que ya quedo:

```text
Colab muestra una GPU y ultralytics esta instalado.
```

Prompt pequeno:

```text
Guiame para subir mi dataset a Colab y verificar que la GPU esta activa.
```

## Sprint 6: Entrenar modelo real

Objetivo: generar un nuevo `best.pt`.

Comando recomendado en Colab:

```python
!yolo classify train data=dataset model=yolo11n-cls.pt imgsz=224 epochs=30 batch=32 name=damage_retrain_big
```

Si el dataset es muy grande y Colab se queda sin memoria, baja batch:

```python
!yolo classify train data=dataset model=yolo11n-cls.pt imgsz=224 epochs=30 batch=16 name=damage_retrain_big
```

Si quieres un modelo un poquito mas fuerte:

```python
!yolo classify train data=dataset model=yolo11s-cls.pt imgsz=224 epochs=30 batch=32 name=damage_retrain_big
```

Para empezar, usa `yolo11n-cls.pt`. Es mas ligero y suficiente para iterar.

Como saber que ya quedo:

```text
Existe un archivo parecido a:
runs/classify/damage_retrain_big/weights/best.pt
```

Prompt pequeno:

```text
Ayudame a elegir epochs, batch y modelo base para mi entrenamiento en Colab.
```

## Sprint 7: Descargar el modelo y probarlo local

Objetivo: usar el nuevo modelo en tu UI.

Que hacer:

1. Descarga desde Colab:

```text
runs/classify/damage_retrain_big/weights/best.pt
```

2. Copialo en tu repo local:

```text
models/best.pt
```

3. Abre la UI:

```powershell
.\run_ui.ps1
```

4. Prueba imagenes faciles y dificiles.

Como saber que ya quedo:

```text
La UI abre y predice usando el modelo nuevo.
```

Prompt pequeno:

```text
Ya tengo mi nuevo best.pt, ayudame a reemplazarlo y probarlo en la UI.
```

## Sprint 8: Evaluar sin clavarse demasiado

Objetivo: saber si mejoro o empeoro.

Haz una mini tabla manual:

| Imagen | Real | Predijo | Confianza | Comentario |
| --- | --- | --- | ---: | --- |
| ejemplo_1.jpg | damage | damage | 94% | bien |
| ejemplo_2.jpg | no_damage | damage | 71% | falso positivo |

Prueba minimo:

```text
10 imagenes con damage
10 imagenes sin damage
10 imagenes raras/dificiles
```

Como saber que ya quedo:

```text
Ya sabes en que se equivoca el modelo.
```

Prompt pequeno:

```text
Ayudame a armar una tabla simple para evaluar mis predicciones.
```

## Sprint 9: Mejorar con los errores

Objetivo: que el siguiente entrenamiento aprenda de lo que fallo.

Que hacer:

1. Junta las imagenes donde fallo.
2. Revisa si estaban mal etiquetadas.
3. Agrega mas ejemplos parecidos.
4. Reentrena.

Esto es normal:

```text
entreno -> pruebo -> veo errores -> agrego mejores datos -> reentreno
```

Como saber que ya quedo:

```text
Tengo una lista clara de errores y datos nuevos para corregirlos.
```

Prompt pequeno:

```text
Estas son las predicciones donde fallo. Ayudame a decidir que imagenes agregar para mejorar.
```

## Checklist de hoy

Si quieres hacerlo hoy sin perderte:

```text
[ ] Crear data_raw/damage y data_raw/no_damage
[ ] Mover imagenes nuevas a esas carpetas
[ ] Contar imagenes por clase
[ ] Ajustar prepare_cls_dataset.py si hace falta
[ ] Generar dataset
[ ] Probar 1 epoch local
[ ] Subir dataset a Colab
[ ] Activar GPU
[ ] Entrenar 30 epochs
[ ] Descargar best.pt
[ ] Reemplazar models/best.pt
[ ] Probar UI
[ ] Anotar 10-30 resultados
```

## Prompt maestro, pero chiquito

Cuando quieras empezar conmigo, dime:

```text
Vamos con el Sprint 1. Revisa mi repo y ayudame a ordenar las imagenes para reentrenar.
```

Y nos vamos paso por paso, sin brincarnos media escalera.

