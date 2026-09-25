# Changelog

Alle nennenswerten Änderungen an dieser Integration werden hier dokumentiert.
Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/);
die Versionsnummerierung folgt grob [Semantic Versioning](https://semver.org/lang/de/)
mit optionaler vierter Build-Komponente.

## [2.6.1] — 2026-09-26

Laufzeit-Korrekturen aus dem Code-Review. Anders als 2.6.0.7 ändert dieses
Release sichtbares Verhalten — siehe „Hinweis" unten.

### Behoben
- **Jede Entity wurde doppelt aktualisiert.** `should_poll` gab hart `True`
  zurück; das spätere `_attr_should_poll = False` war dadurch wirkungslos.
  HA pollte jede Entity zusätzlich alle 30 s (Sensor-Default) neben dem
  eigenen Timer — Stundenkalender rechneten alle 30 s neu, und bei den
  Plugins mit synchronem `update()` konnten beide Läufe gleichzeitig in zwei
  Executor-Threads auf derselben Instanz laufen. `should_poll` ist jetzt
  `False`; der Timer ist die einzige Quelle. Zusätzlich überspringt der Timer
  einen Tick, solange der vorherige noch läuft (relevant bei `ut1`, dessen
  10-s-Timeout länger ist als sein 1-s-Intervall).
- **Optionsänderungen griffen erst nach Neustart.** Es war kein
  `update_listener` registriert; der 2.6.0.6-Options-Dialog speicherte also
  korrekt, ohne dass etwas passierte. Jetzt lädt HA den Eintrag nach dem
  Speichern automatisch neu. Der Options-Flow reicht `entry.options`
  unverändert durch, damit kein zweiter Reload ausgelöst wird.
- **Fehlgeschlagene Updates waren unsichtbar.** Exceptions aus `update()`
  wurden nur auf DEBUG geloggt; der State blieb stumm stehen. Jetzt: erster
  Fehler einer Serie auf WARNING (Traceback auf DEBUG), Folgefehler auf DEBUG,
  Erholung auf INFO. Nach 3 aufeinanderfolgenden Fehlern wird die Entity als
  **nicht verfügbar** markiert, beim nächsten Erfolg wieder verfügbar.
- **`ut1` konnte die IERS-API fluten.** Bei Ausfall der API versuchte das
  Plugin jede Sekunde erneut (mit je 10 s Timeout, serialisiert über den
  Lock) und schrieb jedes Mal eine WARNING. Jetzt: HA-weite geteilte
  `aiohttp`-Session statt einer neuen Session pro Aufruf, exponentielles
  Backoff 60 s → 120 s → … → 3600 s (Cap), WARNING nur beim ersten Fehler
  einer Serie und einmal pro Stunde am Cap, INFO bei Erholung.
- `_CONFIG_ENTRIES` in `sensor.py` wurde nie geleert — entfernte Einträge
  blieben bis zum Prozessende referenziert. Wird beim Unload jetzt bereinigt.
- `__init__.py` fing Fehler beim Platform-Setup mit einem breiten `except`
  und gab `False` zurück — der Eintrag erschien als „geladen" ohne Entities,
  die Ursache war nur im Log zu ahnen. Fehler propagieren jetzt an HA.

### Entfernt
- `async_reload_entry` in `__init__.py`: rief Unload und Setup direkt auf
  (am HA-Zustandsautomaten vorbei) und hatte keinen Aufrufer.

### Hinweis
- **Entities können jetzt „nicht verfügbar" werden**, wenn ein Plugin
  dreimal hintereinander scheitert — bisher zeigten sie stattdessen den
  letzten alten Wert. Wer Automationen auf diese Sensoren hat, sollte das
  wissen; die Ursache steht ab dem ersten Fehler als WARNING im Log.
- **Nach dem Speichern von Optionen wird der Eintrag neu geladen** — die
  Entities verschwinden dabei für einen Moment und kommen zurück.
- Stundenkalender ändern `last_updated` jetzt tatsächlich nur stündlich,
  nicht mehr alle 30 s.
- Die sekündlichen `Updated …`-DEBUG-Zeilen der 1-s-Plugins sind unverändert;
  sie erscheinen nur mit `logger: custom_components.alternative_time: debug`
  in der `configuration.yaml`. Wer das aus einer früheren Fehlersuche noch
  aktiv hat, sollte es auf `info` zurücksetzen.

## [2.6.0.7] — 2026-09-26

Hotfix-Release nach einem vollständigen Code-Review. Nur isolierte Korrekturen,
kein geändertes Laufzeitverhalten außer den unten genannten Punkten.

### Behoben
- **Drei Kalender erzeugten nie einen Sensor:** `julian_date`, `minguo_taiwan`
  und `suriyakati_thai` waren im Assistenten auswählbar, wurden beim Setup aber
  kommentarlos übersprungen. Ursache: Discovery liest die `id` aus der Datei,
  das Setup importierte anschließend *nach dieser id* (`.calendars.suriyakati_thai`),
  die Datei heißt aber `suriyakati.py`. Discovery merkt sich jetzt den
  Dateinamen je id (`_CALENDAR_MODULE_NAMES`), Setup importiert darüber.
  **Wer einen der drei Kalender konfiguriert hatte, bekommt nach dem Update
  erstmals den Sensor.**
- **`sensor.alternative_time_*` funktionierte nicht** (eingeführt in 2.6.0.4):
  `_attr_suggested_object_id` gibt es in Home Assistant nicht — `Entity` hat
  nur eine berechnete Property. Die stabile entity_id kommt jetzt aus einer
  überschriebenen `suggested_object_id`-Property in `AlternativeTimeSensorBase`.
  Gilt weiterhin nur für *neu* registrierte Entities.
- **Optionen von `dtg`, `german_rescue_dtg` und `julian_date` erschienen nie im
  Assistenten:** die Plugins legten sie unter `plugin_options` statt
  `config_options` ab. Umbenannt. Dabei zwei kaputte Selects repariert:
  `dtg.iana_timezone` hatte statt einer Optionsliste den String
  `"iana_timezone_options"` (wäre als 22 Einzelbuchstaben gerendert worden)
  und ist jetzt ein Freitextfeld; `german_rescue_dtg.month_language` hatte
  ein `{wert: {sprache: label}}`-Dict statt der `[{value, label}]`-Liste.
- **`test_debug.py` wurde als echter Kalender ausgeliefert** (Kategorie
  „technical", 30-s-Intervall, loggt jeden Event auf WARNING, zwei Listen
  wachsen unbegrenzt). Discovery überspringt jetzt `test_*.py`; `build.sh`
  und `release.yml` nehmen `test_*.py`, `template.py.example` und
  `calendars/README.md` nicht mehr ins ZIP.
- **`tzlocal` fehlte in `manifest.json`**, obwohl `hindu_panchang`,
  `japanese_era` und `japanese_lunar` es für die Option „lokale Zeitzone"
  importieren — ohne Paket fiel die Option still auf UTC zurück.

### Geändert
- `hacs.json`: `"homeassistant": "2024.12.0"` als Mindestversion. Der
  OptionsFlow-Fix aus 2.6.0.5 setzt das voraus; ältere Installationen hätten
  das Update angenommen und wären gebrochen.

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
