@echo off
chcp 65001 > nul
title Синхронизация WebXR с GitHub (Boltutin/station)
cls
echo =========================================================================
echo    Синхронизация проекта WebXR с GitHub (Boltutin/station)
echo =========================================================================
echo.
cd /d "%~dp0"

echo [1/3] Проверка изменений...
git add .

echo [2/3] Фиксация коммита...
git commit -m "Update WebXR station application"

echo [3/3] Отправка на GitHub...
git push origin main

echo.
echo =========================================================================
echo [УСПЕХ] Проект успешно обновлен на GitHub!
echo Ссылка на работающий WebXR сайт:
echo     https://boltutin.github.io/station/
echo =========================================================================
echo.
pause
