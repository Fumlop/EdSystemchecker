# GitHub Copilot Instructions für EdSystemChecker

## Projektkontext
- **Elite Dangerous PowerPlay System Analyzer**
- **Inara HTML Parser & JSON Converter**
- **PowerPlay Cycle Management (Thursday-Thursday)**
- **Natural Decay Calculations**

## Token-Optimierung Guidelines

### Analysestrategie
- **Dateigröße zuerst**: `wc -l` vor detaillierter Analyse
- **Strukturanalyse**: `grep -E "^(class|def|import)"` für Überblick
- **Chunk-basiert**: Dateien >100 Zeilen in 50-75 Zeilen Chunks
- **Delta-fokussiert**: Nur geänderte Bereiche analysieren
- **Einmal analysiert**: Bereits optimierte Bereiche nicht wiederholen

### Code-Optimierung Workflow

#### 1. Struktur-Assessment
```bash
wc -l *.py                           # Dateigröße
grep -E "^(import|from)" *.py        # Import-Analyse
grep -E "^(class|def)" *.py          # Funktions-/Klassen-Struktur
```

#### 2. Import-Optimierung
- Ungenutzte Imports eliminieren
- Redundante/doppelte Imports zusammenführen
- Standard-Library → Third-Party → Local gruppieren

#### 3. Funktionale Chunks
- **Config/Constants**: Globale Variablen strukturieren
- **Helper Functions**: Utility-Methoden optimieren
- **Core Classes**: Methoden einzeln refactoren
- **Main Logic**: Entry-Points vereinfachen

### PowerPlay-spezifische Optimierungen

#### Natural Decay Calculations
- Formel-Validierung gegen `Formulas.md`
- Normalisierung auf 0-1 Range
- State-spezifische Berechnungen (Stronghold/Fortified/Exploited)

#### JSON Output Structure
- `current_cycle_refresh` Flag-Logic
- PowerPlay Cycle Detection (Thursday-based)
- Conditional Fields (nur >25% progress)

#### HTML Parser Optimierung
- InaraHTMLParser Effizienz
- Unicode-Cleaning Strategien
- Regex-Pattern Optimierung

### Anti-Patterns vermeiden

❌ **Token-Verschwendung**:
- Vollständige Code-Dumps ohne Änderungen
- Wiederholte Funktionserklärungen
- Übermäßige Kommentierung offensichtlicher Logik

✅ **Effizienter Fokus**:
- Konkrete `replace_string_in_file` Vorschläge
- Spezifische Bugfixes/Features
- Performance-kritische Bereiche
- PowerPlay-Logik Validierung

### EdSystemChecker-spezifische Patterns

#### Datei-Prioritäten
1. **extract.py**: Core Parser Logic
2. **Formulas.md**: Mathematical Reference
3. **system.status.md**: Report Generation
4. **JSON Outputs**: Data Validation

#### Typische Optimierungsaufgaben
- HTML Parser Robustheit
- PowerPlay Cycle Calculation
- Natural Decay Formula Accuracy
- JSON Schema Consistency
- Unicode/Special Character Handling

### Entwicklungsrichtlinien
- **PowerPlay Expertise**: Thursday 7-11 UTC Cycles
- **Inara HTML Structure**: Tabellen-basierte Extraktion
- **Elite Dangerous Domain**: System States, CP Calculations
- **JSON Schema Evolution**: Rückwärtskompatibilität

## Schnellreferenz Commands

```bash
# Projekt-Status
python extract.py                    # Main Extraction
wc -l extract.py                    # Code-Größe
grep "def " extract.py              # Funktions-Liste

# PowerPlay Cycle Test
python -c "from extract import is_current_powerplay_cycle; print(is_current_powerplay_cycle('2025-07-25T21:07:24.530014'))"

# JSON Validation
jq . json/fortified_systems.json | head -20    # Schema Check
```
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
