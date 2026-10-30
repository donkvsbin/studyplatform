. "$PSScriptRoot\runtime.ps1"
Push-Location (Join-Path $ProjectRoot 'frontend')
try { npm.cmd run build; Assert-Success } finally { Pop-Location }
Push-Location (Join-Path $ProjectRoot 'backend')
try {
    Write-Output 'LearnHub: http://127.0.0.1:5000 (Ctrl+C to stop)'
    & '.\.venv\Scripts\waitress-serve.exe' --host=127.0.0.1 --port=5000 --call app:create_app
    Assert-Success
} finally { Pop-Location }
