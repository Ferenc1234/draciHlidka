#!/usr/bin/env python3
"""
Script to add ALL columns (except id, nazev/jmeno, and pad1-7) to filters in JSON database files.
"""

import json
import os
import re

def load_json_file(filepath):
    """Load and parse JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_json_file(filepath, data):
    """Save data to JSON file with proper formatting."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

def should_exclude_column(col_name):
    """Check if column should be excluded from filters."""
    col_lower = col_name.lower()
    
    # Exclude id columns
    if col_lower == 'id':
        return True
    
    # Exclude name-like columns
    if col_lower in ['nazev', 'jmeno', 'name']:
        return True
    
    # Exclude pad1-7 columns
    if re.match(r'^pad[1-7]$', col_lower):
        return True
    
    return False

def get_all_columns_from_data(data):
    """Extract all column names from the data records."""
    if not data or 'data' not in data or not data['data']:
        return []
    
    # Get all unique column names from all records
    all_columns = set()
    for record in data['data']:
        if isinstance(record, dict):
            all_columns.update(record.keys())
    
    # Filter out excluded columns
    filtered_columns = [col for col in sorted(all_columns) if not should_exclude_column(col)]
    
    return filtered_columns

def create_filters_from_columns(columns):
    """Create filter structure from column list."""
    if not columns:
        return []
    
    # Create a single filter group with all available columns
    filters = [{
        "name": "Všechny sloupce",
        "filters": columns
    }]
    
    return filters

def update_file_filters(filepath):
    """Update filters in a single JSON file."""
    filename = os.path.basename(filepath)
    table_name = filename.replace('drd_table_', '').replace('.json', '')
    
    print(f"\nAnalyzing {table_name}...")
    
    # Load the file
    data = load_json_file(filepath)
    if not data:
        print(f"  ❌ Failed to load file")
        return False
    
    # Get all columns
    columns = get_all_columns_from_data(data)
    if not columns:
        print(f"  ⚠️  No filterable columns found")
        return False
    
    print(f"  Found columns: {columns}")
    
    # Create new filters
    new_filters = create_filters_from_columns(columns)
    
    # Update the data
    data['filters'] = new_filters
    
    # Save the file
    if save_json_file(filepath, data):
        print(f"  ✅ Updated filters for {table_name}")
        return True
    else:
        print(f"  ❌ Failed to save file")
        return False

def main():
    """Main function to process all JSON files."""
    json_dir = "docs/DrD-Jmena"
    
    if not os.path.exists(json_dir):
        print(f"Directory {json_dir} not found!")
        return
    
    # Find all JSON files
    json_files = []
    for filename in os.listdir(json_dir):
        if filename.endswith('.json') and filename.startswith('drd_table_'):
            json_files.append(os.path.join(json_dir, filename))
    
    if not json_files:
        print("No JSON table files found!")
        return
    
    print(f"Found {len(json_files)} files to process")
    
    updated_count = 0
    for filepath in sorted(json_files):
        if update_file_filters(filepath):
            updated_count += 1
    
    print(f"\n📊 Summary: Updated {updated_count}/{len(json_files)} files")

if __name__ == "__main__":
    main()