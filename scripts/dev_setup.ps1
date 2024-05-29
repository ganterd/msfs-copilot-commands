# Create and activate the venv
python -m venv env
./env/Scripts/Activate.ps1

# Install requirements
pip install -r requirements.txt

# Build external bits like Piper TTS for windows
Push-Location .
try
{
    cd ./ext
    ./setup.ps1
}
finally
{
    Pop-Location
}

