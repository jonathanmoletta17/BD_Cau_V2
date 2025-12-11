# MCP Toolbox Setup for BD_Cau_V2

## Overview
This directory contains the custom MCP (Model Context Protocol) tools implemented to assist in the management, debugging, and operation of the `BD_Cau_V2` project.

## Tool Definitions (`tools.yaml`)
The tools are defined in `tools.yaml` and implemented in Python.

### Database Operations (`db_ops.py`)
- **`db_list_tables(schema='all')`**: Lists tables in `dtic`, `sis`, and `public` schemas.
- **`db_get_schema(table_name)`**: Returns column definitions.
- **`db_read_sql(query)`**: Safely executes SELECT queries (Read-Only).

### GLPI Operations (`glpi_ops.py`)
- **`glpi_trigger_sync(context, sync_type)`**: Executes `scripts/sync.py` inside the `glpi-data-service` container explicitly.
- **`glpi_check_sync()`**: Retrieves recent logs from the data service container.

### Agent Operations (`agent_ops.py`)
- **`agent_simulate_classification(title, description)`**: Injects a python wrapper into the `glpi-agent-classificator-worker` container to run the `SimpleAgent` model on demand, returning the breakdown of classification (Vector vs LLM).

## Requirements
- Python env with `psycopg2` and `requests`.
- Docker containers (`bd_cau_postgres`, `glpi-data-service`, `glpi-agent-classificator-worker`) must be running.

## Verification
Run `python mcp_toolbox/verify_tools.py` to test the tools against the current environment.
