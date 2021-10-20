from setuptools import setup, find_packages
from os.path import join, dirname
import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
	print("This script requires Python >= 3.6")
	exit(1)

setup(
    name="msspeech",
    version="2.7",
    author="alekssamos",
    author_email="aleks-samos@yandex.ru",
    url="https://github.com/alekssamos/msspeech/",
    packages=find_packages(),
    include_package_data=True,
    long_description_content_type="text/markdown",
    long_description=open(join(dirname(__file__), "README.md"), encoding="UTF8").read(),
)
