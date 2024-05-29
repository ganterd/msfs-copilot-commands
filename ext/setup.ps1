# Build piper-phonemize
$install_path = "$PSScriptRoot/install" -replace "\\","/"
echo $install_path

Push-Location .
try
{
    cd piper-phonemize

    # This is most of the stuff from their makefile
    cmake -Bbuild -DCMAKE_INSTALL_PREFIX="$install_path"
    cmake --build build --config Release
    cmake --install build --prefix "$install_path"
}
finally
{
    Pop-Location
}

# Build piper
Push-Location .
try
{
    cd piper

    # This is most of the stuff from their makefile
	cmake -Bbuild -DCMAKE_INSTALL_PREFIX="$install_path" -DPIPER_PHONEMIZE_DIR="$install_path"
	cmake --build build --config Release
	cmake --install build --prefix "$install_path"
}
finally
{
    Pop-Location
}

# Build package piper-phonemize and piper into python
Push-Location .
try
{
    cd py

    Get-Item -Path "build" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    Get-Item -Path "dist" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    Get-Item -Path "piper_phonemize" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    
    Remove-Item -Path "piper" -Recurse -Force

    Copy-Item -Path "../piper-phonemize/piper_phonemize" -Destination "piper_phonemize" -Recurse -Force
    Copy-Item -Path "../install/bin/piper_phonemize.dll" -Destination "." -Force
    Copy-Item -Path "../install/bin/espeak-ng.dll" -Destination "." -Force
    Copy-Item -Path "../install/share/espeak-ng-data" -Destination "piper_phonemize/espeak-ng-data" -Recurse -Force
    Copy-Item -Path "../install/share/libtashkeel_model.ort" -Destination "." -Force
    

    Copy-Item -Path "../piper/src/python_run/piper" -Destination "piper" -Recurse -Force

    python ./setup.py build
    python ./setup.py install
}
finally
{
    Pop-Location
}