#!/bin/bash

# Automatický skript pro aktualizaci statistik DrD databáze
# Spouští Python skript a zobrazuje výsledky

echo "🚀 Spouštím aktualizaci statistik DrD databáze..."
echo "=================================================="

# Změň do správného adresáře
cd "$(dirname "$0")"

# Spusť Python skript
python3 update_database_stats.py

# Kontrola úspěchu
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Statistiky byly úspěšně aktualizovány!"
    echo ""
    echo "📁 Soubory byly vytvořeny/aktualizovány:"
    echo "  - docs/database_stats.json (JSON statistiky)"
    echo "  - docs/database-stats.html (webové rozhraní)"
    echo ""
    echo "🌐 Pro zobrazení statistik otevřete:"
    echo "  - Lokálně: http://localhost:8000/docs/database-stats.html"
    echo "  - GitHub Pages: https://ferenc1234.github.io/draciHlidka/database-stats.html"
    echo ""
else
    echo ""
    echo "❌ Chyba při aktualizaci statistik!"
    echo "   Zkontrolujte chybové hlášky výše."
    exit 1
fi