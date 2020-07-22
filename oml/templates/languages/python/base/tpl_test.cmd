@echo off
pytest tests --cov={{namespace}} --verbose
pylint {{namespace}}
bandit --recursive {{namespace}}