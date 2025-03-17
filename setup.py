from setuptools import setup, find_packages

setup(
  name="resource-segmentation",
  version="0.0.1",
  author="Tao Zeyu",
  author_email="i@taozeyu.com",
  url="https://github.com/moskize91/resource-segmentation",
  packages=find_packages(),
  long_description=open("./README.md", encoding="utf8").read(),
  long_description_content_type="text/markdown",
)