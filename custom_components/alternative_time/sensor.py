"""Sensor platform for Alternative Time Systems - PARTIAL FILE WITH KEY FIXES."""
# HINWEIS: Dies ist nur ein Ausschnitt der wichtigsten Änderungen in sensor.py
# Die vollständige Datei ist zu groß für ein Artefakt

# ... [Imports und andere Teile bleiben unverändert] ...

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time Systems sensors from a config entry."""
    
    # Store config entry for sensor access
    entry_id = config_entry.entry_id
    _CONFIG_ENTRIES[entry_id] = config_entry
    
    # Get selected calendars from config
    selected_calendars = config_entry.data.get("calendars", [])
    name = config_entry.data.get("name", "Alternative Time")
    
    # FIX: Try both "plugin_options" and "calendar_options" for compatibility
    plugin_options = config_entry.data.get("plugin_options", {})
    if not plugin_options:
        # Fallback to old key name for backward compatibility
        plugin_options = config_entry.data.get("calendar_options", {})
        if plugin_options:
            _LOGGER.info("Found options under 'calendar_options' (legacy), using them")
    
    _LOGGER.info(f"=== Setting up Alternative Time '{name}' ===")
    _LOGGER.debug(f"Config Entry ID: {entry_id[:8]}...")
    _LOGGER.debug(f"Selected calendars: {selected_calendars}")
    _LOGGER.info(f"Plugin options available: {list(plugin_options.keys())}")
    for cal_id, opts in plugin_options.items():
        _LOGGER.debug(f"  {cal_id}: {opts}")
    
    # ... [Rest der Funktion bleibt unverändert] ...


class AlternativeTimeSensorBase(SensorEntity):
    """Base class for Alternative Time System sensors."""

    # ... [Andere Methoden bleiben unverändert] ...

    def get_plugin_options(self) -> Dict[str, Any]:
        """Get plugin options for this sensor with detailed debugging."""
        # Basis-Debug nur wenn wirklich ein Problem besteht
        if not self._config_entry_id or not self._calendar_id:
            _LOGGER.debug(f"get_plugin_options called for {self.__class__.__name__}")
            _LOGGER.debug(f"  _config_entry_id: {self._config_entry_id}")
            _LOGGER.debug(f"  _calendar_id: {self._calendar_id}")
            
            if not self._config_entry_id:
                _LOGGER.warning(f"{self.__class__.__name__}: No config_entry_id set - called too early?")
            if not self._calendar_id:
                _LOGGER.warning(f"{self.__class__.__name__}: No calendar_id set - called too early?")
            return {}
        
        config_entry = _CONFIG_ENTRIES.get(self._config_entry_id)
        if not config_entry:
            _LOGGER.error(f"Config entry {self._config_entry_id} not found in _CONFIG_ENTRIES")
            _LOGGER.debug(f"Available entries: {list(_CONFIG_ENTRIES.keys())}")
            return {}
        
        # FIX: Try both "plugin_options" and "calendar_options" for compatibility
        plugin_options = config_entry.data.get("plugin_options", {})
        if not plugin_options:
            # Fallback to old key name for backward compatibility
            plugin_options = config_entry.data.get("calendar_options", {})
            if plugin_options:
                _LOGGER.debug(f"Using 'calendar_options' (legacy) for {self._calendar_id}")
        
        calendar_options = plugin_options.get(self._calendar_id, {})
        
        # Nur loggen wenn tatsächlich Optionen vorhanden sind
        if calendar_options:
            _LOGGER.debug(f"{self.__class__.__name__} ({self._calendar_id}) loaded options: {calendar_options}")
        
        return calendar_options
    
    # NEUE METHODE: Für Kompatibilität mit Kalendern die _get_plugin_options() verwenden
    def _get_plugin_options(self) -> Dict[str, Any]:
        """Private method for backward compatibility with calendars using _get_plugin_options()."""
        return self.get_plugin_options()
    
    # ... [Rest der Klasse bleibt unverändert] ...