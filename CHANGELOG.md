# Changelog

Alle nennenswerten Änderungen an dieser Integration werden hier dokumentiert.
Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/);
die Versionsnummerierung folgt grob [Semantic Versioning](https://semver.org/lang/de/)
mit optionaler vierter Build-Komponente.

## [2.6.0.6] — 2026-05-21

### Behoben
- **`formatjs MISSING_VALUE` im Options-Dialog**: die Übersetzung der Options-Seite
  („Kalenderoptionen konfigurieren") enthielt einen `{title}`-Platzhalter, der
  vom bisherigen Stub nie befüllt wurde. Der `description_placeholders`-Wert
  wird jetzt aus dem Instanznamen übergeben.
- **Options-Dialog war ein Platzhalter**: zeigte nur einen ungenutzten
  `show_info`-Schalter. Stattdessen läuft jetzt ein zweistufiger Flow:
  1. Kalender aus den konfigurierten Einträgen wählen
  2. Dessen `config_options`-Schema mit den aktuellen Werten als Default
     bearbeiten und speichern
- **Schlüssel-Mismatch beim Lesen der Optionen**: `sensor.py` las Optionen aus
  `data["plugin_options"]`, der Config-Flow schrieb sie aber als
  `data["calendar_options"]`. Damit hatten alle bisher im Einrichtungs-Assistenten
  gesetzten Plugin-Optionen *keinerlei Wirkung* — die Plugins liefen mit ihren
  Code-Defaults. `sensor.py` liest jetzt primär `calendar_options` und fällt nur
  bei Alt-Einträgen auf `plugin_options` zurück.

### Hinweis
- **Nach dem Update können sich angezeigte Werte ändern**, wenn du im Wizard
  Plugin-Optionen abweichend vom Default eingestellt hattest: bisher wurden
  sie ignoriert, ab v2.6.0.6 greifen sie korrekt. Über *Konfigurieren* am
  Integrations-Eintrag kannst du sie jetzt jederzeit nachjustieren.

## [2.6.0.5] — 2026-05-21

### Behoben
- **500 Internal Server Error** beim Öffnen der Options des Integrations-Eintrags
  unter Home Assistant ≥ 2024.12. Der `OptionsFlowHandler` wies dort `config_entry`
  noch selbst zu — seit HA 2024.12 ist das aber eine read-only property der
  `OptionsFlow`-Basisklasse, was zu
  `AttributeError: property 'config_entry' of 'OptionsFlowHandler' object has no setter`
  führte. Der Konstruktor entfällt komplett, HA versorgt die Klasse jetzt
  automatisch mit `self.config_entry`.

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
