
# JavaScript API a Database Stats pro GitHub Pages

Tento projekt obsahuje jednoduché client-side API v JavaScriptu a systém pro generování statistik databáze DrD.

## Soubory

### API
- `api.js` - Hlavní API logika
- `api-demo.html` - Demo stránka s ukázkami použití API

### Database Stats
- `update_database_stats.py` - Python skript pro generování statistik
- `update-stats.sh` - Automatizační shell skript
- `docs/database_stats.json` - Vygenerované statistiky (JSON)
- `docs/database-stats.html` - Webové rozhraní pro statistiky
- `docs/` - Složka pro GitHub Pages

## Dostupné endpointy

### GET /
Vrací uvítací zprávu s časovým razítkem.

**Odpověď:**
```json
{
  "status": 200,
  "data": {
    "message": "Hello from JavaScript API!",
    "timestamp": "2024-12-19T10:30:00.000Z"
  }
}
```

### GET /data
Vrací ukázková data s položkami.

**Odpověď:**
```json
{
  "status": 200,
  "data": {
    "items": [
      { "id": 1, "name": "Item 1", "value": "Value 1" },
      { "id": 2, "name": "Item 2", "value": "Value 2" },
      { "id": 3, "name": "Item 3", "value": "Value 3" }
    ],
    "count": 3
  }
}
```

### GET /status
Vrací stav API a seznam všech endpointů.

**Odpověď:**
```json
{
  "status": 200,
  "data": {
    "status": "OK",
    "uptime": 1703002200000,
    "endpoints": [
      { "path": "/", "method": "GET", "description": "Get welcome message" },
      { "path": "/data", "method": "GET", "description": "Get sample data" },
      { "path": "/status", "method": "GET", "description": "Get API status" }
    ]
  }
}
```

## Použití

### V HTML stránce
```html
<script src="api.js"></script>
<script>
    const response = api.get('/');
    console.log(response);
</script>
```

### Vytvoření vlastní instance
```javascript
const myAPI = new SimpleAPI();
const data = myAPI.get('/data');
console.log(data);
```

## GitHub Pages

API je dostupné na GitHub Pages na adrese: `https://[username].github.io/[repository]/api-demo.html`

## Database Stats System

### Použití
```bash
# Spuštění aktualizace statistik
./update-stats.sh

# Nebo manuálně
python3 update_database_stats.py
```

### Vlastnosti
- Analyzuje všechny JSON soubory ve složce `docs/DrD-Jmena/`
- Generuje podrobné statistiky o počtu záznamů, velikosti souborů, struktuře
- Vytváří JSON output pro další zpracování
- Webové rozhraní s přehlednými grafy a tabulkami
- Automatické obnovování statistik

### Výstupní soubory
- `docs/database_stats.json` - Kompletní statistiky v JSON formátu
- `docs/database-stats.html` - Interaktivní webové rozhraní

## Spuštění lokálně

1. **API Demo:**
   ```bash
   python3 -m http.server 8000
   ```
   Otevřete `http://localhost:8000/api-demo.html`

2. **Database Stats:**
   ```bash
   ./update-stats.sh
   python3 -m http.server 8000
   ```
   Otevřete `http://localhost:8000/docs/database-stats.html`

## GitHub Pages

Po commitu do main branche budou dostupné:
- API Demo: `https://ferenc1234.github.io/draciHlidka/api-demo.html`
- Database Stats: `https://ferenc1234.github.io/draciHlidka/database-stats.html`

## Poznámky

- API je client-side simulace, vhodné pro statické stránky
- Database Stats analyzuje pouze JSON soubory z docs složky
- Webové rozhraní se automaticky obnovuje každých 5 minut
- Pro produkční použití zvažte použití skutečného backend API