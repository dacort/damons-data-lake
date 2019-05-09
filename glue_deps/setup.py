from setuptools import setup, find_packages
setup(
    name = "glue_deps",
    version = "0.3",
    packages = find_packages(),
    install_requires=[
        'requests==2.21.0',
    ]
)