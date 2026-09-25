"""strings.json and translations/*.json: valid, complete, hassfest-clean.

hassfest rejects anything tag-shaped ("the string should not contain HTML")
but only validates strings.json and en.json; the other languages carried the
same `<...>` pattern in v2.6.2 and rendered wrongly. This checks all of them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from conftest import REPO_ROOT

INTEGRATION_DIR = REPO_ROOT / "custom_components" / "alternative_time"
STRINGS = INTEGRATION_DIR / "strings.json"
TRANSLATIONS = sorted((INTEGRATION_DIR / "translations").glob("*.json"))

HTML_TAG = re.compile(r"<[^>]*>")
PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")


def _walk(node, prefix=""):
    for key, value in node.items():
        if isinstance(value, dict):
            yield from _walk(value, f"{prefix}{key}.")
        else:
            yield f"{prefix}{key}", value


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def reference():
    return dict(_walk(_load(STRINGS)))


def test_translation_files_present():
    assert len(TRANSLATIONS) >= 12
    assert (INTEGRATION_DIR / "translations" / "en.json").exists()
    assert not (INTEGRATION_DIR / "translations" / "ps.json").exists(), "ps.json held Polish text"


@pytest.mark.parametrize("path", TRANSLATIONS, ids=lambda p: p.name)
def test_translation_is_valid_json(path):
    _load(path)


@pytest.mark.parametrize("path", TRANSLATIONS, ids=lambda p: p.name)
def test_translation_has_same_keys_as_strings(path, reference):
    keys = set(dict(_walk(_load(path))))
    assert keys == set(reference), {
        "missing": sorted(set(reference) - keys), "extra": sorted(keys - set(reference))
    }


@pytest.mark.parametrize("path", [STRINGS, *TRANSLATIONS], ids=lambda p: p.name)
def test_no_html_like_tags(path):
    hits = [(k, HTML_TAG.search(v).group(0)) for k, v in _walk(_load(path))
            if isinstance(v, str) and HTML_TAG.search(v)]
    assert not hits, hits


@pytest.mark.parametrize("path", TRANSLATIONS, ids=lambda p: p.name)
def test_placeholders_match_strings(path, reference):
    """A translation must use exactly the placeholders strings.json defines."""
    bad = {}
    for key, value in _walk(_load(path)):
        if not isinstance(value, str):
            continue
        want = set(PLACEHOLDER.findall(reference.get(key, "")))
        got = set(PLACEHOLDER.findall(value))
        if want != got:
            bad[key] = {"expected": sorted(want), "got": sorted(got)}
    assert not bad, json.dumps(bad, indent=2)


def test_en_matches_strings():
    assert dict(_walk(_load(INTEGRATION_DIR / "translations" / "en.json"))) == \
        dict(_walk(_load(STRINGS)))
