import os
from setuptools import setup, find_packages


version = None
base_path = os.path.abspath(os.path.dirname(__file__))
metadata_file_path = os.path.join(base_path, 'oml.yml')
with open(metadata_file_path, 'r') as f:
    for line in f:
        if line.startswith('version:'):
            version = line.replace('version:', '').strip()
            break

if not version:
    raise Exception('Version number not found in oml.yml file.')

setup(
    name='{{namespace}}',
    version=version,
    license='Proprietary',
    author='Microsoft Corporation',
    packages=find_packages(exclude=['tests', 'tests.*']),
)
