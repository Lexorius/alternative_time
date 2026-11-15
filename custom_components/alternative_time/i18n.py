"""Language lookup shared by the sensors and the config flow."""
from __future__ import annotations

from typing import Any, Mapping


def pick_language(texts: Mapping[str, Any], lang: str | None, default: str = "") -> str:
    """Pick the text for a Home Assistant language code.

    Order: the exact code ("pt-BR", "zh-Hans"), the base language ("pt",
    "zh"), English, the given default, and last any text at all.
    """
    lang = lang or "en"
    if lang in texts:
        return str(texts[lang])
    base = lang.replace("_", "-").split("-")[0]
    if base in texts:
        return str(texts[base])
    if "en" in texts:
        return str(texts["en"])
    if default:
        return default
    return str(next(iter(texts.values()), ""))
