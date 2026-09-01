# Automated Deploy Pipeline

A FastAPI service packaged with Docker and deployed through Ansible. The
repository includes GitHub Actions scaffolding for CI and a safe deployment
workflow placeholder.

## Project structure

- `app/` — database models, schemas, and API routes
- `main.py` — FastAPI application entry point
- `Dockerfile` and `docker-compose.yml` — container build and local runtime
- `ansible/` — EC2 provisioning, Docker configuration, and deployment playbooks
- `.github/workflows/` — CI and deployment workflow structure

## Local setup

1. Copy the safe environment template:

   ```sh
   cp .env.example .env
   ```

2. Fill in the database values in `.env`.

3. Create and activate a virtual environment, then install dependencies:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run the API:

   ```sh
   uvicorn main:app --reload
   ```

The API is available at `http://localhost:8000`; interactive documentation is
at `http://localhost:8000/docs`.

## Docker

Copy `.env.example` to `.env`, update the values, then run:

```sh
docker compose up --build
```

## Ansible

Use the checked-in templates to create local deployment files:

```sh
cp ansible/inventory.ini.example ansible/inventory.ini
cp ansible/roles/vars/main.yml.example ansible/roles/vars/main.yml
cp ansible/group_vars/all/vault.yml.example ansible/group_vars/all/vault.yml
ansible-vault encrypt ansible/group_vars/all/vault.yml
```

Install required collections before running playbooks:

```sh
ansible-galaxy collection install -r ansible/collections/requirements.yml
```
