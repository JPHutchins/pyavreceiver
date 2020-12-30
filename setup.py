"""pyavreceiver"""

import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join("README.md"), "r") as fh:
    long_description = fh.read()

const = {}
with open(os.path.join("pyavreceiver", "const.py"), "r") as fp:
    exec(fp.read(), const)

setup(
    name=const["__title__"],
    version=const["__version__"],
    description="An async python library for controlling Audio Video Receiver devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jphutchins/pyavreceiver",
    author="J.P. Hutchins",
    author_email="jphutchins@gmail.com",
    license="ASL 2.0",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=["aiohttp", "PyYAML", "telnetlib3"],
    include_package_data=True,
    tests_require=["tox>=3.5.0,<4.0.0"],
    platforms=["any"],
    keywords="denon marantz receiver",
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Home Automation",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
)
