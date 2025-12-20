import re

def format_table(lines):
    # Parse table lines
    rows = []
    for line in lines:
        # Split by pipe, strip whitespace
        cols = [c.strip() for c in line.strip().split('|')]
        # Remove empty first/last elements if line starts/ends with pipe
        if line.strip().startswith('|'): cols.pop(0)
        if line.strip().endswith('|'): cols.pop()
        rows.append(cols)
    
    if not rows: return lines

    # Calculate max width for each column
    num_cols = len(rows[0])
    col_widths = [0] * num_cols
    
    for row in rows:
        # Normalize row length
        while len(row) < num_cols: row.append("")
        for i, col in enumerate(row):
            # Ignore separator lines like :--- for width calculation (we set min width 3)
            if set(col) <= set(":-"): continue
            col_widths[i] = max(col_widths[i], len(col))
    
    # Add padding
    col_widths = [w + 2 for w in col_widths] # +2 for spaces padding

    formatted_lines = []
    for row in rows:
        formatted_row = "|"
        is_separator = all(set(c) <= set(":-") for c in row)
        
        for i, col in enumerate(row):
            target_width = col_widths[i]
            if is_separator:
                # Reconstruct separator :---:
                base = "-" * (target_width - 2)
                if col.startswith(":") and col.endswith(":"):
                    val = f":{base}:"
                elif col.endswith(":"):
                    val = f"{base}-:"
                elif col.startswith(":"):
                    val = f":-{base}"
                else:
                    val = f"-{base}-"
                formatted_row += val + "|"
            else:
                formatted_row += f" {col.ljust(target_width - 2)} |"
        formatted_lines.append(formatted_row)
    
    return formatted_lines

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().splitlines()

    new_content = []
    table_buffer = []
    in_table = False

    for line in content:
        stripped = line.strip()
        if stripped.startswith('|'):
            in_table = True
            table_buffer.append(line)
        else:
            if in_table:
                # Process collected table
                new_content.extend(format_table(table_buffer))
                table_buffer = []
                in_table = False
            new_content.append(line)
    
    # Flush remaining table if file ends with table
    if in_table:
        new_content.extend(format_table(table_buffer))

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))

if __name__ == "__main__":
    process_file(r"c:\Users\jonathan-moletta\Projetos_Locais\BD_Cau_V2\relatorio_desempenho_2025.md")
    print("Tabelas formatadas com sucesso.")