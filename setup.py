# -*- coding: utf-8 -*-
from setuptools import setup

setup(name="pyrestcli",
      author="Daniel Carrión",
      author_email="dani@computados.com",
      description="Generic REST client for Python",
      version="0.6.11",
      license="MIT",
      url="https://github.com/danicarrion/pyrestcli",
      install_requires=['requests>=2.10.0', 'python-dateutil>=2.5.3', 'future>=0.15.2'],
      packages=["pyrestcli"])
