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

## Push Python test results to OakCore (local)

Use these commands to generate a JUnit report and push it to a locally running OakCore backend (`http://localhost:8000`).

```bash
# 1) Generate pytest JUnit XML
mkdir -p test-results/python
pytest --junitxml=test-results/python/junit.xml

# 2) Normalize classname values for current OakCore parser behavior
python3 -c "import xml.etree.ElementTree as ET; p='test-results/python/junit.xml'; o='test-results/python/junit.oakcore.xml'; t=ET.parse(p); r=t.getroot(); [tc.set('classname', tc.attrib.get('classname','')[6:]) for tc in r.iter('testcase') if tc.attrib.get('classname','').startswith('tests.')]; t.write(o, encoding='utf-8', xml_declaration=True)"

# 3) Set OakCore connection values
export OAKCORE_URL="http://localhost:8000"
export OAKCORE_PROJECT_ID="550e8400-e29b-11d4-a716-446655440000"
export OAKCORE_EMAIL="demo@neuronoak.com"
export OAKCORE_PASSWORD="xk9Km2pLq7vN4wR"

# 4) Authenticate and upload report
RUN_ID=$(date +%s)
TOKEN=$(curl -s -X POST "$OAKCORE_URL/api/v1/auth/login/access-token" \
  -d "username=$OAKCORE_EMAIL&password=$OAKCORE_PASSWORD" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s -X POST \
  "$OAKCORE_URL/api/v1/projects/$OAKCORE_PROJECT_ID/ci/test-results?ci_run_url=http://localhost/run/$RUN_ID&commit_sha=local-$RUN_ID&repo_url=http://localhost/demo_project" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test-results/python/junit.oakcore.xml"
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
