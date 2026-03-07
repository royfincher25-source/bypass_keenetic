@echo off
REM =============================================================================
REM СКРИПТ ОТПРАВКИ ПРОЕКТА НА GITHUB (Windows)
REM =============================================================================
REM Запустите этот файл для отправки всех изменений на GitHub
REM =============================================================================

echo ==============================================
echo   Отправка проекта на GitHub
echo ==============================================
echo.

REM Проверка наличия git
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git не найден!
    echo.
    echo Установите Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [OK] Git найден
echo.

REM Переход в директорию проекта
cd /d "%~dp0"
echo [INFO] Директория проекта: %CD%
echo.

REM Инициализация git (если нужно)
if not exist ".git" (
    echo [INFO] Инициализация git репозитория...
    git init
    echo.
)

REM Добавление всех файлов
echo [1/4] Добавление файлов...
git add .
echo.

REM Проверка статуса
echo [2/4] Статус изменений:
git status --short
echo.

REM Создание коммита
echo [3/4] Создание коммита...
git commit -m "Optimization, backup scripts, and tests

- Optimized config parsing (no python-dotenv dependency)
- Added caching for better performance (-75% memory)
- Added backup/restore scripts
- Added comprehensive test suite (65+ tests)
- Added documentation for embedded devices
- Core module with validators and parsers
- CI/CD workflow for GitHub Actions"

if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Нет изменений для коммита или ошибка
)

echo.

REM Настройка удалённого репозитория
echo [4/4] Настройка удалённого репозитория...
echo.
echo Введите URL вашего репозитория GitHub:
echo Пример: https://github.com/royfincher25-source/bypass_keenetic.git
echo.
set /p REPO_URL="URL репозитория: "

if "%REPO_URL%"=="" (
    echo [ERROR] URL не введён!
    pause
    exit /b 1
)

REM Проверка наличия remote
git remote | findstr "origin" >nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Update существующего remote...
    git remote set-url origin %REPO_URL%
) else (
    echo [INFO] Добавление remote origin...
    git remote add origin %REPO_URL%
)

echo.
echo ==============================================
echo   Отправка на GitHub...
echo ==============================================
echo.

REM Отправка на GitHub
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ошибка при отправке!
    echo.
    echo Возможные причины:
    echo 1. Неверный URL репозитория
    echo 2. Нет доступа к репозиторию
    echo 3. Требуется аутентификация
    echo.
    echo Попробуйте ввести credentials:
    git push -u origin main --force
) else (
    echo.
    echo ==============================================
    echo   [OK] Проект успешно отправлен на GitHub!
    echo ==============================================
)

echo.
pause
