. "$PSScriptRoot\runtime.ps1"
Push-Location $ProjectRoot
try {
    & $ProjectPython --version; Assert-Success
    node --version; Assert-Success
    & $ProjectPython -m venv backend/.venv; Assert-Success
    $venvPython = Join-Path $ProjectRoot 'backend\.venv\Scripts\python.exe'
    & $venvPython -m pip install -r backend/requirements.txt; Assert-Success
    if (-not (Test-Path -LiteralPath 'backend/.env')) { Copy-Item -LiteralPath 'backend/.env.example' -Destination 'backend/.env' }
    Push-Location backend
    try {
        & $venvPython -m flask --app app:create_app db upgrade; Assert-Success
        & $venvPython -m flask --app app:create_app seed-demo; Assert-Success
    } finally { Pop-Location }
    Push-Location frontend
    try { npm.cmd ci; Assert-Success } finally { Pop-Location }
    Write-Output 'Setup complete. Run .\scripts\start.ps1 and open http://127.0.0.1:5000'
} finally { Pop-Location }
