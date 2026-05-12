import argparse
import json
import mimetypes
import os
import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote


BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault("YOLO_CONFIG_DIR", str((BASE_DIR / "Ultralytics").resolve()))


HTML = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rescue Vision</title>
  <style>
    :root {
      color-scheme: light;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
      background: #f4f5f7;
      color: #111827;
      --ink: #111827;
      --muted: #667085;
      --line: rgba(17, 24, 39, 0.11);
      --panel: rgba(255, 255, 255, 0.78);
      --panel-solid: #ffffff;
      --blue: #0a84ff;
      --orange: #ff7a1a;
      --red: #ff3b30;
      --green: #2fb344;
      --shadow: 0 24px 70px rgba(15, 23, 42, 0.12);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      padding: 28px;
      background:
        radial-gradient(circle at 18% 14%, rgba(10, 132, 255, 0.16), transparent 28%),
        radial-gradient(circle at 82% 12%, rgba(255, 122, 26, 0.14), transparent 24%),
        linear-gradient(135deg, #fbfcff 0%, #eef2f7 48%, #f8fafc 100%);
    }
    main {
      width: min(1120px, 100%);
      min-height: calc(100vh - 56px);
      margin: 0 auto;
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 16px;
      align-items: stretch;
    }
    .panel, .result {
      background: var(--panel);
      border: 1px solid rgba(255, 255, 255, 0.72);
      border-radius: 8px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(22px);
    }
    .panel {
      padding: 18px;
      min-height: 650px;
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 16px;
    }
    .toolbar {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 240px;
    }
    .mark {
      width: 46px;
      height: 46px;
      border-radius: 8px;
      display: grid;
      place-items: center;
      color: #fff;
      font-weight: 900;
      background: linear-gradient(145deg, #111827, #2f3a4f 48%, #ff7a1a);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.28), 0 14px 28px rgba(17, 24, 39, 0.18);
    }
    h1 {
      margin: 0;
      font-size: 28px;
      line-height: 1.1;
      letter-spacing: 0;
    }
    .subtitle {
      margin: 5px 0 0;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }
    .actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    input[type="file"] { display: none; }
    button, label.pick {
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.82);
      border-radius: 7px;
      padding: 10px 14px;
      min-height: 42px;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
      color: var(--ink);
      transition: transform 150ms ease, border-color 150ms ease, box-shadow 150ms ease;
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
    }
    button:hover:not(:disabled), label.pick:hover {
      transform: translateY(-1px);
      border-color: rgba(10, 132, 255, 0.38);
    }
    button.primary {
      border-color: rgba(10, 132, 255, 0.28);
      background: linear-gradient(180deg, #0a84ff, #0067d7);
      color: #ffffff;
    }
    button:disabled {
      opacity: 0.55;
      cursor: not-allowed;
      transform: none;
    }
    .drop {
      border: 1px solid rgba(17, 24, 39, 0.09);
      border-radius: 8px;
      display: grid;
      place-items: center;
      min-height: 520px;
      overflow: hidden;
      background:
        linear-gradient(rgba(255, 255, 255, 0.72), rgba(255, 255, 255, 0.72)),
        repeating-linear-gradient(0deg, transparent 0 34px, rgba(10, 132, 255, 0.06) 35px),
        repeating-linear-gradient(90deg, transparent 0 34px, rgba(10, 132, 255, 0.06) 35px);
      position: relative;
    }
    .drop::after {
      content: "";
      position: absolute;
      inset: 18px;
      border: 1px dashed rgba(15, 23, 42, 0.16);
      border-radius: 8px;
      pointer-events: none;
    }
    .drop.drag {
      border-color: rgba(10, 132, 255, 0.54);
      box-shadow: inset 0 0 0 1px rgba(10, 132, 255, 0.16);
    }
    .empty {
      text-align: center;
      color: var(--muted);
      padding: 24px;
      max-width: 420px;
      line-height: 1.5;
      display: grid;
      gap: 18px;
      justify-items: center;
      z-index: 1;
    }
    .robot {
      width: min(260px, 72vw);
      aspect-ratio: 1;
      position: relative;
      filter: drop-shadow(0 26px 30px rgba(15, 23, 42, 0.14));
    }
    .bot-head {
      position: absolute;
      left: 22%;
      right: 22%;
      top: 10%;
      height: 35%;
      border-radius: 8px;
      background: linear-gradient(145deg, #ffffff, #dce3ec);
      border: 1px solid rgba(17, 24, 39, 0.11);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.95);
    }
    .bot-head::before, .bot-head::after {
      content: "";
      position: absolute;
      top: 42%;
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: #0a84ff;
      box-shadow: 0 0 20px rgba(10, 132, 255, 0.75);
    }
    .bot-head::before { left: 27%; }
    .bot-head::after { right: 27%; }
    .bot-visor {
      position: absolute;
      left: 18%;
      right: 18%;
      top: 58%;
      height: 8px;
      border-radius: 999px;
      background: #111827;
    }
    .bot-core {
      position: absolute;
      left: 16%;
      right: 16%;
      top: 48%;
      height: 30%;
      border-radius: 8px;
      background: linear-gradient(145deg, #f8fafc, #cfd8e4);
      border: 1px solid rgba(17, 24, 39, 0.12);
    }
    .bot-core::before {
      content: "";
      position: absolute;
      left: 50%;
      top: 22%;
      width: 34px;
      height: 34px;
      transform: translateX(-50%);
      border-radius: 50%;
      background: radial-gradient(circle at 35% 35%, #fff, #ffb36b 42%, #ff7a1a 72%);
      box-shadow: 0 0 22px rgba(255, 122, 26, 0.48);
    }
    .bot-arm, .bot-arm.right {
      position: absolute;
      top: 55%;
      width: 20%;
      height: 11%;
      border-radius: 999px;
      background: #111827;
    }
    .bot-arm { left: 0; transform: rotate(-16deg); }
    .bot-arm.right { left: auto; right: 0; transform: rotate(16deg); }
    .bot-track {
      position: absolute;
      left: 20%;
      right: 20%;
      bottom: 10%;
      height: 12%;
      border-radius: 999px;
      background: repeating-linear-gradient(90deg, #111827 0 18px, #2f3a4f 18px 28px);
      box-shadow: inset 0 -3px 0 rgba(255, 255, 255, 0.12);
    }
    .empty strong {
      color: var(--ink);
      font-size: 20px;
      line-height: 1.2;
    }
    img {
      width: 100%;
      height: 100%;
      max-height: 650px;
      object-fit: contain;
      display: none;
      background: #0b1020;
      z-index: 1;
    }
    .result {
      padding: 18px;
      display: grid;
      grid-template-rows: auto auto auto 1fr;
      gap: 14px;
    }
    .badge {
      width: 100%;
      border-radius: 8px;
      padding: 24px;
      color: #ffffff;
      background: linear-gradient(145deg, #111827, #344154);
      min-height: 160px;
      display: grid;
      align-content: end;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
    }
    .badge.damage { background: linear-gradient(145deg, #3a1214, #ff3b30); }
    .badge.no_damage { background: linear-gradient(145deg, #11351e, #2fb344); }
    .label {
      display: block;
      font-size: 12px;
      opacity: 0.86;
      margin-bottom: 6px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0;
    }
    .prediction {
      font-size: 38px;
      line-height: 1;
      font-weight: 800;
      overflow-wrap: anywhere;
      text-transform: capitalize;
    }
    .meter {
      height: 10px;
      border-radius: 99px;
      background: rgba(17, 24, 39, 0.1);
      overflow: hidden;
    }
    .bar {
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, #0a84ff, #ff7a1a);
      transition: width 180ms ease;
    }
    .meta {
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }
    .mission {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .tile {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: rgba(255, 255, 255, 0.58);
    }
    .tile span {
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }
    .tile strong {
      display: block;
      color: var(--ink);
      font-size: 15px;
    }
    .scores {
      display: grid;
      gap: 8px;
      align-content: start;
    }
    .score {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.5);
      font-size: 14px;
    }
    .score span { color: var(--muted); font-weight: 700; }
    @media (max-width: 820px) {
      main { grid-template-columns: 1fr; }
      .panel { min-height: auto; }
      .drop { min-height: 420px; }
      .result { grid-template-rows: auto; }
    }
    @media (max-width: 560px) {
      body { padding: 14px; }
      main { min-height: calc(100vh - 28px); }
      .toolbar, .actions { width: 100%; }
      .actions { display: grid; grid-template-columns: 1fr 1fr; }
      button, label.pick { text-align: center; width: 100%; }
      h1 { font-size: 24px; }
      .prediction { font-size: 32px; }
    }
  </style>
</head>
<body>
  <main>
    <section class="panel">
      <div class="toolbar">
        <div class="brand">
          <div class="mark">RV</div>
          <div>
            <h1>Rescue Vision</h1>
            <p class="subtitle">Clasificador de danos para inspeccion rapida.</p>
          </div>
        </div>
        <div class="actions">
          <label class="pick" for="file">Elegir imagen</label>
          <input id="file" type="file" accept="image/*">
          <button id="predict" class="primary" disabled>Analizar</button>
        </div>
      </div>
      <div id="drop" class="drop">
        <div id="empty" class="empty">
          <div class="robot" aria-hidden="true">
            <div class="bot-head"><div class="bot-visor"></div></div>
            <div class="bot-arm"></div>
            <div class="bot-arm right"></div>
            <div class="bot-core"></div>
            <div class="bot-track"></div>
          </div>
          <div>
            <strong>Unidad de rescate lista</strong>
            <p>Arrastra una imagen o eligela desde tu computadora.</p>
          </div>
        </div>
        <img id="preview" alt="Vista previa">
      </div>
    </section>

    <aside class="result">
      <div id="badge" class="badge">
        <span class="label">Estado detectado</span>
        <div id="prediction" class="prediction">Lista</div>
      </div>
      <div class="mission">
        <div class="tile">
          <span>Modelo</span>
          <strong>YOLO CLS</strong>
        </div>
        <div class="tile">
          <span>Modo</span>
          <strong>Rescate</strong>
        </div>
      </div>
      <div>
        <div class="meter"><div id="bar" class="bar"></div></div>
        <p id="confidence" class="meta">Carga una imagen para probar el modelo.</p>
      </div>
      <div id="scores" class="scores"></div>
    </aside>
  </main>

  <script>
    const fileInput = document.getElementById("file");
    const predictButton = document.getElementById("predict");
    const preview = document.getElementById("preview");
    const empty = document.getElementById("empty");
    const drop = document.getElementById("drop");
    const badge = document.getElementById("badge");
    const prediction = document.getElementById("prediction");
    const confidence = document.getElementById("confidence");
    const bar = document.getElementById("bar");
    const scores = document.getElementById("scores");
    const labels = {
      damage: "Dano",
      no_damage: "Sin dano"
    };
    let selectedFile = null;

    function setFile(file) {
      if (!file || !file.type.startsWith("image/")) return;
      selectedFile = file;
      preview.src = URL.createObjectURL(file);
      preview.style.display = "block";
      empty.style.display = "none";
      predictButton.disabled = false;
      prediction.textContent = "Lista";
      confidence.textContent = file.name;
      scores.innerHTML = "";
      badge.className = "badge";
      bar.style.width = "0%";
    }

    fileInput.addEventListener("change", () => setFile(fileInput.files[0]));

    for (const eventName of ["dragenter", "dragover"]) {
      drop.addEventListener(eventName, event => {
        event.preventDefault();
        drop.classList.add("drag");
      });
    }

    for (const eventName of ["dragleave", "drop"]) {
      drop.addEventListener(eventName, event => {
        event.preventDefault();
        drop.classList.remove("drag");
      });
    }

    drop.addEventListener("drop", event => setFile(event.dataTransfer.files[0]));

    predictButton.addEventListener("click", async () => {
      if (!selectedFile) return;
      predictButton.disabled = true;
      predictButton.textContent = "Analizando...";

      const form = new FormData();
      form.append("image", selectedFile);

      try {
        const response = await fetch("/predict", { method: "POST", body: form });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "No se pudo analizar la imagen.");

        const pct = Math.round(data.confidence * 1000) / 10;
        prediction.textContent = labels[data.class_name] || data.class_name;
        confidence.textContent = `${pct}% de confianza`;
        badge.className = `badge ${data.class_name}`;
        bar.style.width = `${pct}%`;
        scores.innerHTML = data.scores.map(item => `
          <div class="score">
            <strong>${labels[item.name] || item.name}</strong>
            <span>${Math.round(item.confidence * 1000) / 10}%</span>
          </div>
        `).join("");
      } catch (error) {
        prediction.textContent = "Error";
        confidence.textContent = error.message;
        badge.className = "badge";
      } finally {
        predictButton.disabled = false;
        predictButton.textContent = "Analizar";
      }
    });
  </script>
</body>
</html>
"""


class MultipartError(ValueError):
    pass


def parse_multipart_image(content_type: str, body: bytes) -> tuple[bytes, str]:
    marker = "boundary="
    if marker not in content_type:
        raise MultipartError("No se encontro boundary en el formulario.")

    boundary = content_type.split(marker, 1)[1].strip().strip('"')
    delimiter = ("--" + boundary).encode()

    for part in body.split(delimiter):
        if b"Content-Disposition" not in part:
            continue

        header_end = part.find(b"\r\n\r\n")
        if header_end == -1:
            continue

        headers = part[:header_end].decode("utf-8", errors="ignore")
        data = part[header_end + 4 :]
        data = data.rstrip(b"\r\n-")

        if 'name="image"' not in headers:
            continue

        filename = "upload.jpg"
        for piece in headers.split(";"):
            piece = piece.strip()
            if piece.startswith("filename="):
                filename = unquote(piece.split("=", 1)[1].strip('"')) or filename

        if not data:
            raise MultipartError("La imagen llego vacia.")

        return data, Path(filename).name

    raise MultipartError("No se encontro el campo image.")


def make_handler(model_path: Path):
    model_cache = {"model": None}

    def get_model():
        if model_cache["model"] is None:
            if not model_path.exists():
                raise FileNotFoundError(f"No existe el modelo: {model_path}")
            from ultralytics import YOLO

            model_cache["model"] = YOLO(str(model_path))
        return model_cache["model"]

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML.encode("utf-8"))
                return

            self.send_error(404)

        def do_POST(self):
            if self.path != "/predict":
                self.send_error(404)
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                content_type = self.headers.get("Content-Type", "")
                image_bytes, filename = parse_multipart_image(content_type, self.rfile.read(length))
                suffix = Path(filename).suffix.lower()
                if suffix not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                    suffix = mimetypes.guess_extension(self.headers.get("Content-Type", "")) or ".jpg"

                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                    temp.write(image_bytes)
                    temp_path = Path(temp.name)

                try:
                    model = get_model()
                    result = model.predict(str(temp_path), verbose=False)[0]
                    top_id = int(result.probs.top1)
                    class_name = result.names[top_id]
                    confidence = float(result.probs.top1conf.item())
                    probs = result.probs.data.tolist()
                    scores = [
                        {"name": result.names[index], "confidence": float(score)}
                        for index, score in enumerate(probs)
                    ]
                    scores.sort(key=lambda item: item["confidence"], reverse=True)
                finally:
                    temp_path.unlink(missing_ok=True)

                self.send_json(
                    200,
                    {
                        "class_name": class_name,
                        "confidence": confidence,
                        "scores": scores,
                    },
                )
            except Exception as exc:
                self.send_json(400, {"error": str(exc)})

        def send_json(self, status: int, payload: dict):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            print(format % args)

    return Handler


def main():
    parser = argparse.ArgumentParser(description="UI local para clasificar damage vs no_damage.")
    parser.add_argument("--model", default="models/best.pt", help="Ruta al modelo .pt entrenado.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="No abrir navegador automaticamente.")
    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.is_absolute():
        model_path = BASE_DIR / model_path

    server = ThreadingHTTPServer((args.host, args.port), make_handler(model_path))
    url = f"http://{args.host}:{args.port}"
    print(f"UI lista en {url}")
    print(f"Modelo: {model_path}")

    if not args.no_browser:
        webbrowser.open(url)

    server.serve_forever()


if __name__ == "__main__":
    main()
