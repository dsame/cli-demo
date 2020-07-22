# Machine Learning Model Management Tool (OML)

[![Build Status](https://office.visualstudio.com/GSX/_apis/build/status/AIPlatformBuilds/AIPlatform.OML-CI?branchName=master)](https://office.visualstudio.com/GSX/_build/latest?definitionId=4645?branchName=master)

OML is a command-line tool that makes it easy to manage model and
to automate the model deployment workflow. It provides tools for
data scientist to develop, serve and test model code locally.
It is simple - you only need to implement predict() -
and reusable for many serving platforms.

**Write once. Use many.**

## Deployment workflow

![](../docs/images/compliant-workflow.png)

## Quick start

Read the onboarding [doc](../docs/onboarding.md).

## Local development

1. Install [miniconda](https://conda.io/miniconda.html)
1. Setup conda environment

    ```
        > make activate
        > conda create -n oml python=3.5
        > conda activate oml
        > make dev
    ```
1. Run shell in virtual env
    ```
        > pipenv shell
    ```
> Please run `pipenv update` whenever making changes to `DEPENDENCIES` in `setup.py`

### Run tests
```
    > make test
```

### Clean up cache
```
    > make clean
```

## Package deployment to PyPi repository

To publish a new package, increment the version number in setup.py

## Publish package to test feed

1. Add credentials for [AIPlatform-Test](https://dev.azure.com/office/GSX/_packaging?_a=package&feed=AIPlatform-Test&package=oml&protocolType=PyPI) feed. Select Connect to feed, Python, Set up your pip.ini/pip.conf, Generate Credentials, and paste into local pip.ini.
1. Check that current version in setup.py version is not already uploaded to the test feed, or update to a new version for testing
1. Create new package
    ```
        > python setup.py bdist_wheel
    ```
1. Publish the package to the test feed
    ```
        > twine upload -r AIPlatform-Test dist/*
    ```
