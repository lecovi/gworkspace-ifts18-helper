# IFTS18 Google Workspace Helper

IFTS18's Google Workspace Helper is for interacting with the Google Workspace Admin
Console API.

## Installation

```bash
poetry install
``` 

## Test with Jupyter Notebook

```bash
poetry run jupyter lab
```

Make sure you have a proper Credentials file in the `credentials` directory.

# Usage

1. Generate a CSV with the following information:
    - N°
    - APELLIDO
    - NOMBRE
    - DNI
    - MAIL
2. Execute `poetry run python gwi.py --csv CSV_PATH --credentials CREDENTIALS_JSON_PATH`
to generate students email address accounts.
