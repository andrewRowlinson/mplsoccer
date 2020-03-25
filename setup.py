from setuptools import setup

with open('README.md') as readme_file:
    README = readme_file.read()

setup(name='mplsoccer',
      version='0.0.1',
      description='mplsoccer is a Python plotting library for drawing soccer / football pitches quickly in Matplotlib.',
      long_description_content_type = "text/markdown",
      long_description = README,
      url='https://github.com/andrewRowlinson/mplsoccer',
      author='Andrew Rowlinson',
      author_email='rowlinsonandy@gmail.com',
      author_twitter='@numberstorm',
      license='MIT',
      packages=['mplsoccer'],
      python_requires='>=3.6',
      zip_safe=False)

install_requires=['matplotlib',
                  'seaborn',
                  'numpy']
