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

### Vermeidung von Token-Verschwendung

❌ Nicht wiederholen:
- Vollständige Datei-Analysen wenn nur Teilbereiche relevant
- Detaillierte Code-Erklärungen für bereits optimierte Bereiche
- Doppelte Funktionsbeschreibungen

✅ Fokus auf:
- Konkrete Änderungsvorschläge
- Spezifische Optimierungspotentiale  
- Neue Funktionalitäten oder Bugfixes
