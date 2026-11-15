"""Constants for the Alternative Time integration."""

DOMAIN = "alternative_time"

# Every sensor gets the entity_id sensor.alternative_time_<calendar_id>, so one
# recorder glob (sensor.alternative_time_*) covers the whole integration.
ENTITY_ID_PREFIX = "alternative_time_"
