#!/usr/bin/env python

from distutils.core import setup
try:
	from setuptools import setup
except:
	pass

requirements = open('requirements.txt').read().split('\n')
test_requirements = open('requirements.test.txt').read().split('\n')
long_description = open('README.rst').read()

setup(name='flask_rdf',
      version='0.2.1',
      description='Flask decorator to output RDF using content negotiation',
      author='Walter Huf',
      author_email='hufman@gmail.com',
      url='https://github.com/hufman/flask_rdf',
      packages=['flask_rdf'],
      install_requires=requirements,
      test_requires=requirements + test_requirements,
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Flask',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
     ],
     license='BSD',
     platforms=['Any']
)
