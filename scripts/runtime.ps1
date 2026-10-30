$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$localNode = Join-Path $ProjectRoot '.tools\node-v24.12.0-win-x64'
if (Test-Path -LiteralPath $localNode) { $env:Path = $localNode + ';' + $env:Path }
$pythonCandidates = @(Get-ChildItem -Path (Join-Path $ProjectRoot '.tools\python') -Filter python.exe -Recurse -ErrorAction SilentlyContinue)
if ($pythonCandidates.Count -gt 0) { $ProjectPython = $pythonCandidates[0].FullName }
else { $ProjectPython = (& py -3.14 -c 'import sys; print(sys.executable)'); if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.14.2 first.' } }
function Assert-Success { if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code $LASTEXITCODE" } }
