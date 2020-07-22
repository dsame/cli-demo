@ECHO OFF

if "%1" == "clean" (
	for /d %%i in (oml.egg-info\ build\ dist\ .pytest_cache\ .tox\) do rmdir /q /s %%i
	del /q /s .coverage
	goto end
)

if "%1" == "deploy" (
    for /d %%i in (dist\) do rmdir /q /s %%i
	del /q /s dist\
    python setup.py bdist_wheel --universal
	twine upload -r AIPlatform dist/*
    goto end
)

if "%1" == "dev" (
    pip install pipenv
    setx PIPENV_VENV_IN_PROJECT 1
    echo ENVIRONMENT=dev>> .env
    echo DB_PASSWORD=>> .env
    pipenv install --dev
    goto end
)

if "%1" == "test" (
    pipenv check
    pipenv run pytest --verbose --cov=oml
    pipenv run flake8 oml tests
    pipenv run bandit --recursive oml
    goto end
)

if "%1" == "docker-build" (
    docker build -t oml .
    goto end
)

if "%1" == "docker-run" (
    docker run -it --rm -p 127.0.0.1:8000:8000 oml
    goto end
)

if "%1" == "activate" (
    if exist C:\ProgramData\Miniconda3\Scripts\activate.bat (
        C:\ProgramData\Miniconda3\Scripts\activate
    ) else (
        %USERPROFILE%\AppData\Local\Continuum\miniconda3\Scripts\activate
    )
    conda activate "%2"
    goto end
)

:end
