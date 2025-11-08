# 1️⃣ Python yolunu al
$pythonPath = (Get-Command python).Source
$homePath = Split-Path $pythonPath

# 2️⃣ pyvenv.cfg dosyası
$cfgFile = ".\.venv\pyvenv.cfg"

# 3️⃣ İçeriği sıfırdan yaz
@"
home = $homePath
include-system-site-packages = false
version = 3.10.11
"@ | Set-Content $cfgFile -Encoding UTF8

Write-Output "pyvenv.cfg güncellendi: home = $homePath"
