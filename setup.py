from setuptools import setup, find_packages
from os import path
import sdist_upip

here = path.abspath(path.dirname(__file__))

REQUIRES_PYTHON = '>=3'
REQUIRED = ['urequests']


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='micropython-uEagle',
    version='0.0.1',
    packages=find_packages(),

    install_requires=REQUIRED,
    python_requires=REQUIRES_PYTHON,
    cmdclass={'sdist': sdist_upip.sdist},


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
