# Dashboard Náhodných Uživatelů

## Přehled

Tento projekt je webový dashboard, který vizualizuje data z náhodně generovaných uživatelů z API (https://randomuser.me/api/). Využívá Dash a Plotly pro frontendovou vizualizaci, připojuje se k databázi MySQL pro ukládání dat a zahrnuje službu PHPMyAdmin pro snadnou správu databáze.

## Funkce

- **Dynamická vizualizace dat uživatelů**: Vizualizujte data z náhodně generovaných uživatelů v reálném čase.
- **Integrace databáze**: Používá MySQL pro ukládání dat uživatelů.
- **Administrační rozhraní**: PHPMyAdmin pro snadnou správu databáze.

## Požadavky

Před zahájením se ujistěte, že máte na svém systému nainstalováno následující:
- Docker
- Docker Compose
- Python 3.x

## Struktura projektu

- `app.py`: Hlavní soubor aplikace Dash - zde se nastavuje časový interval aktualizace grafů!
- `data.py`: Obsahuje funkce pro načítání a ukládání dat uživatelů - zde se nastavují parametry pro API! (časový údaj pro dotazování API)
- `Dockerfiles/`: Obsahuje Dockerfiles pro webové a databázové služby.
- `compose.yml`: Soubor Docker Compose pro orchestraci služeb.

## Nastavení a instalace

1. **Klonujte repozitář:**
bash
git clone https://github.com/Marty808s/DashApp

2. **Sestavte a spusťte služby pomocí Docker Compose:**
bash
docker-compose -f compose.yml up --build


3. **Přístup k aplikaci:**
   - Dash aplikace je dostupná na `http://localhost:8050`
   - PHPMyAdmin je dostupný na `http://localhost:9001`

## Použití

Jakmile je aplikace spuštěna, můžete interagovat s Dash rozhraním pro zobrazení a analýzu dat náhodně generovaných uživatelů. PHPMyAdmin vám umožní přímo spravovat databázi prostřednictvím webového rozhraní.