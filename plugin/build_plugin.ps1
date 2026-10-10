# Build a TITP plugin DLL with the system .NET Framework C# compiler and install it
# into the game's BepInEx/plugins folder.
#   powershell -ExecutionPolicy Bypass -File build_plugin.ps1
#   powershell -ExecutionPolicy Bypass -File build_plugin.ps1 -Source plugin\probe\TMPProbe.cs -Name TMPProbe
param(
  [string]$Source = 'plugin\TITPFontFix.cs',
  [string]$Name   = 'TITPFontFix'
)
$ErrorActionPreference = 'Stop'

$proj  = 'C:\Users\96333\TITP-CHS'
$game  = 'C:\Program Files (x86)\Steam\steamapps\common\This Is the President'
$man   = Join-Path $game 'This Is the President_Data\Managed'
$csc   = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$src   = Join-Path $proj $Source
if (-not (Test-Path $src)) { $src = $Source }
if (-not (Test-Path $src)) { throw "missing source: $src" }
$outD  = Join-Path $proj 'plugin\out'
$dll   = Join-Path $outD "$Name.dll"
$dest  = Join-Path $game "BepInEx\plugins\$Name.dll"

if (-not (Test-Path $outD)) { New-Item -ItemType Directory -Path $outD | Out-Null }

$refs = @(
  (Join-Path $man 'UnityEngine.dll'),
  (Join-Path $man 'UnityEngine.CoreModule.dll'),
  (Join-Path $man 'UnityEngine.TextRenderingModule.dll'),
  (Join-Path $man 'UnityEngine.TextCoreModule.dll'),
  (Join-Path $man 'UnityEngine.UIModule.dll'),
  (Join-Path $man 'UnityEngine.UI.dll'),
  (Join-Path $man 'Unity.TextMeshPro.dll'),
  (Join-Path $game 'BepInEx\core\BepInEx.dll')
)
foreach ($r in $refs) { if (-not (Test-Path $r)) { throw "missing reference: $r" } }

$cscArgs = @('/nologo', '/target:library', '/optimize+', "/out:$dll")
foreach ($r in $refs) { $cscArgs += "/reference:$r" }
$cscArgs += $src

& $csc @cscArgs
if ($LASTEXITCODE -ne 0) { throw "csc failed with exit code $LASTEXITCODE" }

Copy-Item -LiteralPath $dll -Destination $dest -Force
$fi = Get-Item $dll
"sources  : $src"
"built    : $dll ($($fi.Length) bytes, $($fi.LastWriteTime))"
"sha256   : $((Get-FileHash $dll -Algorithm SHA256).Hash)"
"installed: $dest"
