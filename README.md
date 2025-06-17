# python-google-weather-api

A python client library for Google Weather API.

See <https://developers.google.com/maps/documentation/weather>

Only API keys are supported, see <https://developers.google.com/maps/documentation/weather/get-api-key>

## Development environment

```sh
python3 -m venv .venv
source .venv/bin/activate
# for Windows CMD:
# .venv\Scripts\activate.bat
# for Windows PowerShell:
# .venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -e .

# Run pre-commit
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files

# Alternative: run formatter, lint, and type checking
python -m pip install isort black flake8 ruff mypy
isort . ; black . ; flake8 . ; ruff check . --fix ; mypy --install-types .

# Run tests
python -m pip install pytest
pytest

# Build package
python -m pip install build
python -m build
```
