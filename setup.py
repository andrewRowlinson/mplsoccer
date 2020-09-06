from setuptools import setup

with open("README.md", "r") as ofile:
    long_description = ofile.read()

setup(
    name="soccerplots",
    version="1.0.0",
    description="A Python package for data visualization for football analytics",
    packages=['soccerplots'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Anmol Durgapal",
    author_email="slothfulwave10@gmail.com",
    url="https://github.com/Slothfulwave612/soccerplots",
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "numpy",
        "matplotlib",
        "pillow"
    ]
)

