#!/usr/bin/env python


from setuptools import setup, find_packages

VERSION = (0, 2, 1)
VERSION_STR = ".".join([str(x) for x in VERSION])

setup(
    name='mangaGet',
    version=VERSION_STR,
    description="CLI manga ripper.",
    author='Christopher Jackson',
    author_email='darkdragn.cj@gmail.com',
    license='GNU GPLv2',
    url='https://github.com/darkdragn/mangaGet',
    packages = ['mangaGet', 'mangaGet.sites'],
    py_modules = ['mangaGetCli'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
