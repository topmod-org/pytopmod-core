from setuptools import setup

setup(
    name="pytopmod",
    author="Davy Risso <davy.risso@gmail.com>",
    version="0.1.0",
    packages=["pytopmod"],
    package_dir={"pytopmod": "src/pytopmod"},
    package_data={"pytopmod": ["py.typed"]},
)
