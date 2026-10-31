. "$PSScriptRoot\runtime.ps1"
$venvPython = Join-Path $ProjectRoot 'backend\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) { throw 'Run setup.bat or scripts/setup.ps1 first.' }
Push-Location (Join-Path $ProjectRoot 'backend')
try {
    & $venvPython -m flask --app app:create_app db upgrade; Assert-Success
    & $venvPython -m flask --app app:create_app seed-demo; Assert-Success
} finally { Pop-Location }
Push-Location (Join-Path $ProjectRoot 'frontend')
try { npm.cmd run build; Assert-Success } finally { Pop-Location }
Push-Location (Join-Path $ProjectRoot 'backend')
try {
    Write-Output 'LearnHub: http://127.0.0.1:5000 (Ctrl+C to stop)'
    & '.\.venv\Scripts\waitress-serve.exe' --host=127.0.0.1 --port=5000 --call app:create_app
    Assert-Success
} finally { Pop-Location }
