# Claude Instructions für EdSystemChecker

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
- `python/extract.py` - PowerPlay Datenextraktion mit Unicode-Fixes
- `python/create_contested_md.py` - Contested Systems Report mit FAT Target Integration
- `python/create_stronghold_md.py` - Stronghold Status Report
- `python/create_exploited_md.py` - Exploited Status Report
- `python/create_fortified_md.py` - Fortified Status Report
- `python/genreadme.py` - README Template Generator
- `python/download.py` - HTML Download Script

#### Analysiert, aber nicht optimiert:
- `python/generate.py` - Pipeline Automation (kompakt, aber funktional)

#### Projektstruktur-Status:
- **Pipeline-Scripts**: Automatisierte Report-Generierung ✅
- **JSON-Extraktion**: HTML Parsing mit Unicode-Handling ✅
- **Markdown-Reports**: Formatierte Status-Reports ✅
- **Template-System**: README mit dynamischen Inhalten ✅

### PowerPlay-Spezifische Richtlinien

#### 1. Datenintegrität
- Unicode-Handling für Systemnamen priorisieren
- Mathematische Berechnungen gegen Formulas.md validieren
- Natural Decay ≥25% Limit einhalten

#### 2. Report-Standards
- Status-Emojis konsistent verwenden (🟢🟡🟠🔴🔵)
- Dezimalstellen auf 1 Nachkommastelle formatieren
- FAT Target Integration in contested_status.md

#### 3. Pipeline-Automatisierung
- Fehlerbehandlung mit exit codes
- Schritt-für-Schritt Fortschrittsanzeige
- Dateien-Cleanup zwischen Runs

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
- **HTML Parser**: InaraHTMLParser und InaraContestedHTMLParser
- **JSON Generator**: System-Daten Extraktion und Verarbeitung
- **Report Generator**: Markdown-Formatierung und Status-Berechnung
- **Pipeline Logic**: Automatisierung und Fehlerbehandlung

**Für große Dateien (>150 Zeilen):**
1. **Header-Chunk**: Imports, Globals, Config (Zeilen 1-50)
2. **Parser-Methods-Chunk**: HTML-Parsing Logik (Zeilen 51-100)
3. **Data-Processing-Chunk**: JSON-Verarbeitung, Berechnungen (Zeilen 101-150)
4. **Output-Generation-Chunk**: Markdown-Generierung (Zeilen 151+)

### Vermeidung von Token-Verschwendung

❌ Nicht wiederholen:
- Vollständige Pipeline-Analysen wenn nur einzelne Scripts relevant
- Unicode-Handling Details für bereits gefixte Bereiche
- Mathematische Formeln wenn bereits validiert

✅ Fokus auf:
- Neue Report-Features oder Formatierungen
- Pipeline-Optimierungen und Automatisierung
- Datenqualität und Accuracy Verbesserungen

### Projektstruktur (Referenz)

```
EdSystemChecker/
├── python/
│   ├── extract.py              ✅ Optimiert (Unicode + HTML Parsing)
│   ├── download.py             ✅ Optimiert (Multi-URL Download)
│   ├── create_contested_md.py  ✅ Optimiert (FAT Target Integration)
│   ├── create_stronghold_md.py ✅ Optimiert (Status Reports)
│   ├── create_exploited_md.py  ✅ Optimiert (Status Reports)
│   ├── create_fortified_md.py  ✅ Optimiert (Status Reports)
│   ├── genreadme.py            ✅ Optimiert (Template System)
│   └── generate.py             📋 Funktional (Pipeline Automation)
├── json/                       📁 Generated JSON Data
├── html/                       📁 Downloaded HTML Files
├── accquise.conf              🎯 FAT Target Configuration
├── README.tpl                 📝 README Template
├── generate.bat               🔄 Windows Pipeline
├── contested_status.md        📊 Main PowerPlay Report
├── stronghold_status.md       📊 Stronghold Analysis
├── exploited_status.md        📊 Exploited Systems
├── fortified_status.md        📊 Fortified Systems
└── README.md                  📖 Generated Documentation
```

### Spezielle Optimierungsbereiche

#### 1. Unicode & Encoding
- System Namen Unicode-Artifacts bereinigen
- Windows PowerShell Kompatibilität sicherstellen
- UTF-8 Encoding konsistent verwenden

#### 2. Mathematical Accuracy
- Natural Decay Berechnungen validieren
- Progress Percentage Formatierung (1 Dezimalstelle)
- Opposition vs Progress Vergleiche

#### 3. Report Quality
- FAT Target prominente Platzierung
- Quick Summary für strategische Übersicht
- Status-Icons für visuelle Klarheit

#### 4. Pipeline Robustheit
- Error-Handling mit informativen Meldungen
- Schritt-Validierung zwischen Pipeline-Stufen
- Cleanup und Fresh-Data Workflows
