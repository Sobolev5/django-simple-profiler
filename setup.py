import os
import sys
import setuptools

__author__ = 'Sobolev Andrey <email.asobolev@gmail.com>'
__version__ = '0.5'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-simple-profiler',
    version=__version__,
    install_requires=['terminaltables', 'psutil'],
    author='Sobolev Andrey',
    url="https://github.com/Sobolev5/django-simple-profiler",        
    author_email='email.asobolev@gmail.com',
    description='Django simple profiler it is a useful tool for Django framework that allows you to profile your views.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=[".git", ".gitignore"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)