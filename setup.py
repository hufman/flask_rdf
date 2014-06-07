#!/usr/bin/env python

from distutils.core import setup
try:
	from setuptools import setup
except:
	pass

requirements = open('requirements.txt').read().split('\n')
test_requirements = open('requirements.test.txt').read().split('\n')

setup(name='flask_rdf',
      version='0.1.3',
      description='Flask decorator to output RDF using content negotiation',
      author='Walter Huf',
      url='https://github.com/hufman/flask_rdf',
      packages=['flask_rdf'],
      install_requires=requirements,
      test_requires=requirements + test_requirements
)
