# Alternative Time Systems – HACS Validation Fixes

Dieses ZIP enthält **nur die geänderten Dateien**, die in das Repository
`Lexorius/alternative_time` übernommen werden müssen, um die HACS- und
hassfest-Validierung zu bestehen.

## Behobene Fehler

### 1. HACS Manifest – `extra keys not allowed @ data['domains']`
- **Datei:** `hacs.json`
- **Fix:** Schlüssel `domains` entfernt (in der HACS-Manifest-Spec nicht erlaubt).

### 2. Translations – `the string should not contain URLs`
- **Dateien:** `strings.json` + alle 12 Sprachen unter `translations/`
- **Fix:** Die GitHub-URL im `disclaimer.description` wurde durch den
  Placeholder `{github_url}` ersetzt. Die URL selbst wird jetzt zur Laufzeit
  über `description_placeholders` aus `config_flow.py` geliefert.

### 3. hassfest – `CONFIG_SCHEMA` Warnung bei `async_setup`
- **Datei:** `custom_components/alternative_time/__init__.py`
- **Fix:** `CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)` ergänzt.
  `async_setup` bleibt für Rückwärtskompatibilität bestehen, gibt aber nur
  `True` zurück – die Integration wird ausschließlich per Config-Entry/UI
  konfiguriert.

### 4. config_flow.py – minimaler Patch
- **Datei:** `custom_components/alternative_time/config_flow.py`
- **Fix:** Neue Konstante `GITHUB_URL` und `description_placeholders={"github_url": GITHUB_URL}`
  in `async_step_disclaimer`. Sonst keine funktionalen Änderungen.

## Übernahme

ZIP entpacken und die Dateien 1:1 in das Repository kopieren – die
Verzeichnisstruktur entspricht bereits dem Repo-Layout:

```
hacs.json
custom_components/
└── alternative_time/
    ├── __init__.py
    ├── config_flow.py
    ├── strings.json
    └── translations/
        ├── de.json
        ├── en.json
        ├── es.json
        ├── fr.json
        ├── it.json
        ├── ja.json
        ├── ko.json
        ├── nl.json
        ├── pl.json
        ├── pt.json
        ├── ru.json
        └── zh.json
```

## Sprachen

Alle 12 unterstützten Sprachen sind enthalten:
en, de, es, fr, it, nl, pl, pt, ru, ja, zh, ko

## Hinweis zu `translations/ps.json`

Im aktuellen Repo existiert eine Datei `translations/ps.json`, die polnische
Inhalte enthält und vermutlich ein Tippfehler (`ps` statt `pl`) ist. Sie wurde
hier **nicht** angefasst – falls gewünscht, kann sie nachträglich aus dem Repo
gelöscht werden, da `pl.json` die korrekte polnische Übersetzung bereitstellt.
