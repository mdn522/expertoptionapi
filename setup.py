"""The python wrapper for ExpertOption API package setup."""
from setuptools import (setup, find_packages)

setup(
    name="expertoptionapi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests", "websocket-client", "simplejson", "pause"],
    include_package_data=True,
    description="ExpertOption API for python",
    long_description="ExpertOption API for python",
    url="https://github.com/mdn522/expertoptionapi",
    author="Abdullah Mallik",
    author_email="mdn522@gmail.com",
    zip_safe=False
)
