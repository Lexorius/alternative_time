"""Config flow for Alternative Time Systems integration."""
from __future__ import annotations

import logging
import os
from importlib import import_module
from typing import Any, Dict, List

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN

# Fixed category order for the wizard
FIXED_CATEGORY_ORDER = [
    'technical', 'historical', 'cultural', 'military', 'space', 'fantasy', 'scifi', 'religion', 'uncategorized', 'gaming'
]

# GitHub repository URL - used as a description placeholder for the disclaimer
# IMPORTANT: HACS validation forbids URLs in translation strings; we pass the
# URL via description_placeholders instead and reference it as {github_url}.
GITHUB_URL = "https://github.com/Lexorius/alternative_time"

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("name", default="Alternative Time"): str,
})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    return {"title": data.get("name", "Alternative Time")}


ENTITY_ID_PREFIX = "alternative_time_"


def plan_entity_id_migration(pairs, generate):
    """Plan renames to the stable ``sensor.alternative_time_<calendar_id>`` scheme.

    ``pairs``: iterable of (current_entity_id, calendar_id).
    ``generate(calendar_id, current_entity_id)``: returns a free target entity_id
    (the caller wires this to entity_registry.async_generate_entity_id, which
    appends _2/_3 on collisions and treats current_entity_id as available).

    Returns [(old_entity_id, new_entity_id)] for entities whose object_id does
    not already start with ENTITY_ID_PREFIX. Pure function, unit-tested.
    """
    plan = []
    for current, cid in pairs:
        if not current or not cid:
            continue
        object_id = current.split(".", 1)[1] if "." in current else current
        if object_id.startswith(ENTITY_ID_PREFIX):
            continue
        target = generate(cid, current)
        if target and target != current:
            plan.append((current, target))
    return plan


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alternative Time Systems."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._discovered_calendars: Dict[str, Dict[str, Any]] = {}
        self._selected_calendars: List[str] = []
        self._selected_categories: List[str] = []
        self._category_order: List[str] = []
        self._category_index: int = 0
        self._selected_options: Dict[str, Dict[str, Any]] = {}
        self._option_calendars: List[str] = []
        self._option_index: int = 0
        self._user_input: Dict[str, Any] = {}
        # Store mapping between displayed labels and actual keys for each calendar
        self._option_key_mapping: Dict[str, Dict[str, str]] = {}

    def _categories(self) -> List[str]:
        """Get list of available categories from discovered calendars."""
        cats = set()
        for _cid, info in (self._discovered_calendars or {}).items():
            cat = str((info or {}).get("category") or "uncategorized")
            if cat == "religious":
                cat = "religion"
            cats.add(cat)
        # Intersect with fixed order to get a stable sequence
        ordered = [c for c in FIXED_CATEGORY_ORDER if c in cats]
        return ordered

    def _lcal(self, info: dict, key: str, default: str = "") -> str:
        """Get localized value from calendar info or option metadata."""
        # Get current language
        lang = self.hass.config.language if self.hass else "en"

        # Try to get localized value
        if isinstance(info, dict):
            translations = info.get("translations", {})
            if translations and lang in translations:
                trans = translations[lang]
                if isinstance(trans, dict) and key in trans:
                    return trans[key]

            # Fallback to direct key
            if key in info:
                val = info[key]
                if isinstance(val, str):
                    return val
                elif isinstance(val, dict):
                    # Could be a nested structure with language keys
                    if lang in val:
                        return str(val[lang])
                    elif "en" in val:
                        return str(val["en"])

        return default

    def _details_text(self, calendars: Dict[str, Dict]) -> str:
        """Generate a details text for discovered calendars."""
        if not calendars:
            return "No calendars discovered"

        lang = self.hass.config.language if self.hass else "en"

        # Translations for the details text
        translations = {
            "en": "Available calendars: {count}",
            "de": "Verfügbare Kalender: {count}",
            "fr": "Calendriers disponibles: {count}",
            "es": "Calendarios disponibles: {count}",
            "it": "Calendari disponibili: {count}",
            "nl": "Beschikbare kalenders: {count}",
            "pl": "Dostępne kalendarze: {count}",
            "pt": "Calendários disponíveis: {count}",
            "ru": "Доступные календари: {count}",
            "zh": "可用日历: {count}",
            "ja": "利用可能なカレンダー: {count}",
            "ko": "사용 가능한 달력: {count}"
        }

        template = translations.get(lang, translations["en"])
        return template.format(count=len(calendars))

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            # Discover calendars asynchronously
            await self._async_discover_calendars()
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        try:
            _ = await validate_input(self.hass, user_input)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
                errors={"base": "unknown"}
            )

        # Store user input and move to category selection
        self._user_input = user_input
        await self._async_discover_calendars()
        return await self.async_step_select_categories()

    async def async_step_select_categories(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step to select which categories to configure."""
        categories = self._categories()
        if not categories:
            return self.async_abort(reason="no_calendars_found")

        if user_input is None:
            options = [{"label": c.title(), "value": c} for c in categories]
            schema = vol.Schema({
                vol.Required("categories", default=categories): SelectSelector(
                    SelectSelectorConfig(
                        options=options,
                        multiple=True,
                        mode=SelectSelectorMode.DROPDOWN
                    )
                )
            })
            return self.async_show_form(
                step_id="select_categories",
                data_schema=schema,
                description_placeholders={
                    "details": self._details_text(self._discovered_calendars)
                }
            )

        # Save and proceed
        selected = user_input.get("categories", [])
        self._selected_categories = [c for c in selected if c in categories]
        self._category_order = [c for c in FIXED_CATEGORY_ORDER if c in self._selected_categories]
        self._category_index = 0
        self._selected_calendars = []
        return await self.async_step_select_calendars_by_category()

    async def async_step_select_calendars_by_category(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Iterate category list and collect calendars with checkbox UI and detailed labels."""
        # Process user input if we're coming back from a form
        if user_input is not None and self._category_index > 0:
            # Save selected for previous category
            selected = list(user_input.get("calendars", []))
            self._selected_calendars.extend(selected)

        # Check if we're done with all categories
        if self._category_index >= len(self._category_order):
            # Done with categories -> go to plugin options
            self._option_calendars = [
                cid for cid in self._selected_calendars
                if isinstance(
                    self._discovered_calendars.get(cid, {}).get("config_options"),
                    dict
                )
            ]
            self._option_index = 0

            if self._option_calendars:
                return await self.async_step_plugin_options()

            # No options to configure, go to disclaimer
            _LOGGER.info("No plugin options to configure, moving to disclaimer")
            return await self.async_step_disclaimer()

        # Get current category
        current_cat = self._category_order[self._category_index]

        # Get calendars for this category
        cals = [
            (cid, info) for cid, info in self._discovered_calendars.items()
            if str(info.get("category", "uncategorized")).replace("religious", "religion") == current_cat
        ]

        if not cals:
            # Skip empty category
            self._category_index += 1
            return await self.async_step_select_calendars_by_category()

        # Build options dict with detailed labels
        options_dict = {}

        for i, (cid, info) in enumerate(cals):
            name = self._lcal(info, "name", cid)
            desc = self._lcal(info, "description", "")

            # Extra info
            extra_parts = []
            interval = info.get("update_interval")
            if interval:
                if interval == 1:
                    extra_parts.append("Updates every second")
                elif interval < 60:
                    extra_parts.append(f"Updates every {interval} seconds")
                elif interval == 60:
                    extra_parts.append("Updates every minute")
                elif interval < 3600:
                    extra_parts.append(f"Updates every {interval // 60} minutes")
                else:
                    extra_parts.append(f"Updates every {interval // 3600} hour(s)")

            acc = info.get("accuracy")
            if acc:
                extra_parts.append(f"Accuracy: {acc}")
            extra = " • ".join(extra_parts)

            # Format the label
            label_parts = [name]
            if desc:
                label_parts.append(f"  ↳ {desc}")
            if extra:
                label_parts.append(f"  ↳ {extra}")

            label = "\n".join(label_parts)
            options_dict[cid] = label

        # WICHTIGE ÄNDERUNG: Keine automatische Vorauswahl von Kalendern
        # Nur bereits ausgewählte Kalender bleiben ausgewählt (für Navigation zurück)
        already = [cid for cid, _ in cals if cid in self._selected_calendars]
        default = already  # NICHT mehr "or [cid for cid, _ in cals]" - keine automatische Auswahl aller Kalender

        schema = vol.Schema({
            vol.Required("calendars", default=default): cv.multi_select(options_dict)
        })

        # Increment index for next iteration
        self._category_index += 1

        return self.async_show_form(
            step_id="select_calendars_by_category",
            data_schema=schema,
            description_placeholders={
                "category": current_cat.title(),
                "details": self._details_text(dict(cals))
            }
        )

    async def async_step_plugin_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Iterate selected calendars that expose CALENDAR_INFO['config_options'] and collect values."""
        # Process user input from previous form
        if user_input is not None and self._option_index > 0:
            # Store data from the previous calendar (index already incremented)
            prev_cid = self._option_calendars[self._option_index - 1]
            normalized = {}

            _LOGGER.debug(f"Processing options for {prev_cid}, raw input: {user_input}")

            # Get the key mapping for this calendar
            key_mapping = self._option_key_mapping.get(prev_cid, {})

            # Process each input value
            for input_key, value in user_input.items():
                # Look up the actual config key from our mapping
                if input_key in key_mapping:
                    actual_key = key_mapping[input_key]
                    normalized[actual_key] = value
                    _LOGGER.debug(f"Mapped '{input_key}' to '{actual_key}' with value: {value}")
                else:
                    # Fallback: use as is
                    normalized[input_key] = value
                    _LOGGER.warning(f"No mapping found for '{input_key}', using as-is")

            self._selected_options[prev_cid] = normalized
            _LOGGER.info(f"Stored options for {prev_cid}: {normalized}")

        # Check if we're done with all calendars
        if self._option_index >= len(self._option_calendars):
            # Go to disclaimer before creating entry
            _LOGGER.info("All plugin options processed, moving to disclaimer")
            return await self.async_step_disclaimer()

        # Get current calendar to configure
        cid = self._option_calendars[self._option_index]
        info = self._discovered_calendars.get(cid, {})
        opts = info.get("config_options", {})

        # Get calendar name and description for the form (before any skip logic)
        calendar_name = self._lcal(info, "name", cid)
        calendar_desc = self._lcal(info, "description", "")

        # Skip calendars without options
        if not opts:
            _LOGGER.debug(f"Calendar {cid} has no config options, skipping")
            self._option_index += 1
            return await self.async_step_plugin_options()

        # Build schema from config_options
        schema_dict = {}
        current_mapping = {}

        for key, meta in opts.items():
            try:
                # Get metadata
                typ = meta.get("type", "string")
                default = meta.get("default")

                # Get localized label and description
                label = self._lcal(meta, "label", key)
                option_desc = self._lcal(meta, "description", "")

                # Store the mapping from label to actual key
                current_mapping[label] = key

                # Handle SELECT type
                if typ == "select":
                    options = meta.get("options", [])
                    if options:
                        # Convert options to selector format
                        select_options = []
                        for opt in options:
                            if isinstance(opt, dict):
                                # Option with label and value
                                opt_label = self._lcal(opt, "label", str(opt.get("value", opt)))
                                opt_value = opt.get("value", opt_label)
                            else:
                                # Simple string option
                                opt_label = str(opt)
                                opt_value = opt
                            select_options.append({"label": opt_label, "value": opt_value})

                        schema_dict[vol.Optional(label, default=default, description=option_desc)] = SelectSelector(
                            SelectSelectorConfig(
                                options=select_options,
                                mode=SelectSelectorMode.DROPDOWN
                            )
                        )
                    else:
                        # Fallback to text if no options
                        _LOGGER.warning(f"No options for select field {key} in {cid}, using text")
                        schema_dict[vol.Optional(label, default=str(default) if default is not None else "", description=option_desc)] = TextSelector(
                            TextSelectorConfig(type=TextSelectorType.TEXT)
                        )
                    continue  # Skip the rest of type handling

                # BOOLEAN type
                if typ == "boolean":
                    schema_dict[vol.Optional(label, default=bool(default) if default is not None else False, description=option_desc)] = BooleanSelector()

                # NUMBER types
                elif typ in ("number", "integer", "float"):
                    # Handle min/max if present
                    min_val = meta.get("min")
                    max_val = meta.get("max")

                    if typ == "integer":
                        default_num = int(default) if default is not None else 0
                        mode = NumberSelectorMode.BOX
                    else:
                        default_num = float(default) if default is not None else 0.0
                        mode = NumberSelectorMode.BOX

                    config = NumberSelectorConfig(mode=mode)
                    if min_val is not None:
                        config["min"] = float(min_val)
                    if max_val is not None:
                        config["max"] = float(max_val)

                    schema_dict[vol.Optional(label, default=default_num, description=option_desc)] = NumberSelector(config)

                # TEXT/STRING types
                elif typ in ("string", "text"):
                    schema_dict[vol.Optional(label, default=str(default) if default is not None else "", description=option_desc)] = TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    )

                else:
                    # Fallback for unknown types
                    _LOGGER.warning(f"Unknown config option type '{typ}' for {key} in {cid}, using text")
                    schema_dict[vol.Optional(label, default=str(default) if default is not None else "", description=option_desc)] = TextSelector(
                        TextSelectorConfig(type=TextSelectorType.TEXT)
                    )

            except Exception as e:
                _LOGGER.error(f"Error building schema for {key} in {cid}: {e}", exc_info=True)
                continue

        # Store the mapping for this calendar
        self._option_key_mapping[cid] = current_mapping
        _LOGGER.info(f"Key mapping for {cid}: {current_mapping}")

        # If no valid options, skip to next
        if not schema_dict:
            _LOGGER.info(f"No valid config options for {cid}, skipping")
            self._option_index += 1
            return await self.async_step_plugin_options()

        # Increment index AFTER we know we're showing the form
        self._option_index += 1
        _LOGGER.info(f"Incremented index to {self._option_index} after showing form for {cid}")

        try:
            schema = vol.Schema(schema_dict)

            return self.async_show_form(
                step_id="plugin_options",
                data_schema=schema,
                description_placeholders={
                    "calendar_name": calendar_name,
                    "calendar_description": calendar_desc
                }
            )
        except Exception as e:
            _LOGGER.error(f"Error creating form for {cid}: {e}", exc_info=True)
            # Skip this calendar on error
            return await self.async_step_plugin_options()

    async def async_step_disclaimer(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show disclaimer before creating the entry."""
        if user_input is not None:
            # Create the config entry
            _LOGGER.info(f"Creating config entry with {len(self._selected_calendars)} calendars")

            # Build final data
            data = {
                **self._user_input,
                "calendars": self._selected_calendars,
                "calendar_options": self._selected_options,
                "groups": self._build_groups(self._selected_calendars, self._discovered_calendars)
            }

            return self.async_create_entry(title=self._user_input["name"], data=data)

        # Simple schema with just a confirmation
        schema = vol.Schema({})

        # IMPORTANT: HACS validation forbids URLs inside translation strings,
        # so we expose the GitHub URL as a description placeholder instead.
        return self.async_show_form(
            step_id="disclaimer",
            data_schema=schema,
            description_placeholders={
                "github_url": GITHUB_URL
            }
        )

    def _build_groups(self, calendars: List[str], discovered: Dict[str, Dict]) -> Dict[str, List[str]]:
        """Build groups based on calendar categories."""
        groups = {}
        for cal_id in calendars:
            info = discovered.get(cal_id, {})
            category = info.get("category", "uncategorized")
            if category == "religious":
                category = "religion"
            if category not in groups:
                groups[category] = []
            groups[category].append(cal_id)
        return groups

    async def _async_discover_calendars(self) -> None:
        """Discover available calendar implementations asynchronously."""
        try:
            # Try to import from sensor module first
            try:
                from .sensor import export_discovered_calendars
                discovered = await self.hass.async_add_executor_job(
                    export_discovered_calendars
                )
                if discovered:
                    self._discovered_calendars = discovered
                    return
            except ImportError:
                pass

            # Fallback to direct discovery
            self._discovered_calendars = await self._async_direct_discovery()

        except Exception as e:
            _LOGGER.error(f"Failed to discover calendars: {e}")
            self._discovered_calendars = {}

    async def _async_direct_discovery(self) -> Dict[str, Dict[str, Any]]:
        """Directly discover calendar modules from the calendars directory."""
        discovered = {}

        # Get calendars directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        calendars_dir = os.path.join(current_dir, "calendars")

        if not os.path.exists(calendars_dir):
            _LOGGER.warning(f"Calendars directory not found: {calendars_dir}")
            return discovered

        # List files asynchronously
        files = await self.hass.async_add_executor_job(
            os.listdir, calendars_dir
        )

        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]  # Remove .py extension

                # Skip template and example files
                if "template" in module_name.lower() or "example" in module_name.lower():
                    continue

                try:
                    # Import module asynchronously
                    module = await self.hass.async_add_executor_job(
                        self._import_calendar_module, module_name
                    )

                    if module and hasattr(module, 'CALENDAR_INFO'):
                        cal_info = module.CALENDAR_INFO
                        cal_id = cal_info.get('id', module_name)
                        discovered[cal_id] = cal_info
                        _LOGGER.debug(f"Discovered calendar: {cal_id}")

                except Exception as e:
                    _LOGGER.warning(f"Failed to load calendar {module_name}: {e}")
                    continue

        _LOGGER.info(f"Discovered {len(discovered)} calendars")
        return discovered

    def _import_calendar_module(self, module_name: str):
        """Import a calendar module (blocking operation for executor)."""
        try:
            # Try different import methods
            try:
                module = import_module(f'.calendars.{module_name}', package='custom_components.alternative_time')
            except ImportError:
                try:
                    module = import_module(f'custom_components.alternative_time.calendars.{module_name}')
                except ImportError:
                    module = import_module(module_name)

            return module
        except Exception as e:
            _LOGGER.error(f"Failed to import calendar module {module_name}: {e}")
            return None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        # HA >= 2024.12: config_entry is a read-only property on OptionsFlow
        # that HA sets automatically. Do NOT pass it through the constructor.
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Edit per-calendar options of an existing Alternative Time entry.

    Two-step flow: ``init`` picks one of the configured calendars,
    ``configure_calendar`` renders the same schema the wizard used to set up
    that calendar and writes the new values back into ``config_entry.data``.

    Note: no ``__init__`` — HA's ``OptionsFlow`` base class provides
    ``self.config_entry`` automatically since 2024.12.
    """

    _selected_calendar: str | None = None
    _discovered: Dict[str, Dict[str, Any]] | None = None
    _key_mapping: Dict[str, str] | None = None

    def _lcal(self, info: dict, key: str, default: str = "") -> str:
        """Localized value lookup, mirrors ConfigFlow._lcal."""
        lang = self.hass.config.language if self.hass else "en"
        if isinstance(info, dict):
            translations = info.get("translations", {})
            if translations and lang in translations:
                trans = translations[lang]
                if isinstance(trans, dict) and key in trans:
                    return trans[key]
            if key in info:
                val = info[key]
                if isinstance(val, str):
                    return val
                if isinstance(val, dict):
                    if lang in val:
                        return str(val[lang])
                    if "en" in val:
                        return str(val["en"])
        return default

    async def _ensure_discovered(self) -> None:
        """Discover calendar modules once per flow instance."""
        if self._discovered:
            return
        try:
            from .sensor import export_discovered_calendars
            self._discovered = await self.hass.async_add_executor_job(
                export_discovered_calendars
            )
        except Exception as e:
            _LOGGER.warning(f"Options flow: discovery via sensor failed: {e}")
            self._discovered = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Entry menu: reconfigure a calendar, or migrate entity IDs."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["select_calendar", "migrate_entity_ids"],
        )

    async def async_step_select_calendar(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Let the user pick which configured calendar to reconfigure."""
        await self._ensure_discovered()

        configured: List[str] = list(self.config_entry.data.get("calendars", []))
        # Only offer calendars that actually expose options
        options_capable = [
            cid for cid in configured
            if (self._discovered.get(cid, {}) or {}).get("config_options")
        ]

        if not options_capable:
            return self.async_abort(
                reason="no_options",
                description_placeholders={
                    "message": "None of the configured calendars exposes options."
                },
            )

        if user_input is not None:
            self._selected_calendar = user_input["calendar"]
            return await self.async_step_configure_calendar()

        select_options = [
            {
                "value": cid,
                "label": self._lcal(self._discovered.get(cid, {}), "name", cid),
            }
            for cid in options_capable
        ]
        schema = vol.Schema({
            vol.Required("calendar"): SelectSelector(
                SelectSelectorConfig(
                    options=select_options,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
        })
        return self.async_show_form(
            step_id="select_calendar",
            data_schema=schema,
            description_placeholders={"title": self.config_entry.title},
        )

    async def async_step_migrate_entity_ids(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Rename this entry's sensors to sensor.alternative_time_<calendar_id>.

        Opt-in and one-shot: the stable prefix is what the documented recorder
        glob ``sensor.alternative_time_*`` matches. Entities created before
        v2.6.0.7 kept their old ids; this step brings them onto the scheme.
        Dashboards and automations referencing the old ids must be updated by
        the user — a persistent notification lists every old -> new pair.
        """
        from homeassistant.components import persistent_notification
        from homeassistant.helpers import entity_registry as er

        from .sensor import entities_for_entry

        registry = er.async_get(self.hass)

        def _generate(cid: str, current: str) -> str:
            return er.async_generate_entity_id(
                registry, "sensor", f"{ENTITY_ID_PREFIX}{cid}", current_entity_id=current
            )

        plan = plan_entity_id_migration(entities_for_entry(self.config_entry.entry_id), _generate)

        if not plan:
            return self.async_abort(reason="nothing_to_migrate")

        if user_input is None:
            preview = "\n".join(f"- `{old}` \u2192 `{new}`" for old, new in plan)
            return self.async_show_form(
                step_id="migrate_entity_ids",
                data_schema=vol.Schema({}),
                description_placeholders={"count": str(len(plan)), "preview": preview},
            )

        done: List[tuple[str, str]] = []
        for old, new in plan:
            try:
                registry.async_update_entity(old, new_entity_id=new)
                done.append((old, new))
                _LOGGER.info(f"Migrated entity_id {old} -> {new}")
            except ValueError as e:
                _LOGGER.warning(f"Could not migrate {old} -> {new}: {e}")

        if done:
            lines = "\n".join(f"- `{old}` \u2192 `{new}`" for old, new in done)
            yaml_hint = (
                "```yaml\nrecorder:\n  exclude:\n    entity_globs:\n"
                f"      - sensor.{ENTITY_ID_PREFIX}*\n```"
            )
            persistent_notification.async_create(
                self.hass,
                (
                    f"{len(done)} entity ID(s) of **{self.config_entry.title}** were renamed "
                    f"to the `sensor.{ENTITY_ID_PREFIX}*` scheme. Update dashboards and "
                    f"automations that reference the old IDs:\n\n{lines}\n\n"
                    f"Recorder exclusion for all of them:\n{yaml_hint}"
                ),
                title="Alternative Time: entity IDs migrated",
                notification_id=f"{DOMAIN}_entity_id_migration_{self.config_entry.entry_id}",
            )

        return self.async_abort(
            reason="migration_done",
            description_placeholders={"count": str(len(done))},
        )

    async def async_step_configure_calendar(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: show schema for the selected calendar; save on submit."""
        cid = self._selected_calendar
        if cid is None:
            return await self.async_step_init()

        info = (self._discovered or {}).get(cid, {})
        opts = info.get("config_options", {}) or {}

        if user_input is not None:
            # Map localized labels back to actual config keys
            mapping = self._key_mapping or {}
            normalized: Dict[str, Any] = {}
            for label, value in user_input.items():
                actual_key = mapping.get(label, label)
                normalized[actual_key] = value

            # Persist into entry.data["calendar_options"][cid] without dropping
            # the other top-level data fields (calendars, groups, name, ...).
            current_data = dict(self.config_entry.data)
            current_cal_opts = dict(current_data.get("calendar_options", {}))
            existing = dict(current_cal_opts.get(cid, {}))
            existing.update(normalized)
            current_cal_opts[cid] = existing
            current_data["calendar_options"] = current_cal_opts

            self.hass.config_entries.async_update_entry(
                self.config_entry, data=current_data
            )
            _LOGGER.info(f"OptionsFlow saved new options for {cid}: {normalized}")

            # The real data lives in entry.data (written above, which fires the
            # update listener -> reload). Pass entry.options through unchanged so
            # HA sees no options diff and does not trigger a second reload.
            return self.async_create_entry(title="", data=dict(self.config_entry.options))

        # Build schema (duplicated from ConfigFlow.async_step_plugin_options
        # to keep this fix self-contained)
        schema_dict: Dict[Any, Any] = {}
        current_mapping: Dict[str, str] = {}
        existing_opts = (
            self.config_entry.data.get("calendar_options", {}).get(cid, {}) or {}
        )

        for key, meta in opts.items():
            try:
                typ = meta.get("type", "string")
                default = existing_opts.get(key, meta.get("default"))
                label = self._lcal(meta, "label", key)
                option_desc = self._lcal(meta, "description", "")
                current_mapping[label] = key

                if typ == "select":
                    sel_options = meta.get("options", [])
                    formatted = []
                    for opt in sel_options:
                        if isinstance(opt, dict):
                            opt_label = self._lcal(opt, "label", str(opt.get("value", opt)))
                            opt_value = opt.get("value", opt_label)
                        else:
                            opt_label = str(opt)
                            opt_value = opt
                        formatted.append({"label": opt_label, "value": opt_value})
                    if formatted:
                        schema_dict[
                            vol.Optional(label, default=default, description=option_desc)
                        ] = SelectSelector(
                            SelectSelectorConfig(
                                options=formatted, mode=SelectSelectorMode.DROPDOWN
                            )
                        )
                    else:
                        schema_dict[
                            vol.Optional(label, default=str(default) if default is not None else "", description=option_desc)
                        ] = TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT))
                elif typ == "boolean":
                    schema_dict[
                        vol.Optional(label, default=bool(default) if default is not None else False, description=option_desc)
                    ] = BooleanSelector()
                elif typ in ("number", "integer", "float"):
                    if typ == "integer":
                        default_num: Any = int(default) if default is not None else 0
                    else:
                        default_num = float(default) if default is not None else 0.0
                    config = NumberSelectorConfig(mode=NumberSelectorMode.BOX)
                    min_val = meta.get("min")
                    max_val = meta.get("max")
                    if min_val is not None:
                        config["min"] = float(min_val)
                    if max_val is not None:
                        config["max"] = float(max_val)
                    schema_dict[
                        vol.Optional(label, default=default_num, description=option_desc)
                    ] = NumberSelector(config)
                else:
                    schema_dict[
                        vol.Optional(label, default=str(default) if default is not None else "", description=option_desc)
                    ] = TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT))
            except Exception as e:
                _LOGGER.error(f"OptionsFlow schema build error for {key} in {cid}: {e}", exc_info=True)

        self._key_mapping = current_mapping

        if not schema_dict:
            return self.async_abort(
                reason="no_options",
                description_placeholders={
                    "message": f"{self._lcal(info, 'name', cid)} has no editable options."
                },
            )

        return self.async_show_form(
            step_id="configure_calendar",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={
                "calendar_name": self._lcal(info, "name", cid),
                "calendar_description": self._lcal(info, "description", ""),
            },
        )
