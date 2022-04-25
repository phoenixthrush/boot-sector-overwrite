@echo off

SETLOCAL EnableDelayedExpansion
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")

call :colorEcho 0B "[Info] Tool made by 'Phoenixthrush UwU'" && echo. && echo.

if not exist .\mingw64 (
	call :colorEcho 0C "[Info] downloading the mingw64 package" && echo.
	powershell -Command "Start-Sleep -s 3; Invoke-WebRequest https://github.com/phoenixthrush/winlibs_mingw/releases/download/12.0.1-snapshot20220123-9.0.0-msvcrt-r1/winlibs-x86_64-posix-seh-gcc-12.0.1-snapshot20220123-mingw-w64-9.0.0-r1.zip -OutFile mingw64.zip"	
	call :colorEcho 0C "[Info] extracting the mingw64 package" && echo.
	powershell -Command "Start-Sleep -s 3; Expand-Archive -Path mingw64.zip -DestinationPath ."
	del .\mingw64.zip
)

call :colorEcho 0C "[Info] compiling executable "
call :colorEcho 0F " (mbr-custom-message.exe)" && echo.
.\mingw64\bin\windres.exe mbr-custom-message.rc mbr-custom-message.o
.\mingw64\bin\g++ -O3 -Os -s -o mbr-custom-message.exe mbr-custom-message.cpp mbr-custom-message.o
del mbr-custom-message.o
del boot.bin

echo.
call :colorEcho 0A "[Info] finished!" && echo.
call :colorEcho 0A "[Info] Press enter to exit!" && echo.
pause >nul
exit

:colorEcho
@echo off
< nul set /p ".=%DEL%" > "%~2"
findstr /v /a:%1 /R "^$" "%~2" nul
del "%~2" > nul 2>&1