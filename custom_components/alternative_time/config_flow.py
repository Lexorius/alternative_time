"""Config flow for Alternative Time Systems integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
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

from .const import DOMAIN, ENTITY_ID_PREFIX
from .i18n import pick_language
from .sensor import async_discover_all_calendars, entities_for_entry

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

_AVAILABLE_CALENDARS = {
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


def _lang(flow) -> str:
    """Language of the Home Assistant instance a flow runs in."""
    return flow.hass.config.language if flow.hass else "en"


def _category(info: dict) -> str:
    """Category of a calendar as the wizard groups it."""
    category = str((info or {}).get("category") or "uncategorized")
    return "religion" if category == "religious" else category


def lcal(info: Any, key: str, lang: str, default: str = "") -> str:
    """Localized value of a CALENDAR_INFO entry or of one of its options.

    The value is either a plain string or a {language: text} mapping; some
    calendars keep texts under info["translations"][language][key] instead.
    Language matching is i18n.pick_language, the same rule the sensors use.
    """
    if not isinstance(info, dict):
        return default
    translations = info.get("translations")
    if isinstance(translations, dict):
        for code in (lang, lang.replace("_", "-").split("-")[0]):
            texts = translations.get(code)
            if isinstance(texts, dict) and key in texts:
                return str(texts[key])
    value = info.get(key)
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and value:
        return pick_language(value, lang, default)
    return default


def build_options_schema(
    opts: Dict[str, Any], current: Dict[str, Any], lang: str
) -> tuple[Dict[Any, Any], Dict[str, str]]:
    """Turn a calendar's config_options into form fields.

    Returns (fields, {shown label: option key}). Fields are keyed by the
    localized label because the form shows the key as the field name; the
    mapping translates the submitted labels back. Values in ``current``
    (already stored options) win over the declared defaults.
    """
    fields: Dict[Any, Any] = {}
    mapping: Dict[str, str] = {}

    for key, meta in opts.items():
        try:
            typ = meta.get("type", "string")
            default = current.get(key, meta.get("default"))
            label = lcal(meta, "label", lang, key)
            description = lcal(meta, "description", lang, "")
            mapping[label] = key

            if typ == "select" and meta.get("options"):
                choices = []
                for opt in meta["options"]:
                    if isinstance(opt, dict):
                        opt_label = lcal(opt, "label", lang, str(opt.get("value", opt)))
                        choices.append({"label": opt_label, "value": opt.get("value", opt_label)})
                    else:
                        choices.append({"label": str(opt), "value": opt})
                fields[vol.Optional(label, default=default, description=description)] = SelectSelector(
                    SelectSelectorConfig(options=choices, mode=SelectSelectorMode.DROPDOWN)
                )
            elif typ == "boolean":
                fields[vol.Optional(label, default=bool(default) if default is not None else False,
                                    description=description)] = BooleanSelector()
            elif typ in ("number", "integer", "float"):
                if typ == "integer":
                    number: Any = int(default) if default is not None else 0
                else:
                    number = float(default) if default is not None else 0.0
                config = NumberSelectorConfig(mode=NumberSelectorMode.BOX)
                if meta.get("min") is not None:
                    config["min"] = float(meta["min"])
                if meta.get("max") is not None:
                    config["max"] = float(meta["max"])
                fields[vol.Optional(label, default=number, description=description)] = NumberSelector(config)
            else:
                # string, text, a select without choices, and unknown types
                fields[vol.Optional(label, default=str(default) if default is not None else "",
                                    description=description)] = TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT)
                )
        except Exception:  # noqa: BLE001 — a bad option must not break the whole form
            _LOGGER.exception("Could not build the form field for option %s", key)

    return fields, mapping


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
        cats = {_category(info) for info in self._discovered_calendars.values()}
        return [c for c in FIXED_CATEGORY_ORDER if c in cats]

    def _details_text(self, calendars: Dict[str, Dict]) -> str:
        """Generate a details text for discovered calendars."""
        if not calendars:
            return "No calendars discovered"
        return pick_language(_AVAILABLE_CALENDARS, _lang(self)).format(count=len(calendars))

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        self._discovered_calendars = await async_discover_all_calendars(self.hass)

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Store user input and move to category selection
        self._user_input = user_input
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
            return await self.async_step_disclaimer()

        # Get current category
        current_cat = self._category_order[self._category_index]

        # Get calendars for this category
        cals = [
            (cid, info) for cid, info in self._discovered_calendars.items()
            if _category(info) == current_cat
        ]

        if not cals:
            # Skip empty category
            self._category_index += 1
            return await self.async_step_select_calendars_by_category()

        # Build options dict with detailed labels
        lang = _lang(self)
        options_dict = {}

        for cid, info in cals:
            name = lcal(info, "name", lang, cid)
            desc = lcal(info, "description", lang, "")

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

            options_dict[cid] = "\n".join(label_parts)

        # No calendar is pre-selected; only ones picked earlier stay selected
        default = [cid for cid, _ in cals if cid in self._selected_calendars]

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
            key_mapping = self._option_key_mapping.get(prev_cid, {})
            self._selected_options[prev_cid] = {
                key_mapping.get(label, label): value for label, value in user_input.items()
            }

        # Check if we're done with all calendars
        if self._option_index >= len(self._option_calendars):
            # Go to disclaimer before creating entry
            return await self.async_step_disclaimer()

        # Get current calendar to configure
        cid = self._option_calendars[self._option_index]
        info = self._discovered_calendars.get(cid, {})
        lang = _lang(self)

        fields, mapping = build_options_schema(info.get("config_options") or {}, {}, lang)
        self._option_key_mapping[cid] = mapping
        self._option_index += 1

        # Nothing to ask for this calendar: go on to the next one
        if not fields:
            return await self.async_step_plugin_options()

        return self.async_show_form(
            step_id="plugin_options",
            data_schema=vol.Schema(fields),
            description_placeholders={
                "calendar_name": lcal(info, "name", lang, cid),
                "calendar_description": lcal(info, "description", lang, "")
            }
        )

    async def async_step_disclaimer(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show disclaimer before creating the entry."""
        if user_input is not None:
            data = {
                **self._user_input,
                "calendars": self._selected_calendars,
                "calendar_options": self._selected_options,
            }
            return self.async_create_entry(title=self._user_input["name"], data=data)

        # IMPORTANT: HACS validation forbids URLs inside translation strings,
        # so we expose the GitHub URL as a description placeholder instead.
        return self.async_show_form(
            step_id="disclaimer",
            data_schema=vol.Schema({}),
            description_placeholders={
                "github_url": GITHUB_URL
            }
        )

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

    ``init`` is a menu: reconfigure one of the entry's calendars
    (``select_calendar`` then ``configure_calendar``, which shows the same
    fields as the setup wizard and writes them to ``config_entry.data``), or
    rename the entry's sensors to the stable entity_id scheme
    (``migrate_entity_ids``).

    Note: no ``__init__`` — HA's ``OptionsFlow`` base class provides
    ``self.config_entry`` automatically since 2024.12.
    """

    _selected_calendar: str | None = None
    _discovered: Dict[str, Dict[str, Any]] | None = None
    _key_mapping: Dict[str, str] | None = None

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
        self._discovered = await async_discover_all_calendars(self.hass)

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

        lang = _lang(self)
        select_options = [
            {"value": cid, "label": lcal(self._discovered.get(cid, {}), "name", lang, cid)}
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
        glob ``sensor.alternative_time_*`` matches. Entities created by older
        versions kept their old ids; this step brings them onto the scheme.
        Dashboards and automations referencing the old ids must be updated by
        the user — a persistent notification lists every old -> new pair.
        """
        from homeassistant.components import persistent_notification
        from homeassistant.helpers import entity_registry as er

        registry = er.async_get(self.hass)

        def _generate(cid: str, current: str) -> str:
            return er.async_generate_entity_id(
                registry, "sensor", f"{ENTITY_ID_PREFIX}{cid}", current_entity_id=current
            )

        plan = plan_entity_id_migration(entities_for_entry(self.config_entry.entry_id), _generate)

        if not plan:
            return self.async_abort(reason="nothing_to_migrate")

        if user_input is None:
            preview = "\n".join(f"- `{old}` → `{new}`" for old, new in plan)
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
                _LOGGER.info("Migrated entity_id %s -> %s", old, new)
            except ValueError as err:
                _LOGGER.warning("Could not migrate %s -> %s: %s", old, new, err)

        if done:
            lines = "\n".join(f"- `{old}` → `{new}`" for old, new in done)
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
        """Show the fields of the selected calendar; save on submit."""
        cid = self._selected_calendar
        if cid is None:
            return await self.async_step_init()

        info = (self._discovered or {}).get(cid, {})
        stored = self.config_entry.data.get("calendar_options", {}).get(cid, {}) or {}

        if user_input is not None:
            # Map localized labels back to actual config keys
            mapping = self._key_mapping or {}
            new_values = {mapping.get(label, label): value for label, value in user_input.items()}

            # Persist into entry.data["calendar_options"][cid] without dropping
            # the other top-level data fields (calendars, name, ...).
            data = dict(self.config_entry.data)
            calendar_options = dict(data.get("calendar_options", {}))
            calendar_options[cid] = {**stored, **new_values}
            data["calendar_options"] = calendar_options
            self.hass.config_entries.async_update_entry(self.config_entry, data=data)

            # The real data lives in entry.data (written above, which fires the
            # update listener -> reload). Pass entry.options through unchanged so
            # HA sees no options diff and does not trigger a second reload.
            return self.async_create_entry(title="", data=dict(self.config_entry.options))

        lang = _lang(self)
        fields, self._key_mapping = build_options_schema(info.get("config_options") or {}, stored, lang)

        if not fields:
            return self.async_abort(
                reason="no_options",
                description_placeholders={
                    "message": f"{lcal(info, 'name', lang, cid)} has no editable options."
                },
            )

        return self.async_show_form(
            step_id="configure_calendar",
            data_schema=vol.Schema(fields),
            description_placeholders={
                "calendar_name": lcal(info, "name", lang, cid),
                "calendar_description": lcal(info, "description", lang, ""),
            },
        )
