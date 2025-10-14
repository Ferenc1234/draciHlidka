#!/usr/bin/env python3
import json
import os
import glob

def analyze_data_fields(data_list):
    """Analyze data to find binary (0/1) fields that should be filters"""
    if not data_list:
        return {}
    
    # Get all fields from first few items
    all_fields = set()
    for item in data_list[:10]:  # Check first 10 items
        all_fields.update(item.keys())
    
    # Common fields that are not filters
    exclude_fields = {
        'id', 'nazev', 'jmeno', 'rod', 'pohlavi', 'ekvivalence', 
        'pad2', 'pad3', 'pad4', 'pad5', 'pad6', 'pad7', 'slova'
    }
    
    # Find binary fields (contain only "0", "1", or empty values)
    binary_fields = {}
    for field in all_fields:
        if field in exclude_fields:
            continue
            
        values = set()
        for item in data_list[:50]:  # Check more items for binary validation
            if field in item:
                val = str(item[field]).strip()
                if val:
                    values.add(val)
        
        # If field only has 0 and 1 values, it's a binary filter field
        if values.issubset({'0', '1'}):
            binary_fields[field] = values
    
    return binary_fields

def create_filter_config(binary_fields, table_name):
    """Create filter configuration based on binary fields"""
    filters = {}
    
    # Special handling for specific tables
    if table_name in ['jmena', 'prijmeni', 'jmena_upraveno']:
        # For names/surnames, group race and class fields
        race_fields = ['clovek', 'elf', 'trpaslik', 'hobit', 'kuduk', 'barbar', 'kroll', 'gnom', 'pulcik', 'obr']
        class_fields = ['valecnik', 'hranicar', 'alchymista', 'kouzelnik', 'zlodej', 'psionik', 'klerik']
        
        race_options = []
        class_options = []
        
        for field in race_fields:
            if field in binary_fields:
                label_map = {
                    'clovek': 'Člověk',
                    'elf': 'Elf', 
                    'trpaslik': 'Trpaslík',
                    'hobit': 'Půlčík',
                    'kuduk': 'Kudlak',
                    'barbar': 'Barbar',
                    'kroll': 'Kroll',
                    'gnom': 'Gnom',
                    'pulcik': 'Půlčík',
                    'obr': 'Obr'
                }
                race_options.append({
                    "value": field,
                    "label": label_map.get(field, field.capitalize())
                })
        
        for field in class_fields:
            if field in binary_fields:
                label_map = {
                    'valecnik': 'Válečník',
                    'hranicar': 'Hraničář',
                    'alchymista': 'Alchymista',
                    'kouzelnik': 'Kouzelník',
                    'zlodej': 'Zloděj',
                    'psionik': 'Psionik',
                    'klerik': 'Klerik'
                }
                class_options.append({
                    "value": field,
                    "label": label_map.get(field, field.capitalize())
                })
        
        if race_options:
            filters["race"] = {
                "field": "multiple",
                "label": "Rasa",
                "options": race_options
            }
        
        if class_options:
            filters["class"] = {
                "field": "multiple", 
                "label": "Povolání",
                "options": class_options
            }
    
    elif table_name == 'domy':
        # For buildings
        building_fields = ['dum', 'hospoda', 'obchod', 'nevestinec']
        building_options = []
        
        for field in building_fields:
            if field in binary_fields:
                label_map = {
                    'dum': 'Dům',
                    'hospoda': 'Hospoda',
                    'obchod': 'Obchod',
                    'nevestinec': 'Nevěstinec'
                }
                building_options.append({
                    "value": field,
                    "label": label_map.get(field, field.capitalize())
                })
        
        if building_options:
            filters["type"] = {
                "field": "multiple",
                "label": "Typ budovy",
                "options": building_options
            }
    
    else:
        # For other tables, check if there are any binary fields
        if binary_fields:
            # Create generic filters for any binary fields found
            for field in sorted(binary_fields.keys()):
                filters[field] = {
                    "field": field,
                    "label": field.capitalize(),
                    "options": [
                        {"value": "1", "label": "Ano"},
                        {"value": "0", "label": "Ne"}
                    ]
                }
    
    return filters

def fix_table_filters():
    """Fix filters for all table files"""
    table_files = glob.glob('/workspaces/draciHlidka/docs/DrD-Jmena/drd_table_*.json')
    
    print(f"Found {len(table_files)} files to analyze")
    
    for file_path in sorted(table_files):
        filename = os.path.basename(file_path)
        table_name = filename.replace('drd_table_', '').replace('.json', '')
        
        print(f"\nAnalyzing {table_name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'data' not in data or not data['data']:
                print(f"  No data found in {table_name}")
                continue
            
            # Analyze the data structure
            binary_fields = analyze_data_fields(data['data'])
            print(f"  Found binary fields: {list(binary_fields.keys())}")
            
            # Create appropriate filters
            new_filters = create_filter_config(binary_fields, table_name)
            
            if new_filters:
                print(f"  Created {len(new_filters)} filter groups")
                # Update the filters
                data['filters'] = new_filters
                
                # Write back to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                print(f"  ✓ Updated filters for {table_name}")
            else:
                print(f"  No suitable filters found for {table_name}")
                # Set empty filters
                data['filters'] = {}
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
        
        except Exception as e:
            print(f"  ✗ Error processing {table_name}: {e}")

if __name__ == "__main__":
    fix_table_filters()