@echo off
REM =============================================================================
REM СКРИПТ ЗАМЕНЫ АВТОРА ВО ВСЕХ КОММИТАХ
REM =============================================================================
REM Автор: royfincher25-source
REM =============================================================================

echo ==============================================
echo   Замена автора на royfincher25-source
echo ==============================================
echo.

cd /d "%~dp0"

REM 1. Настройка Git config
echo [1/3] Настройка Git config...
git config user.name "royfincher25-source"
git config user.email "royfincher25-source@users.noreply.github.com"
echo      ✅ Настроено
echo.

REM 2. Замена автора во всех коммитах
echo [2/3] Замена автора во всех коммитах...
echo      Это может занять несколько минут...
echo.

git filter-branch --force --env-filter ^
"export GIT_AUTHOR_NAME='royfincher25-source'^
export GIT_AUTHOR_EMAIL='royfincher25-source@users.noreply.github.com'^
export GIT_COMMITTER_NAME='royfincher25-source'^
export GIT_COMMITTER_EMAIL='royfincher25-source@users.noreply.github.com'" ^
--tag-name-filter cat -- --branches --tags

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ошибка при замене автора!
    pause
    exit /b 1
)

echo      ✅ Автор заменён
echo.

REM 3. Проверка
echo [3/3] Проверка...
echo.
echo Последние 5 коммитов:
git log --oneline -5
echo.

echo ==============================================
echo   Готово!
echo ==============================================
echo.
echo Теперь выполните:
echo   git push --force --tags origin 'refs/heads/*'
echo.
pause
