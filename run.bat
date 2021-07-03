cd /D "%~dp0"

python "main.py" %*

if NOT ["%errorlevel%"]==["0"] pause
