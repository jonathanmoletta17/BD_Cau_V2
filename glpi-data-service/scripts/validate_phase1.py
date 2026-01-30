#!/usr/bin/env python3
"""
Phase 1 Validation Script
Tests actor sync fix with limited scope before full deployment.

Usage:
    python scripts/validate_phase1.py --context sis --limit 100
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.sync import run_sync

def main():
    parser = argparse.ArgumentParser(description='Validate Phase 1 Fix')
    parser.add_argument('--context', choices=['dtic', 'sis'], default='sis',
                       help='Context to test (default: sis for staging)')
    parser.add_argument('--limit', type=int, default=100,
                       help='Limit tickets to sync (default: 100)')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🧪 PHASE 1 VALIDATION TEST (ADR-001)")
    print("=" * 70)
    print(f"Context: {args.context.upper()}")
    print(f"Limit: {args.limit} tickets")
    print(f"Expected: Actor sync always runs (no skip)")
    print("=" * 70 + "\n")
    
    # Run sync with limit
    run_sync(
        context=args.context,
        sync_type='tickets',
        limit=args.limit,
        incremental=True  # Test the fix in incremental mode
    )
    
    print("\n" + "=" * 70)
    print("✅ VALIDATION COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review logs for 'Actor Sync completed' message")
    print("2. Check consistency metrics (should be >99%)")
    print("3. If successful, proceed to full deployment")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
