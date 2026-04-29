@echo off
REM -------------------------------
REM PGM Envanter - Windows Starter
REM -------------------------------

setlocal ENABLEDELAYEDEXPANSION
title PGM Envanter Sunucusu

REM 0) Proje kokunu current dir yap
cd /d "%~dp0"

REM 1) Python var mi?
where python >nul 2>nul
if errorlevel 1 (
  echo [HATA] Python bulunamadi. Lutfen Python 3.11+ kurun: https://www.python.org/downloads/
  echo Kurulumda "Add Python to PATH" kutusunu isaretlemeyi unutmayin.
  pause
  exit /b 1
)

REM 2) Sanal ortam: .venv varsa onu kullan; yoksa venv varsa onu; hicbiri yoksa .venv olustur
set VENV_DIR=.venv
if not exist ".venv\Scripts\python.exe" (
  if exist "venv\Scripts\python.exe" (
    set VENV_DIR=venv
  ) else (
    echo [INFO] Sanal ortam olusturuluyor (.venv)...
    python -m venv .venv
    if errorlevel 1 (
      echo [HATA] Sanal ortam olusturulamadi.
      pause & exit /b 1
    )
  )
)

REM 3) Sanal ortami aktive et
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
  echo [HATA] Sanal ortam aktive edilemedi.
  pause & exit /b 1
)

REM 4) Gerekli paketler
echo [INFO] Gerekli paketler yukleniyor...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo [HATA] Paket kurulumu basarisiz.
  pause & exit /b 1
)

REM 5) .env yoksa, .env.template'dan kopyala
if not exist ".env" (
  if exist ".env.template" (
    copy /Y ".env.template" ".env" >nul
    echo [INFO] .env olusturuldu (.env.template kopyalandi). Lutfen kimlik bilgilerinizi .env dosyasina girin.
  ) else (
    echo [UYARI] .env.template bulunamadi. Ortam degiskenlerini manuel olusturmaniz gerekecek.
  )
)

REM (Opsiyonel) Demo verisi istiyorsaniz seed scriptlerini buradan calistirabilirsiniz:
REM python -m backend.seed_regions_branches
REM python -m backend.seed_users

REM 6) Flask ayarlari ve calistirma
set FLASK_APP=backend.app
set FLASK_DEBUG=0
set PYTHONUTF8=1

echo.
echo [OK] Sunucu basliyor: http://127.0.0.1:5000
echo [IP] Agdan erisim icin: http://<BU_BILGISAYARIN_IP_ADRESI>:5000  (Windows Guvenlik Duvari'nda izin vermeniz gerekebilir)
echo.

flask --app backend.app run --host=0.0.0.0 --port=5000
if errorlevel 1 (
  echo [HATA] Flask baslatilamadi.
  pause & exit /b 1
)

endlocal
