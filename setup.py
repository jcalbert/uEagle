from setuptools import setup, find_packages
from os import path
here = path.abspath(path.dirname(__file__))

REQUIRES_PYTHON = '>=3'
REQUIRED = ['requests']


# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='uEagle',
    version='0.0.1',
    packages=find_packages(),

    install_requires=REQUIRED,
    python_requires=REQUIRES_PYTHON,

    # metadata to display on PyPI
    author='Joseph Albert',
    author_email='joe@jcalbert.com',
    description='Tool to read data from Rainforest Legacy Eagle.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='rainforest eagle',
    url='https://github.com/jcalbert/uEagle',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Home Automation'
    ]
)
