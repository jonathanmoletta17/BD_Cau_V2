# Designing Advanced MCP Architecture

## Goal Description
Expand the current local MCP Toolbox to include Cloud Native capabilities (GCP) and Code Operations (Git), creating a "Hybrid" agent environment suitable for enterprise usage.
The focus is on **AlloyDB**, **BigQuery**, **Dataplex**, **Cloud Storage**, and **Git**.

## User Review Required
> [!IMPORTANT]
> **Authentication**: All GCP tools require `GOOGLE_APPLICATION_CREDENTIALS` or configured `gcloud` CLI.
> **Cost**: Using BigQuery/AlloyDB implies cloud costs. Tools are designed with "preview" limits to minimize impact.
> **Security**: Write operations (Backup, Deploy, Git Push) will enforce `human_approval_required`.

## Proposed Changes

### New Modules (`mcp_toolbox/`)
#### [NEW] `gcp_ops.py`
- **AlloyDB/PostgreSQL**: `alloydb_read_sql`, `alloydb_backup`
- **BigQuery**: `bq_query` (with dry-run), `bq_preview`
- **Dataplex**: `dataplex_search_assets`
- **Storage**: `gcs_list`, `gcs_read_head`

#### [NEW] `git_ops.py`
- **Git**: `git_status`, `git_diff`, `git_log`, `git_create_branch` (Safe ops)

### Configuration Update
#### [MODIFY] `tools.yaml`
- Integrate new tools with strict JSON schemas.
- Apply `read_only_default` policy to most.
- Apply `human_approval_required` to `git_push`, `alloydb_backup`.

## Verification Plan

### Automated Tests
- `verify_advanced_tools.py`:
    - Check for GCP Credential availability (warn if missing).
    - Dry-run BQ query construction.
    - Check local Git repository access.

### Manual Verification
- User approves `tools.yaml` contents.
- User validates connection strings/secrets if they decide to deploy to actual Cloud.
