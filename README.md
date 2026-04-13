# Todo App Demo Project

This repository contains a small but realistic customer-style Todo application for NeuronOak demos.

## Stack

- Python
- Flask
- SQLite
- Pytest

## Features

- Create, edit, delete todos
- Mark todos as done/open
- Filter list by all/open/done
- Persist data in SQLite
- Add optional description and tags

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app src.todo_app run --debug
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Run tests

```bash
pytest
```

## Run frontend tests

```bash
npm install
npm run test:frontend
```

## CI

- `Python Tests` workflow runs `pytest` and uploads `test-results/python/junit.xml` as an artifact.
- `Frontend Tests` workflow runs Jest and uploads `test-results/frontend/junit.xml` as an artifact.

## NeuronOak seed data

The file `neuronoak.seed.json` in the repo root is the single source of truth for demo requirements, tests, issues, and risks.
