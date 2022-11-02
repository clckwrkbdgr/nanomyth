import os, sys, re
from setuptools import setup, find_packages

with open('README.md') as f: # pragma: no cover
    readme = f.read()

setup(
    name='nanomyth',
    version='0.0.0',
    author='Igor Chaika',
    author_email='clckwrkbdgr@gmail.com',
    url='https://github.com/clckwrkbdgr/nanomyth',
    license='LICENSE',
    description='Very minimal engine for very simple RPGs',
    long_description=readme,
    packages=find_packages(exclude=('dist', 'test', 'nanomyth.math.test')),
    include_package_data=True,
    install_requires=[
    ],
)
