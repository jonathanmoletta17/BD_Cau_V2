import os
import glob
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(PROJECT_ROOT, 'reports')

def main():
    list_of_files = glob.glob(os.path.join(REPORTS_DIR, 'accuracy_report_*.json'))
    if not list_of_files:
        print('No reports found.')
        return
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Reading: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    output_path = os.path.join(os.path.dirname(latest_file), 'summary_latest.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Total Tickets: {data.get('total_tickets')}\n")
        f.write(f"Skipped: {data.get('skipped')}\n")
        f.write(f"Accuracy Valid: {data.get('accuracy_valid')}%\n")
        f.write(f"Accuracy Total: {data.get('accuracy_total')}%\n")
        
        f.write("\n--- Top Errors ---\n")
        # If not present, compute top errors from confusion_pairs
        top_errors = data.get('top_errors')
        if not top_errors and data.get('confusion_pairs'):
            pairs = sorted(data['confusion_pairs'].items(), key=lambda x: x[1], reverse=True)[:10]
            for pair, count in pairs:
                if '→' in pair:
                    true, pred = pair.split(' → ')
                elif '->' in pair:
                    true, pred = pair.split('->')
                    true, pred = true.strip(), pred.strip()
                else:
                    true, pred = pair, ''
                f.write(f"{count}x: {true} -> {pred}\n")
        else:
            for error in (top_errors or [])[:10]:
                f.write(f"{error['count']}x: {error['true']} -> {error['pred']}\n")
            
        f.write("\n--- Errors by Category ---\n")
        errors_by_cat = sorted(data.get('errors_by_category', {}).items(), key=lambda x: len(x[1]), reverse=True)
        for cat, errors in errors_by_cat[:10]:
            f.write(f"{len(errors)} errors: {cat}\n")
            
    print(f"Summary written to: {output_path}")


if __name__ == "__main__":
    main()
