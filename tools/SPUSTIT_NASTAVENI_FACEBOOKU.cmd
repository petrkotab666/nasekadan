@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Naše Kadaň - propojení Facebook stránky
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0nastavit-facebook.ps1"
exit /b %errorlevel%
