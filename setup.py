from setuptools import find_packages,setup
from typing import List

def get_requirements(file_path: str = "requirements.txt") -> List[str]:
    requirements = []

    try:
        with open(file_path) as file:
            for line in file:
                requirement = line.strip()

                if requirement and requirement != "-e .":
                    requirements.append(requirement)

    except FileNotFoundError:
        print(f"{file_path} not found.")

    return requirements


setup(
    name = 'NetworkSecurity',
    version='0.0.1',
    author='Amrit Raj',
    author_email='amrritt1804@gamil.com',
    packages=find_packages(),
    install_requires=get_requirements()
)