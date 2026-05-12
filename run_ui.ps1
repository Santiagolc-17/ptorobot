$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$model = Join-Path $PSScriptRoot "models\best.pt"
$env:YOLO_CONFIG_DIR = Join-Path $PSScriptRoot "Ultralytics"

if (-not (Test-Path $python)) {
    throw "No encontre Python en: $python"
}

if (-not (Test-Path $model)) {
    throw "No encontre el modelo en: $model"
}

Write-Host ""
Write-Host "UI lista en: http://127.0.0.1:8001"
Write-Host "Deja esta ventana abierta mientras usas la pagina."
Write-Host "Para detener el servidor, presiona Ctrl+C."
Write-Host ""

& $python .\predict_ui.py --model $model --host 127.0.0.1 --port 8001 --no-browser
