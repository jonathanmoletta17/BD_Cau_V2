# Maintenance Log

## 2025-12-06 — Consolidation: Remove `glpi-agent-classificator`
- Decision: Consolidate `context-validation` as the primary GLPI DTIC ticket classifier.
- Rationale:
  - Alternate project stalled; keyword-only classifier inferior to embedding-based approach.
  - Missing module dependency (`classifier/text.py`) indicates incomplete state.
  - Redundant features (mass categorize, replication) overlap with `context-validation` (`deploy_to_test.py`, GLPI client).
  - External docs referencing non-existent scripts in `context-validation/tools` are outdated.
- Action:
  - Remove directory `crawl4ai/glpi-agent-classificator/`.
  - Retention: No critical artifacts required; category mappings are available via API in `glpi_agent.glpi_client`.
- Validation:
  - Run `tools/evaluate_accuracy.py` and `tools/read_latest_report.py` to confirm integrity post-cleanup.
- Rollback:
  - Directory can be restored from VCS/history if needed. No data-only artifacts required for current pipeline.

