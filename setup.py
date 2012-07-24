# encoding: utf-8

from setuptools import setup, find_packages

name = 'auf.django.permissions'
version = '0.4'

setup(name=name,
      version=version,
      description="Extensions au système de permissions de Django",
      author='Éric Mc Sween',
      author_email='eric.mcsween@auf.org',
      url='http://pypi.auf.org/%s' % name,
      license='GPL',
      packages=find_packages(exclude=['tests', 'tests.*']),
      namespace_packages=['auf', 'auf.django'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools'],
     )
