from setuptools import setup, find_packages
from io import open
import os

version = '2.1'
ldesc = open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf8').read()

setup(name='confiture',
      version=version,
      description='Advanced configuration parser for Python',
      long_description=ldesc,
      classifiers=['Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Text Processing'],
      keywords='configuration parser confiture conf dotconf',
      author='Antoine Millet',
      author_email='antoine@inaps.org',
      url='https://idevelop.org/p/confiture/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=['ply'])
