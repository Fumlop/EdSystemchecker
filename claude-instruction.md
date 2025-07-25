# Claude Instructions für EliteMeritTracker

## Token-Economy Richtlinien

### Analysestrategie
- **Dateigröße prüfen**: Zuerst `wc -l` oder Zeilenzahl ermitteln
- **Imports analysieren**: Unnötige/redundante Imports identifizieren
- **Einzelne Komponenten**: Methoden/Funktionen/Klassen separat betrachten
- **Dateien >100 Zeilen**: In logische Chunks analysieren (50-75 Zeilen pro Chunk)  
- **Keine redundanten Analysen**: Einmal analysierte Dateien nur bei Änderungen erneut betrachten
- **Fokus auf geänderte Bereiche**: Bei Updates nur modifizierte Sektionen analysieren

### Optimierungs-Workflow

#### 1. Dateigröße & Struktur
- Zeilenzahl ermitteln
- Grobe Struktur erfassen (Imports, Klassen, Funktionen)

#### 2. Import-Analyse
- Ungenutzte Imports identifizieren
- Redundante/doppelte Imports eliminieren
- Import-Reihenfolge optimieren

#### 3. Komponentenweise Analyse
- **Funktionen**: Einzeln analysieren, DRY-Prinzip anwenden
- **Klassen**: Methoden optimieren, Code-Duplikation eliminieren  
- **Globale Variablen**: Strukturieren, unnötige entfernen

#### 4. Code-Optimierung
- Code-Duplikation eliminieren
- Helper-Methoden extrahieren
- Logik vereinfachen

### Datei-Status Tracking

#### Vollständig optimiert:
- `pluginConfig.py` - Kompakt, keine weitere Optimierung nötig
- `pluginUI.py` - Widget-Management optimiert
- `pluginDetailsUI.py` - UI-Logik und Styling abgeschlossen
- `power.py` - JSON-Handling optimiert, DRY-Prinzip angewendet
- `system.py` - StarSystem-Klasse refactored, Code-Duplikation eliminiert
- `report.py` - Discord-Integration optimiert, bessere Fehlerbehandlung, URL-Validierung

#### Analysiert, aber nicht optimiert:
- `load.py` - Plugin Loader (360 Zeilen, große Datei - teilweise optimiert: Imports bereinigt, Update-Funktionen refactored, strategische Logger.info hinzugefügt)

#### Noch nicht analysiert:
- `history.py` - Merit-History
- `log.py` - Logging-Utilities
- `salvage.py` - Salvage-Handling
- `ppcargo.py` - PowerPlay Cargo

### Chunk-Analyse Richtlinien

**Schritt 1: Dateigröße & Überblick**
```bash
wc -l datei.py  # Zeilenzahl
grep -E "^(class|def|import)" datei.py  # Struktur
```

**Schritt 2: Import-Block (Zeilen 1-X)**
- Ungenutzte Imports identifizieren
- Duplikate eliminieren
- Standard-Library vs. Third-Party vs. Local trennen

**Schritt 3: Funktionale Chunks**
- **Globale Variablen**: Initialisierung, Konfiguration
- **Helper-Funktionen**: Utility-Methoden einzeln
- **Hauptklassen**: Methode für Methode
- **Main-Logic**: Event-Handler, Entry-Points

**Für große Dateien (>150 Zeilen):**
1. **Header-Chunk**: Imports, Globals, Init (Zeilen 1-50)
2. **Core-Methods-Chunk**: Hauptfunktionalität (Zeilen 51-100) 
3. **Utility-Chunk**: Helper-Methoden, JSON-Handling (Zeilen 101+)
4. **UI-Chunk**: GUI-Komponenten separat betrachten

### Vermeidung von Token-Verschwendung

❌ Nicht wiederholen:
- Vollständige Datei-Analysen wenn nur Teilbereiche relevant
- Detaillierte Code-Erklärungen für bereits optimierte Bereiche
- Doppelte Funktionsbeschreibungen

✅ Fokus auf:
- Konkrete Änderungsvorschläge
- Spezifische Optimierungspotentiale  
- Neue Funktionalitäten oder Bugfixes

### Projektstruktur (Referenz)

```
EliteMeritTracker/
├── pluginConfig.py      ✅ Optimiert
├── pluginUI.py          ✅ Optimiert  
├── pluginDetailsUI.py   ✅ Optimiert
├── power.py             ✅ Optimiert
├── system.py            ✅ Optimiert
├── load.py              📋 Teiloptimiert
├── report.py            ⏳ Pending
├── history.py           ⏳ Pending
├── log.py               ⏳ Pending
├── salvage.py           ⏳ Pending
├── ppcargo.py           ⏳ Pending
└── assets/              📁 Assets
```

### Nächste Optimierungskandidaten

1. **load.py** - Plugin-Initialisierung  
2. **report.py** - Discord-Integration
3. **history.py** - Merit-History Management
