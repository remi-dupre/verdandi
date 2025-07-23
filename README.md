# Verdandi

Drawing beautiful configurable dashboard screens for trmnl.

## Developpement

Install pre-commit hook and dependancies :

```shell
$ uv sync --dev
$ pre-commit install
```

This will start the server on port _8000_:

```shell
$ uv run fastapi dev src/verdandi/main.py
```

## Scripts

To (re)generate the documentation of available modules :

```shell
$ uv run docgen
```

## Why the name "Verdandi"?

In Norse mythology Verðandi (Old Norse, meaning possibly "happening" or
"present") is one of the norns. Along with Urðr (Old Norse "fate") and Skuld
(possibly "debt" or "future"), Verðandi makes up a trio of Norns that are
described as deciding the fates (wyrd) of people.
