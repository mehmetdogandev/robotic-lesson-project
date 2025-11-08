@echo off
setlocal

REM Manuel olarak doğru Python yolunu ayarla
set PYTHON_PATH=C:\Users\ANDCARBPROJE2\AppData\Local\Programs\Python\Python310
for %%i in ("%PYTHON_PATH%") do set HOME_PATH=%%~dpi

REM pyvenv.cfg dosyası
set CFG_FILE=.venv\pyvenv.cfg

REM İçeriği sıfırdan yaz
(
echo home = %HOME_PATH%
echo include-system-site-packages = false
echo version = 3.10.11
) > %CFG_FILE%

echo pyvenv.cfg güncellendi: home = %HOME_PATH%
pause
