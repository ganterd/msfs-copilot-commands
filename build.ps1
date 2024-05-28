./env/Scripts/Activate.ps1

pip install -r requirements.txt

pyinstaller --noconfirm build.spec
