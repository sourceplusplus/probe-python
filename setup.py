import setuptools
from setuptools import setup

setup(name='sourceplusplus',
      version='0.1.6',
      description='Source++ Python Probe',
      url='https://github.com/sourceplusplus/probe-python',
      author='Source++',
      author_email='hello@sourceplusplus.com',
      license='Apache License, Version 2.0',
      packages=setuptools.find_packages(),
      install_requires=['vertx-eventbus-client>=1.0.0',
                        'apache-skywalking>=0.8.0',
                        'nopdb>=0.2.0',
                        'pyhumps>=3.7.2',
                        'PyYAML>=6.0'])
