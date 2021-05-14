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
        "aws-cdk.core==1.95.0",
        "aws-cdk.aws-iam",
        "aws-cdk.aws-ec2",
        "aws-cdk.aws-ecs",
        "aws-cdk.aws-ecs-patterns",
        "aws-cdk.aws-applicationautoscaling",
        "aws-cdk.aws-s3"
        "aws-cdk.aws-secretsmanager",
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
