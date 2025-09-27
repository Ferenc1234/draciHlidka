import json

# Načtení původního souboru
try:
    with open('DrD-Jmena/drd_table_jmena.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Chyba: Soubor 'DrD-Jmena/drd_table_jmena.json' nebyl nalezen.")
    exit()
except json.JSONDecodeError:
    print("Chyba: Soubor 'DrD-Jmena/drd_table_jmena.json' není platný JSON.")
    exit()

# Zpracování dat
for jmeno_data in data['data']:
    # Pravidlo pro Půlčíka
    is_hobit = jmeno_data.get('hobit') == '1'
    is_kuduk = jmeno_data.get('kuduk') == '1'
    jmeno_data['pulcik'] = '1' if is_hobit or is_kuduk else '0'

    # Pravidlo pro Klerika
    is_kouzelnik = jmeno_data.get('kouzelnik') == '1'
    jmeno_data['klerik'] = '1' if is_kouzelnik else '0'

    # Pravidlo pro Gnoma
    is_small_race = jmeno_data.get('trpaslik') == '1' or jmeno_data.get('hobit') == '1'
    is_intellectual = jmeno_data.get('alchymista') == '1' or jmeno_data.get('kouzelnik') == '1'
    jmeno_data['gnom'] = '1' if is_small_race and is_intellectual else '0'
    
    # Odstranění starého pole 'kuduk', pokud ho už nepotřebuješ
    # Pokud ho chceš zachovat, tento řádek smaž nebo zakomentuj
    if 'kuduk' in jmeno_data:
        del jmeno_data['kuduk']
    
    # Přemapování Kroll -> Obr
    if 'kroll' in jmeno_data:
        jmeno_data['obr'] = jmeno_data['kroll']
        del jmeno_data['kroll']


# Uložení upravených dat do nového souboru
with open('DrD-Jmena/drd_table_jmena_upraveno.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Zpracování dokončeno! Výsledek byl uložen do 'DrD-Jmena/drd_table_jmena_upraveno.json'.")