# encoding: utf-8

from distutils.core import setup

name = 'auf.django.permissions'

setup(name=name,
      version='0.1',
      description="Extensions au système de permissions de Django",
      author='Éric Mc Sween',
      author_email='eric.mcsween@auf.org',
      url='http://pypi.auf.org/%s' % name,
      license='GPL',
      packages=['auf.django.permissions'],
     )
