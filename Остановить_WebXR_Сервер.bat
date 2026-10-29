@echo off
chcp 65001 > nul
echo =========================================================================
echo    Остановка локального WebXR сервера (порт 8000)
echo =========================================================================
echo.
powershell -NoProfile -Command "$p = (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue).OwningProcess; if ($p) { Stop-Process -Id $p -Force; Write-Host '[УСПЕХ] Процесс сервера с PID ' $p ' успешно остановлен! Порт 8000 освобожден.' -ForegroundColor Green } else { Write-Host '[ИНФО] Сервер на порту 8000 не запущен (уже остановлен).' -ForegroundColor Yellow }"

taskkill /f /fi "WINDOWTITLE eq WebXR_Station_Server_8000*" >nul 2>&1
echo.
echo =========================================================================
ping 127.0.0.1 -n 3 > nul
