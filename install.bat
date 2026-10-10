@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo   《This Is the President》简体中文汉化补丁 - 安装
echo ============================================================
echo.

rem ---- 1. 找 Python（优先用包内自带的便携版，免安装） -------------------
set PY=
if exist "%~dp0runtime\python\python.exe" (
  set PY="%~dp0runtime\python\python.exe"
  echo [i] 使用包内自带 Python（无需你安装任何东西）
) else (
  where py >nul 2>nul && set PY=py -3
  if not defined PY ( where python >nul 2>nul && set PY=python )
  if not defined PY (
    echo [x] 没找到 Python，且包内没有 runtime 目录。
    echo     请重新下载完整压缩包（含 runtime\），或自行安装 Python 3.9+ ^(64 位^)：
    echo     https://www.python.org/downloads/windows/
    echo     安装时务必勾选 "Add python.exe to PATH"，然后重新运行本脚本。
    pause & exit /b 1
  )
  echo [i] Python: %PY%
)

rem ---- 2. 定位游戏 ----------------------------------------------------
set GAME=
for /f "delims=" %%i in ('%PY% "%~dp0patch.py" --list-games 2^>nul') do (
  if not defined GAME set GAME=%%i
)
if not defined GAME (
  echo [x] 没在 Steam 库里找到游戏。请把游戏根目录拖到本窗口后回车：
  set /p GAME=游戏根目录: 
)
if not exist "!GAME!\This Is the President_Data\resources.assets" (
  echo [x] 目录无效: !GAME!
  pause & exit /b 1
)
echo [i] 游戏目录: !GAME!
echo.

rem ---- 3. 依赖（便携版已内置，跳过） -----------------------------------
echo [1/4] 检查依赖 UnityPy ...
%PY% -c "import UnityPy" 2>nul
if errorlevel 1 (
  echo       正在安装 UnityPy ^(需要联网^) ...
  %PY% -m pip install -r "%~dp0requirements.txt"
  if errorlevel 1 ( echo [x] pip 安装失败，请手动执行: %PY% -m pip install UnityPy & pause & exit /b 1 )
)
echo       OK

rem ---- 4. 注入译文 -----------------------------------------------------
echo [2/4] 注入译文到 assets ...
%PY% "%~dp0patch.py" --game "!GAME!"
if errorlevel 1 ( echo [x] 注入失败 & pause & exit /b 1 )

rem ---- 5. BepInEx + 插件 ----------------------------------------------
echo [3/4] 安装 BepInEx 与字体插件 ...
if not exist "!GAME!\winhttp.dll" copy /y "%~dp0bepinex\winhttp.dll" "!GAME!\" >nul
if not exist "!GAME!\doorstop_config.ini" copy /y "%~dp0bepinex\doorstop_config.ini" "!GAME!\" >nul
xcopy /e /i /y "%~dp0bepinex\BepInEx" "!GAME!\BepInEx" >nul
if not exist "!GAME!\BepInEx\plugins" mkdir "!GAME!\BepInEx\plugins"
copy /y "%~dp0plugins\TITPFontFix.dll" "!GAME!\BepInEx\plugins\" >nul
if not exist "!GAME!\BepInEx\plugins\TITP-CHS" mkdir "!GAME!\BepInEx\plugins\TITP-CHS"
copy /y "%~dp0data\fonts\sub-Regular.ttf" "!GAME!\BepInEx\plugins\TITP-CHS\" >nul
copy /y "%~dp0data\ui_extra.tsv" "!GAME!\BepInEx\plugins\TITP-CHS\" >nul
echo       OK

rem ---- 6. 校验 --------------------------------------------------------
echo [4/4] 校验 ...
if exist "!GAME!\BepInEx\plugins\TITPFontFix.dll" (echo       插件  OK) else (echo       [x] 插件复制失败)
if exist "!GAME!\BepInEx\plugins\TITP-CHS\ui_extra.tsv" (echo       UI 覆盖表 OK) else (echo       [!] UI 覆盖表缺失，少量界面会残留英文)
if exist "!GAME!\winhttp.dll" (echo       BepInEx OK) else (echo       [x] winhttp.dll 缺失)

echo.
echo ============================================================
echo   安装完成！直接从 Steam 启动游戏即可。
echo   日志: "!GAME!\BepInEx\LogOutput.log"
echo   还原: 运行 uninstall.bat
echo   ^(安装完可以删掉本目录下的 runtime\ 文件夹以省空间^)
echo ============================================================
pause
