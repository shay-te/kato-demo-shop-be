import os
import re

from setuptools import find_namespace_packages, find_packages, setup

dir_path = os.path.dirname(os.path.realpath(__file__))


def _read(*path_parts) -> str:
    with open(os.path.join(dir_path, *path_parts), 'r', encoding='utf-8') as file:
        return file.read()


# Read as text: importing the package would load core_lib, SQLAlchemy and
# Hydra before the build has installed them.
version = re.search(r"^__version__ = '([^']+)'", _read('demo_shop_core_lib', '__init__.py'), re.MULTILINE).group(1)

requirements = [
    line.strip()
    for line in _read('requirements.txt').splitlines()
    if line.strip() and not line.strip().startswith('#')
]

packages = find_packages(exclude=['tests', 'tests.*']) + find_namespace_packages(include=['hydra_plugins.*'])

setup(
    name='demo_shop_core_lib',
    version=version,
    author='Kato Demo',
    description='Demo shop library built on core-lib',
    long_description=_read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/shay-te/kato-demo-shop-be',
    packages=packages,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.7',
)
