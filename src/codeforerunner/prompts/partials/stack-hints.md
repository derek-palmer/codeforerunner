# Stack Detection Hints — Partial

## Detection Signals

### JavaScript / TypeScript
- package.json, tsconfig.json, node_modules/
- Frameworks: next.config.* -> Next.js, vite.config.* -> Vite, react in deps -> React

### Python
- pyproject.toml, setup.py, requirements.txt, Pipfile, uv.lock
- Frameworks: fastapi -> FastAPI, flask -> Flask, django -> Django, airflow -> Airflow

### Infrastructure / IaC
- *.tf -> Terraform
- .github/workflows/*.yml -> GitHub Actions
- docker-compose.yml, Dockerfile -> Docker
- kubernetes/, k8s/, *.yaml with kind: -> Kubernetes

### ETL / Data Pipelines
- dags/ -> Airflow
- dbt_project.yml -> dbt
- Prefect, Dagster, Luigi config files

### Go
- go.mod, go.sum; entry: main.go, cmd/

### Rust
- Cargo.toml, Cargo.lock; entry: src/main.rs, src/lib.rs

## Documentation Style by Stack
| Stack             | README style          | Diagram priority            | Key sections                           |
|-------------------|-----------------------|-----------------------------|----------------------------------------|
| React/Next.js     | User-facing + dev     | Component tree, routes      | Setup, env vars, routing, components   |
| Python API        | Developer-first       | Endpoint flow, data model   | Install, endpoints, auth, models       |
| Terraform module  | Ops-focused           | Infrastructure topology     | Inputs, outputs, resources, examples   |
| ETL pipeline      | Data engineer-focused | Data flow, DAG structure    | Sources, transforms, targets, schedule |
| CLI tool          | User-first            | Command flow                | Install, commands, flags, examples     |
| Monorepo          | Package-first         | Package dependency graph    | Packages, shared libs, dev workflow    |

## Monorepo Detection
If the file tree contains multiple package.json, pyproject.toml, or equivalent manifest files
at different directory levels, treat as a monorepo. Document each package independently
and add a top-level dependency graph.
