from setuptools import setup


setup(
    name='cultio',
    version='0.0.1',
    packages=['cultio'],
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["cultio/switch/switch_build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0"],
)
