import os
import site
import sys

from setuptools import setup

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

with open("./requirements.txt") as f:
    install_requires = f.read().splitlines()

print(os.getcwd())

with open("./README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="elasticsearchquerygenerator",
    version="1.1.0",
    description="""
    Create Complex Elastic Search Query in Seconds
    Please see documentation for more details
     """,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juguerre/elasticsearchquerygenerator.git",
    author="Andres Guerrero",
    author_email="juguerre@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["elasticsearchquerygenerator"],
    include_package_data=True,
    install_requires=install_requires,
    python_requires="<3.9",
)
