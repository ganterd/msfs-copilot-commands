import platform
from pathlib import Path

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
import setuptools
from setuptools import setup

_DIR = Path(__file__).parent / ".."
_INSTALL_DIR = _DIR / "install"

__version__ = "1.2.0"

ext_modules = [
    Pybind11Extension(
        "piper_phonemize_cpp",
        [
            "../piper-phonemize/src/python.cpp",
            "../piper-phonemize/src/phonemize.cpp",
            "../piper-phonemize/src/phoneme_ids.cpp",
            "../piper-phonemize/src/tashkeel.cpp",
        ],
        define_macros=[("VERSION_INFO", __version__)],
        include_dirs=[str(_INSTALL_DIR / "include")],
        library_dirs=[str(_INSTALL_DIR / "lib")],
        libraries=["espeak-ng", "onnxruntime"],
        extra_compile_args=["/utf-8"]
    ),
]

setup(
    name="piper_phonemize",
    version=__version__,
    author="Michael Hansen",
    author_email="mike@rhasspy.org",
    url="https://github.com/rhasspy/piper-phonemize",
    description="Phonemization libary used by Piper text to speech system",
    long_description="",
    packages=["piper_phonemize"],
    package_data={
        "piper_phonemize": [
            "../piper_phonemize.dll",
            "../espeak-ng.dll"
        ]
        + [str(p) for p in (_DIR / "py" / "piper_phonemize" / "espeak-ng-data").rglob("*") ]
        + [str("libtashkeel_model.ort")]
    },
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7"
)

piper_module_dir = _DIR / "src" / "python_run" / "piper"
piper_data_files = [piper_module_dir / "voices.json"]

setup(
    name="piper-tts",
    version="1.2.0",
    description="A fast, local neural text to speech system that sounds great and is optimized for the Raspberry Pi 4.",
    url="http://github.com/rhasspy/piper",
    author="Michael Hansen",
    author_email="mike@rhasspy.org",
    license="MIT",
    packages=["piper"],
    package_data={"piper": [str(p.relative_to(piper_module_dir)) for p in piper_data_files]},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "piper = piper.__main__:main",
        ]
    },
    install_requires=[
        f"piper-phonemize~={__version__}",
        "onnxruntime==1.15.0"
    ],
    extras_require={"gpu": ["onnxruntime-gpu>=1.11.0,<2"], "http": ["flask>=3,<4"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="rhasspy piper tts",
)
