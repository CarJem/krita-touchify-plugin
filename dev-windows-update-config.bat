set SCRIPT_DIR=%CD%
set PLUGIN_NAME=touchify
set KRITA_PATH=C:\Users\demo\AppData\Roaming\krita\pykrita\
set PLUGIN_PATH=C:\Users\demo\AppData\Roaming\krita\pykrita\%PLUGIN_NAME%\

rmdir "%SCRIPT_DIR%\plugin\%PLUGIN_NAME%\resources\" /s /q
rmdir "%SCRIPT_DIR%\plugin\%PLUGIN_NAME%\configs\" /s /q

xcopy "%PLUGIN_PATH%\resources" "%SCRIPT_DIR%\plugin\%PLUGIN_NAME%\resources"  /E /H /C /I
xcopy "%PLUGIN_PATH%\configs" "%SCRIPT_DIR%\plugin\%PLUGIN_NAME%\configs"   /E /H /C /I