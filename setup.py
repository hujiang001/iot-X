#-*-coding=utf8-*-

from setuptools import setup,find_packages

setup(
    name = 'iotX',
    version = '1.0',
    author = 'Jeffery Jiang',
    author_email = 'hujiang001@gmail.com',
    url = 'www.iotx.com',
    summary = 'iotX - a simple framework for connecting devices with the web cloud',
    license = 'MIT',
    description = 'A simple framework for connecting devices with the web cloud',
    long_description = open('README.md').read(),
    keywords = "iot cloud framework",
    packages= find_packages(),
    install_requires = ['tornado'],
    requires = ['tornado (>=1.2.1)']
)

