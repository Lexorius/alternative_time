# Changelog

Alle nennenswerten Änderungen an dieser Integration werden hier dokumentiert.
Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/);
die Versionsnummerierung folgt grob [Semantic Versioning](https://semver.org/lang/de/)
mit optionaler vierter Build-Komponente.

## [2.6.0.4] — 2026-05-21

### Hinzugefügt
- **Sri Lankan Buddhist Calendar** (`sri_lanka_buddhist.py`) — neuer Kalender mit
  Buddhist Era (BE = CE + 543), den zwölf singhalesischen Poya-Tagen (Duruthu,
  Nawam, Medin, Bak, Vesak, Poson, Esala, Nikini, Binara, Vap, Il, Unduvap)
  inkl. religiöser Bedeutung, Singhalesisch-Tamilischem Neujahr (Aluth
  Avurudda / Puthandu) und singhalesischen Wochentagsnamen. Vollmond-Berechnung
  per Meeus-Algorithmus (Kap. 49) mit periodischen Korrekturen plus
  Mondaufgangs-Regel für die zivile Poya-Datierung — reproduziert alle 11
  offiziell verkündeten Poya-Tage 2023–2026 exakt.
- **Recorder-freundliche Entity-IDs**: Alle neu erzeugten Sensoren bekommen
  jetzt eine stabile entity_id `sensor.alternative_time_<calendar_id>`,
  unabhängig vom in der Config-Flow vergebenen Instanznamen. Damit reicht ein
  einziger Glob `sensor.alternative_time_*` in der Recorder-Konfiguration aus,
  um die komplette Integration aus der History auszuschließen.

### Geändert
- README erweitert um den Abschnitt „Excluding from Recorder / History" mit
  Glob-Beispiel und Upgrade-Hinweis (bestehende Entities behalten ihre
  vorhandenen IDs — `suggested_object_id` greift nur bei der Erst-Registrierung).
- README-Liste der Cultural Calendars um den Sri-lankisch-buddhistischen
  Kalender ergänzt.

### Behoben
- _keine_

## [2.6.0.2] — 2026

### Geändert
- CI-Workflow `validate.yml` aufgeteilt in `hassfest.yml`, `hacs.yml` und
  `python-checks.yml`, sodass jeder Check ein eigenes Status-Badge hat.
- Status-Badges (hassfest, HACS, Python checks) im README-Header ergänzt.

## [2.6.0.1] — 2026

### Geändert
- Alle Plugin-Dateien sind jetzt ruff-clean (`E, F, W, I`, mit `--ignore E501`).
- Bare `except:` in `dtg.py`, `german_rescue_dtg.py`, `mars.py`,
  `hindu_panchang.py`, `japanese_era.py`, `japanese_lunar.py`,
  `stellar_distances.py` durch `except Exception:` ersetzt.
- Tote Variablen in `geez.py`, `japanese_lunar.py`, `lunar_tcl.py`, `maya.py`,
  `solar_system.py`, `star_wars.py` entfernt.
- Duplizierter Dict-Key `"holidays"` in `star_wars.py` aufgelöst.
- Unbenutzter Import `Lunar` aus `chinese_lunar.py` entfernt.
- Einzeilige if/else-Statements in `stellar_distances.py` in mehrzeilige Form.

### Hinzugefügt
- `scripts/bump-version.sh` unterstützt 4-teilige Versionen (`x.y.z.b`) und ein
  neues `build`-Subkommando, das nur die 4. Komponente erhöht.
