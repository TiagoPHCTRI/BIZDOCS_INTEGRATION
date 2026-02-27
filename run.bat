@echo off
REM Script para executar o BizDocs Integrator

REM Definir o diretório do script
cd /d "%~dp0"

REM Executar o main.exe
if exist "C:\Trigenius\bizdocs_integrator\main.exe" (
    echo Executando BizDocs Integrator...
    C:\Trigenius\bizdocs_integrator\main.exe
    if errorlevel 0 (
        echo.
        echo Execução concluída com sucesso!
        echo Os ficheiros JSON foram guardados em: reports\
        pause
    ) else (
        echo Erro ao executar!
        pause
    )
) else (
    echo Erro: main.exe não encontrado em dist\
    echo Execute primeiro: pyinstaller --onefile main.py
    pause
)
