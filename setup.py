from setuptools import setup, find_packages

setup(
    name="omniharness",
    version="0.1.0",
    description="Lightweight performance & token-reduction harness for Claude Code and coding agents",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="OmniHarness",
    url="https://github.com/repclosed/omniharness",
    packages=find_packages(),
    install_requires=[
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "omniharness=omniharness.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
)
