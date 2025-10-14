#!/usr/bin/env python3
"""
Script to create proper filters with Czech labels for all JSON database files.
This version creates filters compatible with the JavaScript filtering system.
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
    
    # Exclude name-like columns (main display fields)
    if col_lower in ['nazev', 'jmeno', 'name']:
        return True
    
    # Exclude pad1-7 columns (declension forms)
    if re.match(r'^pad[1-7]$', col_lower):
        return True
    
    return False

def get_czech_label(column_name, table_name):
    """Get Czech label for column name."""
    
    # Special labels by table
    if table_name == 'jmena' or table_name == 'jmena_upraveno':
        labels = {
            'pohlavi': 'Pohlaví',
            'ekvivalence': 'Ekvivalence',
            'clovek': 'Člověk',
            'elf': 'Elf', 
            'trpaslik': 'Trpaslík',
            'hobit': 'Hobit',
            'kuduk': 'Kuduk',
            'barbar': 'Barbar',
            'kroll': 'Kroll',
            'valecnik': 'Válečník',
            'hranicar': 'Hraničář',
            'alchymista': 'Alchymista',
            'kouzelnik': 'Kouzelník',
            'zlodej': 'Zloděj',
            'klerik': 'Klerik',
            'gnom': 'Gnom',
            'obr': 'Obr',
            'pulcik': 'Půlčík'
        }
    elif table_name == 'prijmeni':
        labels = {
            'prijmeni': 'Příjmení',
            'clovek': 'Člověk',
            'elf': 'Elf',
            'trpaslik': 'Trpaslík',
            'hobit': 'Hobit',
            'kuduk': 'Kuduk',
            'barbar': 'Barbar',
            'kroll': 'Kroll',
            'zena': 'Ženská forma',
            'zena2': 'Ženská forma 2',
            'zena3': 'Ženská forma 3',
            'zena4': 'Ženská forma 4',
            'zena5': 'Ženská forma 5',
            'zena6': 'Ženská forma 6',
            'zena7': 'Ženská forma 7'
        }
    elif table_name == 'domy':
        labels = {
            'rod': 'Rod',
            'dum': 'Dům',
            'hospoda': 'Hospoda',
            'obchod': 'Obchod',
            'nevestinec': 'Nevěstinec'
        }
    elif table_name == 'pridomky':
        labels = {
            'pohlavi': 'Pohlaví',
            'pridomek': 'Přídomek'
        }
    elif table_name == 'drd_sklonovani':
        labels = {
            'priorita': 'Priorita',
            'vysl_pad2': 'Výsledek 2. pád',
            'vysl_pad3': 'Výsledek 3. pád',
            'vysl_pad4': 'Výsledek 4. pád',
            'vysl_pad5': 'Výsledek 5. pád',
            'vysl_pad6': 'Výsledek 6. pád',
            'vysl_pad7': 'Výsledek 7. pád',
            'vysl_rod': 'Výsledný rod',
            'zadani_nazev': 'Zadaný název',
            'zadani_rod': 'Zadaný rod'
        }
    elif table_name == 'drd_tabulky':
        labels = {
            'razeni': 'Řazení',
            'slova': 'Slova'
        }
    elif table_name == 'udelat_jmena':
        labels = {
            'ekvivalent': 'Ekvivalent'
        }
    else:
        # Default labels for common columns
        labels = {
            'rod': 'Rod',
            'pohlavi': 'Pohlaví',
            'ekvivalence': 'Ekvivalence'
        }
    
    return labels.get(column_name, column_name.title())

def analyze_column_values(data, column_name):
    """Analyze unique values in a column to determine filter type."""
    if not data or 'data' not in data or not data['data']:
        return None, []
    
    values = set()
    for record in data['data']:
        if isinstance(record, dict) and column_name in record:
            value = record[column_name]
            if value is not None and value != '':
                values.add(str(value))
    
    values = sorted(list(values))
    
    # Determine filter type based on values
    if set(values).issubset({'0', '1'}):
        return 'binary', values
    elif set(values).issubset({'M', 'F', 'N', ''}):
        return 'gender', values
    elif len(values) <= 20:  # Reasonable number for select options
        return 'select', values
    else:
        return None, values  # Too many values, skip filter

def create_gender_filter_options(values):
    """Create options for gender/rod filter."""
    options = []
    for value in values:
        if value == 'M':
            options.append({'value': 'M', 'label': 'Mužský'})
        elif value == 'F':
            options.append({'value': 'F', 'label': 'Ženský'})
        elif value == 'N':
            options.append({'value': 'N', 'label': 'Střední'})
    return options

def create_binary_filter_options():
    """Create options for binary (0/1) filters."""
    return [
        {'value': '1', 'label': 'Ano'},
        {'value': '0', 'label': 'Ne'}
    ]

def create_select_filter_options(values):
    """Create options for general select filters."""
    options = []
    for value in values:
        if value and value.strip():
            options.append({'value': value, 'label': value})
    return options

def create_filters_from_data(data, table_name):
    """Create properly structured filters from data."""
    if not data or 'data' not in data or not data['data']:
        return {}
    
    # Get all columns except excluded ones
    all_columns = set()
    for record in data['data']:
        if isinstance(record, dict):
            all_columns.update(record.keys())
    
    filtered_columns = [col for col in sorted(all_columns) if not should_exclude_column(col)]
    
    if not filtered_columns:
        return {}
    
    filters = {}
    
    # Special handling for names tables (race and class filters)
    if table_name in ['jmena', 'jmena_upraveno']:
        # Gender filter
        if 'pohlavi' in filtered_columns:
            filter_type, values = analyze_column_values(data, 'pohlavi')
            if filter_type == 'gender':
                filters['gender'] = {
                    'field': 'pohlavi',
                    'label': 'Pohlaví',
                    'options': create_gender_filter_options(values)
                }
        
        # Race filters
        race_columns = ['clovek', 'elf', 'trpaslik', 'hobit', 'kuduk', 'barbar', 'kroll', 'gnom', 'obr', 'pulcik']
        race_options = []
        for col in race_columns:
            if col in filtered_columns:
                filter_type, values = analyze_column_values(data, col)
                if filter_type == 'binary' and '1' in values:
                    race_options.append({
                        'value': col,
                        'label': get_czech_label(col, table_name)
                    })
        
        if race_options:
            filters['race'] = {
                'field': 'race',
                'label': 'Rasa',
                'options': race_options
            }
        
        # Class filters
        class_columns = ['valecnik', 'hranicar', 'alchymista', 'kouzelnik', 'zlodej', 'klerik']
        class_options = []
        for col in class_columns:
            if col in filtered_columns:
                filter_type, values = analyze_column_values(data, col)
                if filter_type == 'binary' and '1' in values:
                    class_options.append({
                        'value': col,
                        'label': get_czech_label(col, table_name)
                    })
        
        if class_options:
            filters['class'] = {
                'field': 'class',
                'label': 'Povolání',
                'options': class_options
            }
    
    elif table_name == 'prijmeni':
        # Race filters for surnames
        race_columns = ['clovek', 'elf', 'trpaslik', 'hobit', 'kuduk', 'barbar', 'kroll']
        race_options = []
        for col in race_columns:
            if col in filtered_columns:
                filter_type, values = analyze_column_values(data, col)
                if filter_type == 'binary' and '1' in values:
                    race_options.append({
                        'value': col,
                        'label': get_czech_label(col, table_name)
                    })
        
        if race_options:
            filters['race'] = {
                'field': 'race',
                'label': 'Rasa',
                'options': race_options
            }
    
    elif table_name == 'domy':
        # Special filters for houses
        binary_columns = ['dum', 'hospoda', 'obchod', 'nevestinec']
        for col in binary_columns:
            if col in filtered_columns:
                filter_type, values = analyze_column_values(data, col)
                if filter_type == 'binary' and '1' in values:
                    filters[col] = {
                        'field': col,
                        'label': get_czech_label(col, table_name),
                        'options': create_binary_filter_options()
                    }
        
        # Rod filter
        if 'rod' in filtered_columns:
            filter_type, values = analyze_column_values(data, 'rod')
            if filter_type == 'gender':
                filters['gender'] = {
                    'field': 'rod',
                    'label': 'Rod',
                    'options': create_gender_filter_options(values)
                }
    
    else:
        # Generic filters for other tables
        for col in filtered_columns:
            filter_type, values = analyze_column_values(data, col)
            
            if filter_type == 'gender':
                filters['gender'] = {
                    'field': col,
                    'label': get_czech_label(col, table_name),
                    'options': create_gender_filter_options(values)
                }
            elif filter_type == 'binary' and '1' in values:
                filters[col] = {
                    'field': col,
                    'label': get_czech_label(col, table_name),
                    'options': create_binary_filter_options()
                }
            elif filter_type == 'select' and len(values) <= 10:  # Limit to reasonable number
                filters[col] = {
                    'field': col,
                    'label': get_czech_label(col, table_name),
                    'options': create_select_filter_options(values)
                }
    
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
    
    # Create proper filters
    filters = create_filters_from_data(data, table_name)
    
    if not filters:
        print(f"  ⚠️  No suitable filters found")
        # Still set empty filters structure
        data['filters'] = {}
    else:
        print(f"  Found {len(filters)} filter groups: {list(filters.keys())}")
        data['filters'] = filters
    
    # Set displayField if not present
    if 'displayField' not in data:
        if table_name in ['jmena', 'jmena_upraveno', 'jmena_ekvivalence']:
            data['displayField'] = 'jmeno'
        else:
            data['displayField'] = 'nazev'
    
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