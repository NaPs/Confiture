from setuptools import setup, find_packages
import os

version = '0.4'
ldesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(name='dotconf',
      version=version,
      description='Advanced configuration parser for Python',
      long_description=ldesc,
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Text Processing'],
      keywords='configuration parser dotconf conf',
      author='Antoine Millet',
      author_email='antoine@inaps.org',
      url='https://idevelop.org/p/dotconf/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=['ply', 'nose'])
