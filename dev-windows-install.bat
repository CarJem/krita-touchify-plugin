set SCRIPT_DIR=%CD%
set PLUGIN_NAME=touchify
set KRITA_PATH=C:\Users\demo\AppData\Roaming\krita\pykrita\
set PLUGIN_PATH=C:\Users\demo\AppData\Roaming\krita\pykrita\%PLUGIN_NAME%\

rmdir "%PLUGIN_PATH%" /s /q
copy "%SCRIPT_DIR%\plugin\%PLUGIN_NAME%.desktop" "%KRITA_PATH%"
copy "%SCRIPT_DIR%\plugin\%PLUGIN_NAME%.action" "%KRITA_PATH%"
xcopy "%SCRIPT_DIR%\plugin\%PLUGIN_NAME%" "%PLUGIN_PATH%" /E/H