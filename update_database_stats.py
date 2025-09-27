#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to count entries in all DrD database JSON files and update README
"""

import json
import os
import glob
from datetime import datetime

def count_entries_in_json(file_path):
    """Count entries in a JSON database file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if it has 'data' field (table files)
        if isinstance(data, dict) and 'data' in data:
            return len(data['data'])
        # Check if it's an array (some files might be direct arrays)
        elif isinstance(data, list):
            return len(data)
        else:
            return 0
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        return 0

def get_table_name_from_filename(filename):
    """Extract readable table name from filename"""
    # Remove drd_table_ prefix and .json suffix
    name = filename.replace('drd_table_', '').replace('.json', '')
    
    # Map Czech table names to readable English names
    name_mapping = {
        'baziny': 'Swamps',
        'brody': 'Fords', 
        'domy': 'Houses',
        'drd_sklonovani': 'DRD Declensions',
        'drd_tabulky': 'DRD Tables',
        'hory': 'Mountains',
        'hrady': 'Castles',
        'jeskyne': 'Caves',
        'jezera': 'Lakes',
        'jmena': 'Names',
        'jmena_ekvivalence': 'Name Equivalents',
        'ledovce': 'Glaciers',
        'lesy': 'Forests',
        'lode': 'Ships',
        'mesta': 'Cities',
        'more': 'Seas',
        'mysy': 'Capes',
        'ostrovy': 'Islands',
        'plane': 'Plains',
        'pohori': 'Mountain Ranges',
        'pouste': 'Deserts',
        'pridomky': 'Epithets',
        'prijmeni': 'Surnames',
        'prusmyky': 'Passes',
        'reky': 'Rivers',
        'rokle': 'Ravines',
        'soutesky': 'Gorges',
        'stepi': 'Steppes',
        'udelat_jmena': 'Generated Names',
        'udoli': 'Valleys',
        'ulice': 'Streets',
        'utesy': 'Cliffs',
        'zatoky': 'Bays',
        'zeme': 'Lands'
    }
    
    return name_mapping.get(name, name.title())

def generate_database_stats():
    """Generate database statistics"""
    drd_folder = 'DrD-Jmena'
    
    # Find all JSON files except the main database file
    json_files = glob.glob(os.path.join(drd_folder, 'drd_table_*.json'))
    json_files.sort()
    
    stats = []
    total_entries = 0
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        table_name = get_table_name_from_filename(filename)
        entry_count = count_entries_in_json(file_path)
        
        stats.append({
            'filename': filename,
            'table_name': table_name,
            'count': entry_count
        })
        total_entries += entry_count
    
    return stats, total_entries

def update_readme():
    """Update README.md with database statistics"""
    stats, total_entries = generate_database_stats()
    
    # Generate the statistics section
    stats_section = f"""## Database Statistics

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

Total entries across all tables: **{total_entries:,}**

| Table | Entries | Description |
|-------|---------|-------------|
"""
    
    for stat in stats:
        stats_section += f"| {stat['filename']} | {stat['count']:,} | {stat['table_name']} |\n"
    
    # Read current README
    readme_path = 'README.md'
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "# draciHlidka\n\n"
    
    # Find and replace the statistics section
    import re
    
    # Pattern to match the existing statistics section
    stats_pattern = r'## Database Statistics.*?(?=\n##|\n#|$)'
    
    if re.search(stats_pattern, content, re.DOTALL):
        # Replace existing section
        new_content = re.sub(stats_pattern, stats_section.strip(), content, flags=re.DOTALL)
    else:
        # Add new section at the end
        if not content.endswith('\n'):
            content += '\n'
        new_content = content + '\n' + stats_section
    
    # Write updated README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ README.md updated with database statistics")
    print(f"✓ Total entries: {total_entries:,}")
    print(f"✓ Tables processed: {len(stats)}")

def main():
    """Main function"""
    print("Analyzing DrD database files...")
    
    # Check if DrD-Jmena folder exists
    if not os.path.exists('DrD-Jmena'):
        print("Error: DrD-Jmena folder not found!")
        return
    
    try:
        update_readme()
        print("\nDatabase statistics successfully updated in README.md!")
    except Exception as e:
        print(f"Error updating README: {e}")

if __name__ == "__main__":
    main()