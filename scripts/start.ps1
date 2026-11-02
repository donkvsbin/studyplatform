param([int]$Port = 0)
. "$PSScriptRoot\runtime.ps1"
if ($Port -ne 0) { $env:LEARNHUB_PORT = [string]$Port }
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
    & $venvPython run.py
    Assert-Success
} finally { Pop-Location }
