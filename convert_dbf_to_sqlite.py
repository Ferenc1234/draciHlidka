#!/usr/bin/env python3
"""
DBF to SQLite Converter Script

This script converts all .DBF files from the 'jmena' folder into a single SQLite database file (jmena.sqlite).
Each DBF file becomes a separate table named after the file (without the .DBF extension).
All data is stored as TEXT columns to maintain compatibility and avoid data loss.

Requirements:
    - Python 3.x
    - dbfread package: pip install dbfread

Usage:
    python3 convert_dbf_to_sqlite.py

The script will:
1. Scan the 'jmena' directory for all .DBF files
2. Create or overwrite 'jmena.sqlite' database
3. For each DBF file, create a table with the same name (lowercase)
4. Import all records from the DBF file as TEXT fields
5. Display progress and statistics

Author: Auto-generated script
"""

import os
import sqlite3
import sys
from pathlib import Path
from dbfread import DBF


def get_dbf_files(directory):
    """
    Get all DBF files from the specified directory.
    
    Args:
        directory (str): Path to directory containing DBF files
        
    Returns:
        list: List of Path objects for DBF files
    """
    dbf_dir = Path(directory)
    if not dbf_dir.exists():
        raise FileNotFoundError(f"Directory '{directory}' does not exist")
    
    dbf_files = list(dbf_dir.glob("*.DBF"))
    dbf_files.extend(dbf_dir.glob("*.dbf"))  # Also check lowercase
    
    return sorted(dbf_files)


def try_encodings(dbf_path, encodings=['cp1250', 'utf-8', 'iso-8859-2', 'latin-1', 'cp852']):
    """
    Try different encodings to read the DBF file successfully.
    
    Args:
        dbf_path (Path): Path to the DBF file
        encodings (list): List of encodings to try
        
    Returns:
        tuple: (DBF table object, successful encoding) or (None, None)
    """
    for encoding in encodings:
        try:
            table = DBF(str(dbf_path), encoding=encoding)
            # Try to read the first record to verify encoding works
            first_record = next(iter(table), None)
            if first_record is not None:
                return table, encoding
        except Exception as e:
            print(f"  Failed with encoding '{encoding}': {str(e)[:50]}...")
            continue
    
    # If all else fails, try with ignore errors
    for encoding in encodings:
        try:
            table = DBF(str(dbf_path), encoding=encoding, char_decode_errors='ignore')
            first_record = next(iter(table), None)
            if first_record is not None:
                print(f"  WARNING: Using encoding '{encoding}' with error ignore mode")
                return table, f"{encoding} (ignore errors)"
        except Exception as e:
            continue
    
    return None, None


def create_table_from_dbf(cursor, table_name, dbf_table):
    """
    Create a SQLite table based on the DBF table structure.
    All columns are created as TEXT to avoid data type issues.
    
    Args:
        cursor: SQLite cursor object
        table_name (str): Name of the table to create
        dbf_table: DBF table object
    """
    # Drop table if it exists
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    # Get field names from DBF
    field_names = dbf_table.field_names
    
    # Create table with all TEXT columns
    columns = ", ".join([f'"{field}" TEXT' for field in field_names])
    create_sql = f"CREATE TABLE {table_name} ({columns})"
    
    cursor.execute(create_sql)
    
    print(f"    Created table '{table_name}' with {len(field_names)} columns: {', '.join(field_names)}")


def insert_dbf_data(cursor, table_name, dbf_table):
    """
    Insert all data from DBF table into SQLite table.
    
    Args:
        cursor: SQLite cursor object
        table_name (str): Name of the SQLite table
        dbf_table: DBF table object
        
    Returns:
        int: Number of records inserted
    """
    field_names = dbf_table.field_names
    placeholders = ", ".join(["?" for _ in field_names])
    quoted_fields = ", ".join([f'"{field}"' for field in field_names])
    insert_sql = f"INSERT INTO {table_name} ({quoted_fields}) VALUES ({placeholders})"
    
    records_inserted = 0
    
    try:
        for record in dbf_table:
            # Convert all values to strings, handle None values
            values = []
            for field in field_names:
                value = record.get(field)
                if value is None:
                    values.append("")
                else:
                    # Convert to string and handle potential encoding issues
                    try:
                        values.append(str(value))
                    except Exception:
                        values.append("")
            
            cursor.execute(insert_sql, values)
            records_inserted += 1
            
            # Show progress for large tables
            if records_inserted % 1000 == 0:
                print(f"    Inserted {records_inserted} records...")
                
    except Exception as e:
        print(f"    WARNING: Error during data insertion after {records_inserted} records: {str(e)}")
        # Continue with partial data if possible
    
    return records_inserted


def convert_dbf_to_sqlite(dbf_directory="jmena", sqlite_file="jmena.sqlite"):
    """
    Main conversion function that processes all DBF files.
    
    Args:
        dbf_directory (str): Directory containing DBF files
        sqlite_file (str): Output SQLite database file
    """
    print(f"DBF to SQLite Converter")
    print(f"Converting DBF files from '{dbf_directory}' to '{sqlite_file}'")
    print("-" * 60)
    
    try:
        # Get list of DBF files
        dbf_files = get_dbf_files(dbf_directory)
        
        if not dbf_files:
            print(f"No DBF files found in '{dbf_directory}' directory")
            return
        
        print(f"Found {len(dbf_files)} DBF files:")
        for dbf_file in dbf_files:
            print(f"  - {dbf_file.name}")
        print()
        
        # Create or overwrite SQLite database
        if os.path.exists(sqlite_file):
            print(f"Removing existing '{sqlite_file}' database...")
            os.remove(sqlite_file)
        
        # Connect to SQLite database
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        
        total_records = 0
        successful_conversions = 0
        
        # Process each DBF file
        for dbf_file in dbf_files:
            print(f"Processing {dbf_file.name}...")
            
            # Try to open DBF file with different encodings
            dbf_table, encoding = try_encodings(dbf_file)
            
            if dbf_table is None:
                print(f"  ERROR: Could not read {dbf_file.name} with any encoding")
                continue
            
            print(f"  Successfully opened with encoding: {encoding}")
            
            # Generate table name (filename without extension, lowercase)
            table_name = dbf_file.stem.lower()
            
            try:
                # Create SQLite table
                create_table_from_dbf(cursor, table_name, dbf_table)
                
                # Insert data
                records_count = insert_dbf_data(cursor, table_name, dbf_table)
                
                print(f"  Successfully inserted {records_count} records into '{table_name}' table")
                
                total_records += records_count
                successful_conversions += 1
                
            except Exception as e:
                print(f"  ERROR: Failed to process {dbf_file.name}: {str(e)}")
                continue
            
            print()
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        # Print summary
        print("=" * 60)
        print(f"Conversion completed!")
        print(f"Successfully converted {successful_conversions}/{len(dbf_files)} DBF files")
        print(f"Total records imported: {total_records}")
        print(f"SQLite database saved as: {sqlite_file}")
        
        if successful_conversions < len(dbf_files):
            print(f"WARNING: {len(dbf_files) - successful_conversions} files failed to convert")
        
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        sys.exit(1)


def main():
    """Main entry point of the script."""
    # Check if we're in the correct directory (should contain 'jmena' folder)
    if not os.path.exists("jmena"):
        print("ERROR: 'jmena' directory not found!")
        print("Please run this script from the repository root directory.")
        sys.exit(1)
    
    # Run the conversion
    convert_dbf_to_sqlite()


if __name__ == "__main__":
    main()