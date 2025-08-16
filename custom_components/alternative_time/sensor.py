async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Alternative Time Systems sensors from a config entry."""
    
    # Get selected calendars from config
    selected_calendars = config_entry.data.get("calendars", [])
    name = config_entry.data.get("name", "Alternative Time")
    plugin_options = config_entry.data.get("plugin_options", {})
    
    if not selected_calendars:
        _LOGGER.warning("No calendars selected")
        return
    
    # Discover all available calendars
    discovered_calendars = await async_discover_all_calendars(hass)
    
    # Create sensors for selected calendars
    sensors = []
    for calendar_id in selected_calendars:
        if calendar_id not in discovered_calendars:
            _LOGGER.warning(f"Calendar {calendar_id} not found")
            continue
        
        calendar_info = discovered_calendars[calendar_id]
        
        try:
            # Import the calendar module asynchronously
            module = await async_import_calendar_module(hass, calendar_id)
            
            if not module:
                _LOGGER.error(f"Failed to import calendar module: {calendar_id}")
                continue
            
            # Find the sensor class
            sensor_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type) and 
                    issubclass(item, AlternativeTimeSensorBase) and 
                    item != AlternativeTimeSensorBase):
                    sensor_class = item
                    break
            
            if not sensor_class:
                _LOGGER.error(f"No sensor class found in calendar module: {calendar_id}")
                continue
            
            # Get plugin options for this specific calendar
            calendar_plugin_options = plugin_options.get(calendar_id, {})
            
            # Create sensor instance with different parameter combinations
            # Try different initialization signatures for compatibility
            try:
                # Method 1: Try with all parameters
                sensor = sensor_class(name, hass, config_entry, calendar_plugin_options)
                _LOGGER.debug(f"Created sensor for {calendar_id} with config_entry and plugin_options")
            except TypeError:
                try:
                    # Method 2: Try with config_entry only
                    sensor = sensor_class(name, hass, config_entry)
                    _LOGGER.debug(f"Created sensor for {calendar_id} with config_entry")
                except TypeError:
                    try:
                        # Method 3: Try with basic parameters only
                        sensor = sensor_class(name, hass)
                        _LOGGER.debug(f"Created sensor for {calendar_id} with basic parameters")
                    except TypeError as e:
                        _LOGGER.error(f"Failed to create sensor for {calendar_id}: {e}")
                        continue
            
            sensors.append(sensor)
            _LOGGER.info(f"Created sensor for calendar: {calendar_id}")
            
        except Exception as e:
            _LOGGER.error(f"Failed to create sensor for calendar {calendar_id}: {e}")
            continue
    
    if sensors:
        async_add_entities(sensors)