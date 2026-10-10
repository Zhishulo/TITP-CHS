@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo   《This Is the President》汉化补丁 - 还原 / 卸载
echo ============================================================

set PY=
rem ---- 优先用包内自带的便携版 Python，免安装 ----
if exist "%~dp0runtime\python\python.exe" (
  set PY="%~dp0runtime\python\python.exe"
)
if not defined PY ( where py >nul 2>nul && set PY=py -3 )
if not defined PY ( where python >nul 2>nul && set PY=python )

set GAME=
if exist "%~dp0install_info.json" (
  for /f "usebackq tokens=2 delims=:," %%a in (`findstr /i "\"game\"" "%~dp0install_info.json"`) do (
    if not defined GAME set GAME=%%a
  )
  set GAME=!GAME:"=!
  set GAME=!GAME: =!
)
if not defined GAME (
  echo 请把游戏根目录拖到本窗口后回车：
  set /p GAME=游戏根目录: 
)
echo [i] 游戏目录: !GAME!
echo.

if defined PY (
  echo [1/2] 还原 assets ...
  %PY% "%~dp0patch.py" --game "!GAME!" --restore
) else (
  echo [!] 没找到 Python，跳过 assets 还原。
  echo     可改用 Steam 右键游戏 -^> 属性 -^> 已安装文件 -^> 验证游戏文件完整性。
)

echo [2/2] 移除字体插件 ...
if exist "!GAME!\BepInEx\plugins\TITPFontFix.dll" del /q "!GAME!\BepInEx\plugins\TITPFontFix.dll"
if exist "!GAME!\BepInEx\plugins\TITP-CHS" rmdir /s /q "!GAME!\BepInEx\plugins\TITP-CHS"
echo      OK

echo.
echo 完成。BepInEx 本体仍保留在游戏目录（如需彻底删除，手动删掉
echo winhttp.dll、doorstop_config.ini、BepInEx 三项即可）。
pause
