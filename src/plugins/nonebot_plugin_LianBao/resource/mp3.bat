@echo off
setlocal enabledelayedexpansion
 
set SOURCE_DIR=D:\Desktop\0\software\wbushu\Bot\IRONY\src\plugins\nonebot_plugin_LianBao\resource
set DEST_DIR=D:\Desktop\0\software\wbushu\Bot\IRONY\src\plugins\nonebot_plugin_LianBao\resource
 
if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"
 
for %%i in ("%SOURCE_DIR%\*.aac") do (
    set FILENAME=%%~ni
    set SOURCE_FILE=%%i
    set DEST_FILE="%DEST_DIR%\!FILENAME!.mp3"
    
    ffmpeg -i "!SOURCE_FILE!" -codec:a libmp3lame -q:a 4 "!DEST_FILE!"
)
 
echo Conversion complete.
pause