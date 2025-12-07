# GLPI Data Service V3 - Scripts

Sync scripts for populating the database from GLPI API.

**Note:** All scripts can be run from **any directory** (project root or scripts/).

## 🔄 Complete Database Rebuild (Recommended)

**Destroys and recreates everything from scratch:**

```bash
# From project root OR from scripts/ folder
python scripts/rebuild_database.py
# OR
cd scripts && python rebuild_database.py
# Type 'REBUILD' to confirm
```

This runs the complete cycle:
1. **DROP** all tables
2. **CREATE** all tables from models
3. **SYNC** all data from GLPI

Total time: ~40 seconds

---

## 🗑️ Database Management (⚠️ DANGER)

### Drop All Tables
```bash
python scripts/drop_tables.py
# Type 'DROP TABLES' to confirm
```

### Create All Tables
```bash
python scripts/create_tables.py
```

### Clean Data Only (keep structure)
```bash
python scripts/clean_database.py
# Type 'DELETE ALL' to confirm
```

---

## 📊 Individual Syncs

```bash
# Metadata only
python scripts/sync_metadata.py

# Tickets only
python scripts/sync_tickets_simple.py
```

---

## 🚀 Full Sync (Keep Existing Structure)

```bash
python scripts/sync_all.py
```

This runs all syncs in correct dependency order:
1. Metadata (Users, Groups, Entities, Categories, Locations, Profiles)
2. Tickets

---

## ✅ Validation

```bash
python validate_database.py
```

Shows record counts and last sync timestamps for all tables.
