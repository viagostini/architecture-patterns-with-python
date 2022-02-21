all-unit-tests:
    @poetry run pytest -v --cov=made --cov-report term-missing:skip-covered made/tests/unit

lint:
    @poetry run flake8 made
    @poetry run mypy made
    @poetry run isort --check made
    @poetry run black --check made
    @poetry run autoflake --check --remove-unused-variables --expand-star-imports --ignore-init-module-imports --recursive made

format:
    @poetry run black made
    @poetry run autoflake --remove-unused-variables --expand-star-imports --ignore-init-module-imports --recursive made