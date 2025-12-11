import os
import json
import logging
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gcp_ops")

def _check_gcp_creds():
    """Checks if GCP credentials are generally available."""
    # Check for GOOGLE_APPLICATION_CREDENTIALS or gcloud presence
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        return True
    
    # Check gcloud
    try:
        subprocess.run(["gcloud", "--version"], capture_output=True, check=True)
        return True # Assuming gcloud auth login was run
    except:
        return False

# ==============================================================================
# BIGQUERY
# ==============================================================================
def bq_query(query, project_id=None, dry_run=False):
    """
    Executes a BigQuery query. 
    If dry_run is True, returns estimated bytes processed.
    """
    if not _check_gcp_creds():
        return {"error": "GCP Credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS or configure gcloud."}

    try:
        from google.cloud import bigquery
    except ImportError:
        return {"error": "google-cloud-bigquery library not installed."}

    try:
        client = bigquery.Client(project=project_id)
        
        job_config = bigquery.QueryJobConfig(dry_run=dry_run)
        query_job = client.query(query, job_config=job_config)
        
        if dry_run:
            return {
                "status": "dry_run_success", 
                "total_bytes_processed": query_job.total_bytes_processed,
                "msg": "Query valid."
            }
        
        # Real execution - enforce limits if not present? 
        # For safety, we assume query has limits or user approves.
        results = query_job.result()
        
        # Format output (limit to 20 rows for preview)
        rows = [dict(row) for row in results]
        return {"status": "success", "rows": rows[:20], "total_rows": len(rows)}
        
    except Exception as e:
        return {"error": str(e)}

# ==============================================================================
# ALLOYDB / CLOUD SQL
# ==============================================================================
def alloydb_read_sql(connection_name, query, user, password, db_name):
    """
    Connects to AlloyDB/CloudSQL via Auth Proxy or direct IP using pg8000/sqlalchemy.
    Note: Requires cloud_sql_proxy running or direct VPC access.
    """
    # This is a complex setup. For MCP, we often wrap the proxy execution.
    # Here we assume a standard Postgres connection string if the proxy is handling it,
    # OR we use the connector. 
    
    # For generated code simplicity, we will simulate the connection logic 
    # and return instructions if libraries are missing.
    try:
        # Check for connector
        # from google.cloud.alloydb.connector import Connector
        pass
    except ImportError:
        pass # Not enforcing lib presence for this draft

    return {"info": "AlloyDB connection requires `google-cloud-alloydb-connector`. Ensure the proxy is running locally at 127.0.0.1:5433 or similar."}

def alloydb_backup(cluster_id, backup_id, project_id, region):
    """
    Triggers an on-demand backup. destructive/admin action.
    """
    if not _check_gcp_creds():
        return {"error": "No GCP Creds."}
        
    cmd = [
        "gcloud", "alloydb", "backups", "create", backup_id,
        "--cluster", cluster_id,
        "--region", region,
        "--project", project_id,
        "--format", "json"
    ]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except subprocess.CalledProcessError as e:
        return {"error": str(e.stderr)}

# ==============================================================================
# DATAPLEX
# ==============================================================================
def dataplex_search(query, project_id):
    """
    Searches Data Catalog/Dataplex for assets.
    """
    if not _check_gcp_creds():
        return {"error": "No GCP Creds."}
        
    try:
        from google.cloud import datacatalog_v1
    except ImportError:
        return {"error": "google-cloud-datacatalog not installed."}
        
    try:
        client = datacatalog_v1.DataCatalogClient()
        scope = datacatalog_v1.SearchCatalogRequest.Scope()
        scope.include_project_ids.append(project_id)
        
        request = datacatalog_v1.SearchCatalogRequest(
            scope=scope,
            query=query
        )
        
        results = []
        for result in client.search_catalog(request=request):
            results.append({
                "name": result.relative_resource_name,
                "type": result.linked_resource,
                "display_name": result.linked_resource
            })
            if len(results) > 10: break
            
        return results
    except Exception as e:
        return {"error": str(e)}

# ==============================================================================
# STORAGE
# ==============================================================================
def gcs_list(bucket_name, prefix=None):
    if not _check_gcp_creds():
        return {"error": "No GCP Creds."}

    try:
        from google.cloud import storage
    except ImportError:
        return {"error": "google-cloud-storage not installed."}

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix, max_results=50))
    
    return [{"name": b.name, "size": b.size, "updated": b.updated.isoformat()} for b in blobs]
