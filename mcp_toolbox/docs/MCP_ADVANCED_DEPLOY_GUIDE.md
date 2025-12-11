# Deploying Advanced MCP Tools (GCP & Git)

This guide details how to deploy and configure the extended MCP toolbox, including cloud-native capabilities (AlloyDB, BigQuery, Dataplex, Storage) and Git integration.

## 1. Prerequisites

### Environment Variables
Ensure the following variables are set in your `.env` or Docker environment:

```bash
# GCP Credentials (Recommended: Use Workload Identity for Cloud, Service Account Key for Local)
GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
GCP_PROJECT_ID="your-project-id"
GCP_REGION="us-central1"

# AlloyDB (If not using Auth Proxy sidecar)
ALLOYDB_CLUSTER_ID="..."
ALLOYDB_INSTANCE_ID="..."

# Git Configuration (For git_ops.py)
# Ensure the agent container has a valid .gitconfig or minimal user setup
GIT_AUTHOR_NAME="Antigravity Agent"
GIT_AUTHOR_EMAIL="antigravity@example.com"
```

### Python Dependencies
The `gcp_ops.py` module requires specific libraries. Add these to your `requirements.txt` or `pyproject.toml`:

```text
google-cloud-bigquery
google-cloud-storage
google-cloud-datacatalog
google-cloud-alloydb-connector[pg8000]
SQLAlchemy
```

## 2. Security Configuration

### A. Read-Only by Default
The `tools.yaml` is configured to enforce `read_only` policies on most database tools.
- **BigQuery**: Queries are `dry_run=True` by default implies cost estimation only. Real execution requires logic change or explicit overrides (not currently exposed to agent to prevent high costs).
- **Git**: `git_status`, `git_log` are safe. `git_create_branch` requires `human_approval`.

### B. Human Approval
Destructive or costly actions MUST trigger an approval request. This is handled by the `policy: human_approval_required` in `tools.yaml`.
- **Protected Actions:**
  - `alloydb_backup_create`
  - `glpi_trigger_sync`
  - `git_create_branch` (and any future `git_push`)

### C. Secret Management
- **Local:** Use `.env` file (gitignored).
- **Production (Docker/Cloud):** Mount secrets via Docker Swarm Secrets or Kubernetes Secrets. Do NOT hardcode credentials in `tools.yaml` or Python scripts.

## 3. Universal Deployment Strategies

### Option A: Sidecar Container (Recommended)
Deploy the MCP Toolbox as a distinct service in your `docker-compose.yml`.

```yaml
services:
  mcp-toolbox:
    build: ./mcp_toolbox
    volumes:
      - ./:/app/project # Mount project logic for Git ops
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    depends_on:
      - postgres
      - glpi-data-service
```

### Option B: Library / Submodule
Integrate `mcp_toolbox` as a git submodule in specific agent repositories.
1. `git submodule add <repo-url> mcp_toolbox`
2. Configure agent to import from `mcp_toolbox.tools`.

## 4. Verification

Run the automated verification script:
```bash
python mcp_toolbox/verify_advanced.py
```
This script performs:
1. **Git Check:** Reads local repo status to verify file system access.
2. **GCP Dry-Run:** Attempts a cost estimation query on BigQuery (requires creds).

## 5. Troubleshooting
- **Missing GCP Creds:** Ensure the json key file path is correct and accessible by the container.
- **AlloyDB Connection Refused:** Verify if `cloud-sql-proxy` is running or if you are in the same VPC.
- **Git Errors:** If running in Docker, ensure `.git` directory is mounted.
