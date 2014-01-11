from setuptools import setup, find_packages
setup(
    name="Wink",
    version="0.1",
    packages=find_packages(),
    install_requires=['httplib2'],
    author="John S. Otto",
    author_email="me@johnotto.net",
    description="Library for interfacing with Wink devices by Quirky",
    license="MIT",
    keywords=("Wink Quirky Nimbus Spotter Porkfolio Pivot Power Genius"
              "Eggminder"),
    url="https://github.com/jso/py-wink",
)
