from setuptools import setup, find_packages

setup(
    name="articles",
    version="0.1.0",
    description="An extremely simple blog engine based on Markdown files",
    url="https://github.com/svpino/articles",
    author="Santiago L. Valdarrama",
    author_email="svpino@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["tests",]),
    install_requires=["markdown", "pygments"],
    zip_safe=False,
)
