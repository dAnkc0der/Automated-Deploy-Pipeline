# Automated Deploy Pipeline

An end-to-end CI/CD pipeline that takes a FastAPI service from a `git push`
to a running, health-verified deployment on AWS — no manual steps.

**Stack:** FastAPI · Docker · Ansible · GitHub Actions · AWS (EC2, ECR, RDS, IAM/OIDC)

## How it works

1. Push to `main`
2. **CI** (GitHub Actions) builds a multi-stage Docker image and pushes it to
   ECR, tagged with both the commit SHA and `latest`
3. **CD** (GitHub Actions → Ansible) authenticates to EC2, pulls the new
   image, restarts the container, and verifies `/health` before declaring
   the deploy successful — a failed health check fails the pipeline, it
   does not silently succeed
4. The app serves traffic from EC2, backed by a PostgreSQL database on RDS

## Key design decisions

- **Keyless AWS auth everywhere** — both the EC2 instance (ECR pulls) and
  GitHub Actions (ECR pushes + deploy trigger) authenticate via IAM roles
  and OIDC, not long-lived access keys
- **Secrets never touch the image or git history** — DB credentials are
  encrypted with Ansible Vault, committed safely, and templated onto the
  host only at deploy time
- **RDS over a containerized database** — keeps the app tier stateless and
  independently redeployable; the database's lifecycle isn't tied to the
  EC2 host's
- **Health-gated deploys** — `/health` checks live DB connectivity, and the
  deploy playbook retries against it before considering a release good,
  giving the pipeline a genuine pass/fail signal instead of "the container
  started"

## Project structure

- `app/` — database models, schemas, and API routes
- `main.py` — FastAPI application entry point
- `Dockerfile`, `docker-compose.yml` — container build and local runtime
- `ansible/` — EC2 provisioning (`provision.yml`), host configuration
  (`configure.yml`), and application deployment (`deploy.yml`)
- `.github/workflows/ci.yml` — build/push (CI) and deploy (CD) jobs

## Local setup

1. Copy the environment template and fill in your local DB values:
```sh
   cp .env.example .env
```
2. Install dependencies and run:
```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
```
   API: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

## Docker

```sh
docker build --platform linux/amd64 -t deployment-api .
docker compose up --build
```

## Infrastructure (Ansible)

```sh
cp ansible/inventory.ini.example ansible/inventory.ini
cp ansible/roles/vars/main.yml.example ansible/roles/vars/main.yml
ansible-galaxy collection install -r ansible/collections/requirements.yml

# provision + configure run once, or when infrastructure changes
ansible-playbook -i ansible/inventory.ini ansible/provision.yml
ansible-playbook -i ansible/inventory.ini ansible/configure.yml

# deploy runs on every release (this is what CI/CD automates)
ansible-playbook -i ansible/inventory.ini ansible/deploy.yml \
  --ask-vault-pass
```

Secrets (DB credentials) are stored in `ansible/group_vars/all/vault.yml`,
encrypted with Ansible Vault:
```sh
ansible-vault edit ansible/group_vars/all/vault.yml
```

## CI/CD

GitHub Actions runs on every push to `main` (`.github/workflows/ci.yml`):
- **build-and-push** — builds the Docker image and pushes to ECR
- **deploy** — runs the Ansible deploy playbook against the EC2 host,
  gated on the build succeeding

Both jobs authenticate to AWS via OIDC (no static AWS keys in GitHub
Secrets). SSH access and the Ansible Vault password are stored as GitHub
Secrets and used only transiently on the runner.