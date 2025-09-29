# JavaScript API pro GitHub Pages

Tento projekt obsahuje jednoduché client-side API v JavaScriptu, které funguje na GitHub Pages.

## Soubory

- `api.js` - Hlavní API logika
- `api-demo.html` - Demo stránka s ukázkami použití API
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

## Spuštění lokálně

1. Otevřete `api-demo.html` ve webovém prohlížeči
2. Nebo spusťte lokální server:
   ```bash
   python3 -m http.server 8000
   ```
   a přejděte na `http://localhost:8000/api-demo.html`

## Poznámky

- Toto je client-side API simulace, ne skutečný server
- Vhodné pro statické stránky a prototypování
- Pro produkční použití zvažte použití skutečného backend API