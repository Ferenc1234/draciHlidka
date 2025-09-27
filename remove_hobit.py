#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to remove 'hobit' field from all records in the names database
"""

import json

def remove_hobit_field():
    """Remove 'hobit' field from all records"""
    
    # Load the modified file
    try:
        with open('DrD-Jmena/drd_table_jmena_upraveno.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Chyba: Soubor 'DrD-Jmena/drd_table_jmena_upraveno.json' nebyl nalezen.")
        return
    except json.JSONDecodeError:
        print("Chyba: Soubor není platný JSON.")
        return
    
    # Count records with 'hobit' field
    hobit_count = 0
    total_records = len(data['data'])
    
    # Remove 'hobit' field from all records
    for record in data['data']:
        if 'hobit' in record:
            del record['hobit']
            hobit_count += 1
    
    # Save the updated data
    with open('DrD-Jmena/drd_table_jmena_upraveno.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Zpracování dokončeno!")
    print(f"📊 Celkem záznamů: {total_records:,}")
    print(f"🗑️ Odstraněno pole 'hobit' z {hobit_count:,} záznamů")
    print(f"💾 Soubor byl aktualizován: DrD-Jmena/drd_table_jmena_upraveno.json")

if __name__ == "__main__":
    remove_hobit_field()