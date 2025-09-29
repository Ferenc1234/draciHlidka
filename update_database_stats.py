#!/usr/bin/env python3
"""
Skript pro aktualizaci statistik databáze DrD.
Analyzuje JSON soubory ve složce docs/DrD-Jmena a vytvoří statistiky.
"""

import json
import os
from collections import defaultdict
from datetime import datetime


class DatabaseStatsUpdater:
    def __init__(self, docs_dir="docs/DrD-Jmena"):
        self.docs_dir = docs_dir
        self.stats = {
            "generated_at": None,
            "total_files": 0,
            "total_records": 0,
            "tables": {},
            "summary": {}
        }
    
    def find_json_files(self):
        """Najde všechny JSON soubory ve složce docs."""
        json_files = []
        
        if not os.path.exists(self.docs_dir):
            print(f"Složka {self.docs_dir} neexistuje!")
            return json_files
        
        for filename in os.listdir(self.docs_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.docs_dir, filename)
                json_files.append(filepath)
        
        return sorted(json_files)
    
    def analyze_json_file(self, filepath):
        """Analyzuje jeden JSON soubor a vrátí statistiky."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            filename = os.path.basename(filepath)
            
            # Základní info o souboru
            file_stats = {
                "filename": filename,
                "size_bytes": os.path.getsize(filepath),
            }
            
            # Rozpoznej typ souboru podle struktury
            if isinstance(data, list):
                # Soubor je pole (např. drd_database.json)
                file_stats.update({
                    "type": "array",
                    "name": filename.replace('.json', '').replace('drd_table_', '').replace('drd_', ''),
                    "database": "drd",
                    "record_count": len(data),
                    "fields": [],
                    "field_count": 0
                })
                
                # Pokud obsahuje objekty, analyzuj první
                if data and isinstance(data[0], dict):
                    sample_record = data[0]
                    file_stats["fields"] = list(sample_record.keys())
                    file_stats["field_count"] = len(sample_record.keys())
                    
            elif isinstance(data, dict):
                # Standardní formát tabulky
                file_stats.update({
                    "type": data.get("type", "table"),
                    "name": data.get("name", filename.replace('.json', '').replace('drd_table_', '').replace('drd_', '')),
                    "database": data.get("database", "drd")
                })
                
                # Počet záznamů
                if "data" in data and isinstance(data["data"], list):
                    file_stats["record_count"] = len(data["data"])
                    
                    # Analyzuj strukturu prvního záznamu
                    if data["data"] and isinstance(data["data"][0], dict):
                        sample_record = data["data"][0]
                        file_stats["fields"] = list(sample_record.keys())
                        file_stats["field_count"] = len(sample_record.keys())
                    else:
                        file_stats["fields"] = []
                        file_stats["field_count"] = 0
                else:
                    file_stats["record_count"] = 0
                    file_stats["fields"] = []
                    file_stats["field_count"] = 0
            else:
                # Neznámý formát
                file_stats.update({
                    "type": "unknown",
                    "name": filename.replace('.json', ''),
                    "database": "unknown",
                    "record_count": 0,
                    "fields": [],
                    "field_count": 0
                })
            
            return file_stats
            
        except Exception as e:
            print(f"Chyba při zpracování souboru {filepath}: {e}")
            return {
                "filename": os.path.basename(filepath),
                "error": str(e),
                "record_count": 0,
                "size_bytes": 0
            }
    
    def generate_stats(self):
        """Vygeneruje kompletní statistiky."""
        print(f"Analyzuji JSON soubory ve složce: {self.docs_dir}")
        
        json_files = self.find_json_files()
        
        if not json_files:
            print("Nebyly nalezeny žádné JSON soubory!")
            return
        
        print(f"Nalezeno {len(json_files)} JSON souborů")
        
        # Základní statistiky
        self.stats["generated_at"] = datetime.now().isoformat()
        self.stats["total_files"] = len(json_files)
        
        # Analyzuj každý soubor
        total_records = 0
        total_size = 0
        table_types = defaultdict(int)
        
        for filepath in json_files:
            print(f"Zpracovávám: {os.path.basename(filepath)}")
            
            file_stats = self.analyze_json_file(filepath)
            table_name = file_stats.get("name", "unknown")
            
            # Uložíme statistiky pro tuto tabulku
            self.stats["tables"][table_name] = file_stats
            
            # Aktualizuj celkové statistiky
            total_records += file_stats.get("record_count", 0)
            total_size += file_stats.get("size_bytes", 0)
            
            if "type" in file_stats:
                table_types[file_stats["type"]] += 1
        
        # Celkové statistiky
        self.stats["total_records"] = total_records
        self.stats["total_size_bytes"] = total_size
        self.stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Souhrnné statistiky
        self.stats["summary"] = {
            "table_types": dict(table_types),
            "largest_table": max(
                self.stats["tables"].items(),
                key=lambda x: x[1].get("record_count", 0),
                default=("none", {"record_count": 0})
            )[0],
            "average_records_per_table": round(total_records / len(json_files), 2) if json_files else 0
        }
    
    def save_stats(self, output_file="database_stats.json"):
        """Uloží statistiky do JSON souboru."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            
            print(f"\nStatistiky uloženy do souboru: {output_file}")
            
        except Exception as e:
            print(f"Chyba při ukládání statistik: {e}")
    
    def print_summary(self):
        """Vypíše shrnutí statistik na konzoli."""
        print("\n" + "="*50)
        print("SHRNUTÍ STATISTIK DATABÁZE")
        print("="*50)
        
        print(f"Datum generování: {self.stats['generated_at']}")
        print(f"Celkem souborů: {self.stats['total_files']}")
        print(f"Celkem záznamů: {self.stats['total_records']:,}")
        print(f"Celková velikost: {self.stats.get('total_size_mb', 0)} MB")
        print(f"Průměr záznamů na tabulku: {self.stats['summary'].get('average_records_per_table', 0)}")
        
        print(f"\nNejvětší tabulka: {self.stats['summary'].get('largest_table', 'N/A')}")
        
        print(f"\nTypy tabulek:")
        for table_type, count in self.stats['summary'].get('table_types', {}).items():
            print(f"  - {table_type}: {count}")
        
        print(f"\nTop 10 největších tabulek:")
        sorted_tables = sorted(
            self.stats["tables"].items(),
            key=lambda x: x[1].get("record_count", 0),
            reverse=True
        )[:10]
        
        for table_name, table_stats in sorted_tables:
            record_count = table_stats.get("record_count", 0)
            size_kb = round(table_stats.get("size_bytes", 0) / 1024, 1)
            print(f"  {table_name}: {record_count:,} záznamů ({size_kb} KB)")


def main():
    """Hlavní funkce skriptu."""
    print("DrD Database Stats Updater")
    print("-" * 30)
    
    # Vytvoř aktualizátor
    updater = DatabaseStatsUpdater()
    
    # Vygeneruj statistiky
    updater.generate_stats()
    
    # Uložíme statistiky
    updater.save_stats("docs/database_stats.json")
    
    # Vypíšeme shrnutí
    updater.print_summary()
    
    print("\nHotovo! ✅")


if __name__ == "__main__":
    main()