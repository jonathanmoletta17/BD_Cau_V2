"""
SIS Data Validation Suite - Comprehensive Tests
Validates data integrity, relationships, and quality in SIS schema
"""
import sys
from pathlib import Path
from datetime import datetime
import psycopg2

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core import config, Database
from src.core.glpi_client import GLPIClient
from src.modules.sis.metadata import Entity, Group, ITILCategory, Location

# PostgreSQL connection
DB_CONFIG = {
    'host': config.POSTGRES_HOST,
    'port': config.POSTGRES_PORT,
    'database': config.POSTGRES_DB,
    'user': config.POSTGRES_USER,
    'password': config.POSTGRES_PASSWORD
}


class TestResult:
    """Test result container."""
    def __init__(self, name, status, details=""):
        self.name = name
        self.status = status  # PASS, FAIL, WARN
        self.details = details
    
    def __repr__(self):
        symbol = "✓" if self.status == "PASS" else ("⚠" if self.status == "WARN" else "✗")
        return f"{symbol} {self.name}: {self.details}"


class SISValidator:
    """SIS database validation suite."""
    
    def __init__(self):
        self.results = []
        self.conn = None
        self.session = None
    
    def connect(self):
        """Establish connections."""
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.session = Database.get_session(context="sis")
    
    def close(self):
        """Close connections."""
        if self.conn:
            self.conn.close()
        if self.session:
            self.session.close()
    
    # ========================================================================
    # TEST 1: Schema Structure
    # ========================================================================
    
    def test_schema_exists(self):
        """Validate SIS schema exists."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.schemata 
                WHERE schema_name = 'sis'
            );
        """)
        exists = cursor.fetchone()[0]
        cursor.close()
        
        if exists:
            self.results.append(TestResult("Schema Existence", "PASS", "Schema 'sis' exists"))
        else:
            self.results.append(TestResult("Schema Existence", "FAIL", "Schema 'sis' not found"))
    
    def test_tables_exist(self):
        """Validate all required tables exist."""
        required_tables = [
            'glpi_entities', 'glpi_groups', 'glpi_itilcategories', 
            'glpi_locations', 'tickets'
        ]
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'sis';
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        missing = set(required_tables) - set(existing_tables)
        if not missing:
            self.results.append(TestResult("Table Existence", "PASS", f"{len(required_tables)} tables found"))
        else:
            self.results.append(TestResult("Table Existence", "FAIL", f"Missing: {missing}"))
    
    # ========================================================================
    # TEST 2: Data Integrity
    # ========================================================================
    
    def test_data_counts(self):
        """Validate data was loaded."""
        counts = {}
        cursor = self.conn.cursor()
        
        tables = ['glpi_entities', 'glpi_groups', 'glpi_itilcategories', 'glpi_locations']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM sis.{table};")
            counts[table] = cursor.fetchone()[0]
        
        cursor.close()
        
        total = sum(counts.values())
        if total > 0:
            details = ", ".join([f"{t.split('_')[-1]}: {c}" for t, c in counts.items()])
            self.results.append(TestResult("Data Population", "PASS", f"{total} total records ({details})"))
        else:
            self.results.append(TestResult("Data Population", "FAIL", "No data found in any table"))
    
    def test_no_nulls_in_required_fields(self):
        """Validate required fields are not null."""
        cursor = self.conn.cursor()
        
        # Test entities
        cursor.execute("SELECT COUNT(*) FROM sis.glpi_entities WHERE name IS NULL;")
        null_entities = cursor.fetchone()[0]
        
        # Test groups
        cursor.execute("SELECT COUNT(*) FROM sis.glpi_groups WHERE name IS NULL;")
        null_groups = cursor.fetchone()[0]
        
        # Test categories
        cursor.execute("SELECT COUNT(*) FROM sis.glpi_itilcategories WHERE name IS NULL;")
        null_categories = cursor.fetchone()[0]
        
        cursor.close()
        
        total_nulls = null_entities + null_groups + null_categories
        if total_nulls == 0:
            self.results.append(TestResult("Required Fields", "PASS", "No NULL values in required fields"))
        else:
            self.results.append(TestResult("Required Fields", "FAIL", 
                f"{total_nulls} NULL values found (entities:{null_entities}, groups:{null_groups}, categories:{null_categories})"))
    
    # ========================================================================
    # TEST 3: Data Quality
    # ========================================================================
    
    def test_duplicates(self):
        """Check for duplicate IDs."""
        cursor = self.conn.cursor()
        
        issues = []
        tables = ['glpi_entities', 'glpi_groups', 'glpi_itilcategories', 'glpi_locations']
        
        for table in tables:
            cursor.execute(f"""
                SELECT id, COUNT(*) 
                FROM sis.{table} 
                GROUP BY id 
                HAVING COUNT(*) > 1;
            """)
            dupes = cursor.fetchall()
            if dupes:
                issues.append(f"{table}: {len(dupes)} duplicates")
        
        cursor.close()
        
        if not issues:
            self.results.append(TestResult("Duplicate IDs", "PASS", "No duplicates found"))
        else:
            self.results.append(TestResult("Duplicate IDs", "FAIL", "; ".join(issues)))
    
    def test_timestamps(self):
        """Validate synchronization timestamps."""
        cursor = self.conn.cursor()
        
        # Check if timestamps are recent (within last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sis.glpi_entities 
            WHERE sincronizado_em > NOW() - INTERVAL '24 hours';
        """)
        recent = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sis.glpi_entities;")
        total = cursor.fetchone()[0]
        
        cursor.close()
        
        if total > 0:
            if recent == total:
                self.results.append(TestResult("Sync Timestamps", "PASS", f"All {total} records synced recently"))
            else:
                self.results.append(TestResult("Sync Timestamps", "WARN", 
                    f"Only {recent}/{total} records synced in last 24h"))
        else:
            self.results.append(TestResult("Sync Timestamps", "FAIL", "No data to check"))
    
    # ========================================================================
    # TEST 4: API Comparison
    # ========================================================================
    
    def test_api_vs_db_counts(self):
        """Compare API counts with database counts."""
        try:
            with GLPIClient(
                config.GLPI_SIS_URL,
                config.GLPI_SIS_APP_TOKEN,
                config.GLPI_SIS_USER_TOKEN
            ) as client:
                
                # Get counts from API (sample)
                api_entities = len(client.get_entities())
                api_groups = len(client.get_groups())
                api_categories = len(client.get_itil_categories())
                
                # Get counts from DB
                cursor = self.conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sis.glpi_entities;")
                db_entities = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM sis.glpi_groups;")
                db_groups = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM sis.glpi_itilcategories;")
                db_categories = cursor.fetchone()[0]
                cursor.close()
                
                # Compare
                matches = []
                if api_entities == db_entities:
                    matches.append(f"entities:{db_entities}")
                else:
                    matches.append(f"entities:API={api_entities},DB={db_entities}")
                
                if api_groups == db_groups:
                    matches.append(f"groups:{db_groups}")
                else:
                    matches.append(f"groups:API={api_groups},DB={db_groups}")
                
                if api_categories == db_categories:
                    matches.append(f"categories:{db_categories}")
                else:
                    matches.append(f"categories:API={api_categories},DB={db_categories}")
                
                if api_entities == db_entities and api_groups == db_groups and api_categories == db_categories:
                    self.results.append(TestResult("API vs DB Count", "PASS", ", ".join(matches)))
                else:
                    self.results.append(TestResult("API vs DB Count", "WARN", ", ".join(matches)))
                
        except Exception as e:
            self.results.append(TestResult("API vs DB Count", "FAIL", f"API error: {str(e)[:50]}"))
    
    # ========================================================================
    # REPORT GENERATION
    # ========================================================================
    
    def generate_report(self):
        """Generate comprehensive validation report."""
        print("\n" + "=" * 80)
        print("SIS DATA VALIDATION REPORT")
        print("=" * 80)
        print(f"\nExecuted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tests: {len(self)}")
        
        # Summary
        passed = sum(1 for r in self.results if r.status == "PASS")
        warnings = sum(1 for r in self.results if r.status == "WARN")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        
        print(f"\nResults: {passed} PASS, {warnings} WARN, {failed} FAIL")
        
        # Detailed results
        print("\n" + "-" * 80)
        for result in self.results:
            print(f"  {result}")
        
        print("\n" + "=" * 80)
        
        # Final verdict
        if failed == 0:
            print("✓ VALIDATION SUCCESSFUL - All critical tests passed")
        else:
            print(f"✗ VALIDATION FAILED - {failed} test(s) failed")
        
        print("=" * 80)
        
        return failed == 0
    
    def __len__(self):
        return len(self.results)


def main():
    """Run all validation tests."""
    validator = SISValidator()
    
    try:
        validator.connect()
        
        # Run all tests
        print("Running SIS validation tests...")
        validator.test_schema_exists()
        validator.test_tables_exist()
        validator.test_data_counts()
        validator.test_no_nulls_in_required_fields()
        validator.test_duplicates()
        validator.test_timestamps()
        validator.test_api_vs_db_counts()
        
        # Generate report
        success = validator.generate_report()
        
        validator.close()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n✗ Validation error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
