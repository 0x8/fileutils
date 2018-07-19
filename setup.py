from setuptools import setup, find_packages

setup (
    name = 'fileutils',
    author = 'Nullp0inter',
    version = '0.0.1',
    description = 'Library to bring some file niceness to your life',
    long_description = 'Adds file related functions for handling copying of files'\
                    + ' some hashing options and more.',

    install_requires = [
        'coloredlogs==10.0'
    ],
    packages = find_packages()
)
