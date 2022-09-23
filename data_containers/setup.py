import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="data_containers",
    version="0.0.1",

    description="Data Lake ECS Deployment",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "data_containers"},
    packages=setuptools.find_packages(where="data_containers"),

    install_requires=[
        "aws-cdk-lib>=2.0.0",
        "constructs>=10.0.0",
        "aws-cdk.aws-glue-alpha==2.43.1a0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
