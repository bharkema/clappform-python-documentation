# PyPi modules
from setuptools import setup

# clappform Package imports.
import clappform


def readme():
    with open("README.md") as fd:
        return fd.read()


setup(
    name="clappform",
    version=clappform.__version__,
    description=clappform.__doc__,
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    url="https://clappform.readthedocs.io",
    author=clappform.__author__,
    author_email=clappform.__email__,
    keywords="wrapper",
    license=clappform.__license__,
    packages=["clappform"],
    install_requires=clappform.__requires__,
    include_package_data=True,
    project_urls={
        "Documentation": "https://clappform.readthedocs.io",
        "Source": "https://github.com/ClappFormOrg/clappform-python",
    }
)
