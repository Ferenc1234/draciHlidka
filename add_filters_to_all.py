#!/usr/bin/env python3
"""
Script to add appropriate filter metadata to all database JSON files.
"""

import json
import os
import glob

def get_sample_record(data):
    """Get a sample record to analyze available fields"""
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    elif isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
        return data['data'][0]
    return {}

def has_race_fields(sample_record):
    """Check if the record has race-related fields"""
    race_fields = ['clovek', 'elf', 'trpaslik', 'hobit', 'kuduk', 'kroll', 'barbar']
    return any(field in sample_record for field in race_fields)

def has_class_fields(sample_record):
    """Check if the record has class-related fields"""
    class_fields = ['valecnik', 'hranicar', 'alchymista', 'kouzelnik', 'zlodej']
    return any(field in sample_record for field in class_fields)

def has_gender_field(sample_record):
    """Check if the record has gender-related fields"""
    return 'rod' in sample_record or 'pohlavi' in sample_record

def create_filters_config(sample_record, table_name):
    """Create appropriate filters config based on available fields"""
    filters = {}
    
    # Add gender filter if available
    if has_gender_field(sample_record):
        gender_field = 'pohlavi' if 'pohlavi' in sample_record else 'rod'
        
        # For names table, only M/F options
        if table_name == 'jmena':
            gender_options = [
                {"value": "M", "label": "Mužský"},
                {"value": "F", "label": "Ženský"}
            ]
        else:
            # For other tables, include neutral gender
            gender_options = [
                {"value": "M", "label": "Mužský"},
                {"value": "F", "label": "Ženský"},
                {"value": "N", "label": "Střední"}
            ]
            
        filters["gender"] = {
            "field": gender_field,
            "label": "Rod",
            "options": gender_options
        }
    
    # Add race filter if available
    if has_race_fields(sample_record):
        filters["race"] = {
            "field": "race",
            "label": "Rasa",
            "options": [
                {"value": "clovek", "label": "Člověk"},
                {"value": "elf", "label": "Elf"},
                {"value": "trpaslik", "label": "Trpaslík"},
                {"value": "hobit", "label": "Půlčík"},
                {"value": "kuduk", "label": "Kuduk"},
                {"value": "kroll", "label": "Kroll"},
                {"value": "barbar", "label": "Barbar"}
            ]
        }
    
    # Add class filter if available
    if has_class_fields(sample_record):
        filters["class"] = {
            "field": "class",
            "label": "Povolání",
            "options": [
                {"value": "valecnik", "label": "Válečník"},
                {"value": "hranicar", "label": "Hraničář"},
                {"value": "alchymista", "label": "Alchymista"},
                {"value": "kouzelnik", "label": "Kouzelník"},
                {"value": "zlodej", "label": "Zloděj"}
            ]
        }
    
    return filters

def get_display_field(table_name, sample_record):
    """Determine the appropriate display field for the table"""
    if table_name == 'jmena':
        return 'jmeno'
    elif table_name == 'prijmeni':
        return 'prijmeni'
    elif 'nazev' in sample_record:
        return 'nazev'
    else:
        return 'nazev'  # fallback

def update_table_file(file_path):
    """Update a single table file with metadata"""
    table_name = os.path.basename(file_path).replace('drd_table_', '').replace('.json', '')
    print(f"Processing {table_name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Skip if already has filters (recently updated files)
        if 'filters' in data:
            print(f"  {table_name} already has filters, skipping")
            return
        
        # Get sample record to analyze structure
        sample_record = get_sample_record(data)
        if not sample_record:
            print(f"  {table_name} has no data, skipping")
            return
        
        # Create appropriate filters
        filters = create_filters_config(sample_record, table_name)
        display_field = get_display_field(table_name, sample_record)
        
        # Add metadata to the data structure
        if 'type' not in data:
            data['type'] = 'table'
        if 'name' not in data:
            data['name'] = table_name
        if 'database' not in data:
            data['database'] = 'drd'
        
        data['displayField'] = display_field
        data['filters'] = filters
        
        print(f"  Added {len(filters)} filters: {list(filters.keys())}")
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        
        print(f"  Successfully updated {table_name}")
        
    except Exception as e:
        print(f"  Error updating {table_name}: {e}")

def main():
    docs_path = "/workspaces/draciHlidka/docs/DrD-Jmena/"
    
    # Get all table files
    pattern = os.path.join(docs_path, "drd_table_*.json")
    files = glob.glob(pattern)
    
    print(f"Found {len(files)} table files to process\n")
    
    for file_path in sorted(files):
        update_table_file(file_path)
        print()

if __name__ == "__main__":
    main()