import setuptools
from setuptools import find_packages
from os import path

import uEagle

here = path.abspath(path.dirname(__file__))

REQUIRES_PYTHON = '>=3'
REQUIRED = ['urequests']


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='micropython-uEagle',
    version=uEagle.__version__,
    packages=find_packages(),

    install_requires=REQUIRED,
    python_requires=REQUIRES_PYTHON,

    # metadata to display on PyPI
    author='Joseph Albert',
    description='Micropython tool to read data from Rainforest Legacy Eagle.',
    long_description=long_description,
    keywords='rainforest eagle micropython',
    url='https://github.com/jcalbert/uEagle',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: Implementation :: MicroPython',
        'Topic :: Home Automation'
    ]
)