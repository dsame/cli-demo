from setuptools import setup, find_packages


VERSION = '1.5.3'

DEPENDENCIES = [
    'adal~=1.2.1',
    'applicationinsights~=0.11.7',
    'azure-datalake-store~=0.0.45',
    'azure-identity~=1.0.1',
    'azure-keyvault~=4.0.0',
    'azure-mgmt-containerregistry~=2.8.0',
    'azure-storage-blob~=1.5.0',
    'azureml-core~=1.6.0.post1',
    'azureml-contrib-mir~=1.6.0',
    'bottle~=0.12',
    'click~=7.0',
    'colorama~=0.4.1',
    'cryptography==2.8',
    'GitPython>=2.1.0',
    'Jinja2~=2.10.1',
    'PTable==0.9.2',
    'pyopenssl==19.1.0',
    'PyYAML>=5.1',
    'requests>=2.0',
    'rsa==4.7',
    'ruamel.yaml==0.16.10',
]

setup(
    name='oml',
    version=VERSION,
    description='Machine Learning Model Management Tool',
    license='Proprietary',
    author='Microsoft Corporation',
    author_email='omldev@microsoft.com',
    python_requires='>=3.5',
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'oml=oml.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    install_requires=DEPENDENCIES,
)
