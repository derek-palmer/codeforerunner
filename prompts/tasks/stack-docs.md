# Task: Generate Stack Documentation

Generates stack-specific developer documentation.
Template selected based on detected stack from scan result.

## Input
- Scan result
- Key module files for the target stack
- Config files relevant to the stack

## Template: Python Application / API
1. Environment Setup: Python version, virtualenv/uv/poetry, dependency install
2. Application Structure: modules, responsibilities, how they connect
3. Database: models, migrations, connection config
4. Configuration: settings pattern, env vars
5. Running Locally: exact commands
6. Running Tests: pytest commands, fixtures overview

## Template: JavaScript / TypeScript Application
1. Environment Setup: Node version, package manager, install
2. Application Structure: src layout, key directories
3. Environment Variables: .env keys and what they control
4. Dev Server: how to run, port, hot reload
5. Build: command, output dir, what gets produced
6. Testing: test runner, how to run, coverage

## Template: Terraform / IaC
1. Overview: what infrastructure this provisions
2. Prerequisites: Terraform version, provider auth
3. Inputs: full table (name, type, required, default, description)
4. Outputs: exported values
5. Resources Provisioned: resource types and purpose
6. Usage: terraform init, plan, apply with required var flags
7. State: where state is stored

## Template: ETL Pipeline
1. Pipeline Overview: source(s), transforms, destination(s)
2. Scheduler / Orchestrator: how to trigger
3. Data Sources: connection requirements, credentials
4. Transformation Logic: key transforms, business rules
5. Data Destinations: output format, target system
6. Configuration: all config vars
7. Running Locally: how to test a pipeline run
8. Monitoring: how to observe pipeline health

## Output
<!-- output: docs/stack.md -->
