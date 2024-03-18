import os
import setuptools

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "requirements.txt")) as f:
    required_packages = f.read().splitlines()
with open(os.path.join(dir_path, "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="activity_validator",
    version="0.1.0",
    author="David Neuroth",
    author_email="d.neuroth@fz-juelich.de",
    description="An activity profile validation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="TODO",
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=required_packages,
    setup_requires=["setuptools-git"],
    license="MIT",
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Framework :: Dash",
        "Topic :: Scientific/Engineering",
    ],
    keywords=[
        "activity validation",
        "behavior model validation",
        "occupant behavior",
        "load profile generator",
        "validation framework",
    ],
)
