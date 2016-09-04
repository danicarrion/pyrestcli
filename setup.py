# -*- coding: utf-8 -*-
from setuptools import setup

setup(name="pyrestcli",
      author="Daniel Carrión",
      author_email="dani@computados.com",
      description="Generic REST client for Python",
      version="0.0.1",
      license="MIT",
      url="https://github.com/danicarrion/pyrestcli",
      install_requires=['requests==2.11.1', 'python-dateutil==2.5.3'],
      packages=["pyrestcli"])
