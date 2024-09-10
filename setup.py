from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()
setup(
    name="colint",
    version="0.1",
    packages=find_packages(),
    package_data={
        "colint": ["pyproject.toml"],
    },
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "colint=colint.colinter:main",
        ],
    },
)
