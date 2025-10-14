#!/usr/bin/env python3
"""
Script to reorganize JSON files with correct structure: metadata first, then data.
"""

import json
import os
import glob

def fix_json_structure(file_path):
    """Fix the JSON structure to have metadata first, then data"""
    table_name = os.path.basename(file_path).replace('drd_table_', '').replace('.json', '')
    print(f"Fixing structure for {table_name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if structure is already correct
        if (isinstance(data, dict) and 'type' in data and 'data' in data and 
            'displayField' in data and 'filters' in data and 
            list(data.keys())[0:5] == ['type', 'name', 'database', 'displayField', 'filters']):
            print(f"  {table_name} already has correct structure")
            return
        
        # If it's a list or has filters at the end, we need to restructure
        if isinstance(data, list):
            # Old format: just array of data
            actual_data = data
            metadata = {}
        elif isinstance(data, dict) and 'data' in data:
            # Extract metadata and data
            actual_data = data.get('data', [])
            metadata = {k: v for k, v in data.items() if k != 'data'}
        else:
            print(f"  {table_name} has unexpected structure, skipping")
            return
        
        # Create the correct structure
        correct_structure = {
            "type": metadata.get("type", "table"),
            "name": metadata.get("name", table_name),
            "database": metadata.get("database", "drd"),
            "displayField": metadata.get("displayField", "nazev" if table_name != "jmena" else "jmeno"),
            "filters": metadata.get("filters", {}),
            "data": actual_data
        }
        
        # If no filters exist, create appropriate ones based on data
        if not correct_structure["filters"] and len(actual_data) > 0:
            sample = actual_data[0]
            filters = {}
            
            # Add gender filter if available
            if 'rod' in sample or 'pohlavi' in sample:
                gender_field = 'pohlavi' if 'pohlavi' in sample else 'rod'
                gender_options = [
                    {"value": "M", "label": "Mužský"},
                    {"value": "F", "label": "Ženský"}
                ]
                if table_name != 'jmena':  # Add neutral for non-name tables
                    gender_options.append({"value": "N", "label": "Střední"})
                
                filters["gender"] = {
                    "field": gender_field,
                    "label": "Rod",
                    "options": gender_options
                }
            
            # Add race filters for tables that have them
            race_fields = ['clovek', 'elf', 'trpaslik', 'hobit', 'kuduk', 'kroll', 'barbar']
            if any(field in sample for field in race_fields):
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
            
            # Add class filters for tables that have them
            class_fields = ['valecnik', 'hranicar', 'alchymista', 'kouzelnik', 'zlodej']
            if any(field in sample for field in class_fields):
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
            
            correct_structure["filters"] = filters
        
        print(f"  Restructuring with {len(correct_structure['filters'])} filters")
        
        # Write the corrected structure
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(correct_structure, f, ensure_ascii=False, indent=4, separators=(',', ': '))
        
        print(f"  Successfully fixed {table_name}")
        
    except Exception as e:
        print(f"  Error fixing {table_name}: {e}")

def main():
    docs_path = "/workspaces/draciHlidka/docs/DrD-Jmena/"
    
    # Get all table files
    pattern = os.path.join(docs_path, "drd_table_*.json")
    files = glob.glob(pattern)
    
    print(f"Found {len(files)} table files to fix\n")
    
    for file_path in sorted(files):
        fix_json_structure(file_path)
        print()

if __name__ == "__main__":
    main()