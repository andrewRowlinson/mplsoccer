from setuptools import setup

import mplsoccer
VERSION = mplsoccer.__version__

with open('README.md') as readme_file:
    README = readme_file.read()

setup(name='mplsoccer',
      version=VERSION,
      description='A Python package for data visualization for football/ soccer analytics.',
      long_description_content_type="text/markdown",
      long_description=README,
      classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Scientific/Engineering :: Visualization'],
      url='https://github.com/andrewRowlinson/mplsoccer',
      author='Anmol Durgapal, Andrew Rowlinson',
      author_email='slothfulwave10@gmail.com, rowlinsonandy@gmail.com',
      author_twitter='@numberstorm, @slothfulwave612',
      license='MIT',
      packages=['mplsoccer'],
      python_requires='>=3.6',
      zip_safe=False)

install_requires = ['matplotlib',
                    'seaborn',
                    'scipy',
                    'pandas',
					'pillow',
                    'numpy']
